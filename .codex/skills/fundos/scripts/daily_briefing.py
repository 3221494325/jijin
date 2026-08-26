#!/usr/bin/env python3
"""FundOS Daily Briefing - combines holdings report with news analysis."""

import sys, io, json, re
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    import argparse
    p = argparse.ArgumentParser(description='FundOS Daily Briefing Generator')
    p.add_argument('--holdings', '-H', required=True, help='Holdings Excel file')
    p.add_argument('--news', '-N', help='News markdown file (optional)')
    p.add_argument('--output', '-o', default=None, help='Output file')
    args = p.parse_args()

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    out_lines = []
    out_lines.append(f'# FundOS Daily Briefing')
    out_lines.append(f'> {now}')
    out_lines.append('')
    out_lines.append('## Disclaimer')
    out_lines.append('> This is an objective data summary. Not investment advice.')
    out_lines.append('')

    # 1. Run portfolio report
    out_lines.append('## Portfolio Summary')
    out_lines.append('')
    report_script = Path(__file__).parent / 'portfolio_report.py'
    if report_script.exists():
        import subprocess
        result = subprocess.run(
            ['python', str(report_script), '--holdings', args.holdings, '--format', 'console'],
            capture_output=True, text=True, encoding='utf-8'
        )
        out_lines.append('```')
        out_lines.append(result.stdout[:3000])
        out_lines.append('```')
    out_lines.append('')

    # 2. Parse news if available
    if args.news and Path(args.news).exists():
        out_lines.append('## News Cross-Reference')
        out_lines.append('')
        news_text = Path(args.news).read_text(encoding='utf-8')
        
        # Extract fund sections and sentiment counts
        fund_stats = {}
        current_fund = None
        for line in news_text.split('\n'):
            line = line.strip()
            if line.startswith('### '):
                current_fund = line[4:].strip()
                fund_stats[current_fund] = {'UP': 0, 'DOWN': 0, 'NEUTRAL': 0, 'items': []}
            elif current_fund and line.startswith('- ') and '[UP]' in line or '[up]' in line or 'up' in line.lower():
                if current_fund in fund_stats:
                    fund_stats[current_fund]['UP'] += 1
            elif current_fund and line.startswith('- ') and '[DOWN]' in line or '[down]' in line:
                if current_fund in fund_stats:
                    fund_stats[current_fund]['DOWN'] += 1
        
        for fund, stats in fund_stats.items():
            if stats['UP'] > 0 or stats['DOWN'] > 0:
                out_lines.append(f'- **{fund[:30]}**: UP={stats["UP"]} DOWN={stats["DOWN"]}')
        out_lines.append('')

    output = '\n'.join(out_lines)
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f'Saved: {args.output}')
    else:
        print(output)

if __name__ == '__main__':
    main()
