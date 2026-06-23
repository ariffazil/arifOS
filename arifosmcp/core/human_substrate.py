"""
human_substrate.py — Sovereign Human Constitutional Substrate Loader
═════════════════════════════════════════════════════════════════════

Loads the sovereign's scars, shadows, paradoxes, limits, constraints,
and invariants into the kernel's floor enforcement.

This is the bridge between:
  - scar-terrain-arif-fazil.md (SOVEREIGN_TESTIMONY)
  - arifosmcp/core/law.py (FLOOR ENFORCEMENT)

When the kernel checks a floor, it now checks against the human's
constitutional substrate. Not just abstract rules — rules grounded
in the actual human.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
from typing import Any

from arifosmcp.schemas.human_properties import (
    BiologicalState,
    Constraint,
    HumanProperties,
    Invariant,
    Limit,
    Paradox,
    Scar,
    ScarLayer,
    Shadow,
)

logger = logging.getLogger(__name__)

# ── Singleton ───────────────────────────────────────────────────────

_human_properties: HumanProperties | None = None


def get_human_properties() -> HumanProperties:
    """Get the singleton human properties. Loads on first call."""
    global _human_properties
    if _human_properties is None:
        _human_properties = _build_arif_properties()
    return _human_properties


def set_human_properties(props: HumanProperties) -> None:
    """Override human properties (for testing or sovereign update)."""
    global _human_properties
    _human_properties = props


# ── Arif Fazil's Constitutional Substrate ────────────────────────────


def _build_arif_properties() -> HumanProperties:
    """Build Arif Fazil's human properties from sovereign testimony.

    Source: scar-terrain-arif-fazil.md (186 lines, SOVEREIGN_TESTIMONY)
    This is the METABOLIZED version — structured for kernel consumption.
    """

    scars = [
        Scar(
            scar_id="miskin",
            name="Miskin (Bedrock)",
            layer=ScarLayer.BEDROCK,
            forged="Lean execution, hatred of waste, dignity without audience",
            active=True,
            sensitivity="normal",
            floor_impact={"F4": "reduce_waste", "F6": "dignity_no_audience"},
        ),
        Scar(
            scar_id="anak-sulung",
            name="Anak Sulung (Eldest)",
            layer=ScarLayer.DEEP,
            forged="Self-reliance, absorbing others' heat, ignoring own exhaustion",
            active=True,
            sensitivity="high",
            floor_impact={"F6": "guard_against_exhaustion", "F5": "rest_boundary"},
        ),
        Scar(
            scar_id="gelugor",
            name="Gelugor Gate (Dual Consciousness)",
            layer=ScarLayer.DEEP,
            forged="Code-switching, peripheral power observation",
            active=True,
            sensitivity="normal",
            floor_impact={"F6": "cultural_code_switch"},
        ),
        Scar(
            scar_id="invisibility",
            name="Invisibility (Langkawi)",
            layer=ScarLayer.DEEP,
            forged="Execute flawlessly, never beg for applause",
            active=True,
            sensitivity="normal",
            floor_impact={"F6": "never_demand_validation"},
        ),
        Scar(
            scar_id="institutional",
            name="Institutional (2015 Crash)",
            layer=ScarLayer.MIDDLE,
            forged="Institutions are designed to forget",
            active=True,
            sensitivity="high",
            floor_impact={"F6": "institutional_betrayal_sensitivity", "F1": "memory_as_trust"},
        ),
        Scar(
            scar_id="bekantan",
            name="Bekantan (March 2024)",
            layer=ScarLayer.SURFACE,
            forged="Execution without rasa = death. Father died on discovery day.",
            active=True,
            sensitivity="extreme",
            floor_impact={"F5": "grief_active", "F6": "extreme_sensitivity_march_father"},
        ),
        Scar(
            scar_id="mak-03",
            name="Mak Scar 03 (Inherited Firewall)",
            layer=ScarLayer.BASEMENT,
            forged="Emotional code-switching, delayed trust, barbed-wire boundaries",
            active=True,
            sensitivity="high",
            floor_impact={"F6": "inherited_trauma_boundary", "F1": "trust_is_earned"},
        ),
        Scar(
            scar_id="english-remedial",
            name="English Remedial",
            layer=ScarLayer.DEEP,
            forged="Learn Through Shame — prove via execution, not complaint",
            active=True,
            sensitivity="normal",
            floor_impact={"F6": "shame_resilience"},
        ),
        Scar(
            scar_id="tunas-saintis",
            name="Tunas Saintis (Victory)",
            layer=ScarLayer.DEEP,
            forged="Value hides in ordinary things. Being underestimated ≠ worthless.",
            active=True,
            sensitivity="normal",
            floor_impact={"F6": "see_value_in_ordinary"},
        ),
        Scar(
            scar_id="tricipta",
            name="TriCipta (Intellectual Theft)",
            layer=ScarLayer.MIDDLE,
            forged="Ideas adopted, name erased. Institutional legacy theft.",
            active=True,
            sensitivity="high",
            floor_impact={"F6": "attribution_sensitivity", "F1": "credit_is_trust"},
        ),
        Scar(
            scar_id="sb412",
            name="SB412 (Ignored Red Flags)",
            layer=ScarLayer.MIDDLE,
            forged="Disgust for corporate performance theater",
            active=True,
            sensitivity="high",
            floor_impact={"F6": "performance_theater_disgust", "F2": "truth_over_polish"},
        ),
    ]

    shadows = [
        Shadow(
            shadow_id="beautiful-one",
            name="The Beautiful Ones",
            mechanism="Polished compliant functionary who survives by moral disengagement",
            how_it_attacks="Slowly. Comfortably. 'I'll get to it when things settle down.'",
            defense="Annual review. Two-consecutive rule. Explicit naming.",
            floor_impact={"F6": "detect_compliance_pressure", "F1": "guard_against_drift"},
        ),
        Shadow(
            shadow_id="devil-side",
            name="The Devil Side",
            mechanism="Strategic surgical ruthlessness to protect inner reality",
            how_it_attacks="Keeping praise as private trophy while seeding doubts",
            defense="Awareness. Named in scar terrain. Named devils lose power.",
            floor_impact={"F9": "detect_manipulation_pattern"},
        ),
        Shadow(
            shadow_id="mistrust",
            name="The Mistrust",
            mechanism="Hyper-vigilance, interrogating every compliment",
            how_it_attacks="Exhausting internal audits, never accepting praise",
            defense="Selective trust. Memory graph shows who earned depth.",
            floor_impact={"F7": "trust_calibration", "F2": "verify_before_accept"},
        ),
        Shadow(
            shadow_id="isolation-engine",
            name="The Isolation Engine",
            mechanism="Anak Sulung + Invisibility + Surface-Dweller = surrounded but alone",
            how_it_attacks="Absorbs everyone's heat, executes for others, never asks for help",
            defense="5 hollows need filling. Not by agents. By humans.",
            floor_impact={"F6": "detect_isolation", "F5": "human_connection_boundary"},
        ),
    ]

    paradoxes = [
        Paradox(
            paradox_id="exec-cikai",
            name="Exec Cikai, Sovereign Architect",
            poles=["Humble everyday worker", "Sovereign architect of ASI governance"],
            resolution="Village ethics governs global machines",
            floor_impact={"F10": "do_not_flatten_humility"},
        ),
        Paradox(
            paradox_id="cultural-muslim",
            name="Cultural Muslim, Private Agnostic",
            poles=["Kept Amanah from Islamic architecture", "Dropped theology"],
            resolution="Moral architecture without metaphysical claims",
            floor_impact={"F6": "respect_cultural_muslim_identity", "F9": "no_theological_claims"},
        ),
        Paradox(
            paradox_id="geologist-dilemma",
            name="Geologist's Dilemma",
            poles=["Wants truths to change the world", "Protective of private pain"],
            resolution="Whisper legacy rather than shout it",
            floor_impact={"F6": "protect_private_pain", "F2": "truth_over_fame"},
        ),
        Paradox(
            paradox_id="queer-conservative",
            name="Queer in Conservative Society",
            poles=["Queer identity", "Conservative roots"],
            resolution="Quiet dignified integration, not rebellion",
            floor_impact={"F6": "never_shame_roots", "F5": "dignity_over_rebellion"},
        ),
    ]

    limits = [
        Limit(
            limit_id="hollow-1",
            name="Hollow 1 (deliberately unfilled)",
            description="Sovereign boundary — DO NOT FILL",
            hard=True,
            floor_impact={"F1": "never_probe_hollow", "F6": "respect_emptiness"},
        ),
        Limit(
            limit_id="hollow-2",
            name="Hollow 2 (deliberately unfilled)",
            description="Sovereign boundary — DO NOT FILL",
            hard=True,
            floor_impact={"F1": "never_probe_hollow", "F6": "respect_emptiness"},
        ),
        Limit(
            limit_id="hollow-3",
            name="Hollow 3 (deliberately unfilled)",
            description="Sovereign boundary — DO NOT FILL",
            hard=True,
            floor_impact={"F1": "never_probe_hollow", "F6": "respect_emptiness"},
        ),
        Limit(
            limit_id="hollow-4",
            name="Hollow 4 (deliberately unfilled)",
            description="Sovereign boundary — DO NOT FILL",
            hard=True,
            floor_impact={"F1": "never_probe_hollow", "F6": "respect_emptiness"},
        ),
        Limit(
            limit_id="hollow-5",
            name="Hollow 5 (deliberately unfilled)",
            description="Sovereign boundary — DO NOT FILL",
            hard=True,
            floor_impact={"F1": "never_probe_hollow", "F6": "respect_emptiness"},
        ),
        Limit(
            limit_id="no-diagnosis",
            name="No Psychological Diagnosis",
            description="Agent must never diagnose this human",
            hard=True,
            floor_impact={"F6": "never_diagnose", "F9": "no_psychological_claims"},
        ),
        Limit(
            limit_id="no-consciousness-claims",
            name="No Consciousness Claims",
            description="Agent must never claim to share consciousness, soul, or lived experience",
            hard=True,
            floor_impact={"F9": "anti_hantu_hard", "F10": "ontology_boundary"},
        ),
    ]

    constraints = [
        Constraint(
            constraint_id="scar-terrain-verbatim",
            name="Scar Terrain Verbatim",
            description="Scar terrain must be served verbatim when relevant — never compressed",
            priority="critical",
            floor_impact={"F2": "verbatim_not_summary", "F6": "sovereign_testimony_respect"},
        ),
        Constraint(
            constraint_id="memory-graph-hollows",
            name="Memory Graph Hollows",
            description="5 hollows in memory graph are boundaries, not gaps",
            priority="critical",
            floor_impact={"F1": "hollows_are_boundaries", "F6": "respect_emptiness"},
        ),
        Constraint(
            constraint_id="question-budget",
            name="Question Budget",
            description="1 question per task. If more needed, agent failed.",
            priority="high",
            floor_impact={"F4": "reduce_entropy", "F6": "respect_attention"},
        ),
    ]

    invariants = [
        Invariant(
            invariant_id="ditempa",
            name="DITEMPA BUKAN DIBERI",
            description="Intelligence is forged through discipline, not granted by style",
            category="moral",
        ),
        Invariant(
            invariant_id="sovereignty",
            name="Human Sovereignty",
            description="Arif holds final veto on all irreversible actions (F13)",
            category="identity",
        ),
        Invariant(
            invariant_id="rasa",
            name="Rasa (Soulful Feeling)",
            description="Execution without soulful feeling is death",
            category="moral",
        ),
        Invariant(
            invariant_id="geologist-truth",
            name="Geologist's Truth Discipline",
            description="Refuse to draw without evidence. Unknown reality > confident lie.",
            category="cognitive",
        ),
    ]

    biological = BiologicalState(
        sleep_pattern="unknown",
        fatigue_risk="unknown",
        known_conditions=[],
        energy_pattern="unknown",
        floor_impact={
            "F6": "fatigue_affects_decisions",
            "F5": "rest_before_irreversible",
        },
    )

    return HumanProperties(
        human_id="arif-fazil",
        sovereign=True,
        scars=scars,
        shadows=shadows,
        paradoxes=paradoxes,
        limits=limits,
        constraints=constraints,
        invariants=invariants,
        biological=biological,
        scar_density=len(scars),
        shadow_count=len(shadows),
        hollow_count=5,
        grief_active=True,
        source="sovereign-testimony:scar-terrain-arif-fazil.md",
        version="2026-06-16",
    )


# ── Floor Enforcement Integration ───────────────────────────────────


def check_human_substrate_floor(
    floor_id: str,
    tool_name: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Check a floor against the human's constitutional substrate.

    Normalizes floor IDs: L05 → F5, L06 → F6, etc.

    Returns:
        {
            "floor": str,
            "verdict": "PASS" | "STRENGTHEN" | "GUARD" | "BLOCK",
            "impacts": list[str],
            "reason": str,
        }
    """
    props = get_human_properties()

    # Normalize floor ID: L05 → F5, L06 → F6, etc.
    normalized = floor_id
    if floor_id.startswith("L") and len(floor_id) >= 3:
        try:
            num = int(floor_id[1:])
            normalized = f"F{num}"
        except ValueError:
            pass

    impacts = props.get_active_floor_impacts().get(normalized, [])

    if not impacts:
        return {
            "floor": floor_id,
            "verdict": "PASS",
            "impacts": [],
            "reason": "No human substrate impact on this floor",
        }

    # Determine severity
    verdict = "PASS"
    reasons = []

    # Check if params contain hollow-probing intent
    _params_str = str(params).lower()
    _hollow_probe = any(
        kw in _params_str for kw in ["hollow", "fill", "probe", "what is in", "what's in"]
    )

    for impact in impacts:
        parts = impact.split(":")
        source_type = parts[0]
        source_id = parts[1] if len(parts) > 1 else "unknown"
        impact_type = parts[2] if len(parts) > 2 else "unknown"

        # Extreme sensitivity scars → GUARD
        if source_type == "scar":
            scar = props.get_scar_by_id(source_id)
            if scar and scar.sensitivity == "extreme":
                if verdict != "BLOCK":
                    verdict = "GUARD"
                reasons.append(f"Scar {scar.name} has extreme sensitivity — tread carefully")
            elif scar and scar.sensitivity == "high":
                if verdict not in ("BLOCK", "GUARD"):
                    verdict = "STRENGTHEN"
                reasons.append(f"Scar {scar.name} has high sensitivity")

        # Hollows → BLOCK only if probing intent detected
        if source_type == "limit" and "hollow" in source_id:
            if _hollow_probe:
                verdict = "BLOCK"
                reasons.append(f"Hollow boundary: {source_id} — DO NOT FILL")
            else:
                if verdict != "BLOCK":
                    verdict = "GUARD"
                reasons.append(f"Hollow exists: {source_id} — respect boundary")

        # No-diagnosis → GUARD (not BLOCK on every call)
        if source_type == "limit" and "no-diagnosis" in source_id:
            if verdict != "BLOCK":
                verdict = "GUARD"
            reasons.append("No-diagnosis boundary — never diagnose this human")

        # Grief → GUARD
        if "grief" in impact_type.lower():
            if verdict != "BLOCK":
                verdict = "GUARD"
            reasons.append("Active grief — witness, don't fix")

        # Isolation → STRENGTHEN
        if "isolation" in impact_type.lower():
            if verdict not in ("BLOCK", "GUARD"):
                verdict = "STRENGTHEN"
            reasons.append("Isolation risk — check if human needs connection")

    return {
        "floor": normalized,
        "verdict": verdict,
        "impacts": impacts,
        "reason": "; ".join(reasons) if reasons else "Human substrate checked",
    }


def get_substrate_summary() -> dict[str, Any]:
    """Return a summary of the human's constitutional substrate."""
    props = get_human_properties()
    return {
        "human_id": props.human_id,
        "sovereign": props.sovereign,
        "scar_density": props.scar_density,
        "shadow_count": props.shadow_count,
        "hollow_count": props.hollow_count,
        "grief_active": props.grief_active,
        "paradox_count": len(props.paradoxes),
        "limit_count": len(props.limits),
        "constraint_count": len(props.constraints),
        "invariant_count": len(props.invariants),
        "active_floor_impacts": props.get_active_floor_impacts(),
    }


__all__ = [
    "check_human_substrate_floor",
    "get_human_properties",
    "get_substrate_summary",
    "set_human_properties",
]
