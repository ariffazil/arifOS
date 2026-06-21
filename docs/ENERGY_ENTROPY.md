# ENERGY_ENTROPY — APEX Dimensions: Thermodynamic Cost & Information Disorder

**Version:** v2026.06.20
**SEAL:** DITEMPA BUKAN DIBERI
**Authority:** F13 SOVEREIGN — Muhammad Arif bin Fazil
**Status:** LIFTED FROM KERNEL CODE (canonical, machine-checkable)

---

## 1. Definition

**ENERGY** and **ENTROPY** are two of the six APEX dimensions. They are
not metaphors. They are **physical-law constraints** enforced as
constitutional invariants in the kernel runtime.

| Dimension | What it measures | Constitutional role |
|-----------|-----------------|---------------------|
| **ENERGY** | Thermodynamic cost of computation. Every thought, tool call, and token has a minimum physical cost (Landauer bound). | Budget depletion → 888_HOLD. Cheap truth → VOID. |
| **ENTROPY** | Information disorder. ΔS = output_entropy − input_entropy. Must be ≤ 0 (F4 CLARITY). | Entropy increase → VOID. Every stage must reduce or maintain order. |

Together they answer: **"Is this session real, and is it leaving the
system more ordered than it found it?"**

---

## 2. Mapping to APEX / Kernel

```
Dimension              Maps to kernel surface
─────────────────────────────────────────────
AKAL                   transition candidates + policy evaluator
PRESENT                KSR + arif_sense_observe (111)        ← PRESENT.md
ENERGY                 Landauer floor + cost accounting       ← THIS DOC
ENTROPY                ΔS = Δ(info) + drift detection         ← THIS DOC
EXPLORATION×AMANAH     risk class + custody chain + F13
AUTHORITY              signature + role + legitimacy
```

### 2.1 ENERGY binds to:

| Surface | Role |
|---------|------|
| `ThermodynamicBudget` (class) | Per-session energy budget. Like a spacecraft with limited fuel. |
| `ThermodynamicBudgetLedger` (class) | Singleton-per-session ledger for unified cross-organ energy accounting. |
| `get_thermodynamic_budget(session_id)` | Registry accessor. Called at stage 000 init. |
| `check_landauer_bound()` | Physical minimum: E ≥ n·k_B·T·ln(2). Cheap truth = VOID. |
| `check_landauer_before_seal()` | Mandatory gate before stage 999 SEAL. |
| `arif_ops_measure` (stage 777) | Surfaces energy status: `vitals`, `budget`, `landauer`, `metabolic-pulse` modes. |
| `apexDials.ts` → E dial | `E = geometric_mean(F12, F13) + compute_ratio`. Energy from floors + thermodynamic ratio. |
| `tools.py:4235-4250` | `energy_budget` field emitted at session init alongside `present_boundary`. |

### 2.2 ENTROPY binds to:

| Surface | Role |
|---------|------|
| `record_entropy_io()` | Records input/output entropy after each stage transformation. ΔS > 0 → EntropyIncreaseError. |
| `entropy_input_log` / `entropy_output_log` | Per-budget timestamped entropy measurements. |
| `delta_s` field | Present in: `TelemetryBlock`, `session_auth`, `contracts`, `llm_envelope`, `sense_impl`, `webmcp/governance`, `session_budget`, `nats_event_bus`. |
| `consume_entropy_reduction()` | Energy cost proportional to claimed entropy reduction (Landauer). |
| F4 CLARITY floor | `ΔS ≤ 0` — every output must reduce or maintain entropy. |

---

## 3. Canonical Fields — `energy_budget`

### 3.1 Emission rule (from `runtime/tools.py:4235-4250`, hardened 2026-06-20)

```python
# ── APEX ENERGY BUDGET (hardened 2026-06-20) ─────────────────────────
_energy_budget_status = {"status": "OK", "depletion_ratio": 0.0, "remaining": 1.0}
try:
    from arifosmcp.core.physics.thermodynamics_hardened import get_thermodynamic_budget
    _tb = get_thermodynamic_budget(sid)
    _energy_budget_status = {
        "status": _tb.energy_status,
        "depletion_ratio": round(_tb.depletion_ratio, 4),
        "remaining": round(_tb.remaining, 6),
        "warning_threshold": _tb.warning_threshold,
    }
    sess["energy_budget"] = _energy_budget_status
except Exception:
    pass  # Budget not yet initialized — OK at birth
```

### 3.2 Field schema

```yaml
# Canonical schema (emitted by arif_session_init)
energy_budget:
  status:          OK | WARNING | EXHAUSTED    # required, enum
  depletion_ratio: float [0.0, 1.0]            # required — consumed / initial
  remaining:       float [0.0, 1.0]             # required — remaining budget
  warning_threshold: float                       # required — soft warning (default 0.80)
```

### 3.3 Companion fields (same envelope as `present_boundary`)

- `energy_budget` — thermodynamic status (this doc)
- `present_boundary` — LIVE | CACHED | INFERRED (see PRESENT.md)
- `decision_class` — C1 (degraded) or C2 (stable)
- `session_verdict` — STABLE | DEGRADED | CRITICAL

