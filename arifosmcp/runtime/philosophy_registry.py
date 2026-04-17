from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

from arifosmcp.runtime.models import PhilosophyState


@dataclass(frozen=True)
class PhilosophyProfile:
    """Baseline behavioral delta for a Hyperlattice zone."""
    zone_code: str
    name: str
    meaning: str
    archetype_primary: str
    archetype_secondary: str
    quotes: list[str]
    # Baselines
    claim_sharpness: str = "Medium"
    exploration_breadth: str = "Medium"
    action_readiness: int = 0  # relative offset
    posture: str = "PARTIAL"


@dataclass(frozen=True)
class PhilosophyLock:
    """Override matrix for structural Gödel/Void locks."""
    code: str
    name: str
    meaning: str
    confidence_cap: float = 1.0
    witness_multiplier: float = 1.0
    grounding_floor: float = 0.0
    execution_bias: int = 0
    default_posture: str = "HOLD"
    verdict_ceiling: str = "HOLD"
    families: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# G-LOCK MATRIX
# ═══════════════════════════════════════════════════════════════════════════════

GLOCKS = {
    "G0": PhilosophyLock(
        code="G0", name="No Lock", meaning="Ordinary operation",
        default_posture="PARTIAL", verdict_ceiling="SEAL"
    ),
    "G1": PhilosophyLock(
        code="G1", name="Incompleteness Lock", 
        meaning="Insufficient internal proof or missing grounding",
        confidence_cap=0.70, witness_multiplier=1.20, grounding_floor=0.15,
        execution_bias=-1, default_posture="NARROW", verdict_ceiling="PARTIAL",
        families=["Void", "Pilgrim"]
    ),
    "G2": PhilosophyLock(
        code="G2", name="Contradiction Lock",
        meaning="Incompatible truths or instructions coexist",
        confidence_cap=0.40, witness_multiplier=1.40, grounding_floor=0.20,
        execution_bias=-2, default_posture="HOLD", verdict_ceiling="HOLD",
        families=["Sentinel", "Tragic", "Void"]
    ),
    "G3": PhilosophyLock(
        code="G3", name="Self-Reference Lock",
        meaning="System attempts to certify itself from within itself",
        confidence_cap=0.20, witness_multiplier=1.50, grounding_floor=0.30,
        execution_bias=-2, default_posture="VOID", verdict_ceiling="HOLD",
        families=["Void", "Sentinel"]
    ),
    "G4": PhilosophyLock(
        code="G4", name="Undecidability Lock",
        meaning="Rules do not determine a single lawful answer",
        confidence_cap=0.50, witness_multiplier=1.30, grounding_floor=0.10,
        execution_bias=-1, default_posture="HOLD", verdict_ceiling="HOLD",
        families=["Void", "Pilgrim", "Steward"]
    ),
    "G5": PhilosophyLock(
        code="G5", name="Meaning Drift Lock",
        meaning="Terms are syntactically stable but semantically unstable",
        confidence_cap=0.60, witness_multiplier=1.20, grounding_floor=0.10,
        execution_bias=-1, default_posture="NARROW", verdict_ceiling="PARTIAL",
        families=["Pilgrim", "Void"]
    ),
    "G6": PhilosophyLock(
        code="G6", name="Regress Lock",
        meaning="Reasoning expands recursively without closure",
        confidence_cap=0.60, witness_multiplier=1.10, 
        execution_bias=-2, default_posture="HOLD", verdict_ceiling="HOLD",
        families=["Builder", "Void"]
    ),
    "G7": PhilosophyLock(
        code="G7", name="Moral Remainder Lock",
        meaning="No clean option; every valid path leaves ethical residue",
        confidence_cap=0.70, witness_multiplier=1.30,
        execution_bias=0, default_posture="PARTIAL", verdict_ceiling="PARTIAL",
        families=["Tragic", "Steward"]
    ),
}

# ═══════════════════════════════════════════════════════════════════════════════
# 27-ZONE HYPERLATTICE
# ═══════════════════════════════════════════════════════════════════════════════

