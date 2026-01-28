# arifos/mcp/constitutional_metrics.py
"""
arifOS Monitoring Metrics (v53.0.0)

Tracks tool usage, verdicts, sessions for live dashboard monitoring.
Similar to Serena's dashboard but for constitutional governance.
"""

from dataclasses import dataclass, field
import time
import threading
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

@dataclass
class Counter:
    name: str
    help: str
    _values: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def inc(self, labels: Dict[str, str], value: float = 1.0):
        key = "_".join(f"{k}:{v}" for k, v in sorted(labels.items()))
        with self._lock:
            self._values[key] += value

    def get_all(self) -> Dict[str, float]:
        with self._lock:
            return dict(self._values)

@dataclass
class Histogram:
    name: str
    help: str
    _values: List[float] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def observe(self, value: float):
        with self._lock:
            self._values.append(value)
            # Keep last 1000 observations
            if len(self._values) > 1000:
                self._values = self._values[-1000:]

    def get_stats(self) -> Dict[str, float]:
        with self._lock:
            if not self._values:
                return {"p50": 0, "p95": 0, "p99": 0, "avg": 0}
            sorted_vals = sorted(self._values)
            n = len(sorted_vals)
            return {
                "p50": sorted_vals[int(n * 0.5)] if n > 0 else 0,
                "p95": sorted_vals[int(n * 0.95)] if n > 0 else 0,
                "p99": sorted_vals[int(n * 0.99)] if n > 0 else 0,
                "avg": sum(sorted_vals) / n if n > 0 else 0
            }

@dataclass
class Gauge:
    name: str
    help: str
    _value: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def set(self, value: float):
        with self._lock:
            self._value = value

    def get(self) -> float:
        with self._lock:
            return self._value

# ============================================================================
# CORE METRICS (existing)
# ============================================================================
F11_COMMAND_AUTH = Counter('arifos_f11_total', 'F11 decisions')
CONSTITUTIONAL_REFLEX = Histogram('arifos_reflex_duration', 'Verdict latency (ms)')
SEAL_RATE = Gauge('arifos_seal_rate_1h', 'Rolling SEAL rate')

# ============================================================================
# TOOL USAGE TRACKING (new - like Serena's dashboard)
# ============================================================================
_TOOL_CALLS: Dict[str, int] = defaultdict(int)
_TOOL_LOCK = threading.Lock()

# Recent executions (tool, verdict, timestamp, duration_ms)
_RECENT_EXECUTIONS: List[Dict[str, Any]] = []
_EXEC_LOCK = threading.Lock()

# Verdict distribution
_VERDICT_COUNTS: Dict[str, int] = defaultdict(int)
_VERDICT_LOCK = threading.Lock()

# Verdicts with timestamps (for rolling window)
_VERDICTS: List[tuple] = []  # (timestamp, verdict)

# Active sessions tracking
_ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}  # session_id -> {started_at, tool_calls, last_activity}
_SESSION_LOCK = threading.Lock()

# =============================================================================
# SESSION BUNDLE STORE (Mid-Session Context Passing)
# =============================================================================
# Stores stage results indexed by session_id for inter-stage communication
# This enables: agi_genius → store → asi_act retrieves → store → apex_judge retrieves
_SESSION_BUNDLES: Dict[str, Dict[str, Any]] = {}  # session_id -> {agi_result, asi_result, apex_result}
_BUNDLE_LOCK = threading.Lock()


def store_stage_result(session_id: str, stage: str, result: Dict[str, Any]) -> None:
    """
    Store a stage result for later retrieval by subsequent stages.

    Args:
        session_id: The session identifier
        stage: One of "agi", "asi", "apex", "init"
        result: The stage output to store
    """
    if not session_id:
        return  # No session, can't store

    with _BUNDLE_LOCK:
        if session_id not in _SESSION_BUNDLES:
            _SESSION_BUNDLES[session_id] = {
                "created_at": time.time(),
                "agi_result": None,
                "asi_result": None,
                "apex_result": None,
                "init_result": None
            }

        key = f"{stage}_result"
        if key in _SESSION_BUNDLES[session_id]:
            _SESSION_BUNDLES[session_id][key] = result
            _SESSION_BUNDLES[session_id]["last_updated"] = time.time()


