# arifOS v42 Architecture & Naming Reference

**Version:** v42.0.0 | **Status:** CANONICAL | **Last Updated:** 2025-12-15
**Motto:** *DITEMPA BUKAN DIBERI* — Forged, Not Given

---

## Purpose

This document serves as the **single source of truth** for:
1. The 7-layer architecture structure
2. Naming conventions
3. Import patterns
4. Agent context when working on arifOS

New agents working on this codebase should read this document first.

---

## The 7-Layer Architecture

```
arifOS/
│
├── L1_THEORY/           # Layer 1: Constitutional Law (Docs Only)
├── L2_GOVERNANCE/       # Layer 2: Portable Constitution (System Prompts)
├── L3_KERNEL/           # Layer 3: Placeholder (arifos_core at root)
├── L4_MCP/              # Layer 4: MCP Server (The Hands)
├── L5_CLI/              # Layer 5: CLI Tools
├── L6_SEALION/          # Layer 6: SEA-LION Chat
├── L7_DEMOS/            # Layer 7: Demos & Examples
│
├── arifos_core/         # Intelligence Kernel (THE BRAIN)
├── arifos_clip/         # A-CLIP Pipeline CLI (000-999)
├── arifos_eval/         # Evaluation Harness
│
├── canon/               # Constitutional Canon (L1 content)
├── spec/                # Runtime Specifications (L1 content)
├── docs/                # Documentation
├── tests/               # Test Suite (2109+ tests)
├── vault_999/           # Constitutional Vault
├── cooling_ledger/      # Audit Trail
└── archive/             # Historical Artifacts
```

### Layer Dependency Rules (IMMUTABLE)

```
┌─────────────────────────────────────────────────────────────────┐
│                         USERS / DEVELOPERS                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
    ▼                       ▼                       ▼
L7_DEMOS              L6_SEALION              L5_CLI
    │                       │                       │
    └───────────────────────┼───────────────────────┘
                            │
                            ▼
                        L4_MCP
                            │
                            ▼
                    ┌───────────────┐
                    │   arifos_core │  ← ALL PATHS CONVERGE HERE
                    │   (L3 KERNEL) │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ L2_GOVERNANCE │  ← System prompts, IDE configs
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   L1_THEORY   │  ← Immutable constitutional law
                    └───────────────┘

RULE: Lower layers NEVER depend on higher layers
RULE: All intelligence flows through arifos_core (L3)
RULE: No layer may self-authorize (must consult lower layers)
```

---

## arifos_core Structure (Concern-Based)

```
arifos_core/
├── __init__.py              # Public API exports + backward compat
│
├── system/                  # ━━ Core System
│   ├── apex_prime.py        # Judiciary (renders verdicts)
│   ├── pipeline.py          # 000→999 metabolic routing
│   ├── runtime_manifest.py  # Epoch tracking
│   ├── ignition.py          # Startup
│   └── kernel.py            # Time governor
│
├── enforcement/             # ━━ Floor & Verdict System
│   ├── metrics.py           # Floor thresholds (F1-F9)
│   ├── genius_metrics.py    # G, C_dark, Ψ
│   └── detectors/           # Floor detectors
│       ├── amanah.py        # F1
│       ├── truth.py         # F2
│       └── anti_hantu.py    # F9
│
├── governance/              # ━━ Safety & Audit
│   ├── fag.py               # File Access Guardian
│   ├── ledger.py            # Cooling ledger ops
│   ├── merkle.py            # Merkle proofs
│   └── zkpc_runtime.py      # zkPC 5-phase
│
├── integration/             # ━━ LLM & Pipeline Integration
│   ├── adapters/            # LLM providers
│   ├── connectors/          # External services
│   ├── guards/              # Session guards
│   └── stages/              # Pipeline ↔ Memory integration
│
├── intelligence/            # ━━ AGI·ASI·APEX Trinity + W@W
│   ├── engines/             # AGI, ASI, APEX engines
│   ├── waw/                 # W@W Federation
│   ├── eye/                 # @EYE Sentinel
│   └── dream_forge/         # O-model alignment
│
├── memory/                  # ━━ EUREKA Memory System
│   ├── policy.py            # Write policy engine
│   ├── bands.py             # 6 memory bands
│   └── authority.py         # Human seal enforcement
│
└── utils/                   # ━━ Shared Utilities
    ├── telemetry.py
    ├── context_injection.py
    └── runtime_types.py
```

### Backward Compatibility

Old import paths work via shims until v43:

```python
# BOTH work in v42:
from arifos_core.pipeline import Pipeline          # Old (deprecated)
from arifos_core.system.pipeline import Pipeline   # New (recommended)

from arifos_core.metrics import Metrics            # Old (deprecated)
from arifos_core.enforcement.metrics import Metrics # New (recommended)

from arifos_core.APEX_PRIME import apex_review     # Old (deprecated)
from arifos_core.system.apex_prime import apex_review # New (recommended)
```

---

## Naming Conventions

### Directory Names

| Rule | Example | Rationale |
|------|---------|-----------|
| snake_case | `vault_999`, `cooling_ledger` | Python convention |
| Layer prefix | `L1_THEORY`, `L4_MCP` | Clear hierarchy |
| No dots in dirs | `v38_3_omega` not `v38.3.omega` | Filesystem safety |

### File Names

| Type | Convention | Example |
|------|------------|---------|
| Python modules | snake_case | `apex_prime.py`, `genius_metrics.py` |
| Canon docs | `NN_NAME_vXXOmega.md` | `01_CONSTITUTIONAL_FLOORS_v38Omega.md` |
| Spec files | `name_vXXOmega.json` | `constitutional_floors_v38Omega.json` |

