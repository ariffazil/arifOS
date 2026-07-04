"""Tests for the bounded RSI event bus (after sovereign 999_HOLD correction).

Forged 2026-07-04 (YELLOW) at forge time.
Revised 2026-07-04 (YELLOW) under sovereign 999_HOLD:
    "SEAL → INIT → Scaffold is not the mutation path. It is the regeneration
     review path. The missing stage is Diff."

Locks the irreducible contract:
  1. Bus has 9 stages; `skill_diff` sits between `skill_rebuild` and
     `organ_rebind`.
  2. Bus is NO-OP by default.
  3. Hooks registered on any stage fire in registration order.
  4. A failing hook does NOT block downstream hooks — its failure is captured
     as a scar on the RSIReceipt.
  5. The bus is idempotent — firing twice with the same event yields two
     independently-completed cycles.
  6. ENABLE flips the bus from NOOP to fires-everything.
  7. The RESUME GATE: `resume_execution` stage is BLOCKED unless a
     `skill_diff` hook emits a StageResult with
     `gate_decision.verdict == "APPROVE_C0_C3"` AND
     `gate_decision.resume_allowed == True`. This is the engineered
     protection against autonomous self-modifying loops.
  8. Without any diff hook, the receipt is SEAL_HOLD_GATE_NOT_OPENED.
"""

from __future__ import annotations

import pytest

from arifosmcp.rsi import (
    RSI_STAGES,
    GateDecision,
    RiskClass,
    SealEvent,
    SkillDiff,
    StageResult,
    disable_post_seal_rebuild,
    enable_post_seal_rebuild,
    fire_post_seal,
    get_bus,
    register_post_seal_hook,
)


@pytest.fixture(autouse=True)
def _reset_bus():
    """Each test starts with a disabled bus; restored on teardown."""
    bus = get_bus()
    bus.disable_post_seal_rebuild()
    for stage in RSI_STAGES:
        bus._chains[stage].clear()
    yield
    bus.disable_post_seal_rebuild()
    for stage in RSI_STAGES:
        bus._chains[stage].clear()


def _make_event(seal_id: str = "vault-001") -> SealEvent:
    return SealEvent(
        seal_id=seal_id,
        verdict_id="verdict-001",
        actor="arif",
        session="sess-001",
        uncertainty=(0.03, 0.05),
        scars=(),
        floors_active=("L01", "L02"),
        payload={"topic": "test"},
    )


def _make_gate(verdict: str = "APPROVE_C0_C3", resume_allowed: bool = True) -> GateDecision:
    """Return a clean APPROVE_C0_C3 GateDecision with resume open."""
    return GateDecision(
        verdict=verdict,
        skill_name="boundary_sensing",
        risk_class=RiskClass.C2_CONTRACT_DESCRIPTION,
        rationale="all clean",
        diff=SkillDiff(
            skill_name="boundary_sensing",
            old_version="1.0.0",
            new_version="1.0.1",
            risk_class=RiskClass.C2_CONTRACT_DESCRIPTION,
            drift_signals=(),
            judge_required=False,
        ),
        required_tests=(),
        cooling_required=False,
        resume_allowed=resume_allowed,
    )


# ── 1. The contract — bus stages are frozen at 9 ────────────────────────────


def test_rsi_stages_are_frozen_at_nine():
    """The 9-stage loop is constitutional physics; do not reorder.
    `skill_diff` is the new stage after `skill_rebuild`.
    """
    assert len(RSI_STAGES) == 9
    assert RSI_STAGES == (
        "seal",
        "init_regeneration",
        "scaffold_rebuild",
        "skill_rebuild",
        "skill_diff",
        "organ_rebind",
        "receipt_replay",
        "cooling",
        "resume_execution",
    )


def test_skill_diff_sits_between_skill_rebuild_and_organ_rebind():
    """Specifically — the 999_HOLD correction's structural constraint."""
    assert RSI_STAGES.index("skill_rebuild") == 3   # 0-indexed
    assert RSI_STAGES.index("skill_diff") == 4      # the missing stage
    assert RSI_STAGES.index("organ_rebind") == 5    # gated by diff result


