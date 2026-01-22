# FILE SCAN REPORT: v42 → v45 Migration

**Scan Date:** 2025-12-29 11:44 +08  
**Mode:** /000 INIT + /entropy SCAN  
**Authority:** SEAL Decision 1 (Single Canon)  
**Search Patterns:** `v42`, `v42.0`, `_v42`, `V42`, `version 42`

---

## SUMMARY METRICS

| Category | Files Affected | Matches Found | Risk Level |
|:---------|:---------------|:--------------|:-----------|
| **L1_THEORY (Canon)** | 25+ | 143+ | **HIGH** (Constitutional) |
| **L2_GOVERNANCE** | 1 | 1 | LOW |
| **Code Files (*.py)** | 30+ | 169+ | **MEDIUM** (Test comments) |
| **Config (*.json, *.yaml)** | 20+ | 218+ | **HIGH** (Spec references) |
| **Documentation (*.md)** | 50+ | 909+ | **HIGH** (Extensive) |

**TOTAL ESTIMATED MATCHES:** 1400+ occurrences

---

## CATEGORY 1: L1_THEORY (CANONICAL GOVERNANCE)

### Priority: **CRITICAL** — Must update with care

| File | Line(s) | Current Content | Change Required |
|:-----|:--------|:----------------|:----------------|
| `L1_THEORY/README.md` | 41-42 | `10_AGI_ENGINE_SPEC_v42.md`, `20_ASI_ENGINE_SPEC_v42.md` | YES |
| `L1_THEORY/canon/_INDEX/ROOT_MAP.md` | 1, 15-33 | Multiple `_v42.md` references | YES |
| `L1_THEORY/canon/_INDEX/00_MASTER_INDEX_v45.md` | 15, 169, 175, 179 | Historical archive references | MAYBE (archive context) |
| `L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md` | 1, 12, 14, 20, 517, 557, 560, 561, 567, 573, 580 | v42 epoch/hash references | **PARTIAL** (per Patch Interpretation) |
| `L1_THEORY/canon/04_measurement/010_MEASUREMENT_CANON_v45.md` | 1, 3, 8, 14, 77, 116 | `v42` epoch, spec refs | YES |
| `L1_THEORY/canon/04_measurement/020_CONTROL_LOGIC_v45.md` | 1, 5, 6, 12 | `v42` header, spec refs | YES |
| `L1_THEORY/canon/05_memory/010_COOLING_LEDGER_PHOENIX_v45.md` | 4 | `v42.0 (Thermodynamic Epoch)` | YES (epoch label) |
| `L1_THEORY/canon/05_memory/020_VAULT_999_SOVEREIGN_KNOWLEDGE_v45.md` | 4 | `v42.0 (Thermodynamic Epoch)` | YES (epoch label) |
| `L1_THEORY/canon/05_memory/030_ZKPC_GOVERNANCE_PROOF_v45.md` | 4, 61, 72, 415 | v42 references | MIXED |
| `L1_THEORY/canon/05_memory/040_FORENSICS_AUDIT_v45.md` | 4, 7, 22, 85 | v42 cross-links | YES |
| `L1_THEORY/canon/06_paradox/010_PARADOX_ENGINE_v45.md` | 4 | `v42.0 (Thermodynamic Epoch)` | YES (epoch label) |
| `L1_THEORY/canon/06_paradox/06_GREY_ZONE_v45.md` | 5 | Source note | MAYBE (historical) |
| `L1_THEORY/canon/07_safety/01_SECURITY_SCENARIOS_v45.md` | 4 | `v42.0 (The Vaccine)` | YES (epoch label) |
| `L1_THEORY/canon/07_safety/02_MASTER_FLAW_SET_v45.md` | 258, 260, 261 | Cross-refs to _v42.md files | YES |

---

## CATEGORY 2: L2_GOVERNANCE

### Priority: **LOW** — Single reference

| File | Line | Current Content | Change Required |
|:-----|:-----|:----------------|:----------------|
| `L2_GOVERNANCE/README.md` | 94 | `archive/legacy_specs/system_prompt_v42.md` | NO (archive path) |

---

## CATEGORY 3: CODE FILES (*.py)

### Priority: **MEDIUM** — Mostly test comments

| File | Line(s) | Category | Risk |
|:-----|:--------|:---------|:-----|
| `tests/test_apex_prime_floors_mocked.py` | 244 | Comment | LOW |
| `tests/test_api_contract.py` | 10, 245, 247, 298, 413, 428, 436, 450 | API version docs | MEDIUM |
| `tests/test_spec_loader_unified.py` | 36-274 (15+ refs) | Version test fixtures | **HIGH** (Logic) |
| `tests/test_spec_v44_authority.py` | 70, 88, 90, 92, 94, 95, 260-262 | v44 vs v42 fallback tests | **HIGH** (Logic) |
| `tests/test_v35_features.py` | 44, 46 | Version constant tests | MEDIUM |
| `tests/test_fag_write.py` | 2 | Header comment | LOW |
| `tests/test_engines_arif_adam.py` | 441, 443 | API version comment | LOW |
| `tests/test_caged_llm_harness.py` | 337 | Verdict type comment | LOW |
| `tests/test_apex_genius_verdicts.py` | 144, 146 | Version constant tests | MEDIUM |
| `tests/integration/test_pipeline_with_memory.py` | 107-306 (10+ refs) | Patch path comments | LOW |

