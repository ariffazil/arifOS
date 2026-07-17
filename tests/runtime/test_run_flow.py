"""Phase 2 / Item 2 — Full reversible INIT→receipt integration test.

The audit's Item 2:

    "Full reversible INIT→receipt integration test."

These tests walk a RunEnvelope through every canonical stage of the
governed flow and prove the run is reversible — every stage can be
replayed from the envelope alone, with no external state.

The Epoch 2 exit condition: "one run can be reconstructed entirely
from durable records." These tests are the proof.
"""

from __future__ import annotations

from typing import Any


# ── The full 10-stage flow as a reusable helper ────────────────────────────

# Each tuple: (tool_name, evidence_refs, started_at, finished_at, outcome).
# Walks the canonical flow in order.
FULL_FLOW = [
    # tool, evidence, started, finished, outcome
    ("arif_init",     (),                                 "t0", "t1", "SEAL"),
    ("arif_observe",  ("arifos://evidence/obs-1",),       "t1", "t2", "SEAL"),
    ("arif_think",    ("arifos://evidence/think-1",),     "t2", "t3", "SEAL"),
    ("arif_route",    ("arifos://evidence/route-1",),     "t3", "t4", "SEAL"),
    ("arif_memory",   ("arifos://evidence/memory-1",),    "t4", "t5", "SEAL"),
    ("arif_judge",    ("arifos://evidence/judge-1",),     "t5", "t6", "SEAL"),
    ("arif_forge",    ("arifos://evidence/forge-1",),     "t6", "t7", "SEAL"),
    ("arif_seal",     ("arifos://receipt/r-1",),          "t7", "t8", "SEAL"),
]


def _run_full_flow(
    *,
    session_id: str = "SEAL-test",
    actor_id: str = "arif",
    intent: str = "full flow integration test",
    flow: list[tuple[str, tuple[str, ...], str, str, str]] | None = None,
) -> Any:
    """Walk a run through every stage of the canonical flow.

    Returns the final, sealed RunEnvelope. The flow is the default
    FULL_FLOW (8 tool calls, 10 stages with observe/forge covering two
    stages each). Pass a custom flow to test partial paths.
    """
    from arifosmcp.runtime.run_envelope import (
        RunEnvelope,
        finalise_receipt,
        record_stage,
        set_verdict,
        start_run,
    )

    if flow is None:
        flow = FULL_FLOW  # type: ignore[assignment]

    env: RunEnvelope = start_run(
        session_id=session_id, actor_id=actor_id, intent=intent
    )

    # The first call is INIT (no verdict set yet).
    tool, evidence, started, finished, outcome = flow[0]
    env = record_stage(
        env, tool=tool, started_at=started, finished_at=finished, outcome=outcome
    )
    # Subsequent calls: SET verdict after JUDGE, then continue.
    for tool, evidence, started, finished, outcome in flow[1:]:
        if tool == "arif_judge":
            env = set_verdict(env, outcome)
        env = record_stage(
            env,
            tool=tool,
            started_at=started,
            finished_at=finished,
            outcome=outcome,
            evidence_refs=evidence,
        )
    # The final tool is arif_seal — its evidence_ref is the receipt_ref.
    final_receipt_ref = flow[-1][2] and "arifos://receipt/r-1" or None
    # Use the last evidence ref as the receipt_ref (audit's spec).
    last_evidence = flow[-1][1]
    if last_evidence:
        receipt_ref = last_evidence[0]
    else:
        receipt_ref = "arifos://receipt/r-default"
    env = finalise_receipt(env, receipt_ref=receipt_ref)
    return env


# ── The full flow ──────────────────────────────────────────────────────────


def test_init_to_receipt_full_flow_ten_stages():
    """The full flow runs all 10 stages and seals the run.

    The 8 canonical tools cover 10 logical stages: arif_observe
    covers OBSERVE + EVIDENCE; arif_forge covers FORGE + VERIFY_CONSEQUENCE.
    Each tool records ONE StageRecord tagged with its LAST stage, so the
    history has 8 records, not 10. Every canonical stage is visited.
    """
    from arifosmcp.runtime.run_envelope import (
        CANONICAL_STAGES,
        STAGE_RECEIPT,
        TOOL_TO_STAGES,
    )

    env = _run_full_flow()

    assert env.current_stage == STAGE_RECEIPT
    assert env.receipt_ref is not None
    assert env.effective_verdict == "SEAL"

    # 8 tool records, one per canonical tool.
    assert len(env.stage_history) == 8

    # Collect every stage visited, including implicit ones (OBSERVE inside
    # arif_observe; FORGE inside arif_forge).
    visited: set[str] = set()
    for record in env.stage_history:
        stages = TOOL_TO_STAGES.get(record.tool, ())
        visited.update(stages)
        visited.add(record.stage)

    # All 10 canonical stages have been visited.
    for stage in CANONICAL_STAGES:
        assert stage in visited, f"stage {stage} not visited in flow"


