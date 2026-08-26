import urllib.request, json, re, sys, os
sys.stdout.reconfigure(encoding='utf-8')

H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

results = []

# CLS 财联社 - 电报
try:
    url = "https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6"
    req = urllib.request.Request(url, headers={**H, "Referer": "https://www.cls.cn/telegraph"})
    resp = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
    # The data structure might be complex
    data = json.loads(resp)
    # Try to navigate to rolling news
    rolling = data.get("data", {}).get("rolling", []) or data.get("data", [])
    if isinstance(rolling, list):
        for item in rolling[:15]:
            if isinstance(item, dict):
                title = item.get("title", "") or str(item.get("content", ""))
                if len(title) > 5:
                    results.append({"source": "财联社电报", "title": title[:100]})
except Exception as e:
    results.append({"source": "财联社", "title": f"ERR: {str(e)[:60]}"})

# Try CLS depth articles
try:
    url = "https://www.cls.cn/v3/depth/home/assembled/1000"
    req = urllib.request.Request(url, headers={**H, "Referer": "https://www.cls.cn/"})
    resp = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
    data = json.loads(resp)
    articles = data.get("data", {}).get("depth_list", [])
    for a in articles[:10]:
        title = a.get("title", "") or a.get("brief", "")
        if len(title) > 5:
            results.append({"source": "财联社深度", "title": title[:100]})
except:
    pass

# EastMoney - financial news section
try:
    url = "https://finance.eastmoney.com/a/czqyw.html"
    req = urllib.request.Request(url, headers=H)
    resp = urllib.request.urlopen(req, timeout=10).read()
    text = resp.decode("gbk", errors="replace")
    # Find all article links
    links = re.findall(r'href="(/a/c[^"]+)"[^>]*>(.*?)</a>', text)
    for href, title in links[:15]:
        clean = re.sub(r'<[^>]+>', '', title).strip()
        if len(clean) > 6:
            results.append({"source": "东财要闻", "title": clean[:100]})
except:
    pass

# Try specific financial news API
try:
    # EM financial news list API
    url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns?client=web&columnId=102&pageIndex=1&pageSize=10"
    req = urllib.request.Request(url, headers={**H, "Referer": "https://finance.eastmoney.com/"})
    resp = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
    data = json.loads(resp)
    items = data.get("data", {}).get("list", [])
    for item in items:
        title = item.get("title", "")
        if len(title) > 5:
            results.append({"source": "东财快讯", "title": title[:100]})
except:
    pass

# Print
print(f"=== FundOS 周末综合情报 | 共{len(results)}条 ===\n")

# Filter for relevant keywords
relevant_kw = ["半导体", "芯片", "AI", "人工智能", "科创", "科技", "光伏", "新能源", 
               "电力", "绿电", "美股", "纳斯达克", "标普", "美联储", "利率", "关税",
               "政策", "补贴", "制裁", "华为", "算力", "大模型", "GDP", "PMI",
               "汽车", "机器人", "数据", "信创", "国产"]

for r in results:
    title = r["title"]
    # Check relevance
    is_relevant = any(kw in title for kw in relevant_kw)
    tag = "⭐" if is_relevant else "  "
    print(f"{tag} [{r['source']}] {title}")

if not results:
    print("  未获取到有效新闻")

print(f"\n⭐ = 与你的持仓相关")
