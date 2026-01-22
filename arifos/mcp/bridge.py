"""
arifOS MCP-Core Bridge (v50.5.23)

Bridges MCP tools to Core engines with proper Three Trinities integration.

This bridge provides:
    1. Engine instantiation and lifecycle management
    2. Data transformation between MCP and Core formats
    3. Tool link registry for external integrations
    4. Proper error handling with constitutional floor checks

MCP → Bridge → Core:
    mcp_agi_genius → AGIEngine.execute()
    mcp_asi_act    → ASIEngine.execute()
    mcp_apex_judge → APEXEngine.execute()

Tool Links (via MCP):
    AGI: mcp://search, mcp://code, mcp://memory, mcp://docs
    ASI: mcp://email, mcp://desktop, mcp://api, mcp://notify
    APEX: mcp://vault, mcp://audit, mcp://proof

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
import time

# Core engines
from arifos.core.engines import (
    # AGI
    AGIEngine,
    AGIOutput,
    Lane,
    # ASI
    ASIEngine,
    ASIOutput,
    # APEX
    APEXEngine,
    APEXOutput,
)

# Trinity framework
from arifos.core.trinity import (
    Verdict,
    ThreeTrinities,
    ThermodynamicSignature,
)

logger = logging.getLogger(__name__)


# =============================================================================
# TOOL LINK REGISTRY
# =============================================================================

@dataclass
class ToolLink:
    """External tool link for MCP integration."""
    name: str
    uri: str
    engine: str  # AGI, ASI, APEX
    category: str  # search, code, action, audit
    executor: Optional[Callable] = None
    requires_auth: bool = False


class ToolRegistry:
    """
    Central registry for external tool links.

    NOTE: These tools will be connected via MCP protocol.
    The registry tracks what's available; executors are registered at runtime.
    """

    _instance: Optional['ToolRegistry'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_registry()
        return cls._instance

    def _init_registry(self):
        """Initialize the tool registry with default links."""
        self._tools: Dict[str, ToolLink] = {}

        # AGI Tools (Mind/Δ)
        self._register_defaults_agi()

        # ASI Tools (Heart/Ω)
        self._register_defaults_asi()

        # APEX Tools (Soul/Ψ)
        self._register_defaults_apex()

    def _register_defaults_agi(self):
        """Register default AGI tool links."""
        agi_tools = [
            ToolLink("search", "mcp://arifos/search", "AGI", "search"),
            ToolLink("code_analysis", "mcp://arifos/code", "AGI", "code"),
            ToolLink("memory_read", "mcp://arifos/vault999/read", "AGI", "memory"),
            ToolLink("docs_lookup", "mcp://arifos/docs", "AGI", "docs"),
            ToolLink("knowledge_graph", "mcp://arifos/kg", "AGI", "knowledge"),
        ]
        for tool in agi_tools:
            self._tools[f"agi_{tool.name}"] = tool

    def _register_defaults_asi(self):
        """Register default ASI tool links."""
        asi_tools = [
            ToolLink("email", "mcp://arifos/email", "ASI", "action", requires_auth=True),
            ToolLink("desktop", "mcp://arifos/desktop", "ASI", "action", requires_auth=True),
            ToolLink("api_call", "mcp://arifos/api", "ASI", "action", requires_auth=True),
            ToolLink("notify", "mcp://arifos/notify", "ASI", "action"),
            ToolLink("calendar", "mcp://arifos/calendar", "ASI", "action", requires_auth=True),
            ToolLink("file_ops", "mcp://arifos/files", "ASI", "action", requires_auth=True),
            ToolLink("browser", "mcp://arifos/browser", "ASI", "action", requires_auth=True),
        ]
        for tool in asi_tools:
            self._tools[f"asi_{tool.name}"] = tool

    def _register_defaults_apex(self):
        """Register default APEX tool links."""
        apex_tools = [
            ToolLink("vault_seal", "mcp://arifos/vault999/seal", "APEX", "audit"),
            ToolLink("audit_log", "mcp://arifos/audit", "APEX", "audit"),
            ToolLink("proof_gen", "mcp://arifos/proof", "APEX", "audit"),
            ToolLink("merkle", "mcp://arifos/merkle", "APEX", "audit"),
        ]
        for tool in apex_tools:
            self._tools[f"apex_{tool.name}"] = tool

    def register(self, key: str, tool: ToolLink) -> None:
        """Register a tool link."""
        self._tools[key] = tool
        logger.info(f"ToolRegistry: Registered {key} -> {tool.uri}")

    def register_executor(self, key: str, executor: Callable) -> None:
        """Register an executor for a tool link."""
        if key in self._tools:
            self._tools[key].executor = executor
            logger.info(f"ToolRegistry: Executor registered for {key}")
        else:
            logger.warning(f"ToolRegistry: Unknown tool {key}")

    def get(self, key: str) -> Optional[ToolLink]:
        """Get a tool link by key."""
        return self._tools.get(key)

    def get_by_engine(self, engine: str) -> List[ToolLink]:
        """Get all tool links for an engine (AGI, ASI, APEX)."""
        return [t for t in self._tools.values() if t.engine == engine]

    def list_all(self) -> Dict[str, str]:
        """List all registered tools."""
        return {k: v.uri for k, v in self._tools.items()}


# =============================================================================
# MCP-CORE BRIDGE
# =============================================================================

class MCPCoreBridge:
    """
    Bridges MCP tools to Core engines.

    Manages engine lifecycle and provides unified interface for MCP tools.
    """

    def __init__(self, session_id: Optional[str] = None):
        """Initialize the bridge."""
        self.session_id = session_id or f"bridge_{int(time.time()*1000)}"
        self.start_time = time.time()

        # Engine instances (lazy initialization)
        self._agi: Optional[AGIEngine] = None
        self._asi: Optional[ASIEngine] = None
        self._apex: Optional[APEXEngine] = None

        # Tool registry
        self._registry = ToolRegistry()

        # Session state
        self._agi_output: Optional[AGIOutput] = None
        self._asi_output: Optional[ASIOutput] = None
        self._apex_output: Optional[APEXOutput] = None

    @property
    def agi(self) -> AGIEngine:
        """Lazy-load AGI engine."""
        if self._agi is None:
            self._agi = AGIEngine(session_id=f"{self.session_id}_agi")
        return self._agi

    @property
    def asi(self) -> ASIEngine:
        """Lazy-load ASI engine."""
        if self._asi is None:
            self._asi = ASIEngine(session_id=f"{self.session_id}_asi")
        return self._asi

    @property
    def apex(self) -> APEXEngine:
        """Lazy-load APEX engine."""
        if self._apex is None:
            self._apex = APEXEngine(session_id=f"{self.session_id}_apex")
        return self._apex

    # =========================================================================
    # AGI BRIDGE
    # =========================================================================

    def execute_agi(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute AGI engine and return MCP-compatible result.

        Maps: SENSE → THINK → ATLAS → FORGE
        """
        try:
            output = self.agi.execute(query, context)
            self._agi_output = output

            # Transform to MCP format
            return self._transform_agi_output(output)

        except Exception as e:
            logger.error(f"MCPCoreBridge.execute_agi failed: {e}")
            return {
                "status": "VOID",
                "session_id": self.session_id,
                "error": str(e),
                "floors_checked": [],
                "floor_violations": [f"AGI_ENGINE_ERROR: {e}"]
            }

    def _transform_agi_output(self, output: AGIOutput) -> Dict[str, Any]:
        """Transform AGIOutput to MCP-compatible format."""
        result = output.as_dict()

        # Add MCP-specific fields
        result["mcp_bridge"] = True
        result["tool_links"] = [t.uri for t in self._registry.get_by_engine("AGI")]

        # Transform lane enum to string
        if output.sense:
            result["lane"] = output.sense.gpv.lane.value

        return result

    # =========================================================================
    # ASI BRIDGE
    # =========================================================================

    def execute_asi(self, agi_output: Dict[str, Any],
                    user_context: Optional[Dict[str, Any]] = None,
                    proposed_action: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute ASI engine and return MCP-compatible result.

        Maps: EVIDENCE → EMPATHY → ALIGN → ACT
        """
        try:
            output = self.asi.execute(agi_output, user_context, proposed_action)
            self._asi_output = output

            # Transform to MCP format
            return self._transform_asi_output(output)

        except Exception as e:
            logger.error(f"MCPCoreBridge.execute_asi failed: {e}")
            return {
                "status": "VOID",
                "session_id": self.session_id,
                "error": str(e),
                "floors_checked": [],
                "floor_violations": [f"ASI_ENGINE_ERROR: {e}"]
            }

    def _transform_asi_output(self, output: ASIOutput) -> Dict[str, Any]:
        """Transform ASIOutput to MCP-compatible format."""
        result = output.as_dict()

        # Add MCP-specific fields
        result["mcp_bridge"] = True
        result["tool_links"] = [t.uri for t in self._registry.get_by_engine("ASI")]
        result["action_queue"] = self.asi.get_action_queue()

        return result

    # =========================================================================
    # APEX BRIDGE
    # =========================================================================

    def execute_apex(self, agi_output: Dict[str, Any],
                     asi_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute APEX engine and return MCP-compatible result.

        Maps: EUREKA → JUDGE → PROOF
        """
        try:
            output = self.apex.execute(agi_output, asi_output)
            self._apex_output = output

            # Transform to MCP format
            return self._transform_apex_output(output)

        except Exception as e:
            logger.error(f"MCPCoreBridge.execute_apex failed: {e}")
            return {
                "status": "VOID",
                "session_id": self.session_id,
                "error": str(e),
                "floors_checked": [],
                "floor_violations": [f"APEX_ENGINE_ERROR: {e}"]
            }

    def _transform_apex_output(self, output: APEXOutput) -> Dict[str, Any]:
        """Transform APEXOutput to MCP-compatible format."""
        result = output.as_dict()

        # Add MCP-specific fields
        result["mcp_bridge"] = True
        result["tool_links"] = [t.uri for t in self._registry.get_by_engine("APEX")]

        return result

    # =========================================================================
    # FULL PIPELINE
    # =========================================================================

    def execute_full_pipeline(self, query: str,
                              context: Optional[Dict[str, Any]] = None,
                              proposed_action: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute complete pipeline: AGI → ASI → APEX

        Returns unified result with all engine outputs.
        """
        start = time.time()

        # Step 1: AGI (Mind)
        agi_result = self.execute_agi(query, context)

        if agi_result.get("status") == "VOID":
            return {
                "status": "VOID",
                "session_id": self.session_id,
                "stage": "AGI",
                "agi_result": agi_result,
                "reason": "AGI stage failed"
            }

        # Step 2: ASI (Heart)
        asi_result = self.execute_asi(agi_result, context, proposed_action)

        if asi_result.get("status") == "VOID":
            return {
                "status": "VOID",
                "session_id": self.session_id,
                "stage": "ASI",
                "agi_result": agi_result,
                "asi_result": asi_result,
                "reason": "ASI stage failed"
            }

        # Step 3: APEX (Soul)
        apex_result = self.execute_apex(agi_result, asi_result)

        # Calculate thermodynamics
        elapsed = time.time() - start

        return {
            "status": apex_result.get("status", "SABAR"),
            "session_id": self.session_id,
            "verdict": apex_result.get("verdict", "SABAR"),
            "agi_result": agi_result,
            "asi_result": asi_result,
            "apex_result": apex_result,
            "pipeline_duration": elapsed,
            "three_trinities": apex_result.get("three_trinities"),
            "thermodynamics": {
                "total_time": elapsed,
                "energy_consumed": elapsed * 0.1
            },
            "tool_links": {
                "agi": [t.uri for t in self._registry.get_by_engine("AGI")],
                "asi": [t.uri for t in self._registry.get_by_engine("ASI")],
                "apex": [t.uri for t in self._registry.get_by_engine("APEX")]
            }
        }

    # =========================================================================
    # TOOL LINK EXECUTION
    # =========================================================================

    def execute_tool(self, tool_key: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a registered tool link.

        Returns result from the tool executor if registered.
        """
        tool = self._registry.get(tool_key)

        if not tool:
            return {
                "status": "VOID",
                "error": f"Unknown tool: {tool_key}"
            }

        if not tool.executor:
            return {
                "status": "SABAR",
                "tool": tool_key,
                "uri": tool.uri,
                "message": "Tool registered but no executor available",
                "params": params
            }

        try:
            result = tool.executor(**params)
            return {
                "status": "SEAL",
                "tool": tool_key,
                "result": result
            }
        except Exception as e:
            return {
                "status": "VOID",
                "tool": tool_key,
                "error": str(e)
            }

    # =========================================================================
    # STATE ACCESS
    # =========================================================================

    def get_state(self) -> Dict[str, Any]:
        """Get current bridge state."""
        return {
            "session_id": self.session_id,
            "duration": time.time() - self.start_time,
            "agi_ready": self._agi is not None,
            "asi_ready": self._asi is not None,
            "apex_ready": self._apex is not None,
            "has_agi_output": self._agi_output is not None,
            "has_asi_output": self._asi_output is not None,
            "has_apex_output": self._apex_output is not None,
            "registered_tools": len(self._registry._tools)
        }

    def reset(self) -> None:
        """Reset bridge state."""
        self._agi = None
        self._asi = None
        self._apex = None
        self._agi_output = None
        self._asi_output = None
        self._apex_output = None
        self.start_time = time.time()


# =============================================================================
# SINGLETON BRIDGE
# =============================================================================

_bridge_instance: Optional[MCPCoreBridge] = None


def get_bridge(session_id: Optional[str] = None) -> MCPCoreBridge:
    """Get or create the MCP-Core bridge instance."""
    global _bridge_instance
    if _bridge_instance is None or session_id:
        _bridge_instance = MCPCoreBridge(session_id)
    return _bridge_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MCPCoreBridge",
    "ToolRegistry",
    "ToolLink",
    "get_bridge",
]
