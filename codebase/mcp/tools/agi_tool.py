"""
AGI Tool - Mind Engine (Δ) MCP Interface
v52.6.0 - Exposes upgraded AGI capabilities: metrics, evidence, parallel

This tool wraps the codebase AGIRoom with MCP-compatible interface.
"""

from typing import Any, Dict, Optional
from codebase.agi import AGIRoom, execute_agi_room
from codebase.agi.metrics import get_dashboard
from codebase.agi.evidence import get_evidence_kernel
from codebase.agi.parallel import ParallelHypothesisMatrix


class AGITool:
    """
    Mind Engine: SENSE → THINK → REASON → (upgraded v52.6.0)
    
    Actions:
    - "full": Execute complete AGI pipeline with all upgrades
    - "metrics": Get thermodynamic dashboard for session
    - "evidence": Get evidence injection summary
    - "parallel": Execute parallel hypothesis generation
    """
    
    @staticmethod
    def execute(action: str, query: str, session_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Execute AGI action via MCP interface"""
        
        if action == "full":
            return AGITool._execute_full(query, session_id, **kwargs)
        elif action == "metrics":
            return AGITool._get_metrics(session_id, **kwargs)
        elif action == "evidence":
            return AGITool._get_evidence(session_id, **kwargs)
        elif action == "parallel":
            return AGITool._execute_parallel(query, session_id, **kwargs)
        else:
            return {"verdict": "VOID", "reason": f"Unknown action: {action}"}
    
    @staticmethod
    def _execute_full(query: str, session_id: Optional[str], **kwargs) -> Dict[str, Any]:
        """Execute complete AGI pipeline with all v52.6.0 upgrades"""
        
        # Execute AGI room (includes all 3 upgrades automatically)
        result = execute_agi_room(query, session_id)
        
        return {
            "verdict": result.vote.value,
            "reasoning": result.reasoning.conclusion if result.reasoning else "",
            "confidence": {
                "low": result.confidence_low,
                "high": result.confidence_high,
                "omega_0": result.omega_0
            },
            "entropy_delta": result.entropy_delta,
            "dashboard": result.dashboard,  # v52.6.0: Includes all metrics
            "session_id": result.session_id,
            "evidence_injected": result.metadata.get("evidence_injected", 0) if hasattr(result, 'metadata') else 0
        }
    
    @staticmethod
    def _get_metrics(session_id: str, **kwargs) -> Dict[str, Any]:
        """Get thermodynamic dashboard metrics for session"""
        
        dashboard = get_dashboard(session_id)
        return dashboard.generate_report()
    
    @staticmethod
    def _get_evidence(session_id: str, **kwargs) -> Dict[str, Any]:
        """Get evidence injection summary for session"""
        
        kernel = get_evidence_kernel(session_id)
        return kernel.get_evidence_summary()
    
    @staticmethod
    def _execute_parallel(query: str, session_id: Optional[str], **kwargs) -> Dict[str, Any]:
        """Execute parallel hypothesis generation only"""
        
        # This would integrate with parallel matrix
        # For now, call full execution and extract parallel info
        result = execute_agi_room(query, session_id)
        
        # Extract parallel info from dashboard if available
        dashboard = result.dashboard if hasattr(result, 'dashboard') else {}
        
        return {
            "verdict": result.vote.value,
            "parallel_info": dashboard.get("convergence_stats", {}),
            "hypotheses_explored": dashboard.get("convergence_stats", {}).get("hypotheses_explored", 0),
            "query": query
        }
