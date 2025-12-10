#!/bin/bash

# arifOS v36.1Omega Tiered Governance Deployment Script
# Epoch: 36Omega - Industry-Aligned Architecture
# Status: PRODUCTION-READY

set -e

echo "arifOS v36.1Omega Tiered Governance Deployment"
echo "=============================================="
echo ""

# Step 1: Backup existing files
echo "Step 1: Backing up existing files..."
[ -f AGENTS.md ] && cp AGENTS.md AGENTS_v36_backup_$(date +%s).md && echo "  AGENTS.md backed up"
[ -f CLAUDE.md ] && cp CLAUDE.md CLAUDE_v36_backup_$(date +%s).md && echo "  CLAUDE.md backed up"
echo ""

# Step 2: Create directories
echo "Step 2: Creating .claude/ directory..."
mkdir -p .claude
echo "  .claude/ ready"
echo ""

# Step 3: Verify files exist
echo "Step 3: Verifying configuration files..."
[ -f AGENTS.md ] && echo "  AGENTS.md present" || echo "  WARNING: AGENTS.md not found"
[ -f CLAUDE.md ] && echo "  CLAUDE.md present" || echo "  WARNING: CLAUDE.md not found"
[ -f .claude/TEARFRAME.md ] && echo "  TEARFRAME.md present" || echo "  WARNING: TEARFRAME.md not found"
[ -f .claude/SECURITY.md ] && echo "  SECURITY.md present" || echo "  WARNING: SECURITY.md not found"
[ -f .claude/CONSTITUTION.md ] && echo "  CONSTITUTION.md present" || echo "  WARNING: CONSTITUTION.md not found"
echo ""

# Step 4: Create symlinks (optional - for other platforms)
echo "Step 4: Creating platform symlinks..."
[ ! -L GEMINI.md ] && ln -sf AGENTS.md GEMINI.md 2>/dev/null && echo "  GEMINI.md -> AGENTS.md"
[ ! -L COPILOT.md ] && ln -sf AGENTS.md COPILOT.md 2>/dev/null && echo "  COPILOT.md -> AGENTS.md"
echo ""

# Step 5: Verify
echo "Step 5: Verifying deployment..."
echo ""
echo "Root-level files:"
ls -lh AGENTS.md CLAUDE.md 2>/dev/null | head -2
echo ""
echo ".claude/ directory:"
ls -lh .claude/*.md 2>/dev/null | head -3
echo ""

# Step 6: Line count validation
echo "Step 6: Line count validation..."
AGENTS_LINES=$(wc -l < AGENTS.md 2>/dev/null || echo "0")
CLAUDE_LINES=$(wc -l < CLAUDE.md 2>/dev/null || echo "0")
echo "  AGENTS.md: $AGENTS_LINES lines"
echo "  CLAUDE.md: $CLAUDE_LINES lines"
echo ""

echo "DEPLOYMENT COMPLETE"
echo "==================="
echo ""
echo "arifOS v36.1Omega is ready for use."
echo "DITEMPA BUKAN DIBERI"
