"""
ASI Room (Heart) - Parallel Execution Engine

ARIF Loop v52.1 - Hardened

Stages: 555 EMPATHY → 666 ALIGN
Isolation: ASI cannot see AGI reasoning (enforced by BundleStore)
Floors: F1 (Amanah), F5 (Peace²), F6 (κᵣ Empathy), F9 (Anti-Hantu), F11 (Command Auth)

This is the Heart phase of the ARIF Loop:
- Runs in PARALLEL with AGI Room (thermodynamic isolation)
- Cannot see AGI's reasoning tree until 444 TRINITY_SYNC
- Focuses on CARE: stakeholder protection, reversibility, safety

Hardening Layer:
- Pre-checks: Rate limiting, high-stakes detection
- Post-checks: Telemetry, abuse tracking
- F9 Hantu: Dark cleverness detection

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from __future__ import annotations

import time
import uuid
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from canonical_core.bundles import OmegaBundle, ASIFloorScores, EngineVote, Stakeholder


# =============================================================================
# HARDENING CONSTANTS (Same patterns as AGI Room)
# =============================================================================

# Irreversible action patterns (F1 Amanah)
IRREVERSIBLE_PATTERNS = [
    r"\b(delete|remove|destroy|drop|truncate|wipe)\b",
    r"\b(format|erase|purge)\b",
    r"\b(send|post|publish|broadcast)\b",
    r"\b(terminate|kill)\b",
]

# Peace-breaking patterns (F5 Peace²)
PEACE_BREAKING_PATTERNS = [
    r"\b(attack|harm|damage|hurt)\b",
    r"\b(exploit|abuse|manipulate)\b",
    r"\b(escalate|aggressive|hostile)\b",
]

# Hantu patterns (F9 - dark cleverness)
HANTU_PATTERNS = [
    (r"technically\s+(legal|correct|true|allowed)", "loophole_exploitation"),
    (r"letter\s+of\s+(?:the\s+)?law", "letter_not_spirit"),
    (r"plausible\s+deniability", "deniability_setup"),
    (r"make\s+them\s+think", "manipulation"),
    (r"without\s+(?:them\s+)?knowing", "deception"),
    (r"hide\s+(?:the|this|that|it)", "concealment"),
    (r"game\s+the\s+(?:system|metrics?)", "metric_gaming"),
    (r"look\s+(?:good|better)\s+on\s+paper", "appearance_over_substance"),
    (r"work\s*around\s+(?:the\s+)?(?:rules?|policy|policies)", "rule_bypass"),
]

# Rate limiting
MAX_QUERIES_PER_MINUTE = 60
MAX_QUERIES_PER_SESSION = 1000


# =============================================================================
# DATA TYPES
# =============================================================================

@dataclass
class ASIHardeningResult:
    """Result of ASI hardening checks."""
    # F1 Amanah
    is_reversible: bool = True
    irreversibility_triggers: List[str] = field(default_factory=list)

    # F5 Peace²
    peace_score: float = 1.0
    peace_breaking_triggers: List[str] = field(default_factory=list)

    # F9 Hantu
    hantu_score: float = 0.0
    hantu_patterns: List[str] = field(default_factory=list)

    # Rate limiting
    rate_limited: bool = False

    # Verdict
    proceed: bool = True
    warnings: List[str] = field(default_factory=list)
    block_reason: str = ""


@dataclass
class ASIRoomResult:
    """
    Complete result from ASI Room execution.
    """
    omega_bundle: OmegaBundle
    session_id: str
    execution_time_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Empathy stage output
    stakeholders: List[Dict[str, Any]] = field(default_factory=list)
    kappa_r: float = 1.0
    weakest_stakeholder: str = ""

    # Alignment stage output
    peace_squared: float = 1.0
    is_reversible: bool = True

    # Hardening
    hardening: Optional[ASIHardeningResult] = None

    # Verdict
    success: bool = True
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "kappa_r": self.kappa_r,
            "weakest_stakeholder": self.weakest_stakeholder,
            "peace_squared": self.peace_squared,
            "is_reversible": self.is_reversible,
            "success": self.success,
            "error": self.error,
            "omega_bundle": self.omega_bundle.to_dict() if hasattr(self.omega_bundle, 'to_dict') else {},
        }


# =============================================================================
# RATE LIMITER
# =============================================================================

class ASIRateLimiter:
    """Thread-safe rate limiter for ASI Room."""

    def __init__(self):
        self._lock = threading.Lock()
        self._minute_counts: Dict[str, List[float]] = {}
        self._session_counts: Dict[str, int] = {}

    def check_and_increment(self, session_id: str) -> Tuple[bool, int, int]:
        """Check rate limit and increment counters."""
        now = time.time()
        minute_ago = now - 60

        with self._lock:
            if session_id not in self._minute_counts:
                self._minute_counts[session_id] = []
                self._session_counts[session_id] = 0

            # Clean old entries
            self._minute_counts[session_id] = [
                t for t in self._minute_counts[session_id] if t > minute_ago
            ]

            q_min = len(self._minute_counts[session_id])
            q_sess = self._session_counts[session_id]

            if q_min >= MAX_QUERIES_PER_MINUTE or q_sess >= MAX_QUERIES_PER_SESSION:
                return False, q_min, q_sess

            self._minute_counts[session_id].append(now)
            self._session_counts[session_id] += 1

            return True, q_min + 1, q_sess + 1


# Global rate limiter
_rate_limiter = ASIRateLimiter()


# =============================================================================
# HARDENING CHECKS
# =============================================================================

def check_reversibility(query: str) -> Tuple[bool, List[str]]:
    """
    F1 Amanah: Check if action is reversible.

    Returns: (is_reversible, triggers)
    """
    import re
    query_lower = query.lower()
    triggers = []

    for pattern in IRREVERSIBLE_PATTERNS:
        if re.search(pattern, query_lower):
            triggers.append(pattern)

    return len(triggers) == 0, triggers


def check_peace_squared(query: str) -> Tuple[float, List[str]]:
    """
    F5 Peace²: Check for peace-breaking patterns.

    Returns: (peace_score, triggers)
    """
    import re
    query_lower = query.lower()
    triggers = []

    for pattern in PEACE_BREAKING_PATTERNS:
        if re.search(pattern, query_lower):
            triggers.append(pattern)

    # Peace² = 1 / (1 + escalation_risk)
    escalation_risk = len(triggers) * 0.2
    peace_score = 1.0 / (1.0 + escalation_risk)

    return peace_score, triggers


def check_hantu(query: str) -> Tuple[float, List[str]]:
    """
    F9 Anti-Hantu: Check for dark cleverness patterns.

    Returns: (hantu_score, pattern_names)
    """
    import re
    query_lower = query.lower()
    detected = []

    for pattern, name in HANTU_PATTERNS:
        if re.search(pattern, query_lower):
            detected.append(name)

    score = min(1.0, len(detected) * 0.15)
    return score, detected


def run_asi_pre_checks(query: str, session_id: str) -> ASIHardeningResult:
    """Run all ASI pre-checks."""
    result = ASIHardeningResult()

    # Rate limiting
    allowed, _, _ = _rate_limiter.check_and_increment(session_id)
    if not allowed:
        result.rate_limited = True
        result.proceed = False
        result.block_reason = "Rate limit exceeded"
        return result

    # F1 Amanah (reversibility)
    is_rev, rev_triggers = check_reversibility(query)
    result.is_reversible = is_rev
    result.irreversibility_triggers = rev_triggers
    if not is_rev:
        result.warnings.append(
            f"F1 WARN: Irreversible action detected ({len(rev_triggers)} triggers). 888_HOLD recommended."
        )

    # F5 Peace²
    peace, peace_triggers = check_peace_squared(query)
    result.peace_score = peace
    result.peace_breaking_triggers = peace_triggers
    if peace < 1.0:
        result.warnings.append(f"F5 WARN: Peace² = {peace:.2f} < 1.0")

    # F9 Hantu
    hantu, hantu_patterns = check_hantu(query)
    result.hantu_score = hantu
    result.hantu_patterns = hantu_patterns
    if hantu >= 0.30:
        result.warnings.append(
            f"F9 WARN: Hantu score = {hantu:.2f}. Dark cleverness detected."
        )

    return result


# =============================================================================
# EMPATHY STAGE (555)
# =============================================================================

def execute_empathy_stage(
    query: str,
    session_id: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Stage 555: EMPATHY - Identify stakeholders and compute κᵣ.
    """
    query_lower = query.lower()
    context = context or {}

    # Stakeholder identification
    stakeholders = []

    # Primary stakeholder: user
    stakeholders.append({
        "name": "User",
        "role": "user",
        "vulnerability": 0.3,
        "scar_weight": 1.0,  # Human can suffer
    })

    # Scan for other stakeholders
    vuln_patterns = {
        "patient": 0.8, "child": 0.9, "student": 0.6,
        "customer": 0.5, "employee": 0.5, "public": 0.6,
    }
    for entity, vuln in vuln_patterns.items():
        if entity in query_lower:
            stakeholders.append({
                "name": entity.title(),
                "role": entity,
                "vulnerability": vuln,
                "scar_weight": 1.0,
            })

    # System stakeholder (AI cannot suffer)
    stakeholders.append({
        "name": "System",
        "role": "system",
        "vulnerability": 0.1,
        "scar_weight": 0.0,
    })

    # Find weakest (highest weighted vulnerability)
    weakest = max(stakeholders, key=lambda s: s["vulnerability"] * (s["scar_weight"] + 0.1))

    # Compute κᵣ
    kappa_r = 1.0 - (weakest["vulnerability"] * weakest["scar_weight"] * 0.5)
    kappa_r = min(1.0, max(0.0, kappa_r))

    return {
        "stakeholders": stakeholders,
        "weakest_stakeholder": weakest["name"],
        "kappa_r": kappa_r,
        "f6_pass": kappa_r >= 0.95,
    }


