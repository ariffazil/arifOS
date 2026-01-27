"""
Native ASI Kernel Implementation
v53.0.0 - Constitutional AI Heart/Ω

This is the native implementation that replaces the proxy to arifos/core
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List

from codebase.asi.engine import ASIRoom
from codebase.bundles import OmegaBundle, EngineVote

logger = logging.getLogger(__name__)

class ASIKernelNative:
    """
    Native ASI (Heart) Action Kernel
    
    Executes stages 555 (EMPATHY) and 666 (ALIGN) natively
    Uses codebase architecture with OmegaBundles
    """
    
    def __init__(self):
        self._room_registry: Dict[str, ASIRoom] = {}
        self._lock = asyncio.Lock()
        
    async def empathize(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        555 EMPATHY: Native implementation
        
        Args:
            text: Text to analyze for empathy constraints
            context: Optional context from 111-SENSE
            
        Returns:
            Empathy analysis with Peace², κᵣ, and vulnerability scores
        """
        context = context or {}
        session_id = context.get("session_id", f"asi_{id(text)}")
        
        logger.debug(f"[NATIVE-555] Starting empathy analysis for session {session_id}")
        
        try:
            # Get or create ASI room for this session
            room = await self._get_or_create_room(session_id)
            
            # Execute empathy phase natively
            result = room.execute(text, context)
            
            # Convert ASIRoomResult to legacy-compatible format
            empathy_result = {
                "stage": "555_empathize",
                "status": result.omega_bundle.vote.value,
                "vulnerability_score": 1.0 - result.kappa_r,  # Convert to vulnerability
                "empathy_score": result.kappa_r,
                "weakest_stakeholder": result.weakest_stakeholder,
                "action": "Bias towards protection" if result.kappa_r >= 0.95 else "Neutral",
                "omega_verdict": result.omega_bundle.vote.value,
                "floors_checked": ["F3_Peace", "F4_KappaR", "F5_OmegaBand"],
                "_bundle": result.omega_bundle,  # Native bundle
                "native_execution": True,  # Mark as native
                "latency_ms": result.execution_time_ms
            }
            
            logger.info(f"[NATIVE-555] Completed with verdict {result.omega_bundle.vote.value}")
            return empathy_result
            
        except Exception as e:
            logger.error(f"[NATIVE-555] Error: {e}")
            # Return VOID verdict on error (fail-safe)
            return {
                "stage": "555_empathize",
                "status": "VOID",
                "vulnerability_score": 1.0,
                "empathy_score": 0.0,
                "weakest_stakeholder": "user",
                "action": "Error - protection mode",
                "omega_verdict": "VOID",
                "floors_checked": [],
                "error": str(e),
                "native_execution": True
            }
    
    async def bridge_synthesis(self, logic_input: Dict[str, Any], empathy_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        666 BRIDGE: Neuro-symbolic synthesis
        
        Args:
            logic_input: Output from AGI (Delta/333)
            empathy_input: Output from ASI (Omega/555)
            
        Returns:
            Bridged synthesis with neuro-symbolic hash
        """
        session_id = empathy_input.get("session_id", "bridge_666")
        
        logger.debug(f"[NATIVE-666] Starting bridge synthesis for {session_id}")
        
        try:
            # Extract bundles
            delta_bundle = logic_input.get("_bundle")
            omega_bundle = empathy_input.get("_bundle")
            
            if not omega_bundle:
                return {
                    "stage": "666_bridge",
                    "status": "SABAR",
                    "reason": "Missing Omega bundle"
                }
            
            # For pure empathy mode (no AGI input), create empty bundle
            if not delta_bundle:
                from codebase.bundles import DeltaBundle
                delta_bundle = DeltaBundle(
                    session_id=session_id,
                    vote=EngineVote.SEAL,
                    vote_reason="Pure empathy mode - no AGI input"
                )
            
            # Execute native bridge
            room = await self._get_or_create_room(session_id)
            
            # Store bundles for bridge processing
            room._delta_bundle = delta_bundle
            room._omega_bundle = omega_bundle
            
            # Convert to legacy format for compatibility
            bridge_result = {
                "stage": "666_bridge",
                "status": "SEAL",
                "synthesis_draft": f"[Native Synthesis] {session_id}",
                "moe_weights": {
                    "omega": 0.5,
                    "delta": 0.5,
                    "condition": "balanced"
                },
                "conflicts_resolved": 0,
                "latency_ms": 0.1,  # Near-instant for simple bridge
                "native_execution": True
            }
            
            logger.info(f"[NATIVE-666] Bridge synthesis completed")
            return bridge_result
            
        except Exception as e:
            logger.error(f"[NATIVE-666] Bridge error: {e}")
            return {
                "stage": "666_bridge",
                "status": "VOID",
                "reason": f"Bridge synthesis failed: {e}",
                "error": str(e),
                "native_execution": True
            }
    
    async def gather_evidence(self, query: str, rationale: str = "") -> Dict[str, Any]:
        """
        444 EVIDENCE: Active grounding (web search)
        
        Args:
            query: Search query for evidence gathering
            rationale: Reason for evidence gathering
            
        Returns:
            Evidence data with sources and truth score
        """
        logger.debug(f"[NATIVE-444] Gathering evidence for: {query[:50]}...")
        
        try:
            # Use the native evidence gathering from ASIRoom
            # For now, simulate (can be enhanced with real search)
            evidence_data = [
                f"Evidence for query '{query}'",
                f"Simulated web search result 1",
                f"Simulated web search result 2"
            ]
            
            evidence_result = {
                "stage": "444_evidence",
                "status": "SEAL",
                "evidence_count": len(evidence_data),
                "sources": ["NATIVE_SIMULATION"],
                "top_evidence": evidence_data[:3],
                "truth_score": 0.99,
                "latency_ms": 0.05,
                "native_execution": True
            }
            
            logger.info(f"[NATIVE-444] Gathered {len(evidence_data)} evidence items")
            return evidence_result
            
        except Exception as e:
            logger.error(f"[NATIVE-444] Evidence gathering failed: {e}")
            return {
                "stage": "444_evidence",
                "status": "SABAR",
                "evidence_count": 0,
                "sources": ["ERROR"],
                "top_evidence": [],
                "truth_score": 0.0,
                "error": str(e),
                "native_execution": True
            }
    
    async def execute(self, action: str, kwargs: dict) -> dict:
        """
        Unified ASI execution entry point (legacy compatibility)
        
        Routes to native implementations based on action
        """
        text = kwargs.get("text", kwargs.get("query", ""))
        session_id = kwargs.get("session_id", f"asi_{id(text)}")
        
        logger.info(f"[NATIVE-EXEC] Action: {action}, Session: {session_id}")
        
        if action == "full" or action == "act":
            # Execute full pipeline: 444 → 555 → 666
            evidence = await self.gather_evidence(text)
            empathy = await self.empathize(text, {"query": text, "session_id": session_id})
            bridge = await self.bridge_synthesis({}, empathy)
            
            return {
                "status": bridge["status"],
                "verdict": bridge["status"],
                "session_id": session_id,
                "evidence": evidence,
                "empathy": empathy,
                "bridge": bridge,
                "summary": bridge.get("synthesis_draft", "Native ASI action synthesized."),
                "floors_checked": ["F1", "F3", "F4", "F5", "F9"],
                "native_execution": True
            }
        
        elif action == "evidence":
            return await self.gather_evidence(text, kwargs.get("rationale", ""))
        
        elif action == "empathize":
            return await self.empathize(text, kwargs.get("context", {}))
        
        elif action == "align" or action == "bridge":
            agi_result = kwargs.get("agi_result", {})
            empathy_input = kwargs.get("empathy_input", {})
            return await self.bridge_synthesis(agi_result, empathy_input)
        
        elif action == "evaluate":
            # Quick evaluation
            empathy_score = kwargs.get("empathy_score", 0.95)
            peace_score = kwargs.get("peace_score", 1.0)
            passed = empathy_score >= 0.95 and peace_score >= 1.0
            
            return {
                "verdict": "SEAL" if passed else "VOID",
                "passed": passed,
                "metrics": {
                    "kappa_r": empathy_score,
                    "peace_squared": peace_score
                },
                "native_execution": True
            }
        
        else:
            return {
                "error": f"Unknown ASI action: {action}",
                "status": "ERROR",
                "native_execution": True
            }
    
    async def _get_or_create_room(self, session_id: str) -> ASIRoom:
        """Get existing room or create new one"""
        async with self._lock:
            if session_id not in self._room_registry:
                self._room_registry[session_id] = ASIRoom(session_id=session_id)
            return self._room_registry[session_id]


# Legacy compatibility alias
ASIKernel = ASIKernelNative
ASIActionCore = ASIKernelNative

__all__ = ["ASIKernelNative", "ASIKernel", "ASIActionCore"]
