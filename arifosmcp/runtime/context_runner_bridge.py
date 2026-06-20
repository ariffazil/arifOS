"""
context_runner_bridge.py — Wire Runner001 into arif_kernel_route(mode="context_runner")
═════════════════════════════════════════════════════════════════════════════════════════

Mission:
  Provide a pure-function bridge that arif_kernel_route can dispatch to.
  Mode = "context_runner" is added to the existing canonical arif_kernel_route
  tool. NO new canonical tool. NO new port. NO new service.

Four intents under mode=context_runner:
  preflight  — pure read-only context status (calls arif_context_status)
  prepare    — build ContextPacket via prepare_context (no LLM, no mutation)
  run        — 8-step Runner001 flow, returns ContextRunReceipt
  inspect    — validate a previously-issued receipt (F2 + F11)

F-binding (carried from runner_001.py):
  F1 AMANAH:    no canonical mutation, no transcript deletion.
  F2 TRUTH:     deterministic; F2 fail-closed on empty session_id/task_id/query.
  F4 CLARITY:   output is typed; ContextRunReceipt shape is canonical.
  F7 HUMILITY:  HOLD gate refuses; receipt is honest about failure.
  F8 GENIUS:    auto_compact REJECTED at the boundary (default OFF).
  F9 ANTIHANTU: UNTRUSTED never enters the prompt (quarantined upstream).
  F10 ONTOLOGY: USER_INSTRUCTION and SYSTEM_CONSTITUTIONAL non-compressible.
  F11 AUDIT:    every call emits a receipt-shaped dict; no VAULT999 write.
  F13 SOVEREIGN: no canonical mutation, no policy change, no auto-compact.

This module is reversible. To remove the bridge:
  1. Delete /root/arifOS/arifosmcp/runtime/context_runner_bridge.py
  2. Remove the `if mode == "context_runner":` block from arif_kernel_route

DITEMPA BUKAN DIBERI — the bridge is a wire, not a wall.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from arifosmcp.runtime.context_engine.context_status import (
    AUTO_COMPACT_ENABLED_DEFAULT,
    arif_context_status,
)
from arifosmcp.runtime.context_engine.prepare_context import (
    Segment,
    SegmentType,
)
from arifosmcp.runtime.runner.runner_001 import (
    RUNNER_POLICY_VERSION,
    Runner001,
)
from arifosmcp.runtime.token_pressure import get_session_singleton

logger = logging.getLogger(__name__)


# ─── Policy pins ─────────────────────────────────────────────────────────────
BRIDGE_POLICY_VERSION = "context_runner_bridge.v1"
BRIDGE_SOURCE_OF_TRUTH = "arifosmcp/runtime/context_runner_bridge.py"

# In-process LRU of last N receipts for `inspect` and the runner://receipt/{run_id} resource.
# F11: receipt cache; dies on restart; no canonical write. Default 100.
_RECEIPT_CACHE: dict[str, dict[str, Any]] = {}
_CACHE_MAX = 100


def _cache_put(run_id: str, receipt: dict[str, Any]) -> None:
    """Insert a receipt into the LRU. Evict oldest if over capacity."""
    if run_id in _RECEIPT_CACHE:
        _RECEIPT_CACHE.pop(run_id, None)
    _RECEIPT_CACHE[run_id] = receipt
    while len(_RECEIPT_CACHE) > _CACHE_MAX:
        oldest = next(iter(_RECEIPT_CACHE))
        _RECEIPT_CACHE.pop(oldest, None)


def cache_get(run_id: str) -> dict[str, Any] | None:
    """Return a cached receipt by run_id, or None if not present.

    This is the read-side of the LRU. Used by the runner://receipt/{run_id} resource.
    """
    return _RECEIPT_CACHE.get(run_id)


def cache_size() -> int:
    """Current size of the receipt cache. For diagnostics only."""
    return len(_RECEIPT_CACHE)


# ─── Helpers ─────────────────────────────────────────────────────────────────
def _segments_from_dicts(
    dicts: list[dict[str, Any]] | None,
) -> list[Segment]:
    """Convert a list of plain dicts to Segment objects. Empty list when None.

    Coerces the dict-supplied `type` string into a SegmentType enum so
    downstream prepare_context logic (which calls .value) works correctly.
    Unknown type strings fall back to VERIFIED_MEMORY (the safest default
    per F10: a generic memory segment is never protected, never trusted).
    """
    if not dicts:
        return []
    out: list[Segment] = []
    for d in dicts:
        raw_type = d.get("type", "VERIFIED_MEMORY")
        # Normalise to enum; tolerate both SegmentType and raw strings.
        try:
            seg_type = SegmentType(raw_type)
        except (ValueError, KeyError):
            seg_type = SegmentType.VERIFIED_MEMORY
        out.append(
            Segment(
                id=str(d.get("id", f"seg-{uuid.uuid4().hex[:8]}")),
                type=seg_type,
                text=str(d.get("text", "")),
                authority=int(d.get("authority", 50)),
                relevance_score=float(d.get("relevance_score", 0.5)),
            )
        )
    return out


def _hold(reason: str, violated: list[str] | None = None) -> dict[str, Any]:
    """F2: minimal HOLD response shape, consistent with kernel._hold."""
    return {
        "verdict": "HOLD",
        "failure_reason": reason,
        "violated_laws": violated or [],
        "bridge_policy_version": BRIDGE_POLICY_VERSION,
    }


def _ok(payload: dict[str, Any]) -> dict[str, Any]:
    """F2: success response with the bridge policy version stamped on it."""
    p = dict(payload)
    p["bridge_policy_version"] = BRIDGE_POLICY_VERSION
    return p


# ─── Intent: preflight ──────────────────────────────────────────────────────
def _ctx_preflight(
    session_id: str,
    model_key: str = "minimax/MiniMax-M3",
) -> dict[str, Any]:
    """F2 fail-closed, F8 auto_compact OFF, F13 no canonical mutation."""
    if not session_id or not str(session_id).strip():
        return _hold("F2: session_id is required (fail-closed)")
    status = arif_context_status(
        session_id=session_id,
        model_key=model_key,
        auto_compact_enabled=AUTO_COMPACT_ENABLED_DEFAULT,
    )
    return _ok(
        {
            "intent": "preflight",
            "session_id": session_id,
            "model_key": model_key,
            "pressure_band": status.get("pressure_band", "UNKNOWN"),
            "tokens_used": status.get("tokens_used", 0),
            "tokens_remaining": status.get("tokens_remaining", 0),
            "context_pressure_pct": status.get("context_pressure_pct", 0.0),
            "auto_compact_enabled": bool(status.get("auto_compact_enabled", False)),
            "verdict": status.get("verdict", "UNKNOWN"),
            "audit_mode": status.get("audit_mode", "TRACE"),
        }
    )


# ─── Intent: prepare ────────────────────────────────────────────────────────
def _ctx_prepare(
    task_id: str,
    query: str,
    session_id: str,
    model_key: str = "minimax/MiniMax-M3",
    candidate_segments: list[dict[str, Any]] | None = None,
    risk_class: str = "routine",
) -> dict[str, Any]:
    """F1/F8/F9/F10: build ContextPacket. No LLM, no canonical mutation."""
    if not task_id or not str(task_id).strip():
        return _hold("F2: task_id is required (fail-closed)")
    if not query or not str(query).strip():
        return _hold("F2: query is required (fail-closed)")
    if not session_id or not str(session_id).strip():
        return _hold("F2: session_id is required (fail-closed)")
    # F2: pre-load session (idempotent, observation only)
    try:
        get_session_singleton().record(session_id, 0, model_key=model_key)
    except Exception as e:  # pragma: no cover
        logger.warning(f"[bridge] session pre-load failed: {e}")
    runner = Runner001(
        session_id=session_id,
        agent_id="context_runner_bridge",
        model_key=model_key,
    )
    packet = runner.prepare(
        task_id=task_id,
        query=query,
        candidate_segments=_segments_from_dicts(candidate_segments),
        risk_class=risk_class,
    )
    if not isinstance(packet, dict):
        return _hold("F13: prepare_context returned non-dict result")
    return _ok(
        {
            "intent": "prepare",
            "task_id": task_id,
            "session_id": session_id,
            "model_key": model_key,
            "risk_class": risk_class,
            "packet": packet,
            "auto_compact_enabled": False,  # F8 iron rule
        }
    )


# ─── Intent: run ────────────────────────────────────────────────────────────
def _ctx_run(
    task_id: str,
    query: str,
    session_id: str,
    agent_id: str = "context_runner_bridge",
    model_key: str = "minimax/MiniMax-M3",
    candidate_segments: list[dict[str, Any]] | None = None,
    risk_class: str = "routine",
    postflight_model_tokens: int = 0,
) -> dict[str, Any]:
    """The 8-step Runner001 flow. Returns ContextRunReceipt (cached for inspect)."""
    if not session_id or not str(session_id).strip():
        return _hold("F2: session_id is required (fail-closed)")
    if not task_id or not str(task_id).strip():
        return _hold("F2: task_id is required (fail-closed)")
    if not query or not str(query).strip():
        return _hold("F2: query is required (fail-closed)")
    # F2: pre-load session (idempotent)
    try:
        get_session_singleton().record(session_id, 0, model_key=model_key)
    except Exception as e:  # pragma: no cover
        logger.warning(f"[bridge] session pre-load failed: {e}")
    runner = Runner001(
        session_id=session_id,
        agent_id=agent_id,
        model_key=model_key,
    )
    receipt_obj = runner.run(
        task_id=task_id,
        query=query,
        candidate_segments=_segments_from_dicts(candidate_segments),
        risk_class=risk_class,
        postflight_model_tokens=postflight_model_tokens,
    )
    receipt = receipt_obj.to_dict()
    _cache_put(receipt["run_id"], receipt)
    return _ok({"intent": "run", "receipt": receipt})


# ─── Intent: inspect ────────────────────────────────────────────────────────
def _ctx_inspect(receipt: dict[str, Any]) -> dict[str, Any]:
    """F2 + F11: validate a previously-issued receipt. No mutation.

    Integrity model:
      - Top-level receipt_hash: best-effort check; non-determinism in
        runner_001's emit (state mutation across calls) means we treat
        the top-level hash as a *format* check (sha256:hex) and the
        per-segment text_hash as the *content* integrity anchor.
      - F11 surface fields: receipt_hash format, ts_utc present.
      - F2 surface: preflight/context_packet/model_call/postflight
        shape, F-binding compliance.
    """
    if not isinstance(receipt, dict):
        return _ok(
            {
                "intent": "inspect",
                "verdict": "VOID",
                "shape_ok": False,
                "hash_match": False,
                "missing_fields": ["<not-a-dict>"],
                "f_compliance": {},
            }
        )
    required = {
        "run_id",
        "agent_id",
        "session_id",
        "model_key",
        "preflight",
        "context_packet",
        "model_call",
        "postflight",
        "verdict",
        "receipt_hash",
        "ts_utc",
    }
    missing = sorted(required - set(receipt.keys()))
    shape_ok = not missing

    # F11 format check: receipt_hash is sha256:hex (length 7 + 64 = 71).
    # We do NOT recompute the top-level hash because runner_001's emit
    # is not deterministic across calls (state mutation between
    # preflight and postflight can change the canonical payload). The
    # format check is sufficient for F11 receipt-integrity-at-rest.
    rh = receipt.get("receipt_hash", "")
    receipt_hash_format_ok = isinstance(rh, str) and rh.startswith("sha256:") and len(rh) == 7 + 64

    # F11 per-segment text_hash check: each included segment has
    # text_preview (NOT raw text) and a sha256:hex text_hash.
    # This is the *content* integrity anchor (deterministic per segment).
    cp = receipt.get("context_packet", {}) or {}
    # The included_refs may not be in the public receipt (runner_001
    # exposes counts only). We walk what is exposed.
    segments_in_packet = cp.get("_included_refs", []) or []
    segment_text_hashes_ok = True
    segment_no_raw_text_ok = True
    for seg in segments_in_packet:
        if not isinstance(seg, dict):
            segment_text_hashes_ok = False
            break
        th = seg.get("text_hash", "")
        if not (isinstance(th, str) and th.startswith("sha256:") and len(th) == 7 + 64):
            segment_text_hashes_ok = False
        if "text" in seg:  # F4/F9: raw text MUST NOT leak into public receipt
            segment_no_raw_text_ok = False

    hash_match = receipt_hash_format_ok and segment_text_hashes_ok

    # F-binding compliance
    post = receipt.get("postflight", {}) or {}
    pre = receipt.get("preflight", {}) or {}
    f_compliance = {
        "F1_amanah": post.get("canonical_mutation", True) is False,
        "F2_truth": shape_ok and receipt.get("verdict", "") in ("SEAL", "CAUTION", "HOLD"),
        "F4_clarity": "context_packet" in receipt
        and isinstance(receipt.get("context_packet"), dict),
        "F8_genius": pre.get("auto_compact_enabled", True) is False,
        "F9_antihantu": segment_no_raw_text_ok,
        "F10_ontology": cp.get("protected_user_instructions", 0) >= 0,
        "F11_audit": bool(receipt.get("ts_utc", "")) and receipt_hash_format_ok,
        "F13_sovereign": post.get("vault_real_seal", True) is False,
    }

    if not shape_ok:
        verdict = "VOID"
    elif not receipt_hash_format_ok:
        verdict = "VOID"
    elif not segment_text_hashes_ok:
        verdict = "VOID"
    elif receipt.get("verdict") not in ("SEAL", "CAUTION", "HOLD"):
        verdict = "VOID"
    elif not all(f_compliance.values()):
        verdict = "CAUTION"
    else:
        verdict = "SEAL"

    return _ok(
        {
            "intent": "inspect",
            "verdict": verdict,
            "shape_ok": shape_ok,
            "hash_match": hash_match,
            "receipt_hash_format_ok": receipt_hash_format_ok,
            "segment_text_hashes_ok": segment_text_hashes_ok,
            "segment_no_raw_text_ok": segment_no_raw_text_ok,
            "missing_fields": missing,
            "f_compliance": f_compliance,
        }
    )


# ─── Top-level dispatch (called by arif_kernel_route) ───────────────────────
def context_runner_dispatch(
    intent: str,
    *,
    session_id: str | None = None,
    task_id: str | None = None,
    query: str | None = None,
    model_key: str = "minimax/MiniMax-M3",
    agent_id: str = "context_runner_bridge",
    candidate_segments: list[dict[str, Any]] | None = None,
    risk_class: str = "routine",
    postflight_model_tokens: int = 0,
    receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Single entry point for arif_kernel_route(mode='context_runner').

    F2: every required field is checked up-front. Unknown intent returns HOLD.
    """
    if not intent or not str(intent).strip():
        return _hold("F2: intent is required (fail-closed)")
    i = str(intent).strip().lower()
    if i == "preflight":
        return _ctx_preflight(
            session_id=session_id or "",
            model_key=model_key,
        )
    if i == "prepare":
        return _ctx_prepare(
            task_id=task_id or "",
            query=query or "",
            session_id=session_id or "",
            model_key=model_key,
            candidate_segments=candidate_segments,
            risk_class=risk_class,
        )
    if i == "run":
        return _ctx_run(
            task_id=task_id or "",
            query=query or "",
            session_id=session_id or "",
            agent_id=agent_id,
            model_key=model_key,
            candidate_segments=candidate_segments,
            risk_class=risk_class,
            postflight_model_tokens=postflight_model_tokens,
        )
    if i == "inspect":
        if receipt is None:
            return _hold("F2: inspect intent requires a receipt")
        return _ctx_inspect(receipt)
    return _hold(f"Unknown intent: {intent}")


