"""
arifosmcp/runtime/resources.py — arifOS Double Helix Resources

Peripheral Nervous System (PNS) organs and Constitutional Ring assets.
Exposes operational grounding, health, and invariants as dynamic resources.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from fastmcp import FastMCP
from fastmcp.tools import ToolResult

from .public_registry import (
    RUNTIME_ENVELOPE_SCHEMA,
    public_resource_uris,
    public_tool_input_schemas,
    public_tool_specs,
    release_version,
)

logger = logging.getLogger(__name__)

def apex_tools_html_rows() -> str:
    """Compatibility helper for legacy REST status pages."""
    rows: list[str] = []
    for spec in public_tool_specs():
        rows.append(
            f"<tr><td><span class='name'>{spec.name}</span></td>"
            f"<td class='role'>{spec.layer}</td>"
            f"<td class='role'>{spec.description}</td></tr>"
        )
    return "\n".join(rows)


def apex_tools_markdown_table() -> str:
    """Compatibility helper for markdown status summaries."""
    header = "| Tool Name | Layer | Role |\n|-----------|-------|------|"
    rows = [f"| {spec.name} | {spec.layer} | {spec.description} |" for spec in public_tool_specs()]
    return "\n".join([header, *rows])


def register_resources(mcp: FastMCP) -> None:
    """Wire the functional arifOS resources onto *mcp*."""

    @mcp.resource("arifos://bootstrap")
    def arifos_bootstrap() -> dict[str, Any]:
        """Startup path, canonical sequence, and system entry guide."""
        return {
            "motto": "DITEMPA BUKAN DIBERI",
            "version": release_version(),
            "sequence": [
                "1. get_tool_registry() — Discovery",
                "2. init_session_anchor() — Identity established",
                "3. route_execution() — Metabolic processing",
            ]
        }

    @mcp.resource("arifos://governance/floors")
    def arifos_governance_floors() -> dict[str, Any]:
        """Constitutional F1-F13 thresholds, doctrine, and formal criteria."""
        from core.shared.floors import get_all_floor_specs
        try:
            return {"floors": get_all_floor_specs()}
        except Exception:
            return {"error": "Could not load floors from core."}

    @mcp.resource("arifos://status/vitals")
    def arifos_status_vitals() -> dict[str, Any]:
        """Current server health, deployment info, and version status."""
        from .rest_routes import _build_governance_status_payload
        return _build_governance_status_payload()

    @mcp.resource("arifos://sessions/{session_id}/vitals")
    def arifos_session_vitals(session_id: str) -> dict[str, Any]:
        """Session-specific telemetry snapshot and thermodynamic state."""
        from core.physics.thermodynamics_hardened import get_thermodynamic_report
        try:
            return {"session_id": session_id, "vitals": get_thermodynamic_report(session_id)}
        except Exception:
            return {"session_id": session_id, "status": "UNKNOWN"}

    @mcp.resource("arifos://agents/skills")
    def arifos_agents_skills() -> str:
        """Consolidated agent skills and atomic competence registry."""
        root_agents_md = os.path.join(os.path.dirname(__file__), "..", "..", "AGENTS.md")
        if os.path.exists(root_agents_md):
            with open(root_agents_md, encoding="utf-8") as f:
                return f.read()
        return "AGENTS.md not found in root."

    @mcp.resource("arifos://tools/{tool_name}")
    def arifos_tool_contract(tool_name: str) -> dict[str, Any]:
        """Detailed contract, examples, and auth requirements for a specific tool."""
        from .public_registry import public_tool_spec_by_name
        registry = public_tool_spec_by_name()
        spec = registry.get(tool_name)
        if spec:
            return {
                "name": spec.name,
                "description": spec.description,
                "inputSchema": spec.input_schema,
                "stage": spec.stage,
                "trinity": spec.trinity,
                "floors": list(spec.floors)
            }
        return {"error": "Tool not found", "name": tool_name}

    @mcp.resource("arifos://vault/recent")
    def arifos_vault_recent() -> dict[str, Any]:
        """Read-only summary of the most recent constitutional verdict ledger."""
        try:
            vault_path = os.environ.get("VAULT999_PATH", "/root/VAULT999")
            audit_dir = os.path.join(vault_path, "audit")
            if os.path.isdir(audit_dir):
                files = sorted(
                    (f for f in os.listdir(audit_dir) if f.endswith(".json")),
                    reverse=True,
                )[:5]
                records = []
                for fname in files:
                    with open(os.path.join(audit_dir, fname), encoding="utf-8") as fh:
                        records.append(json.load(fh))
                return {"recent_verdicts": records}
        except Exception:
            pass
        return {"recent_verdicts": [], "note": "Vault audit unavailable"}

    @mcp.resource("ui://arifos/vault-seal-widget.html")
    def arifos_vault_seal_widget() -> str:
        """HTML resource for ChatGPT Apps widget rendering."""
        from .chatgpt_integration.apps_sdk_tools import vault_seal_widget_html
        return vault_seal_widget_html()

    logger.info("Registered functional arifOS resources.")


def manifest_resources() -> list[str]:
    """Return list of all registered resource URIs."""
    return [
        "arifos://bootstrap",
        "arifos://governance/floors",
        "arifos://status/vitals",
        "arifos://agents/skills",
        "arifos://vault/recent",
        "ui://arifos/vault-seal-widget.html"
    ]