---

## CATEGORY 4: CONFIG FILES (*.json, *.yaml)

### Priority: **HIGH** — Spec authority references

| File | Line(s) | Content Type | Change Required |
|:-----|:--------|:-------------|:----------------|
| `spec/v45/constitutional_floors.json` | 6, 336 | Evolution history | MAYBE (historical) |
| `spec/v45/genius_law.json` | 6, 239, 240, 254, 264 | Evolution, integration refs | MAYBE (historical) |
| `spec/v45/cooling_ledger_phoenix.json` | 6, 14, 286, 287, 301 | Ledger version, refs | MAYBE (historical) |
| `spec/v45/waw_prompt_floors.json` | 6, 529-541 | Evolution, fallback refs | MAYBE (historical) |
| `spec/v45/UNIFIED_ARIFOS_v44_FULL_SPEC.json` | 759, 999 | Ledger version | MAYBE (historical) |
| `spec/v45/schema/genius_law.schema.json` | 87 | `integration_v42` key | MAYBE (schema) |
| `spec/v44/` (all files) | Multiple | v42 references | DEFER (v44 archive) |

---

## CATEGORY 5: DOCUMENTATION (*.md)

### Priority: **MEDIUM** — Many informational references

| File | Lines | Category | Change Required |
|:-----|:------|:---------|:----------------|
| `vault_999/EUREKA.md` | 3 | Sealed epoch | NO (historical) |
| `spec/v45/README.md` | 13, 35, 62, 75 | History/migration notes | NO (informational) |
| `spec/v44/README.md` | 13, 35, 62, 75 | History/migration notes | NO (informational) |
| `spec/v42/README.md` | All | v42 spec directory | NO (archive) |
| `L7_DEMOS/sealion_legacy/README.md` | 28 | Version reference | MAYBE |
| `L6_SEALION/tests/README_RAW_VS_GOVERNED.md` | 112 | Example banner | NO (demo) |

---

## CATEGORY 6: ARCHIVE FILES

These are in `archive/` directories and should **NOT** be changed:

- `archive/01_CONSTITUTIONAL_FLOORS_v42.md`
- `archive/v38_0_0/canon/_CONSTITUTIONAL_FLOORS_v38Omega.md`
- `archive/v42_detail/` (full v42 archive)
- `archive/legacy_specs/v42/` (if exists)

**Status:** ❌ DO NOT MODIFY (F1 Amanah — historical truth)

---

## DECISION MATRIX

| Scope | Count | Action | SEAL Required |
|:------|:------|:-------|:--------------|
| **Epoch labels only** (_v45.md files content) | ~20 | Update v42.0 → v45.0 | YES (per file) |
| **Cross-reference paths** (point to _v42.md) | ~50 | Update to _v45.md | YES |
| **Historical/evolution notes** | ~100 | KEEP as-is (audit trail) | NO |
| **Archive files** | ~30 | DO NOT TOUCH | FORBIDDEN |
| **Test logic** (v44 vs v42 fallback) | ~20 | SABAR (may break tests) | HUMAN DECISION |
| **Spec JSON evolution fields** | ~30 | KEEP (historical metadata) | NO |

---

## RECOMMENDED EXECUTION PLAN

### Phase 1: Epoch Labels (Low Risk)
Update `**Epoch:** v42.0` → `**Epoch:** v45.0` in all `_v45.md` canon files.
- ~15-20 files
- Single-line patches
- SEAL per file required

### Phase 2: Cross-References (Medium Risk)
Update file path references from `_v42.md` → `_v45.md` where actual files exist.
- Verify target file exists before updating
- ~30-50 references
- SEAL per file required

### Phase 3: Test Logic (High Risk) — SABAR
Test files with v42 fallback logic need human decision:
- Keep for backward compatibility?
- Update to v45-only?
- Archive v42 tests?

### Phase 4: Config Files (Medium Risk) — SABAR
JSON spec files with `_source_evolution` fields:
- Keep historical trail? (Current recommendation)
- Or update references?

---

## Ω₀ ESTIMATE

**Ω₀ = 0.05** (at upper humility band)

**Uncertainty Sources:**
- Total exact count unknown (909+ matches truncated)
- Some references are historical and MUST remain v42
- Test logic changes may break builds
- JSON evolution fields require human interpretation

---

**AWAITING:** Human decision on execution phases.

**Recommended First Action:** Phase 1 (Epoch labels) — lowest risk, highest signal.
