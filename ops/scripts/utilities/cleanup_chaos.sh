#!/bin/bash
# arifOS Chaos Cleanup Script
# Run this to archive old files and keep only live code

echo "🧹 Starting chaos cleanup..."

# Create archive structure
mkdir -p _ARCHIVE/{scripts,root_files,old_tests,old_docs}

# Move old root files
echo "📁 Archiving old root files..."
mv arifos_router.py _ARCHIVE/root_files/ 2>/dev/null || true
mv test_*.py _ARCHIVE/old_tests/ 2>/dev/null || true
mv verify_*.py _ARCHIVE/old_tests/ 2>/dev/null || true
mv verify_output.txt _ARCHIVE/old_tests/ 2>/dev/null || true

# Move old docs
echo "📄 Archiving old docs..."
mv CLAUDE.md _ARCHIVE/old_docs/ 2>/dev/null || true
mv GEMINI.md _ARCHIVE/old_docs/ 2>/dev/null || true
mv INSIGHTS.md _ARCHIVE/old_docs/ 2>/dev/null || true

# Archive most scripts (keep only essential)
echo "🔧 Archiving scripts (keeping only 5 essential)..."
mkdir -p _ARCHIVE/scripts/essential
for script in scripts/deploy_production.py scripts/generate_llms_docs.py scripts/housekeeping.py scripts/truth_logger.py scripts/diagnose_tools.py; do
    if [ -f "$script" ]; then
        mv "$script" _ARCHIVE/scripts/essential/ 2>/dev/null || true
    fi
done

# Move remaining scripts to archive
mv scripts/* _ARCHIVE/scripts/ 2>/dev/null || true

# Restore essential scripts
mkdir -p scripts
mv _ARCHIVE/scripts/essential/* scripts/ 2>/dev/null || true
rmdir _ARCHIVE/scripts/essential 2>/dev/null || true

echo "✅ Cleanup complete!"
echo ""
echo "📊 Summary:"
echo "  Live code: arifosmcp.transport/, railway.toml, Dockerfile"
echo "  Archived: _ARCHIVE/"
echo ""
echo "To finalize: git add -A && git commit -m 'chore: Archive old chaos'"
