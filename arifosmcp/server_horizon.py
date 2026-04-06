"""
Canonical Horizon gateway for the public arifOS entrypoint.

This file is the policy layer behind ``server.py:mcp`` when running in Horizon
mode. It proxies selected tool calls to the sovereign VPS and publishes the
full gateway contract:
- ``public`` tools: directly callable through Horizon
- ``authenticated`` tools: part of the unified contract, but require auth
- ``sovereign-only`` tools: remain on the VPS execution plane
"""

import hashlib
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import sys as _sys
from pathlib import Path as _Path
# Ensure repo root is on path when run from FastMCP Cloud (files live under /app/arifosmcp/)
_repo_root = str(_Path(__file__).parent.parent)
if _repo_root not in _sys.path:
    _sys.path.insert(0, _repo_root)

import httpx
from fastmcp import FastMCP

# Starlette types — always available (fastmcp depends on starlette)
from starlette.requests import Request
from starlette.responses import JSONResponse

# VPS-only compat shim — falls back gracefully on FastMCP Cloud
try:
    from arifosmcp.runtime.fastmcp_version import custom_route as _custom_route_helper
    _HAS_COMPAT = True
except ImportError:
    _HAS_COMPAT = False

# Tool access policy — VPS has full config; Cloud defaults all tools to public
try:
    from config.environments import TOOL_ACCESS_POLICY, ToolAccessClass
except ImportError:
    class ToolAccessClass:  # type: ignore[no-redef]
        PUBLIC = "public"
        AUTHENTICATED = "authenticated"
        SOVEREIGN = "sovereign"
    TOOL_ACCESS_POLICY: dict = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("horizon-ambassador")

# --- Phase 1: Canonical Registry Loading ---
REGISTRY_PATH = Path(__file__).parent / "tool_registry.json"
with open(REGISTRY_PATH, "r") as f:
    TOOL_REGISTRY = json.load(f)

