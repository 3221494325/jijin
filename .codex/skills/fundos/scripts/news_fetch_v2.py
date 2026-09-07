#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FundOS 六维新闻情报系统 v2.1
============================
v2.1 (2026-08-28) 引擎修复 —— 依据 fund_engine_audit.md 审计：
  - 移除死源: cls_telegram(405) / searchapi.eastmoney.com(JSONDecodeError)
              / push2.eastmoney.com(ProxyError, 架构矩阵禁用) / 政府网爬虫(pbc/miit/nea 长期空)
  - 东财搜索切换到已验证的 search-api-web.eastmoney.com (jsonp, 限流保护)
  - 新增已验证源: 同花顺快讯 / 新浪滚动快讯
  - 修复维度错标 bug: v2.0 所有搜索结果都标成"快讯"，导致政策/公告/宏观/资金/海外恒为空
  - 东财调用加全局限速 + 调用预算，防限流封禁

用法:
  python news_fetch_v2.py                           # 全维度采集
  python news_fetch_v2.py --mode quick              # 快速模式(仅快讯)
  python news_fetch_v2.py --dimensions 快讯,海外    # 指定维度
  python news_fetch_v2.py --format json             # 引擎契约输出(fund_engine 调用)
  python news_fetch_v2.py --format markdown -o out.md

六维:
  1.实时快讯  2.行业政策  3.基金公告  4.宏观数据  5.资金流向  6.海外联动
