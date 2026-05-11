# APEX Metrics Hardening Implementation Plan

## Status

- Status: implemented on 2026-03-08
- Verdict: SEAL CANDIDATE
- Outcome:
  - `arifosmcp/intelligence/core/thermo_budget.py` now emits the expanded APEX runtime schema and caps entropy removal to the available entropy baseline
  - `arifosmcp/sites/apex-dashboard/index.html` now posts `SystemCall` payloads for live polling, normalizes bridge/runtime payloads, and renders canonical fields (`G_dagger`, `eta`, `C`)
  - `tests/aclip_cai/test_thermo.py` includes regression coverage for the entropy-baseline cap
  - `docs/CHANGELOG.md`, `docs/00_META/CHANGELOG.md`, and `DEPLOY.md` were updated to reflect the March 8 hardening and deployment/runtime split
- Verification:
  - `pytest tests/aclip_cai/test_thermo.py -q`
  - `pytest tests/core/test_outputs.py -q`

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extend `ThermoSnapshot` and `ThermoBudget` with APEX metrics (effort, token_cost, A, P, X, η, G*, G†) without creating new files — only harden existing code.

**Architecture:** Add 8 new fields to `ThermoSnapshot` dataclass; extend `ThermoBudget.open_session()` and `record_step()` to track effort accumulation and token cost; update `thermo_estimator.py` to surface token count in its return dict so callers can feed it back. All backward-compat — existing fields untouched.

**Tech Stack:** Python 3.11+, stdlib `dataclasses`, existing arifOS kernel singleton pattern.

**Constraint:** No new .py files. Only modify:
- `arifosmcp/intelligence/core/thermo_budget.py`
- `arifosmcp/intelligence/tools/thermo_estimator.py`

---

## Variable mapping

| G† term | Field name | Semantic |
|---|---|---|
| A (architecture) | `architecture` | Static model quality index, set at session open |
| P (parameters) | `parameters` | Normalized param count, static per model |
| X (data quality) | `data_quality` | Context/RAG quality, updated per session |
| E (effort) | `effort` | Accumulates per step (+1.0 base, +0.5 per tool call) |
| ΔS (entropy reduction) | derived from `delta_s` | `abs(min(0, delta_s))` — magnitude of negative entropy delta |
| C (token cost) | `token_cost` | Cumulative tokens across session |
| η = ΔS/C | `eta` | Computed: `abs(min(0, delta_s)) / token_cost` |
| G* = A·P·X·E² | `G_star` | Capacity × effort |
| G† = G*·η | `G_dagger` | Full governed intelligence score |

**Note on ΔS sign:** existing `delta_s` is ≤ 0 for "clarity gain". For η we need positive entropy *reduction*, so: `delta_S_reduction = abs(min(0.0, delta_s))`.

---

## Task 1: Extend `ThermoSnapshot` dataclass

**File:** `arifosmcp/intelligence/core/thermo_budget.py:29-65`

**Step 1: Add 8 new fields after `genius_pass`**

In the `ThermoSnapshot` dataclass, after line 40 (`genius_pass: bool`), add:

```python
    # --- APEX Metrics (G† = A·P·X·E²·ΔS/C) ---
    effort: float = 0.0        # E: accumulated tool calls + reasoning steps
    token_cost: int = 0        # C: cumulative tokens this session
    architecture: float = 1.0  # A: static model quality index
    parameters: float = 1.0    # P: normalized param count
    data_quality: float = 0.95 # X: context/data quality ∈ [0,1]
    eta: float = 0.0           # η = |ΔS| / C  (insight per token)
    G_star: float = 0.0        # A·P·X·E²
    G_dagger: float = 0.0      # G* · η  (governed intelligence score)
    G_dagger_pass: bool = False # G† ≥ 0.80
```

**Step 2: Update `ThermoSnapshot.compute()` signature**

Replace the current `compute()` classmethod signature (lines 42-52) to add the new parameters:

```python
    @classmethod
    def compute(
        cls,
        session_id: str,
        delta_s: float = 0.0,
        peace2: float = 1.0,
        omega0: float = 0.04,
        akal: float = 0.95,
        exploration: float = 0.90,
        energy: float = 0.92,
        # APEX parameters
        effort: float = 0.0,
        token_cost: int = 0,
        architecture: float = 1.0,
        parameters: float = 1.0,
        data_quality: float = 0.95,
    ) -> ThermoSnapshot:
```

**Step 3: Update `ThermoSnapshot.compute()` body**

Replace the current body (lines 53-65) with:

```python
        genius = akal * peace2 * exploration * (energy ** 2)
        # ΔS is reduction: magnitude of negative delta_s (clarity gain)
        delta_s_reduction = abs(min(0.0, delta_s))
        eta = delta_s_reduction / token_cost if token_cost > 0 else 0.0
        G_star = architecture * parameters * data_quality * (effort ** 2)
        G_dagger = G_star * eta
        return cls(
            session_id=session_id,
            timestamp=datetime.now(tz=timezone.utc).isoformat(),
            delta_s=delta_s,
            peace2=peace2,
            omega0=omega0,
            akal=akal,
            exploration=exploration,
            energy=energy,
            genius=genius,
            genius_pass=genius >= 0.80,
            effort=effort,
            token_cost=token_cost,
            architecture=architecture,
            parameters=parameters,
            data_quality=data_quality,
            eta=round(eta, 6),
            G_star=round(G_star, 6),
            G_dagger=round(G_dagger, 6),
            G_dagger_pass=G_dagger >= 0.80,
        )
```

---

## Task 2: Update `ThermoBudget` constants and `open_session()`

**File:** `arifosmcp/intelligence/core/thermo_budget.py:85-112`

**Step 1: Add G† threshold constant** after `DELTA_S_TARGET = 0.00`:

```python
    G_DAGGER_THRESHOLD = 0.80  # G† ≥ 0.80 required
```

**Step 2: Update `open_session()` signature** to accept A, P, X:

```python
    def open_session(
        self,
        session_id: str,
        initial_akal: float = 0.98,
        initial_energy: float = 0.95,
        initial_exploration: float = 0.95,
        # APEX static factors
        architecture: float = 1.0,
        parameters: float = 1.0,
        data_quality: float = 0.95,
    ) -> None:
        """Register a new session with default thermodynamic state."""
        self._sessions[session_id] = {
            "delta_s": 0.0,
            "peace2": 1.0,
            "omega0": 0.04,
            "akal": initial_akal,
            "exploration": initial_exploration,
            "energy": initial_energy,
            "step_count": 0,
            "history": [],
            # APEX
            "effort": 0.0,
            "token_cost": 0,
            "architecture": architecture,
            "parameters": parameters,
            "data_quality": data_quality,
        }
```

---

## Task 3: Update `record_step()` to accumulate effort and token_cost

**File:** `arifosmcp/intelligence/core/thermo_budget.py:114-162`

**Step 1: Add new parameters to `record_step()` signature**

After `energy: float | None = None,` add:

```python
        tool_calls: int = 0,    # number of MCP tool calls in this step
        tokens: int = 0,        # tokens consumed in this step
        data_quality: float | None = None,  # update X if changed
```

**Step 2: Update the body to accumulate effort and token_cost**

After `state["step_count"] += 1` add:

```python
        # APEX: accumulate effort and token cost
        state["effort"] += 1.0 + 0.5 * tool_calls
        state["token_cost"] += tokens
        if data_quality is not None:
            state["data_quality"] = data_quality
```

**Step 3: Update the `ThermoSnapshot.compute()` call** in `record_step()` to pass APEX fields:

```python
        snap = ThermoSnapshot.compute(
            session_id=session_id,
            delta_s=state["delta_s"],
            peace2=state["peace2"],
            omega0=state["omega0"],
            akal=state["akal"],
            exploration=state["exploration"],
            energy=state["energy"],
            effort=state["effort"],
            token_cost=state["token_cost"],
            architecture=state["architecture"],
            parameters=state["parameters"],
            data_quality=state["data_quality"],
        )
```

**Step 4: Update history entry** to include G†:

```python
        state["history"].append(
            {
                "step": state["step_count"],
                "genius": snap.genius,
                "delta_s": snap.delta_s,
                "G_dagger": snap.G_dagger,
                "effort": snap.effort,
            }
        )
```

---

## Task 4: Update `snapshot()` and `budget_summary()`

**File:** `arifosmcp/intelligence/core/thermo_budget.py:190-235`

**Step 1: Update `snapshot()` to pass APEX fields**

The `snapshot()` method calls `ThermoSnapshot.compute()` — update it to pass the same APEX fields as `record_step()`:

```python
    def snapshot(self, session_id: str) -> ThermoSnapshot | None:
        """Return the current thermodynamic snapshot for a session."""
        state = self._sessions.get(session_id)
        if not state:
            return None
        return ThermoSnapshot.compute(
            session_id=session_id,
            delta_s=state["delta_s"],
            peace2=state["peace2"],
            omega0=state["omega0"],
            akal=state["akal"],
            exploration=state["exploration"],
            energy=state["energy"],
            effort=state.get("effort", 0.0),
            token_cost=state.get("token_cost", 0),
            architecture=state.get("architecture", 1.0),
            parameters=state.get("parameters", 1.0),
            data_quality=state.get("data_quality", 0.95),
        )
```

Note the `.get()` with defaults — this keeps backward compat for sessions opened before the upgrade.

**Step 2: Update `budget_summary()` to include APEX metrics**

Replace the return dict body with:

```python
        return {
            "session_id": snap.session_id,
            # existing G*
            "genius": round(snap.genius, 4),
            "genius_pass": snap.genius_pass,
            "delta_s": round(snap.delta_s, 4),
            "peace2": round(snap.peace2, 4),
            "omega0": round(snap.omega0, 4),
            "omega_in_band": self.omega_in_band(session_id),
            "step_count": self._sessions[session_id]["step_count"],
            # APEX metrics
            "effort": round(snap.effort, 3),
            "token_cost": snap.token_cost,
            "architecture": snap.architecture,
            "parameters": snap.parameters,
            "data_quality": round(snap.data_quality, 4),
            "eta": round(snap.eta, 6),
            "G_star": round(snap.G_star, 4),
            "G_dagger": round(snap.G_dagger, 4),
            "G_dagger_pass": snap.G_dagger_pass,
        }
```

**Step 3: Add `is_G_dagger_pass()` helper** after `is_genius_pass()`:

```python
    def is_G_dagger_pass(self, session_id: str) -> bool:
        """Return True if current G† ≥ 0.80."""
        snap = self.snapshot(session_id)
        return snap.G_dagger_pass if snap else False
```

---

## Task 5: Update `thermo_estimator.py` to surface token count

**File:** `arifosmcp/intelligence/tools/thermo_estimator.py:129-144`

**Step 1: Add `apex_input` dict to the return payload**

Inside the `ok({...})` dict in `cost_estimator()`, add a new `apex_input` key after `thermodynamic`:

```python
            "apex_input": {
                "tokens": token_count or 0,
                "tool_calls": api_calls or 0,
            },
```

This gives callers everything they need to call `budget.record_step(tokens=..., tool_calls=...)`.

---

## Task 6: Update `update_budget()` alias

**File:** `arifosmcp/intelligence/core/thermo_budget.py:164-188`

`update_budget()` is a backwards-compat alias for `record_step()`. Add the new parameters to its signature and forward them:

```python
    def update_budget(
        self,
        session_id: str,
        *,
        delta_s: float = 0.0,
        peace2: float | None = None,
        omega0: float | None = None,
        akal: float | None = None,
        exploration: float | None = None,
        energy: float | None = None,
        tool_calls: int = 0,
        tokens: int = 0,
        data_quality: float | None = None,
    ) -> ThermoSnapshot:
        return self.record_step(
            session_id=session_id,
            delta_s=delta_s,
            peace2=peace2,
            omega0=omega0,
            akal=akal,
            exploration=exploration,
            energy=energy,
            tool_calls=tool_calls,
            tokens=tokens,
            data_quality=data_quality,
        )
```

---

## Verification

After all tasks, run:

```bash
cd c:/arifosmcp
python -c "
from arifosmcp.intelligence.core import ThermoBudget, ThermoSnapshot

b = ThermoBudget()
b.open_session('test-001', architecture=1.05, parameters=1.2, data_quality=0.9)

# Simulate 3 steps with tool calls and tokens
b.record_step('test-001', delta_s=-0.3, tool_calls=2, tokens=500)
b.record_step('test-001', delta_s=-0.2, tool_calls=1, tokens=300)
b.record_step('test-001', delta_s=-0.1, tool_calls=0, tokens=200)

s = b.budget_summary('test-001')
print('genius:', s['genius'])
print('effort:', s['effort'])
print('token_cost:', s['token_cost'])
print('eta:', s['eta'])
print('G_star:', s['G_star'])
print('G_dagger:', s['G_dagger'])
print('G_dagger_pass:', s['G_dagger_pass'])
"
```

Expected: all 8 APEX fields present and non-zero; `G_dagger_pass` reflects whether G† ≥ 0.80.

---

## Execution choice

**Plan complete and saved. Two execution options:**

1. **Subagent-Driven (this session)** — fresh subagent per task, review between tasks
2. **Parallel Session** — open new session, use executing-plans

**Which approach?**
