@echo off
chcp 65001 >nul
rem FundOS 启动器：已在运行则只把窗口叫出来，未运行则先起服务再开应用窗口
setlocal
set "PYW=C:\Users\lzf13\AppData\Local\Programs\Python\Python312\pythonw.exe"
if not exist "%PYW%" set "PYW=pythonw"
start "" "%PYW%" "%~dp0dashboard.py" --app
endlocal
