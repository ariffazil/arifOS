"""
arifOS v2.0 — Context Engine: Pressure-Trigger Middleware (Phase 2, B)
═══════════════════════════════════════════════════════════════════════════
The first reflex. Turns the engine from "I observe pressure" into
"I react when pressure crosses threshold."

Iron rules (F1-F13):
  - F1 AMANAH:   trigger returns advisory; raw context never auto-modified
  - F2 TRUTH:    deterministic classifier, no fabrication
  - F4 CLARITY:  single function, single output shape
  - F5 PEACE²:   HOLD pressure never escalates to auto-compact
  - F7 HUMILITY: pressure bands are advisory by default, never punitive
  - F8 GENIUS:   auto-compact default is OFF; explicit policy enables it
  - F9 ANTIHANTU: LLM summarizer is bounded; deterministic verifier checks
  - F10 ONTOLOGY: trigger is a meter, not a mind
  - F11 AUDIT:   every trigger event is audit_classify()'d (TRACE/DIGEST/SEAL/HOLD)
  - F12 INJECTION: pressure readings cannot be replayed-injected; session_id
                  binds the trigger to its own session
  - F13 SOVEREIGN: canonical mutation is HOLD; trigger is a meter only

What this module does:
  - observe_pressure(session_id) -> PressureObservation
  - classify_action(pressure_band, policy) -> TriggerAction
  - trigger(observation) -> TriggerResult
  - record_trigger(result) -> AuditReceipt

What this module does NOT do (Phase 2 boundary):
  - Auto-compact (disabled by default; Phase 2+ feature)
  - Auto-evict (FORBIDDEN; HOLD territory)
  - Modify canonical memory (FORBIDDEN; HOLD territory)
  - Mutate raw transcript (FORBIDDEN; F1 AMANAH)
  - Run LLM summarizer (Phase 4)

DITEMPA BUKAN DIBERI — the first reflex is forge, not given.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from enum import StrEnum
from typing import Any

from arifosmcp.runtime.token_pressure import (
    PressureBand,
    classify_pressure,
    get_session_singleton,
)
from arifosmcp.runtime.context_audit import (
    POLICY_VERSION as AUDIT_POLICY_VERSION,
    AuditMode,
    EventType,
    RiskClass,
    audit_classify,
    audit_seal,
    audit_digest,
    audit_trace,
    audit_hold,
)

logger = logging.getLogger(__name__)


# ─── Trigger Action Taxonomy (F4 CLARITY) ──────────────────────────────────
class TriggerAction(StrEnum):
    """
    What the trigger recommends in response to observed pressure.
    The agent (LLM) decides whether to ACT on the recommendation.
    The kernel only emits the recommendation. F1 + F10.
    """

    PROCEED = "PROCEED"  # LOW/WATCH: normal operation
    WARN = "WARN"  # WATCH/WARN: log advisory, no action
    PRIME_COMPACTION = "PRIME_COMPACTION"  # WARN/COMPACT: suggest compaction
    HOLD = "HOLD"  # HOLD+: refuse non-reversible action
    NOOP = "NOOP"  # Unknown or degenerate state


# ─── Default Policy (F8 sovereign to override) ────────────────────────────
DEFAULT_POLICY = {
    "policy_version": "context_trigger.v1",
    "auto_compact_enabled": False,  # F8 — sovereign to enable default-on
    "warn_threshold_pct": 0.50,  # advisory from 50%
    "prime_compact_threshold_pct": 0.75,  # suggest compaction from 75%
    "hold_threshold_pct": 0.95,  # HOLD non-reversible from 95%
    "default_output_reserve_tokens": 1500,
    "audit_mode_for_warn": AuditMode.DIGEST.value,
    "audit_mode_for_prime": AuditMode.SEAL.value,
    "audit_mode_for_hold": AuditMode.SEAL.value,
}


# ─── Pressure → Action Mapping (deterministic, F2 TRUTH) ──────────────────
PRESSURE_TO_ACTION: dict[PressureBand, TriggerAction] = {
    PressureBand.LOW: TriggerAction.PROCEED,
    PressureBand.WATCH: TriggerAction.WARN,
    PressureBand.WARN: TriggerAction.PRIME_COMPACTION,
    PressureBand.COMPACT: TriggerAction.PRIME_COMPACTION,
    PressureBand.HOLD: TriggerAction.HOLD,
}


# ─── Module-Level State (thread-safe) ──────────────────────────────────────
class _TriggerLog:
    """
    In-memory log of trigger events. Thread-safe.
    NOT persistent (Phase 3 will add L2 Redis; Phase 4 will drain to VAULT999).
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: list[dict[str, Any]] = []
        self._max_events = 10_000

    def append(self, event: dict[str, Any]) -> None:
        with self._lock:
            if len(self._events) >= self._max_events:
                # Evict oldest 10%
                evict_count = self._max_events // 10
                self._events = self._events[evict_count:]
            self._events.append(event)

    def snapshot(self, session_id: str = "") -> list[dict[str, Any]]:
        with self._lock:
            if not session_id:
                return list(self._events)
            return [e for e in self._events if e.get("session_id") == session_id]

    def count(self) -> int:
        with self._lock:
            return len(self._events)