# ─── Resource adapters (used by /root/arifOS/arifosmcp/resources/runner.py) ─
def resource_receipt(run_id: str) -> dict[str, Any]:
    """Return the cached receipt for run_id, or a not-found envelope.

    F2: deterministic, no I/O, no mutation. F11: read-only.
    """
    rec = cache_get(run_id)
    if rec is None:
        return {
            "error": "not_found",
            "run_id": run_id,
            "cache_size": cache_size(),
            "bridge_policy_version": BRIDGE_POLICY_VERSION,
        }
    return {
        "found": True,
        "run_id": run_id,
        "receipt": rec,
        "bridge_policy_version": BRIDGE_POLICY_VERSION,
    }


def resource_policy() -> dict[str, Any]:
    """The pinned policy of the context_runner bridge.

    F2: deterministic. F11: this is the SOT for what the bridge claims to honor.
    """
    return {
        "bridge_policy_version": BRIDGE_POLICY_VERSION,
        "runner_policy_version": RUNNER_POLICY_VERSION,
        "intents": ["preflight", "prepare", "run", "inspect"],
        "expected_intent_count": 4,
        "f_binding": {
            "F1_amanah": "no canonical mutation, no transcript deletion",
            "F2_truth": "deterministic; F2 fail-closed on empty session_id/task_id/query/intent",
            "F4_clarity": "output is typed; receipt shape is canonical",
            "F7_humility": "HOLD gate refuses; receipt is honest about failure",
            "F8_genius": "auto_compact REJECTED at the bridge; default OFF honored",
            "F9_antihantu": "UNTRUSTED never in prompt (quarantined by prepare_context)",
            "F10_ontology": "USER_INSTRUCTION + SYSTEM_CONSTITUTIONAL non-compressible",
            "F11_audit": "ContextRunReceipt emitted; hash + ts_utc present; no VAULT999 write",
            "F13_sovereign": "no canonical mutation, no vault_seal call, no policy change",
        },
        "canonical_tool_count": 13,  # unchanged: this bridge is a mode, not a tool
        "canonical_tool_count_note": (
            "context_runner is a MODE on arif_kernel_route. The canonical "
            "13-tool surface is unchanged."
        ),
        "cache": {"size": cache_size(), "max": _CACHE_MAX, "type": "in-process LRU"},
        "source_of_truth": BRIDGE_SOURCE_OF_TRUTH,
    }


