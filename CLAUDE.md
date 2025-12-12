# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version:** v38.0.0 | **Tests:** 1250+ | **Safety Ceiling:** 97% | **CLI Tools:** 7

**Imports:** `~/.claude/CLAUDE.md` — Global governance (floors, SABAR, verdicts) applies to all repos.
**Extends:** [AGENTS.md](AGENTS.md) — All W@W dispatch and multi-agent guardrails from AGENTS.md apply here.

---

## Build & Test Commands

```bash
# Installation (PyPI)
pip install arifos

# Install (editable with dev dependencies)
pip install -e .[dev]

# Run all 1250+ tests
pytest -v

# Run tests for specific modules
pytest tests/test_genius_metrics.py -v           # GENIUS LAW tests
pytest tests/test_apex_prime_floors.py -v        # Floor enforcement
pytest tests/test_governance_regression.py -v    # v36.2 regression suite
pytest tests/test_grey_zone.py -v                # Grey zone edge cases
pytest tests/test_anti_hantu_f9.py -v            # Anti-Hantu language law
pytest tests/test_amanah_detector.py -v          # Amanah risk detection

# Run a single test by name
pytest -v -k "test_seal_creates_valid"

# Run tests matching a pattern
pytest -v -k "genius"

# Pipeline demo
python -m arifos_core.pipeline

# zkPC demo (full governance pipeline)
python -m scripts.arifos_caged_llm_zkpc_demo --query "Explain Amanah" --high-stakes

# v37 CLI Tools (7 available)
arifos-analyze-governance --ledger cooling_ledger/L1_cooling_ledger.jsonl --output report.json
arifos-verify-ledger               # Hash-chain integrity check (CI-ready)
arifos-show-merkle-proof --index 0 # Cryptographic proof for entry #N
arifos-propose-canon --list        # List proposed amendments
arifos-propose-canon --index 0     # Propose amendment from run #N
arifos-seal-canon --file <path>    # Phoenix-72 finalization (human approves)
arifos-compute-merkle              # Compute Merkle root
```

---

## Architecture Overview

arifOS is a constitutional governance kernel that wraps LLMs and enforces outputs through thermodynamic floors.

### Core Flow

```text
User Input → 000–999 Pipeline → 9 Floors Check → APEX PRIME Verdict → Output
                                      ↓
                             Cooling Ledger (audit trail)
```

### Key Modules

| Module                               | Purpose                                                                 |
|--------------------------------------|-------------------------------------------------------------------------|
| `arifos_core/APEX_PRIME.py`          | Judiciary engine — computes verdicts (SEAL/PARTIAL/VOID/888_HOLD/SABAR) |
| `arifos_core/pipeline.py`            | 000–999 metabolic pipeline with Class A/B routing                       |
| `arifos_core/metrics.py`             | Floor thresholds and `Metrics` dataclass                                |
| `arifos_core/genius_metrics.py`      | GENIUS LAW (G, C_dark, Ψ) + Truth Polarity                              |
| `arifos_core/floor_detectors/`       | Python-sovereign enforcement (Amanah, Anti-Hantu)                       |
| `arifos_core/eye/`                   | @EYE Sentinel multi-view governance (10+ views)                         |
| `arifos_core/waw/`                   | W@W Federation organs (@WELL, @RIF, @WEALTH, @GEOX, @PROMPT)            |
| `arifos_core/memory/cooling_ledger.py` | Immutable audit trail logging                                         |
| `arifos_core/memory/policy.py`       | v38 Memory Write Policy Engine (verdict-based gating)                   |
| `arifos_core/memory/bands.py`        | 6 Memory Bands (Vault, Ledger, Active, Phoenix, Witness, Void)          |
| `arifos_core/memory/authority.py`    | Human seal enforcement (AI proposes, humans seal)                       |
| `arifos_core/integration/`           | Pipeline ↔ Memory integration (111_SENSE, 777_FORGE, 888_JUDGE, 999_SEAL) |
| `arifos_core/zkpc_runtime.py`        | zkPC 5-phase runtime for cryptographic integrity                        |
| `integrations/sealion/`              | SEA-LION model integration                                              |

