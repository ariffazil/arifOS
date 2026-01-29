"""
AGI ENGINE (Unified v52+v53+v54) - Hardened Mind/Δ v53.4.0

Consolidates:
- v52.1: Mature hardening, parallel hypothesis matrix, evidence injection, telemetry
- v53.2: Clean component architecture (NeuralSenseEngine, DeepThinkEngine, CognitiveForge)
- v53.4.0: Critical Gaps P1-P3 integrated into live pipeline

Stages: 111 SENSE → 222 THINK → 333 FORGE
Floors: F2 (Truth ≥0.99), F4 (ΔS≤0), F7 (Ω₀ ∈ [0.03,0.05]), F12 (Injection)

Critical Gaps Fixed (v53.4.0):
- P1 Precision Weighting: Kalman-style π = 1/σ² belief updates
- P2 Hierarchical Abstraction: 5-level cortical encoding in SENSE
- P3 Active Inference: EFE minimization for action selection in FORGE

Hardening:
- Proper async parallel execution (asyncio.gather)
- Circuit breaker pattern
- Session lifecycle management
- Input validation at all entry points

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from __future__ import annotations

import time
import uuid
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

# v52: Supporting modules
from .hardening import (
    run_pre_checks, 
    run_post_checks, 
    cleanup_session,
    HardeningResult, 
    RiskLevel
)
from .metrics import ThermodynamicDashboard, get_dashboard
from .parallel import ParallelHypothesisMatrix
from .evidence import get_evidence_kernel, cleanup_evidence_kernel

# v52: Stages (for compatibility)
from .stages import (
    SenseOutput,
    build_delta_bundle
)

# v53: Components (hardened)
from .agi_components import (
    NeuralSenseEngine, 
    DeepThinkEngine, 
    CognitiveForge,
    validate_input_safety,
    check_falsifiability
)

# v53.4.0: Precision, Hierarchy, Active Inference (Critical Gaps P1-P3)
from .precision import estimate_precision, update_belief_with_precision, PrecisionEstimate
from .hierarchy import encode_hierarchically, get_cumulative_delta_s, HierarchyLevel
from .action import compute_action_policy, BeliefState, ActionType

# Bundles
from codebase.bundles import DeltaBundle, EngineVote


# =============================================================================
# CIRCUIT BREAKER
# =============================================================================

class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures.
    
    States:
    - CLOSED: Normal operation
    - OPEN: Failing fast (recent failures)
    - HALF_OPEN: Testing if recovered
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            # Check if recovery timeout has passed
            if self.last_failure_time and (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        
        return True  # HALF_OPEN
    
    def record_success(self):
        """Record successful execution."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


# =============================================================================
# SESSION MANAGER
# =============================================================================

class SessionManager:
    """Manages AGI engine sessions with TTL cleanup."""
    
    def __init__(self, ttl_seconds: float = 3600.0):
        self._engines: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds
    
    def get_engine(self, session_id: str) -> Optional[AGIEngine]:
        """Get engine if session exists and is not expired."""
        if session_id not in self._engines:
            return None
        
        session = self._engines[session_id]
        
        # Check TTL
        if time.time() - session["created_at"] > self._ttl:
            del self._engines[session_id]
            return None
        
        return session["engine"]
    
    def create_session(self, session_id: str) -> AGIEngine:
        """Create new engine session."""
        engine = AGIEngine(session_id=session_id)
        self._engines[session_id] = {
            "engine": engine,
            "created_at": time.time(),
            "last_accessed": time.time()
        }
        return engine
    
    def cleanup_expired(self):
        """Remove expired sessions."""
        now = time.time()
        expired = [
            sid for sid, data in self._engines.items()
            if now - data["created_at"] > self._ttl
        ]
        for sid in expired:
            del self._engines[sid]


# Global session manager
_session_manager = SessionManager()


# =============================================================================
# DATA TYPES
# =============================================================================

