#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FundOS Core v2.2 — 权威快照 + 手动更新融合
数据源: portfolio_snapshot.json(权威持仓) + 东方财富lsjz + 新浪指数 + 用户手动输入
"""
import urllib.request, json, io, sys, time
from datetime import datetime
from pathlib import Path
from portfolio_data import load_portfolio

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ============================================================
# CONFIG
# ============================================================
H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://fund.eastmoney.com/",
}

# 权威持仓来源（2026-08-08 纠错后快照）
SNAPSHOT = Path(r"D:\基金项目\portfolio_snapshot.json")
DAILY_RESULT = SNAPSHOT.parent / "daily_check_result.json"
MANUAL_DATA = Path(r"D:\基金项目\manual_updates.json")

# 代码 -> 元数据(类别/板块)，用于估值映射与展示（已纠错代码）
METADATA = {
    "018735": {"name": "华夏绿电",    "type": "A股ETF",   "sector": "绿色电力"},
    "012922": {"name": "全球成长",    "type": "QDII",     "sector": "全球QDII"},
    "017641": {"name": "标普500",     "type": "QDII美股", "sector": "美股指数"},
    "019172": {"name": "纳斯达克100", "type": "QDII美股", "sector": "美股科技"},
    "019764": {"name": "半导体",      "type": "A股行业",  "sector": "半导体"},
    "011608": {"name": "科创50联接",  "type": "A股指数",  "sector": "科创50"},
    "022365": {"name": "科技智选",    "type": "A股混合",  "sector": "AI科技"},
    "019018": {"name": "信息产业",    "type": "A股混合",  "sector": "TMT"},
}

INDEX_MAP = {
    "sh000001": "上证指数", "sz399001": "深证成指", "sz399006": "创业板指",
    "sh000688": "科创50",   "sh000300": "沪深300", "sh000016": "上证50",
    "sz399673": "创业板50",
}

TYPE_WEIGHTS = {
    "A股指数": 0.95, "A股ETF": 0.30, "A股行业": 0.70,
    "A股混合": 0.65, "QDII": 0.0, "QDII美股": 0.0,
}


def load_snapshot():
    """从权威快照读取持仓，返回 (快照日期, funds列表)"""
    shared = load_portfolio()
    if shared.get("data_source") == "daily_check_result.json":
        funds = []
        for item in shared["holdings"]:
            meta = METADATA.get(item["code"], {"name": item["name"], "type": "A股混合", "sector": "其他"})
            funds.append({**item, "return": item["value"] - item["cost"],
                          "type": meta["type"], "sector": meta["sector"]})
        return shared["as_of"], funds
    d = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    latest = {}
    latest_checked_at = None
    if DAILY_RESULT.exists():
        daily = json.loads(DAILY_RESULT.read_text(encoding="utf-8"))
        latest = {item.get("name"): item for item in daily.get("holdings", [])}
        latest_checked_at = daily.get("checked_at")
    funds = []
    for h in d["holdings"]:
        code = h["code"]
        meta = METADATA.get(code, {"name": h["name"], "type": "A股混合", "sector": "其他"})
        current = latest.get(h["name"], {})
        ret_pct = float(current.get("ret_pct", h["ret_pct"]))
        cost = float(h["cost"])
        value = float(current.get("value", cost * (1 + ret_pct / 100)))
        funds.append({
            "name": h["name"],
            "code": code,
            "cost": cost,
            "return": value - cost,
            "ret_pct": ret_pct,
            "value": value,
            "weight": float(current.get("weight", h.get("weight", 0))),
            "type": meta["type"],
            "sector": meta["sector"],
        })
    return (latest_checked_at or d.get("date", "unknown"), funds)


def fetch_indices():
    indices = {}
    try:
        codes = ",".join(INDEX_MAP.keys())
        url = f"https://hq.sinajs.cn/list={codes}"
        req = urllib.request.Request(url, headers={**H, "Referer": "https://finance.sina.com.cn/"})
        resp = urllib.request.urlopen(req, timeout=10).read().decode("gbk")
        for line in resp.strip().split("\n"):
            parts = line.split('"')
            if len(parts) >= 2:
                code = line.split("var hq_str_")[1].split("=")[0]
                data = parts[1].split(",")
                if len(data) > 5:
                    price, prev = float(data[3]), float(data[2])
                    indices[code] = {
                        "name": INDEX_MAP.get(code, code),
                        "price": price, "prev_close": prev,
                        "chg_pct": (price - prev) / prev * 100 if prev else 0,
                        "open": float(data[1]), "high": float(data[4]), "low": float(data[5]),
                    }
    except:
        pass
    return indices


def fetch_fund_nav(code):
    try:
        url = f"https://api.fund.eastmoney.com/f10/lsjz?callback=jQuery&fundCode={code}&pageIndex=1&pageSize=3"
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=10).read().decode("utf-8")
        clean = resp[resp.index("(") + 1 : resp.rindex(")")]
        data = json.loads(clean)
        items = data.get("Data", {}).get("LSJZList", [])
        if items:
            return {
                "date": items[0]["FSRQ"],
                "nav": float(items[0]["DWJZ"]),
                "day_chg": float(items[0].get("JZZZL", 0)),
                "history": [{"date": it["FSRQ"], "nav": float(it["DWJZ"]), "chg": float(it.get("JZZZL", 0))} for it in items],
            }
    except:
        pass
    return None


def load_manual_updates():
    if MANUAL_DATA.exists():
        d = json.loads(MANUAL_DATA.read_text(encoding="utf-8"))
        today = datetime.now().strftime("%Y-%m-%d")
        return d.get("updates", {}).get(today, {})
    return {}


def calc_portfolio(funds):
    for f in funds:
        time.sleep(0.3)
        nav = fetch_fund_nav(f["code"])
        if nav:
            f["nav"] = nav["nav"]
            f["nav_date"] = nav["date"]
            f["nav_day_chg"] = nav["day_chg"]
            f["history"] = nav["history"]
        else:
            f["nav"] = 0
            f["nav_date"] = "N/A"
            f["nav_day_chg"] = 0
        # 市值以权威快照为准，净值取不到时也不归零
        f["value"] = f.get("value") or (f["cost"] + f["return"])
        f["shares"] = f["value"] / f["nav"] if f["nav"] > 0 else 0

    total_value = 0
    for f in funds:
        total_value += f["value"]

    for f in funds:
        f["weight"] = (f["value"] / total_value * 100) if total_value > 0 else 0

    return total_value


def estimate_today(funds, indices, manual_updates):
    idx_688 = indices.get("sh000688", {})
    idx_cyb = indices.get("sz399006", {})
    today_chg_688 = idx_688.get("chg_pct", 0) if idx_688 else 0
    today_chg_cyb = idx_cyb.get("chg_pct", 0) if idx_cyb else 0

    for f in funds:
        code = f["code"]

        # 优先使用手动输入的数据
        if code in manual_updates:
            f["today_est"] = manual_updates[code]["day_change_pct"]
            f["today_source"] = "manual"
        elif f["type"].startswith("QDII"):
            f["today_est"] = 0
            f["today_source"] = "QDII滞后"
        else:
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


def print_report(funds, indices, manual_updates, snap_date):
    print()
    print("=" * 80)
    print(f"  📊 FundOS 持仓诊断报告 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  📁 数据基准: {snap_date} 持仓快照(portfolio_snapshot.json)")
    print("=" * 80)

    # Market snapshot
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

    idx_688 = indices.get("sh000688", {})
    idx_cyb = indices.get("sz399006", {})
    today_chg_688 = idx_688.get("chg_pct", 0) if idx_688 else 0
    today_chg_cyb = idx_cyb.get("chg_pct", 0) if idx_cyb else 0
    status = "🔥 全面大涨" if today_chg_688 > 3 else ("✅ 普涨" if today_chg_688 > 1 else ("➡️ 震荡" if abs(today_chg_688) < 1 else "📉 下跌"))

    manual_count = len(manual_updates)
    manual_note = f"  |  ✋ 手动更新: {manual_count}只基金" if manual_count > 0 else ""
    print(f"  📅 今日状态: {status}  |  科创50 {today_chg_688:+.2f}%  |  创业板 {today_chg_cyb:+.2f}%{manual_note}")

    # Fund table
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

    # Today estimate
    est_total_val = sum(f.get("est_value", f.get("value", 0)) for f in funds)
    est_total_ret = est_total_val - total_cost
    print(f'\n  📈 今日估算: 总市值 ¥{est_total_val:,.0f}  |  总收益 ¥{est_total_ret:+,.0f}  ({est_total_ret/total_cost*100:+.2f}%)')
    print()

    # Analysis
    print("=" * 80)
    print("  🔍 诊断分析")
    print("=" * 80)
    print()

    # Risk layers
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

    # Concentration
    print()
    print("  📋 仓位集中度:")
    for f in sorted(funds, key=lambda x: x.get("weight", 0), reverse=True):
        bar = "█" * int(f.get("weight", 0) * 2)
        print(f'     {f["name"]:10s} {f.get("weight",0):5.1f}% {bar}')

    # Sectors
    tech_sectors = ["半导体", "TMT", "科创50", "AI科技"]
    qdii_sectors = ["全球QDII", "美股指数", "美股科技"]
    green_sectors = ["绿色电力"]

    tech_w = sum(f.get("weight", 0) for f in funds if f["sector"] in tech_sectors)
    qdii_w = sum(f.get("weight", 0) for f in funds if f["sector"] in qdii_sectors)
    green_w = sum(f.get("weight", 0) for f in funds if f["sector"] in green_sectors)

    print()
    print(f"  📋 板块敞口: 科技/AI {tech_w:.0f}%  |  QDII海外 {qdii_w:.0f}%  |  绿电 {green_w:.0f}%")

    # Thresholds
    print()
    print("=" * 80)
    print("  ⚠️ 策略阈值检查")
    print("=" * 80)
    print()

    thresholds = {"loss_alert": -10.0, "single_industry_max": 40.0, "qdii_max": 50.0}

    if deep_red:
        print(f'  🚨 回撤阈值(-10%): {len(deep_red)}只触发 → {", ".join(f["name"] for f in deep_red)}')
    else:
        print(f'  ✅ 回撤阈值(-10%): 无触发 (最差: {min(f["ret_pct"] for f in funds):+.1f}%)')

    if tech_w > thresholds["single_industry_max"]:
        print(f"  🚨 行业集中度(>{thresholds['single_industry_max']}%): 科技 {tech_w:.0f}% 过高")
    else:
        print(f"  ✅ 行业集中度: 科技 {tech_w:.0f}%")

    if qdii_w > thresholds["qdii_max"]:
        print(f"  ℹ️ QDII占比(>{thresholds['qdii_max']}%): {qdii_w:.0f}%")
    else:
        print(f"  ✅ QDII占比: {qdii_w:.0f}%")

    # Per-fund observations
    print()
    print("=" * 80)
    print("  💡 观察框架 (客观数据，非操作建议)")
    print("=" * 80)
    print()

    for f in funds:
        ret_pct, est, code = f["ret_pct"], f.get("today_est", 0), f["code"]

        print(f'  ▸ {f["name"]} [{code}]')

        if ret_pct <= -20:
            print(f'     ⚠️ 严重亏损 ({ret_pct:+.1f}%)，深套区间')
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
            if est > 5:
                print(f'     ✋ 今日涨跌(手动): {est:+.2f}% — 大幅上涨')
            elif est > 2:
                print(f'     ✋ 今日涨跌(手动): {est:+.2f}% — 上涨')
            elif est > 0:
                print(f'     ✋ 今日涨跌(手动): {est:+.2f}% — 微涨')
            elif est == 0:
                print(f'     ✋ 今日涨跌(手动): {est:+.2f}% — 持平')
            else:
                print(f'     ✋ 今日涨跌(手动): {est:+.2f}% — 下跌')
        elif est > 5:
            print(f'     📈 今日预估 ~{est:+.1f}% (指数映射)')
        elif est > 2:
            print(f'     📈 今日预估 ~{est:+.1f}% (指数映射)')
        elif est > 0:
            print(f'     📈 今日预估 ~{est:+.1f}% (指数映射)')
        elif f["type"].startswith("QDII"):
            print(f'     🌍 QDII海外，净值滞后1-2天')

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
    print("  📌 投资有风险 · 决策请独立判断")
    print("=" * 80)


def main():
    print("📡 正在获取数据...")

    snap_date, funds = load_snapshot()
    print(f"  ✅ 持仓快照: {len(funds)}只 (日期 {snap_date})")

    # 1. 指数
    indices = fetch_indices()
    print(f"  ✅ 指数: {len(indices)}个")

    # 2. 净值
    total_value = calc_portfolio(funds)
    print(f"  ✅ 基金净值: {len([f for f in funds if f.get('nav',0)>0])}只取到")

    # 3. 手动更新
    manual = load_manual_updates()
    if manual:
        print(f"  ✅ 手动更新: {len(manual)}只")

    # 4. 今日估算
    estimate_today(funds, indices, manual)

    # 5. 输出
    print_report(funds, indices, manual, snap_date)


if __name__ == "__main__":
    main()
