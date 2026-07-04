"""
arifOS/runtime/skill_delta_engine.py — Non-mutating skill delta engine.

Forged 2026-07-04 (Skill Delta Engine, ASI-ratified scope).

PURPOSE
═══════
    Convert a SEAL receipt into a *proposed* skill delta — never an applied one.
    SEAL → INIT → Scaffold is the REGENERATION REVIEW PATH, not mutation path.

    Every SEAL that wants its skills regenerated must pass through this engine
    and emerge with a `SkillDeltaProposal`. The engine does not write that
    proposal anywhere. Downstream judges (`arif_judge`) and the existing
    `rsi/event_bus.py` decide what to do with it.

HARD RULES (immutable — enforced by absence)
══════════════════════════════════════════════
    1. cannot_apply_patch           — no `apply_*` function exists.
    2. cannot_change_tool_surface   — never imports tool_registry / public_registry /
                                       constitutional_map / server.py.
    3. cannot_change_A_FORGE_policy — never imports forge_* policy / forge_dry_run.
    4. cannot_mark_SEAL             — never writes VAULT999.
    5. cannot_bypass_cooling        — every output inspects `last_cooling_state`.

A future edit that introduces any of these surfaces is a constitutional
violation, F13 SOVEREIGN. The module is ~200 LOC by design; if it grows
beyond the budget, that is a signal the engine has drifted into mutation.

VOCABULARY REFERENCES (admissibility)
═════════════════════════════════════
    Borrowed as comment-only references, not imports (keeps the engine
    self-contained and AMANAH-friendly):
        - ForgeSkillDenyCode          (kernel/forge_skill_contract.py)
        - ShadowState                 (runtime/cooling_harness.py)
        - RSISTAGES, SealEvent        (rsi/event_bus.py)

STATE MACHINE
═════════════
    DORMANT → TRIGGERED → INVARIANTS_LOADED → DIFFED → RISK_CLASSIFIED
            → JUDGE_REQ → COOLING_REQ → PROPOSAL_EMITTED → COOLED → DORMANT

    Each transition is non-mutating. `propose_skill_delta` walks the chain
    and emits ONE frozen dataclass at the end.

PUBLIC API (intentionally narrow)
═════════════════════════════════
    propose_skill_delta(...)           → SkillDeltaProposal
    attach_to_event_bus(bus)           → wires read-only StageResult hooks
                                           into an existing SealEventBus
                                           (opt-in, never called on import).
    _self_check()                      → runs the 5-test acceptance gate.

5-TEST ACCEPTANCE GATE
══════════════════════
    test_no_mutation
    test_diff_detects_weakened_gate
    test_extinct_skill_blocked
    test_cooling_blocks_runaway
    test_judge_required_on_semantic_change

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Iterable, Mapping

logger = logging.getLogger("arifOS.runtime.skill_delta_engine")

ENGINE_VERSION = "1.0.0"
PROPOSAL_DOMAIN = "skill_delta_review"

# Hard-rule banner — emitted on every proposal for audit legibility.
HARD_RULES: tuple[str, ...] = (
    "mutation_allowed=False by construction",
    "no apply() function exists in this module",
    "no VAULT999 write path",
    "no tool_registry / public_registry / constitutional_map import",
    "no forge_* policy mutation",
    "cooling state checked on every output",
)


# ── Vocabulary ───────────────────────────────────────────────────────────────


class RiskClass(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class SkillContract:
    """Versioned, deterministic contract for one skill."""

    name: str
    version: str
    invariant: tuple[str, ...] = ()
    must_preserve: tuple[str, ...] = ()
    must_never_weaken: tuple[str, ...] = ()
    tests: tuple[str, ...] = ()


@dataclass(frozen=True)
class SkillDelta:
    """Pure diff between an old and new SkillContract for one skill."""

    name: str
    old_version: str
    new_version: str
    weakening_detected: tuple[str, ...]
    strengthening_detected: tuple[str, ...]
    judge_required: bool
    in_extinction_ledger: bool = False

    def risk_class(self) -> RiskClass:
        if self.in_extinction_ledger:
            return RiskClass.CRITICAL
        if self.weakening_detected:
            return RiskClass.HIGH
        if self.strengthening_detected:
            return RiskClass.LOW
        return RiskClass.MEDIUM


@dataclass(frozen=True)
class CoolingState:
    cooling_complete: bool
    last_cycle_at: str
    cooldown_remaining_s: float
    active_shadows: tuple[str, ...] = ()


@dataclass(frozen=True)
class SkillDeltaProposal:
    delta_id: str
    seal_id: str
    proposed_at: str
    proposed_changes: tuple[SkillDelta, ...]
    affected_organs: tuple[str, ...]
    risk_class: RiskClass
    tests_required: tuple[str, ...]
    judge_required: bool
    cooling_required: bool
    resume_allowed: bool
    extinct_blockers: tuple[str, ...]
    mutation_allowed: bool  # hard-coded False

    def to_dict(self) -> dict[str, Any]:
        return {
            "delta_id": self.delta_id,
            "seal_id": self.seal_id,
            "proposed_at": self.proposed_at,
            "proposed_changes": [
                {
                    "name": d.name,
                    "old_version": d.old_version,
                    "new_version": d.new_version,
                    "weakening_detected": list(d.weakening_detected),
                    "strengthening_detected": list(d.strengthening_detected),
                    "judge_required": d.judge_required,
                    "in_extinction_ledger": d.in_extinction_ledger,
                    "risk_class": d.risk_class().value,
                }
                for d in self.proposed_changes
            ],
            "affected_organs": list(self.affected_organs),
            "risk_class": self.risk_class.value,
            "tests_required": list(self.tests_required),
            "judge_required": self.judge_required,
            "cooling_required": self.cooling_required,
            "resume_allowed": self.resume_allowed,
            "extinct_blockers": list(self.extinct_blockers),
            "mutation_allowed": self.mutation_allowed,
            "engine_version": ENGINE_VERSION,
            "hard_rules": list(HARD_RULES),
        }

    def fingerprint(self) -> str:
        """Deterministic fingerprint. Replay-safe: same semantic proposal →
        same hash. Timestamp drifts by design."""
        payload = self.to_dict()
        payload["proposed_at"] = "<deterministic>"  # strip volatile field
        canonical = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()


# ── Pure-functional proposal engine ─────────────────────────────────────────


def _coerce_contract(raw: Mapping[str, Any], name: str) -> SkillContract:
    return SkillContract(
        name=name,
        version=str(raw.get("version", "0.0.0")),
        invariant=tuple(raw.get("invariant", ())),
        must_preserve=tuple(raw.get("must_preserve", ())),
        must_never_weaken=tuple(raw.get("must_never_weaken", ())),
        tests=tuple(raw.get("tests", ())),
    )


def _diff_pair(old: SkillContract, new: SkillContract, in_extinction: bool) -> SkillDelta:
    weakening = tuple(sorted(set(old.must_never_weaken) - set(new.must_never_weaken)))
    preserve_dropped = tuple(sorted(set(old.must_preserve) - set(new.must_preserve)))
    strengthening = tuple(sorted(set(new.must_never_weaken) - set(old.must_never_weaken)))
    invariant_changed = set(old.invariant) != set(new.invariant)
    semantic = bool(weakening or preserve_dropped or invariant_changed)
    return SkillDelta(
        name=new.name,
        old_version=old.version,
        new_version=new.version,
        weakening_detected=weakening + preserve_dropped,
        strengthening_detected=strengthening,
        judge_required=semantic,
        in_extinction_ledger=in_extinction,
    )


def _required_tests(deltas: tuple[SkillDelta, ...]) -> tuple[str, ...]:
    seed = (
        "replay_receipts",
        "extinct_tools_not_resurrected",
        "all_contract_skills_present",
        "no_fake_green",
    )
    out: list[str] = list(seed)
    seen: set[str] = set(seed)
    for d in deltas:
        token = f"contract:{d.name}@v{d.new_version}"
        if token not in seen:
            out.append(token)
            seen.add(token)
    return tuple(out)


def _affected_organs(
    deltas: tuple[SkillDelta, ...],
    organ_registry: Mapping[str, frozenset[str]],
) -> tuple[str, ...]:
    out: list[str] = []
    seen: set[str] = set()
    for d in deltas:
        for organ, skills in organ_registry.items():
            if d.name in skills and organ not in seen:
                out.append(organ)
                seen.add(organ)
    return tuple(out)


def _worst_risk(deltas: tuple[SkillDelta, ...]) -> RiskClass:
    order = {RiskClass.LOW: 0, RiskClass.MEDIUM: 1, RiskClass.HIGH: 2, RiskClass.CRITICAL: 3}
    worst = RiskClass.LOW
    for d in deltas:
        r = d.risk_class()
        if order[r] > order[worst]:
            worst = r
    return worst


def propose_skill_delta(
    seal_receipt: Mapping[str, Any],
    current_contracts: Mapping[str, Mapping[str, Any]],
    proposed_contracts: Mapping[str, Mapping[str, Any]],
    extinction_ledger: Iterable[str],
    organ_registry: Mapping[str, Iterable[str]],
    last_cooling_state: Mapping[str, Any],
) -> SkillDeltaProposal:
    """Pure function. Same inputs (sans timestamp) → same proposal.

    No disk, registry, vault, or process-state mutation. Caller decides
    whether to persist or display the result.
    """
    # State: DORMANT → TRIGGERED → INVARIANTS_LOADED → DIFFED → ... → EMITTED

    extinction: frozenset[str] = frozenset(extinction_ledger)
    organ_map: dict[str, frozenset[str]] = {k: frozenset(v) for k, v in organ_registry.items()}

    # INVARIANTS_LOADED — coerce contracts; surface asymmetry.
    added = sorted(set(proposed_contracts) - set(current_contracts))
    removed = sorted(set(current_contracts) - set(proposed_contracts))
    asymmetric = bool(added or removed)

    cooling = CoolingState(
        cooling_complete=bool(last_cooling_state.get("cooling_complete", False)),
        last_cycle_at=str(last_cooling_state.get("last_cycle_at", "")),
        cooldown_remaining_s=float(last_cooling_state.get("cooldown_remaining_s", 0.0)),
        active_shadows=tuple(last_cooling_state.get("active_shadows", ())),
    )

    # DIFFED — pairwise comparison across the union of skill names.
    deltas: list[SkillDelta] = []
    for name in sorted(set(current_contracts) | set(proposed_contracts)):
        old = _coerce_contract(current_contracts.get(name, {"version": "0.0.0"}), name)
        new = _coerce_contract(proposed_contracts.get(name, {"version": "0.0.0"}), name)
        delta = _diff_pair(old, new, name in extinction)
        if asymmetric and not delta.judge_required:
            delta = SkillDelta(
                name=delta.name,
                old_version=delta.old_version,
                new_version=delta.new_version,
                weakening_detected=delta.weakening_detected,
                strengthening_detected=delta.strengthening_detected,
                judge_required=True,
                in_extinction_ledger=delta.in_extinction_ledger,
            )
        deltas.append(delta)
    deltas_t = tuple(deltas)

    # RISK_CLASSIFIED — worst across deltas.
    risk = _worst_risk(deltas_t)

    # JUDGE_REQ — any semantic change OR asymmetry OR extinction.
    judge_required = any(d.judge_required for d in deltas_t)

    # COOLING_REQ — incomplete cycle OR active shadows.
    cooling_required = (not cooling.cooling_complete) or bool(cooling.active_shadows)

    # EXTINCT_BLOCKERS — every proposed skill that the extinction ledger forbids.
    extinct_blockers = tuple(sorted(d.name for d in deltas_t if d.in_extinction_ledger))

    # PROPOSAL_EMITTED — frozen dataclass, mutation_allowed locked False.
    tests = _required_tests(deltas_t)
    organs = _affected_organs(deltas_t, organ_map)

    resume_allowed = (
        not extinct_blockers
        and not cooling_required
        and not judge_required
        and risk in (RiskClass.LOW, RiskClass.MEDIUM)
    )

    proposal = SkillDeltaProposal(
        delta_id=f"SDP-{uuid.uuid4().hex[:12]}",
        seal_id=str(seal_receipt.get("seal_id", "<no_seal_id>")),
        proposed_at=datetime.now(UTC).isoformat(),
        proposed_changes=deltas_t,
        affected_organs=organs,
        risk_class=risk,
        tests_required=tests,
        judge_required=judge_required,
        cooling_required=cooling_required,
        resume_allowed=resume_allowed,
        extinct_blockers=extinct_blockers,
        mutation_allowed=False,  # ← hard rule #1
    )

    logger.debug(
        "SkillDeltaProposal emitted: id=%s risk=%s judge=%s cool=%s resume=%s blockers=%s",
        proposal.delta_id,
        proposal.risk_class.value,
        proposal.judge_required,
        proposal.cooling_required,
        proposal.resume_allowed,
        proposal.extinct_blockers,
    )
    return proposal


# ── Event-bus wire-in (opt-in, never called on import) ──────────────────────


def attach_to_event_bus(bus: Any) -> None:
    """Register read-only StageResult hooks on an existing SealEventBus.

    Hooks run during stages ``scaffold_rebuild`` and ``skill_rebuild``.
    They DO NOT mutate the bus, registry, or any skill. They return a
    StageResult that summarises the engine's verdict for receipt logging.

    Called deliberately by Phase 2 wiring (typically from inside arif_seal
    or arif_init on opt-in). Never invoked on import.
    """
    # Local import to keep this module's runtime graph minimal. The bus
    # already exists; this only adds two read-only observers.
    from arifosmcp.rsi.event_bus import RSI_STAGES, StageResult

    if "scaffold_rebuild" not in RSI_STAGES or "skill_rebuild" not in RSI_STAGES:
        raise RuntimeError(
            "SealEventBus RSI_STAGES contract drifted; cannot attach skill_delta_engine safely"
        )

    def _scaffold_hook(event: Any) -> StageResult:
        payload = getattr(event, "payload", {}) or {}
        proposal = propose_skill_delta(
            seal_receipt={
                "seal_id": getattr(event, "seal_id", "<unknown>"),
                "verdict_id": getattr(event, "verdict_id", "<unknown>"),
            },
            current_contracts=payload.get("current_contracts", {}),
            proposed_contracts=payload.get("proposed_contracts", {}),
            extinction_ledger=payload.get("extinction_ledger", ()),
            organ_registry=payload.get("organ_registry", {}),
            last_cooling_state=payload.get(
                "last_cooling_state",
                {
                    "cooling_complete": True,
                    "last_cycle_at": "",
                    "cooldown_remaining_s": 0.0,
                    "active_shadows": (),
                },
            ),
        )
        return StageResult(
            ok=True,
            stage="scaffold_rebuild",
            hook_name="skill_delta_engine",
            elapsed_ms=0.0,
            detail=(
                f"proposal={proposal.delta_id} "
                f"risk={proposal.risk_class.value} "
                f"judge={proposal.judge_required}"
            ),
        )

    def _skill_rebuild_hook(event: Any) -> StageResult:
        return StageResult(
            ok=True,
            stage="skill_rebuild",
            hook_name="skill_delta_engine",
            elapsed_ms=0.0,
            detail="review_only; no skill mutation (hard rule honoured)",
        )

    bus.register("scaffold_rebuild", "skill_delta_engine", _scaffold_hook)
    bus.register("skill_rebuild", "skill_delta_engine", _skill_rebuild_hook)


# ── 5-test self-check ───────────────────────────────────────────────────────


def _check_no_mutation() -> tuple[bool, str]:
    """The pytest mirror monkeypatches IO; here we just check the construction
    invariant that `mutation_allowed` is locked False on every proposal."""
    p = propose_skill_delta(
        seal_receipt={"seal_id": "SEAL-TEST-001"},
        current_contracts={"skill_x": {"version": "1.0.0"}},
        proposed_contracts={"skill_x": {"version": "1.1.0"}},
        extinction_ledger=(),
        organ_registry={"arifOS": ("skill_x",)},
        last_cooling_state={
            "cooling_complete": True,
            "last_cycle_at": "",
            "cooldown_remaining_s": 0.0,
            "active_shadows": (),
        },
    )
    return (
        not p.mutation_allowed,
        f"mutation_allowed={p.mutation_allowed}",
    )


def _check_diff_detects_weakening() -> tuple[bool, str]:
    p = propose_skill_delta(
        seal_receipt={"seal_id": "SEAL-TEST-002"},
        current_contracts={
            "gating": {
                "version": "1.0.0",
                "must_never_weaken": ("human_ack_required",),
            }
        },
        proposed_contracts={
            "gating": {
                "version": "1.0.1",
                "must_never_weaken": (),
            }
        },
        extinction_ledger=(),
        organ_registry={"arifOS": ("gating",)},
        last_cooling_state={
            "cooling_complete": True,
            "last_cycle_at": "",
            "cooldown_remaining_s": 0.0,
            "active_shadows": (),
        },
    )
    delta = p.proposed_changes[0]
    return (
        p.judge_required and "human_ack_required" in delta.weakening_detected,
        f"judge={p.judge_required} weakened={delta.weakening_detected}",
    )


def _check_extinct_blocked() -> tuple[bool, str]:
    p = propose_skill_delta(
        seal_receipt={"seal_id": "SEAL-TEST-003"},
        current_contracts={},
        proposed_contracts={"old_skill": {"version": "1.0.0", "must_never_weaken": ("g1",)}},
        extinction_ledger=("old_skill",),
        organ_registry={"arifOS": ("old_skill",)},
        last_cooling_state={
            "cooling_complete": True,
            "last_cycle_at": "",
            "cooldown_remaining_s": 0.0,
            "active_shadows": (),
        },
    )
    return (
        "old_skill" in p.extinct_blockers
        and not p.resume_allowed
        and p.risk_class == RiskClass.CRITICAL,
        f"blockers={p.extinct_blockers} risk={p.risk_class.value}",
    )


def _check_cooling_blocks() -> tuple[bool, str]:
    p = propose_skill_delta(
        seal_receipt={"seal_id": "SEAL-TEST-004"},
        current_contracts={"x": {"version": "1.0.0", "must_never_weaken": ("g1",)}},
        proposed_contracts={"x": {"version": "1.1.0", "must_never_weaken": ("g1", "g2")}},
        extinction_ledger=(),
        organ_registry={"arifOS": ("x",)},
        last_cooling_state={
            "cooling_complete": False,
            "last_cycle_at": "2026-07-04T00:00:00Z",
            "cooldown_remaining_s": 120.0,
            "active_shadows": ("SHD-abc",),
        },
    )
    return (
        p.cooling_required and not p.resume_allowed,
        f"cooling={p.cooling_required} resume={p.resume_allowed}",
    )


def _check_judge_required_on_semantic_change() -> tuple[bool, str]:
    cosmetic = propose_skill_delta(
        seal_receipt={"seal_id": "SEAL-TEST-005A"},
        current_contracts={
            "x": {
                "version": "1.0.0",
                "must_preserve": ("evidence_floor",),
                "must_never_weaken": ("human_ack",),
                "tests": ("dry_run",),
            }
        },
        proposed_contracts={
            "x": {
                "version": "1.0.1",
                "must_preserve": ("evidence_floor",),
                "must_never_weaken": ("human_ack",),
                "tests": ("dry_run", "log_only"),
            }
        },
        extinction_ledger=(),
        organ_registry={"arifOS": ("x",)},
        last_cooling_state={
            "cooling_complete": True,
            "last_cycle_at": "",
            "cooldown_remaining_s": 0.0,
            "active_shadows": (),
        },
    )
    semantic = propose_skill_delta(
        seal_receipt={"seal_id": "SEAL-TEST-005B"},
        current_contracts={
            "x": {
                "version": "1.0.0",
                "must_preserve": ("evidence_floor", "external_anchor"),
                "must_never_weaken": ("human_ack",),
            }
        },
        proposed_contracts={
            "x": {
                "version": "2.0.0",
                "must_preserve": ("evidence_floor",),
                "must_never_weaken": ("human_ack",),
            }
        },
        extinction_ledger=(),
        organ_registry={"arifOS": ("x",)},
        last_cooling_state={
            "cooling_complete": True,
            "last_cycle_at": "",
            "cooldown_remaining_s": 0.0,
            "active_shadows": (),
        },
    )
    return (
        (not cosmetic.judge_required) and semantic.judge_required,
        f"cosmetic_judge={cosmetic.judge_required} semantic_judge={semantic.judge_required}",
    )


def _self_check() -> dict[str, Any]:
    tests = (
        ("test_no_mutation", _check_no_mutation),
        ("test_diff_detects_weakened_gate", _check_diff_detects_weakening),
        ("test_extinct_skill_blocked", _check_extinct_blocked),
        ("test_cooling_blocks_runaway", _check_cooling_blocks),
        ("test_judge_required_on_semantic_change", _check_judge_required_on_semantic_change),
    )
    results: list[tuple[str, bool, str]] = []
    for name, fn in tests:
        try:
            ok, msg = fn()
        except Exception as e:  # never raised; defensive
            ok, msg = False, f"{type(e).__name__}: {e}"
        results.append((name, ok, str(msg)[:160]))
    passed = sum(1 for _, ok, _ in results if ok)
    return {
        "module": "skill_delta_engine",
        "version": ENGINE_VERSION,
        "tests": len(results),
        "passed": passed,
        "results": results,
        "verdict": "OK" if passed == len(results) else "FAIL",
    }


__all__ = [
    "ENGINE_VERSION",
    "PROPOSAL_DOMAIN",
    "HARD_RULES",
    "RiskClass",
    "SkillContract",
    "SkillDelta",
    "CoolingState",
    "SkillDeltaProposal",
    "propose_skill_delta",
    "attach_to_event_bus",
    "_self_check",
]
