#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FundOS 操作指南引擎 v1.0 — 规则化决策框架（总裁批示的机器可读版）

设计原则（persona.md / SKILL.md 约束）:
  - 每条输出必须携带【依据 / 动作 / 边界】三要素
  - 新闻与情绪只进观察层，不单独触发买卖（price-action-first）
  - 深亏禁止摊平、高分位禁止追高、集中度超限禁止新增（六条铁律 + 蒸馏技能规则）
  - 全部输出确定性可复现：同一输入必得同一输出，LLM 只做其上的叙事层

输入全部可注入 → 纯函数，可单测。
"""
from datetime import datetime, date

from fundos_config import FUND_META, THRESHOLDS, SECTOR_LABEL

HOLDING_SECTOR_TO_NEWS = {
    "tech": ["半导体", "AI科技", "科创50"],
    "qdii": ["美股"],
    "green": ["绿色电力"],
}
# 行业前瞻：持仓板块 → 新浪板块关键词（用于板块传导预警与强弱差）
HOLDING_SECTOR_TO_BOARDS = {
    "tech": ["半导体", "软件", "计算机", "电子信息", "通信", "消费电子", "芯片", "元件"],
    "green": ["光伏", "电力", "新能源", "风电", "储能", "电网"],
    "qdii": [],
}
LEVEL_ORDER = {"指令": 0, "警告": 1, "观察": 2}


def _pct(v):
    return f"{v:+.1f}%"


def build_industry_outlook(industry, held_sectors, holdings=None):
    """行业前瞻（动量事实层，非预测）。

    industry: {
      "today": [{"name","chg_pct"} 按涨幅降序, 前20],
      "days":  [[每日行业涨幅前15名单(名字列表)] 旧→新],
      "related": {板块关键词映射}（缺省用 HOLDING_SECTOR_TO_BOARDS）,
    }
    holdings: 用于计算弱势板块传导影响（可选）
    返回 {leaders, new_mains, confirmed_mains, weak_boards, strength_gap_pct, notes}
    全部为事实与预案，禁止出现预测性表述。
    """
    holdings = holdings or []
    industry = industry or {}
    related_map = industry.get("related") or HOLDING_SECTOR_TO_BOARDS
    today = industry.get("today") or []
    days = industry.get("days") or []
    if not today:
        return {"available": False, "notes": ["板块数据缺失，行业前瞻跳过"]}

    rank_now = {b["name"]: i + 1 for i, b in enumerate(today)}
    prev_names = days[-2] if len(days) >= 2 else None
    rank_prev = {n: i + 1 for i, n in enumerate(prev_names or [])}

    # 连续在榜天数（今日向前数）
    def streak(name):
        if not days:
            return 0
        s = 0
        for day in reversed(days):
            if name in day:
                s += 1
            else:
                break
        return s

    top5 = today[:5]
    leaders = [{"name": b["name"], "chg_pct": b["chg_pct"],
                "rank_now": rank_now[b["name"]],
                "rank_prev": rank_prev.get(b["name"]),
                "streak": streak(b["name"])} for b in top5]

    new_mains, confirmed_mains = [], []
    for ld in leaders:
        if ld["streak"] >= 2:
            confirmed_mains.append(f"{ld['name']}（连续{ld['streak']}天）")
        elif ld["rank_prev"] is None:
            new_mains.append(f"{ld['name']}（新进第{ld['rank_now']}名，{_pct(ld['chg_pct'])}）")
        elif ld["rank_prev"] - ld["rank_now"] >= 30:
            new_mains.append(f"{ld['name']}（第{ld['rank_prev']}→{ld['rank_now']}名，{_pct(ld['chg_pct'])}）")

    # 持仓相关板块：传导预警 + 强弱差
    all_names = [b["name"] for b in today]
    related_hits = []   # (板块, chg, 命中的持仓板块)
    seen = set()
    for hs, kws in related_map.items():
        if hs not in held_sectors:
            continue
        for kw in kws:
            for b in today:
                if kw in b["name"] and b["name"] not in seen:
                    seen.add(b["name"])
                    related_hits.append((b["name"], b["chg_pct"], hs))
    weak_boards = []
    weight_by_sector = {}
    for h in holdings:
        weight_by_sector[h.get("sector")] = weight_by_sector.get(h.get("sector"), 0) + h.get("weight", 0)
    for name, chg, hs in related_hits:
        if chg <= -1.0:
            weak_boards.append({"board": name, "chg_pct": chg,
                                "hits_sector": hs,
                                "sector_weight": round(weight_by_sector.get(hs, 0), 1)})

    strong_avg = sum(b["chg_pct"] for b in top5) / len(top5) if top5 else 0
    related_avg = (sum(c for _, c, _ in related_hits) / len(related_hits)
                   if related_hits else None)
    strength_gap_pct = (round(strong_avg - related_avg, 2)
                        if related_avg is not None else None)

    notes = []
    if new_mains:
        notes.append("新主线首日不追：等连续2日居前且持仓板块获得价格确认后再议。〔sector-rotation-detector〕")
    if confirmed_mains:
        notes.append(f"已确认主线：{'、'.join(confirmed_mains)}——按既定纪律执行，不因主线熟悉而放松分批。")
    for wb in weak_boards:
        if wb["sector_weight"] >= 5:
            notes.append(f"传导预警：{wb['board']} {_pct(wb['chg_pct'])} → 影响{'科技/AI' if wb['hits_sector']=='tech' else '绿电' if wb['hits_sector']=='green' else 'QDII'}仓"
                         f"（约{wb['sector_weight']}%）：持有不动、禁接飞刀，等净值落地再评估。〔铁律2〕")
    if strength_gap_pct is not None and strength_gap_pct > 2:
        notes.append(f"强弱差 {strength_gap_pct:+.1f}%：持仓板块弱于主线前5，风格偏移期禁新增、优先守纪律。")
    return {"available": True, "leaders": leaders, "new_mains": new_mains,
            "confirmed_mains": confirmed_mains, "weak_boards": weak_boards,
            "strength_gap_pct": strength_gap_pct, "notes": notes}


def build_guide(*, holdings, sentiment=None, nav_pct=None, indices=None,
                sector_news=None, industry=None, now=None):
    """规则引擎主入口。所有参数可注入，便于测试与复用。

    holdings:    [{name, code, ret_pct, sector, weight}]（fundos_core 口径）
    sentiment:   {index, label, up, down}（news_fetch_v2.compute_sentiment_index 口径）
    nav_pct:     {code: 净值分位0-100}
    indices:     {"sh000688": 当日涨跌%}
    sector_news: {新闻板块名: {"up": 利好条数, "down": 利空条数}}
    industry:    行业前瞻输入（见 build_industry_outlook），缺省跳过
    """
    now = now or datetime.now()
    holdings = holdings or []
    nav_pct = nav_pct or {}
    sector_news = sector_news or {}
    s_index = (sentiment or {}).get("index", 50)
    s_label = (sentiment or {}).get("label", "中性")

    tech_w = sum(h.get("weight", 0) for h in holdings if h.get("sector") == "tech")
    qdii_w = sum(h.get("weight", 0) for h in holdings if h.get("sector") == "qdii")

    # ---------- 行业前瞻（动量事实层） ----------
    held_sectors = {h.get("sector") for h in holdings}
    outlook = build_industry_outlook(industry, held_sectors, holdings)

    # ---------- 市场环境判定 ----------
    kcb = (indices or {}).get("sh000688", 0) or 0
    if s_index >= 55 and kcb > 0:
        env, env_note = "偏暖", (f"情绪指数 {s_index}（偏多{sentiment.get('up', 0)}条/利空{sentiment.get('down', 0)}条），"
                                 f"科创50 {kcb:+.2f}%。按计划执行既定分批节奏，严禁因氛围转热而加大单批比例。")
    elif s_index <= 45 and kcb < 0:
        env, env_note = "防守", (f"情绪指数 {s_index}（偏空），科创50 {kcb:+.2f}%。"
                                 "只出不进：执行触发线的减仓动作，暂停一切新增买入。")
    else:
        env, env_note = "中性", (f"情绪指数 {s_index}，科创50 {kcb:+.2f}%。"
                                 "无增量信息，严格按触发线与分批纪律执行。")

    directives = []

    def add(level, title, evidence, action, boundary, rule):
        directives.append({"level": level, "title": title, "evidence": evidence,
                           "action": action, "boundary": boundary, "rule": rule})

    add("警告" if env == "防守" else "观察", f"市场环境：{env}", env_note,
        "防守日只执行卖出触发线；偏暖日按原计划分批，不提速不加大仓位。"
        if env != "中性" else "按触发线执行，无新增动作。",
        "环境判定不构成买卖理由，仅为执行强度定档。", "环境判定引擎")

    # ---------- 集中度 ----------
    if tech_w > THRESHOLDS["tech_max"]:
        add("警告", f"科技/AI 集中度超限（{tech_w:.1f}% > {THRESHOLDS['tech_max']:.0f}%）",
            "科技簇内部平均相关>0.8，超配=单因子裸露",
            "科技反弹日优先降集中度；新增仅允许右侧确认后分批",
            f"单次调整 ≤ 相关仓位的 {THRESHOLDS['batch_max_pct']}%",
            "position-size-framework / 铁律3")
    if qdii_w > THRESHOLDS["qdii_max"]:
        add("警告", f"QDII 占比超限（{qdii_w:.1f}% > {THRESHOLDS['qdii_max']:.0f}%）",
            "海外敞口含汇率与隔夜跳空风险",
            "暂不新增 QDII；已有仓位按各自触发线管理",
            "不因超配恐慌性清仓，按线执行", "仓位经理规则")

    # ---------- 深亏（-15% 评估线） ----------
    deep = [h for h in holdings if h.get("ret_pct", 0) <= THRESHOLDS["eval_line"] * 100]
    if deep:
        add("指令", "深亏标的：止摊 + 反弹分批退出",
            "；".join(f"{h['name']} {_pct(h['ret_pct'])}" for h in deep),
            "立即停止任何摊平；利用反弹窗口分批（每次≤1/3）降低暴露",
            "不以回本为唯一卖出条件；接近 -25% 硬止损前须完成主要减仓",
            "stop-loss-admission / timely-correction / 铁律4")

    # ---------- 追高风险 ----------
    hot = [h["name"] for h in holdings if nav_pct.get(h.get("code"), 0) >= 85]
    if hot and s_index >= 55:
        add("警告", "高分位 + 偏多情绪 = 追高风险",
            f"分位≥85%：{('、'.join(hot))}；情绪指数 {s_index}",
            "严禁对这些品种新增买入；已持有者按止盈线执行",
            "错过不是亏损，追高被套才是", "铁律2 / price-action-first")

    # ---------- 行业前瞻（观察层指令：事实+预案，非预测） ----------
    if outlook.get("available"):
        if outlook.get("new_mains"):
            add("观察", "新主线出现：" + "；".join(outlook["new_mains"]),
                "板块排名跳变为动量事实，首日未获连续性确认",
                "不追新主线；与持仓相关者等价格确认，无关者仅观察",
                "连续2日居前且成交配合再议", "sector-rotation-detector / 铁律2")
        for wb in outlook.get("weak_boards", []):
            if wb.get("sector_weight", 0) >= 5:
                add("观察", f"板块传导预警：{wb['board']} {_pct(wb['chg_pct'])}",
                    f"影响{SECTOR_LABEL.get(wb['hits_sector'], wb['hits_sector'])}仓约{wb['sector_weight']}%",
                    "持有不动、禁接飞刀，等净值落地再评估",
                    "分位低且未破线，不恐慌卖出", "铁律2 / price-action-first")

    # ---------- 板块利空聚集（仅观察层） ----------
    held_sectors = {h.get("sector") for h in holdings}
    for hs in held_sectors:
        for ns in HOLDING_SECTOR_TO_NEWS.get(hs, []):
            sn = sector_news.get(ns) or {}
            if sn.get("down", 0) >= 3:
                add("观察", f"{ns}板块利空聚集（{sn['down']}条）",
                    "实时快讯关键词命中，未经价格确认",
                    "只提高警惕、收紧执行纪律，不单独作为卖出依据",
                    "价格行为优先：等持仓净值/板块指数确认再行动",
                    "narrative-news-check / price-action-first")

    directives.sort(key=lambda d: LEVEL_ORDER.get(d["level"], 9))

    # ---------- 单基金建议 ----------
    fund_guides = []
    for h in holdings:
        code = h.get("code", "")
        meta = FUND_META.get(code, {})
        ret = h.get("ret_pct", 0) / 100
        cost_nav = meta.get("cost_nav")
        signals, advice, priority = [], "持有观察", 0
        boundary = "分批≤1/3，间隔≥1周"

        if ret <= THRESHOLDS["hard_stop"]:
            advice, priority = "硬止损：当日无条件出清", 5
            signals.append(f"已破 -25% 硬止损线（{_pct(h['ret_pct'])}）")
        elif ret <= THRESHOLDS["eval_line"]:
            advice, priority = "评估退出：反弹分批减仓", 4
            signals.append(f"已破 -15% 评估线（{_pct(h['ret_pct'])}）")
        elif ret >= THRESHOLDS["take_profit_2"]:
            advice, priority = "止盈：再减 1/3", 4
            signals.append("已触 +20% 止盈线")
        elif ret >= THRESHOLDS["take_profit_1"]:
            advice, priority = "止盈：减 1/3", 3
            signals.append("已触 +15% 止盈线")
        else:
            a_code = meta.get("a_code")
            switch_th = meta.get("switch_th")
            if a_code and switch_th is not None and ret >= switch_th:
                penalty = meta.get("penalty")
                if penalty and now.date() < date.fromisoformat(penalty):
                    advice = (f"已达换A阈值（≥{_pct(switch_th * 100)}），"
                              f"但部分批次 30 天赎回费未满，暂缓/避费换仓")
                    signals.append(f"换A候选 {a_code}")
                    priority = 2
                else:
                    advice = f"换A：分批转 {a_code}（≤1/3，间隔≥1周）"
                    signals.append(f"达到换A阈值（≥{_pct(switch_th * 100)}）")
                    priority = 2

        if nav_pct.get(code, 0) >= 85:
            signals.append(f"净值分位 {nav_pct[code]:.0f}%（区间高位，禁追高）")
        if tech_w > THRESHOLDS["tech_max"] and h.get("sector") == "tech":
            signals.append("科技超配期：该基金只减不加")

        # 板块新闻信号（观察层）
        news_secs = HOLDING_SECTOR_TO_NEWS.get(h.get("sector"), [])
        for ns in news_secs:
            sn = sector_news.get(ns) or {}
            if sn.get("down", 0) >= 3:
                signals.append(f"{ns}利空聚集{sn['down']}条（仅观察）")
            elif sn.get("up", 0) >= 3:
                signals.append(f"{ns}利好聚集{sn['up']}条（等价格确认）")

        # 距下一触发线（破线后显示"反弹至线"所需涨幅）
        dist, dist_label = None, ""
        if cost_nav and ret > -0.9:
            nav_now = cost_nav * (1 + ret)
            if ret < THRESHOLDS["eval_line"]:
                target = cost_nav * (1 + THRESHOLDS["eval_line"])
                dist = (target / nav_now - 1) * 100
                dist_label = "反弹至-15%线需"
            elif ret < THRESHOLDS["take_profit_1"]:
                target = cost_nav * (1 + THRESHOLDS["eval_line"])
                dist = (target / nav_now - 1) * 100
                dist_label = "距-15%评估线还有"
            else:
                target = cost_nav * (1 + THRESHOLDS["take_profit_2"])
                dist = (target / nav_now - 1) * 100
                dist_label = "距+20%止盈线还有"

        fund_guides.append({
            "name": h.get("name"), "code": code, "advice": advice,
            "priority": priority, "signals": signals, "boundary": boundary,
            "dist_next_pct": round(dist, 1) if dist is not None else None,
            "dist_next_label": dist_label,
        })
    fund_guides.sort(key=lambda g: -g["priority"])

    # ---------- 今日禁止清单 ----------
    forbidden = []
    for h in deep:
        forbidden.append(f"禁止摊平加仓：{h['name']}（{_pct(h['ret_pct'])}，深坑补仓=放大错误）")
    for name in hot:
        forbidden.append(f"禁止追高：{name}（净值分位≥85%）")
    if tech_w > THRESHOLDS["tech_max"]:
        forbidden.append(f"禁止新增科技/AI 仓位（当前 {tech_w:.1f}% 已超限）")
    if qdii_w > THRESHOLDS["qdii_max"]:
        forbidden.append(f"禁止新增 QDII（当前 {qdii_w:.1f}% 已超限）")
    if env == "防守":
        forbidden.append("防守模式：暂停一切新增买入（只执行卖出触发线）")

    return {
        "generated_at": now.isoformat(timespec="seconds"),
        "environment": {"label": env, "note": env_note},
        "industry_outlook": outlook,
        "directives": directives,
        "fund_guides": fund_guides,
        "forbidden": forbidden,
        "tech_weight": round(tech_w, 1),
        "qdii_weight": round(qdii_w, 1),
    }
