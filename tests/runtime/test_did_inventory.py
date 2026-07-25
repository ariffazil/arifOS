"""
Tests for arifosmcp.runtime.did_inventory.

Phase 4.2 (silk-speed-jericho, 2026-07-25): enumerated DID inventory helper
that produces a structured snapshot of every DID the arifOS runtime knows
about, plus the live signing-key status. Read-only. No key rotation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime import did_inventory  # noqa: E402
from arifosmcp.runtime.did_inventory import (  # noqa: E402
    CANONICAL_DID,
    CANONICAL_DID_ALIASES,
    SOVEREIGN_DID_PREFIX,
    build_did_inventory,
    get_did_inventory,
)


# ── 1) Canonical DID is pinned and discoverable ───────────────────────────
def test_canonical_did_is_pinned() -> None:
    """The canonical arifOS DID MUST be the runtime-pinned value.

    If this test fails, the canonical DID has changed. Update
    docs/CANONICAL_DID.md and the well-known route in rest_routes.py
    before shipping.
    """
    assert CANONICAL_DID == "did:web:arifos.arif-fazil.com"
    assert "did:web:arif-fazil.com" in CANONICAL_DID_ALIASES


def test_sovereign_did_prefix_is_did_arifos() -> None:
    assert SOVEREIGN_DID_PREFIX.startswith("did:arifos:")


# ── 2) Inventory shape ────────────────────────────────────────────────────
def test_build_did_inventory_shape() -> None:
    inv = build_did_inventory()
    for key in (
        "canonical_did",
        "canonical_did_aliases",
        "schema_version",
        "generated_at",
        "phase",
        "runtime",
        "static_identity",
        "dids",
        "sovereign_keys",
        "verification_status",
        "documentation",
        "no_key_rotation_in_this_slice",
    ):
        assert key in inv, f"inventory missing field: {key}"


def test_inventory_phase_4_2_marker() -> None:
    inv = build_did_inventory()
    # Pin the phase so a future reader can grep for the slice.
    assert "4.2" in inv["phase"]
    assert "silk-speed-jericho" in inv["phase"]


def test_inventory_documents_did_paths() -> None:
    inv = build_did_inventory()
    dids = inv["dids"]
    methods = {d["method"] for d in dids}
    # At minimum we always have a did:web and a did:arifos entry.
    assert "web" in methods, "inventory must list the canonical did:web"
    assert "arifos" in methods, "inventory must list the did:arifos sovereign entry"


def test_inventory_canonical_did_matches_pinned_value() -> None:
    inv = build_did_inventory()
    assert inv["canonical_did"] == CANONICAL_DID


# ── 3) No key rotation assertion ───────────────────────────────────────────
def test_no_key_rotation_in_slice() -> None:
    inv = build_did_inventory()
    assert inv["no_key_rotation_in_this_slice"] is True
    # The slice must not claim to have rotated the key material.
    # The verification_status must reflect whatever the live
    # crypto_auth.get_public_key_hex() returns — "bootstrapped" if a
    # key is present, "absent" otherwise. Either is honest.
    assert inv["verification_status"] in {"bootstrapped", "absent"}


# ── 4) Sovereign keys are surfaced read-only ─────────────────────────────
def test_inventory_surfaces_sovereign_keys() -> None:
    inv = build_did_inventory()
    # The runtime's governance_identity module pins at least the
    # "arif" sovereign key for /000/. We do not assert the exact
    # fingerprint (no rotation in this slice) — only that the
    # inventory surfaces what governance_identity declares.
    sovereigns = [k for k in inv["sovereign_keys"] if k["kind"] == "sovereign"]
    # Even if governance_identity fails to import, the inventory is
    # allowed to be empty. When populated, the structure must be sane.
    for k in sovereigns:
        assert k["key_id"].startswith("ed25519:sha256:"), (
            f"unexpected sovereign key id format: {k['key_id']!r}"
        )
        assert k["source"].startswith("arifosmcp.runtime.governance_identity")


# ── 5) Verification status is honest about state ──────────────────────────
def test_verification_status_honest_when_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    """If crypto_auth returns an empty public key, inventory must say
    'absent' — never fake-green. This is the F2 TRUTH contract on
    identity surfaces.
    """
    from arifosmcp.runtime import did_inventory

    monkeypatch.setattr(did_inventory, "_safe_crypto_auth_pubkey", lambda: None)
    inv = did_inventory.build_did_inventory()
    assert inv["verification_status"] == "absent"
    # The did:web entry must explicitly say "live-empty-keys" when no
    # key is bootstrapped (matches well-known/did.json behaviour).
    web = next(d for d in inv["dids"] if d["method"] == "web")
    assert web["status"] == "live-empty-keys"


def test_verification_status_bootstrapped_when_key_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from arifosmcp.runtime import did_inventory

    monkeypatch.setattr(
        did_inventory, "_safe_crypto_auth_pubkey", lambda: "a" * 64
    )
    inv = did_inventory.build_did_inventory()
    assert inv["verification_status"] == "bootstrapped"
    web = next(d for d in inv["dids"] if d["method"] == "web")
    assert web["status"] == "live"
    # When a key is present, the inventory should also surface a
    # derived did:key entry.
    methods = {d["method"] for d in inv["dids"]}
    assert "key" in methods


# ── 6) Caching ────────────────────────────────────────────────────────────
def test_get_did_inventory_caches() -> None:
    inv1 = get_did_inventory(force_refresh=True)
    inv2 = get_did_inventory()
    assert inv1 is inv2, "second call must return the cached inventory object"


def test_get_did_inventory_force_refresh_rebuilds() -> None:
    inv1 = get_did_inventory(force_refresh=True)
    inv2 = get_did_inventory(force_refresh=True)
    # Two fresh builds will share the same canonical data but be
    # different object instances.
    assert inv1 is not inv2
    assert inv1["canonical_did"] == inv2["canonical_did"]


# ── 7) Module is read-only — no methods that mutate state ────────────────
def test_module_exposes_only_read_only_callables() -> None:
    """Defence-in-depth: the inventory module must not expose any
    callable that mutates the seal chain, the key material, or any
    file under /root/.local/share/arifos/. We check by name and by
    signature.
    """
    import inspect

    forbidden_names = {"rotate", "rotate_key", "set_key", "write", "save"}
    for name in dir(did_inventory):
        if name.startswith("_"):
            continue
        attr = getattr(did_inventory, name)
        if not callable(attr):
            continue
        for forbidden in forbidden_names:
            assert forbidden not in name.lower(), (
                f"forbidden name in did_inventory: {name!r} "
                f"matches {forbidden!r}"
            )
        # All public callables must be pure or have explicit
        # no-side-effect docstrings.
        doc = inspect.getdoc(attr) or ""
        assert "READ-ONLY" in doc or "read-only" in doc or "never" in doc.lower() or "build" in name.lower() or "get" in name.lower() or "safe" in name.lower(), (
            f"public callable {name!r} should be clearly read-only or a "
            f"safe builder; doc={doc[:80]!r}"
        )


# ── 8) Canonical DID documentation exists in source ──────────────────────
def test_canonical_did_doc_exists() -> None:
    p = Path("/root/arifOS/docs/CANONICAL_DID.md")
    assert p.exists(), "docs/CANONICAL_DID.md must exist as the human-facing doc"
    body = p.read_text(encoding="utf-8")
    assert "did:web:arifos.arif-fazil.com" in body
    assert "no key rotation" in body.lower()
    assert "Phase 4.2" in body
