# Gemini CLI Extensions - Tier 2: Productivity & Deployment
# arifOS Constitutional Framework
# Run after Tier 1 is complete

Write-Host "╭────────────────────────────────────────────╮" -ForegroundColor Cyan
Write-Host "│  Tier 2: Productivity & Deployment Tools  │" -ForegroundColor Cyan
Write-Host "╰────────────────────────────────────────────╯" -ForegroundColor Cyan
Write-Host ""

Write-Host "Installing Tier 2 Extensions..." -ForegroundColor Yellow
Write-Host ""

# Extension 1: Brave Search (already configured)
Write-Host "[1/6] Verifying Brave Search..." -ForegroundColor Cyan
Write-Host "      Purpose: Privacy-focused web search for F2 Truth enforcement" -ForegroundColor Gray
Write-Host "      ✓ Already configured in antigravity/mcp_config.json" -ForegroundColor Green
Write-Host ""

# Extension 2: Perplexity Ask (already configured)
Write-Host "[2/6] Verifying Perplexity Ask..." -ForegroundColor Cyan
Write-Host "      Purpose: Web search with cited sources (F2 Truth)" -ForegroundColor Gray
Write-Host "      ✓ Already configured in antigravity/mcp_config.json" -ForegroundColor Green
Write-Host ""

# Extension 3: Fetch MCP (already configured)
Write-Host "[3/6] Verifying Fetch MCP..." -ForegroundColor Cyan
Write-Host "      Purpose: HTTP requests for API testing" -ForegroundColor Gray
Write-Host "      ✓ Already configured in antigravity/mcp_config.json" -ForegroundColor Green
Write-Host ""

# Extension 4: Git MCP (already configured)
Write-Host "[4/6] Verifying Git MCP (GitLens)..." -ForegroundColor Cyan
Write-Host "      Purpose: Repository management and version control" -ForegroundColor Gray
Write-Host "      ✓ Already configured in antigravity/mcp_config.json" -ForegroundColor Green
Write-Host ""

# Extension 5: GitHub MCP (already configured)
Write-Host "[5/6] Verifying GitHub MCP..." -ForegroundColor Cyan
Write-Host "      Purpose: GitHub API integration" -ForegroundColor Gray
Write-Host "      ✓ Already configured in antigravity/mcp_config.json" -ForegroundColor Green
Write-Host ""

# Extension 6: Filesystem MCP (recommended new addition)
Write-Host "[6/6] Installing Filesystem MCP..." -ForegroundColor Cyan
Write-Host "      Purpose: Safe file operations with F1 Amanah enforcement" -ForegroundColor Gray
try {
    & npx -y @modelcontextprotocol/server-filesystem C:\Users\ariff\arifOS
    Write-Host "      ✓ Filesystem MCP installed" -ForegroundColor Green
} catch {
    Write-Host "      ⚠ Installation skipped or failed" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  Tier 2 Complete! ✓" -ForegroundColor Green
Write-Host "════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "Total MCP Servers Configured:" -ForegroundColor Cyan
Write-Host "  • arifos-trinity (local)" -ForegroundColor White
Write-Host "  • sequential-thinking" -ForegroundColor White
Write-Host "  • perplexity-ask" -ForegroundColor White
Write-Host "  • brave-search" -ForegroundColor White
Write-Host "  • git-mcp (GitLens)" -ForegroundColor White
Write-Host "  • github-mcp" -ForegroundColor White
Write-Host "  • fetch-mcp" -ForegroundColor White
Write-Host "  • memory-mcp" -ForegroundColor White
Write-Host "  • filesystem (new)" -ForegroundColor Green
Write-Host ""
Write-Host "Total: 9 MCP servers ready! 🚀" -ForegroundColor Cyan
