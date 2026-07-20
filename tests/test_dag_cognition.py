"""
tests/test_dag_cognition.py — DAG Cognition Model Tests (FORGED 2026-07-20)

Tests for the tri-layer architecture: L1 Execution DAG, L2 VAULT999 integration,
L3 disposable index.  F1 AMANAH + F2 TRUTH + F11 AUDIT.

DITEMPA BUKAN DIBERI
"""

import pytest
from arifosmcp.runtime.dag_cognition import (
    DAGEngine,
    DAGNode,
    DAGSession,
    EpistemicLabel,
    SealEvidencePayload,
    TriLayerArchitecture,
    TurnRole,
)

# ── DAGNode ───────────────────────────────────────────────────────────────────


class TestDAGNode:
    def test_compute_sha_is_deterministic(self):
        sha1 = DAGNode.compute_sha("s1", 1, TurnRole.USER, {"msg": "hi"}, None, 1000.0)
        sha2 = DAGNode.compute_sha("s1", 1, TurnRole.USER, {"msg": "hi"}, None, 1000.0)
        assert sha1 == sha2

    def test_compute_sha_differs_on_payload(self):
        sha1 = DAGNode.compute_sha("s1", 1, TurnRole.USER, {"msg": "hi"}, None, 1000.0)
        sha2 = DAGNode.compute_sha("s1", 1, TurnRole.USER, {"msg": "bye"}, None, 1000.0)
        assert sha1 != sha2

    def test_compute_sha_differs_on_turn(self):
        sha1 = DAGNode.compute_sha("s1", 1, TurnRole.USER, {"msg": "hi"}, None, 1000.0)
        sha2 = DAGNode.compute_sha("s1", 2, TurnRole.USER, {"msg": "hi"}, None, 1000.0)
        assert sha1 != sha2

    def test_node_creation_with_trailers(self):
        node = DAGNode(
            session_id="s1",
            branch_ref="refs/agents/s1",
            parent_sha="abc123",
            commit_sha="def456",
            turn_number=1,
            role=TurnRole.USER,
            payload={"text": "hello"},
            trailers={"Subagent-Result": "sha789"},
            epistemic=EpistemicLabel.OBS,
        )
        assert node.trailers["Subagent-Result"] == "sha789"
        assert node.epistemic == EpistemicLabel.OBS


# ── DAGSession ────────────────────────────────────────────────────────────────


class TestDAGSession:
    def test_session_creation(self):
        session = DAGSession()
        assert session.session_id
        assert session.main_branch == f"refs/agents/{session.session_id}"
        assert session.turn_count == 0
        assert session.head_sha is None

    def test_subagent_branch_ref(self):
        session = DAGSession()
        ref = session.subagent_branch("worker1")
        assert ref == f"refs/agents/{session.session_id}/worker1"

    def test_custom_session_id(self):
        session = DAGSession(session_id="custom-id")
        assert session.session_id == "custom-id"


# ── DAGEngine — Commit & Trail ────────────────────────────────────────────────


class TestDAGEngineCommits:
    def test_commit_single_turn(self):
        engine = DAGEngine()
        session = engine.create_session()
        node = engine.commit_turn(session, TurnRole.USER, {"text": "hello"})
        assert node.turn_number == 1
        assert node.role == TurnRole.USER
        assert node.commit_sha
        assert session.turn_count == 1
        assert session.head_sha == node.commit_sha
        assert session.root_sha == node.commit_sha

    def test_commit_multiple_turns_chain(self):
        engine = DAGEngine()
        session = engine.create_session()
        n1 = engine.commit_turn(session, TurnRole.USER, {"text": "q1"})
        n2 = engine.commit_turn(session, TurnRole.ASSISTANT, {"text": "a1"})
        n3 = engine.commit_turn(session, TurnRole.TOOL_CALL, {"tool": "search"})

        assert session.turn_count == 3
        assert n2.parent_sha == n1.commit_sha
        assert n3.parent_sha == n2.commit_sha

    def test_get_trail_returns_ordered_nodes(self):
        engine = DAGEngine()
        session = engine.create_session()
        engine.commit_turn(session, TurnRole.USER, {"text": "t1"})
        engine.commit_turn(session, TurnRole.ASSISTANT, {"text": "t2"})
        engine.commit_turn(session, TurnRole.USER, {"text": "t3"})

        trail = engine.get_trail(session)
        assert len(trail) == 3
        assert [n.turn_number for n in trail] == [1, 2, 3]

    def test_get_trail_max_turns(self):
        engine = DAGEngine()
        session = engine.create_session()
        for i in range(10):
            engine.commit_turn(session, TurnRole.USER, {"text": f"t{i}"})

        trail = engine.get_trail(session, max_turns=5)
        assert len(trail) == 5
        # Should be the LAST 5
        assert trail[0].turn_number == 6

    def test_multiple_sessions_isolated(self):
        engine = DAGEngine()
        s1 = engine.create_session()
        s2 = engine.create_session()
        engine.commit_turn(s1, TurnRole.USER, {"text": "s1"})
        engine.commit_turn(s2, TurnRole.USER, {"text": "s2"})
        engine.commit_turn(s2, TurnRole.ASSISTANT, {"text": "s2a"})

        assert s1.turn_count == 1
        assert s2.turn_count == 2


