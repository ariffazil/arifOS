# TRACK A SCAN: Governance Files v42 → v45 Migration

**Scan Date:** 2025-12-29 12:06 +08  
**Scope:** L1_THEORY/ + L2_GOVERNANCE/ + Root governance files  
**Mode:** Epoch labels + Version stamps + Cross-references  
**Status:** SCAN COMPLETE | AWAITING CODEX + CLAUDE CODE

---

## PART 1: EPOCH/VERSION LABELS (Must Change)

| File | Line | Current | Change to | Status |
|:-----|:-----|:--------|:----------|:-------|
| `L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md` | 3 | `Epoch: v45.0` | ✅ ALREADY FIXED | ✓ Done |
| `L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md` | 557 | `Epoch: v42.0` | `Epoch: v45.0` | ⏳ Change |
| `L1_THEORY/canon/02_actors/010_TRINITY_ROLES_v45.md` | 3 | `Epoch: v42.0` | `Epoch: v45.0` | ⏳ Change |
| `L1_THEORY/canon/02_actors/010_TRINITY_ROLES_v45.md` | 321 | `Epoch: v42.0` | `Epoch: v45.0` | ⏳ Change |
| `L1_THEORY/canon/02_actors/020_AGI_DELTA_ARCHITECT_v45.md` | 3 | `Epoch: v42.0` | `Epoch: v45.0` | ⏳ Change |
| `L1_THEORY/canon/02_actors/020_AGI_DELTA_ARCHITECT_v45.md` | 451 | `Epoch: v42.0` | `Epoch: v45.0` | ⏳ Change |
| `L1_THEORY/canon/02_actors/030_ASI_OMEGA_AUDITOR_v45.md` | 3 | `Epoch: v42.0` | `Epoch: v45.0` | ⏳ Change |
| `L1_THEORY/canon/02_actors/030_ASI_OMEGA_AUDITOR_v45.md` | 451 | `Epoch: v42.0` | `Epoch: v45.0` | ⏳ Change |
| `L1_THEORY/canon/02_actors/040_APEX_PSI_JUDICIARY_v45.md` | 3 | `Epoch: v42.0` | `Epoch: v45.0` | ⏳ Change |
| `L1_THEORY/canon/02_actors/050_FEDERATION_ORGANS_v45.md` | 3 | `Epoch: v42.0` | `Epoch: v45.0` | ⏳ Change |
| `L1_THEORY/canon/03_runtime/010_PIPELINE_000TO999_v45.md` | 3 | `Epoch: v42` | `Epoch: v45.0` | ⏳ Change |
| `L1_THEORY/canon/03_runtime/010_PIPELINE_000TO999_v45.md` | 809 | `Version: v42` | `Version: v45.0` | ⏳ Change |
| `L1_THEORY/canon/03_runtime/010_PIPELINE_000TO999_v45.md` | 810 | `Epoch: v42.0` | `Epoch: v45.0` | ⏳ Change |
| `L1_THEORY/canon/03_runtime/030_SPEC_CODE_BINDING_v45.md` | 4 | `Epoch: v42` | `Epoch: v45.0` | ⏳ Change |
| `L1_THEORY/canon/04_measurement/010_MEASUREMENT_CANON_v45.md` | 3 | `Epoch: v42.0` | `Epoch: v45.0` | ⏳ Change |
| `L1_THEORY/canon/05_memory/010_COOLING_LEDGER_PHOENIX_v45.md` | 4 | `Version: v42.0` | `Version: v45.0` | ⏳ Change |
| `L1_THEORY/canon/05_memory/020_VAULT_999_SOVEREIGN_KNOWLEDGE_v45.md` | 4 | `Version: v42.0` | `Version: v45.0` | ⏳ Change |
| `L1_THEORY/canon/05_memory/030_ZKPC_GOVERNANCE_PROOF_v45.md` | 4 | `Version: v42.0` | `Version: v45.0` | ⏳ Change |
| `L1_THEORY/canon/05_memory/040_FORENSICS_AUDIT_v45.md` | 4 | `Epoch: v42` | `Epoch: v45.0` | ⏳ Change |
| `L1_THEORY/canon/06_paradox/010_PARADOX_ENGINE_v45.md` | 4 | `Version: v42.0` | `Version: v45.0` | ⏳ Change |
| `L1_THEORY/canon/07_safety/01_SECURITY_SCENARIOS_v45.md` | 4 | `Version: v42.0` | `Version: v45.0` | ⏳ Change |
| `GOVERNANCE.md` | 463 | `_v42.md` | `_v45.md` | ✅ ALREADY FIXED |

