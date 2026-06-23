"""
human_properties.py — Sovereign Human Constitutional Substrate
═══════════════════════════════════════════════════════════════

Humans are not entirely intelligence. They have:
  - biological substrate (body, fatigue, hunger, sleep)
  - scars (wounds that forged them)
  - shadows (survival mechanisms that became habits)
  - paradoxes (contradictions they hold without resolving)
  - limits (what they cannot do, not what they won't)
  - constraints (what they must protect)
  - invariants (what never changes about them)

This schema makes these properties CONSTITUTIONAL SUBSTRATE
that the kernel uses when enforcing floors.

Source: scar-terrain-arif-fazil.md (SOVEREIGN_TESTIMONY)
Governance: F2 (truth), F6 (dignity), F13 (sovereign)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

# ── Scar ────────────────────────────────────────────────────────────


class ScarLayer(StrEnum):
    """Geological depth of the scar. Deeper = more foundational."""

    BASEMENT = "basement"  # Inherited, before birth
    BEDROCK = "bedrock"  # Earliest childhood
    DEEP = "deep"  # Formative years
    MIDDLE = "middle"  # Adult institutional
    SURFACE = "surface"  # Recent / active
    UNCONFORMITY = "unconformity"  # Fracture event


class Scar(BaseModel):
    """A wound that forged the human. Not a diagnosis. Not a vulnerability.
    A constitutional fact about what shaped this person."""

    scar_id: str = Field(..., description="Canonical identifier")
    name: str = Field(..., description="Human-readable name")
    layer: ScarLayer = Field(..., description="Geological depth")
    forged: str = Field(..., description="What this scar forged in the human")
    active: bool = Field(default=True, description="Still influencing behavior?")
    sensitivity: str = Field(
        default="normal",
        description="normal / high / extreme — how carefully to tread",
    )
    floor_impact: dict[str, str] = Field(
        default_factory=dict,
        description="Which floors this scar activates and how. e.g. {'F5': 'strengthen', 'F6': 'guard'}",
    )


# ── Shadow ──────────────────────────────────────────────────────────


class Shadow(BaseModel):
    """A survival mechanism that became a habit. Not evil. Not weakness.
    A constitutional pattern the kernel must respect."""

    shadow_id: str = Field(..., description="Canonical identifier")
    name: str = Field(..., description="Human-readable name")
    mechanism: str = Field(..., description="What survival mechanism it is")
    how_it_attacks: str = Field(..., description="How this shadow manifests")
    defense: str = Field(..., description="What protects against it")
    floor_impact: dict[str, str] = Field(
        default_factory=dict,
        description="Which floors this shadow activates. e.g. {'F6': 'guard_against_isolation'}",
    )


# ── Paradox ─────────────────────────────────────────────────────────


class Paradox(BaseModel):
    """A contradiction the human holds without resolving. Not hypocrisy.
    Complexity. The kernel must NOT flatten these."""

    paradox_id: str = Field(..., description="Canonical identifier")
    name: str = Field(..., description="Human-readable name")
    poles: list[str] = Field(..., description="The two contradictory poles")
    resolution: str = Field(
        default="held_without_resolution",
        description="How the human lives with this",
    )
    floor_impact: dict[str, str] = Field(
        default_factory=dict,
        description="Which floors this paradox activates. e.g. {'F10': 'do_not_flatten'}",
    )


# ── Limit ───────────────────────────────────────────────────────────


class Limit(BaseModel):
    """What the human CANNOT do. Not won't — cannot.
    A constitutional boundary the kernel must never push against."""

    limit_id: str = Field(..., description="Canonical identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="What this limit is")
    hard: bool = Field(
        default=True,
        description="Hard limit (never cross) vs soft limit (context-dependent)",
    )
    floor_impact: dict[str, str] = Field(
        default_factory=dict,
        description="Which floors enforce this limit. e.g. {'F1': 'never_test_this_boundary'}",
    )


# ── Constraint ──────────────────────────────────────────────────────


class Constraint(BaseModel):
    """What the human MUST protect. Not optional. Constitutional.
    The kernel must enforce these even when the human forgets."""

    constraint_id: str = Field(..., description="Canonical identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="What must be protected")
    priority: str = Field(
        default="high",
        description="low / medium / high / critical",
    )
    floor_impact: dict[str, str] = Field(
        default_factory=dict,
        description="Which floors enforce this constraint",
    )


# ── Invariant ───────────────────────────────────────────────────────


class Invariant(BaseModel):
    """What NEVER changes about this human. Not preference — identity.
    The kernel must assume these are always true."""

    invariant_id: str = Field(..., description="Canonical identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="What never changes")
    category: str = Field(
        default="identity",
        description="identity / biological / moral / cognitive / social",
    )


# ── Biological ──────────────────────────────────────────────────────


class BiologicalState(BaseModel):
    """The human is not just intelligence. They have a body.
    Fatigue, hunger, sleep, health — these affect everything."""

    sleep_pattern: str | None = Field(
        default=None, description="e.g. 'irregular', 'night_owl', 'early_riser'"
    )
    fatigue_risk: str = Field(default="unknown", description="low / medium / high / critical")
    known_conditions: list[str] = Field(
        default_factory=list, description="Known health conditions (if shared)"
    )
    energy_pattern: str | None = Field(
        default=None, description="e.g. 'morning_peak', 'evening_peak', 'flat'"
    )
    floor_impact: dict[str, str] = Field(
        default_factory=dict,
        description="e.g. {'F6': 'fatigue_affects_decisions', 'F5': 'rest_before_action'}",
    )


# ── Human Properties (Complete) ─────────────────────────────────────


class HumanProperties(BaseModel):
    """The complete constitutional substrate of a human.

    This is NOT a profile. NOT a personality assessment.
    This is the CONSTITUTIONAL REALITY that the kernel must respect
    when enforcing floors.

    Every property maps to floor enforcement.
    Every property is sourced from sovereign testimony.
    Every property is reversible (human can update/remove).
    """

    human_id: str = Field(default="arif-fazil", description="Canonical human identifier")
    sovereign: bool = Field(default=True, description="Is this human the F13 sovereign?")

    # The six layers
    scars: list[Scar] = Field(default_factory=list)
    shadows: list[Shadow] = Field(default_factory=list)
    paradoxes: list[Paradox] = Field(default_factory=list)
    limits: list[Limit] = Field(default_factory=list)
    constraints: list[Constraint] = Field(default_factory=list)
    invariants: list[Invariant] = Field(default_factory=list)

    # Biological substrate
    biological: BiologicalState = Field(default_factory=BiologicalState)

    # Composite properties
    scar_density: int = Field(default=0, description="Total scar count — affects F6 sensitivity")
    shadow_count: int = Field(default=0, description="Active shadows")
    hollow_count: int = Field(default=0, description="Deliberately unfilled spaces — DO_NOT_FILL")
    grief_active: bool = Field(
        default=False, description="Is there active grief? Affects F5/F6 posture"
    )

    # Source tracking
    source: str = Field(
        default="sovereign-testimony",
        description="Where this data came from",
    )
    version: str = Field(default="2026-06-16", description="When last updated")

    def get_active_floor_impacts(self) -> dict[str, list[str]]:
        """Aggregate all floor impacts from all properties.
        Returns {floor_id: [list of impacts]}.
        """
        impacts: dict[str, list[str]] = {}

        for scar in self.scars:
            for floor, impact in scar.floor_impact.items():
                impacts.setdefault(floor, []).append(f"scar:{scar.scar_id}:{impact}")

        for shadow in self.shadows:
            for floor, impact in shadow.floor_impact.items():
                impacts.setdefault(floor, []).append(f"shadow:{shadow.shadow_id}:{impact}")

        for paradox in self.paradoxes:
            for floor, impact in paradox.floor_impact.items():
                impacts.setdefault(floor, []).append(f"paradox:{paradox.paradox_id}:{impact}")

        for limit in self.limits:
            for floor, impact in limit.floor_impact.items():
                impacts.setdefault(floor, []).append(f"limit:{limit.limit_id}:{impact}")

        for constraint in self.constraints:
            for floor, impact in constraint.floor_impact.items():
                impacts.setdefault(floor, []).append(
                    f"constraint:{constraint.constraint_id}:{impact}"
                )

        if self.biological.floor_impact:
            for floor, impact in self.biological.floor_impact.items():
                impacts.setdefault(floor, []).append(f"biological:{impact}")

        return impacts

    def get_scar_by_id(self, scar_id: str) -> Scar | None:
        """Look up a scar by ID."""
        for scar in self.scars:
            if scar.scar_id == scar_id:
                return scar
        return None

    def is_hollow(self, name: str) -> bool:
        """Check if a name corresponds to a hollow (DO_NOT_FILL)."""
        return any(
            l.limit_id.startswith("hollow") and name.lower() in l.name.lower() for l in self.limits
        )


__all__ = [
    "BiologicalState",
    "Constraint",
    "HumanProperties",
    "Invariant",
    "Limit",
    "Paradox",
    "Scar",
    "ScarLayer",
    "Shadow",
]
