"""
ART blast — blast radius mapping and action class utilities.

Maps between:
  - kernel_envelope.ActionClass → art reflex action_class strings
  - kernel_envelope.BlastRadius → art reflex blast_radius strings

Two axes, two purposes. ActionClass = permission-level.
BlastRadius = scope-of-damage. ART consumes both.

DITEMPA BUKAN DIBERI — Blast mapping is forged, not configured.
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════════
# ActionClass → art reflex string
# ═══════════════════════════════════════════════════════════════════════
# Maps the canonical 7-class ActionClass ladder to art.py's 3-string
# action_class field (observe / mutate / execute).

ACTION_CLASS_TO_ART: dict[str, str] = {
    "OBSERVE": "observe",
    "ANALYZE": "observe",
    "DRAFT": "mutate",
    "SIMULATE": "mutate",
    "MUTATE": "mutate",
    "EXTERNAL_SIDE_EFFECT": "mutate",
    "IRREVERSIBLE": "mutate",
}


def action_class_to_art_str(ac_value: str) -> str:
    """Convert canonical ActionClass value → art.py action_class string."""
    return ACTION_CLASS_TO_ART.get(ac_value, "observe")


# ═══════════════════════════════════════════════════════════════════════
# BlastRadius → art reflex string
# ═══════════════════════════════════════════════════════════════════════
# Maps BlastRadius enum values to art.py's blast_radius field
# (low / medium / high / unknown).

BLAST_RADIUS_TO_ART: dict[str, str] = {
    "NONE": "low",
    "LOCAL": "low",
    "ACCOUNT": "medium",
    "ORG": "high",
    "PUBLIC": "high",
    "MARKET": "high",
    "SYSTEM": "medium",
    "INFRASTRUCTURE": "high",
    "CIVILIZATIONAL": "high",
    "UNKNOWN": "unknown",
}


def blast_radius_to_art_str(br_value: str) -> str:
    """Convert BlastRadius value → art.py blast_radius string."""
    return BLAST_RADIUS_TO_ART.get(br_value, "unknown")
