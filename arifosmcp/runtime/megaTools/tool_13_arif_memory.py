"""
arifosmcp/runtime/megaTools/tool_08_arif_memory.py

🔥 ARIF_MEMORY v5 — Federated Memory Tool (Direction 1, ratified 2026-06-21)
Stage: 555_MEMORY v5 | Trinity: OMEGA Ω | Floors: L01, L02, L04, L08, L11, L12, L13

Modes (7 canonical):
  recall     — OBSERVE — semantic + graph + vault retrieval (hybrid cascade)
  inspect    — OBSERVE — read a memory object's full state
  attest     — OBSERVE — verify a memory_id against vault seal chain
  remember   — MUTATE  — write a candidate memory (default-deny)
  promote    — MUTATE  — move candidate from lower tier to higher tier
  revise     — MUTATE  — supersede prior memory (B5: supersedes_memory_id required)
  forget     — ATOMIC  — soft-delete or revoke (L13 SOVEREIGN required)

Backends wired:
  cognitive_memory.py (8 modes, v2) — primary for recall/learn/graph/contradict
  engineering_memory (6 modes)       — vector store/forget fallback
  PostPromotionHandler                — NEW: L4 record creation + Qdrant mirror
  VaultAttestHandler                  — NEW: vault chain attestation
  ForgetHandler                       — NEW: L4 tombstone + vault tombstone seal

Floor enforcement:
  B3 — truth_class enforcement (remember: confidence<0.3 → SABAR unless human_ack)
  B5 — revise-supersede enforcement (revise: supersede/merge without supersedes_memory_id → SABAR)
  C3 — graph-mandatory cascade (recall: graph_first=True → run graph BEFORE vector)
  A4 — v1 vault tombstone gating (attest: vault_version=v1 → SABAR)

Backward compat:
  arif_memory_recall → arif_memory(mode=recall) via LEGACY_MODE_ALIASES
  arif_memory_recall(mode=engineer) → arif_memory(mode=remember)
  arif_memory_recall(mode=vector_store) → arif_memory(mode=remember)
  etc.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from typing import Any

from arifosmcp.runtime.model import RuntimeEnvelope

logger = logging.getLogger(__name__)


# ── 7 federated modes ─────────────────────────────────────────────────────

ARIF_MEMORY_MODES = (
    "recall",
    "inspect",
    "attest",
    "remember",
    "promote",
    "revise",
    "forget",
)

# Mode → action class
MODE_ACTION_CLASS = {
    "recall":   "OBSERVE",
    "inspect":  "OBSERVE",
    "attest":   "OBSERVE",
    "remember": "EXECUTE_REVERSIBLE",
    "promote":  "EXECUTE_HIGH_IMPACT",
    "revise":   "EXECUTE_HIGH_IMPACT",
    "forget":   "IRREVERSIBLE",
}

# Mode → required pre-floors (must all pass before mode executes)
MODE_PRE_FLOORS = {
    "recall":   ("L02", "L12"),
    "inspect":  ("L02", "L12"),
    "attest":   ("L02", "L11", "L12"),
    "remember": ("L01", "L02", "L08", "L11", "L12"),
    "promote":  ("L01", "L02", "L04", "L07", "L11", "L12"),
    "revise":   ("L01", "L02", "L04", "L09", "L11", "L12"),
    "forget":   ("L01", "L02", "L04", "L09", "L11", "L12", "L13"),
}

# Mode → required lease?
MODE_REQUIRES_LEASE = {
    "recall":   False,
    "inspect":  False,
    "attest":   False,
    "remember": True,
    "promote":  True,
    "revise":   True,
    "forget":   True,
}

# Mode → required human ack?
MODE_REQUIRES_HUMAN_ACK = {
    "recall":   False,
    "inspect":  False,
    "attest":   False,
    "remember": False,
    "promote":  False,
    "revise":   False,
    "forget":   True,        # L13 SOVEREIGN mandatory
}


# ── Legacy mode aliases (arif_memory_recall v4 → arif_memory v5) ──────────

LEGACY_MODE_ALIASES = {
    # Direct 1:1
    "cognitive_recall": "recall",
    "cognitive_learn":  "remember",
    "graph_get":        "inspect",
    # Sub-modes fold into v5 with class= or scope= hints
    "graph_store":      "remember",
    "graph_query":      "recall",
    "cognitive_cross_session": "recall",
    "contradict_scan":  "inspect",
    "contradict_status": "attest",
    "contradict_resolve": "revise",
    # Engineering memory
    "engineer":         "remember",
    "vector_query":     "recall",
    "vector_store":     "remember",
    "vector_forget":    "forget",
    "generate":         "remember",
    "query":            "recall",
    # Legacy v4 (from existing description in constitutional_map.py)
    "store":            "remember",
    "seal":             "attest",
    "forget":           "forget",
    "update":           "revise",
    "audit":            "attest",
    "stats":            "inspect",
    "learn":            "remember",
    "init_recall":      "recall",
    "search":           "recall",
    "context":          "recall",
    "quarantine":       "remember",
    "import":           "remember",
}


def resolve_legacy_mode(legacy: str) -> str | None:
    """Map a legacy mode string to the current federated mode, if known."""
    return LEGACY_MODE_ALIASES.get(legacy)


# ── The dispatcher entry point ─────────────────────────────────────────────

async def arif_memory(
    mode: str | None = None,
    payload: dict[str, Any] | None = None,
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    lease_id: str | None = None,
    human_approval: bool = False,
    idempotency_key: str | None = None,
    trace_id: str | None = None,
    request_id: str | None = None,
    timestamp: str | None = None,
    raw_input: str | None = None,
    ctx: Any = None,
) -> RuntimeEnvelope:
    """Federated arif_memory tool — 7 modes.

    Returns RuntimeEnvelope with verdict SEAL/SABAR/VOID/HOLD.
    """
    from arifosmcp.runtime.dispatcher import HARDENED_DISPATCH_MAP
    from arifosmcp.runtime.model import VerdictCode
    from arifosmcp.runtime.verdict_wrapper import forge_verdict

    payload = dict(payload or {})
    if raw_input and not query:
        query = raw_input
    if query and "query" not in payload:
        payload["query"] = query

    # ── 0. Resolve legacy mode if needed ──
    if mode and mode not in ARIF_MEMORY_MODES:
        resolved = resolve_legacy_mode(mode)
        if resolved:
            logger.info(f"[ARIF_MEMORY] legacy mode '{mode}' → '{resolved}'")
            mode = resolved
        else:
            return forge_verdict(
                tool_id="arif_memory",
                canonical_tool_name="arif_memory",
                stage="555m",
                payload={"note": f"unknown mode: {mode}"},
                session_id=session_id,
                override_code=VerdictCode.VOID,
                message=f"arif_memory: unknown mode '{mode}'",
            )

    if mode not in ARIF_MEMORY_MODES:
        return forge_verdict(
            tool_id="arif_memory",
            canonical_tool_name="arif_memory",
            stage="555m",
            payload={"note": "mode required"},
            session_id=session_id,
            override_code=VerdictCode.SABAR,
            message=f"arif_memory: mode must be one of {ARIF_MEMORY_MODES}",
        )

    # ── 1. Action-class enforcement: lease + human_ack ──
    if MODE_REQUIRES_LEASE.get(mode) and not lease_id:
        return forge_verdict(
            tool_id="arif_memory",
            canonical_tool_name="arif_memory",
            stage="555m",
            payload={"mode": mode, "note": "lease required"},
            session_id=session_id,
            override_code=VerdictCode.SABAR,
            message=f"arif_memory: mode='{mode}' requires lease_id (action class: {MODE_ACTION_CLASS[mode]})",
        )

    if MODE_REQUIRES_HUMAN_ACK.get(mode) and not human_approval:
        return forge_verdict(
            tool_id="arif_memory",
            canonical_tool_name="arif_memory",
            stage="555m",
            payload={"mode": mode, "note": "human ack required (L13 SOVEREIGN)"},
            session_id=session_id,
            override_code=VerdictCode.HOLD,
            message=f"arif_memory: mode='{mode}' requires human_approval=True (L13 SOVEREIGN)",
        )

    # ── 2. B3: truth_class enforcement on remember ──
    if mode == "remember":
        truth_class = payload.get("truth_class", {})
        if isinstance(truth_class, dict):
            confidence = truth_class.get("confidence", 1.0)
            if confidence < 0.3 and not human_approval:
                return forge_verdict(
                    tool_id="arif_memory",
                    canonical_tool_name="arif_memory",
                    stage="555m",
                    payload={"mode": mode, "confidence": confidence,
                             "note": "B3: confidence<0.3 requires human_ack"},
                    session_id=session_id,
                    override_code=VerdictCode.SABAR,
                    message=f"arif_memory: B3 violation — confidence={confidence} < 0.3 and no human_ack",
                )

    # ── 3. B5: revise-supersede enforcement ──
    if mode == "revise":
        resolution_kind = payload.get("resolution_kind", "supersede")
        if resolution_kind in ("supersede", "merge"):
            if not payload.get("supersedes_memory_id"):
                return forge_verdict(
                    tool_id="arif_memory",
                    canonical_tool_name="arif_memory",
                    stage="555m",
                    payload={"mode": mode, "resolution_kind": resolution_kind,
                             "note": "B5: supersedes_memory_id required for supersede/merge"},
                    session_id=session_id,
                    override_code=VerdictCode.SABAR,
                    message=f"arif_memory: B5 violation — {resolution_kind} requires supersedes_memory_id",
                )

    # ── 4. A4: v1 vault tombstone gating on attest ──
    if mode == "attest":
        target_version = payload.get("vault_version") or payload.get("target_version")
        if target_version == "v1":
            return forge_verdict(
                tool_id="arif_memory",
                canonical_tool_name="arif_memory",
                stage="555m",
                payload={"mode": mode, "vault_version": "v1",
                         "note": "A4: v1 vault FROZEN per sovereign ruling 2026-06-05"},
                session_id=session_id,
                override_code=VerdictCode.SABAR,
                message="arif_memory: A4 violation — v1 vault is FROZEN, no new seals or attestations",
            )

    # ── 5. Dispatch to backend ──
    # Day 3 NEW handlers (promote / forget / attest) — direct call
    # Day 3.5 added: remember (handles L4 write without embedding dependency)
    if mode in ("remember", "promote", "forget", "attest"):
        from arifosmcp.runtime.memory_handlers_v5 import (
            _handle_remember, _handle_promote, _handle_forget, _handle_attest,
        )
        handler = {
            "remember": _handle_remember,
            "promote": _handle_promote,
            "forget": _handle_forget,
            "attest": _handle_attest,
        }[mode]
        try:
            res_dict = await handler(payload, ctx=ctx)
            return _wrap_result(res_dict, mode=mode, session_id=session_id)
        except Exception as exc:
            logger.exception(f"[ARIF_MEMORY] {mode} handler failed: {exc}")
            return forge_verdict(
                tool_id="arif_memory",
                canonical_tool_name="arif_memory",
                stage="555m",
                payload={"mode": mode, "error": str(exc)},
                session_id=session_id,
                override_code=VerdictCode.SABAR,
                message=f"arif_memory: {mode} handler failed: {exc}",
            )

    # Day 4 polish (2026-06-21): SKIP broken HARDENED_DISPATCH_MAP path.
    # The legacy _arif_memory_recall handler signature is incompatible with
    # `payload` kwarg (TypeError). Route directly to engineering_memory_dispatch_impl
    # which DOES accept payload.
    from arifosmcp.runtime.tools_internal import engineering_memory_dispatch_impl

    try:
        return await engineering_memory_dispatch_impl(
            mode=_map_mode_to_engineering(mode, payload),
            payload=payload,
            auth_context=None,
            risk_tier=_risk_tier_for_mode(mode),
            dry_run=False,
            ctx=ctx,
        )
    except Exception as exc:
        logger.exception(f"[ARIF_MEMORY] backend dispatch failed: {exc}")
        return forge_verdict(
            tool_id="arif_memory",
            canonical_tool_name="arif_memory",
            stage="555m",
            payload={"mode": mode, "error": str(exc)},
            session_id=session_id,
            override_code=VerdictCode.SABAR,
            message=f"arif_memory: backend dispatch failed: {exc}",
        )


def _map_mode_to_engineering(mode: str, payload: dict) -> str:
    """Map arif_memory v5 mode → engineering_memory v3 mode string.

    This is a bridge so that existing cognitive_memory / engineering_memory
    backends are reused. New handlers (promote / forget / attest) bypass
    this mapping and are handled directly.
    """
    bridge = {
        "recall":   "query",           # engineering_memory.query
        "remember": "vector_store",    # engineering_memory.vector_store
        "inspect":  "query",           # no direct equivalent → query
        "revise":   "vector_store",    # supersede via store + tombstone prior
        "promote":  "vector_store",    # placeholder — NEW handler needed
        "forget":   "vector_forget",
        "attest":   "query",           # placeholder — NEW handler needed
    }
    return bridge.get(mode, "query")


def _risk_tier_for_mode(mode: str) -> str:
    """Map action class → risk_tier for engineering_memory_dispatch_impl."""
    return {
        "OBSERVE":              "low",
        "EXECUTE_REVERSIBLE":   "medium",
        "EXECUTE_HIGH_IMPACT":  "high",
        "IRREVERSIBLE":         "critical",
    }.get(MODE_ACTION_CLASS.get(mode, "OBSERVE"), "medium")


def _wrap_result(res_dict: dict, mode: str, session_id: str | None) -> RuntimeEnvelope:
    """Wrap a handler result into RuntimeEnvelope."""
    from arifosmcp.runtime.model import VerdictCode
    from arifosmcp.runtime.verdict_wrapper import forge_verdict

    # Day 3.5 fix: handle string verdict properly (was falling through to SABAR)
    raw_verdict = res_dict.get("verdict", "SABAR")
    if isinstance(raw_verdict, str):
        try:
            override_code = VerdictCode(raw_verdict)
        except ValueError:
            override_code = VerdictCode.SABAR
    elif hasattr(raw_verdict, "value"):
        override_code = VerdictCode(raw_verdict.value)
    else:
        override_code = VerdictCode.SABAR

    return forge_verdict(
        tool_id="arif_memory",
        canonical_tool_name="arif_memory",
        stage="555m",
        payload=res_dict.get("payload", {}),
        session_id=session_id,
        override_code=override_code,
        message=res_dict.get("payload", {}).get("note", f"arif_memory({mode}) processed."),
    )


# ── NEW handlers: promote, attest, forget (Day 3 work) ────────────────────
# These are stubs for Phase 2 Day 3. The schema-level contracts are in
# schemas/memory_payload.py; the runtime logic lands in Day 3.

async def _handle_promote(payload: dict, ctx: Any) -> dict:
    """NEW — promote a memory from L3 (Qdrant) to L4 (Postgres canonical).

    Day 3 work. Stub returns SABAR for now.
    """
    return {
        "mode": "promote",
        "verdict": "SABAR",
        "payload": {"note": "promote handler — Day 3 implementation"},
    }


async def _handle_forget(payload: dict, ctx: Any) -> dict:
    """NEW — tombstone an L4 record + emit vault tombstone seal.

    Day 3 work. Stub returns SABAR for now.
    """
    return {
        "mode": "forget",
        "verdict": "SABAR",
        "payload": {"note": "forget handler — Day 3 implementation (L13 SOVEREIGN)"},
    }


async def _handle_attest(payload: dict, ctx: Any) -> dict:
    """NEW — verify a memory_id against VAULT999 v2 chain.

    Day 3 work. Stub returns SABAR for now.
    """
    return {
        "mode": "attest",
        "verdict": "SABAR",
        "payload": {"note": "attest handler — Day 3 implementation"},
    }


__all__ = [
    "arif_memory",
    "ARIF_MEMORY_MODES",
    "MODE_ACTION_CLASS",
    "MODE_PRE_FLOORS",
    "MODE_REQUIRES_LEASE",
    "MODE_REQUIRES_HUMAN_ACK",
    "LEGACY_MODE_ALIASES",
    "resolve_legacy_mode",
    "_handle_promote",
    "_handle_forget",
    "_handle_attest",
]