# ── DAGEngine — Subagents ─────────────────────────────────────────────────────


class TestDAGEngineSubagents:
    def test_create_subagent(self):
        engine = DAGEngine()
        session = engine.create_session()
        engine.commit_turn(session, TurnRole.USER, {"text": "do work"})

        branch_ref, spawn_node = engine.create_subagent(session, "worker1")
        assert branch_ref == session.subagent_branch("worker1")
        assert spawn_node.role == TurnRole.SUBAGENT_SPAWN
        assert spawn_node.payload["subagent_id"] == "worker1"
        assert "worker1" in session.subagents

    def test_subagent_commits_on_own_branch(self):
        engine = DAGEngine()
        session = engine.create_session()
        engine.commit_turn(session, TurnRole.USER, {"text": "main work"})

        branch_ref, _ = engine.create_subagent(session, "worker1")
        n1 = engine.commit_turn(
            session, TurnRole.TOOL_CALL, {"tool": "read"}, branch_ref=branch_ref
        )
        n2 = engine.commit_turn(
            session, TurnRole.TOOL_RESULT, {"result": "data"}, branch_ref=branch_ref
        )

        # Main branch should still have 2 turns (user + spawn)
        assert session.turn_count == 2
        # Subagent branch should have 2 turns
        assert len(session.branches[branch_ref]) == 2
        assert n2.parent_sha == n1.commit_sha

    def test_complete_subagent_with_terminal_sha(self):
        engine = DAGEngine()
        session = engine.create_session()
        engine.commit_turn(session, TurnRole.USER, {"text": "main"})

        branch_ref, _ = engine.create_subagent(session, "worker1")
        n1 = engine.commit_turn(
            session, TurnRole.TOOL_CALL, {"tool": "search"}, branch_ref=branch_ref
        )

        result_node = engine.complete_subagent(
            session, "worker1",
            result_payload={"found": 42},
            terminal_sha=n1.commit_sha,
        )
        assert result_node.role == TurnRole.SUBAGENT_RESULT
        assert result_node.trailers["Subagent-Result"] == n1.commit_sha
        assert result_node.payload["terminal_sha"] == n1.commit_sha

    def test_export_evidence_sha(self):
        engine = DAGEngine()
        session = engine.create_session()
        engine.commit_turn(session, TurnRole.USER, {"text": "main"})

        branch_ref, _ = engine.create_subagent(session, "worker1")
        node = engine.commit_turn(
            session, TurnRole.ASSISTANT, {"text": "result"}, branch_ref=branch_ref
        )

        sha = engine.export_evidence_sha(session, "worker1")
        assert sha == node.commit_sha

    def test_export_evidence_sha_nonexistent_subagent(self):
        engine = DAGEngine()
        session = engine.create_session()
        assert engine.export_evidence_sha(session, "nonexistent") is None


# ── DAGEngine — Rewind ────────────────────────────────────────────────────────


class TestDAGEngineRewind:
    def test_rewind_shifts_head(self):
        engine = DAGEngine()
        session = engine.create_session()
        n1 = engine.commit_turn(session, TurnRole.USER, {"text": "t1"})
        n2 = engine.commit_turn(session, TurnRole.USER, {"text": "t2"})
        n3 = engine.commit_turn(session, TurnRole.USER, {"text": "t3"})  # bad turn

        assert session.head_sha == n3.commit_sha

        rewind_node = engine.rewind(session, n2.commit_sha, reason="bad turn at t3")
        assert session.head_sha == n2.commit_sha
        assert rewind_node.role == TurnRole.REWIND
        assert rewind_node.payload["rewind_to"] == n2.commit_sha
        assert rewind_node.payload["rewind_from"] == n3.commit_sha
        assert rewind_node.payload["reason"] == "bad turn at t3"

    def test_rewind_records_in_trail(self):
        engine = DAGEngine()
        session = engine.create_session()
        n1 = engine.commit_turn(session, TurnRole.USER, {"text": "t1"})
        n2 = engine.commit_turn(session, TurnRole.USER, {"text": "t2"})

        engine.rewind(session, n1.commit_sha, reason="revert")

        trail = engine.get_trail(session)
        assert trail[-1].role == TurnRole.REWIND

    def test_rewind_invalid_sha_raises(self):
        engine = DAGEngine()
        session = engine.create_session()
        engine.commit_turn(session, TurnRole.USER, {"text": "t1"})

        with pytest.raises(ValueError, match="not found"):
            engine.rewind(session, "nonexistent-sha", reason="nope")


