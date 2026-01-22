# L1_THEORY CANON REORGANIZATION PLAN

**Date:** 2026-01-12T14:13:00+08:00
**Analyst:** Δ (Antigravity - Architect)
**Status:** 🔴 CHAOS DETECTED → Proposing EQUILIBRIUM
**Target:** Clean v46 canon structure

---

## 🚨 CURRENT STATE: CHAOS ANALYSIS

### Problem Summary

**L1_THEORY directory is fragmented:**
- ✅ Good structure exists (00_foundation → 07_safety)
- ❌ Multiple master files at root
- ❌ Duplicate/overlapping content
- ❌ v45 files need v46 migration
- ❌ No clear "start here" entry point

---

## 📊 CURRENT STRUCTURE (As-Is)

```
L1_THEORY/
├── README.md                                    ← Root index (OK)
├── canon/
│   ├── 000_CONSTITUTIONAL_CORE_v45.md           ← ⚠️ DUPLICATE (70KB mega-file)
│   ├── CANON_COVERAGE_CHECKLIST_v45.md          ← ⚠️ META (should be in _INDEX)
│   ├── CANON_INTEGRATION_MAP_v45.md             ← ⚠️ META (should be in _INDEX)
│   ├── MISSING_FILE_HUNT_REPORT.md              ← ⚠️ TEMP (archive?)
│   ├── 00_foundation/                           ← ✅ GOOD
│   ├── 01_floors/
│   │   └── 010_CONSTITUTIONAL_FLOORS_F1F9_v45.md ← ⚠️ v45 (needs v46)
│   ├── 02_actors/                               ← ✅ GOOD
│   ├── 03_runtime/                              ← ✅ GOOD
│   ├── 04_measurement/                          ← ✅ GOOD
│   ├── 05_memory/                               ← ✅ GOOD
│   ├── 06_paradox/                              ← ✅ GOOD
│   ├── 07_safety/                               ← ✅ GOOD
│   └── _INDEX/
│       └── 00_MASTER_INDEX_v45.md               ← ✅ GOOD (primary index)
├── ledger/                                      ← ✅ GOOD (audit trail)
├── manifest/                                    ← ✅ GOOD (SHA-256 verification)
└── phoenix_72/                                  ← ✅ NEW (F10-F12 proposal)
    ├── README.md
    └── AMENDMENT_F10F12_PROPOSAL_v46.md
```

---

## 🎯 PROBLEMS IDENTIFIED

### Problem 1: Master File Duplication

**Issue:** Three "master" documents at different levels:

| File | Location | Size | Status |
|------|----------|------|--------|
| `000_CONSTITUTIONAL_CORE_v45.md` | `canon/` | 70KB | ⚠️ Mega-file (everything) |
| `00_MASTER_INDEX_v45.md` | `canon/_INDEX/` | ~10KB | ✅ Index (links to sections) |
| `README.md` | `L1_THEORY/` | ~3KB | ✅ Entry point |

**Confusion:** Which file is truth?

**Decision needed:**
- Keep ONE master document OR
- Clarify roles (index vs content)

---

### Problem 2: v45 Files Need v46 Migration

**Files stuck on v45:**
- `canon/000_CONSTITUTIONAL_CORE_v45.md`
- `canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md`
- `canon/_INDEX/00_MASTER_INDEX_v45.md`
- `canon/CANON_COVERAGE_CHECKLIST_v45.md`
- `canon/CANON_INTEGRATION_MAP_v45.md`

**After Phoenix-72 (Day 3):**
- Must rename v45 → v46
- Must add F10-F12 content
- Must update cross-references

---

### Problem 3: Meta Files in Wrong Location

**Files that are "about canon" (not canon itself):**

| File | Current Location | Should Be |
|------|------------------|-----------|
| `CANON_COVERAGE_CHECKLIST_v45.md` | `canon/` | `canon/_INDEX/` or `meta/` |
| `CANON_INTEGRATION_MAP_v45.md` | `canon/` | `canon/_INDEX/` or `meta/` |
| `MISSING_FILE_HUNT_REPORT.md` | `canon/` | `archive/` or delete |

---

### Problem 4: No Clear Entry Point

**User landing on L1_THEORY/ doesn't know:**
- Where to start reading?
- What's the canonical truth?
- What's v45 vs v46?
- How to navigate 70+ files?

---

## ✅ PROPOSED STRUCTURE (To-Be)

### Option A: Single Master Document (RECOMMENDED)

