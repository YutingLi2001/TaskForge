$ErrorActionPreference = 'Stop'

$root = Resolve-Path "$PSScriptRoot\..\.."
Set-Location $root

$logDir = Join-Path $root 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$log = Join-Path $logDir "localhost-$ts.log"

Write-Host "Starting localhost services..."

$docker = Get-Command docker -ErrorAction SilentlyContinue
if (-not $docker) {
  Write-Host "Docker not found. Install Docker Desktop or run manually:"
  Write-Host "Backend: cd backend && python -m uvicorn app.main:app --reload"
  Write-Host "Frontend: cd frontend && npm install && npm run dev"
  "Docker not found." | Out-File -FilePath $log -Encoding ASCII
  Read-Host "Press Enter to close"
  exit 1
}

& cmd /c "docker info >> `"$log`" 2>&1"
if ($LASTEXITCODE -ne 0) {
  Write-Host "Docker is installed but not running. Start Docker Desktop and try again."
  Write-Host "See log: $log"
  Read-Host "Press Enter to close"
  exit 1
}

$useComposeV2 = $false
& cmd /c "docker compose version >> `"$log`" 2>&1"
if ($LASTEXITCODE -eq 0) { $useComposeV2 = $true }

if ($useComposeV2) {
  Write-Host "Starting services with docker compose (detached)..."
  & cmd /c "docker compose up --build -d >> `"$log`" 2>&1"
} else {
  Write-Host "Starting services with docker-compose (detached)..."
  & cmd /c "docker-compose up --build -d >> `"$log`" 2>&1"
}

if ($LASTEXITCODE -ne 0) {
  Write-Host "Failed to start services. See log: $log"
  Read-Host "Press Enter to close"
  exit 1
}

if ($useComposeV2) {
  & cmd /c "docker compose ps >> `"$log`" 2>&1"
} else {
  & cmd /c "docker-compose ps >> `"$log`" 2>&1"
}

Write-Host "Services started."
Write-Host "Frontend: http://localhost:5173/"
Write-Host "Backend:  http://localhost:8000/api/health"
Write-Host "Log saved to $log"
Read-Host "Press Enter to close"
