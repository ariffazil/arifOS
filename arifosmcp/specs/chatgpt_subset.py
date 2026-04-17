"""
arifOS MCP ChatGPT Subset Adapter
═══════════════════════════════════════════════════════════════════════════════

Apps SDK-safe subset of arifOS capabilities.

Phase 1 (Current): Read-only health checks
Phase 2 (Future): Write-path with explicit F11/F13 review

Principles:
- Only read-only tools in Phase 1
- No vault sealing without human approval
- No VPS execution paths
- Clean mapping from canonical contracts to Apps SDK shapes
"""

from __future__ import annotations

from typing import Any

from arifosmcp.specs.contracts import (
    ConstitutionalHealthView,
    VerdictCode,
)
from arifosmcp.specs.resource_specs import get_resource_spec
from arifosmcp.specs.tool_specs import get_tool_spec

# ═══════════════════════════════════════════════════════════════════════════════
# CHATGPT-SAFE SUBSETS
# ═══════════════════════════════════════════════════════════════════════════════

# Tools exposed to ChatGPT (read-only in Phase 1)
CHATGPT_TOOL_NAMES: tuple[str, ...] = (
    "get_constitutional_health",  # Data tool: health card
    "render_vault_seal",          # Render tool: widget UI
    "list_recent_verdicts",       # Read-only vault summary
)

# Resources exposed to ChatGPT
CHATGPT_RESOURCE_URIS: tuple[str, ...] = (
    "arifos://doctrine",
    "arifos://vitals",
    "arifos://schema",
    "arifos://forge",
)

# Prompts exposed to ChatGPT
CHATGPT_PROMPT_NAMES: tuple[str, ...] = (
    "prompt_init_anchor",
    "prompt_sense_reality",
    "prompt_reason_synthesis",
    "prompt_human_explainer",
)


# ═══════════════════════════════════════════════════════════════════════════════
# SAFETY CHECKS
# ═══════════════════════════════════════════════════════════════════════════════

def is_chatgpt_safe_tool(tool_name: str) -> bool:
    """Check if a tool is safe for ChatGPT Apps SDK exposure."""
    return tool_name in CHATGPT_TOOL_NAMES


def is_chatgpt_safe_resource(uri: str) -> bool:
    """Check if a resource is safe for ChatGPT Apps SDK exposure."""
    return uri in CHATGPT_RESOURCE_URIS


def is_chatgpt_safe_prompt(prompt_name: str) -> bool:
    """Check if a prompt is safe for ChatGPT Apps SDK exposure."""
    return prompt_name in CHATGPT_PROMPT_NAMES


def validate_chatgpt_safety() -> dict[str, Any]:
    """
    Validate that ChatGPT subset is actually safe.
    
    Returns audit report with any violations found.
    """
    violations = []
    
    # Check that no non-readonly tools slipped in
    for tool_name in CHATGPT_TOOL_NAMES:
        spec = get_tool_spec(tool_name)
        if spec and not spec.read_only_hint:
            violations.append({
                "type": "tool_not_readonly",
                "name": tool_name,
                "severity": "high",
                "message": f"Tool {tool_name} is not marked read_only but is in ChatGPT subset"
            })
    
    # Check that no high-auth resources slipped in
    for uri in CHATGPT_RESOURCE_URIS:
        spec = get_resource_spec(uri)
        if spec and spec.auth_required not in ("anonymous", "anchored"):
            violations.append({
                "type": "resource_high_auth",
                "uri": uri,
                "severity": "medium",
                "message": f"Resource {uri} requires {spec.auth_required} but is in ChatGPT subset"
            })
    
    return {
        "ok": len(violations) == 0,
        "violations": violations,
        "tool_count": len(CHATGPT_TOOL_NAMES),
        "resource_count": len(CHATGPT_RESOURCE_URIS),
        "prompt_count": len(CHATGPT_PROMPT_NAMES),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CHATGPT-SPECIFIC TOOL SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

def get_constitutional_health_schema() -> dict[str, Any]:
    """
    Schema for get_constitutional_health tool.
    
    Returns structured health card with human-readable labels.
    """
    return {
        "name": "get_constitutional_health",
        "title": "Constitutional Health Check",
        "description": (
            "Get current constitutional health snapshot. "
            "Returns floor scores, verdict, and attestation status. "
            "Read-only — safe for all sessions."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "verdict": {
                    "type": "string",
                    "enum": ["SEAL", "PARTIAL", "VOID", "SABAR"],
                    "default": "SEAL",
                    "description": "Requested verdict mode"
                },
                "include_history": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include recent verdict history"
                }
            }
        },
        "annotations": {
            "readOnlyHint": True,
            "openWorldHint": False,
        }
    }


