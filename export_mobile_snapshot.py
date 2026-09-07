#!/usr/bin/env python3
"""Generate a static, mobile-safe FundOS snapshot for scheduled hosting."""
import json
import os
from pathlib import Path

import dashboard

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "mobile_site"

def public_payload(payload):
    private = os.environ.get("FUNDOS_STATIC_PRIVATE") == "1"
    if private:
        return payload
    result = dict(payload)
    portfolio = payload.get("portfolio", {})
    result["portfolio"] = {"as_of": portfolio.get("as_of", ""), "total_ret_pct": portfolio.get("total_ret_pct"), "est_ret_pct": portfolio.get("est_ret_pct")}
    result["holdings"] = [{k: item.get(k) for k in ("name", "sector", "weight", "ret_pct", "nav_day_chg", "today_est", "freshness")} for item in payload.get("holdings", [])]
    result["privacy"] = "redacted"
    return result

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = public_payload(dashboard.collect())
    if os.environ.get("FUNDOS_LLM_API_KEY"):
        try:
            import fundos_llm
            context = {"guide": payload.get("guide"), "news": payload.get("news", []), "news_day": payload.get("news_day"), "portfolio": payload.get("portfolio"), "risk": payload.get("risk")}
            fundos_llm.regenerate(context)
            payload = public_payload(dashboard.collect())
        except Exception as exc:
            payload["static_ai_error"] = str(exc)[:200]
    (OUT / "data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    html = dashboard.HTML.replace("/static/echarts.min.js", "https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js")
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote {OUT / 'data.json'} ({payload.get('privacy', 'private')})")

if __name__ == "__main__":
    main()