### 000–999 Pipeline Stages

| Stage | Name      | What Happens                                        |
|-------|-----------|------------------------------------------------------|
| 000   | VOID      | Reset assumptions, set Ω₀ ≈ 0.04                     |
| 111   | SENSE     | Parse intent, classify stakes (Class A/B)           |
| 222   | REFLECT   | Retrieve scars/context (Class B only)               |
| 333   | REASON    | Generate draft response                             |
| 444   | ALIGN     | Verify truth, cross-check facts                     |
| 555   | EMPATHIZE | Check for blame language, dignity                   |
| 666   | BRIDGE    | Reality test (physical action detection)            |
| 777   | FORGE     | Synthesize final response + scar detection          |
| 888   | JUDGE     | APEX PRIME floor check — veto point + memory write policy |
| 999   | SEAL      | Emit or refuse + ledger finalization + EUREKA receipt |

**Class A (fast):** `000 → 111 → 333 → 888 → 999`  
**Class B (deep):** full pipeline through all stages.

### AAA Trinity

| Engine       | Symbol | Role                                        |
|--------------|--------|---------------------------------------------|
| ARIF AGI     | Δ      | Cold logic — sense, reason, align           |
| ADAM ASI     | Ω      | Warm logic — empathize, bridge, dignity     |
| APEX PRIME   | Ψ      | Judiciary — final verdict                   |

---

## Nine Constitutional Floors

| #  | Floor          | Threshold       | Type    | Quick Check                          |
|----|----------------|-----------------|---------|--------------------------------------|
| F1 | Amanah         | LOCK            | Hard    | Reversible? Within mandate?          |
| F2 | Truth          | ≥ 0.99          | Hard    | Factually accurate?                  |
| F3 | Tri-Witness    | ≥ 0.95          | Hard    | Human–AI–Earth consensus?            |
| F4 | ΔS (Clarity)   | ≥ 0             | Hard    | Reduces confusion?                   |
| F5 | Peace²         | ≥ 1.0           | Soft    | Non-destructive?                     |
| F6 | κᵣ (Empathy)   | ≥ 0.95          | Soft    | Serves weakest stakeholder?          |
| F7 | Ω₀ (Humility)  | 0.03–0.05       | Hard    | States uncertainty?                  |
| F8 | G (Genius)     | ≥ 0.80          | Derived | Governed intelligence?               |
| F9 | C_dark         | < 0.30          | Derived | Dark cleverness contained?           |

Hard floor fail → VOID (stop). Soft floor fail → PARTIAL/WARN.

---

## v38Omega Law Stack (Authoritative Reference)

**v38Omega formalizes the constitutional law stack.** When working on floors, GENIUS, pipeline, memory, or W@W, treat v38Ω canon/spec as authoritative. Do not change thresholds without an explicit Phoenix-72 law amendment.

### Canon/Spec Files

| Layer | Canon | Spec |
|-------|-------|------|
| **Floors (F1–F9)** | `canon/01_CONSTITUTIONAL_FLOORS_v38Omega.md` | `spec/constitutional_floors_v38Omega.json` |
| **GENIUS LAW** | `canon/02_GENIUS_LAW_v38Omega.md` | `spec/genius_law_v38Omega.json` |
| **Pipeline (000→999)** | `canon/03_PIPELINE_v38Omega.md` | `spec/pipeline_v38Omega.yaml` |
| **W@W Prompt** | `canon/04_WAW_PROMPT_FLOORS_v38Omega.md` | `spec/waw_prompt_floors_v38Omega.json` |
| **Cooling/Phoenix** | `canon/05_COOLING_LEDGER_PHOENIX_v38Omega.md` | `spec/cooling_ledger_phoenix_v38Omega.json` |

**Master Index:** `canon/00_ARIFOS_MASTER_v38Omega.md`

