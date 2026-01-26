#!/usr/bin/env pwsh
<#
.SYNOPSIS
    One-time setup for terminal capture integration

.DESCRIPTION
    Sets up the necessary directories and configurations for capturing
text from Visual Studio Code's integrated terminal and sending it to Kimi CLI.
#>

$ErrorActionPreference = "Stop"

Write-Host "Terminal Capture Setup for Kimi CLI" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Step 1: Create capture directory
$captureDir = "$env:USERPROFILE\.arifos_clip"
Write-Host "Creating capture directory: $captureDir" -ForegroundColor Yellow

if (-not (Test-Path $captureDir)) {
    New-Item -ItemType Directory -Path $captureDir -Force | Out-Null
    Write-Host "Directory created successfully" -ForegroundColor Green
} else {
    Write-Host "Directory already exists" -ForegroundColor Green
}

# Step 2: Verify scripts exist
$scripts = @(
    "scripts\kimi_terminal_bridge.py",
    "scripts\copy_terminal_output.ps1",
    "scripts\copy_terminal_output.bat"
)

Write-Host "Verifying capture scripts..." -ForegroundColor Yellow
$allScriptsExist = $true

foreach ($script in $scripts) {
    if (Test-Path $script) {
        Write-Host "  Found: $script" -ForegroundColor Green
    } else {
        Write-Host "  Missing: $script" -ForegroundColor Red
        $allScriptsExist = $false
    }
}

if (-not $allScriptsExist) {
    Write-Host "Some scripts are missing. Please ensure all files are present." -ForegroundColor Red
    exit 1
}

# Step 3: Check Kimi CLI installation
Write-Host "Checking Kimi CLI installation..." -ForegroundColor Yellow

$kimiInstalled = $false
if (Get-Command kimi -ErrorAction SilentlyContinue) {
    Write-Host "Kimi CLI found" -ForegroundColor Green
    $kimiInstalled = $true
} else {
    Write-Host "Kimi CLI not found in PATH" -ForegroundColor Yellow
    Write-Host "Install with: pip install kimi-cli" -ForegroundColor Gray
    
    # Check Python as fallback
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Host "Python found (fallback available)" -ForegroundColor Green
    } else {
        Write-Host "Python not found either" -ForegroundColor Red
        Write-Host "Please install Python 3.8+ and Kimi CLI" -ForegroundColor Yellow
        exit 1
    }
}

# Step 4: Test capture functionality
Write-Host "Testing capture functionality..." -ForegroundColor Yellow

# Create a test output file
$testFile = "$captureDir\terminal_output.log"
"Terminal Capture Test" | Out-File -FilePath $testFile -Encoding UTF8
Get-Date | Out-File -FilePath $testFile -Append -Encoding UTF8
"Test completed successfully" | Out-File -FilePath $testFile -Append -Encoding UTF8

Write-Host "Test file created" -ForegroundColor Green

# Test the capture script
try {
    python scripts\kimi_terminal_bridge.py --lines 3 /echo 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Capture script working" -ForegroundColor Green
    } else {
        Write-Host "Capture script test failed with code $LASTEXITCODE" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Could not test capture script: $_" -ForegroundColor Yellow
}

# Step 5: Display usage information
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Available Commands:" -ForegroundColor Yellow
Write-Host "  /tpaste     - Capture and paste last 50 lines" -ForegroundColor White
Write-Host "  /texplain   - Capture and explain output" -ForegroundColor White
Write-Host "  /tdebug     - Capture for debugging" -ForegroundColor White
Write-Host "  /tcap       - Custom capture command" -ForegroundColor White
Write-Host ""
Write-Host "VS Code Tasks:" -ForegroundColor Yellow
Write-Host "  Ctrl+Shift+T - Capture terminal to Kimi" -ForegroundColor White
Write-Host "  Ctrl+Shift+L - Capture last 100 lines" -ForegroundColor White
Write-Host ""
Write-Host "Files Location:" -ForegroundColor Yellow
Write-Host "  Capture dir: $captureDir" -ForegroundColor Gray
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  Full guide: docs\TERMINAL_CAPTURE_GUIDE.md" -ForegroundColor Gray
Write-Host "  Quick ref: docs\TERMINAL_CAPTURE_QUICKREF.md" -ForegroundColor Gray
Write-Host ""
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Cyan
