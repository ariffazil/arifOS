# arifOS Core — The Constitutional Kernel

**Authority:** Track B (Constitutional Law)
**Version:** v51 PRODUCTION
**Motto:** *DITEMPA BUKAN DIBERI* — Forged, Not Given

---

## 🧬 What is `arifos.core`?

The `arifos.core` package is the **Pure Logic Kernel** of arifOS.
It is the thermodynamic engine that converts raw LLM probability into **governed, auditable truth**.

It is **Headless** — it does not know about MCP, HTTP, or Discord.
It only speaks Python. The Application Layer (`AAA_MCP`) imports *us*.

---

## 🏛️ The Trinity Architecture (ΔΩΨ)

The Core is organized around the **Constitutional Trinity** — three irreducible engines that must agree for a verdict to SEAL.

```
┌─────────────────────────────────────────────────────────────────┐
│                         arifOS Core                             │
│                                                                 │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│   │   Mind (Δ)  │   │  Heart (Ω)  │   │  Soul (Ψ)   │          │
│   │   AGI       │   │   ASI       │   │   APEX      │          │
│   │ ─────────── │   │ ─────────── │   │ ─────────── │          │
│   │ • Sense     │   │ • Empathize │   │ • Judge     │          │
│   │ • Reason    │   │ • Align     │   │ • Proof     │          │
│   │ • Contrast  │   │ • Witness   │   │ • Seal      │          │
│   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘          │
│          │                 │                 │                 │
│          └─────────────────┴─────────────────┘                 │
│                           │                                    │
│                    ┌──────▼──────┐                             │
│                    │ Metabolizer │                             │
│                    │ (000 → 999) │                             │
│                    └──────┬──────┘                             │
│                           │                                    │
│                    ┌──────▼──────┐                             │
│                    │   Verdict   │                             │
│                    │ SEAL | VOID │                             │
│                    └─────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

| Engine | Symbol | Role | Stages |
|--------|--------|------|--------|
| **AGI** | Δ (Delta) | The Mind — Cold Logic | 111 SENSE, 222 REFLECT, 333 REASON |
| **ASI** | Ω (Omega) | The Heart — Warm Empathy | 444 EVIDENCE, 555 EMPATHIZE, 666 ALIGN |
| **APEX** | Ψ (Psi) | The Soul — Final Judgment | 777 FORGE, 888 JUDGE, 889 PROOF, 999 SEAL |

---

## 📂 Folder Map

| Folder | Purpose | Key Files |
|--------|---------|-----------|
| `engines/` | The Trinity Engines | `agi_engine.py`, `asi_engine.py`, `apex_engine.py` |
| `metabolism/` | The Pipeline Stages (000-999) | `000_void/`, `111_sense/`, ... `889_proof/` |
| `system/` | Orchestration & Hypervisor | `apex_prime.py`, `system_coordinator.py`, `hypervisor.py` |
| `enforcement/` | Constitutional Law & Guards | `metrics.py`, `floor_validators.py`, `guards/` |
| `memory/` | State, Ledger, Vault | `ledger/`, `vault/`, `cooling_ledger.py` |
| `spec/` | Schema Validators | `manifest_verifier.py`, `schema_validator.py` |
| `utils/` | Utilities | `telemetry.py`, `entropy.py`, `eye_sentinel.py` |
| `integration/` | API & Server Wiring | `servers/`, `api/`, `waw/` |

---

## 🔥 The Metabolizer (Pipeline Flow)

The `Metabolizer` class (`metabolizer.py`) is the **State Machine** that drives execution.
It enforces **sequential progression** through 11 stages:

```
000 VOID ──▶ 111 SENSE ──▶ 222 REFLECT ──▶ 333 REASON
    │                                          │
    │ (if high-stakes, Class B)                ▼
    │                                   444 EVIDENCE
    │                                          │
    │                                          ▼
    │                                   555 EMPATHIZE
    │                                          │
    │                                          ▼
    │                                   666 ALIGN
    │                                          │
    └──────────────────────────────────────────▼
                                         777 FORGE
                                               │
                                               ▼
                                         888 JUDGE
                                               │
                                               ▼
                                         889 PROOF
                                               │
                                               ▼
                                         999 SEAL ──▶ (Ledger Commit)
