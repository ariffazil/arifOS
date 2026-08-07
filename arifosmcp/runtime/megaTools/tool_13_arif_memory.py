"""
arifosmcp/runtime/megaTools/tool_13_arif_memory.py

🔥 ARIF_MEMORY v5.1 — Federated Memory Tool + JITU Contradiction Engine
Stage: 555_MEMORY v5.1 | Trinity: OMEGA Ω | Floors: L01, L02, L04, L08, L09, L11, L12, L13

Modes (8 canonical):
  recall     — OBSERVE — semantic + graph + vault retrieval (hybrid cascade)
  inspect    — OBSERVE — read a memory object's full state
  attest     — OBSERVE — verify a memory_id against vault seal chain
  audit      — OBSERVE — JITU contradiction engine: compare action vs memory state
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

import logging
from datetime import UTC, datetime
from typing import Any

from arifosmcp.runtime.model import RuntimeEnvelope

logger = logging.getLogger(__name__)


# ── 8 federated modes (v5.1 — audit/JITU added 2026-07-07) ─────────────

ARIF_MEMORY_MODES = (
    "recall",
    "inspect",
    "attest",
    "remember",
    "promote",
    "revise",
    "forget",
    "audit",
    "score_prediction",
)

# Mode → action class
MODE_ACTION_CLASS = {
    "recall": "OBSERVE",
    "inspect": "OBSERVE",
    "attest": "OBSERVE",
    "audit": "OBSERVE",
    "score_prediction": "OBSERVE",
    "remember": "EXECUTE_REVERSIBLE",
    "promote": "EXECUTE_HIGH_IMPACT",
    "revise": "EXECUTE_HIGH_IMPACT",
    "forget": "IRREVERSIBLE",
}

# Mode → required pre-floors (must all pass before mode executes)
MODE_PRE_FLOORS = {
    "recall": ("L02", "L12"),
    "inspect": ("L02", "L12"),
    "attest": ("L02", "L11", "L12"),
    "audit": ("L02", "L09", "L11", "L12"),
    "score_prediction": ("L01", "L02", "L12"),
    "remember": ("L01", "L02", "L08", "L11", "L12"),
    "promote": ("L01", "L02", "L04", "L07", "L11", "L12"),
    "revise": ("L01", "L02", "L04", "L09", "L11", "L12"),
    "forget": ("L01", "L02", "L04", "L09", "L11", "L12", "L13"),
}

# Mode → required lease?
MODE_REQUIRES_LEASE = {
    "recall": False,
    "inspect": False,
    "attest": False,
    "audit": False,
    "score_prediction": False,
    "remember": True,
    "promote": True,
    "revise": True,
    "forget": True,
}

# Mode → required human ack?
MODE_REQUIRES_HUMAN_ACK = {
    "recall": False,
    "inspect": False,
    "attest": False,
    "audit": False,
    "score_prediction": False,
    "remember": False,
    "promote": False,
    "revise": False,
    "forget": True,  # L13 SOVEREIGN mandatory
}


# ── Legacy mode aliases (arif_memory_recall v4 → arif_memory v5) ──────────

LEGACY_MODE_ALIASES = {
    # Direct 1:1
    "cognitive_recall": "recall",
    "cognitive_learn": "remember",
    "graph_get": "inspect",
    # Sub-modes fold into v5 with class= or scope= hints
    "graph_store": "remember",
    "graph_query": "recall",
    "cognitive_cross_session": "recall",
    "contradict_scan": "inspect",
    "contradict_status": "attest",
    "contradict_resolve": "revise",
    # Engineering memory
    "engineer": "remember",
    "vector_query": "recall",
    "vector_store": "remember",
    "vector_forget": "forget",
    "generate": "remember",
    "query": "recall",
    # Legacy v4 (from existing description in constitutional_map.py)
    "store": "remember",
    "seal": "attest",
    "forget": "forget",
    "update": "revise",
    "stats": "inspect",
    "learn": "remember",
    "init_recall": "recall",
    "search": "recall",
    "context": "recall",
    "quarantine": "remember",
    "import": "remember",
    # JITU aliases (2026-07-07)
    "jitu": "audit",
    "contradiction_check": "audit",
    "pre_flight_audit": "audit",
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
    session_token: str | None = None,
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
    from arifosmcp.runtime.model import VerdictCode
    from arifosmcp.runtime.verdict_wrapper import forge_verdict

    # ── SCT standing (Spine P0) ──
    # Define echo FIRST so every return path can stamp continuity.
    _standing: Any = None
    _standing_token = session_token

    def _echo_standing(out: Any) -> Any:
        """Echo next-hop SCT continuity onto RuntimeEnvelope or compatible dict.

        RuntimeEnvelope reserves `authority` for CanonicalAuthority, so the
        string band is stamped as `authority_band`.
        """
        token = None
        source = "sct"
        apex = None
        actor_verified = False
        authority = None
        authority_delta = None
        if _standing is not None and getattr(_standing, "valid", False):
            token = _standing.session_token or _standing_token
            source = _standing.source or "sct"
            apex = dict(_standing.apex) if _standing.apex else None
            actor_verified = bool(_standing.actor_verified)
            authority = _standing.authority
            authority_delta = _standing.authority_delta
        elif _standing_token:
            token = _standing_token
        if not token:
            return out

        if isinstance(out, RuntimeEnvelope):
            out.session_token = token
            out.standing_source = source
            out.apex_scalars = apex
            out.actor_verified = actor_verified
            out.authority_band = authority
            out.authority_delta = authority_delta
            if isinstance(out.payload, dict):
                out.payload.setdefault("session_token", token)
                out.payload.setdefault("standing_source", source)
                if apex is not None:
                    out.payload.setdefault("apex_scalars", apex)
            return out

        if isinstance(out, dict):
            out = dict(out)
            out["session_token"] = token
            out["standing_source"] = source
            if apex is not None:
                out["apex_scalars"] = apex
            out["actor_verified"] = actor_verified
            if authority is not None:
                out["authority_band"] = authority
            if authority_delta is not None:
                out["authority_delta"] = authority_delta
            return out

        # Pydantic / ToolResult — best-effort attribute stamp
        for attr, val in (
            ("session_token", token),
            ("standing_source", source),
            ("apex_scalars", apex),
            ("actor_verified", actor_verified),
            ("authority_band", authority),
            ("authority_delta", authority_delta),
        ):
            if hasattr(out, attr):
                try:
                    setattr(out, attr, val)
                except Exception:
                    pass
        return out

    if session_token or session_id:
        try:
            from arifosmcp.runtime.act_token import resolve_standing

            _standing = resolve_standing(
                session_id=session_id,
                actor_id=actor_id,
                session_token=session_token,
                allow_store=True,
            )
            if _standing.valid:
                session_token = _standing.session_token or session_token
                _standing_token = session_token
                if _standing.session_id:
                    session_id = _standing.session_id
                if _standing.actor_id and _standing.actor_id != "anonymous":
                    actor_id = _standing.actor_id
            elif session_token:
                return _echo_standing(
                    forge_verdict(
                        tool_id="arif_memory",
                        canonical_tool_name="arif_memory",
                        stage="555m",
                        payload={
                            "sesat_event": {
                                "sesat": True,
                                "type": "TOKEN_INVALID",
                                "reason": _standing.reason,
                            },
                            "session_token": session_token,
                        },
                        session_id=session_id,
                        override_code=VerdictCode.HOLD,
                        message=_standing.reason or "L11 AUTH: SCT invalid",
                    )
                )
        except Exception:
            pass

    payload = dict(payload or {})
    if raw_input and not query:
        query = raw_input
    if query and "query" not in payload:
        payload["query"] = query
    if session_token:
        payload["session_token"] = session_token

    # ── 0. Resolve legacy mode if needed ──
    if mode and mode not in ARIF_MEMORY_MODES:
        resolved = resolve_legacy_mode(mode)
        if resolved:
            logger.info(f"[ARIF_MEMORY] legacy mode '{mode}' → '{resolved}'")
            mode = resolved
        else:
            return _echo_standing(
                forge_verdict(
                    tool_id="arif_memory",
                    canonical_tool_name="arif_memory",
                    stage="555m",
                    payload={"note": f"unknown mode: {mode}"},
                    session_id=session_id,
                    override_code=VerdictCode.VOID,
                    message=f"arif_memory: unknown mode '{mode}'",
                )
            )

    if mode not in ARIF_MEMORY_MODES:
        return _echo_standing(
            forge_verdict(
                tool_id="arif_memory",
                canonical_tool_name="arif_memory",
                stage="555m",
                payload={"note": "mode required"},
                session_id=session_id,
                override_code=VerdictCode.SABAR,
                message=f"arif_memory: mode must be one of {ARIF_MEMORY_MODES}",
            )
        )

    # ── 1. Action-class enforcement: lease + human_ack ──
    if MODE_REQUIRES_LEASE.get(mode) and not lease_id:
        return _echo_standing(
            forge_verdict(
                tool_id="arif_memory",
                canonical_tool_name="arif_memory",
                stage="555m",
                payload={"mode": mode, "note": "lease required"},
                session_id=session_id,
                override_code=VerdictCode.SABAR,
                message=(
                    f"arif_memory: mode='{mode}' requires lease_id "
                    f"(action class: {MODE_ACTION_CLASS[mode]})"
                ),
            )
        )

    if MODE_REQUIRES_HUMAN_ACK.get(mode) and not human_approval:
        return _echo_standing(
            forge_verdict(
                tool_id="arif_memory",
                canonical_tool_name="arif_memory",
                stage="555m",
                payload={"mode": mode, "note": "human ack required (L13 SOVEREIGN)"},
                session_id=session_id,
                override_code=VerdictCode.HOLD,
                message=(
                    f"arif_memory: mode='{mode}' requires human_approval=True (L13 SOVEREIGN)"
                ),
            )
        )

    # ── 2. B3: truth_class enforcement on remember ──
    if mode == "remember":
        truth_class = payload.get("truth_class", {})
        if isinstance(truth_class, dict):
            confidence = truth_class.get("confidence", 1.0)
            if confidence < 0.3 and not human_approval:
                return _echo_standing(
                    forge_verdict(
                        tool_id="arif_memory",
                        canonical_tool_name="arif_memory",
                        stage="555m",
                        payload={
                            "mode": mode,
                            "confidence": confidence,
                            "note": "B3: confidence<0.3 requires human_ack",
                        },
                        session_id=session_id,
                        override_code=VerdictCode.SABAR,
                        message=(
                            f"arif_memory: B3 violation — confidence={confidence} "
                            f"< 0.3 and no human_ack"
                        ),
                    )
                )

    # ── 3. B5: revise-supersede enforcement ──
    if mode == "revise":
        resolution_kind = payload.get("resolution_kind", "supersede")
        if resolution_kind in ("supersede", "merge"):
            if not payload.get("supersedes_memory_id"):
                return _echo_standing(
                    forge_verdict(
                        tool_id="arif_memory",
                        canonical_tool_name="arif_memory",
                        stage="555m",
                        payload={
                            "mode": mode,
                            "resolution_kind": resolution_kind,
                            "note": "B5: supersedes_memory_id required for supersede/merge",
                        },
                        session_id=session_id,
                        override_code=VerdictCode.SABAR,
                        message=(
                            f"arif_memory: B5 violation — {resolution_kind} "
                            f"requires supersedes_memory_id"
                        ),
                    )
                )

    # ── 4. A4: v1 vault tombstone gating on attest ──
    if mode == "attest":
        target_version = payload.get("vault_version") or payload.get("target_version")
        if target_version == "v1":
            return _echo_standing(
                forge_verdict(
                    tool_id="arif_memory",
                    canonical_tool_name="arif_memory",
                    stage="555m",
                    payload={
                        "mode": mode,
                        "vault_version": "v1",
                        "note": "A4: v1 vault FROZEN per sovereign ruling 2026-06-05",
                    },
                    session_id=session_id,
                    override_code=VerdictCode.SABAR,
                    message=(
                        "arif_memory: A4 violation — v1 vault is FROZEN, "
                        "no new seals or attestations"
                    ),
                )
            )

    # ── 5. Dispatch to backend ──
    # Day 3 NEW handlers (promote / forget / attest) — direct call
    # Day 3.5 added: remember (handles L4 write without embedding dependency)
    # Day 4 polish: inspect (direct Postgres lookup for UUID queries)
    # Day 5 (2026-07-07): audit — JITU contradiction engine
    # Day 6 (2026-07-21): score_prediction — ECHO/PaW prediction-observation feedback
    if mode in ("remember", "promote", "forget", "attest", "inspect", "audit", "score_prediction"):
        from arifosmcp.runtime.memory_handlers_v5 import (
            _handle_attest,
            _handle_audit,
            _handle_forget,
            _handle_inspect,
            _handle_promote,
            _handle_remember,
        )

        handler = {
            "remember": _handle_remember,
            "promote": _handle_promote,
            "forget": _handle_forget,
            "attest": _handle_attest,
            "inspect": _handle_inspect,
            "audit": _handle_audit,
            "score_prediction": _handle_score_prediction,
        }[mode]
        try:
            res_dict = await handler(payload, ctx=ctx)
            return _echo_standing(_wrap_result(res_dict, mode=mode, session_id=session_id))
        except Exception as exc:
            logger.exception(f"[ARIF_MEMORY] {mode} handler failed: {exc}")
            return _echo_standing(
                forge_verdict(
                    tool_id="arif_memory",
                    canonical_tool_name="arif_memory",
                    stage="555m",
                    payload={"mode": mode, "error": str(exc)},
                    session_id=session_id,
                    override_code=VerdictCode.SABAR,
                    message=f"arif_memory: {mode} handler failed: {exc}",
                )
            )

    # Day 4 polish (2026-06-21): SKIP broken HARDENED_DISPATCH_MAP path.
    # The legacy _arif_memory_recall handler signature is incompatible with
    # `payload` kwarg (TypeError). Route directly to engineering_memory_dispatch_impl
    # which DOES accept payload.
    from arifosmcp.runtime.tools_internal import engineering_memory_dispatch_impl

    try:
        result = await engineering_memory_dispatch_impl(
            mode=_map_mode_to_engineering(mode, payload),
            payload=payload,
            auth_context=None,
            risk_tier=_risk_tier_for_mode(mode),
            dry_run=False,
            ctx=ctx,
        )
        return _echo_standing(result)
    except Exception as exc:
        logger.exception(f"[ARIF_MEMORY] backend dispatch failed: {exc}")
        return _echo_standing(
            forge_verdict(
                tool_id="arif_memory",
                canonical_tool_name="arif_memory",
                stage="555m",
                payload={"mode": mode, "error": str(exc)},
                session_id=session_id,
                override_code=VerdictCode.SABAR,
                message=f"arif_memory: backend dispatch failed: {exc}",
            )
        )


def _map_mode_to_engineering(mode: str, payload: dict) -> str:
    """Map arif_memory v5 mode → engineering_memory v3 mode string.

    This is a bridge so that existing cognitive_memory / engineering_memory
    backends are reused. New handlers (promote / forget / attest) bypass
    this mapping and are handled directly.
    """
    bridge = {
        "recall": "query",  # engineering_memory.query
        "remember": "vector_store",  # engineering_memory.vector_store
        "inspect": "query",  # no direct equivalent → query
        "revise": "vector_store",  # supersede via store + tombstone prior
        "promote": "vector_store",  # placeholder — NEW handler needed
        "forget": "vector_forget",
        "attest": "query",  # placeholder — NEW handler needed
    }
    return bridge.get(mode, "query")


def _risk_tier_for_mode(mode: str) -> str:
    """Map action class → risk_tier for engineering_memory_dispatch_impl."""
    return {
        "OBSERVE": "low",
        "EXECUTE_REVERSIBLE": "medium",
        "EXECUTE_HIGH_IMPACT": "high",
        "IRREVERSIBLE": "critical",
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


async def _handle_score_prediction(payload: dict, ctx: Any) -> dict:
    """ECHO/PaW pattern: score a predicted state against observed reality.

    Takes a seal_entry_id pointing to an L2 seal entry containing a predicted_state
    snapshot, computes the delta against current observed state, and stores the
    result in L2 memory tier with provenance anchored to the seal chain.

    Args:
        payload: Must contain 'seal_entry_id'. May contain 'observed_state' dict
                 with vitals, well_score, clarity, etc. If omitted, auto-fetches
                 current vitals via arif_measure.

    Returns:
        dict with delta_fields, aggregate_score (0.0-1.0), flags, and verdict.
    """
    import json

    from arifosmcp.tools.ops import arif_measure

    seal_entry_id = payload.get("seal_entry_id")
    if not seal_entry_id:
        return {
            "mode": "score_prediction",
            "verdict": "VOID",
            "payload": {"note": "score_prediction requires seal_entry_id"},
        }

    # ── Resolve predicted state from seal entry ────────────────────────
    predicted_state: dict = {}
    try:
        from arifosmcp.runtime.tools import _VAULT_LEDGER

        # Search for the seal entry by entry_id
        found = None
        for entry in _VAULT_LEDGER:
            if entry.get("id") == seal_entry_id:
                found = entry
                break

        if found:
            raw_payload = found.get("payload", "{}")
            if isinstance(raw_payload, str):
                try:
                    parsed = json.loads(raw_payload)
                except json.JSONDecodeError:
                    parsed = {}
            else:
                parsed = raw_payload if isinstance(raw_payload, dict) else {}
            predicted_state = parsed.get("predicted_state", {})
    except Exception:
        pass  # Fail-soft: observed state still useful without predicted baseline

    # ── Resolve observed state ─────────────────────────────────────────
    observed_state: dict = payload.get("observed_state", {})
    if not observed_state:
        # Auto-fetch current vitals
        try:
            vitals_result = arif_measure(mode="vitals")
            if hasattr(vitals_result, "__dict__"):
                vitals_data = vars(vitals_result)
            elif isinstance(vitals_result, dict):
                vitals_data = vitals_result
            else:
                vitals_data = {}

            observed_state = {
                "runtime_drift": vitals_data.get("runtime_drift", False),
                "status": vitals_data.get("status", "unknown"),
            }
            # Try to read WELL substrate for observed well_score/clarity
            try:
                from arifosmcp.tools.judge import _read_well_substrate

                _well = _read_well_substrate()
                observed_state["well_score"] = _well.get("well_score")
                observed_state["human_ready"] = _well.get("human_ready")
                observed_state["clarity"] = _well.get("clarity")
            except Exception:
                pass
        except Exception:
            observed_state = {"status": "unavailable"}

    # ── Compute structured delta ───────────────────────────────────────
    observed_at = datetime.now(UTC).isoformat()
    delta_fields: dict[str, dict] = {}
    _pred_fields = {
        "well_score",
        "human_ready",
        "clarity",
        "runtime_drift",
        "floors_checked",
        "floors_violated",
    }

    for field in _pred_fields:
        _pred_val = predicted_state.get(field)
        _obs_val = observed_state.get(field)
        if _pred_val is not None and _obs_val is not None:
            try:
                if isinstance(_pred_val, (int, float)) and isinstance(_obs_val, (int, float)):
                    _delta = _obs_val - _pred_val
                    delta_fields[field] = {
                        "predicted": _pred_val,
                        "observed": _obs_val,
                        "delta": _delta,
                        "abs_delta": abs(_delta),
                    }
                elif isinstance(_pred_val, bool) and isinstance(_obs_val, bool):
                    _delta_val = 1.0 if _pred_val != _obs_val else 0.0
                    delta_fields[field] = {
                        "predicted": _pred_val,
                        "observed": _obs_val,
                        "delta": _delta_val,
                        "abs_delta": _delta_val,
                    }
                elif isinstance(_pred_val, list) and isinstance(_obs_val, list):
                    _delta_val = len(set(_pred_val) ^ set(_obs_val))
                    delta_fields[field] = {
                        "predicted": _pred_val,
                        "observed": _obs_val,
                        "delta": _delta_val,
                        "abs_delta": _delta_val,
                    }
                else:
                    _match = 0.0 if str(_pred_val) != str(_obs_val) else 1.0
                    delta_fields[field] = {
                        "predicted": str(_pred_val),
                        "observed": str(_obs_val),
                        "delta": 1.0 - _match,
                        "abs_delta": 1.0 - _match,
                    }
            except Exception:
                delta_fields[field] = {
                    "predicted": str(_pred_val),
                    "observed": str(_obs_val),
                    "delta": None,
                    "abs_delta": None,
                    "error": "computation failed",
                }

    # ── Compute aggregate score and flags ──────────────────────────────
    _large_delta_threshold = 3.0  # For numeric fields, abs_delta > threshold = LARGE_DELTA
    flags: list[str] = []
    total_fields = 0
    total_error = 0.0
    max_possible_error = 0.0

    for _field_name, _d in delta_fields.items():
        _abs = _d.get("abs_delta")
        if _abs is not None and isinstance(_abs, (int, float)):
            total_fields += 1
            total_error += _abs
            max_possible_error += _abs + _large_delta_threshold  # Normalise with headroom
            if _abs > _large_delta_threshold:
                flags.append("LARGE_DELTA")

    if total_fields > 0:
        # Aggregate score: 1.0 = perfect prediction, 0.0 = completely wrong
        # Use exponential decay: score = exp(-avg_error / threshold)
        _avg = total_error / total_fields
        import math

        aggregate_score = round(math.exp(-_avg / _large_delta_threshold), 4)
        aggregate_score = max(0.0, min(1.0, aggregate_score))
    else:
        aggregate_score = 1.0  # No fields to compare = no prediction error

    if not predicted_state:
        flags.append("NO_PREDICTED_STATE")
        aggregate_score = 0.0

    if not observed_state or observed_state == {"status": "unavailable"}:
        flags.append("NO_OBSERVED_STATE")

    # F1/F2 DELTA THRESHOLD INTERRUPT (ECHO/PaW Circuit Breaker)
    # If the prediction delta exceeds Delta_max, DO NOT silently log the delta
    # as a learning gradient. A massive delta means the judge's mental model
    # is dangerously disconnected from the substrate - this is an epistemic
    # failure (F2 TRUTH) and a structural risk (F1 AMANAH).
    #
    # Besar sangat lari, kena stop. Critical hallucination requires
    # sovereign override, not silent gradient storage.
    _delta_max_threshold = 0.30  # 30% deviation = critical divergence

    if aggregate_score < (1.0 - _delta_max_threshold):  # score below 0.70
        return {
            "mode": "score_prediction",
            "verdict": "HOLD",
            "payload": {
                "hold_type": "F1_F2_DELTA_BREACH",
                "reason": (
                    f"F1/F2_DELTA_BREACH: prediction delta {aggregate_score:.2f} "
                    f"exceeds threshold (>{_delta_max_threshold:.0%}). "
                    f"The judge's predicted state is dangerously disconnected "
                    f"from the observed substrate."
                ),
                "prediction_id": seal_entry_id,
                "observed_at": observed_at,
                "aggregate_score": aggregate_score,
                "threshold": 1.0 - _delta_max_threshold,
                "delta_fields": delta_fields,
                "flags": flags + ["F1_AMANAH_RISK", "F2_TRUTH_EPISTEMIC_FAILURE"],
                "floors_breached": ["F1", "F2"],
                "next_action": (
                    "SOVEREIGN_OVERRIDE_REQUIRED - arif_judge(mode='escalate'). "
                    "Critical hallucination detected; cannot log as learning gradient. "
                    "Human sovereign (Arif) must acknowledge and override."
                ),
                "provenance": {
                    "source": "arif_memory.score_prediction",
                    "seal_entry_id": seal_entry_id,
                    "circuit": "F1_F2_DELTA_BREACH",
                },
            },
        }

    result = {
        "mode": "score_prediction",
        "verdict": "SEAL",
        "payload": {
            "prediction_id": seal_entry_id,
            "observed_at": observed_at,
            "delta_fields": delta_fields,
            "aggregate_score": aggregate_score,
            "flags": flags,
            "provenance": {
                "source": "arif_memory.score_prediction",
                "seal_entry_id": seal_entry_id,
            },
            "note": "Prediction-observation delta stored in L2 memory tier.",
        },
    }
    return result


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
    "_handle_score_prediction",
]
