#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FundOS 组合体检引擎 (X-Ray) v1.0 — 静态规则体检

设计来源（GitHub 开源思路借鉴）:
  - Ghostfolio 的 X-Ray：把"组合是否健康"拆成一组静态规则，每条规则输出
    通过/不通过 + 当前值 vs 阈值 + 一句可执行的解读，而不是只给一个总分。
  - Portfolio Performance 的风险面板：回撤、夏普、集中度作为独立可解释指标，
    不混进收益数字里。

与 fundos_advisor 的分工:
  advisor   = 今天做什么（动作层，含触发线、分批节奏）
  xray      = 组合长什么样（结构层，通过/不通过 + 阈值校准）
两者共用 fundos_config.THRESHOLDS，避免出现两套阈值。

纯函数：所有输入可注入，无网络、无文件写入，可直接单测。
"""
from fundos_config import THRESHOLDS

# 体检阈值（结构层；与 advisor 的动作阈值分开命名，避免误改）
XRAY_DEFAULTS = {
    "single_fund_max_pct": 25.0,     # 单只基金占总市值上限
    "tech_max_pct": THRESHOLDS["tech_max"],     # 40
    "qdii_max_pct": THRESHOLDS["qdii_max"],     # 40
    "effective_funds_min": 4.0,      # 有效基金数（1/HHI）下限
    "tech_corr_max": 0.85,           # 科技簇内部平均相关上限
    "eval_line_pct": THRESHOLDS["eval_line"] * 100,   # -15
    "hard_stop_pct": THRESHOLDS["hard_stop"] * 100,   # -25
    "max_dd_abs_max_pct": 20.0,      # 组合最大回撤绝对值上限
    "sharpe_min": 0.0,               # 夏普下限（rf=0 口径）
    "snapshot_age_max_days": 7,      # 持仓快照最长可接受天数
    "estimate_ratio_max_pct": 60.0,  # 估算口径（非公布净值）占比上限
}

STATUS_LABEL = {"pass": "通过", "warn": "留意", "fail": "不通过", "na": "无数据"}


def _pct(v, digits=1):
    return f"{v:.{digits}f}%"


def _judge_max(value, limit, *, warn_ratio=0.9):
    """上限型：value 超过 limit 判 fail；超过 limit*warn_ratio 判 warn。"""
    if value is None:
        return "na"
    if value > limit:
        return "fail"
    if limit and value > limit * warn_ratio:
        return "warn"
    return "pass"


def _judge_min(value, limit, *, warn_ratio=0.9):
    """下限型：value 低于 limit 判 fail；低于 limit/warn_ratio 判 warn。"""
    if value is None:
        return "na"
    if value < limit:
        return "fail"
    if limit and value < limit / warn_ratio:
        return "warn"
    return "pass"


def _rule(key, name, category, status, *, value=None, value_text="—",
          limit=None, limit_text="—", evaluation="", action="", weight=1):
    return {"key": key, "name": name, "category": category, "status": status,
            "status_label": STATUS_LABEL.get(status, status), "weight": weight,
            "value": value, "value_text": value_text,
            "limit": limit, "limit_text": limit_text,
            "evaluation": evaluation, "action": action}


def build_xray(*, holdings=None, risk=None, correlation=None, portfolio=None,
               data_sources=None, market=None, thresholds=None, industry=None):
    """组合体检。

    holdings:    [{name, code, weight, ret_pct, today_source, ...}]
    risk:        {ann_vol_pct, max_dd_pct, sharpe, hhi, effective_funds}
    correlation: {tech_cluster_avg, matrix...}（fundos_analytics 输出）
    portfolio:   {snapshot_age_days, freshness_status, total_value, ...}
    data_sources:{portfolio/analytics/boards/news: {status}}
    market:      dashboard.market_clock() 输出（用于判断"估算"是否适用）
    industry:    [{name, yoy, trend:[{month,yoy}], related:[基金代码], month}]（同花顺 EDB 月频）
    返回 {rules, summary, score, counts}
    """
    th = {**XRAY_DEFAULTS, **(thresholds or {})}
    holdings = holdings or []
    risk = risk or {}
    correlation = correlation or {}
    portfolio = portfolio or {}
    data_sources = data_sources or {}
    market = market or {}
    industry = industry or []
    rules = []

    # ---- 1. 集中度：单一基金 ----
    if holdings:
        top = max(holdings, key=lambda h: float(h.get("weight") or 0))
        w = float(top.get("weight") or 0)
        st = _judge_max(w, th["single_fund_max_pct"])
        rules.append(_rule(
            "single_fund", "单一基金占比", "集中度", st,
            value=round(w, 1), value_text=f"{top.get('name')} {_pct(w)}",
            limit=th["single_fund_max_pct"], limit_text=f"≤ {_pct(th['single_fund_max_pct'], 0)}",
            evaluation=(f"最大单只为 {top.get('name')}（{_pct(w)}）。"
                        "单只占比过高时，这只基金的一次错误就等价于整个组合的错误。"),
            action=("无需调整；新增资金优先补给低占比品种。" if st == "pass"
                    else f"后续新增不再加仓 {top.get('name')}；用新增资金稀释占比，不做被动赎回。"),
            weight=2))
    else:
        rules.append(_rule("single_fund", "单一基金占比", "集中度", "na",
                           evaluation="无持仓数据，无法体检集中度。", weight=2))

    # ---- 2. 集中度：科技/AI 簇 ----
    tech_w = sum(float(h.get("weight") or 0) for h in holdings if h.get("sector") == "tech")
    st = _judge_max(tech_w if holdings else None, th["tech_max_pct"], warn_ratio=0.95)
    rules.append(_rule(
        "tech_cluster", "科技/AI 集中度", "集中度", st,
        value=round(tech_w, 1), value_text=_pct(tech_w),
        limit=th["tech_max_pct"], limit_text=f"≤ {_pct(th['tech_max_pct'], 0)}",
        evaluation=("科技簇内部高相关，超配等价于单因子裸露：涨时一起涨，跌时无处躲。"),
        action=("维持现状，反弹日再考虑降集中度。" if st == "pass"
                else "科技反弹日优先降集中度；新增只允许右侧确认后分批，单次≤相关仓位20%。"),
        weight=2))

    # ---- 3. 集中度：QDII 海外 ----
    qdii_w = sum(float(h.get("weight") or 0) for h in holdings if h.get("sector") == "qdii")
    st = _judge_max(qdii_w if holdings else None, th["qdii_max_pct"], warn_ratio=0.95)
    rules.append(_rule(
        "qdii_cluster", "QDII 海外敞口", "集中度", st,
        value=round(qdii_w, 1), value_text=_pct(qdii_w),
        limit=th["qdii_max_pct"], limit_text=f"≤ {_pct(th['qdii_max_pct'], 0)}",
        evaluation="海外敞口自带汇率与隔夜跳空两个额外风险源，且净值滞后1-2天。",
        action=("暂不新增 QDII；已有仓位按各自触发线管理。" if st != "pass"
                else "维持；新增海外仓位需同时确认汇率方向与溢价。"),
        weight=2))

    # ---- 4. 有效分散：有效基金数 ----
    eff = risk.get("effective_funds")
    st = _judge_min(eff, th["effective_funds_min"], warn_ratio=0.95)
    rules.append(_rule(
        "effective_funds", "有效基金数", "分散度", st,
        value=eff, value_text=(f"{eff} 只" if eff is not None else "—"),
        limit=th["effective_funds_min"], limit_text=f"≥ {th['effective_funds_min']:.0f} 只",
        evaluation=(f"HHI 集中度折算的有效基金数 {eff} 只。名字多≠分散，"
                    "同板块同风格的多只基金只算一笔敞口。" if eff is not None else "缺少风险指标。"),
        action=("分散度尚可；继续避免买入与现有持仓高相关的品种。" if st == "pass"
                else "新增资金优先投向低相关方向（非科技、非美股），而不是再买一只同类。"),
        weight=1))

    # ---- 5. 伪分散：科技簇内部相关性 ----
    tc = correlation.get("tech_cluster_avg")
    st = _judge_max(tc, th["tech_corr_max"], warn_ratio=0.95)
    rules.append(_rule(
        "tech_corr", "科技簇内部相关性", "分散度", st,
        value=tc, value_text=(f"{tc:.2f}" if tc is not None else "—"),
        limit=th["tech_corr_max"], limit_text=f"≤ {th['tech_corr_max']:.2f}",
        evaluation=("相关性 > 0.85 意味着这几只基金本质是同一笔敞口，"
                    "组合层面的“分散”只是账面上的。" if tc is not None else "样本不足，暂不判定。"),
        action=("科技持仓按整体一笔敞口管理，不要按基金只数分配风险预算。"
                if st != "pass" else "相关性可控，可继续按单只触发线管理。"),
        weight=1))

    # ---- 6. 深亏：已破 -15% 评估线 ----
    deep = [h for h in holdings if float(h.get("ret_pct") or 0) <= th["eval_line_pct"]]
    if holdings:
        st = "pass" if not deep else "fail"
        names = "、".join(f"{h.get('name')} {_pct(float(h.get('ret_pct') or 0))}" for h in deep)
        rules.append(_rule(
            "deep_loss", "深亏标的（≤-15%）", "风险", st,
            value=len(deep), value_text=(f"{len(deep)} 只" + (f"：{names}" if names else "")),
            limit=0, limit_text="0 只",
            evaluation=("已有标的跌破评估线，说明入场判断或仓位节奏需要修正，不是加仓理由。"),
            action=("无深亏标的，维持纪律。" if st == "pass"
                    else "禁止摊平；利用反弹窗口分批退出（每次≤1/3），先完成主要减仓再谈结构。"),
            weight=2))

    # ---- 7. 硬止损：已破 -25% ----
    hard = [h for h in holdings if float(h.get("ret_pct") or 0) <= th["hard_stop_pct"]]
    if holdings:
        st = "pass" if not hard else "fail"
        rules.append(_rule(
            "hard_stop", "硬止损标的（≤-25%）", "风险", st,
            value=len(hard), value_text=f"{len(hard)} 只",
            limit=0, limit_text="0 只",
            evaluation="硬止损线是账户生存线，不是谈判线；破线后每一根反弹都是减仓窗口。",
            action=("无破线标的。" if st == "pass"
                    else "当日无条件出清仍是唯一的止损纪律；分批退出不得因反弹而放宽。"),
            weight=2))

    # ---- 8. 组合回撤 ----
    dd = risk.get("max_dd_pct")
    st = _judge_max(abs(dd) if dd is not None else None, th["max_dd_abs_max_pct"], warn_ratio=0.9)
    rules.append(_rule(
        "portfolio_dd", "组合最大回撤", "风险", st,
        value=dd, value_text=(f"{dd:.1f}%" if dd is not None else "—"),
        limit=-th["max_dd_abs_max_pct"], limit_text=f"≥ -{_pct(th['max_dd_abs_max_pct'], 0)}",
        evaluation="回撤深度决定恢复所需涨幅：-20% 需要 +25% 才能回本，仓位结构比选基更关键。",
        action=("回撤在可承受区间，维持现有结构。" if st == "pass"
                else "先降集中度与深亏敞口，再考虑收益；恢复顺序是“止血→修复→进攻”。"),
        weight=2))

    # ---- 9. 夏普 ----
    sharpe = risk.get("sharpe")
    if sharpe is None:
        st = "na"
    elif sharpe < th["sharpe_min"]:
        st = "fail"
    elif sharpe < th["sharpe_min"] + 0.3:
        st = "warn"
    else:
        st = "pass"
    rules.append(_rule(
        "sharpe", "夏普比率（rf=0）", "收益质量", st,
        value=sharpe, value_text=(f"{sharpe:.2f}" if sharpe is not None else "—"),
        limit=th["sharpe_min"], limit_text="> 0",
        evaluation=("夏普为负说明这段时间承担的波动没有换来正收益，"
                    "问题在结构而非运气。" if sharpe is not None else "样本不足。"),
        action=("收益质量尚可。" if st == "pass"
                else "不要在负夏普结构上增加风险预算；先削减高波动低相关性的无效敞口。"),
        weight=1))

    # ---- 10. 持仓申报新鲜度（口径：份额/成本哪一天确认的，不是净值算到哪天） ----
    age = portfolio.get("snapshot_age_days")
    v_age = portfolio.get("valuation_age_days")
    st = _judge_max(age, th["snapshot_age_max_days"], warn_ratio=0.6) if age is not None else "na"
    if age is None:
        eval_text = "没有可用的持仓申报日期，这项不做假结论。"
    elif st == "pass":
        eval_text = "份额与成本是近期确认的，权重和收益率可以直接拿来判断。"
    else:
        eval_text = (f"份额与成本已 {age} 天未确认；期间若有申赎或换仓，权重、成本、收益率都会失真，"
                     "而净值（估值）再新也补不回来。")
        if v_age is not None and v_age <= 3:
            eval_text += f"注意区分：净值只滞后 {v_age} 天，看起来一切新鲜，问题在持仓口径。"
    rules.append(_rule(
        "data_freshness", "持仓快照新鲜度", "数据", st,
        value=age, value_text=(f"{age} 天前" if age is not None else "—"),
        limit=th["snapshot_age_max_days"], limit_text=f"≤ {th['snapshot_age_max_days']} 天",
        evaluation=eval_text,
        action=("快照可用。" if st == "pass" else
                "持仓没变就点「确认持仓未变」刷新日期；有变动则先改 portfolio_snapshot.json 再复核。"),
        weight=1))

    # ---- 11. 估算口径占比 ----
    if holdings:
        est = sum(1 for h in holdings
                  if h.get("freshness") == "估算" or (h.get("today_source") or "") not in ("", "QDII滞后"))
        ratio = est / len(holdings) * 100
        non_trading = market and not market.get("is_trading_day")
        if non_trading:
            st = "na"
        else:
            st = _judge_max(ratio, th["estimate_ratio_max_pct"], warn_ratio=0.9)
        rules.append(_rule(
            "estimate_ratio", "估算口径占比", "数据", st,
            value=round(ratio, 1), value_text=f"{est}/{len(holdings)} 只（{_pct(ratio, 0)}）",
            limit=th["estimate_ratio_max_pct"], limit_text=f"≤ {_pct(th['estimate_ratio_max_pct'], 0)}",
            evaluation=("非交易日：当日涨跌已由上一交易日已公布净值体现，估算口径不适用。"
                        if non_trading else
                        "估算值是盘中指数映射，不等于结算收益；占比越高，当日数字越不可当结论。"),
            action=("以已公布净值为准。" if non_trading else
                    ("估算比例正常。" if st == "pass" else "当日以“已公布净值”为准，估算仅用于提前预警。")),
            weight=1))

    # ---- 12. 现金弹药（诚实标注不可用） ----
    rules.append(_rule(
        "cash_reserve", "现金弹药", "流动性", "na",
        value=None, value_text="未接入",
        limit=THRESHOLDS["reserve_min_pct"], limit_text=f"≥ {THRESHOLDS['reserve_min_pct']:.0f}%",
        evaluation="当前数据层没有现金账户数据，这项不做假结论。",
        action="如需体检现金比例，需在 portfolio_snapshot.json 增加现金字段。",
        weight=1))

    # ---- 13. 产业周期背离（月频产业指标 vs 持仓权重） ----
    if holdings:
        wmap = {h.get("code"): float(h.get("weight") or 0) for h in holdings}
        stats = []
        for item in industry:
            codes = item.get("related") or []
            yoy = item.get("yoy")
            if yoy is None or not codes:
                continue
            weight = sum(wmap.get(c, 0) for c in codes)
            if weight <= 0:
                continue
            trend = [t for t in (item.get("trend") or []) if t.get("yoy") is not None]
            streak = 0
            for t in reversed(trend):
                if float(t["yoy"]) < 0:
                    streak += 1
                else:
                    break
            stats.append({"name": item.get("name"), "yoy": float(yoy), "weight": weight,
                          "streak": streak, "month": item.get("month") or ""})
        stats.sort(key=lambda s: -s["weight"])
        if not stats:
            rules.append(_rule(
                "industry_cycle", "产业周期", "基本面", "na",
                value=None, value_text="未接入产业指标",
                evaluation="没有可映射到持仓的月频产业指标，这项不做假结论。",
                action="接上同花顺 EDB 快照后自动体检（data/external/edb_snapshot.json）。",
                weight=2))
        else:
            # 不是只看最大的那一簇：同类仓位可能有多条产业线同时转弱
            dead = [s for s in stats if s["streak"] >= 3 and s["weight"] >= 20]
            soft = [s for s in stats if s["yoy"] < 0 and s["weight"] >= 20]
            if dead:
                st = "fail"
            elif soft:
                st = "warn"
            else:
                st = "pass"
            focus = (dead or soft or [stats[0]])[:2]
            names = "、".join(f"{s['name']} {s['yoy']:+.1f}%（{_pct(s['weight'])}）" for s in focus)
            exposure = (f"对应持仓合计 {_pct(focus[0]['weight'])}" if len(focus) == 1
                        else f"对应持仓 {names}")
            dead_text = "、".join(f"{s['name']}连续 {s['streak']} 月同比为负" for s in dead) or "无连续三月为负的产业线"
            rules.append(_rule(
                "industry_cycle", "产业周期", "基本面", st,
                value=round(sum(s["weight"] for s in focus), 1),
                value_text=names,
                limit=20.0, limit_text="相关持仓 ≤ 20%",
                evaluation=(f"{dead_text}；{exposure}。"
                            "产业需求端没有转正时，价格下跌是估值重定价，不是「跌出便宜」。"),
                action=("产业面与仓位匹配，可按纪律执行。" if st == "pass"
                        else f"暂停对 {'、'.join(s['name'] for s in focus)} 相关持仓加仓/摊平；"
                             "等对应指标同比连续两月收窄或转正再评估。"),
                weight=2))

    # ---- 14. 数据源可用性 ----
    bad = [k for k, v in data_sources.items() if isinstance(v, dict) and v.get("status") == "error"]
    st = "pass" if not bad else "warn"
    rules.append(_rule(
        "sources", "数据源可用性", "数据", st,
        value=len(bad), value_text=("全部可用" if not bad else f"{len(bad)} 项异常：{'、'.join(bad)}"),
        limit=0, limit_text="0 项异常",
        evaluation="单项数据源失败会让对应模块缺失，但不会伪造数字。",
        action=("数据链完整。" if not bad else "异常模块请以“无数据”对待，不要用估算代替。"),
        weight=1))

    # ---- 汇总 ----
    evaluated = [r for r in rules if r["status"] != "na"]
    weight_sum = sum(r["weight"] for r in evaluated) or 1
    earned = sum(r["weight"] * (1.0 if r["status"] == "pass" else 0.5 if r["status"] == "warn" else 0.0)
                 for r in evaluated)
    score = round(earned / weight_sum * 100)
    fails = [r["name"] for r in evaluated if r["status"] == "fail"]
    warns = [r["name"] for r in evaluated if r["status"] == "warn"]
    if not evaluated:
        grade, summary = "无法体检", "缺少持仓与风险数据，体检跳过。"
    elif not fails and not warns:
        grade, summary = "健康", f"{len(evaluated)} 项体检全部通过，按既定纪律执行即可。"
    elif not fails:
        grade, summary = "留意", f"{len(evaluated)} 项体检无硬伤，{len(warns)} 项需留意：{'、'.join(warns)}。"
    else:
        grade = "需处置" if len(fails) >= 3 else "待修复"
        summary = (f"{len(evaluated)} 项体检中 {len(fails)} 项不通过：{'、'.join(fails)}；"
                   f"{len(warns)} 项留意。优先处理不通过项，它们决定这轮亏损的下限。")

    order = {"fail": 0, "warn": 1, "na": 2, "pass": 3}
    rules.sort(key=lambda r: (order.get(r["status"], 9), -r["weight"], r["name"]))
    return {
        "score": score, "grade": grade, "summary": summary,
        "counts": {"total": len(rules), "evaluated": len(evaluated),
                   "pass": sum(1 for r in rules if r["status"] == "pass"),
                   "warn": len(warns), "fail": len(fails),
                   "na": sum(1 for r in rules if r["status"] == "na")},
        "rules": rules,
        "thresholds": th,
    }


if __name__ == "__main__":  # 手动体检：python fundos_xray.py
    import json
    from datetime import datetime
    import fundos_analytics
    import fundos_core

    snap_date, funds = fundos_core.load_snapshot()
    fundos_core.calc_portfolio(funds)
    ana = fundos_analytics.analyze(days=120)
    holdings = [{"name": f["name"], "code": f["code"], "sector": f.get("sector"),
                 "weight": f.get("weight", 0), "ret_pct": f.get("ret_pct", 0),
                 "freshness": "估算"} for f in funds]
    out = build_xray(holdings=holdings, risk=ana.get("portfolio"),
                     correlation=ana.get("correlation"),
                     portfolio={"snapshot_age_days": 0}, data_sources={})
    print(json.dumps(out, ensure_ascii=False, indent=2))
