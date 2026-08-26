#!/usr/bin/env python3
"""FundOS NAV Auto-Updater - pull latest NAV from public APIs.

Usage:
  python nav_update.py                        # Update all holdings
  python nav_update.py --fund 000001          # Single fund
  python nav_update.py --output nav.json      # Export results
"""

import sys, io, json, time, urllib.request
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

H = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fund.eastmoney.com/'}

# Portfolio fund codes (user's actual holdings)
FUND_CODES = {
    "华夏中证绿色电力ETF联接C": "018735",
    "易方达全球成长精选混合(QDII)C": "018354",
    "摩根标普500指数(QDII)A": "017641",
    "摩根纳斯达克100指数(QDII)A": "019173",
    "中欧半导体产业股票C": "020684",
    "易方达信息产业混合C": "019024",
    "易方达科创50联接A": "011608",
    "永赢科技智选混合C": "022365",
}

def fetch_nav(fund_code, fund_name=""):
    """Fetch latest NAV from EastMoney public API"""
    try:
        url = f'https://fundgz.1234567.com.cn/js/{fund_code}.js'
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=10)
        text = resp.read().decode('utf-8')
        # Parse jsonpgz({"fundcode":"018735","name":"...","jzrq":"...","dwjz":"...","gsz":"...","gszzl":"...","gztime":"..."});
        import re
        match = re.search(r'jsonpgz\((.+)\)', text)
        if match:
            data = json.loads(match.group(1))
            return {
                'code': fund_code,
                'name': data.get('name', fund_name),
                'nav_date': data.get('jzrq', ''),
                'nav': float(data.get('dwjz', 0)),
                'estimate_nav': float(data.get('gsz', 0)),
                'estimate_change': float(data.get('gszzl', 0)),
                'estimate_time': data.get('gztime', ''),
            }
    except:
        pass
    return {'code': fund_code, 'name': fund_name, 'error': 'fetch failed'}

def main():
    import argparse
    p = argparse.ArgumentParser(description='FundOS NAV Auto-Updater')
    p.add_argument('--fund', '-f', help='Fund code (6 digits)')
    p.add_argument('--output', '-o', help='Output JSON file')
    args = p.parse_args()

    if args.fund:
        result = fetch_nav(args.fund)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"FundOS NAV Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 55)
    print(f"{'Fund':<22s} {'NAV':>8s} {'Est':>8s} {'Chg%':>7s}")
    print("-" * 55)

    results = []
    for name, code in FUND_CODES.items():
        print(f"  Fetching {name[:20]}...", end=" ")
        time.sleep(0.5)  # Rate limit
        data = fetch_nav(code, name)
        results.append(data)
        if 'error' in data:
            print("FAIL")
        else:
            nav = data.get('nav', 0)
            est = data.get('estimate_nav', 0)
            chg = data.get('estimate_change', 0)
            arrow = '+' if chg >= 0 else ''
            print(f"NAV={nav:.4f} Est={est:.4f} {arrow}{chg:.2f}%")

    if args.output:
        Path(args.output).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"\nSaved: {args.output}")

if __name__ == '__main__':
    main()
