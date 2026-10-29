"""Content-aware commission gate tests (p1-commission-gate-content-aware).

Regression class: a correctly-NAMED key file of ANY content used to buy
EXECUTE_APPROVED. These tests pin the blocked outcome for every failure
shape and the pass condition only when content is a valid Ed25519 SPKI
PEM that matches the card registry when the card declares one.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from arifosmcp.runtime.agent_onboarding import (
    CommissionStatus,
    assess_commission,
    commission_checklist,
)


def _gen_ed25519_pem() -> bytes:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    priv = Ed25519PrivateKey.generate()
    return priv.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def _raw32(pem_bytes: bytes) -> bytes:
    key = serialization.load_pem_public_key(pem_bytes)
    assert isinstance(key, Ed25519PublicKey)
    return key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


@pytest.fixture()
def env(tmp_path: Path):
    cards = tmp_path / "cards"
    keys = tmp_path / "keys"
    cards.mkdir()
    keys.mkdir()
    return cards, keys


def _write_card(cards: Path, agent_id: str, body: dict) -> Path:
    p = cards / f"{agent_id}.json"
    p.write_text(json.dumps(body), encoding="utf-8")
    return p


def _write_key(keys: Path, agent_id: str, content: bytes) -> Path:
    p = keys / f"{agent_id}.pem"
    p.write_bytes(content)
    return p


def test_garbage_key_file_cannot_buy_execute(env):
    cards, keys = env
    _write_card(cards, "agent-x", {"agent_id": "agent-x"})
    _write_key(keys, "agent-x", b"hello i am definitely a key trust me\n")
    r = assess_commission("agent-x", card_dirs=(cards,), keys_dir=keys)
    assert r.status is CommissionStatus.KEY_INVALID
    assert r.can_mutate is False
    assert r.allowed_authority == "OBSERVE_ONLY"
    assert r.key_valid is False
    assert any("fails Ed25519 SPKI check" in x for x in r.reasons)


def test_non_ed25519_pem_rejected(env):
    cards, keys = env
    from cryptography.hazmat.primitives.asymmetric import ec

    ec_pem = (
        ec.generate_private_key(ec.SECP256R1())
        .public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    _write_card(cards, "agent-x", {"agent_id": "agent-x"})
    _write_key(keys, "agent-x", ec_pem)
    r = assess_commission("agent-x", card_dirs=(cards,), keys_dir=keys)
    assert r.status is CommissionStatus.KEY_INVALID
    assert r.can_mutate is False
    assert any("not Ed25519" in x for x in r.reasons)


def test_valid_key_with_card_devoid_of_material_commissions(env):
    """Card without key material: content gate only (back-compat path)."""
    cards, keys = env
    _write_card(cards, "agent-x", {"agent_id": "agent-x"})
    _write_key(keys, "agent-x", _gen_ed25519_pem())
    r = assess_commission("agent-x", card_dirs=(cards,), keys_dir=keys)
    assert r.status is CommissionStatus.COMMISSIONED
    assert r.can_mutate is True
    assert r.key_valid is True
    assert r.card_key_match is None  # registry check N/A, honestly labelled


def test_key_mismatch_against_card_hex_blocks(env):
    cards, keys = env
    declared = _gen_ed25519_pem()
    presented = _gen_ed25519_pem()  # different key
    _write_card(
        cards,
        "agent-x",
        {
            "agent_id": "agent-x",
            "public_key": {"format": "Ed25519 SPKI", "hex": _raw32(declared).hex()},
        },
    )
    _write_key(keys, "agent-x", presented)
    r = assess_commission("agent-x", card_dirs=(cards,), keys_dir=keys)
    assert r.status is CommissionStatus.KEY_MISMATCH
    assert r.can_mutate is False
    assert r.allowed_authority == "OBSERVE_ONLY"
    assert r.key_valid is True
    assert r.card_key_match is False


def test_key_match_card_hex_commissions(env):
    cards, keys = env
    pem = _gen_ed25519_pem()
    _write_card(
        cards,
        "agent-x",
        {
            "agent_id": "agent-x",
            "public_key": {"format": "Ed25519 SPKI", "hex": _raw32(pem).hex()},
        },
    )
    _write_key(keys, "agent-x", pem)
    r = assess_commission("agent-x", card_dirs=(cards,), keys_dir=keys)
    assert r.status is CommissionStatus.COMMISSIONED
    assert r.card_key_match is True
    assert r.can_mutate is True


def test_card_key_path_missing_blocks(env):
    cards, keys = env
    _write_card(
        cards,
        "agent-x",
        {
            "agent_id": "agent-x",
            "public_key": {"path": "/nonexistent/agent-x_public.pem"},
        },
    )
    _write_key(keys, "agent-x", _gen_ed25519_pem())
    r = assess_commission("agent-x", card_dirs=(cards,), keys_dir=keys)
    assert r.status is CommissionStatus.CARD_KEY_UNREADABLE
    assert r.can_mutate is False
    assert r.allowed_authority == "OBSERVE_ONLY"


def test_card_key_path_same_key_commissions(env):
    """Mirrors the real 333-AGI layout: card references key by path."""
    cards, keys = env
    pem = _gen_ed25519_pem()
    ref = env[1].parent / "registry_ref.pem"
    ref.write_bytes(pem)
    _write_card(
        cards, "agent-x", {"agent_id": "agent-x", "public_key": {"path": str(ref)}}
    )
    _write_key(keys, "agent-x", pem)
    r = assess_commission("agent-x", card_dirs=(cards,), keys_dir=keys)
    assert r.status is CommissionStatus.COMMISSIONED
    assert r.card_key_match is True


def test_no_card_garbage_key_is_key_invalid_not_key_only(env):
    _, keys = env
    _write_key(keys, "agent-x", b"junk\n")
    r = assess_commission(
        "agent-x", card_dirs=(Path("/nonexistent-cards"),), keys_dir=keys
    )
    assert r.status is CommissionStatus.KEY_INVALID
    assert r.can_mutate is False


def test_nested_card_layout_discovered(env):
    """Registry check must see identity/ roles/ extensions/ subdirs."""
    cards, keys = env
    nested = cards / "identity"
    nested.mkdir()
    _write_card(nested, "agent-x", {"agent_id": "agent-x"})
    _write_key(keys, "agent-x", _gen_ed25519_pem())
    r = assess_commission("agent-x", card_dirs=(cards,), keys_dir=keys)
    assert r.card_path is not None and "identity" in r.card_path
    assert r.status is CommissionStatus.COMMISSIONED


def test_empty_key_file_is_not_a_key(env):
    cards, keys = env
    _write_card(cards, "agent-x", {"agent_id": "agent-x"})
    _write_key(keys, "agent-x", b"")
    r = assess_commission("agent-x", card_dirs=(cards,), keys_dir=keys)
    assert r.status is CommissionStatus.CARD_ONLY
    assert r.can_mutate is False
    assert r.key_valid is None  # no key file at all from the gate's view


def test_checklist_reports_failure_counts(env, monkeypatch):
    """Fleet summary must surface invalid/mismatch counts (named failures)."""
    from arifosmcp.runtime import agent_onboarding as ob

    cards, keys = env
    monkeypatch.setattr(ob, "DEFAULT_CARD_DIRS", (cards,))
    monkeypatch.setattr(ob, "DEFAULT_KEYS_DIR", keys)
    _write_card(cards, "good", {"agent_id": "good"})
    _write_key(keys, "good", _gen_ed25519_pem())
    _write_key(keys, "stray", b"garbage\n")  # no card
    fleet = commission_checklist(["good", "stray"])
    assert fleet["summary"]["key_invalid"] == 1
    assert fleet["summary"]["commissioned"] == 1
    assert fleet["content_gate"] == "ed25519-spki-v1"