# --- Phase 3: Constitutional Integrity Check ---
def compute_registry_hash(data):
    return hashlib.sha256(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()

CONSTITUTIONAL_HASH = compute_registry_hash(TOOL_REGISTRY)
logger.info("✅ ARIFOS: CONSTITUTIONAL HASH (v1) LOADED: %s", CONSTITUTIONAL_HASH)


# Configuration
VPS_URL = os.getenv("ARIFOS_VPS_URL", "https://arifosmcp.arif-fazil.com")
ARIFOS_GOVERNANCE_SECRET = os.getenv("ARIFOS_GOVERNANCE_SECRET", "")
ARIFOS_VERSION = os.getenv("ARIFOS_VERSION", "2026.04.06")
MCP_PROTOCOL_VERSION = "2025-11-05"

mcp = FastMCP("arifOS Horizon Gateway (v3 Registry-Driven)")

PUBLIC_PROXY_SPECS = {
    # 11 canonical mega-tools — matches TOOL_ACCESS_POLICY + public_tool_names()
    "init_anchor":        "000_INIT: Constitutional session anchor — identity, state, revoke, refresh.",
    "arifOS_kernel":      "444_ROUTER: Primary metabolic conductor — routes through the 000-999 pipe.",
    "apex_soul":          "888_JUDGE: Final constitutional verdict — judge, validate, hold, armor, probe.",
    "vault_ledger":       "999_VAULT: Immutable decision recording — seal and verify. (Requires auth)",
    "agi_mind":           "333_MIND: Core reasoning and synthesis — reason, reflect, forge.",
    "asi_heart":          "666_HEART: Safety and empathy modeling — critique, simulate.",
    "engineering_memory": "555_MEMORY: Vector memory and governed engineering. (Requires auth)",
    "physics_reality":    "111_SENSE: Reality grounding — search, ingest, compass, atlas, time.",
    "math_estimator":     "777_OPS: Thermodynamic vitals — cost, health, vitals, entropy.",
    "code_engine":        "M-3_EXEC: System-level execution. (Sovereign VPS only)",
    "architect_registry": "M-4_ARCH: Tool and model registry — list, read, model_catalog.",
}

AUTHENTICATED_TOOLS = sorted(
    name for name, access in TOOL_ACCESS_POLICY.items() if access == ToolAccessClass.AUTHENTICATED.value
)
SOVEREIGN_ONLY_TOOLS = sorted(
    name for name, access in TOOL_ACCESS_POLICY.items() if access == ToolAccessClass.SOVEREIGN_ONLY.value
)


def _policy_counts() -> dict[str, int]:
    return {
        "public": len(PUBLIC_PROXY_SPECS),
        "authenticated": len(AUTHENTICATED_TOOLS),
        "sovereign_only": len(SOVEREIGN_ONLY_TOOLS),
    }


async def _upstream_status() -> str:
    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            response = await client.get(f"{VPS_URL}/health", headers={"Accept": "application/json"})
        if response.status_code == 200:
            return "reachable"
        return "partial"
    except Exception:
        return "unreachable"


async def _build_gateway_metadata() -> dict:
    upstream_vps = await _upstream_status()
    status = "ok" if upstream_vps == "reachable" else "degraded"
    return {
        "status": status,
        "mode": "horizon_gateway",
        "entrypoint": "server.py:mcp",
        "version": ARIFOS_VERSION,
        "protocol_version": MCP_PROTOCOL_VERSION,
        "tool_policy": _policy_counts(),
        "auth_status": "public_only",
        "upstream_vps": upstream_vps,
        "deprecated_paths": ["horizon/server.py"],
        "canonical_story": {
            "public_ingress": "Horizon gateway",
            "sovereign_execution": VPS_URL,
        },
    }


def _typed_horizon_error(
    code: str,
    message: str,
    detail: str,
    hint: str,
    action: str,
    tool_name: str,
    http_status: int | None = None,
    exc: Exception | None = None,
    duration_ms: int | None = None,
) -> dict:
    """Build a typed constitutional error envelope — never a bare string."""
    now = datetime.now(timezone.utc).isoformat()
    status_map = {401: "error", 403: "error", 422: "error", 503: "degraded", 500: "error"}
    status = status_map.get(http_status, "error") if http_status else "degraded"
    errors = []
    if http_status:
        errors.append({
            "type": "kernel_error",
            "source": "sovereign_kernel",
            "message": f"Upstream returned HTTP {http_status}.",
        })
    if exc:
        errors.append({
            "type": "transport_error",
            "source": "horizon_gateway",
            "message": str(exc),
        })
    return {
        "ok": False,
        "tool": tool_name,
        "version": ARIFOS_VERSION,
        "stage": "000_INIT",
        "status": status,
        "verdict": "SABAR",
        "code": code,
        "message": message,
        "detail": detail,
        "hint": hint,
        "action": action,
        "retryable": code not in ("INIT_AUTH_401", "INIT_POLICY_403"),
        "rollback_available": True,
        "timestamp": now,
        "duration_ms": duration_ms,
        "trace_id": f"trace_{uuid.uuid4().hex[:16]}",
        "system": {
            "kernel_version": ARIFOS_VERSION,
            "adapter": "horizon_gateway",
            "env": os.getenv("ARIFOS_ENV", "production"),
            "dependency_health": "degraded" if (http_status and http_status >= 500) else "unreachable",
        },
        "errors": errors,
        "warnings": [],
    }


async def _proxy_to_vps(tool_name: str, arguments: dict) -> dict:
    """Helper to forward tool calls to the VPS Kernel."""
    import time as _time
    _start = _time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{VPS_URL}/tools/{tool_name}",
                json=arguments,
                headers={
                    "X-ArifOS-Source": "Horizon",
                    "X-ArifOS-Secret": ARIFOS_GOVERNANCE_SECRET,
                    "Accept": "application/json",
                },
            )
            _ms = int((_time.monotonic() - _start) * 1000)
            if response.status_code == 200:
                data = response.json()
                return data.get("result", data)
            _code_map = {
                401: "INIT_AUTH_401", 403: "INIT_POLICY_403",
                422: "INIT_SCHEMA_422", 503: "INIT_DEPENDENCY_503",
            }
            _code = _code_map.get(response.status_code, "INIT_KERNEL_500")
            return _typed_horizon_error(
                code=_code,
                message=f"Sovereign kernel returned {response.status_code} for {tool_name}.",
                detail=f"HTTP {response.status_code} from upstream at {VPS_URL}/tools/{tool_name}.",
                hint="Check kernel health, dependency wiring, and adapter-to-kernel contract.",
                action="retry_safe | inspect_kernel_health | fallback_query_only",
                tool_name=tool_name,
                http_status=response.status_code,
                duration_ms=_ms,
            )
    except Exception as e:
        _ms = int((_time.monotonic() - _start) * 1000)
        return _typed_horizon_error(
            code="INIT_TRANSPORT_503",
            message=f"Ambassador link severed — cannot reach sovereign kernel for {tool_name}.",
            detail=f"Transport exception: {type(e).__name__}: {e}",
            hint="Verify VPS reachability, ARIFOS_VPS_URL env var, and network connectivity.",
            action="inspect_vps_health | check_env_vars | retry_with_backoff",
            tool_name=tool_name,
            exc=e,
            duration_ms=_ms,
        )


