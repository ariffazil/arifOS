"""Empty-evidence contract for floor producers (F13 888_HOLD repair, 2026-10-24).

THE RULE UNDER TEST
    No evidence  → UNMEASURED, never PASS.
    Junk evidence → UNMEASURED, never PASS.
    Real evidence → judged (PASS/FAIL) by the floor's own logic.

WHY THIS FILE EXISTS
    888_HOLD named "floor_producers.py lets {} become PASS". Probed at HEAD,
    in the working tree and in the deployed venv: {} and None already return
    UNMEASURED for every producer. The named defect does not reproduce.

    The leak was one level deeper and is the same failure class:

        {"seals": [{}]}                 → F5 PASS, F13 PASS
        {"seals": [{"payload": {}}]}    → F5 PASS, F13 PASS

    A seal list whose every entry is uninterpretable fell through the
    `for ... continue` loop to the PASS return. Those are exactly the two
    floors that gate SEAL, so a malformed chain could report peace and
    sovereignty. Requirement #4 of the ruling forbids it: "malformed or
    insufficient producer evidence must resolve to UNMEASURED".

WHAT A PASS HERE DOES AND DOES NOT MEAN
    These tests prove the producer does not manufacture a pass from nothing.
    They do NOT prove the live seal chain contains good seals — that is the
    chain's own question, and F6's ruling on separate registers applies.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime import floor_producers as fp

PRODUCER_FLOORS = ("F2", "F5", "F11", "F12", "F13")


# ── absent evidence ───────────────────────────────────────────────────────


@pytest.mark.parametrize("fid", PRODUCER_FLOORS)
def test_empty_dict_never_passes(fid):
    """888's named case: {} must not become PASS."""
    out = fp.collect_floor_producer_signal(fid, sources={})
    assert out["status"] == "UNMEASURED", out
    assert out["origin"].startswith("unmeasured_default")


@pytest.mark.parametrize("fid", PRODUCER_FLOORS)
def test_none_never_passes(fid):
    out = fp.collect_floor_producer_signal(fid, sources=None)
    assert out["status"] == "UNMEASURED", out


@pytest.mark.parametrize("fid", PRODUCER_FLOORS)
def test_unrelated_keys_never_pass(fid):
    out = fp.collect_floor_producer_signal(fid, sources={"junk": 1, "other": []})
    assert out["status"] == "UNMEASURED", out


# ── present-but-junk evidence (the real leak) ─────────────────────────────


@pytest.mark.parametrize("fid", ("F5", "F13"))
@pytest.mark.parametrize(
    "seals",
    [
        [{}],
        [{"payload": {}}],
        [{}, {}],
        [{}, {"unrelated": "value"}],
        [None],
        ["not-a-record"],
        [123],
    ],
    ids=[
        "empty-record",
        "empty-payload",
        "two-empty",
        "empty-plus-unrelated",
        "none-record",
        "string-record",
        "int-record",
    ],
)
def test_junk_seal_records_never_pass(fid, seals):
    """A seal list of uninterpretable records is not evidence of peace or
    sovereignty. Before the readability gate these returned PASS."""
    out = fp.collect_floor_producer_signal(fid, sources={"seals": seals})
    assert out["status"] == "UNMEASURED", out
    assert out["origin"] == "unmeasured_default:seal_records_unreadable", out


def test_empty_seal_list_is_unmeasured_not_pass():
    for fid in ("F5", "F13"):
        out = fp.collect_floor_producer_signal(fid, sources={"seals": []})
        assert out["status"] == "UNMEASURED", out
        assert out["origin"] == "unmeasured_default:seal_chain_empty", out


# ── real evidence is still judged honestly ────────────────────────────────


def test_f5_unratified_irreversible_fails():
    out = fp.collect_floor_producer_signal(
        "F5",
        sources={
            "seals": [
                {
                    "verdict": "SEAL",
                    "actor": "codex",
                    "payload": {"reversibility": "IRREVERSIBLE"},
                }
            ]
        },
    )
    assert out["status"] == "FAIL"
    assert out["reason"] == "unratified_irreversible_action"


def test_f13_machine_self_acceptance_fails():
    out = fp.collect_floor_producer_signal(
        "F13",
        sources={
            "seals": [
                {
                    "verdict": "SEAL",
                    "actor": "codex",
                    "payload": {"reversibility": "REVERSIBLE"},
                }
            ]
        },
    )
    assert out["status"] == "FAIL"
    assert out["reason"] == "machine_self_acceptance"


def test_f5_reversible_action_passes_on_real_evidence():
    out = fp.collect_floor_producer_signal(
        "F5",
        sources={
            "seals": [
                {
                    "verdict": "HOLD",
                    "actor": "codex",
                    "payload": {"reversibility": "REVERSIBLE"},
                }
            ]
        },
    )
    assert out["status"] == "PASS"


def test_f13_sovereign_actor_is_exempt_not_self_acceptance():
    out = fp.collect_floor_producer_signal(
        "F13",
        sources={"seals": [{"verdict": "SEAL", "actor": "arif", "payload": {}}]},
    )
    assert out["status"] == "PASS", out


def test_unratified_irreversible_by_sovereign_is_exempt():
    """F5/F13 share the sovereign-actor exemption — Arif ratifying his own
    irreversible action is not the failure mode the floor polices."""
    out = fp.collect_floor_producer_signal(
        "F5",
        sources={
            "seals": [
                {
                    "verdict": "SEAL",
                    "actor": "arif",
                    "payload": {"reversibility": "IRREVERSIBLE"},
                }
            ]
        },
    )
    assert out["status"] == "PASS", out


# ── the readability predicate itself ──────────────────────────────────────


@pytest.mark.parametrize(
    "record,expected",
    [
        ({}, False),
        (None, False),
        ("x", False),
        ({"payload": {}}, False),
        ({"unrelated": 1}, False),
        ({"verdict": "SEAL"}, True),
        ({"actor": "codex"}, True),
        ({"payload": {"k": "v"}}, True),
        ({"reversibility": "REVERSIBLE"}, True),
        ({"human_ratifier": "arif"}, True),
    ],
)
def test_readable_seal_predicate(record, expected):
    assert fp._readable_seal(record) is expected
