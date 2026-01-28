# Delete all log files
. "$PSScriptRoot\_common.ps1"

Write-Header "Cleaning Log Files"

if (-not (Test-Path $LogDir)) {
    Write-Warning "No logs folder found at: $LogDir"
    Wait-ForKeyPress
    exit 0
}

$files = Get-ChildItem -Path $LogDir -File -Filter "*.log"
if ($files.Count -eq 0) {
    Write-Info "No log files to delete."
    Wait-ForKeyPress
    exit 0
}

Write-Host "Found $($files.Count) log file(s):"
$files | ForEach-Object { Write-Host "  - $($_.Name)" }
Write-Host ""

$files | Remove-Item -Force
Write-Success "Deleted $($files.Count) log file(s)."

Wait-ForKeyPress
