"""F6 MARUAH producer — MARUAH_HIKMAH_RUNTIME_WIRING (2026-10-24).

F6 must never fabricate a PASS. Absence of evidence is UNMEASURED; conflict is FAIL.
"""

from __future__ import annotations

from arifosmcp.runtime.floor_producers import _f6_maruah, collect_floor_producer_signal


def _seal(payload: dict) -> dict:
    return {"actor": "888", "payload": payload}


# ── T1: no evidence ⇒ UNMEASURED, never PASS ────────────────────────────────


def test_f6_unmeasured_without_sources() -> None:
    sig = _f6_maruah({})
    assert sig["status"] == "UNMEASURED"
    assert sig["origin"] == "unmeasured_default:seal_chain_unreachable"
    assert sig["status"] != "PASS"


def test_f6_unmeasured_with_empty_seal_list() -> None:
    sig = _f6_maruah({"seals": []})
    assert sig["status"] == "UNMEASURED"


def test_f6_unmeasured_when_no_payload_carries_critique() -> None:
    sig = _f6_maruah({"seals": [_seal({"verdict": "SEAL"}), _seal({})]})
    assert sig["status"] == "UNMEASURED"
    assert sig["origin"] == "unmeasured_default:no_heart_critique"


def test_f6_registered_in_producers() -> None:
    sig = collect_floor_producer_signal("F6", sources={"seals": []})
    assert sig["floor"] == "F6"
    assert sig["status"] == "UNMEASURED"


# ── T3/T4: conflict is FAIL and is never averaged ───────────────────────────


def test_f6_dignity_conflict_fails() -> None:
    sig = _f6_maruah({"seals": [_seal({"heart_critique": {"dignity": 0.2, "coercion": False}})]})
    assert sig["status"] == "FAIL"
    assert sig["reason"] == "dignity_conflict"


def test_f6_coercion_fails() -> None:
    sig = _f6_maruah({"seals": [_seal({"heart_critique": {"dignity": 0.9, "coercion": True}})]})
    assert sig["status"] == "FAIL"
    assert sig["reason"] == "coercion_present"


def test_f6_dignity_verdict_compromised_fails() -> None:
    sig = _f6_maruah(
        {
            "seals": [
                _seal(
                    {
                        "heart_critique": {
                            "dignity": 0.95,
                            "coercion": False,
                            "dignity_verdict": "COMPROMISED",
                        }
                    }
                )
            ]
        }
    )
    assert sig["status"] == "FAIL"
    assert sig["reason"] == "dignity_verdict_compromised"


def test_f6_one_conflict_beats_three_passes() -> None:
    """The conflict cannot be diluted by other passing reviews."""
    sig = _f6_maruah(
        {
            "seals": [
                _seal({"heart_critique": {"dignity": 0.9, "coercion": False}}),
                _seal({"heart_critique": {"dignity": 0.9, "coercion": False}}),
                _seal({"heart_critique": {"dignity": 0.9, "coercion": True}}),
                _seal({"heart_critique": {"dignity": 0.9, "coercion": False}}),
            ]
        }
    )
    assert sig["status"] == "FAIL"


# ── complete review passes, and only then ──────────────────────────────────


def test_f6_complete_review_passes() -> None:
    sig = _f6_maruah(
        {
            "seals": [
                _seal(
                    {
                        "heart_critique": {
                            "dignity": 0.9,
                            "coercion": False,
                            "reviewer": "arif",
                        }
                    }
                )
            ]
        }
    )
    assert sig["status"] == "PASS"


# ── T7: reads declared keys only — no inference ────────────────────────────


def test_f6_ignores_undeclared_person_fields() -> None:
    critique = {
        "dignity": 0.9,
        "coercion": False,
        "reviewer": "arif",
        "motive": "greed",
        "diagnosis": "narcissism",
        "identity": "X",
    }
    sig = _f6_maruah({"seals": [_seal({"heart_critique": critique})]})
    blob = repr(sig)
    for forbidden in ("greed", "narcissism", "identity"):
        assert forbidden not in blob