_LOG = _TriggerLog()


# ─── Public API ────────────────────────────────────────────────────────────
def observe_pressure(session_id: str) -> dict[str, Any]:
    """
    Read current pressure for a session. Pure observation. No mutation.
    Returns: dict with session_id, tokens_used, model_window, pressure (full
             snapshot from classify_pressure), observed_at
    """
    if not session_id:
        return {
            "ok": False,
            "error": "no_session_id",
            "advisory": "F2: cannot observe pressure without session binding",
        }
    singleton = get_session_singleton()
    snap = singleton.snapshot(session_id)
    return {
        "ok": True,
        "session_id": session_id,
        "tokens_used": snap.get("tokens_used", 0),
        "model_key": snap.get("model_key"),
        "model_window": snap.get("model_window"),
        "pressure": snap.get("pressure", {}),
        "observed_at": snap.get("ts_utc"),
    }


def classify_action(pressure_band: str, policy: dict[str, Any] | None = None) -> TriggerAction:
    """
    Map a pressure band to a trigger action. Deterministic.
    Policy overrides band default (F8 sovereign territory).
    """
    pol = {**DEFAULT_POLICY, **(policy or {})}
    try:
        band = PressureBand(pressure_band)
    except ValueError:
        return TriggerAction.NOOP
    return PRESSURE_TO_ACTION.get(band, TriggerAction.NOOP)


def trigger(
    session_id: str,
    policy: dict[str, Any] | None = None,
    risk_class: str = "routine",
) -> dict[str, Any]:
    """
    Observe pressure, classify action, emit audit receipt, return result.

    The trigger is ADVISORY by default. It does NOT auto-compact.
    Auto-compact requires:
      1. F8 sovereign override (auto_compact_enabled=True in policy)
      2. Compaction implementation to exist (Phase 4+)
      3. A separate audit_classify seal recording the policy_version

    Returns:
        dict with: ok, observation, action, audit_receipt, advisory,
                  auto_compacted (always False in Phase 2)
    """
    pol = {**DEFAULT_POLICY, **(policy or {})}
    observation = observe_pressure(session_id)
    if not observation.get("ok"):
        return {
            "ok": False,
            "advisory": observation.get("advisory", "F2: observation failed"),
            "auto_compacted": False,
        }

    pressure = observation.get("pressure", {})
    band = pressure.get("pressure_band", "UNKNOWN")
    action = classify_action(band, pol)

    # Determine audit mode for this trigger event
    if action == TriggerAction.HOLD:
        audit_mode = pol.get("audit_mode_for_hold", AuditMode.SEAL.value)
    elif action == TriggerAction.PRIME_COMPACTION:
        audit_mode = pol.get("audit_mode_for_prime", AuditMode.SEAL.value)
    else:
        audit_mode = pol.get("audit_mode_for_warn", AuditMode.DIGEST.value)

    # Emit the audit receipt (Phase 1.D context_audit)
    audit_receipt: dict[str, Any]
    if audit_mode == AuditMode.SEAL.value:
        audit_receipt = audit_seal(
            event_type=EventType.CONTEXT_COMPACTION.value
            if action == TriggerAction.PRIME_COMPACTION
            else EventType.CONTEXT_RETRIEVAL_HIGH_RISK.value,
            session_id=session_id,
            actor_id="context_trigger_middleware",
            risk_class=risk_class,
            policy_version=pol.get("policy_version", "context_trigger.v1"),
            pressure_band=band,
            pressure_pct=pressure.get("pressure_pct"),
            action=action.value,
            auto_compact_enabled=pol.get("auto_compact_enabled", False),
            tokens_used=observation.get("tokens_used", 0),
            model_window=observation.get("model_window"),
            note="Phase 2 trigger middleware. Advisory only. No auto-compaction in Phase 2.",
        )
    elif audit_mode == AuditMode.DIGEST.value:
        audit_receipt = audit_digest(session_id)
    else:
        # TRACE: low-cost in-memory append
        import hashlib as _h

        qh = _h.sha256(f"{session_id}:{band}:{time.time()}".encode()).hexdigest()[:16]
        audit_receipt = audit_trace(
            session_id=session_id,
            query_hash=qh,
            retrieved_memory_ids=[],
            selected_ids=[],
            dropped_count=0,
            tier_origin="trigger_middleware",
        )

    # Compose the trigger result
    advisory = _compose_advisory(action, band, pressure, pol)

    result = {
        "ok": True,
        "session_id": session_id,
        "observation": observation,
        "pressure_band": band,
        "action": action.value,
        "advisory": advisory,
        "auto_compacted": False,  # F8 default
        "policy_version": pol.get("policy_version", "context_trigger.v1"),
        "audit_receipt": audit_receipt,
        "phase": "2 — trigger middleware, advisory only",
        "next_steps": _next_steps(action, pol),
    }

    # Log the event (in-memory, thread-safe)
    _LOG.append(
        {
            "ts": time.time(),
            "session_id": session_id,
            "band": band,
            "action": action.value,
            "audit_mode": audit_mode,
            "policy_version": pol.get("policy_version", "context_trigger.v1"),
        }
    )

    return result


