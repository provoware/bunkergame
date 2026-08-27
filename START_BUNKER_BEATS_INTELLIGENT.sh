#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
exec python3 Launcher/gui/repair_gui.py
