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
INDEX_FILE = "index_snapshot.json"
FUND_STATE_FILE = "fund_state_snapshot.json"

# 快照允许的最大陈旧度：净值留 4 天（覆盖周末 + QDII 滞后），板块/指数留 5 天
NAV_MAX_AGE = timedelta(days=4)
BOARD_MAX_AGE = timedelta(days=5)
INDEX_MAX_AGE = timedelta(days=5)


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


KIND_FILES = {
    "nav": NAV_FILE,
    "board": BOARD_FILE,
    "index": INDEX_FILE,
    "fund_state": FUND_STATE_FILE,
}

# kind -> (文件, 最大陈旧度, 中文标签)
KIND_META = {
    "nav": (NAV_FILE, NAV_MAX_AGE, "净值"),
    "board": (BOARD_FILE, BOARD_MAX_AGE, "板块"),
    "index": (INDEX_FILE, INDEX_MAX_AGE, "指数"),
    "fund_state": (FUND_STATE_FILE, NAV_MAX_AGE, "申赎"),
}


def health():
    """四类快照的时效体检：连接器掉线时，这是"还能撑几天"的唯一依据。

    返回 [{kind,label,status,source,as_of,generated_at,days_left}]
    status: ok | expired | missing | invalid
    """
    now = datetime.now(BJ_TZ)
    out = []
    for kind, (name, max_age, label) in KIND_META.items():
        data = _load(name)
        if not data:
            out.append({"kind": kind, "label": label, "status": "missing"})
            continue
        stamp = data.get("generated_at")
        try:
            ts = datetime.fromisoformat(str(stamp))
        except (TypeError, ValueError):
            out.append({"kind": kind, "label": label, "status": "invalid"})
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=BJ_TZ)
        left = max_age - (now - ts)
        out.append({
            "kind": kind, "label": label,
            "status": "ok" if left.total_seconds() > 0 else "expired",
            "source": data.get("source"),
            "as_of": data.get("as_of") or (data.get("funds") and None) or None,
            "generated_at": ts.isoformat(timespec="seconds"),
            "days_left": max(0, int(left.total_seconds() // 86400)),
        })
    return out


def write_snapshot(kind, payload, source):
    """写快照（供 Agent 侧调用）。kind: nav / board / index / fund_state

    未知 kind 直接报错 —— 曾因为默认值静默写进了 nav_snapshot.json，把净值快照冲掉。
    """
    if kind not in KIND_FILES:
        raise ValueError(f"unknown snapshot kind: {kind}")
    EXT_DIR.mkdir(parents=True, exist_ok=True)
    name = KIND_FILES[kind]
    body = dict(payload or {})
    body["source"] = source
    body["generated_at"] = datetime.now(BJ_TZ).isoformat(timespec="seconds")
    (EXT_DIR / name).write_text(json.dumps(body, ensure_ascii=False, indent=1), encoding="utf-8")
    return EXT_DIR / name


def fund_state_snapshot():
    """申赎状态快照 {code: {...}}，过期返回 {}。数据来自盈米 BatchGetFundTradeRules。"""
    data = _load(FUND_STATE_FILE)
    if not data or not _age_ok(data, NAV_MAX_AGE):
        return {}
    funds = data.get("funds")
    return funds if isinstance(funds, dict) else {}


def index_snapshot():
    """指数快照 {"as_of":..., "cn": {code:{name,price,chg_pct}}, "global": {...}}，过期则 None。

    用法约定：只用来**补缺**（抓取链路没返回的指数），不用来覆盖已有的实时值 ——
    盘中快照是上一交易日的，覆盖会写脏当天行情。
    """
    data = _load(INDEX_FILE)
    if not data or not _age_ok(data, INDEX_MAX_AGE):
        return None
    if not (data.get("cn") or data.get("global")):
        return None
    return data
