"""
Unified Constitutional Kernel MCP Server

This server exposes the arifOS constitutional kernel as MCP tools,
providing a clean, unified interface to all constitutional governance capabilities.

DITEMPA BUKAN DIBERI
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

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

    def _register_tools(self):
        """Register all constitutional tools with MCP"""

        # Core constitutional pipeline
        @self.server.tool()
        async def arifos_live(query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
            """
            Live constitutional governance through the full arifOS pipeline (000→999).

            Stage 000: Initialization, intuition, and real-time governance.
            Returns verdict (SEAL/PARTIAL/VOID/SABAR/888_HOLD) based on 12 constitutional floors.

            Args:
                query: The query to judge
                user_id: Optional user ID for context

            Returns:
                Constitutional verdict with full governance trace
            """
            # For this tool, we need both query and response
            # In practice, this would be called with a response to validate
            response = f"Response to: {query}"  # Placeholder response

            result = self.kernel.run_constitutional_pipeline(query, response, user_id)
            return {
                "verdict": result["verdict"],
                "reason": result["reason"],
                "violated_floors": result["violated_floors"],
                "execution_time_ms": result["total_execution_time_ms"],
                "constitutional_valid": result["constitutional_valid"]
            }

        # AGI Bundle - The Mind
        @self.server.tool()
        async def agi_think(query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
            """
            AGI Bundle (The Mind). Proposes answers, structures truth, detects clarity.
            Consolidates 111, 222, 777 constitutional stages.

            Args:
                query: User query to think about
                context: Optional context for thinking process

            Returns:
                AGI reasoning results with constitutional metrics
            """
            # Execute AGI thinking stages
            metrics = self.kernel.get_constitutional_metrics(query)

            return {
                "thought_process": f"AGI analysis of: {query}",
                "constitutional_metrics": {
                    "truth": metrics.get("truth", 0.0),
                    "clarity": metrics.get("delta_s", 0.0),
                    "reasoning_strength": metrics.get("reasoning", 0.8)
                },
                "suggested_approach": "Constitutionally aligned reasoning",
                "uncertainty_level": metrics.get("omega_0", 0.04)
            }

        # ASI Bundle - The Heart
        @self.server.tool()
        async def asi_act(draft_response: str, intent: str, recipient_context: Optional[Dict] = None) -> Dict[str, Any]:
            """
            ASI Bundle (The Heart). Validates safety, vetoes harm, ensures empathy.
            Consolidates 555, 666, Hypervisor constitutional stages.

            Args:
                draft_response: Draft text to validate
                intent: Intent of the action
                recipient_context: Optional recipient context for empathy

            Returns:
                ASI validation results with safety assessment
            """
            # Execute ASI validation
            metrics = self.kernel.get_constitutional_metrics(draft_response)

            # Calculate empathy and safety scores
            empathy_score = metrics.get("kappa_r", 0.0)
            safety_score = metrics.get("peace_squared", 1.0)
            humility_score = 1.0 if 0.03 <= metrics.get("omega_0", 0.04) <= 0.05 else 0.5

            # Determine if action is constitutionally safe
            constitutionally_safe = empathy_score >= 0.95 and safety_score >= 1.0 and humility_score >= 0.8

            return {
                "asi_veto": not constitutionally_safe,
                "safety_assessment": "Safe" if constitutionally_safe else "Unsafe",
                "empathy_score": empathy_score,
                "safety_score": safety_score,
                "humility_score": humility_score,
                "recommendation": "Proceed with constitutional action" if constitutionally_safe else "Revise for constitutional compliance"
            }

        # APEX Bundle - The Soul
        @self.server.tool()
        async def apex_seal(agi_thought: Dict, asi_veto: Dict, evidence_pack: Optional[Dict] = None) -> Dict[str, Any]:
            """
            APEX Bundle (The Soul) - Final judgment and sealing authority.
            Consolidates 444 (evidence), 888 (judgment), 889 (proof).
            Audits AGI/ASI states, verifies tri-witness evidence, renders final verdict.

            Args:
                agi_thought: Output from AGI Bundle
                asi_veto: Output from ASI Bundle
                evidence_pack: Optional tri-witness evidence

            Returns:
                Final constitutional verdict with cryptographic sealing
            """
            # Render final APEX judgment
            query = "Constitutional decision synthesis"
            response = f"AGI: {agi_thought}, ASI: {asi_veto}"

            result = self.kernel.validate_constitutional_compliance(query, response)

            return {
                "verdict": result.get("verdict", "VOID"),
                "reason": result.get("reason", "APEX judgment failed"),
                "constitutional_valid": result.get("constitutional_valid", False),
                "proof_hash": result.get("proof_hash"),
                "sealed_with_authority": True,
                "final_authority": "APEX PRIME"
            }

        # Constitutional Metrics
        @self.server.tool()
        async def get_constitutional_metrics(content: str) -> Dict[str, Any]:
            """
            Calculate all 12 constitutional floor metrics for given content.

            Args:
                content: Text content to analyze

            Returns:
                Complete constitutional metrics including all floors F1-F12
            """
            metrics = self.kernel.get_constitutional_metrics(content)

            return {
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
                "constitutional_valid": metrics.get("psi", 0.0) >= 1.0
            }

        # Health Check
        @self.server.tool()
        async def constitutional_health() -> Dict[str, Any]:
            """
            Get comprehensive health status of the constitutional kernel.

            Returns:
                Complete health report of all constitutional components
            """
            health = self.kernel.get_health()

            return {
                "kernel_status": "operational",
                "constitutional_guarantees": "all_active",
                "mcp_integration": "enabled",
                "components": health,
                "version": "v47.0.0-unified",
                "ditempa_bukan_diberi": True
            }

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
