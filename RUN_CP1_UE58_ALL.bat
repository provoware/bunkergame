@echo off
cd /d "%~dp0"
py -3 Scripts\run_cp1_ue58.py
if errorlevel 9009 python Scripts\run_cp1_ue58.py
exit /b %errorlevel%
