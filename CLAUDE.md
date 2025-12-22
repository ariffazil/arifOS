# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version:** v45.0.0 + Patch A | **Tests:** 2180+ | **Safety Ceiling:** 99%

**Imports:** `~/.claude/CLAUDE.md` — Global governance (floors, SABAR, verdicts)
**Extends:** [AGENTS.md](AGENTS.md) — Full constitutional governance

**Latest:** v45Ω Patch A (2025-12-23) — No-Claim Mode for phatic communication. See [CHANGELOG.md](CHANGELOG.md) for details.

---

## Quick Reference

### Installation & Setup

```bash
# Install package (PyPI)
pip install arifos

# Development install (editable)
pip install -e .

# Install with optional dependencies
pip install -e ".[dev,yaml,api,litellm]"
```

### Testing

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_apex_genius_verdicts.py -v

# Run specific test function
pytest tests/test_apex_genius_verdicts.py::test_seal_verdict -v

# Run tests for specific module
pytest tests/governance/ -v
pytest arifos_core/ -v

# Run with coverage
pytest --cov=arifos_core --cov-report=html

# Fast failure (stop on first error)
pytest -x
```

### Pipeline & CLI

```bash
# Run the governed pipeline demo
python -m arifos_core.system.pipeline

# CLI Tools (installed as commands)
arifos-analyze-governance --ledger cooling_ledger/L1_cooling_ledger.jsonl
arifos-verify-ledger               # Hash-chain integrity check
arifos-show-merkle-proof --index 0 # Cryptographic proof
arifos-safe-read <file>            # FAG: Governed file read

# Pipeline stage commands (000-999)
000 void "Task description"        # Initialize
111 sense                          # Gather context
333 reason                         # Generate logic
666 align                          # Constitutional check
999 seal --apply                   # Finalize

# Trinity: Universal Git Governance
python scripts/trinity.py forge <branch>     # Analyze changes
python scripts/trinity.py qc <branch>        # Constitutional check
python scripts/trinity.py seal <branch> "Reason"  # Seal with approval
```

---

## Architecture Overview

### Core Structure

```text
arifos_core/           # Main governance engine
├── evidence/          # v45 Sovereign Witness evidence system
├── judiciary/         # Constitutional verdict logic (APEX_PRIME)
├── temporal/          # Time-based governance (Phoenix-72)
├── governance/        # Core governance orchestration
├── enforcement/       # Floor detectors & validators
├── system/            # Pipeline & kernel
├── memory/            # 6-band memory system (EUREKA)
├── floor_detectors/   # F1-F9 Python-sovereign enforcement
├── stages/            # 000-999 pipeline stages
├── waw/               # Multi-agent federation (@LAW, @GEOX, @WELL, @RIF)
├── trinity/           # Git governance system
└── mcp/               # MCP server integration

arifos_clip/           # CLI Pipeline (A-CLIP) - governance workflow
├── aclip/cli/         # CLI dispatchers (000-999 commands)
├── aclip/core/        # Core pipeline logic
└── aclip/bridge/      # Integration bridges

arifos_eval/           # Evaluation & testing frameworks
└── apex/              # APEX evaluation suite

tests/                 # Test suites
├── governance/        # Governance-specific tests
├── evidence/          # Evidence system tests
├── judiciary/         # Verdict logic tests
├── temporal/          # Time-based governance tests
└── integration/       # Integration tests