**Subtotal Part 1:** 20 epoch/version changes (18 remaining)

---

## PART 2: CROSS-REFERENCE PATHS (Need Verification)

These reference `_v42.md` files that may or may not exist as `_v45.md`:

| File | Line(s) | References | Action |
|:-----|:--------|:-----------|:-------|
| `L1_THEORY/README.md` | 41-42 | `10_AGI_ENGINE_SPEC_v42.md`, `20_ASI_ENGINE_SPEC_v42.md` | ⚠️ Verify target exists |
| `L1_THEORY/canon/_INDEX/ROOT_MAP.md` | 16-26 | 11 references to `_v42.md` files | ⚠️ Verify each target |
| `L1_THEORY/canon/02_actors/020_AGI_DELTA_ARCHITECT_v45.md` | 1, 352-354, 458-465 | Header + cross-refs | ⏳ Update refs |
| `L1_THEORY/canon/02_actors/030_ASI_OMEGA_AUDITOR_v45.md` | 1, 352-354, 458-465 | Header + cross-refs | ⏳ Update refs |
| `L1_THEORY/canon/02_actors/040_APEX_PSI_JUDICIARY_v45.md` | 30-31, 46, 56 | Cross-refs to measurement/memory | ⏳ Update refs |
| `L1_THEORY/canon/02_actors/050_FEDERATION_ORGANS_v45.md` | 66 | Measurement ref | ⏳ Update ref |
| `L1_THEORY/canon/02_actors/010_TRINITY_ROLES_v45.md` | 1, 328 | Header + next step | ⏳ Update refs |
| `L1_THEORY/canon/03_runtime/030_SPEC_CODE_BINDING_v45.md` | 8 | Pipeline/measurement cross-links | ⏳ Update refs |
| `L1_THEORY/canon/04_measurement/020_CONTROL_LOGIC_v45.md` | 6 | Measurement/pipeline cross-links | ⏳ Update refs |
| `L1_THEORY/canon/05_memory/040_FORENSICS_AUDIT_v45.md` | 7, 22, 85 | Memory cross-links | ⏳ Update refs |
| `L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md` | 1, 567, 580 | Header + next step + footer | ⏳ Update refs |
| `L1_THEORY/canon/07_safety/02_MASTER_FLAW_SET_v45.md` | 258, 260, 261 | Safety cross-refs | ⏳ Update refs |

**Subtotal Part 2:** 50+ cross-reference path updates

---

## PART 3: HISTORICAL REFERENCES (DO NOT CHANGE)

Per Patch Interpretation — historical truth must remain:

| File | Line(s) | Content | Reason |
|:-----|:--------|:--------|:-------|
| `L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md` | 558 | `Forged: 2025-12-16` | Historical timestamp |
| `L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md` | 560 | `Authority: v42.0` | Original authority |
| `L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md` | 561 | `Hash: zkpc_v42` | Original hash |
| `L1_THEORY/canon/_INDEX/00_MASTER_INDEX_v45.md` | 169, 175, 179 | v42 archive references | Archive context |
| `L2_GOVERNANCE/README.md` | 94 | `system_prompt_v42.md` | Archive path |

**Subtotal Part 3:** 0 changes (PROTECTED)

---

## SUMMARY METRICS

| Category | Count | Action |
|:---------|:------|:-------|
| Epoch/Version labels | 18 | ✅ SEAL each |
| Cross-reference paths | ~50 | ⚠️ Verify then SEAL |
| Historical metadata | ~10 | ❌ DO NOT CHANGE |

---

## EXECUTION READINESS

| Track | Owner | Status | Dependencies |
|:------|:------|:-------|:-------------|
| **Track A (Governance)** | Antigravity | ✅ SCAN COMPLETE | None |
| **Track B (Config)** | Codex | ⏳ AWAITING | Codex proposal |
| **Track C (Code)** | Claude Code | ⏳ AWAITING | Claude Code analysis |

---

**Track A scan ready. Awaiting Codex + Claude Code.**
