"""
arifosmcp/runtime/geox_bridge.py — GEOX SSE MCP Client Bridge

DITEMPA BUKAN DIBERI — Forged, Not Given

Bridges arifOS kernel (port 8088) to GEOX organ (port 18081) via SSE + JSON-RPC POST.
The GEOX FastMCP server uses StreamableHTTP with SSE responses.

Pattern:
1. POST JSON-RPC to /mcp with Accept: text/event-stream
2. Server responds with SSE stream (event: message, data: <json>)
3. Parse SSE events to extract JSON-RPC responses
"""

from __future__ import annotations

import json
import logging
import math
import os
import statistics
from collections.abc import Sequence
from typing import Any

import httpx

logger = logging.getLogger("arifosmcp.geox_bridge")

# Bare-metal: use localhost. Docker: override via GEOX_BRIDGE_HOST env var.
GEOX_HOST = os.getenv("GEOX_BRIDGE_HOST", "localhost")
# Bare-metal: 18081 (arifosd). Docker: 8081 (geox_eic container).
GEOX_PORT = int(os.getenv("GEOX_BRIDGE_PORT", "18081"))
GEOX_BASE = f"http://{GEOX_HOST}:{GEOX_PORT}"


async def _post_json_rpc(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Send a JSON-RPC request to GEOX and collect SSE response events.

    Returns the parsed JSON-RPC result dict.
    Raises on error responses.
    """
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.post(
            f"{GEOX_BASE}{endpoint}",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )

        if resp.status_code == 406:
            raise ConnectionError(
                "GEOX 406: Client must accept both application/json and text/event-stream. "
                "Check FastMCP transport configuration."
            )

        if resp.status_code >= 400:
            # Try to parse error from JSON body
            try:
                err_data = resp.json()
                msg = err_data.get("error", {}).get("message", resp.text[:200])
            except Exception:
                msg = resp.text[:200]
            raise ConnectionError(f"GEOX HTTP {resp.status_code}: {msg}")

        content_type = resp.headers.get("content-type", "")
        if "text/event-stream" in content_type:
            buffer = b""
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    buffer += line[6:].encode()
        else:
            buffer = b""
            async for chunk in resp.aiter_bytes():
                buffer += chunk

        if not buffer:
            raise ConnectionError("GEOX returned empty response")

        parsed = json.loads(buffer)
        if parsed.get("error"):
            raise ConnectionError(f"GEOX JSON-RPC error: {parsed['error']}")

        return parsed.get("result", {})


async def call_geox_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Call a GEOX MCP tool by name with arguments.

    Example:
        result = await call_geox_tool("geox_well_compute_petrophysics", {
            "well_id": "WELL_001",
            "computation": "rhob",
            "params": {}
        })
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {},
        },
    }
    result = await _post_json_rpc("/mcp/", payload)
    # GEOX legacy handler wraps tool output in structuredContent.
    # Extract it so callers receive the actual tool data, not the wrapper.
    if isinstance(result, dict) and "structuredContent" in result:
        return result["structuredContent"]
    return result


async def list_geox_tools() -> list[dict[str, Any]]:
    """List all tools available from GEOX MCP server."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {},
    }
    result = await _post_json_rpc("/mcp/", payload)
    return result.get("tools", [])


