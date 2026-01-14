<#
.SYNOPSIS
    Canonical Ignition Script for Kimi AI (Auditor Apex Prime)

.DESCRIPTION
    Forged by Antigravity (Architect) to solve:
    1. "Jumpy Text" (Enforces UTF-8 65001 encoding)
    2. "Version Lock" (Sets ARIFOS_ALLOW_LEGACY_SPEC=1)
    3. TUI Rendering (Sets PYTHONIOENCODING=utf-8)

.USAGE
    ./scripts/ignite_kimi.ps1
#>

Write-Host "[ARIFOS] Igniting Kimi (Auditor Apex Prime)..." -ForegroundColor Cyan

# 1. Enforce UTF-8 Console for TUI Box-Drawing
Write-Host "[SETUP] Forcing UTF-8 Console (chcp 65001)..." -ForegroundColor DarkGray
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

# 2. Set Python IO Encoding
$env:PYTHONIOENCODING = "utf-8"

# 3. Unlock Legacy Spec (Prevent Crash)
$env:ARIFOS_ALLOW_LEGACY_SPEC = "1"

# 4. Ignite
Write-Host "[LAUNCH] Standard Protocol Engaged." -ForegroundColor Green
kimi