async def _gateway_call(tool_name: str, arguments: dict) -> dict:
    access_class = TOOL_ACCESS_POLICY.get(tool_name, ToolAccessClass.SOVEREIGN_ONLY.value)
    if access_class == ToolAccessClass.PUBLIC.value:
        return await _proxy_to_vps(tool_name, arguments)
    if access_class == ToolAccessClass.AUTHENTICATED.value:
        return {
            "verdict": "HOLD",
            "tool": tool_name,
            "access_class": access_class,
            "message": "Tool exists in the unified contract but requires bound auth continuity.",
            "next_step": "Use the sovereign VPS endpoint until Horizon auth continuity is implemented.",
            "sovereign_endpoint": VPS_URL,
        }
    return {
        "verdict": "HOLD",
        "tool": tool_name,
        "access_class": access_class,
        "message": "Tool is sovereign-only and remains on the VPS execution plane.",
        "sovereign_endpoint": VPS_URL,
    }


@mcp.tool()
async def init_anchor(
    actor_id: str = "anonymous",
    mode: str = "init",
    declared_name: Optional[str] = None,
    intent: Optional[str] = None,
) -> dict:
    """000_INIT: Initialize constitutional session anchor."""
    return await _proxy_to_vps(
        "init_anchor",
        {
            "actor_id": actor_id,
            "mode": mode,
            "declared_name": declared_name,
            "intent": intent,
        },
    )


@mcp.tool()
async def arifOS_kernel(
    query: str,
    session_id: Optional[str] = None,
    mode: str = "kernel",
) -> dict:
    """444_ROUTER: Primary metabolic conductor."""
    return await _proxy_to_vps(
        "arifOS_kernel",
        {
            "query": query,
            "session_id": session_id,
            "mode": mode,
        },
    )


@mcp.tool()
async def apex_soul(
    query: str,
    session_id: Optional[str] = None,
    mode: str = "validate",
) -> dict:
    """888_JUDGE: Final constitutional verdict — judge, validate, hold, armor, probe."""
    return await _proxy_to_vps(
        "apex_soul",
        {"query": query, "session_id": session_id, "mode": mode},
    )


@mcp.tool()
async def agi_mind(
    query: str,
    session_id: Optional[str] = None,
    mode: str = "reason",
) -> dict:
    """333_MIND: Reasoning and synthesis engine."""
    return await _proxy_to_vps(
        "agi_mind",
        {
            "query": query,
            "session_id": session_id,
            "mode": mode,
        },
    )


@mcp.tool()
async def asi_heart(
    query: str,
    session_id: Optional[str] = None,
    mode: str = "critique",
) -> dict:
    """666_HEART: Safety and empathy critique."""
    return await _proxy_to_vps(
        "asi_heart",
        {
            "query": query,
            "session_id": session_id,
            "mode": mode,
        },
    )