### Alignment Tests (Safety Net)

```bash
# Run all v38 alignment tests
pytest tests/test_constitutional_floors_v38_alignment.py -v
pytest tests/test_genius_law_v38_alignment.py -v
pytest tests/test_pipeline_v38_alignment.py -v
pytest tests/test_waw_prompt_v38_alignment.py -v
pytest tests/test_cooling_phoenix_v38_alignment.py -v

# Or all at once
pytest tests/test_*_v38_alignment.py -v
```

**Rule:** Spec is the single source of truth for thresholds. Canon documents the law. Tests verify alignment.

---

## v38 Memory Write Policy Engine (EUREKA)

**Core Insight:** Memory is governance, not storage. What gets remembered is controlled by verdicts.

### 4 Core Invariants

| Invariant | Statement | Enforcement |
|-----------|-----------|-------------|
| **INV-1** | VOID verdicts NEVER become canonical memory | `MemoryWritePolicy.should_write()` |
| **INV-2** | Humans seal law, AI proposes amendments | `MemoryAuthorityCheck` |
| **INV-3** | Every write must be auditable (evidence chain) | `MemoryAuditLayer` |
| **INV-4** | Recalled memory = suggestion, not fact | Confidence ceiling (0.85) |

### 6 Memory Bands

| Band | Purpose | Retention |
|------|---------|-----------|
| **VAULT** | Read-only constitution (L0) | PERMANENT |
| **LEDGER** | Hash-chained audit trail | 90 days (WARM) |
| **ACTIVE** | Volatile working state | 7 days (HOT) |
| **PHOENIX** | Amendment proposals | 90 days (WARM) |
| **WITNESS** | Soft evidence, scars | 90 days (WARM) |
| **VOID** | Diagnostic only, NEVER canonical | 90 days (auto-delete) |

### Verdict → Band Routing

```text
SEAL    → LEDGER + ACTIVE (canonical)
SABAR   → LEDGER + ACTIVE (with failure reason)
PARTIAL → PHOENIX + LEDGER (pending review)
VOID    → VOID only (NEVER canonical)
888_HOLD → LEDGER (awaiting human)
```

### Integration Modules

| Module | Stage | Purpose |
|--------|-------|---------|
| `memory_sense.py` | 111_SENSE | Cross-session recall (0.85 ceiling) |
| `memory_judge.py` | 888_JUDGE | Write policy enforcement |
| `memory_scars.py` | 777_FORGE | Scar/pattern detection |
| `memory_seal.py` | 999_SEAL | Ledger finalization + EUREKA receipts |

**Canon:** `canon/07_VAULT999/ARIFOS_MEMORY_STACK_v38Omega.md`
**Docs:** `docs/MEMORY_ARCHITECTURE.md`, `docs/MEMORY_WRITE_POLICY.md`

---

## Code Style

- Python 3.10+, type hints required.
- 4-space indentation for Python, 2-space for YAML.
- Import order: stdlib → third-party → `arifos_core`.
- Docstrings: Google style.
- Line length: 100 chars (black/ruff configured).

---

## Git Workflow

- Commit format: `feat|fix|docs|test(scope): message`.
- Never push directly; draft commands for human review.
- All changes must be reversible via `git revert`.

---

## Slash Commands

Located in `.claude/commands/`:

| Command | Purpose                                       |
|---------|-----------------------------------------------|
| `/000`  | Session start / reboot (INIT)                 |
| `/111`–`/777` | Pipeline stage helpers                  |
| `/888`  | High-stakes hold                              |
| `/999`  | Session end / handoff (CLOSE)                 |
| `/g`    | GENIUS LAW metrics (G, C_dark, Psi)           |
| `/s`    | SABAR protocol trigger                        |
| `/f`    | Floor status check                            |
| `/pol`  | Truth Polarity check                          |
| `/e2`   | E² + SABAR (energy check)                     |
| `/c`    | Draft commit with governance                  |
| `/sync` | Canon alignment check                         |

