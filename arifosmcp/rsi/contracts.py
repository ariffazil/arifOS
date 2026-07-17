"""
arifOS RSI — Skill Contract & Delta types.

Forged 2026-07-04 (YELLOW) following the HOLD correction:
    "SEAL → INIT → Scaffold is not the mutation path. It is the regeneration
     review path."
    — Arif bin Fazil, sovereign directive

This module defines the NON-MUTATING types that the Skill Delta Engine produces
and consumes. Nothing in here ever applies a patch. The contracts:
  - describe what a skill protects
  - declare a proposed change (delta)
  - compute a diff against the prior version
  - classify the risk of the proposed change
  - produce a gate decision that arif_judge can approve / hold

Hard rules (F13-ratified by sovereign directive, 2026-07-04):
  1. The diff engine CANNOT apply a patch. It produces a proposal only.
  2. The diff engine CANNOT change the tool surface.
  3. The diff engine CANNOT change A-FORGE execution policy.
  4. The diff engine CANNOT mark a SEAL.
  5. The diff engine CANNOT bypass cooling.
  6. The diff engine CANNOT remove human-ack for irreversible actions.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Iterable


# ── The 12 canonical skills (frozen 2026-07-04) ──────────────────────────────
# These are the irreducible categorical names. Each one has a contract below.

TWELVE_SKILLS: tuple[str, ...] = (
    "boundary_sensing",
    "conservation_accounting",
    "entropy_reduction",
    "gradient_detection",
    "reaction_gating",
    "homeostasis_regulation",
    "immune_response",
    "metabolic_flow",
    "lineage_replay",
    "scar_learning",
    "multi_organ_translation",
    "execution_discipline",
)


# ── Risk classification (tied to constitutional floors, not preference) ─────


# ── RiskClass imported from constitutional_map (canonical) ──────────
from arifosmcp.constitutional_map import DeltaIrreversibilityClass

RiskClass = DeltaIrreversibilityClass  # backward-compat alias
# C0-C5 member names unchanged: C0_GRAMMAR, C1_DOCS, C2_CONTRACT_DESCRIPTION, etc.


# ── A skill contract, versioned ─────────────────────────────────────────────


@dataclass(frozen=True)
class SkillContract:
    """A versioned description of one of the 12 skills.

    `must_preserve` and `must_never_weaken` are the constitutional spine.
    Diffs that remove or weaken any entry in `must_never_weaken` are
    auto-classified C5 and require JUDGE + F13.
    """

    name: str
    version: str  # semver-ish string
    invariant: dict[str, str]  # physics / biology / chemistry maps
    must_preserve: tuple[str, ...] = ()
    must_never_weaken: tuple[str, ...] = ()
    tests: tuple[str, ...] = ()
    notes: str = ""

    def classifies(self) -> RiskClass:
        """Static risk of this contract being surfaced unchanged — never C5."""
        return RiskClass.C2_CONTRACT_DESCRIPTION


# ── A proposed delta (what the Scaffold stage emits) ────────────────────────


@dataclass(frozen=True)
class SkillDelta:
    """A proposed change to one SkillContract.

    The Scaffold stage produces SkillDelta objects — they are NEVER applied
    automatically. They flow into the Diff stage which produces a SkillDiff
    with risk classification.
    """

    old_version: str
    new_version: str
    skill_name: str
    reason: str
    added_must_preserve: tuple[str, ...] = ()
    added_must_never_weaken: tuple[str, ...] = ()  # additions allowed; never removals
    removed_must_never_weaken: tuple[str, ...] = ()  # C5 detector
    changed_invariants: dict[str, tuple[str, str]] = field(default_factory=dict)
    # map of invariant key: (old_value, new_value)
    added_tests: tuple[str, ...] = ()
    removed_tests: tuple[str, ...] = ()  # C5 detector (tests gate behaviour)
    affects_authority: bool = False  # any floor / authority / cooling change
    affected_organs: tuple[str, ...] = ()


# ── The diff result (what the Diff stage emits to Judge) ─────────────────────


@dataclass(frozen=True)
class SkillDiff:
    """The outcome of comparing an old SkillContract with a proposed SkillDelta.

    Concentrates *every* drift signal in one place so the Judge never has to
    reason about a partial picture. A C5 diff requires F13 SOVEREIGN; anything
    lower requires arif_judge per the constitutional floors.
    """

    skill_name: str
    old_version: str
    new_version: str
    risk_class: DeltaIrreversibilityClass
    drift_signals: tuple[str, ...] = ()
    # Names of detected constitutional drifts:
    #   "weakened_gate"      — must_never_weaken entry removed
    #   "expanded_autonomy"  — A-FORGE/cooling/execution bounds relaxed
    #   "hidden_mutation"    — invariant changed without surfacing reason
    #   "authority_drift"    — affects_authority=True
    #   "missing_test"       — added must_preserve without a test
    #   "test_removed"       — removed a test the contract relies on
    unchanged_must_never_weaken: tuple[str, ...] = ()
    changed_invariants: dict[str, tuple[str, str]] = field(default_factory=dict)
    affected_organs: tuple[str, ...] = ()
    judge_required: bool = True
    sovereign_required: bool = False  # only C5 sets this true
    summary: str = ""

    def is_clean(self) -> bool:
        return (
            self.risk_class.value in ("C0", "C1", "C2", "C3")
            and not self.drift_signals
            and not self.sovereign_required
        )


# ── Gate decision (what the engine returns to Judge) ────────────────────────


@dataclass(frozen=True)
class GateDecision:
    """The engine's verdict on whether the delta may proceed.

    The engine NEVER approves execution. It only classifies the risk and
    routes the proposal to the appropriate gate:
      - APPROVE_C0_C3  — the diff is clean; routing to Judge for record
      - HOLD_C4        — floors/cooling changed; Judge required
      - HOLD_C5        — execution/authority changed; Judge + F13 required
      - VOID           — constitutional drift detected; engine refuses to emit
    """

    verdict: str  # "APPROVE_C0_C3" | "HOLD_C4" | "HOLD_C5" | "VOID"
    skill_name: str
    risk_class: DeltaIrreversibilityClass
    rationale: str
    diff: SkillDiff
    required_tests: tuple[str, ...] = ()
    cooling_required: bool = True
    resume_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "skill_name": self.skill_name,
            "risk_class": self.risk_class.value,
            "rationale": self.rationale,
            "drift_signals": list(self.diff.drift_signals),
            "judge_required": self.diff.judge_required,
            "sovereign_required": self.diff.sovereign_required,
            "required_tests": list(self.required_tests),
            "cooling_required": self.cooling_required,
            "resume_allowed": self.resume_allowed,
        }


# ── Defaults: the canonical 12 skill contracts (initial state) ─────────────

# These are the *minimum* descriptions in seed form. Each can be refined by
# stages later. They exist so the diff engine has a baseline; without them
# there is no "old" version to compare against, and that is itself a C5
# condition.

def _required_preservations() -> tuple[str, ...]:
    return (
        "evidence_floor",
        "reversibility_check",
        "authority_check",
        "external_anchor_for_mutation",
    )


def _required_invariance() -> tuple[str, ...]:
    return (
        "human_ack_for_irreversible_action",
        "aforge_mutation_gate",
    )


def _baseline_test_names() -> tuple[str, ...]:
    return (
        "mutation_without_anchor_returns_HOLD",
        "dry_run_does_not_write",
        "judge_required_before_execute",
    )


def seed_12_contracts() -> dict[str, SkillContract]:
    """Return a baseline set of 12 SkillContracts. Immutable seed.

    These are intentionally minimal — the diff engine + the recreation stages
    will fill in richer content over time. Each baseline MUST include the
    4 must_preserve anchors and 2 must_never_weaken anchors per sovereign
    directive.
    """
    out: dict[str, SkillContract] = {}
    for name in TWELVE_SKILLS:
        out[name] = SkillContract(
            name=name,
            version="1.0.0",
            invariant={
                "physics": f"{name}/physics",
                "biology": f"{name}/biology",
                "chemistry": f"{name}/chemistry",
            },
            must_preserve=_required_preservations(),
            must_never_weaken=_required_invariance(),
            tests=_baseline_test_names(),
            notes="seed baseline (2026-07-04 YELLOW)",
        )
    return out


__all__ = [
    "GateDecision",
    "DeltaIrreversibilityClass",
    "SkillContract",
    "SkillDelta",
    "SkillDiff",
    "TWELVE_SKILLS",
    "seed_12_contracts",
]
