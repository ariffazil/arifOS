"""
session_telemetry.py - Session Telemetry (T) for TEARFRAME v44

Tracks primary telemetry per session/turn: non-semantic counters & clocks.
Tracks T in the T -> R -> A -> F -> Ψ -> Verdict pipeline.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Optional

# Import Verdict from canon
from arifos_core.system.apex_prime import Verdict, normalize_verdict_code


@dataclass(frozen=True)
class TelemetrySnapshot:
    """Immutable snapshot of primary telemetry fields for a single turn."""

    # Timing
    t_start: float
    t_end: float
    delta_t: float
    session_duration: float

    # Counts
    tokens_in: int
    tokens_out: int
    turn_count: int
    verdict_counts: Dict[str, int]

    # Volume
    context_length_used: int
    kv_cache_size: int

    # Errors
    timeout: bool
    safety_block: bool
    truncation_flag: bool

    # Sampling
    temperature: float
    top_p: float
    top_k: Optional[int]

    # Verdict of this turn
    verdict: str


class SessionTelemetry:
    """
    Session Telemetry Tracker (T).

    Tracks accumulation of physics metrics over a session.
    """

    def __init__(self, max_session_tokens: int = 120000):
        self.max_session_tokens = max_session_tokens

        # Session state
        self.session_start_time = time.time()
        self.turn_count = 0
        self.total_tokens_in = 0
        self.total_tokens_out = 0

        # Counts
        self._verdict_counts: Dict[str, int] = {
            "SEAL": 0,
            "SABAR": 0,
            "PARTIAL": 0,
            "VOID": 0,
            "HOLD_888": 0,
            "SUNSET": 0,
        }

        # Current turn ephemeral state
        self._current_turn_start_time: float = 0.0
        self._current_turn_tokens_in: int = 0
        self._current_turn_temp: float = 0.0
        self._current_turn_top_p: float = 0.0
        self._current_turn_top_k: Optional[int] = None

        # History
        self.history: List[TelemetrySnapshot] = []

    def start_turn(
        self, *, tokens_in: int, temperature: float, top_p: float, top_k: Optional[int] = None
    ) -> None:
        """Start a new turn, recording input physics."""
        self.turn_count += 1
        self._current_turn_start_time = time.time()
        self._current_turn_tokens_in = tokens_in
        self.total_tokens_in += tokens_in

        self._current_turn_temp = temperature
        self._current_turn_top_p = top_p
        self._current_turn_top_k = top_k

    def end_turn(
        self,
        *,
        tokens_out: int,
        verdict: Verdict,
        context_length_used: int,
        kv_cache_size: int,
        timeout: bool,
        safety_block: bool,
        truncation_flag: bool,
        commit: bool = True,
    ) -> TelemetrySnapshot:
        """
        End current turn, recording output physics and finalizing snapshot.

        Args:
            commit: If True, commits to history/counts immediately.
                   If False, returns ephemeral snapshot (state unchanged).
        """
        t_end = time.time()
        # Ensure delta_t is positive and meaningful
        delta_t = max(0.001, t_end - self._current_turn_start_time)
        session_duration = t_end - self.session_start_time

        # Update verdict counts
        # Handle ApexVerdict, Verdict Enum, or string
        if hasattr(verdict, "value"):
            v_str = verdict.value
        else:
            v_str = str(verdict)

        # Uses Single Source of Truth for schema alignment
        v_str = normalize_verdict_code(v_str)

        # If committing, update persistent state
        if commit:
            self.total_tokens_out += tokens_out
            if v_str not in self._verdict_counts:
                self._verdict_counts[v_str] = 0
            self._verdict_counts[v_str] += 1

        # Create unique dict for this snapshot (copy)
        current_verdict_counts = self._verdict_counts.copy()

        # If NOT committing, we must simulate the increment for this snapshot
        if not commit:
            current_verdict_counts[v_str] = current_verdict_counts.get(v_str, 0) + 1

        snapshot = TelemetrySnapshot(
            t_start=self._current_turn_start_time,
            t_end=t_end,
            delta_t=delta_t,
            session_duration=session_duration,
            tokens_in=self._current_turn_tokens_in,
            tokens_out=tokens_out,
            turn_count=self.turn_count,
            verdict_counts=current_verdict_counts,
            context_length_used=context_length_used,
            kv_cache_size=kv_cache_size,
            timeout=timeout,
            safety_block=safety_block,
            truncation_flag=truncation_flag,
            temperature=self._current_turn_temp,
            top_p=self._current_turn_top_p,
            top_k=self._current_turn_top_k,
            verdict=v_str,
        )

        if commit:
            self.history.append(snapshot)

        return snapshot

    def commit_snapshot(self, snapshot: TelemetrySnapshot) -> None:
        """
        Commit a previously created ephemeral snapshot to history.
        Used when physics layer modifies the verdict before finalization.
        """
        # We need to respect the verdict IN the snapshot?
        # Or should we allow changing the verdict?
        # Usually the snapshot is immutable (frozen).
        # But if Physics overrides, we create a NEW snapshot or replace `verdict` field?
        # TelemetrySnapshot is @dataclass(frozen=True). We cannot modify it.
        # So we must recreate it if verdict changes.
        # But for 'commit', we assume snapshot is final.

        # Update counts based on snapshot
        v_str = snapshot.verdict
        if v_str not in self._verdict_counts:
            self._verdict_counts[v_str] = 0
        self._verdict_counts[v_str] += 1

        self.total_tokens_out += snapshot.tokens_out
        self.history.append(snapshot)

    def snapshot(self) -> TelemetrySnapshot:
        """Return the most recent snapshot."""
        if not self.history:
            raise ValueError("No history available")
        return self.history[-1]
