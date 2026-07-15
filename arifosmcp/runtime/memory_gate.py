"""
arifosmcp/runtime/memory_gate.py — Pre-Execution Floor Gate for arif_memory
═══════════════════════════════════════════════════════════════════════════

TASK-P0-01a: Constitutional pre-execution gate (F1 / F11 / F13) for
arif_memory_recall, fixing issue #598 — material mutation class without
pre-execution constitutional gate.

Floor enforcement contract:
  F1 AMANAH       — session_id binding required (else SABAR)
  F2 TRUTH        — verdict returns SPECIFIC floor citation, not generic
  F9 ANTI-HANTU   — SABAR returns empty result; NEVER fabricates memory
  F11 AUDIT       — actor_id required; OBSERVE_ONLY sessions blocked from MUTATE
  F13 SOVEREIGN   — IRREVERSIBLE (forget / prune) requires prior arif_judge trace

Taxonomy of operation classes:
  READ          — recall / list / audit / search / context / stats
                   (may proceed without mutation authority; never mutates)
  MUTATE        — store / import / quarantine / seal / update / graph_store /
                   cognitive_learn / contradict_resolve
                   (requires MUTATE/OPERATOR authority)
  IRREVERSIBLE  — forget / prune
                   (requires MUTATE/OPERATOR authority + prior arif_judge trace)

Hook order (canonical, applied in arif_memory_recall):
  1. _mode_aliases normalization
  2. pre_execution_floor_gate() — THIS MODULE
  3. check_laws() — runtime/law.py
  4. mode-specific execution

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

# Bound import: get_session_identity is the canonical session lookup.
# Importing at module level enables clean monkeypatch-based unit testing.
from arifosmcp.runtime.session import get_session_identity

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# OPERATION CLASS TAXONOMY — drives gate strictness
# ═══════════════════════════════════════════════════════════════════════════


# MUTATE class — produces a durable memory artifact (in-place mutates Vault).
MUTATE_MODES: frozenset[str] = frozenset(
    {
        "store",
        "import",
        "quarantine",
        "seal",
        "update",
        "graph_store",
        "cognitive_learn",
        "contradict_resolve",
    }
)

# IRREVERSIBLE class — destroys/forgets memory that may not be recoverable.
IRREVERSIBLE_MODES: frozenset[str] = frozenset(
    {
        "forget",
        "prune",
    }
)

# READ class — never produces durable mutation; safe to run with lighter gate.
READ_MODES: frozenset[str] = frozenset(
    {
        "recall",
        "context",
        "audit",
        "search",
        "list",
        "stats",
        "init_recall",
        "contradict_scan",
        "contradict_status",
        "cognitive_recall",
        "cognitive_cross_session",
        "graph_query",
        "graph_get",
    }
)


# ═══════════════════════════════════════════════════════════════════════════
# F11 AUDIT HYGIENE — never echo plaintext actor IDs
# ═══════════════════════════════════════════════════════════════════════════


def _tokenize_actor(actor_id: str | None) -> str:
    """Return a SHA-256 fingerprint of the actor id.

    F11 AUDIT: never include the plaintext actor_id in any verdict that
    may be persisted, logged, or returned to non-trusted callers. The
    fingerprint is the audit reference; the plaintext lives only in the
    verified-session bound and is never echoed.
    """
    if not actor_id or not str(actor_id).strip():
        return "actor:none"
    digest = hashlib.sha256(str(actor_id).encode("utf-8")).hexdigest()
    return f"actor:sha256:{digest[:16]}"


# ═══════════════════════════════════════════════════════════════════════════
# CLASSIFICATION — operation class drives which floors are strictest
# ═══════════════════════════════════════════════════════════════════════════


def classify_operation(mode: str) -> str:
    """Classify an arif_memory mode into READ / MUTATE / IRREVERSIBLE.

    Unknown modes default to MUTATE (conservative; F1 reversibility prefers
    a stronger gate on unrecognized mutations).
    """
    if mode in IRREVERSIBLE_MODES:
        return "IRREVERSIBLE"
    if mode in MUTATE_MODES:
        return "MUTATE"
    if mode in READ_MODES:
        return "READ"
    # Unknown mode — be conservative; require full MUTATE gate discipline.
    return "MUTATE"


# ═══════════════════════════════════════════════════════════════════════════
# SESSION ADJUDICATORS — observe-only + judge-trace detection
# ═══════════════════════════════════════════════════════════════════════════


def _is_observe_only(session_id: str) -> bool:
    """Detect OBSERVE_ONLY authority via the canonical session identity.

    Reads from arifosmcp/runtime/session.py:get_session_identity().
    Honors both ``authority`` and ``authority_level`` fields so the gate
    stays correct across the bind_session_identity() and authority.py
    binding paths. Fail-closed on lookup error: returns False (treat as
    MUTATE-eligible) so a missing session does NOT escalate to OBSERVE_ONLY.
    """
    try:
        record = get_session_identity(session_id)
    except Exception as exc:  # pragma: no cover — defensive
        logger.debug("memory_gate: get_session_identity failed: %s", exc)
        return False
    if not record or not isinstance(record, dict):
        return False
    authority = str(record.get("authority") or "").upper()
    authority_level = str(record.get("authority_level") or "").upper()
    if authority == "OBSERVE_ONLY":
        return True
    if authority_level in {"L4_WARGA", "OBSERVE_ONLY"}:
        return True
    return False


def _has_judge_trace(session_id: str) -> bool:
    """Detect a prior arif_judge or arif_judge_deliberate tool call.

    F13 SOVEREIGN: forget / prune operations require prior judicial
    authorization in the same session. Without that trace, the gate
    refuses to execute (returns 888_HOLD — does not delete memory).

    Reads session.activity.history and inspects each entry's ``tool``
    key. Defensive on shape mismatch: returns False.
    """
    try:
        record = get_session_identity(session_id)
    except Exception as exc:  # pragma: no cover — defensive
        logger.debug("memory_gate: get_session_identity failed: %s", exc)
        return False
    if not record or not isinstance(record, dict):
        return False
    activity = record.get("activity") or {}
    history = activity.get("history") or []
    if not isinstance(history, list):
        return False
    judge_tools = {"arif_judge", "arif_judge_deliberate"}
    for entry in history:
        if not isinstance(entry, dict):
            continue
        tool = entry.get("tool")
        if isinstance(tool, str) and tool in judge_tools:
            return True
    return False


# ═══════════════════════════════════════════════════════════════════════════
# GATE — pre-execution floor verdict
# ═══════════════════════════════════════════════════════════════════════════


def pre_execution_floor_gate(
    mode: str,
    session_id: str | None,
    actor_id: str | None,
    *,
    memory_id: str | None = None,
) -> dict[str, Any]:
    """Run F1 / F11 / F13 floor gate BEFORE any arif_memory mutation.

    Args:
        mode: The arif_memory mode (store, forget, update, recall, etc.).
            Already mode-aliased by the caller if applicable.
        session_id: From the request — may be None when caller has not bound.
        actor_id: From the request — anonymous is treated as missing.
        memory_id: For forget / update — included in the receipt for audit.

    Returns:
        A verdict dict with:
          - verdict: ``"SEAL"`` | ``"SABAR"`` | ``"VOID"`` | ``"888_HOLD"``
          - operation_class: ``"READ"`` | ``"MUTATE"`` | ``"IRREVERSIBLE"``
          - floor_violation: SPECIFIC floor code (``"F1"`` / ``"F11"`` /
            ``"F13"``) or ``None``.
          - violated_laws: list of floor codes cited.
          - reason: human-readable citation (specific, never generic).
          - actor_token: SHA-256 fingerprint (never plaintext).
          - session_id: provided session_id or ``None``.
          - memory_id: provided memory_id or ``None``.
          - next_safe_action: single-line remediation hint.

        Verdict semantics:
          SEAL      — proceed with downstream check_laws() and execution.
          SABAR     — F1/F11 wait/empty: missing session or actor binding.
                       Per F9, no memory is fabricated; downstream caller
                       MUST translate this into an empty/non-fabricated
                       result.
          VOID      — F11 hard block: OBSERVE_ONLY against MUTATE class.
          888_HOLD  — F13 hard gate: IRREVERSIBLE without prior judge trace.
    """
    operation_class = classify_operation(mode)
    actor_token = _tokenize_actor(actor_id)
    base_payload = {
        "operation_class": operation_class,
        "mode": mode,
        "memory_id": memory_id,
        "session_id": session_id,
        "actor_token": actor_token,
    }

    # ── F1 AMANAH — session binding required for every operation ───────────
    if not session_id or not str(session_id).strip():
        return {
            **base_payload,
            "verdict": "SABAR",
            "floor_violation": "F1",
            "violated_laws": ["F1"],
            "reason": (
                "F1 AMANAH: session_id is required for all arif_memory "
                "operations. Without session binding, no memory can be "
                "attributed or audited. Returning SABAR (empty result). "
                "F9 ANTI-HANTU: we do not fabricate memory without session "
                "provenance."
            ),
            "next_safe_action": (
                "Bind a session via arif_init(session_id=...) and retry; "
                "arif_memory without session_id is SABAR/empty by F1 design."
            ),
        }

    # ── F11 AUDIT — actor_id is mandatory (no anonymous memory) ───────────
    if not actor_id or str(actor_id).strip().lower() in {"", "anonymous"}:
        return {
            **base_payload,
            "verdict": "SABAR",
            "floor_violation": "F11",
            "violated_laws": ["F11"],
            "reason": (
                "F11 AUDIT: actor_id is mandatory for arif_memory. Memory "
                "carries provenance and audit trail; without a verified "
                "actor, no receipt can be sealed. Returning SABAR (empty "
                "result). F9 ANTI-HANTU: never fabricate attributed memory."
            ),
            "next_safe_action": (
                "Provide a verified actor_id via arif_init + actor_signature, "
                "then retry; arif_memory refuses anonymous callers by F11."
            ),
        }

    # ── F11 OBSERVE_ONLY — MUTATE/IRREVERSIBLE needs MUTATE authority ──────
    if operation_class in {"MUTATE", "IRREVERSIBLE"} and _is_observe_only(session_id):
        return {
            **base_payload,
            "verdict": "VOID",
            "floor_violation": "F11",
            "violated_laws": ["F11"],
            "reason": (
                f"F11 AUDIT: session {session_id} authority is OBSERVE_ONLY; "
                f"{operation_class} class operation '{mode}' is blocked. "
                "Memory mutation requires MUTATE authority. OBSERVE_ONLY "
                "sessions may recall but not persist. (See authority_level "
                "in bind_session_identity / runtime/authority.py.)"
            ),
            "next_safe_action": (
                "Promote session to MUTATE/OPERATOR authority via "
                "arif_init(actor_signature=...), or retry with an observe-"
                "mode read (recall / list / audit)."
            ),
        }

    # ── F13 SOVEREIGN — forget / prune require prior judge trace ───────────
    if operation_class == "IRREVERSIBLE" and not _has_judge_trace(session_id):
        return {
            **base_payload,
            "verdict": "888_HOLD",
            "floor_violation": "F13",
            "violated_laws": ["F13", "F1"],
            "reason": (
                f"F13 SOVEREIGN: '{mode}' is IRREVERSIBLE and requires a prior "
                f"arif_judge trace in session {session_id}. Forget/tombstone/"
                f"delete operations cannot execute without sovereign (F13) "
                f"or judicial pre-authorization. Gate holds — forget is "
                f"NOT executed. See runtime/memory_gate.py:_has_judge_trace."
            ),
            "next_safe_action": (
                "Call arif_judge(mode=...) to authorize the forget operation, "
                "then retry arif_memory(mode='forget', ...). F13 path requires "
                "human sovereign ack for production data; for tests, "
                "pre-seed session activity history with arif_judge entries."
            ),
        }

    # ── All clear — proceed with downstream check_laws() + execution ───────
    return {
        **base_payload,
        "verdict": "SEAL",
        "floor_violation": None,
        "violated_laws": [],
        "reason": (
            f"All pre-execution floors clear ({operation_class} class) — "
            f"proceed to check_laws() and mode-specific execution."
        ),
        "next_safe_action": "Proceed — downstream check_laws() + execution.",
    }


# ═══════════════════════════════════════════════════════════════════════════
# HARNESS — verdict → response envelope (for caller convenience)
# ═══════════════════════════════════════════════════════════════════════════


def gate_to_envelope(
    gate_verdict: dict[str, Any],
    *,
    tool: str = "arif_memory_recall",
) -> dict[str, Any] | None:
    """Translate a gate verdict dict into the canonical _hold/_sabar envelope.

    Returns ``None`` when the verdict is ``SEAL`` (caller should proceed
    with check_laws() and execution untouched).

    For SABAR — F9 ANTI-HANTU — the envelope is an empty-result SABAR
    response. NO memory is fabricated. The downstream caller MUST surface
    this as the user-visible response.

    For VOID — F11 OBSERVE_ONLY — the envelope is a HOLD with specific
    F11 floor citation. The caller surfaces this and does NOT execute.

    For 888_HOLD — F13 IRREVERSIBLE — the envelope is a HOLD with F13 +
    F1 floor citations. The forget is NOT executed; the gate prevents it.
    """
    verdict = str(gate_verdict.get("verdict") or "").upper()
    if verdict == "SEAL":
        return None

    floor_violation = gate_verdict.get("floor_violation")
    violated_laws = list(gate_verdict.get("violated_laws") or [])
    reason = str(gate_verdict.get("reason") or "")
    next_safe_action = str(gate_verdict.get("next_safe_action") or "")
    operation_class = gate_verdict.get("operation_class")
    mode = gate_verdict.get("mode")
    actor_token = gate_verdict.get("actor_token")
    session_id = gate_verdict.get("session_id")
    memory_id = gate_verdict.get("memory_id")

    extra_meta = {
        "pre_execution_gate": gate_verdict,
        "floor_violation": floor_violation,
        "operation_class": operation_class,
        "gate_mode": mode,
        "actor_token": actor_token,
        "next_safe_action": next_safe_action,
    }
    if memory_id is not None:
        extra_meta["memory_id"] = memory_id

    # Lazy import to avoid circular dependency at module load time.
    from arifosmcp.runtime.tools import _hold, _sabar

    if verdict == "SABAR":
        # F9 anti-hantu: emit SABAR envelope; result is empty by design.
        return _sabar(
            tool,
            reason,
            session_id=session_id,
        )
    if verdict == "VOID":
        return _hold(
            tool,
            reason,
            floors=violated_laws,
            extra_meta=extra_meta,
            session_id=session_id,
        )
    if verdict in {"888_HOLD", "HOLD"}:
        return _hold(
            tool,
            reason,
            floors=violated_laws,
            extra_meta=extra_meta,
            session_id=session_id,
        )
    # Unknown verdict — fail closed with a HOLD on F2 TRUTH (specific citation).
    return _hold(
        tool,
        f"F2 TRUTH: unknown gate verdict {verdict!r} (floor_violation={floor_violation})",
        floors=["F2"],
        extra_meta=extra_meta,
        session_id=session_id,
    )


__all__ = [
    "MUTATE_MODES",
    "IRREVERSIBLE_MODES",
    "READ_MODES",
    "classify_operation",
    "pre_execution_floor_gate",
    "gate_to_envelope",
]
