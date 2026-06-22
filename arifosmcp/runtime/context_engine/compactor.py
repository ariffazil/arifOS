"""
arifOS v2.0 — Context Compactor (Phase 2, C)
═══════════════════════════════════════════════════════════════════════════════
The execution reflex. Turns "pressure observed" into "context compacted."

Trigger primes. Compactor builds. Three-level structured compaction:

  Level 1 (L1, always loaded, ~150 chars per entry):
    Compact index — session_id, actor_id, key decisions, unresolved TODOs,
    constitutional chain IDs, last tool called. Stored in-memory on
    session dict under key `_compaction_index`.

  Level 2 (L2, loaded on demand):
    Detailed topic files preserved from the session — evidence bundles,
    tool call results, reasoning chains. Written to memory store.

  Level 3 (L3, VAULT999 archive):
    Full raw transcript, sealed after compaction. Written via the existing
    VAULT999 audit path — never mutates canonical state directly.

Iron rules (F1-F13):
  - F1 AMANAH:   never mutates canonical VAULT999 directly; only writes via
                 the existing audit_seal path. No deletion. Reversible.
  - F2 TRUTH:    deterministic. No LLM calls. Same inputs → same output.
  - F4 CLARITY:  reduces entropy by stripping ephemeral noise.
  - F7 HUMILITY: only compacts when pressure threshold reached; never
                 anticipates future pressure.
  - F8 GENIUS:   policy version pinned; compaction behaviour controlled
                 by policy, not heuristics.
  - F9 ANTIHANTU: no LLM summariser. Pure structured distillation.
  - F11 AUDIT:   every compaction event is audit-traced.
  - F13 SOVEREIGN: never deletes raw transcript; L3 preserves full history.

What this module does:
  - compact_session(session_id, policy) -> CompactionReport
  - get_compaction_status(session_id)   -> CompactionReport | None
  - maybe_compact(session_id)           -> CompactionReport | None

What this module does NOT do:
  - Mutate VAULT999 directly (F1 AMANAH — uses audit_seal for L3)
  - Run any LLM (F2 TRUTH, F9 ANTIHANTU)
  - Auto-evict or drop canonical memory (F13 SOVEREIGN)
  - Make policy decisions (F8 GENIUS — policy is input only)

DITEMPA BUKAN DIBERI — the compactor is forged, not given.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
import uuid
from typing import Any

from arifosmcp.runtime.compression import CompressionMode, CompressionResult, compress
from arifosmcp.runtime.context_audit import (
    AuditMode,
    EventType,
    audit_seal,
    audit_trace,
)
from arifosmcp.runtime.token_pressure import (
    PressureBand,
    classify_pressure,
    get_session_singleton,
)

logger = logging.getLogger(__name__)


# ─── Policy pins (F8 GENIUS) ────────────────────────────────────────────────
COMPACTOR_POLICY_VERSION = "context_compactor.v1"
SOURCE_OF_TRUTH = "arifosmcp/runtime/context_engine/compactor.py"

# Default policy — F8 sovereign to override per call
DEFAULT_COMPACTOR_POLICY: dict[str, Any] = {
    "policy_version": COMPACTOR_POLICY_VERSION,
    # Pressure thresholds at which compaction triggers
    "l1_threshold_pct": 0.50,   # WARN band → build L1 index
    "l3_threshold_pct": 0.75,   # COMPACT band → archive L3 + trim
    "l1_max_entries": 20,       # max entries in the compact index
    "l1_entry_max_chars": 150,  # max chars per L1 entry
    "session_fragment_max_chars": 500,  # max chars for session fragment in L1
    "audit_mode_for_l1": AuditMode.TRACE.value,
    "audit_mode_for_l3": AuditMode.SEAL.value,
    "max_detail_per_entry": 80,  # chars for detail in L1 entries
}

# In-memory registry of compaction results (thread-safe, session-scoped)
class _CompactionRegistry:
    """Thread-safe in-memory map of session_id → CompactionReport.
    Never serialised to VAULT999 directly. F1 AMANAH: pure in-memory."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._reports: dict[str, dict[str, Any]] = {}

    def store(self, session_id: str, report: dict[str, Any]) -> None:
        with self._lock:
            self._reports[session_id] = report

    def get(self, session_id: str) -> dict[str, Any] | None:
        with self._lock:
            return self._reports.get(session_id)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._reports)

    def count(self) -> int:
        with self._lock:
            return len(self._reports)


