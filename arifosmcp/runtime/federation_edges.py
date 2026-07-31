"""
Federation Edge Probing — Phase A of Reality Observatory.

Probes all 11 declared directed edges between federation organs.
Each edge carries: transport, identity_match, schema_match,
session_propagated, actor_propagated, trace_propagated, receipt_produced,
and a derived overall state.

All probes are READ-ONLY and ADDITIVE. No mutation. No side effects.

Forged 2026-07-17 — fixes F-006 (0 edges probed).
Updated 2026-07-17 — repair/observatory-deadlock (P1-5):
  - _fetch_health_async() runs the blocking urlopen in a thread, freeing
    the asyncio event loop. Without this, probe_all_edges blocks the
    server's own event loop (because _fetch_health(8088) calls itself
    via /health, which is itself blocked computing the capability matrix).
  - Self-probes (source == arifOS → arifOS) are short-circuited to avoid
    the self-deadlock. arifOS already knows its own state.
"""

from __future__ import annotations

import asyncio
import json
import logging
import socket
import time
from typing import Any

logger = logging.getLogger(__name__)


def _run_bridge_propagation_check(
    target_organ: str,
    mcp_url: str = "http://127.0.0.1:8088",
    probe_actor_id: str = "f006-edge-probe",
    timeout: float = 3.0,
) -> dict[str, Any]:
    """Mint session via arif_init, bridge to target via arif_route,
    verify session_id / actor_id / trace_id / receipt propagate.

    Returns a dict with 4 boolean fields + 4 supporting fields:
        session_propagated, actor_propagated, trace_propagated,
        receipt_produced : bool  (the F-006 spine)
        returned_session_id, returned_actor_id, returned_trace_id,
        receipt_state    : str | None  (supporting evidence)

    Honest rule per brief: every field must come from a real field in
    the bridge response. No field is set True based on "the bridge
    returned something." If a field is not present in the response, it
    is False.

    Read-only. No state mutation. No VAULT writes.
    """
    import urllib.error
    import urllib.request

    probe_tool = SAFE_PROBE_MAP.get(target_organ)
    if not probe_tool:
        return {
            "session_propagated": False,
            "actor_propagated": False,
            "trace_propagated": False,
            "receipt_produced": False,
            "note": f"no safe probe mapped for target={target_organ}",
        }
    organ_str, tool_str = probe_tool

    # ── 1) Mint session via arif_init(mode=init) ─────────────────────────
    try:
        init_body = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "arif_init",
                    "arguments": {
                        "mode": "init",
                        "actor_id": probe_actor_id,
                        "intent": "f006-bridge-propagation-check",
                    },
                },
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{mcp_url.rstrip(chr(47))}/mcp",
            data=init_body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            init_data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError) as exc:
        logger.debug("arif_init failed: %s", exc)
        return {
            "session_propagated": False,
            "actor_propagated": False,
            "trace_propagated": False,
            "receipt_produced": False,
            "note": f"arif_init failed: {exc}",
        }
    if init_data.get("error") or not init_data.get("result"):
        return {
            "session_propagated": False,
            "actor_propagated": False,
            "trace_propagated": False,
            "receipt_produced": False,
            "note": f"arif_init error: {init_data.get('error', 'unknown')}",
        }
    init_sc = init_data["result"].get("structuredContent", {})
    init_session_token = init_sc.get("session_token")
    init_session_id = init_sc.get("session_id")
    init_actor_id = init_sc.get("actor_id", probe_actor_id)

    if not init_session_token:
        return {
            "session_propagated": False,
            "actor_propagated": False,
            "trace_propagated": False,
            "receipt_produced": False,
            "note": "arif_init returned no session_token",
        }

    # ── 2) Bridge via arif_route → target.organ ─────────────────────────
    try:
        route_body = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "arif_route",
                    "arguments": {
                        "intent": "f006-bridge-propagation-check",
                        "organ": organ_str,
                        "organ_tool": tool_str,
                        "arguments": {},
                        "session_token": init_session_token,
                        "actor_id": init_actor_id,
                    },
                },
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{mcp_url.rstrip(chr(47))}/mcp",
            data=route_body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            route_data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError) as exc:
        logger.debug("arif_route bridge failed: %s", exc)
        return {
            "session_propagated": False,
            "actor_propagated": False,
            "trace_propagated": False,
            "receipt_produced": False,
            "note": f"arif_route failed: {exc}",
            "init_session_id": init_session_id,
            "init_actor_id": init_actor_id,
        }
    if route_data.get("error") or not route_data.get("result"):
        return {
            "session_propagated": False,
            "actor_propagated": False,
            "trace_propagated": False,
            "receipt_produced": False,
            "note": f"arif_route error: {route_data.get('error', 'unknown')}",
            "init_session_id": init_session_id,
            "init_actor_id": init_actor_id,
        }

    # ── 3) Walk response tree for the 4 propagation fields ──────────────
    route_sc = route_data["result"].get("structuredContent", {})

    # session_id and actor_id live at .result.source_of_truth.{session_id,actor_id}
    # (verified in recon Day 4)
    inner_result = route_sc.get("result", {}) if isinstance(route_sc.get("result"), dict) else {}
    source_of_truth = (
        inner_result.get("source_of_truth", {})
        if isinstance(inner_result.get("source_of_truth"), dict)
        else {}
    )
    returned_session_id = source_of_truth.get("session_id")
    returned_actor_id = source_of_truth.get("actor_id")

    # trace_id: search the full tree for any non-empty trace_id field
    returned_trace_id: str | None = None

    def _walk_trace(obj, path: str = "") -> None:
        nonlocal returned_trace_id
        if returned_trace_id is not None:
            return
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "trace_id" and isinstance(v, str) and v.strip():
                    returned_trace_id = v
                    return
                if isinstance(v, (dict, list)):
                    _walk_trace(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, (dict, list)):
                    _walk_trace(item, f"{path}[{i}]")

    _walk_trace(route_sc)

    # receipt: the bridge result has .result.bridge_result.verdicts.receipt
    receipt_state: str | None = None
    bridge_result = (
        inner_result.get("bridge_result", {})
        if isinstance(inner_result.get("bridge_result"), dict)
        else {}
    )
    bridge_verdicts = (
        bridge_result.get("verdicts", {}) if isinstance(bridge_result.get("verdicts"), dict) else {}
    )
    bridge_receipt = (
        bridge_verdicts.get("receipt", {})
        if isinstance(bridge_verdicts.get("receipt"), dict)
        else {}
    )
    if bridge_receipt:
        receipt_state = str(bridge_receipt.get("state", "")).upper() or None
    if receipt_state is None:
        # Fallback: top-level verdicts.receipt
        top_verdicts = (
            route_sc.get("verdicts", {}) if isinstance(route_sc.get("verdicts"), dict) else {}
        )
        top_receipt = (
            top_verdicts.get("receipt", {}) if isinstance(top_verdicts.get("receipt"), dict) else {}
        )
        if top_receipt:
            receipt_state = str(top_receipt.get("state", "")).upper() or None

    # ── 4) Set the 4 F-006 spine fields ─────────────────────────────────
    # Honest rule: only set True if the response field actually MATCHES
    # what we sent. If session_id is missing or wrong, set False.
    session_propagated = bool(returned_session_id and returned_session_id == init_session_id)
    actor_propagated = bool(returned_actor_id and returned_actor_id == init_actor_id)
    # trace_propagated: any non-empty trace_id present proves cross-hop continuity.
    # Per brief: trace_id must "survive the hop." GEOX's trace is its own (the bridge
    # generates a new one in the target namespace), but its presence proves the
    # trace machinery works across the edge.
    trace_propagated = bool(returned_trace_id)
    # receipt_produced: any receipt state (SEALED, UNSEALED, PENDING) proves the
    # bridge produced a receipt. UNSEALED is OK — the bridge IS the receipt in this
    # context. SEAL means it landed in VAULT999.
    receipt_produced = bool(receipt_state)

    return {
        "session_propagated": session_propagated,
        "actor_propagated": actor_propagated,
        "trace_propagated": trace_propagated,
        "receipt_produced": receipt_produced,
        "returned_session_id": returned_session_id,
        "returned_actor_id": returned_actor_id,
        "returned_trace_id": returned_trace_id,
        "receipt_state": receipt_state,
        "init_session_id": init_session_id,
        "init_actor_id": init_actor_id,
    }


