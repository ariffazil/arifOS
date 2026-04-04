# Tri-Witness Hardening — Design Document

**Date:** 2026-03-07
**Authority:** Muhammad Arif bin Fazil (Sovereign)
**Status:** APPROVED — awaiting implementation
**Goal:** Transform F3 Tri-Witness from symbolic to real governance

---

## Problem Statement

Audit (2026-03-07) revealed that two of the three witnesses are hardcoded constants:

```python
# core/kernel/evaluator.py:189-191
"human_witness": 0.8,   # hardcoded — not derived
"ai_witness":    1.0,   # ceiling — always passes
"earth_witness": 1.0,   # ceiling — always passes
```

This means `W_3 ≈ ∛(0.8 × 1.0 × 1.0) = 0.93` on every call.
F3 is not measuring governance — it is measuring **the constant 0.93**.

---

## Audit Findings

| Witness | Current Value | Source | Problem |
|---------|--------------|--------|---------|
| Human (H) | 0.8 | Hardcoded in `evaluator.py:189` | Not derived from session/auth |
| AI (A) | 1.0 | Hardcoded in `evaluator.py:190` | Ceiling — always passes |
| Earth (E) | 1.0 | Hardcoded in `evaluator.py:191` | `federation.earth_witness_score()` exists but unwired |

**Secondary issues:**
- Threshold inconsistency: `floors.py` uses 0.90, `physics.py` W_3_check() default uses 0.95
- Consensus formula is geometric mean; safety systems use `min()` for stronger enforcement
- No witness failure modes (MISSING / UNCERTAIN / CONFLICT / CONFIRMED)
- No action-class gating (read vs write vs critical)

---

## Design Decisions

### 1. Consensus Rule: geometric_mean → min()

**Before:** `W_3 = (H × A × E)^(1/3)`
**After:** `W_3 = min(H, A, E)`

**Rationale:** Byzantine consensus and safety-critical systems use min() because
it forces all witnesses to agree. Geometric mean allows one strong witness to
compensate for a weak one — that is gaming, not governance.

```
H=1.0, A=0.8, E=0.9
geometric: 0.93  (looks fine)
min:        0.8  (correctly weak — AI witness uncertain)
```

### 2. Unified Threshold: 0.90

Canonical value in `THRESHOLDS["F3_TriWitness"]["threshold"]` = 0.90.
`physics.py W_3_check()` default parameter corrected to match.

### 3. Witness Derivation (Independence)

**Human witness** — derived from auth/session context:
```
approval_signature present → H = 1.0
actor_id present           → H = 0.8
session_id only            → H = 0.5
no session                 → H = 0.2
```
Signals: `actor_id`, `authority_token`, `session_id`, `approval_bundle`

**AI witness** — derived from reasoning integrity signals already in context:
```
A = min(truth_score, orthogonality, coherence_proxy)
coherence_proxy = 1.0 - abs(entropy_delta) if entropy_delta < 0 else 0.5
```
Signals: `truth_score`, `orthogonality`, `entropy_delta`

**Earth witness** — wire `federation.earth_witness_score()` directly:
```
E = min(
    federation_health,          # fraction of healthy agents
    grounding_score,            # evidence retrieval count proxy
    thermodynamic_validity      # 1.0 if budget not depleted, else 0.5
)
```
Signals: `FederationCoordinator.earth_witness_score()`, `evidence_count`, `budget_depletion`

### 4. Witness Failure Modes

`FloorResult.metadata` extended with:
```python
{
    "witness_status": {
        "human": "CONFIRMED" | "UNCERTAIN" | "MISSING",
        "ai":    "CONFIRMED" | "UNCERTAIN" | "MISSING",
        "earth": "CONFIRMED" | "UNCERTAIN" | "MISSING",
    },
    "witness_reason": {
        "human_reason": "actor session present",
        "ai_reason":    "truth_score=0.92, orthogonality=0.98",
        "earth_reason": "federation 4/5 healthy, evidence_count=3",
    },
    "conflict": bool,  # True if any two witnesses disagree by > 0.3
}
```

### 5. Action-Class Gating (PR2 — after independence)

```python
WITNESS_REQUIREMENTS = {
    "read":     {"min_witnesses": 2, "threshold": 0.80},  # AI + Earth
    "write":    {"min_witnesses": 3, "threshold": 0.90},  # All three
    "critical": {"min_witnesses": 3, "threshold": 0.95, "require_human_sig": True},
}
```

Tool-class mapping:
- `READ`: `reason_mind`, `vector_memory`, `search_reality`, `audit_rules`, `check_vital`
- `WRITE`: `simulate_heart`, `critique_thought`, `eureka_forge`, `ingest_evidence`
- `CRITICAL`: `apex_judge`, `seal_vault`, `anchor_session`

---

## Implementation Plan (PR Sequence)

### PR1 — Witness Independence (0 new files, 2 files modified)

**Files:** `core/shared/floors.py`, `core/kernel/evaluator.py`

1. Add `_compute_human_witness(ctx)`, `_compute_ai_witness(ctx)`, `_compute_earth_witness(ctx)` as module-level helpers in `floors.py`
2. Replace `F3_TriWitness.check()` to call these helpers instead of `context.get()` with 1.0 defaults
3. Switch formula from geometric mean to `min(H, A, E)`
4. Fix threshold: ensure `self.spec["threshold"]` = 0.90 (already correct in THRESHOLDS)
5. In `evaluator.py`: remove hardcoded witness values; inject `earth_witness` from `FederationCoordinator` if available
6. Add witness failure mode metadata to `FloorResult`

### PR2 — Consensus Rule + Threshold Unification (0 new files, 1 file modified)

**Files:** `core/shared/physics.py`

1. Update `W_3_check()` default threshold from 0.95 → 0.90
2. Update docstring to document `min()` vs geometric_mean distinction

### PR3 — Failure Modes + Metadata (0 new files, 1 file modified)

**Files:** `core/shared/floors.py`

1. Add `witness_status`, `witness_reason`, `conflict` to FloorResult metadata
2. Add conflict detection: `conflict = any(|Wi - Wj| > 0.3 for i≠j)`

### PR4 — Tool-Class Gating (0 new files, 2 files modified)

**Files:** `core/kernel/evaluator.py`, `aaa_mcp/server.py`

1. Add `WITNESS_REQUIREMENTS` dict and `TOOL_CLASS_MAP` in `evaluator.py`
2. In `aaa_mcp/server.py`, inject `action_class` into eval context per tool

---

## Success Criteria

- [ ] `ai_witness` and `earth_witness` no longer default to 1.0 anywhere in codebase
- [ ] `W_3` computed via `min()` not geometric mean in F3 enforcement
- [ ] Threshold consistent at 0.90 across `floors.py` and `physics.py`
- [ ] `FloorResult.metadata` includes `witness_reason` for each witness
- [ ] `federation.earth_witness_score()` is wired into F3 context
- [ ] Existing tests pass (or are updated to reflect real scores)
- [ ] Zero new files created

---

## Files Touched (total across all PRs)

| File | PRs | Change |
|------|-----|--------|
| `core/shared/floors.py` | PR1, PR3 | Witness derivation + failure modes |
| `core/kernel/evaluator.py` | PR1, PR4 | Remove hardcoded scores + action gating |
| `core/shared/physics.py` | PR2 | W_3_check() threshold alignment |
| `aaa_mcp/server.py` | PR4 | Inject action_class per tool |

**Total: 4 files, 0 new files.**

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
