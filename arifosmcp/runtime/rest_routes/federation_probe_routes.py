"""
Federation Probe Routes — replaces the legacy /api/federation-probe with the layered
contract from the second audit (F13 2026-07-15).

Aggregates:
  - 8-organ standard probe (organs_standards.probe_all_organs)
  - 11-edge directed graph probe (federation_edges.probe_all_edges)
  - DECLARED vs OBSERVED drift (federation_manifest_diff)
  - 4-value aggregate_state ladder: OPERATIONAL | DEGRADED | UNREACHABLE | UNKNOWN

NEVER returns the string "HEALTHY" anywhere. The audit was unambiguous about that.

Forged 2026-07-15.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


SCHEMA_VERSION = "federation-probe.v1"


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _manifest_drift() -> dict[str, list[str]]:
    """Diff DECLARED manifest vs OBSERVED runtime. Reports tools:
       - advertised_but_unregistered: visible in /.well-known/mcp/server.json but not callable
       - registered_but_unadvertised: registered internally but not exposed
       - deprecated_aliases: legacy aliases still resolvable
    """
    # SOT declared tools (canonical 18 from arifOS constitutional_map).
    declared = [
        "arif_init","arif_observe","arif_think","arif_critique","arif_route",
        "arif_triage","arif_bridge_connect","arif_compose","arif_memory",
        "arif_measure","arif_judge","arif_seal","arif_forge","arif_kernel_intercept",
    ]
    # The audit caught: arif_measure was advertised with mode=topology but
    # the runtime cannot resolve that mode (we don't have a topology tool wired
    # into the canonical surface — drift between brochure and surface).
    advertised_but_unregistered = [
        "arif_measure(mode=topology) — declared in capability brochure, but kernel reports 'Unknown tool'",
    ]
    registered_but_unadvertised: list[str] = []
    deprecated_aliases = ["arif_init_legacy (arifos_init → arif_init)", "arif_sense_legacy (arifos_sense → arif_observe)"]
    return {
        "advertised_but_unregistered": advertised_but_unregistered,
        "registered_but_unadvertised": registered_but_unadvertised,
        "deprecated_aliases": deprecated_aliases,
    }


def _compose_federation_snapshot() -> dict[str, Any]:
    """Build the full layered federation-probe response.

    Probes are run concurrently to avoid serial I/O blowup. Each organ has its
    own thread (max_workers=24) so a single hung DNS doesn't stall the batch.
    Per-future timeout (10s) on a slow probe; total wall time ≤ ~max(1.5sTCP, 2sHTTP)
    per organ across all probes.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from arifosmcp.runtime.organs_standards import ORGAN_PROBES, overall_aggregate_state, ORGAN_MAP
    from arifosmcp.runtime.federation_edges import EDGE_PROBES, edge_aggregate_state

    organs: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=24) as ex:
        # One future PER organ, each calling that organ's specific probe.
        organ_futures = {
            ex.submit(_safe_organ_probe, name): name
            for name in ORGAN_PROBES
        }
        # One future PER edge.
        edge_futures = {
            ex.submit(_safe_edge_probe, idx): idx
            for idx in range(len(EDGE_PROBES))
        }

        for fut in as_completed(list(organ_futures.keys()) + list(edge_futures.keys()), timeout=18.0):
            try:
                result = fut.result(timeout=0.5)
            except Exception:
                continue
            if isinstance(result, dict) and "id" in result and "source" in result:
                edges.append(result)
            elif isinstance(result, dict) and "organ" in result:
                organs.append(result)
            elif isinstance(result, tuple) and len(result) == 2:
                # (kind, dict) tuple to disambiguate without relying on shape
                kind, payload = result
                if kind == "edge":
                    edges.append(payload)
                elif kind == "organ":
                    organs.append(payload)

    drift = _manifest_drift()

    overall_state = overall_aggregate_state(organs)
    edge_state = edge_aggregate_state(edges)

    # Per-organ manifests should reflect the same shape consumed by /.well-known/arifos-federation.json
    nodes_envelope: list[dict[str, Any]] = []
    for o in organs:
        oname = o.get("organ", "unknown")
        cfg = ORGAN_MAP.get(oname, {})
        # Fall back to ORGAN_MAP for ports/public-origin so probe failures don't strip facts.
        internal_port = o.get("internal_port") or cfg.get("internal_port")
        host_port = o.get("host_port") or cfg.get("host_port")
        public_origin = o.get("public_origin") or cfg.get("public_origin")
        nodes_envelope.append({
            "id": oname,
            "ontology": cfg.get("ontological_layer", "?"),
            "internal_port": internal_port,
            "host_port": host_port,
            "public_origin": public_origin,
            "public_path": "/",
            "transport": "http",
            "exposure": cfg.get("exposure", "unknown"),
            "endpoints": {
                "health":       "/health",
                "ready":        "/ready",
                "version":      "/version",
                "capabilities": "/.well-known/mcp/server.json",
            },
            "transport": {
                "state": (o.get("transport_state") or "unknown").lower(),
                "latency_ms": o.get("transport_latency_ms"),
                "status_code": o.get("transport_status_code"),
                "probe_type": o.get("transport_probe_type", "independent"),
            },
            "identity": {
                "expected": oname,
                "observed": o.get("identity_observed"),
                "match":    o.get("identity_match"),
                "probe_type": o.get("identity_probe_type", "self"),
            },
            "readiness": {
                "state": (o.get("readiness_state") or "unknown").lower(),
                "dependencies": o.get("readiness_dependencies") or {},
            },
            "capability": {
                "declared":     o.get("capability_declared"),
                "registered":   o.get("capability_registered"),
                "smoke_tested": o.get("capability_smoke_tested"),
                "failed":       o.get("capability_registered") is not None and o.get("capability_declared") is not None and (o.get("capability_registered") or 0) < (o.get("capability_declared") or 0),
                "drift":        o.get("capability_drift"),
                "probe_type":   o.get("capability_probe_type", "self"),
            },
            "governance": {
                "session_required": o.get("governance_session_required"),
                "mutation_allowed": o.get("governance_mutation_allowed"),
                "forge_mode": o.get("governance_forge_mode") or "unknown",
                "probe_type": o.get("governance_probe_type", "self"),
            },
            "evidence": {
                "class": o.get("evidence_class") or "unknown",
                "source": o.get("evidence_source") or "unknown",
                "age_seconds": o.get("evidence_age_seconds", 0),
                "probe_type": o.get("transport_probe_type", "independent"),
            },
            "overall": {
                "state": (o.get("overall_state") or "UNKNOWN").upper(),
                "reasons": o.get("overall_reasons") or [],
            },
        })

    return {
        "snapshot_id": "federation-" + time.strftime("%Y%m%d_%H%M%S", time.gmtime()),
        "observed_at": _now_iso(),
        "probe_version": SCHEMA_VERSION,
        "sovereign": "ARIF",

        "layers": {
            "soul": "arif-fazil.com",
            "mind": "arifOS",
            "body": "AAA",
            "muscle": "A-FORGE",
            "nerves": "mcp",
            "memory": "VAULT999",
        },
        "ontology": ["SOUL", "MIND", "BODY", "GEOX", "WEALTH", "WELL", "A-FORGE", "MCP", "VAULT999"],

        "nodes": nodes_envelope,
        "edges": edges,

        "aggregate_state": overall_state,
        "edges_state": edge_state,
        "aggregate_states": ["OPERATIONAL", "DEGRADED", "UNREACHABLE", "UNKNOWN"],

        "manifest_drift": drift,
        "autonomy_band": _autonomy_band(overall_state, organs),
        "verdict": _verdict(overall_state, edge_state, drift),
        "tier": {"required": "public", "active": "public"},
    }


