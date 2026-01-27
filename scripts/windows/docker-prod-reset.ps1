# Start production Docker stack with fresh database
. "$PSScriptRoot\_common.ps1"

Set-Location $ProjectRoot

Write-Header "Resetting Production Docker Stack"
Write-Warning "This will DELETE the database volume!"

# Check Docker is available
if (-not (Test-DockerAvailable)) {
    Wait-ForKeyPress
    exit 1
}

# Check .env file exists
$envFile = Join-Path $ProjectRoot '.env'
if (-not (Test-Path $envFile)) {
    Write-Warning ".env file not found. Copying from .env.example..."
    Copy-Item (Join-Path $ProjectRoot '.env.example') $envFile
    Write-Host "Created .env from .env.example. Review and update values for production."
}

$log = Initialize-LogFile -Prefix "docker-prod-reset"
$composeCmd = Get-ComposeCommand
$composeFile = "docker-compose.prod.yml"

Write-Info "Using: $composeCmd -f $composeFile"
Write-Host ""

# Stop and remove volumes
Write-Host "Stopping services and removing volumes..."
& cmd /c "$composeCmd -f $composeFile down -v >> `"$log`" 2>&1"

# Build
Write-Host "Building production images (this may take a few minutes)..."
& cmd /c "$composeCmd -f $composeFile build >> `"$log`" 2>&1"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to build images. See log: $log"
    Wait-ForKeyPress
    exit 1
}

# Start
Write-Host "Starting production services..."
& cmd /c "$composeCmd -f $composeFile up -d >> `"$log`" 2>&1"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to start services. See log: $log"
    Wait-ForKeyPress
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
        Write-Success "All containers healthy!"
        break
    }
}

if ($waited -ge $maxWait) {
    Write-Warning "Timed out waiting for health checks."
}

# Show status
Write-Host ""
& cmd /c "$composeCmd -f $composeFile ps"

# Security check
Write-Host ""
Write-Info "Security check (non-root users):"
$backendUser = & cmd /c "docker exec taskforge-backend-1 whoami 2>&1"
$frontendUser = & cmd /c "docker exec taskforge-frontend-1 whoami 2>&1"
Write-Host "  Backend:  $backendUser"
Write-Host "  Frontend: $frontendUser"

Write-Host ""
Write-Success "Production stack started (DB reset)!"
Write-Host ""
Write-Host "Frontend: http://localhost/"
Write-Host "API:      http://localhost/api/health"
Write-Host ""
Write-Host "To stop:  $composeCmd -f $composeFile down"
Write-Host "Log:      $log"

Wait-ForKeyPress
