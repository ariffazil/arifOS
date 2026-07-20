"""
vault_verify.py — T3.2 Public VAULT verification endpoint.

Exposes /.well-known/arifos-vault-verify.json for external auditors
(OBSERVE_ONLY) to replay and verify VAULT999 receipts through the
public MCP surface without authentication.

Route: GET /.well-known/arifos-vault-verify.json
Access: PUBLIC (no session/token required)
"""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

VAULT_SEAL_CHAIN = Path("/root/.local/share/arifos/vault999/seal_chain.jsonl")


def get_vault_verification_manifest() -> dict:
    """Return public verification manifest for external auditors."""
    manifest = {
        "endpoint": "/.well-known/arifos-vault-verify.json",
        "spec_version": "vault-verify.v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "access": "PUBLIC — OBSERVE_ONLY, no session or token required",
    }

    # Chain integrity
    if VAULT_SEAL_CHAIN.exists():
        try:
            with open(VAULT_SEAL_CHAIN) as f:
                lines = [l.strip() for l in f if l.strip()]

            entries = []
            parse_errors = 0
            for line in lines:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    parse_errors += 1

            chain_hash = hashlib.sha256("\n".join(lines).encode()).hexdigest()[:16]

            manifest["chain"] = {
                "total_lines": len(lines),
                "valid_entries": len(entries),
                "parse_errors": parse_errors,
                "chain_integrity": "VERIFIED"
                if parse_errors == 0
                else f"DEGRADED ({parse_errors} errors)",
                "chain_hash": chain_hash,
                "head_seq": entries[-1].get("seq", "unknown") if entries else "empty",
                "head_actor": entries[-1].get("actor", "unknown") if entries else "empty",
                "head_timestamp": entries[-1].get("timestamp", "unknown") if entries else "empty",
            }

            # Last 5 seals for quick verification
            manifest["recent_seals"] = [
                {
                    "seq": e.get("seq", "?"),
                    "actor": e.get("actor", "?"),
                    "verdict": e.get("verdict", "?"),
                    "timestamp": str(e.get("timestamp", "?"))[:19],
                }
                for e in entries[-5:]
            ]

        except Exception as exc:
            manifest["chain"] = {"error": str(exc)}
    else:
        manifest["chain"] = {"error": "seal_chain.jsonl not found"}

    # Verification instructions
    manifest["verification"] = {
        "how_to_verify": [
            "1. Fetch this manifest: GET /.well-known/arifos-vault-verify.json",
            "2. Verify chain integrity: check chain_integrity field",
            "3. Replay receipts: arif_seal(mode=verify) with session_token from arif_init",
            "4. Cross-reference: compare chain_hash across independent observers",
            "5. Audit trail: every seal carries actor, verdict, timestamp, and content hash",
        ],
        "public_tools": [
            "arif_init(mode=light) — get OBSERVE_ONLY session (no auth required)",
            "arif_observe(mode=search) — search federation evidence",
            "arif_think(mode=verify) — verify claims against evidence",
            "arif_memory(mode=recall) — read memory (public tier only)",
        ],
        "operator_tools": [
            "arif_seal(mode=verify) — verify seal chain integrity (requires session)",
            "arif_seal(mode=chain) — read seal chain entries",
        ],
        "observatory": "https://arifos.arif-fazil.com — live public evidence",
    }

    return manifest


# FastAPI/Starlette route handler
async def vault_verify_endpoint(request):
    """ASGI endpoint for GET /.well-known/arifos-vault-verify.json"""
    from starlette.responses import JSONResponse

    manifest = get_vault_verification_manifest()
    return JSONResponse(
        manifest,
        headers={
            "Cache-Control": "public, max-age=300",
            "Access-Control-Allow-Origin": "*",
        },
    )
