#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FundOS 新闻采集引擎 v3.1 — 双源采集 + 全球指数 + 持仓关联
"""
import urllib.request, json, re, sys, os, time
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(r"D:\基金项目")
CACHE_FILE = OUTPUT_DIR / "news_cache.json"
REPORT_FILE = OUTPUT_DIR / "daily_briefing.md"

H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 关键词
HOLDINGS_KEYWORDS = {
    "半导体": ["半导体", "芯片", "光刻机", "晶圆", "HBM", "先进封装", "EDA", "中芯", "台积电", "GPU", "存储芯片", "集成电路", "英伟达", "NVIDIA"],
    "AI科技":   ["AI", "人工智能", "大模型", "ChatGPT", "DeepSeek", "算力", "机器人", "自动驾驶", "AI Agent", "具身智能", "OpenAI"],
    "科创50":   ["科创50", "科创板", "硬科技", "688", "科技创新"],
    "绿色电力": ["绿电", "光伏", "风电", "储能", "碳中和", "电力改革", "特高压", "虚拟电厂", "新型电力系统", "碳交易", "新能源"],
    "美股科技": ["纳斯达克", "标普500", "美股", "科技股", "苹果", "微软", "谷歌", "亚马逊", "Meta", "特斯拉", "七巨头"],
    "全球宏观": ["美联储", "利率", "CPI", "非农", "PMI", "GDP", "美元", "人民币", "通胀", "加息", "降息", "关税", "中美", "央行"],
    "资金流向": ["北向资金", "主力资金", "外资", "ETF", "龙虎榜", "融资融券"],
}

ALL_KEYWORDS = list(set(kw for kws in HOLDINGS_KEYWORDS.values() for kw in kws))

POSITIVE = ["利好", "大涨", "突破", "创新高", "增长", "盈利", "超预期", "上升", "反弹", "获批", "落地", "支持", "补贴", "回暖", "放量", "涨停"]
NEGATIVE = ["利空", "大跌", "暴跌", "下滑", "亏损", "不及预期", "下降", "制裁", "限制", "调查", "警告", "风险", "危机", "衰退", "违约", "跌停"]


def fetch_wallstreetcn(channel="global", limit=15):
    results = []
    try:
        url = f"https://api-one.wallstcn.com/apiv1/content/lives?channel={channel}-channel&limit={limit}"
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
        data = json.loads(resp)
        for item in data.get("data", {}).get("items", []):
            text = (item.get("title") or item.get("content_text") or "").strip()
            if len(text) > 10:
                results.append({"source": f"见闻·{channel}", "title": text, "time": item.get("display_time", "")})
    except:
        pass
    return results


def fetch_sina_news(limit=20):
    results = []
    try:
        url = f"https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num={limit}&page=1"
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
        data = json.loads(resp)
        for item in data.get("result", {}).get("data", []):
            title = item.get("title", "")
            if len(title) > 10:
                results.append({
                    "source": "新浪财经",
                    "title": title.strip(),
                    "time": datetime.fromtimestamp(int(item.get("ctime", 0))).strftime("%m-%d %H:%M") if item.get("ctime") else "",
                    "intro": (item.get("intro") or "")[:100],
                })
    except:
        pass
    return results


def fetch_global_indices():
    """新浪全球指数"""
    indices = []
    try:
        codes = "gb_$dji,gb_$ixic,gb_$inx,gb_hsi,gb_$n225"
        url = f"https://hq.sinajs.cn/list={codes}"
        req = urllib.request.Request(url, headers={**H, "Referer": "https://finance.sina.com.cn/"})
        resp = urllib.request.urlopen(req, timeout=10).read().decode("gbk", errors="replace")
        name_map = {
            "gb_$dji": "道琼斯", "gb_$ixic": "纳斯达克", "gb_$inx": "标普500",
            "gb_hsi": "恒生指数", "gb_$n225": "日经225",
        }
        for line in resp.strip().split("\n"):
            parts = line.split('"')
            if len(parts) >= 2:
                code = line.split("var hq_str_")[1].split("=")[0]
                data = parts[1].split(",")
                if len(data) > 2 and data[1]:
                    name = name_map.get(code, code.split("_")[-1])
                    price = float(data[1])
                    chg_pct = float(data[2]) if data[2] and data[2] != "" else 0
                    indices.append({"name": name, "price": price, "chg_pct": chg_pct})
    except:
        pass
    
    # A-share indices
    try:
        url = "https://hq.sinajs.cn/list=sh000001,sz399006,sh000688,sh000300"
        req = urllib.request.Request(url, headers={**H, "Referer": "https://finance.sina.com.cn/"})
        resp = urllib.request.urlopen(req, timeout=10).read().decode("gbk", errors="replace")
        a_map = {"sh000001": "上证指数", "sz399006": "创业板指", "sh000688": "科创50", "sh000300": "沪深300"}
        for line in resp.strip().split("\n"):
            parts = line.split('"')
            if len(parts) >= 2:
                code = line.split("var hq_str_")[1].split("=")[0]
                data = parts[1].split(",")
                if len(data) > 3 and data[3]:
                    name = a_map.get(code, code)
                    price = float(data[3])
                    prev = float(data[2])
                    chg_pct = (price - prev) / prev * 100 if prev else 0
                    indices.append({"name": name, "price": price, "chg_pct": chg_pct})
    except:
        pass
    
    return indices


def score_relevance(title, keywords):
    score = 0
    for kw in keywords:
        if kw.lower() in title.lower():
            score += (2 if len(kw) >= 4 else 1)
    return min(score, 5)


def detect_sentiment(title):
    pos = sum(1 for w in POSITIVE if w in title)
    neg = sum(1 for w in NEGATIVE if w in title)
    return "🟢" if pos > neg else ("🔴" if neg > pos else "⚪")


def run():
    print("📡 正在采集...", end=" ", flush=True)
    
    all_news = []
    all_news.extend(fetch_wallstreetcn("global", 15))
    all_news.extend(fetch_wallstreetcn("a-stock", 15))
    all_news.extend(fetch_sina_news(20))
    
    # 去重
    seen = set()
    unique = []
    for n in all_news:
        key = n["title"][:50]
        if key not in seen:
            seen.add(key)
            unique.append(n)
    
    for n in unique:
        n["relevance"] = score_relevance(n["title"], ALL_KEYWORDS)
        n["sentiment"] = detect_sentiment(n["title"])
    
    unique.sort(key=lambda x: (-x["relevance"], x["title"]))
    
    indices = fetch_global_indices()
    print(f"✅ {len(unique)}条新闻 + {len(indices)}个指数")
    
    # === OUTPUT ===
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    high = [n for n in unique if n["relevance"] >= 3]
    mid = [n for n in unique if 1 <= n["relevance"] < 3]
    low = [n for n in unique if n["relevance"] == 0]
    pos = sum(1 for n in unique if n["sentiment"] == "🟢")
    neg = sum(1 for n in unique if n["sentiment"] == "🔴")
    
    lines = []
    lines.append("=" * 70)
    lines.append(f"  📰 FundOS 情报日报 | {now}")
    lines.append("=" * 70)
    
    if indices:
        lines.append("")
        lines.append("  🌍 全球指数:")
        for idx in indices:
            d = "🟢" if idx["chg_pct"] > 0 else ("🔴" if idx["chg_pct"] < 0 else "⚪")
            lines.append(f"     {d} {idx['name']:6s}: {idx['price']:>10.2f}  ({idx['chg_pct']:+.2f}%)")
    
    lines.append("")
    lines.append(f"  📊 {len(unique)}条 | ⭐高关联:{len(high)} | 🔶中:{len(mid)} | 情绪 🟢{pos} 🔴{neg}")
    lines.append("-" * 70)
    
    if high:
        lines.append("")
        lines.append("  ⭐ 高关联 (直接影响持仓):")
        for n in high[:10]:
            lines.append(f"     {n['sentiment']} [{n['source']}] {n['title'][:95]}")
            if n.get("intro"):
                lines.append(f"        {n['intro']}")
    
    if mid:
        lines.append("")
        lines.append("  🔶 中关联:")
        for n in mid[:8]:
            lines.append(f"     {n['sentiment']} [{n['source']}] {n['title'][:95]}")
    
    lines.append("")
    lines.append("-" * 70)
    lines.append("  📌 客观新闻汇总，不构成投资建议")
    lines.append("=" * 70)
    
    report = "\n".join(lines)
    print("\n" + report)
    
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"\n  💾 {REPORT_FILE}")
    
    # Cache
    cache = {
        "updated": now, "count": len(unique),
        "high": [{"s": n["source"], "t": n["title"], "r": n["relevance"], "x": n["sentiment"]} for n in high],
        "mid": [{"s": n["source"], "t": n["title"], "r": n["relevance"], "x": n["sentiment"]} for n in mid],
        "indices": indices,
    }
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    
    return report


if __name__ == "__main__":
    run()
