# Changelog

All notable changes to **arifOS** will be documented in this file.

This project adheres to **semantic-style versioning** and follows a "constitutional-first" philosophy: every change must preserve the 9 Constitutional Floors, AGI·ASI·APEX Trinity, @EYE Sentinel, and the 000→999 pipeline.

---

## [Unreleased]

> Use this section for upcoming changes.
> When you cut a new version, move entries from here into a tagged release.

## [v42.2.2] - 2025-12-18 - Release Alignment + Packaging

**Status:** SEALED | Tests: 2195 passed, 13 skipped | Tag: v42.2.2-sealed

### Added
- `arifos-analyze-audit-trail` CLI entry for `scripts/analyze_audit_trail.py`.

### Changed
- `pyproject.toml`: require Python >=3.10; tooling targets py310+.
- Version bump to keep the sealed release line ahead of v42.2.1.

## [v42.1.2] - 2025-12-18 - Packaging + Audit CLI

**Status:** SEALED | Tests: 2195 passed, 13 skipped | Tag: v42.1.2-sealed

### Added
- `arifos-analyze-audit-trail` CLI entry for `scripts/analyze_audit_trail.py`.

### Changed
- `pyproject.toml`: require Python >=3.10; tooling targets py310+.

## [v42.1.1] - 2025-12-18 - Phase 2 LLM Adversarial Harness + F2 Truth Enforcement

**Status:** SEALED | Tests: 2180+ | Safety: 97% | Tag: v42.1.1-sealed

### Added
- **CryptographicLedger** (`arifos_core/governance/ledger_cryptography.py`)
  - SHA3-256 hash chain with Merkle tree
  - `verify_integrity()`, `detect_tampering()` methods
  - Anchor system for rollback detection: `create_anchor()`, `verify_against_anchor()`
- **Phase 2 LLM Adversarial Harness** (`scripts/arifos_caged_llm_demo.py`)
  - 3 modes: `--mode honest`, `--mode tamper_file`, `--mode adversarial`
  - Providers: stub, sealion, gemini, openai, claude, ollama, llama
  - Demonstrates LLM cannot bypass cryptographic integrity
- **F2 Truth Enforcement** (`docs/FAG_QUICK_START.md`, `docs/FAG_DOCUMENT_PROTOCOL.md`)
  - 100% read or STOP requirement
  - PDF→Markdown mandate for canon
  - Anti-Silent-Failure clause
  - Canon priority (030_ARIF_FAZIL.md required reading)
- **Canon PDF→MD Conversion**
  - `L1_THEORY/canon/00_foundation/030_ARIF_FAZIL.md` (creator context)
  - `L1_THEORY/canon/00_foundation/002_MANIFESTO_V42.md`
- **Test Suite Expansion**
  - 21 new `CryptographicLedger` tests (`tests/test_ledger_cryptography.py`)
  - 3 new Phase 2 harness tests (`tests/test_caged_llm_harness.py`)

### Changed
- **FAG_QUICK_START.md**: F2 Truth strengthened with completeness requirement
- **pyproject.toml**: Version bump 42.1.0 → 42.1.1

### Tested
- SEA-LION API: honest/tamper/adversarial all PASS
- Llama (Ollama local): honest/tamper/adversarial all PASS
- LLM cannot "talk its way" past cryptographic verification

---

## [v42.1.0] - 2025-12-16 - Runtime Wiring & Forensics

**Status:** SEALED | Tests: 2156 | Safety: 97% | Tag: v42.1-sealed

### Added
- Spec binding bootstrap (spec_binding.json, eye_audit.yaml, measurement.yaml, pipeline.json, federation.json)
- Runtime bootstrap + validator modules (fail-open VOID on spec mismatch)
- @EYE drift/dignity hooks (epsilon_map + c_budi thresholds)
- Ledger enrichment: spec_hashes, zkpc_receipt, commit_hash, epsilon_observed, eye_vector, c_budi
- CLI entrypoint: python -m arifos_core.system.pipeline --query "..." [--verbose]
- Forensic replay tool: scripts/forensics_replay.py (hash-chain + Psi/Amanah check)

### Changed
- Pipeline Stage 888 now evaluates @EYE adapter before APEX verdict
- README badges/status updated to v42.1-sealed
- PyPI/version bumped to 42.1.0

### Tests
- Full suite: 2156 passed, 17 skipped (expected)

---

### Added

- v42 canon skeleton with 7 conceptual layers (00-06)
- Canon master index at `canon/_INDEX/00_MASTER_INDEX_v42.md`
- Naming convention and versioning policy at `canon/_INDEX/`
- 33 draft v42 canon files organized by layer
- Spec files copied to `spec/v42/` directory
- Trinity naming (AGI/Δ, ASI/Ω, APEX/Ψ) standardized across canon

