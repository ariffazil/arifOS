"""
mcp_log_bridge — Logging is transport; constitution is logic (Phase 1c).

Spec-locked 2026-07-09:
  - notifications/message NEVER auto-fires 888_HOLD by severity alone.
  - arifOS inspects structured `data` (floor, verdict, organ, tool).
  - Output is HOLD_CANDIDATE | NONE — never mutates vault, never self-authorizes.
  - Human / arif_judge path remains the only enforcement.

Usage:
  from arifosmcp.runtime.mcp_log_bridge import evaluate_log_for_hold, record_hold_candidate
  decision = evaluate_log_for_hold(level="alert", data={...})
  if decision.action == "HOLD_CANDIDATE":
      record_hold_candidate(decision, message=...)
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping

logger = logging.getLogger("arifos.mcp_log_bridge")

# Append-only candidate ledger (not VAULT999 — advisory trail for ops/judge)
_DEFAULT_CANDIDATE_LOG = Path(
    os.environ.get(
        "ARIFOS_MCP_LOG_HOLD_CANDIDATES",
        "/var/lib/arifos/vault/mcp_log_hold_candidates.jsonl",
    )
)

_HOLD_VERDICTS = frozenset(
    {
        "HOLD",
        "SABAR",
        "VOID",
        "BLOCK",
        "BLOCKED",
        "888_HOLD",
        "SOVEREIGN_HOLD",
        "PARTIAL",
    }
)
_ALERT_LEVELS = frozenset({"alert", "emergency"})
_CRITICAL_LEVELS = frozenset({"critical", "alert", "emergency"})


@dataclass(frozen=True)
class HoldDecision:
    """Result of evaluating a structured MCP log event."""

    action: str  # "NONE" | "HOLD_CANDIDATE"
    reason: str
    urgency: str  # info|warning|error|critical|alert|emergency
    floor: str | None = None
    verdict: str | None = None
    organ: str | None = None
    tool: str | None = None
    requires_human: bool = False
    data_snapshot: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_log_for_hold(
    *,
    level: str,
    data: Mapping[str, Any] | None = None,
    message: str = "",
) -> HoldDecision:
    """Map structured log data → HOLD_CANDIDATE or NONE.

    Rules (multiplicative evidence, not severity alone):
      1. data.verdict in HOLD set → HOLD_CANDIDATE
      2. data.floor == F13 or F13 in failed floors → HOLD_CANDIDATE + requires_human
      3. level in {alert, emergency} AND (verdict or floor present) → HOLD_CANDIDATE
      4. level alone without constitutional data → NONE (urgency signal only)

    Never calls arif_judge. Never seals.
    """
    d = dict(data or {})
    level_l = (level or "info").lower()
    verdict = str(d.get("verdict") or "").upper() or None
    floor = str(d.get("floor") or "").upper() or None
    organ = str(d.get("organ") or "") or None
    tool = str(d.get("tool") or "") or None

    # F13 / sovereign always human-required candidate
    if floor == "F13" or "F13" in str(d.get("failed_floors") or ""):
        return HoldDecision(
            action="HOLD_CANDIDATE",
            reason="F13/SOVEREIGN signal in structured log data",
            urgency="alert" if level_l not in _ALERT_LEVELS else level_l,
            floor=floor or "F13",
            verdict=verdict or "888_HOLD",
            organ=organ,
            tool=tool,
            requires_human=True,
            data_snapshot={k: d[k] for k in list(d)[:16]},
        )

    if verdict and verdict in _HOLD_VERDICTS:
        urgency = level_l if level_l in _CRITICAL_LEVELS else "error"
        if verdict in ("888_HOLD", "SOVEREIGN_HOLD"):
            urgency = "alert"
        return HoldDecision(
            action="HOLD_CANDIDATE",
            reason=f"verdict={verdict} in structured log data",
            urgency=urgency,
            floor=floor,
            verdict=verdict,
            organ=organ,
            tool=tool,
            requires_human=verdict in ("888_HOLD", "SOVEREIGN_HOLD", "VOID"),
            data_snapshot={k: d[k] for k in list(d)[:16]},
        )

    # High severity without constitutional anchors = do not escalate to HOLD
    if level_l in _ALERT_LEVELS and not verdict and not floor:
        return HoldDecision(
            action="NONE",
            reason="alert/emergency without floor/verdict — urgency only, no HOLD",
            urgency=level_l,
            organ=organ,
            tool=tool,
            data_snapshot={k: d[k] for k in list(d)[:8]},
        )

    return HoldDecision(
        action="NONE",
        reason="no constitutional hold signal in data",
        urgency=level_l,
        floor=floor,
        verdict=verdict,
        organ=organ,
        tool=tool,
    )


def record_hold_candidate(
    decision: HoldDecision,
    *,
    message: str = "",
    path: Path | None = None,
) -> bool:
    """Append HOLD_CANDIDATE to advisory jsonl. Fail-soft. Not VAULT999."""
    if decision.action != "HOLD_CANDIDATE":
        return False
    target = path or _DEFAULT_CANDIDATE_LOG
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        rec = {
            "ts": time.time(),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "kind": "MCP_LOG_HOLD_CANDIDATE",
            "message": (message or "")[:300],
            "decision": decision.to_dict(),
            "enforcement": "NONE — advisory only; arif_judge / F13 human path required",
        }
        with open(target, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
        logger.warning(
            "HOLD_CANDIDATE organ=%s tool=%s verdict=%s floor=%s reason=%s",
            decision.organ,
            decision.tool,
            decision.verdict,
            decision.floor,
            decision.reason,
        )
        return True
    except Exception as e:
        logger.debug("record_hold_candidate failed: %s", e)
        return False


def evaluate_and_record(
    *,
    level: str,
    data: Mapping[str, Any] | None,
    message: str = "",
) -> HoldDecision:
    """Convenience: evaluate + record if candidate. Safe to call from emit path."""
    decision = evaluate_log_for_hold(level=level, data=data, message=message)
    if decision.action == "HOLD_CANDIDATE":
        record_hold_candidate(decision, message=message)
    return decision
