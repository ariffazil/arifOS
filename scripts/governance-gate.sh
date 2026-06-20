#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# arifOS Federation — Governance Gate
# Binary PASS / FAIL for every push to main
# DITEMPA BUKAN DIBERI 🧠✨🌏
# ═══════════════════════════════════════════════════════════════════════════
#
# This script runs BASIC constitutional hygiene checks on any organ repo.
# It answers: "Is this repo aligned with the arifOS federation contract?"
#
# Usage: bash scripts/governance-gate.sh [--strict]
#   --strict: fail on warnings too
#
# Exit codes:
#   0 = ALL PASS (governed push allowed)
#   1 = FAIL (block push until fixed)
#   2 = WARN (non-blocking, but signal drift)
# ═══════════════════════════════════════════════════════════════════════════
set -euo pipefail

STRICT=false
[[ "${1:-}" == "--strict" ]] && STRICT=true

PASS=0; FAIL=0; WARN=0
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

check() {
    local name="$1"; local result="$2"; local detail="${3:-}"
    case "$result" in
        PASS) echo -e "  ${GREEN}✅ $name${NC}"; PASS=$((PASS + 1)) ;;
        WARN) echo -e "  ${YELLOW}⚠️  $name — $detail${NC}"; WARN=$((WARN + 1)) ;;
        FAIL) echo -e "  ${RED}❌ $name — $detail${NC}"; FAIL=$((FAIL + 1)) ;;
    esac
}

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  🛡️  arifOS Federation — Governance Gate        ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ─── Q1: FEDERATION_CONTRACT.md exists? ─────────────────────────────────
if [ -f "FEDERATION_CONTRACT.md" ]; then
    check "Federation Contract present" PASS
else
    check "Federation Contract present" FAIL "FEDERATION_CONTRACT.md missing — every organ must have one"
fi

# ─── Q2: AGENTS.md exists? ──────────────────────────────────────────────
if [ -f "AGENTS.md" ]; then
    check "AGENTS.md present" PASS
else
    check "AGENTS.md present" FAIL "AGENTS.md missing — agents cannot bootstrap without it"
fi

# ─── Q3: README.md is comprehensive (≥500 lines)? ────────────────────────
README_LINES=$(wc -l < README.md 2>/dev/null || echo 0)
if [ "$README_LINES" -ge 500 ]; then
    check "README comprehensive (${README_LINES} lines)" PASS
elif [ "$README_LINES" -ge 200 ]; then
    check "README comprehensive (${README_LINES} lines)" WARN "Below 500-line threshold for AGI-level context"
else
    check "README comprehensive (${README_LINES} lines)" FAIL "Too short — needs full AGI-level context"
fi

# ─── Q4: LICENSE exists? ────────────────────────────────────────────────
if [ -f "LICENSE" ]; then
    check "LICENSE present" PASS
else
    check "LICENSE present" FAIL "LICENSE file missing"
fi

# ─── Q5: No chaos terms (gospel, PHOENIX-73E, stale ports)? ─────────────
CHAOS_TERMS=""
if grep -rq "gospel\|Gospel\|GOSPEL" README.md FEDERATION_CONTRACT.md AGENTS.md 2>/dev/null; then
    CHAOS_TERMS="$CHAOS_TERMS gospel"
fi
if grep -rq "PHOENIX-73E" README.md TOOL_SURFACE.md CHANGELOG.md 2>/dev/null; then
    CHAOS_TERMS="$CHAOS_TERMS PHOENIX-stale"
fi
REPO=$(basename "$(pwd)")
case "$REPO" in
    WEALTH)
        if grep -rqE '(^|[^0-9])8082([^0-9]|$)' README.md AGENTS.md CONTEXT.md RUNBOOK.md 2>/dev/null; then
            CHAOS_TERMS="$CHAOS_TERMS stale-port"
        fi
        ;;
    WELL)
        if grep -rqE '(^|[^0-9])8083([^0-9]|$)' README.md AGENTS.md CONTEXT.md RUNBOOK.md 2>/dev/null; then
            CHAOS_TERMS="$CHAOS_TERMS stale-port"
        fi
        ;;
