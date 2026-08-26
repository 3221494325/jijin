#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared FundOS portfolio data loader."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SNAPSHOT = ROOT / "portfolio_snapshot.json"
DAILY_RESULT = ROOT / "daily_check_result.json"


def load_portfolio():
    """Load the latest daily result, falling back to the static snapshot."""
    if DAILY_RESULT.exists():
        data = json.loads(DAILY_RESULT.read_text(encoding="utf-8"))
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
            "data_source": DAILY_RESULT.name,
            "holdings": holdings,
            "total_ret_pct": float(data.get("total_ret_pct", 0)),
            "tech_weight": float(data.get("tech_weight", 0)),
            "qdii_weight": float(data.get("qdii_weight", 0)),
        }

    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    return {
        "schema_version": "fundos.portfolio.v1",
        "as_of": data.get("date", "unknown"),
        "data_source": SNAPSHOT.name,
        "holdings": data.get("holdings", []),
        "total_ret_pct": float(data.get("total_ret_pct", 0)),
        "tech_weight": 0.0,
        "qdii_weight": 0.0,
    }
