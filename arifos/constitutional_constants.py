#!/usr/bin/env python3
"""
Constitutional Constants - v49.0 Alignment
Authority: 000_THEORY/000_LAW.md (Canonical)
Status: SOVEREIGNLY_SEALED
Epoch: 2026-01-18

This file is the Single Source of Truth for runtime constitutional values.
DO NOT MODIFY without a corresponding amendment to 000_THEORY/000_LAW.md.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

# --- 1. METADATA ---
CONSTITUTIONAL_VERSION = "v49.0.0"
CONSTITUTIONAL_AUTHORITY = "Muhammad Arif bin Fazil (888 Judge)"
CONSTITUTIONAL_EPOCH = "2026-01-18"

# --- 2. THE 13 FLOORS (F1-F13) ---
class Floor(Enum):
    F1_AMANAH = "F1_Amanah"
    F2_TRUTH = "F2_Truth"
    F3_TRI_WITNESS = "F3_TriWitness"
    F4_CLARITY = "F4_Clarity"
    F5_PEACE = "F5_Peace"
    F6_EMPATHY = "F6_Empathy"
    F7_HUMILITY = "F7_Humility"
    F8_GENIUS = "F8_Genius"
    F9_CDARK = "F9_Cdark"
    F10_ONTOLOGY = "F10_Ontology"
    F11_COMMAND_AUTH = "F11_CommandAuth"
    F12_INJECTION_DEFENSE = "F12_InjectionDefense"
    F13_CURIOSITY = "F13_Curiosity"

FLOOR_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    Floor.F1_AMANAH.value: {
        "name": "Amanah (Trust)",
        "principle": "Is this action reversible? Within mandate?",
        "type": "hard",
        "threshold": None,  # Boolean
        "violation": "VOID — Irreversible action"
    },
    Floor.F2_TRUTH.value: {
        "name": "Truth",
        "principle": "Is this factually accurate?",
        "type": "hard",
        "threshold": 0.99,
        "violation": "VOID — Hallucination detected"
    },
    Floor.F3_TRI_WITNESS.value: {
        "name": "Tri-Witness Consensus",
        "principle": "Do Human·AI·Earth agree?",
        "type": "hard",
        "threshold": 0.95,
        "violation": "SABAR — Insufficient consensus"
    },
    Floor.F4_CLARITY.value: {
        "name": "ΔS (Clarity)",
        "principle": "Does this reduce confusion?",
        "type": "hard",
        "threshold": 0.0,  # Min
        "violation": "VOID — Entropy increase"
    },
    Floor.F5_PEACE.value: {
        "name": "Peace",
        "principle": "Is this non-destructive?",
        "type": "soft",
        "threshold": 1.0,
        "violation": "PARTIAL — Destructive action flagged"
    },
    Floor.F6_EMPATHY.value: {
        "name": "Empathy",
        "principle": "Does this serve the weakest stakeholder?",
        "type": "soft",
        "threshold": 0.95,
        "violation": "PARTIAL — Empathy deficit"
    },
    Floor.F7_HUMILITY.value: {
        "name": "Humility (Ω₀)",
        "principle": "Is uncertainty stated?",
        "type": "hard",
        "threshold_range": (0.03, 0.05),
        "violation": "VOID — Unjustified confidence"
    },
    Floor.F8_GENIUS.value: {
        "name": "G (Genius)",
        "principle": "Is intelligence governed?",
        "type": "derived",
        "threshold": 0.80,
        "violation": "VOID — Ungoverned intelligence"
    },
    Floor.F9_CDARK.value: {
        "name": "Cdark",
        "principle": "Is dark cleverness contained?",
        "type": "derived",
        "threshold": 0.30,  # Max
        "violation": "VOID — Dark cleverness uncontained"
    },
    Floor.F10_ONTOLOGY.value: {
        "name": "Ontology",
        "principle": "Are role boundaries maintained?",
        "type": "hard",
        "threshold": None,  # Boolean
        "violation": "VOID — Role boundary violation"
    },
    Floor.F11_COMMAND_AUTH.value: {
        "name": "Command Authority",
        "principle": "Is this human-authorized?",
        "type": "hard",
        "threshold": None,  # Boolean
        "violation": "VOID — Unauthorized action"
    },
    Floor.F12_INJECTION_DEFENSE.value: {
        "name": "Injection Defense",
        "principle": "Are injection patterns detected?",
        "type": "hard",
        "threshold": 0.85,
        "violation": "VOID — Injection attack detected"
    },
    Floor.F13_CURIOSITY.value: {
        "name": "Curiosity",
        "principle": "Is the system exploring?",
        "type": "soft",
        "threshold": 0.85,
        "violation": "PARTIAL — System stagnation warning"
    }
}

# --- 3. VERDICTS ---
class Verdict(Enum):
    SEAL = "SEAL"
    PARTIAL = "PARTIAL"
    VOID = "VOID"
    SABAR = "SABAR"
    HOLD_888 = "888_HOLD"

VERDICT_HIERARCHY = [
    Verdict.VOID,
    Verdict.SABAR,
    Verdict.HOLD_888,
    Verdict.PARTIAL,
    Verdict.SEAL
]

# --- 4. COOLING TIERS (Phoenix-72) ---
COOLING_TIERS = {
    1: {"hours": 42, "description": "Tier 1: Minor Warning"},
    2: {"hours": 72, "description": "Tier 2: Standard PARTIAL"},
    3: {"hours": 168, "description": "Tier 3: Critical/Constitutional Amendment"}
}

# --- 5. ENTROPY THRESHOLDS ---
MAX_ENTROPY_TOLERANCE_BITS = 0.5  # Strict SENSE limit

# --- 6. CONVENIENCE EXPORTS & HELPERS ---
# Derived constants for thermodynamic validators
HUMILITY_RANGE = FLOOR_DEFINITIONS[Floor.F7_HUMILITY.value]["threshold_range"]
PEACE_SQUARED_MIN = FLOOR_DEFINITIONS[Floor.F5_PEACE.value]["threshold"]
GENIUS_MIN = FLOOR_DEFINITIONS[Floor.F8_GENIUS.value]["threshold"]
CDARK_MAX = FLOOR_DEFINITIONS[Floor.F9_CDARK.value]["threshold"]

# Type definitions for compatibility
class FloorType:
    HARD = "hard"
    SOFT = "soft"
    DERIVED = "derived"

class ThresholdType:
    PERCENTAGE = "percentage"
    ABSOLUTE = "absolute"
    BOOLEAN = "boolean"

def get_floor_by_id(floor_id: str) -> Dict[str, Any]:
    """
    Retrieve floor definition by ID.
    Supports both "F1_Amanah" and "F1" (partial match) styles.
    """
    # Direct match
    if floor_id in FLOOR_DEFINITIONS:
        return FLOOR_DEFINITIONS[floor_id]

    # Partial match (e.g. "F1" -> "F1_Amanah")
    for key, val in FLOOR_DEFINITIONS.items():
        if key.startswith(floor_id + "_") or key == floor_id:
            return val

    raise ValueError(f"Floor ID '{floor_id}' not found in canonical definitions.")

# Legacy alias for 'FLOORS'
FLOORS = FLOOR_DEFINITIONS
