"""
Tests for DAG Cognition Model — Kernel Architecture (FORGED 2026-07-20)

Covers: session creation, subagent branching, turn commits, trailers,
rewind + reversion receipt, terminal SHA export, tri-layer boundary.
"""

from __future__ import annotations

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

# ── Session Creation ──────────────────────────────────────────────────────────


class TestSessionCreation:
    """OBS — verify DAG session lifecycle."""

    def test_create_session_defaults(self) -> None:
        engine = DAGEngine()
        session = engine.create_session()

        assert session.session_id
        assert session.main_branch == f"refs/agents/{session.session_id}"
        assert session.root_sha is None
        assert session.head_sha is None
        assert session.turn_count == 0
        assert session.main_branch in session.branches

    def test_create_session_custom_id(self) -> None:
        engine = DAGEngine()
        session = engine.create_session(session_id="test-session-001")

        assert session.session_id == "test-session-001"
        assert session.main_branch == "refs/agents/test-session-001"

    def test_create_session_with_metadata(self) -> None:
        engine = DAGEngine()
        session = engine.create_session(
            session_id="meta-session",
            metadata={"actor": "hermes-prime", "intent": "dag_test"},
        )

        assert session.metadata["actor"] == "hermes-prime"
        assert session.metadata["intent"] == "dag_test"


# ── Turn Commits ──────────────────────────────────────────────────────────────


class TestTurnCommits:
    """OBS — verify commit mechanics in the execution DAG."""

    @pytest.fixture
    def engine_and_session(self) -> tuple[DAGEngine, DAGSession]:
        engine = DAGEngine()
        session = engine.create_session(session_id="commit-test")
        return engine, session

    def test_commit_user_turn(self, engine_and_session: tuple[DAGEngine, DAGSession]) -> None:
        engine, session = engine_and_session
        node = engine.commit_turn(
            session=session,
            role=TurnRole.USER,
            payload={"text": "Hello, agent."},
        )

        assert node.role == TurnRole.USER
        assert node.turn_number == 1
        assert node.parent_sha is None  # root commit
        assert node.commit_sha
        assert session.head_sha == node.commit_sha
        assert session.root_sha == node.commit_sha
        assert session.turn_count == 1

    def test_commit_chain_forms_dag(self, engine_and_session: tuple[DAGEngine, DAGSession]) -> None:
        engine, session = engine_and_session

        n1 = engine.commit_turn(session, TurnRole.USER, {"text": "t1"})
        n2 = engine.commit_turn(session, TurnRole.ASSISTANT, {"text": "t2"})
        n3 = engine.commit_turn(session, TurnRole.TOOL_CALL, {"tool": "search"})

        # Chain integrity
        assert n2.parent_sha == n1.commit_sha
        assert n3.parent_sha == n2.commit_sha
        assert session.head_sha == n3.commit_sha
        assert session.turn_count == 3

    def test_commit_with_trailers(self, engine_and_session: tuple[DAGEngine, DAGSession]) -> None:
        engine, session = engine_and_session

        node = engine.commit_turn(
            session=session,
            role=TurnRole.ASSISTANT,
            payload={"text": "done"},
            trailers={
                "Subagent-Result": "abc123def456",
                "Token-Count": "1423",
            },
        )

        assert node.trailers["Subagent-Result"] == "abc123def456"
        assert node.trailers["Token-Count"] == "1423"

    def test_commit_epistemic_label(self, engine_and_session: tuple[DAGEngine, DAGSession]) -> None:
        engine, session = engine_and_session

        obs_node = engine.commit_turn(
            session, TurnRole.TOOL_RESULT,
            {"data": "raw"}, epistemic=EpistemicLabel.OBS,
        )
        der_node = engine.commit_turn(
            session, TurnRole.ASSISTANT,
            {"text": "computed"}, epistemic=EpistemicLabel.DER,
        )

        assert obs_node.epistemic == EpistemicLabel.OBS
        assert der_node.epistemic == EpistemicLabel.DER


# ── Subagent Branching ────────────────────────────────────────────────────────


