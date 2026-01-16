<#
.SYNOPSIS
    arifOS Unified Reboot Orchestrator (000 Stage Reset)
    Graceful shutdown and fresh ignition.

.DESCRIPTION
    1. Stops Docker containers.
    2. Stops MCP server.
    3. Cleans up stale session lock files.
    4. Triggers boot_system.ps1 for a fresh start.

.AUTHOR
    Antigravity (Δ)
#>

$ErrorActionPreference = "Continue" # Don't stop on non-critical errors during shutdown

function Write-Step($text) {
    Write-Host "`n[REBOOT] $text" -ForegroundColor Cyan
}

try {
    Write-Host "==========================================" -ForegroundColor Magenta
    Write-Host "   arifOS UNIFIED REBOOT (COLD RESET)     " -ForegroundColor Magenta
    Write-Host "==========================================" -ForegroundColor Magenta

    # Step 1: Stop Services
    Write-Step "1/4: Stopping Services..."
    if (Test-Path "docker-compose.yml") {
        Write-Host "🛑 [REBOOT] Stopping Docker containers..." -ForegroundColor Yellow
        docker-compose down
    }

    $mcpStopScript = "scripts/auto_start_mcp.ps1"
    if (Test-Path $mcpStopScript) {
        Write-Host "🛑 [REBOOT] Stopping MCP server..." -ForegroundColor Yellow
        & $mcpStopScript -Stop
    }

    # Step 2: Cleanup
    Write-Step "2/4: Cleaning Stale Sessions..."
    $cleanupScript = "scripts/cleanup_sessions.py"
    if (Test-Path $cleanupScript) {
        # Use python from .venv if exists
        $python = if (Test-Path ".venv/Scripts/python.exe") { ".venv/Scripts/python.exe" } else { "python" }
        & $python $cleanupScript --force
    } else {
        Write-Warning "⚠️ Cleanup script missing: $cleanupScript"
    }

    # Step 3: Cooldown
    Write-Step "3/4: Cooling Down (Phoenix-72)..."
    Start-Sleep -Seconds 3
    Write-Host "✅ [REBOOT] System is cold." -ForegroundColor Green

    # Step 4: Fresh Ignition
    Write-Step "4/4: Re-Igniting System..."
    $bootScript = "scripts/boot_system.ps1"
    if (Test-Path $bootScript) {
        & $bootScript
    } else {
        Write-Error "❌ Boot script missing: $bootScript"
    }

    Write-Host "`n✅ [REBOOT] System Reboot Complete." -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Magenta
} catch {
    Write-Error "❌ [REBOOT] Critical Failure: $_"
}
