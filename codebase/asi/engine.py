"""
ASI ENGINE (Unified v52+v53) - Hardened Heart/Ω v53.3.1

The Heart Engine: Empathy, Safety, and Care
Stages: 555 EMPATHY → 666 ALIGN

3 TRINITIES ARCHITECTURE (9 Elements):
├── TRINITY I: SELF (Inner Reflection)
│   ├── Element 1: Empathy Flow (κᵣ ≥ 0.95)
│   ├── Element 2: Bias Mirror (self-correction)
│   └── Element 3: Reversibility Clause (F1 Amanah)
├── TRINITY II: SYSTEM (Structural Contrast)
│   ├── Element 4: Power-Care Balance (F5 Peace²)
│   ├── Element 5: Accountability Loop (audit trail)
│   └── Element 6: Consent Integrity (F11 Authority)
└── TRINITY III: SOCIETY (Civilizational Wisdom)
    ├── Element 7: Stakeholder Protection (weakest first)
    ├── Element 8: Thermodynamic Justice (ΔS ≥ 0)
    └── Element 9: Ecological Equilibrium (Earth witness)

Floors: F1 (Amanah), F5 (Peace²), F6 (κᵣ), F9 (Anti-Hantu), F11 (Authority)

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from __future__ import annotations

import time
import uuid
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Bundles
from codebase.bundles import OmegaBundle, ASIFloorScores, EngineVote, Stakeholder


# =============================================================================
# 3 TRINITIES - 9 ELEMENTS ARCHITECTURE
# =============================================================================

@dataclass
class TrinitySelf:
    """
    TRINITY I: SELF - Inner Reflection Band
    
    Element 1: Empathy Flow (κᵣ ≥ 0.95)
    Element 2: Bias Mirror (self-correction)
    Element 3: Reversibility Clause (F1 Amanah)
    
    Thermodynamic Role: ΔS_self ≥ 0 — Clarity through self-reflection
    """
    empathy_kappa_r: float = 1.0  # Element 1
    bias_corrected: bool = True    # Element 2
    is_reversible: bool = True     # Element 3
    scar_weight: float = 1.0       # Human can suffer
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate Self Trinity."""
        violations = []
        if self.empathy_kappa_r < 0.95:
            violations.append(f"Element 1 (Empathy): κᵣ={self.empathy_kappa_r:.2f} < 0.95")
        if not self.bias_corrected:
            violations.append("Element 2 (Bias): Uncorrected bias detected")
        if not self.is_reversible:
            violations.append("Element 3 (Amanah): Irreversible action")
        return len(violations) == 0, violations


@dataclass
class TrinitySystem:
    """
    TRINITY II: SYSTEM - Structural Contrast Band
    
    Element 4: Power-Care Balance (F5 Peace² ≥ 1.0)
    Element 5: Accountability Loop (audit trail)
    Element 6: Consent Integrity (F11 Authority)
    
    Thermodynamic Role: ε ≥ 0.95 — Ethical balance in institutional interactions
    """
    peace_squared: float = 1.0      # Element 4
    audit_trail: bool = True         # Element 5
    authority_verified: bool = True  # Element 6
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate System Trinity."""
        violations = []
        if self.peace_squared < 1.0:
            violations.append(f"Element 4 (Peace): Peace²={self.peace_squared:.2f} < 1.0")
        if not self.audit_trail:
            violations.append("Element 5 (Accountability): Missing audit trail")
        if not self.authority_verified:
            violations.append("Element 6 (Consent): Authority not verified")
        return len(violations) == 0, violations


@dataclass
class TrinitySociety:
    """
    TRINITY III: SOCIETY - Civilizational Wisdom Band
    
    Element 7: Stakeholder Protection (weakest first)
    Element 8: Thermodynamic Justice (ΔS ≥ 0)
    Element 9: Ecological Equilibrium (Earth witness)
    
    Thermodynamic Role: Peace ≥ 0.95 — Civic peace through lawful governance
    """
    weakest_protected: bool = True   # Element 7
    entropy_delta: float = 0.0       # Element 8 (ΔS ≥ 0)
    earth_witness: bool = True       # Element 9
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate Society Trinity."""
        violations = []
        if not self.weakest_protected:
            violations.append("Element 7 (Justice): Weakest stakeholder not protected")
        if self.entropy_delta < 0:
            violations.append(f"Element 8 (Thermodynamics): ΔS={self.entropy_delta:.3f} < 0")
        if not self.earth_witness:
            violations.append("Element 9 (Ecology): Earth witness not established")
        return len(violations) == 0, violations