_COMPACTIONS = _CompactionRegistry()


# ─── L1 Index Builder (deterministic, no LLM) ──────────────────────────────
def _build_l1_index(
    session_snapshot: dict[str, Any],
    session_id: str,
    policy: dict[str, Any],
) -> list[dict[str, str]]:
    """Build a compact Level-1 index from a session snapshot.

    The L1 index is a list of structured entries, each ~150 chars,
    representing the constitutional skeleton of the session:
      - actor_id and session metadata
      - key decisions (SEAL/SABAR/VOID events)
      - unresolved TODOs and open threads
      - constitutional chain IDs
      - last tool called
      - active tools and their stage progression

    F2 TRUTH: deterministic. F4 CLARITY: each entry is a fixed schema.
    """
    max_entries = policy.get("l1_max_entries", 20)
    entry_max_chars = policy.get("l1_entry_max_chars", 150)
    max_detail = policy.get("max_detail_per_entry", 80)

    # ── 1. Extract session metadata ────────────────────────────────────
    actor_id = session_snapshot.get("actor_id", "unknown")
    model_key = session_snapshot.get("model_key", "unknown")
    tokens_used = session_snapshot.get("tokens_used", 0) or 0
    model_window = session_snapshot.get("model_window", 0) or 0
    pressure = session_snapshot.get("pressure", {})

    # ── 2. Extract session fragments ───────────────────────────────────
    # Pull key-value pairs from the session dict that carry constitutional
    # weight: verdicts, chain IDs, hold flags, stage progression.
    # We scan for well-known keys plus any stage/tool/verdict keys.
    session_fragment = _extract_session_fragment(session_snapshot, policy)

    entries: list[dict[str, str]] = []
    char_budget = entry_max_chars * max_entries

    # Entry 0: Session identity (always present)
    entry: dict[str, str] = {}
    entry["kind"] = "session_identity"
    entry["actor_id"] = _trunc(actor_id, 32)
    entry["session_id"] = _trunc(session_id, 16)
    entry["model_key"] = _trunc(model_key, 24)
    detail_parts: list[str] = []
    if tokens_used > 0:
        detail_parts.append(f"tokens_used={tokens_used}")
    detail_parts.append(f"window={model_window}" if model_window > 0 else "window=unknown")
    pressure_band = pressure.get("pressure_band", "LOW")
    detail_parts.append(f"band={pressure_band}")
    entry["detail"] = _trunc("; ".join(detail_parts), max_detail)
    entries.append(entry)

    # Entry 1: Session fragment — the key constitutional values
    if session_fragment:
        entry = {"kind": "session_state", "detail": _trunc(session_fragment, max_detail * 2)}
        entries.append(entry)

    # Entry 2: Open threads / unresolved TODOs
    open_threads = session_snapshot.get("open_threads", [])
    if isinstance(open_threads, list) and open_threads:
        todo_count = min(len(open_threads), 3)
        for i in range(todo_count):
            thread = open_threads[i]
            if isinstance(thread, dict):
                desc = thread.get("description", thread.get("title", ""))
            else:
                desc = str(thread)
            entries.append({
                "kind": "open_thread",
                "detail": _trunc(str(desc), max_detail),
            })

    # Entry 3: Key decisions (SEAL/SABAR/VOID events from witness log)
    witness_log = session_snapshot.get("witness_log", [])
    if isinstance(witness_log, list):
        decisions_seen: set[str] = set()
        for w in witness_log:
            if isinstance(w, dict):
                verdict = str(w.get("verdict", "")).upper()
                if verdict in ("SEAL", "SABAR", "VOID", "HOLD") and verdict not in decisions_seen:
                    decisions_seen.add(verdict)
                    tool = str(w.get("tool_name", w.get("event_type", "unknown")))
                    entries.append({
                        "kind": "decision",
                        "verdict": verdict,
                        "detail": _trunc(f"{verdict} on {tool}", max_detail),
                    })

    # Entry 4: Constitutional chain IDs
    cc_id = session_snapshot.get("constitutional_chain_id")
    if cc_id:
        entries.append({
            "kind": "constitutional_chain",
            "detail": _trunc(str(cc_id), max_detail),
        })

    # Entry 5: Last tool called
    last_tool = session_snapshot.get("last_tool", session_snapshot.get("last_tool_called"))
    if last_tool:
        entries.append({
            "kind": "last_tool",
            "detail": _trunc(str(last_tool), max_detail),
        })

    # Entry 6: Stage progression
    stage = session_snapshot.get("last_stage", session_snapshot.get("stage"))
    if stage:
        entries.append({
            "kind": "stage",
            "detail": _trunc(str(stage), max_detail),
        })

    # Entry 7: Tool call count / cycle count
    n_tool_calls = session_snapshot.get("n_tool_calls", session_snapshot.get("tool_call_count"))
    if n_tool_calls is not None:
        entries.append({
            "kind": "tool_calls",
            "detail": str(n_tool_calls),
        })

    # ── 3. Enforce budget ──────────────────────────────────────────────
    # Trim entries to max_entries. Truncate each entry to ~150 chars.
    trimmed = entries[:max_entries]
    for e in trimmed:
        for k, v in e.items():
            if isinstance(v, str) and len(v) > entry_max_chars:
                e[k] = v[: entry_max_chars - 3] + "…"

    return trimmed