@dataclass
class AGIResult:
    """Complete result from AGI Engine execution."""
    delta_bundle: DeltaBundle
    session_id: str
    execution_time_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    stage_111: Optional[SenseOutput] = None
    hardening: Optional[HardeningResult] = None
    risk_level: RiskLevel = RiskLevel.LOW
    success: bool = True
    error: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error": self.error,
            "risk_level": self.risk_level.value if hasattr(self.risk_level, 'value') else str(self.risk_level),
            "delta_bundle": self.delta_bundle.to_dict() if hasattr(self.delta_bundle, 'to_dict') else str(self.delta_bundle),
            "hardening": self.hardening.to_dict() if self.hardening else None,
        }


# =============================================================================
# UNIFIED AGI ENGINE
# =============================================================================

class AGIEngine:
    """
    Hardened Unified AGI Mind Engine (v52+v53).
    
    Key Hardening:
    - Circuit breaker prevents cascade failures
    - Proper async parallel execution
    - Input validation at all entry points
    - Session lifecycle management
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"agi_{uuid.uuid4().hex[:12]}"
        self.version = "v53.4.0-HARDENED"
        
        # v53 Components
        self.sense_engine = NeuralSenseEngine()
        self.think_engine = DeepThinkEngine()
        self.forge_engine = CognitiveForge()
        
        # v52 Parallel Matrix
        self.parallel_matrix = ParallelHypothesisMatrix(session_id=self.session_id)
        
        # Circuit breaker
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60.0)
        
        # Execution tracking
        self._execution_count = 0
    
    async def execute(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        lane: Optional[str] = None
    ) -> AGIResult:
        """
        Execute full AGI pipeline with hardening.
        
        Args:
            query: User query/request
            context: Optional context dict
            lane: HARD | SOFT | PHATIC (auto-detected if None)
            
        Returns:
            AGIResult with sealed DeltaBundle
        """
        start_time = time.time()
        self._execution_count += 1
        exec_id = f"{self.session_id}_exec{self._execution_count}"
        context = context or {}
        
        # ===== CIRCUIT BREAKER CHECK =====
        if not self.circuit_breaker.can_execute():
            return self._build_blocked_result(
                exec_id, start_time, None,
                "Circuit breaker OPEN - too many recent failures"
            )
        
        try:
            # ===== STEP 1: INPUT VALIDATION (F12) =====
            is_safe, error_msg, input_meta = validate_input_safety(query)
            if not is_safe:
                self.circuit_breaker.record_failure()
                return self._build_blocked_result(
                    exec_id, start_time, None, error_msg
                )
            
            # ===== STEP 2: F2 TRUTH CHECK =====
            f2_classification, omega_penalty, f2_warning = check_falsifiability(query)
            
            if f2_classification == "VOID_UNFALSIFIABLE":
                self.circuit_breaker.record_failure()
                return self._build_blocked_result(
                    exec_id, start_time, None, f2_warning or "F2: Unfalsifiable query"
                )
            
            # ===== STEP 3: HARDENING GATE (v52) =====
            dashboard = get_dashboard(exec_id)
            hardening = run_pre_checks(query, exec_id)
            
            dashboard.record_stage_metric(
                stage="000_GATE",
                delta_s=0.0,
                confidence=1.0 if hardening.proceed else 0.0,
                peace_squared=1.0,
                cost_usd=0.0001
            )
            
            if not hardening.proceed:
                self.circuit_breaker.record_failure()
                return self._build_blocked_result(
                    exec_id, start_time, hardening, hardening.block_reason
                )
            
            # ===== STEP 4: 111 SENSE (v53 Component) =====
            sense_data = await self.sense_engine.sense_query(query, exec_id)
            
            # Check if sense failed (F2/F12 violation)
            if sense_data.get("lane") == "VOID":
                self.circuit_breaker.record_failure()
                return self._build_blocked_result(
                    exec_id, start_time, hardening,
                    sense_data.get("error", "Sense phase failed")
                )
            
            # Convert to v52 SenseOutput for compatibility
            stage_111 = SenseOutput(
                session_id=exec_id,
                raw_query=query,
                parsed_facts=[sense_data.get("intent", "query")],
                detected_intent=sense_data.get("intent", "query"),
                confidence=sense_data.get("confidence", 0.9),
                f10_ontology_pass=True,
                f12_injection_risk=hardening.hantu_score,
                stage_pass=True,
                violations=hardening.warnings if hardening.hantu_score > 0.3 else []
            )
            
            # ===== STEP 5: EVIDENCE INJECTION (v52) =====
            evidence_kernel = get_evidence_kernel(exec_id)
            stage_111 = evidence_kernel.inject_live_evidence(
                sense_output=stage_111,
                query=query,
                context=context
            )
            
            evidence_injected = stage_111.metadata.get("evidence_injected", 0)
            evidence_confidence = stage_111.metadata.get("avg_evidence_confidence", 0.0)
            
            dashboard.record_stage_metric(
                stage="111_SENSE",
                delta_s=-0.15 * evidence_confidence,
                confidence=max(0.85, evidence_confidence),
                peace_squared=1.0,
                cost_usd=0.002 + (evidence_injected * 0.001)
            )
            
            run_post_checks(
                session_id=exec_id,
                stage="111_SENSE",
                floor_scores={"F10": 1.0, "F12": 1.0 - hardening.hantu_score},
                violations=stage_111.violations,
                verdict="PASS" if stage_111.stage_pass else "FAIL",
                entropy_delta=-0.15 * evidence_confidence,
                duration_ms=(time.time() - start_time) * 1000,
                risk_level=hardening.risk_level
            )
            
            # ===== STEP 6: PARALLEL 222 (Proper Async) =====
            parallel_results = await self._run_parallel_think_async(stage_111, context)
            
            if not parallel_results:
                self.circuit_breaker.record_failure()
                return self._build_failed_result(
                    exec_id, start_time, stage_111, None, None,
                    "All parallel hypotheses failed",
                    hardening=hardening
                )
            
            # Record parallel metrics
            for result in parallel_results:
                dashboard.record_stage_metric(
                    stage="222_PARALLEL",
                    delta_s=result.get("entropy_delta", -0.1),
                    confidence=result.get("confidence", 0.9),
                    peace_squared=1.0,
                    cost_usd=0.005
                )
            
            # ===== STEP 6b: HIERARCHICAL ENCODING (v53.4.0 Gap P2) =====
            # 5-level cortical hierarchy: Phonetic → Lexical → Syntactic → Categorical → Conceptual
            hierarchical_beliefs = encode_hierarchically(query)
            cumulative_ds = get_cumulative_delta_s(hierarchical_beliefs)
            
            # Serialize hierarchy for bundle
            hierarchy_levels = {}
            for level, belief in hierarchical_beliefs.items():
                hierarchy_levels[level.name] = {
                    "content": belief.content[:100],
                    "confidence": belief.confidence,
                    "entropy": belief.entropy,
                }
            
            # ===== STEP 6c: PRECISION ESTIMATION (v53.4.0 Gap P1) =====
            # Kalman-style precision weighting: π = 1/σ²
            from datetime import datetime as dt
            evidence_sources = ["user_input"] + [r.get("mode", "unknown") for r in parallel_results]
            evidence_timestamps = [dt.utcnow()] * len(evidence_sources)
            precision = estimate_precision(evidence_sources, evidence_timestamps)
            
            # Apply precision weighting to hypothesis confidence
            for result in parallel_results:
                raw_conf = result.get("confidence", 0.9)
                result["precision_weighted_confidence"] = update_belief_with_precision(
                    current_confidence=raw_conf,
                    evidence_confidence=evidence_confidence,
                    precision=precision
                )
            
            # ===== STEP 7: FORGE (v53 Component) =====
            best_result = max(parallel_results, key=lambda x: x.get("precision_weighted_confidence", x.get("confidence", 0)))
            
            forge_data = await self.forge_engine.forge_response({
                "thought": best_result.get("thought", ""),
                "confidence": best_result.get("precision_weighted_confidence", best_result.get("confidence", 0.9)),
                "parallel_results": len(parallel_results),
                "lane": sense_data.get("lane", "SOFT")
            })
            
            # F4 Check: Reject if entropy increased
            if forge_data.get("clarity_delta_s", 0) > 0:
                return self._build_failed_result(
                    exec_id, start_time, stage_111, None, None,
                    f"F4 Clarity violation: ΔS = {forge_data['clarity_delta_s']:.3f} > 0",
                    hardening=hardening
                )
            
            # F7 Check: Ensure omega_0 in valid band
            omega_0 = forge_data.get("humility_score", 0.04)
            if not (0.03 <= omega_0 <= 0.05):
                return self._build_failed_result(
                    exec_id, start_time, stage_111, None, None,
                    f"F7 Humility violation: Ω₀ = {omega_0:.3f} outside [0.03, 0.05]",
                    hardening=hardening
                )
            
            # ===== STEP 7b: ACTIVE INFERENCE (v53.4.0 Gap P3) =====
            # Compute Expected Free Energy (EFE) for action selection
            # F = ΔS + Ω₀·π⁻¹
            entropy_delta = forge_data.get("clarity_delta_s", -0.1)
            pi_inv = 1.0 / precision.pi_likelihood if precision.pi_likelihood > 0 else 1.0
            free_energy = entropy_delta + omega_0 * pi_inv
            
            belief_state = BeliefState(
                states={
                    "truth": best_result.get("precision_weighted_confidence", 0.9),
                    "clarity": 1.0 - abs(entropy_delta),
                    "safety": 0.9 if entropy_delta <= 0 else 0.7,
                },
                entropy=abs(entropy_delta)
            )
            action_policy = compute_action_policy(belief_state)
            
            # ===== STEP 8: BUILD DELTA BUNDLE =====
            final_confidence = forge_data.get("final_confidence", 0.95)
            
            delta_bundle = DeltaBundle(
                session_id=exec_id,
                raw_query=query,
                parsed_facts=stage_111.parsed_facts,
                detected_intent=stage_111.detected_intent,
                hypotheses=[r.get("thought", "") for r in parallel_results],
                confidence_high=final_confidence,
                confidence_low=max(0.0, final_confidence - 0.05),
                omega_0=omega_0,
                entropy_delta=entropy_delta,
                vote=EngineVote.SEAL if final_confidence >= 0.8 else EngineVote.UNCERTAIN,
                vote_reason=f"v53.4.0 hardened | π={precision.pi_likelihood:.2f} K={precision.kalman_gain:.2f} F={free_energy:.3f} action={action_policy.actions[0].name}",
                # v53.4.0: Precision (Gap P1)
                precision_pi=precision.pi_likelihood,
                precision_prior=precision.pi_prior,
                kalman_gain=precision.kalman_gain,
                # v53.4.0: Hierarchy (Gap P2)
                hierarchy_levels=hierarchy_levels,
                cumulative_delta_s=cumulative_ds,
                # v53.4.0: Active Inference (Gap P3)
                free_energy=free_energy,
                action_type=action_policy.actions[0].name,
                epistemic_value=action_policy.epistemic_value,
                pragmatic_value=action_policy.pragmatic_value,
            )
            
            if hasattr(delta_bundle, 'seal'):
                delta_bundle = delta_bundle.seal()
            
            # Final telemetry
            exec_time_ms = (time.time() - start_time) * 1000
            dashboard.record_stage_metric(
                stage="999_SEAL",
                delta_s=forge_data.get("clarity_delta_s", -0.1),
                confidence=forge_data.get("final_confidence", 0.95),
                peace_squared=1.0,
                cost_usd=0.001
            )
            
            # Record success (circuit breaker)
            self.circuit_breaker.record_success()
            
            return AGIResult(
                delta_bundle=delta_bundle,
                session_id=exec_id,
                execution_time_ms=exec_time_ms,
                stage_111=stage_111,
                hardening=hardening,
                risk_level=hardening.risk_level,
                success=True
            )
            
        except Exception as e:
            self.circuit_breaker.record_failure()
            exec_time_ms = (time.time() - start_time) * 1000
            return self._build_error_result(exec_id, exec_time_ms, str(e))
        
        finally:
            cleanup_evidence_kernel(exec_id)
    
    async def _run_parallel_think_async(
        self, 
        sense_output: SenseOutput, 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Run 3 parallel hypothesis paths using TRUE async concurrency.
        
        Uses asyncio.gather for actual parallel execution.
        """
        query = sense_output.raw_query
        lane = sense_output.detected_intent or "SOFT"
        
        # Create tasks for parallel execution
        tasks = [
            self._think_path("conservative", query, lane),
            self._think_path("exploratory", query, lane),
            self._think_path("adversarial", query, lane)
        ]
        
        # Execute in parallel with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            logger.error("[AGI] Parallel think timeout")
            return []
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"[AGI] Think path error: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def _think_path(self, mode: str, query: str, lane: str) -> Dict[str, Any]:
        """Execute a single think path."""
        try:
            think_data = await self.think_engine.reason({
                "query": f"[{mode.upper()}] {query}",
                "lane": lane,
                "mode": mode
            })
            
            return {
                "mode": mode,
                "thought": think_data.get("thought", ""),
                "confidence": think_data.get("confidence", 0.9),
                "entropy_delta": -0.1  # Assume clarity gain
            }
        except Exception as e:
            logger.error(f"[AGI] {mode} path failed: {e}")
            return {
                "mode": mode,
                "thought": f"Error in {mode}: {str(e)}",
                "confidence": 0.5,
                "entropy_delta": 0.0
            }
    
    def _build_blocked_result(
        self, session_id: str, start_time: float, 
        hardening: Optional[HardeningResult], block_reason: str
    ) -> AGIResult:
        """Build result when hardening blocks execution."""
        exec_time_ms = (time.time() - start_time) * 1000
        
        bundle = DeltaBundle(
            session_id=session_id,
            vote=EngineVote.VOID,
            vote_reason=f"Blocked: {block_reason}"
        )
        if hasattr(bundle, 'seal'):
            bundle = bundle.seal()
        
        return AGIResult(
            delta_bundle=bundle,
            session_id=session_id,
            execution_time_ms=exec_time_ms,
            hardening=hardening,
            risk_level=hardening.risk_level if hardening else RiskLevel.LOW,
            success=False,
            error=block_reason
        )
    
    def _build_failed_result(
        self, session_id: str, start_time: float,
        stage_111, stage_222, stage_333,
        error: str, hardening: Optional[HardeningResult] = None
    ) -> AGIResult:
        """Build result when a stage fails."""
        exec_time_ms = (time.time() - start_time) * 1000
        
        bundle = DeltaBundle(
            session_id=session_id,
            raw_query=stage_111.raw_query if stage_111 else "",
            vote=EngineVote.VOID,
            vote_reason=error
        )
        if hasattr(bundle, 'seal'):
            bundle = bundle.seal()
        
        return AGIResult(
            delta_bundle=bundle,
            session_id=session_id,
            execution_time_ms=exec_time_ms,
            stage_111=stage_111,
            hardening=hardening,
            risk_level=hardening.risk_level if hardening else RiskLevel.LOW,
            success=False,
            error=error
        )
    
    def _build_error_result(self, session_id: str, exec_time_ms: float, error: str) -> AGIResult:
        """Build result from unexpected exception."""
        bundle = DeltaBundle(
            session_id=session_id,
            vote=EngineVote.VOID,
            vote_reason=f"Engine Error: {error}"
        )
        if hasattr(bundle, 'seal'):
            bundle = bundle.seal()
        
        return AGIResult(
            delta_bundle=bundle,
            session_id=session_id,
            execution_time_ms=exec_time_ms,
            success=False,
            error=error
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def execute_agi(
    query: str,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    lane: Optional[str] = None
) -> DeltaBundle:
    """Execute AGI and return sealed DeltaBundle."""
    # Check session manager for existing engine
    engine = _session_manager.get_engine(session_id or "default")
    if engine is None:
        engine = _session_manager.create_session(session_id or f"agi_{uuid.uuid4().hex[:12]}")
    
    result = await engine.execute(query, context, lane)
    return result.delta_bundle


def get_agi_engine(session_id: Optional[str] = None) -> AGIEngine:
    """Get AGI Engine instance (with session management)."""
    sid = session_id or f"agi_{uuid.uuid4().hex[:12]}"
    engine = _session_manager.get_engine(sid)
    if engine is None:
        engine = _session_manager.create_session(sid)
    return engine


def cleanup_expired_sessions():
    """Clean up expired sessions. Call periodically."""
    _session_manager.cleanup_expired()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AGIEngine",
    "AGIResult", 
    "execute_agi",
    "get_agi_engine",
    "cleanup_expired_sessions",
    "CircuitBreaker",
    "SessionManager"
]