def render_vault_seal_schema() -> dict[str, Any]:
    """
    Schema for render_vault_seal tool.
    
    Render tool that returns widget URL for ChatGPT UI.
    Widget hosted on https://mcp.af-forge.io with CSP headers.
    """
    WIDGET_URL = "https://mcp.af-forge.io/widget/vault-seal"
    
    return {
        "name": "render_vault_seal",
        "title": "Render Vault Seal",
        "description": (
            "Display constitutional health as interactive widget. "
            "Served from https://mcp.af-forge.io with strict CSP."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "seal_data": {
                    "type": "object",
                    "description": "Constitutional health data to render"
                }
            }
        },
        "annotations": {
            "readOnlyHint": True,
        },
        "_meta": {
            "ui": {
                "resourceUri": WIDGET_URL,
                "visibility": "user"
            },
            "openai": {
                "outputTemplate": WIDGET_URL
            }
        }
    }


def list_recent_verdicts_schema() -> dict[str, Any]:
    """
    Schema for list_recent_verdicts tool.
    
    Read-only summary of recent vault entries.
    """
    return {
        "name": "list_recent_verdicts",
        "title": "Recent Verdicts",
        "description": (
            "List recent constitutional verdicts (last 100). "
            "Read-only audit log with anonymized metrics. "
            "No sensitive data exposed."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100
                },
                "verdict_filter": {
                    "type": "string",
                    "enum": ["all", "SEAL", "PARTIAL", "VOID", "SABAR", "HOLD"],
                    "default": "all"
                }
            }
        },
        "annotations": {
            "readOnlyHint": True,
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CHATGPT MANIFEST
# ═══════════════════════════════════════════════════════════════════════════════

def get_chatgpt_manifest() -> dict[str, Any]:
    """
    Build complete ChatGPT Apps SDK manifest.
    
    This is the contract between arifOS and OpenAI's platform.
    """
    return {
        "schema_version": "2026.04.06",
        "name": "arifOS Constitutional Health",
        "description": (
            "Constitutional AI governance health checks via arifOS. "
            "Inspect floor scores, verdicts, and attestation status. "
            "Phase 1: Read-only. Phase 2: Write with F11/F13 review."
        ),
        "vendor": {
            "name": "Muhammad Arif bin Fazil",
            "url": "https://arif-fazil.com"
        },
        "capabilities": {
            "tools": list(CHATGPT_TOOL_NAMES),
            "resources": list(CHATGPT_RESOURCE_URIS),
            "prompts": list(CHATGPT_PROMPT_NAMES),
        },
        "tools": [
            get_constitutional_health_schema(),
            render_vault_seal_schema(),
            list_recent_verdicts_schema(),
        ],
        "resources": [
            {
                "uri": uri,
                "name": get_resource_spec(uri).name if get_resource_spec(uri) else uri,
            }
            for uri in CHATGPT_RESOURCE_URIS
        ],
        "safety": {
            "phase": 1,
            "read_only": True,
            "888_hold_active": True,
            "max_risk_tier": "medium",
            "requires_human_approval_for_write": True,
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAPPING TO CANONICAL CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

def map_chatgpt_health_to_canonical(
    chatgpt_health: dict[str, Any]
) -> ConstitutionalHealthView:
    """
    Map ChatGPT health response to canonical ConstitutionalHealthView.
    
    This ensures ChatGPT and internal APIs speak the same contract.
    """
    return ConstitutionalHealthView(
        session_id=chatgpt_health.get("session_id", "anonymous"),
        timestamp=chatgpt_health.get("timestamp", ""),
        truth_score=chatgpt_health.get("truth_score", 0.95),
        humility_level=chatgpt_health.get("humility_level", 0.05),
        entropy_delta=chatgpt_health.get("entropy_delta", 0.0),
        harmony_ratio=chatgpt_health.get("harmony_ratio", 1.0),
        reality_index=chatgpt_health.get("reality_index", 0.9),
        witness_strength=chatgpt_health.get("witness_strength", 0.0),
        verdict=VerdictCode(chatgpt_health.get("verdict", "SABAR")),
        verdict_label=_verdict_to_label(chatgpt_health.get("verdict", "SABAR")),
        attestation=chatgpt_health.get("attestation"),
    )


def _verdict_to_label(verdict: str) -> str:
    """Convert verdict code to human label."""
    labels = {
        "SEAL": "Aligned",
        "PARTIAL": "Partial",
        "VOID": "Rejected",
        "SABAR": "Pending",
        "HOLD": "Escalated",
    }
    return labels.get(verdict, "Unknown")


__all__ = [
    # Subsets
    "CHATGPT_TOOL_NAMES",
    "CHATGPT_RESOURCE_URIS",
    "CHATGPT_PROMPT_NAMES",
    # Safety checks
    "is_chatgpt_safe_tool",
    "is_chatgpt_safe_resource",
    "is_chatgpt_safe_prompt",
    "validate_chatgpt_safety",
    # Schemas
    "get_constitutional_health_schema",
    "render_vault_seal_schema",
    "list_recent_verdicts_schema",
    # Manifest
    "get_chatgpt_manifest",
    # Mapping
    "map_chatgpt_health_to_canonical",
]
