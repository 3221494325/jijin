"""官方/连接器数据桥（external snapshot bridge）。

背景：WorkBuddy 的金融连接器（盈米基金、融聚汇 FIU）只能由 Agent 通过 MCP 调用，
本地 Python 进程拿不到它们；而看板是纯本地服务。所以两侧通过**文件**对接：

    data/external/nav_snapshot.json     # {code: [{date, nav}]} 或 {"funds": {...}}
    data/external/board_snapshot.json   # {as_of, industry:[...], concept:[...]}

Agent 拉到数据后写这两个文件（带 generated_at），fundos_data 优先读它们，
读不到或过期就退回原来的抓取链路 —— 永远保留 fallback，不会因为桥断了而没数据。

对账结论（2026-11-01）：盈米基金与现有东方财富链路在 017641/022364 上
16/16 个交易日净值**完全一致**（差 0.0000），所以切源不影响成本与收益率。
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

BJ_TZ = ZoneInfo("Asia/Shanghai")
ROOT = Path(__file__).resolve().parent
EXT_DIR = Path(os.environ.get("FUNDOS_EXTERNAL_DIR") or (ROOT / "data" / "external"))

NAV_FILE = "nav_snapshot.json"
BOARD_FILE = "board_snapshot.json"

# 快照允许的最大陈旧度：净值留 4 天（覆盖周末 + QDII 滞后），板块留 5 天
NAV_MAX_AGE = timedelta(days=4)
BOARD_MAX_AGE = timedelta(days=5)


def _load(name):
    path = EXT_DIR / name
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def _age_ok(data, max_age):
    stamp = (data or {}).get("generated_at")
    if not stamp:
        return False
    try:
        ts = datetime.fromisoformat(stamp)
    except ValueError:
        return False
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=BJ_TZ)
    return datetime.now(BJ_TZ) - ts <= max_age


def nav_snapshot(code):
    """返回某只基金的外部净值 [{date, nav}]（升序），无/过期/格式不对则 []。"""
    data = _load(NAV_FILE)
    if not data or not _age_ok(data, NAV_MAX_AGE):
        return []
    funds = data.get("funds") if isinstance(data.get("funds"), dict) else data
    rows = funds.get(str(code)) if isinstance(funds, dict) else None
    if not isinstance(rows, list):
        return []
    out = []
    for r in rows:
        try:
            d, v = str(r.get("date") or r.get("navDate") or ""), float(r.get("nav"))
        except (TypeError, ValueError):
            continue
        if len(d) == 10 and v > 0:
            out.append({"date": d, "nav": v})
    return sorted(out, key=lambda x: x["date"])


def board_snapshot():
    """返回板块快照 {"as_of":..., "industry":[...], "concept":[...]}，无/过期则 None。"""
    data = _load(BOARD_FILE)
    if not data or not _age_ok(data, BOARD_MAX_AGE):
        return None
    if not (data.get("industry") or data.get("concept")):
        return None
    return data


def write_snapshot(kind, payload, source):
    """写快照（供 Agent 侧调用）。kind: 'nav' | 'board'"""
    EXT_DIR.mkdir(parents=True, exist_ok=True)
    name = NAV_FILE if kind == "nav" else BOARD_FILE
    body = dict(payload or {})
    body["source"] = source
    body["generated_at"] = datetime.now(BJ_TZ).isoformat(timespec="seconds")
    (EXT_DIR / name).write_text(json.dumps(body, ensure_ascii=False, indent=1), encoding="utf-8")
    return EXT_DIR / name
