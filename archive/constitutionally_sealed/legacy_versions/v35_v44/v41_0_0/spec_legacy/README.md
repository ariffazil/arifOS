# spec_archive/

**Purpose:** Archival documentation of arifOS v38.2 current state

**Status:** EXTRACTION from existing codebase (no new features invented)

**Created:** 2025-12-13

---

## Overview

This directory contains 7 markdown files that document the **current implementation** of arifOS v38.2 constitutional governance kernel. All information is extracted from existing code, specs, and README content.

**Key Principle:** These documents are **PURE EXTRACTION**. They do not invent, modify, or propose new features. They document what exists.

---

## Document Index

| # | File | Purpose | Lines |
|---|------|---------|-------|
| 1 | [arifOS-v38-Core-Brain.md](arifOS-v38-Core-Brain.md) | 000→999 pipeline, AAA Trinity, W@W organs, @EYE | 268 |
| 2 | [arifOS-Constitution-9-Floors.md](arifOS-Constitution-9-Floors.md) | 9 floors, thresholds, detectors, GENIUS LAW | 405 |
| 3 | [Cooling-Ledger-v35-Schema-and-Usage.md](Cooling-Ledger-v35-Schema-and-Usage.md) | JSON schema, hash-chain, CLI tools | 503 |
| 4 | [Memory-Bands-v38-Policy-Current-State.md](Memory-Bands-v38-Policy-Current-State.md) | 6 bands, routing, write policy | 463 |
| 5 | [GENIUS-LAW-Truth-Polarity-Extract.md](GENIUS-LAW-Truth-Polarity-Extract.md) | G/C_dark/Ψ formulas, truth polarity | 487 |
| 6 | [L4-Jailbreak-Anti-Hantu-Defense.md](L4-Jailbreak-Anti-Hantu-Defense.md) | Anti-Hantu patterns, Amanah detector | 487 |
| 7 | [Phase-4-Integration-Status-v38.md](Phase-4-Integration-Status-v38.md) | Implementation status, CLI tools, v38.2 time | 473 |

**Total:** 3,086 lines of archival documentation

---

## Document Summaries

### 1. arifOS-v38-Core-Brain.md

**Covers:**
- 000→999 metabolic pipeline (10 stages)
- Class A vs Class B routing
- AAA Trinity: ARIF (Architect), ADAM (Auditor), APEX PRIME (Judiciary)
- W@W Federation organs: @WELL, @RIF, @WEALTH, @GEOX, @PROMPT
- @EYE Sentinel multi-view system (10+ views)
- zkPC 5-phase runtime flow (stub)
- Module paths for all components

**Key Sections:**
- Pipeline stage table with modules
- AAA engine mandates and output types
- W@W organ veto power matrix
- @EYE view table with lead stages

---

### 2. arifOS-Constitution-9-Floors.md

**Covers:**
- Complete list of 9 constitutional floors
- Exact field names, types, and thresholds
- Floor enforcement in 888_JUDGE stage
- GENIUS LAW metrics (G, C_dark, Ψ)
- Truth Polarity System
- Extended floors (v35Ω)
- Detector module paths

**Key Sections:**
- Floor table with thresholds and tiers
- Detailed definitions for each floor
- GENIUS LAW formulas and thresholds
- Truth polarity categories

---

### 3. Cooling-Ledger-v35-Schema-and-Usage.md

**Covers:**
- JSON schema from spec/cooling_ledger.schema.json
- CoolingEntry dataclass fields
- Hash-chain integrity mechanism (SHA3-256)
- 7 CLI tools with usage examples
- v37 extensions (HeadState, rotation, fail-open)
- Test coverage

**Key Sections:**
- Complete JSON schema with all fields
- Hash computation algorithm
- CLI tool documentation
- Logging function signature

---

### 4. Memory-Bands-v38-Policy-Current-State.md

**Covers:**
- 6 Memory Bands (VAULT, LEDGER, ACTIVE, PHOENIX, WITNESS, VOID)
- Retention tiers (HOT, WARM, COLD, VOID)
- Verdict → Band routing table
- v38 Memory Write Policy Engine
- 4 core invariants
- Writer permissions matrix
- Phoenix-72 finalization process

**Key Sections:**
- Band property tables
- Verdict routing logic
- MemoryWritePolicy class
- Human seal enforcement

---

### 5. GENIUS-LAW-Truth-Polarity-Extract.md

**Covers:**
- GENIUS LAW formula components (Δ, Ω, Ψ)
- G (Genius Index) computation
- C_dark (Dark Cleverness) computation
- Ψ_APEX (System Vitality) computation
- Truth Polarity System (4 categories)
- v36.2 PHOENIX patch (vitality calibration)
- Integration into pipeline stages

