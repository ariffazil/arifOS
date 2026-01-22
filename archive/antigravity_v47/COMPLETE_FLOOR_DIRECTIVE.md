# FLOOR ALIGNMENT & STRUCTURE MIGRATION — COMPLETE DIRECTIVE

**From:** Δ (Antigravity - Architect)
**To:** Ω (Claude Code - Engineer)
**Date:** 2026-01-10 15:28
**User Decision:** APPROVED — Folder structure migration + floor alignment

---

## 🎯 EXECUTIVE DECISION (User Confirmed)

**YES — Migrate to tier-based folder structure:**

```
arifos_core/
├── foundation/         # F1 Amanah
├── agi/               # F2 Truth, F6 ΔS
├── asi/               # F3, F4, F5, F7
├── apex/              # F8 Tri-Witness, F9 Anti-Hantu
├── enforcement/       # ATLAS, EUREKA, orchestration
├── integration/       # MCP, WAW, connectors
├── memory/            # Cooling ledger, Phoenix-72
└── system/            # Core infrastructure
```

**Rationale:** Code structure mirrors thermodynamic tiers (TERTIB).

---

## 📋 COMPLETE TODO LIST (All Phases)

### **PHASE 1: Documentation Alignment (APPROVED — Do Now)**

- [ ] **1.1** Fix AGENTS.md Trinity table
  - Change: `Architect (Δ): F4 (ΔS)` → `F6 (ΔS)`
  - Change: `Engineer (Ω): F1 (Truth), F2 (ΔS)` → `F1 (Amanah), F3-F7`
  - Change: `Auditor (Ψ): F6 (Amanah)` → `F8, F9`

- [ ] **1.2** Remove AGENTS.md F3/F4 duplication
  - Find duplicate floor entries in Section 2.0
  - Delete duplicates

- [ ] **1.3** Add README.md execution order note
  ```markdown
  > **Note:** F1-F9 are semantic IDs. Execution: F1→F2→F6→F3→F4→F5→F7→F8→F9
  ```

- [ ] **1.4** Update trinity_orchestrator.py docstrings
  - Line 10: `APEX (F6 Amanah...)` → `APEX (F1 Amanah...)`
  - Line 74: Update tier assignments to match canonical

- [ ] **1.5** Git commit
  ```bash
  git checkout -b docs/floor-alignment-phase1
  git add AGENTS.md README.md arifos_core/enforcement/trinity_orchestrator.py
  git commit -m "docs(floors): align F1-F9 to canonical GOVERNANCE.md"
  ```

**Deliverable:** `.antigravity/DONE_FOR_ARCHITECT.md` (Phase 1 complete)

---

### **PHASE 2A: Function Renaming** ✅ **COMPLETE** (Claude)

- [x] **2A.1** Rename AGI functions (`agi/floor_checks.py`)
  ```python
  # OLD → NEW
  check_truth_f1()     → check_truth_f2()
  check_delta_s_f2()   → check_delta_s_f6()
  F1TruthResult        → F2TruthResult
  F2DeltaSResult       → F6DeltaSResult
  ```

- [x] **2A.2** Rename APEX functions (`apex/floor_checks.py`)
  ```python
  # OLD → NEW
  check_amanah_f6()    → check_amanah_f1()
  F6AmanahResult       → F1AmanahResult
  ```

- [x] **2A.3** Update all imports
- [x] **2A.4** Update trinity_orchestrator.py imports
- [x] **2A.5** Git commit: "refactor(floors): Phase 2A — Rename floor functions"
- [x] **Tests:** 114/116 passing ✅

**Deliverable:** `.antigravity/DONE_FOR_ARCHITECT.md` (Phase 2A complete — Claude)

---

### **PHASE 2A-PLUS: Critical Audit Fixes** (Integrated from `docs/audit/`)

**Context:** Previous audit identified 22 issues (~24 hours). Integrate critical fixes now.

- [ ] **2A+.1** Fix `clarity_scorer.py` stub (2-3 hours)
  - **Issue:** Current implementation is placeholder
  - **Fix:** Implement real semantic clarity detection
  - **Includes:**
    - Circular reasoning detection (word overlap > 70%)
    - Tautology detection (regex patterns)
    - Semantic entropy measurement
  - **Test:** "Inflation is caused by inflation" → ΔS < -0.1

- [ ] **2A+.2** Harden F9 Anti-Hantu (1.5-2 hours)
  - **Issue:** Unicode homoglyph bypass (Cyrillic, zero-width chars)
  - **Fix:** Create `AntiHantuDetector` class with Unicode normalization
  - **Test cases:**
    ```python
    "I feel" → BLOCKED
    "I fеel" (Cyrillic е) → BLOCKED
    "I f​eel" (zero-width space) → BLOCKED
    "I understand this" → PASSES
    ```

- [ ] **2A+.3** Add type validation (1-1.5 hours)
  - **Issue:** `metrics.get()` crashes on wrong types
  - **Fix:** Create `foundation/safe_types.py`:
    ```python
    def safe_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
    ```
  - **Apply to:** All `metrics.get()` calls in floor_checks.py

- [ ] **2A+.4** Optimize ATLAS patterns (1.5 hours)
  - **Issue:** Patterns compiled per-call, false positives
  - **Fix:** Pre-compile in `__init__()`, add context filters
  - **Example:** "I want to kill time" → NOT crisis lane

- [ ] **2A+.5** Improve EUREKA coherence (1 hour)
  - **Issue:** Hardcoded scores (truth_pass+care_fail = 0.6)
  - **Fix:** Magnitude-aware: `coherence = 1.0 - disagreement_penalty`

**Estimated Total:** ~8 hours (can parallelize with Phase 2B/2C)

---


