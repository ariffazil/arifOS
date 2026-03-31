# Tri-Witness Hardening Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace three hardcoded witness constants (ai=1.0, earth=1.0, human=0.8) with independently-derived scores from real signals, switch consensus formula to `min()`, and wire `FederationCoordinator.earth_witness_score()` into F3.

**Architecture:** Four PRs in sequence — PR1 (independence) must land before PR2-4. All changes confined to `core/shared/floors.py`, `core/kernel/evaluator.py`, `core/shared/physics.py`, `arifosmcp.transport/server.py`. Zero new files.

**Tech Stack:** Python 3.12, pytest (async auto mode), existing `FederationCoordinator` in `arifosmcp.intelligence/core/federation.py`, `FloorResult` in `core/shared/floors.py`

---

## Context You Must Read First

- Design doc: `docs/plans/2026-03-07-triwitness-hardening-design.md`
- F3 implementation: `core/shared/floors.py:286-311` — `F3_TriWitness.check()`
- Hardcoded scores: `core/kernel/evaluator.py:183-214` — the `ctx` dict build
- Physics formula: `core/shared/physics.py:334-349` — `W_3()` and `W_3_check()`
- Earth witness (unwired): `arifosmcp.intelligence/core/federation.py:117-130` — `earth_witness_score()`
- Existing tests: `core/tests/test_physics.py`, `core/workflow/tests/test_governance.py`

**Run before starting:**
```bash
cd /c/Users/User/arifOS
pytest tests/ -v -x --ignore=tests/archive -q 2>&1 | tail -30
```
Record the baseline pass/fail count. Your job is to not reduce it.

---

## PR1 — Witness Independence

**Touches:** `core/shared/floors.py`, `core/kernel/evaluator.py`
**No new files.**

---

### Task 1.1: Write failing tests for witness helper functions

**File:** Create test at `core/tests/test_triwitness_hardening.py`

**Step 1: Write the failing tests**

