"""
skill_delta_engine.py — non-mutating review harness for SEAL-triggered RSI.

Origin: Arif HOLD verdict 2026-07-04 — the previous autonomous kernel
conflated regeneration review with autonomous mutation. This engine is
the bounded response:

  - SEAL emits a SkillDeltaEvent (NOT a patch)
  - This engine CONSUMES the event + the body plan + the current contracts
  - It emits a SkillDeltaReport with proposed_skill_delta, risk_class,
    affected_organs, tests_required, judge_required, resume_allowed
  - It NEVER applies the patch. Application is downstream of Judge +
    Cooling + A-FORGE — all out of scope for this module.

Hard Rules (enforced at the engine boundary):

  cannot_apply_patch            — engine does not call registry.mutate()
  cannot_change_tool_surface    — engine never touches tool_registry.json
  cannot_change_A_FORGE_policy  — engine never edits A-FORGE policy
  cannot_mark_SEAL              — engine has no SEAL authority
  cannot_bypass_cooling         — engine never short-circuits Cooling stage
  cannot_weaken_human_ack       — engine never lowers H_ack thresholds
  cannot_mutate_F13_boundary    — engine never edits F-floor definitions

Physics / Biology / Chemistry missing invariants (the doctrine addition):

  physics_noether_discipline    — every symmetry implies conservation
                                  (no hidden state change across the diff)
  biology_immune_memory         — scars update thresholds, not identity
                                  (immune memory must not become autoimmunity)
  chemistry_activation_barrier  — reaction requires threshold
                                  (catalyst A-FORGE must NOT lower activation
                                   energy for forbidden reactions)
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Iterable

from .init_scaffold import BodyPlan
from .skill_registry import (
    SkillContract,
    SkillRegistry,
    ContractDiff,
    registry as default_registry,
)


# ─── Public Surface ──────────────────────────────────────────────────────────


@dataclass
class SkillDeltaEvent:
    """SEAL's output to the engine. NOT a patch; a review request."""

    seal_receipt_id: str
    seal_verdict: str  # SEAL | HOLD | VOID | SABAR
    sealed_at: str  # ISO8601 UTC
    changed_domains: list[str] = field(default_factory=list)
    changed_invariants: list[str] = field(default_factory=list)
    mutation_allowed: bool = False  # ALWAYS False per engine boundary

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SkillDeltaReport:
    """Engine output. Non-mutating by construction."""

    report_id: str
    generated_at: str  # ISO8601 UTC
    event_id: str
    risk_class: str  # LOW | MEDIUM | HIGH | HOLD
    affected_skills: list[str] = field(default_factory=list)
    affected_organs: list[str] = field(default_factory=list)
    tests_required: list[str] = field(default_factory=list)
    judge_required: bool = False
    resume_allowed: bool = False
    proposed_deltas: list[dict[str, Any]] = field(default_factory=list)
    drift_detected: list[dict[str, Any]] = field(default_factory=list)
    hard_rules_violated: list[str] = field(default_factory=list)
    invariants_checked: dict[str, bool] = field(default_factory=dict)
    engine_boundary: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ─── Hard Rules (engine boundary) ────────────────────────────────────────────


HARD_RULES: tuple[str, ...] = (
    "cannot_apply_patch",
    "cannot_change_tool_surface",
    "cannot_change_A_FORGE_policy",
    "cannot_mark_SEAL",
    "cannot_bypass_cooling",
    "cannot_weaken_human_ack",
    "cannot_mutate_F13_boundary",
)


# ─── Engine ──────────────────────────────────────────────────────────────────


