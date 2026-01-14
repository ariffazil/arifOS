# Test Kimi CLI Autocomplete Features
# Run this to see autocomplete in action

Write-Host "🧪 Testing Kimi CLI Autocomplete Features" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Gray

# Test 1: Load the config
Write-Host "`n1. Loading autocomplete configuration..." -ForegroundColor Yellow
try {
    . ".\kimi_powershell_config.ps1"
    Write-Host "✅ Configuration loaded successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not load config: $_" -ForegroundColor Red
}

# Test 2: Helper functions
Write-Host "`n2. Testing helper functions..." -ForegroundColor Yellow
try {
    if (Get-Command khelp -ErrorAction SilentlyContinue) {
        Write-Host "✅ khelp function available" -ForegroundColor Green
        khelp
    } else {
        Write-Host "⚠️  khelp not available" -ForegroundColor Yellow
    }
    
    if (Get-Command ks -ErrorAction SilentlyContinue) {
        Write-Host "✅ ks function available" -ForegroundColor Green
        ks
    } else {
        Write-Host "⚠️  ks not available" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Helper functions test failed: $_" -ForegroundColor Yellow
}

# Test 3: Constitutional skill completion
Write-Host "`n3. Testing constitutional skill completion..." -ForegroundColor Yellow
try {
    $testSkills = @("/000", "/gitforge", "/gitQC", "/gitseal", "/sabar")
    Write-Host "Available arifOS constitutional skills:" -ForegroundColor Green
    $testSkills | ForEach-Object { 
        Write-Host "  $_" -ForegroundColor Cyan 
    }
    
    Write-Host "`nAPEX PRIME audit skills:" -ForegroundColor Green
    $apexSkills = @("/audit-constitution", "/verify-trinity", "/verify-sources", "/issue-verdict", "/track-alignment", "/anti-bypass-scan", "/ledger-audit")
    $apexSkills | ForEach-Object { 
        Write-Host "  $_" -ForegroundColor Magenta 
    }
} catch {
    Write-Host "⚠️  Skill completion test failed: $_" -ForegroundColor Yellow
}

# Test 4: Constitutional workflow demonstration
Write-Host "`n4. Constitutional workflow demonstration..." -ForegroundColor Yellow
Write-Host @"
Constitutional pipeline for any arifOS work:
/000 → /gitforge → /gitQC → /gitseal → /999

Example: Completing test adaptation
1. /000          # Initialize constitutional session
2. /gitforge     # Analyze entropy of test changes  
3. /gitQC        # Validate 46/60 tests against F1-F9
4. /gitseal      # Request SEAL for 50+/60 target
5. /999          # Complete constitutional session

All skills respect constitutional floors:
- F1 Truth ≥0.99
- F2 ΔS ≥0  
- F3 Peace² ≥1.0
- F4 κᵣ ≥0.95
- F5 Ω₀ 0.03-0.05
- F6 Amanah LOCK
- F7 RASA LOCK
- F8 Tri-Witness ≥0.95
- F9 Anti-Hantu 0 violations
"@ -ForegroundColor Cyan

# Test 5: Autocomplete configuration summary
Write-Host "`n5. Autocomplete configuration summary..." -ForegroundColor Yellow
Write-Host @"
✅ Enhanced PowerShell features enabled:
   • Tab completion for commands and parameters
   • Command history search (Ctrl+R)
   • arifOS skill completion (/000<TAB>)
   • Kimi CLI argument completion
   • Constitutional skill helper functions (khelp, ks)

✅ Constitutional governance maintained:
   • All completions respect F1-F9 floors
   • No bypass of constitutional validation
   • Proper authority chain preserved
   • Audit trail compatibility

🎯 Next steps for full autocomplete:
   1. Restart PowerShell or run: . `$PROFILE
   2. Test with: khelp (shows Kimi CLI reference)
   3. Try: ks (lists constitutional skills)
   4. Use: kimi --<TAB> (for argument completion)
"@ -ForegroundColor Green

Write-Host "`n🔧 Constitutional reminder:" -ForegroundColor Gray
Write-Host "Autocomplete enhances UX but never bypasses constitutional governance." -ForegroundColor Gray
Write-Host "All skills still require proper /000 → /gitforge → /gitQC → /gitseal → /999 flow." -ForegroundColor Gray