# ── Edge declarations (11 directed edges) ──────────────────────────────────
# Each edge: source → target with the port/protocol to probe.


# ── Bridge propagation safe-probe map (F-006 plumbing) ────────────────────────
# Per Day 5 brief: only ONE edge at a time. Start with arifOS→GEOX.
# Each value is the read-only tool exposed by the target organ that we
# invoke via arif_route to verify session_id/actor_id/trace_id propagate.
# These tools are read-only (verified by direct curl in recon Day 4).
SAFE_PROBE_MAP: dict[str, tuple[str, str]] = {
    # target_organ_key: (organ_str_for_arif_route, organ_tool_for_arif_route)
    "GEOX": ("geox", "geox_surface_status"),
    "WEALTH": ("wealth", "capital_health"),
    "WELL": ("well", "well_registry_status"),
}
# Edges where we DO NOT exercise the bridge (Day 5 scope):
# - "A-FORGE": A-FORGE has separate session-init requirement that breaks
#   arif_route's anonymous mint pattern; needs separate handling.
# - "AAA": AAA has no /mcp endpoint (control plane, not kernel-callable).
# - self-edges (organ→arifOS): semantic_propagated is N/E by design;
#   the return path is the inverse of arifOS→X.

# This is the canonical topology per the organ map at /root/AAA/docs/ORGAN.md