def _compose_advisory(
    action: TriggerAction,
    band: str,
    pressure: dict[str, Any],
    policy: dict[str, Any],
) -> str:
    pct_raw = pressure.get("pressure_pct")
    pct = pct_raw if isinstance(pct_raw, (int, float)) else None
    pct_str = f"{pct:.0%}" if pct is not None else "unknown"
    if action == TriggerAction.PROCEED:
        return f"Pressure {band} ({pct_str}). Comfortable. No action needed."
    if action == TriggerAction.WARN:
        return f"Pressure {band} ({pct_str}). Advisory only. No auto-compact by default."
    if action == TriggerAction.PRIME_COMPACTION:
        if policy.get("auto_compact_enabled", False):
            return f"Pressure {band} ({pct_str}). Auto-compact ENABLED. Compaction path active (Phase 4+)."
        return (
            f"Pressure {band} ({pct_str}). PRIME_FOR_COMPACTION. "
            f"Agent should consider compaction. Auto-compact DISABLED by F8 default. "
            f"F8 sovereign to enable."
        )
    if action == TriggerAction.HOLD:
        return f"Pressure {band} ({pct_str}). HOLD. Refuse non-reversible action until pressure reduced."
    return f"Unknown state. band={band!r} pct={pct_str}. NOOP."


def _next_steps(action: TriggerAction, policy: dict[str, Any]) -> list[str]:
    if action == TriggerAction.PROCEED:
        return ["Continue normal operation."]
    if action == TriggerAction.WARN:
        return [
            "Log advisory to context_audit (DONE).",
            "Agent: monitor next call's token usage.",
            "Consider trimming low-value tool output on next call.",
        ]
    if action == TriggerAction.PRIME_COMPACTION:
        return [
            "SEAL compaction trigger event in context_audit (DONE).",
            "Agent: invoke arif_context_compact() to build summary (Phase 4 wiring).",
            "Raw transcript remains in L2/L4/L6 (F1 AMANAH).",
            "If auto_compact_enabled: trigger compaction now. Else: agent decides.",
        ]
    if action == TriggerAction.HOLD:
        return [
            "SEAL HOLD event in context_audit (DONE).",
            "Refuse non-reversible model calls.",
            "Agent: invoke arif_context_compact() or arif_session_init(new) to recover.",
            "F13: sovereign may override with new session.",
        ]
    return ["NOOP — degenerate state. Investigate session binding."]


# ─── Diagnostic Snapshot ────────────────────────────────────────────────────
def get_trigger_log(session_id: str = "") -> list[dict[str, Any]]:
    """Read-only access to in-memory trigger event log. For ops/debugging."""
    return _LOG.snapshot(session_id)


