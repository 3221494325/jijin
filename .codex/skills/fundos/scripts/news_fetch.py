#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FundOS 板块新闻采集器 v1.0
==========================
从多个公开新闻源采集与你持仓相关的板块新闻和利好利空消息。

用法:
  python news_fetch.py                          # 采集全部持仓板块
  python news_fetch.py --sector 半导体          # 指定板块
  python news_fetch.py --sectors 半导体,AI,美股 # 多板块
  python news_fetch.py --output news.json       # 导出JSON
  python news_fetch.py --format markdown         # Markdown格式输出

数据源:
  - 财联社 (cls.cn) — 实时快讯
  - 华尔街见闻 (wallstreetcn.com) — 深度分析
  - 东方财富 (eastmoney.com) — 板块新闻
  - 新浪财经 (finance.sina.com.cn) — 市场资讯
  - 百度财经 (finance.baidu.com) — 综合资讯

继承自: FundOS go-stock 源仓库的新闻采集逻辑
         (tool_cailianpress_opinion.go / tool_wallstreetcn.go / market_news_api.go)
"""

import argparse
import json
import os
import re
import sys
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import quote, urlencode

try:
    import requests
except ImportError:
    print("请先安装: pip install requests")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("提示: pip install beautifulsoup4 可获得更好的解析效果")

# ============================================================
# 配置
# ============================================================

# 用户持仓映射 → 相关板块和关键词
PORTFOLIO_SECTORS = {
    "华夏中证绿色电力ETF联接C": {
        "sectors": ["绿色电力", "新能源", "光伏", "风电", "碳中和"],
        "keywords": ["绿色电力", "新能源", "光伏", "风电", "碳中和", "电力改革"],
    },
    "易方达全球成长精选混合（QDII）C": {
        "sectors": ["QDII", "全球市场", "美股"],
        "keywords": ["全球市场", "美股", "QDII", "海外资产"],
    },
    "摩根标普500指数（QDII）A": {
        "sectors": ["标普500", "美股", "QDII"],
        "keywords": ["标普500", "S&P500", "美股", "美联储", "美国经济"],
    },
    "摩根纳斯达克100指数（QDII）A": {
        "sectors": ["纳斯达克", "美股科技", "QDII"],
        "keywords": ["纳斯达克", "NASDAQ", "科技股", "AI", "七巨头"],
    },
    "中欧半导体产业股票C": {
        "sectors": ["半导体", "芯片", "集成电路"],
        "keywords": ["半导体", "芯片", "集成电路", "光刻机", "先进封装", "晶圆"],
    },
    "易方达信息产业混合C": {
        "sectors": ["AI", "信息技术", "人工智能", "数字经济"],
        "keywords": ["人工智能", "AI", "大模型", "算力", "数字经济", "信创"],
    },
    "易方达科创50联接A": {
        "sectors": ["科创50", "科创板", "硬科技"],
        "keywords": ["科创50", "科创板", "硬科技", "专精特新"],
    },
    "永赢科技智选混合C": {
        "sectors": ["AI", "科技", "TMT"],
        "keywords": ["人工智能", "AI应用", "机器人", "自动驾驶", "科技"],
    },
}

# 默认板块 → 关键词
DEFAULT_SECTORS = {
    "半导体": ["半导体", "芯片", "集成电路", "光刻机", "先进封装"],
    "AI科技": ["人工智能", "AI", "大模型", "算力", "ChatGPT"],
    "美股": ["标普500", "纳斯达克", "美联储", "美股", "QDII"],
    "绿色电力": ["绿色电力", "新能源", "光伏", "风电", "碳中和"],
    "科创50": ["科创50", "科创板", "硬科技"],
}

NEWS_SOURCES = {
    "eastmoney": {
        "name": "东方财富",
        "search_url": "https://searchapi.eastmoney.com/bussiness/Web/GetCMSSearchResult",
        "type": "api",
        "params_template": {
            "type": "8199",
            "pageindex": 1,
            "pagesize": 10,
            "keyword": "{keyword}",
            "name": "zixun",
        },
    },
    "cls": {
        "name": "财联社",
        "url": "https://www.cls.cn/searchPage",
        "type": "web",
        "params_template": {"keyword": "{keyword}", "type": "all"},
    },
    "sina": {
        "name": "新浪财经",
        "search_url": "https://search.sina.com.cn/finance",
        "type": "web",
        "params_template": {"q": "{keyword}", "range": "all", "c": "finance"},
    },
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/json,application/xhtml+xml,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 本地缓存目录
CACHE_DIR = Path.home() / "FundOS" / "news_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cache_key(keyword: str) -> str:
    return hashlib.md5(keyword.encode()).hexdigest()[:12]


def get_cached(keyword: str, max_age_minutes: int = 30) -> Optional[list]:
    """读取本地缓存, 30分钟内的缓存有效"""
    ck = cache_key(keyword)
    cache_file = CACHE_DIR / f"{ck}.json"
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            cache_time = datetime.fromisoformat(data.get("cached_at", "2000-01-01"))
            if datetime.now() - cache_time < timedelta(minutes=max_age_minutes):
                return data.get("items", [])
        except:
            pass
    return None


def save_cache(keyword: str, items: list):
    ck = cache_key(keyword)
    cache_file = CACHE_DIR / f"{ck}.json"
    data = {"keyword": keyword, "cached_at": datetime.now().isoformat(), "items": items}
    cache_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ============================================================
# 新闻源采集器
# ============================================================

class NewsCollector:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def search_eastmoney(self, keyword: str, page_size: int = 10) -> list:
        """东方财富资讯搜索"""
        items = []
        try:
            url = "https://searchapi.eastmoney.com/bussiness/Web/GetCMSSearchResult"
            params = {
                "type": "8196",
                "pageindex": 1,
                "pagesize": page_size,
                "keyword": keyword,
                "name": "zixun",
            }
            resp = self.session.get(url, params=params, timeout=self.timeout)
            data = resp.json()
            articles = data.get("Data", [])
            for art in articles:
                title = art.get("Title", "").replace("<em>", "").replace("</em>", "")
                if not title:
                    continue
                items.append({
                    "title": title,
                    "source": "东方财富",
                    "url": art.get("Url", ""),
                    "date": art.get("Date", ""),
                    "keyword": keyword,
                })
        except Exception as e:
            pass  # 静默失败，不中断整体流程
        return items

    def search_cls(self, keyword: str) -> list:
        """财联社搜索"""
        items = []
        try:
            url = "https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6"
            params = {
                "keyword": keyword,
                "type": "telegram",  # 电报 = 快讯
                "page": 0,
                "rn": 10,
            }
            resp = self.session.get(url, params=params, timeout=self.timeout)
            data = resp.json()
            roll_data = data.get("data", {}).get("roll_data", [])
            for item in roll_data:
                items.append({
                    "title": item.get("title", ""),
                    "content": item.get("brief", "")[:200],
                    "source": "财联社",
                    "url": f"https://www.cls.cn/detail/{item.get('id', '')}",
                    "date": datetime.fromtimestamp(item.get("ctime", 0)).strftime("%m-%d %H:%M"),
                    "keyword": keyword,
                    "sentiment": self._classify_sentiment(item.get("title", "") + item.get("brief", "")),
                })
        except Exception:
            pass
        return items

    def search_sina(self, keyword: str) -> list:
        """新浪财经搜索"""
        items = []
        if not HAS_BS4:
            return items
        try:
            url = f"https://search.sina.com.cn/finance?q={quote(keyword)}&range=all&c=finance&sort=time"
            resp = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(resp.text, "html.parser")
            for box in soup.select(".box-result")[:8]:
                title_el = box.select_one("h2 a")
                if title_el:
                    items.append({
                        "title": title_el.get_text(strip=True),
                        "source": "新浪财经",
                        "url": title_el.get("href", ""),
                        "date": (box.select_one(".fgray_time") or box.select_one("span.time")).get_text(strip=True) if (box.select_one(".fgray_time") or box.select_one("span.time")) else "",
                        "keyword": keyword,
                    })
        except Exception:
            pass
        return items

    def _classify_sentiment(self, text: str) -> str:
        """简单情绪分类: positive / negative / neutral"""
        positive_words = ["利好", "大涨", "突破", "创新高", "增长", "超预期", "政策支持", "扶持",
                         "回暖", "反弹", "拉升", "走强", "领涨", "净流入", "加速"]
        negative_words = ["利空", "大跌", "暴跌", "下挫", "亏损", "不及预期", "监管", "处罚",
                         "退市", "风险", "预警", "承压", "走弱", "领跌", "净流出", "下滑"]

        pos = sum(1 for w in positive_words if w in text)
        neg = sum(1 for w in negative_words if w in text)

        if pos > neg:
            return "🟢 偏多"
        elif neg > pos:
            return "🔴 偏空"
        else:
            return "⚪ 中性"

    def collect(self, keyword: str, sources: list = None) -> list:
        """从指定或全部数据源采集"""
        if sources is None:
            sources = ["eastmoney", "cls", "sina"]

        # 先查缓存
        cached = get_cached(keyword)
        if cached:
            return cached

        all_items = []
        for src in sources:
            try:
                if src == "eastmoney":
                    items = self.search_eastmoney(keyword)
                elif src == "cls":
                    items = self.search_cls(keyword)
                elif src == "sina":
                    items = self.search_sina(keyword)
                else:
                    continue

                all_items.extend(items)
            except Exception:
                continue

        # 去重 (按title)
        seen = set()
        unique = []
        for item in all_items:
            title_hash = hashlib.md5(item["title"].encode()).hexdigest()
            if title_hash not in seen:
                seen.add(title_hash)
                unique.append(item)

        # 按日期/时间排序 (最新的在前)
        unique.sort(key=lambda x: x.get("date", ""), reverse=True)

        # 缓存
        if unique:
            save_cache(keyword, unique)

        return unique


# ============================================================
# 持仓新闻匹配
# ============================================================

def collect_for_portfolio(portfolio_data: dict = None) -> dict:
    """为你持仓的每个板块采集新闻"""
    if portfolio_data is None:
        portfolio_data = PORTFOLIO_SECTORS

    collector = NewsCollector()
    all_keywords = set()
    fund_sector_map = {}

    for fund_name, info in portfolio_data.items():
        for kw in info["keywords"]:
            all_keywords.add(kw)
            if kw not in fund_sector_map:
                fund_sector_map[kw] = []
            fund_sector_map[kw].append(fund_name)

    # 每个关键词搜一次
    results = {}
    for kw in sorted(all_keywords):
        print(f"  🔍 搜索: {kw} ...", end=" ")
        items = collector.collect(kw)
        results[kw] = items
        print(f"{len(items)}条")

    return results


# ============================================================
# 输出格式化
# ============================================================

def format_markdown(results: dict, portfolio_data: dict = None) -> str:
    """Markdown格式输出"""
    if portfolio_data is None:
        portfolio_data = PORTFOLIO_SECTORS

    lines = []
    lines.append(f"# 📰 基金持仓板块新闻简报")
    lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"> 数据源: 东方财富 + 财联社 + 新浪财经")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📊 情绪速览")
    lines.append("")
    lines.append("| 板块 | 偏多 | 偏空 | 中性 | 总条数 |")
    lines.append("|------|:----:|:----:|:----:|:------:|")

    # 按基金分组情绪统计
    for fund_name, info in portfolio_data.items():
        fund_pos = 0
        fund_neg = 0
        fund_neu = 0
        fund_total = 0
        for kw in info["keywords"]:
            for item in results.get(kw, []):
                sentiment = item.get("sentiment", "⚪ 中性")
                if "偏多" in sentiment:
                    fund_pos += 1
                elif "偏空" in sentiment:
                    fund_neg += 1
                else:
                    fund_neu += 1
                fund_total += 1
        short_name = fund_name[:20]
        lines.append(f"| {short_name} | {fund_pos} | {fund_neg} | {fund_neu} | {fund_total} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # 按基金分组展示
    for fund_name, info in portfolio_data.items():
        lines.append(f"## 📌 {fund_name}")
        lines.append(f"*相关板块: {', '.join(info['sectors'])}*")
        lines.append("")

        fund_items = []
        for kw in info["keywords"]:
            fund_items.extend(results.get(kw, []))
        # 去重
        seen = set()
        fund_items_unique = []
        for item in fund_items:
            if item["title"] not in seen:
                seen.add(item["title"])
                fund_items_unique.append(item)

        if fund_items_unique:
            for item in fund_items_unique[:8]:
                sentiment = item.get("sentiment", "")
                source = item.get("source", "")
                date = item.get("date", "")
                url = item.get("url", "")
                title = item["title"]
                content = item.get("content", "")[:100]

                if url:
                    lines.append(f"- {sentiment} [{title}]({url}) — *{source} {date}*")
                else:
                    lines.append(f"- {sentiment} {title} — *{source} {date}*")
                if content:
                    lines.append(f"  > {content}")
        else:
            lines.append("  *未找到相关新闻*")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## ⚠️ 免责声明")
    lines.append("")
    lines.append("> 本简报仅客观汇总公开新闻信息，**不构成任何投资建议**。")
    lines.append("> 新闻标题的情绪分类为关键词匹配，可能存在误判，请阅读原文自行判断。")
    lines.append("> 市场存在波动风险，投资有亏损可能，所有交易决策请自行独立判断。")
    lines.append("")
    lines.append(f"> Generated by FundOS on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return "\n".join(lines)


def format_console(results: dict, portfolio_data: dict = None):
    """控制台彩色输出"""
    if portfolio_data is None:
        portfolio_data = PORTFOLIO_SECTORS

    print("\n" + "=" * 70)
    print("  📰  基金持仓板块新闻简报")
    print("=" * 70)
    print(f"  数据源: 东方财富 + 财联社 + 新浪财经")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-" * 70)

    for fund_name, info in portfolio_data.items():
        print(f"\n  📌 {fund_name}")
        print(f"     ({', '.join(info['sectors'])})")

        fund_items = []
        for kw in info["keywords"]:
            fund_items.extend(results.get(kw, []))

        seen = set()
        count = 0
        for item in fund_items:
            if item["title"] not in seen and count < 5:
                seen.add(item["title"])
                sentiment = item.get("sentiment", "")
                source = item.get("source", "")
                print(f"    {sentiment} {item['title'][:70]}")
                print(f"       {source}  {item.get('date','')}")
                count += 1

    print("\n" + "=" * 70)
    print("  ⚠️  以上为客观新闻汇总，不构成投资建议")
    print("=" * 70)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="FundOS 板块新闻采集器 — 采集与你持仓相关的板块新闻",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python news_fetch.py                           # 采集全部持仓相关板块
  python news_fetch.py --sector 半导体           # 仅采集半导体新闻
  python news_fetch.py --sectors 半导体,AI,美股  # 采集多个板块
  python news_fetch.py --output news.md          # 输出Markdown文件
  python news_fetch.py --format markdown          # 控制台Markdown输出
  python news_fetch.py --sources eastmoney,cls   # 指定新闻源
  python news_fetch.py --clear-cache             # 清除缓存
        """,
    )
    parser.add_argument("--sector", "-s", help="单个板块名称")
    parser.add_argument("--sectors", help="逗号分隔的多板块, 如: 半导体,AI,美股")
    parser.add_argument("--output", "-o", help="输出文件路径 (.md 或 .json)")
    parser.add_argument("--format", "-f", choices=["console", "markdown", "json"], default="console", help="输出格式")
    parser.add_argument("--sources", default="eastmoney,cls,sina", help="新闻源 (逗号分隔)")
    parser.add_argument("--clear-cache", action="store_true", help="清除新闻缓存")
    parser.add_argument("--list-sectors", action="store_true", help="列出持仓对应的板块")
    args = parser.parse_args()

    # 清除缓存
    if args.clear_cache:
        import shutil
        if CACHE_DIR.exists():
            shutil.rmtree(CACHE_DIR)
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
        print("✅ 新闻缓存已清除")
        return

    # 列出板块
    if args.list_sectors:
        print("\n📋 你的持仓对应板块:")
        print("-" * 50)
        for fund, info in PORTFOLIO_SECTORS.items():
            print(f"  {fund}")
            print(f"    → {', '.join(info['sectors'])}")
        print()
        return

    # 构建搜索范围
    sources_list = [s.strip() for s in args.sources.split(",")]

    if args.sector:
        kw_map = {args.sector: [args.sector]}
        portfolio = {"手动指定板块": {"sectors": [args.sector], "keywords": [args.sector]}}
    elif args.sectors:
        sector_list = [s.strip() for s in args.sectors.split(",")]
        kw_map = {s: [s] for s in sector_list}
        portfolio = {"手动指定板块": {"sectors": sector_list, "keywords": sector_list}}
    else:
        kw_map = {}
        portfolio = PORTFOLIO_SECTORS
        for info in portfolio.values():
            for kw in info["keywords"]:
                kw_map[kw] = [kw]

    # 采集
    collector = NewsCollector()
    results = {}
    for kw in sorted(kw_map):
        print(f"  🔍 搜索: {kw} ...", end=" ", flush=True)
        items = collector.collect(kw, sources_list)
        results[kw] = items
        print(f"{len(items)}条")

    # 输出
    if args.format == "json" or (args.output and args.output.endswith(".json")):
        output = json.dumps(results, ensure_ascii=False, indent=2, default=str)
    elif args.format == "markdown" or (args.output and args.output.endswith(".md")):
        output = format_markdown(results, portfolio)
    else:
        format_console(results, portfolio)
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
