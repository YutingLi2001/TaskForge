# Run backend tests with pytest and coverage
. "$PSScriptRoot\_common.ps1"

Set-Location $ProjectRoot

Write-Header "Running Backend Tests (pytest)"

# Check Python is available
if (-not (Test-PythonAvailable)) {
    Wait-ForKeyPress
    exit 1
}

# Initialize log file
$log = Initialize-LogFile -Prefix "test-backend"

# Install dependencies if needed
Write-Info "Checking dependencies..."
& cmd /c "pip install -r backend\requirements.txt -q >> `"$log`" 2>&1"

# Run pytest with coverage (uses pytest.ini config)
Write-Info "Running pytest with coverage..."
Write-Host ""

$env:PYTHONPATH = $ProjectRoot
& cmd /c "python -m pytest backend/tests/ -v --tb=short 2>&1" | Tee-Object -FilePath $log -Append

$testResult = $LASTEXITCODE

Write-Host ""
if ($testResult -eq 0) {
    Write-Success "All backend tests passed!"
    Write-Host "Coverage report: htmlcov/index.html"
} else {
    Write-Error "Some tests failed. Exit code: $testResult"
}

Write-Host "Log saved to: $log"
Wait-ForKeyPress
exit $testResult
