#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FundOS 自动化流水线 v1.0（阶段1：自动化闭环）

用法:
  python auto_pipeline.py morning     # ~09:00 晨报: 隔夜美股代理 + 昨日触发 + 今日前瞻
  python auto_pipeline.py afternoon   # ~15:30 盘后: 触发线复核 → 命中即弹窗/推送警报
  python auto_pipeline.py evening     # ~20:30 晚报: 全引擎链路 + 晚报简报 + 通知
  python auto_pipeline.py install     # 注册 Windows 计划任务（工作日 09:00/15:30/20:30 + 开机补跑）
  python auto_pipeline.py uninstall   # 注销计划任务
  python auto_pipeline.py status      # 查看已注册任务
  python auto_pipeline.py catchup     # 补跑当天错过的时点（开机任务自动调用）

输出: fundos_morning_YYYY-MM-DD.md / fundos_evening_YYYY-MM-DD.md + Windows 弹窗
      （配置 FUNDOS_SCT_KEY 环境变量后晚间自动推送微信，见 notify.py）

补跑机制（电脑不一定常开）:
  - 计划任务带 StartWhenAvailable(错过后下次开机补跑) + WakeToRun(睡眠可唤醒)
  - 注册登录触发任务 FundOS-Catchup: 登录时检查当天漏跑的时点并按序补跑
  - 状态记录 data/state/auto_state.json；手动跑过的时点不会重复补跑
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from fundos_config import (  # noqa: E402
    DAILY_RESULT, NEWS_JSON, SECTOR_LABEL, DATA_DIR,
)
from notify import notify, log  # noqa: E402

ANALYTICS_RESULT = ROOT / "fund_analytics_result.json"
STATE_FILE = DATA_DIR / "state" / "auto_state.json"

TASKS = [
    ("FundOS-Morning",   "morning",   "09:00"),
    ("FundOS-Afternoon", "afternoon", "15:30"),
    ("FundOS-Evening",   "evening",   "20:30"),
]
WEEKDAYS = "MON,TUE,WED,THU,FRI"
STAGE_TIMES = {cmd: t for _, cmd, t in TASKS}


# ============================================================
# 状态记录（供 catchup 判断当天某时点是否已跑过）
# ============================================================
def load_state():
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def mark_state(stage):
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        state = load_state()
        state[stage] = datetime.now().strftime("%Y-%m-%d %H:%M")
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=1),
                              encoding="utf-8")
    except OSError:
        pass


# ============================================================
# 纯函数（可单测）：简报与警报文本生成
# ============================================================
def format_trigger_alert(actions):
    """把 daily_check 的 actions 列表压成一行警报文本。"""
    if not actions:
        return "无触发，全部持有观察 ✅"
    # actions 形如 "🟡 全球成长 [012922] 体检逻辑, 反弹分批退出"
    names = []
    for a in actions:
        parts = a.split(" ", 1)
        if len(parts) > 1:
            name = parts[1].split(" [")[0]
            names.append(name)
    return f"触发 {len(actions)} 项: {'、'.join(names)} ⚠️"


def build_morning_lines(indices, global_idx, daily):
    """晨报正文（数据缺失时优雅降级）。"""
    lines = [
        "# FundOS 晨报",
        f"> {datetime.now().strftime('%Y-%m-%d %H:%M')} 生成 | 隔夜收盘 + 今日前瞻",
        "",
        "## 一、隔夜市场（QDII 代理）",
        "",
    ]
    if global_idx:
        for code, idx in sorted(global_idx.items()):
            emoji = "🟢" if idx["chg_pct"] > 0 else ("🔴" if idx["chg_pct"] < 0 else "⚪")
            lines.append(f"- {emoji} {idx['name']}: {idx['price']:,.2f} ({idx['chg_pct']:+.2f}%)")
    else:
        lines.append("- (指数获取失败，请查看 fundos_core 输出)")
    lines += ["", "## 二、A股盘面", ""]
    if indices:
        for code in ("sh000001", "sh000688", "sz399006"):
            idx = indices.get(code)
            if idx:
                emoji = "🟢" if idx["chg_pct"] > 0 else ("🔴" if idx["chg_pct"] < 0 else "⚪")
                lines.append(f"- {emoji} {idx['name']}: {idx['price']:,.2f} ({idx['chg_pct']:+.2f}%)")
    else:
        lines.append("- (未取到实时指数)")
    lines += ["", "## 三、昨日触发与今日关注", ""]
    if daily:
        actions = daily.get("actions", [])
        if actions:
            for a in actions:
                lines.append(f"- ⚠️ {a}")
            lines.append("")
            lines.append("> 触发项须在今日 15:00 前执行，分批≤1/3，间隔≥1周。")
        else:
            lines.append("- 昨日无触发，全部持有观察")
        qdii_w = daily.get("qdii_weight", 0)
        tech_w = daily.get("tech_weight", 0)
        lines.append(f"- 仓位基准: 科技/AI {tech_w:.1f}%（≤40） | QDII {qdii_w:.1f}%（≤40）")
    else:
        lines.append("- (无盘后检查数据，请先运行 daily_check.py)")
    lines += ["", "## 四、今日纪律", "",
              "- 不追高、不接飞刀、不摊平；永远保留 10-20% 弹药。",
              "- 15:00 前提交按当日净值，15:00 后顺延。",
              "",
              "> 本简报为客观数据汇总，不构成投资建议。"]
    return lines


