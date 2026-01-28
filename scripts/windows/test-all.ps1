# Run all tests (backend + frontend)
. "$PSScriptRoot\_common.ps1"

Set-Location $ProjectRoot

Write-Header "Running All Tests"

$log = Initialize-LogFile -Prefix "test-all"
$backendFailed = $false
$frontendFailed = $false

# ========================================
# Backend Tests
# ========================================
Write-Info "=== Backend Tests (pytest) ==="
Write-Host ""

if (Test-PythonAvailable) {
    $env:PYTHONPATH = $ProjectRoot
    & cmd /c "python -m pytest backend/tests/ -v --tb=short 2>&1" | Tee-Object -FilePath $log -Append
    if ($LASTEXITCODE -ne 0) {
        $backendFailed = $true
    }
} else {
    $backendFailed = $true
}

Write-Host ""

# ========================================
# Frontend Tests
# ========================================
Write-Info "=== Frontend Tests (vitest) ==="
Write-Host ""

if (Test-NodeAvailable) {
    Set-Location (Join-Path $ProjectRoot "frontend")
    & cmd /c "npm test -- --run 2>&1" | Tee-Object -FilePath $log -Append
    if ($LASTEXITCODE -ne 0) {
        $frontendFailed = $true
    }
    Set-Location $ProjectRoot
} else {
    $frontendFailed = $true
}

# ========================================
# Summary
# ========================================
Write-Host ""
Write-Header "Test Summary"

if ($backendFailed) {
    Write-Error "Backend tests: FAILED"
} else {
    Write-Success "Backend tests: PASSED"
}

if ($frontendFailed) {
    Write-Error "Frontend tests: FAILED"
} else {
    Write-Success "Frontend tests: PASSED"
}

Write-Host ""
Write-Host "Log saved to: $log"

if ($backendFailed -or $frontendFailed) {
    Write-Error "Some tests failed!"
    Wait-ForKeyPress
    exit 1
} else {
    Write-Success "All tests passed!"
    Wait-ForKeyPress
    exit 0
}
