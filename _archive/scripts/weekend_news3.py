import urllib.request, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Referer": "https://wallstreetcn.com/"}

results = []

# WallStreetCN - channels
channels = [
    ("global", "全球"),
    ("us-stock", "美股"),
    ("a-stock", "A股"),
]

for ch, label in channels:
    try:
        url = f"https://api-one.wallstcn.com/apiv1/content/lives?channel={ch}-channel&limit=8"
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
        data = json.loads(resp)
        items = data.get("data", {}).get("items", [])
        for item in items:
            title = item.get("title", "") or item.get("content_text", "")
            if title and len(title) > 8:
                results.append({"source": f"见闻-{label}", "title": title[:120]})
    except Exception as e:
        pass

# Print all
print(f"=== 周末财经快讯 | 共{len(results)}条 ===\n")

for r in results:
    print(f"  [{r['source']}] {r['title']}")
    print()

if not results:
    print("  (网络受限)")

# Also print a summary of what we know from Friday's session
print("=" * 60)
print("  📅 本周回顾 (7/28 - 8/1)")
print("=" * 60)
print("""
  周五(7/31)市场回顾:
  - 科创50 +2.99% | 创业板 +3.06% | A股全面反弹
  - 你的持仓8只全红, 科技智选领涨+5.32%
  - 总回血约+2.3%, 亏损收窄至-6.72%

  周末关注方向:
  - 美股周五表现 (纳斯达克/标普500期货)
  - 国内政策面 (周末可能有国务院/部委文件)
  - 半导体/AI板块消息 (影响科技智选和科创50)
  - 全球宏观 (美联储动向、中美关系)
""")
