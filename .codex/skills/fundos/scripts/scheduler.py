#!/usr/bin/env python3
"""FundOS Scheduled Runner - cron-like daily task support.

Usage:
  python scheduler.py --setup     # Register daily task (Windows Task Scheduler)
  python scheduler.py --run       # Run all daily tasks immediately
  python scheduler.py --list      # List configured tasks
"""

import sys, io, os, subprocess
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SCRIPTS_DIR = Path(__file__).parent
HOLDINGS_DIR = Path.home() / "Desktop"

def find_holdings():
    for f in HOLDINGS_DIR.glob("*.xlsx"):
        if "基金持仓" in f.name or "持仓" in f.name:
            return str(f)
    return None

def run_daily():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"FundOS Daily Run - {now}")
    print("=" * 50)
    
    holdings = find_holdings()
    if not holdings:
        print("ERROR: No holdings file found on Desktop")
        return
    
    # 1. News
    news_out = str(HOLDINGS_DIR / f"news_{datetime.now().strftime('%Y%m%d')}.md")
    print("1/3 Collecting news...")
    subprocess.run([sys.executable, str(SCRIPTS_DIR / "news_fetch_v2.py"), 
                    "--mode", "quick", "--output", news_out],
                   capture_output=True)
    
    # 2. Report
    report_out = str(HOLDINGS_DIR / f"report_{datetime.now().strftime('%Y%m%d')}.md")
    print("2/3 Generating report...")
    subprocess.run([sys.executable, str(SCRIPTS_DIR / "portfolio_report.py"),
                    "--holdings", holdings, "--output", report_out],
                   capture_output=True)
    
    # 3. Briefing
    brief_out = str(HOLDINGS_DIR / f"briefing_{datetime.now().strftime('%Y%m%d')}.md")
    print("3/3 Generating briefing...")
    subprocess.run([sys.executable, str(SCRIPTS_DIR / "daily_briefing.py"),
                    "--holdings", holdings, "--news", news_out, "--output", brief_out],
                   capture_output=True)
    
    print(f"\nDone! Outputs on Desktop:")
    print(f"  News:     {Path(news_out).name}")
    print(f"  Report:   {Path(report_out).name}")
    print(f"  Briefing: {Path(brief_out).name}")

def setup_task():
    """Setup Windows Task Scheduler daily run"""
    script = str(SCRIPTS_DIR / "scheduler.py")
    task_name = "FundOS_Daily_Briefing"
    
    cmd = f'schtasks /create /tn "{task_name}" /tr "python {script} --run" /sc daily /st 18:00 /f'
    print(f"Creating scheduled task: {task_name}")
    print(f"Command: {cmd}")
    result = os.system(cmd)
    if result == 0:
        print("Task created! Runs daily at 18:00")
        print(f"Manage: taskschd.msc -> {task_name}")
    else:
        print("Failed. Try running as Administrator.")

if __name__ == "__main__":
    if "--run" in sys.argv:
        run_daily()
    elif "--setup" in sys.argv:
        setup_task()
    elif "--list" in sys.argv:
        os.system('schtasks /query /tn "FundOS_Daily_Briefing"')
    else:
        print("Usage: python scheduler.py --run | --setup | --list")