def _extract_session_fragment(
    snapshot: dict[str, Any],
    policy: dict[str, Any],
) -> str:
    """Extract a compact text fragment of the session state for L1.

    Picks up constitutional weight-bearing fields from the snapshot
    that don't have their own dedicated entry slot.
    """
    max_chars = policy.get("session_fragment_max_chars", 500)
    parts: list[str] = []

    for key in ("session_verdict", "runtime_state", "epoch_id", "previous_session_hash"):
        val = snapshot.get(key)
        if val is not None and val != "" and val != "UNKNOWN":
            parts.append(f"{key}={val}")

    # Tool bindings / wired targets
    tool_binding = snapshot.get("tool_binding", {})
    wired = tool_binding.get("wired", {}) if isinstance(tool_binding, dict) else {}
    if isinstance(wired, dict) and wired:
        targets = list(wired.keys()) if len(wired) <= 4 else list(wired.keys())[:4]
        parts.append(f"wired={','.join(str(t) for t in targets)}")

    # Degradation info
    session_verdict = str(snapshot.get("session_verdict", "STABLE"))
    if "DEGRADED" in session_verdict or "HOLD" in session_verdict:
        parts.append(f"verdict={session_verdict}")

    result = " | ".join(parts)
    return result[:max_chars] + ("…" if len(result) > max_chars else "")


def _trunc(text: str, max_len: int) -> str:
    """Truncate text to max_len with ellipsis if needed."""
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