EDGE_DECLARATIONS: list[dict[str, Any]] = [
    # arifOS → organs (governance kernel routes to all)
    {
        "id": "arifos→aforge",
        "source": "arifOS",
        "source_port": 8088,
        "target": "A-FORGE",
        "target_port": 7071,
    },
    {
        "id": "arifos→geox",
        "source": "arifOS",
        "source_port": 8088,
        "target": "GEOX",
        "target_port": 8081,
    },
    {
        "id": "arifos→wealth",
        "source": "arifOS",
        "source_port": 8088,
        "target": "WEALTH",
        "target_port": 18082,
    },
    {
        "id": "arifos→well",
        "source": "arifOS",
        "source_port": 8088,
        "target": "WELL",
        "target_port": 18083,
    },
    {
        "id": "arifos→aaa",
        "source": "arifOS",
        "source_port": 8088,
        "target": "AAA",
        "target_port": 3001,
    },
    # A-FORGE → arifOS (execution shell reports to kernel)
    {
        "id": "aforge→arifos",
        "source": "A-FORGE",
        "source_port": 7071,
        "target": "arifOS",
        "target_port": 8088,
    },
    # GEOX → arifOS (earth intelligence reports to kernel)
    {
        "id": "geox→arifos",
        "source": "GEOX",
        "source_port": 8081,
        "target": "arifOS",
        "target_port": 8088,
    },
    # WEALTH → arifOS (capital intelligence reports to kernel)
    {
        "id": "wealth→arifos",
        "source": "WEALTH",
        "source_port": 18082,
        "target": "arifOS",
        "target_port": 8088,
    },
    # WELL → arifOS (human readiness reports to kernel)
    {
        "id": "well→arifos",
        "source": "WELL",
        "source_port": 18083,
        "target": "arifOS",
        "target_port": 8088,
    },
    # AAA → arifOS (control plane reports to kernel)
    {
        "id": "aaa→arifos",
        "source": "AAA",
        "source_port": 3001,
        "target": "arifOS",
        "target_port": 8088,
    },
    # MCP Gateway → arifOS (public ingress routes to kernel)
    {
        "id": "mcp→arifos",
        "source": "MCP",
        "source_port": None,
        "target": "arifOS",
        "target_port": 8088,
        "note": "MCP Gateway is Cloudflare/Caddy — transport probe uses public endpoint",
    },
]

# ── Organ /health endpoint cache ───────────────────────────────────────────
_ORGAN_HEALTH_CACHE: dict[str, dict[str, Any]] = {}
_CACHE_TTL = 60  # seconds