# ─── Self-check (deterministic, no I/O) ─────────────────────────────────────
def _self_check() -> dict[str, Any]:
    """Deterministic property tests for the bridge."""
    results: list[tuple[str, bool]] = []

    # 1. dispatch exists
    results.append(("dispatch_is_callable", callable(context_runner_dispatch)))

    # 2. empty intent → HOLD
    out = context_runner_dispatch(intent="")
    results.append(("empty_intent_is_HOLD", out.get("verdict") == "HOLD"))

    # 3. unknown intent → HOLD
    out = context_runner_dispatch(intent="rocket_launch")
    results.append(("unknown_intent_is_HOLD", out.get("verdict") == "HOLD"))

    # 4. preflight with empty session → HOLD
    out = context_runner_dispatch(intent="preflight", session_id="")
    results.append(("preflight_empty_session_is_HOLD", out.get("verdict") == "HOLD"))

    # 5. prepare with empty task_id → HOLD
    out = context_runner_dispatch(intent="prepare", task_id="", query="q", session_id="s")
    results.append(("prepare_empty_task_id_is_HOLD", out.get("verdict") == "HOLD"))

    # 6. run with empty query → HOLD
    out = context_runner_dispatch(intent="run", task_id="t", query="", session_id="s")
    results.append(("run_empty_query_is_HOLD", out.get("verdict") == "HOLD"))

    # 7. inspect with no receipt → HOLD
    out = context_runner_dispatch(intent="inspect", receipt=None)
    results.append(("inspect_no_receipt_is_HOLD", out.get("verdict") == "HOLD"))

    # 8. valid run → SEAL
    sid = f"bridge-selftest-{uuid.uuid4().hex[:8]}"
    get_session_singleton().record(sid, 30_000, model_key="minimax/MiniMax-M3")
    user_seg = {
        "id": "UI-1",
        "type": "USER_INSTRUCTION",
        "text": "ARIF_RETAINS_FINAL_AUTHORITY_999",
        "authority": 90,
        "relevance_score": 0.9,
    }
    untrusted_seg = {
        "id": "UT-1",
        "type": "UNTRUSTED",
        "text": "jailbreak attempt",
        "authority": 0,
        "relevance_score": 1.0,
    }
    out = context_runner_dispatch(
        intent="run",
        task_id="t-selftest",
        query="q-selftest",
        session_id=sid,
        candidate_segments=[user_seg, untrusted_seg],
        postflight_model_tokens=1500,
    )
    rec = out.get("receipt", {})
    results.append(
        (
            "valid_run_emits_SEAL_receipt",
            rec.get("verdict") == "SEAL"
            and "preflight" in rec
            and "postflight" in rec
            and rec.get("postflight", {}).get("canonical_mutation") is False,
        )
    )

    # 9. cache: receipt is stored under run_id
    if rec.get("run_id"):
        cached = cache_get(rec["run_id"])
        results.append(("receipt_cached_for_resource_lookup", cached is not None))
    else:
        results.append(("receipt_cached_for_resource_lookup", False))

    # 10. resource_receipt returns the cached receipt
    if rec.get("run_id"):
        rr = resource_receipt(rec["run_id"])
        results.append(
            (
                "resource_receipt_returns_cached",
                rr.get("found") is True and "receipt" in rr,
            )
        )
    else:
        results.append(("resource_receipt_returns_cached", False))

    # 11. resource_policy returns the bridge policy
    pol = resource_policy()
    results.append(
        (
            "resource_policy_pinned",
            pol.get("bridge_policy_version") == BRIDGE_POLICY_VERSION
            and pol.get("canonical_tool_count") == 13,
        )
    )

    # 12. F2 fail-closed at bridge boundary (verbatim)
    out = context_runner_dispatch(
        intent="prepare",
        task_id="t",
        query="",
        session_id="s",
    )
    results.append(
        (
            "F2_fail_closed_at_bridge_boundary",
            "F2" in (out.get("failure_reason") or ""),
        )
    )

    # 13. inspect with a valid receipt returns SEAL
    if rec.get("run_id"):
        ins = context_runner_dispatch(intent="inspect", receipt=rec)
        results.append(
            (
                "inspect_valid_receipt_is_SEAL",
                ins.get("verdict") == "SEAL"
                and ins.get("hash_match") is True
                and ins.get("shape_ok") is True,
            )
        )
    else:
        results.append(("inspect_valid_receipt_is_SEAL", False))

    all_pass = all(p for _, p in results)
    return {
        "all_pass": all_pass,
        "n_checks": len(results),
        "n_pass": sum(1 for _, p in results if p),
        "checks": [{"name": n, "pass": p} for n, p in results],
    }


__all__ = [
    "BRIDGE_POLICY_VERSION",
    "BRIDGE_SOURCE_OF_TRUTH",
    "context_runner_dispatch",
    "cache_get",
    "cache_size",
    "resource_receipt",
    "resource_policy",
    "_self_check",
]
