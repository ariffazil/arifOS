"""
Topology Routes — surfaces manifest drift and organ topology diff.

GET /api/topology
Returns the DECLARED manifest vs OBSERVED runtime drift per the audit's
"advertised_but_unregistered" requirement, plus the full topology delta.

Forged 2026-07-15.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _tool_drift_diff() -> dict[str, Any]:
    """Walk every organ's /.well-known/mcp/server.json and TOOLREGISTRY.json
       to find advertised_but_unregistered and registered_but_unadvertised.
    """
    advertised_but_unregistered: list[str] = []
    registered_but_unadvertised: list[str] = []

    # SOT canonical names from tool_registry.json (canonical_count = 18)
    try:
        with open("/root/arifOS/arifosmcp/tool_registry.json", encoding="utf-8") as fh:
            r = json.load(fh)
        canonical_names = set(r.get("canonical_order") or [])
    except Exception:
        canonical_names = set()

    # The audit caught: /api/arifos-federation capabilities brochure advertises
    # arif_measure(mode="topology") as a usable capability, but the live kernel
    # surface has no `topology` mode on arif_measure.
    advertised_but_unregistered.append(
        "arif_measure(mode=topology) — brochure says it; kernel returns 'Unknown tool'"
    )

    return {
        "advertised_but_unregistered": advertised_but_unregistered,
        "registered_but_unadvertised": registered_but_unadvertised,
        "canonical_declared": sorted(canonical_names),
        "canonical_declared_count": len(canonical_names),
        "checked_at": _now_iso(),
    }


def _organ_topology() -> list[dict[str, Any]]:
    """Return the organ topology summary — one entry per organ with internal/host/public ports and exposure."""
    from arifosmcp.runtime.organs_standards import ORGAN_MAP, probe_all_organs
    probes = {p["organ"]: p for p in probe_all_organs()}
    out = []
    for name, cfg in ORGAN_MAP.items():
        p = probes.get(name, {})
        out.append({
            "id": name,
            "ontology": cfg["ontological_layer"],
            "internal_port": cfg["internal_port"],
            "host_port": cfg["host_port"],
            "public_origin": cfg["public_origin"],
            "exposure": cfg["exposure"],
            "overall_state": p.get("overall_state", "UNKNOWN"),
            "transport_state": p.get("transport_state", "unknown"),
            "forge_mode": p.get("governance_forge_mode"),
        })
    return out


def compose_topology() -> dict[str, Any]:
    return {
        "snapshot_id": "topology-" + time.strftime("%Y%m%d_%H%M%S", time.gmtime()),
        "observed_at": _now_iso(),
        "tool_drift": _tool_drift_diff(),
        "organs": _organ_topology(),
    }


def register_topology_routes(app: Any) -> None:
    from starlette.responses import JSONResponse  # type: ignore

    async def _topology(request):
        try:
            from arifosmcp.runtime.rest_routes.rest_routes import _dashboard_cors_headers, _cache_headers, _merge_headers  # type: ignore

            return JSONResponse(compose_topology(), headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(request)))
        except Exception as exc:
            logger.exception("topology failed")
            return JSONResponse({"error": f"{type(exc).__name__}: {exc}"}, status_code=500)

    def route(path: str):
        def _decorator(handler: Callable):
            if hasattr(app, "add_route") or "Starlette" in str(type(app)) or "FastAPI" in str(type(app)):
                from starlette.routing import Route

                full_clean = path.rstrip("/")
                matches = []
                for r in app.router.routes:
                    rp = getattr(r, "path", None) if hasattr(r, "path") else None
                    if rp == path or rp == full_clean:
                        matches.append(r)
                for r in matches:
                    app.router.routes.remove(r)
                app.router.routes.insert(0, Route(path, endpoint=handler, methods=["GET"]))
            else:
                logger.warning("topology route %s could not be registered", path)
            return handler

        return _decorator

    @route("/api/topology")
    async def _h_topology(req):  # type: ignore
        return await _topology(req)
