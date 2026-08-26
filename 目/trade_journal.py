#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FundOS 操作记录/复盘系统 v1.1
记录每次建议与操作，留痕复盘
用法:
  python trade_journal.py add                      # 交互式记录
  python trade_journal.py add --code 012922 --action 2 --reason "..." --expect "..."
  python trade_journal.py view                      # 查看历史
  python trade_journal.py review                    # 复盘总结

注: 基金代码已纠错(2026-08-08): 全球成长018354→012922、纳斯达克019173→019172、
半导体020684→019764、信息产业019024→019018。数据以 portfolio_snapshot.json 为准。
"""
import json, sys, io
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
JOURNAL = Path(r"D:\基金项目\trade_journal.json")

# 已纠错代码表（与 portfolio_snapshot.json 一致）
FUNDS = {
    "1": ("018735", "华夏绿电"),
    "2": ("012922", "全球成长"),
    "3": ("017641", "标普500"),
    "4": ("019172", "纳斯达克100"),
    "5": ("019764", "半导体"),
    "6": ("011608", "科创50联接"),
    "7": ("022365", "科技智选"),
    "8": ("019018", "信息产业"),
}

ACTIONS = {"1": "买入/加仓", "2": "卖出/减仓", "3": "换仓", "4": "持有不动", "5": "观察等待"}


def load():
    if JOURNAL.exists():
        return json.loads(JOURNAL.read_text(encoding="utf-8"))
    return {"entries": []}


def save(data):
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    JOURNAL.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _next_id(data):
    return max((e.get("id", 0) for e in data.get("entries", [])), default=0) + 1


def add(code=None, action=None, reason=None, expect=None, fund_name=None):
    """支持交互式与非交互式(参数传入)两种模式。"""
    data = load()

    # ---- 非交互式路径 ----
    if code is not None and action is not None:
        if code in ("ALL", "9", "全组合"):
            code, name = "ALL", "全组合"
        else:
            name = fund_name or next((n for c, n in FUNDS.values() if c == code), code)
        action = ACTIONS.get(str(action), action)  # 允许传编号或文字
        reason = reason or "(未填写)"
        expect = expect or "(未填写)"
        _emit(data, code, name, action, reason, expect)
        return

    # ---- 交互式路径 ----
    print()
    print("=" * 60)
    print(f"  📝 记录操作/建议 | {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)
    print("\n  选择基金:")
    for k, (code, name) in FUNDS.items():
        print(f"    [{k}] {name} ({code})")
    print("    [9] 全组合 / 市场判断")
    try:
        fk = input("\n  基金编号: ").strip()
        if fk in FUNDS:
            code, name = FUNDS[fk]
        elif fk == "9":
            code, name = "ALL", "全组合"
        else:
            print("  无效编号")
            return
    except (EOFError, KeyboardInterrupt):
        return

    print("\n  操作类型:")
    for k, v in ACTIONS.items():
        print(f"    [{k}] {v}")
    try:
        ak = input("\n  类型编号: ").strip()
        action = ACTIONS.get(ak, "持有不动")
    except (EOFError, KeyboardInterrupt):
        return

    try:
        reason = input("\n  理由/判断依据: ").strip() or "(未填写)"
    except (EOFError, KeyboardInterrupt):
        return

    try:
        result = input("  预期结果(如: 1个月内回本): ").strip() or "(未填写)"
    except (EOFError, KeyboardInterrupt):
        return

    _emit(data, code, name, action, reason, result)


def _emit(data, code, name, action, reason, expect):
    entry = {
        "id": _next_id(data),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "fund": name, "code": code,
        "action": action, "reason": reason, "expect": expect,
        "actual": "",
        "closed": False,
    }
    data["entries"].append(entry)
    save(data)
    print(f"\n  ✅ 已记录 #{entry['id']}: {name} → {action}")


def view():
    data = load()
    entries = data["entries"]
    if not entries:
        print("\n  📋 暂无操作记录")
        return
    print()
    print("=" * 66)
    print(f"  📋 操作记录 | 共{len(entries)}条")
    print("=" * 66)
    for e in reversed(entries):
        status = "✅已复盘" if e.get("closed") else "⏳待复盘"
        print(f"\n  #{e['id']} [{e['date']}] {status}")
        print(f"    {e['fund']} → {e['action']}")
        print(f"    理由: {e['reason']}")
        print(f"    预期: {e['expect']}")
        if e.get("actual"):
            print(f"    结果: {e['actual']}")


def review():
    data = load()
    entries = [e for e in data["entries"] if not e.get("closed")]
    if not entries:
        print("\n  📋 没有待复盘的记录")
        return
    print()
    print("=" * 66)
    print(f"  🔍 复盘 | 待复盘{len(entries)}条")
    print("=" * 66)
    for e in entries:
        print(f"\n  #{e['id']} [{e['date']}] {e['fund']} → {e['action']}")
        print(f"    理由: {e['reason']}")
        print(f"    预期: {e['expect']}")
        try:
            actual = input(f"    实际结果: ").strip()
            if actual:
                e["actual"] = actual
                e["closed"] = True
                print(f"    ✅ #{e['id']} 已复盘")
        except (EOFError, KeyboardInterrupt):
            break
    save(data)
    print(f"\n  💾 复盘已保存: {JOURNAL}")


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["add", "view", "review"])
    p.add_argument("--code", default=None, help="基金代码 或 ALL")
    p.add_argument("--action", default=None, help="操作编号(1-5)或文字")
    p.add_argument("--reason", default=None)
    p.add_argument("--expect", default=None)
    p.add_argument("--name", default=None, help="非快照内基金可显式指定名称")
    args = p.parse_args()
    if args.cmd == "add":
        add(args.code, args.action, args.reason, args.expect, args.name)
    elif args.cmd == "view":
        view()
    elif args.cmd == "review":
        review()


if __name__ == "__main__":
    main()
