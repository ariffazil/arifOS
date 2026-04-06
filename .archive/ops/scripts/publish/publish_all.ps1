#!/usr/bin/env pwsh
# Publish arifOS to PyPI and npm
# Usage: .\scripts\publish\publish_all.ps1 -PyPIToken "pypi-xxx" -npmOtp "123456"

param(
    [string]$PyPIToken = "",
    [string]$npmOtp = ""
)

$ErrorActionPreference = "Stop"

Write-Host "🔱 arifOS Publish Script — Ditempa Bukan Diberi" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check versions
Write-Host "📦 Checking versions..." -ForegroundColor Yellow
$pyproject = Get-Content .\pyproject.toml | Select-String 'version = "(.*)"' | ForEach-Object { $_.Matches.Groups[1].Value } | Select-Object -First 1
$packageJson = Get-Content .\npm\arifos-mcp\package.json | Select-String '"version": "(.*)"' | ForEach-Object { $_.Matches.Groups[1].Value } | Select-Object -First 1

Write-Host "  PyPI version: $pyproject" -ForegroundColor Gray
Write-Host "  npm version:  $packageJson" -ForegroundColor Gray
Write-Host ""

if ($pyproject -ne $packageJson) {
    Write-Error "❌ Version mismatch! pyproject.toml ($pyproject) != package.json ($packageJson)"
    exit 1
}

Write-Host "✅ Versions aligned: $pyproject" -ForegroundColor Green
Write-Host ""

# PyPI Publish
Write-Host "📦 Publishing to PyPI..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

try {
    # Clean dist
    if (Test-Path .\dist) {
        Remove-Item -Recurse -Force .\dist
    }
    
    # Build
    Write-Host "🔨 Building distribution..." -ForegroundColor Gray
    python -m build -q
    
    # Check
    Write-Host "🔍 Checking distribution..." -ForegroundColor Gray
    python -m twine check dist/*
    
    # Upload
    Write-Host "📤 Uploading to PyPI..." -ForegroundColor Gray
    if ($PyPIToken) {
        $env:TWINE_USERNAME = "__token__"
        $env:TWINE_PASSWORD = $PyPIToken
    }
    
    python -m twine upload dist/*
    
    Write-Host "✅ PyPI publish successful!" -ForegroundColor Green
    Write-Host "   pip install arifosmcp==$pyproject" -ForegroundColor Cyan
} catch {
    Write-Error "❌ PyPI publish failed: $_"
    exit 1
}

Write-Host ""
Write-Host "📦 Publishing to npm..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

try {
    Set-Location .\npm\arifos-mcp
    
    # Check if already logged in
    $whoami = npm whoami 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "🔑 Please login to npm:" -ForegroundColor Yellow
        npm login
    } else {
        Write-Host "✅ Already logged in as: $whoami" -ForegroundColor Gray
    }
    
    # Publish
    Write-Host "📤 Publishing package..." -ForegroundColor Gray
    if ($npmOtp) {
        npm publish --access public --otp $npmOtp
    } else {
        npm publish --access public
    }
    
    Set-Location ..\..
    
    Write-Host "✅ npm publish successful!" -ForegroundColor Green
    Write-Host "   npm install -g @arifos/mcp@$packageJson" -ForegroundColor Cyan
} catch {
    Set-Location ..\..
    Write-Error "❌ npm publish failed: $_"
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "🎉 All publishes completed successfully!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Installation commands:" -ForegroundColor Cyan
Write-Host "  pip install arifosmcp==$pyproject" -ForegroundColor White
Write-Host "  npm install -g @arifos/mcp@$packageJson" -ForegroundColor White
