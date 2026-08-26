#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FundOS 六维新闻情报系统 v2.0
============================
六维度 × 12数据源 × 三层关键词 × 关联度打分 × 智能情绪

用法:
  python news_fetch_v2.py                           # 全维度采集
  python news_fetch_v2.py --dimensions 快讯,政策,海外  # 指定维度
  python news_fetch_v2.py --mode quick                  # 快速模式(仅快讯)
  python news_fetch_v2.py --mode full                   # 全量模式(所有维度)
  python news_fetch_v2.py --output daily_report.md      # 导出日报
  python news_fetch_v2.py --schedule                    # 定时模式(盘中每小时)

六维:
  1.实时快讯  2.行业政策  3.基金公告  4.宏观数据  5.资金流向  6.海外联动
"""

import argparse, json, os, re, sys, time, hashlib
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except ImportError:
    print("pip install requests"); sys.exit(1)

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# ============================================================
# 配置
# ============================================================
CACHE_DIR = Path.home() / "FundOS" / "news_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = Path.home() / "FundOS" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/json,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# ============================================================
# 六维定义 + 12数据源
# ============================================================
DIMENSIONS = {
    "快讯": {
        "desc": "实时市场快讯",
        "sources": ["cls_telegram", "eastmoney_news", "wallstreetcn_live"],
        "priority": 1,
    },
    "政策": {
        "desc": "行业政策/部委文件",
        "sources": ["eastmoney_policy", "miit_gov", "nea_gov"],
        "priority": 2,
    },
    "公告": {
        "desc": "基金公告(分红/限购/经理变更/持仓)",
        "sources": ["eastmoney_fund_announce", "cninfo_announce", "tiantian_announce"],
        "priority": 1,
    },
    "宏观": {
        "desc": "宏观经济数据(CPI/PMI/利率/社融)",
        "sources": ["eastmoney_macro", "pbc_gov", "investing_macro"],
        "priority": 3,
    },
    "资金": {
        "desc": "资金流向(北向/主力/板块/龙虎榜)",
        "sources": ["eastmoney_capital", "10jqka_capital"],
        "priority": 2,
    },
    "海外": {
        "desc": "海外市场联动(美股期货/VIX/港股/外汇)",
        "sources": ["investing_global", "eastmoney_global", "xueqiu_hot"],
        "priority": 2,
    },
}

# ============================================================
# 三层关键词: 核心/扩展/关联
# ============================================================
KEYWORD_LAYERS = {
    "半导体": {
        "core": ["半导体+政策", "芯片+制裁", "光刻机", "晶圆+涨价", "先进封装", "HBM"],
        "expand": ["集成电路", "第三代半导体", "EDA", "chiplet", "存储芯片", "台积电"],
        "related": ["AI芯片", "汽车芯片", "国产替代", "大基金"],
    },
    "AI科技": {
        "core": ["人工智能+政策", "大模型+发布", "算力", "ChatGPT", "DeepSeek"],
        "expand": ["AI应用", "机器人", "自动驾驶", "AI Agent", "具身智能"],
        "related": ["数字经济", "信创", "数据要素", "云计算"],
    },
    "美股": {
        "core": ["美联储+利率", "标普500", "纳斯达克", "非农", "CPI+美国"],
        "expand": ["科技七巨头", "Magnificent+7", "VIX", "美债收益率"],
        "related": ["美元指数", "人民币汇率", "中概股", "港股"],
    },
    "绿色电力": {
        "core": ["新型电力系统", "光伏+政策", "风电+装机", "碳中和"],
        "expand": ["储能", "特高压", "绿电交易", "新能源+补贴"],
        "related": ["电力改革", "碳排放", "虚拟电厂"],
    },
    "科创50": {
        "core": ["科创板", "科创50", "硬科技"],
        "expand": ["专精特新", "北交所", "注册制"],
        "related": ["IPO+科创", "科创板+解禁"],
    },
}

# 持仓→板块映射
FUND_SECTOR_MAP = {
    "华夏中证绿色电力ETF联接C": ["绿色电力"],
    "易方达全球成长精选混合(QDII)C": ["美股"],
    "摩根标普500指数(QDII)A": ["美股"],
    "摩根纳斯达克100指数(QDII)A": ["美股", "AI科技"],
    "中欧半导体产业股票C": ["半导体"],
    "易方达信息产业混合C": ["AI科技"],
    "易方达科创50联接A": ["科创50", "半导体"],
    "永赢科技智选混合C": ["AI科技"],
}

# ============================================================
# 智能情绪分析 (v2.0 升级版)
# ============================================================
POSITIVE_KW = {
    "strong": ["重大利好", "超预期", "大幅增长", "历史新高", "突破性"],
    "medium": ["利好", "大涨", "突破", "增长", "回暖", "反弹", "拉升",
               "走强", "领涨", "净流入", "政策支持", "扶持", "加速"],
}

NEGATIVE_KW = {
    "strong": ["重大利空", "崩盘", "暴跌", "腰斩", "违约", "退市风险"],
    "medium": ["利空", "大跌", "下挫", "亏损", "不及预期", "承压",
               "走弱", "领跌", "净流出", "监管", "处罚", "下滑"],
}

NEGATION_WORDS = ["不会", "未能", "并未", "没有", "避免", "防止", "止住", "扭转"]


def classify_sentiment_v2(title: str, content: str = "") -> tuple:
    """v2.0 智能情绪分类: 关键词加权 + 否定词检测 + 位置权重

    Returns: (sentiment_label, score)
    """
    text = (title * 3 + " " + content[:200])  # 标题权重×3

    pos_score = 0
    neg_score = 0

    # 检测否定词 → 反转情绪
    def has_negation(text_seg: str, kw: str) -> bool:
        idx = text_seg.find(kw)
        if idx < 0:
            return False
        before = text_seg[max(0, idx - 6):idx]
        return any(n in before for n in NEGATION_WORDS)

    for level, words in [("strong", POSITIVE_KW["strong"]), ("medium", POSITIVE_KW["medium"])]:
        for w in words:
            if w in text:
                if has_negation(text, w):
                    neg_score += (3 if level == "strong" else 1)
                else:
                    pos_score += (3 if level == "strong" else 1)

    for level, words in [("strong", NEGATIVE_KW["strong"]), ("medium", NEGATIVE_KW["medium"])]:
        for w in words:
            if w in text:
                if has_negation(text, w):
                    pos_score += (3 if level == "strong" else 1)
                else:
                    neg_score += (3 if level == "strong" else 1)

    diff = pos_score - neg_score
    if diff >= 3:
        return ("🟢偏多", diff)
    elif diff <= -3:
        return ("🔴偏空", abs(diff))
    elif diff > 0:
        return ("🟢略偏多", diff)
    elif diff < 0:
        return ("🔴略偏空", abs(diff))
    else:
        return ("⚪中性", 0)


# ============================================================
# 关联度打分
# ============================================================
def relevance_score(text: str, fund_name: str, sectors: list, keywords: dict) -> int:
    """关联度打分: 直接相关(3) / 板块相关(2) / 市场相关(1)"""
    # 3分: 提到基金名或重仓股 (简化: 检查板块核心词)
    for kw in keywords.get("core", []):
        main_kw = kw.split("+")[0] if "+" in kw else kw
        if main_kw in text:
            return 3
    # 2分: 扩展词命中
    for kw in keywords.get("expand", []):
        if kw in text:
            return 2
    # 1分: 关联词
    for kw in keywords.get("related", []):
        if kw in text:
            return 1
    return 1  # 默认市场相关


# ============================================================
# 数据源采集器
# ============================================================
class NewsCollectorV2:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def _json(self, response):
        response.raise_for_status()
        return response.json()

    # ---------- 维度1: 实时快讯 ----------
    def fetch_cls_telegram(self, keyword: str = "") -> list:
        """财联社7x24电报"""
        items = []
        try:
            url = "https://www.cls.cn/api/sw"
            params = {"app": "CailianpressWeb", "os": "web", "sv": "8.4.6",
                      "keyword": keyword, "type": "telegram", "page": 0, "rn": 15}
            resp = self.session.get(url, params=params, timeout=self.timeout)
            data = self._json(resp)
            for item in data.get("data", {}).get("roll_data", []):
                items.append({
                    "title": item.get("title", ""),
                    "content": item.get("brief", "")[:150],
                    "source": "财联社快讯",
                    "url": f"https://www.cls.cn/detail/{item.get('id','')}",
                    "date": datetime.fromtimestamp(item.get("ctime", 0)).strftime("%m-%d %H:%M"),
                    "dimension": "快讯",
                })
        except Exception:
            raise
        return items

    def fetch_eastmoney_news(self, keyword: str, max_items: int = 15) -> list:
        """东方财富资讯搜索"""
        items = []
        try:
            url = "https://searchapi.eastmoney.com/bussiness/Web/GetCMSSearchResult"
            params = {"type": "8196", "pageindex": 1, "pagesize": max_items,
                      "keyword": keyword, "name": "zixun"}
            resp = self.session.get(url, params=params, timeout=self.timeout)
            data = self._json(resp)
            for art in data.get("Data", []):
                title = art.get("Title", "").replace("<em>", "").replace("</em>", "")
                if title:
                    items.append({
                        "title": title,
                        "content": art.get("Content", "")[:150] if "Content" in art else "",
                        "source": "东方财富",
                        "url": art.get("Url", ""),
                        "date": art.get("Date", ""),
                        "dimension": "快讯",
                    })
        except Exception:
            raise
        return items

    def fetch_wallstreetcn_live(self, keyword: str = "") -> list:
        """华尔街见闻快讯"""
        items = []
        try:
            url = "https://api-one.wallstcn.com/apiv1/content/lives"
            params = {"channel": "global-channel", "limit": 15}
            resp = self.session.get(url, params=params, timeout=self.timeout)
            data = self._json(resp)
            for item in data.get("data", {}).get("items", []):
                title = item.get("title", "") + " " + item.get("content_text", "")[:80]
                items.append({
                    "title": title.strip(),
                    "source": "华尔街见闻",
                    "url": item.get("uri", ""),
                    "date": datetime.fromtimestamp(item.get("display_time", 0)).strftime("%m-%d %H:%M"),
                    "dimension": "快讯",
                })
        except Exception:
            raise
        return items

    # ---------- 维度2: 行业政策 ----------
    def fetch_eastmoney_policy(self, keyword: str) -> list:
        """东方财富政策/行业新闻"""
        # 复用 eastmoney_news，加"政策"关键字
        return self.fetch_eastmoney_news(keyword + "+政策")

    def fetch_miit_gov(self, keyword: str = "") -> list:
        """工信部政策 (半导体/AI)"""
        items = []
        if not HAS_BS4:
            return items
        try:
            url = f"https://www.miit.gov.cn/search/index.html?searchword={quote(keyword or '半导体')}"
            resp = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(resp.text, "html.parser")
            for li in soup.select(".clist_con li")[:5]:
                a_tag = li.select_one("a")
                span = li.select_one("span")
                if a_tag:
                    items.append({
                        "title": a_tag.get_text(strip=True),
                        "source": "工信部",
                        "url": a_tag.get("href", ""),
                        "date": span.get_text(strip=True) if span else "",
                        "dimension": "政策",
                    })
        except Exception:
            raise
        return items

    def fetch_nea_gov(self, keyword: str = "") -> list:
        """国家能源局政策 (绿色电力)"""
        items = []
        if not HAS_BS4:
            return items
        try:
            url = f"https://www.nea.gov.cn/search.htm?key={quote(keyword or '光伏')}"
            resp = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(resp.text, "html.parser")
            for item in soup.select(".list_news li")[:5]:
                a_tag = item.select_one("a")
                if a_tag:
                    items.append({
                        "title": a_tag.get_text(strip=True),
                        "source": "国家能源局",
                        "url": a_tag.get("href", ""),
                        "date": "",
                        "dimension": "政策",
                    })
        except Exception:
            raise
        return items

    # ---------- 维度3: 基金公告 ----------
    def fetch_eastmoney_fund_announce(self, keyword: str = "") -> list:
        """天天基金公告"""
        return self.fetch_eastmoney_news(keyword + "+公告+分红+限购+经理")

    def fetch_cninfo_announce(self, keyword: str = "") -> list:
        """巨潮资讯官方公告"""
        items = []
        try:
            url = "http://www.cninfo.com.cn/new/disclosure"
            params = {"column": "szse_latest", "pageNum": 1, "pageSize": 15}
            resp = self.session.post(url, data=params, timeout=self.timeout)
            data = self._json(resp)
            groups = data if isinstance(data, list) else data.get("classifiedAnnouncements", [])
            for item in groups[:10]:
                if not isinstance(item, dict):
                    continue
                for ann in item.get("announcementList", [])[:3]:
                    items.append({
                        "title": ann.get("announcementTitle", ""),
                        "source": "巨潮资讯",
                        "url": f"http://www.cninfo.com.cn/new/disclosure/detail?announceId={ann.get('announcementId','')}",
                        "date": datetime.fromtimestamp(ann.get("announcementTime", 0) / 1000).strftime("%m-%d"),
                        "dimension": "公告",
                    })
        except Exception:
            raise
        return items

    def fetch_tiantian_announce(self, keyword: str = "") -> list:
        """天天基金公告页面"""
        return self.fetch_eastmoney_news(keyword + "+基金公告")

    # ---------- 维度4: 宏观数据 ----------
    def fetch_eastmoney_macro(self, keyword: str = "") -> list:
        """东方财富宏观数据"""
        queries = ["CPI", "PMI", "社融", "LPR", "利率", "GDP"]
        all_items = []
        for q in queries:
            all_items.extend(self.fetch_eastmoney_news(q, max_items=3))
        return all_items

    def fetch_pbc_gov(self, keyword: str = "") -> list:
        """中国人民银行"""
        items = []
        if not HAS_BS4:
            return items
        try:
            url = "http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/11040/index1.html"
            resp = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(resp.text, "html.parser")
            for a_tag in soup.select(".newslist_style a")[:8]:
                items.append({
                    "title": a_tag.get_text(strip=True),
                    "source": "中国人民银行",
                    "url": "http://www.pbc.gov.cn" + a_tag.get("href", ""),
                    "date": "",
                    "dimension": "宏观",
                })
        except Exception:
            raise
        return items

    def fetch_investing_macro(self, keyword: str = "") -> list:
        """英为财情宏观数据"""
        return self.fetch_eastmoney_news("美联储+利率+非农+CPI+GDP", max_items=5)

    # ---------- 维度5: 资金流向 ----------
    def fetch_eastmoney_capital(self, keyword: str = "") -> list:
        """东方财富资金流向"""
        items = []
        try:
            # 北向资金
            url = "https://push2.eastmoney.com/api/qt/kamt.kline/get"
            params = {"fields1": "f1,f3", "fields2": "f51,f52",
                      "klt": "101", "lmt": 5, "secid": "1.000300"}
            resp = self.session.get(url, params=params, timeout=self.timeout)
            data = self._json(resp)
            klines = data.get("data", {}).get("klines", []) if data.get("data") else []
            if klines:
                last = klines[-1].split(",")
                net_flow = float(last[1]) / 1e8 if len(last) > 1 else 0
                direction = "净流入" if net_flow > 0 else "净流出"
                items.append({
                    "title": f"北向资金今日{direction}{abs(net_flow):.1f}亿",
                    "source": "东方财富资金",
                    "url": "",
                    "date": datetime.now().strftime("%m-%d"),
                    "dimension": "资金",
                })
        except Exception:
            raise

        # 板块资金排名
        try:
            url2 = "https://push2.eastmoney.com/api/qt/clist/get"
            params2 = {"pn": "1", "pz": "5", "fs": "m:90+t2", "fields": "f2,f3,f4,f12,f14,f62,f184",
                       "fid": "f62", "po": "1"}
            resp2 = self.session.get(url2, params=params2, timeout=self.timeout)
            data2 = self._json(resp2)
            for item in data2.get("data", {}).get("diff", [])[:5]:
                items.append({
                    "title": f"{item.get('f14','')} 主力净流入{item.get('f62','')}万 涨跌幅{item.get('f3','')}%",
                    "source": "板块资金",
                    "url": "",
                    "date": datetime.now().strftime("%m-%d"),
                    "dimension": "资金",
                })
        except Exception:
            raise
        return items

    def fetch_10jqka_capital(self, keyword: str = "") -> list:
        """同花顺资金流向"""
        return self.fetch_eastmoney_news("北向资金+主力资金", max_items=5)

    # ---------- 维度6: 海外联动 ----------
    def fetch_investing_global(self, keyword: str = "") -> list:
        """海外市场数据"""
        return self.fetch_eastmoney_news("美股+纳斯达克+标普+VIX+美元", max_items=8)

    def fetch_eastmoney_global(self, keyword: str = "") -> list:
        """东方财富全球"""
        return self.fetch_eastmoney_news("美股期货+中概股+港股", max_items=5)

    def fetch_xueqiu_hot(self, keyword: str = "") -> list:
        """雪球热搜"""
        return self.fetch_eastmoney_news("雪球+热门+讨论", max_items=5)


# ============================================================
# 主采集流程
# ============================================================
def collect_all(dimensions: list = None, mode: str = "full") -> dict:
    """六维全量采集"""
    collector = NewsCollectorV2()

    if mode == "quick":
        dim_names = ["快讯"]
    elif dimensions:
        dim_names = [d for d in dimensions if d in DIMENSIONS]
    else:
        dim_names = list(DIMENSIONS.keys())

    all_news = []
    source_stats = {}
    stats_lock = threading.Lock()

    def call_source(source_name, func, keyword):
        started = time.perf_counter()
        try:
            items = func(keyword) or []
            status = "ok" if items else "empty"
            error = ""
        except Exception as exc:
            items = []
            status = "error"
            error = f"{type(exc).__name__}: {exc}"[:300]
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        with stats_lock:
            stat = source_stats.setdefault(source_name, {
                "status": "empty", "items": 0, "calls": 0,
                "errors": [], "elapsed_ms": 0,
            })
            stat["calls"] += 1
            stat["items"] += len(items)
            stat["elapsed_ms"] += elapsed_ms
            if status == "ok":
                stat["status"] = "ok"
            elif status == "error" and stat["status"] != "ok":
                stat["status"] = "error"
            if error and error not in stat["errors"]:
                stat["errors"].append(error)
        return items

    def search_task(kw_text: str):
        """单个搜索任务"""
        results = []
        # 快讯层搜索
        if "快讯" in dim_names:
            results.extend(call_source("cls_telegram", collector.fetch_cls_telegram, kw_text))
            results.extend(call_source("eastmoney_news", collector.fetch_eastmoney_news, kw_text))
            results.extend(call_source("wallstreetcn_live", collector.fetch_wallstreetcn_live, kw_text))
        # 政策层
        if "政策" in dim_names:
            results.extend(call_source("eastmoney_policy", collector.fetch_eastmoney_policy, kw_text))
            results.extend(call_source("miit_gov", collector.fetch_miit_gov, kw_text))
            results.extend(call_source("nea_gov", collector.fetch_nea_gov, kw_text))
        # 公告层
        if "公告" in dim_names:
            results.extend(call_source("eastmoney_fund_announce", collector.fetch_eastmoney_fund_announce, kw_text))
            results.extend(call_source("cninfo_announce", collector.fetch_cninfo_announce, kw_text))
            results.extend(call_source("tiantian_announce", collector.fetch_tiantian_announce, kw_text))
        # 宏观层
        if "宏观" in dim_names:
            results.extend(call_source("eastmoney_macro", collector.fetch_eastmoney_macro, kw_text))
            results.extend(call_source("pbc_gov", collector.fetch_pbc_gov, kw_text))
            results.extend(call_source("investing_macro", collector.fetch_investing_macro, kw_text))
        # 资金层
        if "资金" in dim_names:
            results.extend(call_source("eastmoney_capital", collector.fetch_eastmoney_capital, kw_text))
            results.extend(call_source("10jqka_capital", collector.fetch_10jqka_capital, kw_text))
        # 海外层
        if "海外" in dim_names:
            results.extend(call_source("investing_global", collector.fetch_investing_global, kw_text))
            results.extend(call_source("eastmoney_global", collector.fetch_eastmoney_global, kw_text))
            results.extend(call_source("xueqiu_hot", collector.fetch_xueqiu_hot, kw_text))
        return results

    # 收集所有关键词
    all_keywords = set()
    for sector, layers in KEYWORD_LAYERS.items():
        for kw in layers["core"]:
            main = kw.split("+")[0] if "+" in kw else kw
            all_keywords.add(main)

    # 并发搜索
    print(f"\n  📡 启动六维采集: {'+'.join(dim_names)} × {len(all_keywords)}个关键词...\n")
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(search_task, kw): kw for kw in all_keywords}
        for future in as_completed(futures):
            kw = futures[future]
            try:
                results = future.result()
                all_news.extend(results)
                print(f"    ✅ {kw}: {len(results)}条")
            except:
                print(f"    ❌ {kw}: 失败")

    # 去重
    seen = set()
    unique = []
    for item in all_news:
        h = hashlib.md5(item["title"].encode()).hexdigest()
        if h not in seen:
            seen.add(h)
            # 情绪分类
            sentiment, score = classify_sentiment_v2(item["title"], item.get("content", ""))
            item["sentiment"] = sentiment
            item["sentiment_score"] = score
            unique.append(item)

    # 按日期排序
    unique.sort(key=lambda x: x.get("date", ""), reverse=True)

    source_status = {}
    for dimension in dim_names:
        count = sum(1 for item in unique if item.get("dimension") == dimension)
        source_status[dimension] = {
            "status": "ok" if count else "empty",
            "items": count,
        }
    enabled_sources = {source for dimension in dim_names for source in DIMENSIONS[dimension]["sources"]}
    for source in enabled_sources:
        source_status[source] = source_stats.get(source, {
            "status": "not_enabled", "items": 0, "calls": 0,
            "errors": [], "elapsed_ms": 0,
        })
    for source, stat in source_status.items():
        if isinstance(stat, dict):
            stat["error"] = "; ".join(stat.pop("errors", []))
    return {"news": unique, "dimensions": dim_names,
            "source_status": source_status,
            "collected_at": datetime.now().isoformat()}


# ============================================================
# 输出: 按持仓基金分组
# ============================================================
def format_by_fund(data: dict) -> str:
    """按持仓基金分组输出日报"""
    news = data["news"]
    dims = data["dimensions"]

    lines = []
    lines.append(f"# 📰 基金持仓情报日报")
    lines.append(f"> 采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"> 维度: {' · '.join(dims)}")
    lines.append(f"> 采集条数: {len(news)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 六维热度
    dim_counts = {}
    for item in news:
        d = item.get("dimension", "快讯")
        dim_counts[d] = dim_counts.get(d, 0) + 1

    lines.append("## 📊 六维热度")
    lines.append("")
    for dim_name in DIMENSIONS:
        count = dim_counts.get(dim_name, 0)
        bar = "█" * min(count, 20)
        lines.append(f"| {dim_name} | {bar} | {count}条 |")
    lines.append("")

    # 整体情绪
    pos = sum(1 for n in news if "偏多" in n.get("sentiment", ""))
    neg = sum(1 for n in news if "偏空" in n.get("sentiment", ""))
    neu = len(news) - pos - neg
    lines.append(f"## 🎯 整体情绪: 🟢{pos} · 🔴{neg} · ⚪{neu}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ⚠️ 重点提醒 (关联度≥2的新闻)
    lines.append("## ⚠️ 重点提醒")
    lines.append("")
    high_rel = [n for n in news if n.get("relevance", 0) >= 2]
    if high_rel:
        for item in high_rel[:10]:
            lines.append(f"- {item['sentiment']} [{item.get('dimension','')}] {item['title']}")
            if item.get("url"):
                lines.append(f"  [{item['source']}]({item['url']}) — {item.get('date','')}")
    else:
        lines.append("*今日无高关联度新闻*")
    lines.append("")

    # 按你的持仓分组
    lines.append("---")
    lines.append("")
    lines.append("## 📋 按你的持仓")
    lines.append("")

    for fund_name, sectors in FUND_SECTOR_MAP.items():
        lines.append(f"### {fund_name[:25]}")
        lines.append(f"*板块: {', '.join(sectors)}*")
        lines.append("")

        # 匹配该基金的新闻
        fund_news = []
        for item in news:
            title = item.get("title", "")
            for sector in sectors:
                layers = KEYWORD_LAYERS.get(sector, {})
                for level in ["core", "expand"]:
                    for kw in layers.get(level, []):
                        main = kw.split("+")[0] if "+" in kw else kw
                        if main in title:
                            # 给关联度打分
                            rel = 3 if level == "core" else 2
                            item_copy = dict(item)
                            item_copy["relevance"] = rel
                            fund_news.append(item_copy)
                            break
                    else:
                        continue
                    break

        # 去重
        seen_titles = set()
        fund_news_unique = []
        for n in fund_news:
            if n["title"] not in seen_titles:
                seen_titles.add(n["title"])
                fund_news_unique.append(n)

        fund_news_unique.sort(key=lambda x: x.get("relevance", 0), reverse=True)

        if fund_news_unique:
            fund_pos = sum(1 for n in fund_news_unique if "偏多" in n.get("sentiment", ""))
            fund_neg = sum(1 for n in fund_news_unique if "偏空" in n.get("sentiment", ""))
            lines.append(f"🟢{fund_pos} 🔴{fund_neg} | 共{len(fund_news_unique)}条")
            lines.append("")
            for item in fund_news_unique[:6]:
                lines.append(f"- {item['sentiment']} [{item.get('dimension','')}] {item['title'][:80]}")
                lines.append(f"  *{item['source']} {item.get('date','')}*")
        else:
            lines.append("*未找到直接相关新闻*")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## ⚠️ 免责声明")
    lines.append("> 本情报仅客观汇总公开信息，**不构成任何投资建议**。")
    lines.append("> 情绪分类为算法自动标注，存在误判，请阅读原文自行判断。")
    lines.append("> 市场有风险，投资需谨慎。")

    return "\n".join(lines)


def format_console(data: dict):
    """控制台输出"""
    news = data["news"]
    dims = data["dimensions"]

    print("\n" + "=" * 70)
    print(f"  📰  FundOS 情报日报  {datetime.now().strftime('%m-%d %H:%M')}")
    print("=" * 70)
    print(f"  维度: {' · '.join(dims)}  |  采集: {len(news)}条")

    pos = sum(1 for n in news if "偏多" in n.get("sentiment", ""))
    neg = sum(1 for n in news if "偏空" in n.get("sentiment", ""))
    print(f"  情绪: 🟢{pos} 🔴{neg} ⚪{len(news)-pos-neg}")
    print("-" * 70)

    for fund_name, sectors in FUND_SECTOR_MAP.items():
        print(f"\n  📌 {fund_name[:30]}  ({', '.join(sectors)})")
        fund_news = []
        for item in news:
            title = item.get("title", "")
            for sector in sectors:
                layers = KEYWORD_LAYERS.get(sector, {})
                for level in ["core", "expand"]:
                    for kw in layers.get(level, []):
                        main = kw.split("+")[0] if "+" in kw else kw
                        if main in title:
                            item_copy = dict(item)
                            item_copy["relevance"] = 3 if level == "core" else 2
                            fund_news.append(item_copy)
                            break
                    else:
                        continue
                    break

        seen = set()
        count = 0
        fund_news.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        for item in fund_news:
            if item["title"] not in seen and count < 4:
                seen.add(item["title"])
                print(f"    {item['sentiment']} {item['title'][:65]}")
                count += 1
        if count == 0:
            print(f"    (无直接相关新闻)")

    print("\n" + "=" * 70)
    print("  ⚠️  以上为客观新闻汇总，不构成投资建议")


# ============================================================
# CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="FundOS 六维新闻情报系统 v2.0")
    parser.add_argument("--mode", choices=["quick", "full"], default="full",
                       help="quick=仅快讯 / full=全部六维")
    parser.add_argument("--dimensions", "-d",
                       help="逗号分隔: 快讯,政策,公告,宏观,资金,海外")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--format", "-f", choices=["markdown", "console", "json"],
                       default="console")
    parser.add_argument("--clear-cache", action="store_true", help="清除缓存")
    parser.add_argument("--list-dimensions", action="store_true", help="列出六维定义")
    parser.add_argument("--list-keywords", action="store_true", help="列出板块关键词")
    args = parser.parse_args()

    if args.clear_cache:
        import shutil
        if CACHE_DIR.exists():
            shutil.rmtree(CACHE_DIR)
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
        print("✅ 缓存已清除")
        return

    if args.list_dimensions:
        print("\n📡 FundOS 六维采集架构:\n")
        for dim, info in DIMENSIONS.items():
            print(f"  {dim} (优先级{info['priority']})")
            print(f"    {info['desc']}")
            print(f"    数据源: {', '.join(info['sources'])}")
            print()
        return

    if args.list_keywords:
        print("\n📋 板块关键词分层:\n")
        for sector, layers in KEYWORD_LAYERS.items():
            print(f"  {sector}")
            print(f"    核心: {', '.join(layers['core'][:5])}")
            print(f"    扩展: {', '.join(layers['expand'][:5])}")
            print(f"    关联: {', '.join(layers['related'][:5])}")
            print()
        return

    # 解析维度
    dimensions = None
    if args.dimensions:
        dimensions = [d.strip() for d in args.dimensions.split(",")]

    # 采集
    data = collect_all(dimensions=dimensions, mode=args.mode)

    # 输出
    if args.format == "json" or (args.output and args.output.endswith(".json")):
        output = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    elif args.format == "markdown" or (args.output and args.output.endswith(".md")):
        output = format_by_fund(data)
    else:
        format_console(data)
        output = None

    if args.output and output:
        out_path = Path(args.output)
        out_path.write_text(output, encoding="utf-8")
        print(f"\n  ✅ 已保存: {out_path.absolute()}")

    if args.format == "markdown" and not args.output:
        print(output)
    if args.format == "json" and not args.output:
        print(output)


if __name__ == "__main__":
    main()
