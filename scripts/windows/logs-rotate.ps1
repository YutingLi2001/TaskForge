# Keep only the 10 most recent log files, delete older ones
. "$PSScriptRoot\_common.ps1"

$KeepCount = 10

Write-Header "Rotating Log Files (keeping last $KeepCount)"

if (-not (Test-Path $LogDir)) {
    Write-Warning "No logs folder found at: $LogDir"
    Wait-ForKeyPress
    exit 0
}

$files = Get-ChildItem -Path $LogDir -File -Filter "*.log" | Sort-Object LastWriteTime -Descending

if ($files.Count -le $KeepCount) {
    Write-Info "Only $($files.Count) log file(s) found. Nothing to delete."
    Wait-ForKeyPress
    exit 0
}

$toKeep = $files | Select-Object -First $KeepCount
$toDelete = $files | Select-Object -Skip $KeepCount

Write-Host "Keeping $($toKeep.Count) most recent log file(s):"
$toKeep | ForEach-Object { Write-Host "  + $($_.Name)" -ForegroundColor Green }

Write-Host ""
Write-Host "Deleting $($toDelete.Count) older log file(s):"
$toDelete | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor Yellow
    Remove-Item $_.FullName -Force
}

Write-Host ""
Write-Success "Rotation complete. Kept $($toKeep.Count), deleted $($toDelete.Count)."

Wait-ForKeyPress
