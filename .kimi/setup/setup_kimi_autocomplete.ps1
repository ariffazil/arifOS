# Setup Kimi CLI Autocomplete for PowerShell
# Run this script to enable enhanced autocomplete for Kimi CLI

Write-Host "🎯 Setting up Kimi CLI autocomplete for PowerShell..." -ForegroundColor Cyan

# Get the PowerShell profile path
$profilePath = $PROFILE
Write-Host "PowerShell profile location: $profilePath" -ForegroundColor Gray

# Check if profile exists, create if not
if (!(Test-Path $profilePath)) {
    Write-Host "Creating PowerShell profile..." -ForegroundColor Yellow
    New-Item -Path $profilePath -ItemType File -Force | Out-Null
}

# Read the config file
$configContent = Get-Content -Path "./kimi_powershell_config.ps1" -Raw

# Check if already configured
if (Select-String -Path $profilePath -Pattern "kimi_powershell_config" -Quiet) {
    Write-Host "✅ Kimi CLI autocomplete already configured in profile" -ForegroundColor Green
} else {
    Write-Host "Adding Kimi CLI autocomplete to profile..." -ForegroundColor Yellow
    
    # Add configuration to profile
    @"

# Kimi CLI Autocomplete Configuration
# Added: $(Get-Date)
# Source: arifOS constitutional framework

# Load Kimi CLI autocomplete
if (Test-Path "$(Split-Path $PROFILE)\kimi_powershell_config.ps1") {
    . "$(Split-Path $PROFILE)\kimi_powershell_config.ps1"
} elseif (Test-Path "$PWD\kimi_powershell_config.ps1") {
    . "$PWD\kimi_powershell_config.ps1"
}
"@ | Add-Content -Path $profilePath
    
    Write-Host "✅ Kimi CLI autocomplete added to PowerShell profile" -ForegroundColor Green
}

# Copy config to profile directory for easy access
$profileDir = Split-Path $profilePath -Parent
$configDest = Join-Path $profileDir "kimi_powershell_config.ps1"

if (!(Test-Path $configDest)) {
    Copy-Item -Path "./kimi_powershell_config.ps1" -Destination $configDest -Force
    Write-Host "✅ Config file copied to profile directory" -ForegroundColor Green
}

Write-Host @"

🎉 Kimi CLI autocomplete setup complete!

Next steps:
1. Restart PowerShell or run: . `$PROFILE
2. Test with: khelp
3. Try: kimi --<TAB> (for autocomplete)
4. Use: ks (to list arifOS skills)

Available enhancements:
- Tab completion for kimi commands
- Command history search (Ctrl+R)
- arifOS skill completion (/000<TAB>)
- Constitutional skill helper functions

For constitutional work:
- /000 → /gitforge → /gitQC → /gitseal → /999
- All skills respect F1-F9 floors
- No self-sealing (Kimi cannot approve own work)

"@ -ForegroundColor Cyan

# Test the configuration
Write-Host "`nTesting configuration..." -ForegroundColor Yellow
try {
    if (Get-Command khelp -ErrorAction SilentlyContinue) {
        Write-Host "✅ Helper functions loaded" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Helper functions not yet available (restart PowerShell)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Configuration will be active after PowerShell restart" -ForegroundColor Yellow
}

Write-Host "`n Constitutional reminder: All autocomplete respects F1-F9 floors" -ForegroundColor Gray