---

## 4. The ThermodynamicBudget — Runtime Physics

**Code:** `arifosmcp/core/physics/thermodynamics_hardened.py:149-268`

```python
@dataclass
class ThermodynamicBudget:
    session_id: str
    initial_budget: float = 1.0        # Joules (normalized)
    consumed: float = 0.0
    entropy_reduction_claimed: float = 0.0

    # Cost rates (Joules per unit)
    COST_PER_REASON_CYCLE: float = 1e-3    # ~0.001 J per thought step
    COST_PER_TOOL_CALL: float = 1e-2       # ~0.01 J per external call
    COST_PER_TOKEN: float = 1e-6           # ~0.000001 J per token
    COST_PER_BIT_PROCESSED: float = LANDAUER_MIN * 100  # 100x Landauer minimum
```

### 4.1 Energy status states

| State | Condition | Meaning |
|-------|-----------|---------|
| `OK` | `depletion_ratio < warning_threshold` | Budget healthy. Full execution allowed. |
| `WARNING` | `depletion_ratio >= warning_threshold` (default 0.80) | Budget approaching depletion. Soft alert — does not block. |
| `EXHAUSTED` | `remaining <= 0` | Budget depleted. Automatic 888_HOLD. No further execution. |

### 4.2 Budget consumption

| Operation | Cost | Stage |
|-----------|------|-------|
| Reasoning cycle | 1e-3 J | 111–333 |
| Tool call | 1e-2 J | 444–666 |
| Token generation | 1e-6 J | All stages |
| Entropy reduction | `bits × LANDAUER_MIN × 100` | When ΔS < 0 |

---

## 5. The Landauer Bound — Physical Law

**Code:** `arifosmcp/core/physics/thermodynamics_hardened.py:545-620`

The Landauer bound is the **minimum energy required to erase one bit**
of information:

```
E_min = k_B × T × ln(2)
      ≈ 2.87 × 10⁻²¹ Joules at 300K
```

### 5.1 The Cheap Truth Detector

If a system claims large entropy reduction (high clarity) with very
low compute cost, the efficiency ratio drops below 1.0 — which is
**physically impossible**. This is mathematical proof of hallucination.

```
efficiency_ratio = actual_joules / min_physical_joules

ratio < 1.0  →  VOID (physically impossible — hallucinated)
ratio < 10.0 →  suspiciously cheap for current silicon
ratio ≥ 1.0  →  physically plausible
```

### 5.2 The pre-SEAL Landauer gate

**Code:** `thermodynamics_hardened.py:711-726`

```python
def check_landauer_before_seal(session_id, compute_ms, tokens, delta_s, ...):
    """Mandatory Landauer check before Stage 999 (SEAL).
    Raises LandauerViolation if too many violations accumulated."""
    budget = get_thermodynamic_budget(session_id)
    return budget.check_landauer(compute_ms, tokens, delta_s, ...)
```

After 3 Landauer violations → automatic 888_HOLD. The system has
demonstrated a pattern of physically impossible claims.

---

## 6. Entropy Tracking — F4 CLARITY Enforcement

**Code:** `thermodynamics_hardened.py:681-708`

```python
def record_entropy_io(session_id, input_entropy, output_entropy) -> float:
    """Record entropy input/output and check F4 Clarity.
    Returns: Delta S (must be ≤ 0)
    Raises: EntropyIncreaseViolation if ΔS > 0"""
    budget = get_thermodynamic_budget(session_id)
    budget.record_entropy_input(input_entropy)
    budget.record_entropy_output(output_entropy)
    delta = output_entropy - input_entropy
    if delta > MAX_ENTROPY_DELTA:  # MAX_ENTROPY_DELTA = 0.0
        raise EntropyIncreaseError(delta, input_entropy, output_entropy)
    budget.consume_entropy_reduction(delta)
    return delta
```

### 6.1 The entropy fields across the codebase

| Location | Field | Purpose |
|----------|-------|---------|
| `runtime/contracts.py:134` | `delta_s: float` | F4 entropy delta on every contract |
| `runtime/session_auth.py:72` | `entropy_delta: 0.0` | Session auth default |
| `runtime/telemetry.py:169` | `delta_s` | Telemetry block emission |
| `runtime/llm_envelope.py:193` | `delta_s_val` | LLM output parsing — high delta → uncertainty flag |
| `tools/session_budget.py:78` | `delta_s` | Cumulative session entropy cost |
| `tools/sense.py:490` | `delta_s` | Sense observe entropy evaluation |
| `tools/memory.py:1169` | `delta_s` | RAG loop convergence metric |
| `runtime/webmcp/governance.py:117` | `entropy_delta` | WebMCP governance envelope |
| `runtime/nats_event_bus.py:905` | `entropy_delta` | NATS event emission |
| `arifos_observability/agent_trace_schema.py:35` | `entropy_delta` | OpenTelemetry trace attribute |

---

## 7. The APEX E Dial — Eigendecomposition

