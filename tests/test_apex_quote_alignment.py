"""
tests/test_apex_quote_alignment.py — Layer E: APEX multiplicative alignment tests.

Forged 2026-07-19 alongside Layer A/B/C/D unification.

These tests prove:
1. APEX fingerprint is multiplicative — zero organ = G collapses to 0
2. Stage binding hard gate — QuoteStageError raised at forbidden stages
3. Council layer forced DRAFT — sovereign ratification required for promotion
4. Doctrine CONSTITUTIONAL → PROVISIONAL tier mapping works
5. Disputed attribution lifts C_dark (Pillar VI shadow governance)
6. Missing prohibited_use list = hidden shadow
7. Federation contract resource exposes all 9 namespace URIs

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import pytest

from arifosmcp.runtime.quote_registry import (
    compute_apex_fingerprint,
    compute_canon_status,
    wisdom_quote_resolve,
    QuoteStageError,
    APEX_ORGANS,
    G_DEPLOY_THRESHOLD,
    C_DARK_CEILING,
    CANON_STATUS_TIERS,
    DEFAULT_CANON_STATUS,
)


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


def _primary_verified_quote(**overrides):
    """A well-behaved primary_verified quote with all gates set."""
    q = {
        "id": "TEST_PRIMARY_001",
        "text": "Test quote",
        "attribution": {
            "speaker": "Test Speaker",
            "source_class": "PRIMARY_VERIFIED",
            "attribution_confidence": 0.95,
        },
        "classification": {
            "tradition": ["philosophy"],
            "arifos_floors": ["F2"],
            "dark_modes": [],
        },
        "usage": {
            "permitted": ["reflection", "receipt"],
            "prohibited": ["factual_evidence", "verdict_authority"],
        },
    }
    q.update(overrides)
    return q


def _disputed_quote():
    return {
        "id": "TEST_DISPUTED_001",
        "attribution": {
            "speaker": "Unknown",
            "source_class": "DISPUTED_ATTRIBUTION",
            "attribution_confidence": 0.35,
        },
        "classification": {
            "tradition": ["philosophy"],
            "arifos_floors": ["F7"],
        },
        "usage": {
            "permitted": ["reflection"],
            "prohibited": ["factual_evidence", "verdict_authority"],
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER E.1 — Multiplicative APEX
# ═══════════════════════════════════════════════════════════════════════════════


def test_apex_fingerprint_returns_seven_organs():
    """All seven conservation organs must be present in fingerprint."""
    fp = compute_apex_fingerprint(_primary_verified_quote())
    assert set(fp["organs"].keys()) == set(APEX_ORGANS)
    assert APEX_ORGANS == (
        "Reality", "Governance", "Civilization",
        "Execution", "Memory", "Witness", "Meaning",
    )


def test_apex_g_is_multiplicative_zero_organ_collapses():
    """Multiplicative invariant: zero anywhere = G collapses to 0."""
    q = _primary_verified_quote()
    # Remove tradition → Civilization = 0
    q["classification"]["tradition"] = []
    fp = compute_apex_fingerprint(q)
    assert fp["organs"]["Civilization"] == 0.0
    assert fp["G"] == 0.0
    assert fp["shadow_state"] != "GOVERNED"
    assert fp["deploy_warrant"] is False


def test_apex_g_well_behaved_quote_is_governed():
    """A clean primary_verified quote with all gates should reach GOVERNED state."""
    fp = compute_apex_fingerprint(_primary_verified_quote())
    assert fp["G"] >= G_DEPLOY_THRESHOLD, f"expected G >= {G_DEPLOY_THRESHOLD}, got {fp['G']}"
    assert fp["C_dark"] <= C_DARK_CEILING, f"expected C_dark <= {C_DARK_CEILING}, got {fp['C_dark']}"
    assert fp["shadow_state"] == "GOVERNED"
    assert fp["deploy_warrant"] is True
    assert fp["true_devil_risk"] is False


def test_apex_disputed_lifts_c_dark():
    """DISPUTED_ATTRIBUTION must elevate C_dark (Pillar VI shadow governance)."""
    fp = compute_apex_fingerprint(_disputed_quote())
    assert fp["C_dark"] > 0.20, f"expected C_dark > 0.20 for disputed, got {fp['C_dark']}"
    # Disputed with low confidence = HIDDEN or UNCHECKED, not GOVERNED
    assert fp["shadow_state"] in ("HIDDEN", "UNCHECKED")


def test_apex_missing_prohibited_list_lifts_c_dark():
    """Missing prohibited_use list = hidden shadow (Pillar VI red flag)."""
    q = _primary_verified_quote()
    q["usage"]["prohibited"] = []  # empty list = missing governance
    fp = compute_apex_fingerprint(q)
    # Should still be GOVERNED but C_dark should be ≥ 0.10 from missing_prohibited
    assert fp["C_dark"] >= 0.10
    # If C_dark crosses ceiling, becomes UNCHECKED
    if fp["C_dark"] > C_DARK_CEILING:
        assert fp["shadow_state"] != "GOVERNED"


def test_apex_fictional_voice_receipt_elevates_shadow():
    """Fictional voices for RECEIPT/RED_TEAM use must elevate shadow."""
    q = _primary_verified_quote()
    q["attribution"]["source_class"] = "FICTIONAL_VOICE"
    fp_receipt = compute_apex_fingerprint(q, intended_use="RECEIPT")
    fp_reflection = compute_apex_fingerprint(q, intended_use="REFLECTION")
    assert fp_receipt["C_dark"] > fp_reflection["C_dark"]


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER E.2 — Stage binding hard gate (Layer D)
# ═══════════════════════════════════════════════════════════════════════════════


def test_stage_binding_permits_555_heart():
    """555_HEART is permitted by default."""
    result = wisdom_quote_resolve(
        context_tags=["truth"],
        intended_use="REFLECTION",
        stage="555_HEART",
    )
    # May return no quote (NO_MATCH) but MUST NOT raise
    assert result is not None


def test_stage_binding_permits_999_receipt():
    """999_RECEIPT is permitted."""
    result = wisdom_quote_resolve(
        context_tags=["truth"],
        intended_use="RECEIPT",
        stage="999_RECEIPT",
    )
    assert result is not None


def test_stage_binding_rejects_333_think():
    """333_THINK is forbidden — quotes are not tools."""
    with pytest.raises(QuoteStageError) as exc_info:
        wisdom_quote_resolve(
            context_tags=["truth"],
            intended_use="REFLECTION",
            stage="333_THINK",
        )
    assert "333_THINK" in str(exc_info.value)
    assert "555_HEART" in str(exc_info.value)
    assert "999_RECEIPT" in str(exc_info.value)


def test_stage_binding_rejects_777_forge():
    """777_FORGE is forbidden."""
    with pytest.raises(QuoteStageError):
        wisdom_quote_resolve(
            context_tags=["truth"],
            intended_use="REFLECTION",
            stage="777_FORGE",
        )


def test_stage_binding_rejects_111_observe():
    """111_OBSERVE is forbidden."""
    with pytest.raises(QuoteStageError):
        wisdom_quote_resolve(
            context_tags=["truth"],
            intended_use="REFLECTION",
            stage="111_OBSERVE",
        )


def test_stage_binding_soft_mode_legacy_compat():
    """enforce_stage_binding=False preserves legacy soft behavior."""
    # Must NOT raise
    result = wisdom_quote_resolve(
        context_tags=["truth"],
        intended_use="REFLECTION",
        stage="333_THINK",
        enforce_stage_binding=False,
    )
    assert result is not None


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER E.3 — Canon status tier ladder (Layer C)
# ═══════════════════════════════════════════════════════════════════════════════


def test_canon_status_default_is_draft():
    """Unspecified quote defaults to DRAFT."""
    q = _primary_verified_quote()
    q.pop("ratification_status", None)
    q.pop("status", None)
    assert compute_canon_status(q) == "DRAFT"


def test_canon_status_council_forced_draft():
    """Council layer entries are FORCED DRAFT — sovereign ratification required."""
    for council_id in ["COUNCIL_GOV_01", "COUNCIL_PAR_03", "COUNCIL_VOID_10"]:
        q = {"id": council_id, "attribution": {"source_class": "PRIMARY_VERIFIED"}}
        # Even with explicit ratification hint, council layer stays DRAFT
        q["status"] = {"ratification": "CANON_SEALED"}
        assert compute_canon_status(q) == "DRAFT", (
            f"sovereign violation: {council_id} auto-promoted"
        )


def test_canon_status_doctrine_constitutional_is_provisional():
    """Doctrine entries with ratification_status=CONSTITUTIONAL map to PROVISIONAL."""
    q = {
        "id": "D_TEST",
        "ratification_status": "CONSTITUTIONAL",
        "attribution": {"source_class": "ARIFOS_DOCTRINE"},
    }
    assert compute_canon_status(q) == "PROVISIONAL"


def test_canon_status_tiers_are_frozen():
    """Tier ladder is frozen: DRAFT < PROVISIONAL < CANON_SEALED."""
    assert CANON_STATUS_TIERS == ("DRAFT", "PROVISIONAL", "CANON_SEALED")
    assert DEFAULT_CANON_STATUS == "DRAFT"


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER E.4 — ResolveResult envelope integration
# ═══════════════════════════════════════════════════════════════════════════════


def test_resolve_result_carries_apex_fingerprint():
    """ResolveResult must carry apex_fingerprint, canon_status, deploy_warrant."""
    result = wisdom_quote_resolve(
        context_tags=["humility", "truth"],
        intended_use="REFLECTION",
        stage="555_HEART",
    )
    assert hasattr(result, "apex_fingerprint")
    assert hasattr(result, "canon_status")
    assert hasattr(result, "deploy_warrant")
    assert hasattr(result, "to_dict")

    d = result.to_dict()
    assert "apex_fingerprint" in d
    assert "canon_status" in d
    assert "deploy_warrant" in d


def test_resolve_result_to_dict_keys_complete():
    """to_dict() must include all envelope fields (original + Layer A/B/C)."""
    result = wisdom_quote_resolve(
        context_tags=["truth"],
        intended_use="REFLECTION",
        stage="555_HEART",
    )
    d = result.to_dict()
    expected_keys = {
        # Original schema (F11 AUDIT — backward compatible)
        "quote", "selection_reason", "provenance_warning", "candidates_considered",
        # Layer A — APEX fingerprint
        "apex_fingerprint",
        # Layer C — canon status
        "canon_status",
        # Layer B — federation contract (deploy_warrant + wisdom_contract envelope)
        "deploy_warrant", "wisdom_contract",
    }
    assert expected_keys.issubset(d.keys()), (
        f"missing keys: {expected_keys - d.keys()}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER E.5 — Federation contract namespace (Layer B)
# ═══════════════════════════════════════════════════════════════════════════════


def test_federation_contract_resource_exposes_nine_uris():
    """wisdom_contract resource must list all 9 namespace URIs."""
    from arifosmcp.resources.wisdom_resources import register_wisdom_resources

    # Mock MCP server that captures resource registrations
    class _MockMCP:
        def __init__(self):
            self.resources = {}

        def resource(self, uri_template):
            def decorator(fn):
                self.resources[uri_template] = fn
                return fn
            return decorator

    mock = _MockMCP()
    registered = register_wisdom_resources(mock)

    expected = [
        "arifos://wisdom/quotes/all",
        "arifos://wisdom/quotes/by-floor/{floor_id}",
        "arifos://wisdom/quotes/by-tradition/{tradition}",
        "arifos://wisdom/quotes/disputed",
        "arifos://wisdom/quotes/arifos-doctrine",
        "arifos://wisdom/quotes/prohibited-uses",
        "arifos://wisdom/fingerprint/{quote_id}",
        "arifos://wisdom/canon-status/{quote_id}",
        "arifos://wisdom/contract",
    ]
    for uri in expected:
        assert uri in registered, f"missing URI: {uri}"

    contract_payload = json.loads(mock.resources["arifos://wisdom/contract"]())
    assert contract_payload["namespace"] == "arifos://wisdom"
    assert contract_payload["owner"] == "arifOS"
    assert "apex_alignment" in contract_payload
    assert contract_payload["draft_council_ids_pending_sovereign_ratification"] is True
    assert contract_payload["sealed_council_ids"] == []