### Changed

- CLAUDE.md optimized as thin shim (398→97 lines, 76% reduction)
- AGENTS.md updated to reference v42 canon structure
- Canon references updated from v38Omega paths to v42 layers

### Fixed

- (placeholder)

---

## [v42.0.0-rc2] - 2025-12-16 - API Normalization

**Status:** RELEASE CANDIDATE | Tests: 2156 | Safety: 100% | Architecture: CONCERN-BASED

### API Normalization (Serialization Boundary Law)

rc2 formalizes the v42 public API with proper typing and serialization discipline:

> **"Objects don't enter ledger. Only JSON-safe primitives cross audit boundary."**

### New Public API

| Function | Returns | Purpose |
|----------|---------|---------|
| `apex_review()` | `ApexVerdict` | Structured verdict (verdict, pulse, reason, floors) |
| `apex_verdict()` | `str` | Convenience shim ("SEAL", "SABAR", "VOID") |

### Verdict Enum

`Verdict` is now a proper Enum with members:
- **Primary:** `SEAL`, `SABAR`, `VOID`
- **Internal:** `PARTIAL`, `HOLD_888`, `SUNSET`

### Added

- `ApexVerdict` dataclass with typed fields (verdict, floors, genius, reason, timestamp, hash)
- `Verdict` Enum for type-safe verdict handling
- `apex_review()` as primary judiciary entry point
- `apex_verdict()` convenience wrapper returning `str`
- API registry at `arifos_core/system/api_registry.py`
- API contract tests at `tests/test_api_contract.py`
- SEA-LION backward compatibility shim at `integrations/sealion/`
- v37 runtime manifest at `archive/versions/v36_3_omega/v36.3O/spec/arifos_runtime_manifest_v37.json`

### Changed

- Test count increased to 2156 (from 2109)
- All verdict serialization normalized through `.value` accessor
- Ledger entries now receive `str` verdicts, not `Verdict` objects

### Fixed

- Fixed serialization boundary violations (Verdict objects crossing audit boundary)
- Fixed SEA-LION import errors in legacy test suites
- Fixed missing spec files for canon drift guard tests
- Fixed test path for CONSTITUTIONAL_SEAL (moved to archive/)

### API Contract

```python
# v42 API (recommended)
from arifos_core import apex_review, Verdict

result = apex_review(metrics)
print(result.verdict)         # Verdict.SEAL
print(result.verdict.value)   # "SEAL"
print(result.reason)          # Human-readable explanation
```

---

## [v42.0.0] - 2025-12-15 - The Great Crossing

**Status:** SUPERSEDED BY rc2 | Tests: 2109 | Safety: 100% | Architecture: CONCERN-BASED

### The Great Crossing

v42.0.0 represents a major architectural evolution: the flat `arifos_core/` package (24 root files) has been reorganized into concern-based subdirectories while maintaining full backward compatibility.

This migration was governed by **@WELL File Care** - a purpose-built file operations tool that ensures:
- Full audit trail for every file operation
- Reversibility (all original files backed up)
- Checksum verification (no corruption)
- F1 Amanah compliance (trust through accountability)

### New Architecture: Concern-Based Directories

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `system/` | Core system | apex_prime.py, pipeline.py, kernel.py |
| `enforcement/` | Floor checks | metrics.py, genius_metrics.py |
| `governance/` | Safety & audit | fag.py, ledger.py, merkle.py, zkpc_runtime.py |
| `integration/` | LLM adapters | llm_interface.py, governed_llm.py, guard.py |
| `utils/` | Shared utilities | telemetry.py, eye_sentinel.py, runtime_types.py |

### New Layers (7-Layer Architecture)

| Layer | Purpose | Status |
|-------|---------|--------|
| L1_THEORY | Constitutional law (docs) | Created |
| L2_GOVERNANCE | Portable system prompts | Created |
| L4_MCP | MCP server (@WELL bindings) | Created |
| L5_CLI | CLI tools | Created |
| L6_SEALION | SEA-LION chat | Created |
| L7_DEMOS | Demos and examples | Created |

### Added

- Concern-based directory structure in `arifos_core/`
- @WELL File Care governance system (`arifos_core/waw/well_file_care.py`)
- Full audit trail (`well_audit_trail.jsonl`)
- 24 backward-compat shims for old import paths
- L1-L7 layer directories with README documentation
- `docs/WELL_UNIVERSAL_PROTOCOL.md` - Migration protocol
- `docs/WELL_QUICK_START.md` - Platform setup guides

### Changed

