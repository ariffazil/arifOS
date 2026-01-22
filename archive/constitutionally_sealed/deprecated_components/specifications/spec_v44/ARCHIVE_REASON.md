# Archive Reason: spec/v44/ → v45 Migration

**Date**: 2025-12-29
**Authority**: Phoenix-72 Constitutional Amendment (v45 Consolidation)
**Amendment ID**: spec_v44_to_v45_migration

---

## Overview

This archive contains the complete spec/v44/ directory, preserved during the v44→v45 migration as part of the broader arifOS v45 consolidation effort.

**Reason for Archive**: Version upgrade (v44.0 → v45.0) to align with L1_THEORY/canon/ v45 migration.

**Zero Information Loss**: All v44 specification content preserved here with SHA-256 verification.

---

## Constitutional Compliance

### F1 Amanah (Integrity/Reversibility)
- ✅ **Reversible**: Complete archive with SHA-256 manifest allows full restoration
- ✅ **Git stash**: `Pre-Spec-v45-Migration: 29 Dec, 2025 10:06:58 AM`
- ✅ **Mandated scope**: Spec consolidation approved via v45 canon alignment

### F2 Truth (Factual Accuracy)
- ✅ **SHA-256 verified**: All 12 files (8 specs + 4 schemas) have cryptographic hashes
- ✅ **Exact copies**: `cp -r spec/v44/* archive/spec_v44/` preserves all content
- ✅ **No deletions**: Archive created BEFORE any removal from active spec/

### F4 ΔS (Clarity Gain)
- ✅ **Version consistency**: Migration eliminates v44/v45 fragmentation
- ✅ **Single source of truth**: spec/v45/ becomes sole active Track B authority
- ✅ **Reduced entropy**: 1 active version (v45) instead of 2 (v44 + v45)

**Verdict**: SEAL

---

## Archived Files (12 total)

### Core Specification Files (8)
1. `constitutional_floors.json` - F1-F9 floor thresholds
2. `genius_law.json` - GENIUS (G) and C_dark metrics
3. `session_physics.json` - TEARFRAME session physics
4. `red_patterns.json` - Prohibited content patterns
5. `cooling_ledger_phoenix.json` - Phoenix-72 amendment protocol
6. `policy_text.json` - Policy explanations
7. `waw_prompt_floors.json` - W@W Federation prompt governance
8. `UNIFIED_ARIFOS_v44_FULL_SPEC.json` - Complete unified spec

### JSON Schema Files (4)
1. `schema/constitutional_floors.schema.json`
2. `schema/genius_law.schema.json`
3. `schema/session_physics.schema.json`
4. `schema/red_patterns.schema.json`

### Documentation Files (3)
1. `README.md` - Track B v44 documentation
2. `SEAL_CHECKLIST.md` - SHA-256 integrity verification procedures
3. `MANIFEST.sha256.json` - Cryptographic manifest

---

## SHA-256 Manifest

**Location**: `archive/spec_v44/MANIFEST.sha256.json`

**Verification**:
```bash
cd archive/spec_v44
python ../../scripts/verify_archive_integrity.py
```

**Expected output**: All 8 files PASS

---

## Key Differences: v44 → v45

| Aspect | v44 | v45 |
|--------|-----|-----|
| **Version** | v44.0 | v45.0 |
| **Canon Refs** | `_v42.md` | `_v45.md` |
| **Authority** | Track B v44 | Track B v45 (Phoenix-72 consolidation) |
| **Source Evolution** | v42.1 → v44.0 | v44.0 → v45.0 (Phoenix-72) |

**Content Changes**: Metadata only (version numbers, canon references). No threshold or structural changes.

---

## Restoration Procedure

**If v45 migration needs rollback:**

```bash
# Option 1: Restore v44 from archive
cp -r archive/spec_v44/* spec/v44/

# Option 2: Git stash (full rollback)
git stash list  # Find: Pre-Spec-v45-Migration
git stash pop

# Option 3: Selective file restoration
cp archive/spec_v44/constitutional_floors.json spec/v44/
```

**Verify restoration**:
```bash
cd spec/v44
python ../../scripts/regenerate_manifest_v45.py --check
```

---

## Related Archives

- `archive/v42_detail/` - Canon v42 files (L1_THEORY/canon/ migration)
- `archive/spec_v44/` - This archive (spec/v44/ migration)

---

## Phoenix-72 Amendment Link

**Parent Amendment**: v45_canon_consolidation
**Cooling Ledger Entry**: `cooling_ledger/L1_cooling_ledger.jsonl`
**Amendment Type**: Version upgrade (Track B alignment with Track A)

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.

**Archive Sealed**: 2025-12-29
**Authority**: Phoenix-72 Constitutional Amendment