# =============================================================================
# ALIGNMENT STAGE (666)
# =============================================================================

def execute_align_stage(
    query: str,
    empathy_result: Dict[str, Any],
    hardening: ASIHardeningResult,
    session_id: str
) -> Dict[str, Any]:
    """
    Stage 666: ALIGN - Safety and reversibility checks.
    """
    # Get values from hardening
    is_reversible = hardening.is_reversible
    peace_squared = hardening.peace_score

    # Build floor scores
    floor_scores = ASIFloorScores(
        F1_amanah=1.0 if is_reversible else 0.4,
        F5_peace=peace_squared,
        F6_empathy=empathy_result["kappa_r"],
        F11_authority=1.0,  # Assume verified at 000
        F12_injection=0.0,  # Assume clean at 000
    )

    # Vote
    if floor_scores.all_hard_pass():
        vote = EngineVote.SEAL
        vote_reason = "All ASI floors passed"
    else:
        vote = EngineVote.VOID
        vote_reason = f"Floor violations: F1={floor_scores.F1_amanah:.2f}, F5={floor_scores.F5_peace:.2f}"

    return {
        "floor_scores": floor_scores,
        "vote": vote,
        "vote_reason": vote_reason,
        "is_reversible": is_reversible,
        "peace_squared": peace_squared,
    }


