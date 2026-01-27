# Run all linters (ruff for backend, eslint for frontend)
. "$PSScriptRoot\_common.ps1"

Set-Location $ProjectRoot

Write-Header "Running Linters"

$log = Initialize-LogFile -Prefix "lint"
$backendFailed = $false
$frontendFailed = $false

# ========================================
# Backend Linting (ruff)
# ========================================
Write-Info "=== Backend Linting (ruff) ==="
Write-Host ""

if (Test-PythonAvailable) {
    if (Test-CommandExists "ruff") {
        & cmd /c "ruff check backend/ 2>&1" | Tee-Object -FilePath $log -Append
        if ($LASTEXITCODE -ne 0) {
            $backendFailed = $true
        } else {
            Write-Success "Backend: All checks passed!"
        }
    } else {
        Write-Warning "ruff not installed. Run: pip install ruff"
        $backendFailed = $true
    }
} else {
    $backendFailed = $true
}

Write-Host ""

# ========================================
# Frontend Linting (eslint)
# ========================================
Write-Info "=== Frontend Linting (eslint) ==="
Write-Host ""

if (Test-NodeAvailable) {
    Set-Location (Join-Path $ProjectRoot "frontend")
    & cmd /c "npm run lint 2>&1" | Tee-Object -FilePath $log -Append
    if ($LASTEXITCODE -ne 0) {
        $frontendFailed = $true
    } else {
        Write-Success "Frontend: All checks passed!"
    }
    Set-Location $ProjectRoot
} else {
    $frontendFailed = $true
}

# ========================================
# Summary
# ========================================
Write-Host ""
Write-Header "Lint Summary"

if ($backendFailed) {
    Write-Error "Backend lint: FAILED"
} else {
    Write-Success "Backend lint: PASSED"
}

if ($frontendFailed) {
    Write-Error "Frontend lint: FAILED"
} else {
    Write-Success "Frontend lint: PASSED"
}

Write-Host ""
Write-Host "Log saved to: $log"

if ($backendFailed -or $frontendFailed) {
    Write-Error "Linting failed!"
    Wait-ForKeyPress
    exit 1
} else {
    Write-Success "All linting passed!"
    Wait-ForKeyPress
    exit 0
}
