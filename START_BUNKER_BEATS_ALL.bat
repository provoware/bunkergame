@echo off
setlocal
cd /d "%~dp0"
title BUNKER BEATS - AUTOSTART ALL
echo ==================================================
echo BUNKER BEATS - AUTOSTART ALL
echo ==================================================
echo.
echo Run without Unreal:
python Scripts\orchestrator.py --format
set CORE_RC=%ERRORLEVEL%
echo.
echo Optional Unreal 5.8 build/PIE/package:
echo   python Scripts\orchestrator.py --format --unreal-build
echo   python Scripts\orchestrator.py --format --unreal-build --unreal-pie
echo   python Scripts\orchestrator.py --format --unreal-build --unreal-pie --unreal-package
echo.
echo Report:
echo   Diagnostics\Reports\orchestrator_report.json
exit /b %CORE_RC%
