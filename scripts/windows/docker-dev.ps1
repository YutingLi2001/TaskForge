# Start development Docker stack
. "$PSScriptRoot\_common.ps1"

Set-Location $ProjectRoot

Write-Header "Starting Development Docker Stack"

# Check Docker is available
if (-not (Test-DockerAvailable)) {
    Write-Host ""
    Write-Host "Alternative: Run services manually:"
    Write-Host "  Backend:  cd backend && python -m uvicorn app.main:app --reload"
    Write-Host "  Frontend: cd frontend && npm install && npm run dev"
    Wait-ForKeyPress
    exit 1
}

$log = Initialize-LogFile -Prefix "docker-dev"
$composeCmd = Get-ComposeCommand

Write-Info "Using: $composeCmd"
Write-Host ""

# Stop existing services
Write-Host "Stopping existing services..."
& cmd /c "$composeCmd down >> `"$log`" 2>&1"

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
Write-Success "Development stack started!"
Write-Host ""
Write-Host "Frontend: http://localhost:5173/"
Write-Host "Backend:  http://localhost:8000/api/health"
Write-Host ""
Write-Host "To stop:  $composeCmd down"
Write-Host "Log:      $log"

Wait-ForKeyPress