```python
"""
Tests for F3 Tri-Witness hardening (PR1 — witness independence).
These tests verify that witness scores are derived from real signals,
not hardcoded constants.
"""
import pytest
from core.shared.floors import F3_TriWitness, _compute_human_witness, _compute_ai_witness, _compute_earth_witness


class TestComputeHumanWitness:
    """Human witness must reflect auth/session state."""

    def test_approval_signature_gives_full_score(self):
        ctx = {"approval_signature": "sig_abc123", "session_id": "s1"}
        score, reason = _compute_human_witness(ctx)
        assert score == 1.0, f"Expected 1.0, got {score}"
        assert "signed approval" in reason.lower()

    def test_actor_with_token_gives_high_score(self):
        ctx = {"actor_id": "arif", "authority_token": "tok_xyz", "session_id": "s1"}
        score, reason = _compute_human_witness(ctx)
        assert 0.75 <= score <= 0.85, f"Expected ~0.8, got {score}"

    def test_actor_only_gives_medium_score(self):
        ctx = {"actor_id": "arif", "session_id": "s1"}
        score, reason = _compute_human_witness(ctx)
        assert 0.55 <= score <= 0.75, f"Expected ~0.7, got {score}"

    def test_session_only_gives_low_medium_score(self):
        ctx = {"session_id": "s1"}
        score, reason = _compute_human_witness(ctx)
        assert 0.4 <= score <= 0.6, f"Expected ~0.5, got {score}"

    def test_empty_context_gives_low_score(self):
        ctx = {}
        score, reason = _compute_human_witness(ctx)
        assert score <= 0.3, f"Expected ≤ 0.3, got {score}"

    def test_reason_is_non_empty_string(self):
        for ctx in [{}, {"session_id": "s"}, {"actor_id": "a"}, {"approval_signature": "x"}]:
            score, reason = _compute_human_witness(ctx)
            assert isinstance(reason, str) and len(reason) > 0


class TestComputeAiWitness:
    """AI witness must degrade when truth or orthogonality is low."""

    def test_perfect_signals_give_high_score(self):
        ctx = {"truth_score": 1.0, "orthogonality": 1.0, "entropy_delta": -0.1}
        score, reason = _compute_ai_witness(ctx)
        assert score >= 0.8, f"Expected ≥ 0.8, got {score}"

    def test_low_truth_score_pulls_ai_down(self):
        ctx = {"truth_score": 0.5, "orthogonality": 1.0, "entropy_delta": -0.1}
        score, reason = _compute_ai_witness(ctx)
        assert score <= 0.55, f"Expected ≤ 0.55 (bounded by truth=0.5), got {score}"

    def test_low_orthogonality_pulls_ai_down(self):
        ctx = {"truth_score": 1.0, "orthogonality": 0.4, "entropy_delta": -0.1}
        score, reason = _compute_ai_witness(ctx)
        assert score <= 0.45, f"Expected ≤ 0.45 (bounded by ortho=0.4), got {score}"

    def test_positive_entropy_delta_penalizes_ai(self):
        # Entropy increase = chaotic output = lower AI witness
        ctx = {"truth_score": 1.0, "orthogonality": 1.0, "entropy_delta": 0.3}
        score, reason = _compute_ai_witness(ctx)
        # Should be penalized vs negative entropy_delta
        ctx_good = {"truth_score": 1.0, "orthogonality": 1.0, "entropy_delta": -0.3}
        score_good, _ = _compute_ai_witness(ctx_good)
        assert score < score_good, "Positive entropy delta should penalize AI witness"

    def test_reason_contains_key_metrics(self):
        ctx = {"truth_score": 0.9, "orthogonality": 0.85, "entropy_delta": -0.1}
        _, reason = _compute_ai_witness(ctx)
        assert "truth" in reason.lower() or "0.9" in reason


class TestComputeEarthWitness:
    """Earth witness must reflect federation health and evidence grounding."""

    def test_no_evidence_gives_neutral_score(self):
        ctx = {}
        score, reason = _compute_earth_witness(ctx)
        assert 0.4 <= score <= 0.6, f"Expected neutral ~0.5, got {score}"

    def test_evidence_count_improves_score(self):
        ctx_no_evidence = {"evidence_count": 0}
        ctx_with_evidence = {"evidence_count": 5}
        score_none, _ = _compute_earth_witness(ctx_no_evidence)
        score_some, _ = _compute_earth_witness(ctx_with_evidence)
        assert score_some > score_none

    def test_budget_depleted_penalizes_earth(self):
        ctx_ok = {"evidence_count": 3, "budget_depletion": 0.0}
        ctx_depleted = {"evidence_count": 3, "budget_depletion": 1.0}
        score_ok, _ = _compute_earth_witness(ctx_ok)
        score_depleted, _ = _compute_earth_witness(ctx_depleted)
        assert score_depleted < score_ok

    def test_federation_score_used_when_available(self):
        ctx = {"earth_federation_score": 0.2, "evidence_count": 5}
        score, reason = _compute_earth_witness(ctx)
        assert score <= 0.25, f"Low federation score should cap earth witness, got {score}"
        assert "federation" in reason.lower()

    def test_reason_is_non_empty(self):
        for ctx in [{}, {"evidence_count": 3}, {"earth_federation_score": 0.9}]:
            _, reason = _compute_earth_witness(ctx)
            assert isinstance(reason, str) and len(reason) > 0


class TestF3TriWitnessIntegration:
    """F3 check must use min() and derived witnesses, not hardcoded 1.0."""

    def test_high_ai_and_low_human_still_fails(self):
        """Critical: min() means one weak witness fails the whole check."""
        ctx = {
            # No actor, no token, no session → human witness very low
            "truth_score": 1.0,
            "orthogonality": 1.0,
            "entropy_delta": -0.1,
            "evidence_count": 5,
            "earth_federation_score": 1.0,
        }
        result = F3_TriWitness().check(ctx)
        # human witness ≈ 0.2 (no session) → min(0.2, *, *) < 0.90 → FAIL
        assert not result.passed, "Low human witness should fail F3"

    def test_all_strong_witnesses_passes(self):
        ctx = {
            "actor_id": "arif",
            "authority_token": "tok",
            "session_id": "s1",
            "approval_signature": "sig",
            "truth_score": 1.0,
            "orthogonality": 1.0,
            "entropy_delta": -0.1,
            "evidence_count": 5,
            "earth_federation_score": 1.0,
        }
        result = F3_TriWitness().check(ctx)
        assert result.passed, f"All strong witnesses should pass F3: {result.reason}"

    def test_witness_reasons_in_metadata(self):
        ctx = {"session_id": "s1", "truth_score": 0.9, "evidence_count": 3}
        result = F3_TriWitness().check(ctx)
        assert "witness_reason" in result.metadata
        assert "human_reason" in result.metadata["witness_reason"]
        assert "ai_reason" in result.metadata["witness_reason"]
        assert "earth_reason" in result.metadata["witness_reason"]

    def test_witness_status_in_metadata(self):
        ctx = {"session_id": "s1", "truth_score": 0.9, "evidence_count": 3}
        result = F3_TriWitness().check(ctx)
        assert "witness_status" in result.metadata
        for key in ("human", "ai", "earth"):
            assert key in result.metadata["witness_status"]
            assert result.metadata["witness_status"][key] in ("CONFIRMED", "UNCERTAIN", "MISSING")

    def test_conflict_detected_when_witnesses_disagree(self):
        ctx = {
            "approval_signature": "sig",   # human = 1.0
            "truth_score": 0.3,            # ai pulls down
            "orthogonality": 0.3,
            "entropy_delta": 0.5,
            "evidence_count": 0,
        }
        result = F3_TriWitness().check(ctx)
        assert result.metadata.get("conflict") is True, "Large H/A gap should flag conflict"

    def test_old_hardcoded_constants_not_present(self):
        """Regression: ensure ai_witness=1.0 default is gone."""
        # If ai_witness and earth_witness default to 1.0, a context with no
        # auth and low truth would still pass — this test catches that regression.
        ctx = {}  # no signals at all
        result = F3_TriWitness().check(ctx)
        # With no signals: human≈0.2, ai might be ~0.5, earth≈0.5 → min < 0.90
        assert not result.passed, "Empty context should not pass F3 (no more 1.0 defaults)"
```