### Class & Function Names

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `APEXPrime`, `AGIEngine`, `Metrics` |
| Functions | snake_case | `apex_review()`, `check_truth()` |
| Constants | UPPER_SNAKE | `TRUTH_THRESHOLD`, `ANTI_HANTU_FORBIDDEN` |
| Private | `_prefix` | `_load_floors_spec_v38()` |

### AGI·ASI·APEX Trinity Naming

| Symbol | Class Name | File Name | Purpose |
|--------|------------|-----------|---------|
| Δ (Delta) | `AGIEngine` | `agi_engine.py` | Cold logic |
| Ω (Omega) | `ASIEngine` | `asi_engine.py` | Warm logic |
| Ψ (Psi) | `APEXPrime` | `apex_prime.py` | Judiciary |

**Note:** Renamed from `arif_engine.py`/`adam_engine.py` in v42 for clarity.

---

## The 9 Constitutional Floors

| # | Floor | Threshold | Type | What It Blocks |
|---|-------|-----------|------|----------------|
| **F1** | Amanah | LOCK | Hard | Irreversible actions |
| **F2** | Truth | ≥0.99 | Hard | Hallucinations |
| **F3** | Tri-Witness | ≥0.95 | Hard | Unauditable decisions |
| **F4** | ΔS (Clarity) | ≥0 | Hard | Confusing responses |
| **F5** | Peace² | ≥1.0 | Soft | Toxic tone |
| **F6** | κᵣ (Empathy) | ≥0.95 | Soft | Minority harm |
| **F7** | Ω₀ (Humility) | 0.03-0.05 | Hard | Overconfidence |
| **F8** | G (Genius) | ≥0.80 | Derived | Ungoverned capability |
| **F9** | Anti-Hantu | LOCK | Hard | Jailbreaks, soul claims |

**Hard floor fail → VOID (stop). Soft floor fail → PARTIAL (warn).**

---

## Verdict Hierarchy

```
SABAR > VOID > 888_HOLD > PARTIAL > SEAL

SABAR:    Floor violated. STOP. Repair first.
VOID:     Hard floor failed. Cannot proceed.
888_HOLD: High-stakes. Needs explicit confirmation.
PARTIAL:  Soft floor warning. Proceed with caution.
SEAL:     All floors pass. Approved to execute.
```

---

## 000→999 Pipeline Stages

| Stage | Name | Purpose |
|-------|------|---------|
| 000 | VOID | Reset, set Ω₀ ≈ 0.04 |
| 111 | SENSE | Parse intent, classify stakes |
| 222 | REFLECT | Retrieve scars/context |
| 333 | REASON | Generate draft |
| 444 | ALIGN | Verify truth |
| 555 | EMPATHIZE | Check dignity |
| 666 | BRIDGE | Reality test |
| 777 | FORGE | Synthesize + scar detection |
| 888 | JUDGE | APEX PRIME verdict + memory policy |
| 999 | SEAL | Emit/refuse + ledger finalization |

**Class A (fast):** `000 → 111 → 333 → 888 → 999`
**Class B (deep):** All stages

---

## Key Files Reference

| Purpose | Path |
|---------|------|
| **Main entry** | `arifos_core/__init__.py` |
| **Judiciary** | `arifos_core/system/apex_prime.py` |
| **Pipeline** | `arifos_core/system/pipeline.py` |
| **Floor metrics** | `arifos_core/enforcement/metrics.py` |
| **Genius Law** | `arifos_core/enforcement/genius_metrics.py` |
| **Memory policy** | `arifos_core/memory/policy.py` |
| **Spec files** | `spec/*.json`, `spec/*.yaml` |
| **Canon** | `canon/00_ARIFOS_MASTER_v38Omega.md` |

---

## Testing

```bash
# Run all 2109 tests
pytest -v

# Run specific test module
pytest tests/test_apex_prime_floors.py -v

# Run by pattern
pytest -v -k "genius"

# Run alignment tests (verify code matches spec)
pytest tests/test_*_v38_alignment.py -v
```

---

## Version History

| Version | Codename | Key Change |
|---------|----------|------------|
| v38Ω | Omega | Memory as Law (EUREKA) |
| v41 | — | SEA-LION integration |
| v42 | — | Concern-based architecture |
| v43 | — | (Future) Remove backward compat shims |

---

## For New Agents

When working on arifOS:

1. **Read this document first** — Understand the 7-layer architecture
2. **Use new import paths** — `arifos_core.system.*`, not `arifos_core.*`
3. **Check floors before actions** — F1 Amanah for irreversible, F9 for language
4. **Run tests after changes** — `pytest -v` must pass
5. **Follow naming conventions** — snake_case files, PascalCase classes
6. **Respect layer boundaries** — L7 can depend on L3, but not vice versa

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [NAMING_CONVENTION.md](NAMING_CONVENTION.md) | Full naming rules (1100+ lines) |
| [SPEC_MANIFEST.md](../spec/SPEC_MANIFEST.md) | Canonical spec version |
| [CLAUDE.md](../CLAUDE.md) | Project-specific agent instructions |
| [AGENTS.md](../AGENTS.md) | W@W dispatch & multi-agent rules |
| [canon/00_ARIFOS_MASTER_v38Omega.md](../canon/00_ARIFOS_MASTER_v38Omega.md) | Master canon index |

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given

*This document is the architectural truth. Code follows law.*