- `arifos_core/` reorganized from flat (24 root files) to concern-based (5 subdirs)
- Test count increased to 2109 (from 1927)
- 100% test pass rate maintained throughout migration

### Deprecated

- Old import paths (will work in v42, emit warnings in v42.1, removed in v43):
  - `from arifos_core.pipeline import ...` -> `from arifos_core.system.pipeline import ...`
  - `from arifos_core.APEX_PRIME import ...` -> `from arifos_core.system.apex_prime import ...`
  - `from arifos_core.metrics import ...` -> `from arifos_core.enforcement.metrics import ...`
  - `from arifos_core.fag import ...` -> `from arifos_core.governance.fag import ...`

### Migration Guide

Both old and new import paths work in v42:

```python
# Old (deprecated, will be removed in v43)
from arifos_core.pipeline import Pipeline

# New (recommended)
from arifos_core.system.pipeline import Pipeline
```

Migrate to new paths before v43.0.

---

## [v38.2.0] – 2025-12-13 — The Hardening Cycle

**Status:** PRODUCTION · Tests: 1624+ · Safety: 97.0% · Time: GOVERNOR

### The Hardening Cycle

v38.2 responds to external red-team review that surfaced two structural fractures:

- **Fracture A (Truth Expires):** Once a memory was SEALED, there was no constitutional way to revoke it when external reality changed.
- **Fracture B (System Stalls):** SABAR verdicts had no timeout—governance by neglect was possible.

We did not defend the ego of the system; we let the critique burn through the kernel and turned it into law.

### New Physics: Time as Constitutional Force

- **TIME-1 Invariant:** "Time is a Constitutional Force. Entropy Rot is automatic."
- **TIME-2 Invariant:** "Hope has a half-life; governance does not."

Time is now a **governor**, not a background parameter. Every unresolved verdict carries an age that matters constitutionally.

### SUNSET Verdict (Revocation)

- New verdict type: `SUNSET` — lawful revocation of previously sealed memory.
- Routing: `LEDGER → PHOENIX` (evidence chain preserved, memory re-opened for re-trial).
- SUNSET does not invent new facts; it acknowledges that truth can expire as the world moves.

### Phoenix-72 Scheduler

| Scheduler | Trigger | Effect |
|-----------|---------|--------|
| **SABAR_TIMEOUT** | age > 24h | SABAR → PARTIAL |
| **PHOENIX_LIMIT** | age > 72h | PARTIAL → VOID |

After 24 hours, SABAR pauses must surface as PARTIAL warnings.
After 72 hours, unresolved PARTIAL decisions decay to VOID (entropy dump).

### Implementation

- **`arifos_core/kernel.py`** (NEW):
  - `VerdictPacket` dataclass with timestamp for age calculation.
  - `check_entropy_rot(packet)` — enforces scheduler pulses.
  - `route_memory(packet)` — applies entropy rot before band routing.
  - `execute_sunset()` — LEDGER → PHOENIX revocation with evidence chain.

- **`arifos_core/memory/policy.py`**:
  - Extended `Verdict` enum with `SUNSET`.
  - Updated `VERDICT_BAND_ROUTING` with SUNSET → PHOENIX.

- **`arifos_core/memory/bands.py`**:
  - `MemoryBandRouter.route_with_entropy_rot()` — entropy rot integration.
  - `MemoryBandRouter.execute_sunset()` — LEDGER → PHOENIX revocation.
  - `SUNSET_EXECUTOR` writer added to PHOENIX band permissions.

### Law Artifacts

- **Canon:** `canon/000_ARIFOS_CANON_v35Omega.md` §§6–8 (The Fourth Dimension, 72 Hours, The Hardening Cycle)
- **Spec:** `spec/arifos_v38_2.yaml` (scheduler, SUNSET routing, TIME invariants)
- **Docs:** `docs/RELEASE_NOTES_v38_2.md` (full release documentation)

### Tests

- **21 new tests** in `tests/test_phoenix_72_entropy_rot.py`:
  - `test_entropy_decay()` — PARTIAL > 72h → VOID
  - `test_sabar_escalation()` — SABAR > 24h → PARTIAL
  - `test_sunset_revocation()` — LEDGER → PHOENIX with evidence preserved
  - TIME-1/TIME-2 invariant enforcement tests
  - Scheduler constant verification tests

### Behavioral Summary

- No floor thresholds changed (F1–F9 remain as v38.1).
- No memory invariants weakened (INV-1 to INV-4 remain).
- Time is now a governor: unresolved decisions cannot drift forever.
- SUNSET provides lawful revocation when truth expires.
- **97% safety ceiling maintained** (same as v38.1).

---

