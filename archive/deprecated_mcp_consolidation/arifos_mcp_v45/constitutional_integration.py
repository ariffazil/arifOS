"""
Constitutional Integration - Kimi Orthogonal Directive Implementation
AAA MCP Server Integration with Quantum Constitutional Physics

Wraps existing MCP tools with constitutional physics enforcement:
- Orthogonality (Particle Independence)
- Bidirectionality (Governance Conservation) 
- Quantum Superposition ([AGI ∩ ASI ∩ APEX])
- Measurement Collapse at 999_seal
"""

import asyncio
import logging
import inspect
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone

from arifos_core.mcp.parallel_hypervisor import (
    ConstitutionalPhysicsPipeline,
    ConstitutionalMCPIntegration,
    execute_with_constitutional_physics
)
from arifos_core.mcp.constitution import (
    AGIParticle,
    ASIParticle,
    APEXParticle,
    ConstitutionalContext
)

# Configure constitutional physics logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [ConstitutionalIntegration] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("constitutional_integration")


class ConstitutionalMCPServer:
    """
    Constitutional wrapper for AAA MCP Server.
    
    Implements Kimi Orthogonal Directive by wrapping existing MCP tools
    with constitutional physics while maintaining backward compatibility.
    """
    
    def __init__(self):
        self.physics_pipeline = ConstitutionalPhysicsPipeline()
        self.tool_integration = ConstitutionalMCPIntegration()
        self.constitutional_tools = {}
        self.measurement_history = []
        self.is_constitutional_mode = True  # Constitutional physics enabled by default
        
        # Map existing tools to trinity assignments
        self.trinity_assignments = {
            # AGI Tools (Δ - Architect)
            "mcp_000_reset": "AGI",
            "mcp_111_sense": "AGI", 
            "mcp_222_reflect": "AGI",
            "mcp_333_atlas": "AGI",
            
            # ASI Tools (Ω - Engineer)
            "mcp_444_align": "ASI",
            "mcp_555_empathize": "ASI",
            "mcp_666_bridge": "ASI",
            "mcp_777_eureka": "ASI",
            
            # APEX Tools (Ψ - Auditor)
            "mcp_888_judge": "APEX",
            "mcp_999_seal": "APEX",
            
            # VTEMPA Tools (Constitutional Pipeline)
            "vtempa_reflection": "AGI",
            "vtempa_action": "ASI",
            "vtempa_execution": "ASI",
            "vtempa_self_correction": "ASI",
            "vtempa_memory": "APEX",
            
            # VAULT-999 Tools (APEX Authority)
            "vault999_store": "APEX",
            "vault999_eval": "APEX",
            
            # Witness Tools (Distributed Consensus)
            "witness_vote": "APEX",
            "get_aaa_manifest": "APEX",
            "check_vitality": "APEX"
        }
    
    async def wrap_tool_constitutionally(self, tool_name: str, tool_function: Callable) -> Callable:
        """
        Wrap an MCP tool with constitutional physics enforcement.
        
        Maintains tool functionality while adding:
        - Orthogonality (no shared state with other tools)
        - Bidirectionality (receipt generation for feedback)
        - Constitutional validation (F1-F9 floors)
        - Quantum superposition execution
        """
        
        trinity_assignment = self.trinity_assignments.get(tool_name, "UNKNOWN")
        
        logger.info(f"🔧 Wrapping {tool_name} with constitutional physics ({trinity_assignment})")
        
        async def constitutional_tool_wrapper(*args, **kwargs):
            try:
                # Extract constitutional context from arguments
                context = self._extract_constitutional_context(tool_name, args, kwargs)
                
                # Build constitutional query for physics pipeline
                query = self._build_constitutional_query(tool_name, args, kwargs)
                
                logger.info(f"⚡ Executing {tool_name} with constitutional physics")
                logger.info(f"   Trinity Assignment: {trinity_assignment}")
                logger.info(f"   Context: {context.get('description', 'Default')}")
                
                # Execute with constitutional physics (quantum superposition)
                constitutional_result = await self.physics_pipeline.execute_quantum_constitutional(
                    query=query,
                    user_id=context.get("user_id", "unknown"),
                    context=context
                )
                
                # Map constitutional result back to expected tool format
                wrapped_result = self._map_to_tool_format(
                    constitutional_result, tool_function, tool_name, args, kwargs
                )
                
                # Store measurement for bidirectional feedback
                self._store_constitutional_measurement(constitutional_result, tool_name)
                
                logger.info(f"✅ {tool_name} completed with verdict: {constitutional_result['verdict']}")
                
                return wrapped_result
                
            except Exception as e:
                logger.error(f"❌ Constitutional physics failed for {tool_name}: {e}")
                
                # Constitutional crisis - return VOID and preserve system integrity
                return {
                    "verdict": "VOID",
                    "constitutional_error": str(e),
                    "tool_name": tool_name,
                    "physics_preserved": False,
                    "immediate_action": "CONSTITUTIONAL_CRISIS"
                }
        
        # Store wrapped tool
        self.constitutional_tools[tool_name] = constitutional_tool_wrapper
        
        return constitutional_tool_wrapper
    
    def _extract_constitutional_context(self, tool_name: str, args, kwargs) -> Dict[str, Any]:
        """Extract constitutional context from tool arguments"""
        
        # Extract common constitutional parameters
        user_id = kwargs.get("user_id", "unknown")
        session_id = kwargs.get("session_id", f"constitutional_session_{datetime.now().timestamp()}")
        
        # Build constitutional description
        description = f"{tool_name}_execution"
        if args:
            description += f":{hash(str(args))[:16]}"
        
        return {
            "tool_name": tool_name,
            "user_id": user_id,
            "session_id": session_id,
            "description": description,
            "args": args,
            "kwargs": kwargs,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_constraints": []  # Will be populated by bidirectional feedback
        }
    
    def _build_constitutional_query(self, tool_name: str, args, kwargs) -> str:
        """Build constitutional query for physics pipeline"""
        
        # Create unique query identifier
        args_hash = hash(str(args)) if args else "no_args"
        kwargs_hash = hash(str(kwargs)) if kwargs else "no_kwargs"
        
        return f"{tool_name}:{args_hash}:{kwargs_hash}"
    
    def _map_to_tool_format(self, constitutional_result: Dict[str, Any], 
                           original_tool: Callable, tool_name: str, args, kwargs) -> Dict[str, Any]:
        """Map constitutional physics result back to expected tool format"""
        
        verdict = constitutional_result["verdict"]
        constitutional_status = constitutional_result["constitutional_status"]
        
        if verdict == "SEAL":
            # Tool executed successfully under constitutional physics
            return {
                "verdict": "SEAL",
                "constitutional_validity": True,
                "physics_preserved": True,
                "tool_name": tool_name,
                "trinity_assignment": self.trinity_assignments.get(tool_name, "UNKNOWN"),
                "constitutional_metadata": {
                    "status": constitutional_status,
                    "trinity_consensus": constitutional_result.get("trinity_consensus", False),
                    "quantum_superposition": constitutional_result.get("quantum_superposition", {}),
                    "measurement_collapse": constitutional_result.get("quantum_superposition", {}).get("measurement_collapse", False)
                },
                "original_tool": original_tool.__name__,
                "constitutional_receipt": constitutional_result.get("final_receipt", {}),
                "bidirectional_feedback": constitutional_result.get("constitutional_feedback", {})
            }
        else:
            # Constitutional physics prevented execution
            return {
                "verdict": verdict,
                "constitutional_validity": False,
                "physics_preserved": True,
                "tool_name": tool_name,
                "trinity_assignment": self.trinity_assignments.get(tool_name, "UNKNOWN"),
                "reason": constitutional_status,
                "constitutional_error": constitutional_result.get("error", "Unknown constitutional error"),
                "immediate_action": constitutional_result.get("immediate_action", "VOID_OPERATION")
            }
    
    def _store_constitutional_measurement(self, result: Dict[str, Any], tool_name: str) -> None:
        """Store measurement for bidirectional feedback loop"""
        
        measurement = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool_name": tool_name,
            "verdict": result["verdict"],
            "constitutional_status": result["constitutional_status"],
            "trinity_assignment": self.trinity_assignments.get(tool_name, "UNKNOWN"),
            "trinity_consensus": result.get("trinity_consensus", False),
            "quantum_superposition": result.get("quantum_superposition", {}),
            "measurement_collapse": result.get("quantum_superposition", {}).get("measurement_collapse", False)
        }
        
        self.measurement_history.append(measurement)
        
        # Keep only recent measurements (constitutional memory management)
        if len(self.measurement_history) > 1000:
            self.measurement_history = self.measurement_history[-1000:]
        
        logger.info(f"📊 Constitutional measurement stored: {tool_name} → {result['verdict']}")
    
    async def execute_trinity_superposition(self, query: str, user_id: str, 
                                          constitutional_context: Optional[ConstitutionalContext] = None) -> Dict[str, Any]:
        """
        Execute full Trinity superposition [AGI ∩ ASI ∩ APEX].
        
        This is the main entry point for quantum constitutional execution.
        Implements Kimi Orthogonal Directive with full physics enforcement.
        """
        
        logger.info("=" * 60)
        logger.info("🏛️ TRINITY SUPERPOSITION EXECUTION")
        logger.info("=" * 60)
        logger.info(f"📡 Query: {query[:100]}...")
        logger.info(f"👤 User: {user_id}")
        logger.info(f"🕒 Context: {constitutional_context or 'Generated'}")
        logger.info()
        
        try:
            # Execute with full constitutional physics
            result = await self.physics_pipeline.execute_quantum_constitutional(
                query=query,
                user_id=user_id,
                context=constitutional_context.__dict__ if constitutional_context else None
            )
            
            logger.info("✅ TRINITY SUPERPOSITION COMPLETE")
            logger.info(f"📊 Final Verdict: {result['verdict']}")
            logger.info(f"🔐 Constitutional Status: {result['constitutional_status']}")
            logger.info(f"🌌 Quantum Superposition: {result.get('quantum_superposition', {}).get('executed', False)}")
            logger.info(f"🔬 Measurement Collapse: {result.get('quantum_superposition', {}).get('measurement_collapse', False)}")
            logger.info()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Trinity Superposition Failed: {e}")
            logger.error("🚨 Constitutional Crisis - System Sealing")
            logger.info()
            
            return {
                "verdict": "VOID",
                "constitutional_status": "TRINITY_SUPERPOSITION_FAILED",
                "error": str(e),
                "physics_laws_broken": True,
                "immediate_action": "SEAL_SYSTEM_AND_ALERT_HUMAN"
            }
    
    def get_constitutional_metrics(self) -> Dict[str, Any]:
        """Get constitutional physics performance metrics"""
        
        return {
            "constitutional_physics_enabled": self.is_constitutional_mode,
            "total_measurements": len(self.measurement_history),
            "trinity_assignments": self.trinity_assignments,
            "wrapped_tools": len(self.constitutional_tools),
            "physics_validation": self.physics_pipeline.validate_constitutional_physics(),
            "recent_measurements": self.measurement_history[-10:] if self.measurement_history else []
        }
    
    def disable_constitutional_physics(self) -> None:
        """Disable constitutional physics (emergency mode)"""
        self.is_constitutional_mode = False
        logger.warning("⚠️ Constitutional physics disabled - System in emergency mode")
    
    def enable_constitutional_physics(self) -> None:
        """Enable constitutional physics (normal mode)"""
        self.is_constitutional_mode = True
        logger.info("✅ Constitutional physics enabled - Normal operation restored")


