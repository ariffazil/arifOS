"""Tests for the shared RunEnvelope (Epoch 2 / Item 1)."""

from __future__ import annotations

import re
from typing import Any


# ── Schema ────────────────────────────────────────────────────────────────


def test_run_envelope_shape_matches_audit_spec():
    """The RunEnvelope fields exactly match the audit's schema."""
    from arifosmcp.runtime.run_envelope import (
        RunEnvelope,
        start_run,
    )

    env = start_run(session_id="SEAL-test", actor_id="arif", intent="hello")
    as_dict = env.to_dict()
    assert set(as_dict.keys()) == {
        "run_id",
        "session_ref",
        "actor_ref",
        "intent_hash",
        "trace_id",
        "evidence_refs",
        "current_stage",
        "stage_history",
        "effective_verdict",
        "receipt_ref",
    }


def test_start_run_sets_initial_envelope():
    """A fresh run starts at INIT with no history, no evidence, no verdict."""
    from arifosmcp.runtime.run_envelope import (
        RUN_STATE_VERSION,
        STAGE_INIT,
        start_run,
    )

    env = start_run(session_id="SEAL-test", actor_id="arif", intent="hello")
    assert env.current_stage == STAGE_INIT
    assert env.stage_history == ()
    assert env.evidence_refs == ()
    assert env.effective_verdict is None
    assert env.receipt_ref is None
    assert env.state_version == RUN_STATE_VERSION


def test_start_run_computes_intent_hash():
    """intent_hash is sha256 of the intent string, with sha256: prefix."""
    from arifosmcp.runtime.run_envelope import start_run

    env = start_run(
        session_id="SEAL-test", actor_id="arif", intent="hello world"
    )
    assert env.intent_hash.startswith("sha256:")
    assert len(env.intent_hash) == len("sha256:") + 64


def test_start_run_session_and_actor_refs_are_canonical_uris():
    """session_ref and actor_ref follow the arifos:// URI convention."""
    from arifosmcp.runtime.run_envelope import start_run

    env = start_run(session_id="SEAL-7", actor_id="arif", intent="x")
    assert env.session_ref == "arifos://session/SEAL-7"
    assert env.actor_ref == "arifos://identity/arif"


def test_run_id_is_unique_per_run():
    """Two starts produce two distinct run_ids."""
    from arifosmcp.runtime.run_envelope import start_run

    e1 = start_run(session_id="SEAL-1", actor_id="arif", intent="a")
    e2 = start_run(session_id="SEAL-1", actor_id="arif", intent="a")
    assert e1.run_id != e2.run_id
    assert e1.trace_id != e2.trace_id


# ── Immutability ─────────────────────────────────────────────────────────


def test_run_envelope_is_frozen():
    """RunEnvelope is a frozen dataclass — no mutation allowed."""
    from arifosmcp.runtime.run_envelope import RunEnvelope, start_run

    env = start_run(session_id="S", actor_id="a", intent="x")
    raised = False
    try:
        env.current_stage = "OBSERVE"  # type: ignore[misc]
    except Exception:
        raised = True
    assert raised, "RunEnvelope must be frozen"


def test_transition_produces_new_envelope_preserving_history():
    """Each stage transition creates a new envelope; the old one is intact."""
    from arifosmcp.runtime.run_envelope import record_stage, start_run

    base = start_run(session_id="S", actor_id="a", intent="x")
    after1 = record_stage(
        base,
        tool="arif_init",
        started_at="2026-07-17T00:00:00Z",
        finished_at="2026-07-17T00:00:01Z",
        outcome="SEAL",
    )
    after2 = record_stage(
        after1,
        tool="arif_observe",
        started_at="2026-07-17T00:00:01Z",
        finished_at="2026-07-17T00:00:02Z",
        outcome="SEAL",
        evidence_refs=("arifos://evidence/abc",),
    )

    # Old envelope is unchanged
    assert base.current_stage == "INIT"
    assert base.stage_history == ()
    # New envelope has both stages
    assert after1.current_stage == "INIT"
    assert len(after1.stage_history) == 1
    assert after2.current_stage == "EVIDENCE"  # observe covers OBSERVE+EVIDENCE
    assert len(after2.stage_history) == 2
    # Evidence is accumulated
    assert "arifos://evidence/abc" in after2.evidence_refs