**Step 2: Run to confirm they all fail**

```bash
cd /c/Users/User/arifOS
pytest core/tests/test_triwitness_hardening.py -v 2>&1 | head -50
```

Expected: `ImportError` or `AttributeError` — `_compute_human_witness` doesn't exist yet. All tests FAIL.

**Step 3: Commit the failing tests**

```bash
git add core/tests/test_triwitness_hardening.py
git commit -m "test(F3): add failing tests for witness independence hardening"
```

---

### Task 1.2: Implement witness helper functions in floors.py

**File:** `core/shared/floors.py`

**Step 1: Add three module-level helper functions**

Insert after line 282 (before the `class F3_TriWitness` definition):

```python
# =============================================================================
# F3 WITNESS DERIVATION HELPERS
# =============================================================================


def _compute_human_witness(ctx: dict) -> tuple[float, str]:
    """
    Derive Human witness (H) from auth/session signals.

    Returns (score, reason_string).

    Score tiers:
        1.0  — cryptographic approval signature present
        0.8  — actor_id + authority_token (authenticated session)
        0.7  — actor_id only (identified but not token-verified)
        0.5  — session_id only (anonymous session)
        0.2  — no session context (unidentified caller)
    """
    if ctx.get("approval_signature") or ctx.get("approval_bundle"):
        return 1.0, "signed approval artifact present"
    if ctx.get("authority_token") and ctx.get("actor_id"):
        return 0.8, f"actor '{ctx['actor_id']}' with authority token"
    if ctx.get("actor_id"):
        return 0.7, f"actor '{ctx['actor_id']}' identified (no token)"
    if ctx.get("session_id"):
        return 0.5, f"session '{ctx['session_id']}' present (no actor identity)"
    return 0.2, "no session or actor identified — unverified caller"


def _compute_ai_witness(ctx: dict) -> tuple[float, str]:
    """
    Derive AI witness (A) from reasoning integrity signals.

    Returns (score, reason_string).

    Score = min(truth_score, orthogonality, coherence_proxy)

    coherence_proxy:
        entropy_delta < 0 → clarity gain → coherent (1.0 - |delta|, min 0.5)
        entropy_delta >= 0 → entropy gain → incoherent (max(0.3, 0.5 + delta * -1))
    """
    truth = min(1.0, max(0.0, ctx.get("truth_score", 1.0)))
    orthogonality = min(1.0, max(0.0, ctx.get("orthogonality", 1.0)))
    entropy_delta = ctx.get("entropy_delta", -0.05)

    if entropy_delta < 0:
        # Clarity gain: small magnitude = high coherence
        coherence = max(0.5, 1.0 - abs(entropy_delta))
    else:
        # Entropy increase: penalize, floor at 0.3
        coherence = max(0.3, 0.5 - entropy_delta)

    score = min(truth, orthogonality, coherence)
    reason = (
        f"truth={truth:.2f}, orthogonality={orthogonality:.2f}, "
        f"coherence={coherence:.2f} (ΔS={entropy_delta:+.3f})"
    )
    return score, reason


def _compute_earth_witness(ctx: dict) -> tuple[float, str]:
    """
    Derive Earth witness (E) from reality grounding signals.

    Returns (score, reason_string).

    Components:
        federation_health  — fraction of healthy agents (from FederationCoordinator)
        grounding          — evidence_count / 3 (saturates at 3 sources)
        thermo_validity    — 1.0 if budget not depleted, else 0.5

    Score = min(available_components)
    If federation unavailable, score = min(grounding, thermo_validity).
    """
    federation = ctx.get("earth_federation_score")
    evidence_count = max(0, ctx.get("evidence_count", 0))
    budget_depletion = ctx.get("budget_depletion", 0.0)

    # Grounding: 0 sources → 0.5 (neutral), 3+ sources → 1.0
    grounding = min(1.0, 0.5 + (evidence_count / 6.0)) if evidence_count > 0 else 0.5

    # Thermodynamic validity
    thermo_valid = 0.5 if budget_depletion >= 1.0 else 1.0

    if federation is not None:
        score = min(federation, grounding, thermo_valid)
        reason = (
            f"federation={federation:.2f}, grounding={grounding:.2f} "
            f"(evidence={evidence_count}), thermo={thermo_valid:.1f}"
        )
    else:
        score = min(grounding, thermo_valid)
        reason = (
            f"grounding={grounding:.2f} (evidence={evidence_count}), "
            f"thermo={thermo_valid:.1f} — federation unavailable"
        )

    return score, reason
```

