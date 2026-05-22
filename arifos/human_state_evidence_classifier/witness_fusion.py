"""Witness fusion — combines evidence from multiple channels safely.

This is the core inference engine.
It is NOT an oracle. It classifies evidence, not human truth.

Core questions it must answer for every output:
1. What is being inferred?
2. From what witnesses?
3. With what confidence?
4. What must NOT be claimed?
5. Does Arif need to confirm?
"""

from typing import Optional, Dict, Any

from .labels import StateDomain, TruthStatus, Confidence
from .schemas import HumanStateEstimate
from .text_signals import analyze_text_signals
from .safety import forbidden_claims_for


def estimate_human_state(
    text: str,
    domain: StateDomain,
    well_telemetry: Optional[Dict[str, Any]] = None,
    user_confirmed: Optional[bool] = None,
) -> HumanStateEstimate:
    """Classify human-state evidence safely.

    This function does not certify human state.
    It combines available witnesses and produces a safe, labelled estimate.

    Parameters
    ----------
    text:
        Raw conversation text.
    domain:
        Which expression domain to classify evidence for.
    well_telemetry:
        Optional WELL output. Must contain truth_status and operator_confirmed.
        If None or empty → biological witness is absent.
    user_confirmed:
        Did Arif explicitly confirm or reject this interpretation?
        None = no confirmation received yet.
    """

    # ── Step 1: Classify text evidence ────────────────────────────────────
    signals = analyze_text_signals(text)
    textual = signals.get(domain.value, [])
    text_signal_count = len([s for s in textual if not s.startswith("cannot_")])

    # ── Step 2: Classify biological/telemetry evidence ────────────────────
    biological_signals: list[str] = []

    if well_telemetry is None or well_telemetry == {}:
        biological_signals.append("no_biological_witness_available")
        telemetry_status = TruthStatus.HOLD
    else:
        truth_status = well_telemetry.get("truth_status", "UNVERIFIED")
        operator_confirmed = well_telemetry.get("operator_confirmed", False)

        if truth_status in ("VOID", "CONTAMINATED", "TEST_FIXTURE"):
            telemetry_status = TruthStatus.VOID_TELEMETRY
            biological_signals.append("well_telemetry_void_or_contradicted")
        elif operator_confirmed is True:
            telemetry_status = TruthStatus.USER_CONFIRMED
            biological_signals.append("well_telemetry_user_confirmed")
        else:
            telemetry_status = TruthStatus.TOOL_REPORTED
            biological_signals.append("well_telemetry_tool_reported_unverified")

    # ── Step 3: Handle sovereign confirmation first ───────────────────────
    # Sovereign witness overrides all other evidence.
    # Arif's word beats any algorithm.

    if user_confirmed is True:
        status = TruthStatus.USER_CONFIRMED
        confidence = Confidence.HIGH
        human_confirmation_required = False
        safe_statement = _build_safe_statement(domain, status, textual)
        safe_statement += " Arif has confirmed this interpretation."

        return HumanStateEstimate(
            domain=domain,
            status=status,
            confidence=confidence,
            textual_signals=textual,
            biological_signals=biological_signals,
            sovereign_confirmation=True,
            safe_statement=safe_statement,
            forbidden_claims=forbidden_claims_for(domain),
            human_confirmation_required=human_confirmation_required,
        )

    if user_confirmed is False:
        status = TruthStatus.CONTRADICTED
        confidence = Confidence.LOW
        human_confirmation_required = True
        safe_statement = (
            "Arif contradicted this interpretation. "
            "The estimate must not be used as truth. "
            f"Textual signals ({len(textual)} found) are overridden by sovereign rejection."
        )

        return HumanStateEstimate(
            domain=domain,
            status=status,
            confidence=confidence,
            textual_signals=textual,
            biological_signals=biological_signals,
            sovereign_confirmation=False,
            safe_statement=safe_statement,
            forbidden_claims=forbidden_claims_for(domain),
            human_confirmation_required=human_confirmation_required,
        )

    # ── Step 4: No sovereign confirmation — use available evidence ────────

    # BODY: Always conservative. Text cannot determine body state.
    if domain == StateDomain.BODY:
        confidence = Confidence.LOW
        status = telemetry_status if well_telemetry else TruthStatus.HOLD
        human_confirmation_required = True
        safe_statement = (
            "Body state cannot be determined from text alone. "
            "Biological telemetry and Arif confirmation are required before "
            "any operational readiness inference can be made."
        )

    # AKAL / PRESENCE / AMANAH: Text can weakly classify reasoning discipline
    elif domain in (StateDomain.AKAL, StateDomain.PRESENCE, StateDomain.AMANAH):
        if text_signal_count >= 3:
            confidence = Confidence.MEDIUM
        elif text_signal_count >= 1:
            confidence = Confidence.LOW
        else:
            confidence = Confidence.LOW
            textual.append("no_signals_detected_for_this_domain")

        status = TruthStatus.TEXT_SIGNAL_ONLY
        human_confirmation_required = True
        safe_statement = _build_safe_statement(domain, status, textual)

    # PEACE / ENERGY: Conservative — text can indicate activation, not capacity
    elif domain in (StateDomain.PEACE, StateDomain.ENERGY):
        if text_signal_count >= 2:
            confidence = Confidence.MEDIUM
        elif text_signal_count >= 1:
            confidence = Confidence.LOW
        else:
            confidence = Confidence.LOW

        status = TruthStatus.TEXT_SIGNAL_ONLY
        human_confirmation_required = True
        safe_statement = _build_safe_statement(domain, status, textual)

    else:
        confidence = Confidence.LOW
        status = TruthStatus.HOLD
        human_confirmation_required = True
        safe_statement = "No evidence available for this domain. Human confirmation required."

    return HumanStateEstimate(
        domain=domain,
        status=status,
        confidence=confidence,
        textual_signals=textual,
        biological_signals=biological_signals,
        sovereign_confirmation=None,
        safe_statement=safe_statement,
        forbidden_claims=forbidden_claims_for(domain),
        human_confirmation_required=human_confirmation_required,
    )