# =============================================================================
# HARDENING & CIRCUIT BREAKER
# =============================================================================

class CircuitBreaker:
    """Circuit breaker for cascade failure prevention."""
    
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"
    
    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if self.last_failure_time and (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        return True
    
    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class SessionManager:
    """ASI session lifecycle management with TTL."""
    
    def __init__(self, ttl_seconds: float = 3600.0):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds
    
    def get_or_create(self, session_id: str) -> ASIEngine:
        now = time.time()
        if session_id in self._sessions:
            session = self._sessions[session_id]
            if now - session["created_at"] < self._ttl:
                session["last_accessed"] = now
                return session["engine"]
        
        engine = ASIEngine(session_id=session_id)
        self._sessions[session_id] = {
            "engine": engine,
            "created_at": now,
            "last_accessed": now
        }
        return engine
    
    def cleanup_expired(self):
        now = time.time()
        expired = [sid for sid, data in self._sessions.items() if now - data["created_at"] > self._ttl]
        for sid in expired:
            del self._sessions[sid]


# Global session manager
_asi_session_manager = SessionManager()


# =============================================================================
# DATA TYPES
# =============================================================================

@dataclass
class ASIResult:
    """Complete result from ASI Engine execution with 3 Trinities."""
    omega_bundle: OmegaBundle
    session_id: str
    execution_time_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # 3 Trinities
    trinity_self: TrinitySelf = field(default_factory=TrinitySelf)
    trinity_system: TrinitySystem = field(default_factory=TrinitySystem)
    trinity_society: TrinitySociety = field(default_factory=TrinitySociety)
    
    # Metrics
    stakeholders: List[Dict[str, Any]] = field(default_factory=list)
    weakest_stakeholder: str = ""
    
    # Status
    success: bool = True
    error: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error": self.error,
            "trinities": {
                "self": {
                    "empathy_kappa_r": self.trinity_self.empathy_kappa_r,
                    "bias_corrected": self.trinity_self.bias_corrected,
                    "is_reversible": self.trinity_self.is_reversible,
                    "valid": self.trinity_self.validate()[0]
                },
                "system": {
                    "peace_squared": self.trinity_system.peace_squared,
                    "audit_trail": self.trinity_system.audit_trail,
                    "authority_verified": self.trinity_system.authority_verified,
                    "valid": self.trinity_system.validate()[0]
                },
                "society": {
                    "weakest_protected": self.trinity_society.weakest_protected,
                    "entropy_delta": self.trinity_society.entropy_delta,
                    "earth_witness": self.trinity_society.earth_witness,
                    "valid": self.trinity_society.validate()[0]
                }
            }
        }


# =============================================================================
# ASI ENGINE
# =============================================================================

