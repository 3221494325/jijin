import json
from pathlib import Path

# 用户最新持仓 (2026-08-08 提供, 市值+收益率反推成本)
holdings = [
    {"name": "华夏绿电",  "code": "018735", "value": 455.75, "ret_pct": -5.05},
    {"name": "全球成长",  "code": "018354", "value": 315.33, "ret_pct": -19.15},
    {"name": "标普500",   "code": "017641", "value": 732.14, "ret_pct": 1.69},
    {"name": "纳斯达克100","code": "019173", "value": 411.67, "ret_pct": -1.98},
    {"name": "半导体",    "code": "020684", "value": 221.15, "ret_pct": -0.82},
    {"name": "科创50联接", "code": "011608", "value": 364.55, "ret_pct": -4.67},
    {"name": "科技智选",  "code": "022365", "value": 629.03, "ret_pct": -0.71},
    {"name": "信息产业",  "code": "019024", "value": 578.68, "ret_pct": 4.38},
]

for h in holdings:
    h["cost"] = round(h["value"] / (1 + h["ret_pct"]/100), 2)
    h["return"] = round(h["value"] - h["cost"], 2)

total_value = sum(h["value"] for h in holdings)
total_cost = sum(h["cost"] for h in holdings)
total_return = total_value - total_cost
total_ret_pct = total_return / total_cost * 100

for h in holdings:
    h["weight"] = round(h["value"] / total_value * 100, 1)

data = {
    "date": "2026-08-08",
    "holdings": holdings,
    "total_value": round(total_value, 2),
    "total_cost": round(total_cost, 2),
    "total_return": round(total_return, 2),
    "total_ret_pct": round(total_ret_pct, 2),
}

Path(r"D:\基金项目\portfolio_snapshot.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"总市值: {total_value:.2f} | 总成本: {total_cost:.2f} | 总收益: {total_return:.2f} ({total_ret_pct:+.2f}%)")
print()
for h in holdings:
    emoji = "🟢" if h["ret_pct"] > 0 else "🔴"
    print(f"{emoji} {h['name']:8s} 市值{h['value']:>7.2f} 成本{h['cost']:>7.2f} 盈亏{h['return']:>7.2f} ({h['ret_pct']:+.2f}%) 占比{h['weight']}%")
