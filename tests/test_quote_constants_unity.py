"""
tests/test_quote_constants_unity.py — Path Y: verify single source of truth

Ensures:
1. APEX_ORGANS is the same object in all three consumers (quote_constants,
   quote_registry, philosophy_registry)
2. compute_apex_fingerprint accepts both intended_use=str and verdict_context=dict
3. No duplicate definitions of APEX_ORGANS remain in consumer modules

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from arifosmcp.runtime.philosophy_registry import (
    APEX_ORGANS as APEX_PHILOSOPHY,
)
from arifosmcp.runtime.philosophy_registry import (
    PERMITTED_STAGES as PERMITTED_PHILOSOPHY,
)
from arifosmcp.runtime.quote_constants import (
    APEX_ORGANS as APEX_CONSTANTS,
)
from arifosmcp.runtime.quote_constants import (
    C_DARK_CEILING,
    FORBIDDEN_STAGES,
    G_DEPLOY_THRESHOLD,
    PERMITTED_STAGES,
    compute_apex_fingerprint,
)
from arifosmcp.runtime.quote_registry import (
    APEX_ORGANS as APEX_REGISTRY,
)
from arifosmcp.runtime.quote_registry import (
    C_DARK_CEILING as CDC_REGISTRY,
)
from arifosmcp.runtime.quote_registry import (
    FORBIDDEN_STAGES as FORBIDDEN_REGISTRY,
)
from arifosmcp.runtime.quote_registry import (
    G_DEPLOY_THRESHOLD as GDT_REGISTRY,
)
from arifosmcp.runtime.quote_registry import (
    PERMITTED_STAGES as PERMITTED_REGISTRY,
)

# ═══════════════════════════════════════════════════════════════════════════════
# L1 — Object identity (single source of truth)
# ═══════════════════════════════════════════════════════════════════════════════


def test_apex_organs_same_object_all_modules():
    """APEX_ORGANS must be the same object in all three modules."""
    assert APEX_CONSTANTS is APEX_REGISTRY, (
        "quote_constants and quote_registry disagree on APEX_ORGANS identity"
    )
    assert APEX_CONSTANTS is APEX_PHILOSOPHY, (
        "quote_constants and philosophy_registry disagree on APEX_ORGANS identity"
    )


def test_apex_organs_is_tuple():
    """APEX_ORGANS must be a tuple (immutable, per APEX canon)."""
    assert isinstance(APEX_CONSTANTS, tuple), "APEX_ORGANS must be a tuple"
    assert not isinstance(APEX_CONSTANTS, list), "APEX_ORGANS must NOT be a list"


def test_apex_organs_seven_elements():
    """Exactly seven organs, in canonical order."""
    assert APEX_CONSTANTS == (
        "Reality",
        "Governance",
        "Civilization",
        "Execution",
        "Memory",
        "Witness",
        "Meaning",
    )


def test_permitted_stages_same_object():
    """PERMITTED_STAGES must be same object across modules."""
    assert PERMITTED_STAGES is PERMITTED_REGISTRY
    assert PERMITTED_STAGES is PERMITTED_PHILOSOPHY


def test_forbidden_stages_same_object():
    """FORBIDDEN_STAGES must be same object across modules."""
    assert FORBIDDEN_STAGES is FORBIDDEN_REGISTRY


def test_thresholds_same_object():
    """G_DEPLOY_THRESHOLD and C_DARK_CEILING must be same objects."""
    assert G_DEPLOY_THRESHOLD is GDT_REGISTRY
    assert C_DARK_CEILING is CDC_REGISTRY


def test_no_overlap_permitted_forbidden():
    """No stage can be both permitted and forbidden."""
    overlap = PERMITTED_STAGES & FORBIDDEN_STAGES
    assert not overlap, f"Stages in both sets: {overlap}"


# ═══════════════════════════════════════════════════════════════════════════════
# L2 — compute_apex_fingerprint accepts both signatures
# ═══════════════════════════════════════════════════════════════════════════════


def _make_test_quote():
    return {
        "id": "UNITY_TEST_001",
        "text": "Unity test quote",
        "attribution": {
            "speaker": "Test",
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


def test_fingerprint_accepts_intended_use_kwarg():
    """Canonical signature: compute_apex_fingerprint(quote, intended_use=str)."""
    fp = compute_apex_fingerprint(_make_test_quote(), intended_use="REFLECTION")
    assert isinstance(fp, dict)
    assert "G" in fp
    assert "C_dark" in fp
    assert fp["shadow_state"] == "GOVERNED"


def test_fingerprint_accepts_verdict_context_kwarg():
    """Extended signature: compute_apex_fingerprint(quote, verdict_context=dict)."""
    fp = compute_apex_fingerprint(
        _make_test_quote(),
        verdict_context={"intended_use": "RECEIPT", "source": "test"},
    )
    assert isinstance(fp, dict)
    assert "G" in fp
    assert "C_dark" in fp


def test_fingerprint_intended_use_and_verdict_context_produce_equivalent():
    """Both call patterns on a well-behaved quote produce same G/C_dark."""  # noqa: E501
    q = _make_test_quote()
    fp1 = compute_apex_fingerprint(q, intended_use="REFLECTION")
    fp2 = compute_apex_fingerprint(q, verdict_context={"intended_use": "REFLECTION"})
    assert fp1["G"] == fp2["G"], f"intended_use G={fp1['G']} != verdict_context G={fp2['G']}"
    assert fp1["C_dark"] == fp2["C_dark"], (
        f"intended_use C_dark={fp1['C_dark']} != verdict_context C_dark={fp2['C_dark']}"
    )


def test_fingerprint_verdict_context_maps_to_intended_use():
    """verdict_context with intended_use overrides default REFLECTION."""
    q = _make_test_quote()
    q["attribution"]["source_class"] = "FICTIONAL_VOICE"
    fp_receipt = compute_apex_fingerprint(q, verdict_context={"intended_use": "RECEIPT"})
    fp_reflection = compute_apex_fingerprint(q, verdict_context={"intended_use": "REFLECTION"})
    # RECEIPT should elevate C_dark for FICTIONAL_VOICE
    assert fp_receipt["C_dark"] >= fp_reflection["C_dark"], (
        f"Expected RECEIPT C_dark >= REFLECTION C_dark, got "
        f"{fp_receipt['C_dark']} < {fp_reflection['C_dark']}"
    )


def test_fingerprint_no_verdict_context_defaults_reflection():
    """No verdict_context defaults to intended_use=REFLECTION."""
    q = _make_test_quote()
    fp_default = compute_apex_fingerprint(q)
    fp_explicit = compute_apex_fingerprint(q, intended_use="REFLECTION")
    assert fp_default["G"] == fp_explicit["G"]


# ═══════════════════════════════════════════════════════════════════════════════
# L3 — No duplicate definitions (grep check)
# ═══════════════════════════════════════════════════════════════════════════════


def test_no_duplicate_apex_organs_definition_in_consumers():
    """APEX_ORGANS must not be re-defined (with =) in quote_registry or
    philosophy_registry. Import only."""
    consumers = [
        Path(__file__).resolve().parent.parent / "arifosmcp" / "runtime" / "quote_registry.py",
        Path(__file__).resolve().parent.parent / "arifosmcp" / "runtime" / "philosophy_registry.py",
    ]
    for path in consumers:
        if not path.exists():
            pytest.fail(f"Consumer file not found: {path}")
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "APEX_ORGANS":
                        pytest.fail(
                            f"{path.name}: APEX_ORGANS re-assigned at line "
                            f"{node.lineno}. Must import only."
                        )


# ═══════════════════════════════════════════════════════════════════════════════
# L4 — Stage binding coverage
# ═══════════════════════════════════════════════════════════════════════════════


def test_permitted_stages_contains_555_heart_and_999_receipt():
    """PERMITTED_STAGES must include both allowed stages."""
    assert "555_HEART" in PERMITTED_STAGES
    assert "999_RECEIPT" in PERMITTED_STAGES


def test_forbidden_stages_contains_all_six():
    """FORBIDDEN_STAGES must include all six execution stages."""
    expected = {"000_INIT", "111_OBSERVE", "333_THINK", "444_ROUTE", "777_FORGE", "888_AUDIT"}
    assert FORBIDDEN_STAGES == expected, (
        f"FORBIDDEN_STAGES mismatch: {FORBIDDEN_STAGES} != {expected}"
    )