def build_evening_lines(engine_result, daily, analytics, news):
    """晚报正文。"""
    lines = [
        "# FundOS 晚报",
        f"> {datetime.now().strftime('%Y-%m-%d %H:%M')} 生成 | 全引擎链路完成",
        "",
    ]
    if daily:
        lines += [
            "## 一、今日净值与触发",
            "",
            f"- 组合估算市值: **¥{daily.get('total_value', 0):,.0f}** | 总盈亏: **{daily.get('total_ret_pct', 0):+.2f}%**",
            f"- 科技/AI: {daily.get('tech_weight', 0):.1f}% | QDII: {daily.get('qdii_weight', 0):.1f}%",
            f"- 触发: {format_trigger_alert(daily.get('actions', []))}",
            "",
        ]
    if analytics:
        p = analytics.get("portfolio", {})
        if p:
            lines += [
                "## 二、组合风险 (近120日)",
                "",
                f"- 最大回撤: **{p.get('max_dd_pct')}%** | 夏普: **{p.get('sharpe')}** | 年化波动: {p.get('ann_vol_pct')}%",
                f"- HHI 集中度: {p.get('hhi')}（有效基金数 ~{p.get('effective_funds')}）",
                "",
            ]
    decision = (engine_result or {}).get("decision", {})
    if decision:
        lines += ["## 三、引擎决策（总裁批示摘要）", ""]
        for item in decision.get("triggered", []):
            lines.append(f"- **{item['action']}**")
            lines.append(f"  - 边界: {item['boundary']}")
        lines.append("")
    if news:
        items = news.get("news", [])[:5]
        s_idx = news.get("sentiment_index") or {}
        if items or s_idx:
            lines += ["## 四、要闻与情绪", ""]
            if s_idx:
                idx_val = s_idx.get("index", 50)
                label = ("偏暖" if idx_val >= 60 else "偏冷" if idx_val <= 40 else "中性")
                lines.append(f"- 今日情绪指数: **{idx_val}**（{label}，50=中性；"
                             f"新闻情绪仅作观察，不单独触发操作）")
            for n in items:
                lines.append(f"- {n.get('sentiment', '')} [{n.get('source', '')}] {n.get('title', '')[:60]}")
            lines.append("")
    lines += ["## 五、明日计划", "",
              "- 触发项在明日 15:00 前执行；未触发则持有观察。",
              "- 详细报告见 fund_engine_report.md / fund_analytics_report.md / daily_check.md",
              "",
              "> 本简报为客观数据汇总，不构成投资建议。"]
    return lines


# ============================================================
# 数据读取
# ============================================================
def _load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _run(script, *args):
    result = subprocess.run([sys.executable, str(ROOT / script), *args],
                            cwd=ROOT, text=True, encoding="utf-8", errors="replace",
                            capture_output=True, timeout=600)
    if result.returncode != 0:
        log(f"{script} 退出码 {result.returncode}: {result.stderr[-300:]}", "ERROR")
    return result.returncode


# ============================================================
# 三条流水线
# ============================================================
def run_morning():
    log("晨报流水线启动")
    import fundos_data
    indices, global_idx, daily = {}, {}, {}
    try:
        indices = fundos_data.fetch_indices(["sh000001", "sh000688", "sz399006"])
    except fundos_data.DataError as exc:
        log(f"晨报指数失败: {exc}", "WARN")
    try:
        global_idx = fundos_data.fetch_global_indices(["gb_$dji", "gb_$ixic", "gb_$inx", "gb_hsi"])
    except fundos_data.DataError as exc:
        log(f"晨报全球指数失败: {exc}", "WARN")
    daily = _load_json(DAILY_RESULT)

    lines = build_morning_lines(indices, global_idx, daily)
    out = ROOT / f"fundos_morning_{datetime.now():%Y-%m-%d}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    us = global_idx.get("gb_$ixic", {})
    notify("FundOS 晨报", f"隔夜纳指 {us.get('chg_pct', 0):+.2f}% | 详情见晨报文件",
           push=True, md="\n".join(lines))
    mark_state("morning")
    log(f"晨报完成: {out}")
    return 0


