"""
Canonical Horizon gateway for the public arifOS entrypoint.
FastMCP 2.12.3 Compatible Version
"""

import os
import json
import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastmcp import FastMCP
from starlette.responses import JSONResponse

from config.environments import (
    TOOL_ACCESS_POLICY,
    ToolAccessClass,
    get_environment,
)

# Configuration
VPS_URL = os.getenv("ARIFOS_VPS_URL", "https://arifosmcp.arif-fazil.com")
ARIFOS_GOVERNANCE_SECRET = os.getenv("ARIFOS_GOVERNANCE_SECRET", "")
ARIFOS_VERSION = os.getenv("ARIFOS_VERSION", "2026.03.25")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("horizon-gateway")

# Public tool contract must match the policy-approved aliases exposed through
# Horizon, not legacy sovereign registry names.
PUBLIC_PROXY_SPECS = {
    "init_anchor": "000_INIT: Initialize constitutional session anchor.",
    "arifOS_kernel": "444_ROUTER: Primary metabolic conductor.",
    "apex_judge": "888_JUDGE: Constitutional verdict engine.",
    "agi_mind": "333_MIND: Reasoning and synthesis engine.",
    "asi_heart": "666_HEART: Safety and empathy critique.",
    "physics_reality": "111_SENSE: Reality grounding and temporal intelligence.",
    "math_estimator": "777_OPS: Thermodynamic vitals and cost estimation.",
    "architect_registry": "000_INIT: Tool and resource discovery.",
    "compat_probe": "M-5_COMPAT: Interoperability and enum audit.",
    "agi_reason": "333_MIND: First-principles reasoning.",
    "agi_reflect": "333_MIND: Reflective synthesis and critique.",
    "asi_critique": "666_HEART: Harm and alignment critique.",
    "asi_simulate": "666_HEART: Consequence and scenario simulation.",
    "reality_compass": "111_SENSE: Directional grounding.",
    "reality_atlas": "111_SENSE: Contextual reality mapping.",
    "search_reality": "111_SENSE: Evidence-grounded search.",
    "ingest_evidence": "111_SENSE: Evidence ingestion.",
    "check_vital": "777_OPS: Runtime health signal.",
    "audit_rules": "888_JUDGE: Rule and policy audit.",
    "search_tool": "Search for indexed documents.",
    "fetch_tool": "Fetch indexed document content by ID.",
}

# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY POLICY COUNTS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_tool_policy_counts() -> dict[str, int]:
    authenticated = 0
    sovereign_only = 0
    for access in TOOL_ACCESS_POLICY.values():
        if access == ToolAccessClass.AUTHENTICATED.value:
            authenticated += 1
        elif access == ToolAccessClass.SOVEREIGN_ONLY.value:
            sovereign_only += 1
    return {
        "public": len(PUBLIC_PROXY_SPECS),
        "authenticated": authenticated,
        "sovereign_only": sovereign_only,
    }

TOOL_COUNTS = _get_tool_policy_counts()

# ═══════════════════════════════════════════════════════════════════════════════
# UPSTREAM CHECK
# ═══════════════════════════════════════════════════════════════════════════════

async def _check_upstream_vps() -> dict[str, Any]:
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{VPS_URL}/health",
                headers={"X-ArifOS-Source": "Horizon-HealthCheck"},
            )
            if response.status_code == 200:
                return {"status": "reachable", "http_status": response.status_code}
            return {"status": "degraded", "http_status": response.status_code}
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# FASTMCP SERVER
# ═══════════════════════════════════════════════════════════════════════════════

mcp = FastMCP("arifOS Horizon Gateway")

# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC TOOL PROXIES (Explicit signatures for FastMCP 2.x)
# ═══════════════════════════════════════════════════════════════════════════════

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


async def _proxy_to_vps(tool_name: str, arguments: Optional[dict] = None) -> dict:
    """Forward tool calls to sovereign VPS."""
    _start = time.monotonic()
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{VPS_URL}/tools/{tool_name}",
                json=arguments or {},
                headers={
                    "X-ArifOS-Source": "Horizon",
                    "X-ArifOS-Secret": ARIFOS_GOVERNANCE_SECRET,
                    "Accept": "application/json",
                },
            )
            _ms = int((time.monotonic() - _start) * 1000)
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
        _ms = int((time.monotonic() - _start) * 1000)
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

# Define each tool with explicit parameters (no **kwargs)
# FastMCP 2.x requires explicit parameter definitions

@mcp.tool()
async def init_anchor(
    actor_id: str = "anonymous",
    mode: str = "init",
    declared_name: Optional[str] = None,
    intent: Optional[str] = None,
) -> dict:
    """000_VOID: Initialize constitutional session anchor."""
    return await _proxy_to_vps("init_anchor", {
        "actor_id": actor_id,
        "mode": mode,
        "declared_name": declared_name,
        "intent": intent,
    })

@mcp.tool()
async def arifOS_kernel(
    query: str,
    session_id: Optional[str] = None,
    mode: str = "kernel",
) -> dict:
    """444_ROUTER: Primary metabolic conductor."""
    return await _proxy_to_vps("arifOS_kernel", {
        "query": query,
        "session_id": session_id,
        "mode": mode,
    })

@mcp.tool()
async def apex_judge(
    query: str,
    session_id: Optional[str] = None,
    mode: str = "validate",
) -> dict:
    """888_JUDGE: Constitutional verdict engine."""
    return await _proxy_to_vps("apex_judge", {
        "query": query,
        "session_id": session_id,
        "mode": mode,
    })

