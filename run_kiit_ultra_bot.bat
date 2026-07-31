@echo off
setlocal

title KIIT Ultra Bot
chcp 65001 >nul

cd /d "%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"

where py >nul 2>&1
if %errorlevel%==0 (
    py -3 "%~dp0kiit_ultra_bot.py"
) else (
    python "%~dp0kiit_ultra_bot.py"
)

echo.
echo Bot exited with code %errorlevel%.
pause
