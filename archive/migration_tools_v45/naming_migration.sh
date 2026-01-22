#!/bin/bash
# naming_migration.sh - Automated Trinity naming migration (ARIF/ADAM → AGI/ASI)
#
# Part of Canonical Naming Convention v42.0 implementation
# See: NAMING_CONVENTION.md Section 2 (Trinity Nomenclature)
#
# BREAKING CHANGES:
# - Renames engine files: arif_engine.py → agi_engine.py, adam_engine.py → asi_engine.py
# - Updates class names: ARIFEngine → AGIEngine, ADAMEngine → ASIEngine
# - Updates packet classes: ARIFPacket → AGIPacket, ADAMPacket → ASIPacket
# - Updates all imports across codebase

set -e  # Exit on error

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== arifOS Trinity Naming Migration Script v42.0 ==="
echo "Migrating ARIF/ADAM → AGI/ASI (BREAKING CHANGES)"
echo ""
echo "⚠ WARNING: This script will modify Python files in place!"
echo "Recommended: Commit current changes before running this script."
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Migration aborted."
    exit 1
fi

echo ""
echo "[1/7] Renaming engine files..."

# Rename arif_engine.py → agi_engine.py
if [ -f "arifos_core/engines/arif_engine.py" ]; then
    git mv arifos_core/engines/arif_engine.py arifos_core/engines/agi_engine.py
    echo "✓ arif_engine.py → agi_engine.py"
else
    echo "⚠ arif_engine.py not found (already renamed?)"
fi

# Rename adam_engine.py → asi_engine.py
if [ -f "arifos_core/engines/adam_engine.py" ]; then
    git mv arifos_core/engines/adam_engine.py arifos_core/engines/asi_engine.py
    echo "✓ adam_engine.py → asi_engine.py"
else
    echo "⚠ adam_engine.py not found (already renamed?)"
fi

echo ""
echo "[2/7] Updating class names in engine files..."

# Update agi_engine.py (formerly arif_engine.py)
if [ -f "arifos_core/engines/agi_engine.py" ]; then
    # ARIFEngine → AGIEngine
    sed -i 's/class ARIFEngine/class AGIEngine/g' arifos_core/engines/agi_engine.py
    sed -i 's/ARIFEngine/AGIEngine/g' arifos_core/engines/agi_engine.py
    
    # ARIFPacket → AGIPacket
    sed -i 's/class ARIFPacket/class AGIPacket/g' arifos_core/engines/agi_engine.py
    sed -i 's/ARIFPacket/AGIPacket/g' arifos_core/engines/agi_engine.py
    
    # Update module docstring
    sed -i 's/arif_engine\.py/agi_engine.py/g' arifos_core/engines/agi_engine.py
    sed -i 's/ARIF AGI/AGI (Architect)/g' arifos_core/engines/agi_engine.py
    sed -i 's/AAA Trinity/AGI·ASI·APEX Trinity/g' arifos_core/engines/agi_engine.py
    
    echo "✓ Updated agi_engine.py"
else
    echo "⚠ agi_engine.py not found"
fi

# Update asi_engine.py (formerly adam_engine.py)
if [ -f "arifos_core/engines/asi_engine.py" ]; then
    # ADAMEngine → ASIEngine
    sed -i 's/class ADAMEngine/class ASIEngine/g' arifos_core/engines/asi_engine.py
    sed -i 's/ADAMEngine/ASIEngine/g' arifos_core/engines/asi_engine.py
    
    # ADAMPacket → ASIPacket
    sed -i 's/class ADAMPacket/class ASIPacket/g' arifos_core/engines/asi_engine.py
    sed -i 's/ADAMPacket/ASIPacket/g' arifos_core/engines/asi_engine.py
    
    # Update imports from arif_engine → agi_engine
    sed -i 's/from \.arif_engine import ARIFPacket/from .agi_engine import AGIPacket/g' arifos_core/engines/asi_engine.py
    
    # Update module docstring
    sed -i 's/adam_engine\.py/asi_engine.py/g' arifos_core/engines/asi_engine.py
    sed -i 's/ADAM ASI/ASI (Auditor)/g' arifos_core/engines/asi_engine.py
    sed -i 's/AAA Trinity/AGI·ASI·APEX Trinity/g' arifos_core/engines/asi_engine.py
    
    echo "✓ Updated asi_engine.py"