"""

import argparse
import hashlib
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import requests

# 项目根 = .codex/skills/fundos/scripts 往上 4 级
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))
from fundos_config import FUND_SECTOR_MAP, DATA_DIR  # noqa: E402

CACHE_DIR = DATA_DIR / "news_cache"
REPORT_DIR = DATA_DIR / "reports"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# ============================================================
# 六维定义 + 数据源（仅保留实测可用源）
# ============================================================
DIMENSIONS = {
    "快讯": {
        "desc": "实时市场快讯",
        "sources": ["wallstreetcn_live", "ths_news", "sina_roll", "eastmoney_search"],
        "priority": 1,
    },
    "政策": {
        "desc": "行业政策/部委动向(搜索聚合)",
        "sources": ["eastmoney_policy"],
        "priority": 2,
    },
    "公告": {
        "desc": "基金公告(分红/限购/经理变更, 搜索聚合)",
        "sources": ["eastmoney_fund_announce"],
        "priority": 1,
    },
    "宏观": {
        "desc": "宏观经济数据(CPI/PMI/利率/社融)",
        "sources": ["eastmoney_macro"],
        "priority": 3,
    },
    "资金": {
        "desc": "资金流向(北向/主力, 搜索聚合)",
        "sources": ["eastmoney_capital"],
        "priority": 2,
    },
    "海外": {
        "desc": "海外市场联动(美股/VIX/港股)",
        "sources": ["eastmoney_global"],
        "priority": 2,
    },
}

# ============================================================
# 三层关键词: 核心/扩展/关联
# ============================================================
KEYWORD_LAYERS = {
    "半导体": {
        "core": ["半导体", "芯片", "光刻机", "晶圆", "先进封装", "HBM"],
        "expand": ["集成电路", "第三代半导体", "EDA", "存储芯片", "台积电"],
        "related": ["AI芯片", "汽车芯片", "国产替代", "大基金"],
    },
    "AI科技": {
        "core": ["人工智能", "大模型", "算力", "ChatGPT", "DeepSeek"],
        "expand": ["AI应用", "机器人", "自动驾驶", "AI Agent", "具身智能"],
        "related": ["数字经济", "信创", "数据要素", "云计算"],
    },
    "美股": {
        "core": ["美联储", "标普500", "纳斯达克", "非农", "CPI"],
        "expand": ["科技七巨头", "VIX", "美债收益率"],
        "related": ["美元指数", "人民币汇率", "中概股", "港股"],
    },
    "绿色电力": {
        "core": ["新型电力系统", "光伏", "风电", "碳中和"],
        "expand": ["储能", "特高压", "绿电交易"],
        "related": ["电力改革", "碳排放", "虚拟电厂"],
    },
    "科创50": {
        "core": ["科创板", "科创50", "硬科技"],
        "expand": ["专精特新", "北交所"],
        "related": ["IPO", "科创板解禁"],
    },
}

# ============================================================
# 智能情绪分析 (v2.0 保留)
# ============================================================
POSITIVE_KW = {
    "strong": ["重大利好", "超预期", "大幅增长", "历史新高", "突破性"],
    "medium": ["利好", "大涨", "涨停", "突破", "增长", "盈利", "回暖", "反弹", "拉升",
               "走强", "领涨", "净流入", "政策支持", "扶持", "加速",
               "上涨", "收涨", "涨超", "涨", "扭亏", "中标", "获批", "创新高"],
}

NEGATIVE_KW = {
    "strong": ["重大利空", "崩盘", "暴跌", "腰斩", "违约", "退市风险", "造假", "欺诈",
               "立案调查", "行政处罚", "被罚", "罚款", "警示函", "监管函", "减持"],
    "medium": ["利空", "大跌", "下挫", "亏损", "不及预期", "承压",
               "走弱", "领跌", "净流出", "监管", "处罚", "下滑",
               "违规", "立案", "问询", "遭遇", "暂停上市",
               "下跌", "收跌", "跌", "减持", "终止", "冻结", "失信", "被执行", "拖欠"],
}

# 数字涨跌幅模式：无关键词但带 "涨/跌 X%" 的快讯（如 "现货钯金涨8.00%"）
import re as _re
RISE_PCT_RE = _re.compile(r"(涨|升)\s*[0-9.]+%")
FALL_PCT_RE = _re.compile(r"(跌|下挫)\s*[0-9.]+%")

NEGATION_WORDS = ["不会", "未能", "并未", "没有", "避免", "防止", "止住", "扭转"]


def classify_sentiment_v2(title: str, content: str = "") -> tuple:
    """v2.2 智能情绪分类: 关键词加权 + 否定词检测 + 位置权重 + 数字涨跌幅模式

    Returns: (sentiment_label, signed_score)
    v2.2 修复: 分值改为【带符号】(正=偏多, 负=偏空)。旧版返回绝对值，
    导致"略偏空2分"与"略偏多2分"无法区分，下游标签错判方向。
    """
    text = (title * 3 + " " + content[:200])  # 标题权重×3

    pos_score = 0
    neg_score = 0

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

    # 数字涨跌幅: "涨8.00%" / "跌0.5%" —— 比泛词更强的方向证据
    if RISE_PCT_RE.search(text):
        pos_score += 2
    if FALL_PCT_RE.search(text):
        neg_score += 2

    diff = pos_score - neg_score
    if diff >= 3:
        return ("🟢偏多", diff)
    elif diff <= -3:
        return ("🔴偏空", diff)
    elif diff > 0:
        return ("🟢略偏多", diff)
    elif diff < 0:
        return ("🔴略偏空", diff)
    return ("⚪中性", 0)


def sentiment_label_cn(item):
    """中文标签（利好/利空/中性），带强弱阈值：|分值|>=2 才定性。
    弱信号(±1分，如标题只扫到一个泛词)一律归中性 —— 宁可少说，不能乱说。"""
    sc = item.get("sentiment_score", 0) if isinstance(item, dict) else item
    if sc >= 2:
        return "利好"
    if sc <= -2:
        return "利空"
    return "中性"


def compute_sentiment_index(items):
    """多空情绪指数 v2: 0-100，50=中性。

    v1 按情绪分数累加，快讯普遍带"增长/盈利"等词时会饱和到100，失去参考价值。
    v2 改为【条数占比 + 阻尼】: index = 50 + 50*(利好条数-利空条数)/(利好+利空+8)
      - 只统计达到定性阈值(±2分)的条目，与页面标签口径一致
      - 阻尼项8条：少量新闻时不轻易给出极端读数
    """
    n_up = sum(1 for i in items if i.get("sentiment_score", 0) >= 2)
    n_down = sum(1 for i in items if i.get("sentiment_score", 0) <= -2)
    n_flat = len(items) - n_up - n_down
    if n_up + n_down == 0:
        index = 50.0
    else:
        index = round(50 + 50 * (n_up - n_down) / (n_up + n_down + 8), 1)
    label = "偏多" if index >= 60 else ("偏空" if index <= 40 else "中性")
    return {"index": index, "label": label, "up": n_up, "down": n_down,
            "flat": n_flat, "count": len(items),
            "pos": sum(max(i.get("sentiment_score", 0), 0) for i in items),
            "neg": sum(max(-i.get("sentiment_score", 0), 0) for i in items)}


# ============================================================
# 数据源采集器（仅保留实测可用源；维度由调用方传入，修复错标）
# ============================================================
class NewsCollectorV21:
    """线程安全的采集器。东财搜索带全局限速（限流保护）。"""

    EM_MIN_INTERVAL = 0.6   # 两次东财搜索最小间隔(秒)
    EM_MAX_CALLS = 40       # 单次运行东财搜索调用预算

    def __init__(self, timeout: int = 12):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self._em_lock = threading.Lock()
        self._em_last = [0.0]
        self._em_calls = [0]

    # ---------- 基础 ----------
    def _get_json(self, url, **kw):
        resp = self.session.get(url, timeout=self.timeout, **kw)
        resp.raise_for_status()
        return resp.json()

    def _em_throttle(self):
        """东财全局限速：超预算抛错，间隔不足等待。"""
        with self._em_lock:
            if self._em_calls[0] >= self.EM_MAX_CALLS:
                raise RuntimeError("东财搜索调用预算已用尽")
            wait = self.EM_MIN_INTERVAL - (time.time() - self._em_last[0])
            if wait > 0:
                time.sleep(wait)
            self._em_last[0] = time.time()
            self._em_calls[0] += 1

    # ---------- 源 1: 华尔街见闻快讯 ----------
    def fetch_wallstreetcn_live(self, keyword: str = "", dimension: str = "快讯") -> list:
        items = []
        for channel in ("global", "a-stock"):
            try:
                data = self._get_json(
                    "https://api-one.wallstcn.com/apiv1/content/lives",
                    params={"channel": f"{channel}-channel", "limit": 15})
                for item in data.get("data", {}).get("items", []):
                    title = (item.get("title") or item.get("content_text") or "").strip()
                    if len(title) < 10:
                        continue
                    ts = item.get("display_time") or 0
                    items.append({
                        "title": title[:120],
                        "content": (item.get("content_text") or "")[:150],
                        "source": f"华尔街见闻·{channel}",
                        "url": item.get("uri", ""),
                        "date": datetime.fromtimestamp(ts).strftime("%m-%d %H:%M") if ts else "",
                        "dimension": dimension,
                    })
            except Exception:
                continue
        return items

    # ---------- 源 2: 同花顺快讯 ----------
    def fetch_ths_news(self, keyword: str = "", dimension: str = "快讯") -> list:
        try:
            data = self._get_json(
                "https://news.10jqka.com.cn/tapp/news/push/stock/",
                params={"page": 1, "tag": "", "track": "website"})
            out = []
            for it in (data.get("data") or {}).get("list", [])[:25]:
                title = (it.get("title") or "").strip()
                if len(title) < 8:
                    continue
                ts = int(it.get("ctime") or 0)
                out.append({
                    "title": title[:120], "content": "",
                    "source": "同花顺",
                    "url": it.get("url", ""),
                    "date": datetime.fromtimestamp(ts).strftime("%m-%d %H:%M") if ts else "",
                    "dimension": dimension,
                })
            return out
        except Exception:
            raise

    # ---------- 源 3: 新浪滚动快讯 ----------
    def fetch_sina_roll(self, keyword: str = "", dimension: str = "快讯") -> list:
        try:
            data = self._get_json(
                "https://feed.mix.sina.com.cn/api/roll/get",
                params={"pageid": 153, "lid": 2509, "k": "", "num": 25, "page": 1})
            out = []
            for it in (data.get("result") or {}).get("data", []) or []:
                title = (it.get("title") or "").strip()
                if len(title) < 8:
                    continue
                ts = int(it.get("ctime") or 0)
                out.append({
                    "title": title[:120],
                    "content": (it.get("intro") or "")[:150],
                    "source": "新浪财经",
                    "url": it.get("url", ""),
                    "date": datetime.fromtimestamp(ts).strftime("%m-%d %H:%M") if ts else "",
                    "dimension": dimension,
                })
            return out
        except Exception:
            raise

    # ---------- 源 4: 东财资讯搜索 (search-api-web, jsonp) ----------
    def fetch_eastmoney_search(self, keyword: str, dimension: str = "快讯",
                               max_items: int = 12, retries: int = 2) -> list:
        """注意: 必须用 urllib 原样透传 URL —— requests 会对百分号编码做规范化，
        破坏 param 中的 JSON 转义，东财会返回错误的 result 维度 (passportWeb)。"""
        import urllib.request
        self._em_throttle()
        param = {
            "uid": "", "keyword": keyword,
            "type": ["cmsArticleWebOld"], "client": "web", "clientVersion": "curr",
            "param": {"cmsArticleWebOld": {
                "searchScope": "default", "sort": "time",
                "pageIndex": 1, "pageSize": max_items,
                "preTag": "<em>", "postTag": "</em>"}},
        }
        url = ("https://search-api-web.eastmoney.com/search/jsonp?cb=cb&param="
               + quote(json.dumps(param)))
        last_err = None
        for attempt in range(retries + 1):
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": HEADERS["User-Agent"],
                    "Referer": "https://so.eastmoney.com/"})
                text = urllib.request.urlopen(req, timeout=self.timeout).read().decode("utf-8", "replace")
                data = json.loads(text[text.index("(") + 1:text.rindex(")")])
                out = []
                for art in (data.get("result") or {}).get("cmsArticleWebOld", []) or []:
                    title = (art.get("title") or "").replace("<em>", "").replace("</em>", "").strip()
                    if not title:
                        continue
                    out.append({
                        "title": title[:120],
                        "content": (art.get("Content") or "")[:150],
                        "source": "东方财富",
                        "url": art.get("url", "") or art.get("Url", ""),
                        "date": (art.get("date") or "")[:16],
                        "dimension": dimension,
                    })
                return out
            except Exception as exc:
                last_err = exc
                if attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
        raise last_err if last_err else RuntimeError("eastmoney_search 未知失败")

    # ---------- 搜索聚合维度（政策/公告/宏观/资金/海外） ----------
    def fetch_eastmoney_policy(self, keyword: str) -> list:
        return self.fetch_eastmoney_search(f"{keyword} 政策", dimension="政策", max_items=6)

    def fetch_eastmoney_fund_announce(self, keyword: str) -> list:
        return self.fetch_eastmoney_search("基金 分红 限购 公告", dimension="公告", max_items=8)

    def fetch_eastmoney_macro(self, keyword: str = "") -> list:
        out = []
        for q in ("CPI", "PMI", "社融", "LPR"):
            out.extend(self.fetch_eastmoney_search(q, dimension="宏观", max_items=4))
        return out

    def fetch_eastmoney_capital(self, keyword: str = "") -> list:
        return self.fetch_eastmoney_search("北向资金 主力资金", dimension="资金", max_items=8)

    def fetch_eastmoney_global(self, keyword: str = "") -> list:
        return self.fetch_eastmoney_search("美股 纳斯达克 标普", dimension="海外", max_items=8)


def collect_direct_news(limit_each: int = 15) -> list:
    """轻量直连快讯：仅三大直连源（见闻/同花顺/新浪），并发拉取约1-2秒。
    供可视化面板等高频场景复用；不写 news_result.json，不动引擎采集契约。
    返回已去重、已情绪标注的 item 列表（与 v1 契约同字段）。"""
    collector = NewsCollectorV21(timeout=8)
    results = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [
            pool.submit(collector.fetch_wallstreetcn_live, "", "快讯"),
            pool.submit(collector.fetch_ths_news, "", "快讯"),
            pool.submit(collector.fetch_sina_roll, "", "快讯"),
        ]
        for fu in futures:
            try:
                results.extend(fu.result())
            except Exception:
                continue
    seen, unique = set(), []
    for item in results:
        title = (item.get("title") or "").strip()
        if not title or len(title) < 8:
            continue
        h = hashlib.md5(title.encode()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        item["title"] = title[:120]
        s, score = classify_sentiment_v2(item["title"], item.get("content", ""))
        item["sentiment"] = s
        item["sentiment_score"] = score
        unique.append(item)
    unique.sort(key=lambda x: x.get("date", ""), reverse=True)
    return unique


# ============================================================
# 当日新闻归档（快讯是流，不落盘就会被冲掉——AI 需要全天图景）
# ============================================================
NEWS_ARCHIVE_DIR = DATA_DIR / "news_history"


def archive_news(items):
    """把一批快讯合并进当日归档（按标题去重），返回当日全量归档列表。
    每日一个文件 data/news_history/news_YYYY-MM-DD.json，上限800条防膨胀。"""
    NEWS_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    path = NEWS_ARCHIVE_DIR / f"news_{datetime.now():%Y-%m-%d}.json"
    try:
        day = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        day = []
    seen = {x.get("id") for x in day}
    for it in items:
        title = (it.get("title") or "").strip()
        if not title:
            continue
        hid = hashlib.md5(title.encode()).hexdigest()
        if hid in seen:
            continue
        seen.add(hid)
        day.append({
            "id": hid, "title": title[:120],
            "label": it.get("label") or sentiment_label_cn(it),
            "score": it.get("sentiment_score", 0),
            "source": it.get("source", ""), "date": it.get("date", ""),
            "url": it.get("url", ""),
            "collected_at": datetime.now().isoformat(timespec="seconds"),
        })
    day = day[-800:]
    path.write_text(json.dumps(day, ensure_ascii=False), encoding="utf-8")
    return day


def load_day_archive(date_str=None):
    """读某日归档（缺省今天）。"""
    day = date_str or datetime.now().strftime("%Y-%m-%d")
    path = NEWS_ARCHIVE_DIR / f"news_{day}.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def day_summary(day_items):
    """全天累计统计：多空计数 + 当日最强利空/利好榜（供 AI 与看板使用）。"""
    scored = [x for x in day_items if isinstance(x.get("score"), (int, float))]
    up = [x for x in scored if x["score"] >= 2]
    down = [x for x in scored if x["score"] <= -2]
    top_bad = sorted(down, key=lambda x: x["score"])[:10]
    top_good = sorted(up, key=lambda x: -x["score"])[:10]
    titles = lambda lst: [{"title": x.get("title", ""), "source": x.get("source", "")}
                          for x in lst]
    return {"up": len(up), "down": len(down),
            "flat": len(day_items) - len(up) - len(down),
            "total": len(day_items),
            "top_bad": titles(top_bad), "top_good": titles(top_good)}


# ============================================================
# 主采集流程
# ============================================================
def collect_all(dimensions: list = None, mode: str = "full") -> dict:
    collector = NewsCollectorV21()

    if mode == "quick":
        dim_names = ["快讯"]
    elif dimensions:
        dim_names = [d for d in dimensions if d in DIMENSIONS]
    else:
        dim_names = list(DIMENSIONS.keys())

    all_news = []
    source_stats = {}
    stats_lock = threading.Lock()

    def call_source(source_name, func, *args):
        started = time.perf_counter()
        try:
            items = func(*args) or []
            status = "ok" if items else "empty"
            error = ""
        except Exception as exc:
            items = []
            status = "error"
            error = f"{type(exc).__name__}: {exc}"[:200]
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
        """单个关键词的多源采集"""
        results = []
        if "快讯" in dim_names:
            results.extend(call_source("eastmoney_search",
                                       collector.fetch_eastmoney_search, kw_text, "快讯"))
        if "政策" in dim_names:
            results.extend(call_source("eastmoney_policy",
                                       collector.fetch_eastmoney_policy, kw_text))
        return results

    # 收集核心关键词
    all_keywords = []
    for layers in KEYWORD_LAYERS.values():
        for kw in layers["core"]:
            if kw not in all_keywords:
                all_keywords.append(kw)
    # 搜索型维度控制在预算内（东财限流保护）
    if len(all_keywords) > 12:
        all_keywords = all_keywords[:12]

    print(f"\n  📡 启动六维采集: {'+'.join(dim_names)} × {len(all_keywords)}个关键词...\n")

    # 快讯直连源（无需关键词扇出，一次拉满）
    direct_results = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {
            pool.submit(call_source, "wallstreetcn_live",
                        collector.fetch_wallstreetcn_live, "", "快讯"): "wallstreetcn_live",
            pool.submit(call_source, "ths_news",
                        collector.fetch_ths_news, "", "快讯"): "ths_news",
            pool.submit(call_source, "sina_roll",
                        collector.fetch_sina_roll, "", "快讯"): "sina_roll",
        }
        for future in as_completed(futures):
            try:
                direct_results.extend(future.result())
            except Exception:
                pass
    if "快讯" in dim_names:
        all_news.extend(direct_results)
        print(f"    ✅ 直连快讯源: {len(direct_results)}条")

    # 搜索层（东财，限速+预算）
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(search_task, kw): kw for kw in all_keywords}
        for future in as_completed(futures):
            kw = futures[future]
            try:
                results = future.result()
                all_news.extend(results)
                print(f"    ✅ {kw}: {len(results)}条")
            except Exception:
                print(f"    ❌ {kw}: 失败")

    # 聚合维度（固定查询，各跑一次，不随关键词扇出）
    one_shot = []
    if "公告" in dim_names:
        one_shot.append(("eastmoney_fund_announce", collector.fetch_eastmoney_fund_announce))
    if "宏观" in dim_names:
        one_shot.append(("eastmoney_macro", collector.fetch_eastmoney_macro))
    if "资金" in dim_names:
        one_shot.append(("eastmoney_capital", collector.fetch_eastmoney_capital))
    if "海外" in dim_names:
        one_shot.append(("eastmoney_global", collector.fetch_eastmoney_global))
    for name, fn in one_shot:
        results = call_source(name, fn, "")
        all_news.extend(results)
        print(f"    ✅ 聚合维度 {name}: {len(results)}条")

    # 一次成功的直连源也要在"非快讯"模式下留状态记录
    if "快讯" not in dim_names:
        source_stats.setdefault("wallstreetcn_live",
                                {"status": "not_enabled", "items": 0, "calls": 0,
                                 "errors": [], "elapsed_ms": 0})

    # 去重 + 情绪
    seen = set()
    unique = []
    for item in all_news:
        h = hashlib.md5(item["title"].encode()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        sentiment, score = classify_sentiment_v2(item["title"], item.get("content", ""))
        item["sentiment"] = sentiment
        item["sentiment_score"] = score
        unique.append(item)

    unique.sort(key=lambda x: x.get("date", ""), reverse=True)

    # 情绪指数: 0-100，50=中性。按情绪分数加权（偏多计正、偏空计负）
    sentiment_index = compute_sentiment_index(unique)

    # 落盘日度情绪序列（情绪 vs 价格背离检测的数据底座）
    try:
        from fundos_config import DATA_DIR as _DD
        sdir = _DD / "sentiment_history"
        sdir.mkdir(parents=True, exist_ok=True)
        spath = sdir / f"sentiment_{datetime.now():%Y-%m-%d}.json"
        spath.write_text(json.dumps(
            {"date": datetime.now().strftime("%Y-%m-%d"),
             "saved_at": datetime.now().isoformat(timespec="seconds"),
             "dimensions": dim_names, **sentiment_index},
            ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass

    source_status = {}
    for dimension in dim_names:
        count = sum(1 for item in unique if item.get("dimension") == dimension)
        source_status[dimension] = {"status": "ok" if count else "empty", "items": count}
    enabled_sources = {s for d in dim_names for s in DIMENSIONS[d]["sources"]}
    for source in enabled_sources:
        source_status[source] = source_stats.get(source, {
            "status": "not_enabled", "items": 0, "calls": 0,
            "errors": [], "elapsed_ms": 0})
    for source, stat in source_status.items():
        if isinstance(stat, dict):
            stat["error"] = "; ".join(stat.pop("errors", []))
    return {"news": unique, "dimensions": dim_names,
            "source_status": source_status,
            "sentiment_index": sentiment_index,
            "collected_at": datetime.now().isoformat()}


# ============================================================
# 输出: 按持仓基金分组
# ============================================================
def format_by_fund(data: dict) -> str:
    news = data["news"]
    dims = data["dimensions"]

    lines = []
    lines.append("# 📰 基金持仓情报日报")
    lines.append(f"> 采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"> 维度: {' · '.join(dims)}")
    lines.append(f"> 采集条数: {len(news)}")
    lines.append("")
    lines.append("---")
    lines.append("")

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

    pos = sum(1 for n in news if "偏多" in n.get("sentiment", ""))
    neg = sum(1 for n in news if "偏空" in n.get("sentiment", ""))
    lines.append(f"## 🎯 整体情绪: 🟢{pos} · 🔴{neg} · ⚪{len(news)-pos-neg}")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 📋 按你的持仓")
    lines.append("")

    for fund_name, sectors in FUND_SECTOR_MAP.items():
        lines.append(f"### {fund_name}")
        lines.append(f"*板块: {', '.join(sectors)}*")
        lines.append("")

        fund_news = []
        seen_titles = set()
        for item in news:
            title = item.get("title", "")
            rel = 0
            for sector in sectors:
                layers = KEYWORD_LAYERS.get(sector, {})
                for level in ("core", "expand"):
                    for kw in layers.get(level, []):
                        if kw in title:
                            rel = max(rel, 3 if level == "core" else 2)
            if rel > 0 and title not in seen_titles:
                seen_titles.add(title)
                item_copy = dict(item)
                item_copy["relevance"] = rel
                fund_news.append(item_copy)

        fund_news.sort(key=lambda x: x.get("relevance", 0), reverse=True)

        if fund_news:
            fund_pos = sum(1 for n in fund_news if "偏多" in n.get("sentiment", ""))
            fund_neg = sum(1 for n in fund_news if "偏空" in n.get("sentiment", ""))
            lines.append(f"🟢{fund_pos} 🔴{fund_neg} | 共{len(fund_news)}条")
            lines.append("")
            for item in fund_news[:6]:
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

    # 六维统计
    dim_counts = {}
    for item in news:
        d = item.get("dimension", "快讯")
        dim_counts[d] = dim_counts.get(d, 0) + 1
    stat = " | ".join(f"{d}:{c}" for d, c in dim_counts.items())
    print(f"  六维分布: {stat}")
    print("-" * 70)

    for fund_name, sectors in FUND_SECTOR_MAP.items():
        print(f"\n  📌 {fund_name}  ({', '.join(sectors)})")
        fund_news = []
        seen = set()
        for item in news:
            title = item.get("title", "")
            rel = 0
            for sector in sectors:
                layers = KEYWORD_LAYERS.get(sector, {})
                for level in ("core", "expand"):
                    for kw in layers.get(level, []):
                        if kw in title:
                            rel = max(rel, 3 if level == "core" else 2)
            if rel > 0 and title not in seen:
                seen.add(title)
                item_copy = dict(item)
                item_copy["relevance"] = rel
                fund_news.append(item_copy)
        fund_news.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        count = 0
        for item in fund_news:
            if count < 4:
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
    parser = argparse.ArgumentParser(description="FundOS 六维新闻情报系统 v2.1")
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
        print("\n📡 FundOS 六维采集架构 (v2.1, 仅实测可用源):\n")
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

    dimensions = None
    if args.dimensions:
        dimensions = [d.strip() for d in args.dimensions.split(",")]

    data = collect_all(dimensions=dimensions, mode=args.mode)

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
