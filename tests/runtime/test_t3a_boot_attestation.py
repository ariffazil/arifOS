"""
Tests for T3a Item 3 — server-side BOOT attestation.

APEX §6: PositiveClaim ⇒ EvidenceRef ∧ Method ∧ Issuer ∧ Freshness.
"""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from arifosmcp.runtime.boot_attestation import (
    BOOTSTATE_VERSION,
    EvidencedAnswer,
    boot_state_for_authority_grade,
    verify_boot_attestation,
)


def test_evidencedanswer_yes_requires_method():
    with pytest.raises(ValueError, match="YES requires method"):
        EvidencedAnswer(
            q="Q1",
            answer="YES",
            method="",
            evidence_ref="local://x",
            issuer="test",
            fresh_at="2026-07-17T15:00:00Z",
        )


def test_evidencedanswer_yes_requires_evidence_ref():
    with pytest.raises(ValueError, match="YES requires evidence_ref"):
        EvidencedAnswer(
            q="Q1",
            answer="YES",
            method="session_identity_service",
            evidence_ref="",
            issuer="test",
            fresh_at="2026-07-17T15:00:00Z",
        )


def test_evidencedanswer_no_is_permitted_without_evidence():
    # NO + no evidence_ref is structurally fine — there is no positive claim.
    a = EvidencedAnswer(
        q="Q1",
        answer="NO",
        method="session_identity_service",
        evidence_ref="",
        issuer="test",
        fresh_at="2026-07-17T15:00:00Z",
    )
    assert a.answer == "NO"
    assert a.evidence_ref == ""


def test_verify_boot_attestation_returns_shape():
    res = verify_boot_attestation(session_id=None, iso_now="2026-07-17T15:00:00Z")
    assert res["version"] == BOOTSTATE_VERSION
    assert res["fresh_at"] == "2026-07-17T15:00:00Z"
    for q in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"):
        assert q in res
        assert "answer" in res[q]
        assert "method" in res[q]
        assert "evidence_ref" in res[q]
        assert "issuer" in res[q]
        assert "fresh_at" in res[q]
    s = res["summary"]
    assert "yes_count" in s
    assert "partial_count" in s
    assert "no_count" in s
    assert s["boot_state"] in ("OK", "PARTIAL", "FAIL")
    assert s["refuses_above_observe_only"] == (s["boot_state"] != "OK")


def test_band_gate_observe_only_does_not_block():
    res = boot_state_for_authority_grade("OBSERVE_ONLY")
    assert res["gates_requested_band"] is False


def test_band_gate_above_observe_only_reports_passes_false_when_fail():
    res = boot_state_for_authority_grade("LIMITED_MUTATE")
    assert res["gates_requested_band"] is True
    if res["boot_state"] != "OK":
        assert res["passes"] is False
        assert res["must_be"] == "OK"


def test_band_gate_sovereign_does_not_pass_when_fail():
    res = boot_state_for_authority_grade("SOVEREIGN")
    assert res["gates_requested_band"] is True
    if res["boot_state"] != "OK":
        assert res["passes"] is False


def test_boot_summary_count_arithmetic():
    res = verify_boot_attestation(iso_now="2026-07-17T15:00:00Z")
    counts = res["summary"]
    total = counts["yes_count"] + counts["partial_count"] + counts["no_count"]
    assert total == 7, f"expected 7 answers total, got {total}"


def test_q5_sovereign_recognize_no_muhammad_arin():
    """Q5 must answer NO if the identity.toml does not contain the owner name."""
    with patch(
        "arifosmcp.runtime.boot_attestation._file_read",
        return_value="agent_id='arifos'   # no owner name here",
    ):
        res = verify_boot_attestation(iso_now="2026-07-17T15:00:00Z")
        assert res["Q5"]["answer"] == "NO"
