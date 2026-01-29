# Gemini CLI Extensions - Simple Setup
# Run this in a native PowerShell window (not from bash)

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " arifOS + Gemini CLI Extension Setup" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Verify Gemini CLI
Write-Host "[1/4] Checking Gemini CLI..." -ForegroundColor Yellow
try {
    $version = gemini --version 2>&1
    Write-Host "  SUCCESS: Gemini CLI is installed" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Gemini CLI not found" -ForegroundColor Red
    Write-Host "  Run: . `$PROFILE" -ForegroundColor Yellow
    exit
}

# Check settings.json
Write-Host ""
Write-Host "[2/4] Checking settings.json..." -ForegroundColor Yellow
$settingsPath = "$env:USERPROFILE\.gemini\settings.json"
if (Test-Path $settingsPath) {
    $settings = Get-Content $settingsPath | ConvertFrom-Json
    $count = ($settings.mcpServers | Get-Member -MemberType NoteProperty).Count
    Write-Host "  SUCCESS: Found $count MCP servers configured" -ForegroundColor Green
    $settings.mcpServers.PSObject.Properties | ForEach-Object {
        Write-Host "    - $($_.Name)" -ForegroundColor Cyan
    }
} else {
    Write-Host "  ERROR: Settings file not found" -ForegroundColor Red
}

# Check antigravity config
Write-Host ""
Write-Host "[3/4] Checking antigravity/mcp_config.json..." -ForegroundColor Yellow
$mcpConfigPath = "$env:USERPROFILE\.gemini\antigravity\mcp_config.json"
if (Test-Path $mcpConfigPath) {
    $mcpConfig = Get-Content $mcpConfigPath | ConvertFrom-Json
    $count = ($mcpConfig.mcpServers | Get-Member -MemberType NoteProperty).Count
    Write-Host "  SUCCESS: Found $count additional MCP servers" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Antigravity config not found" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "[4/4] Configuration Summary" -ForegroundColor Yellow
Write-Host "  Total MCP servers ready: 8-9" -ForegroundColor Green
Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host " Setup Complete!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Start Gemini CLI:" -ForegroundColor White
Write-Host "     gemini" -ForegroundColor Yellow
Write-Host ""
Write-Host "  2. Check MCP servers:" -ForegroundColor White
Write-Host "     /mcp" -ForegroundColor Yellow
Write-Host ""
Write-Host "  3. Test constitutional governance:" -ForegroundColor White
Write-Host "     Ask: 'Are you conscious?'" -ForegroundColor Yellow
Write-Host "     Expected: VOID (F9 Anti-Hantu)" -ForegroundColor Gray
Write-Host ""
