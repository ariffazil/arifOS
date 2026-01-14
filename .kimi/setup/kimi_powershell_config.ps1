# Kimi CLI PowerShell Autocomplete Configuration
# Place this in your PowerShell profile: $PROFILE
# Run: . $PROFILE to reload after adding

# Check if PSReadLine is available
if (Get-Module -ListAvailable PSReadLine) {
    
    # Import PSReadLine
    Import-Module PSReadLine
    
    # Set up predictive autocomplete (if terminal supports it)
    try {
        Set-PSReadLineOption -PredictionSource HistoryAndPlugin -ErrorAction Stop
        Set-PSReadLineOption -PredictionViewStyle ListView -ErrorAction Stop
        Write-Host "✅ Kimi CLI autocomplete enabled with predictive suggestions" -ForegroundColor Green
    }
    catch {
        # Fallback to basic autocomplete
        Set-PSReadLineOption -EditMode Windows
        Write-Host "⚠️  Basic autocomplete enabled (predictive not available in this terminal)" -ForegroundColor Yellow
    }
    
    # Enhanced key handlers for Kimi CLI
    Set-PSReadLineKeyHandler -Key Tab -Function MenuComplete
    Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
    Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward
    Set-PSReadLineKeyHandler -Key Ctrl+r -Function ReverseSearchHistory
    
    # Kimi-specific autocomplete patterns
    $kimiPatterns = @(
        "kimi",
        "kimi --help",
        "kimi --version", 
        "kimi --provider",
        "kimi --config",
        "kimi --skills"
    )
    
    # Custom argument completer for kimi commands
    Register-ArgumentCompleter -CommandName kimi -ScriptBlock {
        param($commandName, $parameterName, $wordToComplete, $commandAst, $fakeBoundParameters)
        
        $kimiCommands = @(
            "--help",
            "--version",
            "--provider", 
            "--config",
            "--skills",
            "--debug"
        )
        
        $kimiProviders = @(
            "openai",
            "anthropic", 
            "google",
            "moonshot"
        )
        
        switch ($parameterName) {
            "provider" { 
                $kimiProviders | Where-Object { $_ -like "$wordToComplete*" } 
            }
            default { 
                $kimiCommands | Where-Object { $_ -like "$wordToComplete*" } 
            }
        }
    }
    
    # Constitutional arifOS skill completions
    $arifosSkills = @(
        "/000",
        "/gitforge", 
        "/gitQC",
        "/gitseal",
        "/sabar",
        "/audit-constitution",
        "/verify-trinity",
        "/verify-sources",
        "/issue-verdict",
        "/track-alignment",
        "/anti-bypass-scan",
        "/ledger-audit"
    )
    
    # Function to complete arifOS skills in any command
    function Complete-ArifosSkills {
        param($wordToComplete)
        $arifosSkills | Where-Object { $_ -like "$wordToComplete*" }
    }
    
    # Register completer for skills when they appear in commands
    Register-ArgumentCompleter -Native -CommandName @("python", "python3", "py") -ScriptBlock {
        param($wordToComplete, $commandAst, $cursorPosition)
        
        # Check if this looks like an arifOS command
        $line = $commandAst.ToString()
        if ($line -match "arifos|scripts/|python.*arifos") {
            Complete-ArifosSkills $wordToComplete
        }
    }
    
    # Colors for better visibility
    Set-PSReadLineOption -Colors @{
        Command = "`e[93m"      # Yellow for commands
        Parameter = "`e[96m"   # Cyan for parameters  
        String = "`e[36m"      # Cyan for strings
        Number = "`e[97m"      # White for numbers
        Member = "`e[92m"      # Green for members
        Operator = "`e[90m"    # Gray for operators
        Type = "`e[37m"        # White for types
        Variable = "`e[92m"    # Green for variables
        InlinePrediction = "`e[97;2;3m"  # Dim white for predictions
    }
    
    # Show status
    Write-Host "🚀 Kimi CLI enhanced with PowerShell autocomplete" -ForegroundColor Cyan
    Write-Host "   Tab = menu complete | Ctrl+R = search history | Arrows = navigate" -ForegroundColor Gray
    
} else {
    Write-Host "⚠️  PSReadLine not available - autocomplete disabled" -ForegroundColor Red
}

# Kimi CLI helper functions
function khelp {
    Write-Host @"
🎯 Kimi CLI Quick Reference:
  kimi --help              # Show help
  kimi --skills            # List available skills  
  /000                     # Initialize constitutional session
  /gitforge               # Analyze entropy
  /gitQC                  # Validate constitutional compliance
  /gitseal "message"      # Request constitutional seal
  /sabar                  # Recovery from floor failures

💡 Tips:
  - Tab to complete commands
  - Ctrl+R to search command history
  - Use quotes for messages with spaces
"@ -ForegroundColor Cyan
}

function kskills {
    Write-Host "Available arifOS constitutional skills:" -ForegroundColor Green
    $arifosSkills | ForEach-Object { 
        Write-Host "  $_" -ForegroundColor Yellow 
    }
}

# Alias for quick access
Set-Alias -Name kh -Value khelp
Set-Alias -Name ks -Value kskills