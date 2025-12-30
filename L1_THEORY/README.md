# L1_THEORY — Constitutional Law (v45.0)

**Layer:** L1 (Constitutional Foundation)
**Purpose:** Immutable law governing all higher layers
**License:** CC-BY-4.0 (APEX Theory & constitutional text only; runtime enforcement governed separately)

---

## What Lives Here

| Directory | Contents |
|-----------|----------|
| `canon/` | Constitutional law (v45.0) — Track A authority |
| `papers/` | Academic publications (archived; non-binding, non-runtime) |
| `research/` | Research artifacts (archived to `archive/research_subsurface/`) |

---

## Quick Start

**New to arifOS canon?** Start here:

1. **Master Index:** [canon/_INDEX/00_MASTER_INDEX_v45.md](canon/_INDEX/00_MASTER_INDEX_v45.md)
2. **Architecture Map:** [canon/00_foundation/000_ARCHITECTURE_MAP_v45.md](canon/00_foundation/000_ARCHITECTURE_MAP_v45.md)
3. **Nine Floors:** [canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md](canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md)
4. **000→999 Pipeline:** [canon/03_runtime/010_PIPELINE_000TO999_v45.md](canon/03_runtime/010_PIPELINE_000TO999_v45.md)

---

## Dependency Rules

```
L1_THEORY (Constitutional Law)
    ↑
    ├─ Track B (spec/v45/) — Operational thresholds
    ├─ Track C (arifos_core/) — Runtime implementation
    └─ All higher layers depend on this foundation

L1 NEVER imports from higher layers (read-only at runtime)
```

**This layer is READ-ONLY at runtime.** Changes require Phoenix-72 amendment process.

---

## Amendment Process

**Phoenix-72 Protocol** (72-hour constitutional cooling):

1. Proposal enters PHOENIX memory band
2. Tri-Witness review (Human-AI-Earth consensus ≥ 0.95)
3. 72-hour cooling period
4. If approved → SEALED to VAULT (immutable)
5. If rejected → VOID (quarantine)

**No AI may self-seal canon.** Humans seal law; AI proposes amendments.

See [canon/05_memory/010_COOLING_LEDGER_PHOENIX_v45.md](canon/05_memory/010_COOLING_LEDGER_PHOENIX_v45.md)

---

## Track A-B-C System

| Track | Location | Purpose | Mutability |
|-------|----------|---------|------------|
| **Track A (Law)** | `L1_THEORY/canon/` | WHY things must be (constitutional theory) | Immutable (Phoenix-72 only) |
| **Track B (Spec)** | `spec/v45/*.json` | WHAT thresholds are (operational tunables) | Medium (manifest-locked) |
| **Track C (Runtime)** | `arifos_core/*.py` | HOW it runs (Python implementation) | High (daily development) |

**Binding Contract:**
- Track C MUST implement Track A laws using Track B thresholds
- Track B CANNOT violate Track A physics
- Track A CANNOT specify implementation details

See [canon/03_runtime/030_SPEC_CODE_BINDING_v45.md](canon/03_runtime/030_SPEC_CODE_BINDING_v45.md)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **v45.0** | 2025-12-29 | Phoenix-72 consolidation: 49→40 files, 100% v45 consistency |
| **v45.0Ω** | 2025-12-30 | Entropy reduction (maintenance): 38→36 files (2 archived), 1 relocated — no law change |
| v44.0 | 2025-12-21 | Session physics layer, TEARFRAME v44 |
| v42.0 | 2024-12-17 | Thermodynamic epoch, ΔΩΨ foundations |

---

**DITEMPA BUKAN DIBERI** — Forged, not given. Truth must cool before it rules.
