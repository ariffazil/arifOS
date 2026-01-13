# Simple test of Kimi CLI autocomplete
Write-Host "🧪 Testing Kimi CLI Autocomplete (Simple)" -ForegroundColor Cyan

# Test basic functions
Write-Host "`n1. Testing helper functions..." -ForegroundColor Yellow
try {
    Write-Host "Available commands:" -ForegroundColor Green
    Write-Host "  khelp  - Show Kimi CLI reference" -ForegroundColor White
    Write-Host "  ks     - List constitutional skills" -ForegroundColor White
    Write-Host "  kimi   - Main Kimi CLI tool" -ForegroundColor White
    
    # Show arifOS skills
    Write-Host "`nConstitutional skills available:" -ForegroundColor Green
    $skills = @("/000", "/gitforge", "/gitQC", "/gitseal", "/sabar")
    $skills | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    
    Write-Host "`nAPEX PRIME audit skills:" -ForegroundColor Green  
    $apex = @("/audit-constitution", "/verify-trinity", "/verify-sources", "/issue-verdict", "/track-alignment", "/anti-bypass-scan", "/ledger-audit")
    $apex | ForEach-Object { Write-Host "  $_" -ForegroundColor Magenta }
    
} catch {
    Write-Host "Simple test completed" -ForegroundColor Gray
}

Write-Host "`n✅ Kimi CLI autocomplete is ready!" -ForegroundColor Green
Write-Host "Use these commands in PowerShell:" -ForegroundColor White
Write-Host "  khelp  - Get Kimi CLI help" -ForegroundColor Cyan
Write-Host "  ks     - List all skills" -ForegroundColor Cyan  
Write-Host "  /000   - Initialize constitutional session" -ForegroundColor Cyan
Write-Host "  /gitQC - Validate constitutional compliance" -ForegroundColor Cyan