def _build_safe_statement(domain: StateDomain, status: TruthStatus, textual: list[str]) -> str:
    signal_count = len([s for s in textual if not s.startswith("cannot_")])

    domain_descriptions = {
        StateDomain.BODY: (
            "Body state evidence cannot be determined from text. Biological data required."
        ),
        StateDomain.PEACE: (
            f"Expression patterns related to non-reactive review detected ({signal_count} signals). "
            "This is not a verdict on inner peace — expression is not inner state."
        ),
        StateDomain.ENERGY: (
            f"Expression patterns related to cognitive activation detected ({signal_count} signals). "
            "This is not a verdict on biological energy — expression is not capacity."
        ),
        StateDomain.AKAL: (
            f"Expression patterns related to reasoning discipline detected ({signal_count} signals). "
            "This is not a verdict on intellect — pattern is not proof."
        ),
        StateDomain.PRESENCE: (
            f"Expression patterns related to contextual tracking detected ({signal_count} signals). "
            "This is not a verdict on consciousness — response is not presence."
        ),
        StateDomain.AMANAH: (
            f"Expression patterns related to truth preservation detected ({signal_count} signals). "
            "This is not a verdict on moral state — behavior is not character."
        ),
    }

    base = domain_descriptions.get(domain, "Evidence classification complete.")

    if status == TruthStatus.TEXT_SIGNAL_ONLY:
        return base + " Confirmation by Arif required before operational use."
    elif status == TruthStatus.VOID_TELEMETRY:
        return base + " Biological telemetry is void. No inference may be drawn."
    elif status == TruthStatus.TOOL_REPORTED:
        return base + " Telemetry is tool-reported only. Arif confirmation required."
    else:
        return base
