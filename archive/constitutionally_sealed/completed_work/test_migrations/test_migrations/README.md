# Test Migration Archive (v35/v36/v38/v41)

**Archive Date:** 2025-12-29
**Phase:** Phase 3 Step 3.1 (Archive Old Alignment Tests)
**Reason:** Version alignment complete — legacy migration tests no longer needed

---

## What Was Archived

**19 alignment test files from v35/v36/v38/v41 era** (~317KB total)

These tests validated spec migrations and version upgrades during the evolutionary path from v35 → v45. Now that v45 alignment is complete and v44 is the only supported fallback, these historical migration tests serve archival purposes only.

---

## Files by Version

### v35 Tests (2 files, ~17KB)
- `test_guard_v35.py` (6.8KB) - v35 floor guard validation
- `test_v35_features.py` (10KB) - v35 feature compatibility tests

**Purpose:** Validated v35 → v36 migration path

---

### v36 Tests (4 files, ~46KB)
- `test_pipeline_order_v36.py` (1.5KB) - Stage ordering validation
- `test_seal_proposed_canon_v36.py` (13KB) - Phoenix-72 amendment sealing
- `test_telemetry_v36_spec_alignment.py` (20KB) - Telemetry spec alignment
- `test_vault_retrieval_v36.py` (12KB) - VAULT band retrieval logic

**Purpose:** Validated v36 → v37 migration path and Phoenix Patch (Neutrality ≠ Death)

---

### v38 Tests (10 files, ~215KB)
**Integration tests (3 files, 69KB):**
- `integration/test_memory_band_routing_v38.py` (22KB) - 6-band memory routing
- `integration/test_memory_eureka_comprehensive_v38.py` (22KB) - EUREKA policy comprehensive
- `integration/test_memory_integration_v38_eureka.py` (25KB) - Memory system integration

**Alignment tests (7 files, 146KB):**
- `test_cooling_phoenix_v38_alignment.py` (16KB) - Phoenix-72 spec alignment
- `test_floors_v38_alignment.py` (14KB) - Constitutional floors alignment
- `test_genius_law_v38_alignment.py` (14KB) - GENIUS LAW spec alignment
- `test_memory_policy_v38.py` (49KB) - Memory write policy validation
- `test_pipeline_v38_alignment.py` (19KB) - Pipeline stage alignment
- `test_v38_runtime_upgrade.py` (13KB) - Runtime upgrade procedures
- `test_waw_prompt_v38_alignment.py` (21KB) - W@W prompt floors alignment

**Purpose:** Validated v38Ω "flat file" spec migration to v42 "versioned directory" structure. Tested Gandhi Patch (Peace² de-escalation) and v38Omega philosophical naming convention.

---

### v41 Tests (3 files, ~39KB)
- `test_aclip_v41_2_adversarial.py` (30KB) - A-CLIP adversarial attack resistance
- `test_apex_prime_output_v41.py` (1.5KB) - APEX_PRIME output contract (v41)
- `test_mcp_honesty_v41.py` (7.5KB) - MCP tool honesty enforcement

**Purpose:** Validated v41 → v42 migration (MCP integration, adversarial testing, output contracts)

---

## What Remains Active

### v44 Tests (4 files - KEPT in tests/)
- `test_spec_v44_authority.py` - Track B authority validation
- `test_spec_v44_manifest_enforcement_subprocess.py` - SHA-256 manifest enforcement
- `test_spec_v44_schema_enforcement_subprocess.py` - JSON Schema validation
- `test_spec_v44_subprocess_proof.py` - Subprocess isolation proof

**Reason:** v44 is current Track B fallback (v45→v44→FAIL). These tests remain critical for cryptographic spec integrity.

---

## Historical Context

### The Evolutionary Path

**v35 → v36 (Phoenix Patch):**
- Problem: Neutral factual text scored low Ψ (vitality) → false SABAR triggers
- Solution: Neutrality buffer (peace_score 0.4-0.6 → effective_peace = 1.0)
- Insight: "For constitutional AI, clarity (order) IS vitality — boring is HEALTHY"

**v36 → v38 (Gandhi Patch + Omega Naming):**
- Problem: AI penalized for user toxicity (input toxicity hurt output scores)
- Solution: De-escalation bonus (toxic input + empathetic output → +0.25 boost)
- Insight: "Peace is the de-escalation of war, not just its absence"
- Naming: v38Omega ("Ω" = philosophical completeness/finality)

**v38 → v42 (Versioned Directories):**
- Problem: Flat file naming prevented parallel version coexistence
- Solution: spec/v42/, spec/v38/, spec/v35/ directory structure
- Insight: "Flat is simpler for small projects, directories scale better"

**v41 → v42 (MCP Integration):**
- Added: MCP server tools (arifos_judge, arifos_recall, arifos_audit)
- Added: Adversarial attack resistance testing
- Added: Output contract validation

**v42 → v44 (Track B Cryptographic Integrity):**
- Added: SHA-256 manifest (MANIFEST.sha256.json)
- Added: JSON Schema validation at load-time
- Added: Tamper-evident spec enforcement
- Insight: "Constitution requires cryptographic proof, not just JSON files"

**v44 → v45 (Lane-Aware Governance + Entropy Reduction):**
- Added: Lane taxonomy (PHATIC/SOFT/HARD/REFUSE)
- Added: PHATIC verbosity ceiling (first quality ceiling, not just safety floors)
- Added: Full 5-spec Track B enforcement
- Removed: v42/v38/v35 fallback code (fail-closed)
- Insight: "Lane taxonomy beats fixed floor suite — context-aware thresholds"