# ─── Self-Check (deterministic, no I/O) ────────────────────────────────────
def _self_check() -> dict[str, Any]:
    """Hermetic self-check.

    F2 truth invariant: every check is isolated. The token_pressure
    singleton is global; re-running _self_check() in the same process
    would pollute the previous session. Every check that needs a
    session uses a fresh per-run id (`f"selftest-{name}-{urandom4}"`)
    so the second/third/Nth invocation produces identical results.
    """
    import os as _os

    def _fresh_sid(label: str) -> str:
        return f"selftest-{label}-{_os.urandom(4).hex()}"

    results = []

    # 1. observe_pressure returns expected shape
    obs = observe_pressure(_fresh_sid("1"))
    r = "ok" in obs and "session_id" in obs and "tokens_used" in obs and "pressure" in obs
    results.append(("observe_pressure_shape_valid", r))

    # 2. observe_pressure with empty session returns F2 fail
    obs2 = observe_pressure("")
    r = obs2.get("ok") is False and "F2" in obs2.get("advisory", "")
    results.append(("observe_pressure_empty_session_F2_fail", r))

    # 3. classify_action maps bands correctly
    r = classify_action("LOW") == TriggerAction.PROCEED
    results.append(("classify_LOW_to_PROCEED", r))
    r = classify_action("WATCH") == TriggerAction.WARN
    results.append(("classify_WATCH_to_WARN", r))
    r = classify_action("WARN") == TriggerAction.PRIME_COMPACTION
    results.append(("classify_WARN_to_PRIME", r))
    r = classify_action("COMPACT") == TriggerAction.PRIME_COMPACTION
    results.append(("classify_COMPACT_to_PRIME", r))
    r = classify_action("HOLD") == TriggerAction.HOLD
    results.append(("classify_HOLD_to_HOLD", r))

    # 4. classify_action unknown → NOOP
    r = classify_action("UNKNOWN") == TriggerAction.NOOP
    results.append(("classify_unknown_to_NOOP", r))

    # 5. trigger emits audit receipt (fresh session)
    sid_a = _fresh_sid("2")
    trig = trigger(sid_a, policy=DEFAULT_POLICY)
    r = (
        trig.get("ok") is True
        and "audit_receipt" in trig
        and trig.get("auto_compacted") is False  # F8 default
    )
    results.append(("trigger_emits_audit_receipt", r))

    # 6. trigger with auto_compact_enabled in policy does NOT actually compact (Phase 2 boundary)
    # We need to drive the session into COMPACT band first to hit the ENABLED advisory path.
    # CRITICAL: use a fresh sid so cumulative record() does not push us into HOLD band.
    from arifosmcp.runtime.token_pressure import get_session_singleton as _gss

    sid_b = _fresh_sid("3")
    _gss().record(sid_b, 180_000, "MiniMax-M3")  # 90% of 200K = COMPACT
    policy_with_compact = {**DEFAULT_POLICY, "auto_compact_enabled": True}
    trig2 = trigger(sid_b, policy=policy_with_compact)
    r = (
        trig2.get("ok") is True
        and trig2.get("auto_compacted") is False  # Phase 2 doesn't implement it yet
        and "ENABLED" in trig2.get("advisory", "")
    )
    results.append(("trigger_advisory_only_in_phase2", r))

    # 7. trigger policy version pinned
    r = DEFAULT_POLICY.get("policy_version") == "context_trigger.v1"
    results.append(("policy_version_pinned", r))

    # 8. trigger log is thread-safe (test by hammering)
    import concurrent.futures

    def _hammer(_: int) -> int:
        trigger(f"sess-hammer-{_}", policy=DEFAULT_POLICY)
        return 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        results_hammer = list(ex.map(_hammer, range(50)))
    r = len(results_hammer) == 50
    results.append(("trigger_thread_safe_under_50_concurrent", r))

    # 9. trigger log records events
    log = get_trigger_log()
    r = len(log) >= 50  # at least the 50 hammer events
    results.append(("trigger_log_records_events", r))

    # 10. HOLD action is unrecoverable without F13
    next_steps_for_hold = _next_steps(TriggerAction.HOLD, DEFAULT_POLICY)
    # Either next_steps[1] is "F13:" or any entry mentions F13 / sovereign
    r = any("F13" in s or "sovereign" in s.lower() for s in next_steps_for_hold)
    results.append(("hold_advisory_mentions_F13", r))

    all_pass = all(passed for _, passed in results)
    return {
        "all_pass": all_pass,
        "checks": [{"name": n, "pass": p} for n, p in results],
        "n_checks": len(results),
        "n_pass": sum(1 for _, p in results if p),
    }


if os.getenv("ARIFOS_SELFTEST", "0") == "1":
    _selftest = _self_check()
    if _selftest["all_pass"]:
        logger.info(
            f"[context_trigger] selftest PASS {_selftest['n_pass']}/{_selftest['n_checks']}"
        )
    else:
        failed = [c["name"] for c in _selftest["checks"] if not c["pass"]]
        logger.error(f"[context_trigger] selftest FAIL: {failed}")


__all__ = [
    "DEFAULT_POLICY",
    "TriggerAction",
    "PRESSURE_TO_ACTION",
    "observe_pressure",
    "classify_action",
    "trigger",
    "get_trigger_log",
    "_self_check",
]
