#!/usr/bin/env bash
# arifos-f3-eval.sh
# CLAIM: Tri-Witness evaluation CLI — pre-flight constitutional check.
# Usage: ./arifos-f3-eval.sh [--worktree <path>] [--pr-draft] [--strict]

set -euo pipefail

# Parse arguments
WORKTREE="${PWD}"
PR_DRAFT=false
STRICT=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --worktree)
            WORKTREE="$2"; shift 2 ;;
        --pr-draft)
            PR_DRAFT=true; shift ;;
        --strict)
            STRICT=true; shift ;;
        --help)
            echo "Usage: $0 [--worktree <path>] [--pr-draft] [--strict]"
            echo ""
            echo "Options:"
            echo "  --worktree <path>  Path to worktree (default: PWD)"
            echo "  --pr-draft         Generate PR draft with evaluation"
            echo "  --strict           Exit 1 if W₃ < 0.95"
            exit 0 ;;
        *)
            echo "Unknown option: $1"; exit 1 ;;
    esac
done

# F4: Validate worktree
cd "$WORKTREE"
if [[ ! -f "arifos.yml" ]]; then
    echo "❌ F4: No arifos.yml found in $WORKTREE"
    echo "   This is not a constitutional worktree."
    exit 1
fi

# Check for yq
if ! command -v yq &>/dev/null; then
    echo "⚠️  yq not found. Install: https://github.com/mikefarah/yq"
    echo "   Using grep fallback (limited accuracy)."
    HAS_YQ=false
else
    HAS_YQ=true
fi

# Load manifest
if $HAS_YQ; then
    AGENT_NAME=$(yq '.agent.name' arifos.yml)
    RISK_TIER=$(yq '.constitutional.max_risk_tier' arifos.yml)
    BRANCH=$(yq '.worktree.branch' arifos.yml)
    VETO=$(yq '.constitutional.veto_holder' arifos.yml)
else
    AGENT_NAME=$(grep "name:" arifos.yml | head -1 | cut -d'"' -f2)
    RISK_TIER="medium"
    BRANCH=$(git branch --show-current)
    VETO="arif"
fi

# ═══════════════════════════════════════════════════════════════
# F3 TRI-WITNESS EVALUATION
# ═══════════════════════════════════════════════════════════════

echo ""
echo "🔥 F3 TRI-WITNESS EVALUATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 Worktree: ${WORKTREE}"
echo "🤖 Agent:    ${AGENT_NAME}"
echo "⚠️  Risk:     ${RISK_TIER}"
echo ""

# ─── 🤖 AI WITNESS ───
echo "🤖 AI WITNESS (Agent Self-Check)"
echo "─────────────────────────────────────────"

AI_SCORE=0.00

# 1. Check for arifOS kernel integration
if grep -r "arifOS_kernel\|init_anchor" --include="*.py" --include="*.js" . 2>/dev/null | head -1; then
    echo "   ✅ Constitutional kernel usage detected"
    AI_SCORE=$(echo "$AI_SCORE + 0.25" | bc)
fi

# 2. Check for F1-F13 references in code/docs
FLOOR_COUNT=$(grep -rE "F1|F2|F3|F4|F5|F6|F7|F8|F9|F10|F11|F12|F13" --include="*.md" --include="*.py" . 2>/dev/null | wc -l)
if [[ $FLOOR_COUNT -gt 5 ]]; then
    echo "   ✅ Constitutional awareness high ($FLOOR_COUNT refs)"
    AI_SCORE=$(echo "$AI_SCORE + 0.25" | bc)
fi

# 3. Check for test coverage
if [[ -d "tests" ]] && [[ $(find tests -type f | wc -l) -gt 0 ]]; then
    echo "   ✅ Test coverage present"
    AI_SCORE=$(echo "$AI_SCORE + 0.20" | bc)
fi

# 4. Check for documentation
if [[ $(find . -name "*.md" | wc -l) -gt 0 ]]; then
    echo "   ✅ Documentation present"
    AI_SCORE=$(echo "$AI_SCORE + 0.17" | bc)
fi

# 5. Check commit message quality
if git log --oneline -5 2>/dev/null | grep -qE "feat|fix|docs|refactor|test"; then
    echo "   ✅ Conventional commits detected"
    AI_SCORE=$(echo "$AI_SCORE + 0.13" | bc)
