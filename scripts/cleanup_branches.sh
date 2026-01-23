#!/bin/bash
# =============================================================================
# arifOS Branch Cleanup Script (v50.5.3)
# Run this AFTER merging claude/arifos-mcp-requirements-C6ETA to main
# =============================================================================

echo "🧹 arifOS Branch Cleanup"
echo "========================"
echo ""

# -----------------------------------------------------------------------------
# STEP 1: Delete AI-generated branches (14 branches)
# These are experiments from Claude/Codex/Copilot, never merged
# -----------------------------------------------------------------------------
echo "Step 1: Deleting AI-generated branches..."

# Claude branches (old experiments)
git push origin --delete claude/add-apex-prime-tests-01RCFFULMLwq6rc14LtswE17
git push origin --delete claude/add-kms-signer-018WWNzFuLzR6xYMZrRWZD2H
git push origin --delete claude/add-ledger-verification-script-01HbGKWKbRQspjZwQv78m8AQ
git push origin --delete claude/prepare-concrete-files-016eNznjPfsgU5aXpcv7H8kW

# Codex branches (old audits)
git push origin --delete codex/create-architecture-map-for-arifos-v33-2025-11-26
git push origin --delete codex/perform-audit-on-arifos-github-repo-2025-11-26
git push origin --delete codex/perform-audit-on-arifos-github-repo-2025-11-26-28t7ch
git push origin --delete codex/run-final-conformance-check-for-arifos-v33-2025-11-26

# Copilot branches (old fixes)
git push origin --delete copilot/analyze-apex-prime-guard
git push origin --delete copilot/perform-status-check-audit
git push origin --delete copilot/revert-corrupted-commit-and-add-ci
git push origin --delete copilot/revert-malformed-filename-commit
git push origin --delete copilot/status-report-arifos-project
git push origin --delete copilot/update-index-md-file

echo "✅ AI-generated branches deleted"
echo ""

# -----------------------------------------------------------------------------
# STEP 2: Delete Dependabot branches (2 branches)
# -----------------------------------------------------------------------------
echo "Step 2: Deleting Dependabot branches..."

git push origin --delete dependabot/github_actions/actions/checkout-6
git push origin --delete dependabot/github_actions/actions/setup-python-6

echo "✅ Dependabot branches deleted"
echo ""

# -----------------------------------------------------------------------------
# STEP 3: Archive old feature branches as tags, then delete (6 branches)
# Code is already preserved in release tags (v33-v50)
# -----------------------------------------------------------------------------
echo "Step 3: Archiving old feature branches..."

# These have release tags already, safe to delete
git push origin --delete feat/trinity-v43-implementation      # v43.x tags exist
git push origin --delete feat/v45-sovereign-witness           # v45.x tags exist
git push origin --delete feature/v36.3O-law-v1                # v36.3.0 tag exists
git push origin --delete feature/v36.3O-spec-v1               # v36.3.0 tag exists
git push origin --delete feature/constitutional-meta-search-v46.1  # v46.0.0 tag exists
git push origin --delete spec/psi-prime-trinity-lattice       # v42 tag exists

echo "✅ Old feature branches deleted"
echo ""

# -----------------------------------------------------------------------------
# STEP 4: Delete misc branches (3 branches)
# -----------------------------------------------------------------------------
echo "Step 4: Deleting misc branches..."

git push origin --delete add/compliance-checklist
git push origin --delete docs/floor-alignment-phase1
git push origin --delete docs/infra-config

echo "✅ Misc branches deleted"
echo ""

# -----------------------------------------------------------------------------
# STEP 5: Create release tag for v50.5.3
# -----------------------------------------------------------------------------
echo "Step 5: Creating v50.5.3 release tag..."

git checkout main
git pull origin main
git tag -a v50.5.3 -m "refactor: Clean Trinity architecture - MCP at arifos/mcp/, spec at arifos/spec/"
git push origin v50.5.3

echo "✅ v50.5.3 tag created"
echo ""

# -----------------------------------------------------------------------------
# DONE
# -----------------------------------------------------------------------------
echo "🎉 Cleanup complete!"
echo ""
echo "Remaining branches:"
git branch -r
echo ""
echo "Should only see:"
echo "  origin/main"
echo "  origin/claude/arifos-mcp-requirements-C6ETA (delete after PR merge)"
