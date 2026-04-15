"""
arifOS Schema Registry
Context-Rich Tool Registry for semantic tool discovery
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SCHEMA_DIR = Path(__file__).parent
REGISTRY_DIR = SCHEMA_DIR / "registry" / "tools"


class SchemaRegistry:
    """
    Context-Rich Tool Registry for arifOS.
    
    Provides semantic tool discovery including:
    - Full tool context packets (purpose, when_to_use, when_not_to_use)
    - Stage transitions and governance flow
    - Trinity lane definitions
    - Shared request/response envelopes
    """
    
    def __init__(self):
        self._master_schema: dict[str, Any] | None = None
        self._tool_packets: dict[str, dict[str, Any]] = {}
        self._request_schema: dict[str, Any] | None = None
        self._response_schema: dict[str, Any] | None = None
        self._context_packet_schema: dict[str, Any] | None = None
        self._loaded = False
    
    def load(self) -> "SchemaRegistry":
        """Load all schema files."""
        if self._loaded:
            return self
            
        # Load master schema
        master_path = SCHEMA_DIR / "arifos.schema.json"
        if master_path.exists():
            with open(master_path) as f:
                self._master_schema = json.load(f)
            logger.info(f"Loaded master schema: {master_path}")
        
        # Load tool context packets
        for tool_file in REGISTRY_DIR.glob("arifos.*.json"):
            try:
                with open(tool_file) as f:
                    packet = json.load(f)
                    tool_id = packet.get("tool_id")
                    if tool_id:
                        self._tool_packets[tool_id] = packet
                        logger.debug(f"Loaded context packet: {tool_id}")
            except Exception as e:
                logger.warning(f"Failed to load {tool_file}: {e}")
        
        # Load envelope schemas
        req_path = SCHEMA_DIR / "request.envelope.schema.json"
        if req_path.exists():
            with open(req_path) as f:
                self._request_schema = json.load(f)
        
        resp_path = SCHEMA_DIR / "response.envelope.schema.json"
        if resp_path.exists():
            with open(resp_path) as f:
                self._response_schema = json.load(f)
        
        ctx_path = SCHEMA_DIR / "context.packet.schema.json"
        if ctx_path.exists():
            with open(ctx_path) as f:
                self._context_packet_schema = json.load(f)
        
        self._loaded = True
        logger.info(f"SchemaRegistry loaded: {len(self._tool_packets)} tool packets")
        return self
    
    @property
    def master_schema(self) -> dict[str, Any] | None:
        """Get the full arifOS master schema."""
        return self._master_schema
    
    @property
    def tool_packets(self) -> dict[str, dict[str, Any]]:
        """Get all tool context packets."""
        return self._tool_packets
    
    def get_tool_packet(self, tool_id: str) -> dict[str, Any] | None:
        """Get context packet for a specific tool."""
        return self._tool_packets.get(tool_id)
    
    def get_request_schema(self) -> dict[str, Any] | None:
        """Get unified request envelope schema."""
        return self._request_schema
    
    def get_response_schema(self) -> dict[str, Any] | None:
        """Get unified response envelope schema."""
        return self._response_schema
    
    def get_context_packet_schema(self) -> dict[str, Any] | None:
        """Get context packet schema definition."""
        return self._context_packet_schema
    
    def get_stage_info(self, stage: str) -> dict[str, Any] | None:
        """Get information about a governance stage."""
        if not self._master_schema:
            return None
        return self._master_schema.get("stages", {}).get(stage)
    
    def get_trinity_info(self, symbol: str) -> dict[str, Any] | None:
        """Get Trinity lane definition."""
        if not self._master_schema:
            return None
        return self._master_schema.get("trinity", {}).get(symbol)
    
    def get_transitions(self, stage: str) -> dict[str, Any] | None:
        """Get valid transitions from a stage."""
        if not self._master_schema:
            return None
        return self._master_schema.get("transitions", {}).get(stage)
    
    def get_alias_map(self) -> dict[str, dict[str, str]]:
        """Get mapping from public aliases to backing tools."""
        if not self._master_schema:
            return {}
        return self._master_schema.get("alias_map", {})
    
    def get_tool_summary(self) -> list[dict[str, Any]]:
        """Get compact summary of all tools for quick reference."""
        summary = []
        for tool_id, packet in self._tool_packets.items():
            summary.append({
                "tool_id": tool_id,
                "stage": packet.get("stage"),
                "desc": packet.get("desc"),
                "trinity": packet.get("trinity"),
                "role": packet.get("role"),
                "modes": packet.get("modes", []),
            })
        return sorted(summary, key=lambda x: x.get("stage", ""))
    
    def get_chatgpt_guidance(self, tool_id: str) -> dict[str, Any] | None:
        """Get ChatGPT-specific usage guidance for a tool."""
        packet = self._tool_packets.get(tool_id)
        if packet:
            return packet.get("chatgpt_guidance")
        return None
    
    def get_routing_guide(self) -> dict[str, Any]:
        """Get complete routing guidance for stage transitions."""
        if not self._master_schema:
            return {}
        
        return {
            "stage_order": self._master_schema.get("stage_order", []),
            "transitions": self._master_schema.get("transitions", {}),
            "tools_by_stage": {
                packet.get("stage"): tool_id
                for tool_id, packet in self._tool_packets.items()
            }
        }


# Global registry instance
_registry: SchemaRegistry | None = None


def get_registry() -> SchemaRegistry:
    """Get the global schema registry (lazy-loaded)."""
    global _registry
    if _registry is None:
        _registry = SchemaRegistry().load()
    return _registry


def get_context_packet(tool_id: str) -> dict[str, Any] | None:
    """Convenience: get context packet for a tool."""
    return get_registry().get_tool_packet(tool_id)


def get_all_context_packets() -> dict[str, dict[str, Any]]:
    """Convenience: get all context packets."""
    return get_registry().tool_packets


def get_master_schema() -> dict[str, Any] | None:
    """Convenience: get master schema."""
    return get_registry().master_schema