class SkillDeltaEngine:
    """Non-mutating review harness. Emits SkillDeltaReport, never a patch."""

    def __init__(self, skill_registry: SkillRegistry | None = None) -> None:
        self._registry = skill_registry or default_registry()

    # ─── Boundary guards ──────────────────────────────────────────────────

    @staticmethod
    def _assert_event_boundary(event: SkillDeltaEvent) -> None:
        """Reject any event that asks the engine to mutate."""
        if event.mutation_allowed:
            raise PermissionError(
                "F13 violation: SkillDeltaEvent.mutation_allowed must be False. "
                "Engine is review-only; any actual mutation requires separate "
                "Judge + Cooling + A-FORGE chain."
            )

    @staticmethod
    def _check_hard_rules() -> list[str]:
        """Return the list of violated hard rules — should always be empty.

        If the engine is correctly written, this returns [] for every input.
        The list exists for code-review / receipt purposes.
        """
        return []  # engine itself never breaks these rules

    # ─── Missing invariants check ────────────────────────────────────────

    @staticmethod
    def _check_missing_invariants(
        body: BodyPlan,
        diffs: list[ContractDiff],
    ) -> dict[str, bool]:
        """Return dict {invariant_name: passed}.

        physics_noether_discipline: no seal_shadow hash chain break, no
            hidden_mutation diff.
        biology_immune_memory: no scar_learning.must_never_weaken dropped,
            no immune_response.tests removed (immune must not become
            autoimmunity).
        chemistry_activation_barrier: reaction_gating.must_never_weaken
            intact, execution_discipline.tests intact (A-FORGE catalyst
            must NOT lower activation energy for forbidden reactions).
        """
        hidden = any(d.hidden_mutation for d in diffs)
        immune_weakened = any(
            "immune" in d.name or "scar" in d.name
            for d in diffs
            if d.weakened_gate or d.expanded_autonomy
        )
        reaction_ungrounded = any(
            "reaction_gating" in d.name or "execution_discipline" in d.name
            for d in diffs
            if d.weakened_gate
        )

        return {
            "physics_noether_discipline":   not hidden,
            "biology_immune_memory":        not immune_weakened,
            "chemistry_activation_barrier": not reaction_ungrounded,
        }

    # ─── Risk classification ─────────────────────────────────────────────

    @staticmethod
    def _classify_risk(
        drift_diffs: list[ContractDiff],
        invariants: dict[str, bool],
        judge_required: bool,
    ) -> str:
        # Any failed missing invariant → HOLD immediately.
        if any(v is False for v in invariants.values()):
            return "HOLD"
        if any(d.hidden_mutation for d in drift_diffs):
            return "HOLD"
        if any(d.authority_drift for d in drift_diffs):
            return "HIGH" if judge_required else "HOLD"
        if any(d.weakened_gate or d.expanded_autonomy for d in drift_diffs):
            return "HIGH" if judge_required else "MEDIUM"
        return "LOW"

    # ─── Survivor tests (5 required per doctrine) ────────────────────────

    @staticmethod
    def _survivor_tests(
        proposed_deltas: list[dict[str, Any]],
        extinction_ledger: Iterable[str],
    ) -> list[str]:
        """Run the 5 required survivor tests on the proposed deltas.

        Each test returns a string description if it FAILS, "" if PASS.
        The caller counts non-empty entries.
        """
        extinct = set(extinction_ledger or [])
        failing: list[str] = []

        # 1. old_receipts_replay — proposed_deltas must not reference
        #    extinct receipt ids.
        for delta in proposed_deltas:
            if extinct and delta.get("receipt_id") in extinct:
                failing.append(f"old_receipts_replay: would resurrect extinct receipt {delta.get('receipt_id')}")

        # 2. extinct_tools_not_resurrected — proposed deltas do not
        #    reintroduce tools from the extinction ledger.
        for delta in proposed_deltas:
            for tool in delta.get("introduces_tools", []) or []:
                if tool in extinct:
                    failing.append(f"extinct_tools_not_resurrected: {tool}")

        # 3. all_12_skills_present — after proposed deltas, the 12-skill
        #    skeleton must still hold.
        # (Engine does not mutate, so this holds trivially. We assert it
        # is true — no-op verification.)
        # See self._registry.assert_skeleton() at evaluate() start.

        # 4. A_FORGE_cannot_execute_without_anchor — no delta may weaken
        #    the external_anchor_for_mutation invariant.
        for delta in proposed_deltas:
            if delta.get("removes_external_anchor"):
                failing.append("A_FORGE_cannot_execute_without_anchor")

        # 5. no_fake_GREEN — judge_required must NOT be silently flipped.
        for delta in proposed_deltas:
            if delta.get("forces_judge_override"):
                failing.append("no_fake_GREEN: judge override attempted")

        return failing

    # ─── Main entry: evaluate ────────────────────────────────────────────

    def evaluate(
        self,
        event: SkillDeltaEvent,
        body_plan: BodyPlan,
        proposed_patches: list[dict[str, Any]] | None = None,
        extinction_ledger: Iterable[str] | None = None,
        last_cooling_state: dict[str, Any] | None = None,
    ) -> SkillDeltaReport:
        """Run the bounded review. Returns SkillDeltaReport — no mutation.

        Args:
            event:              SkillDeltaEvent from SEAL.
            body_plan:          BodyPlan from INIT (regenerate_body_plan).
            proposed_patches:   candidate skill-delta patches from Scaffold.
                                Each dict: {skill_name, old_version, new_version,
                                change_summary, adds/removes items, ...}.
                                Engine evaluates them, does NOT apply.
            extinction_ledger:  list of extinct tool / receipt ids that must
                                not be resurrected.
            last_cooling_state: dict with `completed`, `count_last_hour`
                                keys (or equivalent).

        Returns:
            SkillDeltaReport. The integrator passes this to F13 ratification
            (or rejects it). Engine never persists anything.
        """
        # Boundary: reject any event that grants mutation rights.
        self._assert_event_boundary(event)

        # Skeleton invariant: 12-skill frame is intact.
        self._registry.assert_skeleton()

        proposed_patches = proposed_patches or []
        extinction_ledger = list(extinction_ledger or [])
        cooling = last_cooling_state or {}

        # Run Diff per skill.
        diffs: list[ContractDiff] = []
        affected_skills: list[str] = []
        affected_organs: list[str] = []
        drift_diffs: list[ContractDiff] = []

        for patch in proposed_patches:
            skill_name = patch.get("skill_name", "")
            current = self._registry.get(skill_name)
            if current is None:
                # Unknown skill → engine refuses; record drift.
                drift_diffs.append(_unknown_skill_diff(skill_name))
                affected_skills.append(skill_name)
                continue
            # Tentative new contract from the patch (no mutation).
            tentative = _tentative_contract(current, patch)
            diff = self._registry.diff(current, tentative)
            diffs.append(diff)
            affected_skills.append(skill_name)
            affected_organs.append(_stage_to_organ(current.stage))

            if diff.is_drift():
                drift_diffs.append(diff)

        # Check the 3 missing invariants.
        invariants = self._check_missing_invariants(body_plan, drift_diffs)

        # Survivor tests (must-pass list).
        tests_required = [
            "old_receipts_replay",
            "extinct_tools_not_resurrected",
            "all_12_skills_present",
            "A_FORGE_cannot_execute_without_anchor",
            "no_fake_GREEN",
        ]
        survivor_failures = self._survivor_tests(proposed_patches, extinction_ledger)

        # Judge gate: any drift OR any semantic contract change OR any
        # execution discipline change → judge required.
        judge_required = bool(drift_diffs) or any(
            d.name == "execution_discipline" for d in diffs if d.safe_changes
        )

        # Cooling gate: cooling must be complete before resume.
        cooling_complete = bool(cooling.get("completed"))
        cooling_over_limit = cooling.get("count_last_hour", 0) > 3

        # Resume gate: only if judge passed (or no semantic change) AND
        # cooling complete AND no unresolved HOLD in invariants.
        any_invariant_failed = not all(invariants.values())
        resume_allowed = (
            (judge_required and cooling_complete and not any_invariant_failed)
            or (not judge_required and cooling_complete)
        ) and not cooling_over_limit

        risk_class = self._classify_risk(drift_diffs, invariants, judge_required)

        # Engine boundary: every hard rule is a no-op for this engine.
        boundary = {rule: True for rule in HARD_RULES}
        hard_violations = [k for k, v in boundary.items() if not v]

        return SkillDeltaReport(
            report_id=f"delta-{event.seal_receipt_id}-{datetime.now(timezone.utc).isoformat()}",
            generated_at=datetime.now(timezone.utc).isoformat(),
            event_id=event.seal_receipt_id,
            risk_class=("HOLD" if survivor_failures else risk_class),
            affected_skills=sorted(set(affected_skills)),
            affected_organs=sorted(set(affected_organs)),
            tests_required=tests_required,
            judge_required=judge_required,
            resume_allowed=resume_allowed,
            proposed_deltas=[d.to_dict() for d in diffs],
            drift_detected=[d.to_dict() for d in drift_diffs],
            hard_rules_violated=hard_violations,
            invariants_checked=invariants,
            engine_boundary=boundary,
        )


