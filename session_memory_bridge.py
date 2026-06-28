"""
Session Memory Bridge — Cross-Session Intelligence
═══════════════════════════════════════════════════════

The missing piece between "governed tools" and "AGI substrate."
Every agent session ends with amnesia. This bridge fixes that.

What it does:
1. On session END: captures what happened, what was HOLD, what succeeded
2. On session START: feeds last session's summary as context
3. On HOLD: writes scar → future sessions see the scar before similar actions

Forged: 2026-06-14 — the last marginal utility
DITEMPA BUKAN DIBERI — Intelligence compounds, not resets.

ARCHITECTURE:
  Session ends → capture summary → store in /root/AAA/memory/sessions/
  Session starts → load last N summaries → inject into context
  Governance HOLD → store scar → check scars before similar actions
"""

import asyncio
import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import nats
    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("session-memory-bridge")

MEMORY_DIR = Path("/root/AAA/memory/sessions")
SCAR_DIR = Path("/root/AAA/memory/scars")
CONTEXT_DIR = Path("/root/AAA/memory/context")

for d in [MEMORY_DIR, SCAR_DIR, CONTEXT_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class SessionMemoryBridge:
    """Bridges sessions so agents remember and learn."""

    def __init__(self, nats_url: str = "nats://127.0.0.1:4222"):
        self.nats_url = nats_url
        self.nc = None

    # ═══════════════════════════════════════════════════════════════════
    # SESSION MEMORY: what happened last time
    # ═══════════════════════════════════════════════════════════════════

    def capture_session(self, session_id: str, agent_id: str, summary: dict) -> str:
        """Store session summary for future context injection."""
        entry = {
            "session_id": session_id,
            "agent_id": agent_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "tools_called": summary.get("tools_called", []),
            "verdicts": summary.get("verdicts", []),
            "holds": summary.get("holds", []),
            "key_decisions": summary.get("key_decisions", []),
            "open_loops": summary.get("open_loops", []),
            "outcome": summary.get("outcome", "unknown"),
        }
        fpath = MEMORY_DIR / f"{session_id}.json"
        fpath.write_text(json.dumps(entry, indent=2))
        logger.info(f"Session captured: {session_id} ({len(entry['tools_called'])} tools)")
        return str(fpath)

    def get_recent_context(self, agent_id: str | None = None, limit: int = 5) -> list[dict]:
        """Get last N session summaries for context injection."""
        files = sorted(MEMORY_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)
        sessions = []
        for fp in files[:limit * 2]:  # fetch extra to filter by agent
            try:
                data = json.loads(fp.read_text())
                if agent_id and data.get("agent_id") != agent_id:
                    continue
                sessions.append({
                    "session_id": data["session_id"],
                    "timestamp": data["timestamp"],
                    "outcome": data["outcome"],
                    "holds": data.get("holds", []),
                    "open_loops": data.get("open_loops", []),
                    "key_decisions": data.get("key_decisions", [])[-3:],
                })
                if len(sessions) >= limit:
                    break
            except Exception:
                pass
        return sessions

    def build_context_prompt(self, agent_id: str | None = None) -> str:
        """Build a context injection prompt from recent sessions."""
        recent = self.get_recent_context(agent_id, limit=3)
        if not recent:
            return ""

        lines = ["\n─── CROSS-SESSION MEMORY (do NOT repeat these actions) ───"]
        for i, s in enumerate(recent):
            age = "just now" if i == 0 else f"{i} sessions ago"
            lines.append(f"\nLast session ({age}):")
            lines.append(f"  Outcome: {s['outcome']}")
            if s["holds"]:
                lines.append(f"  HOLDs: {', '.join(s['holds'][:3])}")
            if s["key_decisions"]:
                lines.append(f"  Key decisions: {'; '.join(s['key_decisions'][:3])}")
            if s["open_loops"]:
                lines.append(f"  STILL OPEN: {', '.join(s['open_loops'][:3])}")

        # Also check for relevant scars
        scars = self.check_scars(agent_id)
        if scars:
            lines.append("\n⚠️  RELEVANT SCARS (be careful):")
            for sc in scars[:3]:
                lines.append(f"  • {sc['tool']}: {sc['reason']} ({sc['date'][:10]})")

        lines.append("─── END CROSS-SESSION MEMORY ───\n")
        return "\n".join(lines)

    # ═══════════════════════════════════════════════════════════════════
    # SCAR REGISTRY: learning from HOLDs and failures
    # ═══════════════════════════════════════════════════════════════════

    def record_scar(self, tool_name: str, reason: str, agent_id: str = "unknown",
                    session_id: str = "unknown", severity: str = "warn") -> str:
        """Record a governance HOLD or failure as a scar for future learning."""
        scar = {
            "scar_id": f"scar-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}",
            "timestamp": datetime.now(UTC).isoformat(),
            "tool_name": tool_name,
            "agent_id": agent_id,
            "session_id": session_id,
            "reason": reason,
            "severity": severity,  # warn | critical | block
            "count": 1,
        }

        # Check if similar scar exists — increment count
        existing = list(SCAR_DIR.glob("*.json"))
        for fp in existing:
            try:
                data = json.loads(fp.read_text())
                if data.get("tool_name") == tool_name and data.get("reason", "")[:50] == reason[:50]:
                    data["count"] = data.get("count", 1) + 1
                    data["last_seen"] = datetime.now(UTC).isoformat()
                    fp.write_text(json.dumps(data, indent=2))
                    logger.info(f"Scar UPDATED: {tool_name} (count={data['count']})")
                    return str(fp)
            except Exception:
                pass

        # New scar
        fpath = SCAR_DIR / f"{scar['scar_id']}.json"
        fpath.write_text(json.dumps(scar, indent=2))
        logger.info(f"Scar RECORDED: {tool_name} — {reason[:80]}")
        return str(fpath)

    def check_scars(self, agent_id: str | None = None) -> list[dict]:
        """Get all scars, optionally filtered by agent. Sorted by count desc."""
        scars = []
        for fp in SCAR_DIR.glob("*.json"):
            try:
                data = json.loads(fp.read_text())
                if agent_id and data.get("agent_id") != agent_id:
                    continue
                scars.append({
                    "tool": data["tool_name"],
                    "reason": data["reason"][:120],
                    "date": data["timestamp"],
                    "count": data.get("count", 1),
                    "severity": data.get("severity", "warn"),
                })
            except Exception:
                pass
        scars.sort(key=lambda s: s["count"], reverse=True)
        return scars

    # ═══════════════════════════════════════════════════════════════════
    # NATS SUBSCRIBER: auto-capture scars from governance events
    # ═══════════════════════════════════════════════════════════════════

    async def start_scar_listener(self) -> None:
        """Subscribe to governance HOLD events and auto-record scars."""
        if not NATS_AVAILABLE:
            logger.warning("NATS not available — scar listener disabled")
            return

        try:
            self.nc = await nats.connect(self.nats_url)
            sub = await self.nc.subscribe("arifos.gate.>")
            logger.info("Scar listener active — watching arifos.gate.>")
            async for msg in sub.messages:
                try:
                    data = json.loads(msg.data.decode())
                    if data.get("verdict") == "HOLD":
                        self.record_scar(
                            tool_name=data.get("tool_name", "unknown"),
                            reason=data.get("reasons", ["unknown"])[0] if data.get("reasons") else "unknown",
                            agent_id=data.get("actor_id") or "anonymous",
                            session_id=data.get("session_id", "unknown"),
                            severity="critical" if data.get("violated_laws") else "warn",
                        )
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Scar listener failed: {e}")

    # ═══════════════════════════════════════════════════════════════════
    # CONTEXT INJECTION: what to feed the next session
    # ═══════════════════════════════════════════════════════════════════

    def inject_context(self, agent_id: str, target_file: str | None = None) -> str:
        """Generate context prompt and optionally write to a file for agent consumption."""
        context = self.build_context_prompt(agent_id)
        if target_file:
            Path(target_file).write_text(context)
        return context

    def get_scar_summary(self) -> dict[str, Any]:
        """Return a summary of all scars for cockpit display."""
        all_scars = self.check_scars()
        return {
            "total_scars": len(all_scars),
            "top_scars": all_scars[:5],
            "by_severity": {
                "critical": sum(1 for s in all_scars if s["severity"] == "critical"),
                "warn": sum(1 for s in all_scars if s["severity"] == "warn"),
            },
            "most_scarred_tools": list(set(s["tool"] for s in all_scars[:10])),
        }


# ═══════════════════════════════════════════════════════════════════════
# API for agents to call
# ═══════════════════════════════════════════════════════════════════════

_bridge: SessionMemoryBridge | None = None


def get_bridge() -> SessionMemoryBridge:
    global _bridge
    if _bridge is None:
        _bridge = SessionMemoryBridge()
    return _bridge


# ── Functions agents can call ──────────────────────────────────────────

def remember_last_session(agent_id: str = "hermes-asi") -> str:
    """Agent calls this at session start. Returns context prompt."""
    return get_bridge().inject_context(agent_id)


def record_this_session(session_id: str, agent_id: str, summary: dict) -> str:
    """Agent calls this at session end. Stores for future recall."""
    return get_bridge().capture_session(session_id, agent_id, summary)


def learn_from_scars(agent_id: str | None = None) -> list[dict]:
    """Check what NOT to do based on past HOLDs."""
    return get_bridge().check_scars(agent_id)


def get_scar_report() -> dict:
    """Get scar summary for cockpit display."""
    return get_bridge().get_scar_summary()