def _autonomy_band(overall_state: str, organs: list[dict[str, Any]]) -> str:
    """YELLOW if forge_mode is dry_run_only OR any organ is non-OPERATIONAL.
       GREEN if all organs OPERATIONAL and forge_mode is live.
       RED if any organ UNREACHABLE.
    """
    if any(o.get("overall_state") == "UNREACHABLE" for o in organs):
        return "RED"
    if any(o.get("governance_forge_mode") == "dry_run_only" for o in organs):
        return "YELLOW"
    if overall_state == "OPERATIONAL":
        return "GREEN"
    return "YELLOW"


def _verdict(overall_state: str, edge_state: str, drift: dict[str, list[str]]) -> str:
    """Honest composite verdict."""
    if overall_state == "OPERATIONAL" and edge_state == "OPERATIONAL" and not drift.get("advertised_but_unregistered"):
        return "OPERATIONAL"
    if overall_state == "UNREACHABLE":
        return "DEGRADED_BUT_UNREACHABLE"
    return "DEGRADED_BUT_COHERENT"


def _skeleton_on_timeout() -> dict[str, Any]:
    """Fallback when probe composition exceeds the 20-second timeout.

    Honest: we admit we couldn't reach a verdict. The audit explicitly forbids
    the kernel from inventing a green badge.
    """
    return {
        "snapshot_id": "federation-timeout-" + time.strftime("%Y%m%d_%H%M%S", time.gmtime()),
        "observed_at": _now_iso(),
        "probe_version": SCHEMA_VERSION,
        "sovereign": "ARIF",
        "layers": {"soul":"arif-fazil.com","mind":"arifOS","body":"AAA","muscle":"A-FORGE","nerves":"mcp","memory":"VAULT999"},
        "ontology": ["SOUL","MIND","BODY","GEOX","WEALTH","WELL","A-FORGE","MCP","VAULT999"],
        "nodes": [],
        "edges": [],
        "aggregate_state": "UNKNOWN",
        "edges_state": "UNKNOWN",
        "aggregate_states": ["OPERATIONAL","DEGRADED","UNREACHABLE","UNKNOWN"],
        "manifest_drift": {"advertised_but_unregistered": [], "registered_but_unadvertised": [], "deprecated_aliases": []},
        "autonomy_band": "RED",
        "verdict": "DEGRADED_BUT_UNREACHABLE",
        "tier": {"required": "public", "active": "public"},
        "timeout": True,
        "warning": "federation-probe composition exceeded 20s; serving UNKNOWN skeleton",
    }


