# Fix color issues in Kimi autocomplete config
$configPath = "$env:USERPROFILE\OneDrive\Documents\WindowsPowerShell\kimi_powershell_config.ps1"

if (Test-Path $configPath) {
    Write-Host "Fixing color issues in Kimi config..." -ForegroundColor Yellow
    
    # Read current config
    $content = Get-Content $configPath -Raw
    
    # Fix ANSI escape sequences
    $fixedContent = $content -replace "'`e\[93m\"", '"Yellow"' -replace "'`e\[96m\"", '"Cyan"' -replace "'`e\[36m\"", '"Cyan"' -replace "'`e\[97m\"", '"White"' -replace "'`e\[92m\"", '"Green"' -replace "'`e\[90m\"", '"DarkGray"' -replace "'`e\[97;2;3m\"", '"Gray"'
    
    # Write fixed content
    Set-Content -Path $configPath -Value $fixedContent -Force
    
    Write-Host "✅ Color issues fixed!" -ForegroundColor Green
    Write-Host "Restart PowerShell or run: . `$PROFILE" -ForegroundColor Cyan
} else {
    Write-Host "Config file not found at: $configPath" -ForegroundColor Red
}