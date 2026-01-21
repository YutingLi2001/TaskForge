$ErrorActionPreference = 'Continue'
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

$root = Resolve-Path "$PSScriptRoot\..\.."
Set-Location $root

$logDir = Join-Path $root 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$log = Join-Path $logDir "frontend-tests-$ts.log"

Write-Host "Running frontend tests..."
Write-Host "Ensuring frontend dependencies..."
& cmd /c "cd frontend && npm install >> `"$log`" 2>&1"
if ($LASTEXITCODE -ne 0) {
  Write-Host "Dependency install failed. See log: $log"
  Read-Host "Press Enter to close"
  exit 1
}

& cmd /c "cd frontend && npm run test >> `"$log`" 2>&1"
if ($LASTEXITCODE -ne 0) {
  Write-Host "Tests failed. See log: $log"
  Read-Host "Press Enter to close"
  exit 1
}

Write-Host "Tests passed. Log saved to $log"
Read-Host "Press Enter to close"
