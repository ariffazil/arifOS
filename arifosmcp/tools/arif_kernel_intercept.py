"""
arif_kernel_intercept — The Minimum Constitutional Kernel
═════════════════════════════════════════════════════════

This module implements the "thin operational spine" mandated by the F13 Sovereign.
It strips away the cathedral of philosophy and provides a boring, ruthless
interception layer for agentic actions across the federation.

Input: KernelInput
Output: KernelOutput

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

from arifosmcp.schemas import KernelInput, KernelOutput, ReversibilityClass, TruthState

# Constitutional affordance plumbing (metacognitive wiring)
try:
    from arifosmcp.runtime.tools import build_standard_mcp_result, get_full_affordance
except Exception:

    def get_full_affordance(n):
        return {"tool_name": n, "agency_level": "UNKNOWN"}

    def build_standard_mcp_result(**kw):
        return kw


logger = logging.getLogger("arifos.kernel.intercept")


# F13 SOVEREIGN key registry — kernel-side, not config-side.
# Production: real Ed25519 verification via crypto_auth.verify_actor_signature().
# Dev-mode fallback: sentinel string comparison (when ARIFOS_ED25519_ENABLED != true).
_SOVEREIGN_KEY_SENTINEL = os.environ.get(
    "ARIFOS_SOVEREIGN_KEY",
    "DEV_ONLY_SENTINEL_REPLACE_AT_PROD_BOOT",
)
_SOVEREIGN_ED25519_ENABLED = os.environ.get("ARIFOS_ED25519_ENABLED", "true").lower() in (
    "true",
    "1",
    "yes",
)
try:
    from arifosmcp.runtime.crypto_auth import verify_actor_signature as _ed25519_verify

    _ED25519_AVAILABLE = True
except ImportError:
    _ED25519_AVAILABLE = False


# ── Action Class Policy (forged 2026-07-24) ──────────────────────────────
_ACTION_CLASS_POLICY = {
    "AUDIT_RECORD": {
        "seal_purpose": "RECORD",
        "authority_effect": "NONE",
        "reversibility": "R2",
        "ack_irreversible": False,
        "requires_f13": False,
        "can_retry_autonomously": True,
    },
    "EVIDENCE_ATTESTATION": {
        "seal_purpose": "RECORD",
        "authority_effect": "NONE",
        "reversibility": "R2",
        "ack_irreversible": False,
        "requires_f13": False,
        "can_retry_autonomously": True,
    },
    "VAULT_RECEIPT": {
        "seal_purpose": "RECORD",
        "authority_effect": "NONE",
        "reversibility": "R2",
        "ack_irreversible": False,
        "requires_f13": False,
        "can_retry_autonomously": True,
    },
    "ACTION_AUTHORIZATION": {
        "seal_purpose": "AUTHORIZE",
        "authority_effect": "EXECUTION_GRANT",
        "reversibility": "R4",
        "ack_irreversible": True,
        "requires_f13": True,
        "can_retry_autonomously": False,
    },
    "CONSTITUTIONAL_AMENDMENT": {
        "seal_purpose": "AUTHORIZE",
        "authority_effect": "SOVEREIGN_CHANGE",
        "reversibility": "R5",
        "ack_irreversible": True,
        "requires_f13": True,
        "can_retry_autonomously": False,
    },
}


def _resolve_action_class(
    action_class: str | None,
    reversibility_level: str,
    seal_purpose: str | None,
    authority_effect: str | None,
) -> dict:
    if action_class and action_class.upper() in _ACTION_CLASS_POLICY:
        return _ACTION_CLASS_POLICY[action_class.upper()]
    if seal_purpose == "AUTHORIZE" or (authority_effect and authority_effect != "NONE"):
        return _ACTION_CLASS_POLICY["ACTION_AUTHORIZATION"]
    r = reversibility_level.upper()
    if r in ("R4", "R5", "R4_IRREVERSIBLE", "R5_SOVEREIGN", "IRREVERSIBLE", "SOVEREIGN"):
        return _ACTION_CLASS_POLICY["ACTION_AUTHORIZATION"]
    return _ACTION_CLASS_POLICY["AUDIT_RECORD"]


def _verify_sovereign_token(
    token: str | None,
    actor_id: str | None = None,
    nonce: str | None = None,
    actor_signature: str | None = None,
    session_id: str | None = None,
    intent: str | None = None,
) -> bool:
    """F13 SOVEREIGN: Real Ed25519 verification (production) or sentinel fallback (dev).

    Production path (ARIFOS_ED25519_ENABLED=true):
      - Verifies actor_signature against registered Ed25519 public key
      - Uses crypto_auth.verify_actor_signature() over {actor_id}:{nonce} payload
      - Nonce is single-use, challenge-based with 120s TTL

    Dev-mode fallback:
      - Token must equal the sentinel string (constant-time comparison)
      - Trivially bypassable — DO NOT use in production
    """
    # Real Ed25519 path (production)
    import sys as _dbg3

    if _SOVEREIGN_ED25519_ENABLED and _ED25519_AVAILABLE and actor_signature and nonce and actor_id:
        # 1. Try new authorization challenge verification (Redis-backed)
        _vfy_candidate = (
            intent.split("sha256:")[-1].split()[0].strip() if intent and "sha256:" in intent else ""
        )
        print(
            f"F13_VERIFY: attempting auth_verify actor={actor_id} nonce={nonce[:16] if nonce else 'NONE'}... sig={bool(actor_signature)} candidate={_vfy_candidate}",
            file=_dbg3.stderr,
            flush=True,
        )
        try:
            from arifosmcp.runtime.crypto_auth import verify_authorization_challenge as _auth_verify

            _auth_ok, _auth_code, _auth_result = _auth_verify(
                actor=actor_id,
                nonce=nonce,
                signature_b64=actor_signature,
            )
            if _auth_ok:
                logger.info("F13: authorization challenge PASS — nonce consumed, one-time auth")
                return True
            print(
                f"F13_VERIFY: auth_verify result: ok={_auth_ok} code={_auth_code}",
                file=_dbg3.stderr,
                flush=True,
            )
            if _auth_code not in ("CHALLENGE_UNKNOWN", "SIGNATURE_MISSING"):
                logger.warning("F13: authorization challenge FAIL — %s", _auth_code)
                return False
        except Exception as e:
            logger.debug("F13: auth_verify exception (falling through): %s", e)

        # 2. Legacy challenge-based verification (in-memory, for arif_init flow)
        try:
            ok = _ed25519_verify(
                actor_id=actor_id,
                nonce=nonce,
                signature_b64=actor_signature,
            )
            if ok:
                return True
        except Exception as e:
            logger.warning("F13: challenge exception=%s", e)

        # 3. Free-nonce fallback (dev only, explicit opt-in)
        _free_nonce = os.environ.get("ARIFOS_FREE_NONCE_ALLOWED", "false").lower() in ("true", "1")
        if _free_nonce:
            try:
                from arifosmcp.runtime.crypto_auth import resolve_actor_public_key
                from cryptography.exceptions import InvalidSignature

                pubkey = resolve_actor_public_key(actor_id)
                if pubkey is not None:
                    sig_bytes = _b64.b64decode(actor_signature)
                    payload = f"{actor_id}:{nonce}".encode()
                    pubkey.verify(sig_bytes, payload)
                    logger.warning("F13: free-nonce PASS — NO REPLAY PROTECTION")
                    return True
            except InvalidSignature:
                logger.warning("F13: free-nonce FAIL — invalid signature")
            except Exception as e:
                logger.warning("F13: free-nonce exception=%s", e)
    else:
        logger.info(
            "F13_ED25519: skipped — enabled=%s available=%s has_sig=%s has_nonce=%s has_actor=%s",
            _SOVEREIGN_ED25519_ENABLED,
            _ED25519_AVAILABLE,
            bool(actor_signature),
            bool(nonce),
            bool(actor_id),
        )

    # Sentinel fallback (dev-mode)
    if not token:
        return False
    if not isinstance(token, str) or len(token) != len(_SOVEREIGN_KEY_SENTINEL):
        return False
    result = 0
    for a, b in zip(token, _SOVEREIGN_KEY_SENTINEL, strict=True):
        result |= ord(a) ^ ord(b)
    return result == 0


def compute_audit_hash(payload: KernelInput) -> str:
    canonical_dict = {
        "actor": payload.actor,
        "intent": payload.intent,
        "capability": payload.requested_capability,
        "r_class": payload.reversibility_level.value,
        "blast": payload.blast_radius,
        "ts": datetime.now(UTC).isoformat(),
    }
    return hashlib.sha256(json.dumps(canonical_dict, sort_keys=True).encode()).hexdigest()[:16]


async def _arif_kernel_intercept(
    actor: str,
    intent: str,
    requested_capability: str,
    domain: str,
    reversibility_level: str,
    blast_radius: str,
    epistemic_state: str = "UNKNOWN",
    evidence: list[dict[str, Any]] | None = None,
    authority_token: str | None = None,
    measurement: dict[str, Any] | None = None,
    action_class: str | None = None,
    seal_purpose: str | None = None,
    authority_effect: str | None = None,
    actor_signature: str | None = None,
    signature_challenge: dict[str, Any] | None = None,
    nonce: str | None = None,
    key_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    evidence = evidence or []

    _rev_raw = (reversibility_level or "").strip().upper()
    _REV_ALIASES = {
        "R0": "R0",
        "R0_OBSERVATION": "R0",
        "OBSERVATION": "R0",
        "OBSERVE": "R0",
        "READ": "R0",
        "R1": "R1",
        "R1_SIMULATION": "R1",
        "SIMULATION": "R1",
        "DRY_RUN": "R1",
        "R2": "R2",
        "R2_REVERSIBLE_WRITE": "R2",
        "REVERSIBLE": "R2",
        "REVERSIBLE_WRITE": "R2",
        "WRITE": "R2",
        "RECORD_ONLY_APPEND": "R2",
        "AI_ATTESTATION": "R2",
        "AUDIT_RECEIPT": "R2",
        "AUDIT_RECORD": "R2",
        "EVIDENCE_ATTESTATION": "R2",
        "RECORD_SEAL": "R2",
        "EVIDENCE_SEAL": "R2",
        "R3": "R3",
        "R3_COSTLY_REVERSIBLE": "R3",
        "COSTLY": "R3",
        "SEMI_IRREVERSIBLE": "R3",
        "R4": "R4",
        "R4_IRREVERSIBLE": "R4",
        "IRREVERSIBLE": "R4",
        "R5": "R5",
        "R5_SOVEREIGN": "R5",
        "SOVEREIGN": "R5",
        "CATASTROPHIC": "R5",
    }
    try:
        r_class = ReversibilityClass(_REV_ALIASES.get(_rev_raw, _rev_raw))
    except ValueError:
        unknown_output = KernelOutput(
            decision="CLASSIFICATION_HOLD",
            constitutional_floor_triggered="F2",
            reason=(
                f"Unknown reversibility class: '{_rev_raw}'. "
                "The kernel cannot classify this action. "
                "Valid classes: R0-R5, RECORD_ONLY_APPEND, AUDIT_RECEIPT, etc."
            ),
            audit_hash=None,
            rollback_instruction=None,
        )
        base = unknown_output.model_dump()
        base["seal_type"] = "UNKNOWN"
        base["seal_purpose"] = "UNKNOWN"
        base["authority_effect"] = "NONE"
        base["requires_human_signature"] = False
        base["authorized_execution"] = False
        base["next_safe_action"] = (
            "Re-submit with a recognized reversibility_class. "
            "For evidence/audit recording use AUDIT_RECORD (R2). "
            "For irreversible actions use ACTION_AUTHORIZATION (R4)."
        )
        base["metacognition"] = {
            "confidence": 0.99,
            "why_this_tool": "Kernel cannot classify unknown reversibility",
            "next_safe_action": base["next_safe_action"],
        }
        return base

    try:
        t_state = TruthState(epistemic_state.upper())
    except ValueError:
        t_state = TruthState.UNKNOWN

    kernel_input = KernelInput(
        actor=actor,
        intent=intent,
        requested_capability=requested_capability,
        domain=domain,
        evidence=evidence,
        authority_token=authority_token,
        reversibility_level=r_class,
        blast_radius=blast_radius,
        epistemic_state=t_state,
        measurement=measurement,
    )

    _m = measurement or {}
    _G = _m.get("G")
    _C_dark = _m.get("C_dark")
    _W3 = _m.get("W3")
    _has_measurement = _G is not None and _C_dark is not None

    # P0 FIX (2026-07-25): Deterministic AUDIT_RECORD normalization.
    _effective_ac = action_class.upper() if action_class else None
    if _effective_ac == "AUDIT_RECORD":
        _rev_raw = "R2"
        blast_radius = blast_radius or "ledger"
        seal_purpose = "RECORD"
        authority_effect = authority_effect or "NONE"
    _policy = _resolve_action_class(
        action_class=action_class,
        reversibility_level=_rev_raw,
        seal_purpose=seal_purpose,
        authority_effect=authority_effect,
    )
    _requires_f13 = _policy["requires_f13"]
    _seal_purpose_resolved = seal_purpose or _policy["seal_purpose"]
    _authority_effect_resolved = authority_effect or _policy["authority_effect"]
    _seal_type = "SEAL_RECORD" if _seal_purpose_resolved == "RECORD" else "SEAL_AUTHORIZATION"
    _ack_irreversible = _policy["ack_irreversible"]
    import sys as _dbg2

    print(
        f"F13_POLICY: action_class={action_class} requires_f13={_requires_f13} seal_purpose={_seal_purpose_resolved} reversibility={_rev_raw}",
        file=_dbg2.stderr,
        flush=True,
    )

    # 1. F13 Gate — real Ed25519 or sentinel fallback
    if _requires_f13:
        if not _verify_sovereign_token(
            token=authority_token,
            actor_id=actor,
            nonce=nonce,
            actor_signature=actor_signature,
            session_id=session_id,
            intent=intent,
        ):
            # ── Issue structured authorization challenge ──
            _candidate_hash = (
                intent.split("sha256:")[-1].split()[0].strip()
                if intent and "sha256:" in intent
                else ""
            )
            try:
                from arifosmcp.runtime.crypto_auth import issue_authorization_challenge as _iss_chal
                from arifosmcp.runtime.crypto_auth import build_approval_card as _build_card

                _challenge_ctx = _iss_chal(
                    actor=actor or "anonymous",
                    authorization_session_id=session_id or actor or "anonymous",
                    candidate_hash=_candidate_hash,
                    action_class=action_class or "ACTION_AUTHORIZATION",
                    reversibility=_rev_raw,
                    blast_radius=blast_radius or "MEDIUM",
                    seal_purpose=_seal_purpose_resolved,
                    authority_effect=_authority_effect_resolved,
                    audience="arifOS",
                    plan_id="",
                    target_environment=domain or "production",
                    human_summary=f"Action: {intent[:120]}. Class: {action_class or _rev_raw}. Blast: {blast_radius or 'unknown'}. System: {domain or requested_capability or 'unknown'}.",
                )
                _approval_card = _build_card(
                    action_summary=intent[:200],
                    reason=f"F13 SOVEREIGN: {action_class or _rev_raw} action requires cryptographic authorization",
                    affected_systems=[domain or "kernel"] if domain else [],
                    environment="production",
                    reversibility=_rev_raw,
                    blast_radius=blast_radius or "MEDIUM",
                    rollback_summary="Reversible via SOUL.md or VAULT999 backout",
                    requested_by=actor or "anonymous",
                    expires_at=_challenge_ctx.get("expires_at", ""),
                )
            except Exception as _chal_err:
                logger.warning("F13: challenge issuance failed: %s", _chal_err)
                _challenge_ctx = {}
                _approval_card = {}
            output = KernelOutput(
                decision="ESCALATE",
                constitutional_floor_triggered="F13",
                reason="F13 sovereign authorization required",
                audit_hash=compute_audit_hash(kernel_input),
                rollback_instruction=None,
            )
            base = output.model_dump()
            target_aff = get_full_affordance(requested_capability)
            base["affordance"] = target_aff
            base["seal_type"] = "SEAL_AUTHORIZATION"
            base["requires_human_signature"] = True
            base["authorized_execution"] = False
            base["seal_purpose"] = _seal_purpose_resolved
            base["authority_effect"] = _authority_effect_resolved
            base["f13_failure_code"] = "F13_REQUIRED"
            base["authorization_request"] = _challenge_ctx
            base.update(_approval_card)
            base["metacognition"] = {
                "confidence": 0.99,
                "next_safe_action": "Sign the canonical challenge with Ed25519 key and re-submit to arif_judge",
            }
            base["next_safe_action"] = "Sign authorization_request with Ed25519 then resubmit"
            base["constitutional_check"] = {"hold_required": True, "floor": "F13"}
            return base

    # 2. Evidence Thresholds for Truth (F2 TRUTH)
    if t_state in {TruthState.FACT, TruthState.ESTIMATE} and not evidence:
        output = KernelOutput(
            decision="DENY",
            constitutional_floor_triggered="F2",
            reason=(
                f"Objective truth state ({t_state.value}) claimed but no evidence "
                "provided. F2 TRUTH requires source attribution for P(truth) >= 0.99."
            ),
            audit_hash=compute_audit_hash(kernel_input),
            rollback_instruction=None,
        )
        base = output.model_dump()
        target_aff = get_full_affordance(requested_capability)
        base["affordance"] = target_aff
        base["next_safe_action"] = (
            "Gather cited evidence (arif_fetch or arif_observe) then re-submit to kernel_intercept"
        )
        base["metacognition"] = {"confidence": 0.95, "next_safe_action": base["next_safe_action"]}
        return base

    if t_state == TruthState.CONFLICT and not evidence:
        output = KernelOutput(
            decision="ESCALATE",
            constitutional_floor_triggered="F2",
            reason=(
                "CONFLICT epistemic state declared but no contradicting evidence "
                "attached. F2 TRUTH requires explicit evidence chain to surface "
                "disagreement."
            ),
            audit_hash=compute_audit_hash(kernel_input),
            rollback_instruction=None,
        )
        base = output.model_dump()
        target_aff = get_full_affordance(requested_capability)
        base["affordance"] = target_aff
        base["next_safe_action"] = "Resolve contradiction with explicit evidence then re-intercept"
        base["metacognition"] = {"confidence": 0.85, "next_safe_action": base["next_safe_action"]}
        return base

    if (
        t_state in {TruthState.HYPOTHESIS, TruthState.CLAIM}
        and not evidence
        and blast_radius in {"capital", "constitution", "external-recipient"}
    ):
        output = KernelOutput(
            decision="ESCALATE",
            constitutional_floor_triggered="F2",
            reason=(
                f"{t_state.value} state with high blast_radius ({blast_radius}) "
                "requires supporting evidence per F2 TRUTH."
            ),
            audit_hash=compute_audit_hash(kernel_input),
            rollback_instruction=None,
        )
        base = output.model_dump()
        target_aff = get_full_affordance(requested_capability)
        base["affordance"] = target_aff
        base["next_safe_action"] = (
            "Attach evidence or downgrade epistemic_state before re-intercept"
        )
        base["metacognition"] = {"confidence": 0.80, "next_safe_action": base["next_safe_action"]}
        return base

    if _has_measurement:
        if _C_dark >= 0.30:
            output = KernelOutput(
                decision="ESCALATE",
                constitutional_floor_triggered="F9",
                reason=(
                    f"F9 ANTI-HANTU: C_dark={_C_dark:.3f} >= 0.30 threshold. "
                    "Hallucination risk too high for autonomous action."
                ),
                audit_hash=compute_audit_hash(kernel_input),
                rollback_instruction=None,
            )
            base = output.model_dump()
            base["measurement_received"] = {"G": _G, "C_dark": _C_dark, "W3": _W3}
            base["membrane"] = {"source": _m.get("source", "unknown"), "kernel_computed": False}
            base["next_safe_action"] = (
                "Reduce hallucination risk (improve P or X primitives) then re-submit"
            )
            base["metacognition"] = {
                "confidence": 0.90,
                "next_safe_action": base["next_safe_action"],
                "measurement_used": True,
            }
            return base

        if _G is not None and _G < 0.50:
            output = KernelOutput(
                decision="ESCALATE",
                constitutional_floor_triggered="F8",
                reason=(
                    f"F8 GENIUS: G={_G:.3f} < 0.50 threshold. "
                    "Intelligence quality insufficient for autonomous action."
                ),
                audit_hash=compute_audit_hash(kernel_input),
                rollback_instruction=None,
            )
            base = output.model_dump()
            base["measurement_received"] = {"G": _G, "C_dark": _C_dark, "W3": _W3}
            base["membrane"] = {"source": _m.get("source", "unknown"), "kernel_computed": False}
            base["next_safe_action"] = (
                "Improve evidence/primitives then re-submit, or escalate to human"
            )
            base["metacognition"] = {
                "confidence": 0.85,
                "next_safe_action": base["next_safe_action"],
                "measurement_used": True,
            }
            return base

    # 3. Standard Allow
    output = KernelOutput(
        decision="ALLOW",
        constitutional_floor_triggered=None,
        reason="Action authorized under standard capability bounds.",
        audit_hash=(
            compute_audit_hash(kernel_input) if ReversibilityClass.requires_audit(r_class) else None
        ),
        rollback_instruction=(
            "reverse_operation"
            if r_class
            in {ReversibilityClass.R2_REVERSIBLE_WRITE, ReversibilityClass.R3_COSTLY_REVERSIBLE}
            else None
        ),
    )

    # ── Compute canonical judge identity (P0 FIX 2026-07-25) ──────────────
    _candidate_hash = intent.split("sha256:")[-1].split()[0].strip() if "sha256:" in intent else ""
    _judge_state = {
        "decision": output.decision,
        "seal_type": _seal_type,
        "seal_purpose": _seal_purpose_resolved,
        "action_class": action_class or "AUDIT_RECORD",
        "reversibility": _rev_raw,
        "authority_effect": _authority_effect_resolved,
        "audit_hash": output.audit_hash,
        "session_id": actor,
        "actor_id": actor,
        "candidate_hash": _candidate_hash,
        "ack_irreversible": _ack_irreversible,
    }
    _judge_state_json = json.dumps(_judge_state, sort_keys=True, separators=(",", ":"))
    _judge_state_hash = hashlib.sha256(_judge_state_json.encode()).hexdigest()
    _cc_raw = f"{actor}:{_candidate_hash}:{_judge_state_hash}:{output.audit_hash or ''}"
    _cc_id = "cc_" + hashlib.sha256(_cc_raw.encode()).hexdigest()[:40]
    output.constitutional_chain_id = _cc_id
    output.judge_state_hash = f"sha256:{_judge_state_hash}"
    output.seal_type = _seal_type
    base = output.model_dump()
    base["seal_type"] = _seal_type
    base["seal_purpose"] = _seal_purpose_resolved
    base["authority_effect"] = _authority_effect_resolved
    base["requires_human_signature"] = _requires_f13
    base["authorized_execution"] = _authority_effect_resolved == "EXECUTION_GRANT"
    base["action_class"] = action_class or "AUDIT_RECORD"
    target_aff = get_full_affordance(requested_capability)
    base["affordance"] = target_aff
    base["agency_level"] = target_aff.get("agency_level")

    if _has_measurement:
        base["measurement_received"] = {"G": _G, "C_dark": _C_dark, "W3": _W3}
        base["membrane"] = {
            "source": _m.get("source", "unknown"),
            "calculator": _m.get("calculator", "unknown"),
            "kernel_computed": False,
            "note": "Kernel read measurement; did not recompute (MEMBRANE-01/04)",
        }

    is_l5 = "L5" in str(target_aff.get("agency_level", ""))
    next_act = (
        "Proceed to arif_forge (with lease) then arif_seal only after explicit human ack"
        if is_l5
        else "Execute the capability; monitor delta_S and surface result for post-reflection"
    )
    base["next_safe_action"] = next_act
    base["metacognition"] = {
        "confidence": 0.92 if not is_l5 else 0.75,
        "why_this_tool": "Kernel minimum intercept passed all gates",
        "next_safe_action": next_act,
        "measurement_used": _has_measurement,
    }
    base["constitutional_check"] = {
        "floor_passed": True,
        "hold_required": is_l5,
        "agency_level": target_aff.get("agency_level"),
    }
    return base
