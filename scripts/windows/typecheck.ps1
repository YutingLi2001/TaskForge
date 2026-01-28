# Run type checking (TypeScript for frontend)
. "$PSScriptRoot\_common.ps1"

Set-Location $ProjectRoot

Write-Header "Running Type Checks"

$log = Initialize-LogFile -Prefix "typecheck"
$failed = $false

# ========================================
# Frontend Type Checking (TypeScript)
# ========================================
Write-Info "=== Frontend Type Checking (tsc) ==="
Write-Host ""

if (Test-NodeAvailable) {
    Set-Location (Join-Path $ProjectRoot "frontend")

    # Check if typecheck script exists in package.json
    $packageJson = Get-Content "package.json" | ConvertFrom-Json
    if ($packageJson.scripts.typecheck) {
        & cmd /c "npm run typecheck 2>&1" | Tee-Object -FilePath $log -Append
    } else {
        # Fallback to direct tsc
        & cmd /c "npx tsc --noEmit 2>&1" | Tee-Object -FilePath $log -Append
    }

    if ($LASTEXITCODE -ne 0) {
        $failed = $true
    } else {
        Write-Success "TypeScript: No errors found!"
    }
    Set-Location $ProjectRoot
} else {
    $failed = $true
}

# ========================================
# Summary
# ========================================
Write-Host ""
Write-Host "Log saved to: $log"

if ($failed) {
    Write-Error "Type checking failed!"
    Wait-ForKeyPress
    exit 1
} else {
    Write-Success "All type checks passed!"
    Wait-ForKeyPress
    exit 0
}