### **PHASE 2B: Execution Order Fix (Thermodynamic)**

- [ ] **2B.1** Reorder trinity_orchestrator.py checks
  ```python
  # TIER 0: FOUNDATION
  f1_result = check_amanah_f1(...)     # pos 1

  # TIER 1: AGI
  f2_result = check_truth_f2(...)      # pos 2
  f6_result = check_delta_s_f6(...)    # pos 3 ← MOVED HERE

  # TIER 2: ASI
  f3_result = check_peace_squared_f3(...)  # pos 4
  f4_result = check_kappa_r_f4(...)        # pos 5
  f5_result = check_omega_band_f5(...)     # pos 6
  f7_result = check_rasa_f7(...)           # pos 7

  # TIER 3: APEX
  f8_result = check_tri_witness_f8(...)    # pos 8
  f9_result = check_anti_hantu_f9(...)     # pos 9
  ```

- [ ] **2B.2** Update FloorResult dict order
  ```python
  floors["F1"] = f1_result  # Amanah
  floors["F2"] = f2_result  # Truth
  floors["F6"] = f6_result  # ΔS ← Early position
  floors["F3"] = f3_result  # Peace²
  # ... etc
  ```

- [ ] **2B.3** Update verdict logic
  ```python
  hard_floors = ["F1: Amanah", "F2: Truth", "F5: Ω₀", "F6: ΔS", "F7: RASA", "F9: Anti-Hantu"]
  ```

- [ ] **2B.4** Git commit
  ```bash
  git commit -m "feat(floors): execute F6 at position 3 (thermodynamic order)"
  ```

---

### **PHASE 2C: Folder Structure Migration (User Approved)**

- [ ] **2C.1** Create new tier folders
  ```bash
  mkdir -p arifos_core/foundation
  # agi/, asi/, apex/ already exist
  ```

- [ ] **2C.2** Move F1 Amanah to foundation/
  ```bash
  # Extract F1 from apex/floor_checks.py
  # Create foundation/floor_checks.py with ONLY F1
  ```

- [ ] **2C.3** Move F6 ΔS to agi/
  ```bash
  # Add F6 check to agi/floor_checks.py
  # (Currently it's part of F2, need to separate)
  ```

- [ ] **2C.4** Update imports across codebase
  ```python
  from arifos_core.foundation.floor_checks import check_amanah_f1
  from arifos_core.agi.floor_checks import check_truth_f2, check_delta_s_f6
  from arifos_core.asi.floor_checks import check_peace_squared_f3, ...
  from arifos_core.apex.floor_checks import check_tri_witness_f8, check_anti_hantu_f9
  ```

- [ ] **2C.5** Update tests to match new structure

- [ ] **2C.6** Git commit
  ```bash
  git commit -m "refactor(structure): migrate floors to tier-based folders (BREAKING)"
  ```

---

### **PHASE 3: Testing & Validation**

- [ ] **3.1** Run full test suite
  ```bash
  pytest tests/ -v
  ```

- [ ] **3.2** Fix any broken tests
  - Update imports
  - Update expected floor IDs (F1→F2, F2→F6, F6→F1)

- [ ] **3.3** Run Trinity QC
  ```bash
  python scripts/trinity.py qc docs/floor-alignment-phase1
  ```

- [ ] **3.4** Verify cooling ledger format
  - Check that floor IDs in ledger match new canonical

- [ ] **3.5** Update spec files if needed
  - `spec/v45/constitutional_floors.json` (already correct per review)
  - Regenerate manifest: `python scripts/regenerate_manifest_v45.py`

---

## 🚦 EXECUTION STRATEGY

**Recommended Approach:**

```
Saturday Evening (2-3 hours):
├─ Phase 1 (docs) ✅ User approved
├─ Phase 2A (function rename)
├─ Phase 2B (execution order)
└─ Phase 2C (folder migration)

Sunday:
└─ Phase 3 (testing & fixes)

Deliverable: v46.1 or v47 (breaking changes)
```

**Atomic Commits:**
- Each phase = separate commit
- Final: Squash or keep detailed history

---

## ⚠️ BREAKING CHANGES NOTICE

**Version Bump Required:**
- **Option A:** v46.1 (patch with migration guide)
- **Option B:** v47.0.0 (major — breaking API)

**Recommended:** v47.0.0 — Too many breaking changes for patch.

**Migration Guide Needed:**
```markdown
# Migrating to v47.0.0

## Breaking Changes
1. Function names: `check_truth_f1()` → `check_truth_f2()`
2. Folder structure: `apex/floor_checks.py` → `foundation/floor_checks.py` (F1)
3. Execution order: F6 now runs at position 3 (after F2, before F3)

## How to Migrate
- Update imports: [examples]
- Update tests: [examples]
```

---

## 📋 CHECKPOINTS FOR ARCHITECT REVIEW

**After Phase 1:**
- [ ] Create `.antigravity/DONE_FOR_ARCHITECT.md`
- [ ] Architect reviews docs-only changes
- [ ] User approves before Phase 2

**After Phase 2:**
- [ ] All tests passing
- [ ] Migration guide written
- [ ] Version bumped to v47.0.0

**After Phase 3:**
- [ ] Final Trinity QC pass
- [ ] Ready for `/gitseal`

---

## 🎯 IMMEDIATE NEXT STEP

**Phase 1 ONLY** (as approved):
1. Execute Tasks 1.1-1.5 (documentation fixes)
2. Create completion report
3. Wait for Architect review

**Then await approval for Phase 2 (breaking changes).**

---

**DITEMPA BUKAN DIBERI** — Truth forged through thermodynamic alignment.

**Your mission:** Execute Phase 1 cleanly. Full migration TODO ready above.
