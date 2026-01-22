# arifOS v49 Standardized Test Runner
# Use this script to run the pytest suite in a consistent environment

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir

Write-Host "🧪 arifOS v49 Test Execution" -ForegroundColor Cyan

# 1. Load Environment
Write-Host "Loading Environment..." -ForegroundColor Gray
& "$ScriptDir\load_env.ps1"

# 2. Set Python Path to include root
$env:PYTHONPATH = "$RootDir"

# 3. Run Pytest
# We use 'python -m pytest' to ensure the current interpreter and environment are used
Write-Host "Running pytest suite..." -ForegroundColor White
python -m pytest tests/ --verbose

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "❌ Some tests failed." -ForegroundColor Red
    exit $LASTEXITCODE
}
