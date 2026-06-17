"""
risk.py — Risk assessment types and classifiers.

Risk = blast_radius × reversibility × human_ack.
"""

from __future__ import annotations

from enum import Enum


class BlastRadius(str, Enum):
    """How far an action's effects propagate."""

    NONE = "NONE"
    LOCAL = "LOCAL"
    SESSION = "SESSION"
    FEDERATION = "FEDERATION"
    EXTERNAL = "EXTERNAL"


class Reversibility(str, Enum):
    """Whether an action can be undone."""

    REVERSIBLE = "REVERSIBLE"
    PARTIAL = "PARTIAL"
    IRREVERSIBLE = "IRREVERSIBLE"


# Actions that cannot be undone
IRREVERSIBLE_ACTIONS: frozenset[str] = frozenset(
    {
        "DEPLOY",
        "PUBLISH",
        "DELETE",
        "SPEND",
        "SIGN",
        "GRANT_ACCESS",
        "CREDENTIAL_CHANGE",
        "CONSTITUTION_CHANGE",
    }
)


# Actions that reach outside local scope
EXTERNAL_ACTIONS: frozenset[str] = frozenset(
    {
        "MUTATE_EXTERNAL",
        "DEPLOY",
        "PUBLISH",
        "SPEND",
        "GRANT_ACCESS",
    }
)


def classify_blast_radius(action_class: str) -> BlastRadius:
    """Heuristic blast-radius classification for an action class."""
    if action_class in EXTERNAL_ACTIONS:
        return BlastRadius.EXTERNAL
    if action_class in ("MUTATE_LOCAL", "MUTATE_EXTERNAL"):
        return BlastRadius.LOCAL
    if action_class in ("COMPUTE", "PROPOSE"):
        return BlastRadius.SESSION
    return BlastRadius.NONE


def classify_reversibility(action_class: str) -> Reversibility:
    """Heuristic reversibility classification for an action class."""
    if action_class in IRREVERSIBLE_ACTIONS:
        return Reversibility.IRREVERSIBLE
    if action_class in ("MUTATE_LOCAL", "MUTATE_EXTERNAL"):
        return Reversibility.PARTIAL
    return Reversibility.REVERSIBLE
