"""
vault_verify.py — Public VAULT verification endpoint.

Exposes two public surfaces:
  GET /999/verify           — clean JSON proof for external agents (HEAD hash + chain status)
  GET /.well-known/arifos-vault-verify.json — legacy manifest for older consumers

Both routes: PUBLIC, OBSERVE_ONLY, no session or token required.
No raw receipts, no private data, no internal traces.

F9 compliance: every claim on the /999 page is backed by a live, checkable value here.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# ── Canonical vault chain module (F-004) ─────────────────────────────────────
# Import deferred inside functions to avoid startup failures if vault dir is missing.
VAULT_DIR = Path("/root/.local/share/arifos/vault999")


def _run_verify() -> dict[str, Any]:
    """Run canonical chain verify using the F-004 module. Never raises."""
    try:
        from arifosmcp.runtime.canonical_vault_chain import (
            derive_head,
            verify_chain,
        )

        result = verify_chain(VAULT_DIR, scope="canonical")
        head = derive_head(VAULT_DIR)

        return {
            "ok": True,
            "verified": result.verified,
            "status": str(result.status),
            "entries": result.entries,
            "canonical_entries": result.canonical_entries,
            "historical_entries": result.historical_entries,
            "corrupt_lines": result.corrupt_lines,
            "gap_count": len(result.gaps),
            "head_hash": result.head_hash or head.get("hash"),
            "head_seq": result.head_seq if result.head_seq is not None else head.get("seq"),
            "head_actor": head.get("actor"),
            "head_timestamp": head.get("timestamp"),
            "failure_classes": result.failure_classes,
            "ledger_path": result.ledger_path,
        }
    except Exception as exc:
        return {
            "ok": False,
            "verified": False,
            "status": "error",
            "error": str(exc),
            "head_hash": None,
            "head_seq": None,
        }


# ── /999/verify — the endpoint that makes §2 honest ──────────────────────────


def get_vault_proof() -> dict[str, Any]:
    """
    Public proof response for GET /999/verify.

    Returns the minimum necessary to make 999-CLAIM-001 externally falsifiable:
      - head_hash:    sha256 of the latest seal (embed this on the /999 page)
      - head_seq:     sequence number of latest seal (count of canonical seals)
      - verified:     True only if verify_chain() passes with zero gaps
      - chain_status: human-readable status string
      - verified_at:  ISO timestamp of this check

    An external agent can:
      1. Fetch this JSON → record head_hash + verified_at
      2. Fetch again the next day → compare head_hash (chain grew = activity)
      3. Compare head_hash across independent observers (cross-verification)
      4. If verified=False, chain_integrity is broken → 999-CLAIM-001 falsified
    """
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    v = _run_verify()

    return {
        # ── Core proof (the one line that matters) ────────────────────────
        "head": v.get("head_hash"),
        "head_seq": v.get("head_seq"),
        # ── Integrity ─────────────────────────────────────────────────────
        "verified": v.get("verified", False),
        "chain_status": v.get("status", "unknown"),
        "gap_count": v.get("gap_count", 0),
        "canonical_entries": v.get("canonical_entries", 0),
        # ── Metadata ──────────────────────────────────────────────────────
        "last_seal": v.get("head_timestamp"),
        "last_actor": v.get("head_actor"),
        "verified_at": now,
        "public": True,
        "vault": "VAULT999",
        "constitution": "F1–F13",
        # ── Falsification ─────────────────────────────────────────────────
        "falsification": {
            "how_to_falsify_001": (
                "Record head_hash now. Alter any sealed record. "
                "Fetch /999/verify again — chain_status will show GAPS_FOUND "
                "and verified will be False. This breaks 999-CLAIM-001."
            ),
            "how_to_cross_verify": (
                "Compare head_hash returned by this endpoint with the value "
                "embedded in the /999 page HTML (id=vault-head-hash). "
                "They must match within one seal cycle (~seconds). "
                "A mismatch means the page is stale or the chain diverged."
            ),
            "companion": "https://arif-fazil.com/000/",
        },
        # ── Internal (not exposed on page, but available to agents) ───────
        "_meta": {
            "failure_classes": v.get("failure_classes", {}),
            "corrupt_lines": v.get("corrupt_lines", 0),
            "historical_entries": v.get("historical_entries", 0),
            "ledger": v.get("ledger_path", str(VAULT_DIR / "seal_chain.jsonl")),
        },
    }


# ── /.well-known/arifos-vault-verify.json — legacy surface ───────────────────


def get_vault_verification_manifest() -> dict[str, Any]:
    """Legacy manifest for /.well-known/arifos-vault-verify.json consumers."""
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    v = _run_verify()

    manifest: dict[str, Any] = {
        "endpoint": "/.well-known/arifos-vault-verify.json",
        "spec_version": "vault-verify.v2",
        "generated_at": now,
        "access": "PUBLIC — OBSERVE_ONLY, no session or token required",
        "chain": {
            "total_entries": v.get("entries", 0),
            "canonical_entries": v.get("canonical_entries", 0),
            "historical_entries": v.get("historical_entries", 0),
            "corrupt_lines": v.get("corrupt_lines", 0),
            "chain_integrity": (
                "VERIFIED" if v.get("verified") else f"DEGRADED — {v.get('status', 'unknown')}"
            ),
            "gap_count": v.get("gap_count", 0),
            "head_hash": v.get("head_hash"),
            "head_seq": v.get("head_seq"),
            "head_actor": v.get("head_actor"),
            "head_timestamp": str(v.get("head_timestamp", "unknown"))[:19],
            "failure_classes": v.get("failure_classes", {}),
        },
        "verification": {
            "how_to_verify": [
                "1. GET /999/verify — machine-readable proof (head hash, chain status)",
                "2. Record head_hash + verified_at",
                "3. Fetch again tomorrow — compare head_hash (chain grew = activity proof)",
                "4. verified=False means chain_integrity is broken (CLAIM-001 falsified)",
                "5. Cross-verify: compare head_hash with value in /999 page HTML #vault-head-hash",
            ],
            "canonical_endpoint": "/999/verify",
            "operator_endpoints": {
                "verify": "/api/observatory/v1/seal/verify",
                "replay": "/api/observatory/v1/seal/replay",
            },
            "auth_required_for_operator": "X-Op-Token header (SHA-256 hash verified)",
        },
    }
    return manifest


# ── FastAPI / Starlette route handlers ───────────────────────────────────────


async def vault_proof_endpoint(request: Any) -> Any:
    """ASGI handler: GET /999/verify — clean public proof."""
    from starlette.responses import JSONResponse

    proof = get_vault_proof()
    return JSONResponse(
        proof,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "public, max-age=60",  # 60s — proof should be fresh
        },
    )


async def vault_verify_endpoint(request: Any) -> Any:
    """ASGI handler: GET /.well-known/arifos-vault-verify.json — legacy manifest."""
    from starlette.responses import JSONResponse

    manifest = get_vault_verification_manifest()
    return JSONResponse(
        manifest,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "public, max-age=300",
        },
    )
