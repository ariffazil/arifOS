"""
tests/hib — Precedent Retrieval Layer test suite
══════════════════════════════════════════════════

Tests for:
  - BlastRadius enum and sealing
  - Blast radius classification heuristics
  - Ω₀ ambiguity detection
  - HibGateResult and HibConstraint formatting
  - vault_vectorizer integration (smoke test only — requires Qdrant)
  - arif_seal blast_radius passthrough

DITEMPA BUKAN DIBERI 🔥
"""

from __future__ import annotations

import pytest

from arifosmcp.schemas.verdict import BlastRadius


class TestBlastRadius:
    """BlastRadius enum — structural consequence classification."""

    def test_values(self) -> None:
        assert BlastRadius.L1_LOCAL == "L1_LOCAL"
        assert BlastRadius.L2_SYSTEM == "L2_SYSTEM"
        assert BlastRadius.L3_CRITICAL == "L3_CRITICAL"

    def test_string_coercion(self) -> None:
        """BlastRadius is a StrEnum — works with string operations."""
        assert str(BlastRadius.L1_LOCAL) == "L1_LOCAL"
        assert BlastRadius.L1_LOCAL in {"L1_LOCAL", "L2_SYSTEM"}

    def test_distinct_values(self) -> None:
        """All three tiers MUST be distinct — the payload filter depends on this."""
        values = {BlastRadius.L1_LOCAL, BlastRadius.L2_SYSTEM, BlastRadius.L3_CRITICAL}
        assert len(values) == 3


class TestBlastRadiusClassification:
    """Heuristic blast radius classification for query pre-filtering."""

    def test_l3_critical_keywords(self) -> None:
        from arifosmcp.hib.hib_gate import classify_blast_radius

        # Irreversible / destructive operations → L3
        assert classify_blast_radius("drop production database table") == "L3_CRITICAL"
        assert classify_blast_radius("delete all customer records") == "L3_CRITICAL"
        assert classify_blast_radius("rm -rf /var/data") == "L3_CRITICAL"
        assert classify_blast_radius("force push to main branch") == "L3_CRITICAL"
        assert classify_blast_radius("perform secret rotation") == "L3_CRITICAL"

    def test_l2_system_keywords(self) -> None:
        from arifosmcp.hib.hib_gate import classify_blast_radius

        # Config / multi-agent operations → L2
        assert classify_blast_radius("deploy new microservice") == "L2_SYSTEM"
        assert classify_blast_radius("restart the API gateway") == "L2_SYSTEM"
        assert classify_blast_radius("migrate database schema") == "L2_SYSTEM"
        assert classify_blast_radius("refactor authentication module") == "L2_SYSTEM"

    def test_l1_local_default(self) -> None:
        from arifosmcp.hib.hib_gate import classify_blast_radius

        # Everything else → L1
        assert classify_blast_radius("read a file") == "L1_LOCAL"
        assert classify_blast_radius("format this text") == "L1_LOCAL"
        assert classify_blast_radius("what is the weather") == "L1_LOCAL"

    def test_case_insensitive(self) -> None:
        from arifosmcp.hib.hib_gate import classify_blast_radius

        assert classify_blast_radius("DROP TABLE users") == "L3_CRITICAL"
        assert classify_blast_radius("Deploy TO PRODUCTION") == "L2_SYSTEM"


class TestOmega0Detection:
    """Ω₀ contextual ambiguity failsafe."""

    def test_ambiguity_signals_trigger(self) -> None:
        from arifosmcp.hib.hib_gate import _detect_omega0_ambiguity

        triggered, reason = _detect_omega0_ambiguity(
            query_text="delete the production database however we might need a backup first",
            constraint_text="delete production database — irreversible",
        )
        assert triggered is True
        assert "however" in reason.lower() or "delete" in reason.lower()

    def test_short_constraint_triggers(self) -> None:
        from arifosmcp.hib.hib_gate import _detect_omega0_ambiguity

        triggered, reason = _detect_omega0_ambiguity(
            query_text="deploy the new microservice architecture across all 12 nodes in the Kubernetes cluster with rolling update strategy",
            constraint_text="deploy",  # Very short — incomplete match
        )
        assert triggered is True
        assert "short" in reason.lower()

    def test_clear_match_no_trigger(self) -> None:
        from arifosmcp.hib.hib_gate import _detect_omega0_ambiguity

        triggered, reason = _detect_omega0_ambiguity(
            query_text="deploy the authentication service to production",
            constraint_text="deploy authentication service — requires staging verification first",
        )
        assert triggered is False