else
    echo "⚠ asi_engine.py not found"
fi

echo ""
echo "[3/7] Updating engines/__init__.py..."

if [ -f "arifos_core/engines/__init__.py" ]; then
    # Update imports
    sed -i 's/from \.arif_engine import ARIFEngine/from .agi_engine import AGIEngine/g' arifos_core/engines/__init__.py
    sed -i 's/from \.adam_engine import ADAMEngine/from .asi_engine import ASIEngine/g' arifos_core/engines/__init__.py
    
    # Update __all__
    sed -i 's/"ARIFEngine"/"AGIEngine"/g' arifos_core/engines/__init__.py
    sed -i 's/"ADAMEngine"/"ASIEngine"/g' arifos_core/engines/__init__.py
    
    # Update docstring
    sed -i 's/AAA Engines/AGI·ASI·APEX Engines/g' arifos_core/engines/__init__.py
    sed -i 's/AAA Trinity/AGI·ASI·APEX Trinity/g' arifos_core/engines/__init__.py
    sed -i 's/ARIFEngine (Delta)/AGIEngine (Delta)/g' arifos_core/engines/__init__.py
    sed -i 's/ADAMEngine (Omega)/ASIEngine (Omega)/g' arifos_core/engines/__init__.py
    
    echo "✓ Updated engines/__init__.py"
else
    echo "⚠ engines/__init__.py not found"
fi

echo ""
echo "[4/7] Updating apex_engine.py..."

if [ -f "arifos_core/engines/apex_engine.py" ]; then
    # Update imports
    sed -i 's/from \.arif_engine import ARIFPacket/from .agi_engine import AGIPacket/g' arifos_core/engines/apex_engine.py
    sed -i 's/from \.adam_engine import ADAMPacket/from .asi_engine import ASIPacket/g' arifos_core/engines/apex_engine.py
    
    # Update references in code
    sed -i 's/ARIFPacket/AGIPacket/g' arifos_core/engines/apex_engine.py
    sed -i 's/ADAMPacket/ASIPacket/g' arifos_core/engines/apex_engine.py
    
    echo "✓ Updated apex_engine.py"
else
    echo "⚠ apex_engine.py not found"
fi

echo ""
echo "[5/7] Updating pipeline.py..."

if [ -f "arifos_core/pipeline.py" ]; then
    # Update imports
    sed -i 's/from \.engines\.arif_engine import ARIFPacket/from .engines.agi_engine import AGIPacket/g' arifos_core/pipeline.py
    sed -i 's/from \.engines\.adam_engine import ADAMPacket/from .engines.asi_engine import ASIPacket/g' arifos_core/pipeline.py
    
    # Update references
    sed -i 's/ARIFPacket/AGIPacket/g' arifos_core/pipeline.py
    sed -i 's/ADAMPacket/ASIPacket/g' arifos_core/pipeline.py
    
    echo "✓ Updated pipeline.py"
else
    echo "⚠ pipeline.py not found"
fi

echo ""
echo "[6/7] Updating test files..."

