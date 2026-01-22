# PowerShell Profile - Auto-Governed AI Sessions
# Location: $PROFILE (typically ~\Documents\PowerShell\Microsoft.PowerShell_profile.ps1)

# A CLIP Environment Variables
$env:ARIFOS_ACLIP_ENABLED = "1"
$env:ARIFOS_SESSION_PATH = ".arifos_clip/session.json"

# Function: Start governed Copilot chat
function Start-GovernedCopilot {
    Write-Host "[A CLIP] Starting governed GitHub Copilot session..." -ForegroundColor Cyan
    Write-Host "Instructions: .github/copilot-instructions.md" -ForegroundColor Gray
    Write-Host "Protocol: 000→111→666→999" -ForegroundColor Gray
    # Copilot will read .github/copilot-instructions.md automatically
}

# Function: Start governed Claude Code
function Start-GovernedClaude {
    Write-Host "[A CLIP] Starting governed Claude Code session..." -ForegroundColor Cyan
    Write-Host "Instructions: .claude/aclip-instructions.md" -ForegroundColor Gray
    Write-Host "Protocol: 000→111→666→999" -ForegroundColor Gray
    # Claude Code will read .claude/aclip-instructions.md
}

# Aliases for quick start
Set-Alias -Name aclip-copilot -Value Start-GovernedCopilot
Set-Alias -Name aclip-claude -Value Start-GovernedClaude

# Show A CLIP status on terminal start
if (Test-Path ".arifos_clip/session.json") {
    $session = Get-Content ".arifos_clip/session.json" | ConvertFrom-Json
    Write-Host "[A CLIP] Session active: $($session.status)" -ForegroundColor Green
}

# Reminder function
function Show-AClip {
    Write-Host @"
A CLIP Protocol Active

Stages: 000 → 111 → 222 → 333 → 444 → 555 → 666 → 777 → 888 → 999

Stage 666 checks 9 floors:
F1 Amanah, F2 Truth, F3 Tri-Witness, F4 DeltaS, F5 Peace²,
F6 Kr, F7 Omega0, F8 G, F9 C_dark

Commands:
  000 void "<task>"     - Start session
  666 align             - Check floors
  888 hold              - Pause for review
  999 seal --apply      - Execute

Human has veto power. AI proposes, human decides.
"@ -ForegroundColor Cyan
}

Set-Alias -Name aclip -Value Show-AClip
