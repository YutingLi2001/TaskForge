# Run frontend tests with vitest and coverage
. "$PSScriptRoot\_common.ps1"

Set-Location $ProjectRoot

Write-Header "Running Frontend Tests (vitest)"

# Check Node is available
if (-not (Test-NodeAvailable)) {
    Wait-ForKeyPress
    exit 1
}

# Initialize log file
$log = Initialize-LogFile -Prefix "test-frontend"

# Install dependencies if needed
Write-Info "Checking dependencies..."
Set-Location (Join-Path $ProjectRoot "frontend")
& cmd /c "npm install --silent >> `"$log`" 2>&1"

# Run vitest with coverage
Write-Info "Running vitest with coverage..."
Write-Host ""

& cmd /c "npm test -- --run --coverage 2>&1" | Tee-Object -FilePath $log -Append

$testResult = $LASTEXITCODE

Set-Location $ProjectRoot

Write-Host ""
if ($testResult -eq 0) {
    Write-Success "All frontend tests passed!"
    Write-Host "Coverage report: frontend/coverage/index.html"
} else {
    Write-Error "Some tests failed. Exit code: $testResult"
}

Write-Host "Log saved to: $log"
Wait-ForKeyPress
exit $testResult
