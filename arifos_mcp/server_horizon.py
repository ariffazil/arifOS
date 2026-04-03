"""
Canonical Horizon gateway for the public arifOS entrypoint.

This file is the policy layer behind ``server.py:mcp`` when running in Horizon
mode. It proxies selected tool calls to the sovereign VPS and publishes the
full gateway contract:
- ``public`` tools: directly callable through Horizon
- ``authenticated`` tools: part of the unified contract, but require auth
- ``sovereign-only`` tools: remain on the VPS execution plane
"""

import os
import json
import httpx
import logging
from fastmcp import FastMCP

from config.environments import TOOL_ACCESS_POLICY, ToolAccessClass
from arifos_mcp.runtime.fastmcp_version import JSONResponse, Request, custom_route

# Configuration
VPS_URL = os.getenv("ARIFOS_VPS_URL", "https://arifosmcp.arif-fazil.com")
ARIFOS_GOVERNANCE_SECRET = os.getenv("ARIFOS_GOVERNANCE_SECRET", "")
ARIFOS_VERSION = os.getenv("ARIFOS_VERSION", "2026.03.25")
MCP_PROTOCOL_VERSION = "2025-11-25"

mcp = FastMCP("arifOS Horizon Gateway")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("horizon-ambassador")

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


async def _proxy_to_vps(tool_name: str, arguments: dict) -> dict:
    """Helper to forward tool calls to the VPS Kernel."""
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
            if response.status_code == 200:
                data = response.json()
                return data.get("result", data)
            return {"error": f"Sovereign Kernel error: {response.status_code}", "verdict": "SABAR"}
    except Exception as e:
        return {"error": "Ambassador link severed", "details": str(e), "verdict": "SABAR"}


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


def _register_public_proxy_tools() -> None:
    for tool_name, description in PUBLIC_PROXY_SPECS.items():
        async def _proxy_tool(_tool_name: str = tool_name, **kwargs) -> dict:
            return await _gateway_call(_tool_name, kwargs)

        _proxy_tool.__name__ = f"proxy_{tool_name.replace('-', '_')}"
        _proxy_tool.__doc__ = description
        mcp.tool(name=tool_name)(_proxy_tool)


_register_public_proxy_tools()


@mcp.tool()
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


@custom_route(mcp, "/health", methods=["GET"], include_in_schema=False)
async def horizon_health(_request: Request):
    """Operational liveness endpoint for Horizon mode."""
    return JSONResponse(await _build_gateway_metadata())


@custom_route(mcp, "/metadata", methods=["GET"], include_in_schema=False)
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