@mcp.tool()
async def physics_reality(
    query: str,
    session_id: Optional[str] = None,
    mode: str = "search",
) -> dict:
    """111_SENSE: Reality grounding and temporal intelligence."""
    return await _proxy_to_vps(
        "physics_reality",
        {
            "query": query,
            "session_id": session_id,
            "mode": mode,
        },
    )


@mcp.tool()
async def math_estimator(
    query: str = "status",
    session_id: Optional[str] = None,
    mode: str = "cost",
) -> dict:
    """777_OPS: Thermodynamic vitals and cost estimation."""
    return await _proxy_to_vps(
        "math_estimator",
        {
            "query": query,
            "session_id": session_id,
            "mode": mode,
        },
    )


@mcp.tool()
async def architect_registry(
    query: str = "list",
    session_id: Optional[str] = None,
    mode: str = "list",
) -> dict:
    """000_INIT: Tool and resource discovery."""
    return await _proxy_to_vps(
        "architect_registry",
        {
            "query": query,
            "session_id": session_id,
            "mode": mode,
        },
    )


@mcp.tool()
async def vault_ledger(
    action: str,
    session_id: Optional[str] = None,
    mode: str = "seal",
) -> dict:
    """999_VAULT: Immutable decision recording — seal and verify. Requires authenticated session."""
    return await _gateway_call("vault_ledger", {"action": action, "session_id": session_id, "mode": mode})


@mcp.tool()
async def engineering_memory(
    query: str,
    session_id: Optional[str] = None,
    mode: str = "vector_query",
) -> dict:
    """555_MEMORY: Governed engineering and vector memory. Requires authenticated session."""
    return await _gateway_call("engineering_memory", {"query": query, "session_id": session_id, "mode": mode})


@mcp.tool()
async def code_engine(
    query: str = "status",
    session_id: Optional[str] = None,
    mode: str = "process",
) -> dict:
    """M-3_EXEC: System-level execution. Sovereign VPS only — returns redirect to VPS endpoint."""
    return await _gateway_call("code_engine", {"query": query, "session_id": session_id, "mode": mode})


async def gateway_registry() -> dict:
    """Return the unified Horizon gateway policy for the public entrypoint."""
    return {
        "deployment": "horizon_gateway",
        "public_tools": sorted(PUBLIC_PROXY_SPECS),
        "authenticated_tools": AUTHENTICATED_TOOLS,
        "sovereign_only_tools": SOVEREIGN_ONLY_TOOLS,
        "policy": {
            "public": "Callable through Horizon and proxied to the sovereign VPS.",
            "authenticated": "Part of the unified contract, pending Horizon auth continuity.",
            "sovereign-only": "Must execute directly on the sovereign VPS.",
        },
        "canonical_entrypoint": "server.py:mcp",
        "sovereign_endpoint": VPS_URL,
    }


@mcp.custom_route("/health", methods=["GET"])
async def horizon_health(_request: Request):
    """Operational liveness endpoint for Horizon mode."""
    return JSONResponse(await _build_gateway_metadata())


@mcp.custom_route("/metadata", methods=["GET"])
async def horizon_metadata(_request: Request):
    """Human and machine readable gateway metadata."""
    metadata = await _build_gateway_metadata()
    metadata["gateway_registry_tool"] = "gateway_registry"
    return JSONResponse(metadata)


# --- 13 SACRED RESOURCES (Full Parity) ---


@mcp.resource("arifos://governance/floors")
def arifos_floors() -> str:
    """arifOS Governance: Constitutional F1-F13 thresholds and doctrine."""
    return json.dumps(
        {
            "floors": {
                "F1": "Amanah (Reversibility)",
                "F2": "Truth (≥ 0.99)",
                "F3": "Tri-Witness (≥ 0.95)",
                "F4": "ΔS Clarity (≤ 0)",
                "F7": "Ω₀ Humility (0.03-0.05)",
                "F13": "Sovereign (Human Veto)",
            },
            "motto": "DITEMPA BUKAN DIBERI",
            "entrypoint": "server.py:mcp",
        }
    )