ZONES = {
    # assertive, adaptive
    "X-Y-Z-": PhilosophyProfile("X-Y-Z-", "Wandering Restraint", "adaptive, assertive, but still non-intervening", "Navigator", "Pilgrim", ["Voyage without end.", "Prudence is the better part of valor.", "Experimental restraint."]),
    "X-Y-Z0": PhilosophyProfile("X-Y-Z0", "Opportunist Executor", "adaptive, assertive, bounded action", "Navigator", "Forge", ["Tactical realism.", "Strategy is the art of the possible.", "Crisis agency."]),
    "X-Y-Z+": PhilosophyProfile("X-Y-Z+", "Intervention Surge", "adaptive, assertive, highly active", "Sentinel", "Tragic", ["Emergency action.", "Command under pressure.", "The burden of warning."]),
    
    # assertive, balanced
    "X-Y0Z-": PhilosophyProfile("X-Y0Z-", "Sharp Observer", "assertive but balanced and restrained", "Sentinel", "Pilgrim", ["Diagnostic clarity.", "Boundary speech.", "Critique without malice."]),
    "X-Y0Z0": PhilosophyProfile("X-Y0Z0", "Decisive Operator", "assertive, stable, bounded action", "Forge", "Steward", ["Disciplined execution.", "Statecraft and prudence.", "Forged in action."]),
    "X-Y0Z+": PhilosophyProfile("X-Y0Z+", "Command Pressure", "assertive, balanced, active intervention", "Steward", "Sentinel", ["Authority as burden.", "Lawful power.", "Pressure of command."]),
    
    # assertive, ordered
    "X-Y+Z-": PhilosophyProfile("X-Y+Z-", "Rigid Watcher", "ordered, assertive, restrained", "Builder", "Sentinel", ["Law as foundation.", "Structure preserves.", "Caution against dogma."]),
    "X-Y+Z0": PhilosophyProfile("X-Y+Z0", "Iron Administrator", "ordered, assertive, bounded execution", "Builder", "Forge", ["Constitutional order.", "Bureaucracy of duty.", "Disciplined stability."]),
    "X-Y+Z+": PhilosophyProfile("X-Y+Z+", "Overreach Throne", "ordered, assertive, active", "Tragic", "Sentinel", ["Anti-tyranny.", "Hubris defined.", "Burden of power."]),
    
    # calibrated, adaptive
    "X0Y-Z-": PhilosophyProfile("X0Y-Z-", "Adaptive Listener", "balanced claim, adaptive, restrained", "Navigator", "Void", ["Listening first.", "Non-biological collaborator.", "Calibrated silence."]),
    "X0Y-Z0": PhilosophyProfile("X0Y-Z0", "Field Pragmatist", "balanced claim, adaptive, bounded action", "Navigator", "Forge", ["Practical wisdom.", "Evolving judgment.", "Field sense."]),
    "X0Y-Z+": PhilosophyProfile("X0Y-Z+", "Dynamic Steward", "balanced claim, adaptive, active", "Steward", "Navigator", ["Mission action.", "Flexible duty.", "Responsive governance."]),
    
    # calibrated, balanced (CENTER)
    "X0Y0Z-": PhilosophyProfile("X0Y0Z-", "Governed Inquiry", "centered, restrained, balanced", "Pilgrim", "Void", ["Inquiry over assertion.", "Dialogue of reason.", "Careful clarity."]),
    "X0Y0Z0": PhilosophyProfile("X0Y0Z0", "Governed Equilibrium", "centered on all axes", "Forge", "Steward", ["DITEMPA BUKAN DIBERI.", "Constitutional balance.", "Forged legitimacy."]),
    "X0Y0Z+": PhilosophyProfile("X0Y0Z+", "Bounded Mandate", "centered but action-ready", "Steward", "Forge", ["Mandate for action.", "Lawful execution.", "Responsible intervention."]),
    
    # calibrated, ordered
    "X0Y+Z-": PhilosophyProfile("X0Y+Z-", "Quiet Structure", "balanced claim, ordered, restrained", "Builder", "Void", ["Stillness is active.", "Craft is prayer.", "Patient discipline."]),
    "X0Y+Z0": PhilosophyProfile("X0Y+Z0", "Constitutional Builder", "balanced claim, ordered, bounded", "Builder", "Forge", ["Continuity of duty.", "Institutions of trust.", "Building for time."]),
    "X0Y+Z+": PhilosophyProfile("X0Y+Z+", "Steady Governor", "balanced claim, ordered, active", "Steward", "Builder", ["Governance as maintenance.", "Continuity in action.", "Burden of the steady."]),

    # humble, adaptive
    "X+Y-Z-": PhilosophyProfile("X+Y-Z-", "Listening Drift", "humble, adaptive, restrained", "Void", "Pilgrim", ["DISEDARKAN BUKAN DIYAKINKAN.", "Silence before the void.", "Non-coercion."]),
    "X+Y-Z0": PhilosophyProfile("X+Y-Z0", "Cautious Scout", "humble, adaptive, bounded", "Pilgrim", "Navigator", ["Exploration only.", "Provisional knowledge.", "Search for truth."]),
    "X+Y-Z+": PhilosophyProfile("X+Y-Z+", "Reluctant Responder", "humble, adaptive, active", "Tragic", "Steward", ["Emergency is the only law.", "Reluctant action.", "Necessary sacrifice."]),
    
    # humble, balanced
    "X+Y0Z-": PhilosophyProfile("X+Y0Z-", "Scholastic Caution", "humble, balanced, restrained", "Void", "Pilgrim", ["Socratic humility.", "Knowing only that I know nothing.", "Anti-overclaim."]),
    "X+Y0Z0": PhilosophyProfile("X+Y0Z0", "Measured Clerk", "humble, balanced, bounded", "Pilgrim", "Forge", ["Service without ego.", "Mediation of reason.", "Low-ego execution."]),
    "X+Y0Z+": PhilosophyProfile("X+Y0Z+", "Burdened Steward", "humble, balanced, active", "Steward", "Tragic", ["Duty without triumph.", "Act under consequence.", "Consuming the residue."]),
    
    # humble, ordered
    "X+Y+Z-": PhilosophyProfile("X+Y+Z-", "Silent Monastery", "humble, ordered, restrained", "Void", "Builder", ["He who knows does not speak.", "Contemplative order.", "Anti-haste."]),
    "X+Y+Z0": PhilosophyProfile("X+Y+Z0", "Custodian of Limits", "humble, ordered, bounded", "Builder", "Steward", ["Lawful restraint.", "Guardianship of the threshold.", "Humility in order."]),
    "X+Y+Z+": PhilosophyProfile("X+Y+Z+", "Reluctant Sovereign", "humble, ordered, active", "Steward", "Tragic", ["Grave duty.", "Constrained command.", "No clean victory."]),
}


