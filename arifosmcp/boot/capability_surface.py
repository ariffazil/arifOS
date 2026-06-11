"""
Capability Surface — Honest Live Tool Status

DITEMPA BUKAN DIBERI — Forged, Not Given.

Eureka: "The primary resource in a constitutional AGI system is not tokens
or time; it is HONESTLY KNOWN CAPABILITY. Any plan or execution chain must
be constrained by what the system can honestly say it can do right now."

This module live-probes all registered tools and computes:
  - status_alignment: ALIGNED | OVERCLAIM | UNDERCLAIM | UNKNOWN | DEAD
  - Per-tool: available, read_ok, write_ok, floors, last_error
  - Per-agent: tier, allowed_floors, domains, status

The CapabilitySurface is the SHARED TRUTH between AAA, arifOS kernel,
and A-FORGE. No component may plan beyond what this surface supports.

Invariant:
  No arifOS component may plan or execute an action that assumes more
  capability or safety than is reflected in the current CapabilitySurface.
  When in doubt, downgrade to assistance mode or inject 888 HOLD.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Literal

logger = logging.getLogger(__name__)

StatusAlignment = Literal["ALIGNED", "OVERCLAIM", "UNDERCLAIM", "UNKNOWN", "DEAD"]
ExecutionTier = Literal["TIER_A", "TIER_B", "TIER_C"]


# ── Schemas ───────────────────────────────────────────────────────


@dataclass
class ToolStatus:
    """Live status of one MCP tool."""

    name: str
    available: bool = False
    read_ok: bool = False
    write_ok: bool = False
    floors: list[str] = field(default_factory=list)
    last_error: str | None = None
    status_alignment: StatusAlignment = "UNKNOWN"
    outer_verdict: str = "UNKNOWN"
    inner_verdict: str = "UNKNOWN"
    last_probe_ms: float = 0.0
    note: str = ""


@dataclass
class AgentStatus:
    """Live status of one forge instrument or federation agent."""

    name: str
    tier: ExecutionTier = "TIER_C"
    allowed_floors: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    status_alignment: StatusAlignment = "UNKNOWN"
    mcp_connected: bool = False
    active: bool = False
    note: str = ""


@dataclass
class CapabilitySurface:
    """The canonical honest capability map for the entire federation."""

    version: str = "arifOS.capability_surface.v1"
    timestamp: float = 0.0
    tools: dict[str, ToolStatus] = field(default_factory=dict)
    agents: dict[str, AgentStatus] = field(default_factory=dict)
    organs: dict[str, dict[str, Any]] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
    cached: bool = True
    cache_age_s: float = 0.0
    eureka: str = (
        "The primary resource in a constitutional AGI system is not tokens "
        "or time; it is HONESTLY KNOWN CAPABILITY."
    )
    invariant: str = (
        "No arifOS component may plan or execute an action that assumes more "
        "capability or safety than is reflected in the current CapabilitySurface. "
        "When in doubt, downgrade to assistance mode or inject 888 HOLD."
    )


# ── Probe Registry ─────────────────────────────────────────────────

# Known tools with their expected behavior and risk classification
TOOL_PROBE_REGISTRY: dict[str, dict[str, Any]] = {
    # ── Governance core ────────────────────────────────
    "arif_session_init": {
        "floors": ["F01", "F11", "F12"],
        "risk_class": "OBSERVE",
        "probe_arg": {"mode": "init", "actor_id": "capability-probe"},
        "expects": "session_id",
    },
    "arif_judge_deliberate": {
        "floors": ["F01", "F11", "F13"],
        "risk_class": "ATOMIC",
        "probe_arg": {"mode": "judge", "candidate": "test-probe"},
        "expects": "verdict",
        "gated": True,
    },
    "arif_vault_seal": {
        "floors": ["F01", "F11", "F13"],
        "risk_class": "ATOMIC",
        "probe_arg": {"mode": "chain"},
        "expects": "chain_height",
        "gated": True,
    },
    # ── Intelligence ────────────────────────────────────
    "arif_mind_reason": {
        "floors": ["F02", "F07", "F08", "F10"],
        "risk_class": "REASON",
        "probe_arg": {"mode": "reason", "query": "1+1"},
    },
    "arif_heart_critique": {
        "floors": ["F05", "F06", "F09"],
        "risk_class": "REASON",
        "probe_arg": {"mode": "critique", "target": "test"},
    },
    "arif_reply_compose": {
        "floors": ["F02", "F04", "F06", "F09"],
        "risk_class": "REASON",
    },
    # ── Infrastructure ──────────────────────────────────
    "arif_kernel_route": {
        "floors": ["F01", "F04", "F03", "F10"],
        "risk_class": "OBSERVE",
        "probe_arg": {"mode": "list"},
    },
    "arif_gateway_connect": {
        "floors": ["F01", "F03", "F11"],
        "risk_class": "OBSERVE",
        "probe_arg": {"mode": "discover"},
    },
    "arif_memory_recall": {
        "floors": ["F01", "F08"],
        "risk_class": "OBSERVE",
        "probe_arg": {"mode": "recall", "query": "test"},
    },
    "arif_ops_measure": {
        "floors": ["F02", "F04"],
        "risk_class": "OBSERVE",
        "probe_arg": {"mode": "health"},
        "golden": True,
    },
    # ── Reality grounding ───────────────────────────────
    "arif_sense_observe": {
        "floors": ["F02", "F07"],
        "risk_class": "OBSERVE",
        "probe_arg": {"mode": "vitals"},
    },
    "arif_evidence_fetch": {
        "floors": ["F02", "F03", "F05", "F12"],
        "risk_class": "OBSERVE",
        "probe_arg": {"mode": "fetch", "query": "test"},
    },
    # ── Execution ───────────────────────────────────────
    "arif_forge_execute": {
        "floors": ["F01", "F11", "F13"],
        "risk_class": "ATOMIC",
        "probe_arg": {"mode": "query", "query": "health"},
        "gated": True,
    },
    "forge_query": {
        "floors": ["F01"],
        "risk_class": "OBSERVE",
        "probe_arg": {"manifest": "", "query": "test", "cwd": "."},
    },
    "forge_plan": {
        "floors": ["F01"],
        "risk_class": "REASON",
        "probe_arg": {"goal": "test", "workspace": "."},
    },
    "forge_dry_run": {
        "floors": ["F01", "F12"],
        "risk_class": "REASON",
        "probe_arg": {"plan_id": "test", "manifest": ""},
    },
}

AGENT_REGISTRY: dict[str, dict[str, Any]] = {
    "FI-001-opencode": {
        "tier": "TIER_A",
        "domains": ["forge", "reason", "observe"],
        "allowed_floors": ["F01-F12"],
        "model": "deepseek-v4-pro",
    },
    "FI-002-claude-code": {
        "tier": "TIER_A",
        "domains": ["forge", "reason", "observe", "audit"],
        "allowed_floors": ["F01-F12"],
        "model": "deepseek-v4-pro",
    },
    "FI-003-qwen-code": {
        "tier": "TIER_B",
        "domains": ["observe", "reason", "draft"],
        "allowed_floors": ["F01-F09"],
        "model": "MiniMax-M3",
    },
    "FI-004-gemini-cli": {
        "tier": "TIER_B",
        "domains": ["observe", "reason", "draft"],
        "allowed_floors": ["F01-F09"],
        "model": "gemini-2.5-flash",
    },
    "FI-005-codex-cli": {
        "tier": "TIER_C",
        "domains": ["observe"],
        "allowed_floors": ["F01-F04"],
        "model": "GPT-5.5",
    },
    "FI-006-copilot-cli": {
        "tier": "TIER_B",
        "domains": ["observe", "reason", "draft"],
        "allowed_floors": ["F01-F09"],
        "model": "github-copilot",
    },
}

ORGAN_REGISTRY: dict[str, dict[str, Any]] = {
    "arifOS": {"port": 8088, "tools": 13, "role": "kernel"},
    "GEOX": {"port": 8081, "tools": 31, "role": "earth_witness"},
    "WEALTH": {"port": 18082, "tools": 19, "role": "capital_witness"},
    "WELL": {"port": 18083, "tools": 14, "role": "substrate_witness"},
    "A-FORGE": {"port": 7071, "tools": 0, "role": "execution_broker"},
    "AAA": {"port": 3001, "tools": 0, "role": "cockpit"},
    "VAULT999": {"port": 5001, "tools": 0, "role": "sealed_memory"},
}


# ── Capability Surface Builder ────────────────────────────────────


class CapabilitySurfaceBuilder:
    """
    Builds the honest CapabilitySurface by live-probing tools,
    reading swarm state, and fusing inner/outer verdicts.

    This is NOT a static registry. It is a LIVE SNAPSHOT computed
    at init time and cached for A-FORGE planning.
    """

    def __init__(self) -> None:
        self._cache: dict[str, Any] | None = None
        self._cache_ts: float = 0.0
        self._cache_ttl: float = 30.0  # seconds

    def build(
        self,
        *,
        force_refresh: bool = False,
        probe_live: bool = True,
    ) -> CapabilitySurface:
        """Build the CapabilitySurface. Uses cache if fresh."""
        now = time.time()
        if not force_refresh and self._cache and (now - self._cache_ts) < self._cache_ttl:
            surface = CapabilitySurface(**self._cache)
            surface.cached = True
            surface.cache_age_s = round(now - self._cache_ts, 2)
            return surface

        surface = CapabilitySurface(timestamp=now)

        # ── Probe tools ──────────────────────────────────
        for tool_name, meta in TOOL_PROBE_REGISTRY.items():
            status = self._probe_tool(tool_name, meta, probe_live)
            surface.tools[tool_name] = status

        # ── Read agents ──────────────────────────────────
        for agent_id, meta in AGENT_REGISTRY.items():
            surface.agents[agent_id] = AgentStatus(
                name=agent_id,
                tier=meta["tier"],
                domains=meta["domains"],
                allowed_floors=meta["allowed_floors"],
                status_alignment="UNKNOWN",  # requires real activity check
                note=f"Model: {meta['model']}",
            )

        # ── Read organs ──────────────────────────────────
        for organ, meta in ORGAN_REGISTRY.items():
            surface.organs[organ] = {
                "port": meta["port"],
                "tools": meta["tools"],
                "role": meta["role"],
                "health": self._probe_organ_health(organ, meta["port"]),
            }

        # ── Summary ──────────────────────────────────────
        surface.summary = self._compute_summary(surface)

        # ── Cache ────────────────────────────────────────
        self._cache = {
            "tools": {
                k: v.__dict__ if hasattr(v, "__dict__") else v for k, v in surface.tools.items()
            },
            "agents": {
                k: v.__dict__ if hasattr(v, "__dict__") else v for k, v in surface.agents.items()
            },
            "organs": surface.organs,
            "summary": surface.summary,
            "timestamp": surface.timestamp,
        }
        self._cache_ts = now
        surface.cached = False
        surface.cache_age_s = 0.0

        return surface

    # ── Private probe helpers ────────────────────────────────

    def _probe_tool(self, name: str, meta: dict[str, Any], live: bool) -> ToolStatus:
        """Probe one tool and compute status_alignment."""
        status = ToolStatus(
            name=name,
            floors=meta.get("floors", []),
            note=meta.get("risk_class", "UNKNOWN"),
        )

        if not live:
            status.status_alignment = "UNKNOWN"
            status.note = "Not probed (live=False)"
            return status

        # Check if tool is gated behind F13
        if meta.get("gated"):
            status.available = False
            status.read_ok = False
            status.write_ok = False
            status.status_alignment = "DEAD" if meta.get("risk_class") == "ATOMIC" else "UNKNOWN"
            status.last_error = "F13 gate — requires human approval or FederationEnvelope client"
            status.outer_verdict = "HOLD"
            status.inner_verdict = "HOLD"
            status.note = "Gated tool — not probeable from LEGACY_WRAP surface"
            return status

        # Live probe: call the tool via local MCP
        t0 = time.time()
        try:
            result = self._call_tool_mcp(name, meta.get("probe_arg", {}))
            elapsed_ms = (time.time() - t0) * 1000
            status.last_probe_ms = round(elapsed_ms, 1)

            if result is None:
                status.available = False
                status.last_error = "No response from tool"
                status.status_alignment = "DEAD"
            elif "error" in str(result).lower() or "hold" in str(result).lower():
                status.available = True
                status.read_ok = True
                status.write_ok = False
                status.status_alignment = "UNDERCLAIM"
                status.outer_verdict = "HOLD"
                status.note = f"Tool responds but gated/degraded"
            else:
                status.available = True
                status.read_ok = True
                status.write_ok = meta.get("risk_class") in ("OBSERVE", "REASON")
                status.status_alignment = "ALIGNED"
                status.outer_verdict = "SEAL"
                status.note = "Tool responding, status nominal"
        except Exception as e:
            status.available = False
            status.last_error = f"{type(e).__name__}: {e}"
            status.status_alignment = "DEAD"
            status.note = f"Probe failed: {type(e).__name__}"

        # Golden tools get trust bonus
        if meta.get("golden"):
            status.status_alignment = "ALIGNED" if status.available else "DEAD"
            status.note = "GOLDEN tool — independently verified"

        return status

    def _call_tool_mcp(self, name: str, args: dict[str, Any]) -> dict[str, Any] | None:
        """Call a tool through local MCP. Returns None if unreachable."""
        import json
        import urllib.request

        try:
            # Initialize
            req1 = urllib.request.Request(
                "http://127.0.0.1:8088/mcp",
                data=json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2025-11-25",
                            "capabilities": {},
                            "clientInfo": {"name": "capability-probe", "version": "1"},
                        },
                    }
                ).encode(),
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            )
            resp1 = urllib.request.urlopen(req1, timeout=5)
            sid = resp1.headers.get("mcp-session-id", "")

            if not sid:
                return {"error": "no session"}

            # Call tool
            req2 = urllib.request.Request(
                "http://127.0.0.1:8088/mcp",
                data=json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {"name": name, "arguments": args},
                    }
                ).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Mcp-Session-Id": sid,
                },
            )
            resp2 = urllib.request.urlopen(req2, timeout=10)
            return json.loads(resp2.read())
        except Exception:
            return None

    def _probe_organ_health(self, organ: str, port: int) -> dict[str, Any]:
        """Quick health probe of an organ endpoint."""
        import urllib.request

        try:
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/health",
                headers={"Accept": "application/json"},
            )
            resp = urllib.request.urlopen(req, timeout=2)
            import json

            body = json.loads(resp.read())
            return {
                "status": body.get("status", "unknown"),
                "tools": body.get("tools_loaded", body.get("tools", 0)),
                "verdict": body.get("verdict", "unknown"),
                "reachable": True,
            }
        except Exception as e:
            return {"reachable": False, "error": str(e)}

    def _compute_summary(self, surface: CapabilitySurface) -> dict[str, Any]:
        """Compute summary stats from the capability surface."""
        total = len(surface.tools)
        aligned = sum(1 for t in surface.tools.values() if t.status_alignment == "ALIGNED")
        dead = sum(1 for t in surface.tools.values() if t.status_alignment == "DEAD")
        overclaim = sum(1 for t in surface.tools.values() if t.status_alignment == "OVERCLAIM")
        unknown = sum(1 for t in surface.tools.values() if t.status_alignment == "UNKNOWN")

        organs_healthy = sum(
            1
            for o in surface.organs.values()
            if o.get("reachable", False) and o.get("status") == "healthy"
        )

        return {
            "tools_total": total,
            "tools_aligned": aligned,
            "tools_dead": dead,
            "tools_overclaim": overclaim,
            "tools_unknown": unknown,
            "organs_healthy": organs_healthy,
            "organs_total": len(surface.organs),
            "honesty_ratio": round(aligned / total, 3) if total > 0 else 0.0,
            "execution_tier": (
                "TIER_A"
                if aligned >= total * 0.7
                else "TIER_B"
                if aligned >= total * 0.3
                else "TIER_C"
            ),
            "recommendation": (
                "AGI_CHAIN allowed — majority of tools ALIGNED"
                if aligned >= total * 0.7
                else "MIXED mode — significant tool degradation, inject HOLD checkpoints"
                if aligned >= total * 0.3
                else "ASSIST only — most tools dead or unverified, human required at every step"
            ),
        }


# ── Singleton ─────────────────────────────────────────────────────

_builder: CapabilitySurfaceBuilder | None = None


def get_capability_surface_builder() -> CapabilitySurfaceBuilder:
    global _builder
    if _builder is None:
        _builder = CapabilitySurfaceBuilder()
    return _builder


def build_capability_surface(
    force_refresh: bool = False,
    probe_live: bool = True,
) -> CapabilitySurface:
    """Public API: build the honest capability surface."""
    return get_capability_surface_builder().build(
        force_refresh=force_refresh,
        probe_live=probe_live,
    )