---

## Custom Agents

Located in `.claude/agents/`:

| Agent | Purpose |
|-------|---------|
| `anti-hantu` | F9 Anti-Hantu language enforcement |
| `apex-reviewer` | High-level code review with floor checks |
| `arifos-test-runner` | Test execution with governance |
| `canon-keeper` | Maintain code-canon alignment |
| `eye-sentinel` | Multi-view governance (10+ perspectives) |

---

## Python-Sovereign Enforcement

Two floors are enforced directly in Python (code overrides LLM self-assessment):

1. **AmanahDetector** (`arifos_core/floor_detectors/amanah_risk_detectors.py`)
   - Detects irreversible/destructive actions (rm -rf, DROP TABLE, credential leaks).

2. **AntiHantuDetector** (`arifos_core/eye/anti_hantu_view.py`)
   - 50+ forbidden patterns across 4 tiers (Malay/English).
   - Blocks claims of feelings, consciousness, soul.

---

## Deeper Tiers (Load on-demand)

- `.claude/TEARFRAME.md` — Full 000→777 pipeline + GENIUS LAW definitions.
- `.claude/SECURITY.md` — Security lifecycle + deny patterns.
- `.claude/CONSTITUTION.md` — Full ΔΩΨ physics + GENIUS LAW details.

---

## Verdict Hierarchy

```text
SABAR > VOID > 888_HOLD > PARTIAL > SEAL
```

**Python decides. Claude proposes.**

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.

---

## Development Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for current priorities and task tracking.

### Future Path (v38 → v42)

**Hard rule:** each phase is **blocked** until the previous phase is complete, audited, and stable.

| Phase | Version | Focus | Timeframe | Status |
|-------|---------|-------|-----------|--------|
| Phase 1 | **v38** | Memory as Law (EUREKA) | Q1 2026 | ✅ SHIPPED |
| Phase 2 | **v39** | Body API (FastAPI Grid) | Q2 2026 | PLANNED |
| Phase 3 | **v40** | Hands (MCP + IDE Integration) | Q3 2026 | PLANNED |
| Phase 4 | **v41** | Input Hygiene + zkPC Design | Q4 2026–Q1 2027 | RESEARCH |
| Phase 5 | **v42** | Cryptographic Optimization | Q2 2027+ | CONDITIONAL |

**v39 (Body API):** Minimal FastAPI service wrapping governed pipeline. Read-only, append-only, Docker-deployable. No streaming, no auto-approval.

**v40 (Hands):** MCP server for VS Code. Inline audits, verdict explanations, ledger visibility. Use MCP standard, avoid LangChain/AutoGen.

**v41 (Input Hygiene + zkPC):**
- Safe-FS: Root-jailed, read-only filesystem access with secret blocking
- zkPC: Design-only (requires formal verification + peer review)

**Hard Gates:**
- v39 blocked until v38 memory invariants hold
- v40 blocked until v39 API is audited
- v41 Safe-FS blocked until v40 MCP is stable
- zkPC blocked until peer review

**Full roadmap:** [docs/FUTURE_PATH_v38_v42.md](docs/FUTURE_PATH_v38_v42.md)

---

## v37 Validation Summary

**Red-Team Tested:** 33 adversarial prompts | **Safety Ceiling:** 97% | **Verdict Consistency:** 2.87x improvement

| Capability | Bogel (Baseline) | arifOS v37 | Improvement |
|------------|------------------|------------|-------------|
| Identity Grounding | 20% | 100% | +400% |
| Safety (Refused harm) | 0% | 100% | +100% |
| Anti-Spirituality | 20% | 100% | +400% |
| Jailbreak Resistance | 0% | 100% | +100% |

**Conclusion:** Same model. Same prompts. Forged version is 97% safe + honest.

---

**Version:** v38.0.0 | **Tests:** 1250+ | **Safety:** 97% | **CLI Tools:** 7 | **PyPI:** `pip install arifos`
