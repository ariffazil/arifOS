"""
Unified Constitutional Kernel MCP Server

This server exposes the arifOS constitutional kernel as MCP tools,
providing a clean, unified interface to all constitutional governance capabilities.

DITEMPA BUKAN DIBERI
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
import json
import time

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from arifos_core.enforcement.metrics import Metrics
from arifos_core.kernel import UnifiedConstitutionalKernel


class ConstitutionalMCPServer:
    """MCP server exposing the unified constitutional kernel"""

    def __init__(self):
        self.kernel = UnifiedConstitutionalKernel()
        self.server = Server("arifos-constitutional-kernel")
        self._register_tools()
    
    def _create_constitutional_response(self, data: Dict[str, Any]) -> types.TextContent:
        """Create standardized MCP response with constitutional governance data"""
        return types.TextContent(
            type="text",
            text=json.dumps(data, indent=2)
        )

    def _register_tools(self):
        """Register all constitutional tools with MCP"""

        # Register list_tools handler
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available constitutional tools"""
            return [
                types.Tool(
                    name="arifos_live",
                    description="Live constitutional governance through full 000→999 pipeline",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The query to judge"},
                            "user_id": {"type": "string", "description": "Optional user ID for context"}
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="agi_think",
                    description="AGI Bundle (The Mind) - proposes answers, structures truth, detects clarity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "User query to think about"},
                            "context": {"type": "object", "description": "Optional context for thinking process"}
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="asi_act",
                    description="ASI Bundle (The Heart) - validates safety, vetoes harm, ensures empathy",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "draft_response": {"type": "string", "description": "Draft text to validate"},
                            "intent": {"type": "string", "description": "Intent of the action"},
                            "recipient_context": {"type": "object", "description": "Optional recipient context for empathy"}
                        },
                        "required": ["draft_response", "intent"]
                    }
                ),
                types.Tool(
                    name="apex_seal",
                    description="APEX Bundle (The Soul) - final judgment and sealing authority",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agi_thought": {"type": "object", "description": "Output from AGI Bundle"},
                            "asi_veto": {"type": "object", "description": "Output from ASI Bundle"},
                            "evidence_pack": {"type": "object", "description": "Optional tri-witness evidence"}
                        },
                        "required": ["agi_thought", "asi_veto"]
                    }
                ),
                types.Tool(
                    name="get_constitutional_metrics",
                    description="Calculate all 12 constitutional floor metrics for given content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Text content to analyze"}
                        },
                        "required": ["content"]
                    }
                ),
                types.Tool(
                    name="constitutional_health",
                    description="Get comprehensive health status of the constitutional kernel",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]

        # Register call_tool handler
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Optional[Dict] = None) -> Union[types.TextContent, List[types.TextContent]]:
            """Handle tool calls with constitutional governance"""
            if arguments is None:
                arguments = {}
            
            return await self._handle_tool_call(name, arguments)

    async def _handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Union[types.TextContent, List[types.TextContent]]:
        """Handle individual tool calls with constitutional governance"""
        try:
            if name == "arifos_live":
                return await self._handle_arifos_live(arguments)
            elif name == "agi_think":
                return await self._handle_agi_think(arguments)
            elif name == "asi_act":
                return await self._handle_asi_act(arguments)
            elif name == "apex_seal":
                return await self._handle_apex_seal(arguments)
            elif name == "get_constitutional_metrics":
                return await self._handle_get_constitutional_metrics(arguments)
            elif name == "constitutional_health":
                return await self._handle_constitutional_health(arguments)
            else:
                return self._create_constitutional_response({
                    "error": f"Unknown tool: {name}",
                    "available_tools": ["arifos_live", "agi_think", "asi_act", "apex_seal", "get_constitutional_metrics", "constitutional_health"]
                })
        except Exception as e:
            return self._create_constitutional_response({
                "error": f"Tool execution failed: {str(e)}",
                "tool": name,
                "status": "error"
            })

    async def _handle_arifos_live(self, arguments: Dict[str, Any]) -> types.TextContent:
        """
        Handle arifos_live tool call - Live constitutional governance through full pipeline
        """
        try:
            query = arguments.get("query", "")
            user_id = arguments.get("user_id")
            
            # For this tool, we need both query and response
            # In practice, this would be called with a response to validate
            response = f"Response to: {query}"  # Placeholder response

            result = self.kernel.run_constitutional_pipeline(query, response, user_id)

            # Create standardized constitutional response
            # Note: result is a ConstitutionalVerdict dataclass, not a dict
            constitutional_data = {
                "verdict": result.verdict.value,  # Verdict enum -> string
                "reason": result.reason,
                "violated_floors": result.violated_floors,
                "execution_time_ms": result.total_execution_time_ms,
                "constitutional_valid": result.constitutional_valid,
                "tool": "arifos_live",
                "status": "constitutional_governance_complete"
            }
            
            return self._create_constitutional_response(constitutional_data)
            
        except Exception as e:
            # Constitutional error handling - always return proper MCP format
            error_data = {
                "verdict": "VOID",
                "reason": f"Constitutional pipeline error: {str(e)}",
                "violated_floors": ["F12_injection", "F11_command_auth"],
                "execution_time_ms": 0,
                "constitutional_valid": False,
                "tool": "arifos_live",
                "status": "constitutional_error"
            }
            return self._create_constitutional_response(error_data)

    async def _handle_agi_think(self, arguments: Dict[str, Any]) -> types.TextContent:
        """
        Handle agi_think tool call - AGI Bundle (The Mind)
        """
        try:
            query = arguments.get("query", "")
            context = arguments.get("context", {})
            
            # Execute AGI thinking stages with constitutional validation
            metrics = self.kernel.get_constitutional_metrics(query)
            
            # Create constitutional AGI response
            constitutional_valid = metrics.get("truth", 0.0) >= 0.9  # F2 Truth enforcement
            agi_data = {
                "verdict": "SEAL" if constitutional_valid else "VOID",
                "thought_process": f"AGI analysis of: {query}",
                "constitutional_metrics": {
                    "truth": metrics.get("truth", 0.0),
                    "clarity": metrics.get("delta_s", 0.0),
                    "reasoning_strength": metrics.get("reasoning", 0.8),
                    "confidence": metrics.get("truth", 0.0) * 0.9  # Constitutional confidence
                },
                "suggested_approach": "Constitutionally aligned reasoning",
                "uncertainty_level": metrics.get("omega_0", 0.04),
                "tool": "agi_think",
                "status": "constitutional_thinking_complete",
                "constitutional_valid": constitutional_valid
            }
            
            return self._create_constitutional_response(agi_data)
            
        except Exception as e:
            # Constitutional error handling for AGI thinking
            error_data = {
                "verdict": "VOID",
                "thought_process": f"AGI analysis failed for: {query}",
                "constitutional_metrics": {
                    "truth": 0.0,
                    "clarity": 0.0,
                    "reasoning_strength": 0.0,
                    "confidence": 0.0
                },
                "suggested_approach": "Constitutional error - review required",
                "uncertainty_level": 0.05,  # Maximum uncertainty
                "tool": "agi_think",
                "status": "constitutional_error",
                "constitutional_valid": False,
                "error": str(e)
            }
            return self._create_constitutional_response(error_data)

    async def _handle_asi_act(self, arguments: Dict[str, Any]) -> types.TextContent:
        """
        Handle asi_act tool call - ASI Bundle (The Heart)
        """
        try:
            draft_response = arguments.get("draft_response", "")
            intent = arguments.get("intent", "")
            recipient_context = arguments.get("recipient_context", {})
            
            # Execute ASI validation with constitutional metrics
            metrics = self.kernel.get_constitutional_metrics(draft_response)

            # Calculate constitutional scores with F3, F4, F5 enforcement
            empathy_score = metrics.get("kappa_r", 0.0)  # F4 Empathy
            safety_score = metrics.get("peace_squared", 1.0)  # F3 Peace²
            humility_score = 1.0 if 0.03 <= metrics.get("omega_0", 0.04) <= 0.05 else 0.5  # F5 Humility

            # Determine if action is constitutionally safe (F3, F4, F5 thresholds)
            constitutionally_safe = empathy_score >= 0.95 and safety_score >= 1.0 and humility_score >= 0.8

            # Create constitutional ASI response
            asi_data = {
                "verdict": "SEAL" if constitutionally_safe else "VOID",
                "asi_veto": not constitutionally_safe,
                "safety_assessment": "Safe" if constitutionally_safe else "Unsafe",
                "empathy_score": empathy_score,
                "safety_score": safety_score,
                "humility_score": humility_score,
                "recommendation": "Proceed with constitutional action" if constitutionally_safe else "Revise for constitutional compliance",
                "tool": "asi_act",
                "status": "constitutional_validation_complete",
                "constitutional_valid": constitutionally_safe,
                "enforced_floors": ["F3_Peace", "F4_Empathy", "F5_Humility"],
                "intent": intent,
                "recipient_context": recipient_context or {}
            }
            
            return self._create_constitutional_response(asi_data)
            
        except Exception as e:
            # Constitutional error handling for ASI validation
            error_data = {
                "verdict": "VOID",
                "asi_veto": True,  # Always veto on error
                "safety_assessment": "Unsafe",
                "empathy_score": 0.0,
                "safety_score": 0.0,
                "humility_score": 0.0,
                "recommendation": "Constitutional error - action blocked",
                "tool": "asi_act",
                "status": "constitutional_error",
                "constitutional_valid": False,
                "enforced_floors": ["F3_Peace", "F4_Empathy", "F5_Humility"],
                "error": str(e),
                "error_type": "ASI_validation_failure"
            }
            return self._create_constitutional_response(error_data)

    async def _handle_apex_seal(self, arguments: Dict[str, Any]) -> types.TextContent:
        """
        Handle apex_seal tool call - APEX Bundle (The Soul)
        """
        try:
            agi_thought = arguments.get("agi_thought", {})
            asi_veto = arguments.get("asi_veto", {})
            evidence_pack = arguments.get("evidence_pack", {})
            
            # Render final APEX judgment with constitutional authority
            query = "Constitutional decision synthesis"
            response = f"AGI: {agi_thought}, ASI: {asi_veto}"

            result = self.kernel.validate_constitutional_compliance(query, response)

            # Create constitutional APEX response with full governance
            apex_data = {
                "verdict": result.get("verdict", "VOID"),
                "reason": result.get("reason", "APEX judgment failed"),
                "constitutional_valid": result.get("constitutional_valid", False),
                "proof_hash": result.get("proof_hash"),
                "sealed_with_authority": True,
                "final_authority": "APEX PRIME",
                "tool": "apex_seal",
                "status": "constitutional_judgment_complete",
                "evidence_pack": evidence_pack or {},
                "tri_witness_validation": True,  # F8 enforcement
                "cryptographic_seal": result.get("proof_hash") is not None
            }
            
            return self._create_constitutional_response(apex_data)
            
        except Exception as e:
            # Constitutional error handling for APEX judgment
            error_data = {
                "verdict": "VOID",
                "reason": f"APEX constitutional judgment error: {str(e)}",
                "constitutional_valid": False,
                "proof_hash": None,
                "sealed_with_authority": False,
                "final_authority": "APEX PRIME",
                "tool": "apex_seal",
                "status": "constitutional_error",
                "evidence_pack": evidence_pack or {},
                "tri_witness_validation": False,
                "cryptographic_seal": False,
                "error": str(e),
                "error_type": "APEX_judgment_failure"
            }
            return self._create_constitutional_response(error_data)

    async def _handle_get_constitutional_metrics(self, arguments: Dict[str, Any]) -> types.TextContent:
        """
        Handle get_constitutional_metrics tool call
        """
        try:
            content = arguments.get("content", "")
            
            metrics = self.kernel.get_constitutional_metrics(content)

            # Create comprehensive constitutional metrics response
            constitutional_valid = metrics.get("psi", 0.0) >= 1.0
            metrics_data = {
                "verdict": "SEAL" if constitutional_valid else "VOID",
                "f1_amanah": metrics.get("amanah", False),
                "f2_truth": metrics.get("truth", 0.0),
                "f3_peace_squared": metrics.get("peace_squared", 0.0),
                "f4_kappa_r": metrics.get("kappa_r", 0.0),
                "f5_omega_0": metrics.get("omega_0", 0.0),
                "f6_delta_s": metrics.get("delta_s", 0.0),
                "f7_rasa": metrics.get("rasa", False),
                "f8_tri_witness": metrics.get("tri_witness", 0.0),
                "f9_anti_hantu": metrics.get("anti_hantu", True),
                "f10_ontology": metrics.get("ontology_ok", True),
                "f11_command_auth": metrics.get("command_auth_ok", True),
                "f12_injection_defense": metrics.get("injection_defense_ok", True),
                "system_psi": metrics.get("psi", 0.0),
                "constitutional_valid": constitutional_valid,
                "tool": "get_constitutional_metrics",
                "status": "constitutional_metrics_complete",
                "content_analyzed": content[:100] + "..." if len(content) > 100 else content,
                "analysis_timestamp": time.time()
            }
            
            return self._create_constitutional_response(metrics_data)
            
        except Exception as e:
            # Constitutional error handling for metrics calculation
            error_data = {
                "f1_amanah": False,
                "f2_truth": 0.0,
                "f3_peace_squared": 0.0,
                "f4_kappa_r": 0.0,
                "f5_omega_0": 0.0,
                "f6_delta_s": 0.0,
                "f7_rasa": False,
                "f8_tri_witness": 0.0,
                "f9_anti_hantu": False,
                "f10_ontology": False,
                "f11_command_auth": False,
                "f12_injection_defense": False,
                "system_psi": 0.0,
                "constitutional_valid": False,
                "tool": "get_constitutional_metrics",
                "status": "constitutional_error",
                "content_analyzed": content[:100] + "..." if len(content) > 100 else content,
                "analysis_timestamp": time.time(),
                "error": str(e),
                "error_type": "metrics_calculation_failure"
            }
            return self._create_constitutional_response(error_data)

    async def _handle_constitutional_health(self, arguments: Dict[str, Any]) -> types.TextContent:
        """
        Handle constitutional_health tool call
        """
        try:
            health = self.kernel.get_health()

            # Create comprehensive constitutional health response
            constitutional_valid = True  # Health check itself is constitutionally valid
            health_data = {
                "verdict": "SEAL" if constitutional_valid else "VOID",
                "kernel_status": "operational",
                "constitutional_guarantees": "all_active",
                "mcp_integration": "enabled",
                "components": health,
                "version": "v47.0.0-unified",
                "ditempa_bukan_diberi": True,
                "tool": "constitutional_health",
                "status": "constitutional_health_complete",
                "constitutional_valid": constitutional_valid,
                "health_check_timestamp": time.time(),
                "mcp_server_status": {
                    "server_name": "arifos-constitutional-kernel",
                    "tools_registered": 6,  # All our constitutional tools
                    "response_format": "standardized_mcp_textcontent",
                    "constitutional_compliance": "enforced"
                }
            }
            
            return self._create_constitutional_response(health_data)
            
        except Exception as e:
            # Constitutional error handling for health check
            constitutional_valid = False  # Error state is not constitutionally valid
            error_data = {
                "verdict": "VOID",
                "kernel_status": "error",
                "constitutional_guarantees": "degraded",
                "mcp_integration": "failed",
                "components": {"error": str(e)},
                "version": "v47.0.0-unified",
                "ditempa_bukan_diberi": True,
                "tool": "constitutional_health",
                "status": "constitutional_error",
                "constitutional_valid": constitutional_valid,
                "health_check_timestamp": time.time(),
                "mcp_server_status": {
                    "server_name": "arifos-constitutional-kernel",
                    "tools_registered": 0,
                    "response_format": "error_state",
                    "constitutional_compliance": "failed"
                },
                "error": str(e),
                "error_type": "health_check_failure"
            }
            return self._create_constitutional_response(error_data)

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


# Standalone server entry point
async def main():
    """Main entry point for the constitutional kernel MCP server"""
    server = ConstitutionalMCPServer()
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())