async def geox_health_check() -> dict[str, Any]:
    """
    Check GEOX server health via the geox_health_check tool.
    Raw ping is not supported by GEOX (returns 404).
    """
    try:
        await call_geox_tool("geox_health_check", {})
        return {"status": "healthy", "organ": "GEOX", "host": GEOX_HOST}
    except Exception as e:
        return {"status": "unhealthy", "organ": "GEOX", "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# QC & CONFIDENCE PIPELINE (GeoX Post-Processing)
# ═══════════════════════════════════════════════════════════════════════════════


def compute_confidence_bands(values: Sequence[float]) -> dict[str, float | None]:
    """
    Compute p10/p50/p90 confidence bands from a series of geoscience values.
    Returns None for all bands if fewer than 3 data points.
    """
    clean = [v for v in values if isinstance(v, int | float) and math.isfinite(v)]
    n = len(clean)
    if n < 3:
        return {"p10": None, "p50": None, "p90": None, "n": n}

    clean_sorted = sorted(clean)
    p10_idx = max(0, int(n * 0.10) - 1)
    p50_idx = int(n * 0.50)
    p90_idx = min(n - 1, int(n * 0.90) - 1)

    return {
        "p10": round(clean_sorted[p10_idx], 4),
        "p50": round(clean_sorted[p50_idx], 4),
        "p90": round(clean_sorted[p90_idx], 4),
        "mean": round(statistics.mean(clean), 4),
        "stdev": round(statistics.stdev(clean), 4) if n > 1 else 0.0,
        "n": n,
    }


def validate_physics_constraint(
    result: dict[str, Any], constraint_type: str = "density"
) -> dict[str, Any]:
    """
    Validate a GEOX computation result against Physics-9 constraints.

    constraint_type:
        density   → rhob must be in [1.9, 2.95] g/cm³
        velocity  → vp must be in [1500, 6000] m/s
        porosity  → phi must be in [0, 0.4]
    """
    constraints = {
        "density": {"key": "rhob", "min": 1.9, "max": 2.95, "unit": "g/cm3"},
        "velocity": {"key": "vp", "min": 1500, "max": 6000, "unit": "m/s"},
        "porosity": {"key": "phi", "min": 0.0, "max": 0.4, "unit": "v/v"},
    }

    spec = constraints.get(constraint_type)
    if not spec:
        return {"valid": False, "error": f"Unknown constraint_type: {constraint_type}"}

    val = result.get(spec["key"])
    if val is None:
        return {"valid": False, "error": f"Missing key: {spec['key']}"}

    if not isinstance(val, int | float) or not math.isfinite(val):
        return {"valid": False, "error": f"Non-numeric value for {spec['key']}: {val}"}

    if val < spec["min"] or val > spec["max"]:
        return {
            "valid": False,
            "error": (
                f"Physics-9 violation: {spec['key']}={val} {spec['unit']} "
                f"outside [{spec['min']}, {spec['max']}]"
            ),
        }

    return {"valid": True, "key": spec["key"], "value": val, "unit": spec["unit"]}


def qc_verify_claim(
    result: dict[str, Any],
    required_evidence_refs: int = 3,
    min_confidence: str = "MEDIUM",
) -> dict[str, Any]:
    """
    Promote a GEOX claim from INGESTED to QC_VERIFIED or flag for review.

    Checks:
    1. At least required_evidence_refs citations
    2. Confidence level >= min_confidence
    3. No Physics-9 violations
    4. Non-null primary result
    """
    confidence_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CERTAIN": 3}
    issues: list[str] = []

    # 1. Evidence refs
    refs = result.get("evidence_refs", [])
    if len(refs) < required_evidence_refs:
        issues.append(
            f"F03 WITNESS: Only {len(refs)} evidence refs (required {required_evidence_refs})"
        )

    # 2. Confidence
    actual_conf = result.get("confidence", "LOW")
    if confidence_order.get(actual_conf, 0) < confidence_order.get(min_confidence, 1):
        issues.append(f"F07 HUMILITY: Confidence {actual_conf} below threshold {min_confidence}")

    # 3. Physics-9
    physics_check = result.get("physics_check", {})
    if physics_check.get("valid") is False:
        issues.append(f"F09 ANTIHANTU: Physics check failed — {physics_check.get('error')}")

    # 4. Primary result
    primary = result.get("primary_result")
    if primary is None:
        issues.append("F02 TRUTH: No primary result in claim")

    if issues:
        return {
            "claim_state": "QC_HOLD",
            "previous_state": result.get("claim_state", "INGESTED"),
            "issues": issues,
            "verdict": "VOID",
        }

    return {
        "claim_state": "QC_VERIFIED",
        "previous_state": result.get("claim_state", "INGESTED"),
        "issues": [],
        "verdict": "SEAL",
    }