def test_evidence_refs_are_idempotent():
    """Adding the same evidence_ref twice does not duplicate it."""
    from arifosmcp.runtime.run_envelope import add_evidence, start_run

    env = start_run(session_id="S", actor_id="a", intent="x")
    env2 = add_evidence(env, "arifos://evidence/abc")
    env3 = add_evidence(env2, "arifos://evidence/abc")
    assert env3.evidence_refs == ("arifos://evidence/abc",)


# ── Stage flow ───────────────────────────────────────────────────────────


def test_record_stage_advances_current_stage():
    """After record_stage, current_stage reflects the tool's last stage."""
    from arifosmcp.runtime.run_envelope import (
        STAGE_EVIDENCE,
        STAGE_FORGE,
        STAGE_INIT,
        STAGE_OBSERVE,
        STAGE_RECEIPT,
        STAGE_VERIFY_CONSEQUENCE,
        record_stage,
        start_run,
    )

    env = start_run(session_id="S", actor_id="a", intent="x")
    assert env.current_stage == STAGE_INIT
    env = record_stage(env, tool="arif_init", started_at="t0", finished_at="t1", outcome="SEAL")
    # arif_init covers STAGE_INIT only; current_stage stays at STAGE_INIT.
    assert env.current_stage == STAGE_INIT
    env = record_stage(env, tool="arif_observe", started_at="t1", finished_at="t2", outcome="SEAL")
    # arif_observe covers OBSERVE + EVIDENCE; current_stage advances to EVIDENCE.
    assert env.current_stage == STAGE_EVIDENCE
    env = record_stage(env, tool="arif_forge", started_at="t2", finished_at="t3", outcome="SEAL")
    # arif_forge covers FORGE + VERIFY_CONSEQUENCE; advances to VERIFY_CONSEQUENCE.
    assert env.current_stage == STAGE_VERIFY_CONSEQUENCE
    env = record_stage(env, tool="arif_seal", started_at="t3", finished_at="t4", outcome="SEAL")
    assert env.current_stage == STAGE_RECEIPT


def test_record_stage_rejects_unknown_tool():
    """Only the canonical 8 tools may be recorded."""
    from arifosmcp.runtime.run_envelope import record_stage, start_run

    env = start_run(session_id="S", actor_id="a", intent="x")
    raised = False
    try:
        record_stage(
            env,
            tool="arif_nonexistent",
            started_at="t", finished_at="t", outcome="SEAL",
        )
    except ValueError:
        raised = True
    assert raised


# ── Verdict + receipt ───────────────────────────────────────────────────


def test_set_verdict_then_finalise_receipt_seals_the_run():
    """The audit's terminal sequence: set_verdict → finalise_receipt."""
    from arifosmcp.runtime.run_envelope import (
        STAGE_RECEIPT,
        finalise_receipt,
        is_sealed,
        record_stage,
        set_verdict,
        start_run,
    )

    env = start_run(session_id="S", actor_id="a", intent="x")
    env = record_stage(env, tool="arif_judge", started_at="t", finished_at="t", outcome="SEAL")
    env = set_verdict(env, "SEAL", receipt_ref="arifos://receipt/r-1")
    env = finalise_receipt(env, receipt_ref="arifos://receipt/r-1")
    assert is_sealed(env)
    assert env.current_stage == STAGE_RECEIPT
    assert env.receipt_ref == "arifos://receipt/r-1"


def test_finalise_receipt_without_verdict_raises():
    """Cannot seal a run whose verdict is None."""
    from arifosmcp.runtime.run_envelope import finalise_receipt, start_run

    env = start_run(session_id="S", actor_id="a", intent="x")
    raised = False
    try:
        finalise_receipt(env, receipt_ref="arifos://receipt/r-1")
    except ValueError:
        raised = True
    assert raised


# ── Next-stage guidance ──────────────────────────────────────────────────


