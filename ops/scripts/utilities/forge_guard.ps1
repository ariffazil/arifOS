<#
.SYNOPSIS
    arifOS Forge Guard - Pre-flight constitutional gate for forge sessions.

.DESCRIPTION
    Enforces resource and context floors before allowing arifOS forge operations.
    Floors checked: F1 (Amanah/reversibility), F4 (Clarity), F7 (Humility)

    Verdict:  SEAL    - all floors pass, proceed
              PARTIAL - soft warning, proceed with caution
              VOID    - hard floor failed, fix before forging

.USAGE
    .\forge_guard.ps1                    # Check only; exit 0=SEAL 1=PARTIAL 2=VOID
    .\forge_guard.ps1 -Fix              # Auto-kill Comet/Antigravity if RAM too high
    .\forge_guard.ps1 -Ram 5 -Disk 15  # Custom thresholds in GB
    .\forge_guard.ps1 -Quiet           # JSON-only output

.EXAMPLE
    # Use as forge gate:
    .\forge_guard.ps1 && uv run pytest tests/
#>

param(
    [switch]$Fix,
    [switch]$Quiet,
    [double]$Ram    = 4.0,
    [double]$Disk   = 15.0,
    [double]$RamPct = 88.0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "SilentlyContinue"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

function Write-Verdict {
    param([string]$V, [string]$Msg)
    if ($Quiet) { return }
    $color = switch ($V) {
        "SEAL"    { "Green"  }
        "PARTIAL" { "Yellow" }
        "VOID"    { "Red"    }
        default   { "White"  }
    }
    Write-Host ("  [{0}] {1}" -f $V, $Msg) -ForegroundColor $color
}

function Write-Header {
    param([string]$Text)
    if ($Quiet) { return }
    Write-Host ("`n  {0}" -f $Text) -ForegroundColor Cyan
}

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

$checks  = [ordered]@{}
$verdict = "SEAL"
$warnings = @()
$errors   = @()

Write-Header "=== arifOS Forge Guard ==="

# ---------------------------------------------------------------------------
# 1. RAM check
# ---------------------------------------------------------------------------

Write-Header "F1/F4  RAM Pressure"

$os         = Get-WmiObject Win32_OperatingSystem
$ramTotalGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
$ramFreeGB  = [math]::Round($os.FreePhysicalMemory     / 1MB, 1)
$ramUsedGB  = [math]::Round($ramTotalGB - $ramFreeGB, 1)
$ramPct     = [math]::Round(($ramUsedGB / $ramTotalGB) * 100, 1)

$checks["ram_free_gb"]  = $ramFreeGB
$checks["ram_pct_used"] = $ramPct
$checks["ram_total_gb"] = $ramTotalGB

if ($ramFreeGB -ge $Ram -and $ramPct -le $RamPct) {
    Write-Verdict "SEAL" ("RAM OK - Free: {0} GB / {1} GB [{2}% used]" -f $ramFreeGB, $ramTotalGB, $ramPct)
} elseif ($ramFreeGB -ge ($Ram * 0.6)) {
    $warnings += ("RAM tight: {0} GB free [{1}% used]. Threshold: {2} GB / {3}%" -f $ramFreeGB, $ramPct, $Ram, $RamPct)
    Write-Verdict "PARTIAL" ("RAM tight - {0} GB free [{1}% used]" -f $ramFreeGB, $ramPct)
    if ($verdict -eq "SEAL") { $verdict = "PARTIAL" }
} else {
    $errors += ("RAM CRITICAL: only {0} GB free [{1}% used]. Need {2} GB free." -f $ramFreeGB, $ramPct, $Ram)
    Write-Verdict "VOID" ("RAM CRITICAL - {0} GB free [{1}% used]" -f $ramFreeGB, $ramPct)
    $verdict = "VOID"

    if ($Fix) {
        Write-Header "  Auto-Fix: Killing RAM hogs..."
        $hogs = @("comet", "Antigravity")
        foreach ($hog in $hogs) {
            $procs = Get-Process -Name $hog -ErrorAction SilentlyContinue
            if ($procs) {
                $mbTotal = [math]::Round(($procs | Measure-Object WorkingSet -Sum).Sum / 1MB, 0)
                Stop-Process -Name $hog -Force -ErrorAction SilentlyContinue
                Write-Verdict "SEAL" ("Killed {0} ({1} MB freed)" -f $hog, $mbTotal)
            }
        }
        Start-Sleep -Milliseconds 1500
        $os2        = Get-WmiObject Win32_OperatingSystem
        $ramFree2   = [math]::Round($os2.FreePhysicalMemory / 1MB, 1)
        $ramPct2    = [math]::Round(($ramTotalGB - $ramFree2) / $ramTotalGB * 100, 1)
        if ($ramFree2 -ge $Ram) {
            Write-Verdict "SEAL" ("RAM recovered - {0} GB free [{1}% used]" -f $ramFree2, $ramPct2)
            $verdict = "SEAL"
            $errors  = $errors | Where-Object { $_ -notlike "RAM CRITICAL*" }
        } else {
            Write-Verdict "PARTIAL" ("RAM still tight after kills - {0} GB free. Run: wsl --shutdown" -f $ramFree2)
            if ($verdict -eq "VOID") { $verdict = "PARTIAL" }
        }
    }
}

# ---------------------------------------------------------------------------
# 2. Disk check
# ---------------------------------------------------------------------------

Write-Header "F1     Disk Space (C:)"

$disk       = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'"
$diskFreeGB = [math]::Round($disk.FreeSpace / 1GB, 1)
$diskTotGB  = [math]::Round($disk.Size      / 1GB, 1)
$diskPct    = [math]::Round(($diskTotGB - $diskFreeGB) / $diskTotGB * 100, 1)

$checks["disk_free_gb"]  = $diskFreeGB
$checks["disk_pct_used"] = $diskPct

if ($diskFreeGB -ge $Disk) {
    Write-Verdict "SEAL" ("Disk OK - Free: {0} GB / {1} GB [{2}% used]" -f $diskFreeGB, $diskTotGB, $diskPct)
} elseif ($diskFreeGB -ge ($Disk * 0.5)) {
    $warnings += ("Disk tight: {0} GB free [{1}% used]. Threshold: {2} GB" -f $diskFreeGB, $diskPct, $Disk)
    Write-Verdict "PARTIAL" ("Disk tight - {0} GB free [warn at {1} GB]" -f $diskFreeGB, $Disk)
    if ($verdict -eq "SEAL") { $verdict = "PARTIAL" }
} else {
    $errors += ("Disk CRITICAL: only {0} GB free. Need {1} GB." -f $diskFreeGB, $Disk)
    Write-Verdict "VOID" ("Disk CRITICAL - {0} GB free" -f $diskFreeGB)
    $verdict = "VOID"
}

# ---------------------------------------------------------------------------
# 3. Python venv check
# ---------------------------------------------------------------------------

Write-Header "F11    Python Context"

$venvPath    = "C:\Users\User\arifOS\.venv\Scripts\python.exe"
$activePy    = (Get-Command python -ErrorAction SilentlyContinue).Source

$checks["venv_exists"]    = (Test-Path $venvPath)
$checks["active_python"]  = $activePy
$checks["venv_activated"] = ($activePy -like "*arifOS\.venv*")

if ($checks["venv_activated"]) {
    Write-Verdict "SEAL" ("Python context: arifOS venv active ({0})" -f $activePy)
} elseif ($checks["venv_exists"]) {
    $warnings += "arifOS venv exists but NOT activated."
    Write-Verdict "PARTIAL" ("venv NOT activated (active: {0})" -f $activePy)
    if (-not $Quiet) {
        Write-Host "    Fix: Set-Location C:\Users\User\arifOS; .\.venv\Scripts\Activate.ps1" -ForegroundColor DarkYellow
    }
    if ($verdict -eq "SEAL") { $verdict = "PARTIAL" }
} else {
    $errors += ("arifOS venv missing at: {0}" -f $venvPath)
    Write-Verdict "VOID" "arifOS venv missing - run: uv venv in C:\Users\User\arifOS"
    $verdict = "VOID"
}

# ---------------------------------------------------------------------------
# 4. Python version check
# ---------------------------------------------------------------------------

Write-Header "F2     Python Version"

$pyVer = (& python --version 2>&1)
$checks["python_version"] = "$pyVer"

if ($pyVer -match "3\.12") {
    Write-Verdict "SEAL" ("Python {0} [target: 3.12.x]" -f $pyVer)
} elseif ($pyVer -match "3\.1[013]") {
    $warnings += ("Python {0} may differ from target 3.12" -f $pyVer)
    Write-Verdict "PARTIAL" ("{0} [target: 3.12 - check compat]" -f $pyVer)
    if ($verdict -eq "SEAL") { $verdict = "PARTIAL" }
} else {
    $warnings += ("Unexpected Python {0}" -f $pyVer)
    Write-Verdict "PARTIAL" ("{0} [unexpected - verify venv]" -f $pyVer)
    if ($verdict -eq "SEAL") { $verdict = "PARTIAL" }
}

# ---------------------------------------------------------------------------
# 5. arifOS importable check
# ---------------------------------------------------------------------------

Write-Header "F8     arifOS Importable"

$importTest = (& python -c "import core; print('ok')" 2>&1)
$checks["arifos_importable"] = ($importTest -eq "ok")

if ($importTest -eq "ok") {
    Write-Verdict "SEAL" "arifOS core importable"
} else {
    $warnings += ("core not importable: {0}" -f $importTest)
    Write-Verdict "PARTIAL" ("core not importable ({0}) - run from C:\Users\User\arifOS" -f $importTest)
    if ($verdict -eq "SEAL") { $verdict = "PARTIAL" }
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

Write-Header ("=== VERDICT: {0} ===" -f $verdict)

if (-not $Quiet) {
    if ($verdict -eq "SEAL") {
        Write-Host "  All floors pass. Forge is OPEN." -ForegroundColor Green
    } elseif ($verdict -eq "PARTIAL") {
        Write-Host "  Soft warnings. Forge is OPEN with caution:" -ForegroundColor Yellow
        foreach ($w in $warnings) { Write-Host ("    * {0}" -f $w) -ForegroundColor DarkYellow }
        Write-Host "  Tip: .\forge_guard.ps1 -Fix  to auto-kill RAM hogs" -ForegroundColor DarkYellow
    } else {
        Write-Host "  VOID - Fix before forging:" -ForegroundColor Red
        foreach ($e in $errors) { Write-Host ("    * {0}" -f $e) -ForegroundColor Red }
        Write-Host "  Tip: .\forge_guard.ps1 -Fix  to attempt auto-recovery" -ForegroundColor Yellow
    }
}

# JSON summary (always printed)
$summary = [PSCustomObject]@{
    verdict   = $verdict
    ram_free  = $ramFreeGB
    ram_pct   = $ramPct
    disk_free = $diskFreeGB
    disk_pct  = $diskPct
    python    = "$pyVer"
    venv_ok   = $checks["venv_activated"]
    timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
}
Write-Host ""
$summary | ConvertTo-Json -Compress
Write-Host ""

# Exit codes: 0=SEAL  1=PARTIAL  2=VOID
switch ($verdict) {
    "SEAL"    { exit 0 }
    "PARTIAL" { exit 1 }
    "VOID"    { exit 2 }
}