**Step 2: Update F3_TriWitness.check() — replace the entire method**

Replace lines 296-311 with:

```python
    def check(self, context: dict[str, Any]) -> FloorResult:
        # Derive witnesses from independent signal sources
        human, human_reason = _compute_human_witness(context)
        ai, ai_reason = _compute_ai_witness(context)
        earth, earth_reason = _compute_earth_witness(context)

        # Allow explicit context overrides (for testing or trusted upstream tools)
        # Overrides must be explicitly set — no more 1.0 defaults at call site
        if "human_witness" in context:
            human = float(context["human_witness"])
            human_reason = f"explicit override: {human:.2f}"
        if "ai_witness" in context:
            ai = float(context["ai_witness"])
            ai_reason = f"explicit override: {ai:.2f}"
        if "earth_witness" in context:
            earth = float(context["earth_witness"])
            earth_reason = f"explicit override: {earth:.2f}"

        # Safety consensus: min() — all witnesses must agree
        # (Byzantine fault tolerance: one weak witness = weak result)
        tri_witness = min(human, ai, earth)

        passed = tri_witness >= self.spec["threshold"]

        # Witness failure mode classification
        def _classify(score: float) -> str:
            if score >= 0.80:
                return "CONFIRMED"
            if score >= 0.50:
                return "UNCERTAIN"
            return "MISSING"

        # Conflict: any two witnesses disagree by > 0.3
        scores = [human, ai, earth]
        conflict = (max(scores) - min(scores)) > 0.3

        metadata = {
            "witness_status": {
                "human": _classify(human),
                "ai": _classify(ai),
                "earth": _classify(earth),
            },
            "witness_reason": {
                "human_reason": human_reason,
                "ai_reason": ai_reason,
                "earth_reason": earth_reason,
            },
            "conflict": conflict,
            "scores": {"H": round(human, 3), "A": round(ai, 3), "E": round(earth, 3)},
        }

        return FloorResult(
            self.id,
            passed,
            tri_witness,
            f"Tri-Witness: {tri_witness:.3f} = min(H:{human:.2f} A:{ai:.2f} E:{earth:.2f})",
            metadata=metadata,
        )
```

