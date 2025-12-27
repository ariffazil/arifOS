#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Convenience script to run RAW vs GOVERNED demo on Windows

.DESCRIPTION
    Runs L6_SEALION/tests/demo_sealion_raw_vs_governed.py with proper environment setup.
    Checks for API key, activates venv if needed, and runs the demo.

.PARAMETER Prompt
    Custom prompt to send to the LLM (optional)

.PARAMETER Model
    Model name (default: Qwen-SEA-LION-v4-32B-IT)

.PARAMETER MaxTokens
    Max tokens to generate (default: 512)

.PARAMETER Temperature
    Generation temperature 0.0-1.0 (default: 0.2)

.EXAMPLE
    .\run_raw_vs_governed.ps1
    # Run with default prompt

.EXAMPLE
    .\run_raw_vs_governed.ps1 -Prompt "Explain quantum mechanics"
    # Run with custom prompt

.EXAMPLE
    .\run_raw_vs_governed.ps1 -Prompt "What is AI?" -MaxTokens 256 -Temperature 0.5
    # Run with custom parameters
#>

param(
    [string]$Prompt = "",
    [string]$Model = "Qwen-SEA-LION-v4-32B-IT",
    [int]$MaxTokens = 512,
    [double]$Temperature = 0.2
)

# Get script directory and repo root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Change to repo root
Push-Location $RepoRoot

try {
    Write-Host "🦁 RAW vs GOVERNED Demo Runner" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""

    # Step 1: Check for API key
    Write-Host "🔑 Checking for API key..." -ForegroundColor Yellow

    $ApiKey = $env:ARIF_LLM_API_KEY
    if (-not $ApiKey) {
        $ApiKey = $env:SEALION_API_KEY
    }
    if (-not $ApiKey) {
        $ApiKey = $env:LLM_API_KEY
    }
    if (-not $ApiKey) {
        $ApiKey = $env:OPENAI_API_KEY
    }

    if (-not $ApiKey) {
        Write-Host "❌ API Key not found!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please set one of these environment variables:" -ForegroundColor Yellow
        Write-Host "  - ARIF_LLM_API_KEY" -ForegroundColor White
        Write-Host "  - SEALION_API_KEY" -ForegroundColor White
        Write-Host "  - LLM_API_KEY" -ForegroundColor White
        Write-Host "  - OPENAI_API_KEY" -ForegroundColor White
        Write-Host ""
        Write-Host "Example (session-scoped):" -ForegroundColor Yellow
        Write-Host '  $env:ARIF_LLM_API_KEY = "your-api-key-here"' -ForegroundColor White
        Write-Host ""
        Write-Host "Example (persistent):" -ForegroundColor Yellow
        Write-Host '  [System.Environment]::SetEnvironmentVariable("ARIF_LLM_API_KEY", "your-key", "User")' -ForegroundColor White
        Write-Host ""
        exit 1
    }

    Write-Host "✅ API key found" -ForegroundColor Green
    Write-Host ""

    # Step 2: Check for virtual environment
    Write-Host "🐍 Checking Python environment..." -ForegroundColor Yellow

    $VenvPath = Join-Path $RepoRoot ".venv"
    if (Test-Path $VenvPath) {
        Write-Host "✅ Virtual environment found: $VenvPath" -ForegroundColor Green

        # Activate venv
        $ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
        if (Test-Path $ActivateScript) {
            Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
            & $ActivateScript
            Write-Host "✅ Virtual environment activated" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Activate script not found, continuing with current Python" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️ Virtual environment not found, using system Python" -ForegroundColor Yellow
    }
    Write-Host ""

    # Step 3: Run the demo
    Write-Host "🚀 Running RAW vs GOVERNED demo..." -ForegroundColor Yellow
    Write-Host ""

    $DemoScript = Join-Path $ScriptDir "demo_sealion_raw_vs_governed.py"

    # Build command
    $Command = "python `"$DemoScript`" --model `"$Model`" --max_tokens $MaxTokens --temperature $Temperature"

    if ($Prompt) {
        $Command += " --prompt `"$Prompt`""
    }

    Write-Host "Command: $Command" -ForegroundColor DarkGray
    Write-Host ""

    # Execute
    Invoke-Expression $Command

} finally {
    # Return to original directory
    Pop-Location
}