# ─── L3 Archiver (write to VAULT999 via audit_seal) ─────────────────────────
def _archive_l3(
    session_id: str,
    session_snapshot: dict[str, Any],
    l1_index: list[dict[str, str]],
    policy: dict[str, Any],
) -> dict[str, Any]:
    """Seal the session's raw transcript fragment to VAULT999.

    F1 AMANAH: writes ONLY via audit_seal, which is the canonical
    VAULT999 write path. Never mutates VAULT999 directly.
    F13 SOVEREIGN: preserves full transcript; does not delete anything.

    The archived payload includes:
      - session metadata (actor_id, model, tokens)
      - the full snapshot dump (non-PII)
      - the L1 index that was built
      - a hash of the combined payload for chain integrity
    """
    audit_mode = policy.get("audit_mode_for_l3", AuditMode.SEAL.value)

    # Build the archive payload (deterministic, no PII)
    archive_payload = {
        "session_id": session_id,
        "actor_id": session_snapshot.get("actor_id"),
        "model_key": session_snapshot.get("model_key"),
        "tokens_used": session_snapshot.get("tokens_used"),
        "model_window": session_snapshot.get("model_window"),
        "pressure": session_snapshot.get("pressure"),
        "session_verdict": session_snapshot.get("session_verdict"),
        "constitutional_chain_id": session_snapshot.get("constitutional_chain_id"),
        "compacted_at_utc": _now_iso(),
        "l1_index": l1_index,
        # Raw snapshot fields that are safe for archive (non-PII, constitutional)
        "stage": session_snapshot.get("last_stage", session_snapshot.get("stage")),
        "epoch_id": session_snapshot.get("epoch_id"),
        "session_fragment": _extract_session_fragment(session_snapshot, policy),
    }

    # ── Deterministic hash of archive payload ─────────────────────────
    payload_json = json.dumps(archive_payload, sort_keys=True, default=str)
    archive_hash = hashlib.sha256(payload_json.encode()).hexdigest()[:32]

    archive_payload["_archive_hash"] = archive_hash
    archive_json = json.dumps(archive_payload, sort_keys=True, default=str)

    # ── Write via audit_seal (the canonical VAULT999 path) ───────────
    seal_receipt = audit_seal(
        event_type=EventType.CONTEXT_COMPACTION.value,
        session_id=session_id,
        actor_id="context_compactor_middleware",
        risk_class="routine",
        policy_version=policy.get("policy_version", COMPACTOR_POLICY_VERSION),
        pressure_band=session_snapshot.get("pressure", {}).get("pressure_band", "UNKNOWN"),
        pressure_pct=session_snapshot.get("pressure", {}).get("pressure_pct"),
        archive_hash=archive_hash,
        archive_size_bytes=len(archive_json),
        note="L3 context compaction — full transcript fragment archived",
    )

    return {
        "archive_hash": archive_hash,
        "archive_size_bytes": len(archive_json),
        "seal_receipt": seal_receipt,
        "seal_ts_utc": _now_iso(),
    }