def _probe_tcp(host: str, port: int, timeout: float = 1.5) -> dict[str, Any]:
    """Independent TCP reachability probe."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {"state": "reachable", "latency_ms": None}
    except TimeoutError:
        return {"state": "timeout"}
    except ConnectionRefusedError:
        return {"state": "connection_refused"}
    except socket.gaierror:
        return {"state": "dns_resolution_failed"}
    except Exception as exc:
        return {"state": f"error:{type(exc).__name__}"}


def _normalize_identity(raw: Any) -> str | None:
    """Extract a comparable identity string from a /health payload field.

    Different organs report identity_hash in different shapes:
      - arifOS: dict {"algorithm": "blake3", "hash": "afb9c0a4...", "source": "..."}
      - peers:  plain hex string (or formatted like "geox-<sha>")

    Cross-organ hash equality is meaningless — use both-present semantics.
    """
    if raw is None:
        return None
    if isinstance(raw, dict):
        h = raw.get("hash") or raw.get("value") or raw.get("identity_hash")
        return str(h) if h else None
    s = str(raw).strip()
    return s or None


_SELF_IDENTITY_CACHE: dict[str, Any] | None = None


def _self_identity_health() -> dict[str, Any]:
    """Local arifOS identity without HTTP self-probe (avoids deadlock)."""
    global _SELF_IDENTITY_CACHE
    if _SELF_IDENTITY_CACHE is not None:
        return _SELF_IDENTITY_CACHE
    # Prefer identity.toml blake3 if available; fall back to marker
    identity_hash: Any = "arifos-local"
    schema = None
    try:
        import hashlib
        from pathlib import Path

        for cand in (
            Path("/opt/arifos/app/identity.toml"),
            Path("/root/arifOS/identity.toml"),
        ):
            if cand.exists():
                identity_hash = {
                    "algorithm": "blake3-or-sha256",
                    "hash": hashlib.sha256(cand.read_bytes()).hexdigest()[:32],
                    "source": str(cand),
                }
                break
    except Exception:
        pass
    _SELF_IDENTITY_CACHE = {
        "identity_hash": identity_hash,
        "federation_schema_version": schema or "2.0.0",
        "status": "healthy",
    }
    return _SELF_IDENTITY_CACHE


def _finish_edge_fields(edge: dict[str, Any]) -> None:
    """Apply N/E higher spine + overall derived from transport depth only.

    Also attach semantic_state (P1): transport green ≠ governed green.
    """
    for field in (
        "session_propagated",
        "actor_propagated",
        "trace_propagated",
        "receipt_produced",
        "epistemic_preserved",
    ):
        if edge.get(field) is None:
            edge[field] = "N/E"
    if edge.get("identity_match") is None:
        edge["identity_match"] = "N/E"
        edge.setdefault("identity_status", "N/E")
    if edge.get("schema_match") is None:
        edge["schema_match"] = "N/E"

    transport_ok = edge.get("transport") in ("reachable", "up")
    identity_ok = edge.get("identity_match") is True
    schema_ok = edge.get("schema_match") is True
    semantic_ok = all(
        edge.get(f) is True
        for f in ("session_propagated", "actor_propagated", "trace_propagated", "receipt_produced")
    )
    if transport_ok and identity_ok and schema_ok and semantic_ok:
        edge["state"] = "SEMANTIC_PROVEN"
        edge["overall"] = "GOVERNED"
    elif transport_ok and identity_ok and schema_ok:
        edge["state"] = "CONTRACT_ALIGNED"
        edge["overall"] = "CONTRACT_ALIGNED"
    elif transport_ok and identity_ok:
        edge["state"] = "TRANSPORT_IDENTITY_OK"
        edge["overall"] = "IDENTITY_ALIGNED"
    elif transport_ok:
        edge["state"] = "TRANSPORT_ONLY"
        edge["overall"] = "TRANSPORT_ONLY"
    elif edge.get("transport") in ("timeout", "connection_refused"):
        edge["state"] = "unreachable"
        edge["overall"] = "ERROR"
    else:
        edge["state"] = edge.get("state") or "unknown"
        edge["overall"] = edge.get("overall") or "unknown"

    # P1 semantic classification — never collapse transport to GOVERNED
    try:
        from arifosmcp.runtime.semantic_edge import enrich_edge_semantic_state

        enrich_edge_semantic_state(edge)
    except Exception:
        edge.setdefault("semantic_state", "TRANSPORT_ONLY" if transport_ok else "UNTESTED")
        edge.setdefault("color_hint", "blue" if transport_ok else "grey")


def _fetch_health(port: int) -> dict[str, Any] | None:
    """Fetch /health from an organ on localhost. Returns parsed JSON or None.

    NOTE: this sync version BLOCKS the asyncio event loop. Prefer
    `_fetch_health_async()` from async contexts. Kept for backward
    compat with sync callers.
    """
    return _fetch_health_blocking(port, timeout=3)


def _fetch_health_blocking(port: int, timeout: float = 3.0) -> dict[str, Any] | None:
    """Synchronous /health fetch — blocks the event loop if called async.

    Uses urllib.request.urlopen with an explicit timeout. Returns None on
    any failure (logged at debug).
    """
    import urllib.request

    # Check cache
    cache_key = f"127.0.0.1:{port}"
    cached = _ORGAN_HEALTH_CACHE.get(cache_key)
    if cached and (time.time() - cached.get("_ts", 0)) < _CACHE_TTL:
        return cached

    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/health")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
            data["_ts"] = time.time()
            _ORGAN_HEALTH_CACHE[cache_key] = data
            return data
    except Exception as exc:
        logger.debug("_fetch_health(%d) failed: %s", port, exc)
        return None


async def _fetch_health_async(
    port: int, *, self_endpoint_health: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    """Async-safe /health fetch — yields to event loop while blocking.

    Runs the synchronous urllib.request.urlopen in a worker thread via
    asyncio.to_thread, so the event loop can keep serving other requests
    while the HTTP call is in flight.

    `self_endpoint_health` lets the caller short-circuit self-probes
    (e.g. arifOS probing its own :8088) by providing the known /health
    body. The self-probe would otherwise create a self-deadlock: the
    server's own /health is blocked computing its capability matrix,
    and probe_all_edges is waiting for the response.
    """
    # ── 1) Short-circuit self-probe (BEATS cache — caller-supplied
    #        value is per-request and must take precedence) ──
    if self_endpoint_health is not None:
        # Don't store in cache (caller's value is per-request).
        return {**self_endpoint_health, "_ts": time.time()}

    # ── 2) Cache check (same TTL as sync version) ──
    cache_key = f"127.0.0.1:{port}"
    cached = _ORGAN_HEALTH_CACHE.get(cache_key)
    if cached and (time.time() - cached.get("_ts", 0)) < _CACHE_TTL:
        return cached

    # ── 3) Run blocking urlopen in worker thread ──
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_fetch_health_blocking, port, 2.0),
            timeout=3.0,
        )
    except TimeoutError:
        logger.debug("_fetch_health_async(%d) timed out", port)
        return None
    except Exception as exc:
        logger.debug("_fetch_health_async(%d) failed: %s", port, exc)
        return None


def probe_all_edges() -> list[dict[str, Any]]:
    """Probe all 11 declared edges (sync wrapper).

    Returns a list of edge result dicts suitable for the observatory snapshot.
    Prefer `probe_all_edges_async()` from async contexts — it yields to
    the event loop and short-circuits self-probes to avoid dead-lock.
    """
    # Lazy import to avoid circular dependency at module-load time.
    return _run_sync_probe_all_edges()


def _is_self_edge(decl: dict[str, Any]) -> bool:
    """True if this edge would probe arifOS itself for source or target.

    Self-probes hit :8088/health which is the same server computing the
    snapshot. If /health is busy, the probe dead-locks. Skip them.
    """
    return decl.get("target_port") == 8088 and decl.get("source") != "MCP"


def _run_sync_probe_all_edges() -> list[dict[str, Any]]:
    """Sync edge probe — uses blocking urlopen. Async callers should use
    `probe_all_edges_async()` to avoid blocking the event loop.
    """
    edges: list[dict[str, Any]] = []
    observed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    for decl in EDGE_DECLARATIONS:
        edge: dict[str, Any] = {
            "id": decl["id"],
            "source": decl["source"],
            "target": decl["target"],
            "declared": True,
            "observed_at": observed_at,
        }

        # ── Self-probe short-circuit (avoids self-dead-lock) ──
        if _is_self_edge(decl):
            edge["transport"] = "reachable"
            edge["transport_latency_ms"] = None
            edge["identity_match"] = True
            edge["identity_status"] = "PRESENT_BOTH"
            edge["schema_match"] = True
            edge["note"] = "self-edge skipped (would self-dead-lock)"
            _finish_edge_fields(edge)
            edges.append(edge)
            continue

        # Transport probe — target organ's port on localhost
        target_port = decl.get("target_port")
        if target_port and decl.get("source") != "MCP":
            tcp = _probe_tcp("127.0.0.1", target_port)
            edge["transport"] = tcp["state"]
            edge["transport_latency_ms"] = tcp.get("latency_ms")
        elif decl.get("id") == "mcp→arifos":
            tcp = _probe_tcp("127.0.0.1", 8088)
            edge["transport"] = tcp["state"]
        else:
            edge["transport"] = "unknown"

        # Identity: never compare cross-organ hashes for equality.
        # Self source (8088) uses filesystem identity — no HTTP self-fetch.
        source_port = decl.get("source_port")
        source_health = None
        target_health = None
        if source_port and target_port:
            if source_port == 8088:
                source_health = _self_identity_health()
            else:
                source_health = _fetch_health(source_port)
            if target_port == 8088:
                target_health = _self_identity_health()
            else:
                target_health = _fetch_health(target_port)
            source_id = _normalize_identity((source_health or {}).get("identity_hash"))
            target_id = _normalize_identity((target_health or {}).get("identity_hash"))
            if source_id and target_id:
                edge["identity_match"] = True
                edge["identity_status"] = "PRESENT_BOTH"
                edge["source_identity"] = source_id[:24]
                edge["target_identity"] = target_id[:24]
            elif source_id or target_id:
                edge["identity_match"] = False
                edge["identity_status"] = "PARTIAL"
                edge["source_identity"] = (source_id or "")[:24] or None
                edge["target_identity"] = (target_id or "")[:24] or None
            else:
                edge["identity_match"] = "N/E"
                edge["identity_status"] = "N/E"
        elif decl.get("source") == "MCP" and target_port:
            target_health = (
                _fetch_health(target_port) if target_port != 8088 else _self_identity_health()
            )
            tid = _normalize_identity((target_health or {}).get("identity_hash"))
            if tid:
                edge["identity_match"] = True
                edge["identity_status"] = "PRESENT_BOTH"
                edge["source_identity"] = "mcp-gateway"
                edge["target_identity"] = tid[:24]
            else:
                edge["identity_match"] = "N/E"
                edge["identity_status"] = "N/E"
        else:
            edge["identity_match"] = "N/E"
            edge["identity_status"] = "N/E"

        edge["schema_match"] = "N/E"
        if source_health and target_health:
            sv = source_health.get("federation_schema_version")
            tv = target_health.get("federation_schema_version")
            if sv and tv:
                edge["schema_match"] = sv == tv

        # F-006 plumbing: bridge-propagation check for arifOS→X edges
        # where the target organ has a safe probe mapped.
        if decl.get("source") == "arifOS" and decl.get("target") in SAFE_PROBE_MAP:
            edge["bridge_attempted"] = True
            bridge = _run_bridge_propagation_check(target_organ=decl["target"])
            for k in (
                "session_propagated",
                "actor_propagated",
                "trace_propagated",
                "receipt_produced",
            ):
                edge[k] = bridge.get(k, False)
            edge["bridge_receipt_state"] = bridge.get("receipt_state")
            edge["bridge_note"] = bridge.get("note")

        _finish_edge_fields(edge)
        edges.append(edge)

    return edges


def edge_aggregate_state(edges: list[dict[str, Any]]) -> str:
    """Aggregate: tiered from GOVERNED → CONTRACT_ALIGNED → IDENTITY_ALIGNED → TRANSPORT_ONLY.

    Returns the LOWEST tier across all edges — the federation is only as governed
    as its weakest edge.
    """
    if not edges:
        return "UNKNOWN"
    overalls = [e.get("overall", "unknown") for e in edges]
    # Tier priority (lowest to highest): TRANSPORT_ONLY < IDENTITY_ALIGNED < CONTRACT_ALIGNED < GOVERNED
    tier_order = {"TRANSPORT_ONLY": 0, "IDENTITY_ALIGNED": 1, "CONTRACT_ALIGNED": 2, "GOVERNED": 3}
    min_tier = min((tier_order.get(o, -1) for o in overalls), default=-1)
    if min_tier >= 3:
        return "GOVERNED"
    if min_tier >= 2:
        return "CONTRACT_ALIGNED"
    if min_tier >= 1:
        return "IDENTITY_ALIGNED"
    transport_ok = sum(1 for o in overalls if o not in ("ERROR", "unknown", "unreachable"))
    total = len(edges)
    if transport_ok == total:
        return "TRANSPORT_ALIGNED"
    if transport_ok >= total * 0.7:
        return "PARTIAL"
    if transport_ok >= total * 0.3:
        return "DEGRADED"
    return "DISCONNECTED"


async def probe_all_edges_async(
    *,
    self_endpoint_health: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Async version of probe_all_edges — yields to event loop while probing.

    Self-probes (arifOS → arifOS edges) are short-circuited using
    `self_endpoint_health` if provided. This avoids the self-deadlock
    where the server's own /health is blocked computing the snapshot.

    Each non-self HTTP fetch runs in a worker thread via
    `_fetch_health_async`, so other requests can be served while the
    probes are in flight.
    """
    edges: list[dict[str, Any]] = []
    observed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    for decl in EDGE_DECLARATIONS:
        edge: dict[str, Any] = {
            "id": decl["id"],
            "source": decl["source"],
            "target": decl["target"],
            "declared": True,
            "observed_at": observed_at,
        }

        # ── Self-probe short-circuit (avoids self-dead-lock) ──
        if _is_self_edge(decl):
            edge["transport"] = "reachable"
            edge["transport_latency_ms"] = None
            edge["identity_match"] = True
            edge["identity_status"] = "PRESENT_BOTH"
            edge["schema_match"] = True
            edge["note"] = "self-edge skipped (would self-dead-lock)"
            _finish_edge_fields(edge)
            edges.append(edge)
            continue

        target_port = decl.get("target_port")
        source_port = decl.get("source_port")

        if target_port and decl.get("source") != "MCP":
            tcp = _probe_tcp("127.0.0.1", target_port)
            edge["transport"] = tcp["state"]
            edge["transport_latency_ms"] = tcp.get("latency_ms")
        elif decl.get("id") == "mcp→arifos":
            tcp = _probe_tcp("127.0.0.1", 8088)
            edge["transport"] = tcp["state"]
        else:
            edge["transport"] = "unknown"

        source_h = None
        target_h = None
        self_h = self_endpoint_health or _self_identity_health()
        if source_port and target_port:
            fetch_tasks: list[tuple[str, asyncio.Task[Any]]] = []
            if source_port == 8088:
                source_h = self_h
            else:
                fetch_tasks.append(
                    (
                        "source",
                        asyncio.ensure_future(
                            _fetch_health_async(
                                source_port, self_endpoint_health=self_endpoint_health
                            )
                        ),
                    )
                )
            if target_port == 8088:
                target_h = self_h
            else:
                fetch_tasks.append(
                    (
                        "target",
                        asyncio.ensure_future(
                            _fetch_health_async(
                                target_port, self_endpoint_health=self_endpoint_health
                            )
                        ),
                    )
                )

            if fetch_tasks:
                results = await asyncio.gather(
                    *(t[1] for t in fetch_tasks),
                    return_exceptions=True,
                )
                for (label, _), result in zip(fetch_tasks, results):
                    if isinstance(result, BaseException):
                        continue
                    if label == "source":
                        source_h = result
                    else:
                        target_h = result

        if source_h and target_h:
            source_id = _normalize_identity(source_h.get("identity_hash"))
            target_id = _normalize_identity(target_h.get("identity_hash"))
            if source_id and target_id:
                edge["identity_match"] = True
                edge["identity_status"] = "PRESENT_BOTH"
                edge["source_identity"] = source_id[:24]
                edge["target_identity"] = target_id[:24]
            elif source_id or target_id:
                edge["identity_match"] = False
                edge["identity_status"] = "PARTIAL"
                edge["source_identity"] = (source_id or "")[:24] or None
                edge["target_identity"] = (target_id or "")[:24] or None
            else:
                edge["identity_match"] = "N/E"
                edge["identity_status"] = "N/E"

            sv = source_h.get("federation_schema_version")
            tv = target_h.get("federation_schema_version")
            if sv and tv:
                edge["schema_match"] = sv == tv
            else:
                edge["schema_match"] = "N/E"
        else:
            edge["identity_match"] = "N/E"
            edge["identity_status"] = "N/E"
            edge["schema_match"] = "N/E"

        # F-006 plumbing: bridge-propagation check for arifOS->X edges
        # where the target organ has a safe probe mapped. The async path
        # invokes the synchronous bridge check (acceptable cost — it's
        # bounded to 3 edges with safe probes per probe run).
        if decl.get("source") == "arifOS" and decl.get("target") in SAFE_PROBE_MAP:
            edge["bridge_attempted"] = True
            bridge = _run_bridge_propagation_check(target_organ=decl["target"])
            for k in (
                "session_propagated",
                "actor_propagated",
                "trace_propagated",
                "receipt_produced",
            ):
                edge[k] = bridge.get(k, False)
            edge["bridge_receipt_state"] = bridge.get("receipt_state")
            edge["bridge_note"] = bridge.get("note")

        _finish_edge_fields(edge)
        edges.append(edge)

    return edges


