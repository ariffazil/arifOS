# arifos/core/governance/rate_limiter.py

from dataclasses import dataclass
from typing import Dict, Optional
import threading
import time

@dataclass
class TokenBucket:
    """Thread-safe token bucket for rate limiting."""
    capacity: float
    refill_rate: float
    tokens: float = 0
    last_refill: float = 0
    _lock: threading.Lock = None
    
    def __post_init__(self):
        self.tokens = self.capacity
        self.last_refill = time.time()
        self._lock = threading.Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """Attempt to consume tokens."""
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def _refill(self):
        """Add tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

@dataclass  
class RateLimitResult:
    allowed: bool
    verdict: str
    reason: str
    constitutional_violation: Optional[str] = None
    reset_in_seconds: Optional[int] = None
    remaining: Optional[int] = None

class ConstitutionalRateLimiter:
    """F11 Command Authority enforcement."""
    
    # Constitutional thresholds (Track A canon)
    MIN_PER_SESSION = 10  # F11.1: Minimum service guarantee
    MAX_GLOBAL = 10000     # F11.2: System preservation
    FAIRNESS_THRESHOLD = 0.95  # F11.3: Tri-witness fairness
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            "init_000": {"per_session": 30, "global": 300, "burst": 5},
            "agi_genius": {"per_session": 60, "global": 600, "burst": 10},
            "asi_act": {"per_session": 60, "global": 600, "burst": 10},
            "apex_judge": {"per_session": 60, "global": 600, "burst": 10},
            "vault_999": {"per_session": 30, "global": 300, "burst": 5},
        }
        
        self._session_buckets: Dict[str, Dict[str, TokenBucket]] = {}
        self._global_buckets: Dict[str, TokenBucket] = {}
        self._lock = threading.RLock()
        
        # Initialize global buckets
        for tool, limits in self.config.items():
            self._global_buckets[tool] = TokenBucket(
                capacity=limits["global"],
                refill_rate=limits["global"] / 3600  # Per hour
            )
    
    def check(self, tool_name: str, session_id: str) -> RateLimitResult:
        """
        Check F11 authority for tool invocation.
        
        Constitutional validation:
        1. F11.1: Session-level limits (per-user fairness)
        2. F11.2: Global limits (system preservation)
        3. F11.3: Tri-witness fairness (Human × AI × Earth)
        """
        if tool_name not in self.config:
            return RateLimitResult(True, "SEAL", "Tool not rate limited")
        
        limits = self.config[tool_name]
        
        with self._lock:
            # F11.1: Session authority check
            session_bucket = self._get_session_bucket(tool_name, session_id)
            if not session_bucket.consume(1):
                return RateLimitResult(
                    allowed=False,
                    verdict="VOID",
                    reason="F11.1: Per-session rate limit exceeded",
                    constitutional_violation="F11_1_Session_Exhausted"
                )
            
            # F11.2: Global authority check
            global_bucket = self._global_buckets[tool_name]
            if not global_bucket.consume(1):
                # Refund session token to maintain fairness
                session_bucket.tokens += 1
                return RateLimitResult(
                    allowed=False,
                    verdict="VOID",
                    reason="F11.2: Global rate limit exceeded - system preservation",
                    constitutional_violation="F11_2_Global_Preservation"
                )
            
            # F11.3: Tri-witness fairness check
            fairness_verdict = self._check_fairness(tool_name, session_id)
            if fairness_verdict != "SEAL":
                # Refund both tokens
                session_bucket.tokens += 1
                global_bucket.tokens += 1
                return RateLimitResult(
                    allowed=False,
                    verdict=fairness_verdict,
                    reason="F11.3: Fairness constraints violated",
                    constitutional_violation="F11_3_Fairness_Violation"
                )
        
        return RateLimitResult(
            allowed=True,
            verdict="SEAL",
            reason="F11: Command authority granted"
        )
    
    def _get_session_bucket(self, tool_name: str, session_id: str) -> TokenBucket:
        """Get or create token bucket for session."""
        if session_id not in self._session_buckets:
            self._session_buckets[session_id] = {}
        
        if tool_name not in self._session_buckets[session_id]:
            limits = self.config[tool_name]
            self._session_buckets[session_id][tool_name] = TokenBucket(
                capacity=limits["per_session"],
                refill_rate=limits["per_session"] / 3600
            )
        
        return self._session_buckets[session_id][tool_name]
    
    def _check_fairness(self, tool_name: str, session_id: str) -> str:
        """
        Tri-witness fairness validation (F11.3).
        
        Witnesses:
        - Human: Prevent single session domination
        - AI: System resource availability
        - Earth: Thermodynamic sustainability (ΔS ≤ 0)
        """
        # Human witness: usage ratio vs other sessions
        human_score = self._calculate_human_fairness(session_id)
        
        # AI witness: system load and availability  
        ai_score = self._calculate_ai_fairness(tool_name)
        
        # Earth witness: thermodynamic cost vs value
        earth_score = self._calculate_earth_sustainability()
        
        # Geometric mean (fairer than arithmetic)
        fairness_score = (human_score * ai_score * earth_score) ** (1/3)
        
        if fairness_score >= self.FAIRNESS_THRESHOLD:
            return "SEAL"
        elif fairness_score >= 0.70:
            # Allow with warning (soft failure)
            return "SABAR"
        else:
            # Unfair, deny (hard failure)
            return "VOID"
    
    def _calculate_human_fairness(self, session_id: str) -> float:
        """Prevent single session from dominating."""
        # Calculate ratio of this session's usage vs total
        # Target: Keep below 0.30 (30% of total capacity)
        # Placeholder for v52 implementation
        return 0.99
    
    def _calculate_ai_fairness(self, tool_name: str) -> float:
        """System resource availability."""
        # Check CPU, memory, queue depth
        # Target: > 0.20 (20% headroom minimum)
        # Placeholder for v52 implementation
        return 0.99
    
    def _calculate_earth_sustainability(self) -> float:
        """Thermodynamic sustainability."""
        # Energy cost vs constitutional value
        # Formula: sustainability = 1 - (ΔS / max_ΔS)
        # Target: ΔS ≤ 0 (non-negative sustainability)
        # Placeholder for v52 implementation
        return 0.99

# Singleton instance
_constitutional_rate_limiter = None

def get_rate_limiter() -> ConstitutionalRateLimiter:
    """Get singleton rate limiter instance."""
    global _constitutional_rate_limiter
    if _constitutional_rate_limiter is None:
        _constitutional_rate_limiter = ConstitutionalRateLimiter()
    return _constitutional_rate_limiter