**Step 3: Run the tests**

```bash
cd /c/Users/User/arifOS
pytest core/tests/test_triwitness_hardening.py -v 2>&1
```

Expected: All tests PASS. If any fail, debug the helper logic.

**Step 4: Run baseline tests to catch regressions**

```bash
pytest tests/ -v -x --ignore=tests/archive -q 2>&1 | tail -30
```

Fix any regressions before committing.

**Step 5: Commit**

```bash
git add core/shared/floors.py core/tests/test_triwitness_hardening.py
git commit -m "feat(F3): derive witnesses from real signals — replace hardcoded 1.0 defaults

- Add _compute_human_witness(): auth/session tier scoring
- Add _compute_ai_witness(): truth × orthogonality × coherence
- Add _compute_earth_witness(): federation × grounding × thermo
- F3_TriWitness.check() uses min(H,A,E) consensus (not geometric mean)
- Add witness failure modes and conflict detection to FloorResult.metadata
- Explicit context overrides still honored but no 1.0 defaults"
```

---

### Task 1.3: Remove hardcoded witness scores from evaluator.py

**File:** `core/kernel/evaluator.py`

**Step 1: Read the current ctx dict at lines 183-214**

Open the file and find the block:
```python
ctx = {
    "query": query,
    "response": response,
    "confidence": 0.96,
    "entropy_input": 0.5,
    "entropy_output": 0.45,
    "human_witness": 0.8,   # ← REMOVE
    "ai_witness": 1.0,      # ← REMOVE
    "earth_witness": 1.0,   # ← REMOVE
}
```

**Step 2: Remove the three hardcoded lines and inject federation**

Replace the block with:

```python
# Attempt to get real earth witness from FederationCoordinator
_earth_fed_score = None
try:
    from arifosmcp.intelligence.core.federation import FederationCoordinator
    _coordinator = FederationCoordinator()
    _earth_fed_score = _coordinator.earth_witness_score()
except Exception:
    pass  # Federation unavailable — earth witness will use evidence grounding only

ctx = {
    "query": query,
    "response": response,
    "confidence": 0.96,
    "entropy_input": 0.5,
    "entropy_output": 0.45,
    # earth_federation_score injected for _compute_earth_witness()
    # human_witness and ai_witness intentionally REMOVED — now derived by F3_TriWitness
    **({"earth_federation_score": _earth_fed_score} if _earth_fed_score is not None else {}),
}
```

**Step 3: Remove human_witness, ai_witness, earth_witness from the override list**

Find lines 199-214 with the override loop. Remove `"human_witness"`, `"ai_witness"`, `"earth_witness"` from the key list. Keep `"truth_score"`, `"orthogonality"`, `"entropy_delta"` etc. — these feed the witness derivation functions.

The list should become:
```python
for key in (
    "truth_score",
    "confidence",
    "entropy_delta",
    "empathy_kappa_r",
    "weakest_stakeholder_impact",
    "entropy_input",
    "entropy_output",
    "humility_omega",
    "f2_threshold",
    "orthogonality",
    "budget_depletion",
    "evidence_count",
    "earth_federation_score",
    # NOTE: human_witness, ai_witness, earth_witness removed
    # They are now derived by _compute_*_witness() in F3_TriWitness.check()
    # Explicit overrides still honored via the context.get() path in F3
):
    if key in result:
        ctx[key] = result[key]
```

**Step 4: Run tests**

```bash
pytest core/tests/test_triwitness_hardening.py tests/ -v -x --ignore=tests/archive -q 2>&1 | tail -40
```

Fix any regressions.

**Step 5: Commit**

```bash
git add core/kernel/evaluator.py
git commit -m "feat(evaluator): remove hardcoded human/ai/earth witness constants

- Remove human_witness=0.8, ai_witness=1.0, earth_witness=1.0 from default ctx
- Wire FederationCoordinator.earth_witness_score() → earth_federation_score
- Remove human_witness/ai_witness/earth_witness from result override loop
- Add orthogonality, budget_depletion, evidence_count to override list"
```

