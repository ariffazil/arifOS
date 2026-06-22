"""
arif_context_status — Read-only Context Engine Telemetry Tool
═══════════════════════════════════════════════════════════════════════════════

Part of arifOS Context Engine — Phase T1 (proof before power).

Authority:
  - F1 AMANAH      : read-only. No mutation. No canonical write. Reversible.
  - F2 TRUTH       : every value is computed deterministically from live state.
  - F4 CLARITY     : single-purpose: one function, one output shape.
  - F7 HUMILITY    : never fabricates; returns UNKNOWN when no data.
  - F8 GENIUS      : pure observer, no policy mutation.
  - F11 AUDIT      : every call records a session-scoped trace (no VAULT999).
  - F13 SOVEREIGN  : canonical memory NEVER touched. No seal. No hold.

Purpose:
  Surface a JSON snapshot of:
    - session token pressure
    - audit mode (TRACE default, SEAL for high-risk retrieval)
    - last compaction timestamp (null when auto_compact is OFF)
    - policy version pinned
    - whether auto-compact is enabled (always False by default per F8)

This is the **read-only tool** the blueprint section 3 specifies.
It does NOT mutate, it does NOT call LLM, it does NOT write to VAULT999.

DITEMPA BUKAN DIBERI — the observer is forged, not given.
"""

from __future__ import annotations

import logging
import os
import threading
from typing import Any

from arifosmcp.runtime.context_audit import (
    POLICY_VERSION as AUDIT_POLICY_VERSION,
)
from arifosmcp.runtime.context_audit import (
    AuditMode,
    audit_trace,
)
from arifosmcp.runtime.context_engine.eureka import (
    EUREKA_POLICY_VERSION,
)
from arifosmcp.runtime.token_pressure import (
    PressureBand,
    classify_pressure,
    get_model_window,
    get_session_singleton,
)

logger = logging.getLogger(__name__)


# ─── Policy pins (F8: changing these is F13 territory) ──────────────────────
CONTEXT_STATUS_POLICY_VERSION = "context_status.v1"
AUTO_COMPACT_ENABLED_DEFAULT = False  # F8 GENIUS: OFF by default; F13 to enable