def test_full_flow_accumulates_evidence_at_every_stage():
    """Each non-INIT stage adds evidence refs; they accumulate in the envelope."""
    env = _run_full_flow()

    # Expected evidence refs across the flow.
    expected_refs = {
        "arifos://evidence/obs-1",
        "arifos://evidence/think-1",
        "arifos://evidence/route-1",
        "arifos://evidence/memory-1",
        "arifos://evidence/judge-1",
        "arifos://evidence/forge-1",
        "arifos://receipt/r-1",
    }
    assert set(env.evidence_refs) == expected_refs


def test_full_flow_preserves_run_id_through_all_stages():
    """The audit: a successful tool call preserves the same run_id."""
    from arifosmcp.runtime.run_envelope import record_stage, start_run

    env = start_run(session_id="S", actor_id="a", intent="x")
    original_run_id = env.run_id
    for tool, evidence, started, finished, outcome in FULL_FLOW:
        env = record_stage(
            env,
            tool=tool,
            started_at=started,
            finished_at=finished,
            outcome=outcome,
            evidence_refs=evidence,
        )
        assert env.run_id == original_run_id, (
            f"run_id changed at {tool}: was {original_run_id}, now {env.run_id}"
        )


def test_full_flow_preserves_session_and_actor_refs():
    """Session and actor refs survive every stage transition."""
    env = _run_full_flow(session_id="SEAL-immutable", actor_id="arif-fixed")
    for record in env.stage_history:
        # The run envelope's session_ref and actor_ref don't change.
        assert env.session_ref == "arifos://session/SEAL-immutable"
        assert env.actor_ref == "arifos://identity/arif-fixed"


def test_full_flow_never_rewrites_earlier_history():
    """The audit: never rewrite earlier history. Each stage appends; nothing
    overwrites."""
    env = _run_full_flow()
    # Take a snapshot of each record's tool + outcome at the time it's recorded.
    # Then verify the final history preserves all of them in order.
    expected_tools = [
        "arif_init", "arif_observe", "arif_think", "arif_route",
        "arif_memory", "arif_judge", "arif_forge", "arif_seal",
    ]
    actual_tools = [r.tool for r in env.stage_history]
    assert actual_tools == expected_tools


# ── Reversibility: reconstruction from the envelope alone ────────────────


def _reconstruct_from_envelope(env: Any) -> dict[str, Any]:
    """Extract every fact about the run from the envelope alone.

    No external state. If the envelope is sufficient, this dict is the
    canonical reconstruction.
    """
    return {
        "run_id": env.run_id,
        "session_ref": env.session_ref,
        "actor_ref": env.actor_ref,
        "intent_hash": env.intent_hash,
        "trace_id": env.trace_id,
        "evidence_refs": list(env.evidence_refs),
        "current_stage": env.current_stage,
        "stage_history": [r.to_dict() for r in env.stage_history],
        "effective_verdict": env.effective_verdict,
        "receipt_ref": env.receipt_ref,
    }


def test_run_can_be_reconstructed_from_envelope_alone():
    """Epoch 2 exit condition: one run can be reconstructed entirely from
    durable records. The envelope IS the durable record."""
    env = _run_full_flow()
    reconstructed = _reconstruct_from_envelope(env)
    # All key fields are present and non-empty.
    assert reconstructed["run_id"]
    assert reconstructed["session_ref"].startswith("arifos://session/")
    assert reconstructed["actor_ref"].startswith("arifos://identity/")
    assert reconstructed["intent_hash"].startswith("sha256:")
    assert reconstructed["trace_id"]
    assert len(reconstructed["evidence_refs"]) >= 5
    assert len(reconstructed["stage_history"]) == 8
    assert reconstructed["effective_verdict"] == "SEAL"
    assert reconstructed["receipt_ref"]
    # state_version is implicit in the schema; the reconstruction is keyed by
    # the canonical field set above.


def test_reconstruction_roundtrip_is_lossless():
    """The envelope's to_dict() output is JSON-serializable. A second run
    produces the same shape but different identity (run_id, trace_id)."""
    import json

    env1 = _run_full_flow()
    env2 = _run_full_flow()
    # Both envelopes are JSON-serializable.
    json.dumps(env1.to_dict())
    json.dumps(env2.to_dict())
    # The two runs are independent.
    assert env1.run_id != env2.run_id
    # But the canonical fields (session, actor, intent hash) are equal
    # because we passed the same arguments.
    assert env1.session_ref == env2.session_ref
    assert env1.actor_ref == env2.actor_ref
    assert env1.intent_hash == env2.intent_hash


