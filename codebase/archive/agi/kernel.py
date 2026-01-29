"""
AGI KERNEL (Unified v53.3.0) - Neural Core

The kernel interface between MCP tools and the AGI Engine.
Handles: SENSE (111) → THINK (222) → FORGE (333)

Floors: F2 (Truth), F4 (Clarity), F7 (Humility), F10 (Ontology), F12 (Injection)

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

# Unified Engine
from .engine import AGIEngine, execute_agi, get_agi_engine, cleanup_expired_sessions
from codebase.bundles import DeltaBundle

logger = logging.getLogger(__name__)


class AGINeuralCore:
    """
    AGI Neural Core (Δ) - Unified Kernel Interface.
    
    This is the main interface used by MCP tools (_agi_, _trinity_, etc.).
    It wraps the AGIEngine with a simplified action-based API.
    
    Actions:
        - full: Complete pipeline (111 → 222 → 333)
        - sense: Stage 111 only (parse input)
        - think: Stage 222 only (generate hypotheses)
        - forge: Stage 333 only (converge & output)
        - reflect: Meta-cognition check
        - physics: Rule-checking mode
    """
    
    def __init__(self):
        self.version = "v53.3.0-UNIFIED"
        self._engines: Dict[str, AGIEngine] = {}  # Session cache
        logger.info(f"AGINeuralCore ignited ({self.version})")
    
    def _get_engine(self, session_id: str) -> AGIEngine:
        """Get or create engine for session."""
        if session_id not in self._engines:
            self._engines[session_id] = AGIEngine(session_id=session_id)
        return self._engines[session_id]
    
    async def sense(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Stage 111: SENSE - Parse input, detect intent, check floors.
        
        Floors: F12 (Injection), F10 (Ontology)
        """
        context = context or {}
        session_id = context.get("session_id", f"agi_{id(query):x}")
        
        engine = self._get_engine(session_id)
        
        # Run full pipeline but return early sense data
        result = await engine.execute(query, context)
        
        return {
            "stage": "111_sense",
            "status": "complete" if result.success else "failed",
            "session_id": session_id,
            "query": query,
            "intent": result.stage_111.detected_intent if result.stage_111 else "unknown",
            "confidence": result.stage_111.confidence if result.stage_111 else 0.0,
            "f12_injection_risk": result.hardening.hantu_score if result.hardening else 0.0,
            "risk_level": result.risk_level.value if result.hardening else "unknown",
            "verdict": "SEAL" if result.success else "VOID"
        }
    
    async def think(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Stage 222: THINK - Generate reasoning tree.
        
        Floors: F2 (Truth), F4 (Clarity)
        """
        context = context or {}
        session_id = context.get("session_id", f"agi_{id(query):x}")
        
        engine = self._get_engine(session_id)
        result = await engine.execute(query, context)
        
        bundle = result.delta_bundle
        
        return {
            "stage": "222_think",
            "status": "complete" if result.success else "failed",
            "session_id": session_id,
            "thought": bundle.reasoning.conclusion if bundle.reasoning else "No reasoning",
            "confidence": bundle.confidence_high,
            "delta_s": bundle.entropy_delta,
            "hypotheses": bundle.hypotheses if hasattr(bundle, 'hypotheses') else [],
            "verdict": bundle.vote.value if hasattr(bundle.vote, 'value') else str(bundle.vote)
        }
    
    async def forge(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Stage 333/FORGE: Converge reasoning into final output.
        
        Floors: F7 (Humility)
        """
        context = context or {}
        session_id = context.get("session_id", f"agi_{id(query):x}")
        
        engine = self._get_engine(session_id)
        result = await engine.execute(query, context)
        
        bundle = result.delta_bundle
        
        return {
            "stage": "333_forge",
            "status": "complete" if result.success else "failed",
            "session_id": session_id,
            "insight": bundle.reasoning.conclusion if bundle.reasoning else "Analysis complete",
            "draft": bundle.reasoning.conclusion if bundle.reasoning else "No output",
            "confidence": bundle.confidence_high,
            "omega_0": bundle.omega_0,
            "delta_s": bundle.entropy_delta,
            "verdict": bundle.vote.value if hasattr(bundle.vote, 'value') else str(bundle.vote),
            "vote_reason": bundle.vote_reason
        }
    
    async def reflect(self, thought: str, query: str) -> Dict[str, Any]:
        """
        Meta-cognition: Check reasoning for contradictions.
        
        Floor: F7 (Humility - self-correction)
        """
        # Simple reflection - check for self-reference paradoxes
        contradictions = []
        
        if "I am" in thought and "not" in thought:
            contradictions.append("Potential self-reference paradox")
        
        if len(thought) < 10:
            contradictions.append("Reasoning too brief")
        
        return {
            "stage": "reflect",
            "status": "SEAL",
            "thought": thought,
            "contradictions": contradictions,
            "needs_rethink": len(contradictions) > 0
        }
    
    async def physics(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Physics mode: Apply thermodynamic constraints.
        
        Floor: F4 (ΔS ≤ 0)
        
        FIXED: Calls execute_agi directly to avoid infinite recursion.
        """
        context = context or {}
        session_id = context.get("session_id", f"agi_{id(query):x}")
        
        # Call engine directly - NOT self.execute() to avoid recursion
        delta_bundle = await execute_agi(query, session_id, context)
        delta_s = delta_bundle.entropy_delta if hasattr(delta_bundle, 'entropy_delta') else 0
        
        if delta_s > 0:
            return {
                "stage": "physics",
                "status": "VOID",
                "reason": f"Entropy increase detected: ΔS = {delta_s:.3f}",
                "floor_violated": "F4_Clarity"
            }
        
        return {
            "stage": "physics",
            "status": "SEAL",
            "delta_s": delta_s,
            "entropy_reduced": True
        }
    
    async def execute(self, action: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unified execution entry point.
        
        Routes to appropriate method based on action.
        """
        query = kwargs.get("query", kwargs.get("text", ""))
        context = kwargs.get("context", {})
        
        # Ensure session_id in context
        if "session_id" not in context:
            context["session_id"] = kwargs.get("session_id", f"agi_{id(query):x}")
        
        # Route to appropriate handler
        if action == "full":
            return await self._execute_full(query, context)
        elif action == "sense":
            return await self.sense(query, context)
        elif action == "think":
            return await self.think(query, context)
        elif action == "forge":
            return await self.forge(query, context)
        elif action == "reflect":
            return await self.reflect(kwargs.get("thought", ""), query)
        elif action == "physics":
            return await self.physics(query, context)
        elif action == "atlas":
            # Knowledge mapping - runs full then extracts map
            return await self._execute_atlas(query, context)
        elif action == "reason":
            # Step-by-step reasoning
            return await self._execute_reason(query, context)
        else:
            return {
                "error": f"Unknown AGI action: {action}",
                "status": "ERROR",
                "available_actions": ["full", "sense", "think", "forge", "reflect", "physics", "atlas", "reason"]
            }
    
    async def _execute_full(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete pipeline and return unified result."""
        session_id = context.get("session_id", f"agi_{id(query):x}")
        
        # Use the unified engine
        delta_bundle = await execute_agi(query, session_id, context)
        
        return {
            "stage": "111_222_333",
            "status": "complete",
            "session_id": session_id,
            "query": query,
            "insight": delta_bundle.reasoning.conclusion if delta_bundle.reasoning else "Analysis complete",
            "rationale": delta_bundle.vote_reason,
            "truth_score": delta_bundle.confidence_high,
            "clarity_delta": delta_bundle.entropy_delta,
            "omega_0": delta_bundle.omega_0,
            "verdict": delta_bundle.vote.value if hasattr(delta_bundle.vote, 'value') else str(delta_bundle.vote),
            "_bundle": delta_bundle
        }
    
    async def _execute_atlas(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute and return knowledge map."""
        result = await self._execute_full(query, context)
        bundle = result.get("_bundle")
        
        return {
            "stage": "atlas",
            "status": result["status"],
            "knowledge_map": {
                "query": query,
                "intent": bundle.detected_intent if hasattr(bundle, 'detected_intent') else "unknown",
                "hypotheses": bundle.hypotheses if hasattr(bundle, 'hypotheses') else [],
                "confidence_range": [bundle.confidence_low, bundle.confidence_high] if hasattr(bundle, 'confidence_low') else [0, result.get("truth_score", 0)],
                "boundaries": ["Observable facts", "Inferred conclusions"]
            },
            "uncertainty": result.get("omega_0", 0.04)
        }
    
    async def _execute_reason(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with step-by-step reasoning output."""
        result = await self._execute_full(query, context)
        bundle = result.get("_bundle")
        
        return {
            "stage": "reason",
            "status": result["status"],
            "reasoning": bundle.reasoning.inference_steps if bundle.reasoning and hasattr(bundle.reasoning, 'inference_steps') else ["Analysis complete"],
            "conclusion": result.get("insight", "No conclusion"),
            "confidence": result.get("truth_score", 0),
            "verdict": result.get("verdict", "VOID")
        }


# Backward compatibility
AGIKernel = AGINeuralCore

# Singleton instance
_core_instance: Optional[AGINeuralCore] = None


def get_agi_core() -> AGINeuralCore:
    """Get singleton AGI Neural Core instance."""
    global _core_instance
    if _core_instance is None:
        _core_instance = AGINeuralCore()
    return _core_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AGINeuralCore",
    "AGIKernel",
    "get_agi_core",
    "cleanup_expired_sessions"
]