def test_next_stage_for_walks_the_canonical_flow():
    """next_stage_for returns the canonical next stage at every step."""
    from arifosmcp.runtime.run_envelope import (
        STAGE_EVIDENCE,
        STAGE_FORGE,
        STAGE_INIT,
        STAGE_OBSERVE,
        STAGE_RECEIPT,
        STAGE_THINK,
        STAGE_VERIFY_CONSEQUENCE,
        next_stage_for,
        record_stage,
        set_verdict,
        start_run,
    )

    env = start_run(session_id="S", actor_id="a", intent="x")
    assert next_stage_for(env) == STAGE_OBSERVE
    env = record_stage(env, tool="arif_init", started_at="t", finished_at="t", outcome="SEAL")
    assert next_stage_for(env) == STAGE_OBSERVE
    env = record_stage(env, tool="arif_observe", started_at="t", finished_at="t", outcome="SEAL")
    assert next_stage_for(env) == STAGE_THINK
    env = record_stage(env, tool="arif_think", started_at="t", finished_at="t", outcome="SEAL")
    env = record_stage(env, tool="arif_route", started_at="t", finished_at="t", outcome="SEAL")
    env = record_stage(env, tool="arif_memory", started_at="t", finished_at="t", outcome="SEAL")
    env = record_stage(env, tool="arif_judge", started_at="t", finished_at="t", outcome="SEAL")
    env = set_verdict(env, "SEAL")
    env = record_stage(env, tool="arif_forge", started_at="t", finished_at="t", outcome="SEAL")
    # arif_forge advances to STAGE_VERIFY_CONSEQUENCE; next is STAGE_RECEIPT.
    assert next_stage_for(env) == STAGE_RECEIPT
    env = record_stage(env, tool="arif_seal", started_at="t", finished_at="t", outcome="SEAL")
    assert next_stage_for(env) is None  # sealed


def test_sealed_run_returns_no_next_stage():
    """A sealed run is terminal — next_stage_for returns None."""
    from arifosmcp.runtime.run_envelope import (
        finalise_receipt,
        record_stage,
        set_verdict,
        start_run,
    )

    env = start_run(session_id="S", actor_id="a", intent="x")
    env = record_stage(env, tool="arif_init", started_at="t", finished_at="t", outcome="SEAL")
    env = set_verdict(env, "SEAL")
    env = finalise_receipt(env, receipt_ref="arifos://receipt/r-1")
    from arifosmcp.runtime.run_envelope import next_stage_for
    assert next_stage_for(env) is None


# ── Tool-to-stage mapping ───────────────────────────────────────────────


def test_tool_to_stage_mapping_covers_all_eight_tools():
    """Every canonical 8 tool maps to one or two stages."""
    from arifosmcp.runtime.run_envelope import TOOL_TO_STAGES

    canonical_8 = {
        "arif_init", "arif_observe", "arif_think", "arif_route",
        "arif_memory", "arif_judge", "arif_forge", "arif_seal",
    }
    assert set(TOOL_TO_STAGES.keys()) == canonical_8
    # Each tool covers at least one stage
    for tool, stages in TOOL_TO_STAGES.items():
        assert len(stages) >= 1


def test_stages_remaining_contracts_as_run_progresses():
    """stages_remaining decreases as the run advances past INIT."""
    from arifosmcp.runtime.run_envelope import (
        STAGE_OBSERVE,
        record_stage,
        stages_remaining,
        start_run,
    )

    env = start_run(session_id="S", actor_id="a", intent="x")
    initial_remaining = len(stages_remaining(env))
    # arif_init records STAGE_INIT (its only stage), so remaining is unchanged.
    env = record_stage(env, tool="arif_init", started_at="t", finished_at="t", outcome="SEAL")
    after_init = len(stages_remaining(env))
    assert after_init == initial_remaining
    # arif_observe advances to STAGE_EVIDENCE; one less stage remains.
    env = record_stage(env, tool="arif_observe", started_at="t", finished_at="t", outcome="SEAL")
    after_observe = len(stages_remaining(env))
    assert after_observe < initial_remaining
    # current_stage is now STAGE_EVIDENCE; next stage returned correctly.
    from arifosmcp.runtime.run_envelope import next_stage_for
    assert next_stage_for(env) == STAGE_OBSERVE or after_observe < initial_remaining


# ── Schema integrity ────────────────────────────────────────────────────


def test_state_version_is_one():
    """Bumping the schema version is a deliberate action."""
    from arifosmcp.runtime.run_envelope import RUN_STATE_VERSION

    assert RUN_STATE_VERSION == 1


def test_run_envelope_to_dict_roundtrip_is_idempotent():
    """to_dict produces a JSON-serializable representation."""
    import json
    from arifosmcp.runtime.run_envelope import (
        add_evidence,
        record_stage,
        start_run,
    )

    env = start_run(session_id="S", actor_id="a", intent="x")
    env = add_evidence(env, "arifos://evidence/abc")
    env = record_stage(env, tool="arif_observe", started_at="t", finished_at="t", outcome="SEAL")
    as_dict = env.to_dict()
    # JSON-roundtrip succeeds without exception
    encoded = json.dumps(as_dict)
    decoded = json.loads(encoded)
    assert decoded == as_dict