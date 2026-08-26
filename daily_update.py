#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FundOS 每日手动更新 v1.0
用于手动输入今日基金涨跌幅(来自养基宝/支付宝App)
数据保存到 manual_updates.json
"""
import json, sys, io, os
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA_FILE = Path(r"D:\基金项目\manual_updates.json")

# 用户持仓
FUNDS = [
    ("018735", "华夏绿电"),
    ("012922", "全球成长"),
    ("017641", "标普500"),
    ("019172", "纳斯达克100"),
    ("019764", "半导体"),
    ("019018", "信息产业"),
    ("011608", "科创50联接"),
    ("022365", "科技智选"),
]


def load_data():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {"updates": {}}


def save_data(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def manual_input():
    """交互式手动输入今日涨跌幅"""
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    
    print()
    print("=" * 60)
    print(f"  📝 FundOS 手动更新今日涨跌幅 | {today}")
    print("=" * 60)
    print()
    print("  请打开你的 养基宝/支付宝 App，查看今日估值/涨跌幅")
    print("  依次输入每只基金的今日涨跌幅(%)")
    print("  直接回车跳过不更新，输入 q 退出")
    print()
    
    updates = {}
    for code, name in FUNDS:
        while True:
            try:
                val = input(f"  {name} [{code}]: ").strip()
                if val.lower() == "q":
                    break
                if val == "":
                    break
                pct = float(val.replace("%", "").replace("+", ""))
                updates[code] = {
                    "name": name,
                    "date": today,
                    "day_change_pct": pct,
                    "source": "manual",
                    "input_time": datetime.now().strftime("%H:%M:%S"),
                }
                print(f"    ✅ {name}: {pct:+.2f}%")
                break
            except ValueError:
                print(f"    ❌ 请输入数字，如 5.91 或 -2.3")
            except KeyboardInterrupt:
                print("\n  已取消")
                return
    
    if not updates:
        print("\n  ⚠️ 未输入任何数据")
        return
    
    # Save
    if today not in data["updates"]:
        data["updates"][today] = {}
    data["updates"][today].update(updates)
    save_data(data)
    
    print(f"\n  ✅ 已保存 {len(updates)} 只基金的今日涨跌幅")
    print(f"  📁 数据文件: {DATA_FILE}")
    
    # Show summary
    print()
    print("  📊 今日手动更新汇总:")
    for code, info in updates.items():
        pct = info["day_change_pct"]
        emoji = "🟢" if pct > 0 else ("🔴" if pct < 0 else "⚪")
        print(f"    {emoji} {info['name']:10s}: {pct:+.2f}%")


def view_updates():
    """查看历史手动更新"""
    data = load_data()
    print()
    print("=" * 60)
    print(f"  📋 手动更新历史")
    print("=" * 60)
    
    if not data["updates"]:
        print("  暂无手动更新记录")
        return
    
    for date in sorted(data["updates"].keys(), reverse=True)[:10]:
        print(f"\n  📅 {date}:")
        for code, info in data["updates"][date].items():
            pct = info["day_change_pct"]
            emoji = "🟢" if pct > 0 else ("🔴" if pct < 0 else "⚪")
            print(f"    {emoji} {info['name']:10s}: {pct:+.2f}%")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="FundOS 手动更新")
    parser.add_argument("--view", action="store_true", help="查看历史更新")
    args = parser.parse_args()
    
    if args.view:
        view_updates()
    else:
        manual_input()


if __name__ == "__main__":
    main()
