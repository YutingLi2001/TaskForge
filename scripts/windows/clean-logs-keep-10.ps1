$ErrorActionPreference = 'Stop'

$root = Resolve-Path "$PSScriptRoot\..\.."
$logDir = Join-Path $root 'logs'

if (-not (Test-Path $logDir)) {
  Write-Host "No logs folder found."
  Read-Host "Press Enter to close"
  exit 0
}

$files = Get-ChildItem -Path $logDir -File | Sort-Object LastWriteTime -Descending
if ($files.Count -le 10) {
  Write-Host "No cleanup needed. Found $($files.Count) log file(s)."
  Read-Host "Press Enter to close"
  exit 0
}

$toDelete = $files | Select-Object -Skip 10
$toDelete | Remove-Item -Force

Write-Host "Deleted $($toDelete.Count) old log file(s). Kept latest 10."
Read-Host "Press Enter to close"
