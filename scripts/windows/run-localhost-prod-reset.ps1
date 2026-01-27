$ErrorActionPreference = 'Stop'

$root = Resolve-Path "$PSScriptRoot\..\.."
Set-Location $root

$logDir = Join-Path $root 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$log = Join-Path $logDir "localhost-prod-reset-$ts.log"

Write-Host "Resetting PRODUCTION localhost services (will remove DB volume)..."
Write-Host ""

# Check Docker installation
$docker = Get-Command docker -ErrorAction SilentlyContinue
if (-not $docker) {
  Write-Host "ERROR: Docker not found. Install Docker Desktop."
  "Docker not found." | Out-File -FilePath $log -Encoding ASCII
  Read-Host "Press Enter to close"
  exit 1
}

# Check Docker is running
& cmd /c "docker info >> `"$log`" 2>&1"
if ($LASTEXITCODE -ne 0) {
  Write-Host "ERROR: Docker is installed but not running. Start Docker Desktop and try again."
  Write-Host "See log: $log"
  Read-Host "Press Enter to close"
  exit 1
}

# Check .env file exists
$envFile = Join-Path $root '.env'
if (-not (Test-Path $envFile)) {
  Write-Host "WARNING: .env file not found. Copying from .env.example..."
  Copy-Item (Join-Path $root '.env.example') $envFile
  Write-Host "Created .env from .env.example. Review and update values for production."
}

# Detect compose command
$useComposeV2 = $false
& cmd /c "docker compose version >> `"$log`" 2>&1"
if ($LASTEXITCODE -eq 0) { $useComposeV2 = $true }

$composeCmd = if ($useComposeV2) { "docker compose" } else { "docker-compose" }
$composeFile = "docker-compose.prod.yml"

Write-Host "Using: $composeCmd -f $composeFile"
Write-Host ""

# Stop and remove volumes
Write-Host "Stopping services and removing volumes (DB will be reset)..."
& cmd /c "$composeCmd -f $composeFile down -v >> `"$log`" 2>&1"

# Build and start
Write-Host "Building production images (this may take a few minutes)..."
& cmd /c "$composeCmd -f $composeFile build >> `"$log`" 2>&1"
if ($LASTEXITCODE -ne 0) {
  Write-Host "ERROR: Failed to build images. See log: $log"
  Read-Host "Press Enter to close"
  exit 1
}

Write-Host "Starting production services..."
& cmd /c "$composeCmd -f $composeFile up -d >> `"$log`" 2>&1"
if ($LASTEXITCODE -ne 0) {
  Write-Host "ERROR: Failed to start services. See log: $log"
  Read-Host "Press Enter to close"
  exit 1
}

# Wait for health checks
Write-Host ""
Write-Host "Waiting for containers to become healthy..."
$maxWait = 120
$waited = 0
$interval = 5

while ($waited -lt $maxWait) {
  Start-Sleep -Seconds $interval
  $waited += $interval

  $status = & cmd /c "$composeCmd -f $composeFile ps --format json 2>&1"
  $healthy = ($status | Select-String -Pattern '"Health":"healthy"' -AllMatches).Matches.Count
  $total = ($status | Select-String -Pattern '"Service"' -AllMatches).Matches.Count

  Write-Host "  [$waited s] Health check: $healthy/$total containers healthy"

  if ($healthy -ge 3) {
    Write-Host ""
    Write-Host "All containers healthy!"
    break
  }
}

if ($waited -ge $maxWait) {
  Write-Host ""
  Write-Host "WARNING: Timed out waiting for health checks. Some containers may still be starting."
}

# Show status
Write-Host ""
Write-Host "Container status:"
& cmd /c "$composeCmd -f $composeFile ps"

# Verify non-root users
Write-Host ""
Write-Host "Security check (non-root users):"
$backendUser = & cmd /c "docker exec taskforge-backend-1 whoami 2>&1"
$frontendUser = & cmd /c "docker exec taskforge-frontend-1 whoami 2>&1"
Write-Host "  Backend runs as:  $backendUser"
Write-Host "  Frontend runs as: $frontendUser"

if ($backendUser -eq "root" -or $frontendUser -eq "root") {
  Write-Host "WARNING: Containers running as root - check Dockerfile.prod"
}

# Show URLs
Write-Host ""
Write-Host "=========================================="
Write-Host "PRODUCTION services started (DB reset)!"
Write-Host "=========================================="
Write-Host "Frontend: http://localhost/"
Write-Host "API:      http://localhost/api/health"
Write-Host ""
Write-Host "To stop:  $composeCmd -f $composeFile down"
Write-Host "Log:      $log"
Write-Host ""
Read-Host "Press Enter to close"
