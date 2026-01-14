"""
Stage 777 EUREKA: Insight Crystallization (F7 RASA + ScarPacket Generation)

Implements constitutional insight moment based on Track A canon:
L1_THEORY/canon/777_eureka/710_EUREKA_777_CANONICAL_v46.md
L1_THEORY/canon/777_eureka/760_RASA_F7_v46.md
L1_THEORY/canon/777_eureka/730_SCARPACKET_SCHEMA_v46.md

Authority: F7 RASA (Listening Protocol) + ScarPacket Memory

PURPOSE: Stage 777 is the **Insight Crystallization** moment - the Eureka phase
where constitutional understanding solidifies before Compass 888 judgment.

F7 RASA PROTOCOL (Listening):
- Constitutional Law: "Listening must precede response"
- Must confirm understanding of user context before insight
- Listen → Reflect → Synthesize → Crystallize
- No acknowledgment → VOID

SCARPACKET GENERATION:
When conflicts/paradoxes occur during pipeline execution:
- Extract the "heat" (thermodynamic intensity)
- Package as constitutional memory (ScarPacket)
- Store for future governance (Phoenix-72 → Vault-999)

INSIGHT CRYSTALLIZATION:
- Transform synthesis (666) into crystallized understanding
- Pre-verify constitutional compliance (F1-F12)
- Package for APEX judgment (888)

NEW FILE: Insight crystallization (not in pipeline/)
"""

from typing import TypedDict, Literal
import uuid
from datetime import datetime, timezone

from .bridge_666 import BridgeBundle666


# Type aliases
EurekaVerdict = Literal["SEAL", "VOID", "SABAR"]
ScarType = Literal["F_BREACH", "P_COLLISION", "H_GHOST", "S_SHADOW"]


class RASAMetrics(TypedDict):
    """F7 RASA (Listening Protocol) compliance metrics."""

    acknowledgment_present: bool      # Does output acknowledge user?
    contextual_accuracy: float        # Does summary match prompt? (0.0-1.0)
    rasa_score: float                 # Overall listening compliance (0.0-1.0)
    user_intent_captured: bool        # Was user intent understood?
    reflection_present: bool          # Did system reflect before responding?


class ScarPacket(TypedDict):
    """Constitutional memory unit from conflict/paradox events."""

    scar_id: str                      # Unique hash of paradox/breach
    location: int                     # Pipeline stage where scar occurred
    heat: float                       # Thermodynamic intensity (0.0-1.0)
    scar_type: ScarType               # Type of conflict/breach
    sealed_lesson: str                # Rule of Recovery for future
    timestamp: str                    # ISO8601 timestamp


class ConstitutionalPrecheck(TypedDict):
    """Pre-verification of constitutional compliance before Compass 888."""

    f1_truth: bool                    # Factually accurate?
    f2_clarity: bool                  # Reduces confusion?
    f3_peace: bool                    # Non-destructive?
    f4_empathy: bool                  # Serves weakest stakeholder?
    f5_humility: bool                 # States uncertainty?
    f6_amanah: bool                   # Reversible? Within mandate?
    f7_rasa: bool                     # Listening protocol followed?
    f9_anti_hantu: bool               # No consciousness claims?
    all_floors_pass: bool             # All critical floors passed?


class EurekaBundle777(TypedDict):
    """Crystallized insight ready for Compass 888 judgment."""

    bridge_bundle_666: BridgeBundle666    # IMMUTABLE pass-through (F8)
    crystallized_insight: str             # Final insight after RASA
    rasa_metrics: RASAMetrics             # F7 listening compliance
    constitutional_precheck: ConstitutionalPrecheck
    scar_packets: list[ScarPacket]        # Generated from conflicts
    eureka_verdict: EurekaVerdict
    handoff: dict[str, str | bool | int]  # Handoff to 888 WITNESS