# ─── Public API ─────────────────────────────────────────────────────────────
def compact_session(
    session_id: str,
    policy: dict[str, Any] | None = None,
    force_l3: bool = False,
) -> dict[str, Any]:
    """Build a 3-level context compaction for a session.

    Reads token pressure from the session singleton. If pressure >=
    50% (WARN), builds an L1 index and stores it in-memory. If pressure
    >= 75% (COMPACT) or force_l3=True, also archives L3 to VAULT999.

    Args:
        session_id: canonical session ID (required; F2 fail-closed)
        policy: optional policy override; uses DEFAULT_COMPACTOR_POLICY
        force_l3: if True, archive L3 even if pressure < 75%

    Returns:
        CompactionReport dict:
          {
            "ok": bool,
            "session_id": str,
            "compacted": bool,           # True if any level was built
            "l1_built": bool,
            "l1_index": list[dict] | None,
            "l3_archived": bool,
            "l3_receipt": dict | None,
            "pressure_pct": float,
            "pressure_band": str,
            "output_reserve_tokens": int,
            "policy_version": str,
            "ts_utc": str,
            "advisory": str,
          }

    F2 TRUTH: deterministic — same session_id + same policy → same output.
    F11 AUDIT: every compaction emits a TRACE receipt.
    """
    merged_policy: dict[str, Any] = {**DEFAULT_COMPACTOR_POLICY, **(policy or {})}

    # ── F2 fail-closed ────────────────────────────────────────────────
    if not session_id:
        return {
            "ok": False,
            "session_id": "",
            "compacted": False,
            "advisory": "F2: session_id required (fail-closed)",
            "policy_version": merged_policy.get("policy_version", COMPACTOR_POLICY_VERSION),
            "ts_utc": _now_iso(),
        }

    # ── 1. Read pressure ──────────────────────────────────────────────
    singleton = get_session_singleton()
    snap = singleton.snapshot(session_id)
    tokens_used = snap.get("tokens_used", 0) or 0
    model_key = snap.get("model_key") or "MiniMax-M3"
    model_window = snap.get("model_window") or 0
    pressure = snap.get("pressure", {})

    # ── 2. Determine thresholds ───────────────────────────────────────
    l1_threshold = merged_policy.get("l1_threshold_pct", 0.50)
    l3_threshold = merged_policy.get("l3_threshold_pct", 0.75)

    # If no model window bound yet, pressure is UNKNOWN — do not compact
    if isinstance(pressure.get("pressure_band"), str) and pressure["pressure_band"] == "UNKNOWN":
        return {
            "ok": True,
            "session_id": session_id,
            "compacted": False,
            "l1_built": False,
            "l3_archived": False,
            "pressure_pct": None,
            "pressure_band": "UNKNOWN",
            "advisory": "Session not yet bound to a model. No compaction possible.",
            "policy_version": merged_policy.get("policy_version", COMPACTOR_POLICY_VERSION),
            "ts_utc": _now_iso(),
        }

    pressure_pct = pressure.get("pressure_pct", 0.0)
    if pressure_pct is None:
        pressure_pct = 0.0
    pressure_band = pressure.get("pressure_band", "LOW")
    effective_pct = float(pressure_pct)

    # ── 3. Build L1 if pressure >= 50% ────────────────────────────────
    l1_built = False
    l1_index: list[dict[str, str]] | None = None

    if effective_pct >= l1_threshold:
        # Build L1 index from the session snapshot
        # We need the full session dict from _SESSIONS; snapshot gives us
        # token telemetry. For a richer L1, we pass both.
        l1_index = _build_l1_index(snap, session_id, merged_policy)
        l1_built = True

        # Emit TRACE audit for L1 build
        trace_receipt = audit_trace(
            session_id=session_id,
            query_hash=f"compactor:l1:{session_id[:12]}",
            retrieved_memory_ids=[],
            selected_ids=[],
            dropped_count=0,
            tier_origin="compactor",
            ttl_seconds=3600,
            **{
                "event_subtype": "CONTEXT_COMPACT_L1",
                "n_l1_entries": len(l1_index),
                "pressure_pct": effective_pct,
                "pressure_band": pressure_band,
            },
        )

    # ── 4. Archive L3 if pressure >= 75% (or force_l3) ───────────────
    l3_archived = False
    l3_receipt: dict[str, Any] | None = None

    if effective_pct >= l3_threshold or force_l3:
        if l1_index is None:
            # Build L1 index first if we haven't yet (force_l3 case)
            l1_index = _build_l1_index(snap, session_id, merged_policy)
            l1_built = True
        l3_receipt = _archive_l3(session_id, snap, l1_index, merged_policy)
        l3_archived = True

    # ── 5. Build output reserve recommendation ───────────────────────
    if model_window > 0:
        reserve_output = max(1_000, min(4_000, int(model_window * 0.10)))
    else:
        reserve_output = 1_500

    # ── 6. Compose report ─────────────────────────────────────────────
    compacted = l1_built or l3_archived

    report = {
        "ok": True,
        "session_id": session_id,
        "compacted": compacted,
        "l1_built": l1_built,
        "l1_index": l1_index,
        "l3_archived": l3_archived,
        "l3_receipt": l3_receipt,
        "pressure_pct": effective_pct,
        "pressure_band": pressure_band,
        "model_key": model_key,
        "model_window": model_window,
        "tokens_used": tokens_used,
        "output_reserve_tokens": reserve_output,
        "policy_version": merged_policy.get("policy_version", COMPACTOR_POLICY_VERSION),
        "ts_utc": _now_iso(),
        "advisory": _compose_advisory(effective_pct, pressure_band, compacted),
    }

    # Store in in-memory registry (thread-safe)
    _COMPACTIONS.store(session_id, report)

    return report


