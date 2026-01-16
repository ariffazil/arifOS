<#
.SYNOPSIS
    arifOS Unified Setup Orchestrator (000 Stage)
    Forges the development environment and auto-ignition.

.DESCRIPTION
    1. Runs the core bootstrap (dependencies, venv, arifOS package).
    2. Runs auto-start setup (Task Scheduler, logs).
    3. Verifies installation.

.AUTHOR
    Antigravity (Δ)
#>

$ErrorActionPreference = "Stop"

function Write-Step($text) {
    Write-Host "`n[SETUP] $text" -ForegroundColor Cyan
}

try {
    Write-Host "==========================================" -ForegroundColor Magenta
    Write-Host "   arifOS UNIFIED SETUP (000 IGNITION)     " -ForegroundColor Magenta
    Write-Host "==========================================" -ForegroundColor Magenta

    # Step 1: Core Bootstrap
    Write-Step "1/3: Forging Core Environment..."
    $bootstrapScript = "setup/bootstrap/bootstrap.ps1"
    if (Test-Path $bootstrapScript) {
        # Run bootstrap with -Auto flag if we want it non-interactive
        # But for setup we usually want user choices
        & $bootstrapScript
    } else {
        Write-Error "❌ Core bootstrap script missing: $bootstrapScript"
    }

    # Step 2: Auto-Start Configuration
    Write-Step "2/3: Configuring Auto-Ignition..."
    $autostartScript = "scripts/setup_auto_start.ps1"
    if (Test-Path $autostartScript) {
        & $autostartScript
    } else {
        Write-Warning "⚠️ Auto-start script missing: $autostartScript. Skipping."
    }

    # Step 3: Final Verification
    Write-Step "3/3: Verifying Forge Integrity..."
    $verifyScript = "setup/verification/verify_setup.py"
    if (Test-Path $verifyScript) {
        # Use python from .venv if exists
        $python = if (Test-Path ".venv/Scripts/python.exe") { ".venv/Scripts/python.exe" } else { "python" }
        & $python $verifyScript
    }

    Write-Host "`n✅ [SETUP] Unified Setup Complete." -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Magenta
} catch {
    Write-Error "❌ [SETUP] Critical Failure: $_"
}
