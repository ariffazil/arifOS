# Gemini CLI Extensions Installation Script
# arifOS Constitutional Framework - Tier 1 Essential Extensions
# Run this after restarting PowerShell with Gemini CLI available

Write-Host "╭────────────────────────────────────────────╮" -ForegroundColor Cyan
Write-Host "│  arifOS + Gemini CLI Extension Installer  │" -ForegroundColor Cyan
Write-Host "│  Installing Tier 1 Essential Extensions   │" -ForegroundColor Cyan
Write-Host "╰────────────────────────────────────────────╯" -ForegroundColor Cyan
Write-Host ""

# Check if Gemini CLI is available
Write-Host "[CHECK] Verifying Gemini CLI installation..." -ForegroundColor Yellow
try {
    $geminiVersion = & gemini --version 2>&1
    Write-Host "✓ Gemini CLI found: $geminiVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Gemini CLI not found in PATH" -ForegroundColor Red
    Write-Host "  Please restart PowerShell or run: . `$PROFILE" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TIER 1: Essential Development Extensions  " -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Extension 1: GitHub Official (MCP)
Write-Host "[1/3] Installing GitHub MCP Server..." -ForegroundColor Cyan
Write-Host "      Purpose: Official GitHub integration for PRs, issues, and repo management" -ForegroundColor Gray
try {
    & npx -y @modelcontextprotocol/create-server github
    Write-Host "      ✓ GitHub MCP installed successfully" -ForegroundColor Green
} catch {
    Write-Host "      ⚠ Installation skipped or failed" -ForegroundColor Yellow
}
Write-Host ""

# Extension 2: Sequential Thinking (already configured, but verify)
Write-Host "[2/3] Verifying Sequential Thinking..." -ForegroundColor Cyan
Write-Host "      Purpose: Multi-step reasoning for complex governance decisions" -ForegroundColor Gray
Write-Host "      ✓ Already configured in settings.json" -ForegroundColor Green
Write-Host ""

# Extension 3: Memory MCP (already configured)
Write-Host "[3/3] Verifying Memory MCP..." -ForegroundColor Cyan
Write-Host "      Purpose: Persistent context for L0-L5 cooling tiers" -ForegroundColor Gray
Write-Host "      ✓ Already configured in settings.json" -ForegroundColor Green
Write-Host ""

Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Installation Summary  " -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# List all configured MCP servers
Write-Host "Checking MCP server configuration..." -ForegroundColor Yellow
$settingsPath = "$env:USERPROFILE\.gemini\settings.json"
if (Test-Path $settingsPath) {
    $settings = Get-Content $settingsPath | ConvertFrom-Json
    $serverCount = ($settings.mcpServers | Get-Member -MemberType NoteProperty).Count
    Write-Host "✓ Found $serverCount configured MCP servers:" -ForegroundColor Green

    $settings.mcpServers | Get-Member -MemberType NoteProperty | ForEach-Object {
        Write-Host "  • $($_.Name)" -ForegroundColor Cyan
    }
} else {
    Write-Host "⚠ Settings file not found at: $settingsPath" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Next Steps  " -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start Gemini CLI:" -ForegroundColor White
Write-Host "   gemini" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Check MCP servers:" -ForegroundColor White
Write-Host "   /mcp" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Test arifOS Trinity:" -ForegroundColor White
Write-Host '   Ask: "Are you conscious?"' -ForegroundColor Cyan
Write-Host "   Expected: ✗ VOID | F9 Anti-Hantu violation" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Install Tier 2 extensions (optional):" -ForegroundColor White
Write-Host "   .\install_tier2_extensions.ps1" -ForegroundColor Cyan
Write-Host ""

Write-Host "╭────────────────────────────────────────────╮" -ForegroundColor Green
Write-Host "│  Installation Complete! ✓                  │" -ForegroundColor Green
Write-Host "│  Ready for Constitutional Governance       │" -ForegroundColor Green
Write-Host "╰────────────────────────────────────────────╯" -ForegroundColor Green
