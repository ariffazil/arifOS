"""
PR3 — Correct health and registry surfaces.

Per the audit:
  - /health: minimal process liveness, NO authentication, NO session.
  - /ready: dependency readiness, internal-network only.
  - /capabilities: sanitized public capability summary.
  - /capabilities/full: authenticated operator registry (X-Op-Token).

The observatory /api/observatory/v1/health route is unchanged (it carries
the 7-state vocabulary and is itself a kernel observation). This module
adds a NEW public /api/observatory/v1/health-public that is sovereign-gate-free,
plus /ready and the two /capabilities surfaces.

F1 AMANAH: every route is additive. The observatory /health route is still
served under its prior path.
"""

from __future__ import annotations

import logging
import os
import socket
import time
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


def _tcp(host: str, port: int, timeout: float = 1.5) -> tuple[bool, int | None]:
    started = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout) as _:
            return True, int((time.time() - started) * 1000)
    except Exception:
        return False, None


def _enforce_tier(request, required: str) -> tuple[bool, str | None]:
    """Hashed-token tier check. Operator tier required for /capabilities/full."""
    import hashlib as _hashlib
    import hmac

    if required == "public":
        return True, None
    if required == "operator":
        token = request.headers.get("X-Op-Token", "").strip()
        if not token:
            return False, "X-Op-Token required (tier=operator)"
        expected = os.getenv("ARIFOS_OP_TOKEN_HASH", "").strip()
        if not expected:
            return (
                False,
                "operator tier not bootstrapped on this server (missing ARIFOS_OP_TOKEN_HASH)",
            )
        got_hash = _hashlib.sha256(token.encode("utf-8")).hexdigest()
        if not hmac.compare_digest(got_hash, expected):
            return False, "X-Op-Token hash mismatch"
        return True, None
    return False, f"unknown required tier: {required}"


def _struct_error(
    code: str,
    message: str,
    *,
    retryable: bool = True,
    mutation_occurred: bool = False,
    **extra: Any,
) -> dict:
    return {
        "status": "HOLD",
        "error_code": code,
        "message": message,
        "retryable": retryable,
        "mutation_occurred": mutation_occurred,
        **extra,
    }


