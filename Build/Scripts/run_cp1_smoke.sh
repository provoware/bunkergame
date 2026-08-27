#!/usr/bin/env bash
set -u
if [ "$#" -lt 2 ]; then
  echo "usage: $0 <UnrealRoot> <ProjectFile> [AutomationFilter]"
  exit 2
fi
UE_ROOT="$1"
PROJECT="$2"
FILTER="${3:-BunkerBeats.Smoke}"
UAT="$UE_ROOT/Engine/Build/BatchFiles/RunUAT.sh"
if [ ! -x "$UAT" ]; then
  echo "RunUAT.sh not found: $UAT"
  exit 3
fi
"$UAT" RunUnreal \
  "-test=UE.EditorAutomation" \
  "-runtest=$FILTER" \
  "-project=$PROJECT" \
  "-build=editor"
exit $?