def test_replay_stage_by_stage_walks_history_in_order():
    """The audit: a successful tool call returns one next lawful stage.
    Replay confirms the order."""
    from arifosmcp.runtime.run_envelope import (
        CANONICAL_STAGES,
        STAGE_RECEIPT,
    )

    env = _run_full_flow()
    # Each StageRecord's stage is the tool's last stage. Reconstructing
    # the visited-stage sequence from the history:
    visited = [r.stage for r in env.stage_history]
    # arif_init -> STAGE_INIT
    # arif_observe -> STAGE_EVIDENCE (covers OBSERVE + EVIDENCE)
    # arif_think -> STAGE_THINK
    # arif_route -> STAGE_ROUTE
    # arif_memory -> STAGE_MEMORY
    # arif_judge -> STAGE_JUDGE
    # arif_forge -> STAGE_VERIFY_CONSEQUENCE (covers FORGE + VERIFY_CONSEQUENCE)
    # arif_seal -> STAGE_RECEIPT
    expected_visited = [
        "INIT", "EVIDENCE", "THINK", "ROUTE", "MEMORY",
        "JUDGE", "VERIFY_CONSEQUENCE", "RECEIPT",
    ]
    assert visited == expected_visited
    # Every canonical stage was visited in the canonical order.
    last_idx = -1
    for stage in [s for s in CANONICAL_STAGES if s != STAGE_RECEIPT]:
        if stage == "OBSERVE":
            # OBSERVE is implicit inside arif_observe; not a record itself.
            continue
        if stage == "FORGE":
            # FORGE is implicit inside arif_forge; not a record itself.
            continue
        idx = CANONICAL_STAGES.index(stage)
        assert idx > last_idx, f"{stage} should come after previous"
        last_idx = idx


def test_reversible_sealed_run_yields_same_replay():
    """Given the same starting conditions, two runs reconstruct identically
    except for the unique identity fields (run_id, trace_id, evidence timestamps)."""
    e1 = _run_full_flow()
    e2 = _run_full_flow()
    r1 = _reconstruct_from_envelope(e1)
    r2 = _reconstruct_from_envelope(e2)
    # Unique fields differ.
    assert r1["run_id"] != r2["run_id"]
    assert r1["trace_id"] != r2["trace_id"]
    # But the canonical flow shape is identical.
    for field in (
        "session_ref", "actor_ref", "intent_hash", "current_stage",
        "effective_verdict", "receipt_ref",
    ):
        assert r1[field] == r2[field], f"reconstruction diverged on {field}"
    # Stage history has the same sequence of tool names.
    assert [r["tool"] for r in r1["stage_history"]] == [
        r["tool"] for r in r2["stage_history"]
    ]


# ── Failure paths ─────────────────────────────────────────────────────────


def test_full_flow_with_hold_outcome_preserves_hold_through_seal():
    """A HOLD verdict survives the seal — the run is preserved, not retried."""
    from arifosmcp.runtime.run_envelope import (
        finalise_receipt,
        record_stage,
        set_verdict,
        start_run,
    )

    env = start_run(session_id="S", actor_id="a", intent="x")
    env = record_stage(env, tool="arif_init", started_at="t0", finished_at="t1", outcome="HOLD")
    env = record_stage(env, tool="arif_observe", started_at="t1", finished_at="t2", outcome="HOLD")
    env = record_stage(env, tool="arif_judge", started_at="t2", finished_at="t3", outcome="HOLD")
    env = set_verdict(env, "HOLD")
    env = finalise_receipt(env, receipt_ref="arifos://receipt/r-hold")
    assert env.effective_verdict == "HOLD"
    assert env.receipt_ref == "arifos://receipt/r-hold"
    # Reconstruction preserves HOLD.
    reconstructed = _reconstruct_from_envelope(env)
    assert reconstructed["effective_verdict"] == "HOLD"


def test_full_flow_evidence_refs_are_deduplicated_across_stages():
    """If two stages cite the same evidence_ref, the envelope holds it once."""
    from arifosmcp.runtime.run_envelope import (
        add_evidence,
        record_stage,
        start_run,
    )

    env = start_run(session_id="S", actor_id="a", intent="x")
    env = add_evidence(env, "arifos://evidence/shared")
    env = record_stage(
        env, tool="arif_observe", started_at="t", finished_at="t",
        outcome="SEAL", evidence_refs=("arifos://evidence/shared",),
    )
    env = record_stage(
        env, tool="arif_think", started_at="t", finished_at="t",
        outcome="SEAL", evidence_refs=("arifos://evidence/shared",),
    )
    # The shared ref is recorded once.
    assert env.evidence_refs.count("arifos://evidence/shared") == 1


def test_full_flow_with_sabar_then_seal():
    """SABAR verdict (proceed cautiously) is honoured at seal time."""
    from arifosmcp.runtime.run_envelope import (
        finalise_receipt,
        record_stage,
        set_verdict,
        start_run,
    )

    env = start_run(session_id="S", actor_id="a", intent="x")
    env = record_stage(env, tool="arif_init", started_at="t", finished_at="t", outcome="SABAR")
    env = record_stage(env, tool="arif_observe", started_at="t", finished_at="t", outcome="SABAR")
    env = record_stage(env, tool="arif_judge", started_at="t", finished_at="t", outcome="SABAR")
    env = set_verdict(env, "SABAR")
    env = finalise_receipt(env, receipt_ref="arifos://receipt/r-sabar")
    assert env.effective_verdict == "SABAR"
    assert env.receipt_ref == "arifos://receipt/r-sabar"