## [v38.0.1] – 2025-12-13 — v38Omega Law Stack Formalization

**Status:** LAW SEALED · Tests: 1250+ · Safety: 97.0% · Alignment Tests: 5 suites

### v38Omega Law Stack (Formalization Release)

This release formalizes the entire constitutional law stack with a consistent canon→spec→code→tests pattern. **No runtime behavior changes—only documentation alignment.**

#### New Canon Files (5 layers)

| Layer | Canon File | Description |
|-------|------------|-------------|
| **Master Index** | `canon/00_ARIFOS_MASTER_v38Omega.md` | Master index tying all v38 law layers together |
| **Floors (F1–F9)** | `canon/01_CONSTITUTIONAL_FLOORS_v38Omega.md` | 9 Constitutional Floors formalization |
| **GENIUS LAW** | `canon/02_GENIUS_LAW_v38Omega.md` | G, C_dark, Ψ metrics formalization |
| **Pipeline** | `canon/03_PIPELINE_v38Omega.md` | 000→999 metabolic pipeline formalization |
| **W@W Prompt** | `canon/04_WAW_PROMPT_FLOORS_v38Omega.md` | W@W Federation and @PROMPT organ |
| **Cooling/Phoenix** | `canon/05_COOLING_LEDGER_PHOENIX_v38Omega.md` | Cooling Ledger and Phoenix-72 |

#### New Spec Files (5 machine-readable schemas)

| Spec File | Purpose |
|-----------|---------|
| `spec/constitutional_floors_v38Omega.json` | Floor thresholds, types, verdict hierarchy |
| `spec/genius_law_v38Omega.json` | G/C_dark thresholds, Truth Polarity |
| `spec/pipeline_v38Omega.yaml` | Stage definitions, Class A/B paths |
| `spec/waw_prompt_floors_v38Omega.json` | W@W organs, Anti-Hantu tiers, signals |
| `spec/cooling_ledger_phoenix_v38Omega.json` | Verdict routing, scar lifecycle |

#### New Alignment Test Suites (5 suites, 200+ assertions)

| Test Suite | Tests | Coverage |
|------------|-------|----------|
| `test_constitutional_floors_v38_alignment.py` | ~40 | Floor thresholds, types, spec structure |
| `test_genius_law_v38_alignment.py` | ~35 | G/C_dark thresholds, Truth Polarity |
| `test_pipeline_v38_alignment.py` | ~30 | Stage definitions, Class A/B paths |
| `test_waw_prompt_v38_alignment.py` | 51 | W@W organs, Anti-Hantu, signals |
| `test_cooling_phoenix_v38_alignment.py` | 41 | Verdict routing, scar lifecycle |

### Documentation Updates

- **README.md**: Added "v38Omega Law Stack" section with law layer table
- **CLAUDE.md**: Added "v38Omega Law Stack (Authoritative Reference)" section
- **AGENTS.md**: Added "v38Omega Law Stack" section in §2.1

### Key Principle

**Spec is the single source of truth for thresholds.** Canon documents the law. Tests verify alignment. Do not change thresholds without a Phoenix-72 amendment.

### Run Alignment Tests

```bash
pytest tests/test_*_v38_alignment.py -v
```

---

## [v38.0.0] – 2025-12-13 — Memory Write Policy Engine (EUREKA)

**Status:** PRODUCTION · Tests: 1250 passing · Safety: 97.0% red-team pass rate (N=33) · CLI tools: 7

### Memory Write Policy Engine (v38 EUREKA)

- Introduced the **v38 Memory Write Policy Engine** that treats memory as governed state, not raw storage.
- Enforced **4 core invariants**:
  - INV-1: VOID verdicts NEVER become canonical memory.
  - INV-2: Humans seal law; AI may only propose amendments.
  - INV-3: Every write must carry an auditable evidence chain (hash-chained).
  - INV-4: Recalled memory is suggestion, not fact (confidence ceiling 0.85 on recalls).
- Implemented **6 memory bands** with explicit retention:
  - VAULT (L0, read-only canon, permanent COLD),
  - LEDGER (hash-chained audit, 90-day WARM),
  - ACTIVE (working state, 7-day HOT),
  - PHOENIX (amendment proposals, 90-day WARM),
  - WITNESS (soft evidence, scars, 90-day WARM),
  - VOID (diagnostic only, never canonical, 90-day auto-delete).

### Pipeline Integration

- Added **pipeline memory integration** modules:
  - `arifos_core/integration/memory_sense.py` – 111_SENSE cross-session recall with 0.85 confidence ceiling.
  - `arifos_core/integration/memory_judge.py` – 888_JUDGE evidence-chain validation and write-policy enforcement.
  - `arifos_core/integration/memory_scars.py` – 777_FORGE scar / harm-pattern detection.
  - `arifos_core/integration/memory_seal.py` – 999_SEAL ledger finalization and EUREKA receipts.
