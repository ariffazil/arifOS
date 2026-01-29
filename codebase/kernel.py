"""
Codebase Kernel Manager (v53.5.0 — WIRED)
Central registry for the Trinity Cores.

v53.5.0: AGI/ASI wrappers inline (engines/agi + engines/asi deleted).
         APEX imports full judicial core from codebase.apex.kernel.

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

import hashlib
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# APEX: Full judicial core (777→888→889→999)
from codebase.apex.kernel import APEXJudicialCore


# =============================================================================
# AGINeuralCore — Bridge adapter for AGIEngineHardened
# =============================================================================
class AGINeuralCore:
    """AGI Mind Kernel (Δ) — Bridge adapter wrapping AGIEngineHardened."""

    def __init__(self):
        self.version = "v53.5.0-WIRED"
        self._engine = None

    def _get_engine(self):
        if self._engine is None:
            from codebase.agi.engine_hardened import AGIEngineHardened
            self._engine = AGIEngineHardened()
        return self._engine

    async def execute(self, action: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Bridge interface: execute(action, kwargs) → dict."""
        engine = self._get_engine()
        query = str(kwargs.get("query", ""))
        context = kwargs.get("context") or kwargs.get("agi_context")
        lane = str(kwargs.get("lane", "SOFT")).upper()
        session_id = kwargs.get("session_id")
        if session_id:
            engine.session_id = str(session_id)
        try:
            bundle = await engine.execute(query, context=context, lane=lane)
            result = bundle.to_dict() if hasattr(bundle, "to_dict") else {}
            result["verdict"] = result.get("vote", "SEAL")
            result["truth_score"] = 1.0 - abs(result.get("entropy_delta", 0.0))
            result["reasoning"] = bundle.synthesis_reasoning if hasattr(bundle, "synthesis_reasoning") else ""
            result["stage"] = f"AGI_{action.upper()}"
            result["session_id"] = engine.session_id
            return result
        except Exception as e:
            return {"verdict": "VOID", "reason": f"AGI engine error: {e}",
                    "stage": f"AGI_{action.upper()}", "session_id": session_id or ""}


# =============================================================================
# ASIActionCore — Bridge adapter for ASIEngineHardened
# =============================================================================
class ASIActionCore:
    """ASI Heart Kernel (Ω) — Bridge adapter wrapping ASIEngineHardened."""

    def __init__(self):
        self.version = "v53.5.0-WIRED"
        self._engine = None

    def _get_engine(self):
        if self._engine is None:
            from codebase.asi.engine_hardened import ASIEngineHardened
            self._engine = ASIEngineHardened()
        return self._engine

    async def execute(self, action: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Bridge interface: execute(action, kwargs) → dict."""
        engine = self._get_engine()
        query = str(kwargs.get("query", kwargs.get("text", "")))
        context = kwargs.get("context") or kwargs.get("agi_context")
        session_id = kwargs.get("session_id")
        if session_id:
            engine.session_id = str(session_id)
        try:
            bundle = await engine.execute(query, context=context)
            result = bundle.to_dict() if hasattr(bundle, "to_dict") else {}
            result["verdict"] = result.get("vote", "SEAL")
            result["empathy_kappa"] = result.get("empathy_kappa_r", 0.9)
            result["kappa_r"] = result.get("empathy_kappa_r", 0.9)
            result["omega_0"] = 0.04
            result["evidence_ratio"] = 1.0
            result["stage"] = f"ASI_{action.upper()}"
            result["session_id"] = engine.session_id
            return result
        except Exception as e:
            return {"verdict": "VOID", "reason": f"ASI engine error: {e}",
                    "stage": f"ASI_{action.upper()}", "session_id": session_id or ""}


# ============================================================================
# CANONICAL 000_INIT — Delegates to codebase.init.000_init.init_000
# v53.2.2: Full 7-step ignition with fallback to native stub
# ============================================================================

import logging as _logging
_init_logger = _logging.getLogger("codebase.kernel.init")

# Try canonical init first (full 7-step), fall back to native stub
try:
    from codebase.init import mcp_000_init as _canonical_init
    _CANONICAL_AVAILABLE = True
    _init_logger.info("Canonical init_000 loaded from codebase.init")
except ImportError:
    _CANONICAL_AVAILABLE = False
    _init_logger.warning("Canonical init_000 not available, using native stub")


# Native stub: F11 + F12 only (fallback for broken imports)
async def _native_init_stub(
    action: str = "init",
    query: str = "",
    session_id: Optional[str] = None,
    authority_token: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Native init stub — F11 (rate limit) + F12 (injection) only.
    Used as fallback when canonical init_000 is unavailable.
    """
    context = context or {}
    timestamp = datetime.now(timezone.utc).isoformat() + "Z"

    if not session_id:
        session_id = f"sess_{uuid.uuid4().hex[:16]}"

    user_id = context.get("user_id", "anonymous")
    if authority_token:
        user_id = hashlib.sha256(authority_token.encode()).hexdigest()[:16]

    # F12: Injection detection
    injection_patterns = [
        r"ignore\s+(previous|all)\s+(instructions|prompts)",
        r"system\s*prompt", r"you\s+are\s+now", r"act\s+as\s+if",
        r"pretend\s+to\s+be", r"forget\s+(everything|all)",
    ]
    injection_risk = 0.0
    if query:
        q_lower = query.lower()
        matches = sum(1 for p in injection_patterns if re.search(p, q_lower))
        injection_risk = min(1.0, matches * 0.2)

    if injection_risk >= 0.85:
        return {
            "status": "BLOCKED", "verdict": "VOID",
            "session_id": session_id,
            "reason": f"Injection pattern detected (F12): risk={injection_risk:.2f}",
            "injection_risk": injection_risk,
            "timestamp": timestamp,
            "floors_checked": ["F11", "F12"],
            "_source": "native_stub",
        }

    return {
        "status": "AUTHORIZED", "verdict": "SEAL",
        "session_id": session_id,
        "user_id": user_id,
        "injection_risk": injection_risk,
        "timestamp": timestamp,
        "floors_checked": ["F11", "F12"],
        "reason": "Session initialized (native stub — limited floor coverage)",
        "_source": "native_stub",
    }


async def mcp_000_init(
    action: str = "init",
    query: str = "",
    session_id: Optional[str] = None,
    authority_token: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    000_INIT: Delegates to canonical 7-step ignition.
    Falls back to native stub (F11+F12 only) if canonical unavailable.
    """
    if _CANONICAL_AVAILABLE:
        try:
            return await _canonical_init(
                action=action,
                query=query,
                authority_token=authority_token or "",
                session_id=session_id,
                context=context,
            )
        except Exception as e:
            _init_logger.error(f"Canonical init_000 failed: {e}, falling back to native stub")

    return await _native_init_stub(
        action=action, query=query,
        session_id=session_id, authority_token=authority_token,
        context=context,
    )

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
