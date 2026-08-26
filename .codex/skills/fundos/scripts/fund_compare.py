#!/usr/bin/env python3
"""FundOS Fund Comparison Tool - compare funds side by side.

Usage:
  python fund_compare.py                                  # Compare all holdings
  python fund_compare.py --funds 000001,000002            # Specific funds
"""

import sys, io, json, time, urllib.request
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

H = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fund.eastmoney.com/'}

FUND_CODES = {
    "华夏绿色电力": "018735", "易方达全球成长": "018354", "摩根标普500": "017641",
    "摩根纳斯达克100": "019173", "中欧半导体": "020684", "易方达信息产业": "019024",
    "易方达科创50": "011608", "永赢科技智选": "022365",
}

def fetch_multi_period(fund_code):
    """Fetch NAV for different periods to compute returns"""
    periods = {'1M': 22, '3M': 66, '6M': 132, '1Y': 253}
    result = {'code': fund_code}
    try:
        url = f'https://fund.eastmoney.com/pingzhongdata/{fund_code}.js'
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=10)
        text = resp.read().decode('utf-8')
        # Extract Data_netWorthTrend
        import re
        match = re.search(r'var Data_netWorthTrend = (\[.+?\]);', text, re.DOTALL)
        if match:
            nav_data = json.loads(match.group(1))
            for label, days in periods.items():
                if len(nav_data) >= days:
                    start_nav = nav_data[-days]['y']
                    end_nav = nav_data[-1]['y']
                    result[f'return_{label}'] = round((end_nav - start_nav) / start_nav * 100, 2)
    except:
        pass
    return result

def main():
    import argparse
    p = argparse.ArgumentParser(description='FundOS Fund Comparison')
    p.add_argument('--funds', help='Comma-separated fund codes')
    args = p.parse_args()

    if args.funds:
        codes = {f'Fund_{c}': c for c in args.funds.split(',')}
    else:
        codes = FUND_CODES

    print(f"FundOS Fund Comparison - {datetime.now().strftime('%Y-%m-%d')}")
    print()

    # Header
    header = f"{'Fund':<20s} {'1M':>7s} {'3M':>7s} {'6M':>7s} {'1Y':>7s}"
    print(header)
    print("-" * len(header))

    for name, code in codes.items():
        data = fetch_multi_period(code)
        if data:
            r1m = f'{data.get("return_1M", 0):+.1f}%' if data.get('return_1M') is not None else 'N/A'
            r3m = f'{data.get("return_3M", 0):+.1f}%' if data.get('return_3M') is not None else 'N/A'
            r6m = f'{data.get("return_6M", 0):+.1f}%' if data.get('return_6M') is not None else 'N/A'
            r1y = f'{data.get("return_1Y", 0):+.1f}%' if data.get('return_1Y') is not None else 'N/A'
            print(f"{name:<20s} {r1m:>7s} {r3m:>7s} {r6m:>7s} {r1y:>7s}")
        time.sleep(0.3)

if __name__ == '__main__':
    main()