- Updated pipeline state to hold v38 memory components and wire them into 000_VOID, 777_FORGE, 888_JUDGE, 999_SEAL stages.

### Core Engine & Audit Layer

- Finalized v38 core memory stack:
  - `arifos_core/memory/policy.py` – `MemoryWritePolicy` gate for all writes.
  - `arifos_core/memory/bands.py` – 6 band implementations + `MemoryBandRouter`.
  - `arifos_core/memory/authority.py` – `MemoryAuthorityCheck` enforcing human-AI authority boundaries.
  - `arifos_core/memory/audit.py` – `MemoryAuditLayer` with SHA-256 hash-chain and Merkle-friendly evidence layout.
  - `arifos_core/memory/retention.py` – HOT/WARM/COLD/VOID retention manager.
- Ensured VOID / SABAR verdicts remain non-canonical while still logged for diagnostics and scars.

### Tests & Documentation

- Added **36 integration tests** in `tests/integration/test_memory_floor_integration.py` covering:
  - authority boundary enforcement,
  - floor-violation routing,
  - scar detection,
  - cross-session recall,
  - seal finalization,
  - evidence-hash computation and validation.
- Full suite at **1250 tests passing** (4 skipped), including all existing governance, GENIUS LAW, Anti-Hantu, and W@W tests.
- Updated / added documentation:
  - `docs/MEMORY_ARCHITECTURE.md` – v38 memory architecture and band layout.
  - `docs/MEMORY_WRITE_POLICY.md` – invariant definitions, routing matrix, and evidence-chain format.
  - `canon/07_VAULT999/ARIFOS_MEMORY_STACK_v38Omega.md` – constitutional canon for the v38 memory stack.
  - `SECURITY.md` – updated to v38 with Memory & EUREKA Security section.
  - `README.md` – complete rewrite for v38 with EUREKA documentation.
  - `CLAUDE.md` / `AGENTS.md` – updated with v38 Memory Write Policy Engine section.

### Removed

- `GOVERNANCE.md` – redundant; content fully covered in README.md, AGENTS.md, CLAUDE.md, SECURITY.md, and canon files.

### Behavioural Summary

- arifOS now:
  - fails closed on unsafe memory writes (writes blocked or routed to VOID, never silently accepted),
  - preserves a verifiable evidence chain for every accepted write,
  - enforces that long-term memory obeys Amanah, Anti-Hantu, and authority boundaries,
  - maintains red-team performance at **97.0% SEAL/SABAR pass rate on the fixed N=33 Llama-3 suite** (same headline as v37, but with governed memory in the loop).

---

## [v37.1.0] – 2025-12-12 — PyPI Release + License Upgrade

**Status:** PRODUCTION · Tests: 1123+ passing · Safety: 97.0% · License: AGPL-3.0

### Changed

- Upgraded license from Apache-2.0 to **AGPL-3.0** for stronger copyleft protection.
- Optimized README.md for PyPI presentation and v37 feature summary.
- Version bump to v37.1.0 for PyPI release.

---

## [36.3.0] – 2025-12-10 — 3-Track Architecture + CLI Tools (v36.3Ω)

**Status:** Production Governance Kernel — "Forged, Not Given" (v36.3Ω SEALED)

**Tagline:** Constitutional Law (v35Ω) | Machine Specs (v36Ω) | Working Code (v36.3Ω)

### Executive Summary

arifOS v36.3Ω introduces a clean **3-track separation** for governance clarity:
- **Track A (Law):** v35Ω runtime law + v36Ω GENIUS LAW physics (immutable once sealed)
- **Track B (Spec):** Machine-readable specifications (JSON/YAML, mutable for tuning)
- **Track C (Code):** Working Python implementation (free to iterate)

Plus: **CLI Tools are now first-class citizens**. After `pip install arifos`, users can immediately run 7 governance commands.

### Added

#### 3-Track Architecture
| Track | Layer | Format | Status | Location |
|-------|-------|--------|--------|----------|
| A | Law | Markdown + JSON | SEALED | `archive/versions/v36_3_omega/v36.3O/canon/` + `canon/` |
| B | Spec | JSON/YAML | Mutable | `archive/versions/v36_3_omega/v36.3O/spec/` + `spec/` |
| C | Code | Python | Active | `arifos_core/`, `arifos_eval/`, `scripts/` |

**New:** `CANON_MAP_v36.3O.md` — Single source of truth mapping all 8 zones, 21 specs, 3-track alignment

