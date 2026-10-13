"""Envelope 1 — canonical floor-id fold (pure, no network, no kernel).

Locks the de-alias behaviour that the canonical_floor_id() bridge in
core/shared/laws.py guarantees. If this fails in CI, the alias fold
in _wire_producer is broken regardless of whether /health is up.

No /health dependency, so this cannot false-green when the kernel is down.
"""
from core.shared.laws import canonical_floor_id


def test_f11_folds_to_l11():
    assert canonical_floor_id("F11") == "L11"


def test_f12_folds_to_l12():
    assert canonical_floor_id("F12") == "L12"


def test_f13_folds_to_l13():
    assert canonical_floor_id("F13") == "L13"


def test_f2_passes_through_unchanged():
    assert canonical_floor_id("F2") == "F2"


def test_l11_is_idempotent():
    assert canonical_floor_id("L11") == "L11"


def test_unknown_id_passes_through():
    assert canonical_floor_id("F99") == "F99"
