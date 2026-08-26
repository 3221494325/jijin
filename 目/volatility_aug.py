#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FundOS 波动率分析 - 八月短期波动预测"""
import urllib.request, json, re, sys, os, time
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

H = {"User-Agent": "Mozilla/5.0", "Referer": "https://fund.eastmoney.com/"}

funds = [
    ("华夏绿电", "018735", 462.19, -3.71),
    ("全球成长", "018354", 297.21, -23.79),
    ("标普500", "017641", 706.54, -1.87),
    ("纳斯达克100", "019173", 390.68, -6.98),
    ("半导体", "020684", 215.47, -3.37),
    ("信息产业", "019024", 244.41, -11.89),
    ("科创50联接", "011608", 351.56, -8.07),
    ("科技智选", "022365", 566.65, -10.56),
]

def fetch_nav_history(code):
    """获取完整净值历史"""
    try:
        url = f"https://fund.eastmoney.com/pingzhongdata/{code}.js"
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=10).read().decode("utf-8")
        m = re.search(r"var Data_netWorthTrend = (\[.+?\]);", resp, re.DOTALL)
        if m:
            data = json.loads(m.group(1))
            return [{"date": d["x"], "nav": d["y"]} for d in data if d.get("y")]
    except:
        pass
    return []

def calc_volatility(navs, days=60):
    """计算波动率指标"""
    if len(navs) < 5:
        return {}
    
    # Take last N days
    recent = navs[-days:] if len(navs) >= days else navs
    
    nav_values = [n["nav"] for n in recent]
    
    # Daily changes
    daily_chgs = []
    for i in range(1, len(nav_values)):
        chg = (nav_values[i] - nav_values[i-1]) / nav_values[i-1] * 100
        daily_chgs.append(chg)
    
    if not daily_chgs:
        return {}
    
    # Stats
    avg_chg = sum(daily_chgs) / len(daily_chgs)
    # Standard deviation
    var = sum((c - avg_chg) ** 2 for c in daily_chgs) / len(daily_chgs)
    std = var ** 0.5
    
    # Max up/down days
    max_up = max(daily_chgs)
    max_down = min(daily_chgs)
    
    # Recent monthly range (last 22 trading days)
    if len(nav_values) >= 22:
        month_navs = nav_values[-22:]
        month_high = max(month_navs)
        month_low = min(month_navs)
        month_range = (month_high - month_low) / month_low * 100
    else:
        month_high = max(nav_values)
        month_low = min(nav_values)
        month_range = (month_high - month_low) / month_low * 100
    
    # Weekly range (last 5)
    if len(nav_values) >= 5:
        week_navs = nav_values[-5:]
        week_high = max(week_navs)
        week_low = min(week_navs)
        week_range = (week_high - week_low) / week_low * 100
    else:
        week_range = 0
    
    # Up/down day ratio
    up_days = sum(1 for c in daily_chgs if c > 0)
    down_days = sum(1 for c in daily_chgs if c < 0)
    
    return {
        "std_daily": std,
        "avg_daily": avg_chg,
        "max_up_day": max_up,
        "max_down_day": max_down,
        "month_range": month_range,
        "week_range": week_range,
        "up_days": up_days,
        "down_days": down_days,
        "total_days": len(daily_chgs),
        "latest_nav": nav_values[-1],
        "nav_60d_high": max(nav_values),
        "nav_60d_low": min(nav_values),
    }

print("📡 拉取历史净值...", end=" ", flush=True)

all_data = {}
for name, code, cost, ret in funds:
    time.sleep(0.4)
    navs = fetch_nav_history(code)
    all_data[code] = navs
    print(f"{name[:2]}", end="", flush=True)

print(" ✅\n")

# ============================================================
# 计算 + 输出
# ============================================================
print("=" * 80)
print(f"  📊 八月波动幅度预估 | {datetime.now().strftime('%Y-%m-%d')}")
print(f"  基于近60个交易日数据 (约3个月)")
print("=" * 80)
print()

for name, code, cost, ret_pct in funds:
    navs = all_data[code]
    v = calc_volatility(navs, 60)
    if not v:
        print(f"  {name}: 数据不足")
        continue
    
    std = v["std_daily"]
    # 预估八月波动: 日波动 × sqrt(22) = 月波动
    month_vol = std * (22 ** 0.5)
    # 当前净值
    nav = v["latest_nav"]
    
    # 计算个人持仓的月度波动金额
    # shares = cost * (1 + ret_pct/100) / nav  approximate
    cur_value = cost * (1 + ret_pct / 100)
    shares = cur_value / nav if nav > 0 else 0
    month_amount = cur_value * month_vol / 100
    
    # August range estimate
    aug_low = nav * (1 - month_vol * 1.5 / 100)
    aug_high = nav * (1 + month_vol * 1.5 / 100)
    
    print(f"  ▸ {name} [{code}]")
    print(f"    净值: {nav:.4f}  |  近60日: 高{v['nav_60d_high']:.4f} / 低{v['nav_60d_low']:.4f}")
    print(f"    日波动率: {std:.2f}%  (1σ)")
    print(f"    最大单日涨幅: +{v['max_up_day']:.2f}%  |  最大单日跌幅: {v['max_down_day']:.2f}%")
    print(f"    涨跌比: 🟢{v['up_days']}天 🔴{v['down_days']}天")
    print(f"    近一周波动: {v['week_range']:.1f}%  |  近一月波动: {v['month_range']:.1f}%")
    print(f"    ┌─────────────────────────────────────┐")
    print(f"    │ 八月预估波动: ±{month_vol:.1f}%                   │")
    print(f"    │ 预估区间: {aug_low:.4f} ~ {aug_high:.4f}         │")
    print(f"    │ 你的持仓波动: ±¥{month_amount:.0f} (持仓¥{cur_value:.0f})     │")
    print(f"    └─────────────────────────────────────┘")
    print()

# ============================================================
# 组合汇总
# ============================================================
print("=" * 80)
print("  📋 组合整体八月预估")
print("=" * 80)
print()

total_cost = sum(f[2] for f in funds)
total_cur = sum(f[2] * (1 + f[3]/100) for f in funds)
total_ret = total_cur - total_cost

# Weighted volatility
weighted_vol = 0
for name, code, cost, ret_pct in funds:
    navs = all_data[code]
    v = calc_volatility(navs, 60)
    if v:
        cur_val = cost * (1 + ret_pct / 100)
        weight = cur_val / total_cur if total_cur > 0 else 0
        month_vol = v["std_daily"] * (22 ** 0.5)
        weighted_vol += weight * month_vol

print(f"  总持仓: ¥{total_cost:.0f} → ¥{total_cur:.0f} ({total_ret:+.0f})")
print(f"  组合加权月波动: ±{weighted_vol:.1f}%")
print(f"  八月预估波动金额: ±¥{total_cur * weighted_vol / 100:.0f}")
print()
print(f"  ┌──────────────────────────────────────────┐")
print(f"  │ 八月总资产预估区间:                       │")
print(f"  │ ¥{total_cur * (1 - weighted_vol * 1.5 / 100):.0f} ~ ¥{total_cur * (1 + weighted_vol * 1.5 / 100):.0f}                     │")
print(f"  │ (基于1.5σ，67%概率落在此区间)              │")
print(f"  └──────────────────────────────────────────┘")
print()
print(f"  💡 你的组合波动偏大 (科技42%+QDII43%)，八月日波幅1-3%正常")
print(f"  💡 科创50单日±3-5%不罕见，你的科技智选/科创联接会被带动")
print("=" * 80)