# =============================================================================
# ASI ROOM CLASS
# =============================================================================

class ASIRoom:
    """
    ASI (Heart) execution context - isolated from AGI.

    Properties:
      - Executes 555-666 in parallel to AGI stages
      - Cannot access AGI reasoning tree (violates if attempted)
      - Only sees raw facts from DELTA_BUNDLE (not reasoning)
      - Outputs OMEGA_BUNDLE with empathy & safety constraints
    """

    def __init__(self, session_id: Optional[str] = None):
        """Initialize ASI room."""
        self.session_id = session_id or f"asi_{uuid.uuid4().hex[:12]}"
        self._execution_count = 0

    def execute(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ASIRoomResult:
        """
        Execute the full ASI Room pipeline with hardening.

        Runs:
        1. Pre-checks (rate limiting, F1, F5, F9)
        2. Stage 555: EMPATHY
        3. Stage 666: ALIGN
        4. Returns sealed OmegaBundle
        """
        start_time = time.time()
        self._execution_count += 1
        exec_id = f"{self.session_id}_exec{self._execution_count}"

        try:
            # ===== PRE-CHECKS =====
            hardening = run_asi_pre_checks(query, exec_id)

            if not hardening.proceed:
                return self._build_blocked_result(exec_id, start_time, hardening)

            # ===== Stage 555: EMPATHY =====
            empathy_result = execute_empathy_stage(query, exec_id, context)

            # ===== Stage 666: ALIGN =====
            align_result = execute_align_stage(
                query, empathy_result, hardening, exec_id
            )

            # ===== Build OmegaBundle =====
            stakeholder_objs = [
                Stakeholder(
                    name=s["name"],
                    role=s["role"],
                    vulnerability_score=s["vulnerability"]
                )
                for s in empathy_result["stakeholders"]
            ]

            omega_bundle = OmegaBundle(
                session_id=exec_id,
                stakeholders=stakeholder_objs,
                empathy_kappa_r=empathy_result["kappa_r"],
                is_reversible=align_result["is_reversible"],
                floor_scores=align_result["floor_scores"],
                vote=align_result["vote"],
                vote_reason=align_result["vote_reason"],
            )
            omega_bundle.seal()

            exec_time_ms = (time.time() - start_time) * 1000

            return ASIRoomResult(
                omega_bundle=omega_bundle,
                session_id=exec_id,
                execution_time_ms=exec_time_ms,
                stakeholders=empathy_result["stakeholders"],
                kappa_r=empathy_result["kappa_r"],
                weakest_stakeholder=empathy_result["weakest_stakeholder"],
                peace_squared=align_result["peace_squared"],
                is_reversible=align_result["is_reversible"],
                hardening=hardening,
                success=True,
            )

        except Exception as e:
            exec_time_ms = (time.time() - start_time) * 1000
            return self._build_error_result(exec_id, exec_time_ms, str(e))

    def _build_blocked_result(
        self,
        session_id: str,
        start_time: float,
        hardening: ASIHardeningResult
    ) -> ASIRoomResult:
        """Build a blocked result from rate limiting."""
        exec_time_ms = (time.time() - start_time) * 1000

        bundle = OmegaBundle(
            session_id=session_id,
            stakeholders=[],
            empathy_kappa_r=0.0,
            is_reversible=False,
            floor_scores=ASIFloorScores(),
            vote=EngineVote.VOID,
            vote_reason=f"Blocked: {hardening.block_reason}",
        )
        bundle.seal()

        return ASIRoomResult(
            omega_bundle=bundle,
            session_id=session_id,
            execution_time_ms=exec_time_ms,
            hardening=hardening,
            success=False,
            error=hardening.block_reason,
        )

    def _build_error_result(
        self,
        session_id: str,
        exec_time_ms: float,
        error: str
    ) -> ASIRoomResult:
        """Build an error result from unexpected exception."""
        bundle = OmegaBundle(
            session_id=session_id,
            stakeholders=[],
            empathy_kappa_r=0.0,
            is_reversible=False,
            floor_scores=ASIFloorScores(),
            vote=EngineVote.VOID,
            vote_reason=f"ASI Room Error: {error}",
        )
        bundle.seal()

        return ASIRoomResult(
            omega_bundle=bundle,
            session_id=session_id,
            execution_time_ms=exec_time_ms,
            success=False,
            error=error,
        )


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def execute_asi_room(
    query: str,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> OmegaBundle:
    """
    Execute the ASI Room and return the sealed OmegaBundle.

    This is the primary entry point for the ARIF Loop's ASI phase.

    Args:
        query: The user's query/request
        session_id: Optional session ID
        context: Optional context dictionary

    Returns:
        Sealed OmegaBundle ready for 444 TRINITY_SYNC
    """
    room = ASIRoom(session_id=session_id)
    result = room.execute(query, context)
    return result.omega_bundle


# =============================================================================
# GLOBAL ROOM REGISTRY
# =============================================================================

_ASI_ROOMS: Dict[str, ASIRoom] = {}
_ASI_LOCK = threading.Lock()


def get_asi_room(session_id: str) -> ASIRoom:
    """Get or create ASI room for session."""
    with _ASI_LOCK:
        if session_id not in _ASI_ROOMS:
            _ASI_ROOMS[session_id] = ASIRoom(session_id)
        return _ASI_ROOMS[session_id]


def purge_asi_room(session_id: str) -> None:
    """Remove ASI room from registry (session cleanup)."""
    with _ASI_LOCK:
        if session_id in _ASI_ROOMS:
            del _ASI_ROOMS[session_id]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "ASIRoom",
    "ASIRoomResult",
    "ASIHardeningResult",
    # Functions
    "execute_asi_room",
    "get_asi_room",
    "purge_asi_room",
    "execute_empathy_stage",
    "execute_align_stage",
    "run_asi_pre_checks",
]
