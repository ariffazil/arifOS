"""
arifosmcp/runtime/budget_contract.py — AAA Budget Contract Enforcement Layer
==========================================================================

A-FORGE enforces the shared budget contract owned by AAA.

Contract: contracts/budget/AAA-GOV-BUDGET-v1.json
AAA defines. A-FORGE enforces. arifOS judges.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Locate the budget contract ──────────────────────────────────────────────
_CONTRACT_PATHS = [
    Path("/srv/openclaw/workspace/arifOS/contracts/budget/AAA-GOV-BUDGET-v1.json"),
    Path("/app/arifosmcp/contracts/budget/AAA-GOV-BUDGET-v1.json"),
    Path("/root/arifOS/contracts/budget/AAA-GOV-BUDGET-v1.json"),
]

DEFAULT_CONTRACT = {
    "policy_id": "AAA-GOV-BUDGET-v1",
    "version": "1.0.0",
    "limits": {
        "max_turns": 8,
        "max_tool_calls": 12,
        "max_same_tool_calls": 2,
        "max_retries_per_tool": 1,
        "max_no_progress_turns": 2,
        "max_context_percent": 0.75,
    },
    "on_violation": "888_HOLD",
}


@dataclass
class BudgetSnapshot:
    """Point-in-time budget state for a session."""

    session_id: str
    turns: int = 0
    tool_calls: int = 0
    same_tool_calls: int = 0
    retries: int = 0
    no_progress_turns: int = 0
    context_percent: float = 0.0
    last_tool: str | None = None
    last_action: str | None = None
    policy_id: str = "AAA-GOV-BUDGET-v1"
    held: bool = False
    hold_reason: str | None = None


class BudgetContract:
    """
    Budget contract enforcement for a single session.

    Loads AAA-GOV-BUDGET-v1.json and enforces all limits.
    On violation: emits 888_HOLD, logs to RunLedger.
    """

    def __init__(self, session_id: str, contract_path: Path | None = None):
        self.session_id = session_id
        self._lock = threading.RLock()
        self._snap = BudgetSnapshot(session_id=session_id)
        self._contract = self._load_contract(contract_path)
        self._limits = self._contract.get("limits", DEFAULT_CONTRACT["limits"])
        self._on_violation = self._contract.get("on_violation", "888_HOLD")
        self._policy_id = self._contract.get("policy_id", "AAA-GOV-BUDGET-v1")

    def _load_contract(self, contract_path: Path | None = None) -> dict[str, Any]:
        """Load the budget contract from disk."""
        if contract_path and contract_path.exists():
            try:
                logger.info(f"Budget contract loaded from {contract_path}")
                with open(contract_path) as fh:
                    return json.load(fh)
            except Exception as e:
                logger.warning(f"Could not load contract from {contract_path}: {e}")

        for path in _CONTRACT_PATHS:
            if path.exists():
                try:
                    logger.info(f"Budget contract loaded from {path}")
                    return json.load(open(path))
                except Exception as e:
                    logger.warning(f"Could not load {path}: {e}")

        logger.warning("No budget contract found — using defaults.")
        return DEFAULT_CONTRACT

    # ── Enforcement checks ─────────────────────────────────────────────────

    def check_turn(self) -> tuple[bool, str | None]:
        """Check if another turn is allowed."""
        if self._snap.held:
            return False, self._snap.hold_reason
        max_turns = self._limits.get("max_turns", 8)
        if self._snap.turns >= max_turns:
            msg = f"888_HOLD: max_turns ({max_turns}) reached"
            self._emit_hold(msg)
            return False, msg
        return True, None

    def check_tool_call(self, tool_name: str) -> tuple[bool, str | None]:
        """
        Check if a tool call is allowed.

        Priority:
        1. Already held → block
        2. Same tool repeated > max_same_tool_calls → block
        3. Total calls > max_tool_calls → block
        """
        if self._snap.held:
            return False, self._snap.hold_reason

        max_same = self._limits.get("max_same_tool_calls", 2)
        if tool_name == self._snap.last_tool and self._snap.same_tool_calls >= max_same:
            msg = f"888_HOLD: max_same_tool_calls ({max_same}) for {tool_name}"
            self._emit_hold(msg)
            return False, msg

        max_calls = self._limits.get("max_tool_calls", 12)
        if self._snap.tool_calls >= max_calls:
            msg = f"888_HOLD: max_tool_calls ({max_calls}) reached"
            self._emit_hold(msg)
            return False, msg

        return True, None

    def check_retry(self, tool_name: str) -> tuple[bool, str | None]:
        """Check if a retry of a failed tool is allowed."""
        if self._snap.held:
            return False, self._snap.hold_reason
        max_retries = self._limits.get("max_retries_per_tool", 1)
        if self._snap.retries >= max_retries:
            msg = f"888_HOLD: max_retries_per_tool ({max_retries}) exceeded for {tool_name}"
            self._emit_hold(msg)
            return False, msg
        return True, None

    def check_progress(self, made_progress: bool) -> tuple[bool, str | None]:
        """
        Check if session is making forward progress.
        If no progress: increment counter, block if exceeded.
        If made progress: reset counter.
        """
        if self._snap.held:
            return False, self._snap.hold_reason

        if made_progress:
            self._snap.no_progress_turns = 0
            return True, None

        max_noprogress = self._limits.get("max_no_progress_turns", 2)
        self._snap.no_progress_turns += 1
        if self._snap.no_progress_turns >= max_noprogress:
            msg = f"888_HOLD: max_no_progress_turns ({max_noprogress}) exceeded"
            self._emit_hold(msg)
            return False, msg
        return True, None

    def check_context(self, context_percent: float) -> tuple[bool, str | None]:
        """Check if context usage is within budget."""
        if self._snap.held:
            return False, self._snap.hold_reason
        max_ctx = self._limits.get("max_context_percent", 0.75)
        if context_percent > max_ctx:
            msg = f"888_HOLD: context ({context_percent:.0%}) exceeds budget ({max_ctx:.0%})"
            self._emit_hold(msg)
            return False, msg
        return True, None

    # ── State mutation ─────────────────────────────────────────────────────

    def record_turn(self, action: str | None = None) -> None:
        """Record one turn advancing."""
        with self._lock:
            self._snap.turns += 1
            self._snap.last_action = action

    def record_tool_call(self, tool_name: str) -> None:
        """Record one tool call. Updates same_tool_calls counter."""
        with self._lock:
            self._snap.tool_calls += 1
            if tool_name == self._snap.last_tool:
                self._snap.same_tool_calls += 1
            else:
                self._snap.same_tool_calls = 1
                self._snap.last_tool = tool_name
                self._snap.retries = 0  # new tool resets retry counter

    def record_retry(self) -> None:
        """Record a retry of a failed tool."""
        with self._lock:
            self._snap.retries += 1

    def record_no_progress(self) -> None:
        """Record a turn with no forward progress (called by check_progress)."""
        # No-op — counter managed inside check_progress

    def record_context_usage(self, percent: float) -> None:
        """Record current context usage percent."""
        self._snap.context_percent = percent

    # ── Hold emission ──────────────────────────────────────────────────────

    def _emit_hold(self, reason: str) -> None:
        """Emit 888_HOLD and log to RunLedger."""
        with self._lock:
            self._snap.held = True
            self._snap.hold_reason = reason
        self._log_to_vault(reason)
        logger.critical(
            f"BUDGET CONTRACT VIOLATION [{self._policy_id}] session={self.session_id} "
            f"reason={reason}"
        )

    def _log_to_vault(self, reason: str) -> None:
        """Append violation record to the budget audit log."""
        try:
            audit_dir = Path(os.getenv("TELEMETRY_PATH", "/app/telemetry"))
            audit_dir.mkdir(parents=True, exist_ok=True)
            audit_file = audit_dir / "budget_violations.jsonl"
            entry = {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "policy_id": self._policy_id,
                "session_id": self.session_id,
                "event": "888_HOLD",
                "reason": reason,
                "snapshot": {
                    "turns": self._snap.turns,
                    "tool_calls": self._snap.tool_calls,
                    "same_tool_calls": self._snap.same_tool_calls,
                    "retries": self._snap.retries,
                    "no_progress_turns": self._snap.no_progress_turns,
                    "context_percent": self._snap.context_percent,
                    "last_tool": self._snap.last_tool,
                },
            }
            with open(audit_file, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Could not write budget violation to vault: {e}")

    # ── Snapshot & status ───────────────────────────────────────────────────

    def snapshot(self) -> BudgetSnapshot:
        """Return current budget state."""
        with self._lock:
            return BudgetSnapshot(
                session_id=self._snap.session_id,
                turns=self._snap.turns,
                tool_calls=self._snap.tool_calls,
                same_tool_calls=self._snap.same_tool_calls,
                retries=self._snap.retries,
                no_progress_turns=self._snap.no_progress_turns,
                context_percent=self._snap.context_percent,
                last_tool=self._snap.last_tool,
                last_action=self._snap.last_action,
                policy_id=self._policy_id,
                held=self._snap.held,
                hold_reason=self._snap.hold_reason,
            )

    def is_held(self) -> bool:
        """Return True if session is in 888_HOLD state."""
        return self._snap.held

    def hold_reason(self) -> str | None:
        """Return the hold reason if held, else None."""
        return self._snap.hold_reason

    def reset(self) -> None:
        """Reset budget state for new session."""
        with self._lock:
            self._snap = BudgetSnapshot(session_id=self.session_id)

    def limits(self) -> dict[str, Any]:
        """Return current limits."""
        return dict(self._limits)


# ── Global budget registry ─────────────────────────────────────────────────

_budget_registry: dict[str, BudgetContract] = {}
_registry_lock = threading.RLock()


def get_budget_contract(session_id: str) -> BudgetContract:
    """Get or create budget contract for a session."""
    with _registry_lock:
        if session_id not in _budget_registry:
            _budget_registry[session_id] = BudgetContract(session_id=session_id)
        return _budget_registry[session_id]


def clear_budget_contract(session_id: str) -> None:
    """Remove budget contract (session ended)."""
    with _registry_lock:
        _budget_registry.pop(session_id, None)
