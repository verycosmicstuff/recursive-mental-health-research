@echo off
cd /d %~dp0

echo =========================================
echo Starting Mental Health Dashboard...
echo =========================================
:: Start dashboard in the background but invisible console using a tiny VBS hack or just START /B
start /B cmd /c "python dashboard.py"

echo Waiting a second for the dashboard server to spin up...
timeout /t 2 /nobreak >nul
start http://127.0.0.1:5000

echo =========================================
echo Starting Autonomous Research Loop...
echo =========================================
:: This will take over the main console and show the research loop visibly
python main.py

pause
