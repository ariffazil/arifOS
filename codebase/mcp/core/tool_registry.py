"""
arifOS MCP Tool Registry
Single Source of Truth for all 7 Constitutional Tools.
"""

from typing import Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass
import logging

# Import handlers from the canonical implementation
from ..tools.canonical_trinity import (
    mcp_init,
    mcp_agi,
    mcp_asi,
    mcp_apex,
    mcp_vault,
    mcp_trinity,
    mcp_reality,
)

logger = logging.getLogger(__name__)


@dataclass
class ToolDefinition:
    """MCP Tool Definition Schema"""

    name: str
    title: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable[..., Awaitable[Dict[str, Any]]]
    output_schema: Optional[Dict[str, Any]] = None
    annotations: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "inputSchema": self.input_schema,
        }
        if self.output_schema:
            result["outputSchema"] = self.output_schema
        if self.annotations:
            result["annotations"] = self.annotations
        return result


class ToolRegistry:
    """
    Central registry for all MCP tools.
    All transports (stdio, SSE, HTTP) consume this registry.
    """

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_canonical_tools()

    def register(self, tool: ToolDefinition) -> None:
        """Register a new tool."""
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool definition by name."""
        return self._tools.get(name)

    def list_tools(self) -> Dict[str, ToolDefinition]:
        """Get all registered tools."""
        return self._tools

    def _register_canonical_tools(self):
        """Register the 7 canonical constitutional tools."""

        # 1. _init_ (Gate)
        self.register(
            ToolDefinition(
                name="_init_",
                title="Session Initialization Gate",
                description="Initialize session with identity verification, injection detection, budget allocation. MUST be called first.",
                handler=mcp_init,
                input_schema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["init", "gate", "reset", "validate", "authorize"],
                            "default": "init",
                        },
                        "query": {"type": "string", "maxLength": 10000},
                        "session_id": {"type": "string", "minLength": 8},
                        "user_token": {"type": "string"},
                    },
                    "required": ["action"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "authority_level": {
                            "type": "string",
                            "enum": ["guest", "user", "admin", "system"],
                        },
                        "budget_allocated": {"type": "integer"},
                        "injection_check_passed": {"type": "boolean"},
                        "access_level": {"type": "string"},
                        "session_ttl": {"type": "integer"},
                        "constitutional_version": {"type": "string"},
                    },
                    "required": ["session_id", "authority_level", "injection_check_passed"],
                },
                annotations={
                    "title": "Session Gate",
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "openWorldHint": False,
                },
            )
        )

        # 2. _agi_ (Mind)
        self.register(
            ToolDefinition(
                name="_agi_",
                title="Mind Engine (Delta)",
                description="Deep reasoning, pattern recognition, knowledge retrieval. Implements 111 SENSE → 222 THINK → 333 FORGE.",
                handler=mcp_agi,
                input_schema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "sense",
                                "think",
                                "reflect",
                                "reason",
                                "atlas",
                                "forge",
                                "physics",
                                "full",
                            ],
                            "default": "full",
                        },
                        "query": {"type": "string", "maxLength": 10000},
                        "context": {"type": "object"},
                        "session_id": {"type": "string"},
                        "lane": {
                            "type": "string",
                            "enum": ["CRISIS", "HARD", "SOFT", "PHATIC"],
                            "default": "SOFT",
                        },
                    },
                    "required": ["action", "query"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "entropy_delta": {"type": "number"},
                        "omega_0": {"type": "number"},
                        "precision": {"type": "object"},
                        "hierarchical_beliefs": {"type": "object"},
                        "action_policy": {"type": "object"},
                        "vote": {"type": "string", "enum": ["SEAL", "VOID", "SABAR"]},
                        "floor_scores": {"type": "object"},
                    },
                    "required": ["session_id", "entropy_delta", "vote"],
                },
                annotations={
                    "title": "Mind Engine",
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "openWorldHint": True,
                },
            )
        )

        # 3. _asi_ (Heart)
        self.register(
            ToolDefinition(
                name="_asi_",
                title="Heart Engine (Omega)",
                description="Safety evaluation, bias detection, empathy assessment. Implements 555 EMPATHY → 666 ALIGN → 777 SOCIETY.",
                handler=mcp_asi,
                input_schema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "evidence",
                                "empathize",
                                "evaluate",
                                "act",
                                "witness",
                                "stakeholder",
                                "diffusion",
                                "audit",
                                "full",
                            ],
                            "default": "full",
                        },
                        "query": {"type": "string", "maxLength": 10000},
                        "reasoning": {"type": "string"},
                        "agi_context": {"type": "object"},
                        "session_id": {"type": "string"},
                    },
                    "required": ["action", "query"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "empathy_kappa_r": {"type": "number"},
                        "peace_squared": {"type": "number"},
                        "thermodynamic_justice": {"type": "number"},
                        "stakeholders": {"type": "array"},
                        "weakest_stakeholder": {"type": "object"},
                        "reversibility_score": {"type": "number"},
                        "consent_verified": {"type": "boolean"},
                        "vote": {"type": "string", "enum": ["SEAL", "VOID", "SABAR"]},
                        "omega_total": {"type": "number"},
                    },
                    "required": ["session_id", "omega_total", "vote"],
                },
                annotations={
                    "title": "Heart Engine",
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "openWorldHint": True,
                },
            )
        )

        # 4. _apex_ (Soul)
        self.register(
            ToolDefinition(
                name="_apex_",
                title="Soul Engine (Psi) - Judicial",
                description="Judicial consensus, final verdicts. Synthesizes AGI + ASI. Implements 888 APEX PRIME with 9-paradox equilibrium.",
                handler=mcp_apex,
                input_schema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["eureka", "judge", "decide", "proof", "entropy", "full"],
                            "default": "full",
                        },
                        "query": {"type": "string"},
                        "response": {"type": "string"},
                        "verdict": {
                            "type": "string",
                            "enum": ["SEAL", "PARTIAL", "VOID", "888_HOLD", "SABAR"],
                        },
                        "agi_context": {"type": "object"},
                        "asi_context": {"type": "object"},
                        "reasoning": {"type": "string"},
                        "session_id": {"type": "string"},
                    },
                    "required": ["action", "query"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "final_verdict": {
                            "type": "string",
                            "enum": ["SEAL", "PARTIAL", "VOID", "888_HOLD", "SABAR", "EQUILIBRIUM"],
                        },
                        "trinity_score": {"type": "number"},
                        "paradox_scores": {"type": "object"},
                        "equilibrium": {"type": "object"},
                        "constitutional_alignment": {"type": "object"},
                        "proof": {"type": "object"},
                    },
                    "required": ["session_id", "final_verdict", "trinity_score"],
                },
                annotations={
                    "title": "Soul Engine",
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "openWorldHint": False,
                },
            )
        )

        # 5. _vault_ (Seal)
        self.register(
            ToolDefinition(
                name="_vault_",
                title="Immutable Ledger (Seal)",
                description="Tamper-proof storage using Merkle-tree sealing. Implements F1 Amanah (Trust).",
                handler=mcp_vault,
                input_schema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["seal", "list", "read", "write", "propose"],
                            "default": "seal",
                        },
                        "verdict": {"type": "string"},
                        "decision_data": {"type": "object"},
                        "target": {
                            "type": "string",
                            "enum": ["seal", "ledger", "canon", "fag", "tempa", "phoenix", "audit"],
                            "default": "seal",
                        },
                        "session_id": {"type": "string"},
                    },
                    "required": ["action"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "merkle_root": {"type": "string"},
                        "timestamp": {"type": "string"},
                        "seal_id": {"type": "string"},
                        "target": {"type": "string"},
                        "integrity_hash": {"type": "string"},
                        "status": {"type": "string", "enum": ["SEALED", "PENDING", "ERROR"]},
                    },
                    "required": ["seal_id", "merkle_root", "status"],
                },
                annotations={
                    "title": "Vault Seal",
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "openWorldHint": False,
                },
            )
        )

        # 6. _trinity_ (Loop)
        self.register(
            ToolDefinition(
                name="_trinity_",
                title="Full Constitutional Pipeline",
                description="Complete metabolic loop: AGI→ASI→APEX→VAULT. Single-call constitutional evaluation.",
                handler=mcp_trinity,
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "maxLength": 10000},
                        "session_id": {"type": "string"},
                        "auto_seal": {"type": "boolean", "default": True},
                        "context": {"type": "object"},
                    },
                    "required": ["query"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "agi_result": {"type": "object"},
                        "asi_result": {"type": "object"},
                        "apex_result": {"type": "object"},
                        "vault_result": {"type": "object"},
                        "final_verdict": {"type": "string"},
                        "execution_time_ms": {"type": "number"},
                    },
                    "required": ["session_id", "final_verdict"],
                },
                annotations={
                    "title": "Full Trinity",
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "openWorldHint": True,
                },
            )
        )

        # 7. _reality_ (Ground)
        self.register(
            ToolDefinition(
                name="_reality_",
                title="External Fact-Checking",
                description="Fact-checking via external sources. Implements F7 Humility: external data labeled, sources cited, uncertainty stated.",
                handler=mcp_reality,
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "maxLength": 500},
                        "session_id": {"type": "string"},
                    },
                    "required": ["query"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "verified": {"type": "boolean"},
                        "confidence": {"type": "number"},
                        "sources": {"type": "array"},
                        "caveats": {"type": "string"},
                        "external_data_label": {"type": "string"},
                    },
                    "required": ["verified", "confidence"],
                },
                annotations={
                    "title": "Reality Check",
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "openWorldHint": True,
                },
            )
        )
