import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path(r"D:\基金项目\manual_updates.json")
data = {"updates": {}}
if DATA_FILE.exists():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

today = datetime.now().strftime("%Y-%m-%d")
now = datetime.now().strftime("%H:%M:%S")

updates = {
    "022365": {"name": "科技智选", "date": today, "day_change_pct": 5.32, "source": "manual", "input_time": now},
    "019024": {"name": "信息产业", "date": today, "day_change_pct": 3.72, "source": "manual", "input_time": now},
    "020684": {"name": "半导体", "date": today, "day_change_pct": 2.68, "source": "manual", "input_time": now},
    "019173": {"name": "纳斯达克100", "date": today, "day_change_pct": 3.09, "source": "manual", "input_time": now},
    "011608": {"name": "科创50联接", "date": today, "day_change_pct": 2.84, "source": "manual", "input_time": now},
    "017641": {"name": "标普500", "date": today, "day_change_pct": 1.60, "source": "manual", "input_time": now},
    "018735": {"name": "华夏绿电", "date": today, "day_change_pct": 0.23, "source": "manual", "input_time": now},
    "018354": {"name": "全球成长", "date": today, "day_change_pct": 0.85, "source": "manual", "input_time": now},
}

data["updates"][today] = updates
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Saved {len(updates)} funds to {DATA_FILE}")
