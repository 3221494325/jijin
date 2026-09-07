#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FundOS Core v3.0 — 权威快照 + 数据层 + QDII 代理估值
数据源: portfolio_snapshot.json(权威持仓) + daily_check_result.json + 东方财富lsjz + 新浪指数

v3.0 (2026-08-28) 引擎升级:
  - 持仓元数据/阈值统一走 fundos_config（单一事实来源）
  - HTTP 重试/退避/缓存走 fundos_data（不再裸 except 吞错）
  - 修复: 按【代码】合并 daily_check_result（v2.2 按名称合并，快照全名 vs 日报短名永远合不上）
  - 并行拉取净值（原顺序 sleep 0.3s×N）
  - QDII 今日估算: 美股指数代理（标普500/纳指100，未含汇率），替代恒为 0 的旧口径
"""
import io
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import fundos_data
from fundos_config import (
    SNAPSHOT, DAILY_RESULT, MANUAL_DATA, FUND_META, get_meta,
    INDEX_MAP, TYPE_WEIGHTS, SECTOR_LABEL, THRESHOLDS,
)
from portfolio_data import load_portfolio

# pythonw 无控制台模式下 sys.stdout 为 None，直接包装会崩
if sys.stdout is not None and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

TECH_SECTORS = {"tech"}
QDII_SECTORS = {"qdii"}
GREEN_SECTORS = {"green"}


def load_snapshot():
    """从权威快照读取持仓，返回 (快照日期, funds列表)。
    daily_check_result 按【代码】合并（修 v2.2 按名称合并不上的 bug）。"""
    shared = load_portfolio()
    latest = {}
    latest_checked_at = None
    if DAILY_RESULT.exists():
        daily = json.loads(DAILY_RESULT.read_text(encoding="utf-8"))
        latest = {item.get("code"): item for item in daily.get("holdings", [])}
        latest_checked_at = daily.get("checked_at")

    funds = []
    for item in shared.get("holdings", []):
        code = item.get("code", "")
        meta = get_meta(code)
        cost = float(item.get("cost", 0) or meta.get("cost", 0))
        value = float(item.get("value", 0))
        ret_pct = float(item.get("ret_pct", 0))
        # daily_check_result 比快照新 → 用它的收益率/市值
        cur = latest.get(code)
        if cur is not None:
            ret_pct = float(cur.get("ret_pct", ret_pct))
            value = float(cur.get("value", value)) or value
        funds.append({
            "name": meta.get("name", item.get("name", code)),
            "code": code,
            "cost": cost or (value / (1 + ret_pct / 100) if ret_pct > -100 else 0),
            "value": value,
            "return": value - (cost or value / (1 + ret_pct / 100)),
            "ret_pct": ret_pct,
            "weight": float(item.get("weight", 0)),
            "type": meta.get("type", "A股混合"),
            "sector": meta.get("sector", item.get("sector", "other")),
        })
    return (latest_checked_at or shared.get("as_of", "unknown"), funds)


def fetch_indices():
    """A股指数（数据层，带重试）。失败返回空 dict，不中断诊断。"""
    try:
        return fundos_data.fetch_indices(INDEX_MAP.keys())
    except fundos_data.DataError as exc:
        print(f"  ⚠️ 指数获取失败: {exc}")
        return {}


def fetch_qdii_proxies():
    """QDII 代理指数 + 汇率因子。返回 ({指数行情}, fx_chg_pct)。"""
    codes = set()
    for meta in FUND_META.values():
        for c, _ in meta.get("proxy", []):
            codes.add(c)
    proxies = {}
    try:
        proxies = fundos_data.fetch_global_indices(sorted(codes))
    except fundos_data.DataError as exc:
        print(f"  ⚠️ QDII代理指数获取失败: {exc}")
    fx_chg = None
    try:
        fx = fundos_data.fetch_fx("fx_susdcnh")
        fx_chg = fx.get("chg_pct", 0)
        print(f"  ✅ 汇率因子: USDCNH {fx['price']:.4f} ({fx_chg:+.2f}%)")
    except fundos_data.DataError as exc:
        print(f"  ⚠️ 汇率因子获取失败: {exc}")
    return proxies, fx_chg


def _fetch_nav_safe(code):
    try:
        return code, fundos_data.fetch_fund_nav(code)
    except fundos_data.DataError as exc:
        print(f"  ⚠️ {code} 净值获取失败: {exc}")
        return code, None


def calc_portfolio(funds):
    """并行拉取全部基金最新净值并回填 shares。"""
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(_fetch_nav_safe, f["code"]) for f in funds]
        nav_by_code = {code: nav for code, nav in
                       (fu.result() for fu in as_completed(futures))}
    for f in funds:
        nav = nav_by_code.get(f["code"])
        if nav:
            f["nav"] = nav["nav"]
            f["nav_date"] = nav["date"]
            f["nav_day_chg"] = nav["day_chg"]
        else:
            f["nav"] = 0
            f["nav_date"] = "N/A"
            f["nav_day_chg"] = 0
        # 市值以权威快照为准，净值取不到时也不归零
        f["value"] = f.get("value") or (f["cost"] / (1 + f["ret_pct"] / 100)
                                        if f["ret_pct"] > -100 else 0)
        f["shares"] = f["value"] / f["nav"] if f["nav"] > 0 else 0

    total_value = sum(f["value"] for f in funds)
    for f in funds:
        f["weight"] = (f["value"] / total_value * 100) if total_value > 0 else 0
    return total_value


def estimate_today(funds, indices, qdii_proxies, manual_updates, fx_chg=None):
    """今日估算: 手动输入 > QDII美股代理(含汇率) > A股指数映射。"""
    idx_688 = indices.get("sh000688", {})
    idx_cyb = indices.get("sz399006", {})
    today_chg_688 = idx_688.get("chg_pct", 0) if idx_688 else 0
    today_chg_cyb = idx_cyb.get("chg_pct", 0) if idx_cyb else 0

    for f in funds:
        code = f["code"]
        if code in manual_updates:
            f["today_est"] = manual_updates[code]["day_change_pct"]
            f["today_source"] = "manual"
            continue

        meta = FUND_META.get(code, {})
        proxy = meta.get("proxy")
        if proxy and qdii_proxies:
            parts = [(qdii_proxies[c]["chg_pct"], w) for c, w in proxy if c in qdii_proxies]
            if parts:
                est = sum(chg * w for chg, w in parts) / sum(w for _, w in parts)
                if fx_chg is not None:
                    # 人民币贬值(USDCNH上涨)→QDII人民币净值增厚，估算叠加汇率变动
                    est += fx_chg
                    f["today_est"] = est
                    f["today_source"] = "美股代理含汇率"
                else:
                    f["today_est"] = est
                    f["today_source"] = "美股代理"
                continue

        if f["type"].startswith("QDII"):
            f["today_est"] = 0
            f["today_source"] = "QDII滞后"
            continue

        w = TYPE_WEIGHTS.get(f["type"], 0.5)
        f["today_est"] = today_chg_688 * w * 0.7 + today_chg_cyb * w * 0.3
        f["today_source"] = "指数映射"

        nav = f.get("nav", 0)
        if nav > 0 and f.get("today_est", 0) != 0:
            est_nav = nav * (1 + f["today_est"] / 100)
            f["est_nav"] = est_nav
            f["est_value"] = f.get("shares", 0) * est_nav
            f["est_return"] = f["est_value"] - f["cost"]
        else:
            f["est_nav"] = nav
            f["est_value"] = f.get("value", 0)
            f["est_return"] = f.get("return", 0)


def print_report(funds, indices, qdii_proxies, manual_updates, snap_date):
    print()
    print("=" * 80)
    print(f"  📊 FundOS 持仓诊断报告 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  📁 数据基准: {snap_date} 持仓快照(portfolio_snapshot.json)")
    print("=" * 80)

    print()
    print("  📡 市场快照:")
    if indices:
        for code, idx in sorted(indices.items()):
            emoji = "🟢" if idx["chg_pct"] > 0 else ("🔴" if idx["chg_pct"] < 0 else "⚪")
            bar_len = min(20, int(abs(idx["chg_pct"]) * 3))
            bar = "█" * bar_len
            print(f"     {emoji} {idx['name']:6s}: {idx['price']:10.2f}  ({idx['chg_pct']:+.2f}%)  {bar}")
    else:
        print("     (离线/休市：未取到实时指数，以下基于快照市值)")
    if qdii_proxies:
        for code, idx in sorted(qdii_proxies.items()):
            emoji = "🟢" if idx["chg_pct"] > 0 else ("🔴" if idx["chg_pct"] < 0 else "⚪")
            print(f"     {emoji} {idx['name']:6s}: {idx['price']:10.2f}  ({idx['chg_pct']:+.2f}%)  ← QDII代理")

    idx_688 = indices.get("sh000688", {})
    today_chg_688 = idx_688.get("chg_pct", 0) if idx_688 else 0
    status = ("🔥 全面大涨" if today_chg_688 > 3 else
              ("✅ 普涨" if today_chg_688 > 1 else
               ("➡️ 震荡" if abs(today_chg_688) < 1 else "📉 下跌")))
    manual_count = len(manual_updates)
    manual_note = f"  |  ✋ 手动更新: {manual_count}只基金" if manual_count > 0 else ""
    print(f"  📅 今日状态: {status}  |  科创50 {today_chg_688:+.2f}%{manual_note}")

    print()
    print(f"  {'基金':10s} {'成本':>7s} {'市值':>8s} {'盈亏':>8s} {'盈亏%':>7s} {'占比':>5s} {'净值日':>10s} {'前日%':>7s} {'今估%':>7s} {'来源':>6s}")
    print(f"  {'-'*10} {'-'*7} {'-'*8} {'-'*8} {'-'*7} {'-'*5} {'-'*10} {'-'*7} {'-'*7} {'-'*6}")

    total_cost = 0
    total_value = 0
    for f in funds:
        ret, ret_pct = f["return"], f["ret_pct"]
        ret_emoji = "🔴" if ret_pct < -10 else ("🟠" if ret_pct < -5 else ("🟡" if ret_pct < 0 else "🟢"))
        day_emoji = "🟢" if f.get("nav_day_chg", 0) > 0 else ("🔴" if f.get("nav_day_chg", 0) < 0 else "⚪")
        est = f.get("today_est", 0)
        today_emoji = "🟢" if est > 0 else ("🔴" if est < 0 else "⚪")
        src = f.get("today_source", "-")[:4]
        print(f'  {f["name"]:10s} {f["cost"]:>7.0f} {f.get("value",0):>8.0f} '
              f'{ret_emoji}{ret:>7.0f} {ret_pct:>+6.2f}% {f.get("weight",0):>4.1f}% '
              f'{f.get("nav_date","N/A"):>10s} {day_emoji}{f.get("nav_day_chg",0):>+6.2f}% {today_emoji}{est:>+6.2f}% {src:>6s}')
        total_cost += f["cost"]
        total_value += f.get("value", 0)

    total_return = total_value - total_cost
    total_ret_pct = total_return / total_cost * 100 if total_cost else 0
    ret_emoji = "🔴" if total_return < 0 else "🟢"
    print(f"  {'-'*10} {'-'*7} {'-'*8} {'-'*8} {'-'*7} {'-'*5} {'-'*10} {'-'*7} {'-'*7} {'-'*6}")
    print(f'  {"合计":10s} {total_cost:>7.0f} {total_value:>8.0f} '
          f'{ret_emoji}{total_return:>7.0f} {total_ret_pct:>+6.2f}% {"100":>5}%')

    est_total_val = sum(f.get("est_value", f.get("value", 0)) for f in funds)
    est_total_ret = est_total_val - total_cost
    if est_total_val:
        print(f'\n  📈 今日估算: 总市值 ¥{est_total_val:,.0f}  |  总收益 ¥{est_total_ret:+,.0f}  ({est_total_ret/total_cost*100:+.2f}%)')
    print()

    print("=" * 80)
    print("  🔍 诊断分析")
    print("=" * 80)
    print()

    deep_red = [f for f in funds if f["ret_pct"] <= -10]
    red = [f for f in funds if -10 < f["ret_pct"] <= -5]
    yellow = [f for f in funds if -5 < f["ret_pct"] <= 0]
    green = [f for f in funds if f["ret_pct"] > 0]

    print("  📋 风险分层:")
    if deep_red:
        print(f'     🔴 深度亏损(-10%+): {len(deep_red)}只 - {", ".join(f["name"] for f in deep_red)}')
    if red:
        print(f'     🟠 中度亏损(-5~-10%): {len(red)}只 - {", ".join(f["name"] for f in red)}')
    if yellow:
        print(f'     🟡 轻度亏损(0~-5%): {len(yellow)}只 - {", ".join(f["name"] for f in yellow)}')
    if green:
        print(f'     🟢 已盈利: {len(green)}只 - {", ".join(f["name"] for f in green)}')

    print()
    print("  📋 仓位集中度:")
    for f in sorted(funds, key=lambda x: x.get("weight", 0), reverse=True):
        bar = "█" * int(f.get("weight", 0) * 2)
        print(f'     {f["name"]:10s} {f.get("weight",0):5.1f}% {bar}')

    tech_w = sum(f.get("weight", 0) for f in funds if f["sector"] in TECH_SECTORS)
    qdii_w = sum(f.get("weight", 0) for f in funds if f["sector"] in QDII_SECTORS)
    green_w = sum(f.get("weight", 0) for f in funds if f["sector"] in GREEN_SECTORS)

    print()
    print(f"  📋 板块敞口: {SECTOR_LABEL['tech']} {tech_w:.0f}%  |  "
          f"{SECTOR_LABEL['qdii']} {qdii_w:.0f}%  |  {SECTOR_LABEL['green']} {green_w:.0f}%")

    print()
    print("=" * 80)
    print("  ⚠️ 策略阈值检查")
    print("=" * 80)
    print()

    if deep_red:
        print(f'  🚨 回撤阈值({THRESHOLDS["eval_line"]:.0%}): {len(deep_red)}只触发 → {", ".join(f["name"] for f in deep_red)}')
    elif funds:
        print(f'  ✅ 回撤阈值({THRESHOLDS["eval_line"]:.0%}): 无触发 (最差: {min(f["ret_pct"] for f in funds):+.1f}%)')

    if tech_w > THRESHOLDS["tech_max"]:
        print(f"  🚨 行业集中度(>{THRESHOLDS['tech_max']:.0f}%): 科技 {tech_w:.0f}% 过高")
    else:
        print(f"  ✅ 行业集中度: 科技 {tech_w:.0f}%")

    if qdii_w > THRESHOLDS["qdii_max"]:
        print(f"  ℹ️ QDII占比(>{THRESHOLDS['qdii_max']:.0f}%): {qdii_w:.0f}%")
    else:
        print(f"  ✅ QDII占比: {qdii_w:.0f}%")

    print()
    print("=" * 80)
    print("  💡 观察框架 (客观数据，非操作建议)")
    print("=" * 80)
    print()

    for f in funds:
        ret_pct, est, code = f["ret_pct"], f.get("today_est", 0), f["code"]
        print(f'  ▸ {f["name"]} [{code}]')
        if ret_pct <= -20:
            print(f'     ⚠️ 严重亏损 ({ret_pct:+.1f})%，深套区间')
        elif ret_pct <= -10:
            print(f'     🔴 大幅亏损 ({ret_pct:+.1f}%)')
        elif ret_pct <= -5:
            print(f'     🟠 中度亏损 ({ret_pct:+.1f}%)')
        elif ret_pct < 0:
            print(f'     🟡 轻微亏损 ({ret_pct:+.1f}%)')
        else:
            print(f'     🟢 盈利 ({ret_pct:+.1f}%)')

        src_label = f.get("today_source", "")
        if src_label == "manual":
            print(f'     ✋ 今日涨跌(手动): {est:+.2f}%')
        elif src_label == "美股代理含汇率":
            print(f'     🌍 今日预估 ~{est:+.1f}% (美股代理+汇率)')
        elif src_label == "美股代理":
            print(f'     🌍 今日预估 ~{est:+.1f}% (美股代理, 未含汇率)')
        elif f["type"].startswith("QDII"):
            print(f'     🌍 QDII海外，净值滞后1-2天')
        elif est != 0:
            print(f'     📈 今日预估 ~{est:+.1f}% (指数映射)')

        if ret_pct < -15 and est > 3:
            print(f'     💬 今日反弹中但仍在深亏区，关注回本节奏')
        elif ret_pct < -5 and est > 2:
            print(f'     💬 反弹中亏损收窄，关注是否突破成本线')
        elif -3 < ret_pct < 0 and est > 1:
            print(f'     💬 接近回本，今日可能翻红')
        print()

    print("-" * 80)
    print("  📌 免责声明: 以上为数据展示与策略观察，不构成投资建议")
    print("  📌 场外基金估值不等于实际净值，请以基金公司约20:00公布为准")
    print("  📌 QDII 代理估算基于美股指数，未含汇率损益与溢价折价")
    print("  📌 投资有风险 · 决策请独立判断")
    print("=" * 80)


def main():
    print("📡 正在获取数据...")

    snap_date, funds = load_snapshot()
    print(f"  ✅ 持仓快照: {len(funds)}只 (日期 {snap_date})")

    indices = fetch_indices()
    print(f"  ✅ 指数: {len(indices)}个")

    qdii_proxies, fx_chg = fetch_qdii_proxies()
    print(f"  ✅ QDII代理指数: {len(qdii_proxies)}个")

    total_value = calc_portfolio(funds)
    print(f"  ✅ 基金净值: {len([f for f in funds if f.get('nav',0)>0])}只取到 | 组合市值 ¥{total_value:,.0f}")

    manual = {}
    if MANUAL_DATA.exists():
        d = json.loads(MANUAL_DATA.read_text(encoding="utf-8"))
        manual = d.get("updates", {}).get(datetime.now().strftime("%Y-%m-%d"), {})
    if manual:
        print(f"  ✅ 手动更新: {len(manual)}只")

    estimate_today(funds, indices, qdii_proxies, manual, fx_chg)
    print_report(funds, indices, qdii_proxies, manual, snap_date)


if __name__ == "__main__":
    main()
