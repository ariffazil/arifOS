"""
arifOS Verbosity Control — Goal 4, Priority 1.

DITEMPA BUKAN DIBERI

Forged 2026-07-16 under Fable-5 audit directive. Goal 4 of the acceptance
spec:

  arif_init verbosity: minimal | standard | full
  - minimal <= 500 tokens
  - minimal contains: verdict, session_id, actor (unified),
                       call_hash, next_safe_action
  - full byte-identical to today

Anti-gaming clause: what gets cut is metadata, never evidence. If
`minimal` drops call_hash or the authority block, F11 is breached — HOLD.

Levels:
  - "minimal"  : verdict + session_id + actor (unified) + call_hash +
                 next_safe_action + status. Strips atlas333 boot,
                 work_contract, full SCT, clarity_metrics,
                 constitution block, session_birth.
  - "standard" : current default behavior (preserved).
  - "full"     : current default + atlas333 boot + session_birth
                 (kept from session start anyway). Identical to
                 "standard" today.

Reversible: delete the wire-in in `_wrap_handler` and this file.
"""

from __future__ import annotations

from typing import Any

# Fields KEPT in minimal mode (required by audit spec + F11 audit + F2 truth).
_MINIMAL_KEEP_TOP_LEVEL = {
    "status",
    "tool",
    "verdict",
    "actor_verified",
    "actor_id",
    "session_id",
    "call_hash",
    "trace_id",
    "signature",
    "_identity_consistency_applied",
    "_identity_drift_count",
}

_MINIMAL_KEEP_RESULT = {
    "actor_verified",
    "session_id",
    "actor_id",
    "next_safe_action",
    "kernel_epoch",
    "public_surface_version",
    "tool_registry_version",
    "verdict",
    "actor_bound",
    "authority",
    "mode",
    "init_mode",
    "session_mode",
    "authority_scope",
}

# Fields STRIPPED in minimal mode (metadata, not evidence).
_MINIMAL_STRIP_TOP_LEVEL = {
    "session",  # nested session_birth + SCT
    "actor",  # full actor block — re-collapsed into unified actor
    "constitution",  # constitution detail_ref by hash — loadable
    "embodiment",
    "causality_warning",
    "execution_law",
    "attention_surface",
    "tool_surface",
    "risk_leash",
    "warnings",
    "operator_identity",
    "intent_model",
    "belief_state",
    "preference_memory",
    "false_belief_flags",
    "well_mirror_enhanced",
    "session_continuity",
    "consent_boundaries",
    "context_completeness",
    "output_contract",
    "result",  # we keep selected fields from result below
    "meta",  # we keep selected fields from meta below
    "authority_state",  # rebuilt under unified actor below
    "doctrine",
    "nine_signal",  # stripped — verdict already conveys pass/fail
    "_affordance",  # metadata
    "_meta",  # shim metadata
    "_canonical",  # shim metadata
    "_identity_drift_violations",  # violation list — empty on clean path
    "_identity_drift_narrowed_from",  # only present on drift
    "_identity_drift_count",
    "_identity_drift_first",
    "_identity_drift_tool",
    "verdict_code",  # in result
    "witness",  # in result
    "degraded",
    "call_hash",
    "stage_progression",
    # NOTE (F2 TRUTH audit 2026-07-27): the following semantic fields used to be
    # in the strip list, which silently discarded the kernel's actual output
    # payload (facts, inferences, confidence, etc.) when verbosity=minimal.
    # They are now PRESERVED in minimal mode. See _SEMANTIC_PRESERVED_FIELDS
    # in trim_for_verbosity(). Stripping here would be a regression.
    # "facts",
    # "inferences",
    # "recommendations",
    # "unknowns",
    # "do_not_conclude",
    # "confidence",
    # "metacognition",
    # "constitutional_check",
    # "next_safe_action",
    # "risk",
    "_nine_signal_compliant",
    "_violations",
    "live_kernel_envelope",
    "authority_band",
    "reversibility",
    "route_owner",
    "proposed_action",
    "expected_receipt",
    "stop_condition",
    "clarity_metrics",
    "clarity_contract",
    "apex_scalars",
    "standing_source",
    "sct_claims",
    "work_contract",
    "session_token",
    "session_birth",
}


