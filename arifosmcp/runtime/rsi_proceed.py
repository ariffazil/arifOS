"""RSI recording for the PERMISSION side of consequential decisions.

FI-003, 2026-10-29 — Phase 5 wiring, BOUNDED (Arif: "wiring PROCEED dengan had").

Why bounded
-----------
The Gödel Lock gate emits PROCEED only for SEAL-BOUND actions whose auditor
validated, and SABAR for the observation and reasoning tiers — i.e. for every
read. Recording every SABAR would record every read: noise at scale, and a
rate whose denominator is a firehose of non-decisions.

So this recorder owns exactly ONE population:

    a consequential (seal-bound) action that was ALLOWED

That is the only population where "false proceed" is even possible: a
mutation that was permitted and turned out wrong. HOLDs are NOT recorded here
— the tools.py refusal path owns the refusal population, and recording both
would double-count one decision.

The bound is visible, not silent: every suppression is counted and logged, and
the counters are readable via :func:`proceed_recorder_stats`.

Recording never changes a verdict. A failure inside the recorder is counted
and swallowed; a governance decision must not be taken hostage by its own
audit trail.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

from arifosmcp.runtime.rsi_audit import RSILedger, RSIDecisionRecord

logger = logging.getLogger(__name__)

CEILING_ENV = "ARIFOS_RSI_PROCEED_CEILING_PER_HOUR"
DEFAULT_CEILING_PER_HOUR = 500

# Verdicts this recorder owns. HOLD is excluded on purpose (see module docstring).
OWNED_VERDICTS = ("PROCEED", "SABAR")


class ProceedRecorder:
    """Bounded recorder for ALLOWED consequential decisions."""

    def __init__(
        self,
        ledger: RSILedger | None = None,
        *,
        ceiling_per_hour: int | None = None,
        now_fn: Any = None,
    ) -> None:
        self._ledger = ledger
        self._ceiling = (
            ceiling_per_hour
            if ceiling_per_hour is not None
            else int(os.environ.get(CEILING_ENV, DEFAULT_CEILING_PER_HOUR))
        )
        self._now = now_fn or time.time
        self._window: int | None = None
        self._recorded_this_window = 0
        self._counters: dict[str, int] = {
            "recorded": 0,
            "suppressed_by_scope": 0,
            "suppressed_by_ceiling": 0,
            "suppressed_hold": 0,
            "failed": 0,
        }

    # ── helpers ─────────────────────────────────────────────────────────────
    def _write_ledger(self) -> RSILedger:
        """The ledger this recorder writes to (the attribute shadowed the method once)."""
        if self._ledger is None:
            self._ledger = RSILedger()
        return self._ledger

    def _roll_window(self) -> None:
        window = int(self._now() // 3600)
        if self._window != window:
            self._window = window
            self._recorded_this_window = 0

    def stats(self) -> dict[str, Any]:
        self._roll_window()
        return {
            **self._counters,
            "ceiling_per_hour": self._ceiling,
            "recorded_this_window": self._recorded_this_window,
            "scope": "seal_bound_allowed_only",
        }

    # ── the record path ─────────────────────────────────────────────────────
    def record(
        self,
        *,
        verdict: str,
        seal_bound: bool,
        tool: str,
        reason_class: str = "EVIDENCE",
        severity_weight: float = 1.0,
        evidence: list[str] | None = None,
    ) -> dict[str, Any]:
        """Record one ALLOWED consequential decision. Never raises."""
        self._roll_window()
        v = str(verdict or "").upper()

        if v == "HOLD":
            self._counters["suppressed_hold"] += 1
            return {"recorded": False, "reason": "HOLD_OWNED_BY_REFUSAL_PATH"}

        if v not in OWNED_VERDICTS:
            self._counters["suppressed_by_scope"] += 1
            return {"recorded": False, "reason": "VERDICT_OUT_OF_SCOPE"}

        if not seal_bound:
            self._counters["suppressed_by_scope"] += 1
            return {"recorded": False, "reason": "NOT_SEAL_BOUND"}

        if self._recorded_this_window >= self._ceiling:
            self._counters["suppressed_by_ceiling"] += 1
            logger.warning(
                "rsi_proceed: hourly ceiling reached (%d/h) — recording suppressed, "
                "the decision itself is NOT affected",
                self._ceiling,
            )
            return {"recorded": False, "reason": "CEILING_REACHED"}

        try:
            decision = RSIDecisionRecord(
                tool=tool,
                original_verdict=v,
                reason_class=reason_class,
                severity_weight=severity_weight,
                evidence_available_at_decision=list(evidence or []),
            )
            self._write_ledger().record(decision)
            self._recorded_this_window += 1
            self._counters["recorded"] += 1
            return {
                "recorded": True,
                "reason": None,
                "decision_id": decision.decision_id,
            }
        except Exception as exc:  # noqa: BLE001 — an audit trail must not veto a decision
            self._counters["failed"] += 1
            logger.warning("rsi_proceed: recording failed (decision unaffected): %s", exc)
            return {"recorded": False, "reason": f"RECORD_FAILED:{type(exc).__name__}"}


_default_recorder: ProceedRecorder | None = None


def _get_recorder() -> ProceedRecorder:
    global _default_recorder
    if _default_recorder is None:
        _default_recorder = ProceedRecorder()
    return _default_recorder


def record_governed_proceed(
    *,
    verdict: str,
    seal_bound: bool,
    tool: str,
    reason_class: str = "EVIDENCE",
    severity_weight: float = 1.0,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    """Record an ALLOWED consequential decision (module-level entry point).

    Never raises and never changes the verdict it is told about.
    """
    try:
        return _get_recorder().record(
            verdict=verdict,
            seal_bound=seal_bound,
            tool=tool,
            reason_class=reason_class,
            severity_weight=severity_weight,
            evidence=evidence,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("rsi_proceed: recorder unavailable (decision unaffected): %s", exc)
        return {"recorded": False, "reason": "RECORDER_UNAVAILABLE"}


def proceed_recorder_stats() -> dict[str, Any]:
    """Visible counters for the bound (suppression is never silent)."""
    try:
        return _get_recorder().stats()
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}"}
