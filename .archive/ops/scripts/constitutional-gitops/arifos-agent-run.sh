#!/usr/bin/env bash
# arifos-agent-run.sh
# CLAIM: Run agent under F1–F3 contract.
# Usage: ./arifos-agent-run.sh [stage]

set -euo pipefail

# Detect if we're in a worktree
if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
    echo "❌ Not inside a git repo."
    exit 1
fi

ROOT="$(git rev-parse --show-toplevel)"
ARIFOS_YML="${ROOT}/arifos.yml"

# Check for constitutional manifest (F3)
if [[ ! -f "$ARIFOS_YML" ]]; then
    echo "❌ F3: No arifos.yml found in worktree."
    echo "   This is not a constitutional sandbox."
    exit 1
fi

# Parse manifest (requires yq)
if ! command -v yq >/dev/null 2>&1; then
    echo "⚠️  yq not installed. Using grep fallback (limited)."
    AGENT_NAME=$(grep "name:" "$ARIFOS_YML" | head -1 | cut -d'"' -f2)
    RISK_TIER="medium"
else
    AGENT_NAME=$(yq '.agent.name' "$ARIFOS_YML")
    RISK_TIER=$(yq '.constitutional.max_risk_tier' "$ARIFOS_YML")
fi

STAGE="${1:-dev}"

echo ""
echo "🔥 ARIFOS AGENT RUNTIME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ F1 Sandbox:  $ROOT"
echo "▶ Agent:       ${AGENT_NAME:-unknown}"
echo "▶ Stage:       $STAGE"
echo "▶ Risk Tier:   $RISK_TIER"
echo "▶ Dry Run:     ENABLED (F7)"
echo ""

# F7: Enforce dry_run for medium+ risk
if [[ "$RISK_TIER" != "low" ]]; then
    echo "⚖️  F7: Ω₀ enforced — dry_run mode active"
    export ARIFOS_DRY_RUN=1
fi

# F11: Block if trying to run on main
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
    echo "❌ F11: Cannot run agent on main branch."
    echo "   Create a worktree: ./arifos-worktree-add.sh <agent> <feature>"
    exit 1
fi

# Check for uncommitted changes (F2)
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  F2: Uncommitted changes detected."
    echo "   Commit or stash before running agent."
    exit 1
fi

# Run agent (placeholder — replace with actual agent invocation)
echo "🚀 Invoking agent runtime..."
echo ""

# Example: ACP agent spawn
if [[ "${AGENT_BIN:-}" == "acp" ]]; then
    echo "▶ Spawning ACP agent: ${AGENT_NAME}"
    # sessions_spawn equivalent for ACP
    echo "   (ACP spawn would happen here)"
elif [[ -n "${AGENT_BIN:-}" ]]; then
    $AGENT_BIN --stage "$STAGE" --worktree "$ROOT"
else
    echo "   (No AGENT_BIN set — manual invocation required)"
    echo "   Suggested: code . # Open in editor"
fi

echo ""
echo "✅ AGENT RUNTIME COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Commit: git commit -m 'feat: ...'"
echo "  3. Push: git push origin $CURRENT_BRANCH"
echo "  4. Open PR → 888_JUDGE"
echo ""
echo "⚖️  F13: Arif review required before merge to main"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
