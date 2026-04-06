#!/usr/bin/env bash
# arifos-worktree-remove.sh
# CLAIM: Cleanly collapse rejected universe → VOID.
# Usage: ./arifos-worktree-remove.sh <branch-name>

set -euo pipefail

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
    echo "❌ Not inside a git repo."
    exit 1
fi

BRANCH="${1:-}"
if [[ -z "$BRANCH" ]]; then
    echo "Usage: $0 <branch-name>"
    echo "Example: $0 feature/claude-mcp-hardening"
    exit 1
fi

# Strip refs/heads/ if present
BRANCH="${BRANCH#refs/heads/}"

ROOT="$(git rev-parse --show-toplevel)"
WORKTREE_PATH=$(git worktree list --porcelain 2>/dev/null | \
    awk -v b="refs/heads/${BRANCH}" '
        $1=="worktree" { path=$2 }
        $1=="branch" && $2==b { print path }
    ')

if [[ -z "${WORKTREE_PATH}" ]]; then
    echo "❌ No worktree found for branch: ${BRANCH}"
    echo "   Available worktrees:"
    git worktree list
    exit 1
fi

# F1: Confirm reversibility (unless --force)
if [[ "${1:-}" != "--force" && "${2:-}" != "--force" ]]; then
    echo "⚠️  F1 REVERSIBILITY CHECK"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🗑️  This will permanently delete:"
    echo "   $WORKTREE_PATH"
    echo ""
    echo "🔒 Branch: $BRANCH"
    echo ""
    read -p "Type 'VOID' to confirm deletion: " confirm
    if [[ "$confirm" != "VOID" ]]; then
        echo "❌ Aborted. Worktree preserved."
        exit 0
    fi
fi

echo "🔥 Collapsing universe → VOID..."

# F1: Remove worktree
git worktree remove "$WORKTREE_PATH" --force 2>/dev/null || \
    rm -rf "$WORKTREE_PATH"

# Clean up branch if it exists
if git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
    git branch -D "$BRANCH" 2>/dev/null || true
fi

# Remove from VAULT999 tracking (if exists)
VAULT_FILE="${ROOT}/VAULT999/worktrees.json"
if [[ -f "$VAULT_FILE" ]]; then
    jq --arg branch "$BRANCH" 'del(.worktrees[$branch])' "$VAULT_FILE" > "${VAULT_FILE}.tmp" && \
        mv "${VAULT_FILE}.tmp" "$VAULT_FILE" 2>/dev/null || true
fi

echo ""
echo "🗑️  UNIVERSE COLLAPSED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔥 Verdict: VOID"
echo "🔒 Branch:  $BRANCH (deleted)"
echo "📁 Path:    $WORKTREE_PATH (removed)"
echo ""
echo "✅ F1: Reversibility confirmed."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
