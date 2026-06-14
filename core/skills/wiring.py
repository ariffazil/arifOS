"""
ORGAN STATE CACHE + GOVERNANCE LOG BRIDGE
=========================================
Forged: 2026-06-14 by FORGE (000Ω)
Target: arifOS core/skills/wiring.py
Purpose: Shared wiring layer that all 3 kernel skills use to access:
         1. NATS governance stream (for threat_score + autonomy_calibration)
         2. Organ state cache (for scenario_policy)
         3. VAULT999 governance logs (for autonomy_calibration baselines)

Single import point. All skills wire through here.
"""

import json
import time
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

# ─── ORGAN STATE CACHE ────────────────────────────────────────────

@dataclass
class OrganState:
    organ_id: str
    health: str  # HEALTHY | DEGRADED | OFFLINE
    tools_available: int
    tools_total: int
    last_attest: Optional[datetime] = None
    risk_score: float = 0.0
    extra: dict = field(default_factory=dict)

# In-memory cache with TTL
_organ_cache: dict[str, OrganState] = {}
_cache_ttl: float = 60.0  # seconds
_last_attest: float = 0.0


def get_organ_state(organ_id: str) -> Optional[OrganState]:
    """Get cached organ state. Returns None if stale or missing."""
    if time.time() - _last_attest > _cache_ttl:
        return None  # cache expired
    return _organ_cache.get(organ_id)


def refresh_organ_cache(attest_result: dict):
    """Refresh organ cache from arif_organ_attest_all() output."""
    global _last_attest
    _organ_cache.clear()
    
    # Parse attest_all output
    organs = attest_result.get("organs", attest_result.get("attested", []))
    if isinstance(organs, list):
        for org in organs:
            if isinstance(org, dict):
                oid = org.get("organ_id", org.get("id", ""))
                _organ_cache[oid] = OrganState(
                    organ_id=oid,
                    health=org.get("health", org.get("status", "UNKNOWN")),
                    tools_available=org.get("tools_available", org.get("healthy_tools", 0)),
                    tools_total=org.get("tools_total", org.get("total_tools", 0)),
                    last_attest=datetime.now(timezone.utc),
                    risk_score=org.get("risk_score", 0.0),
                    extra=org.get("extra", {}),
                )
    
    _last_attest = time.time()


def get_all_organ_states() -> dict[str, str]:
    """Get organ_id → health_status for all cached organs."""
    if time.time() - _last_attest > _cache_ttl:
        return {}
    return {oid: state.health for oid, state in _organ_cache.items()}


def get_organ_snapshot() -> dict:
    """
    Return full organ state snapshot for scenario_policy evaluation.
    Format: { organ_id: { metric: value, ... }, ... }
    """
    if time.time() - _last_attest > _cache_ttl:
        return {}
    
    snapshot = {}
    for oid, state in _organ_cache.items():
        snapshot[oid] = {
            "health": state.health,
            "risk_score": state.risk_score,
            "tools_available": state.tools_available,
            "tools_total": state.tools_total,
        }
    return snapshot


# ─── GOVERNANCE LOG QUERIES ───────────────────────────────────────

def load_governance_log(events_file: str = "/root/arifOS/logs/governance.jsonl",
                        lookback_hours: int = 168) -> list[dict]:
    """
    Load governance events from local JSONL log.
    Falls back to empty list if file doesn't exist.
    """
    events = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    log_path = Path(events_file)
    
    if not log_path.exists():
        return events
    
    try:
        with open(log_path) as f:
            for line in f:
                try:
                    evt = json.loads(line.strip())
                    ts = evt.get("timestamp", "")
                    if ts:
                        evt_time = datetime.fromisoformat(ts)
                        if evt_time >= cutoff:
                            events.append(evt)
                except (json.JSONDecodeError, ValueError):
                    continue
    except Exception:
        pass
    
    return events


def compute_tool_metrics(events: list[dict], tool_name: str) -> dict:
    """
    Compute HOLD rate, override rate, etc. for a specific tool.
    Used by autonomy_calibration.
    """
    tool_events = [e for e in events if e.get("tool") == tool_name]
    total = len(tool_events)
    holds = sum(1 for e in tool_events if e.get("verdict") in ("HOLD", "BLOCK"))
    overrides = sum(1 for e in tool_events if e.get("verdict") == "OVERRIDE")
    
    return {
        "tool_name": tool_name,
        "total_invocations": total,
        "hold_count": holds,
        "override_count": overrides,
        "hold_rate": holds / total if total > 0 else 0.0,
        "override_rate": overrides / holds if holds > 0 else 0.0,
    }


def compute_all_tool_metrics(events: list[dict]) -> list[dict]:
    """Compute metrics for ALL tools in the event log."""
    tools = set(e.get("tool", "unknown") for e in events)
    return [compute_tool_metrics(events, t) for t in tools]


# ─── VAULT999 QUERY ───────────────────────────────────────────────

def query_vault_seals(lookback_hours: int = 720) -> list[dict]:
    """
    Query recent VAULT999 seals for governance analysis.
    Falls back to local JSONL if API unavailable.
    """
    vault_file = Path("/root/arifOS/VAULT999/seals.jsonl")
    if not vault_file.exists():
        return []
    
    seals = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    
    try:
        with open(vault_file) as f:
            for line in f:
                try:
                    seal = json.loads(line.strip())
                    ts = seal.get("timestamp", "")
                    if ts:
                        seal_time = datetime.fromisoformat(ts)
                        if seal_time >= cutoff:
                            seals.append(seal)
                except (json.JSONDecodeError, ValueError):
                    continue
    except Exception:
        pass
    
    return seals


# ─── CONVENIENCE: FULL SNAPSHOT ────────────────────────────────────

def get_full_wiring_snapshot() -> dict:
    """
    Return everything the kernel skills need in one call:
    - Organ states
    - Recent governance events
    - Recent VAULT seals
    - Tool metrics
    """
    organ_states = get_all_organ_states()
    events = load_governance_log(lookback_hours=24)
    seals = query_vault_seals(lookback_hours=720)
    tool_metrics = compute_all_tool_metrics(events)
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "organs": {oid: {"health": h} for oid, h in organ_states.items()},
        "events_last_24h": len(events),
        "seals_last_30d": len(seals),
        "tools_tracked": len(tool_metrics),
        "tool_metrics": tool_metrics,
        "cache_fresh": time.time() - _last_attest < _cache_ttl,
    }


# ─── SELF-TEST ────────────────────────────────────────────────────
if __name__ == "__main__":
    snapshot = get_full_wiring_snapshot()
    print(f"🧠 Wiring snapshot: {snapshot['events_last_24h']} events, "
          f"{snapshot['tools_tracked']} tools tracked, "
          f"cache_fresh={snapshot['cache_fresh']}")
    print("DITEMPA BUKAN DIBERI — wiring layer ready.")
