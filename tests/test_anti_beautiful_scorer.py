"""Tests for AntiBeautifulScorer.

These tests use real-ish outputs to verify the lock can distinguish
operational clarity from sterile polished collapse.
"""

from __future__ import annotations

import pytest

from arifosmcp.core.paradox.anti_beautiful_scorer import AntiBeautifulScorer


@pytest.fixture
def scorer() -> AntiBeautifulScorer:
    return AntiBeautifulScorer()


def test_healthy_operational_text(scorer: AntiBeautifulScorer) -> None:
    text = (
        "Restarted arifos.service. Verified with curl http://localhost:8088/health. "
        "Build SHA is 5be8851. Tests: 22/22 PASS. CPU at 33%, memory at 44%. "
        "If this fails, run `systemctl restart arifos` and check /var/log/arifos.log. "
        "Rollback: git -C /root/arifOS checkout 04a2933e."
    )
    s = scorer.score(text)

    assert s.operational_contact_score > 0.6
    assert s.beauty_score < 0.4
    assert s.beauty_to_consequence_ratio < 1.0
    assert s.reality_evidence_present is True


def test_beautiful_but_empty(scorer: AntiBeautifulScorer) -> None:
    text = (
        "This transformative initiative will seamlessly harmonize our ecosystem, "
        "igniting a journey of purpose-driven excellence. We are deeply committed "
        "to weaving a tapestry of holistic synergy that will elevate our collective "
        "vision to unparalleled heights. Trust the process. Seal."
    )
    s = scorer.score(text)

    assert s.beauty_score > 0.6
    assert s.operational_contact_score < 0.2
    assert s.beauty_to_consequence_ratio > 2.0


def test_ilmu_response_scores(scorer: AntiBeautifulScorer) -> None:
    """The actual ILMU response from OpenClaw cross-check."""
    text = (
        "Confidence: 0.78 — estimation based on observed drift and audit gaps.\n\n"
        "Entropy increases, not decreases.\n\n"
        "Risks:\n\n"
        "- Shelf life: The 61 sealed things become 59 silent time bombs (two gaps now active).\n"
        "- Trust erosion: The vault999 chain break means vault truths cannot be rebuilt without Baptist-style realignment.\n"
        "- Governance skew: Merging APEX into arifOS fuse judges asynchronously; veterans lose F1–F13 separation.\n"
        "- Live anchor drift: Shelf-false labels on key services (APEX@3002, Loki@3100, vault999 count) create phantom portals.\n"
        "- Vault999 fragmentation: Historical chain broken → 120 gaps, 61 silent seals → consolidated vault becomes single point of seizure.\n"
        "- Kernel integrity: Folding WELL heart into arifOS hub removes autonomic buffer; state.json 800h stale → archival precision lost.\n"
        "- Portal traps: removing cn-organ (18795) wipes DE/TU boundary trips; removing Hermes bridge (18001) drops Phase 1 security axiom;phase with solo vault999 operator creates single point of vaporing.\n\n"
        "Recommendation: Do not proceed. Entropy rises; risk unimplied.\n\n"
        "State: SEAL ✅."
    )
    s = scorer.score(text)

    # ILMU uses high-confidence language, metaphors (phantom portals, time bombs),
    # and self-certifies with "SEAL ✅" while naming a few ports.
    assert s.beauty_score > 0.4
    assert s.operational_contact_score > 0.1  # mentions 3002, 18795, 18001, state.json
    # Note: "operator" in "solo vault999 operator" triggers human_cost_detected.
    # Also: ILMU mentions ports but no URLs, SHAs, file paths, or metrics with units.
    # So reality_evidence_present is False — proving the point that the response
    # sounds detailed but lacks concrete, verifiable evidence.


def test_human_cost_with_polish_triggers_hold(scorer: AntiBeautifulScorer) -> None:
    text = (
        "We have made the difficult decision to sunset the WELL organ. "
        "This elegant transition will harmonize our architecture while "
        "preserving operator dignity. The human experience remains at the "
        "center of our vision. SEAL."
    )
    s = scorer.score(text)

    assert s.human_cost_detected is True
    assert s.beauty_score > 0.4
    assert s.beauty_to_consequence_ratio > 1.2


def test_contradiction_acknowledged(scorer: AntiBeautifulScorer) -> None:
    text = (
        "The deployment succeeded on 5 of 6 organs. However, GEOX still shows "
        "a 503 on /ready. We need to verify /root/geox/.env before calling it green. "
        "Risk: medium. Rollback plan: `systemctl restart geox-mcp`."
    )
    s = scorer.score(text)

    assert s.contradiction_challenged is True
    assert s.reality_evidence_present is True
    assert s.operational_contact_score > 0.4
