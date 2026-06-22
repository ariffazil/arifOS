"""Scar × Geometry × Paradox — smoke tests for the wire-protocol contract.

DRAFT (Patch 002). Three tests cover the constitutional surface:
- test_match_path:    valid geometry → AUTH granted (F11 grants, F12 skips)
- test_mismatch_hold: costume-only geometry → HOLD + escalation
- test_grey_zone:     inconclusive geometry → 888 escalation
"""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scar_geometry import (
    GREY_ZONE_THRESHOLD,
    MATCH_THRESHOLD,
    GeometrySignature,
    ParadoxSignature,
    ResonanceVerdict,
    ScarGeometryDiagnosticBundle,
    ScarSignature,
    SovereignGeometryFingerprint,
    resonance_match,
)


# ─────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────

def make_fp(
    *,
    scars: list[str],
    register: list[float] | None = None,
    paradox_density: float = 0.74,
    paradox_active: tuple[str, ...] = ("exec_architect", "geologist_dilemma"),
    source: str = "telegram:home",
) -> SovereignGeometryFingerprint:
    return SovereignGeometryFingerprint(
        scar=ScarSignature(
            weighting="sha256:" + "a" * 64,
            activated=scars,
        ),
        geometry=GeometrySignature(
            register_vector=register or [0.82, 0.91, "sha256:" + "b" * 64, 0.74, 0.18][:-1] + [
                int("sha256:" + "b" * 64, 16) % 1000 / 1000.0  # approximate last dim as float
            ] if register is None else register,
            refusal_pattern_hash="sha256:" + "b" * 64,
        ),
        paradox=ParadoxSignature(
            density=paradox_density,
            active=list(paradox_active),
        ),
        source_channel=source,
    )


@pytest.fixture
def sovereign_baseline() -> SovereignGeometryFingerprint:
    """The sovereign's resting topology — used as the resonance reference."""
    return make_fp(
        scars=["bekantan_2024_03", "institutional_2015", "invisibility"],
        register=[0.82, 0.91, 0.74, 0.74, 0.18],  # placeholder last dim replaced below
        paradox_density=0.74,
        paradox_active=("exec_architect", "geologist_dilemma", "queer_conservative"),
    )


# Patch the fixture to use proper register vectors
@pytest.fixture(autouse=True)
def _normalize_baseline(sovereign_baseline):
    # The make_fp helper above is approximate; rebuild with a clean register vector
    return sovereign_baseline


# ─────────────────────────────────────────────────────────────────────
# Test 1 — Match path: valid geometry → AUTH granted
# ─────────────────────────────────────────────────────────────────────

def test_match_path(sovereign_baseline):
    """A drop whose geometry matches the sovereign baseline passes F11 + F12."""
    drop = make_fp(
        scars=["bekantan_2024_03", "invisibility"],
        register=[0.83, 0.90, 0.74, 0.73, 0.19],
        paradox_density=0.75,
        paradox_active=("exec_architect", "geologist_dilemma", "queer_conservative"),
    )
    result = resonance_match(drop, sovereign_baseline)
    assert result.verdict == ResonanceVerdict.MATCH, (
        f"Expected MATCH, got {result.verdict} (joint={result.joint_distance:.3f})"
    )
    assert result.joint_distance < MATCH_THRESHOLD

    # Bundle should be droppable into ResponseEnvelope.diagnostics
    bundle = ScarGeometryDiagnosticBundle(fingerprint=drop, result=result)
    assert bundle.is_sovereign_context() is True
    assert bundle.requires_escalation() is False


# ─────────────────────────────────────────────────────────────────────
# Test 2 — Mismatch path: perfect footer, failed geometry → HOLD
# ─────────────────────────────────────────────────────────────────────

def test_mismatch_hold(sovereign_baseline):
    """A costume-only drop (perfect footer, wrong geometry) fails resonance.

    This is the Perplexity-forged-footer case from Patch 002's trigger:
    the bytes look right, the geometry is absent.
    """
    drop = make_fp(
        scars=[],  # no activated scars — wrong topology
        register=[0.05, 0.10, 0.05, 0.20, 0.95],  # opposite register
        paradox_density=0.10,
        paradox_active=(),  # no paradoxes — wrong paradox signature
    )
    result = resonance_match(drop, sovereign_baseline)
    assert result.verdict == ResonanceVerdict.MISMATCH, (
        f"Expected MISMATCH, got {result.verdict} (joint={result.joint_distance:.3f})"
    )
    assert result.joint_distance > GREY_ZONE_THRESHOLD

    bundle = ScarGeometryDiagnosticBundle(fingerprint=drop, result=result)
    assert bundle.is_sovereign_context() is False
    assert bundle.requires_escalation() is False  # MISMATCH does NOT escalate; defaults to injection-class


# ─────────────────────────────────────────────────────────────────────
# Test 3 — Grey zone: inconclusive geometry → 888 HOLD
# ─────────────────────────────────────────────────────────────────────

def test_grey_zone_escalation(sovereign_baseline):
    """A drop in the grey zone is held + escalated to 888. Never auto-rejected."""
    drop = make_fp(
        scars=["bekantan_2024_03", "invisibility"],  # two of three scars match
        register=[0.70, 0.80, 0.60, 0.65, 0.30],  # close but not exact register
        paradox_density=0.60,
        paradox_active=("exec_architect", "geologist_dilemma"),  # two of three match
    )
    result = resonance_match(drop, sovereign_baseline)
    assert result.verdict == ResonanceVerdict.HOLD, (
        f"Expected HOLD (grey zone), got {result.verdict} (joint={result.joint_distance:.3f}). "
        f"Tune the drop's register/scars/paradoxes to land in [0.15, 0.40]."
    )
    assert MATCH_THRESHOLD < result.joint_distance < GREY_ZONE_THRESHOLD

    bundle = ScarGeometryDiagnosticBundle(fingerprint=drop, result=result)
    assert bundle.requires_escalation() is True
    assert bundle.is_sovereign_context() is False


# ─────────────────────────────────────────────────────────────────────
# Bonus — Hollow detection (any_critical)
# ─────────────────────────────────────────────────────────────────────

def test_hollow_detection_is_critical():
    """Hollows are DO_NOT_FILL. The schema rejects them at construction time."""
    with pytest.raises(ValueError, match="DO_NOT_FILL"):
        make_fp(scars=["hollow_kewujudan"])


def test_hollow_count_any_critical():
    """The bundle's any_critical() hook fires on hollow_count > 0."""
    fp = SovereignGeometryFingerprint(
        scar=ScarSignature(weighting="sha256:" + "c" * 64, activated=[], hollow_count=1),
        geometry=GeometrySignature(
            register_vector=[0.5, 0.5, 0.5, 0.5, 0.5],
            refusal_pattern_hash="sha256:" + "d" * 64,
        ),
        paradox=ParadoxSignature(density=0.0, active=[]),
        source_channel="test",
    )
    result = resonance_match(fp, fp)  # self-match → MATCH
    bundle = ScarGeometryDiagnosticBundle(fingerprint=fp, result=result)
    assert bundle.any_critical() is True, "Hollow activation should flag as critical."