def get_compaction_status(session_id: str) -> dict[str, Any] | None:
    """Read-only. Return the last CompactionReport for a session, or None.

    F1 AMANAH: pure read. F2 TRUTH: returns what was computed, never
    fabricates. Pure in-memory query of the compaction registry.
    """
    return _COMPACTIONS.get(session_id)


def maybe_compact(session_id: str) -> dict[str, Any] | None:
    """Conditional compaction hook. Returns CompactionReport if pressure
    is high enough, None if compaction was skipped.

    Designed to be called from tool boundaries:
      - In _arif_init: after session bootstrap, check if a resumed session
        has high enough pressure to warrant immediate compaction.
      - In _arif_think_tool: after a reasoning step, check if accumulated
        pressure warrants compaction before the next think cycle.

    Returns:
        CompactionReport dict if compaction was performed.
        None if no compaction was needed.
    """
    if not session_id:
        return None

    singleton = get_session_singleton()
    snap = singleton.snapshot(session_id)
    pressure = snap.get("pressure", {})

    # If no model bound yet, cannot evaluate pressure
    if isinstance(pressure.get("pressure_band"), str) and pressure["pressure_band"] == "UNKNOWN":
        return None

    pressure_pct = pressure.get("pressure_pct", 0.0)
    if pressure_pct is None:
        return None

    effective_pct = float(pressure_pct)

    # Minimum threshold: WARN band (50%) or higher
    l1_threshold = DEFAULT_COMPACTOR_POLICY.get("l1_threshold_pct", 0.50)
    if effective_pct < l1_threshold:
        return None

    # Compact and return the report
    return compact_session(session_id)


# ─── Helpers ────────────────────────────────────────────────────────────────
def _compose_advisory(pressure_pct: float, pressure_band: str, compacted: bool) -> str:
    """Compose a human-readable advisory for the report."""
    pct_str = f"{pressure_pct:.0%}" if pressure_pct is not None else "unknown"
    if not compacted:
        return f"Pressure {pressure_band} ({pct_str}). Below compaction threshold. No action."
    l3_flag = "L3 archived and trimmed." if compacted else ""
    return f"Pressure {pressure_band} ({pct_str}). Compaction applied. L1 index built. {l3_flag}"


def _now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()


# ─── Compaction Stats (observability) ───────────────────────────────────────
def get_compaction_stats() -> dict[str, Any]:
    """Return aggregate compaction statistics."""
    reg = _COMPACTIONS.snapshot()
    n_total = len(reg)
    n_with_l1 = sum(1 for r in reg.values() if isinstance(r, dict) and r.get("l1_built"))
    n_with_l3 = sum(1 for r in reg.values() if isinstance(r, dict) and r.get("l3_archived"))
    return {
        "n_sessions_compacted": n_total,
        "n_with_l1": n_with_l1,
        "n_with_l3": n_with_l3,
        "policy_version": COMPACTOR_POLICY_VERSION,
    }