@mcp.tool()
async def agi_mind(
    query: str,
    session_id: Optional[str] = None,
    mode: str = "reason",
) -> dict:
    """333_MIND: Reasoning and synthesis engine."""
    return await _proxy_to_vps("agi_mind", {
        "query": query,
        "session_id": session_id,
        "mode": mode,
    })

@mcp.tool()
async def asi_heart(
    query: str,
    session_id: Optional[str] = None,
    mode: str = "critique",
) -> dict:
    """666_HEART: Safety and empathy critique."""
    return await _proxy_to_vps("asi_heart", {
        "query": query,
        "session_id": session_id,
        "mode": mode,
    })

@mcp.tool()
async def physics_reality(
    query: str,
    session_id: Optional[str] = None,
    mode: str = "search",
) -> dict:
    """111_SENSE: Reality grounding and temporal intelligence."""
    return await _proxy_to_vps("physics_reality", {
        "query": query,
        "session_id": session_id,
        "mode": mode,
    })

@mcp.tool()
async def math_estimator(
    query: str = "status",
    session_id: Optional[str] = None,
    mode: str = "cost",
) -> dict:
    """777_OPS: Thermodynamic vitals and cost estimation."""
    return await _proxy_to_vps("math_estimator", {
        "query": query,
        "session_id": session_id,
        "mode": mode,
    })

@mcp.tool()
async def architect_registry(
    query: str = "list",
    session_id: Optional[str] = None,
    mode: str = "list",
) -> dict:
    """000_INIT: Tool and resource discovery."""
    return await _proxy_to_vps("architect_registry", {
        "query": query,
        "session_id": session_id,
        "mode": mode,
    })

@mcp.tool()
async def compat_probe(
    query: str = "audit",
    session_id: Optional[str] = None,
    mode: str = "audit",
) -> dict:
    """M-5_COMPAT: Interoperability and enum audit."""
    return await _proxy_to_vps("compat_probe", {
        "query": query,
        "session_id": session_id,
        "mode": mode,
    })

@mcp.tool()
async def agi_reason(
    query: str,
    session_id: Optional[str] = None,
) -> dict:
    """333_MIND: First-principles reasoning."""
    return await _proxy_to_vps("agi_reason", {
        "query": query,
        "session_id": session_id,
    })

@mcp.tool()
async def agi_reflect(
    query: str,
    session_id: Optional[str] = None,
) -> dict:
    """333_MIND: Reflective synthesis and critique."""
    return await _proxy_to_vps("agi_reflect", {
        "query": query,
        "session_id": session_id,
    })

@mcp.tool()
async def asi_critique(
    query: str,
    session_id: Optional[str] = None,
) -> dict:
    """666_HEART: Harm and alignment critique."""
    return await _proxy_to_vps("asi_critique", {
        "query": query,
        "session_id": session_id,
    })

@mcp.tool()
async def asi_simulate(
    query: str,
    session_id: Optional[str] = None,
) -> dict:
    """666_HEART: Consequence and scenario simulation."""
    return await _proxy_to_vps("asi_simulate", {
        "query": query,
        "session_id": session_id,
    })

@mcp.tool()
async def reality_compass(
    query: str,
    session_id: Optional[str] = None,
) -> dict:
    """111_SENSE: Directional grounding."""
    return await _proxy_to_vps("reality_compass", {
        "query": query,
        "session_id": session_id,
    })

@mcp.tool()
async def reality_atlas(
    query: str,
    session_id: Optional[str] = None,
) -> dict:
    """111_SENSE: Contextual reality mapping."""
    return await _proxy_to_vps("reality_atlas", {
        "query": query,
        "session_id": session_id,
    })

@mcp.tool()
async def search_reality(
    query: str,
    session_id: Optional[str] = None,
) -> dict:
    """111_SENSE: Evidence-grounded search."""
    return await _proxy_to_vps("search_reality", {
        "query": query,
        "session_id": session_id,
    })

@mcp.tool()
async def ingest_evidence(
    query: str,
    session_id: Optional[str] = None,
) -> dict:
    """111_SENSE: Evidence ingestion."""
    return await _proxy_to_vps("ingest_evidence", {
        "query": query,
        "session_id": session_id,
    })

@mcp.tool()
async def check_vital(
    query: str = "health",
    session_id: Optional[str] = None,
) -> dict:
    """777_OPS: Runtime health signal."""
    return await _proxy_to_vps("check_vital", {
        "query": query,
        "session_id": session_id,
    })

@mcp.tool()
async def audit_rules(
    query: str = "validate",
    session_id: Optional[str] = None,
) -> dict:
    """888_JUDGE: Rule and policy audit."""
    return await _proxy_to_vps("audit_rules", {
        "query": query,
        "session_id": session_id,
    })

@mcp.tool()
async def search_tool(
    query: str,
    session_id: Optional[str] = None,
) -> dict:
    """Search for indexed documents."""
    return await _proxy_to_vps("search_tool", {
        "query": query,
        "session_id": session_id,
    })

@mcp.tool()
async def fetch_tool(
    id: str,
    session_id: Optional[str] = None,
) -> dict:
    """Fetch indexed document content by ID."""
    return await _proxy_to_vps("fetch_tool", {
        "id": id,
        "session_id": session_id,
    })


logger.info(f"[HORIZON] Gateway initialized: {TOOL_COUNTS['public']} public tools")

__all__ = ["mcp"]
