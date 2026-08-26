#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request, json, re, sys, os, time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://finance.eastmoney.com/",
}

results = []

# 1. EastMoney 要闻
try:
    url = "https://finance.eastmoney.com/a/czqyw.html"
    req = urllib.request.Request(url, headers=H)
    resp = urllib.request.urlopen(req, timeout=10).read()
    text = resp.decode("gbk", errors="replace")
    
    # Find news list - look for <p class="title"> or similar
    items = re.findall(r'<p[^>]*class="title"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', text, re.DOTALL)
    if not items:
        items = re.findall(r'<a[^>]*href="(/a/[^"]+)"[^>]*>(.*?)</a>', text)
    
    for href, title in items[:15]:
        clean = re.sub(r'<[^>]+>', '', title).strip()
        if len(clean) > 6:
            url_full = href if href.startswith("http") else f"https://finance.eastmoney.com{href}"
            results.append({"source": "东方财富要闻", "title": clean, "url": url_full})
except Exception as e:
    results.append({"source": "ERROR", "title": f"EM: {str(e)[:60]}", "url": ""})

# 2. CLS 财联社电报
try:
    url = "https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6"
    req = urllib.request.Request(url, headers={**H, "Referer": "https://www.cls.cn/"})
    resp = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
    data = json.loads(resp)
    # Try to find articles
    if isinstance(data, dict):
        for k, v in list(data.items())[:3]:
            if isinstance(v, list):
                for item in v[:5]:
                    if isinstance(item, dict):
                        title = item.get("title", "") or item.get("content", "") or ""
                        if title and len(title) > 5:
                            results.append({"source": "财联社", "title": title[:100], "url": ""})
except:
    pass

# 3. WallStreetCN 华尔街见闻
try:
    url = "https://api-one.wallstcn.com/apiv1/content/lives?channel=global-channel&limit=10"
    req = urllib.request.Request(url, headers={**H, "Referer": "https://wallstreetcn.com/"})
    resp = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
    data = json.loads(resp)
    items = data.get("data", {}).get("items", [])
    for item in items[:10]:
        title = item.get("title", "") or item.get("content_text", "")
        if title and len(title) > 5:
            results.append({"source": "华尔街见闻", "title": title[:100], "url": ""})
except:
    pass

# Print results
print(f"=== FundOS 周末情报 | {datetime.now().strftime('%m-%d %H:%M')} ===")
print(f"共采集: {len(results)}条\n")

if results:
    for i, r in enumerate(results[:30]):
        src = r["source"]
        title = r["title"]
        print(f"  [{src}] {title}")
        if r["url"]:
            print(f"         {r['url']}")
        print()
else:
    print("  (网络受限，未能获取新闻)")
    print("  建议: 在浏览器中查看以下网站")
    print("    - https://finance.eastmoney.com/")
    print("    - https://www.cls.cn/")
    print("    - https://wallstreetcn.com/")

# Save to file
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weekend_news.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n已保存: {out_path}")