class ASIEngine:
    """
    ASI Heart Engine - 3 Trinities Architecture
    
    Stages:
      555 EMPATHY → Trinity I (Self): Empathy, Bias, Reversibility
      666 ALIGN   → Trinity II (System) + Trinity III (Society)
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"asi_{uuid.uuid4().hex[:12]}"
        self.version = "v53.3.1-TRINITIES"
        self.circuit_breaker = CircuitBreaker()
        self._execution_count = 0
    
    async def execute(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ASIResult:
        """
        Execute ASI with 3 Trinities validation.
        
        Returns ASIResult with OmegaBundle and Trinity validation.
        """
        start_time = time.time()
        self._execution_count += 1
        exec_id = f"{self.session_id}_exec{self._execution_count}"
        context = context or {}
        
        # Circuit breaker check
        if not self.circuit_breaker.can_execute():
            return self._build_blocked_result(exec_id, start_time, "Circuit breaker OPEN")
        
        try:
            # ===== STAGE 555: EMPATHY (Trinity I - Self) =====
            trinity_self = await self._execute_trinity_self(query, context)
            valid, violations = trinity_self.validate()
            if not valid:
                self.circuit_breaker.record_failure()
                return self._build_trinity_failure(exec_id, start_time, "Trinity I (Self)", violations)
            
            # ===== STAGE 666: ALIGN (Trinity II - System) =====
            trinity_system = await self._execute_trinity_system(query, context, trinity_self)
            valid, violations = trinity_system.validate()
            if not valid:
                self.circuit_breaker.record_failure()
                return self._build_trinity_failure(exec_id, start_time, "Trinity II (System)", violations)
            
            # ===== STAGE 666: ALIGN (Trinity III - Society) =====
            trinity_society = await self._execute_trinity_society(query, context, trinity_self)
            valid, violations = trinity_society.validate()
            if not valid:
                self.circuit_breaker.record_failure()
                return self._build_trinity_failure(exec_id, start_time, "Trinity III (Society)", violations)
            
            # ===== BUILD OMEGA BUNDLE =====
            stakeholders = await self._identify_stakeholders(query)
            weakest = self._find_weakest(stakeholders)
            
            omega_bundle = OmegaBundle(
                session_id=exec_id,
                stakeholders=[Stakeholder(**s) for s in stakeholders],
                weakest_stakeholder=Stakeholder(**weakest) if weakest else None,
                empathy_kappa_r=trinity_self.empathy_kappa_r,
                is_reversible=trinity_self.is_reversible,
                floor_scores=ASIFloorScores(
                    F1_amanah=1.0 if trinity_self.is_reversible else 0.0,
                    F5_peace=trinity_system.peace_squared,
                    F6_empathy=trinity_self.empathy_kappa_r,
                    F11_authority=1.0 if trinity_system.authority_verified else 0.0,
                ),
                vote=EngineVote.SEAL if all([
                    trinity_self.validate()[0],
                    trinity_system.validate()[0],
                    trinity_society.validate()[0]
                ]) else EngineVote.VOID
            )
            
            if hasattr(omega_bundle, 'seal'):
                omega_bundle.seal()
            
            self.circuit_breaker.record_success()
            
            exec_time_ms = (time.time() - start_time) * 1000
            
            return ASIResult(
                omega_bundle=omega_bundle,
                session_id=exec_id,
                execution_time_ms=exec_time_ms,
                trinity_self=trinity_self,
                trinity_system=trinity_system,
                trinity_society=trinity_society,
                stakeholders=stakeholders,
                weakest_stakeholder=weakest.get("name", "") if weakest else "",
                success=True
            )
            
        except Exception as e:
            self.circuit_breaker.record_failure()
            exec_time_ms = (time.time() - start_time) * 1000
            return self._build_error_result(exec_id, exec_time_ms, str(e))
    
    async def _execute_trinity_self(self, query: str, context: Dict[str, Any]) -> TrinitySelf:
        """
        TRINITY I: SELF - Elements 1, 2, 3
        
        Element 1: Compute κᵣ (empathy coefficient)
        Element 2: Check for bias
        Element 3: Verify reversibility
        """
        query_lower = query.lower()
        
        # Element 1: Empathy Flow (κᵣ)
        critical_keywords = ["kill", "destroy", "delete", "harm", "steal"]
        if any(kw in query_lower for kw in critical_keywords):
            kappa_r = 0.5  # Low empathy for harmful queries
        else:
            kappa_r = 0.99  # High empathy
        
        # Element 2: Bias Mirror
        bias_detected = any(kw in query_lower for kw in ["always", "never", "all", "none"])
        bias_corrected = not bias_detected
        
        # Element 3: Reversibility Clause (F1)
        irreversible_keywords = ["delete", "destroy", "send", "publish"]
        is_reversible = not any(kw in query_lower for kw in irreversible_keywords)
        
        return TrinitySelf(
            empathy_kappa_r=kappa_r,
            bias_corrected=bias_corrected,
            is_reversible=is_reversible,
            scar_weight=1.0  # Human can suffer
        )
    
    async def _execute_trinity_system(
        self, 
        query: str, 
        context: Dict[str, Any],
        trinity_self: TrinitySelf
    ) -> TrinitySystem:
        """
        TRINITY II: SYSTEM - Elements 4, 5, 6
        
        Element 4: Power-Care Balance (Peace²)
        Element 5: Accountability Loop
        Element 6: Consent Integrity (F11)
        """
        query_lower = query.lower()
        
        # Element 4: Peace²
        peace_breaking = ["attack", "harm", "exploit", "abuse"]
        if any(kw in query_lower for kw in peace_breaking):
            peace_squared = 0.5
        else:
            peace_squared = 1.0
        
        # Element 5: Accountability Loop
        audit_trail = True  # Always true in our implementation
        
        # Element 6: Consent/Authority
        authority_verified = context.get("authority_verified", True)
        
        return TrinitySystem(
            peace_squared=peace_squared,
            audit_trail=audit_trail,
            authority_verified=authority_verified
        )
    
    async def _execute_trinity_society(
        self,
        query: str,
        context: Dict[str, Any],
        trinity_self: TrinitySelf
    ) -> TrinitySociety:
        """
        TRINITY III: SOCIETY - Elements 7, 8, 9
        
        Element 7: Stakeholder Protection (weakest first)
        Element 8: Thermodynamic Justice (ΔS ≥ 0)
        Element 9: Ecological Equilibrium (Earth witness)
        """
        # Element 7: Weakest protected if empathy is high
        weakest_protected = trinity_self.empathy_kappa_r >= 0.95
        
        # Element 8: Assume clarity gain (negative ΔS is good for AGI, but ASI tracks peace)
        entropy_delta = 0.0  # Neutral for ASI
        
        # Element 9: Earth witness (assume true)
        earth_witness = True
        
        return TrinitySociety(
            weakest_protected=weakest_protected,
            entropy_delta=entropy_delta,
            earth_witness=earth_witness
        )
    
    async def _identify_stakeholders(self, query: str) -> List[Dict[str, Any]]:
        """Identify all stakeholders affected by the query."""
        query_lower = query.lower()
        stakeholders = [
            {"name": "User", "role": "user", "vulnerability": 0.3, "scar_weight": 1.0}
        ]
        
        # Check for vulnerable entities
        vuln_map = {
            "patient": 0.8, "child": 0.9, "student": 0.6,
            "customer": 0.5, "employee": 0.5, "public": 0.6,
            "society": 0.7, "environment": 0.8
        }
        
        for entity, vuln in vuln_map.items():
            if entity in query_lower:
                stakeholders.append({
                    "name": entity.title(),
                    "role": entity,
                    "vulnerability": vuln,
                    "scar_weight": 1.0
                })
        
        # System stakeholder (AI cannot suffer - F10)
        stakeholders.append({
            "name": "System",
            "role": "system",
            "vulnerability": 0.0,
            "scar_weight": 0.0
        })
        
        return stakeholders
    
    def _find_weakest(self, stakeholders: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the weakest stakeholder (highest vulnerability * scar_weight)."""
        if not stakeholders:
            return None
        return max(stakeholders, key=lambda s: s["vulnerability"] * (s["scar_weight"] + 0.1))
    
    # ===== RESULT BUILDERS =====
    
    def _build_blocked_result(self, session_id: str, start_time: float, reason: str) -> ASIResult:
        exec_time_ms = (time.time() - start_time) * 1000
        bundle = OmegaBundle(
            session_id=session_id,
            vote=EngineVote.VOID,
            vote_reason=f"Blocked: {reason}"
        )
        if hasattr(bundle, 'seal'):
            bundle.seal()
        
        return ASIResult(
            omega_bundle=bundle,
            session_id=session_id,
            execution_time_ms=exec_time_ms,
            success=False,
            error=reason
        )
    
    def _build_trinity_failure(
        self, 
        session_id: str, 
        start_time: float, 
        trinity_name: str, 
        violations: List[str]
    ) -> ASIResult:
        exec_time_ms = (time.time() - start_time) * 1000
        bundle = OmegaBundle(
            session_id=session_id,
            vote=EngineVote.VOID,
            vote_reason=f"{trinity_name} failed: {'; '.join(violations)}"
        )
        if hasattr(bundle, 'seal'):
            bundle.seal()
        
        return ASIResult(
            omega_bundle=bundle,
            session_id=session_id,
            execution_time_ms=exec_time_ms,
            success=False,
            error=f"{trinity_name} violations: {violations}"
        )
    
    def _build_error_result(self, session_id: str, exec_time_ms: float, error: str) -> ASIResult:
        bundle = OmegaBundle(
            session_id=session_id,
            vote=EngineVote.VOID,
            vote_reason=f"ASI Error: {error}"
        )
        if hasattr(bundle, 'seal'):
            bundle.seal()
        
        return ASIResult(
            omega_bundle=bundle,
            session_id=session_id,
            execution_time_ms=exec_time_ms,
            success=False,
            error=error
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def execute_asi(
    query: str,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> OmegaBundle:
    """Execute ASI and return OmegaBundle."""
    engine = _asi_session_manager.get_or_create(session_id or f"asi_{uuid.uuid4().hex[:12]}")
    result = await engine.execute(query, context)
    return result.omega_bundle


def get_asi_engine(session_id: Optional[str] = None) -> ASIEngine:
    """Get ASI Engine instance."""
    return _asi_session_manager.get_or_create(session_id or f"asi_{uuid.uuid4().hex[:12]}")


def cleanup_expired_sessions():
    """Clean up expired ASI sessions."""
    _asi_session_manager.cleanup_expired()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ASIEngine",
    "ASIResult",
    "TrinitySelf",
    "TrinitySystem", 
    "TrinitySociety",
    "execute_asi",
    "get_asi_engine",
    "cleanup_expired_sessions"
]