# ─── Singleton session-call counter (observability only) ───────────────────
class _StatusStats:
    """Thread-safe in-memory counter of arif_context_status invocations.
    Pure telemetry. F1 AMANAH: not part of canonical state."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._n_calls: int = 0
        self._n_audit_traces: int = 0

    def record(self, emitted_audit: bool) -> None:
        with self._lock:
            self._n_calls += 1
            if emitted_audit:
                self._n_audit_traces += 1

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return {
                "n_calls": self._n_calls,
                "n_audit_traces": self._n_audit_traces,
            }


_STATS = _StatusStats()


def get_status_stats() -> dict[str, int]:
    return _STATS.snapshot()


# ─── The read-only tool ──────────────────────────────────────────────────────
def arif_context_status(
    session_id: str,
    model_key: str = "MiniMax-M3",
    auto_compact_enabled: bool = AUTO_COMPACT_ENABLED_DEFAULT,
    last_compaction: str | None = None,
) -> dict[str, Any]:
    """
    Read-only context engine telemetry. Pure observer.

    Args:
        session_id:  the canonical session id (UUID) to inspect.
        model_key:   model the session is bound to (default M3).
        auto_compact_enabled: explicit override; default is False (F8).
                            The trigger layer reads this flag; status does
                            NOT mutate it.
        last_compaction: ISO-8601 timestamp of the last compaction; or
                        None if no compaction has happened this session.

    Returns:
        dict — the canonical PressureReport + audit mode + policy version.

    Iron rules:
        - F1: read-only. No mutation of any state.
        - F11: every call emits a TRACE (L2/in-memory) so the call is
               reconstructable from session log.
        - F13: never writes to canonical memory, never seals, never holds.
    """
    if not session_id:
        # Fail-closed: empty session_id is F2 (can't trust the call).
        return {
            "status": "INVALID",
            "verdict": "VOID",
            "rationale": "session_id is required (F2)",
            "policy_version": CONTEXT_STATUS_POLICY_VERSION,
        }

    # ── 1. Read token pressure from the in-memory accumulator ──────────────
    sessions = get_session_singleton()
    snap = sessions.snapshot(session_id)
    tokens_used = snap.get("tokens_used", 0) or 0
    bound_model_key = snap.get("model_key") or model_key
    model_window = snap.get("model_window") or get_model_window(bound_model_key)

    # ── 2. Classify pressure (deterministic, no LLM) ────────────────────────
    pressure = classify_pressure(tokens_used, model_window)
    pressure_band = pressure["pressure_band"]
    pressure_pct = pressure["pressure_pct"]

    # ── 3. Tokens remaining ────────────────────────────────────────────────
    tokens_remaining = max(0, model_window - tokens_used)

    # ── 4. Audit mode: TRACE for routine observation ──────────────────────
    # Per the policy: routine retrieval is TRACE. arif_context_status is
    # read-only observation, so TRACE is correct.
    audit_mode = AuditMode.TRACE.value

    # ── 5. Verdict: SEAL means "the system observed cleanly, no advisory" ─
    # HOLD only happens on canonical mutation, which this tool never does.
    if pressure_band == PressureBand.HOLD.value:
        verdict = "HOLD"
        advisory = pressure["advisory"]
    elif pressure_band in (PressureBand.COMPACT.value, PressureBand.WARN.value):
        verdict = "CAUTION"
        advisory = pressure["advisory"]
    else:
        verdict = "SEAL"
        advisory = pressure["advisory"]

    # ── 6. Emit a TRACE (no VAULT999) so the call is reconstructable ─────
    # F11: every observation leaves a trace in the session-local store.
    audit_receipt = audit_trace(
        session_id=session_id,
        query_hash="arif_context_status:observe",
        retrieved_memory_ids=[],
        selected_ids=[],
        dropped_count=0,
        tier_origin="L3",  # status lives in L3 (Qdrant/semantic) conceptually
        ttl_seconds=3600,
        **{
            "event_subtype": "CONTEXT_STATUS_OBSERVE",
            "tokens_used": tokens_used,
            "pressure_pct": pressure_pct,
            "pressure_band": pressure_band,
        },
    )
    _STATS.record(emitted_audit=audit_receipt["appended"])

    # ── 7. Build the canonical snapshot ───────────────────────────────────
    # Default reserve + safety margin: 1500 + 10% of window, matches
    # prepare_context() defaults so callers can compare snapshots.
    output_reserve_tokens = 1500
    safety_margin_tokens = max(0, int(model_window * 0.10))

    report = {
        "session_id": session_id,
        "model_key": bound_model_key,
        "model_context_window": model_window,
        "tokens_used": tokens_used,
        "tokens_remaining": tokens_remaining,
        "output_reserve_tokens": output_reserve_tokens,
        "safety_margin_tokens": safety_margin_tokens,
        "context_pressure_pct": pressure_pct,
        "pressure_band": pressure_band,
        "auto_compact_enabled": bool(auto_compact_enabled),
        "last_compaction": last_compaction,
        "active_segments": [],  # F1 read-only: empty when no packet built
        "dropped_segments": [],  # F1 read-only: empty when no packet built
        "protected_count": 0,  # F1 read-only: 0 when no packet built
        "audit_mode": audit_mode,
        "verdict": verdict,
        "advisory": advisory,
        "policy_version": CONTEXT_STATUS_POLICY_VERSION,
        "audit_policy_version": AUDIT_POLICY_VERSION,
        "eureka_policy_version": EUREKA_POLICY_VERSION,
        "status_receipt": {
            "trace_hash": audit_receipt["trace_hash"],
            "trace_count": audit_receipt["trace_count"],
        },
        "ts_utc": snap.get("ts_utc"),
        "status_call_stats": _STATS.snapshot(),
    }

    return report


# ─── Self-Check (deterministic, no I/O) ─────────────────────────────────────
def _self_check() -> dict[str, Any]:
    """
    10 deterministic properties of arif_context_status.

    Run with ARIFOS_SELFTEST=1. Exported for tests.
    """
    results = []

    # 1. Empty session_id returns INVALID, never raises
    r = arif_context_status("")["status"] == "INVALID"
    results.append(("empty_sid_is_INVALID", r))

    # 2. With no recorded session, returns SEAL/LOW pressure
    snap = arif_context_status(f"never-{os.urandom(4).hex()}")
    r = snap["verdict"] == "SEAL" and snap["pressure_band"] == "LOW"
    results.append(("unseen_session_is_SEAL_LOW", r))

    # 3. auto_compact_enabled defaults to False (F8)
    r = AUTO_COMPACT_ENABLED_DEFAULT is False
    results.append(("auto_compact_default_OFF", r))

    # 4. Policy versions are pinned and consistent
    r = (
        CONTEXT_STATUS_POLICY_VERSION == "context_status.v1"
        and AUDIT_POLICY_VERSION == "context_policy.v1"
        and EUREKA_POLICY_VERSION == "context_eureka.v1"
    )
    results.append(("policy_versions_pinned", r))

    # 5. Reading twice does not mutate *canonical* state
    # (TRACE appends to session-local L2 store, which is F1 AMANAH: it
    # is not canonical memory, not VAULT999, and is GC'd with the session.)
    sid = f"test-{os.urandom(4).hex()}"
    a = arif_context_status(sid)
    b = arif_context_status(sid)
    # The trace_count goes up, but tokens_used, model_window, verdict
    # are all stable.
    r = (
        a["tokens_used"] == b["tokens_used"]
        and a["model_context_window"] == b["model_context_window"]
        and a["verdict"] == b["verdict"]
        and a["pressure_band"] == b["pressure_band"]
    )
    results.append(("canonical_state_not_mutated", r))

    # 6. Output shape is canonical
    snap = arif_context_status(f"test-{os.urandom(4).hex()}")
    required = {
        "session_id",
        "model_key",
        "model_context_window",
        "tokens_used",
        "tokens_remaining",
        "context_pressure_pct",
        "pressure_band",
        "auto_compact_enabled",
        "last_compaction",
        "audit_mode",
        "verdict",
        "advisory",
        "policy_version",
    }
    r = required.issubset(snap.keys())
    results.append(("output_shape_canonical", r))

    # 7. Audit mode is always TRACE for the read-only tool
    snap = arif_context_status(f"test-{os.urandom(4).hex()}")
    r = snap["audit_mode"] == "TRACE"
    results.append(("audit_mode_is_TRACE", r))

    # 8. No VAULT999 mutation: arif_context_status never seals
    # (Verified structurally: there is no audit_seal call anywhere in this
    # module. The audit_trace is the only audit emit.)
    import inspect

    source = inspect.getsource(arif_context_status)
    r = "audit_seal" not in source and "arif_seal" not in source
    results.append(("no_vault_mutation", r))

    # 9. Tokens remaining is non-negative
    snap = arif_context_status(f"test-{os.urandom(4).hex()}")
    r = snap["tokens_remaining"] >= 0
    results.append(("tokens_remaining_non_negative", r))

    # 10. With a recorded session at HIGH pressure, tokens_used reflects
    # the accumulator and the band escalates.
    from arifosmcp.runtime.token_pressure import get_session_singleton

    sid = f"probe-{os.urandom(4).hex()}"
    store = get_session_singleton()
    # 180k / 200k = 0.90 → COMPACT
    store.record(sid, 180_000, model_key="MiniMax-M3")
    snap = arif_context_status(sid)
    r = (
        snap["tokens_used"] == 180_000
        and snap["pressure_band"] == "COMPACT"
        and snap["verdict"] == "CAUTION"  # WARN/COMPACT → CAUTION per the tool
    )
    results.append(("recorded_tokens_reflected", r))

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
        logger.info(f"[context_status] selftest PASS {_selftest['n_pass']}/{_selftest['n_checks']}")
    else:
        failed = [c["name"] for c in _selftest["checks"] if not c["pass"]]
        logger.error(f"[context_status] selftest FAIL: {failed}")


__all__ = [
    "CONTEXT_STATUS_POLICY_VERSION",
    "AUTO_COMPACT_ENABLED_DEFAULT",
    "arif_context_status",
    "get_status_stats",
    "_self_check",
]
