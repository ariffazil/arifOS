"""
Tests for /999/verify and the slash-routing contract.

Phase 4.1 (silk-speed-jericho, 2026-07-25): the falsification contract of
GET /999/verify was changed so that cross-verification compares the live
head_hash against the INDEPENDENT live reading at
https://aaa.arif-fazil.com/api/seal-chain/head, NOT against a static HTML
element on the /999 page (which would go stale after the next seal).

This module asserts:

  1. ``get_vault_proof()`` exposes the new cross-verify fields
     (falsification.cross_verify_endpoint, falsification.cross_verify_owner)
     and that the falsification.how_to_cross_verify string names the AAA
     endpoint, not a static HTML element.
  2. The legacy ``get_vault_verification_manifest()`` (the
     ``/.well-known/arifos-vault-verify.json`` consumer surface) also
     carries the same updated contract — no stale
     "#vault-head-hash" reference in how_to_verify.
  3. The /999/verify/ → /999/verify slash-routing redirect returns 308
     Permanent Redirect (the canonical IA contract).
  4. The dynamic-proof element on the canonical /999 source
     (``static/index.html``) renders BOTH live endpoints side-by-side
     with no static hash baked into the page. We assert against the
     static HTML's structure (not against the runtime fetch) because the
     whole point is that the page MUST NOT carry a baked-in head_hash.

Read-only. No service mutation. No vault write. No commit / push.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime.rest_routes import vault_verify  # noqa: E402
from arifosmcp.runtime.rest_routes.vault_verify import (  # noqa: E402
    CANONICAL_DID_PLACEHOLDER,
    get_vault_proof,
    get_vault_verification_manifest,
)


# ── 1) /999/verify contract — cross-verification must point to AAA ────────
def test_get_vault_proof_named_cross_verify_endpoint_is_aaa() -> None:
    proof = get_vault_proof()
    f = proof.get("falsification") or {}
    assert "cross_verify_endpoint" in f, (
        "Phase 4.1 contract: /999/verify must name the INDEPENDENT live "
        "reading at /aaa/api/seal-chain/head for cross-verification."
    )
    endpoint = f["cross_verify_endpoint"]
    assert "aaa" in endpoint, (
        f"cross_verify_endpoint must point to the AAA cockpit, got {endpoint!r}"
    )
    assert "seal-chain/head" in endpoint, (
        f"cross_verify_endpoint must be the seal-chain/head route, got {endpoint!r}"
    )


def test_get_vault_proof_how_to_cross_verify_names_aaa_not_static_html() -> None:
    proof = get_vault_proof()
    f = proof.get("falsification") or {}
    how = f.get("how_to_cross_verify", "")
    # Must reference the independent live reading at AAA
    assert "aaa" in how.lower() or "/api/seal-chain/head" in how, (
        "how_to_cross_verify must instruct the reader to compare against "
        "the AAA /api/seal-chain/head endpoint, not a static HTML element."
    )
    # The text may MENTION "static HTML" in a negative sense ("Do NOT
    # cross-verify against a static HTML element...") — that is the
    # correct Phase 4.1 contract. What it must NOT do is INSTRUCT the
    # reader to use a static HTML element as a witness.
    how_lower = how.lower()
    instructs_static_html = (
        "cross-verify against a static html" in how_lower
        or "compare with the value embedded in the /999 page html" in how_lower
        or "compare head_hash with the value embedded in" in how_lower
    )
    assert not instructs_static_html, (
        "how_to_cross_verify must not INSTRUCT the reader to cross-verify "
        "against a static HTML element on the /999 page; that element is "
        "a display convenience, not a witness. Mentioning it as something "
        "to avoid is fine."
    )
    assert "id=vault-head-hash" not in how, (
        "Phase 4.1 retired the id=vault-head-hash cross-verify contract; "
        "the page no longer embeds a single static hash."
    )


def test_get_vault_proof_carries_owner_label() -> None:
    proof = get_vault_proof()
    f = proof.get("falsification") or {}
    assert f.get("cross_verify_owner"), (
        "cross_verify_owner must be present so consumers can attribute "
        "the independent reading to its owner (AAA cockpit)."
    )


def test_get_vault_proof_keeps_head_and_verified_fields() -> None:
    """Belt-and-braces: the falsification refactor must not drop the
    head / verified / verified_at fields that the rest of the federation
    already consumes."""
    proof = get_vault_proof()
    for key in ("head", "head_seq", "verified", "chain_status", "verified_at"):
        assert key in proof, f"/999/verify lost field: {key}"


# ── 2) Legacy manifest must also use the new contract ────────────────────
def test_legacy_manifest_how_to_verify_names_aaa_not_static_html() -> None:
    manifest = get_vault_verification_manifest()
    steps = manifest.get("verification", {}).get("how_to_verify", [])
    blob = " ".join(steps)
    assert any("aaa" in s.lower() or "/api/seal-chain/head" in s for s in steps), (
        "legacy /.well-known/arifos-vault-verify.json must also point at "
        "AAA /api/seal-chain/head for cross-verification."
    )
    assert "id=vault-head-hash" not in blob, (
        "Phase 4.1 retired the static-HTML cross-verify contract; the "
        "legacy manifest must not still reference it."
    )
    assert manifest["verification"].get("cross_verify_endpoint", "").startswith("https"), (
        "legacy manifest must surface the cross_verify_endpoint as a "
        "fully-qualified URL."
    )


# ── 3) Canonical DID is exported on the module surface ───────────────────
def test_module_exposes_canonical_did_placeholder_constant() -> None:
    """The DID the falsification contract points consumers at is the
    canonical arifOS DID, surfaced as a module constant. This is a
    forward-looking contract — future slices may add a
    `cross_verify_did` field to the proof response, and the constant is
    where it would come from.
    """
    assert isinstance(CANONICAL_DID_PLACEHOLDER, str)
    assert CANONICAL_DID_PLACEHOLDER.startswith("did:"), (
        f"expected a DID-shaped constant, got {CANONICAL_DID_PLACEHOLDER!r}"
    )


# ── 4) Canonical /999 source — dynamic proof block, no baked hash ───────
def test_canonical_999_source_has_dynamic_proof_block() -> None:
    p = Path("/root/arifOS/static/index.html")
    assert p.exists(), "canonical /999 source missing"
    html = p.read_text(encoding="utf-8")
    # The block itself
    assert 'id="proofBlock"' in html, (
        "canonical /999 source must include a dynamic proof block "
        "with id=proofBlock (Phase 4.1)."
    )
    # The two source labels
    assert "/999/verify" in html
    assert "/api/seal-chain/head" in html, (
        "canonical /999 source must reference the AAA /api/seal-chain/head "
        "endpoint as the INDEPENDENT cross-verification reading."
    )
    # No static-baked head hash pattern: the page must not contain a
    # pre-rendered sha256 hex blob adjacent to the proof block. We test
    # this loosely — there is no first-party content like
    # `id="vault-head-hash"` AND it must not be rendered with a 64-char
    # hex value embedded next to it.
    assert 'id="vault-head-hash"' not in html, (
        "Phase 4.1 retired id=vault-head-hash — the canonical /999 source "
        "must not bake a static head hash into the page."
    )


def test_canonical_999_source_polls_both_endpoints() -> None:
    p = Path("/root/arifOS/static/index.html")
    html = p.read_text(encoding="utf-8")
    # Both endpoints must be in the JS polling block
    assert "PROOF_A_URL" in html and "PROOF_B_URL" in html
    assert "/999/verify" in html
    assert "aaa.arif-fazil.com/api/seal-chain/head" in html
    # The pollProof function must be wired with a setInterval
    assert "setInterval(pollProof" in html, (
        "dynamic proof block must poll both endpoints on a timer, not "
        "only on initial load."
    )


def test_canonical_999_source_proof_block_has_no_baked_hash() -> None:
    """Defence-in-depth: scan the proof block region for any 64-char hex
    string that could be a baked-in seal head. The block is small; we
    slice from `id="proofBlock"` to the next closing `</div>` and search
    that substring.
    """
    p = Path("/root/arifOS/static/index.html")
    html = p.read_text(encoding="utf-8")
    m = re.search(r'id="proofBlock".*?</div>\s*</div>', html, re.DOTALL)
    assert m, "could not isolate the proofBlock region"
    region = m.group(0)
    # A baked sha256 head is a 64-char (or 32-char truncated) hex string.
    # The dynamic block may contain the word "head" and other labels, but
    # no pre-rendered hash.
    baked_hex = re.findall(r"\b[0-9a-f]{32,64}\b", region)
    assert not baked_hex, (
        f"canonical /999 source must not bake a static hash into the "
        f"proof block; found candidate(s): {baked_hex[:3]!r}"
    )


# ── 5) Slash-routing contract — /999/verify/ → 308 → /999/verify ────────
@pytest.fixture
def rest_app():
    """A fresh Starlette app with arifOS rest routes registered."""
    from starlette.applications import Starlette  # type: ignore

    from arifosmcp.runtime.rest_routes import rest_routes as routes

    app = Starlette()
    routes.register_rest_routes(app, tool_registry={})
    return app


def test_999_verify_slash_redirects_308(rest_app) -> None:
    """The /999/verify/ path MUST 308 to /999/verify.

    308 is the right verb for canonical normalisation: it preserves the
    method and body, and signals that the trailing-slash form is
    permanent. 307 also works but 308 is the stricter contract.
    """
    from tests.conftest import SyncASGIClient

    client = SyncASGIClient(rest_app)
    r = client.get("/999/verify/", follow_redirects=False)
    assert r.status_code == 308, (
        f"/999/verify/ must return 308 Permanent Redirect, got {r.status_code}"
    )
    # Location header MUST point to the canonical /999/verify
    location = r.headers.get("location") or r.headers.get("Location") or ""
    assert location.rstrip("/").endswith("/999/verify"), (
        f"308 Location must point to /999/verify, got {location!r}"
    )


def test_999_verify_no_slash_serves_200(rest_app) -> None:
    """The canonical /999/verify (no trailing slash) must return 200.

    We do not assert on the proof payload shape here — that is covered
    by the test_999_verify module's structural tests on
    get_vault_proof(). This test only asserts the route exists and
    returns 200.
    """
    from tests.conftest import SyncASGIClient

    client = SyncASGIClient(rest_app)
    r = client.get("/999/verify", follow_redirects=False)
    assert r.status_code == 200, (
        f"/999/verify must return 200, got {r.status_code}"
    )


# ── 6) Sanity — public module surface is honest about the contract ──────
def test_vault_verify_module_docstring_documents_phase_4_1() -> None:
    src = Path(vault_verify.__file__).read_text(encoding="utf-8")
    # The cross-verify rewrite should be named in the module so a future
    # reader can find it without grepping the plan
    assert "cross_verify_endpoint" in src or "cross-verify" in src.lower(), (
        "vault_verify module must document the cross-verify contract"
    )