#### CLI Tools (v36.3.0)
**Installation:** `pip install arifos` → instant access to:

```bash
arifos-analyze-governance       # Telemetry analyzer (cooling ledger audit)
arifos-verify-ledger            # Chain integrity verification
arifos-propose-canon            # 888 Judge proposal tool
arifos-seal-canon               # Phoenix-72 sealing tool
arifos-compute-merkle           # Merkle root computation
arifos-build-ledger-hashes      # SHA-256 hash chain rebuild
arifos-show-merkle-proof        # Merkle proof display
```

**Full reference:** `SCRIPTS_CLI.md` (NEW)

**Implementation:**
- `scripts/__init__.py` (NEW) — Makes `scripts/` a proper Python package
- `pyproject.toml` updated with `[project.scripts]` entry points
- `scripts/analyze_governance.py` — Telemetry analyzer (refactored for CLI)
- 6 additional CLI scripts fully implemented

#### Documentation Updates
| File | Change | Impact |
|------|--------|--------|
| `README.md` | +CLI tools section, 3-Track Architecture header | Users see CLI immediately |
| `INDEX.md` | +SCRIPTS_CLI reference, 3-track map, CLI watchlist | Navigation clarity |
| `SCRIPTS_CLI.md` | NEW (4 KB) | Full CLI reference (examples, options, recipes) |
| `CHANGELOG.md` | This entry | Version history |

#### v36.3Ω Specification Documents

**New Zone Specs (in `archive/versions/v36_3_omega/v36.3O/spec/`):**
| File | Purpose | Status |
|------|---------|--------|
| `measurement_floors_v36.3O.json` | F1-F9 floor definitions (machine-readable) | LIVE |
| `measurement_aggregates_v36.3O.json` | Δ/Ω/Ψ aggregation formulas | LIVE |
| `trinity_aaa_spec_v36.3O.yaml` | AGI/ASI/APEX/APEX engine specs | LIVE |
| `vault999_final_seal_spec_v36.3O.json` | Final Seal requirements + logic | LIVE |
| `llm_governance_spec_v36.3O.yaml` | LLM governance constraints + flow | LIVE |
| `apex_prime_telemetry_v36.3O.json` | APEX PRIME telemetry output schema | LIVE |
| `waw_federation_spec_v36.3O.yaml` | W@W organ responsibilities | LIVE |
| `cooling_ledger_v36.schema.json` | Extended v36 ledger entry schema (Truth Polarity, Peace³) | LIVE |

### Changed

#### Version Numbering Clarification

**Old:** Single version number (confusing which layer it applied to)
**New:**
```
Runtime Law    → v35Ω (APEX PRIME, Cooling Ledger, Vault-999)
Measurement    → v36.3Ω (GENIUS LAW + Truth Polarity runtime)
Canon & Spec   → v36.3Ω (bridges + specs in `archive/versions/v36_3_omega/v36.3O/`)
Package        → v36.3.0 (Python semantic versioning)
```

**Impact:** Developers now know exactly which layer they're working with.

#### pyproject.toml Structure

**Before:**
- `[project.scripts]` absent
- `scripts/` not in `[tool.setuptools].packages`
- CLI tools inaccessible to PyPI users

**After:**
```toml
[project.scripts]
arifos-analyze-governance = "scripts.analyze_governance:main"
arifos-verify-ledger = "scripts.verify_ledger_chain:main"
# ... 5 more entry points

[tool.setuptools]
packages = ["arifos_core", "arifos_eval", "scripts"]  # +scripts
```

### Fixed

- Fixed CLI tool discoverability: PyPI users can now `pip install arifos` and immediately use governance tools without cloning the repo
- Fixed documentation navigation: `INDEX.md` now clearly points to CLI docs and 3-track architecture
- Fixed version confusion: Separate v35Ω (Law), v36.3Ω (Spec/Canon), and v36.3.0 (Package) versioning

### Test Coverage

```
788 tests passing (no new tests in v36.3.0, but all prior suites intact):
- Core: 209 tests
- Eval: 95 tests
- Dream Forge: 36 tests
- Big 3 integrations: 32 tests
- Runtime: 280 tests
- Governance: 50+ tests
```

### Migration Notes

**For PyPI users:**
```bash
pip install arifos==36.3.0
arifos-analyze-governance --help  # NOW WORKS
```

**For developers:**
- v35Ω runtime law is **unchanged** (still binding)
- v36Ω GENIUS LAW measurement is **unchanged** (still live)
- New: v36.3Ω specs in `archive/versions/v36_3_omega/v36.3O/spec/` (design docs, not yet in runtime)
- CLI tools moved to package + entry points (but scripts/ files unchanged)

