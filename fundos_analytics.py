#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FundOS 组合分析引擎 v1.0 — 风险/收益指标（此前引擎完全缺失的能力）

基于本地沉淀的净值历史 (data/nav_history/*.json，由 fundos_data 补拉) 计算:
  单基金:  区间收益 / 年化波动 / 最大回撤 / 夏普 / 最差单日
  组合级:  组合净值曲线 / 年化波动 / 最大回撤 / 夏普 / 基金相关性 / 风险贡献 / HHI 集中度

口径说明:
  - 夏普比率 rf=0（个人组合简化口径），252 交易日年化
  - 组合日收益 = Σ(当前权重 × 单基金日收益)，静态权重近似
  - QDII 缺失交易日按前值填充（净值滞后）
"""
import argparse
import json
import math
import sys
from datetime import datetime

from portfolio_data import load_portfolio
from fundos_config import FUND_META, ROOT, THRESHOLDS
from fundos_data import fetch_fund_nav_history, DataError

ANALYTICS_JSON = ROOT / "fund_analytics_result.json"
ANALYTICS_MD = ROOT / "fund_analytics_report.md"
TRANSACTIONS = ROOT / "transactions.json"
RF = 0.0
TRADING_DAYS = 252


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs):
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def daily_returns(navs):
    return [navs[i] / navs[i - 1] - 1 for i in range(1, len(navs))]


def max_drawdown(navs):
    """返回 (最大回撤小数, 峰值日, 谷值日)。"""
    peak, peak_i = navs[0], 0
    mdd, mdd_peak, mdd_trough = 0.0, 0, 0
    for i, v in enumerate(navs):
        if v > peak:
            peak, peak_i = v, i
        dd = v / peak - 1
        if dd < mdd:
            mdd, mdd_peak, mdd_trough = dd, peak_i, i
    return mdd, mdd_peak, mdd_trough


def corr(xs, ys):
    if len(xs) != len(ys) or len(xs) < 3:
        return 0.0
    mx, my = _mean(xs), _mean(ys)
    cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    vx, vy = sum((a - mx) ** 2 for a in xs), sum((b - my) ** 2 for b in ys)
    return cov / math.sqrt(vx * vy) if vx > 0 and vy > 0 else 0.0


def fund_metrics(dates, navs):
    rets = daily_returns(navs)
    n = len(navs)
    period_ret = navs[-1] / navs[0] - 1
    ann_ret = (1 + period_ret) ** (TRADING_DAYS / max(n - 1, 1)) - 1 if n > 2 else period_ret
    ann_vol = _std(rets) * math.sqrt(TRADING_DAYS)
    mdd, pk_i, tr_i = max_drawdown(navs)
    sharpe = (ann_ret - RF) / ann_vol if ann_vol > 0 else 0.0
    return {
        "start": dates[0], "end": dates[-1], "days": n,
        "period_ret_pct": round(period_ret * 100, 2),
        "ann_ret_pct": round(ann_ret * 100, 2),
        "ann_vol_pct": round(ann_vol * 100, 2),
        "max_dd_pct": round(mdd * 100, 2),
        "max_dd_window": f"{dates[pk_i]}→{dates[tr_i]}" if n > 2 else "-",
        "sharpe": round(sharpe, 2),
        "worst_day_pct": round(min(rets) * 100, 2) if rets else 0,
    }


def percentile(navs):
    """最新净值在窗口内的分位（0-100，越高越接近区间顶部）。"""
    if not navs:
        return 0.0
    last = navs[-1]
    below = sum(1 for v in navs if v <= last)
    return round(below / len(navs) * 100, 1)


def xirr(cashflows, lo=-0.99, hi=10.0, tol=1e-6):
    """XIRR：cashflows = [(date, amount)]，流出为负/流入为正。二分求解。"""
    from datetime import date as _date

    def npv(rate):
        def to_date(d):
            return (d if isinstance(d, _date)
                    else datetime.strptime(str(d)[:10], "%Y-%m-%d").date())
        d0 = to_date(cashflows[0][0])
        total = 0.0
        for d, amt in cashflows:
            days = to_date(d) - d0
            total += amt / (1 + rate) ** (days.days / 365.0)
        return total

    if len(cashflows) < 2:
        return None
    f_lo, f_hi = npv(lo), npv(hi)
    if f_lo * f_hi > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = npv(mid)
        if abs(f_mid) < tol:
            return round(mid * 100, 2)
        if f_lo * f_mid < 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return round(((lo + hi) / 2) * 100, 2)


def compute_xirr_from_transactions(snap):
    """从 transactions.json 重建现金流，结合当前市值算组合/单基金 XIRR。
    返回 {portfolio: pct, funds: {code: pct}, skipped: 原因}；无流水返回 None。"""
    if not TRANSACTIONS.exists():
        return None
    try:
        tx = json.loads(TRANSACTIONS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    value_by_code = {h.get("code"): float(h.get("value", 0)) for h in snap.get("holdings", [])}
    today = datetime.now().strftime("%Y-%m-%d")
    all_cf, fund_cf, skipped = [], {}, []
    for code, info in (tx.get("funds") or {}).items():
        flows = []
        for t in info.get("tx", []):
            amt = float(t.get("amount", 0))
            typ = str(t.get("type", "buy"))
            if amt == 0:
                continue
            sign = -1 if typ in ("buy", "dca") else 1  # 买入/定投=流出，卖/分红=流入
            flows.append((str(t.get("date", "")), sign * amt))
        if not flows:
            continue
        terminal = value_by_code.get(code)
        if not terminal:
            # 已清仓且无当前市值 → 无法定锚，跳过单基金但保留其历史现金流
            skipped.append(code)
            all_cf.extend(flows)
            continue
        flows.append((today, terminal))
        r = xirr(sorted(flows))
        if r is not None:
            fund_cf[code] = r
        all_cf.extend(flows)
    if not all_cf:
        return None
    r_all = xirr(sorted(all_cf))
    return {"portfolio": r_all, "funds": fund_cf,
            "note": "基于 transactions.json 快照(2026-08-08 重建)，未含其后结构调账，仅供粗略参考" if skipped or True else "",
            "skipped": skipped}


def analyze(days=120):
    snap = load_portfolio()
    holdings = snap.get("holdings", [])
    series = {}   # code -> {date: nav}
    meta = {}
    for h in holdings:
        code = h.get("code")
        if not code:
            continue
        try:
            hist = fetch_fund_nav_history(code, days=days)
        except DataError:
            hist = []
        if len(hist) >= 5:
            series[code] = {r["date"]: r["nav"] for r in hist}
            meta[code] = {
                "name": h.get("name") or FUND_META.get(code, {}).get("name", code),
                "sector": h.get("sector") or FUND_META.get(code, {}).get("sector", "other"),
                "value": float(h.get("value", 0)),
                "weight": float(h.get("weight", 0)),
            }
    result = {"generated_at": datetime.now().isoformat(timespec="seconds"),
              "window_days": days, "funds": {}, "portfolio": {},
              "data_gaps": [c for c in (h.get("code") for h in holdings)
                            if c and c not in series]}
    if not series:
        result["error"] = "无任何基金取到净值历史"
        return result

    # 对齐日期（前值填充 QDII 滞后缺口）
    all_dates = sorted(set().union(*[set(s.keys()) for s in series.values()]))
    aligned = {}
    for code, s in series.items():
        filled, last = [], None
        for d in all_dates:
            if d in s:
                last = s[d]
            if last is not None:
                filled.append(last)
        # 裁掉序列头部填充前的 None 区（最后一只是有效值）
        while filled and filled[0] == filled[1 if len(filled) > 1 else 0]:
            # 无法区分"恰好相等"与"填充"，用日期起点回退一位即可
            break
        aligned[code] = filled
    n = min(len(v) for v in aligned.values())
    common_dates = all_dates[-n:]
    aligned = {c: v[-n:] for c, v in aligned.items()}

    total_value = sum(m["value"] for m in meta.values()) or 1.0
    for code, m in meta.items():
        m["weight"] = round(m["value"] / total_value * 100, 2)
        result["funds"][code] = {**m, **fund_metrics(common_dates, aligned[code]),
                                 "nav_pct": percentile(aligned[code])}

    # ---- 组合级 ----
    port_rets = []
    for i in range(1, n):
        r = sum(m["weight"] / 100 * (aligned[c][i] / aligned[c][i - 1] - 1)
                for c, m in meta.items())
        port_rets.append(r)
    port_curve, v = [], 1.0
    for r in port_rets:
        v *= (1 + r)
        port_curve.append(v)
    ann_vol = _std(port_rets) * math.sqrt(TRADING_DAYS)
    ann_ret = (port_curve[-1] ** (TRADING_DAYS / max(len(port_rets), 1))) - 1
    mdd, pk_i, tr_i = max_drawdown(port_curve)
    port_sharpe = (ann_ret - RF) / ann_vol if ann_vol > 0 else 0
    hhi = sum((m["weight"] / 100) ** 2 for m in meta.values())
    result["portfolio"] = {
        "ann_ret_pct": round(ann_ret * 100, 2),
        "ann_vol_pct": round(ann_vol * 100, 2),
        "max_dd_pct": round(mdd * 100, 2),
        "max_dd_window": f"{common_dates[pk_i + 1]}→{common_dates[tr_i + 1]}" if len(port_rets) > 2 else "-",
        "sharpe": round(port_sharpe, 2),
        "hhi": round(hhi, 3),
        "effective_funds": round(1 / hhi, 1) if hhi > 0 else 0,
    }

    # 相关性矩阵 + 风险贡献
    rets_by_code = {c: daily_returns(v) for c, v in aligned.items()}
    contribs = []
    for c, m in meta.items():
        beta = corr(rets_by_code[c], port_rets)
        risk_contrib = m["weight"] / 100 * beta
        contribs.append({"code": c, "name": m["name"], "weight": m["weight"],
                         "corr_portfolio": round(beta, 2),
                         "risk_contrib_pct": round(risk_contrib * 100, 1)})
    result["risk_contribution"] = sorted(contribs, key=lambda x: -x["risk_contrib_pct"])

    # 两两相关性（识别"伪分散"——同涨同跌的基金簇）
    codes = list(meta.keys())
    pairs = []
    for i, a in enumerate(codes):
        for b in codes[i + 1:]:
            pairs.append({"a": meta[a]["name"], "b": meta[b]["name"],
                          "corr": round(corr(rets_by_code[a], rets_by_code[b]), 2)})
    pairs.sort(key=lambda p: -p["corr"])
    tech_codes = [c for c, m in meta.items() if m["sector"] == "tech"]
    tech_pairs = [corr(rets_by_code[a], rets_by_code[b])
                  for i, a in enumerate(codes) for b in codes[i + 1:]
                  if a in tech_codes and b in tech_codes]
    result["correlation"] = {
        "pairs": pairs,
        "top_pairs": pairs[:3],
        "bottom_pairs": pairs[-3:],
        "tech_cluster_avg": round(sum(tech_pairs) / len(tech_pairs), 2) if tech_pairs else None,
    }

    # XIRR（真实资金加权收益）
    try:
        result["xirr"] = compute_xirr_from_transactions(snap)
    except Exception:
        result["xirr"] = None
    return result


def write_report(result):
    lines = [
        "# FundOS 组合风险分析报告",
        f"> 生成时间: {result['generated_at']} | 观察窗口: 近{result['window_days']}天"
        f"（夏普 rf=0，{TRADING_DAYS}日年化；组合为静态权重近似）",
        "",
        "## 一、组合级指标",
        "",
    ]
    p = result.get("portfolio", {})
    if p:
        lines += [
            f"- 年化收益(区间折算): **{p['ann_ret_pct']:+.2f}%** | 年化波动: **{p['ann_vol_pct']:.2f}%**",
            f"- 最大回撤: **{p['max_dd_pct']:.2f}%** ({p['max_dd_window']})",
            f"- 夏普比率: **{p['sharpe']:.2f}** | HHI 集中度: **{p['hhi']:.3f}**（有效基金数 ~{p['effective_funds']} 只）",
            "",
            "> 组合最大回撤 > 15% 或夏普 < 0，通常说明仓位结构（而非选基）是主要矛盾。",
            "",
        ]
    lines += ["## 二、单基金指标", "",
              "| 基金 | 区间收益 | 年化收益 | 年化波动 | 最大回撤 | 夏普 | 最差单日 | 权重 | 净值分位 |",
              "|---|---|---|---|---|---|---|---|---|"]
    for code, f in sorted(result["funds"].items(), key=lambda kv: -kv[1]["weight"]):
        lines.append(f"| {f['name']} | {f['period_ret_pct']:+.1f}% | {f['ann_ret_pct']:+.1f}% | "
                     f"{f['ann_vol_pct']:.1f}% | {f['max_dd_pct']:.1f}% | {f['sharpe']:.2f} | "
                     f"{f['worst_day_pct']:+.1f}% | {f['weight']:.1f}% | {f.get('nav_pct', 0):.0f}% |")
    lines += ["", "> 净值分位 = 当前净值在观察窗口的位置（0%谷底 / 100%区间顶），>80% 提示短期拥挤，<20% 提示相对低位。"]

    c = result.get("correlation", {})
    if c.get("pairs"):
        lines += ["", "## 三、两两相关性（识别伪分散）", ""]
        top = c.get("top_pairs", [])
        bot = c.get("bottom_pairs", [])
        if top:
            lines.append("- 同涨同跌最明显: " + " | ".join(
                f"{p['a']}×{p['b']} {p['corr']:+.2f}" for p in top))
        if bot:
            lines.append("- 分散效果最好: " + " | ".join(
                f"{p['a']}×{p['b']} {p['corr']:+.2f}" for p in bot))
        if c.get("tech_cluster_avg") is not None:
            lines.append(f"- 科技内部平均相关性: **{c['tech_cluster_avg']:+.2f}**"
                         f"（>0.85 说明科技持仓本质上是同一笔敞口，集中度风险需按整体计）")
        x = result.get("xirr")
        if x and x.get("portfolio") is not None:
            lines += ["", "## 四、XIRR 资金加权收益", ""]
            lines.append(f"- 组合 XIRR: **{x['portfolio']:+.2f}%/年**（{x.get('note', '')}）")
            lines.append("- 单基金 XIRR 含结构调账误差，明细见 fund_analytics_result.json")
        lines += ["", "## 五、风险贡献（权重 × 与组合相关性）", ""]
    for r in result.get("risk_contribution", []):
        bar = "█" * max(1, int(r["risk_contrib_pct"]))
        lines.append(f"- {r['name']:<8s} 权重{r['weight']:5.1f}% × 相关{r['corr_portfolio']:+.2f}"
                     f" → 风险贡献 {r['risk_contrib_pct']:5.1f}%  {bar}")
    if result.get("data_gaps"):
        lines += ["", f"> ⚠️ 未取得净值历史（数据缺口）: {', '.join(result['data_gaps'])}"]
    lines += ["", "---", "",
              "> 本报告为统计计算与客观观察，不构成投资建议。基金有风险，决策请独立判断。"]
    ANALYTICS_MD.write_text("\n".join(lines), encoding="utf-8")
    ANALYTICS_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    return ANALYTICS_MD


def main():
    parser = argparse.ArgumentParser(description="FundOS 组合风险分析")
    parser.add_argument("--days", type=int, default=120)
    parser.add_argument("--json", action="store_true", help="仅输出JSON")
    args = parser.parse_args()
    try:
        result = analyze(days=args.days)
    except DataError as exc:
        print(f"❌ 数据层不可用: {exc}", file=sys.stderr)
        return 1
    if result.get("error"):
        print(f"❌ {result['error']}", file=sys.stderr)
        return 2
    write_report(result)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(ANALYTICS_MD.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