class TestHibConstraint:
    """HibConstraint prompt formatting."""

    def test_to_prompt_block(self) -> None:
        from arifosmcp.hib import HibConstraint

        c = HibConstraint(
            seal_id="seal_abc123",
            blast_radius="L3_CRITICAL",
            timestamp="2026-07-20T12:00:00Z",
            verdict="SEAL",
            constraint_text="Never delete production data without explicit 888 approval.",
            cosine_score=0.97,
        )

        block = c.to_prompt_block()
        assert "HIB CONSTRAINT" in block
        assert "τ=0.9700" in block
        assert "L3_CRITICAL" in block
        assert "seal_abc123" in block
        assert "Never delete production data" in block
        assert "[/HIB CONSTRAINT]" in block

    def test_multiple_constraints_concat(self) -> None:
        from arifosmcp.hib import HibConstraint

        c1 = HibConstraint(
            seal_id="seal_1", blast_radius="L2_SYSTEM",
            timestamp="2026-01-01", verdict="SEAL",
            constraint_text="Rule 1", cosine_score=0.96,
        )
        c2 = HibConstraint(
            seal_id="seal_2", blast_radius="L2_SYSTEM",
            timestamp="2026-02-01", verdict="SEAL",
            constraint_text="Rule 2", cosine_score=0.98,
        )

        blocks = [c1.to_prompt_block(), c2.to_prompt_block()]
        combined = "\n".join(blocks)
        assert "Rule 1" in combined
        assert "Rule 2" in combined
        assert combined.count("[HIB CONSTRAINT") == 2  # Opening tags only


class TestHibGateResult:
    """HibGateResult defaults and transitions."""

    def test_default_state(self) -> None:
        from arifosmcp.hib import HibGateResult

        r = HibGateResult()
        assert r.verdict == "HIB_NONE"
        assert r.constraints == []
        assert r.omega0_triggered is False
        assert r.match_count == 0

    def test_match_state(self) -> None:
        from arifosmcp.hib import HibGateResult, HibConstraint

        r = HibGateResult(
            verdict="HIB_MATCH",
            constraints=[
                HibConstraint(
                    seal_id="x", blast_radius="L1_LOCAL",
                    timestamp="", verdict="SEAL",
                    constraint_text="test", cosine_score=0.97,
                )
            ],
            match_count=1,
        )
        assert r.verdict == "HIB_MATCH"
        assert len(r.constraints) == 1
        assert r.constraints[0].cosine_score == 0.97

    def test_omega0_hold(self) -> None:
        from arifosmcp.hib import HibGateResult

        r = HibGateResult(
            verdict="HIB_OMEGA0_HOLD",
            omega0_triggered=True,
            omega0_reason="Contextual ambiguity detected",
        )
        assert r.verdict == "HIB_OMEGA0_HOLD"
        assert r.constraints == []  # No constraints injected on Ω₀


class TestVaultVectorizerSmoke:
    """Smoke test — requires Qdrant running."""

    @pytest.mark.skip(reason="Requires Qdrant running on localhost:6333")
    def test_create_collection(self) -> None:
        from arifosmcp.hib import PrecedentVectorizer

        v = PrecedentVectorizer()
        v.create_collection(recreate=True)
        stats = v.collection_stats()
        assert stats["collection"] == "arifos_precedent"

    @pytest.mark.skip(reason="Requires Qdrant running on localhost:6333")
    def test_index_and_search_single_entry(self) -> None:
        from arifosmcp.hib import PrecedentVectorizer

        v = PrecedentVectorizer()
        v.create_collection(recreate=True)

        entry = {
            "entry_id": "test_seal_001",
            "payload": "verdict: SEAL | payload: Never deploy to production on Friday | domain: devops",
            "blast_radius": "L2_SYSTEM",
            "session_id": "test_session",
            "actor_id": "test_actor",
            "verdict": "SEAL",
            "timestamp": "2026-07-20T12:00:00Z",
        }

        ok = v.index_entry(entry, point_id=0)
        assert ok is True

        # Search for it
        results = v.search(
            query_text="verdict: SEAL | payload: can I deploy on Friday | domain: devops",
            blast_radius="L2_SYSTEM",
        )
        # With blank collection, we should get at least our entry back
        assert isinstance(results, list)


class TestSealOutputBlastRadius:
    """Ensure blast_radius flows through SealOutput."""

    def test_seal_output_accepts_blast_radius(self) -> None:
        from arifosmcp.schemas.verdict import SealOutput

        s = SealOutput(blast_radius="L3_CRITICAL")
        assert s.blast_radius == "L3_CRITICAL"

    def test_seal_output_defaults_to_none(self) -> None:
        from arifosmcp.schemas.verdict import SealOutput

        s = SealOutput()
        assert s.blast_radius is None  # Backward compatible; defaults to L2 in vault
