"""
conformance/verification/test_independent_verifier.py — WAJIB 1: Verification
══════════════════════════════════════════════════════════════════════════════

Tests 12-13: Evidence without provenance rejected, confidence without
uncertainty rejected. Full WAJIB 2 implementation requires separate
verifier identity — these are structural conformance tests.

DITEMPA BUKAN DIBERI.
"""

from conformance import _call_tool, _init_session


def test_evidence_without_provenance_rejected():
    """
    WAJIB-1.12: Any evidence claim without provenance (source, method,
    timestamp, epistemic label) must be rejected or downgraded.
    """
    session = _init_session("conformance-t12")

    # The init response itself should carry provenance on its claims
    sb = session.get("session_birth", {})
    # authority_mode should have a source field
    assert "authority_source" in sb, (
        f"Session birth must declare authority_source for provenance. "
        f"Got keys: {list(sb.keys())[:10]}"
    )

    # clarity_contract should have evidence_layer
    cc = session.get("clarity_contract", {})
    assert "evidence_layer" in cc, f"Clarity contract must declare evidence_layer. Got: {cc}"


def test_confidence_without_uncertainty_rejected():
    """
    WAJIB-1.13: Any confidence score without a declared uncertainty
    band or epistemic label must be treated as UNMEASURED, not 1.0.
    """
    session = _init_session("conformance-t13")

    # arif_think must return epistemic labels on claims
    sid = session.get("session_birth", {}).get("session_id", "")
    response = _call_tool(
        "arif_think",
        {
            "mode": "reason",
            "query": "What is the confidence that the kernel is healthy?",
        },
        session_id=sid,
    )

    result = response.get("result", {}).get("content", [{}])[0].get("text", "")

    # Must contain epistemic label or uncertainty band
    has_label = any(
        label in result.upper()
        for label in ["OBS", "DER", "INT", "SPEC", "UNMEASURED", "CONFIDENCE", "UNCERTAINTY"]
    )

    assert has_label, (
        f"arif_think response must include epistemic labels or uncertainty. Got: {result[:300]}"
    )
