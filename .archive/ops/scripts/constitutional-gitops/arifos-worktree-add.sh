#!/usr/bin/env bash
# arifos-worktree-add.sh
# CLAIM: F1-compliant agent sandbox creator.
# Usage: ./arifos-worktree-add.sh <agent-name> <feature-slug>

set -euo pipefail

# F12: Injection defense — sanitize inputs
sanitize() {
    echo "$1" | tr -cd '[:alnum:]-_' | cut -c1-32
}

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
    echo "❌ F12: Not inside a git repo."
    exit 1
fi

AGENT_NAME="${1:-}"
FEATURE="${2:-}"

if [[ -z "$AGENT_NAME" || -z "$FEATURE" ]]; then
    echo "Usage: $0 <agent-name> <feature-slug>"
    echo "Example: $0 claude mcp-hardening"
    exit 1
fi

# Sanitize inputs (F12)
AGENT_NAME=$(sanitize "$AGENT_NAME")
FEATURE=$(sanitize "$FEATURE")

ROOT="$(git rev-parse --show-toplevel)"
REPO_NAME=$(basename "$ROOT")
WORKTREES_ROOT="${WORKTREES_ROOT:-${ROOT}-worktrees}"

# F4: Clarity — ensure clean naming
mkdir -p "$WORKTREES_ROOT"

BRANCH="feature/${AGENT_NAME}-${FEATURE}"
WORKTREE_NAME="${REPO_NAME}-${AGENT_NAME}-${FEATURE}"
WORKTREE_PATH="${WORKTREES_ROOT}/${WORKTREE_NAME}"

# F1: Check if already exists
if [[ -d "$WORKTREE_PATH" ]]; then
    echo "❌ F1: Worktree already exists at $WORKTREE_PATH"
    echo "   Run: ./arifos-worktree-remove.sh $BRANCH"
    exit 1
fi

# F2: Ensure main is clean
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  F2: Main worktree has uncommitted changes."
    echo "   Commit or stash before creating agent sandbox."
    exit 1
fi

# Create constitutional sandbox
echo "🔥 Creating F1-compliant sandbox..."
git worktree add "$WORKTREE_PATH" -b "$BRANCH" origin/main 2>/dev/null || \
    git worktree add "$WORKTREE_PATH" -b "$BRANCH"

# Generate arifos.yml manifest
cat > "$WORKTREE_PATH/arifos.yml" << EOF
# arifos.yml — Constitutional Worktree Manifest
# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
# F3: Tri-Witness discovery schema

arifos_version: "2026.03.24"
worktree:
  id: "${WORKTREE_NAME}"
  branch: "${BRANCH}"
  parent: "main"
  created_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  path: "${WORKTREE_PATH}"
  
agent:
  name: "${AGENT_NAME}"
  type: "coding"
  runtime: "acp"
  model: "${AGENT_MODEL:-unknown}"
  
constitutional:
  floors:
    - F1   # Reversibility: worktree can be rm -rf'd
    - F2   # Truth: dry_run mode enforced
    - F4   # Clarity: naming convention checked
    - F11  # Command auth: no push to main
  veto_holder: "arif"
  max_risk_tier: "medium"
  dry_run: true
  
governance:
  tri_witness:
    human: "pending"
    ai: "pending"
    earth: "pending"
  verdict: "SABAR"
  
vault:
  lineage: true
  ttl_days: 30
  sealed: false
EOF

# Create .gitignore if not exists
if [[ ! -f "$WORKTREE_PATH/.gitignore" ]]; then
    cat > "$WORKTREE_PATH/.gitignore" << 'EOF'
# F12: Injection defense — no secrets
*.key
*.pem
*.env
.env.local
.env.*.local
secrets/
.gitleaks.toml
EOF
fi

echo ""
echo "✅ F1 SANDBOX CREATED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 Path:    $WORKTREE_PATH"
echo "🔒 Branch:  $BRANCH"
echo "🤖 Agent:   $AGENT_NAME"
echo "⚖️  Veto:    Arif (F13)"
echo ""
echo "🚀 Next steps:"
echo "   cd $WORKTREE_PATH"
echo "   ./arifos-agent-run.sh"
echo ""
echo "🗑️  F1 Reversibility:"
echo "   ./arifos-worktree-remove.sh $BRANCH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