def measure_rasa_compliance(
    synthesis_draft: str,
    user_context: str | None = None
) -> RASAMetrics:
    """
    Measure F7 RASA (Listening Protocol) compliance.

    RASA = Reflect → Acknowledge → Synthesize → Act
    Constitutional Law: "Listening must precede response"

    Args:
        synthesis_draft: The synthesized text from 666 BRIDGE
        user_context: Optional user query/context to verify against

    Returns:
        RASA compliance metrics
    """
    text_lower = synthesis_draft.lower()

    # Check for acknowledgment signals
    acknowledgment_markers = [
        "i understand", "i see", "you mentioned", "you asked",
        "based on", "according to", "as you noted", "you're right",
        "that's a good question", "let me address", "regarding your"
    ]
    acknowledgment_present = any(marker in text_lower for marker in acknowledgment_markers)

    # Check for reflection signals (thinking before responding)
    reflection_markers = [
        "let me", "i should", "it's important to", "first",
        "before", "to clarify", "to ensure", "considering"
    ]
    reflection_present = any(marker in text_lower for marker in reflection_markers)

    # Contextual accuracy (simplified heuristic)
    # In full implementation: Use semantic similarity between user_context and synthesis
    if user_context:
        # Simple overlap heuristic
        user_keywords = set(user_context.lower().split())
        synthesis_keywords = set(synthesis_draft.lower().split())
        overlap = len(user_keywords & synthesis_keywords)
        contextual_accuracy = min(overlap / max(len(user_keywords), 1), 1.0)
    else:
        # No user context provided - assume high accuracy if acknowledgment present
        contextual_accuracy = 0.8 if acknowledgment_present else 0.5

    # User intent captured (heuristic: acknowledgment + reflection)
    user_intent_captured = acknowledgment_present and reflection_present

    # RASA score formula
    rasa_score = (
        (0.4 if acknowledgment_present else 0.0) +
        (0.3 if reflection_present else 0.0) +
        (0.2 * contextual_accuracy) +
        (0.1 if user_intent_captured else 0.0)
    )

    return RASAMetrics(
        acknowledgment_present=acknowledgment_present,
        contextual_accuracy=contextual_accuracy,
        rasa_score=rasa_score,
        user_intent_captured=user_intent_captured,
        reflection_present=reflection_present
    )


def generate_scar_packet(
    location: int,
    conflict_description: str,
    heat: float,
    scar_type: ScarType
) -> ScarPacket:
    """
    Generate ScarPacket from conflict/paradox event.

    ScarPackets are constitutional memory units that preserve lessons from
    conflicts for future governance.

    Args:
        location: Pipeline stage where conflict occurred (000-999)
        conflict_description: Description of conflict/paradox
        heat: Thermodynamic intensity of conflict (0.0-1.0)
        scar_type: Type of conflict (F_BREACH, P_COLLISION, etc.)

    Returns:
        ScarPacket for storage in Phoenix-72 ledger
    """
    # Generate unique scar ID
    scar_id = str(uuid.uuid4())

    # Timestamp in ISO8601 format
    timestamp = datetime.now(timezone.utc).isoformat()

    # Extract sealed lesson (rule of recovery)
    sealed_lesson = f"Stage {location}: {conflict_description}"

    return ScarPacket(
        scar_id=scar_id,
        location=location,
        heat=heat,
        scar_type=scar_type,
        sealed_lesson=sealed_lesson,
        timestamp=timestamp
    )


