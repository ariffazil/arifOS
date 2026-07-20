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
# In production, this is loaded from /root/.secrets/ via SOPS+AGE decryption at boot.
# For now, a dev-mode sentinel is used; production MUST replace this with a key file load.
_SOVEREIGN_KEY_SENTINEL = os.environ.get(
    "ARIFOS_SOVEREIGN_KEY",
    "DEV_ONLY_SENTINEL_REPLACE_AT_PROD_BOOT",
)


def _verify_sovereign_token(token: str | None) -> bool:
    """
    F11 AUTH: Cryptographically verify F13 SOVEREIGN token.

    Strict requirements (production):
    - Token MUST be a non-empty ed25519 signature
    - Signature MUST verify against the SOVEREIGN public key
    - Public key fingerprint MUST match the on-disk fingerprint at
      /root/.secrets/sovereign_key.fp

    Dev-mode fallback (current):
    - Token MUST equal the sentinel string (env-loaded)
    - This is trivially bypassable — DO NOT use in production
    """
    if not token:
        return False
    # Dev-mode constant-time comparison to prevent timing attacks
    if len(token) != len(_SOVEREIGN_KEY_SENTINEL):
        return False
    result = 0
    for a, b in zip(token, _SOVEREIGN_KEY_SENTINEL, strict=True):
        result |= ord(a) ^ ord(b)
    return result == 0


def compute_audit_hash(payload: KernelInput) -> str:
    """Generate a stable sha256 receipt for the vault."""
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
) -> dict[str, Any]:
    """
    The Minimum Constitutional Kernel. All federation actions pass through here.

    This replaces the heavy deliberation of the 888_JUDGE for runtime execution
    checks. It returns a ruthless ALLOW, DENY, ESCALATE, or SIMULATE.

    F13 SOVEREIGN gate: R4/R5 actions require cryptographic sovereign token
    (ed25519). Dev-mode fallback uses constant-time sentinel comparison;
    production MUST load the sovereign public key from
    /root/.secrets/sovereign_key.pub at boot.

    MEMBRANE-03: When measurement dict is provided (from A-FORGE MeasurementPacket),
    the kernel uses G, C_dark, W3 for floor checks WITHOUT recomputing.
    When absent, falls back to current advisory behavior.
    """
    evidence = evidence or []

    # Normalize human-friendly reversibility aliases → R0..R5.
    # Unknown tokens fail CLOSED to R4 (was already the case).
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
        r_class = ReversibilityClass.R4_IRREVERSIBLE  # Fail closed

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

    # ── MEMBRANE-03: Extract pre-computed APEX from MeasurementPacket ──
    # When A-FORGE passes measurement, the kernel reads G, C_dark, W3
    # for floor checks. It NEVER recomputes these values.
    _m = measurement or {}
    _G = _m.get("G")
    _C_dark = _m.get("C_dark")
    _W3 = _m.get("W3")
    _has_measurement = _G is not None and _C_dark is not None

    # 1. 888 HOLD trigger for Irreversible or Sovereign actions (F13 SOVEREIGN)
    if r_class in {ReversibilityClass.R4_IRREVERSIBLE, ReversibilityClass.R5_SOVEREIGN}:
        if not _verify_sovereign_token(authority_token):
            output = KernelOutput(
                decision="ESCALATE",
                # 888_HOLD is on F13 SOVEREIGN, not F8 (corrected 2026-06-22)
                constitutional_floor_triggered="F13",
                reason=(
                    f"{r_class.value} action blocked. "
                    "F13 SOVEREIGN cryptographic signature required (F11 AUTH)."
                ),
                audit_hash=compute_audit_hash(kernel_input),
                rollback_instruction=None,
            )
            base = output.model_dump()
            # Wire the new metacognitive plumbing into the kernel
            target_aff = get_full_affordance(requested_capability)
            base["affordance"] = target_aff
            base["agency_level"] = target_aff.get("agency_level")
            base["metacognition"] = {
                "confidence": 0.99,
                "why_this_tool": "Kernel intercept on L5 path",
                "next_safe_action": "Obtain F13 sovereign token or downgrade to reversible action",
                "uncertainty_reason": "Missing sovereign authority for irreversible action",
            }
            base["next_safe_action"] = (
                "Request explicit human 888 confirmation or revise to lower blast_radius"
            )
            base["constitutional_check"] = {
                "hold_required": True,
                "floor": "F13",
                "agency": target_aff.get("agency_level"),
            }
            return base

    # 2. Evidence Thresholds for Truth (F2 TRUTH)
    # Per FLOOR_INVARIANTS_v2026.06.23: P(truth) ≥ 0.99 requires source attribution.
    # FACT/ESTIMATE claims without evidence = cheap_claim (score = 0.4) → DENY.
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

    # 2b. CONFLICT state — sources disagree. Must surface contradiction, not
    # resolve silently.
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

    # 2c. HYPOTHESIS/CLAIM with substantial blast radius → require evidence anyway
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

    # 2d. MEMBRANE: Measurement-based floor checks (F9 ANTI-HANTU)
    # When A-FORGE passes a MeasurementPacket, use it for floor gating.
    # The kernel reads, never recomputes (MEMBRANE-01/04).
    if _has_measurement:
        # F9 ANTI-HANTU: C_dark < 0.30 — hallucination detector
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

        # F8 GENIUS: G < 0.50 — intelligence quality too low
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
    base = output.model_dump()
    target_aff = get_full_affordance(requested_capability)
    base["affordance"] = target_aff
    base["agency_level"] = target_aff.get("agency_level")

    # ── MEMBRANE: Attach measurement receipt when present ──
    if _has_measurement:
        base["measurement_received"] = {"G": _G, "C_dark": _C_dark, "W3": _W3}
        base["membrane"] = {
            "source": _m.get("source", "unknown"),
            "calculator": _m.get("calculator", "unknown"),
            "kernel_computed": False,
            "note": "Kernel read measurement; did not recompute (MEMBRANE-01/04)",
        }

    # Metacognitive next step from kernel perspective
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
