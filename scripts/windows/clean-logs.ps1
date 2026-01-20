$ErrorActionPreference = 'Stop'

$root = Resolve-Path "$PSScriptRoot\..\.."
$logDir = Join-Path $root 'logs'

if (-not (Test-Path $logDir)) {
  Write-Host "No logs folder found."
  Read-Host "Press Enter to close"
  exit 0
}

$files = Get-ChildItem -Path $logDir -File
if ($files.Count -eq 0) {
  Write-Host "No log files to delete."
  Read-Host "Press Enter to close"
  exit 0
}

$files | Remove-Item -Force
Write-Host "Deleted $($files.Count) log file(s)."
Read-Host "Press Enter to close"