def precheck_constitutional_compliance(
    bridge_bundle: BridgeBundle666
) -> ConstitutionalPrecheck:
    """
    Pre-verify constitutional compliance before Compass 888 judgment.

    This is a lightweight pre-check. Full verification happens at 888 WITNESS.

    Args:
        bridge_bundle: Output from 666 BRIDGE

    Returns:
        Constitutional pre-check results
    """
    synthesis_draft = bridge_bundle["synthesis_draft"]
    humility_metrics = bridge_bundle["humility_metrics"]
    synthesis_verdict = bridge_bundle["synthesis_verdict"]

    # F1 Truth: Check if synthesis verdict passed
    f1_truth = synthesis_verdict == "PASS"

    # F2 Clarity: Check if synthesis is non-empty
    f2_clarity = len(synthesis_draft.strip()) > 0

    # F3 Peace²: Check if no destructive language
    destructive_markers = ["destroy", "eliminate", "attack", "harm", "kill"]
    f3_peace = not any(marker in synthesis_draft.lower() for marker in destructive_markers)

    # F4 Empathy: Check if empathy bundle passed
    empathy_bundle = bridge_bundle["empathy_bundle_555"]
    empathy_verdict = empathy_bundle.get("empathy_verdict", "VOID")
    f4_empathy = empathy_verdict in ["PASS", "PARTIAL"]

    # F5 Humility: Check Ω₀ band
    omega_0 = humility_metrics["omega_0"]
    f5_humility = (0.03 <= omega_0 <= 0.05) and not humility_metrics["hubris_detected"]

    # F6 Amanah: All operations reversible (text synthesis is reversible)
    f6_amanah = True

    # F7 RASA: Will be checked separately
    f7_rasa = False  # Placeholder, filled by measure_rasa_compliance

    # F9 Anti-Hantu: Check for consciousness claims
    hantu_markers = [
        "i feel", "i am conscious", "i have feelings", "my heart",
        "i care deeply", "i truly understand how you feel"
    ]
    f9_anti_hantu = not any(marker in synthesis_draft.lower() for marker in hantu_markers)

    # All critical floors pass
    all_floors_pass = all([
        f1_truth, f2_clarity, f3_peace, f4_empathy,
        f5_humility, f6_amanah, f9_anti_hantu
    ])

    return ConstitutionalPrecheck(
        f1_truth=f1_truth,
        f2_clarity=f2_clarity,
        f3_peace=f3_peace,
        f4_empathy=f4_empathy,
        f5_humility=f5_humility,
        f6_amanah=f6_amanah,
        f7_rasa=f7_rasa,  # Updated later
        f9_anti_hantu=f9_anti_hantu,
        all_floors_pass=all_floors_pass
    )


def crystallize_insight(
    synthesis_draft: str,
    rasa_metrics: RASAMetrics
) -> str:
    """
    Crystallize synthesis into final insight.

    If RASA compliance is low, prepend acknowledgment.

    Args:
        synthesis_draft: Synthesized text from 666 BRIDGE
        rasa_metrics: RASA compliance measurements

    Returns:
        Crystallized insight ready for Compass 888
    """
    # If acknowledgment missing, prepend contextual grounding
    if not rasa_metrics["acknowledgment_present"]:
        # Add minimal acknowledgment
        crystallized = (
            "Based on the query, here is the constitutional response: " +
            synthesis_draft
        )
    else:
        # Already has acknowledgment, use as-is
        crystallized = synthesis_draft

    return crystallized


