"""
Phase 1 — Single Writer Middleware (2026-08-06)

One middleware. One function. It is the ONLY thing permitted to answer
"may I proceed?".

FastMCP 3.4.4. Architecture: on_call_tool fires AFTER the handler computes
the result. This hook sees the assembled payload and injects one authority
block. No other code path may emit mutation_allowed, seal_allowed, verdict,
execution_readiness, or any field answering the proceed question.

Phase 2 will add ContradictionDetector to prove the legacy 64 are wrong.
Phase 3 will enforce outputSchema. Phase 4 deletes the 64.
"""

from __future__ import annotations

import logging
from typing import Any

from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)

# ── VERSION PIN — FastMCP 3.4.4 ──────────────────────────────────────────
# MiddlewareContext.message has: .name (tool name), .params (Tool arguments)
# call_next(context) returns ToolResult with .structured_content (dict | None)
# ══════════════════════════════════════════════════════════════════════════


def _dig(d: dict, path: str, default: Any = None) -> Any:
    """Drill into nested dict by dot-separated path."""
    keys = path.split(".")
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, default)
        else:
            return default
    return d


def compute_authority(payload: dict) -> dict:
    """Pure function. Sole writer of proceed-authority.

    Reads ONLY measured inputs. Never reads the fields it replaces.

    Returns a dict suitable for injection as payload['authority'].
    """
    substrate = (payload.get("substrate") or {}).get("state", "UNMEASURED")
    software = payload.get("software_release") or {}
    drift = software.get("drift", None)

    # Crypto verification — check actor authority state
    actor = payload.get("actor") or {}
    auth_state = actor.get("authority_state") or {}
    identity = auth_state.get("identity") or {}
    crypto = identity.get("cryptographically_verified", None)

    # Mutation/seal allowed from runtime_grant
    runtime_grant = auth_state.get("runtime_grant") or {}
    mutation_granted = runtime_grant.get("mutation_allowed", None)
    seal_granted = runtime_grant.get("seal_allowed", None)

    # Session bound status
    session = auth_state.get("session") or {}
    session_bound = session.get("bound", None)

    # ── Compute ──
    unmeasured = any(
        v in (None, "UNMEASURED")
        for v in [substrate, crypto, drift, mutation_granted, seal_granted, session_bound]
    )

    if unmeasured:
        return {
            "verdict": "HOLD",
            "may_mutate": False,
            "may_seal": False,
            "reason_code": "UNMEASURED_INPUT",
            "computed_from": {
                "substrate": str(substrate),
                "crypto": str(crypto),
                "drift": str(drift),
                "mutation_granted": str(mutation_granted),
                "seal_granted": str(seal_granted),
                "session_bound": str(session_bound),
            },
            "writer": "AuthorityMiddleware.compute",
        }

    # DEGRADED substrate → HOLD, no mutation
    if substrate == "DEGRADED" or substrate == "FAIL":
        return {
            "verdict": "HOLD",
            "may_mutate": False,
            "may_seal": False,
            "reason_code": f"SUBSTRATE_{substrate}",
            "computed_from": {
                "substrate": substrate,
                "crypto": crypto,
                "drift": drift,
            },
            "writer": "AuthorityMiddleware.compute",
        }

    # Crypto not verified → OBSERVE_ONLY
    if not crypto:
        return {
            "verdict": "SABAR",
            "may_mutate": False,
            "may_seal": False,
            "reason_code": "CRYPTO_NOT_VERIFIED",
            "computed_from": {
                "substrate": substrate,
                "crypto": crypto,
                "drift": drift,
            },
            "writer": "AuthorityMiddleware.compute",
        }

    # Drift detected → HOLD
    if drift is True:
        return {
            "verdict": "HOLD",
            "may_mutate": False,
            "may_seal": False,
            "reason_code": "DEPLOYMENT_DRIFT",
            "computed_from": {
                "substrate": substrate,
                "crypto": crypto,
                "drift": drift,
            },
            "writer": "AuthorityMiddleware.compute",
        }

    # Clean state, verified, no drift → respect grants
    return {
        "verdict": "SEAL" if seal_granted else "PROCEED",
        "may_mutate": bool(mutation_granted),
        "may_seal": bool(seal_granted),
        "reason_code": "CLEAN",
        "computed_from": {
            "substrate": substrate,
            "crypto": crypto,
            "drift": drift,
            "mutation_granted": mutation_granted,
            "seal_granted": seal_granted,
        },
        "writer": "AuthorityMiddleware.compute",
    }


class AuthorityMiddleware(Middleware):
    """Sole writer of proceed-authority. Injects `authority` block into every tool response.

    Registered LAST so it sees the final assembled payload after all other
    middleware and handlers have had their say.

    Reads only measured inputs. Never reads the fields it replaces.
    """

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        import sys as _sys

        _sys.stderr.write(f"AUTH_MW: on_call_tool fired for {context.message.name}\n")
        result = await call_next(context)

        sc = getattr(result, "structured_content", None)
        _sys.stderr.write(
            f"AUTH_MW: structured_content present: {sc is not None}, keys: {list(sc.keys())[:5] if sc else 'NONE'}\n"
        )
        if sc is None:
            _sys.stderr.write(f"AUTH_MW: NO structured_content, checking content list...\n")
            content = getattr(result, "content", [])
            _sys.stderr.write(f"AUTH_MW: content items: {len(content) if content else 0}\n")
            # Try to find structured content in content blocks
            for i, c in enumerate(content):
                if hasattr(c, "type"):
                    _sys.stderr.write(f"AUTH_MW:   content[{i}]: type={c.type}\n")
            return result

        # Inject the single authority block
        sc["authority"] = compute_authority(sc)
        _sys.stderr.write(
            f"AUTH_MW: injected authority block: {sc.get('authority', {}).get('verdict', '?')}\n"
        )

        return result
