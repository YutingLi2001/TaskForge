# Common utilities for TaskForge Windows scripts
# Usage: . "$PSScriptRoot\_common.ps1"

# Error handling - don't stop on first error for better control
$ErrorActionPreference = 'Continue'

# Disable native command error propagation for compatibility
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

# Project root directory
$ProjectRoot = Resolve-Path "$PSScriptRoot\..\.."

# Logs directory
$LogDir = Join-Path $ProjectRoot 'logs'

function Initialize-LogFile {
    param(
        [Parameter(Mandatory)]
        [string]$Prefix
    )

    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    $logPath = Join-Path $LogDir "$Prefix-$ts.log"
    return $logPath
}

function Test-DockerAvailable {
    $docker = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $docker) {
        Write-Error "Docker not found. Install Docker Desktop."
        return $false
    }

    & cmd /c "docker info > nul 2>&1"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker is installed but not running. Start Docker Desktop."
        return $false
    }

    return $true
}

function Get-ComposeCommand {
    & cmd /c "docker compose version > nul 2>&1"
    if ($LASTEXITCODE -eq 0) {
        return "docker compose"
    }
    return "docker-compose"
}

function Write-Success {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "WARNING: $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "ERROR: $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Wait-ForKeyPress {
    Read-Host "Press Enter to close"
}

function Test-PythonAvailable {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Error "Python not found. Install Python 3.11+."
        return $false
    }
    return $true
}

function Test-NodeAvailable {
    $node = Get-Command node -ErrorAction SilentlyContinue
    if (-not $node) {
        Write-Error "Node.js not found. Install Node.js 20+."
        return $false
    }
    return $true
}

function Test-CommandExists {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}
