"""Critique gate — MARUAH_HIKMAH_RUNTIME_WIRING (2026-10-24).

A consequential action (MUTATE / IRREVERSIBLE) may not return better than HOLD
without an admissible heart_critique. The cap only ever moves a verdict DOWN,
and a complete critique authorizes nothing.
"""

from __future__ import annotations

from arifosmcp.runtime.tools import _cap_critique, _critique_admissibility

GOOD = {"dignity": 0.9, "coercion": False, "reviewer": "arif"}


# ── T2: consequential action without critique ⇒ HOLD ───────────────────────


def test_mutate_without_critique_is_hold() -> None:
    out = _cap_critique({"verdict": "SEAL"}, "MUTATE", None)
    assert out["verdict"] == "HOLD"
    assert out["error_code"] == "CRITIQUE_ABSENT"
    assert out["critique_gate"]["status"] == "ABSENT"


def test_irreversible_without_critique_is_hold() -> None:
    out = _cap_critique({"verdict": "SEAL"}, "IRREVERSIBLE", None)
    assert out["verdict"] == "HOLD"
    assert out["error_code"] == "CRITIQUE_ABSENT"


def test_incomplete_critique_is_hold() -> None:
    out = _cap_critique({"verdict": "SEAL"}, "MUTATE", {"dignity": 0.9})
    assert out["verdict"] == "HOLD"
    assert out["error_code"] == "CRITIQUE_INCOMPLETE"


def test_self_attested_critique_is_hold() -> None:
    out = _cap_critique({"verdict": "SEAL"}, "MUTATE", {**GOOD, "self_attested": True})
    assert out["verdict"] == "HOLD"
    assert out["error_code"] == "CRITIQUE_SELF_ATTESTED"


def test_critique_without_reviewer_is_hold() -> None:
    out = _cap_critique({"verdict": "SEAL"}, "MUTATE", {"dignity": 0.9, "coercion": False})
    assert out["verdict"] == "HOLD"
    assert out["error_code"] == "CRITIQUE_SELF_ATTESTED"


# ── T3/T4: dignity conflict and coercion ⇒ HOLD ────────────────────────────


def test_low_dignity_is_hold() -> None:
    out = _cap_critique({"verdict": "SEAL"}, "MUTATE", {**GOOD, "dignity": 0.2})
    assert out["verdict"] == "HOLD"
    assert out["error_code"] == "CRITIQUE_DIGNITY_CONFLICT"


def test_dignity_verdict_compromised_is_hold() -> None:
    out = _cap_critique({"verdict": "SEAL"}, "MUTATE", {**GOOD, "dignity_verdict": "COMPROMISED"})
    assert out["verdict"] == "HOLD"
    assert out["error_code"] == "CRITIQUE_DIGNITY_CONFLICT"


def test_coercion_is_hold() -> None:
    out = _cap_critique({"verdict": "SEAL"}, "MUTATE", {**GOOD, "coercion": True})
    assert out["verdict"] == "HOLD"
    assert out["error_code"] == "CRITIQUE_COERCION"


# ── T5: a complete critique authorizes nothing ─────────────────────────────


def test_complete_critique_does_not_upgrade_hold() -> None:
    out = _cap_critique({"verdict": "HOLD"}, "MUTATE", GOOD)
    assert out["verdict"] == "HOLD"
    assert "critique_gate" not in out


def test_complete_critique_does_not_upgrade_void() -> None:
    out = _cap_critique({"verdict": "VOID"}, "IRREVERSIBLE", GOOD)
    assert out["verdict"] == "VOID"


def test_complete_critique_leaves_seal_alone_but_adds_no_authority() -> None:
    out = _cap_critique({"verdict": "SEAL"}, "MUTATE", GOOD)
    assert out["verdict"] == "SEAL"
    assert "critique_gate" not in out
    assert "seal_verdict_id" not in out


def test_cap_never_touches_888_hold() -> None:
    out = _cap_critique({"verdict": "888_HOLD"}, "IRREVERSIBLE", None)
    assert out["verdict"] == "888_HOLD"


# ── T8: low-risk paths unchanged ───────────────────────────────────────────


def test_low_risk_action_classes_not_gated() -> None:
    for cls in (None, "OBSERVE", "DRAFT", "OBSERVE_ONLY", "READ"):
        assert _critique_admissibility(cls, None)[0] == "NOT_REQUIRED"
        assert _cap_critique({"verdict": "SEAL"}, cls, None)["verdict"] == "SEAL"


def test_admissibility_matrix() -> None:
    assert _critique_admissibility("MUTATE", None)[0] == "ABSENT"
    assert _critique_admissibility("MUTATE", {"dignity": 1})[0] == "INCOMPLETE"
    assert _critique_admissibility("MUTATE", GOOD)[0] == "OK"
    assert _critique_admissibility("mutate", GOOD)[0] == "OK"  # case-insensitive
