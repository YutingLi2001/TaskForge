$ErrorActionPreference = 'Continue'
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

$root = Resolve-Path "$PSScriptRoot\..\.."
Set-Location $root

$logDir = Join-Path $root 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$log = Join-Path $logDir "backend-tests-$ts.log"

Write-Host "Running backend tests..."
Write-Host "Ensuring backend dependencies..."
& cmd /c "pip install -r backend\\requirements.txt >> `"$log`" 2>&1"
if ($LASTEXITCODE -ne 0) {
  Write-Host "Dependency install failed. See log: $log"
  Read-Host "Press Enter to close"
  exit 1
}

Write-Host "Ensuring compatible bcrypt version..."
& cmd /c "pip install bcrypt==3.2.2 --force-reinstall >> `"$log`" 2>&1"
if ($LASTEXITCODE -ne 0) {
  Write-Host "bcrypt install failed. See log: $log"
  Read-Host "Press Enter to close"
  exit 1
}

& cmd /c "python -m unittest discover -s backend\\tests >> `"$log`" 2>&1"
if ($LASTEXITCODE -ne 0) {
  Write-Host "Tests failed. See log: $log"
  Read-Host "Press Enter to close"
  exit 1
}

Write-Host "Tests passed. Log saved to $log"
Read-Host "Press Enter to close"