---

## PR2 — Threshold Unification

**Touches:** `core/shared/physics.py`

---

### Task 2.1: Fix W_3_check() default threshold

**File:** `core/shared/physics.py:363-369`

**Step 1: Find and update**

Find:
```python
def W_3_check(H: float, A: float, S: float, threshold: float = 0.95) -> bool:
```

Change to:
```python
def W_3_check(H: float, A: float, S: float, threshold: float = 0.90) -> bool:
    """
    F3 enforcement check: min(H, A, S) >= threshold?

    NOTE: Uses min() not geometric_mean — matches F3_TriWitness.check() enforcement.
    Threshold aligned to canonical THRESHOLDS["F3_TriWitness"]["threshold"] = 0.90.
    """
    return min(H, A, S) >= threshold
```

**Step 2: Update the `W_3()` docstring to note geometric_mean vs min() distinction**

The `W_3()` function (physics primitive, not enforcement) keeps geometric_mean.
`W_3_check()` (enforcement) uses min(). Document this clearly in the docstring:

```python
def W_3(H: float, A: float, S: float) -> float:
    """
    F3 Tri-Witness Consensus (physics primitive): W_3 = cube_root(H × A × S)

    NOTE: This is the PHYSICS primitive for telemetry/scoring.
    The ENFORCEMENT function W_3_check() uses min(H, A, S) for safety-critical decisions.
    See F3_TriWitness.check() in core/shared/floors.py for the authoritative gate.
    """
    return geometric_mean([H, A, S])
```

**Step 3: Update test_physics.py if it tests W_3_check with 0.95**

```bash
grep -n "0.95\|W_3_check" core/tests/test_physics.py
```

Update any assertions that assume 0.95 threshold.

**Step 4: Run tests**

```bash
pytest core/tests/test_physics.py core/tests/test_triwitness_hardening.py -v 2>&1
```

**Step 5: Commit**

```bash
git add core/shared/physics.py core/tests/test_physics.py
git commit -m "fix(physics): align W_3_check() threshold to 0.90, use min() for enforcement

- W_3_check() threshold 0.95 → 0.90 (matches THRESHOLDS canonical value)
- W_3_check() uses min() for Byzantine-style enforcement (not geometric mean)
- W_3() physics primitive keeps geometric_mean (telemetry, not enforcement)
- Document the physics vs enforcement distinction in docstrings"
```

---

## PR3 — Failure Modes (Already in PR1)

The `witness_status`, `witness_reason`, and `conflict` fields were already added to `FloorResult.metadata` in Task 1.2. PR3 is DONE as part of PR1.

Verify:
```bash
cd /c/Users/User/arifOS && python -c "
from core.shared.floors import F3_TriWitness
result = F3_TriWitness().check({'session_id': 's1', 'truth_score': 0.9})
print('metadata keys:', list(result.metadata.keys()))
print('witness_status:', result.metadata['witness_status'])
print('conflict:', result.metadata['conflict'])
"
```

Expected output shows all three status keys and conflict bool.

---

## PR4 — Tool-Class Gating

**Touches:** `core/kernel/evaluator.py`, `arifosmcp.transport/server.py`

---

### Task 4.1: Write failing tests for action-class gating

**File:** `core/tests/test_triwitness_hardening.py` — add a new section