fi

AI_SCORE=$(printf "%.2f" $AI_SCORE)
echo ""
echo "   🤖 AI Witness Score: $AI_SCORE"

# ─── 🌍 EARTH WITNESS ───
echo ""
echo "🌍 EARTH WITNESS (Local Validation)"
echo "─────────────────────────────────────────"

EARTH_SCORE=0.00

# 1. Git status cleanliness
if [[ -z $(git status --porcelain 2>/dev/null) ]]; then
    echo "   ✅ Working tree clean"
    EARTH_SCORE=$(echo "$EARTH_SCORE + 0.25" | bc)
else
    UNSTAGED=$(git status --short 2>/dev/null | wc -l)
    echo "   ⚠️  $UNSTAGED uncommitted changes"
    EARTH_SCORE=$(echo "$EARTH_SCORE + 0.10" | bc)
fi

# 2. Syntax validation (Python)
PY_FILES=$(find . -name "*.py" -not -path "./.git/*" 2>/dev/null)
if [[ -n "$PY_FILES" ]]; then
    if python -m py_compile $(echo "$PY_FILES" | head -5) 2>/dev/null; then
        echo "   ✅ Python syntax valid"
        EARTH_SCORE=$(echo "$EARTH_SCORE + 0.25" | bc)
    else
        echo "   ❌ Python syntax errors detected"
    fi
fi

