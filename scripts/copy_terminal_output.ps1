#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Captures terminal output and sends it to Kimi CLI

.DESCRIPTION
    This script captures the last N lines from a terminal output file
    and sends it to Kimi CLI for processing. Designed for VS Code integration.

.PARAMETER Lines
    Number of lines to capture from the terminal output (default: 50)

.PARAMETER OutputFile
    Path to the terminal output file (default: .arifos_clip/terminal_output.log)

.PARAMETER Command
    The Kimi slash command to execute (default: /paste)

.EXAMPLE
    # Capture last 50 lines and send to Kimi
    .\scripts\copy_terminal_output.ps1

    # Capture last 100 lines
    .\scripts\copy_terminal_output.ps1 -Lines 100

    # Use custom output file
    .\scripts\copy_terminal_output.ps1 -OutputFile "~/.arifos_clip/my_output.log"
#>

param(
    [int]$Lines = 50,
    [string]$OutputFile = "$env:USERPROFILE\.arifos_clip\terminal_output.log",
    [string]$Command = "/paste"
)

# Ensure the output directory exists
$outputDir = Split-Path -Parent $OutputFile
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# Check if output file exists
if (-not (Test-Path $OutputFile)) {
    Write-Host "❌ Terminal output file not found: $OutputFile" -ForegroundColor Red
    Write-Host "💡 Tip: Configure your VS Code to log terminal output to this file" -ForegroundColor Yellow
    exit 1
}

# Read the last N lines from the file
try {
    $content = Get-Content -Path $OutputFile -Tail $Lines -ErrorAction Stop
    
    if ($content.Count -eq 0) {
        Write-Host "⚠️  No content found in terminal output file" -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host "📋 Captured $($content.Count) lines from terminal output" -ForegroundColor Green
    
    # Create a temporary file with the captured content
    $tempFile = [System.IO.Path]::GetTempFileName() + ".log"
    $content | Out-File -FilePath $tempFile -Encoding UTF8
    
    # Display preview
    Write-Host "\n📝 Preview (first 10 lines):" -ForegroundColor Cyan
    $content | Select-Object -First 10 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    
    if ($content.Count -gt 10) {
        Write-Host "  ... ($($content.Count - 10) more lines)" -ForegroundColor Gray
    }
    
    Write-Host "\n🚀 Sending to Kimi CLI..." -ForegroundColor Green
    
    # Prepare the command for Kimi
    $kimiCommand = "$Command $tempFile"
    
    # Execute Kimi CLI with the captured output
    if (Get-Command kimi -ErrorAction SilentlyContinue) {
        kimi $kimiCommand
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        # Fallback to direct Python execution
        python -m kimi_cli $kimiCommand
    } else {
        Write-Host "❌ Neither 'kimi' nor 'python' commands found in PATH" -ForegroundColor Red
        Write-Host "💡 Please ensure Kimi CLI is installed and in your PATH" -ForegroundColor Yellow
        exit 1
    }
    
    # Cleanup temp file after a delay
    Start-Job -ScriptBlock {
        Start-Sleep -Seconds 30
        Remove-Item -Path $using:tempFile -ErrorAction SilentlyContinue
    } | Out-Null
    
} catch {
    Write-Host "❌ Error reading terminal output: $_" -ForegroundColor Red
    exit 1
}
