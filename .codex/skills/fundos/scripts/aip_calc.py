#!/usr/bin/env python3
"""FundOS AIP Calculator - Dollar-Cost Averaging analysis.

Inherits from xalpha toolbox.py (IRR/XIRR/fee calculation).

Usage:
  python aip_calc.py --amount 1000 --period monthly --years 3 --annual-return 0.08
  python aip_calc.py --amount 500 --period weekly --years 5
"""

import sys, io, math
from datetime import datetime, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def xirr(cashflows: list) -> float:
    """Calculate XIRR (annualized return) from cashflow series.
    Inherited from xalpha toolbox.py logic.
    
    cashflows: list of (date_str, amount) - negative for investments, positive for redemptions
    """
    if not cashflows or len(cashflows) < 2:
        return 0.0
    
    # Simple Newton's method for IRR
    rate = 0.1
    for _ in range(100):
        npv = 0
        dnpv = 0
        ref_date = datetime.strptime(cashflows[0][0], "%Y-%m-%d")
        for date_str, amount in cashflows:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            years = (d - ref_date).days / 365.0
            npv += amount / ((1 + rate) ** years)
            dnpv -= years * amount / ((1 + rate) ** (years + 1))
        
        if abs(dnpv) < 1e-10:
            break
        rate -= npv / dnpv
    
    return rate

def simulate_aip(amount: float, period: str, years: int, annual_return: float = 0.08, volatility: float = 0.15):
    """Simulate AIP returns with Monte Carlo-like projection."""
    periods_per_year = {'daily': 252, 'weekly': 52, 'biweekly': 26, 'monthly': 12, 'quarterly': 4}[period]
    total_periods = years * periods_per_year
    period_return = (1 + annual_return) ** (1 / periods_per_year) - 1
    period_vol = volatility / math.sqrt(periods_per_year)
    
    total_invested = 0
    total_units = 0
    nav = 1.0
    
    # Simulate with average returns (best case scenario based on assumed annual_return)
    for i in range(total_periods):
        total_invested += amount
        # Deterministic projection based on assumed return
        nav *= (1 + period_return)
        units_bought = amount / nav
        total_units += units_bought
    
    final_value = total_units * nav
    total_return = final_value - total_invested
    return_pct = (final_value / total_invested - 1) * 100
    avg_cost = total_invested / total_units if total_units > 0 else 0
    
    return {
        'total_invested': total_invested,
        'final_value': final_value,
        'total_return': total_return,
        'return_pct': return_pct,
        'total_units': total_units,
        'avg_cost': avg_cost,
        'final_nav': nav,
    }

def main():
    import argparse
    p = argparse.ArgumentParser(description='FundOS AIP Calculator (inherits xalpha toolbox logic)')
    p.add_argument('--amount', '-a', type=float, required=True, help='Per-period investment amount')
    p.add_argument('--period', '-p', choices=['daily','weekly','biweekly','monthly','quarterly'], default='monthly')
    p.add_argument('--years', '-y', type=int, default=3)
    p.add_argument('--annual-return', '-ar', type=float, default=0.08, help='Assumed annual return (0.08 = 8%%)')
    p.add_argument('--volatility', '-v', type=float, default=0.15, help='Assumed annual volatility')
    p.add_argument('--fee', '-f', type=float, default=0.0015, help='Annual management fee')
    args = p.parse_args()

    result = simulate_aip(args.amount, args.period, args.years, args.annual_return, args.volatility)
    
    # Subtract fees
    fee_impact = result['total_invested'] * args.fee * args.years * 0.5  # Avg balance fee
    result['final_value'] -= fee_impact
    result['total_return'] -= fee_impact
    result['return_pct'] = (result['final_value'] / result['total_invested'] - 1) * 100

    print()
    print("=" * 55)
    print("  FundOS AIP Calculator (inherits xalpha toolbox)")
    print("=" * 55)
    print(f"  Per-period: {args.amount:,.0f} ({args.period})")
    print(f"  Duration: {args.years} years ({args.years * {'daily':252,'weekly':52,'biweekly':26,'monthly':12,'quarterly':4}[args.period]} periods)")
    print(f"  Assumed annual return: {args.annual_return*100:.1f}%")
    print(f"  Assumed volatility: {args.volatility*100:.1f}%")
    print("-" * 55)
    print(f"  Total invested:    {result['total_invested']:>12,.2f}")
    print(f"  Final value:       {result['final_value']:>12,.2f}")
    print(f"  Total return:      {result['total_return']:>+12,.2f}")
    print(f"  Return rate:       {result['return_pct']:>+11.2f}%")
    print(f"  Average cost:      {result['avg_cost']:>12.4f}")
    print("-" * 55)
    print(f"  Fee impact:         {fee_impact:>12,.2f}")
    print("=" * 55)
    print()
    print("  Note: Projections are hypothetical and NOT predictive.")
    print("  Historical returns do not guarantee future results.")
    print()

if __name__ == '__main__':
    main()
