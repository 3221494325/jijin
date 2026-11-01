#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared FundOS portfolio data loader."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SNAPSHOT = ROOT / "portfolio_snapshot.json"
DAILY_RESULT = ROOT / "daily_check_result.json"


def load_portfolio():
    """Load the latest daily result, falling back to the static snapshot.

    两个日期必须分开，别再混成一个：
      as_of          = 估值日期（daily_check 的 checked_at，代表净值算到哪天）
      holdings_as_of = 持仓申报日期（portfolio_snapshot.json 的 date，代表份额/成本是哪天确认的）
    以前只有一个 as_of，用的又是 daily 的时间，导致"持仓快照新鲜度"把 18 天前的持仓判成 2 天前。
    """
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    snap_date = snap.get("date", "unknown")

    if DAILY_RESULT.exists():
        daily = json.loads(DAILY_RESULT.read_text(encoding="utf-8"))
        snap_codes = {h.get("code") for h in snap.get("holdings", [])}
        daily_codes = {h.get("code") for h in daily.get("holdings", [])}
        if snap_codes and snap_codes == daily_codes:
            data = daily
            holdings = []
            for item in data.get("holdings", []):
                cost = float(item.get("cost", 0))
                ret_pct = float(item.get("ret_pct", 0))
                holdings.append({
                    "name": item.get("name", ""),
                    "code": item.get("code", ""),
                    "ret_pct": ret_pct,
                    "weight": float(item.get("weight", 0)),
                    "cost": cost,
                    "value": float(item.get("value", cost * (1 + ret_pct / 100))),
                    "sector": item.get("sector", ""),
                    "nav_date": item.get("nav_date", ""),
                    "data_status": "verified",
                })
            return {
                "schema_version": "fundos.portfolio.v1",
                "as_of": data.get("checked_at", "unknown"),
                "holdings_as_of": snap_date,
                "data_source": DAILY_RESULT.name,
                "holdings_source": SNAPSHOT.name,
                "holdings": holdings,
                "total_ret_pct": float(data.get("total_ret_pct", 0)),
                "tech_weight": float(data.get("tech_weight", 0)),
                "qdii_weight": float(data.get("qdii_weight", 0)),
            }

    return {
        "schema_version": "fundos.portfolio.v1",
        "as_of": snap_date,
        "holdings_as_of": snap_date,
        "data_source": SNAPSHOT.name,
        "holdings_source": SNAPSHOT.name,
        "holdings": snap.get("holdings", []),
        "total_ret_pct": float(snap.get("total_ret_pct", 0)),
        "tech_weight": float(snap.get("tech_weight", 0)),
        "qdii_weight": float(snap.get("qdii_weight", 0)),
    }