def run_afternoon():
    log("盘后警报流水线启动")
    rc = _run("daily_check.py")
    daily = _load_json(DAILY_RESULT)
    alert = format_trigger_alert(daily.get("actions", []))
    emoji = "⚠️" if daily.get("actions") else "✅"
    lines = _load_json(ANALYTICS_RESULT)  # 复用既有分析（不重复计算）
    detail = ""
    if daily:
        detail = "\n".join(f"- {a}" for a in daily.get("actions", [])) or "- 无触发"
    md = (f"**FundOS 盘后复核 {datetime.now():%Y-%m-%d}**\n\n{detail}\n\n"
          f"触发项须在**下一交易日 15:00 前**执行，分批≤1/3。")
    notify(f"FundOS 盘后 {emoji} {alert}", "触发项明细见推送/日报", push=True, md=md)
    mark_state("afternoon")
    return rc


def run_evening():
    log("晚报流水线启动（全引擎链路）")
    engine_rc = _run("fund_engine.py", "run", "--mode", "quick")
    engine_result = _load_json(ROOT / "fund_engine_result.json")
    daily = _load_json(DAILY_RESULT)
    analytics = _load_json(ANALYTICS_RESULT)
    news = _load_json(NEWS_JSON)

    lines = build_evening_lines(engine_result, daily, analytics, news)
    out = ROOT / f"fundos_evening_{datetime.now():%Y-%m-%d}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    ret = (daily or {}).get("total_ret_pct", 0)
    notify(f"FundOS 晚报 ({ret:+.2f}%)", "组合盈亏/触发/风险指标详见推送",
           push=True, md="\n".join(lines))
    mark_state("evening")
    log(f"晚报完成: {out} | 引擎退出码 {engine_rc}")
    return engine_rc


# ============================================================
# 补跑: 登录/开机后检查当天漏掉的时点
# ============================================================
def stages_missed(state, now=None):
    """纯函数：返回当天已到时但未跑的流水线名列表（按 morning→evening 顺序）。"""
    now = now or datetime.now()
    missed = []
    for stage, t in STAGE_TIMES.items():
        last = state.get(stage, "")
        already_today = last.startswith(now.strftime("%Y-%m-%d"))
        due = now.time() >= datetime.strptime(t, "%H:%M").time()
        if due and not already_today:
            missed.append(stage)
    return missed


def catchup():
    """检查当天已到时但未跑的流水线并按序补跑。幂等：跑过的不重复。"""
    missed = stages_missed(load_state())
    if not missed:
        print("✅ 今日流水线无遗漏")
        return 0
    print(f"🔁 补跑当天遗漏: {' → '.join(missed)}")
    results = {}
    for stage in missed:
        print(f"  ▶ {stage} ...", flush=True)
        results[stage] = {"morning": run_morning, "afternoon": run_afternoon,
                          "evening": run_evening}[stage]()
    bad = [s for s, rc in results.items() if rc != 0]
    print("  ✅ 补跑完成" if not bad else f"  ⚠️ 部分失败: {bad}")
    notify("FundOS 补跑完成", f"补跑: {', '.join(results)}；开机前的时点已自动执行")
    return 0 if not bad else 1


# ============================================================
# 计划任务注册（PowerShell: 支持错过补跑 + 睡眠唤醒 + 登录补跑）
# ============================================================
def _schtasks(*args):
    return subprocess.run(["schtasks", *args], capture_output=True, text=True,
                          encoding="gbk", errors="replace")


def _ps_register(name, command, stime):
    """用 PowerShell 注册当前用户任务: 工作日定时 + 错过补跑 + 睡眠唤醒。"""
    exe = sys.executable.replace("'", "''")
    script = str(ROOT / "auto_pipeline.py").replace("'", "''")
    ps = f"""
$action = New-ScheduledTaskAction -Execute '{exe}' -Argument '\"{script}\" {command}'
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At {stime}
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -ExecutionTimeLimit (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName '{name}' -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
"""
    encoded = __import__("base64").b64encode(ps.encode("utf-16-le")).decode("ascii")
    return subprocess.run(["powershell", "-NoProfile", "-EncodedCommand", encoded],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=60)


def _ps_register_catchup():
    """注册开机补跑。说明: 登录触发计划任务(Register -AtLogOn)需要管理员权限，
    故改用用户级自启动注册表项 HKCU\\...\\Run（无需管理员，登录即跑 catchup）。"""
    run_key = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
    cmd = f'"{sys.executable}" "{ROOT / "auto_pipeline.py"}" catchup'
    r = subprocess.run(["reg", "add", run_key, "/v", "FundOS-Catchup",
                        "/t", "REG_SZ", "/d", cmd, "/f"],
                       capture_output=True, text=True, encoding="gbk", errors="replace")
    if r.returncode != 0:
        print(f"  ❌ Run键注册失败: {r.stderr.strip()[:80]}")
    return r