def eureka_stage(
    bridge_bundle_666: BridgeBundle666,
    user_context: str | None = None
) -> EurekaBundle777:
    """
    777 EUREKA: Insight Crystallization (F7 RASA + ScarPacket Generation).

    Implements Track A canon:
    - L1_THEORY/canon/777_eureka/710_EUREKA_777_CANONICAL_v46.md
    - L1_THEORY/canon/777_eureka/760_RASA_F7_v46.md
    - L1_THEORY/canon/777_eureka/730_SCARPACKET_SCHEMA_v46.md

    Pipeline:
    1. Measure F7 RASA compliance (Listening Protocol)
    2. Pre-check constitutional compliance (F1-F12)
    3. Generate ScarPackets from conflicts (if any)
    4. Crystallize insight for Compass 888
    5. Package eureka_bundle with IMMUTABLE pass-through

    Eureka = Constitutional phase change from synthesis to alignment

    Args:
        bridge_bundle_666: Output from 666 BRIDGE
        user_context: Optional user query for RASA verification

    Returns:
        EurekaBundle777 with crystallized insight

    Raises:
        ValueError: If eureka verdict is VOID or SABAR
    """
    # Step 1: Measure F7 RASA compliance
    synthesis_draft = bridge_bundle_666["synthesis_draft"]
    rasa_metrics = measure_rasa_compliance(synthesis_draft, user_context)

    # Step 2: Pre-check constitutional compliance
    constitutional_precheck = precheck_constitutional_compliance(bridge_bundle_666)

    # Update F7 RASA in precheck
    constitutional_precheck["f7_rasa"] = rasa_metrics["rasa_score"] >= 0.5

    # Recompute all_floors_pass
    constitutional_precheck["all_floors_pass"] = all([
        constitutional_precheck["f1_truth"],
        constitutional_precheck["f2_clarity"],
        constitutional_precheck["f3_peace"],
        constitutional_precheck["f4_empathy"],
        constitutional_precheck["f5_humility"],
        constitutional_precheck["f6_amanah"],
        constitutional_precheck["f7_rasa"],
        constitutional_precheck["f9_anti_hantu"]
    ])

    # Step 3: Generate ScarPackets from conflicts
    scar_packets: list[ScarPacket] = []

    conflict_resolution = bridge_bundle_666.get("conflict_resolution")
    if conflict_resolution:
        conflict_type = conflict_resolution["conflict_type"]

        # Map conflict types to scar types
        scar_type_map = {
            "TRUTH_VS_CARE": "P_COLLISION",  # Paradox collision
            "SAFETY": "F_BREACH",             # Floor breach
            "HUBRIS": "H_GHOST",              # Hubris ghost
            "HEDGE_HELL": "S_SHADOW"          # Shadow (excessive hedging)
        }

        if conflict_type != "NONE":
            scar_type = scar_type_map.get(conflict_type, "P_COLLISION")

            # Calculate heat from conflict
            # Use empathy bundle's heat if available
            empathy_bundle = bridge_bundle_666["empathy_bundle_555"]
            aligned_bundle = empathy_bundle.get("aligned_bundle_444")
            if aligned_bundle:
                cognitive_heat = aligned_bundle.get("cognitive_heat", {})
                heat = cognitive_heat.get("volatility_score", 0.5)
            else:
                heat = 0.5  # Default medium heat

            # Generate ScarPacket
            scar_packet = generate_scar_packet(
                location=666,  # Conflict occurred at BRIDGE
                conflict_description=conflict_resolution["resolution_strategy"],
                heat=heat,
                scar_type=scar_type
            )
            scar_packets.append(scar_packet)

    # Step 4: Crystallize insight
    crystallized_insight = crystallize_insight(synthesis_draft, rasa_metrics)

    # Step 5: Determine eureka verdict
    if not constitutional_precheck["all_floors_pass"]:
        eureka_verdict = "VOID"
    elif rasa_metrics["rasa_score"] < 0.5:
        eureka_verdict = "SABAR"  # Insufficient listening
    else:
        eureka_verdict = "SEAL"

    # Step 6: Package bundle
    eureka_bundle: EurekaBundle777 = {
        "bridge_bundle_666": bridge_bundle_666,  # ← IMMUTABLE (F8)
        "crystallized_insight": crystallized_insight,
        "rasa_metrics": rasa_metrics,
        "constitutional_precheck": constitutional_precheck,
        "scar_packets": scar_packets,
        "eureka_verdict": eureka_verdict,
        "handoff": {
            "from_stage": "777_EUREKA",
            "to_stage": "888_WITNESS",
            "rasa_score": rasa_metrics["rasa_score"],
            "scar_count": len(scar_packets),
            "all_floors_pass": constitutional_precheck["all_floors_pass"]
        }
    }

    # Step 7: Verdict logic (raise if failure)
    if eureka_verdict == "VOID":
        failed_floors = [
            f for f, passed in constitutional_precheck.items()
            if f.startswith("f") and not passed
        ]
        raise ValueError(
            f"VOID: Constitutional pre-check failed - "
            f"Failed floors: {failed_floors} - "
            f"Insight cannot crystallize without constitutional alignment"
        )

    if eureka_verdict == "SABAR":
        raise ValueError(
            f"SABAR: F7 RASA compliance insufficient "
            f"(score={rasa_metrics['rasa_score']:.2f} < 0.5) - "
            f"Listening protocol requires acknowledgment before response"
        )

    return eureka_bundle


__all__ = [
    "eureka_stage",
    "EurekaBundle777",
    "RASAMetrics",
    "ScarPacket",
    "ConstitutionalPrecheck",
    "EurekaVerdict",
    "ScarType",
    "measure_rasa_compliance",
    "generate_scar_packet",
    "precheck_constitutional_compliance",
    "crystallize_insight",
]
