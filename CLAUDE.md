# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Extends:** [AGENTS.md](AGENTS.md) — All floors, W@W dispatch, and guardrails from AGENTS.md apply here.

---

## Build & Test Commands

```bash
# Install (editable with dev dependencies)
pip install -e .[dev]

# Run all tests
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
```

---

## Architecture Overview

arifOS is a constitutional governance kernel that wraps LLMs and enforces outputs through thermodynamic floors.

### Core Flow
```
User Input → 000-999 Pipeline → 9 Floors Check → APEX PRIME Verdict → Output
                                      ↓
                              Cooling Ledger (audit trail)
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `arifos_core/APEX_PRIME.py` | Judiciary engine — computes verdicts (SEAL/PARTIAL/VOID/888_HOLD/SABAR) |
| `arifos_core/pipeline.py` | 000→999 metabolic pipeline with Class A/B routing |
| `arifos_core/metrics.py` | Floor thresholds and `Metrics` dataclass |
| `arifos_core/genius_metrics.py` | GENIUS LAW (G, C_dark, Ψ) + Truth Polarity |
| `arifos_core/floor_detectors/` | Python-sovereign enforcement (Amanah, Anti-Hantu) |
| `arifos_core/eye/` | @EYE Sentinel multi-view governance (10+ views) |
| `arifos_core/waw/` | W@W Federation organs (@WELL, @RIF, @WEALTH, @GEOX, @PROMPT) |
| `arifos_core/memory/cooling_ledger.py` | Immutable audit trail logging |
| `arifos_core/zkpc_runtime.py` | zkPC 5-phase runtime for cryptographic integrity |
| `integrations/sealion/` | SEA-LION model integration |

### 000-999 Pipeline Stages

| Stage | Name | What Happens |
|-------|------|--------------|
| 000 | VOID | Reset assumptions, set Ω₀ = 0.04 |
| 111 | SENSE | Parse intent, classify stakes (Class A/B) |
| 222 | REFLECT | Retrieve scars/context (Class B only) |
| 333 | REASON | Generate draft response |
| 444 | ALIGN | Verify truth, cross-check facts |
| 555 | EMPATHIZE | Check for blame language, dignity |
| 666 | BRIDGE | Reality test (physical action detection) |
| 777 | FORGE | Synthesize final response |
| 888 | JUDGE | APEX PRIME floor check — veto point |
| 999 | SEAL | Emit or refuse based on verdict |

**Class A (fast):** 000 → 111 → 333 → 888 → 999
**Class B (deep):** Full pipeline through all stages

### AAA Trinity

| Engine | Symbol | Role |
|--------|--------|------|
| ARIF AGI | Δ | Cold logic — sense, reason, align |
| ADAM ASI | Ω | Warm logic — empathize, bridge, dignity |
| APEX PRIME | Ψ | Judiciary — final verdict |

---

## Nine Constitutional Floors

| # | Floor | Threshold | Type | Quick Check |
|---|-------|-----------|------|-------------|
| F1 | Amanah | LOCK | Hard | Reversible? Within mandate? |
| F2 | Truth | ≥0.99 | Hard | Factually accurate? |
| F3 | Tri-Witness | ≥0.95 | Hard | Human-AI-Earth consensus? |
| F4 | ΔS (Clarity) | ≥0 | Hard | Reduces confusion? |
| F5 | Peace² | ≥1.0 | Soft | Non-destructive? |
| F6 | κᵣ (Empathy) | ≥0.95 | Soft | Serves weakest stakeholder? |
| F7 | Ω₀ (Humility) | 0.03-0.05 | Hard | States uncertainty? |
| F8 | G (Genius) | ≥0.80 | Derived | Governed intelligence? |
| F9 | C_dark | <0.30 | Derived | Dark cleverness contained? |

**Hard floor fail → VOID (stop). Soft floor fail → PARTIAL (warn).**

---

## Code Style

- Python 3.8+, type hints required
- 4-space indentation for Python, 2-space for YAML
- Import order: stdlib → third-party → arifos_core
- Docstrings: Google style
- Line length: 100 chars (black/ruff configured)

---

## Git Workflow

- Commit format: `feat|fix|docs|test(scope): message`
- Never push directly; draft commands for human review
- All changes must be reversible via `git revert`

---

## Slash Commands

Located in `.claude/commands/`:

| Command        | Purpose                                      |
|----------------|----------------------------------------------|
| /000           | v36.3O session start / reboot (INIT)         |
| /111–/777      | Pipeline stage helpers (view/explain stages) |
| /888           | High-stakes hold                             |
| /999           | v36.3O session end / handoff (CLOSE)         |
| /g             | GENIUS LAW metrics                           |
| /s             | SABAR protocol                               |
| /f             | Floor status                                 |
| /pol           | Truth Polarity check                         |

---

## Python-Sovereign Enforcement

Two floors are enforced directly in Python (code overrides LLM self-assessment):

1. **AmanahDetector** (`arifos_core/floor_detectors/amanah_risk_detectors.py`)
   - Detects irreversible/destructive actions (rm -rf, DROP TABLE, credential leaks)

2. **AntiHantuDetector** (`arifos_core/eye/anti_hantu_view.py`)
   - 50+ forbidden patterns across 4 tiers (Malay/English)
   - Blocks claims of feelings, consciousness, soul

---

## Deeper Tiers (Load on-demand)

- [.claude/TEARFRAME.md](.claude/TEARFRAME.md) — Full 000→777 pipeline + GENIUS LAW definitions
- [.claude/SECURITY.md](.claude/SECURITY.md) — Security lifecycle + deny patterns
- [.claude/CONSTITUTION.md](.claude/CONSTITUTION.md) — Full ΔΩΨ physics + GENIUS LAW details

---

## Verdict Hierarchy

```
SABAR > VOID > 888_HOLD > PARTIAL > SEAL
```

**Python decides. Claude proposes.**

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.

---

**Version:** v36.3Ω (LAW+SPEC, runtime v35Ω) | **Tests:** 752+ passing