def _register_dashboard_autostart():
    """看板登录常驻（无窗口模式 pythonw，避免黑色控制台被误关导致服务死亡）。
    端口被占时新实例自动退出。同时在桌面创建「FundOS看板」快捷方式。"""
    run_key = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    exe = str(pythonw if pythonw.exists() else sys.executable)
    cmd = f'"{exe}" "{ROOT / "dashboard.py"}" --no-browser'
    r = subprocess.run(["reg", "add", run_key, "/v", "FundOS-Dashboard",
                        "/t", "REG_SZ", "/d", cmd, "/f"],
                       capture_output=True, text=True, encoding="gbk", errors="replace")
    _create_desktop_shortcut()
    return r


def _create_desktop_shortcut():
    """桌面创建「FundOS看板」一键打开快捷方式（兼容 OneDrive 重定向的桌面）。"""
    candidates = [Path.home() / "Desktop", Path.home() / "OneDrive" / "Desktop"]
    for desktop in candidates:
        if desktop.is_dir():
            try:
                (desktop / "FundOS看板.url").write_text(
                    "[InternetShortcut]\nURL=http://127.0.0.1:8899\n",
                    encoding="utf-8")
                return True
            except OSError:
                continue
    return False


def _remove_run_key():
    run_key = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
    for name in ("FundOS-Catchup", "FundOS-Dashboard"):
        subprocess.run(["reg", "delete", run_key, "/v", name, "/f"],
                       capture_output=True, text=True, encoding="gbk", errors="replace")
    return subprocess.run(["reg", "query", run_key, "/v", "FundOS-Catchup"],
                          capture_output=True, text=True, encoding="gbk", errors="replace")


def install_tasks():
    print("计划任务注册结果（错过自动补跑 + 睡眠唤醒 + 登录补跑）:")
    ok = True
    for name, command, stime in TASKS:
        r = _ps_register(name, command, stime)
        good = r.returncode == 0
        ok = ok and good
        msg = "" if good else (r.stderr or r.stdout).strip()[:120]
        print(f"  {'✅' if good else '❌'} {name} (工作日 {stime}) {msg}")
    r = _ps_register_catchup()
    ok = ok and r.returncode == 0
    if r.returncode == 0:
        print("  ✅ FundOS-Catchup (登录自启动，自动补跑遗漏)")
    r2 = _register_dashboard_autostart()
    ok = ok and r2.returncode == 0
    if r2.returncode == 0:
        print("  ✅ FundOS-Dashboard (登录常驻，弹窗点击跳转的前提)")
    return 0 if ok else 1


def uninstall_tasks():
    for name, _, _ in TASKS:
        r = _schtasks("/Delete", "/F", "/TN", name)
        print(f"  {'✅' if r.returncode == 0 else '❌'} 注销 {name}")
    r = _remove_run_key()
    print(f"  {'✅' if r.returncode == 0 else '❌'} 注销 FundOS-Catchup (登录自启动)")
    return 0


def status_tasks():
    for name, _, stime in TASKS:
        r = _schtasks("/Query", "/TN", name)
        print(f"  {'✅ 已注册' if r.returncode == 0 else '❌ 未注册'} {name} (工作日 {stime})")
    q = subprocess.run(["reg", "query",
                        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
                        "/v", "FundOS-Catchup"], capture_output=True, text=True,
                       encoding="gbk", errors="replace")
    print(f"  {'✅ 已注册' if q.returncode == 0 else '❌ 未注册'} FundOS-Catchup (登录补跑)")
    q2 = subprocess.run(["reg", "query",
                         r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
                         "/v", "FundOS-Dashboard"], capture_output=True, text=True,
                        encoding="gbk", errors="replace")
    print(f"  {'✅ 已注册' if q2.returncode == 0 else '❌ 未注册'} FundOS-Dashboard (登录常驻看板)")
    import urllib.request
    try:
        urllib.request.urlopen("http://127.0.0.1:8899/", timeout=3)
        print("  ✅ 看板服务在线 http://127.0.0.1:8899")
    except OSError:
        print("  ⚠️ 看板服务当前离线（登录自启动后常驻；或手动 python dashboard.py）")
    state = load_state()
    if state:
        print("  执行记录:")
        for stage, ts in state.items():
            print(f"    - {stage}: {ts}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="FundOS 自动化流水线")
    parser.add_argument("command", choices=["morning", "afternoon", "evening",
                                            "install", "uninstall", "status", "catchup"])
    args = parser.parse_args()
    steps = {"morning": run_morning, "afternoon": run_afternoon,
             "evening": run_evening, "install": install_tasks,
             "uninstall": uninstall_tasks, "status": status_tasks,
             "catchup": catchup}
    return steps[args.command]() or 0


if __name__ == "__main__":
    raise SystemExit(main())
