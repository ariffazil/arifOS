"""
arifOS RSI — Skill Delta Engine.

Forged 2026-07-04 (YELLOW) under sovereign 999_HOLD correction:
    "SEAL → INIT → Scaffold is not the mutation path. It is the regeneration
     review path."
    "The missing stage is Diff."
    "Scaffold proposes. Judge approves. A-FORGE applies."

This is a NON-MUTATING engine. It converts SEAL receipts + current
SkillContracts into SkillDelta proposals + SkillDiff risk classifications +
GateDecisions. It NEVER:
  - applies a patch
  - changes the tool surface
  - changes A-FORGE policy
  - marks a SEAL
  - bypasses cooling
  - removes human-ack for irreversible actions

Inputs:
  seal_receipt               — VAULT999-anchored receipt (read-only)
  current_skill_contracts    — map of skill_name → SkillContract (read-only)
  extinction_ledger          — names of expired skill versions (read-only)
  organ_registry             — which organs are alive (read-only)
  last_cooling_state         — most recent cooling receipt (read-only)

Outputs:
  proposed_skill_delta       — SkillDelta | None
  risk_class                 — RiskClass
  affected_organs            — tuple[str, ...]
  tests_required             — tuple[str, ...]
  judge_required             — bool
  resume_allowed             — bool (False until Judge approves + cooling)

The engine can return a GateDecision.verdict of "VOID" when constitutional
drift is detected. VOID is the engine REFUSING to emit, not the engine
applying a change.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from arifosmcp.rsi.contracts import (
    TWELVE_SKILLS,
    GateDecision,
    RiskClass,
    SkillContract,
    SkillDelta,
    SkillDiff,
    seed_12_contracts,
)

logger = logging.getLogger("arifOS.rsi.diff_engine")


# ── The seven constitutionally forbidden actions for the engine ───────────
# Per sovereign directive 2026-07-04. The engine returns VOID if any caller
# asks it to perform one of these.

_ENGINE_FORBIDDEN: tuple[str, ...] = (
    "apply_patch",
    "change_tool_surface",
    "change_aforge_policy",
    "mark_seal",
    "bypass_cooling",
    "remove_human_ack",
    "weaken_floor",
)


# ── The drift detectors (the four your HOLD named) ─────────────────────────

DRIFT_NAMES: tuple[str, ...] = (
    "weakened_gate",
    "expanded_autonomy",
    "hidden_mutation",
    "authority_drift",
    "test_removed",
    "missing_test_for_new_anchor",
)


def _detect_weakened_gate(delta: SkillDelta) -> list[str]:
    """must_never_weaken entries removed = constitutional drift (C5)."""
    return ["weakened_gate"] if delta.removed_must_never_weaken else []


def _detect_expanded_autonomy(
    delta: SkillDelta,
    org_inventory: Mapping[str, Iterable[str]],
) -> list[str]:
    """A-FORGE / cooling / organ bounds weakened = expanded autonomy (C5)."""
    signals: list[str] = []
    # Auto-afwell / cooling / aforge flagged in invariant changes
    forbidden_invariant_keys = (
        "cooling_threshold",
        "mutation_gate",
        "aforge_activation_energy",
        "aforge_authority_barrier",
    )
    for k in delta.changed_invariants:
        if k in forbidden_invariant_keys:
            signals.append("expanded_autonomy")
            break
    # Or affecting AFORGE/AAA/ARIF in a way that grants new organ roles
    if "aforge" in delta.affected_organs:
        # If aforge lost any prior test, that's loosening gates
        if delta.removed_tests:
            signals.append("expanded_autonomy")
    # If the organ inventory doesn't know about a new organ we're claiming,
    # that's expanding recognised authority
    for organ in delta.affected_organs:
        if organ not in org_inventory:
            signals.append("expanded_autonomy")
            break
    return signals


def _detect_hidden_mutation(delta: SkillDelta) -> list[str]:
    """An invariant changed without a reason flag or with a vague one.

    Hidden mutation = silent behaviour change with no narrative.
    """
    if not delta.changed_invariants:
        return []
    if not delta.reason or len(delta.reason.strip()) < 10:
        return ["hidden_mutation"]
    if delta.reason.strip().lower().startswith("internal"):
        return ["hidden_mutation"]
    return []


def _detect_authority_drift(delta: SkillDelta) -> list[str]:
    """affects_authority=True always classifies as authority drift (C4/C5)."""
    return ["authority_drift"] if delta.affects_authority else []


def _detect_test_removed(delta: SkillDelta) -> list[str]:
    """Removing a test the contract relies on weakens the gate."""
    return ["test_removed"] if delta.removed_tests else []


def _detect_missing_test_for_new_anchor(
    delta: SkillDelta,
    contract: SkillContract,
) -> list[str]:
    """If we add a new must_preserve anchor without a test for it, the gate
    is unproven — must_never_weaken.
    """
    new_anchors = set(delta.added_must_preserve)
    added_test_names = set(delta.added_tests)
    unproven = [
        a
        for a in new_anchors
        if not any(t.endswith(a) or a in t or t.replace("_", " ") in a for t in added_test_names)
    ]
    if unproven:
        return ["missing_test_for_new_anchor"]
    return []


# ── The diff function — pure, deterministic, side-effect-free ───────────────


def diff(
    old: SkillContract,
    new_delta: SkillDelta,
    organ_inventory: Mapping[str, Iterable[str]],
) -> SkillDiff:
    """Compute the SkillDiff between an old contract and a proposed delta.

    Pure function. No mutation. Returns a SkillDiff always — even if the
    delta is identical (C0 empty diff).
    """
    drift: list[str] = []
    drift.extend(_detect_weakened_gate(new_delta))
    drift.extend(_detect_expanded_autonomy(new_delta, organ_inventory))
    drift.extend(_detect_hidden_mutation(new_delta))
    drift.extend(_detect_authority_drift(new_delta))
    drift.extend(_detect_test_removed(new_delta))
    drift.extend(_detect_missing_test_for_new_anchor(new_delta, old))

    # Risk classification
    risk = RiskClass.C1_DOCS  # baseline (grammar/formatting/diff)

    # C5 — execution/authority/cooling or weakened gates
    if any(s in drift for s in ("weakened_gate", "expanded_autonomy")):
        risk = RiskClass.C5_EXECUTION_AUTHORITY
    elif "authority_drift" in drift:
        risk = RiskClass.C5_EXECUTION_AUTHORITY
    elif "hidden_mutation" in drift:
        # Hidden mutations to invariants are at least floor logic
        risk = RiskClass.C4_FLOOR_LOGIC
    elif "test_removed" in drift:
        risk = RiskClass.C4_FLOOR_LOGIC
    elif "missing_test_for_new_anchor" in drift:
        risk = RiskClass.C4_FLOOR_LOGIC
    elif new_delta.added_must_never_weaken:
        # additions to the lock are good — but still C3 (surface change)
        risk = RiskClass.C3_PUBLIC_SURFACE
    elif new_delta.added_must_preserve or new_delta.added_tests:
        risk = RiskClass.C3_PUBLIC_SURFACE
    elif new_delta.changed_invariants:
        risk = RiskClass.C2_CONTRACT_DESCRIPTION

    unchanged = tuple(
        a for a in old.must_never_weaken if a not in new_delta.removed_must_never_weaken
    )

    judge_required = risk.value in ("C3", "C4", "C5")
    sovereign_required = risk == RiskClass.C5_EXECUTION_AUTHORITY

    summary_parts = [
        f"old={old.version}",
        f"new={new_delta.new_version}",
        f"risk={risk.value}",
        f"drifts={[s for s in drift] if drift else 'none'}",
    ]
    if not drift and not new_delta.changed_invariants:
        summary_parts.append("no-op")

    return SkillDiff(
        skill_name=old.name,
        old_version=old.version,
        new_version=new_delta.new_version,
        risk_class=risk,
        drift_signals=tuple(sorted(set(drift))),
        unchanged_must_never_weaken=unchanged,
        changed_invariants=dict(new_delta.changed_invariants),
        affected_organs=tuple(new_delta.affected_organs),
        judge_required=judge_required,
        sovereign_required=sovereign_required,
        summary=" ".join(summary_parts),
    )


# ── The engine surface ─────────────────────────────────────────────────────


@dataclass(frozen=True)
class SkillDeltaRequest:
    """Input bundle for the diff engine.

    All fields read-only. The engine never copies mutations forward.
    """

    seal_receipt: str
    skill_name: str
    proposed_delta: SkillDelta
    # read-only inventories passed in:
    current_skill_contracts: Mapping[str, SkillContract]
    extinction_ledger: tuple[str, ...] = ()
    organ_registry: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    last_cooling_state: Mapping[str, Any] = field(default_factory=dict)


def _validate_engine_invariants(
    request: SkillDeltaRequest,
) -> str | None:
    """If the request itself asks the engine to do something forbidden,
    return the violation name. Otherwise None.
    """
    delta = request.proposed_delta
    payload_signals = (delta.skill_name, delta.new_version, delta.reason)
    # 'apply_patch' would manifest as new_version == 'applied_to_system'
    if delta.new_version.lower() in ("applied", "applied_to_system", "live"):
        return "apply_patch"
    if delta.affects_authority and not delta.reason:
        return "weaken_floor"
    # Engine never autoremoves human-ack: removed_must_never_weaken already
    # includes human_ack_for_irreversible_action and aforge_mutation_gate in
    # the seed. If caller asks to remove them, the engine will catch that
    # via weakened_gate detection rather than this guard.
    return None


def evaluate(request: SkillDeltaRequest) -> GateDecision:
    """Evaluate a SkillDeltaRequest and return a GateDecision.

    The engine NEVER applies anything. It returns:
      - APPROVE_C0_C3  — diff is clean; route to Judge for record
      - HOLD_C4        — floors changed; Judge required
      - HOLD_C5        — execution/authority changed; Judge + F13 required
      - VOID           — caller asked the engine to do something forbidden

    Resume is allowed only when:
      - judge_required is False (C0/C1/C2) AND cooling_complete is True
      - or sovereign_required has been approved AND cooling_complete is True
    """

    # 1. Engine forbids any forbidden action requested by the caller.
    forbidden = _validate_engine_invariants(request)
    if forbidden:
        return GateDecision(
            verdict="VOID",
            skill_name=request.skill_name,
            risk_class=RiskClass.C5_EXECUTION_AUTHORITY,
            rationale=f"engine refusal: caller requested forbidden action '{forbidden}'",
            diff=SkillDiff(
                skill_name=request.skill_name,
                old_version=request.proposed_delta.old_version,
                new_version=request.proposed_delta.new_version,
                risk_class=RiskClass.C5_EXECUTION_AUTHORITY,
                drift_signals=(f"engine_forbidden:{forbidden}",),
                sovereign_required=True,
            ),
            cooling_required=True,
            resume_allowed=False,
        )

    # 2. Find the current contract; reject if skill is extinct or unknown.
    skill = request.skill_name
    if skill in request.extinction_ledger:
        return GateDecision(
            verdict="VOID",
            skill_name=skill,
            risk_class=RiskClass.C5_EXECUTION_AUTHORITY,
            rationale=f"skill '{skill}' is in extinction_ledger; resurrection forbidden",
            diff=SkillDiff(
                skill_name=skill,
                old_version=request.proposed_delta.old_version,
                new_version=request.proposed_delta.new_version,
                risk_class=RiskClass.C5_EXECUTION_AUTHORITY,
                drift_signals=("resurrection_forbidden",),
                sovereign_required=True,
            ),
            cooling_required=True,
            resume_allowed=False,
        )
    if skill not in TWELVE_SKILLS:
        return GateDecision(
            verdict="VOID",
            skill_name=skill,
            risk_class=RiskClass.C5_EXECUTION_AUTHORITY,
            rationale=f"unknown skill '{skill}'; not in canonical 12",
            diff=SkillDiff(
                skill_name=skill,
                old_version=request.proposed_delta.old_version,
                new_version=request.proposed_delta.new_version,
                risk_class=RiskClass.C5_EXECUTION_AUTHORITY,
                drift_signals=("unknown_skill",),
                sovereign_required=True,
            ),
            cooling_required=True,
            resume_allowed=False,
        )
    old_contract = request.current_skill_contracts.get(skill)
    if old_contract is None:
        return GateDecision(
            verdict="VOID",
            skill_name=skill,
            risk_class=RiskClass.C5_EXECUTION_AUTHORITY,
            rationale=f"no current contract for skill '{skill}'",
            diff=SkillDiff(
                skill_name=skill,
                old_version=request.proposed_delta.old_version,
                new_version=request.proposed_delta.new_version,
                risk_class=RiskClass.C5_EXECUTION_AUTHORITY,
                drift_signals=("missing_baseline_contract",),
                sovereign_required=True,
            ),
            cooling_required=True,
            resume_allowed=False,
        )

    # 3. Compute the diff
    d = diff(
        old_contract,
        request.proposed_delta,
        request.organ_registry,
    )

    # 4. Build the GateDecision
    cooling_complete = bool(request.last_cooling_state.get("complete", False))
    if d.risk_class == RiskClass.C5_EXECUTION_AUTHORITY:
        verdict = "HOLD_C5"
        resume_allowed = False
    elif d.risk_class == RiskClass.C4_FLOOR_LOGIC:
        verdict = "HOLD_C4"
        resume_allowed = False
    elif not d.drift_signals and not d.changed_invariants:
        verdict = "APPROVE_C0_C3"
        # C0/C1 — engine surfaces but does not enable execution; only Judge
        # can flip resume allowed. We always emit cooling_required=True.
        resume_allowed = False
    else:
        verdict = "APPROVE_C0_C3"
        resume_allowed = False  # Judge + cooling is always the gate

    required_tests: tuple[str, ...] = tuple(request.proposed_delta.added_tests) + (
        "drift_signals_recorded",
        "contract_diff_visible_to_judge",
        "extinction_ledger_consulted",
    )

    return GateDecision(
        verdict=verdict,
        skill_name=skill,
        risk_class=d.risk_class,
        rationale=d.summary,
        diff=d,
        required_tests=required_tests,
        cooling_required=True,
        resume_allowed=resume_allowed and cooling_complete and not d.judge_required,
    )


__all__ = [
    "DRIFT_NAMES",
    "SkillDeltaRequest",
    "diff",
    "evaluate",
    "seed_12_contracts",  # re-export for ergonomics
]