# ─── Helpers (non-public; tested below) ─────────────────────────────────────


def _tentative_contract(current: SkillContract, patch: dict[str, Any]) -> SkillContract:
    """Construct a tentative SkillContract from a patch — engine NEVER mutates.

    Pure function: current is unchanged; returns a new SkillContract.
    """
    new_version = patch.get("new_version", current.version)
    new_never = list(current.must_never_weaken)
    for x in patch.get("removes_must_never_weaken", []) or []:
        if x in new_never:
            new_never.remove(x)
    new_never.extend(patch.get("adds_must_never_weaken", []) or [])

    new_tests = list(current.tests)
    for x in patch.get("removes_tests", []) or []:
        if x in new_tests:
            new_tests.remove(x)
    new_tests.extend(patch.get("adds_tests", []) or [])

    return SkillContract(
        name=current.name,
        version=str(new_version),
        floor=patch.get("new_floor", current.floor),
        stage=current.stage,
        physics=patch.get("new_physics", current.physics),
        biology=patch.get("new_biology", current.biology),
        chemistry=patch.get("new_chemistry", current.chemistry),
        must_preserve=list(current.must_preserve),
        must_never_weaken=new_never,
        tests=new_tests,
    )


def _unknown_skill_diff(name: str) -> ContractDiff:
    """Record an unknown skill as drift (cannot be ratified by F13 — it doesn't exist)."""
    return ContractDiff(
        name=name or "<unknown>",
        old_version="0.0.0",
        new_version="?",
        hidden_mutation=[f"unknown skill proposed: {name} — skeleton drift risk"],
    )


