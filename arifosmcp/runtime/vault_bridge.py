"""
arifosmcp/runtime/vault_bridge.py — VAULT999 Health & Tool Bridge

DITEMPA BUKAN DIBERI — Forged, Not Given

Bridges arifOS kernel to VAULT999 API (port 8100) and writer (port 5001).
Used by organ_attestation.py to verify VAULT999 liveness, chain integrity,
and seal count during federation-wide attestation.

VAULT999 is the immutable audit ledger — not an MCP organ, but a substrate
service. It exposes:
  - API (REST): port 8100 — /health, /vault/status, /vault/audit/{id}
  - Writer (REST): port 5001 — /health, /seal, /ratify
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger("arifosmcp.vault_bridge")

VAULT999_API_HOST = "127.0.0.1"
VAULT999_API_PORT = 8100
VAULT999_API_BASE = f"http://{VAULT999_API_HOST}:{VAULT999_API_PORT}"

VAULT999_WRITER_HOST = "127.0.0.1"
VAULT999_WRITER_PORT = 5001
VAULT999_WRITER_BASE = f"http://{VAULT999_WRITER_HOST}:{VAULT999_WRITER_PORT}"


async def vault_health_check() -> dict[str, Any]:
    """
    Check VAULT999 health via both API (port 8100) and writer (port 5001).

    Returns a merged health dict with:
      - status: healthy/degraded based on API response
      - version: from writer health
      - vault_seals_total: from /vault/status
      - chain_integrity: INTACT/BROKEN from /vault/status
      - identity/domain info for organ attestation
    """
    result: dict[str, Any] = {
        "status": "unhealthy",
        "organ": "VAULT999",
        "host": VAULT999_API_HOST,
        "version": "unknown",
    }

    # ── API health endpoint ─────────────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{VAULT999_API_BASE}/health")
            if resp.status_code == 200:
                data = resp.json()
                result["status"] = data.get("status", "healthy")
                result["vault"] = data.get("vault", "connected")
            else:
                result["api_health_error"] = f"HTTP {resp.status_code}"
    except Exception as e:
        result["api_health_error"] = str(e)

    # ── Vault status endpoint (chain integrity, seal count) ─────
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{VAULT999_API_BASE}/vault/status")
            if resp.status_code == 200:
                status_data = resp.json()
                result["vault_seals_total"] = status_data.get("vault_seals_total", 0)
                result["chain_integrity"] = status_data.get("chain_integrity", "UNKNOWN")
                result["chain_gaps"] = status_data.get("chain_gaps", 0)
                result["pending_holds"] = status_data.get("pending_holds", 0)
                result["append_only_enforced"] = status_data.get("append_only_enforced", False)

                last_seal = status_data.get("last_seal", {})
                if last_seal:
                    result["last_seal_action"] = last_seal.get("action")
                    result["last_seal_epoch"] = last_seal.get("epoch")
                    result["last_seal_chain_hash"] = last_seal.get("chain_hash")
    except Exception as e:
        result["vault_status_error"] = str(e)

    # ── Writer health (version info) ────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{VAULT999_WRITER_BASE}/health")
            if resp.status_code == 200:
                writer_data = resp.json()
                result["version"] = writer_data.get("version", "unknown")
                # Writer may have independent seal count
                writer_seals = writer_data.get("vault_seals_count", 0)
                if writer_seals:
                    result["writer_seals_count"] = writer_seals
                result["writer_pending_holds"] = writer_data.get("pending_holds", 0)
    except Exception as e:
        result["writer_health_error"] = str(e)

    # ── Domain identity (for organ attestation anchor) ──────────
    # VAULT999 answers to the immutable ledger law
    result["domain_law"] = "IMMUTABLE_LEDGER"
    result["identity_anchor_type"] = "vault_manifest"

    # Derive identity anchor hash from chain tip, if available
    chain_hash = result.get("last_seal_chain_hash")
    if chain_hash:
        result["identity_anchor_hash"] = f"sha256:{chain_hash}"
    else:
        result["identity_anchor_hash"] = "sha256:genesis"

    return result


async def list_vault_tools() -> list[dict[str, Any]]:
    """
    Return VAULT999's available tool surface.

    VAULT999 is a REST API, not an MCP server, so tool surface is
    defined by its HTTP endpoints. Returns the canonical endpoint list.
    """
    return [
        {"name": "health", "endpoint": "GET /health"},
        {"name": "vault_status", "endpoint": "GET /vault/status"},
        {"name": "vault_audit", "endpoint": "GET /vault/audit/{id}"},
        {"name": "vault_receipt", "endpoint": "GET /vault/receipt/{id}"},
        {"name": "cli_pending", "endpoint": "GET /cli/pending"},
        {"name": "cli_inspect", "endpoint": "GET /cli/inspect/{id}"},
        {"name": "secrets_access", "endpoint": "POST /secrets/access"},
    ]