class TestSubagentBranching:
    """DER — verify subagent spawn as child branches."""

    @pytest.fixture
    def engine_and_session(self) -> tuple[DAGEngine, DAGSession]:
        engine = DAGEngine()
        session = engine.create_session(session_id="subagent-test")
        engine.commit_turn(session, TurnRole.USER, {"text": "start"})
        engine.commit_turn(session, TurnRole.ASSISTANT, {"text": "ack"})
        return engine, session

    def test_spawn_subagent_branch(self, engine_and_session: tuple[DAGEngine, DAGSession]) -> None:
        engine, session = engine_and_session

        branch_ref, spawn_node = engine.create_subagent(
            session=session,
            subagent_id="worker-1",
            spawn_payload={"task": "analyze"},
        )

        assert "worker-1" in session.subagents
        assert branch_ref == f"refs/agents/{session.session_id}/worker-1"
        assert branch_ref in session.branches
        assert len(session.branches[branch_ref]) == 0  # empty child branch
        assert spawn_node.role == TurnRole.SUBAGENT_SPAWN

    def test_subagent_commits_on_own_branch(
        self, engine_and_session: tuple[DAGEngine, DAGSession],
    ) -> None:
        engine, session = engine_and_session

        branch_ref, _ = engine.create_subagent(session, "worker-2")

        # Commit turns on subagent branch
        n1 = engine.commit_turn(
            session, TurnRole.TOOL_CALL,
            {"tool": "read"}, branch_ref=branch_ref,
        )
        n2 = engine.commit_turn(
            session, TurnRole.TOOL_RESULT,
            {"result": "data"}, branch_ref=branch_ref,
        )

        assert len(session.branches[branch_ref]) == 2
        assert n1.parent_sha is None  # first on branch
        assert n2.parent_sha == n1.commit_sha

        # Main branch unchanged by subagent work
        # user + assistant + spawn = 3 turns on main branch
        assert session.turn_count == 3

    def test_complete_subagent_links_sha(
        self, engine_and_session: tuple[DAGEngine, DAGSession],
    ) -> None:
        engine, session = engine_and_session

        branch_ref, _ = engine.create_subagent(session, "worker-3")
        engine.commit_turn(
            session, TurnRole.TOOL_CALL,
            {"tool": "compute"}, branch_ref=branch_ref,
        )
        terminal = engine.commit_turn(
            session, TurnRole.ASSISTANT,
            {"text": "result: 42"}, branch_ref=branch_ref,
        )

        result_node = engine.complete_subagent(
            session=session,
            subagent_id="worker-3",
            result_payload={"answer": 42},
            terminal_sha=terminal.commit_sha,
        )

        assert result_node.role == TurnRole.SUBAGENT_RESULT
        assert result_node.trailers["Subagent-Result"] == terminal.commit_sha
        assert result_node.payload["terminal_sha"] == terminal.commit_sha

    def test_no_merge_pollution(self, engine_and_session: tuple[DAGEngine, DAGSession]) -> None:
        """Subagent branch commits never appear on main branch — pointer only."""
        engine, session = engine_and_session

        branch_ref, _ = engine.create_subagent(session, "worker-4")
        engine.commit_turn(session, TurnRole.TOOL_CALL, {"tool": "x"}, branch_ref=branch_ref)
        engine.commit_turn(session, TurnRole.TOOL_CALL, {"tool": "y"}, branch_ref=branch_ref)

        main_trail = engine.get_trail(session)
        for node in main_trail:
            assert node.branch_ref == session.main_branch


# ── Rewind ────────────────────────────────────────────────────────────────────


