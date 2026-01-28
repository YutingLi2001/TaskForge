# Start development Docker stack with fresh database
. "$PSScriptRoot\_common.ps1"

Set-Location $ProjectRoot

Write-Header "Resetting Development Docker Stack"
Write-Warning "This will DELETE the database volume!"

# Check Docker is available
if (-not (Test-DockerAvailable)) {
    Wait-ForKeyPress
    exit 1
}

$log = Initialize-LogFile -Prefix "docker-dev-reset"
$composeCmd = Get-ComposeCommand

Write-Info "Using: $composeCmd"
Write-Host ""

# Stop and remove volumes
Write-Host "Stopping services and removing volumes..."
& cmd /c "$composeCmd down -v >> `"$log`" 2>&1"

# Build and start
Write-Host "Building and starting services..."
& cmd /c "$composeCmd up --build -d >> `"$log`" 2>&1"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to start services. See log: $log"
    Wait-ForKeyPress
    exit 1
}

# Show status
Write-Host ""
& cmd /c "$composeCmd ps"

Write-Host ""
Write-Success "Development stack started (DB reset)!"
Write-Host ""
Write-Host "Frontend: http://localhost:5173/"
Write-Host "Backend:  http://localhost:8000/api/health"
Write-Host ""
Write-Host "To stop:  $composeCmd down"
Write-Host "Log:      $log"

Wait-ForKeyPress