# ── TriLayerArchitecture ──────────────────────────────────────────────────────


class TestTriLayerArchitecture:
    def test_architecture_creation(self):
        dag = DAGEngine()
        arch = TriLayerArchitecture(layer1_dag=dag)
        assert arch.layer2_ledger_ref == "VAULT999"
        assert arch.layer3_index_ref == "VECTOR_INDEX"

    def test_verify_boundary(self):
        dag = DAGEngine()
        arch = TriLayerArchitecture(layer1_dag=dag)
        boundary = arch.verify_boundary()
        assert boundary["layer1_mutable"] is True
        assert boundary["layer2_immutable"] is True
        assert boundary["layer3_disposable"] is True
        assert boundary["boundary_intact"] is True

    def test_terminal_sha_for_seal(self):
        dag = DAGEngine()
        arch = TriLayerArchitecture(layer1_dag=dag)
        session = DAGSession(session_id="test")
        session.branches[session.main_branch] = []
        dag._sessions["test"] = session

        # Add subagent with terminal commit
        engine = dag  # same engine
        engine.commit_turn(session, TurnRole.USER, {"text": "main"})
        branch_ref, _ = engine.create_subagent(session, "sub1")
        node = engine.commit_turn(
            session, TurnRole.ASSISTANT, {"text": "done"}, branch_ref=branch_ref
        )

        sha = arch.terminal_sha_for_seal(session, "sub1")
        assert sha == node.commit_sha


# ── SealEvidencePayload ───────────────────────────────────────────────────────


class TestSealEvidencePayload:
    def test_payload_creation(self):
        payload = SealEvidencePayload(
            session_id="s1",
            subagent_id="worker1",
            terminal_sha="abc123",
            branch_ref="refs/agents/s1/worker1",
            turn_count=42,
            result_summary={"status": "ok"},
        )
        assert payload.terminal_sha == "abc123"
        assert payload.epistemic == EpistemicLabel.DER

    def test_to_seal_payload(self):
        payload = SealEvidencePayload(
            session_id="s1",
            subagent_id="worker1",
            terminal_sha="abc123",
            branch_ref="refs/agents/s1/worker1",
            turn_count=5,
            result_summary={"found": True},
        )
        json_str = payload.to_seal_payload()
        assert "abc123" in json_str
        assert "s1" in json_str
        assert "worker1" in json_str


# ── EpistemicLabel ────────────────────────────────────────────────────────────


def test_epistemic_labels():
    assert EpistemicLabel.OBS == "OBS"
    assert EpistemicLabel.DER == "DER"
    assert EpistemicLabel.INT == "INT"
    assert EpistemicLabel.SPEC == "SPEC"


# ── TurnRole ──────────────────────────────────────────────────────────────────


def test_turn_roles():
    assert TurnRole.USER == "user"
    assert TurnRole.SUBAGENT_SPAWN == "subagent_spawn"
    assert TurnRole.SUBAGENT_RESULT == "subagent_result"
    assert TurnRole.REWIND == "rewind"
    assert TurnRole.SEAL == "seal"


# ── Backward Compatibility — SealOutput schema ────────────────────────────────


class TestSealOutputDAGFields:
    """Verify that the new evidence_sha and reversion_event fields on SealOutput
    are backward-compatible — they default to None and don't break existing usage."""

    def test_seal_output_accepts_evidence_sha(self):
        from arifosmcp.schemas.verdict import SealOutput

        out = SealOutput(
            mode="seal",
            status="OK",
            verdict="SEAL",
            entry_id="e1",
            evidence_sha="abc123def456",
        )
        assert out.evidence_sha == "abc123def456"

    def test_seal_output_accepts_reversion_event(self):
        from arifosmcp.schemas.verdict import SealOutput

        out = SealOutput(
            mode="seal",
            status="OK",
            verdict="SEAL",
            entry_id="e1",
            reversion_event={
                "previous_sha": "old_sha",
                "reason": "bad execution path",
                "new_sha": "new_sha",
                "reverted_at": "2026-07-20T00:00:00Z",
            },
        )
        assert out.reversion_event["previous_sha"] == "old_sha"
        assert out.reversion_event["reason"] == "bad execution path"

    def test_seal_output_defaults_none(self):
        """Backward compat: without the new fields, they default to None."""
        from arifosmcp.schemas.verdict import SealOutput

        out = SealOutput(mode="seal", status="OK", verdict="SEAL", entry_id="e1")
        assert out.evidence_sha is None
        assert out.reversion_event is None