# Update test_engines_arif_adam.py
if [ -f "tests/test_engines_arif_adam.py" ]; then
    # Update imports
    sed -i 's/from arifos_core\.engines import ARIFEngine, ADAMEngine/from arifos_core.engines import AGIEngine, ASIEngine/g' tests/test_engines_arif_adam.py
    sed -i 's/from arifos_core\.engines\.arif_engine import ARIFPacket/from arifos_core.engines.agi_engine import AGIPacket/g' tests/test_engines_arif_adam.py
    sed -i 's/from arifos_core\.engines\.adam_engine import ADAMPacket/from arifos_core.engines.asi_engine import ASIPacket/g' tests/test_engines_arif_adam.py
    
    # Update class names
    sed -i 's/ARIFEngine/AGIEngine/g' tests/test_engines_arif_adam.py
    sed -i 's/ADAMEngine/ASIEngine/g' tests/test_engines_arif_adam.py
    sed -i 's/ARIFPacket/AGIPacket/g' tests/test_engines_arif_adam.py
    sed -i 's/ADAMPacket/ASIPacket/g' tests/test_engines_arif_adam.py
    
    # Update test class names
    sed -i 's/class TestARIFEngine/class TestAGIEngine/g' tests/test_engines_arif_adam.py
    sed -i 's/class TestADAMEngine/class TestASIEngine/g' tests/test_engines_arif_adam.py
    
    # Update test method names
    sed -i 's/test_import_arif_engine/test_import_agi_engine/g' tests/test_engines_arif_adam.py
    sed -i 's/test_import_adam_engine/test_import_asi_engine/g' tests/test_engines_arif_adam.py
    
    echo "✓ Updated test_engines_arif_adam.py"
else
    echo "⚠ test_engines_arif_adam.py not found"
fi

# Update test_runtime_manifest.py
if [ -f "tests/test_runtime_manifest.py" ]; then
    sed -i 's/ARIFEngine/AGIEngine/g' tests/test_runtime_manifest.py
    sed -i 's/ADAMEngine/ASIEngine/g' tests/test_runtime_manifest.py
    sed -i 's/"arif"/"agi"/g' tests/test_runtime_manifest.py
    sed -i 's/"adam"/"asi"/g' tests/test_runtime_manifest.py
    
    echo "✓ Updated test_runtime_manifest.py"
else
    echo "⚠ test_runtime_manifest.py not found"
fi

echo ""
echo "[7/7] Searching for remaining references..."

# Search for any remaining ARIF/ADAM references in Python files (excluding archive)
remaining_py=$(grep -r "ARIFEngine\|ADAMEngine\|ARIFPacket\|ADAMPacket" \
    --include="*.py" \
    --exclude-dir=archive \
    --exclude-dir=.git \
    . 2>/dev/null | wc -l)

if [ "$remaining_py" -gt 0 ]; then
    echo "⚠ Found $remaining_py remaining references in Python files:"
    grep -r "ARIFEngine\|ADAMEngine\|ARIFPacket\|ADAMPacket" \
        --include="*.py" \
        --exclude-dir=archive \
        --exclude-dir=.git \
        . 2>/dev/null | head -10
    echo ""
    echo "⚠ Manual review needed for these files"
else
    echo "✓ No remaining ARIF/ADAM class references found in Python files"
fi

echo ""
echo "=== Migration Complete ==="
echo ""
echo "Summary:"
echo "  - Renamed: arif_engine.py → agi_engine.py"
echo "  - Renamed: adam_engine.py → asi_engine.py"
echo "  - Updated: ARIFEngine → AGIEngine"
echo "  - Updated: ADAMEngine → ASIEngine"
echo "  - Updated: ARIFPacket → AGIPacket"
echo "  - Updated: ADAMPacket → ASIPacket"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Test imports: python -c 'from arifos_core.engines import AGIEngine, ASIEngine; print(\"OK\")'"
echo "  3. Run test suite: pytest -v tests/"
echo "  4. Update documentation (see Phase 4 in NAMING_CONVENTION.md)"
echo "  5. Commit: git commit -m 'feat: Rename ARIF/ADAM engines to AGI/ASI (BREAKING CHANGE)'"
echo ""
echo "See: NAMING_CONVENTION.md Section 2 (Trinity Nomenclature)"