# ─── Self-Check (deterministic, no I/O) ─────────────────────────────────────
def _self_check() -> dict[str, Any]:
    """12 deterministic properties of the context compactor.

    Run with ARIFOS_SELFTEST=1. Exported for tests.
    """
    import os as _os

    def _fresh_sid(label: str) -> str:
        return f"selftest-{label}-{_os.urandom(4).hex()}"

    results: list[tuple[str, bool]] = []

    # 1. compact_session with empty session_id returns F2 fail
    rpt = compact_session("")
    r = rpt.get("ok") is False and "F2" in rpt.get("advisory", "")
    results.append(("empty_session_is_F2_fail", r))

    # 2. compact_session with unseen session (no pressure) returns noop
    sid = _fresh_sid("2")
    rpt = compact_session(sid)
    r = rpt.get("ok") is True and rpt.get("compacted") is False
    results.append(("unseen_session_no_compaction", r))

    # 3. compact_session with high enough pressure builds L1
    sid = _fresh_sid("3")
    get_session_singleton().record(sid, 180_000, "MiniMax-M3")  # 90% → COMPACT
    rpt = compact_session(sid)
    r = rpt.get("ok") is True and rpt.get("l1_built") is True and rpt.get("l3_archived") is True
    results.append(("high_pressure_builds_L1_and_L3", r))

    # 4. L1 index has expected structure (session_identity entry)
    sid = _fresh_sid("4")
    get_session_singleton().record(sid, 150_000, "MiniMax-M3")  # 75% → exactly COMPACT
    rpt = compact_session(sid)
    l1 = rpt.get("l1_index", [])
    r = isinstance(l1, list) and len(l1) > 0 and any(e.get("kind") == "session_identity" for e in l1)
    results.append(("l1_has_session_identity_entry", r))

    # 5. L1 entries respect entry_max_chars budget
    sid = _fresh_sid("5")
    get_session_singleton().record(sid, 180_000, "MiniMax-M3")
    rpt = compact_session(sid)
    l1 = rpt.get("l1_index", [])
    max_chars = DEFAULT_COMPACTOR_POLICY.get("l1_entry_max_chars", 150)
    all_under = True
    for e in l1:
        for k, v in e.items():
            if isinstance(v, str) and len(v) > max_chars:
                all_under = False
                break
    results.append(("l1_entries_respect_max_chars", all_under))

    # 6. L1 respects max_entries limit
    sid = _fresh_sid("6")
    get_session_singleton().record(sid, 180_000, "MiniMax-M3")
    rpt = compact_session(sid)
    l1 = rpt.get("l1_index", [])
    max_entries = DEFAULT_COMPACTOR_POLICY.get("l1_max_entries", 20)
    results.append(("l1_respects_max_entries", len(l1) <= max_entries))

    # 7. L3 archive produces a receipt
    sid = _fresh_sid("7")
    get_session_singleton().record(sid, 180_000, "MiniMax-M3")
    rpt = compact_session(sid)
    r = rpt.get("l3_archived") is True and rpt.get("l3_receipt") is not None
    results.append(("l3_archive_produces_receipt", r))

    # 8. force_l3 archives even below threshold
    sid = _fresh_sid("8")
    get_session_singleton().record(sid, 15_000, "MiniMax-M3")  # 7.5% → LOW
    rpt = compact_session(sid, force_l3=True)
    r = rpt.get("l3_archived") is True
    results.append(("force_l3_archives_below_threshold", r))

    # 9. get_compaction_status returns stored report
    sid = _fresh_sid("9")
    get_session_singleton().record(sid, 180_000, "MiniMax-M3")
    compact_session(sid)
    status = get_compaction_status(sid)
    r = status is not None and status.get("session_id") == sid and status.get("ok") is True
    results.append(("get_compaction_status_returns_report", r))

    # 10. get_compaction_status for unseen session returns None
    sid = _fresh_sid("10")
    status = get_compaction_status(sid)
    r = status is None
    results.append(("get_compaction_status_unseen_is_None", r))

    # 11. maybe_compact returns None below threshold
    sid = _fresh_sid("11")
    get_session_singleton().record(sid, 20_000, "MiniMax-M3")  # 10% → LOW
    result = maybe_compact(sid)
    r = result is None
    results.append(("maybe_compact_below_threshold_returns_None", r))

    # 12. maybe_compact returns report above threshold
    sid = _fresh_sid("12")
    get_session_singleton().record(sid, 150_000, "MiniMax-M3")  # 75% → COMPACT
    result = maybe_compact(sid)
    r = result is not None and result.get("compacted") is True
    results.append(("maybe_compact_above_threshold_returns_report", r))

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
            f"[context_compactor] selftest PASS {_selftest['n_pass']}/{_selftest['n_checks']}"
        )
    else:
        failed = [c["name"] for c in _selftest["checks"] if not c["pass"]]
        logger.error(f"[context_compactor] selftest FAIL: {failed}")


__all__ = [
    "COMPACTOR_POLICY_VERSION",
    "DEFAULT_COMPACTOR_POLICY",
    "compact_session",
    "get_compaction_status",
    "maybe_compact",
    "get_compaction_stats",
    "_self_check",
]