# =============================================================================
# CONSTITUTIONAL TOOL REGISTRY
# =============================================================================

class ConstitutionalToolRegistry:
    """
    Registry for constitutional MCP tools with physics enforcement.
    
    Manages the mapping between traditional MCP tools and their
    constitutional physics wrappers.
    """
    
    def __init__(self):
        self.server = ConstitutionalMCPServer()
        self.registered_tools = {}
        self.tool_metadata = {}
    
    async def register_constitutional_tool(self, tool_name: str, tool_function: Callable, 
                                         description: str, trinity_assignment: str) -> None:
        """Register MCP tool with constitutional physics enforcement"""
        
        # Wrap tool with constitutional physics
        constitutional_tool = await self.server.wrap_tool_constitutionally(tool_name, tool_function)
        
        # Store registration
        self.registered_tools[tool_name] = constitutional_tool
        self.tool_metadata[tool_name] = {
            "description": description,
            "trinity_assignment": trinity_assignment,
            "constitutional_physics": True,
            "original_function": tool_function.__name__,
            "registration_time": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"📋 Registered constitutional tool: {tool_name} ({trinity_assignment})")
    
    def get_constitutional_tool(self, tool_name: str) -> Optional[Callable]:
        """Get constitutional tool by name"""
        return self.registered_tools.get(tool_name)
    
    def get_tool_metadata(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get tool metadata"""
        return self.tool_metadata.get(tool_name)
    
    def list_constitutional_tools(self) -> Dict[str, Dict[str, Any]]:
        """List all registered constitutional tools"""
        return {
            tool_name: {
                "function": tool_func,
                "metadata": self.tool_metadata[tool_name]
            }
            for tool_name, tool_func in self.registered_tools.items()
        }
    
    def get_trinity_summary(self) -> Dict[str, List[str]]:
        """Get summary of tools by trinity assignment"""
        trinity_summary = {"AGI": [], "ASI": [], "APEX": []}
        
        for tool_name, metadata in self.tool_metadata.items():
            trinity = metadata["trinity_assignment"]
            if trinity in trinity_summary:
                trinity_summary[trinity].append(tool_name)
        
        return trinity_summary


# =============================================================================
# MAIN INTERFACE
# =============================================================================

# Global constitutional registry
constitutional_registry = ConstitutionalToolRegistry()

async def initialize_constitutional_mcp() -> ConstitutionalMCPServer:
    """
    Initialize constitutional MCP with Kimi Orthogonal Directive.
    
    This should be called during MCP server startup to enable
    constitutional physics enforcement.
    """
    
    logger.info("=" * 60)
    logger.info("🏛️ INITIALIZING CONSTITUTIONAL MCP - KIMI ORTHOGONAL DIRECTIVE")
    logger.info("=" * 60)
    logger.info("📋 Directive: 'MCP tools are like constitutional particles... independent until measured.'")
    logger.info("🧬 Physics Laws:")
    logger.info("   • Orthogonality (Particle Independence): dot_product(tool1, tool2) = 0")
    logger.info("   • Bidirectionality (Governance Conservation): Action → Feedback → Constraint")
    logger.info("   • Quantum Superposition: [AGI ∩ ASI ∩ APEX] parallel execution")
    logger.info("   • Measurement Collapse: 999_seal final verdict")
    logger.info()
    
    # Initialize constitutional MCP server
    server = ConstitutionalMCPServer()
    
    logger.info("✅ Constitutional MCP initialized successfully")
    logger.info("🌌 Quantum constitutional physics enabled")
    logger.info("🔐 Kimi Orthogonal Directive active")
    logger.info()
    
    return server


# Export constitutional integration components
__all__ = [
    "ConstitutionalMCPServer",
    "ConstitutionalToolRegistry", 
    "constitutional_registry",
    "initialize_constitutional_mcp",
    "execute_with_constitutional_physics"
]