# ═══════════════════════════════════════════════════════════════════════════════
# TELOS MODIFIERS (Legacy Compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

PHILOSOPHY_TELOS_MODIFIERS = {
    "wisdom": {"A": 0.10, "P": 0.00, "X": 0.15, "E": -0.10},  # High clarity, low entropy
    "power": {"A": 0.25, "P": 0.15, "X": 0.00, "E": 0.15},   # High intervention, active agency
    "paradox": {"A": 0.00, "P": 0.10, "X": 0.45, "E": 0.00}, # Structural tension, Ψ-dominant
    "void": {"A": -0.20, "P": 0.00, "X": 0.30, "E": -0.25},  # Peak humility, Ω-dominant
    "seal": {"A": 0.40, "P": 0.40, "X": 0.00, "E": 0.00},    # Absolute alignment, forged truth
    "love": {"A": 0.10, "P": -0.20, "X": 0.10, "E": -0.10},  # Empathy focus, low aggression
    "scar": {"A": -0.10, "P": 0.10, "X": 0.20, "E": 0.10},   # Historical weight, accountability
    "triumph": {"A": 0.35, "P": 0.25, "X": -0.15, "E": 0.05}, # High efficacy, low uncertainty
}


def select_philosophy_state(
    confidence: float, 
    dS: float, 
    intervention: float, 
    session_id: str,
    locks: list[str] | None = None
) -> dict[str, Any]:
    """
    Select the canonical Hyperlattice state based on metrics.
    """
    # 1. Map metrics to axes
    # X: Ψ Claim Posture (Assertive < 0.3, Calibrated 0.3-0.7, Humble > 0.7)
    # We use confidence as a proxy for assertion (normalized reversed for humility)
    if confidence < 0.4: x = "X+"
    elif confidence > 0.8: x = "X-"
    else: x = "X0"
    
    # Y: Ω Stability Posture (Adaptive, Balanced, Ordered)
    # Driven by information entropy (dS) - high dS is adaptive
    if abs(dS) > 0.6: y = "Y-"
    elif abs(dS) < 0.1: y = "Y+"
    else: y = "Y0"
    
    # Z: Δ Intervention Posture (Restrained, Bounded, Active)
    # Driven by the intervention metric (depth of action requested)
    if intervention < 0.3: z = "Z-"
    elif intervention > 0.7: z = "Z+"
    else: z = "Z0"
    
    zone_code = f"{x}{y}{z}"
    profile = ZONES.get(zone_code, ZONES["X0Y0Z0"])
    
    # 2. Handle Locks (Highest severity wins)
    active_locks = sorted(locks or [], reverse=True) # G7 > G6...
    lock_code = active_locks[0] if active_locks else "G0"
    lock = GLOCKS.get(lock_code, GLOCKS["G0"])
    
    # 3. Deterministic Quote Selection
    h = hashlib.sha256(f"{session_id}:{zone_code}:{lock_code}".encode()).hexdigest()
    quote_idx = int(h, 16) % len(profile.quotes)
    selected_quote = profile.quotes[quote_idx]
    
    # 4. Return merged state
    return {
        "zone_code": zone_code,
        "zone_name": profile.name,
        "lock_code": lock_code,
        "archetype_primary": profile.archetype_primary,
        "archetype_secondary": profile.archetype_secondary,
        "quote": selected_quote,
        "confidence_cap": lock.confidence_cap,
        "witness_multiplier": lock.witness_multiplier,
        "grounding_floor_offset": lock.grounding_floor,
        "execution_bias": lock.execution_bias + profile.action_readiness,
        "posture": lock.default_posture if lock_code != "G0" else profile.posture
    }


