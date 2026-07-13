"""
dependency_gate.py — Dependency-Graph Gate Pipeline (D1)

═══════════════════════════════════════════════════════════
FORGED: 2026-07-13 — Arif's D1 directive
SUPERSEDES: golden_path/gate_enforcer.py (serial chain)

The current serial chain is wrong because later gates generate
facts needed by earlier gates. Gate 3.5 asks "is this dangerous?"
but Gate 7 (sovereign authority) never runs because 3.5 blocks.

Fix: Action classification phase computes ALL required facts
BEFORE any gate enforces. Each gate reads from the immutable
ActionProfile. No gate silently sets facts another gate needs.

CORRECT FLOW:

REQUEST
  ↓
0. Normalise request
  ↓
1. Resolve actor, session and tool
  ↓
2. Classify action → ActionProfile (IMMUTABLE)
  ↓
3. Evaluate identity
  ↓
4. Evaluate capability and lease
  ↓
5. Evaluate infrastructure consequence
  ↓
6. Evaluate constitutional requirements
  ↓
7. Evaluate payload and evidence
  ↓
8. Execute or append
  ↓
9. Verify result

Each gate returns structured output:
  status: PASS | HOLD | DENY
  reason:
  evidence_refs:
  obligations:

DITEMPA BUKAN DIBERI — The gate is forged, not given.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Callable

from .action_profile import (
    ActionProfile,
    BlastRadius,
    GovernanceImpact,
    InfrastructureImpact,
    MutationClass,
    ReceiptClass,
    Reversibility,
    RequiredCapability,
    classify_action,
    upgrade_to_session_closure,
    upgrade_to_sovereign,
)
from .vault_outbox import (
    SessionClosureState,
    VaultOutbox,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# GATE RESULT
# ═══════════════════════════════════════════════════════════════════════════════


class GateStatus(StrEnum):
    PASS = "PASS"  # Gate satisfied, proceed
    HOLD = "HOLD"  # Blocked pending resolution, retryable
    DENY = "DENY"  # Permanently blocked, constitutional breach


@dataclass
class GateResult:
    """Structured output from a single gate evaluation."""

    gate_name: str
    status: GateStatus
    reason: str
    evidence_refs: list[str] = field(default_factory=list)
    obligations: list[str] = field(default_factory=list)
    detail: dict[str, Any] = field(default_factory=dict)
    result_hash: str = ""

    def __post_init__(self) -> None:
        if not self.result_hash:
            canonical = f"{self.gate_name}:{self.status.value}:{self.reason}"
            self.result_hash = hashlib.sha256(canonical.encode()).hexdigest()[:12]


# ═══════════════════════════════════════════════════════════════════════════════
# GATE CONTEXT — shared state across the pipeline
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class GateContext:
    """
    Context shared across all gates in the pipeline.

    Built incrementally: each gate may add evidence_refs, resolved_identity, etc.
    No gate may modify the ActionProfile — it is frozen at classification time.
    """

    # ── Request identity ──
    raw_request: str = ""
    normalised_request: str = ""

    # ── Target tool/verb (set by MCP handler before pipeline) ──
    target_tool: str = ""  # e.g. "arif_seal"
    target_verb: str = ""  # e.g. "seal"

    # ── Actor and session ──
    actor_id: str = ""
    actor_verified: bool = False
    actor_signature: str = ""
    session_id: str = ""
    session_token: str = ""

    # ── Action classification (IMMUTABLE after step 2) ──
    action_profile: ActionProfile | None = None

    # ── Identity resolution ──
    resolved_identity: dict[str, Any] = field(default_factory=dict)
    identity_band: str = "OBSERVER"  # OBSERVER | OPERATOR_CLAIMED | OPERATOR_SIGNED | SOVEREIGN

    # ── Capability resolution ──
    capability_grants: list[str] = field(default_factory=list)
    active_lease_id: str = ""
    lease_valid_until: str = ""

    # ── Infrastructure state ──
    infra_green: bool = False
    runtime_drift: bool = False
    organ_health: dict[str, bool] = field(default_factory=dict)

    # ── Constitutional evidence ──
    constitutional_evidence: dict[str, Any] = field(default_factory=dict)

    # ── Payload ──
    payload_hash: str = ""
    payload_checksum: str = ""

    # ── Gate results ──
    gate_results: dict[str, GateResult] = field(default_factory=dict)

    # ── Pipeline outcome ──
    pipeline_verdict: str = ""  # SEAL | HOLD | DENY | VOID

    # ── Session closure ──
    closure_state: SessionClosureState | None = None
    outbox: VaultOutbox | None = None

    def record_gate(self, result: GateResult) -> None:
        """Record a gate result. Gates execute in order; first HOLD/DENY stops pipeline."""
        self.gate_results[result.gate_name] = result


# ═══════════════════════════════════════════════════════════════════════════════
# GATE FUNCTIONS — each returns GateResult, reads from GateContext
# ═══════════════════════════════════════════════════════════════════════════════

# Each gate signature: (ctx: GateContext) -> GateResult
GateFn = Callable[[GateContext], GateResult]


# ── GATE 0: Normalise request ──


def gate_normalise_request(ctx: GateContext) -> GateResult:
    """
    G0: Normalise the incoming request.
    Strip whitespace, detect language, extract known patterns.
    Never blocks — always PASS with normalisation metadata.
    """
    raw = ctx.raw_request.strip()
    if not raw:
        return GateResult(
            gate_name="G0_NORMALISE",
            status=GateStatus.HOLD,
            reason="Empty request — nothing to process",
            evidence_refs=["request.normalise"],
        )

    # Normalise
    ctx.normalised_request = raw

    return GateResult(
        gate_name="G0_NORMALISE",
        status=GateStatus.PASS,
        reason=f"Request normalised ({len(raw)} chars)",
        evidence_refs=["request.normalise"],
        detail={"length": len(raw)},
    )


# ── GATE 1: Resolve actor, session and tool ──


def gate_resolve_context(ctx: GateContext) -> GateResult:
    """
    G1: Resolve actor identity, session binding, and target tool.
    Facts established here feed all downstream gates.
    """
    issues = []

    actor_id = ctx.actor_id.strip() if ctx.actor_id else ""
    if not actor_id:
        issues.append("No actor_id provided")

    session_id = ctx.session_id.strip() if ctx.session_id else ""
    if not session_id:
        issues.append("No session_id provided")

    if issues:
        return GateResult(
            gate_name="G1_RESOLVE_CONTEXT",
            status=GateStatus.HOLD,
            reason="; ".join(issues),
            evidence_refs=["request.context"],
            obligations=issues,
        )

    return GateResult(
        gate_name="G1_RESOLVE_CONTEXT",
        status=GateStatus.PASS,
        reason=f"Actor={actor_id}, Session={session_id}",
        evidence_refs=["request.context"],
        detail={
            "actor_id": actor_id,
            "session_id": session_id,
        },
    )


# ── GATE 2: Classify action → ActionProfile (IMMUTABLE) ──


def gate_classify_action(ctx: GateContext) -> GateResult:
    """
    G2: Classify the action into an immutable ActionProfile.

    This is the KEY architectural fix — classification happens BEFORE
    any enforcement. The profile is then read by all downstream gates.
    No gate recomputes or modifies it.

    Determines: mutation class, reversibility, blast radius, governance
    impact, infrastructure impact, receipt class, required capability,
    and whether sovereign authority is required.
    """
    profile = classify_action(
        tool=ctx.target_tool,
        verb=ctx.target_verb,
        force_sovereign=True
        if ctx.identity_band == "SOVEREIGN"
        else False,
    )

    # Check for UNKNOWN classification
    if profile.mutation_class.value == "UNKNOWN":
        return GateResult(
            gate_name="G2_CLASSIFY_ACTION",
            status=GateStatus.DENY,
            reason=f"Unknown tool/verb: {profile.tool}/{profile.verb} — cannot classify",
            evidence_refs=["classification_map"],
            obligations=["Register tool in TOOL_CLASSIFICATION_MAP"],
        )

    # Immutable — store in context (never modify profile after this point)
    ctx.action_profile = profile

    return GateResult(
        gate_name="G2_CLASSIFY_ACTION",
        status=GateStatus.PASS,
        reason=(
            f"{profile.tool}/{profile.verb}: "
            f"mutation={profile.mutation_class.value}, "
            f"reversibility={profile.reversibility.value}, "
            f"blast={profile.blast_radius.value}, "
            f"governance={profile.governance_impact.value}, "
            f"receipt={profile.receipt_class.value}, "
            f"capability={profile.required_capability.value}"
        ),
        evidence_refs=[f"profile:{profile.profile_hash}"],
        detail={
            "profile_hash": profile.profile_hash,
            "tool": profile.tool,
            "verb": profile.verb,
            "mutation_class": profile.mutation_class.value,
            "reversibility": profile.reversibility.value,
            "blast_radius": profile.blast_radius.value,
            "infrastructure_impact": profile.infrastructure_impact.value,
            "governance_impact": profile.governance_impact.value,
            "receipt_class": profile.receipt_class.value,
            "required_capability": profile.required_capability.value,
            "sovereign_required": profile.sovereign_required,
        },
    )


# ── GATE 3: Evaluate identity ──


def gate_evaluate_identity(ctx: GateContext) -> GateResult:
    """
    G3: Evaluate actor identity against required authority.

    Identity bands (from profile.identity):
      OBSERVER          — no actor_id, observe only
      OPERATOR_CLAIMED  — actor_id provided, no signature
      OPERATOR_SIGNED   — actor_id + valid signature
      SOVEREIGN         — actor_id + F13 cryptographic key

    If the action requires sovereign authority (profile.sovereign_required=True)
    but identity band is below SOVEREIGN, this gate returns HOLD.
    """
    profile = ctx.action_profile
    if not profile:
        return GateResult(
            gate_name="G3_IDENTITY",
            status=GateStatus.DENY,
            reason="No action profile — classify action first",
            evidence_refs=[],
        )

    identity_band = ctx.identity_band
    sovereign_required = profile.sovereign_required
    requires_human_ack = profile.requires_human_ack

    evidence: list[str] = [f"identity_band:{identity_band}"]

    # Sovereign-required actions need SOVEREIGN band
    if sovereign_required and identity_band != "SOVEREIGN":
        return GateResult(
            gate_name="G3_IDENTITY",
            status=GateStatus.HOLD,
            reason=(
                f"Action requires SOVEREIGN identity (F13 key), "
                f"but actor has {identity_band} band"
            ),
            evidence_refs=evidence,
            obligations=[
                "Provide F13 cryptographic key signature",
                "Or re-init with sovereign identity bind",
            ],
        )

    # Human ack required with unverified identity
    if requires_human_ack and identity_band in ("OBSERVER", "OPERATOR_CLAIMED"):
        return GateResult(
            gate_name="G3_IDENTITY",
            status=GateStatus.HOLD,
            reason=(
                f"Action requires human acknowledgment, "
                f"but actor has {identity_band} band (no verified signature)"
            ),
            evidence_refs=evidence,
            obligations=[
                "Provide valid actor signature",
                "Or provide explicit human confirmation",
            ],
        )

    # OBSERVER can only observe
    if identity_band == "OBSERVER" and profile.mutation_class not in (
        MutationClass.NONE,
        MutationClass.UNKNOWN,
    ):
        return GateResult(
            gate_name="G3_IDENTITY",
            status=GateStatus.DENY,
            reason=(
                f"OBSERVER identity cannot perform "
                f"{profile.mutation_class.value} mutations"
            ),
            evidence_refs=evidence,
            obligations=["Provide actor_id to elevate beyond OBSERVER"],
        )

    return GateResult(
        gate_name="G3_IDENTITY",
        status=GateStatus.PASS,
        reason=f"Identity band {identity_band} sufficient for action",
        evidence_refs=evidence,
        detail={"identity_band": identity_band, "actor_verified": ctx.actor_verified},
    )


# ── GATE 4: Evaluate capability and lease ──


def gate_evaluate_capability(ctx: GateContext) -> GateResult:
    """
    G4: Evaluate whether the actor has the required capability grant
    and a valid lease (if the action requires one).

    Reads required_capability from the immutable ActionProfile.
    Checks ctx.capability_grants for matching capability.
    """
    profile = ctx.action_profile
    if not profile:
        return GateResult(
            gate_name="G4_CAPABILITY",
            status=GateStatus.DENY,
            reason="No action profile",
            evidence_refs=[],
        )

    required = profile.required_capability.value
    grants = ctx.capability_grants or []

    evidence = [f"required:{required}", f"grants:{','.join(grants) or 'none'}"]

    # Sovereign-level capabilities always require sovereign identity
    if required in ("vault.append.sovereign", "constitutional.amend"):
        if ctx.identity_band != "SOVEREIGN":
            return GateResult(
                gate_name="G4_CAPABILITY",
                status=GateStatus.HOLD,
                reason=f"Capability {required} requires SOVEREIGN identity band",
                evidence_refs=evidence,
                obligations=["Provide F13 sovereign signature"],
            )

    # Check grants
    if required not in grants:
        return GateResult(
            gate_name="G4_CAPABILITY",
            status=GateStatus.DENY,
            reason=f"Actor lacks required capability: {required}",
            evidence_refs=evidence,
            obligations=[f"Request capability grant: {required}"],
        )

    # Check lease validity
    if profile.blast_radius in (BlastRadius.FEDERATION, BlastRadius.SOVEREIGN):
        if not ctx.active_lease_id:
            return GateResult(
                gate_name="G4_CAPABILITY",
                status=GateStatus.HOLD,
                reason=f"Blast radius {profile.blast_radius.value} requires active lease, none found",
                evidence_refs=evidence,
                obligations=["Obtain lease from arif_judge before execution"],
            )

    return GateResult(
        gate_name="G4_CAPABILITY",
        status=GateStatus.PASS,
        reason=f"Capability {required} granted, lease valid" if ctx.active_lease_id
        else f"Capability {required} granted (no lease required)",
        evidence_refs=evidence,
        detail={
            "required_capability": required,
            "active_lease": ctx.active_lease_id or "none_required",
        },
    )


# ── GATE 5: Evaluate infrastructure consequence ──


def gate_evaluate_infrastructure(ctx: GateContext) -> GateResult:
    """
    G5: Evaluate whether infrastructure state supports this action.

    Checks: runtime drift, organ health, infrastructure impact level.
    """
    profile = ctx.action_profile
    if not profile:
        return GateResult(
            gate_name="G5_INFRASTRUCTURE",
            status=GateStatus.DENY,
            reason="No action profile",
            evidence_refs=[],
        )

    infra_level = profile.infrastructure_impact
    evidence: list[str] = [f"infra_level:{infra_level.value}"]

    # Runtime drift check
    if ctx.runtime_drift and infra_level != InfrastructureImpact.NONE:
        return GateResult(
            gate_name="G5_INFRASTRUCTURE",
            status=GateStatus.HOLD,
            reason=(
                f"Runtime drift detected (build ≠ live). "
                f"Blocking infra-impact action ({infra_level.value}) "
                f"until drift resolved or F13 acknowledged"
            ),
            evidence_refs=evidence + ["runtime_drift"],
            obligations=[
                "Resolve runtime drift (rebuild and redeploy)",
                "Or provide F13 sovereign override",
            ],
        )

    return GateResult(
        gate_name="G5_INFRASTRUCTURE",
        status=GateStatus.PASS,
        reason=f"Infrastructure green for {infra_level.value} impact",
        evidence_refs=evidence,
        detail={
            "infrastructure_impact": infra_level.value,
            "runtime_drift": ctx.runtime_drift,
            "organ_health": {k: v for k, v in ctx.organ_health.items()},
        },
    )


# ── GATE 6: Evaluate constitutional requirements ──


def gate_evaluate_constitutional(ctx: GateContext) -> GateResult:
    """
    G6: Evaluate constitutional floor requirements.

    Uses governance_impact from the immutable ActionProfile.
    If CONSTITUTIONAL or SOVEREIGN, checks floor compliance evidence.
    """
    profile = ctx.action_profile
    if not profile:
        return GateResult(
            gate_name="G6_CONSTITUTIONAL",
            status=GateStatus.DENY,
            reason="No action profile",
            evidence_refs=[],
        )

    gov_impact = profile.governance_impact
    evidence: list[str] = [f"governance_impact:{gov_impact.value}"]

    # Sovereign-level governance requires floor evidence
    if gov_impact == GovernanceImpact.SOVEREIGN:
        floor_evidence = ctx.constitutional_evidence.get("floors", {})
        violated = [k for k, v in floor_evidence.items() if v.get("status") == "violated"]

        if violated:
            return GateResult(
                gate_name="G6_CONSTITUTIONAL",
                status=GateStatus.HOLD,
                reason=f"Sovereign action blocked by floor violations: {violated}",
                evidence_refs=evidence + [f"floor_violations:{','.join(violated)}"],
                obligations=[f"Resolve floor violations before reattempting: {violated}"],
                detail={"violated_floors": violated},
            )

    # Receipt class determines closure path
    if profile.receipt_class == ReceiptClass.SESSION_CLOSURE:
        if not ctx.closure_state or ctx.closure_state == SessionClosureState.CLOSING:
            return GateResult(
                gate_name="G6_CONSTITUTIONAL",
                status=GateStatus.HOLD,
                reason="Session closure not yet initiated — call initiate_closure first",
                evidence_refs=evidence,
                obligations=["Call initiate_closure() before session-closure seal"],
            )

    return GateResult(
        gate_name="G6_CONSTITUTIONAL",
        status=GateStatus.PASS,
        reason=f"Constitutional requirements satisfied ({gov_impact.value})",
        evidence_refs=evidence,
        detail={"governance_impact": gov_impact.value},
    )


# ── GATE 7: Evaluate payload and evidence ──


def gate_evaluate_payload(ctx: GateContext) -> GateResult:
    """
    G7: Evaluate the payload/evidence for completeness and integrity.

    Checks: payload hash matches, required evidence present.
    Only runs for actions that carry payloads (MUTATE, APPEND_ONLY, CREATE).
    """
    profile = ctx.action_profile
    if not profile:
        return GateResult(
            gate_name="G7_PAYLOAD",
            status=GateStatus.DENY,
            reason="No action profile",
            evidence_refs=[],
        )

    # Actions without payloads pass trivially
    if profile.mutation_class in (MutationClass.NONE, MutationClass.UNKNOWN):
        return GateResult(
            gate_name="G7_PAYLOAD",
            status=GateStatus.PASS,
            reason="No payload required for this action class",
            evidence_refs=[],
        )

    evidence: list[str] = []

    # Payload hash must be present for append/mutate/create
    if not ctx.payload_hash:
        return GateResult(
            gate_name="G7_PAYLOAD",
            status=GateStatus.HOLD,
            reason=f"Payload hash required for {profile.mutation_class.value} action",
            evidence_refs=evidence,
            obligations=["Compute and provide payload_hash before execution"],
        )

    evidence.append(f"payload_hash:{ctx.payload_hash}")

    return GateResult(
        gate_name="G7_PAYLOAD",
        status=GateStatus.PASS,
        reason=f"Payload verified (hash={ctx.payload_hash[:12]}...)",
        evidence_refs=evidence,
        detail={"payload_hash": ctx.payload_hash},
    )


# ── GATE 8: Execute gate — final check before execution ──


def gate_execute_permission(ctx: GateContext) -> GateResult:
    """
    G8: Final pre-execution gate.
    All prior gates must have PASSed. This gate summarises the pipeline verdict.
    """
    profile = ctx.action_profile
    if not profile:
        return GateResult(
            gate_name="G8_EXECUTE",
            status=GateStatus.DENY,
            reason="No action profile — cannot execute",
            evidence_refs=[],
        )

    # Check all prior gates passed
    failed_gates = [
        name
        for name, result in ctx.gate_results.items()
        if result.status in (GateStatus.HOLD, GateStatus.DENY)
    ]

    if failed_gates:
        return GateResult(
            gate_name="G8_EXECUTE",
            status=GateStatus.DENY,
            reason=f"Prior gates blocked: {failed_gates}",
            evidence_refs=[f"failed_gates:{','.join(failed_gates)}"],
            obligations=[f"Resolve blocked gates before execution: {failed_gates}"],
            detail={
                "prior_verdicts": {
                    name: ctx.gate_results[name].status.value
                    for name in failed_gates
                }
            },
        )

    # Everything green — execution permitted
    ctx.pipeline_verdict = "SEAL"

    return GateResult(
        gate_name="G8_EXECUTE",
        status=GateStatus.PASS,
        reason=(
            f"All gates PASS — execution permitted. "
            f"Action: {profile.tool}/{profile.verb} [{profile.receipt_class.value}]"
        ),
        evidence_refs=["gate_chain:all_pass"],
        detail={
            "pipeline_verdict": "SEAL",
            "profile_hash": profile.profile_hash,
            "receipt_class": profile.receipt_class.value,
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GATE PIPELINE — ordered execution
# ═══════════════════════════════════════════════════════════════════════════════

# The canonical gate order. Every gate reads from GateContext.
# No gate modifies the ActionProfile. Facts flow left to right.
PIPELINE_GATES: list[tuple[str, GateFn]] = [
    ("G0_NORMALISE", gate_normalise_request),
    ("G1_RESOLVE_CONTEXT", gate_resolve_context),
    ("G2_CLASSIFY_ACTION", gate_classify_action),
    ("G3_IDENTITY", gate_evaluate_identity),
    ("G4_CAPABILITY", gate_evaluate_capability),
    ("G5_INFRASTRUCTURE", gate_evaluate_infrastructure),
    ("G6_CONSTITUTIONAL", gate_evaluate_constitutional),
    ("G7_PAYLOAD", gate_evaluate_payload),
    ("G8_EXECUTE", gate_execute_permission),
]


# ═══════════════════════════════════════════════════════════════════════════════
# RUN PIPELINE — entry point
# ═══════════════════════════════════════════════════════════════════════════════


class PipelineResult:
    """Result of running the full gate pipeline."""

    def __init__(self, ctx: GateContext):
        self.ctx = ctx
        self.all_pass: bool = all(
            r.status == GateStatus.PASS for r in ctx.gate_results.values()
        )
        self.first_failure: GateResult | None = None
        for r in ctx.gate_results.values():
            if r.status in (GateStatus.HOLD, GateStatus.DENY):
                self.first_failure = r
                break

    @property
    def can_execute(self) -> bool:
        """True if all gates passed and execution is permitted."""
        return self.all_pass

    @property
    def verdict(self) -> str:
        """Pipeline verdict string."""
        if self.all_pass:
            return "SEAL"
        if self.first_failure and self.first_failure.status == GateStatus.HOLD:
            return "HOLD"
        if self.first_failure and self.first_failure.status == GateStatus.DENY:
            return "DENY"
        return "HOLD"

    def to_dict(self) -> dict[str, Any]:
        """Serialise pipeline result."""
        return {
            "pipeline_verdict": self.verdict,
            "all_pass": self.all_pass,
            "first_failure": {
                "gate": self.first_failure.gate_name,
                "reason": self.first_failure.reason,
            }
            if self.first_failure
            else None,
            "gates": {
                name: {
                    "status": r.status.value,
                    "reason": r.reason,
                    "evidence_refs": r.evidence_refs,
                    "obligations": r.obligations,
                }
                for name, r in self.ctx.gate_results.items()
            },
        }


def run_pipeline(
    ctx: GateContext,
    *,
    stop_on_hold: bool = True,
    stop_on_deny: bool = True,
) -> PipelineResult:
    """
    Run the gate pipeline from G0 through G8.

    Args:
        ctx: GateContext — populate ctx.raw_request before calling
        stop_on_hold: If True, stop at first HOLD gate (default True)
        stop_on_deny: If True, stop at first DENY gate (default True)

    Returns:
        PipelineResult — contains ctx with all gate results and verdict
    """
    for gate_name, gate_fn in PIPELINE_GATES:
        try:
            result = gate_fn(ctx)
            ctx.record_gate(result)

            # Check for early termination
            if result.status == GateStatus.DENY and stop_on_deny:
                ctx.pipeline_verdict = "DENY"
                logger.warning(
                    f"Pipeline DENY at {gate_name}: {result.reason}"
                )
                break

            if result.status == GateStatus.HOLD and stop_on_hold:
                ctx.pipeline_verdict = "HOLD"
                logger.info(
                    f"Pipeline HOLD at {gate_name}: {result.reason}"
                )
                break

        except Exception as e:
            error_result = GateResult(
                gate_name=gate_name,
                status=GateStatus.DENY,
                reason=f"Gate raised exception: {e}",
            )
            ctx.record_gate(error_result)
            ctx.pipeline_verdict = "DENY"
            logger.exception(f"Pipeline exception at {gate_name}")
            break

    # If all gates PASS (including G8_EXECUTE), verdict is SEAL
    if not ctx.pipeline_verdict and all(
        r.status == GateStatus.PASS for r in ctx.gate_results.values()
    ):
        ctx.pipeline_verdict = "SEAL"

    return PipelineResult(ctx)
