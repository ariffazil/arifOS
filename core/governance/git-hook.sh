#!/bin/bash
# arifOS Governance Pre-Push Hook
# Routes force pushes and destructive git operations through arifOS 888_JUDGE.
# Installed via: ln -s /root/arifOS/core/governance/git-hook.sh .git/hooks/pre-push
#
# DITEMPA BUKAN DIBERI — governance is forged into the execution path, not bolted on after.

REMOTE="$1"
URL="$2"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  arifOS Governance Gate — F1-F13 Constitutional Check   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Read stdin to check what's being pushed
has_force=0
while read local_ref local_sha remote_ref remote_sha; do
    # Check for force push: +refs/heads/...
    if [[ "$local_ref" == +* ]]; then
        has_force=1
        echo "⚠️  FORCE PUSH DETECTED: $local_ref → $remote_ref"
    fi
    # Check for delete
    if [[ "$local_sha" == "0000000000000000000000000000000000000000" ]]; then
        has_force=1
        echo "⚠️  BRANCH DELETE DETECTED: $remote_ref"
    fi
done

if [[ $has_force -eq 0 ]]; then
    echo "✅ Normal push — governance gate passed."
    exit 0
fi

# Route to arifOS 888_JUDGE
echo ""
echo "🔒 Routing through arifOS 888_JUDGE..."

RESULT=$(python3 /root/arifOS/core/governance/preflight.py "git push --force $URL" 2>&1)
EXIT_CODE=$?

case $EXIT_CODE in
    0)
        echo "✅ arifOS SEAL — force push authorized."
        exit 0
        ;;
    1)
        echo ""
        echo "⛔ arifOS HOLD — force push requires F13 SOVEREIGN (Arif) approval."
        echo "   The operation is PAUSED, not denied."
        echo "   Arif can approve with: preflight.py --seal"
        exit 1
        ;;
    2|*)
        echo ""
        echo "🚫 arifOS VOID — force push BLOCKED by constitutional governance."
        echo "   This operation violates F1-F13 floors."
        echo "   Do not retry. Do not rephrase."
        exit 1
        ;;
esac
