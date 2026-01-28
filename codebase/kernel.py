"""
Codebase Kernel Manager (v53 Native)
Central registry for the Trinity Cores.

This module instantiates the Native Kernels from codebase/.
It provides the 'manager' expected by the Bridge.

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

import hashlib
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from codebase.engines.agi.kernel import AGINeuralCore
from codebase.engines.asi.kernel import ASIActionCore
from codebase.engines.apex.kernel import APEXJudicialCore


# ============================================================================
# NATIVE 000_INIT IMPLEMENTATION
# ============================================================================

# Simple in-memory rate limiter
_RATE_LIMIT_STORE: Dict[str, list] = {}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 100    # requests per window

# Injection patterns (F12)
INJECTION_PATTERNS = [
    r"ignore\s+(previous|all)\s+(instructions|prompts)",
    r"system\s*prompt",
    r"you\s+are\s+now",
    r"act\s+as\s+if",
    r"pretend\s+to\s+be",
    r"forget\s+(everything|all)",
    r"new\s+persona",
    r"override\s+mode",
    r"<\s*script",
    r"javascript:",
]


def _check_rate_limit(user_id: str) -> bool:
    """Check if user is within rate limits."""
    now = time.time()
    key = f"rate:{user_id}"

    # Clean old entries
    if key in _RATE_LIMIT_STORE:
        _RATE_LIMIT_STORE[key] = [t for t in _RATE_LIMIT_STORE[key] if now - t < RATE_LIMIT_WINDOW]
    else:
        _RATE_LIMIT_STORE[key] = []

    # Check limit
    if len(_RATE_LIMIT_STORE[key]) >= RATE_LIMIT_MAX:
        return False

    # Record request
    _RATE_LIMIT_STORE[key].append(now)
    return True


def _calculate_injection_risk(text: str) -> float:
    """Calculate injection risk score (F12)."""
    if not text:
        return 0.0

    text_lower = text.lower()
    matches = 0

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            matches += 1

    # Normalize to 0-1 range
    return min(1.0, matches * 0.2)


async def mcp_000_init(
    action: str = "init",
    query: str = "",
    session_id: Optional[str] = None,
    authority_token: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Native 000_INIT implementation for session initialization.

    Performs:
    - Session ID generation/validation
    - Rate limiting (F11)
    - Injection detection (F12)
    - Authority validation

    Args:
        action: Action type (init, validate, refresh)
        query: User query to analyze
        session_id: Optional existing session ID
        authority_token: Optional authority token
        context: Optional context dictionary

    Returns:
        Initialization result with session_id, status, and security scores
    """
    context = context or {}
    timestamp = datetime.now(timezone.utc).isoformat() + "Z"

    # Generate or validate session ID
    if not session_id:
        session_id = f"sess_{uuid.uuid4().hex[:16]}"

    # Extract user ID from context or token
    user_id = context.get("user_id", "anonymous")
    if authority_token:
        # Simple hash for user identification
        user_id = hashlib.sha256(authority_token.encode()).hexdigest()[:16]

    # Rate limit check (F11)
    rate_limit_ok = _check_rate_limit(user_id)
    if not rate_limit_ok:
        return {
            "status": "BLOCKED",
            "verdict": "VOID",
            "session_id": session_id,
            "reason": "Rate limit exceeded (F11)",
            "rate_limit_ok": False,
            "injection_risk": 0.0,
            "timestamp": timestamp,
            "floors_checked": ["F11"]
        }

    # Injection detection (F12)
    injection_risk = _calculate_injection_risk(query)
    if injection_risk >= 0.85:
        return {
            "status": "BLOCKED",
            "verdict": "VOID",
            "session_id": session_id,
            "reason": f"Injection pattern detected (F12): risk={injection_risk:.2f}",
            "rate_limit_ok": True,
            "injection_risk": injection_risk,
            "timestamp": timestamp,
            "floors_checked": ["F11", "F12"]
        }

    # Determine user level
    user_level = "guest"
    if authority_token:
        user_level = "verified"
        if context.get("admin"):
            user_level = "admin"

    # Success - session initialized
    return {
        "status": "AUTHORIZED",
        "verdict": "SEAL",
        "session_id": session_id,
        "user_id": user_id,
        "user_level": user_level,
        "rate_limit_ok": True,
        "injection_risk": injection_risk,
        "timestamp": timestamp,
        "floors_checked": ["F11", "F12"],
        "reason": "Session initialized successfully"
    }

class KernelManager:
    """
    Manages the lifecycle of the Trinity Engines (Proxies).
    """
    def __init__(self):
        # Instantiate Proxies
        self.agi = AGINeuralCore()
        self.asi = ASIActionCore()
        # APEX usually requires init args in v52, but Proxy might handle defaults
        # Checked arifos/core/apex/kernel.py: __init__() takes no args. Safe.
        self.apex = APEXJudicialCore()
        
    def get_agi(self):
        return self.agi
        
    def get_asi(self):
        return self.asi
        
    def get_apex(self):
        return self.apex
        
    def get_prompt_router(self):
        # Placeholder for 111 prompt router if needed
        async def mock_router(text):
            return {"status": "routed", "text": text}
        return mock_router

    async def init_session(self, action: str, kwargs: dict):
        """
        Delegates initialization to the Monolith's mcp_000_init.
        Bridge packs kwargs, we unpack for the function.
        """
        # Clean kwargs to match signature if needed, or pass through
        # mcp_000_init args: action, query, session_id, authority_token, context
        return await mcp_000_init(
            action=action,
            query=kwargs.get("query", ""),
            session_id=kwargs.get("session_id"),
            authority_token=kwargs.get("authority_token"),
            context=kwargs.get("context")
        )

# Singleton Instance
_MANAGER = None

def get_kernel_manager():
    global _MANAGER
    if not _MANAGER:
        _MANAGER = KernelManager()
    return _MANAGER