class TestRewind:
    """DER — verify rewind as pointer shift + reversion receipt."""

    @pytest.fixture
    def engine_and_session(self) -> tuple[DAGEngine, DAGSession]:
        engine = DAGEngine()
        session = engine.create_session(session_id="rewind-test")
        return engine, session

    def test_rewind_shifts_head(self, engine_and_session: tuple[DAGEngine, DAGSession]) -> None:
        engine, session = engine_and_session

        n1 = engine.commit_turn(session, TurnRole.USER, {"text": "good"})
        _n2 = engine.commit_turn(session, TurnRole.ASSISTANT, {"text": "bad response"})
        n3 = engine.commit_turn(session, TurnRole.USER, {"text": "continue"})

        assert session.head_sha == n3.commit_sha

        engine.rewind(session, target_sha=n1.commit_sha, reason="undo bad turn")

        assert session.head_sha == n1.commit_sha  # pointer shifted

    def test_rewind_creates_reversion_receipt(
        self, engine_and_session: tuple[DAGEngine, DAGSession],
    ) -> None:
        engine, session = engine_and_session

        n1 = engine.commit_turn(session, TurnRole.USER, {"text": "start"})
        engine.commit_turn(session, TurnRole.ASSISTANT, {"text": "bad"})

        rewind_node = engine.rewind(session, target_sha=n1.commit_sha, reason="correction")

        assert rewind_node.role == TurnRole.REWIND
        assert rewind_node.payload["rewind_to"] == n1.commit_sha
        assert rewind_node.payload["reason"] == "correction"

        # The rewind node itself is on the main branch — auditable
        main_trail = engine.get_trail(session)
        assert any(n.role == TurnRole.REWIND for n in main_trail)

    def test_rewind_nonexistent_sha(self, engine_and_session: tuple[DAGEngine, DAGSession]) -> None:
        engine, session = engine_and_session
        engine.commit_turn(session, TurnRole.USER, {"text": "ok"})

        with pytest.raises(ValueError, match="Target SHA"):
            engine.rewind(session, target_sha="nonexistent_sha", reason="test")


# ── Terminal SHA Export ───────────────────────────────────────────────────────


class TestTerminalSHAExport:
    """DER — verify evidence SHA export for Layer 2 sealing."""

    def test_export_terminal_sha(self) -> None:
        engine = DAGEngine()
        session = engine.create_session(session_id="export-test")
        engine.commit_turn(session, TurnRole.USER, {"text": "go"})

        branch_ref, _ = engine.create_subagent(session, "export-worker")
        engine.commit_turn(session, TurnRole.TOOL_CALL, {"tool": "read"}, branch_ref=branch_ref)
        terminal = engine.commit_turn(
            session, TurnRole.ASSISTANT,
            {"result": "done"}, branch_ref=branch_ref,
        )

        sha = engine.export_evidence_sha(session, "export-worker")
        assert sha == terminal.commit_sha

    def test_export_nonexistent_subagent(self) -> None:
        engine = DAGEngine()
        session = engine.create_session(session_id="nonexistent-test")

        sha = engine.export_evidence_sha(session, "no-such-agent")
        assert sha is None

    def test_export_empty_branch(self) -> None:
        engine = DAGEngine()
        session = engine.create_session(session_id="empty-branch")
        engine.create_subagent(session, "empty-worker")

        sha = engine.export_evidence_sha(session, "empty-worker")
        assert sha is None  # no commits on branch


# ── Tri-Layer Architecture ────────────────────────────────────────────────────


class TestTriLayerArchitecture:
    """INT — verify tri-layer boundary and bridge mechanics."""

    def test_architecture_instantiation(self) -> None:
        dag = DAGEngine()
        arch = TriLayerArchitecture(layer1_dag=dag)

        assert arch.layer1_dag is dag
        assert arch.layer2_ledger_ref == "VAULT999"
        assert arch.layer3_index_ref == "VECTOR_INDEX"
        assert "CRITICAL BOUNDARY" in arch.boundary_doc

    def test_terminal_sha_bridge(self) -> None:
        dag = DAGEngine()
        arch = TriLayerArchitecture(layer1_dag=dag)
        session = dag.create_session(session_id="bridge-test")

        dag.commit_turn(session, TurnRole.USER, {"text": "task"})
        branch_ref, _ = dag.create_subagent(session, "bridge-worker")
        terminal = dag.commit_turn(
            session, TurnRole.ASSISTANT,
            {"answer": "bridged"}, branch_ref=branch_ref,
        )

        sha = arch.terminal_sha_for_seal(session, "bridge-worker")
        assert sha == terminal.commit_sha

    def test_boundary_verification(self) -> None:
        dag = DAGEngine()
        arch = TriLayerArchitecture(layer1_dag=dag)
        verdict = arch.verify_boundary()

        assert verdict["layer1_mutable"] is True
        assert verdict["layer2_immutable"] is True
        assert verdict["layer3_disposable"] is True
        assert verdict["boundary_intact"] is True