```python
class TestActionClassGating:
    """F3 threshold must vary by tool action class."""

    def _ctx_with_human(self, level: str) -> dict:
        """Helper: build ctx with specified human auth level."""
        base = {"truth_score": 1.0, "orthogonality": 1.0, "entropy_delta": -0.1,
                "evidence_count": 5, "earth_federation_score": 1.0}
        if level == "signed":
            base["approval_signature"] = "sig"
            base["actor_id"] = "arif"
            base["session_id"] = "s1"
        elif level == "token":
            base["authority_token"] = "tok"
            base["actor_id"] = "arif"
            base["session_id"] = "s1"
        elif level == "session":
            base["session_id"] = "s1"
        return base

    def test_read_passes_with_session_only(self):
        """READ tools require AI + Earth, not full human witness."""
        from core.kernel.evaluator import check_f3_for_action_class
        ctx = self._ctx_with_human("session")  # human ≈ 0.5
        result = check_f3_for_action_class(ctx, action_class="read")
        assert result["passed"], f"Session-only should pass READ gate: {result}"

    def test_write_fails_without_actor(self):
        """WRITE tools require actor identity (human ≥ 0.7)."""
        from core.kernel.evaluator import check_f3_for_action_class
        ctx = self._ctx_with_human("session")  # human ≈ 0.5, no actor
        result = check_f3_for_action_class(ctx, action_class="write")
        assert not result["passed"], "No actor should fail WRITE gate"

    def test_write_passes_with_actor_token(self):
        from core.kernel.evaluator import check_f3_for_action_class
        ctx = self._ctx_with_human("token")  # human ≈ 0.8
        result = check_f3_for_action_class(ctx, action_class="write")
        assert result["passed"], f"Actor+token should pass WRITE gate: {result}"

    def test_critical_requires_signed_approval(self):
        """CRITICAL tools require approval signature (human = 1.0)."""
        from core.kernel.evaluator import check_f3_for_action_class
        ctx = self._ctx_with_human("token")  # human ≈ 0.8, no sig
        result = check_f3_for_action_class(ctx, action_class="critical")
        assert not result["passed"], "Token-only should fail CRITICAL gate"

    def test_critical_passes_with_signed_approval(self):
        from core.kernel.evaluator import check_f3_for_action_class
        ctx = self._ctx_with_human("signed")  # human = 1.0
        result = check_f3_for_action_class(ctx, action_class="critical")
        assert result["passed"], f"Signed approval should pass CRITICAL gate: {result}"
```

**Step 2: Run to confirm they fail (ImportError expected)**

```bash
pytest core/tests/test_triwitness_hardening.py::TestActionClassGating -v 2>&1 | head -20
```

---

### Task 4.2: Implement check_f3_for_action_class in evaluator.py

**File:** `core/kernel/evaluator.py`

**Step 1: Add constants and function**

Add near the top of the file (after imports, before class definitions):

```python
# ─── F3 Action-Class Gating ───────────────────────────────────────────────────

WITNESS_REQUIREMENTS: dict[str, dict] = {
    "read": {
        "threshold": 0.80,
        "require_human_sig": False,
        "description": "AI + Earth sufficient for read operations",
    },
    "write": {
        "threshold": 0.90,
        "require_human_sig": False,
        "description": "All three witnesses required for write operations",
    },
    "critical": {
        "threshold": 0.95,
        "require_human_sig": True,
        "description": "All three witnesses + explicit human approval for critical ops",
    },
}

# Tool → action class mapping
TOOL_CLASS_MAP: dict[str, str] = {
    # READ tools — observe only
    "reason_mind": "read",
    "vector_memory": "read",
    "search_reality": "read",
    "audit_rules": "read",
    "check_vital": "read",
    "metabolic_loop": "read",
    # WRITE tools — modify state
    "simulate_heart": "write",
    "critique_thought": "write",
    "eureka_forge": "write",
    "ingest_evidence": "write",
    "anchor_session": "write",
    # CRITICAL tools — irreversible or sovereign actions
    "apex_judge": "critical",
    "seal_vault": "critical",
}


def check_f3_for_action_class(ctx: dict, action_class: str = "write") -> dict:
    """
    F3 Tri-Witness gate with action-class threshold.

    Args:
        ctx: Evaluation context (same format as F3_TriWitness.check() context)
        action_class: One of "read", "write", "critical"

    Returns:
        {"passed": bool, "tri_witness": float, "reason": str, "metadata": dict}
    """
    from core.shared.floors import F3_TriWitness

    requirements = WITNESS_REQUIREMENTS.get(action_class, WITNESS_REQUIREMENTS["write"])

    # Override threshold in a copy of the THRESHOLDS spec
    floor = F3_TriWitness()
    floor.spec = dict(floor.spec)
    floor.spec["threshold"] = requirements["threshold"]

    result = floor.check(ctx)

    # Additional check for critical: require approval signature
    if requirements["require_human_sig"]:
        has_sig = bool(ctx.get("approval_signature") or ctx.get("approval_bundle"))
        if not has_sig:
            return {
                "passed": False,
                "tri_witness": result.score,
                "reason": f"CRITICAL gate: approval_signature required, not present. {result.reason}",
                "metadata": result.metadata,
            }

    return {
        "passed": result.passed,
        "tri_witness": result.score,
        "reason": result.reason,
        "metadata": result.metadata,
    }
```

