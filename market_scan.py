#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FundOS 全市场板块扫描 v3.0 — 新浪源 · 找强势方向 · 对比持仓 · 主线连续性
v3.0 (2026-08-28):
  - 接入 fundos_data 数据层（重试/缓存）
  - 每日板块快照落盘 data/board_history/YYYY-MM-DD.json
  - 新增「主线连续性」: 今日最强板块 vs 昨日排名/是否连续在榜（轮动识别）
"""
import sys
from datetime import datetime

import fundos_data
from fundos_config import WATCH_BOARDS, ROOT, TECH_SECTOR_BOARDS

sys.stdout.reconfigure(encoding="utf-8")
OUTPUT = ROOT / "market_sector_scan.md"
TOP_N = 15


def scan():
    print("📡 扫描全市场板块 (新浪源)...")
    industries, concepts = fundos_data.fetch_sector_boards()
    print(f"  行业 {len(industries)}个 | 概念 {len(concepts)}个")

    industries.sort(key=lambda x: x["chg_pct"], reverse=True)
    concepts.sort(key=lambda x: x["chg_pct"], reverse=True)

    # 快照落盘 + 读历史（主线连续性）
    try:
        fundos_data.save_board_snapshot(industries, concepts)
    except OSError:
        pass
    history = fundos_data.load_board_history(limit=6)

    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines.append("=" * 76)
    lines.append(f"  🌐 FundOS 全市场板块扫描 | {now}")
    lines.append("=" * 76)

    lines.append("\n  🏭 行业板块 · 涨幅 TOP15")
    lines.append(f"  {'板块':<10s} {'涨跌%':>7s} {'成交(亿)':>9s} {'领涨股':<8s} {'涨%':>6s}")
    lines.append("  " + "-" * 50)
    for it in industries[:15]:
        bar = "█" * min(15, int(abs(it["chg_pct"])))
        lines.append(f"  {it['name']:<10s} {it['chg_pct']:>+7.2f}% {it['amount']:>8.0f} {it['leader']:<8s} {it['leader_chg']:>+5.1f}% {bar}")

    lines.append("\n  📉 行业板块 · 跌幅 TOP8")
    for it in reversed(industries[-8:]):
        if it["chg_pct"] < 0:
            lines.append(f"  {it['name']:<10s} {it['chg_pct']:>+7.2f}% 成交{it['amount']:>7.0f}亿")

    lines.append("\n  💡 概念板块 · 涨幅 TOP20")
    lines.append(f"  {'概念':<12s} {'涨跌%':>7s} {'成交(亿)':>9s} {'领涨':<8s} {'涨%':>6s}")
    lines.append("  " + "-" * 52)
    for it in concepts[:20]:
        bar = "█" * min(15, int(abs(it["chg_pct"])))
        lines.append(f"  {it['name']:<12s} {it['chg_pct']:>+7.2f}% {it['amount']:>8.0f} {it['leader']:<8s} {it['leader_chg']:>+5.1f}% {bar}")

    # ---- 主线连续性（轮动 vs 持续） ----
    if len(history) >= 2:
        lines.append("\n" + "=" * 76)
        lines.append("  🔄 主线连续性 (近5个扫描日)")
        lines.append("=" * 76)
        prev = history[-2]
        prev_boards = sorted(prev.get("industries", []), key=lambda x: x["chg_pct"], reverse=True)
        prev_top = {b["name"]: i + 1 for i, b in enumerate(prev_boards[:TOP_N])}
        lines.append(f"  {'板块':<10s} {'今日%':>7s} {'今日榜':>6s} {'昨日榜':>6s} {'连续在榜':>8s}")
        for i, it in enumerate(industries[:TOP_N]):
            rank_now = i + 1
            rank_prev = prev_top.get(it["name"])
            streak = 0
            for snap in reversed(history):
                boards = sorted(snap.get("industries", []), key=lambda x: x["chg_pct"], reverse=True)
                names = {b["name"] for b in boards[:TOP_N]}
                if it["name"] in names:
                    streak += 1
                else:
                    break
            cont = f"{streak}天" if streak > 1 else "新增"
            rp = str(rank_prev) if rank_prev else "-"
            lines.append(f"  {it['name']:<10s} {it['chg_pct']:>+7.2f}% {rank_now:>6} {rp:>6} {cont:>8}")
        leaders = [it["name"] for it in industries[:5]
                   if all(it["name"] in {b["name"] for b in sorted(s.get("industries", []),
                          key=lambda x: x["chg_pct"], reverse=True)[:TOP_N]}
                          for s in history[-2:] if s.get("date") != history[-1]["date"])]
        if leaders:
            lines.append(f"\n  📌 连续两日居前15: {', '.join(leaders)} → 主线候选（仍需价格与成交确认）")
        else:
            lines.append("\n  📌 今日前5均为新面孔 → 高速轮动日，追高风险大")

        # ---- 主线得分（轮动打分，0-100） ----
        lines.append("\n  🎯 主线得分 TOP5（连续在榜50% + 排名改善30% + 成交趋势20%）")
        scored = []
        for it in industries[:TOP_N]:
            rs = fundos_data.rotation_score(history, it["name"], top_n=TOP_N)
            if rs.get("score") is not None:
                scored.append((it["name"], rs))
        for name, rs in sorted(scored, key=lambda x: -x[1]["score"])[:5]:
            lines.append(f"  {name:<10s} 得分 {rs['score']:>5.1f}  "
                         f"(连续{rs.get('streak', 0)}天, 今日第{rs.get('rank_now', '-')}名"
                         f", 昨日第{rs.get('rank_prev', '-')}名, {rs.get('chg_pct', 0):+.2f}%)")
        if not scored:
            lines.append("  (得分样本不足，自第2个扫描日起启用)")
    else:
        days_cnt = len(history)
        lines.append(f"\n  ℹ️ 主线连续性/轮动打分: 板块历史积累中 ({days_cnt}/2天)，"
                     f"自第2个扫描日起自动启用")

    # ---- 持仓板块定位（关键词包含匹配，适配新浪板块命名变动） ----
    lines.append("\n" + "=" * 76)
    lines.append("  📌 你的持仓相关板块 · 全市场排名")
    lines.append("=" * 76)
    all_boards = industries + concepts
    sorted_all = sorted(all_boards, key=lambda x: x["chg_pct"], reverse=True)
    rank_map = {it["name"]: i + 1 for i, it in enumerate(sorted_all)}
    total = len(sorted_all)

    for kw in WATCH_BOARDS:
        candidates = [it for it in all_boards if kw in it["name"]]
        if not candidates:
            continue
        best = min(candidates, key=lambda x: len(x["name"]))  # 名字最短=最贴近
        rank = rank_map.get(best["name"], "?")
        emoji = "🟢" if best["chg_pct"] > 0 else ("🔴" if best["chg_pct"] < 0 else "⚪")
        extra = f" (含{len(candidates)}个相关板块)" if len(candidates) > 1 else ""
        lines.append(f"  {emoji} {best['name']:<10s} {best['chg_pct']:>+7.2f}% 全市场第{rank}/{total}名{extra}")

    # ---- 强弱对比结论 ----
    lines.append("\n" + "=" * 76)
    lines.append("  ⚖️ 市场主线判断")
    lines.append("=" * 76)
    if industries:
        lines.append(f"  🥇 最强行业: {industries[0]['name']} {industries[0]['chg_pct']:+.2f}% (领涨: {industries[0]['leader']})")
        lines.append(f"  🥈 次强行业: {industries[1]['name']} {industries[1]['chg_pct']:+.2f}%")
        lines.append(f"  🥉 第三行业: {industries[2]['name']} {industries[2]['chg_pct']:+.2f}%")
    if concepts:
        lines.append(f"  💡 最强概念: {concepts[0]['name']} {concepts[0]['chg_pct']:+.2f}%")

    tech_sectors = [it for it in industries if it["name"] in TECH_SECTOR_BOARDS]
    if tech_sectors and industries:
        strong_avg = sum(it["chg_pct"] for it in industries[:5]) / 5
        tech_avg = sum(it["chg_pct"] for it in tech_sectors) / len(tech_sectors)
        lines.append(f"\n  📐 强弱对比: 全市场前5行业均涨 {strong_avg:+.1f}%  vs  你的板块均涨 {tech_avg:+.1f}%")
        diff = strong_avg - tech_avg
        if diff > 2:
            lines.append(f"  ⚠️ 你的持仓板块比市场最强方向落后 {diff:.1f} 个百分点 — 风格偏移明显")
        elif diff > 0:
            lines.append(f"  ℹ️ 你的持仓板块比最强方向落后 {diff:.1f} 个百分点")
        else:
            lines.append(f"  ✅ 你的持仓板块不弱于市场最强方向")

    lines.append("")
    lines.append("  📌 客观行情扫描，不构成投资建议")
    lines.append("=" * 76)

    report = "\n".join(lines)
    OUTPUT.write_text(report, encoding="utf-8")
    print(report)
    print(f"\n  💾 {OUTPUT}")
    return report


if __name__ == "__main__":
    scan()
