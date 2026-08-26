#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FundOS 深度情报 v2.0 — 三稳定源 + 东财搜索重试 + 精准利好利空分类
"""
import urllib.request, json, re, sys, time, urllib.parse
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUTPUT = Path(r"D:\基金项目\deep_news_report.md")

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 板块核心词 (用于匹配新闻是否与持仓相关)
SECTOR_TERMS = {
    "半导体": ["半导体", "芯片", "存储", "光刻", "算力", "GPU", "晶圆", "封装", "HBM", "EDA", "台积电", "中芯", "英伟达", "SK海力士", "三星电子"],
    "AI科技": ["AI", "人工智能", "大模型", "DeepSeek", "OpenAI", "ChatGPT", "机器人", "具身智能", "自动驾驶", "智能体", "AI应用", "Agent"],
    "科创50": ["科创板", "科创50", "硬科技", "国产替代", "创新药", "半导体设备"],
    "绿色电力": ["光伏", "风电", "绿电", "储能", "碳中和", "特高压", "电力", "新能源", "太阳能"],
    "美股QDII": ["美股", "纳斯达克", "标普", "道琼斯", "美联储", "降息", "加息", "通胀", "CPI", "非农", "美元"],
    "全球宏观": ["人民币", "汇率", "外资", "北向", "A股", "央行", "政策", "GDP", "PMI", "出口"],
}

# 所有相关词(用于综合判断)
ALL_TERMS = []
for terms in SECTOR_TERMS.values():
    ALL_TERMS.extend(terms)

# 利好/利空词 (强化)
POSITIVE_KW = ["利好", "大涨", "涨停", "突破", "创新高", "增长", "超预期", "盈利", "回升", "反弹",
               "获批", "落地", "支持", "补贴", "回暖", "放量", "增持", "回购", "上调", "降息",
               "融资", "扩产", "订单", "中标", "涨价", "提升", "加速", "景气", "新高", "涨超",
               "翻倍", "创新", "突破", "超18倍", "扭亏", "推荐", "看好", "增配", "流入"]
NEGATIVE_KW = ["利空", "大跌", "暴跌", "跌停", "下滑", "亏损", "不及预期", "下降", "制裁", "限制",
               "调查", "警告", "风险", "危机", "衰退", "违约", "减持", "下调", "加息", "暂停",
               "裁员", "停产", "召回", "诉讼", "处罚", "爆雷", "破发", "退市", "恶化", "蒸发",
               "黑色星期五", "同比降", "失守", "撤离", "流出", "担忧", "恐慌"]

FUND_SECTOR = [
    ("华夏绿电", ["绿色电力"]),
    ("全球成长", ["美股QDII", "全球宏观"]),
    ("标普500", ["美股QDII"]),
    ("纳斯达克100", ["美股QDII", "AI科技"]),
    ("半导体", ["半导体"]),
    ("信息产业", ["AI科技", "半导体"]),
    ("科创50联接", ["科创50", "半导体"]),
    ("科技智选", ["AI科技", "半导体"]),
]


def fetch_em_search(keyword, retries=3):
    """东财搜索 (带重试)"""
    for attempt in range(retries):
        try:
            kw = urllib.parse.quote(keyword)
            param = {
                "uid": "", "keyword": kw, "type": ["cmsArticleWebOld"],
                "client": "web", "clientVersion": "curr",
                "param": {"cmsArticleWebOld": {
                    "searchScope": "default", "sort": "time",
                    "pageIndex": 1, "pageSize": 8,
                    "preTag": "<em>", "postTag": "</em>"}}
            }
            url = "https://search-api-web.eastmoney.com/search/jsonp?cb=cb&param=" + urllib.parse.quote(json.dumps(param))
            req = urllib.request.Request(url, headers={**H, "Referer": "https://so.eastmoney.com/"})
            resp = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
            clean = resp[resp.index("(")+1:resp.rindex(")")]
            data = json.loads(clean)
            items = data.get("result", {}).get("cmsArticleWebOld", [])
            out = []
            for it in items:
                title = re.sub(r"<[^>]+>", "", it.get("title", "")).strip()
                if title:
                    out.append({"title": title, "date": it.get("date", ""), "url": it.get("url", ""), "source": "东财"})
            return out
        except Exception:
            time.sleep(2)
    return []


def fetch_ths():
    out = []
    try:
        url = "https://news.10jqka.com.cn/tapp/news/push/stock/?page=1&tag=&track=website"
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
        data = json.loads(resp)
        for it in data.get("data", {}).get("list", []):
            t = it.get("title", "").strip()
            ts = int(it.get("ctime", 0))
            if t:
                out.append({"title": t, "date": datetime.fromtimestamp(ts).strftime("%m-%d %H:%M") if ts else "", "url": "", "source": "同花顺"})
    except:
        pass
    return out


def fetch_sina():
    out = []
    try:
        url = "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=20&page=1"
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
        data = json.loads(resp)
        for it in data.get("result", {}).get("data", []):
            t = it.get("title", "").strip()
            if len(t) > 8:
                out.append({"title": t, "date": datetime.fromtimestamp(int(it.get("ctime", 0))).strftime("%m-%d %H:%M") if it.get("ctime") else "", "url": it.get("url", ""), "source": "新浪"})
    except:
        pass
    return out


def fetch_wsc(channel="global", limit=20):
    out = []
    try:
        url = f"https://api-one.wallstcn.com/apiv1/content/lives?channel={channel}-channel&limit={limit}"
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
        data = json.loads(resp)
        for it in data.get("data", {}).get("items", []):
            t = (it.get("title") or it.get("content_text") or "").strip()
            if len(t) > 10:
                out.append({"title": t, "date": "", "url": it.get("uri", ""), "source": f"见闻·{channel}"})
    except:
        pass
    return out


def classify(title):
    pos = sum(1 for w in POSITIVE_KW if w in title)
    neg = sum(1 for w in NEGATIVE_KW if w in title)
    if pos > neg:
        return "利好"
    elif neg > pos:
        return "利空"
    return "中性"


def get_sectors(title):
    """判断新闻涉及哪些板块"""
    matched = []
    for sector, terms in SECTOR_TERMS.items():
        for term in terms:
            if term.lower() in title.lower():
                matched.append(sector)
                break
    return matched


def collect():
    print("📡 深度采集...")
    all_news = []
    seen = set()

    # 1. 稳定源
    for item in fetch_ths() + fetch_sina() + fetch_wsc("global") + fetch_wsc("a-stock"):
        key = item["title"][:50]
        if key not in seen:
            seen.add(key)
            all_news.append(item)

    # 2. 东财搜索 (针对每个板块的关键词, 重试)
    search_kws = ["半导体", "芯片", "人工智能", "大模型", "光伏", "风电", "美股", "美联储", "科创板", "人民币"]
    for kw in search_kws:
        for item in fetch_em_search(kw):
            key = item["title"][:50]
            if key not in seen:
                seen.add(key)
                all_news.append(item)
        time.sleep(0.5)

    # 3. 标注板块 + 分类
    for n in all_news:
        n["sectors"] = get_sectors(n["title"])
        n["type"] = classify(n["title"])
        n["relevant"] = len(n["sectors"]) > 0

    return all_news


def build_report(all_news):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    relevant = [n for n in all_news if n["relevant"]]
    good = [n for n in relevant if n["type"] == "利好"]
    bad = [n for n in relevant if n["type"] == "利空"]
    neutral = [n for n in relevant if n["type"] == "中性"]

    lines = []
    lines.append("=" * 72)
    lines.append(f"  🧠 FundOS 深度利好利空情报 | {now}")
    lines.append("=" * 72)
    lines.append(f"  采集: {len(all_news)}条 | 持仓相关: {len(relevant)}条")
    lines.append(f"  📊 相关新闻: 🟢利好 {len(good)} | 🔴利空 {len(bad)} | ⚪中性 {len(neutral)}")
    lines.append("-" * 72)

    # 先按基金
    for fund_name, sectors in FUND_SECTOR:
        fund_news = []
        seen2 = set()
        for n in relevant:
            if n["title"][:50] in seen2:
                continue
            if any(s in n["sectors"] for s in sectors):
                seen2.add(n["title"][:50])
                fund_news.append(n)

        goods = [n for n in fund_news if n["type"] == "利好"][:4]
        bads = [n for n in fund_news if n["type"] == "利空"][:4]
        mids = [n for n in fund_news if n["type"] == "中性"][:2]

        lines.append("")
        lines.append(f"  📌 {fund_name}")
        if goods:
            for n in goods:
                lines.append(f"    🟢 [{n['source']}] {n['title'][:72]}")
        if bads:
            for n in bads:
                lines.append(f"    🔴 [{n['source']}] {n['title'][:72]}")
        if mids:
            for n in mids:
                lines.append(f"    ⚪ [{n['source']}] {n['title'][:72]}")
        if not goods and not bads and not mids:
            lines.append(f"    (无直接相关)")

    lines.append("")
    lines.append("=" * 72)
    lines.append("  📌 客观新闻分类汇总，不构成投资建议")
    lines.append("=" * 72)

    report = "\n".join(lines)
    OUTPUT.write_text(report, encoding="utf-8")
    print(report)
    print(f"\n  💾 {OUTPUT}")
    return report


if __name__ == "__main__":
    news = collect()
    build_report(news)