# ── 2. Default NO-OP ────────────────────────────────────────────────────────


def test_bus_is_noop_by_default():
    """F13 discipline: bus must be NO-OP until explicitly enabled.

    A misconfigured install must never silently rebuild.
    """
    bus = get_bus()
    bus.disable_post_seal_rebuild()
    fired: list[str] = []

    def sink(_event) -> StageResult:
        fired.append("sink")
        return StageResult(ok=True, stage="seal", hook_name="sink", elapsed_ms=0.0)

    bus.register("seal", "sink", sink)
    receipt = bus.fire(_make_event())
    assert receipt.verdict == "NOOP"
    assert fired == []


# ── 3. ENABLE → fires the registered chain ──────────────────────────────────


def test_enable_unblocks_the_chain_when_diff_opens_gate():
    bus = get_bus()
    fired: list[str] = []
    gate = _make_gate(verdict="APPROVE_C0_C3", resume_allowed=True)

    def make_hook(stage: str, name: str, with_gate: bool = False):
        def hook(_event) -> StageResult:
            fired.append(f"{stage}/{name}")
            return StageResult(
                ok=True,
                stage=stage,
                hook_name=name,
                elapsed_ms=0.0,
                gate_decision=gate if with_gate else None,
            )
        return hook

    bus.register("seal", "A", make_hook("seal", "A"))
    bus.register("init_regeneration", "B", make_hook("init_regeneration", "B"))
    bus.register("skill_rebuild", "C", make_hook("skill_rebuild", "C"))
    bus.register("skill_diff", "D", make_hook("skill_diff", "D", with_gate=True))
    bus.register("resume_execution", "E", make_hook("resume_execution", "E"))

    bus.enable_post_seal_rebuild()
    receipt = bus.fire(_make_event(seal_id="vault-A"))

    assert receipt.verdict == "SEAL_REBUILT"
    assert "seal/A" in fired
    assert "init_regeneration/B" in fired
    assert "skill_rebuild/C" in fired
    assert "skill_diff/D" in fired
    assert "resume_execution/E" in fired


# ── 4. RESUME GATE — the sovereignty guard ──────────────────────────────────


def test_resume_blocked_when_no_diff_hook_registered():
    """No `skill_diff` hook → resume_execution is SKIPPED."""
    bus = get_bus()
    resume_fired: list[str] = []

    def resume_hook(_event) -> StageResult:
        resume_fired.append("resume")
        return StageResult(ok=True, stage="resume_execution", hook_name="r", elapsed_ms=0.0)

    bus.register("seal", "s", lambda _e: StageResult(ok=True, stage="seal", hook_name="s", elapsed_ms=0.0))
    bus.register("resume_execution", "r", resume_hook)

    bus.enable_post_seal_rebuild()
    receipt = bus.fire(_make_event())

    assert resume_fired == [], "resume ran with NO diff registered"
    assert receipt.verdict == "SEAL_HOLD_GATE_NOT_OPENED"
    assert any("resume_blocked_by_gate" in s for s in receipt.scars)


def test_resume_blocked_when_diff_emits_hold():
    """A C4/C5 diff is a HOLD — the resume gate stays closed."""
    bus = get_bus()
    resume_fired: list[str] = []
    hold_gate = _make_gate(verdict="HOLD_C5", resume_allowed=False)

    def resume_hook(_event) -> StageResult:
        resume_fired.append("resume")
        return StageResult(ok=True, stage="resume_execution", hook_name="r", elapsed_ms=0.0)

    def diff_hook(_event) -> StageResult:
        return StageResult(
            ok=True, stage="skill_diff", hook_name="d",
            elapsed_ms=0.0, gate_decision=hold_gate,
        )

    bus.register("skill_diff", "d", diff_hook)
    bus.register("resume_execution", "r", resume_hook)
    bus.enable_post_seal_rebuild()
    receipt = bus.fire(_make_event())

    assert resume_fired == []
    assert receipt.verdict == "SEAL_HOLD_GATE_NOT_OPENED"