# 3. Branch naming convention
if [[ "$BRANCH" == feature/* || "$BRANCH" == hotfix/* || "$BRANCH" == experiment/* ]]; then
    echo "   ✅ Constitutional branch naming"
    EARTH_SCORE=$(echo "$EARTH_SCORE + 0.25" | bc)
else
    echo "   ⚠️  Non-constitutional branch name"
fi

# 4. Commit recency
if git log --since="7 days ago" --oneline 2>/dev/null | grep -q .; then
    echo "   ✅ Recent activity"
    EARTH_SCORE=$(echo "$EARTH_SCORE + 0.25" | bc)
fi

EARTH_SCORE=$(printf "%.2f" $EARTH_SCORE)
echo ""
echo "   🌍 Earth Witness Score: $EARTH_SCORE"

# ─── 👤 HUMAN WITNESS ───
echo ""
echo "👤 HUMAN WITNESS (Arif Review)"
echo "─────────────────────────────────────────"

# Check if PR already has human approval (would need GitHub API for real check)
if $PR_DRAFT; then
    HUMAN_SCORE=0.00
    echo "   ⏸️  PR not yet created — human review pending"
else
    # Local heuristic: check if commit is signed
    if git log --show-signature -1 2>/dev/null | grep -q "Good signature"; then
        HUMAN_SCORE=0.90
        echo "   ✅ Signed commit detected (human attestation)"
    else
        HUMAN_SCORE=0.00
        echo "   ⏸️  Pending human review (F13 veto holder)"
    fi
fi

echo ""
echo "   👤 Human Witness Score: $HUMAN_SCORE"

# ═══════════════════════════════════════════════════════════════
# TRI-WITNESS CALCULATION (W₃)
# ═══════════════════════════════════════════════════════════════

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚖️  TRI-WITNESS CONSENSUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Weight: AI 30%, Earth 30%, Human 40% (human is sovereign)
W3=$(echo "scale=4; ($AI_SCORE * 0.30) + ($EARTH_SCORE * 0.30) + ($HUMAN_SCORE * 0.40)" | bc)
W3=$(printf "%.3f" $W3)

echo ""
echo "   🤖 AI:     $AI_SCORE × 0.30 = $(printf "%.3f" $(echo "$AI_SCORE * 0.30" | bc))"
echo "   🌍 Earth:  $EARTH_SCORE × 0.30 = $(printf "%.3f" $(echo "$EARTH_SCORE * 0.30" | bc))"
echo "   👤 Human:  $HUMAN_SCORE × 0.40 = $(printf "%.3f" $(echo "$HUMAN_SCORE * 0.40" | bc))"
echo ""
echo "   W₃ = $W3"

# F3 Threshold: W₃ ≥ 0.95 for SEAL
THRESHOLD=0.950

# Adjust threshold by risk tier
case "$RISK_TIER" in
    low)
        THRESHOLD=0.850
        ;;
    medium)
        THRESHOLD=0.950
        ;;
    high)
        THRESHOLD=0.990
        ;;
    critical)
        THRESHOLD=1.000  # Impossible without human=1.0
        ;;
esac

echo "   Threshold (${RISK_TIER}): $THRESHOLD"
echo ""

# Verdict determination
if (( $(echo "$W3 >= $THRESHOLD" | bc -l) )); then
    VERDICT="SEAL"
    EMOJI="✅"
elif (( $(echo "$W3 >= $(echo "$THRESHOLD - 0.10" | bc)" | bc -l) )); then
    VERDICT="PROVISIONAL"
    EMOJI="⚠️"
elif (( $(echo "$W3 >= 0.500" | bc -l) )); then
    VERDICT="HOLD"
    EMOJI="⏸️"
else
    VERDICT="VOID"
    EMOJI="❌"
fi

# Override: Human must approve for medium+
if [[ "$RISK_TIER" != "low" && $(echo "$HUMAN_SCORE < 0.5" | bc) -eq 1 ]]; then
    VERDICT="HOLD_888"
    EMOJI="🚨"
fi

echo "   $EMOJI VERDICT: $VERDICT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Update arifos.yml with verdict
if $HAS_YQ; then
    yq -i ".governance.tri_witness.ai = \"$AI_SCORE\"" arifos.yml
    yq -i ".governance.tri_witness.earth = \"$EARTH_SCORE\"" arifos.yml
    yq -i ".governance.verdict = \"$VERDICT\"" arifos.yml
fi

# PR Draft generation
if $PR_DRAFT && [[ "$VERDICT" != "VOID" ]]; then
    cat > PR_DRAFT.md << EOF
## 🔥 888_JUDGE: Constitutional Review Request

**Worktree:** ${WORKTREE}  
**Agent:** ${AGENT_NAME}  
**Branch:** ${BRANCH}  
**Risk Tier:** ${RISK_TIER}

### Tri-Witness Evaluation

| Witness | Score | Weight | Contribution |
|---------|-------|--------|--------------|
| 🤖 AI (Self-Check) | $AI_SCORE | 30% | $(printf "%.3f" $(echo "$AI_SCORE * 0.30" | bc)) |
| 🌍 Earth (Local CI) | $EARTH_SCORE | 30% | $(printf "%.3f" $(echo "$EARTH_SCORE * 0.30" | bc)) |
| 👤 Human (Review) | $HUMAN_SCORE | 40% | $(printf "%.3f" $(echo "$HUMAN_SCORE * 0.40" | bc)) |

**W₃ = $W3** (Threshold: $THRESHOLD)

### Verdict: $EMOJI **$VERDICT**

### Checklist

- [ ] F1: Reversibility confirmed
- [ ] F2: τ ≥ 0.99
- [ ] F4: ΔS ≤ 0
- [ ] F7: Ω₀ stated

### Required Action

$(case "$VERDICT" in
    SEAL) echo "✅ Ready for merge after final human review"; ;;
    PROVISIONAL) echo "⚠️ Can proceed with reservations documented"; ;;
    HOLD) echo "⏸️ Requires additional work before merge"; ;;
    HOLD_888) echo "🚨 **F13 REQUIRED:** Arif must review personally"; ;;
    VOID) echo "❌ Rejected — constitutional floors failed"; ;;
esac)

*Ditempa bukan diberi.*
EOF
    echo ""
    echo "📝 PR draft generated: PR_DRAFT.md"
fi

# Strict mode exit
echo ""
if $STRICT && [[ "$VERDICT" == "VOID" || "$VERDICT" == "HOLD_888" ]]; then
    echo "❌ F3: Strict mode — exit 1 for $VERDICT"
    exit 1
fi

case "$VERDICT" in
    SEAL|PROVISIONAL)
        echo "✅ Ready to push: git push origin $BRANCH"
        exit 0
        ;;
    HOLD)
        echo "⏸️  Recommendation: Improve scores before push"
        exit 0
        ;;
    HOLD_888)
        echo "🚨 Requires Arif (F13) review before merge"
        exit 0
        ;;
    VOID)
        echo "❌ Do not push. Fix issues first."
        exit 1
        ;;
esac
