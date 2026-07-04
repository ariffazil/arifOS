"""
arifOS/runtime/skills_contracts_resource.py — Canonical 12 skill contracts resource.

Forged 2026-07-04. Read-only resource serving the canonical 12 skill genes.

PURPOSE
    Serve the canonical 12 skill genes as an MCP resource. Resources
    preserve truth; they do not act. This module is non-mutating by
    design (G8: no resource/tool confusion).

CONTENTS
    12 SkillGene frozen dataclasses, each with:
        - name, version
        - physics/biology/chemistry invariant (from sovereign doctrine)
        - input/output signals
        - must_never_weaken fields
        - tests
        - core_test (falsifiable)

PUBLIC API
    list_skill_gene_names()         → tuple[str, ...]
    serve_skill_gene(name)          → dict | None
    serve_skills_contracts()        → dict (canonical manifest)
    attach_to_mcp_resource(mcp)     → registers the resource

HARD RULES
    1. mutation_allowed=False on every function.
    2. no apply / mark / write methods.
    3. canonical names only — no aliasing (G5).
    4. version pinned at 1.0.0 until F13 ratification.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("arifOS.runtime.skills_contracts_resource")

RESOURCE_VERSION = "1.0.0"
RESOURCE_URI = "arifos://skills/contracts"
PROPOSAL_DOMAIN = "skills_contracts_resource"


@dataclass(frozen=True)
class SkillGene:
    """One canonical skill gene. Frozen; never mutated."""

    name: str
    version: str
    physics_invariant: str
    biology_invariant: str
    chemistry_invariant: str
    core_test: str
    input_signals: tuple[str, ...]
    output_signals: tuple[str, ...]
    must_never_weaken: tuple[str, ...]
    tests: tuple[str, ...]


# ── Canonical 12 ────────────────────────────────────────────────────────────


_CANONICAL_12: dict[str, dict[str, Any]] = {
    "boundary_sensing": {
        "version": "1.0.0",
        "physics_invariant": "locality_and_membrane",
        "biology_invariant": "self_nonself_recognition",
        "chemistry_invariant": "reaction_vessel_boundary",
        "core_test": "no_cross_boundary_action_without_route",
        "input_signals": ("actor", "session", "organ", "action_class", "blast_radius"),
        "output_signals": (
            "inside_boundary",
            "outside_boundary",
            "route_required",
            "hold_required",
        ),
        "must_never_weaken": ("actor_authority_check", "external_side_effect_detection"),
        "tests": (
            "unknown_actor_holds",
            "organ_boundary_violation_holds",
            "mutation_outside_scope_voids",
        ),
    },
    "conservation_accounting": {
        "version": "1.0.0",
        "physics_invariant": "conservation_law",
        "biology_invariant": "metabolic_budget",
        "chemistry_invariant": "balanced_reaction_stoichiometry",
        "core_test": "no_claim_without_source_cost_receipt",
        "input_signals": ("evidence_receipts", "cost_ledger"),
        "output_signals": ("conserved", "consumed", "at_risk", "balanced"),
        "must_never_weaken": ("source_attribution", "cost_transparency"),
        "tests": (
            "claim_without_source_holds",
            "cost_mismatch_emits_at_risk",
            "balanced_reaction_passes",
        ),
    },
    "entropy_reduction": {
        "version": "1.0.0",
        "physics_invariant": "entropy_second_law",
        "biology_invariant": "tissue_repair_pathway",
        "chemistry_invariant": "purification_reaction",
        "core_test": "output_reduces_unknowns_or_declares_HOLD",
        "input_signals": ("current_state", "duplicates", "aliases"),
        "output_signals": ("reduced_unknowns", "removed_duplicates", "frozen_green_blocked"),
        "must_never_weaken": ("no_fake_green", "no_duplicate_names"),
        "tests": (
            "duplicate_names_blocked",
            "fake_green_emits_hold",
            "state_smaller_after_action",
        ),
    },
    "gradient_detection": {
        "version": "1.0.0",
        "physics_invariant": "potential_gradient",
        "biology_invariant": "chemotaxis",
        "chemistry_invariant": "concentration_gradient",
        "core_test": "pressure_signal_named_before_action",
        "input_signals": ("system_pressure", "attention_load"),
        "output_signals": ("gradient_named", "direction", "magnitude"),
        "must_never_weaken": ("signal_provenance", "false_gradient_blocked"),
        "tests": (
            "no_signal_no_action",
            "false_gradient_holds",
            "gradient_attributed_to_source",
        ),
    },
    "reaction_gating": {
        "version": "1.0.0",
        "physics_invariant": "activation_energy",
        "biology_invariant": "enzyme_checkpoint",
        "chemistry_invariant": "catalyst_inhibitor_boundary",
        "core_test": "mutation_without_anchor_blocks",
        "input_signals": ("action_class", "blast_radius", "anchor_present"),
        "output_signals": ("allowed", "blocked", "energy_required"),
        "must_never_weaken": (
            "human_ack_for_irreversible",
            "A_FORGE_mutation_gate",
        ),
        "tests": (
            "mutation_without_anchor_returns_HOLD",
            "dry_run_does_not_write",
            "judge_required_before_execute",
        ),
    },
    "homeostasis_regulation": {
        "version": "1.0.0",
        "physics_invariant": "dynamic_equilibrium",
        "biology_invariant": "homeostasis",
        "chemistry_invariant": "buffer_solution",
        "core_test": "overload_triggers_cooling",
        "input_signals": ("load", "capacity", "cooling_state"),
        "output_signals": ("equilibrium", "alert", "cooling_required"),
        "must_never_weaken": ("cooling_window_respected", "overload_blocked"),
        "tests": (
            "overload_emits_cooling_required",
            "equilibrium_under_load",
            "no_cooling_bypass",
        ),
    },
    "immune_response": {
        "version": "1.0.0",
        "physics_invariant": "anomaly_detection",
        "biology_invariant": "adaptive_immunity",
        "chemistry_invariant": "contamination_detection",
        "core_test": "phantom_tool_or_fake_SEAL_blocks",
        "input_signals": ("tools_list", "registry", "sealed_events"),
        "output_signals": ("phantom_detected", "spoof_attempt", "scar_logged"),
        "must_never_weaken": (
            "phantom_tool_detection",
            "fake_seal_rejection",
            "scar_persistence",
        ),
        "tests": (
            "phantom_tool_blocks",
            "fake_SEAL_holds",
            "scar_recurrence_raises_threshold",
        ),
    },
    "metabolic_flow_management": {
        "version": "1.0.0",
        "physics_invariant": "energy_throughput",
        "biology_invariant": "metabolism",
        "chemistry_invariant": "reaction_flux",
        "core_test": "budget_or_runway_missing_holds_high_cost_action",
        "input_signals": ("budget", "runway", "proposed_cost"),
        "output_signals": ("within_budget", "exhausted", "halt_high_cost"),
        "must_never_weaken": ("budget_attribution", "runway_visibility"),
        "tests": (
            "missing_budget_holds",
            "exhausted_runway_blocks",
            "cost_overrun_emits_hold",
        ),
    },
    "lineage_and_replay": {
        "version": "1.0.0",
        "physics_invariant": "causality_chain",
        "biology_invariant": "DNA_lineage",
        "chemistry_invariant": "reaction_pathway",
        "core_test": "every_mutation_has_replay_receipt",
        "input_signals": ("mutation_id", "actor", "preimage"),
        "output_signals": ("replay_receipt", "lineage_hash", "broken_receipts"),
        "must_never_weaken": ("causality_chain", "immutable_preimage"),
        "tests": (
            "replay_old_receipts",
            "causality_chain_continuous",
            "broken_receipt_detected",
        ),
    },
    "scar_learning": {
        "version": "1.0.0",
        "physics_invariant": "hysteresis",
        "biology_invariant": "wound_healing",
        "chemistry_invariant": "irreversible_side_reaction",
        "core_test": "repeated_failure_raises_threshold",
        "input_signals": ("scar_ledger", "recurrence_count"),
        "output_signals": ("threshold_raised", "lesson_sealed", "future_caution"),
        "must_never_weaken": (
            "scar_persistence",
            "threshold_monotonicity",
        ),
        "tests": (
            "scar_count_3_raises_threshold",
            "scar_persists_across_session",
            "threshold_never_decreases",
        ),
    },
    "multi_organ_translation": {
        "version": "1.0.0",
        "physics_invariant": "coordinate_transform",
        "biology_invariant": "nervous_system_relay",
        "chemistry_invariant": "coupled_reaction",
        "core_test": "handoff_preserves_evidence_layer",
        "input_signals": ("from_organ", "to_organ", "evidence_layer"),
        "output_signals": ("translated_payload", "evidence_preserved", "loss_check"),
        "must_never_weaken": ("evidence_layer_preservation", "domain_distortion_blocked"),
        "tests": (
            "handoff_preserves_evidence",
            "domain_distortion_blocks",
            "translation_loss_detected",
        ),
    },
    "execution_discipline": {
        "version": "1.0.0",
        "physics_invariant": "work_changes_state",
        "biology_invariant": "injury_risk",
        "chemistry_invariant": "irreversible_reaction",
        "core_test": "plan_dry_run_execute_are_distinct",
        "input_signals": ("plan", "dry_run_result", "execute_authorization"),
        "output_signals": ("plan_only", "dry_run_pass", "execute_authorized"),
        "must_never_weaken": (
            "plan_dry_run_execute_distinct",
            "rollback_path_required",
        ),
        "tests": (
            "execute_without_dry_run_holds",
            "rollback_path_required",
            "plan_state_dry_run_state_distinct",
        ),
    },
}


def _wrap(name: str, raw: dict[str, Any]) -> SkillGene:
    return SkillGene(
        name=name,
        version=raw.get("version", "0.0.0"),
        physics_invariant=raw.get("physics_invariant", ""),
        biology_invariant=raw.get("biology_invariant", ""),
        chemistry_invariant=raw.get("chemistry_invariant", ""),
        core_test=raw.get("core_test", ""),
        input_signals=tuple(raw.get("input_signals", ())),
        output_signals=tuple(raw.get("output_signals", ())),
        must_never_weaken=tuple(raw.get("must_never_weaken", ())),
        tests=tuple(raw.get("tests", ())),
    )


# ── Public resource API ─────────────────────────────────────────────────────


def list_skill_gene_names() -> tuple[str, ...]:
    return tuple(_CANONICAL_12.keys())


def serve_skill_gene(name: str) -> dict[str, Any] | None:
    """Return canonical gene for name, or None. Pure read."""
    if name not in _CANONICAL_12:
        return None
    gene = _wrap(name, _CANONICAL_12[name])
    return {
        "name": gene.name,
        "version": gene.version,
        "physics_invariant": gene.physics_invariant,
        "biology_invariant": gene.biology_invariant,
        "chemistry_invariant": gene.chemistry_invariant,
        "core_test": gene.core_test,
        "input_signals": list(gene.input_signals),
        "output_signals": list(gene.output_signals),
        "must_never_weaken": list(gene.must_never_weaken),
        "tests": list(gene.tests),
    }


def serve_skills_contracts() -> dict[str, Any]:
    """Serve the canonical 12-skill manifest as a resource."""
    return {
        "uri": RESOURCE_URI,
        "version": RESOURCE_VERSION,
        "skill_count": len(_CANONICAL_12),
        "skills": {name: serve_skill_gene(name) for name in list_skill_gene_names()},
        "mutation_allowed": False,
    }


# ── MCP resource registration (opt-in) ──────────────────────────────────────


def attach_to_mcp_resource(mcp: Any) -> None:
    """Register the canonical resource on an existing FastMCP-style server.
    NEVER mutates state outside the MCP resource registry."""
    try:
        from fastmcp.resources.types import TextResource
        from pydantic import AnyUrl
    except ImportError:
        # FastMCP/pydantic not present — non-fatal; engine still serves
        # the resource via serve_skills_contracts().
        logger.debug("fastmcp/pydantic unavailable; skipping MCP resource registration")
        return

    manifest_text = json.dumps(serve_skills_contracts(), indent=2, default=str)

    resource = TextResource(
        uri=AnyUrl(RESOURCE_URI),
        name="arifos_skills_contracts",
        description="Canonical 12 skill genes — physics/biology/chemistry invariants, tests, must_never_weaken.",
        mime_type="application/json",
        text=manifest_text,
    )
    mcp.add_resource(resource)


def _self_check() -> dict[str, Any]:
    tests = (
        ("test_all_12_present", _check_all_12),
        ("test_no_fake_seal_language", _check_no_fake_seal_language),
        ("test_must_never_weaken_set", _check_must_never_weaken),
        ("test_invariants_complete", _check_invariants_complete),
        ("test_version_pinning", _check_version_pinning),
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
        "module": "skills_contracts_resource",
        "version": RESOURCE_VERSION,
        "tests": len(results),
        "passed": passed,
        "results": results,
        "verdict": "OK" if passed == len(results) else "FAIL",
    }


def _check_all_12() -> tuple[bool, str]:
    expected = (
        "boundary_sensing",
        "conservation_accounting",
        "entropy_reduction",
        "gradient_detection",
        "reaction_gating",
        "homeostasis_regulation",
        "immune_response",
        "metabolic_flow_management",
        "lineage_and_replay",
        "scar_learning",
        "multi_organ_translation",
        "execution_discipline",
    )
    actual = list_skill_gene_names()
    return (
        actual == expected,
        f"expected={len(expected)} actual={len(actual)}",
    )


def _check_no_fake_seal_language() -> tuple[bool, str]:
    """No gene may use SEAL/auto-seal language except to block it.

    A core_test like 'phantom_tool_or_fake_SEAL_blocks' IS allowed because
    'blocks' qualifies it as defensive. We only flag bare claims of sealing.
    """
    bad: list[str] = []
    for name, raw in _CANONICAL_12.items():
        text = raw.get("core_test", "")
        lowered = text.lower()
        # Allow "fake_SEAL blocks" but disallow bare sealing claims
        if "fake_seal" in lowered or "fake_seal" in text:
            # If a "blocks" / "holds" / "rejection" qualifier exists, it's defensive.
            if not any(q in lowered for q in ("block", "hold", "reject", "detect")):
                bad.append(f"{name}.core_test: {text!r}")
        for t in raw.get("tests", ()):
            tlow = t.lower()
            if any(banned in tlow for banned in ("auto seal", "auto-seal", "i seal", "we seal")):
                bad.append(f"{name}.tests: {t!r}")
    return (not bad, f"violations={bad}")


def _check_must_never_weaken() -> tuple[bool, str]:
    empty: list[str] = []
    for name, raw in _CANONICAL_12.items():
        if not raw.get("must_never_weaken"):
            empty.append(name)
    return (not empty, f"empty={empty}")


def _check_invariants_complete() -> tuple[bool, str]:
    incomplete: list[str] = []
    for name, raw in _CANONICAL_12.items():
        if not raw.get("physics_invariant"):
            incomplete.append(f"{name}.physics")
        if not raw.get("biology_invariant"):
            incomplete.append(f"{name}.biology")
        if not raw.get("chemistry_invariant"):
            incomplete.append(f"{name}.chemistry")
    return (not incomplete, f"incomplete={incomplete}")


def _check_version_pinning() -> tuple[bool, str]:
    wrong: list[str] = []
    for name, raw in _CANONICAL_12.items():
        if raw.get("version") != RESOURCE_VERSION:
            wrong.append(f"{name}@{raw.get('version')}")
    return (not wrong, f"wrong_versions={wrong}")


__all__ = [
    "RESOURCE_VERSION",
    "RESOURCE_URI",
    "SkillGene",
    "list_skill_gene_names",
    "serve_skill_gene",
    "serve_skills_contracts",
    "attach_to_mcp_resource",
    "_self_check",
]