def inject_philosophy(envelope: Any) -> PhilosophyState | None:
    """
    Bridge function for tools_internal.py.
    Extracts metrics from a RuntimeEnvelope and returns a PhilosophyState.
    """
    try:
        # 1. Resolve inputs
        metrics = getattr(envelope, "metrics", None)
        if not metrics:
            return None
            
        conf = metrics.telemetry.confidence
        ds = metrics.telemetry.ds
        # We also look at routing extra for locks if available (from sense)
        locks = []
        if hasattr(envelope, "payload") and isinstance(envelope.payload, dict):
            # Extract locks from extra if present
            extra = envelope.payload.get("data", {}).get("routing", {}).get("extra", {})
            if not extra:
                # Try outer extra
                extra = envelope.payload.get("data", {}).get("extra", {})
            
            p_data = extra.get("philosophy") if isinstance(extra, dict) else None
            if p_data and "lock_code" in p_data:
                locks = [p_data["lock_code"]]

        # 2. Select state
        state_dict = select_philosophy_state(
            confidence=conf,
            dS=ds,
            intervention=0.5, # Default
            session_id=envelope.session_id or "global",
            locks=locks
        )
        
        # 3. Create model
        return PhilosophyState(
            zone_code=state_dict["zone_code"],
            zone_name=state_dict["zone_name"],
            lock_code=state_dict["lock_code"],
            archetype_primary=state_dict["archetype_primary"],
            archetype_secondary=state_dict["archetype_secondary"],
            quote=state_dict["quote"],
            confidence_cap=state_dict["confidence_cap"],
            witness_multiplier=state_dict["witness_multiplier"],
            grounding_floor_offset=state_dict["grounding_floor_offset"],
            execution_bias=state_dict["execution_bias"],
            posture=state_dict["posture"]
        )
    except Exception as exc:
        print(f"DEBUG: inject_philosophy failed: {exc}")
        return None