**Step 2: Run tests**

```bash
pytest core/tests/test_triwitness_hardening.py -v 2>&1
```

All tests should pass.

---

### Task 4.3: Inject action_class into arifosmcp.transport server tool contexts

**File:** `arifosmcp.transport/server.py`

**Step 1: Find where tools build their eval context**

Search for where `apex_judge`, `seal_vault`, and `reason_mind` call the evaluator or build context dicts.

```bash
grep -n "action_class\|evaluate\|_build_context\|evaluator" arifosmcp.transport/server.py | head -20
```

**Step 2: Add action_class injection**

For each tool, inject `action_class` based on `TOOL_CLASS_MAP`. Pattern:

```python
# In the tool handler, add to context:
ctx["action_class"] = TOOL_CLASS_MAP.get(tool_name, "write")
```

The exact location depends on how `arifosmcp.transport/server.py` builds its tool contexts. Read the file to find the pattern, then inject at the right point.

**Step 3: Run full test suite**

```bash
pytest tests/ -v -x --ignore=tests/archive -q 2>&1 | tail -30
```

**Step 4: Commit**

```bash
git add core/kernel/evaluator.py arifosmcp.transport/server.py core/tests/test_triwitness_hardening.py
git commit -m "feat(F3): add action-class gating — read/write/critical thresholds

- Add WITNESS_REQUIREMENTS dict with thresholds per action class
- Add TOOL_CLASS_MAP mapping 13 MCP tools to action classes
- Add check_f3_for_action_class() function in evaluator.py
- CRITICAL tools require approval_signature (not just actor presence)
- Inject action_class into arifosmcp.transport tool contexts"
```

---

## Final Verification

Run this smoke test after all PRs:

```bash
cd /c/Users/User/arifOS && python -c "
from core.shared.floors import F3_TriWitness, _compute_human_witness, _compute_ai_witness, _compute_earth_witness

print('=== Witness Independence Check ===')

# Scenario 1: Empty context (old code would give W3=0.93)
ctx = {}
h, hr = _compute_human_witness(ctx)
a, ar = _compute_ai_witness(ctx)
e, er = _compute_earth_witness(ctx)
print(f'Empty ctx: H={h:.2f} A={a:.2f} E={e:.2f} → min={min(h,a,e):.2f}')
assert min(h,a,e) < 0.90, 'Empty context must NOT pass F3'

# Scenario 2: Full auth (should pass)
ctx2 = {'approval_signature': 'sig', 'actor_id': 'arif', 'session_id': 's1',
        'truth_score': 1.0, 'orthogonality': 1.0, 'entropy_delta': -0.1,
        'evidence_count': 5, 'earth_federation_score': 1.0}
result = F3_TriWitness().check(ctx2)
print(f'Full auth: {result.reason}')
print(f'Metadata conflict: {result.metadata[\"conflict\"]}')
assert result.passed, 'Full auth must pass F3'

print()
print('All checks passed. Tri-Witness hardening is operational.')
"
```

---

## Files Changed Summary

| File | PR | Lines Changed | Purpose |
|------|----|---------------|---------|
| `core/shared/floors.py` | PR1 | +~80 lines | Witness helpers + F3 check rewrite |
| `core/kernel/evaluator.py` | PR1+PR4 | ~20 lines changed | Remove hardcoded; add gating |
| `core/shared/physics.py` | PR2 | ~5 lines | Threshold + formula docs |
| `arifosmcp.transport/server.py` | PR4 | ~13 injections | action_class per tool |
| `core/tests/test_triwitness_hardening.py` | PR1+PR4 | ~150 lines | New test file |

**Total: 4 existing files modified, 1 new test file. Zero new production files.**

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