```

### Stage Execution

Each stage folder (e.g., `metabolism/111_sense/`) contains a `stage.py` with an `execute_stage(context) -> context` function.
The Metabolizer dynamically imports and executes these:

```python
# metabolizer.py (simplified)
STAGE_MODULES = {
    0:   "arifos.core.metabolism.000_void.stage",
    111: "arifos.core.metabolism.111_sense.stage",
    # ...
    999: "arifos.core.metabolism.999_seal.stage",
}

def _execute_stage(self, stage: int):
    module = importlib.import_module(STAGE_MODULES[stage])
    self.context = module.execute_stage(self.context)
```

---

## ⚖️ Constitutional Floors (F1-F13)

Every output must pass **all floors** (AND logic). Failure on any floor -> VOID.

| Floor | Symbol | Threshold | Type |
|-------|--------|-----------|------|
| **F1** | Amanah | Boolean | Hard (Kill-Switch) |
| **F2** | Truth (Δ) | ≥ 0.99 | Hard |
| **F3** | Tri-Witness | ≥ 0.95 | Hard |
| **F4** | Clarity (ΔS) | ≥ 0 | Hard |
| **F5** | Peace² | ≥ 1.0 | Soft |
| **F6** | Empathy (κᵣ) | ≥ 0.95 | Soft |
| **F7** | Humility (Ω₀) | [0.03, 0.05] | Hard |
| **F8** | Genius (G) | ≥ 0.80 | Derived |
| **F9** | C_dark | < 0.30 | Derived |
| **F10** | Ontology | Boolean | Hard |
| **F11** | CommandAuth | Boolean | Hard |
| **F12** | InjectionDefense | ≥ 0.85 | Hard |
| **F13** | Curiosity | ≥ 0.85 | Soft |

### The Ψ Formula (Life Force Index)

```
Ψ = (ΔS × Peace² × κᵣ × RASA × Amanah) / (Entropy + Shadow + ε)
```

- **Numerator**: Clarity, Peace, Empathy, Listening, Trust.
- **Denominator**: Confusion, Hidden Intent.
- **Threshold**: Ψ ≥ 1.0 → SEAL.

---

## 🔌 Usage (For App Developers)

**Rule:** `AAA_MCP` imports `core`. Core does NOT import `AAA_MCP`.

```python
from arifos.core.engines.agi_engine import AGIEngine
from arifos.core.metabolizer import Metabolizer
from arifos.core import apex_review, Metrics

# 1. Direct Engine Call (Low Level)
mind = AGIEngine()
result = mind.sense("What is 2+2?")

# 2. Metabolizer Pipeline (Full Flow)
m = Metabolizer()
m.initialize({"query": "Should I invest in Bitcoin?", "user_id": "u1"})
m.transition_to(111)  # SENSE
m.transition_to(222)  # REFLECT
# ... continue through 999

# 3. APEX Review (High Level)
verdict = apex_review(task="Hello world", context={})
print(verdict.verdict)  # SEAL, VOID, SABAR, PARTIAL
```

---

## 🧪 Verification

```bash
# Smoke check imports
python -c "import arifos.core"
python -c "from arifos.core.metabolizer import Metabolizer"
python -c "from arifos.core.engines import AGIEngine, ASIEngine, APEXEngine"

# Run tests
pytest tests/core/ -v
```

---

## 📚 References

| Document | Location |
|----------|----------|
| **Full Canon** | `000_THEORY/` |
| **Physics Codex** | `docs/PHYSICS_CODEX.md` |
| **Constitutional Floors** | `000_THEORY/canon/00_FLOORS.md` |
| **GENIUS LAW** | `000_THEORY/canon/08_genius/GENIUS_LAW.md` |
| **APEX PRIME** | `arifos/core/system/apex_prime.py` |

---

**DITEMPA BUKAN DIBERI.**