# ── SealEvidencePayload ───────────────────────────────────────────────────────


class TestSealEvidencePayload:
    """DER — verify VAULT999 integration payload format."""

    def test_payload_serialisation(self) -> None:
        p = SealEvidencePayload(
            session_id="ses-001",
            subagent_id="worker-1",
            terminal_sha="abc123",
            branch_ref="refs/agents/ses-001/worker-1",
            turn_count=5,
            result_summary={"answer": 42},
        )

        payload_str = p.to_seal_payload()
        assert "ses-001" in payload_str
        assert "abc123" in payload_str
        assert "worker-1" in payload_str
        assert "answer" in payload_str

        # Must be valid JSON
        import json
        parsed = json.loads(payload_str)
        assert parsed["session_id"] == "ses-001"
        assert parsed["terminal_sha"] == "abc123"

    def test_payload_is_deterministic(self) -> None:
        ts = 1000000.0
        p1 = SealEvidencePayload(
            session_id="ses-001",
            subagent_id="worker-1",
            terminal_sha="abc",
            branch_ref="refs/agents/ses-001/worker-1",
            turn_count=3,
            result_summary={"done": True},
            sealed_at=ts,
        )
        p2 = SealEvidencePayload(
            session_id="ses-001",
            subagent_id="worker-1",
            terminal_sha="abc",
            branch_ref="refs/agents/ses-001/worker-1",
            turn_count=3,
            result_summary={"done": True},
            sealed_at=ts,
        )

        assert p1.to_seal_payload() == p2.to_seal_payload()


# ── Multi-Session Isolation ───────────────────────────────────────────────────


class TestMultiSessionIsolation:
    """OBS — verify sessions do not cross-contaminate."""

    def test_independent_sessions(self) -> None:
        engine = DAGEngine()

        s1 = engine.create_session(session_id="session-a")
        s2 = engine.create_session(session_id="session-b")

        engine.commit_turn(s1, TurnRole.USER, {"text": "A-1"})
        engine.commit_turn(s1, TurnRole.ASSISTANT, {"text": "A-2"})

        engine.commit_turn(s2, TurnRole.USER, {"text": "B-1"})

        assert s1.turn_count == 2
        assert s2.turn_count == 1
        assert s1.head_sha != s2.head_sha


# ── DAGNode Properties ────────────────────────────────────────────────────────


class TestDAGNodeProperties:
    """OBS — verify DAGNode data integrity."""

    def test_sha_determinism(self) -> None:
        sha1 = DAGNode.compute_sha(
            session_id="test", turn_number=1, role=TurnRole.USER,
            payload={"msg": "hello"}, parent_sha=None, timestamp=1000.0,
        )
        sha2 = DAGNode.compute_sha(
            session_id="test", turn_number=1, role=TurnRole.USER,
            payload={"msg": "hello"}, parent_sha=None, timestamp=1000.0,
        )
        assert sha1 == sha2

    def test_sha_changes_with_content(self) -> None:
        sha1 = DAGNode.compute_sha(
            session_id="test", turn_number=1, role=TurnRole.USER,
            payload={"msg": "hello"}, parent_sha=None, timestamp=1000.0,
        )
        sha2 = DAGNode.compute_sha(
            session_id="test", turn_number=1, role=TurnRole.USER,
            payload={"msg": "different"}, parent_sha=None, timestamp=1000.0,
        )
        assert sha1 != sha2

    def test_repr(self) -> None:
        node = DAGNode(
            session_id="s1", branch_ref="refs/agents/s1",
            parent_sha=None, commit_sha="abcd1234efgh5678",
            turn_number=1, role=TurnRole.USER,
            payload={"text": "hi"},
        )
        r = repr(node)
        assert "s1" in r
        assert "abcd1234" in r
        assert "user" in r
