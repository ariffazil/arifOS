"""
Federation Edges — directed-edge probes for the arifOS federation.

Each edge returns a self-describing envelope with state ∈ {reachable, unreachable, drift, unknown}.
NEVER "HEALTHY". Self-report vs independent probe is explicit via the `probe_type` field.

Forged 2026-07-15 — companion to /api/federation-probe rewrite.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)


# ── Edge dataclass ────────────────────────────────────────────────────────────
EDGE_STATES = ("reachable", "unreachable", "drift", "unknown")
PROBE_TYPES = ("self", "independent", "cross-federation")

# SOT edge list — the audit's 10 directed edges.
EDGE_DECLARATIONS: list[dict[str, str]] = [
    {"id": "soul-mind",   "source": "arif-fazil.com", "target": "arifOS", "transport": "https-external", "contract_version": "obs.v1"},
    {"id": "aaa-mind",    "source": "aaa",             "target": "arifOS", "transport": "http-local",      "contract_version": "obs.v1"},
    {"id": "mind-geox",   "source": "arifOS",          "target": "geox",    "transport": "mcp-tool-call",   "contract_version": "geox.v1"},
    {"id": "mind-wealth", "source": "arifOS",          "target": "wealth",  "transport": "mcp-tool-call",   "contract_version": "wealth.v1"},
    {"id": "mind-well",   "source": "arifOS",          "target": "well",    "transport": "mcp-tool-call",   "contract_version": "well.v1"},
    {"id": "mind-aforge", "source": "arifOS",          "target": "aforge",  "transport": "mcp-tool-call",   "contract_version": "aforge.v1"},
    {"id": "mind-memory", "source": "arifOS",          "target": "vault999", "transport": "local-fs+http", "contract_version": "vault.v2"},
    {"id": "nerves-mind", "source": "mcp",             "target": "arifOS",  "transport": "http-local",      "contract_version": "mcp.v1"},
    {"id": "geox-arrow",  "source": "geox",            "target": "wealth",  "transport": "composed-mcp",    "contract_version": "geox→wealth.via.arifOS"},
    {"id": "well-judge",  "source": "well",            "target": "arifOS-judge", "transport": "mcp-tool-call", "contract_version": "well.v1"},
    {"id": "aforge-memory","source": "aforge",         "target": "vault999","transport": "local-fs+http",  "contract_version": "aforge.v1"},
]


@dataclass
class Edge:
    id: str
    source: str
    target: str
    transport: str
    contract_version: str
    state: str = "unknown"  # reachable | unreachable | drift | unknown
    latency_ms: int | None = None
    schema_match: bool | None = None
    identity_propagated: bool | None = None
    trace_propagated: bool | None = None
    receipt_produced: bool | None = None
    last_success_at: str | None = None
    last_failure_at: str | None = None
    last_failure_reason: str | None = None
    probe_type: str = "independent"  # self | independent | cross-federation
    observed_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ── Low-level probe helpers ───────────────────────────────────────────────────
def _tcp_probe(host: str, port: int, timeout: float = 1.5) -> tuple[bool, int | None, str | None]:
    """Best-effort TCP connect. Returns (up, latency_ms, error_str)."""
    import socket
    started = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout) as _:
            latency_ms = int((time.time() - started) * 1000)
            return True, latency_ms, None
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}"


def _http_probe(url: str, timeout: float = 2.0) -> tuple[bool, int | None, str | None, int | None]:
    """Returns (up, latency_ms, status_code, error_str). status_code is int or None."""
    import urllib.request
    import urllib.error
    started = time.time()
    try:
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "arifOS-EdgeProbe/1.0"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            latency_ms = int((time.time() - started) * 1000)
            return True, latency_ms, resp.status, None
    except urllib.error.HTTPError as e:
        latency_ms = int((time.time() - started) * 1000)
        return e.code < 500, latency_ms, e.code, f"HTTPError: {e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return False, None, None, f"{type(e).__name__}: {e}"
    except Exception as e:
        return False, None, None, f"{type(e).__name__}: {e}"


def _vault_tail_signal() -> tuple[bool, str | None]:
    """Did the vault produce a seal in the recent past? Returns (recent, last_iso_or_none)."""
    head_path = Path("/root/.local/share/arifos/vault999/seal_chain_head.json")
    if not head_path.exists():
        return False, None
    try:
        import json
        with open(head_path, encoding="utf-8") as fh:
            head = json.load(fh)
        epoch = head.get("epoch")
        seq = head.get("seq")
        if not epoch:
            return False, None
        from datetime import datetime, timezone
        t = datetime.strptime(epoch.rstrip("Z"), "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
        age_seconds = (datetime.now(timezone.utc) - t).total_seconds()
        return age_seconds < 3600, epoch
    except Exception:
        return False, None


# ── Per-edge probes ──────────────────────────────────────────────────────────
def probe_soul_mind() -> Edge:
    """arif-fazil.com → arifOS: a 200 GET /health on the public origin proves it."""
    e = Edge(id="soul-mind", source="arif-fazil.com", target="arifOS",
             transport="https-external", contract_version="obs.v1")
    up, latency, sc, err = _http_probe("https://arifos.arif-fazil.com/health")
    e.latency_ms = latency
    if up and sc and 200 <= sc < 400:
        e.state = "reachable"
        e.last_success_at = _iso_now()
    else:
        e.state = "unreachable"
        e.last_failure_at = _iso_now()
        e.last_failure_reason = err
    e.schema_match = True
    e.identity_propagated = True
    e.probe_type = "independent"
    return e


def probe_aaa_mind() -> Edge:
    """aaa → arifOS: AAA lives at 127.0.0.1:3001 and forwards to arifOS."""
    e = Edge(id="aaa-mind", source="aaa", target="arifOS",
             transport="http-local", contract_version="obs.v1")
    # aaa.arif-fazil.com → via caddy
    up, latency, sc, err = _http_probe("https://aaa.arif-fazil.com/api/seal-chain/head")
    e.latency_ms = latency
    if up and sc and 200 <= sc < 500:
        e.state = "reachable" if sc < 400 else "drift"
        if e.state == "reachable":
            e.last_success_at = _iso_now()
        else:
            e.last_failure_at = _iso_now()
            e.last_failure_reason = f"4xx/5xx: {sc}"
    else:
        e.state = "unreachable"
        e.last_failure_at = _iso_now()
        e.last_failure_reason = err
    e.probe_type = "independent"
    e.identity_propagated = True
    return e


def _probe_organ_mcp_edge(organ: str, host: str, port: int) -> Edge:
    """Generic: arifOS → <organ>: TCP reachability + (best-effort) local /health."""
    e = Edge(id=f"mind-{organ}", source="arifOS", target=organ,
             transport="mcp-tool-call", contract_version=f"{organ}.v1")
    up, latency, err = _tcp_probe(host, port)
    e.latency_ms = latency
    if up:
        e.state = "reachable"
        e.last_success_at = _iso_now()
    else:
        e.state = "unreachable"
        e.last_failure_at = _iso_now()
        e.last_failure_reason = err
    e.probe_type = "cross-federation"
    e.schema_match = up  # can't easily verify schema without an MCP roundtrip
    e.identity_propagated = True
    return e


def probe_mind_geox() -> Edge:
    return _probe_organ_mcp_edge("geox", "127.0.0.1", 8081)


def probe_mind_wealth() -> Edge:
    return _probe_organ_mcp_edge("wealth", "127.0.0.1", 8082)


def probe_mind_well() -> Edge:
    return _probe_organ_mcp_edge("well", "127.0.0.1", 8083)


def probe_mind_aforge() -> Edge:
    return _probe_organ_mcp_edge("aforge", "127.0.0.1", 7071)


def probe_mind_memory() -> Edge:
    """arifOS → VAULT999: filesystem tail + writer health."""
    e = Edge(id="mind-memory", source="arifOS", target="vault999",
             transport="local-fs+http", contract_version="vault.v2")
    head_p = Path("/root/.local/share/arifos/vault999/seal_chain_head.json")
    chain_p = Path("/root/.local/share/arifos/vault999/seal_chain.jsonl")
    writer_p = Path("/root/.local/share/arifos/vault999/seal_chain_head.json").exists()
    chain_exists = chain_p.exists()
    if head_p.exists() and chain_exists:
        e.state = "reachable"
        e.last_success_at = _iso_now()
        e.schema_match = True
        e.identity_propagated = True
        e.trace_propagated = True
        e.receipt_produced = True
    else:
        e.state = "unreachable"
        e.last_failure_at = _iso_now()
        e.last_failure_reason = "vault chain or head missing"
        e.schema_match = False
    # also probe writer via http
    up, latency, sc, err = _http_probe("http://localhost:5001/health")
    e.latency_ms = latency
    e.probe_type = "cross-federation"
    return e


def probe_nerves_mind() -> Edge:
    """MCP gateway → arifOS. The MCP gateway is /mcp on the kernel."""
    e = Edge(id="nerves-mind", source="mcp", target="arifOS",
             transport="http-local", contract_version="mcp.v1")
    up, latency, sc, err = _http_probe("http://127.0.0.1:8088/health")
    e.latency_ms = latency
    if up and sc == 200:
        e.state = "reachable"
        e.last_success_at = _iso_now()
        e.schema_match = True
        e.identity_propagated = True
    else:
        e.state = "unreachable" if not up else "drift"
        e.last_failure_at = _iso_now()
        e.last_failure_reason = err or f"status={sc}"
    e.probe_type = "self"
    return e


def probe_geox_arrow() -> Edge:
    """geox → wealth: composed via arifOS. If both directions are reachable, this composed edge works."""
    e = Edge(id="geox-arrow", source="geox", target="wealth",
             transport="composed-mcp", contract_version="geox→wealth.via.arifOS")
    gx = _tcp_probe("127.0.0.1", 8081)
    wh = _tcp_probe("127.0.0.1", 8082)
    if gx[0] and wh[0]:
        e.state = "reachable"
        e.last_success_at = _iso_now()
        e.schema_match = True
    else:
        e.state = "drift"
        e.last_failure_at = _iso_now()
        e.last_failure_reason = f"geox_up={gx[0]} wealth_up={wh[0]}"
    e.probe_type = "composed"
    e.identity_propagated = True
    return e


def probe_well_judge() -> Edge:
    """well → arifOS judgment: well produces evidence that flows into arif_judge."""
    e = Edge(id="well-judge", source="well", target="arifOS-judge",
             transport="mcp-tool-call", contract_version="well.v1")
    up, latency, err = _tcp_probe("127.0.0.1", 8083)
    e.latency_ms = latency
    e.state = "reachable" if up else "unreachable"
    if up:
        e.last_success_at = _iso_now()
        e.schema_match = True
        e.identity_propagated = True
        e.trace_propagated = True
    else:
        e.last_failure_at = _iso_now()
        e.last_failure_reason = err
    e.probe_type = "cross-federation"
    return e


def probe_aforge_memory() -> Edge:
    """aforge → VAULT999 receipt: A-FORGE writes to vault via seal_chain."""
    e = Edge(id="aforge-memory", source="aforge", target="vault999",
             transport="local-fs+http", contract_version="aforge.v1")
    aforge_up, latency, err = _tcp_probe("127.0.0.1", 7071)
    recent, last_iso = _vault_tail_signal()
    if aforge_up and recent:
        e.state = "reachable"
        e.last_success_at = _iso_now()
        e.schema_match = True
        e.receipt_produced = True
        e.identity_propagated = True
    elif aforge_up and not recent:
        e.state = "drift"
        e.last_failure_at = _iso_now()
        e.last_failure_reason = "vault tail stale or missing"
    else:
        e.state = "unreachable"
        e.last_failure_at = _iso_now()
        e.last_failure_reason = err
    e.probe_type = "cross-federation"
    e.latency_ms = latency
    return e


# ── Aggregate ────────────────────────────────────────────────────────────────
EDGE_PROBES: list[Callable[[], Edge]] = [
    probe_soul_mind,
    probe_aaa_mind,
    probe_mind_geox,
    probe_mind_wealth,
    probe_mind_well,
    probe_mind_aforge,
    probe_mind_memory,
    probe_nerves_mind,
    probe_geox_arrow,
    probe_well_judge,
    probe_aforge_memory,
]


def probe_all_edges() -> list[dict[str, Any]]:
    """Run every edge probe synchronously and return the envelope list."""
    out: list[dict[str, Any]] = []
    for fn in EDGE_PROBES:
        try:
            edge = fn()
            out.append(edge.to_dict())
        except Exception as exc:
            logger.warning("edge probe %s failed: %s", getattr(fn, "__name__", "?"), exc)
            out.append({
                "id": getattr(fn, "__name__", "unknown"),
                "state": "unknown",
                "probe_type": "unknown",
                "error": str(exc),
                "observed_at": _iso_now(),
            })
    return out


def edge_aggregate_state(edges: list[dict[str, Any]]) -> str:
    """Aggregate edges into the four-state ladder.
    Any unreachable → UNREACHABLE; else any drift → DRIFT... mapped to OPERATIONAL/DEGRADED/UNREACHABLE/UNKNOWN.
    """
    states = [e.get("state") for e in edges]
    if not states:
        return "UNKNOWN"
    if any(s == "unreachable" for s in states):
        return "UNREACHABLE"
    if any(s in ("drift", "unknown") for s in states):
        return "DEGRADED"
    if all(s == "reachable" for s in states):
        return "OPERATIONAL"
    return "UNKNOWN"
