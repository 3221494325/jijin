#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FundOS 全市场板块扫描 v2.0 — 新浪源(稳定) · 找强势方向 · 对比持仓
"""
import urllib.request, json, sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUTPUT = Path(r"D:\基金项目\market_sector_scan.md")

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def fetch_sina(url):
    req = urllib.request.Request(url, headers=H)
    resp = urllib.request.urlopen(req, timeout=12).read().decode("gbk", errors="replace")
    start = resp.index("{")
    end = resp.rindex("}") + 1
    data = json.loads(resp[start:end])
    out = []
    for k, v in data.items():
        p = v.split(",")
        if len(p) >= 13:
            try:
                out.append({
                    "code": p[0], "name": p[1], "count": int(p[2]),
                    "avg_price": float(p[3]), "avg_chg": float(p[4]),
                    "chg_pct": float(p[5]),
                    "amount": float(p[6]) / 1e8,  # 成交额(亿)
                    "leader": p[12], "leader_chg": float(p[9]),
                })
            except:
                pass
    return out


def scan():
    print("📡 扫描全市场板块 (新浪源)...")
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines.append("=" * 76)
    lines.append(f"  🌐 FundOS 全市场板块扫描 | {now} (周五收盘数据)")
    lines.append("=" * 76)

    # 行业板块
    print("  行业板块...", end=" ", flush=True)
    industries = fetch_sina("https://vip.stock.finance.sina.com.cn/q/view/newSinaHy.php")
    print(f"{len(industries)}个")
    industries.sort(key=lambda x: x["chg_pct"], reverse=True)

    # 概念板块
    print("  概念板块...", end=" ", flush=True)
    concepts = fetch_sina("https://vip.stock.finance.sina.com.cn/q/view/newFLJK.php?param=class")
    print(f"{len(concepts)}个")
    concepts.sort(key=lambda x: x["chg_pct"], reverse=True)

    # 1. 行业涨幅榜
    lines.append("\n  🏭 行业板块 · 涨幅 TOP15")
    lines.append(f"  {'板块':<10s} {'涨跌%':>7s} {'成交(亿)':>9s} {'领涨股':<8s} {'涨%':>6s}")
    lines.append("  " + "-" * 50)
    for it in industries[:15]:
        bar = "█" * min(15, int(abs(it["chg_pct"])))
        lines.append(f"  {it['name']:<10s} {it['chg_pct']:>+7.2f}% {it['amount']:>8.0f} {it['leader']:<8s} {it['leader_chg']:>+5.1f}% {bar}")

    # 2. 行业跌幅榜
    lines.append("\n  📉 行业板块 · 跌幅 TOP8")
    for it in reversed(industries[-8:]):
        if it["chg_pct"] < 0:
            lines.append(f"  {it['name']:<10s} {it['chg_pct']:>+7.2f}% 成交{it['amount']:>7.0f}亿")

    # 3. 概念涨幅榜
    lines.append("\n  💡 概念板块 · 涨幅 TOP20")
    lines.append(f"  {'概念':<12s} {'涨跌%':>7s} {'成交(亿)':>9s} {'领涨':<8s} {'涨%':>6s}")
    lines.append("  " + "-" * 52)
    for it in concepts[:20]:
        bar = "█" * min(15, int(abs(it["chg_pct"])))
        lines.append(f"  {it['name']:<12s} {it['chg_pct']:>+7.2f}% {it['amount']:>8.0f} {it['leader']:<8s} {it['leader_chg']:>+5.1f}% {bar}")

    # 4. 持仓板块定位
    lines.append("\n" + "=" * 76)
    lines.append("  📌 你的持仓相关板块 · 全市场排名")
    lines.append("=" * 76)
    watch = ["半导体", "软件开发", "通信设备", "电子元件", "消费电子", "计算机行业",
             "电力行业", "新能源", "医疗器械", "生物制药"]
    all_boards = industries + concepts
    # 统计排名
    sorted_all = sorted(all_boards, key=lambda x: x["chg_pct"], reverse=True)
    rank_map = {it["name"]: i + 1 for i, it in enumerate(sorted_all)}
    total = len(sorted_all)

    for name in watch:
        for it in all_boards:
            if it["name"] == name:
                rank = rank_map.get(name, "?")
                emoji = "🟢" if it["chg_pct"] > 0 else ("🔴" if it["chg_pct"] < 0 else "⚪")
                lines.append(f"  {emoji} {name:<10s} {it['chg_pct']:>+7.2f}% 全市场第{rank}/{total}名")
                break

    # 5. 强弱对比结论
    lines.append("\n" + "=" * 76)
    lines.append("  ⚖️ 市场主线判断")
    lines.append("=" * 76)
    if industries:
        lines.append(f"  🥇 最强行业: {industries[0]['name']} {industries[0]['chg_pct']:+.2f}% (领涨: {industries[0]['leader']})")
        lines.append(f"  🥈 次强行业: {industries[1]['name']} {industries[1]['chg_pct']:+.2f}%")
        lines.append(f"  🥉 第三行业: {industries[2]['name']} {industries[2]['chg_pct']:+.2f}%")
    if concepts:
        lines.append(f"  💡 最强概念: {concepts[0]['name']} {concepts[0]['chg_pct']:+.2f}%")

    # 持仓板块 vs 强势板块差距
    tech_sectors = [it for it in industries if it["name"] in watch]
    if tech_sectors and industries:
        strong_avg = sum(it["chg_pct"] for it in industries[:5]) / 5
        tech_avg = sum(it["chg_pct"] for it in tech_sectors) / len(tech_sectors) if tech_sectors else 0
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
