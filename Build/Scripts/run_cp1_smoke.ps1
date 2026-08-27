param(
  [Parameter(Mandatory=$true)][string]$UnrealRoot,
  [Parameter(Mandatory=$true)][string]$ProjectFile,
  [string]$AutomationFilter = "BunkerBeats.Smoke",
  [string]$Platform = "Win64"
)

$ErrorActionPreference = "Stop"
$uat = Join-Path $UnrealRoot "Engine\Build\BatchFiles\RunUAT.bat"
if (!(Test-Path $uat)) { throw "RunUAT.bat not found: $uat" }
if (!(Test-Path $ProjectFile)) { throw "Project file not found: $ProjectFile" }

& $uat RunUnreal `
  -test=UE.EditorAutomation `
  "-runtest=$AutomationFilter" `
  "-project=$ProjectFile" `
  "-build=editor"
exit $LASTEXITCODE
