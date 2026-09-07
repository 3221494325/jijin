#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FundOS 通知模块 v1.1 — Windows toast 弹窗 + Server酱微信推送 + 日志

零强制依赖：toast 走 PowerShell(Windows 10/11 自带)；
v1.1: toast 改为可交互——点击弹窗/通知中心条目直接用浏览器打开可视化看板；
      duration=long 停留约25秒；过期前保留在通知中心(Win+N)10分钟。
Server酱为可选项——设置环境变量 FUNDOS_SCT_KEY（或写进本文件 SCT_SENDKEY）即启用，
密钥获取: https://sct.ftqq.com/ 。所有通知失败只记日志，绝不中断流水线。
"""
import base64
import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

from fundos_config import DATA_DIR

LOG_DIR = DATA_DIR / "logs"

# 点击 toast 打开的目标（本地看板）
DASHBOARD_URL = "http://127.0.0.1:8899"

# 可选: Server酱 SendKey（留空则只用 Windows 弹窗）。也可用环境变量 FUNDOS_SCT_KEY。
SCT_SENDKEY = ""


def log(msg, tag="INFO"):
    """按天落盘到 data/logs/auto_YYYY-MM-DD.log。"""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        path = LOG_DIR / f"auto_{datetime.now().strftime('%Y-%m-%d')}.log"
        with path.open("a", encoding="utf-8") as fh:
            fh.write(f"[{datetime.now().strftime('%H:%M:%S')}] [{tag}] {msg}\n")
    except OSError:
        pass


def _toast_ps(title, msg, link=DASHBOARD_URL):
    """可交互 toast：点击打开 link（协议激活），长停留，保留通知中心10分钟。
    标题/正文经 base64 传入 + XML转义，避免引号/特殊字符破坏命令或XML。"""
    ps = f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$title = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{base64.b64encode(title.encode("utf-8")).decode("ascii")}'))
$msg = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{base64.b64encode(msg.encode("utf-8")).decode("ascii")}'))
$link = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{base64.b64encode(link.encode("utf-8")).decode("ascii")}'))
$t = [System.Security.SecurityElement]::Escape($title)
$m = [System.Security.SecurityElement]::Escape($msg)
$xml = "<toast activationType='protocol' launch='$link' duration='long'>" +
       "<visual><binding template='ToastGeneric'>" +
       "<text>$t</text><text>$m</text>" +
       "</binding></visual>" +
       "<action content='打开看板' arguments='$link' activationType='protocol'/>" +
       "<audio src='ms-winsoundevent:Notification.Default'/>" +
       "</toast>"
$doc = New-Object Windows.Data.Xml.Dom.XmlDocument
$doc.LoadXml($xml)
$toast = [Windows.UI.Notifications.ToastNotification]::new($doc)
$toast.ExpirationTime = [DateTimeOffset]::Now.AddMinutes(10)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('FundOS 基金引擎').Show($toast)
"""
    encoded = base64.b64encode(ps.encode("utf-16-le")).decode("ascii")
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-EncodedCommand", encoded],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if result.returncode != 0:
            log(f"toast 失败: {result.stderr[:200]}", "WARN")
            return False
        return True
    except (OSError, subprocess.TimeoutExpired) as exc:
        log(f"toast 异常: {exc}", "WARN")
        return False


def _serverchan(title, msg_md):
    """Server酱微信推送（未配置密钥时静默跳过）。"""
    key = SCT_SENDKEY or os.environ.get("FUNDOS_SCT_KEY", "")
    if not key:
        return False
    url = f"https://sctapi.ftqq.com/{key}.send"
    data = urllib.parse.urlencode({"title": title[:32], "desp": msg_md[:30000]}).encode()
    try:
        req = urllib.request.Request(url, data=data)
        resp = json.loads(urllib.request.urlopen(req, timeout=15).read().decode("utf-8"))
        ok = resp.get("code") == 0
        if not ok:
            log(f"Server酱返回异常: {resp}", "WARN")
        return ok
    except (OSError, json.JSONDecodeError, urllib.error.URLError) as exc:
        log(f"Server酱推送失败: {exc}", "WARN")
        return False


def notify(title, msg, *, push=False, md=None):
    """统一通知入口。toast 总是发；push=True 且配置了密钥时走微信。
    md: 微信推送用的 markdown 正文（缺省用 msg）。"""
    log(f"{title} | {msg[:100]}")
    ok_toast = _toast_ps(title, msg)
    ok_push = _serverchan(title, md if md is not None else msg) if push else False
    channels = []
    if ok_toast:
        channels.append("toast")
    if ok_push:
        channels.append("serverchan")
    return channels


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
    ch = notify("FundOS 通知测试", "如果你看到这条弹窗，说明通知通道正常 ✅", push=True,
                md="**FundOS 通知测试**\n\n微信通道正常 ✅")
    print("已送达通道:", " ".join(ch) or "无（toast 失败且未配置 Server酱）")