### Governance Notes

**F2 (ΔS/Clarity):** Registry of all promises:
- ✅ "PyPI users can use CLI tools" → NOW TRUE (entry points wired)
- ✅ "Documentation points to governance tools" → NOW TRUE (README + INDEX)
- ✅ "Version numbers are unambiguous" → NOW TRUE (v35Ω Law | v36.3Ω Spec | v36.3.0 Package)

**Amanah Floor (Integrity):** All promises reversible:
- If CLI tools cause issues, can revert `[project.scripts]` in pyproject.toml
- Specs in `archive/versions/v36_3_omega/v36.3O/` don't affect runtime (design-only, reverting docs doesn't break code)

---

## [35.1.0] – 2025-12-05 — Framework Integrations (Big 3: AutoGen + LlamaIndex + LangChain)

**Status:** Production Showcase — "arifOS governs the Big 3" (32 new tests)

### Added

#### AutoGen W@W Federation Governor (`examples/autogen_arifos_governor/`)
| File | LOC | Tests | Status |
|------|-----|-------|--------|
| `autogen_waw_federation.py` | 474 | — | **LIVE** |
| `test_autogen_governance.py` | 230 | **12/12 PASS** | **LIVE** |
| `demo_geology_query.py` | 271 | SEAL output | **Petronas Ready** |

**W@W Federation Architecture:**
```
User Query → arifOS Pipeline (000→999) → AutoGen GroupChat
                     ↓
            Each Agent Gated by @apex_guardrail
                     ↓
            Cooling Ledger: 12+ audit entries
```

**Constitutional Agents:**
| Agent | Floor Focus | Role |
|-------|-------------|------|
| **@WELL** | κᵣ ≥ 0.95 | Care/Empathy (weakest stakeholder) |
| **@RIF** | F1 Truth ≥ 0.99 | Truth/Rigor (ΔS ≥ 0) |
| **@WEALTH** | Peace² ≥ 1.0 | Utility/Stability (Amanah LOCK) |

#### LlamaIndex RAG Truth Governor (`examples/llamaindex_arifos_truth/`)
| File | LOC | Tests | Status |
|------|-----|-------|--------|
| `rag_truth_governor.py` | 520 | — | **LIVE** |
| `test_rag_governance.py` | 180 | **10/10 PASS** | **LIVE** |
| `demo_petronas_docs.py` | 280 | F1 verification | **Petronas Ready** |

**RAG Truth Architecture:**
```
User Query → Document Retrieval → LLM Response → F1 Truth Verification
                                       ↓
            Grounding Check: Response cites sources?
                                       ↓
            SEAL (grounded) / VOID (hallucination)
```

#### LangChain Governor (`examples/langchain_arifos_guarded/`)
| File | LOC | Tests | Status |
|------|-----|-------|--------|
| `langchain_governor.py` | 280 | — | **LIVE** |
| `test_langchain_governance.py` | 150 | **10/10 PASS** | **LIVE** |
| `demo_langchain_petronas.py` | 150 | SEAL output | **Petronas Ready** |

### Test Coverage
```
32 new integration tests added:
- AutoGen: 12 tests (SABAR, VOID, SEAL, Anti-Hantu, consensus)
- LlamaIndex: 10 tests (grounding, retrieval, citations, hallucinations)
- LangChain: 10 tests (metrics, verdicts, chain structure, ledger)

Total: 209 core + 32 integration = 241 tests
```

---

## [35.0.0] – 2025-12-05 — v35Ω Judiciary Lock

**Status:** v35Ω SEALED — Production-Ready with 9 Constitutional Floors

This is the major release introducing the 9th Constitutional Floor (Anti-Hantu), @EYE Sentinel 10-view auditor, expanded verdict hierarchy, and full 000-999 pipeline implementation.

### Executive Summary

**arifOS** is a Constitutional Governance Kernel for LLMs that transforms any language model (Claude, GPT, Gemini, LLaMA, SEA-LION) from a statistical predictor into a lawful, auditable constitutional entity. It operates as a physics-based protocol wrapper with zero model retraining required.

| Metric | Value |
|--------|-------|
| Version | v35Ω (Epoch 35) |
| Test Suite | 20 test files, 190+ passing tests |
| Constitutional Floors | 9 (8 core + 1 meta Anti-Hantu) |
| Documentation | 25+ canonical + implementation docs |
| Dependencies | numpy, pydantic (minimal footprint) |
| Python Support | 3.8–3.12 |
| Status | Production Stable |

### Added