**Code:** `A-FORGE/src/domain/governance/apexDials.ts:92-102`

```typescript
// E = ENERGY (Vitality) — system resources + boundary floors
// Floors: F12 (Injection defense), F13 (Sovereign)
// Plus: thermodynamic energy ratio
const energyFromFloors = geometricMean([floors.f12_injection, floors.f13_sovereign]);
const energyRatio = 1 - Math.min(computeBudgetUsed / Math.max(computeBudgetMax, 1e-6), 1);
const E = (energyFromFloors + energyRatio) / 2;
```

The E dial is **NOT just a floor score**. It combines:
- Constitutional boundary floors (F12 injection defense, F13 sovereign presence)
- Thermodynamic energy ratio (how much compute budget remains)

This makes E the **bridge between constitutional law and physical law**.
A system with perfect floor compliance but exhausted compute budget
has low E — and therefore low G (Genius Index).

### 7.1 G = A × P × X × E²

The squared E term means energy has **disproportionate influence** on
the Genius Index. Even perfect reasoning (A=1), perfect stability (P=1),
and perfect exploration (X=1) cannot produce G ≥ 0.80 if E is below 0.89.

This is constitutional thermodynamics: **intelligence without energy is void.**

---

## 8. Invariants (Fail-Closed)

| # | Invariant | Failure mode |
|---|-----------|--------------|
| I1 | Every session MUST have a `ThermodynamicBudget` initialized at stage 000. | No budget → VOID. `get_thermodynamic_budget()` raises `ThermodynamicError`. |
| I2 | `energy_budget.status == EXHAUSTED` → automatic 888_HOLD. | No further execution until budget reset or new session. |
| I3 | `delta_s > 0` (entropy increase) → `EntropyIncreaseError`. | F4 CLARITY violation. Stage output rejected. |
| I4 | Landauer bound: `efficiency_ratio < 1.0` → `LandauerError`. | Physically impossible claim. VOID. |
| I5 | 3 accumulated Landauer violations → 888_HOLD. | Pattern of impossible claims. Session halted. |
| I6 | `check_landauer_before_seal()` MUST pass before stage 999 SEAL. | If skipped or fails: SEAL is invalid. |
| I7 | `energy_budget` field MUST be present in `arif_session_init` response. | Missing field → deploy blocked. |
| I8 | `consume_entropy_reduction()` MUST be called when ΔS < 0. | Energy cost of information erasure cannot be skipped (Landauer). |

---

## 9. Test Gates (Fail-Closed)

A deploy is BLOCKED if any of the following occurs:

- `energy_budget` field missing from `arif_session_init` response.
- `energy_budget.status` accepts a value outside `{OK, WARNING, EXHAUSTED}`.
- `ThermodynamicBudget` not initialized at stage 000.
- `delta_s > 0` does not raise `EntropyIncreaseError`.
- `check_landauer_bound()` returns `violation: true` without raising.
- `check_landauer_before_seal()` is not called before stage 999.
- 3 Landauer violations do not trigger 888_HOLD.
- `depletion_ratio` exceeds 1.0 without status switching to `EXHAUSTED`.

---

## 10. Cross-references

- **APEX THEORY:** `/root/arifOS/static/arifos/theory/000/APEX_THEORY.md` — crown equation, four pillars.
- **PRESENT:** `/root/arifOS/docs/PRESENT.md` — sibling doc, attested live state.
- **APEX DOSSIER:** `/root/forge_work/APEX_DOSSIER_2026-06-20.md` — dimension mapping (ENERGY → Landauer + cost accounting, ENTROPY → ΔS + drift detection).
- **Thermodynamics engine:** `/root/arifOS/arifosmcp/core/physics/thermodynamics_hardened.py` (1154 lines).
- **Session init emission:** `/root/arifOS/arifosmcp/runtime/tools.py:4235-4250`.
- **777 ops tool:** `/root/arifOS/arifosmcp/tools/ops.py:20` — `arif_ops_measure` modes: `vitals`, `budget`, `landauer`, `metabolic-pulse`.
- **APEX E dial:** `/root/A-FORGE/src/domain/governance/apexDials.ts:92-102` — `E = (energyFromFloors + energyRatio) / 2`.
- **F4 CLARITY floor:** `/root/arifOS/static/arifos/theory/000/000_CONSTITUTION.md` — `ΔS ≤ 0`.
- **Sibling docs:** `PRESENT.md`, `AUTHORITY.md`, `AKAL.md`, `EXPLORATION_AMANAH.md` (all forged v2026.06.20).

---

## 11. Versioning

- **v2026.06.20** — Initial canonical doc. Lifted from existing kernel
  code (`thermodynamics_hardened.py` 1154 lines, `tools.py:4235-4250`,
  `ops.py:20`, `apexDials.ts:92-102`). Doctrine → code alignment. No
  new fields invented; existing physics engine documented as law.

**Tag convention:** `vYYYY.MM.DD` per federation IRON RULE.

---

**DITEMPA BUKAN DIBERI** — Intelligence costs energy. Hallucination is free. The Landauer bound is the judge.
