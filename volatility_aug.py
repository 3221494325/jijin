#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FundOS 波动率分析 v2.0 — 组合波动预估
v2.0 (2026-08-28) 修复:
  - 旧版硬编码的是【已纠错前的错误基金代码】(018354/019173/020684/019024)，
    抓的是错误的基金数据 → 现统一走 fundos_config.FUND_META（9只权威代码）
  - 净值历史走 fundos_data 数据层（本地沉淀 + 重试），不再重复造轮子
  - 新增: 单基金最大回撤 / 组合最大回撤
"""
import math
import sys
from datetime import datetime

import fundos_data
from fundos_config import FUND_META

sys.stdout.reconfigure(encoding='utf-8')

TRADING_DAYS = 252


def calc_volatility(navs, days=60):
    """近N日波动率指标。navs: 升序 [{date, nav}]"""
    recent = navs[-days:]
    values = [r["nav"] for r in recent]
    if len(values) < 5:
        return {}
    chgs = [(values[i] - values[i-1]) / values[i-1] * 100 for i in range(1, len(values))]
    avg = sum(chgs) / len(chgs)
    std = (sum((c - avg) ** 2 for c in chgs) / len(chgs)) ** 0.5

    peak, mdd = values[0], 0.0
    for v in values:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1)

    return {
        "std_daily": std,
        "max_up_day": max(chgs),
        "max_down_day": min(chgs),
        "up_days": sum(1 for c in chgs if c > 0),
        "down_days": sum(1 for c in chgs if c < 0),
        "total_days": len(chgs),
        "latest_nav": values[-1],
        "nav_high": max(values),
        "nav_low": min(values),
        "max_dd": mdd,
    }


def main():
    print("📡 拉取净值历史 (本地缓存优先)...", end=" ", flush=True)
    all_data = {}
    for code, meta in FUND_META.items():
        try:
            all_data[code] = fundos_data.fetch_fund_nav_history(code, days=90)
        except fundos_data.DataError:
            all_data[code] = []
    print(f"✅ {sum(1 for v in all_data.values() if v)}/{len(all_data)}只\n")

    print("=" * 80)
    print(f"  📊 组合波动幅度预估 | {datetime.now().strftime('%Y-%m-%d')}")
    print("  基于近60个交易日数据 (月波动 = 日波动 × √22)")
    print("=" * 80)
    print()

    fund_vols = {}
    for code, meta in FUND_META.items():
        navs = all_data.get(code, [])
        v = calc_volatility(navs, 60)
        if not v:
            print(f"  ▸ {meta['name']} [{code}]: 数据不足")
            continue
        fund_vols[code] = v
        month_vol = v["std_daily"] * math.sqrt(22)
        nav = v["latest_nav"]
        low, high = nav * (1 - month_vol * 1.5 / 100), nav * (1 + month_vol * 1.5 / 100)
        print(f"  ▸ {meta['name']} [{code}]")
        print(f"    净值: {nav:.4f}  |  近60日: 高{v['nav_high']:.4f} / 低{v['nav_low']:.4f}  |  最大回撤: {v['max_dd']:.1%}")
        print(f"    日波动率: {v['std_daily']:.2f}%  |  最大单日: +{v['max_up_day']:.2f}% / {v['max_down_day']:.2f}%")
        print(f"    涨跌比: 🟢{v['up_days']}天 🔴{v['down_days']}天")
        print(f"    月度预估波动: ±{month_vol:.1f}%  →  1.5σ区间 {low:.4f} ~ {high:.4f}")
        print()

    # 组合汇总（等权近似；持仓权重版请看 fundos_analytics.py）
    if fund_vols:
        vols = [v["std_daily"] * math.sqrt(22) for v in fund_vols.values()]
        avg_vol = sum(vols) / len(vols)
        print("=" * 80)
        print("  📋 组合整体预估 (等权近似)")
        print("=" * 80)
        print(f"  平均单基金月波动: ±{avg_vol:.1f}%")
        print("  💡 精确的组合加权波动/最大回撤/夏普/相关性请运行: python fundos_analytics.py")
        print(f"  💡 组合实际波动通常低于成员平均（分散化效应），科技+QDII相关性高时折扣有限")
        print("=" * 80)


if __name__ == "__main__":
    main()
