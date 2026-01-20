<#
.SYNOPSIS
    Unified Boot Script for arifOS v49 (Single Body)

.DESCRIPTION
    Ignites the arifOS runtime in either Cloud (SSE) or Local (STDIO) mode.
    Handles environment loading, wiring verification, and server startup.

.PARAMETER Mode
    'Cloud' (default) - Starts SSE server on Port 8000 (new window).
    'Local' - Starts STDIO server (blocking, for IDE/Agent use).

.PARAMETER Verify
    Switch to run verification before boot (Default: $true).
#>
param (
    [ValidateSet("Cloud", "Local")]
    [string]$Mode = "Cloud",
    [switch]$Verify = $true
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir

Write-Host "🔵 arifOS v49 Unified Boot | Mode: $Mode" -ForegroundColor Cyan

# 1. Load Environment
Write-Host "Loading Environment..." -ForegroundColor Gray
& "$ScriptDir\load_env.ps1"

# 2. Verify Wiring (if requested)
if ($Verify) {
    Write-Host "Verifying Wiring..." -ForegroundColor Gray
    python "$ScriptDir\verify_v49_wiring.py"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Wiring verification failed. Aborting boot."
    }
}

# 3. Ignite Server
if ($Mode -eq "Cloud") {
    Write-Host "Igniting Cloud SSE Server (Port 8000)..." -ForegroundColor Green
    # Launch in new window to keep terminal free (mimics boot_mcp.ps1)
    Start-Process "cmd.exe" -ArgumentList "/k `"$ScriptDir\boot_server.bat`"" -WorkingDirectory $RootDir
}
elseif ($Mode -eq "Local") {
    Write-Host "Igniting Local STDIO Server..." -ForegroundColor Green
    # Run inline for stdio communication
    $env:PYTHONPATH = "$RootDir"
    $env:ARIFOS_ALLOW_LEGACY_SPEC = '1'
    python -u -m arifos.core.mcp.unified_server
}