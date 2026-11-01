#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FundOS 桌面外壳 —— 原生窗口（WebView2），不启动浏览器。

工作方式：
  1. 若 127.0.0.1:8899 没在跑，用项目内的 Python(pythonw) 拉起 dashboard.py --no-browser
  2. 等端口就绪
  3. 用 pywebview 开一个原生窗口加载它（无地址栏、无标签页、无浏览器）

打包：pyinstaller --onefile --windowed --icon assets/fundos.ico --name FundOS app_shell.py
依赖：pywebview（Windows 走系统自带的 WebView2 运行时）
"""
from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8899
URL = f"http://{HOST}:{PORT}"
WINDOW_TITLE = "FundOS 投资驾驶舱"


def _app_root() -> Path:
    """exe 所在目录（打包后）或脚本所在目录（源码运行）。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


ROOT = _app_root()


def _port_open(timeout: float = 0.4) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((HOST, PORT)) == 0


def _python_exe() -> str:
    """找能跑 dashboard.py 的解释器：优先 pythonw（无控制台窗口）。"""
    if not getattr(sys, "frozen", False):
        win = Path(sys.executable).with_name("pythonw.exe")
        return str(win if win.exists() else sys.executable)
    # 打包后：desktop.json 里写的解释器 > 同目录 pythonw > PATH > 已知安装路径
    cfg = ROOT / "desktop.json"
    if cfg.exists():
        try:
            p = json.loads(cfg.read_text(encoding="utf-8")).get("pythonw")
            if p and Path(p).exists():
                return p
        except (json.JSONDecodeError, OSError):
            pass
    known = Path.home() / "AppData/Local/Programs/Python/Python312/pythonw.exe"
    if known.exists():
        return str(known)
    import shutil
    return shutil.which("pythonw") or "python"


def _start_server() -> subprocess.Popen | None:
    """起本地服务；已在跑则返回 None。"""
    if _port_open():
        return None
    script = ROOT / "dashboard.py"
    if not script.exists():
        raise SystemExit(f"找不到 {script} —— 请把 FundOS.exe 放在项目目录下运行")
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    proc = subprocess.Popen([_python_exe(), str(script), "--no-browser"],
                            cwd=str(ROOT), creationflags=flags,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(80):          # 最多等 40 秒（首次要算数据）
        if _port_open():
            return proc
        time.sleep(0.5)
    return proc


def main() -> int:
    import webview

    server = _start_server()
    if not _port_open():
        webview.create_window("FundOS 启动失败",
                              html="<h3 style='font-family:sans-serif'>本地服务未能启动</h3>"
                                   "<p style='font-family:sans-serif'>请检查项目目录与 Python 环境，"
                                   "或直接运行 启动FundOS.cmd 查看报错。</p>",
                              width=520, height=220, background_color="#0b1626")
        webview.start()
        return 1

    window = webview.create_window(
        WINDOW_TITLE, URL,
        width=1500, height=940, min_size=(1080, 700),
        background_color="#060e1a",
        easy_drag=False, text_select=True,
    )

    def _on_closed():
        # 只关掉"本进程拉起的"服务，别把计划任务常驻的那个也杀了
        if server is not None and server.poll() is None:
            server.terminate()

    window.events.closed += _on_closed
    webview.start(gui="edgechromium", debug=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
