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
    # GitHub Pages is intentionally public in this deployment; retain the full
    # dashboard fields so the mobile view can show portfolio value and P/L.
    result["privacy"] = "public-financial-data"
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
