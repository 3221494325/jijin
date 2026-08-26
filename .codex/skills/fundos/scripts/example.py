"""FundOS utility - validate data against canonical schema."""
import json, sys
from pathlib import Path

SCHEMAS = {
    "fund_nav": ["code", "name", "date", "nav", "acc_nav", "daily_return", "source"],
    "stock_quote": ["code", "market", "name", "open", "high", "low", "close", "volume", "amount", "change_pct", "source"],
}

def validate(schema_name, data):
    required = SCHEMAS.get(schema_name, [])
    return [f for f in required if f not in data]

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python example.py SCHEMA_NAME JSON_FILE")
        print("Schemas:", list(SCHEMAS.keys()))
        sys.exit(1)
    data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    missing = validate(sys.argv[1], data)
    if missing:
        print(f"Missing fields: {missing}")
        sys.exit(1)
    print("Schema valid!")