def _public_health_envelope() -> dict[str, Any]:
    """Minimal liveness. No auth. No session. No interiority."""
    host = "127.0.0.1"
    port = int(os.getenv("PORT", "8088"))
    up, latency = _tcp(host, port)
    return {
        "endpoint": "/api/observatory/v1/health-public",
        "policy": "unauthenticated_process_liveness",
        "status": "healthy" if up else "down",
        "transport": {
            "state": "reachable" if up else "unreachable",
            "host": host,
            "port": port,
            "latency_ms": latency,
        },
        "readiness": "n/a",
        "governance": "n/a",
        "session_required": False,
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _ready_envelope() -> dict[str, Any]:
    """Internal-network dependency readiness. NO external exposure.

    The audit says /ready is "internal network or monitoring credential" — we
    publish it on /ready but expect Caddy to gate it via ``import private_net``.

    P0-5 (2026-07-25): Added deployment invariant check — degraded when
    source≠built≠deployed (drift detected).
    """
    deps: dict[str, str] = {}
    for label, host, port in (
        ("postgres", "127.0.0.1", 5432),
        ("redis", "127.0.0.1", 6379),
        ("qdrant", "127.0.0.1", 6333),
        ("vault_writer", "127.0.0.1", 5001),
    ):
        up, _ = _tcp(host, port)
        deps[label] = "ready" if up else "degraded"

    # P0-5: Deployment invariant — source==built==deployed
    deploy_ok = True
    drift_info: dict[str, Any] = {"ok": True}
    try:
        from arifosmcp.runtime.rest_routes.rest_routes import _compute_runtime_drift

        drift = _compute_runtime_drift()
        drift_detected = drift.get("runtime_drift", False)
        src = drift.get("source_commit", "?") or "?"
        built = drift.get("built_commit", "?") or "?"
        deployed = drift.get("deployed_commit", "?") or "?"
        deploy_ok = not drift_detected and src == built == deployed
        drift_info = {
            "ok": deploy_ok,
            "drift_detected": drift_detected,
            "source_commit": src,
            "built_commit": built,
            "deployed_commit": deployed,
            "rule": "source_commit == built_commit == deployed_commit",
        }
    except Exception:
        drift_info = {"ok": False, "error": "drift_check_failed"}

    all_ready = all(v == "ready" for v in deps.values()) and deploy_ok

    return {
        "endpoint": "/ready",
        "policy": "internal_network_only",
        "session_required": False,
        "status": "ready" if all_ready else "degraded",
        "dependencies": deps,
        "deploy_invariant": drift_info,
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _capabilities_envelope() -> dict[str, Any]:
    """Sanitized public capability summary. No secrets. No schema. No interiority."""
    try:
        from arifosmcp.runtime.manifest.generator import compose_manifest  # type: ignore

        m = compose_manifest()
        tools = [
            {
                "name": t["name"],
                "version": t["version"],
                "action_class": t["effects"]["action_class"],
                "authority": t["authority"]["minimum_authority"],
                "public_simulation": t["authority"]["public_simulation"],
                "registered": t["runtime"]["registered"],
                "callable": t["runtime"]["callable"],
                "status": t["runtime"]["status"],
            }
            for t in m["tools"]
        ]
        totals = m["totals"]
        return {
            "endpoint": "/capabilities",
            "policy": "sanitized_public",
            "session_required": False,
            "totals": totals,
            "tools": tools,
            "schema_version": m["schema_version"],
            "observed_at": m["issued_at"],
        }
    except Exception as exc:
        return _struct_error(
            "INTERNAL_ERROR", f"capabilities compose failed: {exc}", retryable=False
        )


def _capabilities_full_envelope() -> dict[str, Any]:
    """Operator-only: includes schema hashes, drift, last-smoke-test, governance."""
    try:
        from arifosmcp.runtime.manifest.generator import compose_manifest  # type: ignore

        m = compose_manifest()
        return {
            "endpoint": "/capabilities/full",
            "policy": "operator_only",
            "session_required": True,
            "auth": "X-Op-Token hash-checked against ARIFOS_OP_TOKEN_HASH",
            "totals": m["totals"],
            "tools": m["tools"],
            "manifest_drift": m["manifest_drift"],
            "schema_version": m["schema_version"],
            "observed_at": m["issued_at"],
        }
    except Exception as exc:
        return _struct_error(
            "INTERNAL_ERROR", f"capabilities/full compose failed: {exc}", retryable=False
        )


def register_health_routes(app: Any) -> None:
    """Register /api/observatory/v1/health-public, /ready, /capabilities, /capabilities/full."""
    from starlette.responses import JSONResponse  # type: ignore

    async def _health_public(request):
        return JSONResponse(_public_health_envelope())

    async def _ready(request):
        return JSONResponse(_ready_envelope())

    async def _capabilities(request):
        return JSONResponse(_capabilities_envelope())

    async def _capabilities_full(request):
        ok, reason = _enforce_tier(request, required="operator")
        if not ok:
            return JSONResponse(
                _struct_error(
                    "SESSION_REQUIRED", reason or "tier=operator required", retryable=True
                ),
                status_code=403,
            )
        return JSONResponse(_capabilities_full_envelope())

    def route(path: str, methods: list[str]):
        full = path

        def _decorator(handler: Callable):
            if (
                hasattr(app, "add_route")
                or "Starlette" in str(type(app))
                or "FastAPI" in str(type(app))
            ):
                from starlette.routing import Route

                full_clean = full.rstrip("/")
                matches = []
                for r in app.router.routes:
                    rp = getattr(r, "path", None) if hasattr(r, "path") else None
                    if rp == full or rp == full_clean:
                        matches.append(r)
                for r in matches:
                    app.router.routes.remove(r)
                app.router.routes.insert(0, Route(full, endpoint=handler, methods=methods))
                logger.info("health_routes: replaced %d prior route(s) for %s", len(matches), full)
            else:
                logger.warning("health_routes: failed to register %s", full)
            return handler

        return _decorator

    @route("/api/observatory/v1/health-public", ["GET"])
    async def _h_health(req):  # type: ignore
        return await _health_public(req)

    @route("/api/observatory/v1/ready", ["GET"])
    async def _h_ready(req):  # type: ignore
        return await _ready(req)

    @route("/api/observatory/v1/capabilities", ["GET"])
    async def _h_caps(req):  # type: ignore
        return await _capabilities(req)

    @route("/api/observatory/v1/capabilities/full", ["GET"])
    async def _h_caps_full(req):  # type: ignore
        return await _capabilities_full(req)