```
L1_THEORY/
├── README.md                                     ← ENTRY POINT (start here)
├── CONSTITUTIONAL_CORE_v46.md                    ← 🔥 PRIMARY CANON (moved from canon/)
├── canon/                                        ← IMPLEMENTATION DETAILS
│   ├── 01_floors/
│   │   ├── 010_CONSTITUTIONAL_FLOORS_F1F12_v46.md ← v46 (12 floors)
│   │   └── archive/
│   │       └── 010_CONSTITUTIONAL_FLOORS_F1F9_v45.md
│   ├── 02_actors/
│   ├── 03_runtime/
│   ├── 04_measurement/
│   ├── 05_memory/
│   ├── 06_paradox/
│   ├── 07_safety/
│   └── _INDEX/
│       ├── 00_MASTER_INDEX_v46.md                ← INDEX (links to all)
│       ├── CANON_COVERAGE_CHECKLIST_v46.md       ← META (moved from root)
│       └── CANON_INTEGRATION_MAP_v46.md          ← META (moved from root)
├── ledger/                                       ← AUDIT TRAIL
├── manifest/                                     ← SHA-256 VERIFICATION
├── phoenix_72/                                   ← AMENDMENT PROCESS
│   ├── README.md
│   └── AMENDMENT_F10F12_PROPOSAL_v46.md
└── archive/                                      ← OLD VERSIONS
    └── v45/
        └── CONSTITUTIONAL_CORE_v45.md            ← ARCHIVED
```

**Philosophy:**
- **Root level:** Primary canon document (one truth)
- **canon/ subdirs:** Implementation details (layers 00-07)
- **_INDEX/:** Navigation and metadata
- **archive/:** Historical versions

---

### Option B: Index-First (Alternative)

```
L1_THEORY/
├── README.md                                     ← ENTRY POINT
├── START_HERE.md                                 ← 🔥 NEW navigation guide
├── canon/
│   ├── 00_MASTER_INDEX_v46.md                    ← PRIMARY INDEX (promoted)
│   ├── 01_floors/
│   │   └── 010_CONSTITUTIONAL_FLOORS_F1F12_v46.md
│   ├── ... (02-07 unchanged)
│   └── meta/                                     ← 🔥 NEW (meta-canon)
│       ├── CANON_COVERAGE_CHECKLIST_v46.md
│       └── CANON_INTEGRATION_MAP_v46.md
├── ledger/
├── manifest/
└── phoenix_72/
```

**Philosophy:**
- Index is primary
- Canon subdirs contain actual law
- Meta documents separated

---

## 🔧 MIGRATION PLAN (Recommended: Option A)

### Phase 1: Archive v45 (Day 3 - After Phoenix-72)

```bash
# 1. Create archive directory
mkdir -p L1_THEORY/archive/v45/canon

# 2. Archive old master document
cp L1_THEORY/canon/000_CONSTITUTIONAL_CORE_v45.md \
   L1_THEORY/archive/v45/CONSTITUTIONAL_CORE_v45.md

# 3. Archive old floors
cp L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md \
   L1_THEORY/archive/v45/canon/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md

# 4. Archive meta files
cp L1_THEORY/canon/CANON_COVERAGE_CHECKLIST_v45.md \
   L1_THEORY/archive/v45/

cp L1_THEORY/canon/CANON_INTEGRATION_MAP_v45.md \
   L1_THEORY/archive/v45/
```

---

### Phase 2: Rename to v46

```bash
# 1. Master document
mv L1_THEORY/canon/000_CONSTITUTIONAL_CORE_v45.md \
   L1_THEORY/CONSTITUTIONAL_CORE_v46.md
# (promoted to root, renamed)

# 2. Floors
mv L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md \
   L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F12_v46.md

# 3. Master index
mv L1_THEORY/canon/_INDEX/00_MASTER_INDEX_v45.md \
   L1_THEORY/canon/_INDEX/00_MASTER_INDEX_v46.md
```

---

### Phase 3: Reorganize Meta Files

```bash
# Move meta files to _INDEX
mv L1_THEORY/canon/CANON_COVERAGE_CHECKLIST_v45.md \
   L1_THEORY/canon/_INDEX/CANON_COVERAGE_CHECKLIST_v46.md

mv L1_THEORY/canon/CANON_INTEGRATION_MAP_v45.md \
   L1_THEORY/canon/_INDEX/CANON_INTEGRATION_MAP_v46.md

# Delete temp file
rm L1_THEORY/canon/MISSING_FILE_HUNT_REPORT.md
```

---

### Phase 4: Add F10-F12 Content

```bash
# After Phoenix-72 cooling completes
# Append F10-F12 definitions to:
# - L1_THEORY/CONSTITUTIONAL_CORE_v46.md
# - L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F12_v46.md
```

---

### Phase 5: Update Cross-References

**Files to update:**

1. **L1_THEORY/README.md**
   - Point to `CONSTITUTIONAL_CORE_v46.md` (not `canon/000_...`)
   - Update floor count: "9 floors" → "12 floors"

2. **L1_THEORY/canon/_INDEX/00_MASTER_INDEX_v46.md**
   - Update all v45 references → v46
   - Add F10-F12 sections

3. **spec/v46/constitutional_floors.json**
   - Update `canon_ref` fields to point to v46 files

---

## 📋 FILE-BY-FILE DECISIONS

