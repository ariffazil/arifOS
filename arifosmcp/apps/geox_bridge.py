"""
arifosmcp/apps/geox_bridge.py
GEOX Domain Coprocessor Bridge — delegates geoscience tasks under arifOS governance.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("arifosmcp.apps.geox_bridge")


class GEOXBridge:
    """
    Bridge to GEOX domain coprocessor with arifOS constitutional pre/post checks.

    Uses httpx directly — no SSE session management required.
    GEOX responds with JSON when Accept: application/json (stateless) or
    SSE when Accept: text/event-stream (sessionful). We use JSON stateless
    for synchronous calls.
    """

    def __init__(
        self,
        geox_endpoint: str = "https://geox.arif-fazil.com",
        geox_internal: str = "http://geox_eic:8081",
    ) -> None:
        # Prefer internal Docker host; fall back to public endpoint
        self._internal = geox_internal
        self._public = geox_endpoint
        self._base: str | None = None
        self._client: Any | None = None

    def _get_base(self) -> str:
        """Resolve base URL — internal Docker network preferred."""
        if self._base:
            return self._base
        # Check connectivity to internal Docker host
        import httpx

        try:
            # Internal only works from within the arifOS container network
            r = httpx.get(
                f"{self._internal}/health",
                timeout=3.0,
                headers={"Accept": "application/json"},
            )
            if r.status_code == 200:
                self._base = self._internal
            else:
                self._base = self._public
        except Exception:
            self._base = self._public
        return self._base

    async def _call_mcp(
        self,
        method: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Make a JSON-RPC call to GEOX MCP server. Returns parsed result dict."""
        import json

        import httpx

        base = self._get_base()
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.post(
                f"{base}/mcp",
                json=payload,
                headers=headers,
            )
            if resp.status_code >= 400:
                try:
                    err = resp.json()
                    msg = err.get("error", {}).get("message", resp.text[:200])
                except Exception:
                    msg = resp.text[:200]
                raise ConnectionError(f"GEOX HTTP {resp.status_code}: {msg}")

            # GEOX may return SSE (text/event-stream) or JSON depending on config
            content_type = resp.headers.get("content-type", "")
            text = resp.text

            if "text/event-stream" in content_type:
                # Parse SSE: "data: {...}" lines
                buffer = ""
                for line in text.splitlines():
                    if line.startswith("data: "):
                        buffer += line[6:]
                    elif line.startswith("{"):
                        buffer += line
                if not buffer:
                    raise ConnectionError("GEOX returned empty SSE stream")
                parsed = json.loads(buffer)
            else:
                parsed = json.loads(text)

            if parsed.get("error"):
                raise ConnectionError(f"GEOX JSON-RPC error: {parsed['error']}")
            return parsed.get("result", {})

    async def _judge_pre_check(self, operation: str, data_classification: str) -> dict[str, Any]:
        """Run arifOS Judge pre-check before delegating to GEOX."""
        try:
            from arifosmcp.runtime.tools_hardened_dispatch import get_tool_handler

            handler = get_tool_handler("arifos_judge")
            result = handler(
                query=f"Delegate {operation} to GEOX with classification {data_classification}",
                risk_tier="medium",
            )
            if hasattr(result, "model_dump"):
                return result.model_dump(mode="json")
            return (
                dict(result)
                if isinstance(result, dict)
                else {"verdict": "HOLD", "error": "judge_handler_failed"}
            )
        except Exception as exc:
            return {"verdict": "HOLD", "error": str(exc)}

    async def _audit_post_check(self, result: dict[str, Any]) -> None:
        """Run arifOS Judge audit after GEOX returns."""
        try:
            from arifosmcp.runtime.tools_hardened_dispatch import get_tool_handler

            handler = get_tool_handler("arifos_judge")
            handler(
                query=f"Audit GEOX result: {result.get('status', 'unknown')}",
                risk_tier="low",
            )
        except Exception:
            pass

    async def compute_petrophysics(
        self, well_id: str, computation: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Delegate petrophysics computation to GEOX with governance gating.

        Args:
            well_id:    Well identifier (e.g. "WELL_001")
            computation: Computation type (e.g. "rhob", "phi", "sw")
            params:     Computation parameters
        """
        verdict = await self._judge_pre_check(
            operation="compute_petrophysics",
            data_classification="well_log",
        )
        if verdict.get("verdict") != "SEAL":
            return {"error": "Governance rejection", "verdict": verdict}

        try:
            result = await self._call_mcp(
                "tools/call",
                {
                    "name": "geox_subsurface_generate_candidates",
                    "arguments": {
                        "target_class": "petrophysics",
                        "well_id": well_id,
                        **params,
                    },
                },
            )
            await self._audit_post_check(result)
            return result
        except Exception as e:
            logger.error(f"compute_petrophysics GEOX call failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "operation": "compute_petrophysics",
                "well_id": well_id,
            }

    async def render_well_section(
        self, well_id: str, section_params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Delegate well section rendering to GEOX with governance gating.

        Note: GEOX does not have a "render_well_section" tool.
        The closest canonical tool is geox_section_interpret_correlation
        for correlation rendering, or geox_data_ingest_bundle for log loading.
        """
        verdict = await self._judge_pre_check(
            operation="render_well_section",
            data_classification="well_log",
        )
        if verdict.get("verdict") != "SEAL":
            return {"error": "Governance rejection", "verdict": verdict}

        try:
            result = await self._call_mcp(
                "tools/call",
                {
                    "name": "geox_section_interpret_correlation",
                    "arguments": {
                        "well_refs": [well_id],
                        "section_ref": section_params.get("section_id", well_id),
                        "mode": section_params.get("mode", "correlation"),
                    },
                },
            )
            await self._audit_post_check(result)
            return result
        except Exception as e:
            logger.error(f"render_well_section GEOX call failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "operation": "render_well_section",
                "well_id": well_id,
            }

    async def ingest_well_log(self, source_uri: str, well_id: str | None = None) -> dict[str, Any]:
        """Ingest a LAS/CSV well log file into GEOX."""
        verdict = await self._judge_pre_check(
            operation="ingest_well_log",
            data_classification="well_log",
        )
        if verdict.get("verdict") != "SEAL":
            return {"error": "Governance rejection", "verdict": verdict}

        try:
            result = await self._call_mcp(
                "tools/call",
                {
                    "name": "geox_data_ingest_bundle",
                    "arguments": {
                        "source_uri": source_uri,
                        "source_type": "well",
                        "well_id": well_id,
                    },
                },
            )
            await self._audit_post_check(result)
            return result
        except Exception as e:
            logger.error(f"ingest_well_log GEOX call failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "operation": "ingest_well_log",
                "source_uri": source_uri,
            }

    async def list_tools(self) -> list[dict[str, Any]]:
        """List all GEOX MCP tools."""
        try:
            result = await self._call_mcp("tools/list", {})
            return result.get("tools", [])
        except Exception as e:
            logger.error(f"list_tools GEOX call failed: {e}")
            return []

    async def health_check(self) -> dict[str, Any]:
        """Check GEOX MCP server health."""
        try:
            await self._call_mcp(
                "tools/call",
                {"name": "geox_system_registry_status", "arguments": {}},
            )
            return {"status": "healthy", "organ": "GEOX"}
        except Exception as e:
            return {"status": "unhealthy", "organ": "GEOX", "error": str(e)}


__all__ = ["GEOXBridge"]