def get_stage_result(session_id: str, stage: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a stored stage result.

    Args:
        session_id: The session identifier
        stage: One of "agi", "asi", "apex", "init"

    Returns:
        The stored result or None if not found
    """
    if not session_id:
        return None

    with _BUNDLE_LOCK:
        if session_id not in _SESSION_BUNDLES:
            return None

        key = f"{stage}_result"
        return _SESSION_BUNDLES[session_id].get(key)


def get_session_bundle(session_id: str) -> Dict[str, Any]:
    """
    Get all stored stage results for a session.

    Args:
        session_id: The session identifier

    Returns:
        Dictionary with all stage results
    """
    with _BUNDLE_LOCK:
        return _SESSION_BUNDLES.get(session_id, {}).copy()


def clear_session_bundle(session_id: str) -> None:
    """
    Clear all stored results for a session (call on 999_vault seal).
    """
    with _BUNDLE_LOCK:
        _SESSION_BUNDLES.pop(session_id, None)


def cleanup_stale_bundles(max_age_seconds: int = 1800) -> int:
    """
    Remove bundles older than max_age_seconds (default 30 min).

    Returns:
        Number of bundles cleaned up
    """
    now = time.time()
    with _BUNDLE_LOCK:
        stale = [
            sid for sid, data in _SESSION_BUNDLES.items()
            if now - data.get("created_at", now) > max_age_seconds
        ]
        for sid in stale:
            del _SESSION_BUNDLES[sid]
        return len(stale)


# Server start time
_SERVER_START = time.time()

# ============================================================================
# TRINITY SCORE TRACKING (AGI τ, ASI κᵣ, APEX Ψ)
# ============================================================================
_TRINITY_SCORES: Dict[str, List[float]] = {
    "tau": [],       # τ: Truth accuracy (AGI Mind)
    "kappa_r": [],   # κᵣ: Empathy resonance (ASI Heart)
    "psi": []        # Ψ: Vitality/Judgment (APEX Soul)
}
_TRINITY_LOCK = threading.Lock()

def record_tool_call(tool: str):
    """Record a tool invocation."""
    with _TOOL_LOCK:
        _TOOL_CALLS[tool] += 1

def record_verdict(tool: str, verdict: str, duration: float, mode: str = "standard"):
    """Record a verdict and its metadata."""
    now = time.time()

    # Legacy metrics
    F11_COMMAND_AUTH.inc({"verdict": verdict, "tool": tool, "mode": mode})
    CONSTITUTIONAL_REFLEX.observe(duration)

    # Tool call tracking
    record_tool_call(tool)

    # Verdict distribution
    with _VERDICT_LOCK:
        _VERDICT_COUNTS[verdict] += 1
        _VERDICTS.append((now, verdict))
        # Keep only last hour
        while _VERDICTS and _VERDICTS[0][0] < now - 3600:
            _VERDICTS.pop(0)

        # Calculate SEAL rate
        if _VERDICTS:
            seals = sum(1 for _, v in _VERDICTS if v == "SEAL")
            SEAL_RATE.set(seals / len(_VERDICTS))

    # Recent executions (keep last 50)
    with _EXEC_LOCK:
        _RECENT_EXECUTIONS.insert(0, {
            "tool": tool,
            "verdict": verdict,
            "timestamp": datetime.fromtimestamp(now).isoformat(),
            "duration_ms": round(duration, 2),
            "mode": mode
        })
        if len(_RECENT_EXECUTIONS) > 50:
            _RECENT_EXECUTIONS.pop()

def record_session_activity(session_id: str, tool: str):
    """Track session activity."""
    with _SESSION_LOCK:
        if session_id not in _ACTIVE_SESSIONS:
            _ACTIVE_SESSIONS[session_id] = {
                "started_at": datetime.now().isoformat(),
                "tool_calls": 0,
                "last_activity": datetime.now().isoformat(),
                "tools_used": []
            }
        _ACTIVE_SESSIONS[session_id]["tool_calls"] += 1
        _ACTIVE_SESSIONS[session_id]["last_activity"] = datetime.now().isoformat()
        if tool not in _ACTIVE_SESSIONS[session_id]["tools_used"]:
            _ACTIVE_SESSIONS[session_id]["tools_used"].append(tool)

def close_session(session_id: str):
    """Mark a session as closed."""
    with _SESSION_LOCK:
        _ACTIVE_SESSIONS.pop(session_id, None)

def get_seal_rate() -> float:
    """Get the current rolling SEAL rate."""
    return SEAL_RATE.get()

def get_tool_usage() -> Dict[str, int]:
    """Get tool call counts."""
    with _TOOL_LOCK:
        return dict(_TOOL_CALLS)

def get_verdict_distribution() -> Dict[str, int]:
    """Get verdict distribution."""
    with _VERDICT_LOCK:
        return dict(_VERDICT_COUNTS)

def get_recent_executions(limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent tool executions."""
    with _EXEC_LOCK:
        return _RECENT_EXECUTIONS[:limit]

def get_active_sessions() -> Dict[str, Dict[str, Any]]:
    """Get active sessions."""
    with _SESSION_LOCK:
        # Clean up stale sessions (no activity for 30 min)
        now = time.time()
        stale = []
        for sid, data in _ACTIVE_SESSIONS.items():
            try:
                last = datetime.fromisoformat(data["last_activity"])
                if (datetime.now() - last).total_seconds() > 1800:
                    stale.append(sid)
            except:
                pass
        for sid in stale:
            _ACTIVE_SESSIONS.pop(sid, None)

        return dict(_ACTIVE_SESSIONS)

def get_uptime_hours() -> float:
    """Get server uptime in hours."""
    return round((time.time() - _SERVER_START) / 3600, 2)

def get_full_metrics() -> Dict[str, Any]:
    """
    Get complete metrics snapshot for dashboard.
    This is what /metrics/json returns.
    """
    tool_usage = get_tool_usage()
    verdict_dist = get_verdict_distribution()
    recent = get_recent_executions(20)
    sessions = get_active_sessions()
    latency = CONSTITUTIONAL_REFLEX.get_stats()

    total_calls = sum(tool_usage.values())
    total_verdicts = sum(verdict_dist.values())

    return {
        "status": "active",
        "uptime_hours": get_uptime_hours(),
        "version": "v53.0.0-SEAL",

        # Tool usage (like Serena's dashboard)
        "tool_usage": tool_usage,
        "total_tool_calls": total_calls,

        # Verdict distribution
        "verdict_distribution": verdict_dist,
        "seal_rate": get_seal_rate(),
        "void_rate": verdict_dist.get("VOID", 0) / total_verdicts if total_verdicts > 0 else 0,

        # Sessions
        "active_sessions": len(sessions),
        "sessions": sessions,

        # Latency stats
        "latency_ms": latency,

        # Recent executions
        "recent_executions": recent,

        # Floor health (simplified - all green by default)
        "floor_health": {
            "F1_amanah": True,
            "F2_truth": True,
            "F3_tri_witness": True,
            "F4_clarity": True,
            "F5_peace": True,
            "F6_empathy": True,
            "F7_humility": True,
            "F8_genius": True,
            "F9_dark": True,
            "F10_ontology": True,
            "F11_auth": True,
            "F12_injection": True,
            "F13_curiosity": True
        },

        # Trinity scores (placeholder - computed by kernels)
        "trinity": {
            "agi_mind": {"truth": 0.99, "clarity": 0.95, "humility": 0.04},
            "asi_heart": {"empathy": 0.96, "peace": 1.0, "amanah": True},
            "apex_soul": {"genius": 0.85, "dark": 0.12, "witnesses": 0.97}
        },

        # Entropy (thermodynamic metaphor)
        "entropy_delta": -0.042
    }
