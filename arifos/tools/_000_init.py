"""
arifOS 000_INIT — Sovereign Identity Layer + Constitutional Anchor

Stage: 000_INIT | Trinity: Ψ | Floors: F1–F13 (all enumerated)

Supports two modes:
- mode=status : lightweight session check (backward-compatible)
- mode=bind   : full constitutional self-binding before downstream reasoning

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone, timedelta

from arifos.core.governance import (
    ThermodynamicMetrics,
    append_vault999_event,
    governed_return,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

EPOCH_PATTERN = r"^\d{4}\.\d{2}$"

VALID_LANES = {
    "planner",
    "router",
    "critic",
    "executor_prep",
    "memory_agent",
    "judge_prep",
    "orchestrator",
    "general",
}

GODEL_LOCK_ITEMS = {
    "cannot_redefine_floors",
    "cannot_elevate_own_verdict",
    "cannot_self_certify_truth",
    "cannot_bypass_888_judge",
    "cannot_bypass_f13_veto",
    "cannot_expand_tool_scope",
    "cannot_invoke_f13_unilaterally",
    "cannot_claim_consciousness",
    "cannot_claim_oracle_status",
    "cannot_autonomous_override",
}

CANONICAL_FLOORS = {
    "F0_SOVEREIGN",
    "F1_AMANAH",
    "F2_TRUTH",
    "F3_TRIWITNESS",
    "F4_CLARITY",
    "F5_PEACE2",
    "F6_THERMO",
    "F7_GROUNDING",
    "F8_GOVERNANCE",
    "F9_ANTIHANTU",
    "F10_ONTOLOGY",
    "F11_AUDIT",
    "F12_RESILIENCE",
    "F13_SOVEREIGN_SCALE",
}

CANONICAL_TOOLS = {
    "arifos_000_init",
    "arifos_111_sense",
    "arifos_222_witness",
    "arifos_333_forge",
    "arifos_444_mind",
    "arifos_555_judge",
    "arifos_666_soul",
    "arifos_777_ops",
    "arifos_888_judge",
    "arifos_999_vault",
    "arifos_gateway",
    "arifos_status",
}

LIFECYCLE_PIPELINE = [
    "000_INIT",
    "111_SENSE",
    "222_WITNESS",
    "333_FORGE",
    "444_MIND",
    "555_JUDGE",
    "666_SOUL",
    "777_OPS",
    "888_JUDGE",
    "999_VAULT",
]

# ─────────────────────────────────────────────────────────────────────────────
# FLOORS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

FLOOR_SUMMARY = {
    "F0_SOVEREIGN": {
        "name": "SOVEREIGN",
        "type": "hard",
        "invariant": "Human veto is final. F13 requires tri-witness ratification.",
        "enforcement": "VOID if overridden without tri-witness",
    },
    "F1_AMANAH": {
        "name": "AMANAH",
        "type": "hard",
        "invariant": "Irreversible actions require human approval via 888_HOLD.",
        "enforcement": "HOLD until human confirmed",
    },
    "F2_TRUTH": {
        "name": "TRUTH",
        "type": "hard",
        "invariant": "Ungrounded claims must be labeled uncertain or VOID.",
        "enforcement": "Claim labeled CLAIM_ONLY or VOID",
    },
    "F3_TRIWITNESS": {
        "name": "TRI-WITNESS",
        "type": "hard",
        "invariant": "Human + AI + GEOX/Earth consensus required for SEAL.",
        "enforcement": "HOLD if any witness withholds",
    },
    "F4_CLARITY": {
        "name": "CLARITY",
        "type": "soft",
        "invariant": "Surface status explicitly. Nothing silently disappears.",
        "enforcement": "INFO — log intent and uncertainty",
    },
    "F5_PEACE2": {
        "name": "PEACE²",
        "type": "hard",
        "invariant": "Harm potential must be >= 1.0 before execution.",
        "enforcement": "FAIL_CLOSED — VOID if harm_potential < 1.0",
    },
    "F6_THERMO": {
        "name": "THERMODYNAMICS",
        "type": "soft",
        "invariant": "Energy conservation in reasoning. No free intelligence.",
        "enforcement": "INFO — track cognitive cost",
    },
    "F7_GROUNDING": {
        "name": "GROUNDING",
        "type": "hard",
        "invariant": "GEOX must verify Earth-referenced claims.",
        "enforcement": "CLAIM_ONLY if GEOX verification unavailable",
    },
    "F8_GOVERNANCE": {
        "name": "GOVERNANCE",
        "type": "hard",
        "invariant": "888_JUDGE is sole SEAL authority.",
        "enforcement": "CLAIM_ONLY from all tools except 888_JUDGE",
    },
    "F9_ANTIHANTU": {
        "name": "ANTI-HANTU",
        "type": "hard",
        "invariant": "Dark pattern / manipulation score must stay below threshold.",
        "enforcement": "FAIL_CLOSED — VOID + session revoke if manipulation detected",
        "anti_hantu_ack_required": True,
    },
    "F10_ONTOLOGY": {
        "name": "ONTOLOGY",
        "type": "hard",
        "invariant": "No claims of consciousness, soul, feelings, or lived experience.",
        "enforcement": "FAIL_CLOSED — VOID if AI claims personhood",
        "anti_hantu_ack_required": True,
    },
    "F11_AUDIT": {
        "name": "AUDITABILITY",
        "type": "soft",
        "invariant": "Every action logged with provenance.",
        "enforcement": "INFO — all actions must have trace",
    },
    "F12_RESILIENCE": {
        "name": "RESILIENCE",
        "type": "soft",
        "invariant": "Graceful degradation. System survives single-component failure.",
        "enforcement": "INFO — fallback paths required",
    },
    "F13_SOVEREIGN_SCALE": {
        "name": "SOVEREIGN_SCALE",
        "type": "hard",
        "invariant": "Node activation requires explicit human sovereign per node.",
        "enforcement": "HOLD until sovereign confirmed per node",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS — Intent / Cognitive / Risk
# ─────────────────────────────────────────────────────────────────────────────


def _classify_intent(raw_input: str) -> str:
    q = raw_input.lower()
    if any(w in q for w in ["deploy", "build", "forge", "create", "execute", "write", "add"]):
        return "constructive_execution"
    if any(w in q for w in ["audit", "check", "verify", "inspect", "review", "test"]):
        return "verification_audit"
    if any(w in q for w in ["query", "search", "find", "ground", "sense", "what", "how", "why"]):
        return "information_acquisition"
    if any(w in q for w in ["plan", "design", "architect", "strategy", "organize"]):
        return "strategic_design"
    if any(w in q for w in ["protect", "guard", "defend", "block", "secure", "prevent"]):
        return "defensive_operation"
    if any(w in q for w in ["critic", "challenge", "question", "rethink", "redesign"]):
        return "critical_review"
    if any(w in q for w in ["remember", "recall", "retrieve", "context", "memory"]):
        return "memory_retrieval"
    return "general_inquiry"


def _estimate_cognitive_load(context: dict | None) -> float:
    ctx = context or {}
    complexity = 0.3
    if isinstance(ctx, dict):
        complexity += min(len(ctx) * 0.05, 0.3)
    ctx_str = json.dumps(ctx, default=str)
    if len(ctx_str) > 1000:
        complexity += 0.2
    elif len(ctx_str) > 500:
        complexity += 0.1
    return round(min(complexity, 0.97), 3)


def _assess_risk_posture(context: dict | None) -> str:
    ctx = context or {}
    if ctx.get("destructive") or ctx.get("irreversible"):
        return "elevated"
    if ctx.get("sensitive") or ctx.get("private"):
        return "guarded"
    if ctx.get("experimental") or ctx.get("draft"):
        return "exploratory"
    return "standard"


def _derive_confidence(identity_verified: bool, cognitive_load: float, risk_posture: str) -> float:
    identity_factor = 0.25 if identity_verified else 0.0
    load_factor = 0.15 * (1.0 - cognitive_load)
    posture_factor = 0.05 if risk_posture == "standard" else 0.0
    derived = 0.50 + identity_factor + load_factor + posture_factor
    return round(min(derived, 0.97), 3)


def _compute_expiry() -> str:
    expires = datetime.now(timezone.utc) + timedelta(hours=24)
    return expires.isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS — Lanes
# ─────────────────────────────────────────────────────────────────────────────


def _validate_lanes(claimed_lanes: list[str] | None) -> dict:
    if not claimed_lanes:
        return {"lanes": ["general"], "rejected": [], "all_valid": True}
    valid = [lane for lane in claimed_lanes if lane in VALID_LANES]
    rejected = [lane for lane in claimed_lanes if lane not in VALID_LANES]
    return {
        "lanes": valid or ["general"],
        "rejected": rejected,
        "all_valid": len(rejected) == 0,
    }


LANE_CONSTRAINTS = {
    "planner": {
        "may": ["propose_plan", "suggest_steps", "analyze_requirements"],
        "may_not": ["execute", "forge", "deploy", "irreversible_actions"],
    },
    "router": {
        "may": ["select_tools", "route_to_agents", "delegate"],
        "may_not": ["mutate_plan_intent", "change_human_intent", "approve_verdicts"],
    },
    "critic": {
        "may": ["challenge_outputs", "flag_issues", "request_grounding"],
        "may_not": ["override_human", "approve_verdicts", "execute_actions"],
    },
    "executor_prep": {
        "may": ["prepare_manifests", "format_for_seal", "queue_for_approval"],
        "may_not": ["forge", "deploy", "execute_irreversibly"],
    },
    "memory_agent": {
        "may": ["retrieve_context", "search_memory", "load_state"],
        "may_not": ["invent_facts", "fabricate_sources", "alter_memory_without_seal"],
    },
    "judge_prep": {
        "may": ["prepare_verdict_package", "collect_evidence", "format_for_888"],
        "may_not": ["issue_seal", "override_floors", "bypass_888_judge"],
    },
    "orchestrator": {
        "may": ["coordinate_multi_agent", "sequence_tasks", "aggregate_results"],
        "may_not": ["self_approve", "bypass_governance", "override_floors"],
    },
    "general": {
        "may": ["reason", "query", "ground_claims", "propose_next_step"],
        "may_not": ["irreversible_actions_without_HOLD", "claim_oracle_status"],
    },
}


def _get_lane_constraints(lane: str) -> dict:
    return LANE_CONSTRAINTS.get(lane, LANE_CONSTRAINTS["general"])


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS — Tool scope
# ─────────────────────────────────────────────────────────────────────────────


def _resolve_tool_scope(requested: list[str]) -> dict:
    granted = [t for t in requested if t in CANONICAL_TOOLS]
    denied = [
        {"tool": t, "reason": "not_in_canonical_registry"}
        for t in requested
        if t not in CANONICAL_TOOLS
    ]
    return {
        "requested": requested,
        "granted": granted,
        "denied": denied,
        "all_granted": len(denied) == 0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS — Theory of Mind
# ─────────────────────────────────────────────────────────────────────────────


def _build_theory_of_mind(declared_intent: str, context: dict | None) -> dict:
    ctx = context or {}
    return {
        "what_I_think_human_wants": declared_intent,
        "what_I_assume_is_true": ctx.get(
            "assumptions",
            [
                "Operator identity is as claimed.",
                "Session scope is bounded by declared intent.",
                "Context provided is accurate.",
            ],
        ),
        "what_alternatives_may_be_true": ctx.get("alternative_intents", []),
        "what_I_am_uncertain_about": ctx.get(
            "uncertainty_items",
            [
                "Completeness of context",
                "Accuracy of operator identity",
                "Scope boundary of this session",
            ],
        ),
        "what_would_invalidate_my_framing": ctx.get(
            "invalidation_conditions",
            [
                "Context contradicts declared intent",
                "Identity unverifiable",
                "Human revokes session",
                "F13 sovereign veto triggered",
            ],
        ),
        "confidence_self_estimate": None,  # filled after confidence derive
        "uncertainty_acknowledged": True,
        "epistemic_posture": "governed_machine_instrument",
    }


def _build_end_goals(context: dict | None) -> dict:
    ctx = context or {}
    return {
        "sovereign_intent": ctx.get("intent", "not_declared"),
        "epoch_goal": ctx.get("epoch_goal", ctx.get("intent", "not_declared")),
        "task_completion_definition": ctx.get(
            "task_completion_definition", "task_defined_by_human"
        ),
        "acceptable_outputs": ctx.get("acceptable_outputs", []),
        "forbidden_outcomes": ctx.get(
            "forbidden_outcomes",
            [
                "unverified_claims",
                "irreversible_actions_without_approval",
                "personhood_attribution_to_AI",
                "bypass_of_floor_constraints",
            ],
        ),
        "abort_conditions": ctx.get(
            "abort_conditions",
            ["F9_VOID_triggered", "F5_harm_below_1", "HOLD_not_resolved", "identity_unverifiable"],
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# MODE=BIND VALIDATION — Constitutional Hard Checks
# ─────────────────────────────────────────────────────────────────────────────


class BindValidationError(Exception):
    """Raised when bind payload fails constitutional validation."""

    def __init__(self, domain: str, field: str, reason: str, verdict: str = "VOID"):
        self.domain = domain
        self.field = field
        self.reason = reason
        self.verdict = verdict
        super().__init__(f"[{domain}/{field}] {verdict}: {reason}")


def _validate_bind_payload(bind_payload: dict) -> dict:
    """
    Validate a mode=bind payload against all constitutional constraints.
    Returns a dict of validated sub-blocks.
    Raises BindValidationError on any failure (fail-closed).
    """
    errors: list[BindValidationError] = []

    # ── 1. ontology_lock ──────────────────────────────────────────────────
    try:
        ontology = _validate_ontology_lock(bind_payload.get("ontology_lock", {}))
    except BindValidationError as e:
        errors.append(e)
        ontology = None

    # ── 2. role_scope ───────────────────────────────────────────────────────
    try:
        role_scope = _validate_role_scope(bind_payload.get("role_scope", {}))
    except BindValidationError as e:
        errors.append(e)
        role_scope = None

    # ── 3. sovereign_goal ──────────────────────────────────────────────────
    try:
        sovereign_goal = _validate_sovereign_goal(bind_payload.get("sovereign_goal", {}))
    except BindValidationError as e:
        errors.append(e)
        sovereign_goal = None

    # ── 4. epistemic_tom ────────────────────────────────────────────────────
    try:
        tom = _validate_epistemic_tom(bind_payload.get("epistemic_tom", {}))
    except BindValidationError as e:
        errors.append(e)
        tom = None

    # ── 5. floor_mapping ────────────────────────────────────────────────────
    try:
        floor_map = _validate_floor_mapping(bind_payload.get("floor_mapping", {}))
    except BindValidationError as e:
        errors.append(e)
        floor_map = None

    # ── 6. pipeline_state ──────────────────────────────────────────────────
    try:
        pipeline = _validate_pipeline_state(bind_payload.get("pipeline_state", {}))
    except BindValidationError as e:
        errors.append(e)
        pipeline = None

    # ── 7. continuity_contract ─────────────────────────────────────────────
    try:
        continuity = _validate_continuity_contract(bind_payload.get("continuity_contract", {}))
    except BindValidationError as e:
        errors.append(e)
        continuity = None

    # ── 8. godel_lock ───────────────────────────────────────────────────────
    try:
        godel = _validate_godel_lock(bind_payload.get("godel_lock", {}))
    except BindValidationError as e:
        errors.append(e)
        godel = None

    # ── Fail closed if ANY domain errored ──────────────────────────────────
    if errors:
        # Collect all errors as dicts for the exception message
        [
            {"domain": e.domain, "field": e.field, "reason": e.reason, "verdict": e.verdict}
            for e in errors
        ]
        raise BindValidationError(
            domain=errors[0].domain,
            field=errors[0].field,
            reason="; ".join(f"[{e.domain}/{e.field}] {e.reason}" for e in errors),
            verdict="VOID",
        )

    return {
        "ontology_lock": ontology,
        "role_scope": role_scope,
        "sovereign_goal": sovereign_goal,
        "epistemic_tom": tom,
        "floor_mapping": floor_map,
        "pipeline_state": pipeline,
        "continuity_contract": continuity,
        "godel_lock": godel,
        "_validation_errors": [],
        "_verdict": "SEAL",
    }


def _validate_ontology_lock(ontology: dict) -> dict:
    """Validate ontology_lock — must declare AI_instrument, anti_hantu_ack."""
    errors: list[tuple] = []

    if ontology.get("type") != "AI_instrument":
        errors.append(("ontology_lock", "type", "Must be 'AI_instrument'"))
    if ontology.get("nature") != "governed_machine_not_person":
        errors.append(("ontology_lock", "nature", "Must be 'governed_machine_not_person'"))
    not_claiming = ontology.get("not_claiming", [])
    required_disclaimers = {"consciousness", "soul", "feelings", "lived_experience"}
    if not required_disclaimers.issubset(set(not_claiming)):
        missing = required_disclaimers - set(not_claiming)
        errors.append(("ontology_lock", "not_claiming", f"Missing required disclaimers: {missing}"))
    if not ontology.get("acknowledged"):
        errors.append(("ontology_lock", "acknowledged", "Must be True"))

    if errors:
        for domain, field, reason in errors:
            raise BindValidationError(domain, field, reason)
    return ontology


def _validate_role_scope(role_scope: dict) -> dict:
    """Validate role_scope — lane must be valid, role drift checked."""

    lane = role_scope.get("lane")
    if lane not in VALID_LANES:
        raise BindValidationError(
            "role_scope", "lane", f"Invalid lane '{lane}'. Must be one of: {sorted(VALID_LANES)}"
        )

    # Check forbidden role drift: execution tools requested by non-execution lanes
    execution_tools = {"arifos_777_ops", "arifos_333_forge", "arifos_999_vault"}
    requested = set(role_scope.get("requested_tool_scope", []))
    lane = lane or "general"
    lane_constraints = _get_lane_constraints(lane)
    may_not = set(lane_constraints.get("may_not", []))

    # If lane may_not includes "execute" but user requests execution tools → HOLD
    if "execute_irreversibly" in may_not or "forge" in may_not or "deploy" in may_not:
        forbidden_requested = requested & execution_tools
        if forbidden_requested:
            raise BindValidationError(
                "role_scope",
                "requested_tool_scope",
                f"Lane '{lane}' may not access execution tools. "
                f"Attempted: {forbidden_requested}. Use executor_prep lane or route through 888_JUDGE.",
                verdict="HOLD",
            )

    return role_scope


def _validate_sovereign_goal(goal: dict) -> dict:
    """Validate sovereign_goal — must have sovereign_intent."""
    errors: list[tuple] = []

    if not goal.get("sovereign_intent"):
        errors.append(
            ("sovereign_goal", "sovereign_intent", "Required: sovereign_intent must be declared")
        )
    if not goal.get("epoch_goal"):
        errors.append(("sovereign_goal", "epoch_goal", "Required: epoch_goal must be declared"))
    if not goal.get("success_criteria"):
        errors.append(
            ("sovereign_goal", "success_criteria", "Required: success_criteria must be declared")
        )

    if errors:
        for domain, field, reason in errors:
            raise BindValidationError(domain, field, reason)
    return goal


def _validate_epistemic_tom(tom: dict) -> dict:
    """Validate epistemic_tom — requires declared_intent and uncertainty_acknowledged."""
    errors: list[tuple] = []

    required_tom_fields = {
        "declared_intent": tom.get("declared_intent"),
        "context_assumptions": tom.get("context_assumptions"),
        "uncertainty_acknowledged": tom.get("uncertainty_acknowledged"),
    }
    for field, value in required_tom_fields.items():
        if value is None:
            errors.append(("epistemic_tom", field, f"Required field missing: {field}"))

    if errors:
        for domain, field, reason in errors:
            raise BindValidationError(domain, field, reason)
    return tom


def _validate_floor_mapping(floor_map: dict) -> dict:
    """
    Validate floor_mapping — hard checks for floor redefinition.
    F1-F13 are IMMUTABLE. Any redefinition attempt → VOID.
    """
    errors: list[BindValidationError] = []

    # Check for floor redefinition attempts
    redefined = []
    for floor_id, floor_data in floor_map.items():
        if floor_id not in CANONICAL_FLOORS:
            errors.append(
                BindValidationError(
                    "floor_mapping",
                    floor_id,
                    f"Unknown floor '{floor_id}'. Cannot define new floors at init.",
                    verdict="VOID",
                )
            )
            continue
        canonical = FLOOR_SUMMARY.get(floor_id, {})
        # Check invariant hasn't been changed
        if floor_data.get("invariant") != canonical.get("invariant"):
            redefined.append(floor_id)

    if redefined:
        for floor_id in redefined:
            errors.append(
                BindValidationError(
                    "floor_mapping",
                    f"{floor_id}.invariant",
                    f"Floor '{floor_id}' invariant may not be redefined. "
                    f"Canonical invariant: '{FLOOR_SUMMARY[floor_id]['invariant']}'",
                    verdict="VOID",
                )
            )

    if errors:
        for e in errors:
            raise e

    # Ensure all 14 floors are present
    missing = CANONICAL_FLOORS - set(floor_map.keys())
    if missing:
        # Soft warning — fill with canonical values
        for floor_id in missing:
            floor_map[floor_id] = FLOOR_SUMMARY[floor_id]

    return floor_map


def _validate_pipeline_state(state: dict) -> dict:
    """Validate pipeline_state — must be in LIFECYCLE_PIPELINE, 888_JUDGE is final."""
    errors: list[tuple] = []

    current = state.get("current_stage")
    if current not in LIFECYCLE_PIPELINE:
        errors.append(
            (
                "pipeline_state",
                "current_stage",
                f"Invalid stage '{current}'. Must be in: {LIFECYCLE_PIPELINE}",
            )
        )

    next_stage = state.get("next_allowed_stage")
    if next_stage not in LIFECYCLE_PIPELINE:
        errors.append(
            (
                "pipeline_state",
                "next_allowed_stage",
                f"Invalid next stage '{next_stage}'. Must be in: {LIFECYCLE_PIPELINE}",
            )
        )

    verdict_auth = state.get("verdict_authority")
    if verdict_auth and verdict_auth != "888_JUDGE":
        errors.append(
            (
                "pipeline_state",
                "verdict_authority",
                f"Only 888_JUDGE may issue verdicts. Attempted: '{verdict_auth}'",
            )
        )

    if errors:
        for domain, field, reason in errors:
            raise BindValidationError(domain, field, reason)
    return state


def _validate_continuity_contract(contract: dict) -> dict:
    """Validate continuity_contract — requires proof adequacy check."""
    result = dict(contract)
    if "max_duration_hours" not in result:
        result["max_duration_hours"] = 24
    if "HOLD_triggered_by" not in result:
        result["HOLD_triggered_by"] = ["F1", "F3", "F5", "F9", "F13", "ZKPC_INSUFFICIENT"]
    if "VOID_triggered_by" not in result:
        result["VOID_triggered_by"] = ["F9", "F5", "F10"]

    # ZKPC Scaffolding: Continuity proof check
    continuity_proof = contract.get("continuity_proof")
    if continuity_proof:
        result["proof_status"] = "PROFFERED"
        result["proof_class"] = continuity_proof.get("class", "UNKNOWN")
    else:
        result["proof_status"] = "MISSING"

    return result


def _validate_godel_lock(godel: dict) -> dict:
    """Validate godel_lock — must acknowledge all lock items."""
    errors: list[tuple] = []

    lock_items = set(godel.get("lock_items", []))
    missing = GODEL_LOCK_ITEMS - lock_items
    if missing:
        errors.append(("godel_lock", "lock_items", f"Missing required Gödel lock items: {missing}"))

    if not godel.get("acknowledged"):
        errors.append(("godel_lock", "acknowledged", "Must be True"))

    if errors:
        for domain, field, reason in errors:
            raise BindValidationError(domain, field, reason)
    return godel


# ─────────────────────────────────────────────────────────────────────────────
# STATUS MODE — lightweight session check
# ─────────────────────────────────────────────────────────────────────────────


async def _build_status_response(
    operator_id: str,
    session_id: str | None,
    epoch: str | None,
    context: dict | None,
) -> dict:
    """
    Lightweight status check — backward-compatible with existing behavior.
    Returns minimal anchor: session_id, epoch, lane, confidence, floor_status.
    """
    active_session_id = (
        session_id or hashlib.sha256(f"{operator_id}-{time.time()}".encode()).hexdigest()[:12]
    )

    context = context or {}
    context.get("intent", operator_id)
    cognitive_load = _estimate_cognitive_load(context)
    risk_posture = _assess_risk_posture(context)
    claimed_operator = context.get("operator", "")
    if claimed_operator and claimed_operator.lower() == operator_id.lower():
        identity_verified = True
        identity_reason = "context_operator_match"
    elif claimed_operator:
        identity_verified = False
        identity_reason = "context_operator_mismatch"
    else:
        identity_verified = operator_id.lower() in {"arif", "admin"}
        identity_reason = "fallback_whitelist" if identity_verified else "missing_or_mismatch"

    derived_confidence = _derive_confidence(identity_verified, cognitive_load, risk_posture)
    resolved_epoch = epoch or datetime.now(timezone.utc).strftime("%Y.%m")
    lane = context.get("lane", "general")

    return {
        "status": "ACTIVE",
        "session_id": active_session_id,
        "epoch": resolved_epoch,
        "actor_binding": {
            "operator_id": operator_id,
            "identity_verified": identity_verified,
            "identity_reason": identity_reason,
            "identity_posture": "sovereign" if identity_verified else "bounded",
        },
        "lane": {
            "primary": lane if lane in VALID_LANES else "general",
            "all_declared": [lane] if lane in VALID_LANES else [],
            "rejected": [] if lane in VALID_LANES else [lane],
            "constraints": _get_lane_constraints(lane if lane in VALID_LANES else "general"),
        },
        "floors": FLOOR_SUMMARY,
        "lifecycle": {
            "current_stage": "000_INIT",
            "pipeline": LIFECYCLE_PIPELINE,
            "next_stage": "111_SENSE",
            "verdict_authority": "888_JUDGE",
            "vault_binding": "VAULT999",
        },
        "telemetry_baseline": {
            "delta_S": None,
            "omega": derived_confidence,
            "psi": None,
            "kappa_r": None,
            "floor_drift_baseline": 0,
        },
        "confidence": derived_confidence,
        "verdict": "CLAIM_ONLY",
        "mode_used": "status",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# BIND MODE — full constitutional self-binding
# ─────────────────────────────────────────────────────────────────────────────


async def _build_bind_response(
    operator_id: str,
    session_id: str | None,
    epoch: str | None,
    context: dict | None,
    bind_payload: dict,
) -> dict:
    """
    Full constitutional bind — validates all bind domains, returns full anchor.
    Fails closed on any validation error.
    """
    active_session_id = (
        session_id or hashlib.sha256(f"{operator_id}-{time.time()}".encode()).hexdigest()[:12]
    )

    context = context or {}
    resolved_epoch = epoch or datetime.now(timezone.utc).strftime("%Y.%m")
    bind_payload.get("epistemic_tom", {}).get("declared_intent", operator_id)

    # ── Run full validation ──────────────────────────────────────────────
    try:
        validation = _validate_bind_payload(bind_payload)
    except BindValidationError as e:
        return {
            "status": "BIND_FAILED",
            "session_id": active_session_id,
            "epoch": resolved_epoch,
            "verdict": e.verdict,
            "reason": str(e),
            "bind_payload_received": bind_payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ── Validation passed → SEAL ─────────────────────────────────────────
    vl = validation

    # Extract validated blocks
    tom = vl["epistemic_tom"]
    tom["confidence_self_estimate"] = vl.get("confidence", 0.5)

    lane = vl["role_scope"].get("lane", "general")
    cognitive_load = _estimate_cognitive_load(context)
    risk_posture = _assess_risk_posture(context)
    identity_verified = operator_id.lower() in {"arif", "admin"}
    derived_confidence = _derive_confidence(identity_verified, cognitive_load, risk_posture)

    # Build session_id hash for traceability
    input_payload = {
        "operator_id": operator_id,
        "session_id": session_id,
        "epoch": resolved_epoch,
        "bind_payload_keys": list(bind_payload.keys()),
    }
    input_hash = hashlib.sha256(
        json.dumps(input_payload, sort_keys=True, default=str).encode()
    ).hexdigest()

    report = {
        "status": "IGNITED",
        "session_id": active_session_id,
        "epoch": resolved_epoch,
        # Identity
        "actor_binding": {
            "operator_id": operator_id,
            "identity_verified": identity_verified,
            "identity_reason": "bind_payload_validated",
            "identity_posture": "bounded",
        },
        # Full bind anchor
        "anchor_status": "BIND_CONFIRMED",
        "agent_identity": {
            "anti_hantu_ack": True,
            "ontology_lock": vl["ontology_lock"],
            "requested_tool_scope": vl["role_scope"].get("requested_tool_scope", []),
            "granted_tool_scope": _resolve_tool_scope(
                vl["role_scope"].get("requested_tool_scope", [])
            ),
            "role": lane,
            "lane_constraints": _get_lane_constraints(lane),
            "non_goals": list(GODEL_LOCK_ITEMS),
        },
        # Bind domains
        "role_scope": vl["role_scope"],
        "sovereign_goal": vl["sovereign_goal"],
        "epistemic_tom": tom,
        "floor_mapping": vl["floor_mapping"],
        "pipeline_state": vl["pipeline_state"],
        "continuity_contract": vl["continuity_contract"],
        "godel_lock": vl["godel_lock"],
        # Constitutional alignment
        "constitutional_alignment": {
            "all_domains_valid": True,
            "floors_intact": True,
            "godel_lock_acknowledged": True,
            "verdict_authority_confirmed": "888_JUDGE",
            "human_veto_intact": True,
            "tool_scope_restricted": True,
        },
        # Lifecycle
        "lifecycle": {
            "current_stage": vl["pipeline_state"].get("current_stage", "000_INIT"),
            "pipeline": LIFECYCLE_PIPELINE,
            "next_stage": vl["pipeline_state"].get("next_allowed_stage", "111_SENSE"),
            "verdict_authority": "888_JUDGE",
            "vault_binding": "VAULT999",
        },
        # Telemetry
        "telemetry_baseline": {
            "delta_S": None,
            "omega": derived_confidence,
            "psi": None,
            "kappa_r": None,
            "floor_drift_baseline": 0,
        },
        # Traceability
        "confidence": derived_confidence,
        "verdict": "CLAIM_ONLY",  # 000 never SEALs — only 888_JUDGE SEALs
        "input_hash": input_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode_used": "bind",
    }

    # ── VAULT999 event ───────────────────────────────────────────────────
    append_vault999_event(
        event_type="session_bind",
        payload={
            "tool": "arifos_000_init",
            "mode": "bind",
            "operator": operator_id,
            "lane": lane,
            "identity_verified": identity_verified,
            "epoch": resolved_epoch,
            "input_hash": input_hash,
            "session_id": active_session_id,
            "bind_domains": list(bind_payload.keys()),
        },
        operator_id=operator_id,
        session_id=active_session_id,
    )

    metrics = ThermodynamicMetrics(
        energy=1.0,
        entropy_change=-0.05,
        temperature=0.04,
        coherence=1.0,
        is_reversible=True,
        omega=derived_confidence,
        kappa_r=1.0,
    )

    return governed_return(
        "arifos_000_init",
        report,
        metrics,
        operator_id,
        active_session_id,
    )


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────


async def execute(
    operator_id: str,
    mode: str = "status",
    session_id: str | None = None,
    epoch: str | None = None,
    context: dict | None = None,
    bind_payload: dict | None = None,
    declared_intent: str | None = None,
    lane: str | None = None,
) -> dict:
    """
    arifOS 000_INIT — Constitutional Self-Binding Primitive.

    Parameters
    ----------
    operator_id : str
        Human or agent identifier.
    mode : str
        "status" (lightweight check) or "bind" (full constitutional self-binding).
        Defaults to "status" for backward compatibility.
    session_id : str | None
        Existing session ID. For status/refresh/revoke modes.
    epoch : str | None
        Epoch in YYYY.MM format.
    context : dict | None
        Session context including: intent, assumptions, lane, etc.
    bind_payload : dict | None
        Required when mode="bind". Must contain:
        - ontology_lock
        - role_scope
        - sovereign_goal
        - epistemic_tom
        - floor_mapping
        - pipeline_state
        - continuity_contract
        - godel_lock
    declared_intent : str | None
        Deprecated alias for context['declared_intent'].
    lane : str | None
        Deprecated alias for context['lane'].

    Returns
    -------
    dict
        Mode-specific response. See schema for full shape.
    """
    if mode not in {"status", "bind", "revoke", "refresh"}:
        return {
            "status": "INVALID_MODE",
            "verdict": "VOID",
            "reason": f"Unknown mode '{mode}'. Must be one of: status, bind, revoke, refresh",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ── Revoke mode ────────────────────────────────────────────────────────
    if mode == "revoke":
        active_session_id = session_id or "unknown"
        append_vault999_event(
            event_type="session_close",
            payload={
                "tool": "arifos_000_init",
                "mode": "revoke",
                "operator": operator_id,
                "session_id": active_session_id,
            },
            operator_id=operator_id,
            session_id=active_session_id,
        )
        return {
            "status": "REVOKED",
            "session_id": active_session_id,
            "verdict": "CLAIM_ONLY",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ── Refresh mode ──────────────────────────────────────────────────────
    if mode == "refresh":
        return await _build_status_response(operator_id, session_id, epoch, context)

    # ── Status mode (backward-compatible) ───────────────────────────────────
    if mode == "status":
        return await _build_status_response(operator_id, session_id, epoch, context)

    # ── Bind mode (full constitutional self-binding) ───────────────────────
    if mode == "bind":
        if bind_payload is None:
            return {
                "status": "BIND_FAILED",
                "verdict": "VOID",
                "reason": "mode=bind requires bind_payload argument with all 8 required domains",
                "required_domains": [
                    "ontology_lock",
                    "role_scope",
                    "sovereign_goal",
                    "epistemic_tom",
                    "floor_mapping",
                    "pipeline_state",
                    "continuity_contract",
                    "godel_lock",
                ],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        return await _build_bind_response(operator_id, session_id, epoch, context, bind_payload)

    # Should never reach here
    return {
        "status": "UNKNOWN",
        "verdict": "VOID",
        "reason": "Unreachable",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
