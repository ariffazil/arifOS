#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Load .env file into current PowerShell session and optionally persist to User environment

.DESCRIPTION
    This script reads .env file and loads variables into:
    1. Current session (temporary - until you close terminal)
    2. User environment (optional - persists across sessions)
    3. Supports comments (#) and empty lines
    4. Skips malformed lines safely

.PARAMETER Path
    Path to .env file (defaults to .env in current directory)

.PARAMETER Persist
    If set, also saves variables to User-level environment (persists across sessions)

.PARAMETER ShowVariables
    If set, displays loaded variables (useful for debugging)

.EXAMPLE
    # Load .env into current session only (temporary)
    .\scripts\load_env.ps1

.EXAMPLE
    # Load and persist to User environment (survives restarts)
    .\scripts\load_env.ps1 -Persist

.EXAMPLE
    # Load from specific file
    .\scripts\load_env.ps1 -Path "C:\path\to\.env"

.EXAMPLE
    # Load and show what was loaded
    .\scripts\load_env.ps1 -ShowVariables

.NOTES
    Author: arifOS Engineer (Claude Code Ω)
    Authority: F6 Amanah - Reversible, safe file operations
    Version: v1.0
#>

param(
    [string]$Path = ".env",
    [switch]$Persist,
    [switch]$ShowVariables
)

# Constitutional colors for output
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "Cyan"

Write-Host "========================================" -ForegroundColor $ColorInfo
Write-Host "  arifOS .env Loader" -ForegroundColor $ColorInfo
Write-Host "  DITEMPA BUKAN DIBERI" -ForegroundColor $ColorInfo
Write-Host "========================================" -ForegroundColor $ColorInfo
Write-Host ""

# Check if .env file exists
if (-not (Test-Path $Path)) {
    Write-Host "[ERROR] .env file not found at: $Path" -ForegroundColor $ColorError
    Write-Host "Expected location: $(Resolve-Path -Path '.' -ErrorAction SilentlyContinue)\$Path" -ForegroundColor $ColorWarning
    exit 1
}

# Resolve full path
$EnvFilePath = Resolve-Path $Path
Write-Host "[OK] Found .env file: $EnvFilePath" -ForegroundColor $ColorSuccess
Write-Host ""

# Read .env file
$EnvContent = Get-Content $EnvFilePath -ErrorAction Stop
$LoadedCount = 0
$SkippedCount = 0
$LoadedVars = @()

Write-Host "Loading environment variables..." -ForegroundColor $ColorInfo
Write-Host ""

foreach ($Line in $EnvContent) {
    # Skip empty lines
    if ([string]::IsNullOrWhiteSpace($Line)) {
        continue
    }

    # Skip comments
    if ($Line.Trim().StartsWith("#")) {
        continue
    }

    # Parse KEY=VALUE
    if ($Line -match '^([^=]+)=(.*)$') {
        $Key = $matches[1].Trim()
        $Value = $matches[2].Trim()

        # Remove quotes if present
        if ($Value -match '^"(.*)"$' -or $Value -match "^'(.*)'$") {
            $Value = $matches[1]
        }

        try {
            # Set in current session (Process scope - temporary)
            [System.Environment]::SetEnvironmentVariable($Key, $Value, "Process")

            # Also set in PowerShell session (for immediate use)
            Set-Item -Path "env:$Key" -Value $Value -Force

            # Optionally persist to User environment
            if ($Persist) {
                [System.Environment]::SetEnvironmentVariable($Key, $Value, "User")
                Write-Host "  [PERSIST] $Key" -ForegroundColor $ColorSuccess
            } else {
                Write-Host "  [SESSION] $Key" -ForegroundColor $ColorInfo
            }

            $LoadedCount++
            $LoadedVars += @{ Key = $Key; Value = $Value }
        }
        catch {
            Write-Host "  [SKIP] $Key (failed to load)" -ForegroundColor $ColorWarning
            $SkippedCount++
        }
    }
    else {
        Write-Host "  [SKIP] Invalid line: $($Line.Substring(0, [Math]::Min(50, $Line.Length)))..." -ForegroundColor $ColorWarning
        $SkippedCount++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor $ColorInfo
Write-Host "  SUMMARY" -ForegroundColor $ColorInfo
Write-Host "========================================" -ForegroundColor $ColorInfo
Write-Host "  Loaded: $LoadedCount variables" -ForegroundColor $ColorSuccess
if ($SkippedCount -gt 0) {
    Write-Host "  Skipped: $SkippedCount lines" -ForegroundColor $ColorWarning
}

if ($Persist) {
    Write-Host "  Mode: PERSISTED (survives restart)" -ForegroundColor $ColorSuccess
} else {
    Write-Host "  Mode: SESSION ONLY (temporary)" -ForegroundColor $ColorInfo
}

# Show loaded variables if requested
if ($ShowVariables -and $LoadedVars.Count -gt 0) {
    Write-Host ""
    Write-Host "Loaded Variables:" -ForegroundColor $ColorInfo
    foreach ($Var in $LoadedVars) {
        $DisplayValue = $Var.Value
        # Mask sensitive values (anything with TOKEN, KEY, SECRET, PASSWORD)
        if ($Var.Key -match "TOKEN|KEY|SECRET|PASSWORD|PASS") {
            if ($DisplayValue.Length -gt 8) {
                $DisplayValue = $DisplayValue.Substring(0, 8) + "..." + $DisplayValue.Substring($DisplayValue.Length - 4)
            } else {
                $DisplayValue = "***MASKED***"
            }
        }
        Write-Host "  $($Var.Key) = $DisplayValue" -ForegroundColor $ColorInfo
    }
}

Write-Host ""
Write-Host "[SEAL] Environment loaded successfully" -ForegroundColor $ColorSuccess

if (-not $Persist) {
    Write-Host ""
    Write-Host "TIP: Use -Persist flag to save variables across sessions" -ForegroundColor $ColorWarning
    Write-Host "     Example: .\scripts\load_env.ps1 -Persist" -ForegroundColor $ColorWarning
}

Write-Host ""