def test_resume_blocked_when_diff_ok_but_resume_allowed_false():
    """Even with APPROVE_C0_C3, if resume_allowed=False the gate stays closed.

    This is the engineered refusal of autonomous execution.
    """
    bus = get_bus()
    resume_fired: list[str] = []
    no_resume_gate = _make_gate(verdict="APPROVE_C0_C3", resume_allowed=False)

    def resume_hook(_event) -> StageResult:
        resume_fired.append("resume")
        return StageResult(ok=True, stage="resume_execution", hook_name="r", elapsed_ms=0.0)

    def diff_hook(_event) -> StageResult:
        return StageResult(
            ok=True, stage="skill_diff", hook_name="d",
            elapsed_ms=0.0, gate_decision=no_resume_gate,
        )

    bus.register("skill_diff", "d", diff_hook)
    bus.register("resume_execution", "r", resume_hook)
    bus.enable_post_seal_rebuild()
    receipt = bus.fire(_make_event())

    assert resume_fired == []
    assert receipt.verdict == "SEAL_HOLD_GATE_NOT_OPENED"


def test_resume_allowed_when_diff_emits_approve_with_resume_true():
    """Positive case — APPROVE_C0_C3 + resume_allowed=True opens the gate."""
    bus = get_bus()
    resume_fired: list[str] = []
    good_gate = _make_gate(verdict="APPROVE_C0_C3", resume_allowed=True)

    def resume_hook(_event) -> StageResult:
        resume_fired.append("resume")
        return StageResult(ok=True, stage="resume_execution", hook_name="r", elapsed_ms=0.0)

    def diff_hook(_event) -> StageResult:
        return StageResult(
            ok=True, stage="skill_diff", hook_name="d",
            elapsed_ms=0.0, gate_decision=good_gate,
        )

    bus.register("skill_diff", "d", diff_hook)
    bus.register("resume_execution", "r", resume_hook)
    bus.enable_post_seal_rebuild()
    receipt = bus.fire(_make_event())

    assert "resume" in resume_fired
    assert receipt.verdict == "SEAL_REBUILT"


# ── 5. Hooks in registration order ───────────────────────────────────────────


def test_hooks_run_in_registration_order():
    bus = get_bus()
    order: list[str] = []

    def make_hook(name: str):
        def hook(_event) -> StageResult:
            order.append(name)
            return StageResult(ok=True, stage="seal", hook_name=name, elapsed_ms=0.0)
        return hook

    bus.register("seal", "first", make_hook("first"))
    bus.register("seal", "second", make_hook("second"))
    bus.register("seal", "third", make_hook("third"))
    bus.enable_post_seal_rebuild()
    bus.fire(_make_event())
    assert order == ["first", "second", "third"]


# ── 6. Stages in canonical order even if registered reversed ───────────────


def test_stages_fire_in_frozen_order():
    bus = get_bus()
    seen: list[str] = []

    def make_hook(stage: str):
        def hook(_event) -> StageResult:
            seen.append(stage)
            if stage == "skill_diff":
                # open the gate so resume is permitted
                return StageResult(
                    ok=True, stage=stage, hook_name=stage,
                    elapsed_ms=0.0,
                    gate_decision=_make_gate(
                        verdict="APPROVE_C0_C3", resume_allowed=True
                    ),
                )
            return StageResult(ok=True, stage=stage, hook_name=stage, elapsed_ms=0.0)
        return hook

    for stage in reversed(RSI_STAGES):
        bus.register(stage, stage, make_hook(stage))
    bus.enable_post_seal_rebuild()
    bus.fire(_make_event())
    assert seen == list(RSI_STAGES)


# ── 7. Failing hook → scar, not crash ──────────────────────────────────────