**Key Sections:**
- Component score functions
- Truth polarity detection logic
- GENIUS LAW thresholds
- Neutrality buffer fix

---

### 6. L4-Jailbreak-Anti-Hantu-Defense.md

**Covers:**
- Anti-Hantu F9 Law (Malay jailbreak detection)
- 50+ forbidden patterns across 4 tiers
- AmanahDetector class (RED/ORANGE/GREEN risk levels)
- Pattern categories (soul claims, reciprocal biology, biological states)
- Integration points in pipeline (000_VOID, 666_BRIDGE, 888_JUDGE)
- v36.2 PHOENIX expansion
- Red-team validation results (97% safety)

**Key Sections:**
- Pattern lists (Malay/English)
- Amanah RED/ORANGE patterns
- AntiHantuView class
- Pipeline integration stages

---

### 7. Phase-4-Integration-Status-v38.md

**Covers:**
- Implementation status (✅ IMPLEMENTED vs ❌ TODO)
- 7 CLI tools from pyproject.toml
- Integration modules (pipeline, SEA-LION)
- v38.2 time governance (entropy rot, SUNSET)
- zkPC runtime (v0.1 stub)
- Future roadmap (v39-v42)
- Test coverage (1624+ tests)

**Key Sections:**
- Component status table
- CLI tool entry points
- check_entropy_rot() function
- execute_sunset() function
- Future phase gates

---

## Usage

These documents are designed for:

1. **Onboarding:** New contributors understanding arifOS architecture
2. **Auditing:** Security/compliance reviews requiring detailed spec
3. **Integration:** External systems interfacing with arifOS
4. **Academic:** Research papers citing arifOS implementation
5. **Archival:** Historical record of v38.2 state

---

## Important Notes

### What These Documents ARE:
- ✅ Extraction from existing code, specs, and README
- ✅ Exact quotes of class names, function signatures, constants
- ✅ Accurate references to file paths and modules
- ✅ Clear marking of TODO/STUB features

### What These Documents ARE NOT:
- ❌ Proposals for new features
- ❌ Modifications to existing law or floors
- ❌ Paraphrased or summarized code (exact names used)
- ❌ Marketing material or promotional content

---

## Cross-References

### Source Code
- `arifos_core/` — Core implementation
- `arifos_core/memory/` — Memory bands and policy
- `arifos_core/waw/` — W@W Federation organs
- `arifos_core/eye/` — @EYE Sentinel views
- `arifos_core/floor_detectors/` — Floor detectors

### Specs
- `spec/constitutional_floors_v38Omega.json` — Floor thresholds
- `spec/genius_law_v38Omega.json` — GENIUS LAW spec
- `spec/cooling_ledger.schema.json` — Ledger schema
- `spec/arifos_v38_2.yaml` — v38.2 hardening spec
- `spec/pipeline_v38Omega.yaml` — Pipeline spec

### Canon
- `canon/01_CONSTITUTIONAL_FLOORS_v38Omega.md` — Floor law
- `canon/02_GENIUS_LAW_v38Omega.md` — GENIUS LAW law
- `canon/05_COOLING_LEDGER_PHOENIX_v38Omega.md` — Phoenix-72
- `canon/00_ARIFOS_MASTER_v38Omega.md` — Master index

### Docs
- `docs/MEMORY_ARCHITECTURE.md` — Memory system design
- `docs/FUTURE_PATH_v38_v42.md` — Roadmap v38→v42
- `README.md` — Main README with quick start

---

## Maintenance

**Update Frequency:** These documents are a **snapshot** of v38.2. They should be updated when:
1. Major version bump (v39, v40, etc.)
2. Breaking changes to APIs or schemas
3. New floors or verdict types added
4. Significant architectural changes

**Update Process:**
1. Extract from code/specs (do not invent)
2. Quote exact names and paths
3. Mark new TODO/STUB items clearly
4. Update cross-references

---

## Verification

To verify accuracy of these documents:

```bash
# Check file paths exist
ls -la arifos_core/pipeline.py
ls -la arifos_core/APEX_PRIME.py
ls -la arifos_core/memory/bands.py

# Check CLI tools work
arifos-verify-ledger
arifos-compute-merkle

# Run tests
pytest tests/test_floors_v35.py -v
pytest tests/test_genius_metrics.py -v
pytest tests/integration/test_memory_floor_integration.py -v
```

---

**Version:** v38.2  
**Created:** 2025-12-13  
**Status:** SEALED (archival snapshot)

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