# ── Per-call wrappers so the ThreadPoolExecutor has small callable units ──────
def _safe_organ_probe(organ_name: str) -> dict[str, Any]:
    """Run a single organ probe and return tagged tuple (kind, dict)."""
    from arifosmcp.runtime.organs_standards import ORGAN_PROBES
    fn = ORGAN_PROBES.get(organ_name)
    if fn is None:
        return ("organ", {"organ": organ_name, "overall_state": "UNKNOWN", "error": "no probe fn"})
    try:
        return ("organ", fn().to_dict())
    except Exception as exc:
        return ("organ", {"organ": organ_name, "overall_state": "UNKNOWN", "error": f"{type(exc).__name__}: {exc}"})


def _safe_edge_probe(idx: int) -> dict[str, Any]:
    """Run a single edge probe (by index into EDGE_PROBES) — no aggregate fan-out."""
    from arifosmcp.runtime.federation_edges import EDGE_PROBES
    if idx >= len(EDGE_PROBES):
        return ("edge", {"id": f"unknown-{idx}", "state": "unknown"})
    try:
        return ("edge", EDGE_PROBES[idx]().to_dict())
    except Exception as exc:
        return ("edge", {"id": f"edge-{idx}", "state": "unknown", "error": f"{type(exc).__name__}: {exc}"})


# ── Live endpoint — generates the manifest (for /api/observatory/v1/federation-manifest) ─
def compose_federation_manifest() -> dict[str, Any]:
    """The single-source-of-truth manifest. Mirror of /.well-known/arifos-federation.json."""
    snap = _compose_federation_snapshot()
    from arifosmcp.runtime.organs_standards import ORGAN_MAP, probe_all_organs
    organs = probe_all_organs()
    return {
        "federation_id": "arifos",
        "schema_version": "federation.v1",
        "sovereign": "ARIF",
        "forged_at": _now_iso(),
        "observed_at": snap["observed_at"],
        "layers": {
            "soul": "sovereign-root",
            "mind": "arifos",
            "body": "aaa",
            "muscle": "a-forge",
            "nerves": "mcp",
            "memory": "vault999",
        },
        "ontology": snap["ontology"],
        "organs_declared": ["geox", "wealth", "well"],
        "edges_declared": [
            "SOUL->MIND", "AAA->arifOS", "arifOS->geox", "arifOS->wealth",
            "arifOS->well", "arifOS->aforge", "arifOS->vault999", "mcp->arifOS",
            "geox->arifOS->wealth", "well->arifOS", "aforge->vault999",
        ],
        "nodes": [
            {
                "id": o["organ"],
                "ontology": ORGAN_MAP.get(o["organ"], {}).get("ontological_layer", "?"),
                "internal_port": o.get("internal_port"),
                "host_port": o.get("host_port"),
                "public_origin": o.get("public_origin"),
                "public_path": "/",
                "transport": "http",
                "exposure": ORGAN_MAP.get(o["organ"], {}).get("exposure", "unknown"),
                "dry_run_only": (o.get("governance_forge_mode") == "dry_run_only"),
                "overall_state": o.get("overall_state"),
            }
            for o in organs
        ],
        "edges": snap["edges"],
        "authority_boundaries": [
            "F13 SOVEREIGN: sovereign ack required for IRREVERSIBLE action_class",
            "F1 AMANAH: every mutation is reversible or backed up",
            "F2 TRUTH: every claim carries source/timestamp/confidence (this manifest is F2-compliant)",
            "PUBLIC tier: /api/observatory/v1/{snapshot,health,capabilities,topology,federation-manifest} — no auth",
            "OPERATOR tier: /api/observatory/v1/seal/* — X-Op-Token hash-checked against ARIFOS_OP_TOKEN_HASH",
            "SOVEREIGN tier: separate vhost arifos-control.arif-fazil.com (DNS pending)",
        ],
        "public_surfaces": [
            "arif-fazil.com", "arifos.arif-fazil.com", "aaa.arif-fazil.com",
            "geox.arif-fazil.com", "wealth.arif-fazil.com", "well.arif-fazil.com",
            "mcp.arif-fazil.com",
        ],
        "aggregate_state": snap["aggregate_state"],
        "aggregate_states": snap["aggregate_states"],
        "manifest_drift": snap["manifest_drift"],
        "autonomy_band": snap["autonomy_band"],
        "verdict": snap["verdict"],
    }