---

## Why Archive Now?

**v45.0 alignment complete (Dec 2025):**

1. ✅ All 5 Track B specs runtime-loaded (constitutional_floors, genius_law, session_physics, waw_prompt_floors, cooling_ledger_phoenix)
2. ✅ v45→v44→FAIL pattern established (no legacy fallbacks)
3. ✅ Cryptographic manifest verification enforced
4. ✅ Verdict unification complete (all import from apex_prime)
5. ✅ Spec path updates to v45 (with v44 fallback)
6. ✅ Legacy fallback code removed (v42/v38/v35)

**Migration window closed:**
- v35/v36: 9+ versions behind (archived ~3 years ago)
- v38: 7 versions behind (Omega era ended with v42)
- v41: 4 versions behind (pre-Track B cryptography)
- v44: Current fallback (1 version behind, KEPT ACTIVE)

**Tests preserved institutional knowledge:**
- Gandhi Patch insights → documented in archive/v42_v38_v35_eureka_insights.md
- Phoenix Patch insights → documented in archive/v42_v38_v35_eureka_insights.md
- Migration patterns → documented in this README
- All learnings captured before archival

---

## Restoration Procedure

**To restore archived tests (if needed for historical research):**

```bash
# From repo root
cp archive/test_migrations/*.py tests/
cp archive/test_migrations/integration/*.py tests/integration/

# Verify restoration
ls tests/test_*_v35*.py tests/test_*_v36*.py tests/test_*_v38*.py tests/test_*_v41*.py
# Expected: 19 files restored
```

**To run archived tests (may require spec restoration):**

```bash
# Archived tests expect old spec files - restore specs first
git checkout v38.0.0 -- spec/constitutional_floors_v38Omega.json
git checkout v42.1.0 -- spec/v42/

# Run specific version tests
pytest tests/test_floors_v38_alignment.py -v
pytest tests/test_pipeline_v36.py -v

# Cleanup after testing
git restore spec/
```

---

## Entropy Metrics

**Before Phase 3 Step 3.1:**
- tests/ directory: 23 version-tagged files (v35/v36/v38/v41/v44)
- Total size: ~355KB
- Version span: v35 → v44 (9 version increments)
- Migration debt: 19 files testing historical transitions

**After Phase 3 Step 3.1:**
- tests/ directory: 4 version-tagged files (v44 only)
- Active size: ~38KB
- Archived size: ~317KB (moved to archive/test_migrations/)
- Version span: v44 only (current fallback)
- Migration debt: 0 files (historical tests archived)

**Net Impact:**
- Active test directory: 355KB → 38KB (-89.3% version-tagged files)
- Entropy reduction: 23 → 4 version-tagged files (-82.6%)
- Maintenance burden: 5 versions → 1 version (v44 fallback only)
- Historical knowledge: 100% preserved in archive + eureka insights

---

## Phase Context

**Phase 1 (COMPLETE):** Core v45 alignment
- Verdict unification (12 → 1 canonical source)
- Spec loaders (5/5 Track B specs runtime-loaded)
- v45→v44 fallback priority

**Phase 2 (COMPLETE):** SEA-LION & Legacy Cleanup
- SEA-LION test consolidation (tests_consolidated/ archived)
- v42/v38/v35 fallback code removal
- Eureka insights documented

**Phase 3 Step 3.1 (THIS STEP):** Archive old alignment tests
- 19 files (v35/v36/v38/v41) moved to archive/test_migrations/
- v44 tests remain active (current fallback)
- Historical context preserved in this README

**Next:** Phase 3 Step 3.2 - Consolidate telemetry_v36.py into telemetry.py

---

## Verification Checklist

**Before archiving:**
- [x] All 19 files identified (v35: 2, v36: 4, v38: 10, v41: 3)
- [x] File sizes documented (~317KB total)
- [x] Historical context researched (Gandhi Patch, Phoenix Patch, Omega naming)
- [x] Restoration procedures documented
- [x] This README created

**After archiving:**
- [ ] All 19 files moved to archive/test_migrations/
- [ ] v44 tests remain in tests/ (4 files)
- [ ] v44 tests still pass: `pytest tests/test_spec_v44*.py -v`
- [ ] No broken imports or references

---

## Related Documentation

- **Eureka Insights:** [archive/v42_v38_v35_eureka_insights.md](../v42_v38_v35_eureka_insights.md) - Design principles from legacy code
- **Scripts Insights:** [archive/scripts_eureka_insights_v45.md](../scripts_eureka_insights_v45.md) - Institutional knowledge from 5 generations
- **SEA-LION Archive:** [archive/sealion_tests_snapshot_20251227/ARCHIVE_MANIFEST.md](../sealion_tests_snapshot_20251227/ARCHIVE_MANIFEST.md) - Test consolidation archive
- **Migration Guide:** [docs/MIGRATION_v42_to_v45.md](../../docs/MIGRATION_v42_to_v45.md) - Version upgrade procedures
- **Track B Specs:** [spec/v45/](../../spec/v45/) - Current authoritative specifications

---

**Authority:** Phase 3 Step 3.1 per plan file `C:\Users\User\.claude\plans\lovely-nibbling-owl.md`

**DITEMPA BUKAN DIBERI** — Historical tests forged knowledge; now they rest in archive.

*Created: 2025-12-29 | arifOS v45.0 | Phase 3 Step 3.1*