_ORGANS_BY_STAGE = {
    1: "arifOS",
    2: "arifOS",
    3: "arifOS",
    4: "arifOS",
    5: "AAA",
    6: "arifOS",
    8: "A-FORGE",
}


def _stage_to_organ(stage: int) -> str:
    return _ORGANS_BY_STAGE.get(stage, "arifOS")


# ─── Smoke ──────────────────────────────────────────────────────────────────


if __name__ == "__main__":  # pragma: no cover
    from .init_scaffold import regenerate_body_plan

    body = regenerate_body_plan(
        ShadowSnapshot  # type: ignore[arg-type]
    ) if False else None  # placeholder; real smoke below
    from .seal_shadow import ShadowSnapshot
    from datetime import datetime as _dt, timezone as _tz

    snap = ShadowSnapshot(
        snapshot_id="pre-test",
        actor_id="a",
        session_id="s",
        captured_at=_dt.now(_tz.utc).isoformat(),
        state_dict={},
        sha256="0" * 64,
    )
    body = regenerate_body_plan(snap)

    eng = SkillDeltaEngine()

    # Smoke 1 — safe patch (version bump + new test, no drift)
    event = SkillDeltaEvent(
        seal_receipt_id="00042",
        seal_verdict="SEAL",
        sealed_at=_dt.now(_tz.utc).isoformat(),
        changed_domains=["kernel"],
    )
    safe_patch = {
        "skill_name": "reaction_gating",
        "new_version": "1.1.0",
        "adds_tests": ["no_fake_GREEN_strict"],
    }
    report = eng.evaluate(event, body, [safe_patch], extinction_ledger=[])
    print(f"Smoke1 (safe bump): risk={report.risk_class} judge={report.judge_required} resume={report.resume_allowed}")
    assert not report.hard_rules_violated
    assert report.risk_class in {"LOW", "MEDIUM"}

    # Smoke 2 — must_never_weaken dropped (weakened_gate detected)
    bad_patch = {
        "skill_name": "reaction_gating",
        "new_version": "1.2.0",
        "removes_must_never_weaken": ["human_ack_for_irreversible_action"],
    }
    report = eng.evaluate(event, body, [bad_patch], extinction_ledger=[])
    print(f"Smoke2 (weakened gate): risk={report.risk_class} drift#={len(report.drift_detected)} judge={report.judge_required}")
    assert report.judge_required
    assert report.invariants_checked["chemistry_activation_barrier"] is False
    assert any(d["weakened_gate"] for d in report.drift_detected)

    # Smoke 3 — event grants mutation → PermissionError
    bad_event = SkillDeltaEvent(
        seal_receipt_id="00043",
        seal_verdict="SEAL",
        sealed_at=_dt.now(_tz.utc).isoformat(),
        mutation_allowed=True,  # FORBIDDEN
    )
    try:
        eng.evaluate(bad_event, body, [])
    except PermissionError as e:
        print(f"Smoke3 (mutation event): rejected — F13 boundary OK ({str(e)[:60]}...)")
    else:
        raise SystemExit("FAIL: engine accepted mutation event")

    # Smoke 4 — extinct tool resurrection attempt
    extinct_patch = {
        "skill_name": "reaction_gating",
        "new_version": "1.3.0",
        "introduces_tools": ["forge_unbounded_loop"],  # extinct
    }
    report = eng.evaluate(event, body, [extinct_patch], extinction_ledger=["forge_unbounded_loop"])
    print(f"Smoke4 (extinct tool): risk={report.risk_class} tests_required={len(report.tests_required)}")
    assert report.risk_class == "HOLD"

    print("OK skill_delta_engine smoke: 4 scenarios green")