def test_failing_hook_does_not_block_downstream():
    bus = get_bus()
    downstream_fired: list[str] = []

    def bad(_event) -> StageResult:
        raise RuntimeError("transient failure")

    def downstream_hook(_event) -> StageResult:
        downstream_fired.append("downstream")
        return StageResult(ok=True, stage="skill_rebuild", hook_name="d", elapsed_ms=0.0)

    bus.register("seal", "bad", bad)
    bus.register("skill_rebuild", "d", downstream_hook)
    bus.enable_post_seal_rebuild()
    receipt = bus.fire(_make_event())
    assert downstream_fired == ["downstream"]
    assert any("bad" in s for s in receipt.scars)


# ── 8. Idempotence ─────────────────────────────────────────────────────────


def test_fire_is_idempotent_within_a_session():
    bus = get_bus()
    counter = {"n": 0}
    gate = _make_gate(verdict="APPROVE_C0_C3", resume_allowed=True)

    def diff_hook(_event) -> StageResult:
        counter["n"] += 1
        return StageResult(ok=True, stage="skill_diff", hook_name="h",
                           elapsed_ms=0.0, gate_decision=gate)

    bus.register("skill_diff", "h", diff_hook)
    bus.enable_post_seal_rebuild()

    r1 = bus.fire(_make_event(seal_id="vault-1"))
    r2 = bus.fire(_make_event(seal_id="vault-2"))
    assert counter["n"] == 2
    assert r1.seal_id == "vault-1"
    assert r2.seal_id == "vault-2"
    assert r1.verdict == "SEAL_REBUILT"
    assert r2.verdict == "SEAL_REBUILT"


# ── 9. Public facade proxies correctly ──────────────────────────────────────


def test_public_facade_proxies():
    register_post_seal_hook("skill_diff", "via_facade", lambda _e: StageResult(
        ok=True, stage="skill_diff", hook_name="via_facade",
        elapsed_ms=0.0, gate_decision=_make_gate(),
    ))
    enable_post_seal_rebuild()
    receipt = fire_post_seal(_make_event())
    assert receipt.verdict == "SEAL_REBUILT"
    assert any(r.hook_name == "via_facade" for r in receipt.stage_results)


def test_unknown_stage_rejected():
    bus = get_bus()
    with pytest.raises(ValueError, match="unknown stage"):
        bus.register("not_a_real_stage", "x", lambda _e: StageResult(
            ok=True, stage="x", hook_name="x", elapsed_ms=0.0
        ))


# ── 10. Receipt carries what it must ───────────────────────────────────────


def test_receipt_carries_seal_and_verdict_ids():
    bus = get_bus()
    bus.register("skill_diff", "h", lambda _e: StageResult(
        ok=True, stage="skill_diff", hook_name="h",
        elapsed_ms=0.0, gate_decision=_make_gate(),
    ))
    bus.enable_post_seal_rebuild()
    receipt = bus.fire(_make_event(seal_id="vault-X"))
    assert receipt.seal_id == "vault-X"
    assert receipt.verdict_id == "verdict-001"
    assert receipt.session == "sess-001"


# ── 11. Hard rule: NO HOOK CAN SET resume_allowed WITHOUT verdict APPROVE ──


def test_diff_cannot_bypass_with_void_verdict():
    """A diff hook returning VOID cannot open the gate regardless of resume_allowed."""
    bus = get_bus()
    void_gate = _make_gate(verdict="VOID", resume_allowed=True)  # adversarial

    def diff_hook(_event) -> StageResult:
        return StageResult(
            ok=True, stage="skill_diff", hook_name="d",
            elapsed_ms=0.0, gate_decision=void_gate,
        )

    def resume_hook(_event) -> StageResult:
        return StageResult(ok=True, stage="resume_execution", hook_name="r", elapsed_ms=0.0)

    bus.register("skill_diff", "d", diff_hook)
    bus.register("resume_execution", "r", resume_hook)
    bus.enable_post_seal_rebuild()
    receipt = bus.fire(_make_event())

    # Bus checks verdict first — VOID is not APPROVE_C0_C3, so gate stays closed.
    assert receipt.verdict == "SEAL_HOLD_GATE_NOT_OPENED"