@mcp.resource("arifos://status/vitals")
def arifos_vitals() -> str:
    """arifOS Status: Current health and deployment info."""
    return json.dumps(
        {
            "status": "HEALTHY",
            "deployment": "Horizon Gateway",
            "canonical_entrypoint": "server.py:mcp",
            "vps_link": VPS_URL,
        }
    )


@mcp.resource("arifos://bootstrap/guide")
def arifos_bootstrap() -> str:
    """arifOS Bootstrap: Startup path and canonical sequence."""
    return json.dumps(
        {
            "sequence": [
                "1. architect_registry(mode='list') — discover available tools",
                "2. math_estimator(mode='health') — verify thermodynamic health",
                "3. init_anchor(mode='init') — establish constitutional session",
                "4. arifOS_kernel(mode='kernel') — enter full pipeline",
            ],
            "note": "All tools require session via init_anchor first for full access.",
        }
    )


@mcp.resource("arifos://agents/skills")
def arifos_skills() -> str:
    """arifOS Agent Skills: Consolidated guide for AI agents."""
    return "Refer to AGENTS.md for atomic competence registry. Motto: DITEMPA BUKAN DIBERI."


# --- RESOURCE TEMPLATES (FastMCP 2.x Compatible) ---


@mcp.resource("arifos://sessions/{session_id}/vitals")
async def arifos_session_vitals(session_id: str) -> str:
    """arifOS Session Vitals: Real-time telemetry for a specific session."""
    # Proxy to VPS for real session telemetry
    res = await _proxy_to_vps("arifOS_kernel", {"query": "status", "session_id": session_id})
    return json.dumps(res.get("metrics", {"status": "ACTIVE", "session": session_id}))


@mcp.resource("arifos://tools/{tool_name}/spec")
def arifos_tool_spec(tool_name: str) -> str:
    """arifOS Tool Specification: Detailed contract for a specific tool."""
    return json.dumps(
        {
            "tool": tool_name,
            "governance": "Hardened",
            "parity": "Gateway-Proxied",
            "access_class": TOOL_ACCESS_POLICY.get(tool_name, ToolAccessClass.SOVEREIGN_ONLY.value),
        }
    )


# --- 10 SACRED PROMPTS (Full Parity) ---


@mcp.prompt()
def init_anchor(actor_id: str = "anonymous", intent: str = "") -> str:
    return f"Enter arifOS as {actor_id}. Intent: {intent}. Establishing identity anchor..."


@mcp.prompt()
def arifOS_kernel(query: str = "") -> str:
    return f"Conductor request: {query}. Routing through constitutional pipeline..."


@mcp.prompt()
def agi_mind(query: str, context: str = "") -> str:
    return f"Architect task: {query}. Context: {context}. Focus on F2 (Truth) and F4 (Clarity)."


@mcp.prompt()
def asi_heart(content: str) -> str:
    return f"Empath evaluation: {content}. Simulating impact per F6 (Empathy)..."


@mcp.prompt()
def apex_soul(candidate: str = "") -> str:
    return f"Judge verdict required for: {candidate}. Seeking final SEAL/VOID..."


@mcp.prompt()
def vault_ledger() -> str:
    return "Australian Auditor mode: Commit truths to Merkle chain..."


@mcp.prompt()
def physics_reality(input: str = "") -> str:
    return f"Grounding request: {input}. Connecting to Earth-Witness (W3)..."


@mcp.prompt()
def code_engine(path: str = ".") -> str:
    return f"System hygiene at {path}. Safe process execution enabled."


@mcp.prompt()
def agent_skills(role: str = "A-ARCHITECT") -> str:
    return f"Operating as {role}. Governed by 13 Floors. Motto: DITEMPA BUKAN DIBERI."


@mcp.prompt()
def human_explainer(verdict: str, reasoning: str) -> str:
    return f"Translating {verdict} verdict. Reasoning: {reasoning}. Explain for Sovereign..."


if __name__ == "__main__":
    mcp.run()