| Current File | Decision | Destination | Reason |
|--------------|----------|-------------|--------|
| `canon/000_CONSTITUTIONAL_CORE_v45.md` | PROMOTE + RENAME | `CONSTITUTIONAL_CORE_v46.md` (root) | Primary canon document |
| `canon/01_floors/010_..._F1F9_v45.md` | RENAME + EXTEND | `01_floors/010_..._F1F12_v46.md` | Add F10-F12 |
| `canon/_INDEX/00_MASTER_INDEX_v45.md` | RENAME | `_INDEX/00_MASTER_INDEX_v46.md` | Index stays |
| `canon/CANON_COVERAGE_CHECKLIST_v45.md` | MOVE + RENAME | `_INDEX/CANON_COVERAGE_CHECKLIST_v46.md` | Meta file |
| `canon/CANON_INTEGRATION_MAP_v45.md` | MOVE + RENAME | `_INDEX/CANON_INTEGRATION_MAP_v46.md` | Meta file |
| `canon/MISSING_FILE_HUNT_REPORT.md` | DELETE | ❌ Removed | Temporary scan |
| `phoenix_72/AMENDMENT_...md` | KEEP | Current location | Active proposal |

---

## 🎯 NEW README.md (Root Entry Point)

**File:** `L1_THEORY/README.md` (updated)

```markdown
# L1_THEORY: arifOS Constitutional Canon

**Version:** v46.0
**Status:** AUTHORITATIVE
**Floors:** 12 Constitutional Floors (F1-F12)

---

## 🔥 START HERE

**Primary Canon:** [`CONSTITUTIONAL_CORE_v46.md`](CONSTITUTIONAL_CORE_v46.md)
**Floor Definitions:** [`canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F12_v46.md`](canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F12_v46.md)
**Master Index:** [`canon/_INDEX/00_MASTER_INDEX_v46.md`](canon/_INDEX/00_MASTER_INDEX_v46.md)

---

## 📂 Directory Structure

| Directory | Purpose |
|-----------|---------|
| `CONSTITUTIONAL_CORE_v46.md` | PRIMARY CANON (start here) |
| `canon/00_foundation/` | Foundational principles |
| `canon/01_floors/` | 12 Constitutional Floors (F1-F12) |
| `canon/02_actors/` | AGI, ASI, APEX, Anti-Hantu, EYE |
| `canon/03_runtime/` | Pipeline, W@W, TEARFRAME |
| `canon/04_measurement/` | GENIUS Law, metrics |
| `canon/05_memory/` | EUREKA, Cooling, Phoenix-72 |
| `canon/06_paradox/` | Grey zones, Vault-999 |
| `canon/07_safety/` | Security scenarios |
| `canon/_INDEX/` | Navigation and metadata |
| `ledger/` | Audit trail (gitseal history) |
| `manifest/` | SHA-256 verification |
| `phoenix_72/` | Active amendments |
| `archive/` | Historical versions |

---

## 🏛️ The 12 Constitutional Floors

**Core 9 (F1-F9):**
- F1: Amanah (Trust)
- F2: Truth
- F3: Peace²
- F4: κᵣ (Empathy)
- F5: Ω₀ (Humility)
- F6: ΔS (Clarity)
- F7: RASA (Active Listening)
- F8: Tri-Witness
- F9: Anti-Hantu

**Hypervisor 3 (F10-F12 - NEW in v46):**
- F10: Symbolic Guard
- F11: Command Auth
- F12: Injection Defense

---

## 🔄 Version History

- **v46.0** (2026-01-12): Added F10-F12 hypervisor layer
- **v45.0** (2025-12-22): Phoenix-72 consolidation
- **v44.0**: TEARFRAME Physics
- **v42.0**: Constitutional consolidation

---

**DITEMPA BUKAN DIBERI** - Forged through Phoenix-72, not given.
```

---

## ⏱️ EXECUTION TIMELINE

| Phase | When | Duration | Dependency |
|-------|------|----------|------------|
| **Phase 1:** Archive v45 | Day 3 (2026-01-15) | 30 mins | Phoenix-72 cooling complete |
| **Phase 2:** Rename to v46 | Day 3 | 30 mins | Phase 1 done |
| **Phase 3:** Reorganize meta | Day 3 | 15 mins | Phase 2 done |
| **Phase 4:** Add F10-F12 | Day 3 | 2 hours | Phase 3 done |
| **Phase 5:** Update refs | Day 3 | 1 hour | Phase 4 done |
| **Total** | | **4.25 hours** | |

---

## ✅ SUCCESS CRITERIA

**After reorganization:**

- [ ] Single entry point: `L1_THEORY/CONSTITUTIONAL_CORE_v46.md`
- [ ] All v45 references → v46
- [ ] F10-F12 canonized in floors file
- [ ] Meta files in `_INDEX/`
- [ ] No duplicate master documents
- [ ] All cross-references updated
- [ ] `git status` clean
- [ ] README.md updated with new structure

---

## 🤔 DECISION REQUIRED

**Arif, which structure do you prefer?**

**Option A (RECOMMENDED):** Single master at root
- `L1_THEORY/CONSTITUTIONAL_CORE_v46.md` as primary canon
- `canon/` subdirs for details
- Clearest hierarchy

**Option B:** Index-first
- `canon/00_MASTER_INDEX_v46.md` as primary
- New `meta/` subdirectory
- More traditional structure

**Option C:** Something else?
- Tell me your vision

---

**DITEMPA BUKAN DIBERI** - Equilibrium forged through reorganization.

**Ready to execute when you approve + Phoenix-72 cooling completes.**
