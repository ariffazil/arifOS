#!/bin/bash
# archive_migration.sh - Consolidate historical artifacts into archive/
#
# Part of Canonical Naming Convention v42.0 implementation
# See: NAMING_CONVENTION.md Section 5 (Archive Policy)

set -e  # Exit on error

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== arifOS Archive Migration Script v42.0 ==="
echo "Consolidating historical artifacts into archive/"
echo ""

# Create archive structure
echo "[1/5] Creating archive directory structure..."
mkdir -p archive/spec
mkdir -p archive/versions
mkdir -p archive/arifos_clip
echo "✓ Created: archive/{spec,versions,arifos_clip}"

# Migrate spec_archive to archive/spec
if [ -d "spec_archive" ]; then
    echo ""
    echo "[2/5] Migrating spec_archive/ → archive/spec/"
    if [ "$(ls -A spec_archive)" ]; then
        cp -r spec_archive/* archive/spec/
        echo "✓ Copied $(ls spec_archive | wc -l) files to archive/spec/"
        # Keep original for safety, will be removed manually after verification
        echo "⚠ Original spec_archive/ kept for safety (remove after verification)"
    else
        echo "⚠ spec_archive/ is empty, skipping"
    fi
else
    echo ""
    echo "[2/5] spec_archive/ not found, skipping"
fi

# Migrate v36.3O to archive/versions/v36_3_omega
if [ -d "v36.3O" ]; then
    echo ""
    echo "[3/5] Migrating v36.3O/ → archive/versions/v36_3_omega/"
    cp -r v36.3O archive/versions/v36_3_omega
    echo "✓ Copied v36.3O/ to archive/versions/v36_3_omega/"
    echo "⚠ Original v36.3O/ kept for safety (remove after verification)"
else
    echo ""
    echo "[3/5] v36.3O/ not found, skipping"
fi

# Migrate .arifos_clip_archive_* to archive/arifos_clip_YYYYMMDD
echo ""
echo "[4/5] Migrating .arifos_clip_archive_* → archive/arifos_clip_*/"
aclip_count=0
for dir in .arifos_clip_archive_*; do
    if [ -d "$dir" ]; then
        # Extract date from directory name (format: .arifos_clip_archive_YYYYMMDD_HHMMSS)
        basename=$(basename "$dir")
        # Extract YYYYMMDD portion
        date_part=$(echo "$basename" | grep -oE '[0-9]{8}' | head -1)
        if [ -n "$date_part" ]; then
            new_name="archive/arifos_clip_${date_part}"
            cp -r "$dir" "$new_name"
            echo "✓ $dir → $new_name"
            aclip_count=$((aclip_count + 1))
        else
            echo "⚠ Could not extract date from $dir, skipping"
        fi
    fi
done

if [ $aclip_count -eq 0 ]; then
    echo "⚠ No .arifos_clip_archive_* directories found"
else
    echo "✓ Migrated $aclip_count ACLIP archive(s)"
    echo "⚠ Original .arifos_clip_archive_* kept for safety (remove after verification)"
fi

# Create archive README
echo ""
echo "[5/5] Creating archive/README.md index..."
cat > archive/README.md << 'EOF'
# arifOS Archive

This directory contains historical artifacts that are no longer actively maintained but preserved for reference.

## Structure

### `spec/` (from `spec_archive/`)
Historical specification files from earlier versions:
- Constitutional floors (pre-v38)
- GENIUS LAW extracts
- Anti-Hantu defense specs
- Memory band policies
- Phase integration docs

### `versions/` 
Snapshots of specific version releases:
- `v36_3_omega/` - Version 36.3 Omega release (from `v36.3O/`)

### `arifos_clip_YYYYMMDD/`
Archived ACLIP (arifOS CLI Pipeline) state snapshots from automated backups.

## Archive Policy

See [NAMING_CONVENTION.md](../NAMING_CONVENTION.md) Section 5 for archive policy.

**Key principles:**
1. Archives are **read-only** - never modify archived content
2. Archives are **indexed** - this README provides overview
3. Archives are **dated** - use YYYYMMDD format for time-based artifacts
4. Archives are **safe** - old naming conventions (ARIF/ADAM/AAA) are preserved here

## Accessing Historical Content

To reference archived content in code or documentation:

```python
# Don't import from archive
# Instead, refer to it in comments or docstrings:
# "Historical reference: see archive/spec/arifOS-Constitution-9-Floors.md"
```

```markdown
For historical context, see [archived spec](archive/spec/arifOS-Constitution-9-Floors.md).
Note: Uses legacy naming (ARIF AGI → now AGI).
```

## Maintenance

- **When to archive:** Content superseded by newer versions, deprecated features
- **When NOT to archive:** Active code, current specs, test fixtures in use
- **Retention:** Archives preserved indefinitely unless explicitly removed via governance decision

---

**Last Updated:** 2025-12-14 (v42.0 Canonical Naming Convention)
EOF

echo "✓ Created archive/README.md"

echo ""
echo "=== Migration Complete ==="
echo ""
echo "Summary:"
echo "  - archive/spec/         $(ls archive/spec 2>/dev/null | wc -l) files"
echo "  - archive/versions/     $(ls archive/versions 2>/dev/null | wc -l) directories"
echo "  - archive/arifos_clip_* $aclip_count directories"
echo ""
echo "Next steps:"
echo "  1. Verify archive contents: ls -R archive/"
echo "  2. Run tests to ensure nothing broke: pytest -v"
echo "  3. If all good, manually remove old directories:"
echo "     rm -rf spec_archive v36.3O .arifos_clip_archive_*"
echo ""
echo "See: NAMING_CONVENTION.md Section 5 (Archive Policy)"