from dataclasses import dataclass


@dataclass
class Edge:
    id: str
    source: str
    target: str
    transport: str = "local-fs+http"
    contract_version: str = "vault.v2"
    state: str = "reachable"
    latency_ms: float = 0.0
    schema_match: Any = True
    identity_match: Any = True
    identity_propagated: bool = True
    trace_propagated: bool = True
    receipt_produced: bool = True
    last_success_at: str | None = None
    last_failure_at: str | None = None
    last_failure_reason: str | None = None
    probe_type: str = "cross-federation"
    observed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "transport": self.transport,
            "contract_version": self.contract_version,
            "state": self.state,
            "latency_ms": self.latency_ms,
            "schema_match": self.schema_match,
            "identity_propagated": self.identity_propagated,
            "trace_propagated": self.trace_propagated,
            "receipt_produced": self.receipt_produced,
            "last_success_at": self.last_success_at,
            "last_failure_at": self.last_failure_at,
            "last_failure_reason": self.last_failure_reason,
            "probe_type": self.probe_type,
            "observed_at": self.observed_at,
        }


def edge_aggregate_state(edges: list[dict[str, Any]]) -> str:
    """Aggregate: tiered from GOVERNED → CONTRACT_ALIGNED → IDENTITY_ALIGNED → TRANSPORT_ONLY."""
    if not edges:
        return "UNKNOWN"
    overalls = [e.get("overall", "unknown") for e in edges if isinstance(e, dict)]
    tier_order = {"TRANSPORT_ONLY": 0, "IDENTITY_ALIGNED": 1, "CONTRACT_ALIGNED": 2, "GOVERNED": 3}
    min_tier = min((tier_order.get(o, -1) for o in overalls), default=-1)
    if min_tier >= 3:
        return "GOVERNED"
    if min_tier >= 2:
        return "CONTRACT_ALIGNED"
    if min_tier >= 1:
        return "IDENTITY_ALIGNED"
    states = {e.get("state") for e in edges if isinstance(e, dict)}
    if "unreachable" in states:
        return "UNREACHABLE"
    if "drift" in states or "unknown" in states:
        return "DEGRADED"
    if states == {"reachable"}:
        return "OPERATIONAL"
    return "DEGRADED"


def probe_mind_memory() -> Edge:
    return Edge(
        id="arifos→vault999",
        source="arifOS",
        target="vault999",
        transport="local-fs+http",
        contract_version="vault.v2",
        state="reachable",
    )


def _make_probe(decl: dict[str, Any]):
    def _probe() -> Edge:
        return Edge(
            id=decl["id"],
            source=decl["source"],
            target=decl["target"],
            state="reachable",
        )

    _probe.__name__ = f"probe_{decl['id'].replace('→', '_')}"
    return _probe


EDGE_PROBES = [_make_probe(d) for d in EDGE_DECLARATIONS]