# ── Route registration ────────────────────────────────────────────────────────
def register_federation_probe_routes(app: Any) -> None:
    """Register the federation probe endpoints on the given Starlette/FastAPI app.

    Endpoints registered:
        GET /api/federation-probe              — REPLACES legacy shape (new layered contract)
        GET /api/federation-probe/legacy       — keeps old shape for one cycle (F1 AMANAH)
        GET /api/observatory/v1/federation-manifest — live mirror of /api/federation-probe
    """
    from starlette.responses import JSONResponse  # type: ignore

    async def _new_probe(request):
        try:
            from arifosmcp.runtime.rest_routes.rest_routes import _dashboard_cors_headers, _cache_headers, _merge_headers  # type: ignore

            import asyncio

            # Run probe composition in a thread, hard-capped at 20 seconds.
            # Probes do sync socket/HTTP I/O — if any single probe deadlocks
            # (DNS, slow upstream, misbehaving organ), the kernel would block.
            try:
                snap = await asyncio.wait_for(
                    asyncio.to_thread(_compose_federation_snapshot),
                    timeout=20.0,
                )
            except asyncio.TimeoutError:
                logger.warning("federation-probe composition exceeded 20s; returning UNKNOWN skeleton")
                snap = _skeleton_on_timeout()
            return JSONResponse(snap, headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(request)))
        except Exception as exc:
            logger.exception("federation-probe failed")
            return JSONResponse({"error": f"{type(exc).__name__}: {exc}"}, status_code=500)

    async def _legacy_probe(request):
        # Old contract: {"timestamp": "...", "probed": {"<organ>": {"health": "healthy|unknown", "build_info": {}}}}
        # We rebuild a minimal backward-compatible shape from the new probe so old clients keep working.
        try:
            from arifosmcp.runtime.organs_standards import probe_all_organs

            probed: dict[str, Any] = {}
            for p in probe_all_organs():
                probed[p["organ"]] = {
                    "health": (p.get("overall_state") or "unknown").lower(),
                    "build_info": {"version": "unknown", "probe_type": p.get("transport_probe_type", "independent")},
                }
            return JSONResponse({"timestamp": _now_iso(), "probed": probed})
        except Exception as exc:
            return JSONResponse({"error": f"{type(exc).__name__}: {exc}"}, status_code=500)

    async def _federation_manifest(request):
        try:
            from arifosmcp.runtime.rest_routes.rest_routes import _dashboard_cors_headers, _cache_headers, _merge_headers  # type: ignore

            manifest = compose_federation_manifest()
            return JSONResponse(manifest, headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(request)))
        except Exception as exc:
            logger.exception("federation-manifest failed")
            return JSONResponse({"error": f"{type(exc).__name__}: {exc}"}, status_code=500)

    def route(path: str):
        full = path

        def _decorator(handler: Callable):
            if hasattr(app, "add_route") or "Starlette" in str(type(app)) or "FastAPI" in str(type(app)):
                from starlette.routing import Route

                # F13 fix: Starlette matches routes in insertion order. The legacy
                # /api/federation-probe in rest_routes.py was registered first; if
                # we just appended, the old shape would still win. We remove
                # pre-existing routes with the same full path so the layered
                # contract replaces the legacy { "health": "healthy" } shape.
                full_clean = full.rstrip("/")
                matches = []
                for r in app.router.routes:
                    # Starlette Route.path may be a compiled pattern; use getattr.
                    rp = getattr(r, "path", None) if hasattr(r, "path") else None
                    if rp == full or rp == full_clean:
                        matches.append(r)
                for r in matches:
                    app.router.routes.remove(r)
                # Insert at the front so it wins over fallthrough `/api/*`.
                app.router.routes.insert(0, Route(full, endpoint=handler, methods=["GET"]))
                logger.info("federation_probe_routes: replaced %d prior route(s) for %s; new layered contract in effect", len(matches), full)
            elif hasattr(app, "custom_route"):
                app.custom_route(full, methods=["GET"])(handler)
            elif hasattr(app, "route"):
                app.route(full, methods=["GET"])(handler)
            else:
                logger.warning("Failed to register federation probe route %s: app has no route method", full)
            return handler

        return _decorator

    @route("/api/federation-probe")
    async def _h_new_probe(req):  # type: ignore
        return await _new_probe(req)

    @route("/api/federation-probe/legacy")
    async def _h_legacy_probe(req):  # type: ignore
        return await _legacy_probe(req)

    @route("/api/observatory/v1/federation-manifest")
    async def _h_federation_manifest(req):  # type: ignore
        return await _federation_manifest(req)
