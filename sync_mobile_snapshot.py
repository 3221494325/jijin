#!/usr/bin/env python3
"""Generate and publish the current computer snapshot to GitHub Pages."""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent

def run(*args):
    return subprocess.run(args, cwd=ROOT, text=True, encoding="utf-8", errors="replace")

def main():
    if run(sys.executable, str(ROOT / "export_mobile_snapshot.py")).returncode:
        return 1
    path = ROOT / "mobile_site" / "data.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        data["snapshot_meta"] = {"source": "local_computer", "generated_at": now.isoformat(timespec="seconds"), "timezone": "Asia/Shanghai", "status": "success"}
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        print(f"快照校验失败：{exc}", file=sys.stderr)
        return 1
    files = ["mobile_site/data.json", "mobile_site/index.html"]
    if run("git", "add", "-f", *files).returncode:
        return 1
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
    if staged.returncode == 0:
        print("未发现变化，手机端无需同步。")
        return 0
    if run("git", "commit", "-m", "同步电脑最新手机快照").returncode:
        return 1
    if run("git", "push", "origin", "main").returncode:
        print("推送失败：手机端仍保留上一版快照。", file=sys.stderr)
        return 1
    print("同步提交已推送，等待 GitHub Pages 部署完成。")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
