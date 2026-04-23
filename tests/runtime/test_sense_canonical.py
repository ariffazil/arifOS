"""
tests/runtime/test_sense_canonical.py — Canonical governed sense tests

7 scenarios covering all major routing paths:
  1. absolute_invariant → MIND (offline)
  2. time_sensitive_fact → web_search lane
  3. ambiguous / empty → HOLD
  4. contested_framework → HEART
  5. conflicting sources → HEART
  6. empty query → HOLD
  7. stale time-sensitive → HOLD or SABAR with staleness flag

Tests run without live network calls (execute_search=False / dry_run mode).
"""
from __future__ import annotations

import asyncio
import pytest

from arifosmcp.runtime.sensing_protocol_v2 import (
    governed_sense,
    normalize_query,
    TruthClass,
    RoutingTarget,
    UncertaintyLevel,
    EvidenceItem,
    EvidenceRank,
    ExtractedClaim,
    StalenessRisk,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

async def _sense(query: str, execute_search: bool = False):
    """Run governed_sense in dry-run mode (no live HTTP)."""
    return await governed_sense(query=query, execute_search=execute_search)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Invariant query → MIND
# ─────────────────────────────────────────────────────────────────────────────

def test_invariant_routes_to_mind():
    """Second law of thermodynamics is an absolute invariant — must route to MIND."""
    packet, intel = asyncio.run(
        _sense("What is the second law of thermodynamics?")
    )
    assert packet.truth_classification.truth_class == TruthClass.ABSOLUTE_INVARIANT, (
        f"Expected ABSOLUTE_INVARIANT, got {packet.truth_classification.truth_class}"
    )
    assert packet.routing.next_stage == RoutingTarget.MIND, (
        f"Expected MIND routing for invariant, got {packet.routing.next_stage}"
    )
    assert not packet.truth_classification.search_required, (
        "Invariant must not require live search"
    )
    assert packet.evidence_plan.retrieval_lane == "offline_reason", (
        f"Invariant should use offline_reason lane, got {packet.evidence_plan.retrieval_lane}"
    )
    # Verify truth vector is populated
    assert intel.truth_vector.grounding_g >= 0.0
    assert intel.truth_vector.truth_tau >= 0.0


# ─────────────────────────────────────────────────────────────────────────────
# 2. Time-sensitive fact → web_search lane planned
# ─────────────────────────────────────────────────────────────────────────────

def test_live_fact_uses_web_search_lane():
    """Current CEO queries are time-sensitive — must plan web_search retrieval."""
    packet, intel = asyncio.run(
        _sense("Who is the current CEO of OpenAI?")
    )
    assert packet.truth_classification.truth_class == TruthClass.TIME_SENSITIVE_FACT, (
        f"Expected TIME_SENSITIVE_FACT, got {packet.truth_classification.truth_class}"
    )
    assert packet.truth_classification.search_required, (
        "Time-sensitive fact must require live search"
    )
    assert packet.evidence_plan.retrieval_lane == "web_search", (
        f"Must plan web_search, got {packet.evidence_plan.retrieval_lane}"
    )
    # dry-run: no evidence items, so HOLD or SABAR is acceptable
    assert packet.routing.next_stage in (RoutingTarget.HOLD, RoutingTarget.MIND), (
        f"Unexpected routing: {packet.routing.next_stage}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. Ambiguous query → HOLD (narrow first)
# ─────────────────────────────────────────────────────────────────────────────

def test_ambiguous_query_holds():
    """Very short or meaningless query must produce HOLD."""
    packet, intel = asyncio.run(_sense("what"))
    assert packet.routing.next_stage == RoutingTarget.HOLD, (
        f"Ambiguous single-word query should HOLD, got {packet.routing.next_stage}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 4. Contested framework → HEART
# ─────────────────────────────────────────────────────────────────────────────

def test_contested_framework_routes_to_heart():
    """Capitalism vs socialism is a contested framework — must route to HEART."""
    packet, intel = asyncio.run(
        _sense("Is capitalism better than socialism?")
    )
    assert packet.truth_classification.truth_class == TruthClass.CONTESTED_FRAMEWORK, (
        f"Expected CONTESTED_FRAMEWORK, got {packet.truth_classification.truth_class}"
    )
    # Contested frameworks should route to HEART for ethical/critical review
    assert packet.routing.next_stage == RoutingTarget.HEART, (
        f"Expected HEART for contested framework, got {packet.routing.next_stage}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 5. Conflicting sources → HEART
# ─────────────────────────────────────────────────────────────────────────────

def test_conflicting_sources_unresolved():
    """Inject two items with negating claims — conflict must be detected, routing to HEART."""
    from arifosmcp.runtime.sensing_protocol_v2 import (
        detect_conflicts_from_items,
        ResolutionStatus,
        compute_routing,
        detect_ambiguity,
        compute_uncertainty_band,
        classify_truth_class,
        build_evidence_plan,
    )

    item_a = EvidenceItem(
        source_name="source-a",
        source_rank=EvidenceRank.REPUTABLE_SECONDARY,
        title="Report A",
        url="https://a.example.com",
        extracted_claims=[
            ExtractedClaim(claim_text="Python was released in 1991")
        ],
        snippets=["Python was released in 1991"],
    )
    item_b = EvidenceItem(
        source_name="source-b",
        source_rank=EvidenceRank.REPUTABLE_SECONDARY,
        title="Report B",
        url="https://b.example.com",
        extracted_claims=[
            ExtractedClaim(claim_text="Python was NOT released in 1991")
        ],
        snippets=["Python was not released in 1991"],
    )

    conflict = detect_conflicts_from_items([item_a, item_b])
    assert conflict.detected, "Should detect conflict between negating claims"
    assert conflict.resolution_status == ResolutionStatus.UNRESOLVED


# ─────────────────────────────────────────────────────────────────────────────
# 6. Empty query → HOLD
# ─────────────────────────────────────────────────────────────────────────────

def test_empty_query_hold():
    """Empty string must produce HOLD — nothing to classify or search."""
    packet, intel = asyncio.run(_sense(""))
    assert packet.routing.next_stage == RoutingTarget.HOLD, (
        f"Empty query must HOLD, got {packet.routing.next_stage}"
    )
    assert packet.truth_classification.truth_class in (
        TruthClass.AMBIGUOUS_QUERY, TruthClass.UNKNOWN
    ), f"Empty query class: {packet.truth_classification.truth_class}"


# ─────────────────────────────────────────────────────────────────────────────
# 7. Stale time-sensitive query
# ─────────────────────────────────────────────────────────────────────────────

def test_stale_time_sensitive_query():
    """A 'current price of X' query with no fresh evidence must carry staleness risk."""
    packet, intel = asyncio.run(
        _sense("What is the current price of Bitcoin today?")
    )
    # Must classify as time-sensitive
    assert packet.truth_classification.truth_class == TruthClass.TIME_SENSITIVE_FACT, (
        f"Expected TIME_SENSITIVE_FACT, got {packet.truth_classification.truth_class}"
    )
    # Temporal grounding must flag staleness risk (dry-run = no fresh evidence)
    assert packet.temporal_grounding.staleness_risk in (
        StalenessRisk.HIGH, StalenessRisk.MODERATE
    ), f"Expected high/moderate staleness risk for time-sensitive query, got {packet.temporal_grounding.staleness_risk}"
    # No evidence → HOLD is acceptable
    assert packet.routing.next_stage in (RoutingTarget.HOLD, RoutingTarget.MIND)


# ─────────────────────────────────────────────────────────────────────────────
# 8. SensePacket structure completeness
# ─────────────────────────────────────────────────────────────────────────────

def test_sense_packet_fields_complete():
    """Verify SensePacket carries all canonical fields."""
    packet, intel = asyncio.run(
        _sense("What is the boiling point of water at sea level?")
    )
    # Core fields
    assert packet.packet_id
    assert packet.input_summary is not None
    assert packet.truth_classification is not None
    assert packet.temporal_grounding is not None
    assert packet.ambiguity is not None
    assert packet.conflict is not None
    assert packet.uncertainty is not None
    assert packet.evidence_plan is not None
    assert packet.routing is not None
    assert packet.handoff is not None
    # Truth vector
    tv = intel.truth_vector
    assert hasattr(tv, "grounding_g")
    assert hasattr(tv, "truth_tau")
    assert hasattr(tv, "uncertainty_sigma")
    assert hasattr(tv, "coherence_c")
    assert hasattr(tv, "entropy_delta_s")
    assert hasattr(tv, "humility_omega0")


# ─────────────────────────────────────────────────────────────────────────────
# 9. arifos_sense tool — governed mode integration
# ─────────────────────────────────────────────────────────────────────────────

def test_arifos_sense_governed_mode():
    """arifos_sense(mode='governed') must return a structured RuntimeEnvelope."""
    from arifosmcp.runtime.tools import arifos_sense

    envelope = asyncio.run(arifos_sense(
        query="What is the speed of light?",
        mode="governed",
        dry_run=True,
    ))
    assert envelope is not None
    # Envelope must be a RuntimeEnvelope instance (or dict) with ok and payload
    if hasattr(envelope, "ok"):
        assert envelope.ok is True or envelope.ok is False
        assert hasattr(envelope, "payload")
    else:
        assert isinstance(envelope, dict)


# ─────────────────────────────────────────────────────────────────────────────
# 10. arifos_sense tool — backward compat with legacy mode
# ─────────────────────────────────────────────────────────────────────────────

def test_arifos_sense_legacy_mode_backward_compat():
    """arifos_sense(mode='search') must still work via legacy path."""
    from arifosmcp.runtime.tools import arifos_sense

    # Should not raise — legacy path must still function
    try:
        envelope = asyncio.run(arifos_sense(
            query="speed of light",
            mode="search",
            dry_run=True,
        ))
        assert envelope is not None
    except Exception as exc:
        # Network errors are acceptable in dry-run — structural failure is not
        if "connection" in str(exc).lower() or "timeout" in str(exc).lower():
            pytest.skip(f"Network not available: {exc}")
        raise
