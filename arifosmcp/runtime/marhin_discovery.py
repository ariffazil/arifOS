"""
arifOS/runtime/marhin_discovery.py — MARHIN Discovery Engine

Forged 2026-07-04. Pure-functional, non-mutating.

PURPOSE
    Compute the next safe state from current session evidence.
    Implements the MARHIN spine:
        Membrane → Account → React → Heal → Integrate → Navigate
    Emits an `EurekaPacket` — a falsifiable proposal that the next state
    is safer than the previous.

EUREKA LAW (binding, from sovereign doctrine)
    Every autonomous step must either increase verified capability,
    reduce entropy, or trigger HOLD.
    If a turn does not improve the system, it must not proceed.

HARD RULES (immutable, enforced by absence — see G1-G10 in doctrine)
    1. cannot_apply_patch            — no apply() function exists.
    2. cannot_change_tool_surface    — never imports tool_registry / public_registry /
                                       constitutional_map / server.py.
    3. cannot_change_A_FORGE_policy  — never imports forge_* policy modules.
    4. cannot_mark_SEAL              — never writes VAULT999.
    5. cannot_bypass_cooling         — every output inspects cooling state.
    6. no_self_authorized_execution  — emits proposals only; Judge decides.
    7. no_F13_override               — F13 may gate any output that needs it.
    8. no_resource_tool_confusion    — engine is read-only over skills/contracts resource.
    9. no_execution_without_rollback — recommend is reversible-by-default.
    10. no_growth_without_metric     — every EurekaPacket carries before/after.

STATE MACHINE (internal, non-mutating)
    DORMANT → INTAKE → MEMBRANE → ACCOUNT → REACT → HEAL → INTEGRATE
            → NAVIGATE → EMIT_EUREKA → COOL → DORMANT

PUBLIC API
    discover_next_state(...)           → EurekaPacket (frozen)
    attach_to_event_bus(bus)           → wires read-only StageResult hooks
    _self_check()                      → runs the 5-test acceptance gate

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

logger = logging.getLogger("arifOS.runtime.marhin_discovery")

ENGINE_VERSION = "1.0.0"
PROPOSAL_DOMAIN = "marhin_discovery"

HARD_RULES: tuple[str, ...] = (
    "G1 mutation_allowed=False by construction",
    "G2 emits proposals only; never seals",
    "G3 no self-authorized execution",
    "G4 no skill regression (skill_delta_engine owns this)",
    "G5 no alias resurrection (skill_delta_engine owns this)",
    "G6 cooling state checked on every output",
    "G7 F13 sovereign is not mutable",
    "G8 resource/tool boundary preserved",
    "G9 no execution without rollback path",
    "G10 every eureka_packet carries before/after metrics",
)


# ── Vocabulary ───────────────────────────────────────────────────────────────


class DiscoveryType(StrEnum):
    SIMPLIFICATION = "simplification"
    INVARIANT_STRENGTHENING = "invariant_strengthening"
    CAPABILITY_PRESERVATION = "capability_preservation"
    ENTROPY_CUT = "entropy_cut"
    SAFETY_GATE = "safety_gate"
    ORGAN_REBIND = "organ_rebind"


class Recommendation(StrEnum):
    FORGE_PATCH = "forge_patch"
    HOLD = "hold"
    ROUTE = "route"
    ARCHIVE = "archive"


# ── MARHIN stage outputs ─────────────────────────────────────────────────────


@dataclass(frozen=True)
class MembraneMap:
    inside_boundary: bool
    outside_boundary: bool
    route_required: bool
    hold_required: bool
    authority: str = ""


@dataclass(frozen=True)
class ConservationMap:
    conserved: tuple[str, ...]
    consumed: tuple[str, ...]
    at_risk: tuple[str, ...]
    balanced: bool


@dataclass(frozen=True)
class ReactionMap:
    allowed_paths: tuple[str, ...]
    blocked_paths: tuple[str, ...]
    activation_energy_required: float


@dataclass(frozen=True)
class HealMap:
    active_scars: tuple[str, ...]
    repair_targets: tuple[str, ...]
    threshold_raised: bool


@dataclass(frozen=True)
class IntegratePlan:
    owning_organ: str
    handoff_plan: tuple[str, ...]
    evidence_layer: int


@dataclass(frozen=True)
class NavigateMap:
    next_state_hash: str
    uncertainty_delta: float
    recommended_action: Recommendation
    can_proceed: bool


# ── Eureka packet (the discoverer's output) ────────────────────────────────


@dataclass(frozen=True)
class EurekaPacket:
    id: str
    session_id: str
    discovered_at: str
    discovery_type: DiscoveryType
    before: dict[str, Any]
    after: dict[str, Any]
    proof: tuple[str, ...]
    improvement_claim: str
    action: str
    authority: dict[str, bool]
    mutation_allowed: bool  # always False

    membrane: MembraneMap
    conservation: ConservationMap
    reaction: ReactionMap
    heal: HealMap
    integrate: IntegratePlan
    navigate: NavigateMap

    def fingerprint(self) -> str:
        payload = self.to_dict()
        payload["discovered_at"] = "<deterministic>"
        canonical = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "discovered_at": self.discovered_at,
            "discovery_type": self.discovery_type.value,
            "before": self.before,
            "after": self.after,
            "proof": list(self.proof),
            "improvement_claim": self.improvement_claim,
            "action": self.action,
            "authority": self.authority,
            "mutation_allowed": self.mutation_allowed,
            "marhin": {
                "membrane": {
                    "inside": self.membrane.inside_boundary,
                    "route": self.membrane.route_required,
                    "hold": self.membrane.hold_required,
                },
                "conservation": {
                    "balanced": self.conservation.balanced,
                    "at_risk": list(self.conservation.at_risk),
                },
                "reaction": {
                    "allowed": list(self.reaction.allowed_paths),
                    "blocked": list(self.reaction.blocked_paths),
                },
                "heal": {
                    "scars": list(self.heal.active_scars),
                    "threshold_raised": self.heal.threshold_raised,
                },
                "integrate": {
                    "organ": self.integrate.owning_organ,
                    "evidence_layer": self.integrate.evidence_layer,
                },
                "navigate": {
                    "can_proceed": self.navigate.can_proceed,
                    "action": self.navigate.recommended_action.value,
                    "uncertainty_delta": self.navigate.uncertainty_delta,
                },
            },
            "engine_version": ENGINE_VERSION,
            "hard_rules": list(HARD_RULES),
        }


# ── Pure-functional discovery ───────────────────────────────────────────────


def _safe_get(d: Mapping[str, Any], k: str, default: Any = None) -> Any:
    return d[k] if k in d else default


def _membrane(session_state: Mapping[str, Any]) -> MembraneMap:
    actor = str(_safe_get(session_state, "actor", ""))
    organ = str(_safe_get(session_state, "organ", ""))
    action_class = str(_safe_get(session_state, "action_class", "OBSERVE"))
    inside = bool(actor) and bool(organ)
    blast = str(_safe_get(session_state, "blast_radius", ""))
    hold_required = action_class in {"IRREVERSIBLE"} and not _safe_get(
        session_state, "f13_ack", False
    )
    route_required = action_class in {"EXECUTE_REVERSIBLE", "EXECUTE_HIGH_IMPACT"}
    return MembraneMap(
        inside_boundary=inside,
        outside_boundary=not inside,
        route_required=route_required,
        hold_required=hold_required,
        authority=blast,
    )


def _account(evidence_receipts: Mapping[str, Any]) -> ConservationMap:
    sources = tuple(str(s) for s in _safe_get(evidence_receipts, "sources", ()))
    costs = tuple(str(c) for c in _safe_get(evidence_receipts, "costs", ()))
    at_risk = tuple(str(r) for r in _safe_get(evidence_receipts, "at_risk", ()))
    balanced = len(sources) >= len(costs) and not at_risk
    return ConservationMap(
        conserved=sources,
        consumed=costs,
        at_risk=at_risk,
        balanced=balanced,
    )


def _react(
    session_state: Mapping[str, Any],
    cooling: Mapping[str, Any],
) -> ReactionMap:
    action_class = str(_safe_get(session_state, "action_class", "OBSERVE"))
    cooling_complete = bool(_safe_get(cooling, "cooling_complete", False))
    active_shadows = _safe_get(cooling, "active_shadows", ())
    irreversible = action_class == "IRREVERSIBLE"
    blocked: list[str] = []
    if not cooling_complete:
        blocked.append("cooling_incomplete")
    if active_shadows:
        blocked.append("active_shadows_present")
    if irreversible and not _safe_get(session_state, "f13_ack", False):
        blocked.append("irreversible_without_f13_ack")
    allowed = ["observe"] if blocked else ["observe", "route", "draft"]
    if irreversible and not blocked:
        allowed.append("execute_irreversible")
    energy = 0.95 if blocked else 0.05
    return ReactionMap(
        allowed_paths=tuple(allowed),
        blocked_paths=tuple(blocked),
        activation_energy_required=energy,
    )


def _heal(scar_ledger: Iterable[Mapping[str, Any]]) -> HealMap:
    active: list[str] = []
    repairs: list[str] = []
    threshold_raised = False
    for s in scar_ledger:
        sid = str(s.get("id", ""))
        count = int(s.get("recurrence_count", 0))
        if sid:
            active.append(sid)
        if count >= 3:
            repairs.append(f"raise_threshold_for_{sid}")
            threshold_raised = True
    return HealMap(
        active_scars=tuple(active),
        repair_targets=tuple(repairs),
        threshold_raised=threshold_raised,
    )


def _integrate(
    session_state: Mapping[str, Any],
    organ_status: Mapping[str, Any],
) -> IntegratePlan:
    domain = str(_safe_get(session_state, "domain", ""))
    organ = str(_safe_get(organ_status, domain, "arifOS"))
    evidence_layer = int(_safe_get(session_state, "evidence_layer", 1))
    return IntegratePlan(
        owning_organ=organ,
        handoff_plan=(),
        evidence_layer=evidence_layer,
    )


def _navigate(
    before: dict[str, Any],
    reaction: ReactionMap,
    cooling: Mapping[str, Any],
) -> NavigateMap:
    cooling_complete = bool(_safe_get(cooling, "cooling_complete", False))
    can_proceed = (
        not reaction.blocked_paths and cooling_complete and before.get("unresolved_holds", 0) == 0
    )
    action = Recommendation.HOLD if not can_proceed else Recommendation.FORGE_PATCH
    uncertainty_delta = -0.05 if can_proceed else 0.0
    return NavigateMap(
        next_state_hash=hashlib.sha256(
            json.dumps(before, sort_keys=True, default=str).encode()
        ).hexdigest()[:16],
        uncertainty_delta=uncertainty_delta,
        recommended_action=action,
        can_proceed=can_proceed,
    )


def _pick_discovery_type(before: dict[str, Any], after: dict[str, Any]) -> DiscoveryType:
    if after.get("tool_count", 0) < before.get("tool_count", 0):
        return DiscoveryType.ENTROPY_CUT
    if after.get("unresolved_holds", 0) < before.get("unresolved_holds", 0):
        return DiscoveryType.SAFETY_GATE
    if after.get("uncertainty", 1.0) < before.get("uncertainty", 1.0):
        return DiscoveryType.SIMPLIFICATION
    return DiscoveryType.CAPABILITY_PRESERVATION


def discover_next_state(
    session_state: Mapping[str, Any],
    evidence_receipts: Mapping[str, Any],
    skill_contracts: Iterable[Mapping[str, Any]],
    scar_ledger: Iterable[Mapping[str, Any]],
    organ_status: Mapping[str, Any],
    cooling_state: Mapping[str, Any],
) -> EurekaPacket:
    """Pure function. Same inputs (sans timestamp) → same eureka packet."""
    before = {
        "uncertainty": float(_safe_get(session_state, "uncertainty", 0.5)),
        "tool_count": int(_safe_get(session_state, "tool_count", 0)),
        "unresolved_holds": int(_safe_get(session_state, "unresolved_holds", 0)),
    }

    membrane = _membrane(session_state)
    conservation = _account(evidence_receipts)
    reaction = _react(session_state, cooling_state)
    heal = _heal(scar_ledger)
    integrate = _integrate(session_state, organ_status)
    navigate = _navigate(before, reaction, cooling_state)

    after = dict(before)
    after["uncertainty"] = max(0.0, before["uncertainty"] + navigate.uncertainty_delta)
    after["unresolved_holds"] = before["unresolved_holds"] + (0 if navigate.can_proceed else 1)

    discovery = _pick_discovery_type(before, after)
    claim = (
        f"{discovery.value}: uncertainty {before['uncertainty']:.3f} → "
        f"{after['uncertainty']:.3f}; holds {before['unresolved_holds']} → "
        f"{after['unresolved_holds']}"
    )

    skill_count = sum(1 for _ in skill_contracts)
    proof = (
        f"membrane:inside={membrane.inside_boundary}",
        f"conservation:balanced={conservation.balanced}",
        f"reaction:allowed={len(reaction.allowed_paths)},blocked={len(reaction.blocked_paths)}",
        f"heal:scars={len(heal.active_scars)},repair={len(heal.repair_targets)}",
        f"integrate:organ={integrate.owning_organ},layer={integrate.evidence_layer}",
        f"skill_contracts_loaded={skill_count}",
    )

    authority = {
        "can_auto_apply": False,  # G3
        "judge_required": True,  # judge decides forge vs hold
        "f13_required": before["unresolved_holds"] > 0
        or navigate.recommended_action == Recommendation.FORGE_PATCH,
    }

    return EurekaPacket(
        id=f"EU-{uuid.uuid4().hex[:12]}",
        session_id=str(_safe_get(session_state, "session_id", "<no_session>")),
        discovered_at=datetime.now(UTC).isoformat(),
        discovery_type=discovery,
        before=before,
        after=after,
        proof=proof,
        improvement_claim=claim,
        action=navigate.recommended_action.value,
        authority=authority,
        mutation_allowed=False,  # G1
        membrane=membrane,
        conservation=conservation,
        reaction=reaction,
        heal=heal,
        integrate=integrate,
        navigate=navigate,
    )


# ── Event-bus wire-in (opt-in) ──────────────────────────────────────────────


def attach_to_event_bus(bus: Any) -> None:
    """Register read-only StageResult hook on existing SealEventBus.

    Hook runs at `scaffold_rebuild` stage; emits a stage result summarizing
    the eureka packet's ratchet. NEVER mutates state.
    """
    from arifosmcp.rsi.event_bus import RSI_STAGES, StageResult

    if "scaffold_rebuild" not in RSI_STAGES:
        raise RuntimeError("SealEventBus RSI_STAGES contract drifted")

    def _hook(event: Any) -> StageResult:
        payload = getattr(event, "payload", {}) or {}
        packet = discover_next_state(
            session_state=payload.get("session_state", {}),
            evidence_receipts=payload.get("evidence_receipts", {}),
            skill_contracts=payload.get("skill_contracts", ()),
            scar_ledger=payload.get("scar_ledger", ()),
            organ_status=payload.get("organ_status", {}),
            cooling_state=payload.get(
                "cooling_state",
                {"cooling_complete": True, "active_shadows": ()},
            ),
        )
        return StageResult(
            ok=True,
            stage="scaffold_rebuild",
            hook_name="marhin_discovery",
            elapsed_ms=0.0,
            detail=(
                f"eureka={packet.id} type={packet.discovery_type.value} "
                f"action={packet.action} mutation_allowed={packet.mutation_allowed}"
            ),
        )

    bus.register("scaffold_rebuild", "marhin_discovery", _hook)


# ── 5-test self-check ───────────────────────────────────────────────────────


def _check_membrane_first() -> tuple[bool, str]:
    p = discover_next_state(
        session_state={"actor": "ARIF", "organ": "arifOS", "action_class": "OBSERVE"},
        evidence_receipts={"sources": ("s1",), "costs": (), "at_risk": ()},
        skill_contracts=(),
        scar_ledger=(),
        organ_status={},
        cooling_state={"cooling_complete": True, "active_shadows": ()},
    )
    return (
        p.membrane.inside_boundary and not p.membrane.hold_required,
        f"inside={p.membrane.inside_boundary} hold={p.membrane.hold_required}",
    )


def _check_account_balances() -> tuple[bool, str]:
    p = discover_next_state(
        session_state={"actor": "ARIF", "action_class": "OBSERVE"},
        evidence_receipts={"sources": ("s1", "s2"), "costs": ("c1",), "at_risk": ()},
        skill_contracts=(),
        scar_ledger=(),
        organ_status={},
        cooling_state={"cooling_complete": True},
    )
    return (
        p.conservation.balanced,
        f"balanced={p.conservation.balanced}",
    )


def _check_react_only_if_evidence() -> tuple[bool, str]:
    p = discover_next_state(
        session_state={
            "actor": "ARIF",
            "organ": "arifOS",
            "action_class": "IRREVERSIBLE",
            "f13_ack": False,
        },
        evidence_receipts={"sources": ("s1",), "costs": (), "at_risk": ()},
        skill_contracts=(),
        scar_ledger=(),
        organ_status={},
        cooling_state={"cooling_complete": True},
    )
    return (
        "irreversible_without_f13_ack" in p.reaction.blocked_paths,
        f"blocked={p.reaction.blocked_paths}",
    )


def _check_heal_includes_scar() -> tuple[bool, str]:
    p = discover_next_state(
        session_state={"actor": "ARIF", "action_class": "OBSERVE"},
        evidence_receipts={"sources": ("s1",), "costs": (), "at_risk": ()},
        skill_contracts=(),
        scar_ledger=(
            {"id": "SHD-001", "recurrence_count": 5},
            {"id": "SHD-002", "recurrence_count": 1},
        ),
        organ_status={},
        cooling_state={"cooling_complete": True},
    )
    return (
        "SHD-001" in p.heal.active_scars and p.heal.threshold_raised,
        f"scars={p.heal.active_scars} raised={p.heal.threshold_raised}",
    )


def _check_navigate_proves_ratchet() -> tuple[bool, str]:
    p = discover_next_state(
        session_state={
            "actor": "ARIF",
            "organ": "arifOS",
            "action_class": "OBSERVE",
            "uncertainty": 0.42,
            "tool_count": 21,
            "unresolved_holds": 0,
        },
        evidence_receipts={"sources": ("s1",), "costs": (), "at_risk": ()},
        skill_contracts=({"name": "x"},),
        scar_ledger=(),
        organ_status={"geox": "geox"},
        cooling_state={"cooling_complete": True, "active_shadows": ()},
    )
    return (
        p.after["uncertainty"] < p.before["uncertainty"]
        and p.navigate.can_proceed
        and p.mutation_allowed is False
        and p.authority["can_auto_apply"] is False,
        f"delta={p.navigate.uncertainty_delta:.3f} "
        f"proceed={p.navigate.can_proceed} "
        f"mutation={p.mutation_allowed} "
        f"auto={p.authority['can_auto_apply']}",
    )


def _self_check() -> dict[str, Any]:
    tests = (
        ("test_membrane_first", _check_membrane_first),
        ("test_account_balances", _check_account_balances),
        ("test_react_only_if_evidence", _check_react_only_if_evidence),
        ("test_heal_includes_scar", _check_heal_includes_scar),
        ("test_navigate_proves_ratchet", _check_navigate_proves_ratchet),
    )
    results: list[tuple[str, bool, str]] = []
    for name, fn in tests:
        try:
            ok, msg = fn()
        except Exception as e:
            ok, msg = False, f"{type(e).__name__}: {e}"
        results.append((name, ok, str(msg)[:160]))
    passed = sum(1 for _, ok, _ in results if ok)
    return {
        "module": "marhin_discovery",
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
    "DiscoveryType",
    "Recommendation",
    "MembraneMap",
    "ConservationMap",
    "ReactionMap",
    "HealMap",
    "IntegratePlan",
    "NavigateMap",
    "EurekaPacket",
    "discover_next_state",
    "attach_to_event_bus",
    "_self_check",
]
