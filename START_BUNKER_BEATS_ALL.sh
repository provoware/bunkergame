#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
echo "=============================================="
echo "BUNKER BEATS - AUTOSTART ALL 2.2"
echo "=============================================="
echo
python3 Scripts/diagnose_autostart.py || exit $?
echo
python3 Scripts/orchestrator.py --format
rc=$?
echo
echo "Report: Diagnostics/Reports/orchestrator_report.json"
echo "Return code: $rc"
exit "$rc"