def trim_for_verbosity(response: Any, verbosity: str | None) -> Any:
    """Apply minimal/standard/full trim to a tool response dict.

    Preserves:
      - minimal: verdict, session_id, actor_id, actor_verified, call_hash,
                 trace_id, next_safe_action, status. Strips atlas333 boot,
                 work_contract, full SCT, clarity_metrics, constitution,
                 session_birth (F11 audit fields KEPT).
      - standard: current behavior (default).
      - full: current behavior — same as standard today.

    Anti-gaming: F11 audit fields (call_hash, trace_id, signature,
    actor_verified) are NEVER stripped. If the audit's required fields
    are missing post-trim, the trimmer FAILS CLOSED — it returns the
    untrimmed response rather than violate F11.
    """
    if not isinstance(response, dict):
        return response
    if verbosity is None or verbosity == "standard":
        return response  # default behavior unchanged
    if verbosity == "full":
        return response  # byte-identical to today

    if verbosity != "minimal":
        # Unknown verbosity value — fail closed, return standard
        return response

    # Helper: field lookup that searches top-level, then result, then meta.
    # Many kernel responses put call_hash / trace_id inside result or meta,
    # not at the top level.
    def _lookup(*keys: str) -> Any:
        for k in keys:
            v = response.get(k)
            if v:
                return v
        for nested_key in ("result", "meta"):
            nested = response.get(nested_key)
            if isinstance(nested, dict):
                for k in keys:
                    v = nested.get(k)
                    if v:
                        return v
        return None

    actor_id = _lookup("actor_id") or "anonymous"
    actor_verified = bool(_lookup("actor_verified"))
    # F13 SOVEREIGN 2026-08-01: if the top-level actor_verified is False
    # but the session_token (the canonical cryptographic proof of binding)
    # has av=True, trust the JWT. The kernel's standing projection can
    # collapse the in-memory session state after the JWT is minted; the
    # JWT is immutable and authoritative. Same for the auth band.
    _stok = _lookup("session_token")
    _jwt_av = None
    _jwt_auth = None
    if _stok and isinstance(_stok, str) and _stok.startswith("sct_v1."):
        try:
            import base64 as _b64
            import json as _json

            _payload_b64 = _stok.split(".", 2)[1]
            _payload_b64 += "=" * (4 - len(_payload_b64) % 4)
            _claims = _json.loads(_b64.urlsafe_b64decode(_payload_b64))
            _jwt_av = _claims.get("av")
            _jwt_auth = _claims.get("auth")
        except Exception:
            pass
    if not actor_verified and _jwt_av is True:
        actor_verified = True
    session_id = _lookup("session_id")
    call_hash = _lookup("call_hash")
    trace_id = _lookup("trace_id")
    signature = _lookup("signature")
    verdict = _lookup("verdict") or response.get("status", "SEAL")

    # Unified actor block
    authority_level = "OBSERVER"
    nested_actor = response.get("actor")
    if isinstance(nested_actor, dict):
        authority_level = nested_actor.get("authority_level", "OBSERVER")
    # F13 SOVEREIGN 2026-08-01 / audit 2026-08-04: prefer JWT auth band.
    # Include SOVEREIGN — omitting it left authority_level stuck at OBSERVER
    # while SCT carried auth:SOVEREIGN (authority fork / Mode 3).
    if _jwt_auth and _jwt_auth in (
        "OBSERVE_ONLY",
        "LIMITED_MUTATE",
        "FULL",
        "SOVEREIGN",
        "OPERATOR",
    ):
        authority_level = _jwt_auth

    unified_actor = {
        "actor_id": actor_id,
        "actor_verified": actor_verified,
        "authority_level": authority_level,
    }

    minimal = {
        "status": response.get("status", "OK"),
        "tool": response.get("tool"),
        "verdict": verdict,
        "actor": unified_actor,
        "session_id": session_id,
        "call_hash": call_hash,
        "trace_id": trace_id,
        "signature": signature,
        "session_token": _lookup("session_token"),
        "audit_provenance": {
            "call_hash": call_hash,
            "trace_id": trace_id,
            "signature": signature,
            "kernel_signature_anchor": "constitutional_init_v1",
        },
    }

    # Pull next_safe_action from anywhere it's set
    nsa = _lookup("next_safe_action")
    if nsa:
        minimal["next_safe_action"] = nsa

    # F2 TRUTH: PRESERVE semantic content in minimal mode.
    # Audit 2026-07-27 found that arif_observe / arif_think / arif_route returned
    # only the control-plane envelope (status, call_hash, trace_id, etc.) without
    # the actual facts/inferences/confidence — because _MINIMAL_STRIP_FIELDS was
    # dropping them, AND the minimal dict was constructed from scratch without
    # including them. Metabolic utility was 41/100.
    #
    # The whole point of `minimal` is to drop *verbose* metadata (atlas333 boot,
    # work_contract, full SCT, etc.), NOT the semantic payload itself.
    _SEMANTIC_PRESERVED_FIELDS = (
        "facts",
        "inferences",
        "recommendations",
        "unknowns",
        "do_not_conclude",
        "confidence",
        "metacognition",
        "constitutional_check",
        "risk",
        # 2026-08-02: External audit (Claude Opus) — minimal verbosity
        # must not silently drop constitutional verdict fields.
        # A lazy client reading minimal sees no DENY without these.
        "substrate",
        "substrate_gate",
        "effective_verdict",
        "canonical_verdict",
        "receipt_state",
        "floor_passed",
        # 2026-08-04 audit: metabolic payload MUST survive minimal trim.
        # arif_observe returned status=OK + organs live via direct call, but
        # MCP minimal strip left only control-plane → agents saw pending/empty.
        "result",
        "organs",
        "organs_alive",
        "organs_total",
        "verdicts",
        "nine_signal",
        "reasons",
        "apex_scalars",
        "standing",
        "authority",
        "allowed_next_verbs",
        "runtime_grant",
        "session_birth",
        "mutation_allowed",
        "seal_allowed",
        "affordance_contract",
    )
    for field in _SEMANTIC_PRESERVED_FIELDS:
        value = _lookup(field)
        if value is not None:
            minimal[field] = value

    # 2026-08-04 audit: do not emit status=pending for completed OBSERVE work.
    # pending + empty result is Mode 3 (narrate HOLD while tool already ran).
    _st = str(minimal.get("status") or "").lower()
    _tool = str(minimal.get("tool") or response.get("tool") or "")
    _cc = minimal.get("constitutional_check") or {}
    if _st == "pending" and _tool in (
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_init",
    ):
        # Prefer original response status when it was OK/completed
        _orig = str(response.get("status") or "").upper()
        if _orig in ("OK", "COMPLETED", "SEAL"):
            minimal["status"] = "completed" if _orig != "OK" else "OK"
            if str(minimal.get("verdict")).lower() == "pending":
                minimal["verdict"] = response.get("verdict") or "SEAL"
        elif _cc.get("floor_passed") and not _cc.get("hold_required"):
            minimal["status"] = "OK"
            if str(minimal.get("verdict")).lower() == "pending":
                minimal["verdict"] = "SEAL"

    # W-03: deployment drift is a hard floor — never re-green to SEAL/PROCEED.
    def _has_drift(d: dict) -> bool:
        if not isinstance(d, dict):
            return False
        sub = d.get("substrate") if isinstance(d.get("substrate"), dict) else {}
        if sub.get("state") == "DEGRADED" or sub.get("drift") is True:
            return True
        sw = d.get("software_release") if isinstance(d.get("software_release"), dict) else {}
        if sw.get("drift") is True:
            return True
        deg = d.get("degraded")
        if isinstance(deg, list) and any("drift" in str(x).lower() for x in deg):
            return True
        res = d.get("result") if isinstance(d.get("result"), dict) else {}
        rsub = res.get("substrate") if isinstance(res.get("substrate"), dict) else {}
        return rsub.get("state") == "DEGRADED" or rsub.get("drift") is True

    _drift = _has_drift(minimal) or _has_drift(response if isinstance(response, dict) else {})

    # Derive effective/canonical from constitutional_check — single resolver.
    # 2026-08-04 audit: floor_passed=true + hold_required=false must not
    # coexist with effective_verdict=HOLD / canonical=DENY (Mode 3).
    # 2026-08-04 W-03: drift must not be overpainted by floor_passed=true.
    if _drift:
        minimal["effective_verdict"] = "HOLD"
        minimal["canonical_verdict"] = "HOLD"
        minimal["reason_code"] = minimal.get("reason_code") or "DEPLOYMENT_DRIFT"
        minimal["next_action"] = minimal.get("next_action") or "RECONCILE_SOURCE_BUILT_DEPLOYED"
        if str(minimal.get("status", "")).lower() in ("ok", "completed", "healthy"):
            minimal["status"] = "degraded"
        # Keep nine_signal honest if present
        ns = minimal.get("nine_signal")
        if isinstance(ns, dict):
            overall = ns.get("overall")
            if isinstance(overall, dict) and overall.get("state") in ("SELAMAT", "SAFE"):
                ns["overall"] = {
                    "state": "RETAK",
                    "en": "HOLDING",
                    "reason": "deployment_drift",
                }
        # Mutation never true under drift
        if "mutation_allowed" in minimal:
            minimal["mutation_allowed"] = False
        sb = minimal.get("session_birth")
        if isinstance(sb, dict):
            sb["mutation_allowed"] = False
        st = minimal.get("standing")
        if isinstance(st, dict) and isinstance(st.get("authority"), dict):
            st["authority"]["mutation_allowed"] = False
            st["authority"]["seal_allowed"] = False
        minimal["_drift_floor_applied"] = True
    elif isinstance(_cc, dict) and _cc.get("floor_passed") and not _cc.get("hold_required"):
        _v = str(minimal.get("verdict") or response.get("verdict") or "").upper()
        if _v in ("SEAL", "OK", "COMPLETED", "SYUBHAH", "SABAR", ""):
            # SYUBHAH is epistemic doubt on content, not session DENY
            minimal["effective_verdict"] = (
                "SEAL" if _v in ("SEAL", "OK", "COMPLETED", "") else _v
            )
            minimal["canonical_verdict"] = "PROCEED"
    elif isinstance(_cc, dict) and _cc.get("hold_required"):
        if minimal.get("effective_verdict") is None:
            minimal["effective_verdict"] = "HOLD"
            minimal["canonical_verdict"] = "DENY"

    # F11 SAFETY NET: verify required fields are present
    required = ["verdict", "session_id", "actor", "call_hash"]
    if not all(minimal.get(k) for k in required):
        # F11 BREACH PREVENTION — fail closed
        return response  # return untrimmed

    return minimal


__all__ = ["trim_for_verbosity"]