esac
if [ -z "$CHAOS_TERMS" ]; then
    check "No chaos terms" PASS
else
    check "No chaos terms" WARN "Found:$CHAOS_TERMS"
fi

# ─── Q6: No hardcoded secrets? ──────────────────────────────────────────
SECRET_PATTERNS='sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|bot[0-9]+:[A-Za-z0-9_-]{20,}'
if git rev-parse --git-dir >/dev/null 2>&1; then
    SECRET_HITS="$(
        git ls-files -z --cached --others --exclude-standard \
        | python3 -c 'import os, sys; data=sys.stdin.buffer.read().split(b"\0"); skip=(b"docs/", b"wiki/", b"memory/", b"reports/", b"benchmarks/", b"artifacts/"); out=[p for p in data if p and not p.startswith(skip)]; sys.stdout.buffer.write(b"\0".join(out))' \
        | xargs -0 -r grep -nE "$SECRET_PATTERNS" 2>/dev/null \
        | head -n 5 || true
    )"
else
    SECRET_HITS="$(
        grep -rInE "$SECRET_PATTERNS" . \
            --exclude-dir=.git \
            --exclude-dir=node_modules \
            --exclude-dir=.venv \
            --exclude-dir=tests \
            --exclude-dir=test \
            --exclude='*.baseline' 2>/dev/null \
        | head -n 5 || true
    )"
fi
if [ -n "$SECRET_HITS" ]; then
    check "No hardcoded secrets" FAIL "Secret-like pattern detected in git-visible files"
    printf '%s\n' "$SECRET_HITS" | sed 's/^/       /'
else
    check "No hardcoded secrets" PASS
fi

# ─── Q7: Port consistency ───────────────────────────────────────────────
case "$REPO" in
    arifOS)   EXPECTED_PORT=8088 ;;
    geox)     EXPECTED_PORT=8081 ;;
    WEALTH)   EXPECTED_PORT=18082 ;;
    WELL)     EXPECTED_PORT=18083 ;;
    A-FORGE)  EXPECTED_PORT=7071 ;;
    AAA)      EXPECTED_PORT=3001 ;;
    *)        EXPECTED_PORT="" ;;
esac
if [ -n "$EXPECTED_PORT" ]; then
    PORT_MENTIONS=$(grep -c ":$EXPECTED_PORT\|port.*$EXPECTED_PORT\|Port.*$EXPECTED_PORT" README.md 2>/dev/null || echo 0)
    if [ "$PORT_MENTIONS" -ge 1 ]; then
        check "Port $EXPECTED_PORT referenced in README" PASS
    else
        check "Port $EXPECTED_PORT referenced in README" WARN "Port not mentioned in README"
    fi
fi

# ─── Q8: CONTEXT.md and RUNBOOK.md exist? ────────────────────────────────
for f in CONTEXT.md RUNBOOK.md; do
    if [ -f "$f" ]; then
        check "$f present" PASS
    else
        check "$f present" WARN "$f missing — agent onboarding gap"
    fi
done

# ─── SUMMARY ────────────────────────────────────────────────────────────
echo ""
echo "──────────────────────────────────────────────────"
echo -e "  PASS: $PASS  |  WARN: $WARN  |  FAIL: $FAIL"
echo "──────────────────────────────────────────────────"

if [ "$FAIL" -gt 0 ]; then
    echo -e "  ${RED}VERDICT: BLOCK — $FAIL failure(s) must be fixed${NC}"
    exit 1
elif [ "$STRICT" = true ] && [ "$WARN" -gt 0 ]; then
    echo -e "  ${YELLOW}VERDICT: BLOCK (strict) — $WARN warning(s)${NC}"
    exit 1
elif [ "$WARN" -gt 0 ]; then
    echo -e "  ${YELLOW}VERDICT: PASS with $WARN warning(s) — non-blocking${NC}"
    echo "  Governance drift detected. Fix before next horizon."
    exit 0
else
    echo -e "  ${GREEN}VERDICT: GOVERNED — All checks pass. Push allowed.${NC}"
    exit 0
fi
