# Bash/Zsh Profile - Auto-Governed AI Sessions
# Add to ~/.bashrc or ~/.zshrc

# A CLIP Environment Variables
export ARIFOS_ACLIP_ENABLED=1
export ARIFOS_SESSION_PATH=".arifos_clip/session.json"

# Function: Start governed Copilot chat
aclip-copilot() {
    echo -e "\033[36m[A CLIP] Starting governed GitHub Copilot session...\033[0m"
    echo -e "\033[90mInstructions: .github/copilot-instructions.md\033[0m"
    echo -e "\033[90mProtocol: 000→111→666→999\033[0m"
}

# Function: Start governed Claude Code
aclip-claude() {
    echo -e "\033[36m[A CLIP] Starting governed Claude Code session...\033[0m"
    echo -e "\033[90mInstructions: .claude/aclip-instructions.md\033[0m"
    echo -e "\033[90mProtocol: 000→111→666→999\033[0m"
}

# Show A CLIP status on terminal start
if [ -f ".arifos_clip/session.json" ]; then
    STATUS=$(jq -r '.status' .arifos_clip/session.json 2>/dev/null)
    echo -e "\033[32m[A CLIP] Session active: $STATUS\033[0m"
fi

# Reminder function
aclip() {
    cat <<EOF
$(tput setaf 6)A CLIP Protocol Active$(tput sgr0)

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
EOF
}
