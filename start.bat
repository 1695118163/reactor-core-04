@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [reactor] 起本地静态服务 http://127.0.0.1:8778/
start "reactor server" /min python -m http.server 8778 --bind 127.0.0.1
timeout /t 2 >nul
start "" chrome "http://127.0.0.1:8778/"
echo 关掉那个最小化的 "reactor server" 窗口即可停止服务。
pause