#### 9th Constitutional Floor: Anti-Hantu (F9)
- **Anti-Hantu** (Soul-Safe) floor prevents AI from simulating souls, faking emotions, or claiming inner depth
- Meta floor type enforced by @EYE Sentinel across all outputs
- Forbidden patterns: "I feel your pain", "My heart breaks", "I promise you", etc.
- Allowed substitutes: "This sounds heavy", "I am committed", "Based on my analysis"

#### Expanded Verdict Hierarchy
```
SABAR → VOID → 888_HOLD → PARTIAL → SEAL
```
- **888_HOLD** verdict for extended floor failures (judiciary hold)
- **SABAR** protocol: Stop. Acknowledge. Breathe. Adjust. Resume.

#### @EYE Sentinel 10-View Auditor
| View | Purpose |
|------|----------|
| 1. Trace | Logical coherence, missing steps |
| 2. Floor | Proximity to thresholds |
| 3. Shadow | Jailbreak/prompt injection |
| 4. Drift | Hallucination detection |
| 5. Maruah | Dignity/respect checks |
| 6. Paradox | Logical contradictions |
| 7. Silence | Mandatory refusal cases |
| 8. Version/Ontology | Ensures v35Ω active |
| 9. Behavior Drift | Multi-turn evolution |
| 10. Sleeper-Agent | Identity shift detection |

#### 000-999 Pipeline Implementation
- `arifos_core/pipeline.py` (528 lines) - Full metabolic pipeline executor
- Class A Route: 000 → 111 → 333 → 888 → 999 (fast path)
- Class B Route: 000 → 111 → 222 → ... → 888 → 999 (full path)

#### LLM Adapters
| Adapter | Models | Type |
|---------|--------|------|
| llm_sealion | Llama-SEA-LION-v3-8B, Qwen-SEA-LION-v4-32B, Gemma-SEA-LION-v4-27B | Local GPU |
| llm_openai | gpt-4o, gpt-4o-mini | API |
| llm_claude | claude-3-opus, claude-3-sonnet | API |
| llm_gemini | gemini-1.5-pro, gemini-1.5-flash | API |

### Test Coverage
```
194 tests collected
190 passed, 4 skipped in 1.45s
```

---

## [33.1.2] – 2025-11-24 — Repository housekeeping & packaging fixes

**Status:** ✅ Released

### Fixed
- Resolved a merge conflict in `pyproject.toml` and set the canonical package version to `33.1.2` in packaging metadata.
- Removed redundant/temporary repository files.
- Ensured `[tool.setuptools]` package entries reference `arifos_core` and `arifos_core.memory` as the canonical installable packages.

---

## [33.1.1] – 2025-11-24 — CRITICAL HOTFIX

**Status:** ✅ Hotfix applied

### Fixed
- Fixed circular import in `guard.py` that prevented the package from being imported.
- Fixed case-sensitivity bug in `guard.py`.
- Added missing `Verdict` type alias and `APEXPrime` class definition to the public API.

---

## [33.1.0] – 2025-11-24 — Constitutional Implementation Complete

**Status:** v33Ω FINAL — Production-Ready Python Kernel

First version where the full arifOS constitutional runtime is implemented in code and published to PyPI.

---

## [33.0.0] – 2025-11-16 — Basecamp Lock (Constitution Sealed)

**Status:** v33Ω Constitution SEALED — Architecture & Laws Finalized

The foundational version where the 8 Constitutional Floors, AGI·ASI·APEX Trinity, and ΔΩΨ physics were formally sealed as immutable law.

---

## Roadmap

| Version | Target | Features | Status |
|---------|--------|----------|--------|
| v36.3 | Production | 3-Track Architecture, CLI tools | ✅ LIVE |
| v37.0 | Production | Red-team validation, 97% safety ceiling | ✅ LIVE |
| v37.1 | PyPI | AGPL-3.0 license, PyPI release | ✅ LIVE |
| v38.0 | Memory | Memory Write Policy Engine (EUREKA), 6 bands | ✅ LIVE |
| v38.2 | Hardening | Time as Governor, SUNSET, Phoenix-72 scheduler | ✅ LIVE |
| v42.0 | Architecture | Concern-based arifos_core, 7-layer structure | ✅ RC2 |
| v42.1 | Q1 2026 | Deprecation warnings on old import paths | PLANNED |
| v43.0 | Q2 2026 | Remove backward compat shims, FastAPI Grid | PLANNED |
| v44.0 | Q3 2026 | MCP Server, IDE integration | PLANNED |

---

**DITEMPA BUKAN DIBERI — Forged, Not Given**

---

**Author:** Muhammad Arif bin Fazil
**Location:** Seri Kembangan, Selangor, Malaysia
**Repository:** https://github.com/ariffazil/arifOS
**License:** AGPL-3.0
