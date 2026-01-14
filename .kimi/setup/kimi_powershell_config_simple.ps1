# Kimi CLI PowerShell Autocomplete Configuration (Simple Version)
# This works in all PowerShell terminals

Write-Host "🚀 Kimi CLI enhanced with basic PowerShell autocomplete" -ForegroundColor Cyan

# Basic PSReadLine setup (works in all terminals)
if (Get-Module -ListAvailable PSReadLine) {
    Import-Module PSReadLine
    
    # Basic autocomplete (no colors that break)
    Set-PSReadLineOption -EditMode Windows
    Set-PSReadLineOption -HistorySearchCursorMovesToEnd
    Set-PSReadLineOption -HistorySaveStyle SaveIncrementally
    Set-PSReadLineOption -MaximumHistoryCount 1000
    
    # Key handlers for navigation
    Set-PSReadLineKeyHandler -Key Tab -Function MenuComplete
    Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
    Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward
    Set-PSReadLineKeyHandler -Key Ctrl+r -Function ReverseSearchHistory
    
    Write-Host "✅ Basic autocomplete enabled" -ForegroundColor Green
} else {
    Write-Host "⚠️  PSReadLine not available - basic command line only" -ForegroundColor Yellow
}

# Kimi CLI helper functions
function khelp {
    Write-Host @"
🎯 Kimi CLI Quick Reference:
  kimi --help              # Show help
  kimi --skills            # List available skills  
  kimi --provider          # Set provider
  kimi --config            # Show config

🏛️ Constitutional Skills:
  /000       # Initialize constitutional session
  /gitforge  # Analyze entropy
  /gitQC     # Validate constitutional compliance
  /gitseal   # Request constitutional seal
  /sabar     # Recovery from floor failures

⚖️ APEX PRIME Skills:
  /audit-constitution   # Comprehensive F1-F12 validation
  /verify-trinity      # Separation-of-powers audit
  /verify-sources      # PRIMARY source verification
  /issue-verdict       # Constitutional verdict
  /track-alignment     # Track boundary enforcement
  /anti-bypass-scan    # Zero-bypass detection
  /ledger-audit        # Cryptographic integrity

💡 Tips:
  - Tab to complete commands
  - Ctrl+R to search history
  - Use quotes for messages with spaces
"@ 
}

function ks {
    Write-Host "Available arifOS constitutional skills:" -ForegroundColor Green
    Write-Host "  Core Skills:" -ForegroundColor Yellow
    @("/000", "/gitforge", "/gitQC", "/gitseal", "/sabar") | ForEach-Object {
        Write-Host "    $_" -ForegroundColor White
    }
    
    Write-Host "`n  APEX PRIME Skills:" -ForegroundColor Magenta
    @("/audit-constitution", "/verify-trinity", "/verify-sources", "/issue-verdict", "/track-alignment", "/anti-bypass-scan", "/ledger-audit") | ForEach-Object {
        Write-Host "    $_" -ForegroundColor White
    }
}

# Constitutional workflow reminder
function constitutional-workflow {
    Write-Host "🏛️ Constitutional workflow for any arifOS operation:" -ForegroundColor Cyan
    Write-Host "  /000 → /gitforge → /gitQC → /gitseal → /999" -ForegroundColor Yellow
    Write-Host "`n  Example: Completing constitutional meta-search tests" -ForegroundColor White
    Write-Host "  1. /000          # Initialize session" -ForegroundColor Gray
    Write-Host "  2. /gitforge     # Analyze test changes" -ForegroundColor Gray  
    Write-Host "  3. /gitQC        # Validate 46/60→50+/60 progression" -ForegroundColor Gray
    Write-Host "  4. /gitseal      # Request SEAL for 83%+ threshold" -ForegroundColor Gray
    Write-Host "  5. /999          # Complete constitutional session" -ForegroundColor Gray
}

# Aliases for quick access
Set-Alias -Name kh -Value khelp
Set-Alias -Name kw -Value constitutional-workflow

Write-Host "✅ Kimi CLI autocomplete ready!" -ForegroundColor Green
Write-Host "Available commands: khelp, ks, kh, kw" -ForegroundColor White
Write-Host "Use: Tab for completion, Ctrl+R for history" -ForegroundColor Gray