#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Terminal Output Capture Helper for Kimi CLI
.DESCRIPTION
    Captures terminal output and formats it for easy copy-paste to Kimi
.EXAMPLE
    ./capture.ps1 -Command "git status"
    ./capture.ps1 -Command "python -m pytest" -Lines 20
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Command,
    
    [int]$Lines = 50,
    
    [switch]$Box,
    [switch]$Minimal,
    [switch]$WithLineNumbers
)

# Run command and capture output
$output = Invoke-Expression $Command 2>&1 | Out-String

# Truncate if needed
$linesArray = $output -split "`n"
if ($linesArray.Count -gt $Lines) {
    $truncated = $linesArray[0..($Lines-1)] -join "`n"
    $output = $truncated + "`n[... " + ($linesArray.Count - $Lines) + " more lines ...]"
}

# Format output
if ($Box) {
    $width = 50
    $border = "─" * $width
    Write-Host "┌$border┐" -ForegroundColor Cyan
    foreach ($line in $output -split "`n") {
        $padded = $line.PadRight($width).Substring(0, [Math]::Min($line.Length, $width))
        Write-Host "│  $padded  │" -ForegroundColor Cyan
    }
    Write-Host "└$border┘" -ForegroundColor Cyan
}
elseif ($Minimal) {
    Write-Host $output
}
elseif ($WithLineNumbers) {
    $i = 1
    foreach ($line in $output -split "`n") {
        Write-Host ("{0,4}  {1}" -f $i, $line)
        $i++
    }
}
else {
    # Default clean format
    $width = 50
    $border = "═" * $width
    Write-Host ""
    Write-Host $border -ForegroundColor Green
    Write-Host "  > $Command" -ForegroundColor Yellow
    Write-Host ""
    foreach ($line in $output -split "`n") {
        if ($line.Trim()) {
            Write-Host "  $line"
        }
    }
    Write-Host $border -ForegroundColor Green
    Write-Host ""
}

Write-Host "✓ Output ready for copy-paste" -ForegroundColor Green