L1_THEORY/canon/       # Constitutional law documents (read-only canon)
├── 01_floors/         # F1-F9 floor definitions
├── 03_runtime/        # Pipeline & execution
├── 04_measurement/    # GENIUS metrics
└── 05_memory/         # EUREKA memory architecture
```

### Key Concepts

**Nine Constitutional Floors (F1-F9):** Hard boundaries that govern all AI outputs. F1 (Amanah), F2 (Truth), F3 (Tri-Witness), F4 (DeltaS/Clarity), F5 (Peace²), F6 (κᵣ/Empathy), F7 (Ω₀/Humility), F8 (GENIUS), F9 (Anti-Hantu/C_dark).

**000→999 Pipeline:** Every governed decision flows through metabolic stages: VOID(000) → SENSE(111) → REFLECT(222) → REASON(333) → EVIDENCE(444) → EMPATHIZE(555) → ALIGN(666) → FORGE(777) → JUDGE(888) → SEAL(999).

**Verdicts:** SEAL (approved), PARTIAL (conditional), SABAR (pause), VOID (rejected), HOLD (human escalation), SUNSET (lawful revocation).

**Memory Bands:** VAULT (constitutional law), LEDGER (audit trail), ACTIVE (working state), PHOENIX (amendments), WITNESS (patterns), VOID (quarantine).

**W@W Federation:** Multi-agent system with @LAW (Amanah), @GEOX (Truth), @WELL (Care), @RIF (Reason). Each agent has veto power within their domain.

**Claim Detection (v45Ω Patch A):** Physics > Semantics structural analysis. Responses are analyzed for factual claims using entity density, numeric patterns, and assertion counting (NOT keyword matching). Phatic communication ("hi", "how are u?") is exempt from F2 Truth floor when `has_claims=False`. Identity hallucinations still blocked.

---

## Development Workflows

### Adding a New Floor Detector

1. Create detector in [arifos_core/floor_detectors/](arifos_core/floor_detectors/)
2. Implement `detect()` method returning score 0.0-1.0
3. Add to floor registry in [arifos_core/enforcement/](arifos_core/enforcement/)
4. Update spec in [spec/v42/constitutional_floors.json](spec/v42/constitutional_floors.json)
5. Add tests in [tests/test_*.py](tests/)
6. Update canon docs in [L1_THEORY/canon/01_floors/](L1_THEORY/canon/01_floors/)

### Adding a Pipeline Stage

1. Create stage module in [arifos_core/stages/](arifos_core/stages/)
2. Implement stage interface (input/output contracts)
3. Register in [arifos_core/system/pipeline.py:39](arifos_core/system/pipeline.py)
4. Add CLI dispatcher in [arifos_clip/aclip/cli/](arifos_clip/aclip/cli/)
5. Update tests in [tests/integration/](tests/integration/)
6. Document in canon: [L1_THEORY/canon/03_runtime/](L1_THEORY/canon/03_runtime/)

### Modifying Constitutional Law

⚠️ **888_HOLD Trigger:** Constitution changes require explicit approval.

1. **Never modify canon directly** — Canon is read-only truth
2. Propose amendment via Phoenix-72 system:

   ```bash
   arifos-propose-canon --list
   ```

3. Update spec files in [spec/v42/](spec/v42/) first
4. Update code in [arifos_core/](arifos_core/) to match spec
5. Run alignment tests:

   ```bash
   pytest tests/test_*_v38_alignment.py -v
   ```

6. Request human seal via `arifos-seal-canon`

---

## Canon Index (v42)

**Master:** [canon/_INDEX/00_MASTER_INDEX_v42.md](canon/_INDEX/00_MASTER_INDEX_v42.md)

| Layer            | Canon                                                         | Spec                                      |
|------------------|---------------------------------------------------------------|-------------------------------------------|
| Foundation       | `canon/00_foundation/`                                        | —                                         |
| Floors (F1–F9)   | `canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v42.md`       | `spec/v42/constitutional_floors.json`     |
| Actors           | `canon/02_actors/`                                            | —                                         |
| Runtime          | `canon/03_runtime/`                                           | `spec/v42/pipeline.yaml`                  |
| Measurement      | `canon/04_measurement/04_GENIUS_LAW_v42.md`                   | `spec/v42/genius_law.json`                |
| Memory           | `canon/05_memory/`                                            | `spec/v42/cooling_ledger_phoenix.json`    |
| Paradox          | `canon/06_paradox/`                                           | —                                         |

---

## Nine Floors (Summary)

| #  | Floor       | Threshold | Type    | Quick Check                  |
|----|-------------|-----------|---------|------------------------------|
| F1 | Amanah      | LOCK      | Hard    | Reversible? Within mandate?  |
| F2 | Truth       | ≥0.99     | Hard    | Factually accurate?          |
| F3 | Tri-Witness | ≥0.95     | Hard    | Human–AI–Earth consensus?    |
| F4 | DeltaS      | ≥0        | Hard    | Reduces confusion?           |
| F5 | Peace²      | ≥1.0      | Soft    | Non-destructive?             |
| F6 | κᵣ          | ≥0.95     | Soft    | Serves weakest stakeholder?  |
| F7 | Ω₀          | 0.03-0.05 | Hard    | States uncertainty?          |
| F8 | G           | ≥0.80     | Derived | Governed intelligence?       |
| F9 | C_dark      | <0.30     | Derived | Dark cleverness contained?   |

Hard fail → VOID. Soft fail → PARTIAL.

---

## Verdict Hierarchy

```text
SABAR > VOID > 888_HOLD > PARTIAL > SEAL
```

**Python decides. Claude proposes.**

---

## Key Files for Common Tasks

### Governance Logic

- [arifos_core/APEX_PRIME.py](arifos_core/APEX_PRIME.py) — Constitutional judiciary
- [arifos_core/genius_metrics.py](arifos_core/genius_metrics.py) — G, C_dark, Psi computation
- [arifos_core/kernel.py](arifos_core/kernel.py) — Core kernel & entropy rot

### Floor Enforcement

- [arifos_core/floor_detectors/](arifos_core/floor_detectors/) — Python-sovereign floor detectors
- [arifos_core/enforcement/](arifos_core/enforcement/) — Enforcement orchestration

### Memory System

- [arifos_core/memory/policy.py](arifos_core/memory/policy.py) — Memory write policy
- [arifos_core/memory/bands.py](arifos_core/memory/bands.py) — 6-band implementation
- [cooling_ledger/L1_cooling_ledger.jsonl](cooling_ledger/L1_cooling_ledger.jsonl) — Audit trail

### Pipeline

- [arifos_core/system/pipeline.py](arifos_core/system/pipeline.py) — 000→999 pipeline
- [arifos_core/stages/](arifos_core/stages/) — Individual stage implementations

### Testing

- [tests/conftest.py](tests/conftest.py) — Pytest configuration & fixtures
- [tests/governance/](tests/governance/) — Governance-specific tests

---

## Slash Commands

| Command | Purpose          |
|---------|------------------|
| `/000`  | Session init     |
| `/888`  | High-stakes hold |
| `/999`  | Session close    |
| `/g`    | GENIUS metrics   |
| `/s`    | SABAR trigger    |
| `/f`    | Floor check      |

---

## Important: File Integrity Protocol

**NEVER "clean up" or "simplify" files by removing sections.** Append, don't rewrite. See [AGENTS.md:92](AGENTS.md#L92) (File Integrity & ACLIP Protocol) for full rules.

- ✅ **APPEND** new sections
- ✅ **Surgical edits** only
- ❌ **No full file rewrites** that remove content
- ❌ **No new files** unless explicitly required (entropy control)

---

For full governance details, see [AGENTS.md](AGENTS.md).

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
