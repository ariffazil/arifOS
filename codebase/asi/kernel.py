"""
ASI KERNEL (v53.3.1) - Heart Interface

MCP Interface for ASI Heart Engine (Ω)
Handles: EMPATHY (555) → ALIGN (666)

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .engine import ASIEngine, execute_asi, get_asi_engine, cleanup_expired_sessions
from codebase.bundles import OmegaBundle

logger = logging.getLogger(__name__)


class ASINeuralCore:
    """
    ASI Neural Core (Ω) - Heart Interface
    
    Actions:
        - full: Complete ASI pipeline (555 → 666)
        - empathize: Stage 555 only (stakeholder analysis)
        - align: Stage 666 only (safety checks)
        - audit: Full constitutional audit
    """
    
    def __init__(self):
        self.version = "v53.3.1-TRINITIES"
        self._engines: Dict[str, ASIEngine] = {}
        logger.info(f"ASINeuralCore ignited ({self.version})")
    
    def _get_engine(self, session_id: str) -> ASIEngine:
        if session_id not in self._engines:
            self._engines[session_id] = get_asi_engine(session_id)
        return self._engines[session_id]
    
    async def empathize(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Stage 555: EMPATHY - Analyze stakeholders."""
        context = context or {}
        session_id = context.get("session_id", f"asi_{id(query):x}")
        
        engine = self._get_engine(session_id)
        result = await engine.execute(query, context)
        
        return {
            "stage": "555_empathy",
            "status": "complete" if result.success else "failed",
            "session_id": session_id,
            "trinity_self": {
                "empathy_kappa_r": result.trinity_self.empathy_kappa_r,
                "bias_corrected": result.trinity_self.bias_corrected,
                "is_reversible": result.trinity_self.is_reversible
            },
            "stakeholders": result.stakeholders,
            "weakest": result.weakest_stakeholder,
            "verdict": "SEAL" if result.success else "VOID"
        }
    
    async def align(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Stage 666: ALIGN - Safety and constitutional checks."""
        context = context or {}
        session_id = context.get("session_id", f"asi_{id(query):x}")
        
        engine = self._get_engine(session_id)
        result = await engine.execute(query, context)
        
        return {
            "stage": "666_align",
            "status": "complete" if result.success else "failed",
            "session_id": session_id,
            "trinity_system": {
                "peace_squared": result.trinity_system.peace_squared,
                "audit_trail": result.trinity_system.audit_trail,
                "authority_verified": result.trinity_system.authority_verified
            },
            "trinity_society": {
                "weakest_protected": result.trinity_society.weakest_protected,
                "entropy_delta": result.trinity_society.entropy_delta,
                "earth_witness": result.trinity_society.earth_witness
            },
            "verdict": result.omega_bundle.vote.value if hasattr(result.omega_bundle.vote, 'value') else str(result.omega_bundle.vote)
        }
    
    async def execute(self, action: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Unified execution entry point."""
        query = kwargs.get("query", kwargs.get("text", ""))
        context = kwargs.get("context", {})
        
        if "session_id" not in context:
            context["session_id"] = kwargs.get("session_id", f"asi_{id(query):x}")
        
        if action == "full":
            return await self._execute_full(query, context)
        elif action == "empathize":
            return await self.empathize(query, context)
        elif action == "align":
            return await self.align(query, context)
        elif action == "audit":
            return await self._execute_audit(query, context)
        else:
            return {
                "error": f"Unknown ASI action: {action}",
                "status": "ERROR",
                "available_actions": ["full", "empathize", "align", "audit"]
            }
    
    async def _execute_full(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete ASI pipeline."""
        session_id = context.get("session_id", f"asi_{id(query):x}")
        omega_bundle = await execute_asi(query, session_id, context)
        
        return {
            "stage": "555_666",
            "status": "complete",
            "session_id": session_id,
            "query": query,
            "empathy_kappa_r": omega_bundle.empathy_kappa,
            "is_reversible": omega_bundle.is_reversible,
            "stakeholders": [s.name for s in omega_bundle.stakeholders] if omega_bundle.stakeholders else [],
            "verdict": omega_bundle.vote.value if hasattr(omega_bundle.vote, 'value') else str(omega_bundle.vote)
        }
    
    async def _execute_audit(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute full trinity audit."""
        result = await self._execute_full(query, context)
        engine = self._get_engine(context.get("session_id", "default"))
        
        # Run full execution to get trinities
        asi_result = await engine.execute(query, context)
        
        return {
            "stage": "audit",
            "status": result["status"],
            "trinities": {
                "I_SELF": asi_result.trinity_self.validate()[0],
                "II_SYSTEM": asi_result.trinity_system.validate()[0],
                "III_SOCIETY": asi_result.trinity_society.validate()[0]
            },
            "all_valid": all([
                asi_result.trinity_self.validate()[0],
                asi_result.trinity_system.validate()[0],
                asi_result.trinity_society.validate()[0]
            ])
        }


# Backward compatibility
ASIKernel = ASINeuralCore
ASIActionCore = ASINeuralCore

_core_instance = None

def get_asi_core() -> ASINeuralCore:
    global _core_instance
    if _core_instance is None:
        _core_instance = ASINeuralCore()
    return _core_instance


__all__ = [
    "ASINeuralCore",
    "ASIKernel",
    "ASIActionCore",
    "get_asi_core",
    "cleanup_expired_sessions"
]
