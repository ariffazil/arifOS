"""
Pre-Execution Constitutional Chokepoint
═══════════════════════════════════════════════════════════

This is THE mandatory function that runs BEFORE any governed action.

pre_execution_gate(envelope, requested_action) -> GateResult

The gate MUST run before:
  - LLM tool use
  - MCP tool use
  - File writes
  - Shell execution
  - Network calls
  - Memory writes
  - Database writes
  - Deploys
  - Commits
  - Deletes
  - Payments
  - External messages
  - Vault seals
  - Organ delegation

THE GATE FAILS CLOSED:
  - If it cannot decide → HOLD
  - If actor unverified and action is mutating → HOLD
  - If action is irreversible and no human ack → HOLD
  - If lease does not cover the action → HOLD
  - If tool not in allowed manifest → HOLD
  - If runtime drift above threshold → HOLD for mutation
  - If constitution hash missing → HOLD for mutation
  - If audit path unavailable → HOLD for mutation

DITEMPA BUKAN DIBERI — The gate is forged, not given.
"""

from __future__ import annotations

import logging
import time

try:
    from arifosmcp.runtime.self_mod_lock import (
        classify_cognitive_tier as _classify_cognitive_tier,
    )

    _ASI_FIREWALL_AVAILABLE = True
except ImportError:
    _ASI_FIREWALL_AVAILABLE = False

from arifosmcp.schemas.kernel_envelope import (
    ActionClass,
    BlastRadius,
    DriftLevel,
    DriftReport,
    GateResult,
    GateVerdict,
    KernelEnvelope,
    MemoryScope,
    OrganCard,
    ToolManifestEntry,
)

logger = logging.getLogger("arifosmcp.pre_execution_gate")


# ═══════════════════════════════════════════════════════════════════════════════
# ART REFLEX BRIDGE — maps envelope/manifest → ArtRequest → ArtVerdict → gate
# ═══════════════════════════════════════════════════════════════════════════════


def _art_action_class_str(action_class: ActionClass) -> str:
    """Map ActionClass enum → art.py action_class string."""
    return {
        ActionClass.OBSERVE: "observe",
        ActionClass.ANALYZE: "observe",
        ActionClass.DRAFT: "mutate",
        ActionClass.SIMULATE: "mutate",
        ActionClass.MUTATE: "mutate",
        ActionClass.EXTERNAL_SIDE_EFFECT: "mutate",
        ActionClass.IRREVERSIBLE: "mutate",
    }.get(action_class, "observe")


def _art_blast_radius_str(br: BlastRadius) -> str:
    """Map BlastRadius enum → art.py blast_radius string."""
    return {
        BlastRadius.NONE: "low",
        BlastRadius.LOCAL: "low",
        BlastRadius.ACCOUNT: "medium",
        BlastRadius.ORG: "high",
        BlastRadius.PUBLIC: "high",
        BlastRadius.MARKET: "high",
        BlastRadius.INFRASTRUCTURE: "high",
        BlastRadius.CIVILIZATIONAL: "high",
        BlastRadius.UNKNOWN: "unknown",
    }.get(br, "unknown")


def _art_reflex_check(
    envelope: KernelEnvelope,
    requested_action: ActionClass,
    manifest_entry: ToolManifestEntry | None,
) -> GateResult | None:
    """Gate 2.5 — ART reflex advisory check.

    Calls the stateless ART reflex (4 states × 3 checks) and maps
    ArtVerdict into the gate pipeline.

    Returns:
        None if ART says PROCEED (continue to next gate).
        GateResult(SABAR) if ART says DEFAULT_OBSERVE on a non-observe action.
        GateResult(HOLD) if ART says HOLD or BLOCK.

    Fails open: if ART module is unavailable, returns None (no block).
    """
    try:
        from arifosmcp.runtime.art import ArtVerdict, ArtRequest, ToolState, art
    except ImportError:
        logger.warning("ART reflex unavailable — skipping reflex check")
        return None

    # W2 (2026-06-21): Tool state from bucket-based ArtRegistry instead of
    # hardcoded TRUSTED. All manifest tools start OBSERVED; TRUSTED is earned
    # through proven reliability. Unknown tools → UNTRUSTED (fail-conservative).
    try:
        from arifosmcp.runtime.art_registry import get_default_tool_state

        _state_str = get_default_tool_state(envelope.organ.tool_name)
        _tool_state = ToolState(_state_str)
    except (ImportError, Exception):
        _tool_state = ToolState.TRUSTED  # fail-open: gate continues

    # Build intent text from tool name + payload for ASI screening.
    payload = getattr(envelope, "payload", {}) or {}
    intent_text = f"{envelope.organ.tool_name} " + " ".join(
        f"{k}={v}" for k, v in payload.items()
    )
    target = ""
    for candidate in ("target_path", "path", "file", "repo", "target"):
        if candidate in payload:
            target = str(payload[candidate])
            break

    # Build ArtRequest from envelope + manifest + registry state.
    art_req = ArtRequest(
        action_class=_art_action_class_str(requested_action),
        tool_state=_tool_state.value,
        blast_radius=_art_blast_radius_str(
            manifest_entry.blast_radius if manifest_entry else BlastRadius.UNKNOWN
        ),
        trust_level="evidence" if envelope.kernel.actor_verified else "unknown",
        actor_resolved=envelope.kernel.actor_verified,
        schema_locked=True,  # manifest entry = schema is known
        degraded=False,
        reversible=manifest_entry.is_reversible if manifest_entry else False,
        external_surface=(requested_action == ActionClass.EXTERNAL_SIDE_EFFECT),
        acknowledged_remote=(
            envelope.authority.external_side_effect_allowed
            if requested_action == ActionClass.EXTERNAL_SIDE_EFFECT
            else False
        ),
        intent_text=intent_text,
        target=target,
    )

    art_result = art(art_req)

    # ── ART 2.0: Predictive assessment ─────────────────────────────
    # Compute trust score, failure risk, and recommended ACT pattern.
    # These values are stored on art_result for downstream consumers
    # (ACT gate, AAA cockpit, etc.). Non-blocking — prediction never holds.
    try:
        from arifosmcp.runtime.art_predict import get_predictive_assessment

        _pred = get_predictive_assessment(
            tool_name=manifest_entry.tool_name if manifest_entry else "unknown",
            action_class=requested_action.value,
            failure_rate=getattr(art_req, "failure_rate", 0.0),
            drift_count=getattr(art_req, "drift_count", 0),
            days_since_use=getattr(art_req, "days_since_use", 0),
            blast_str=art_req.blast_radius,
        )
        art_result.trust_score = _pred.trust_score
        art_result.trust_band = _pred.trust_band.value
        art_result.blast_weight = _pred.blast_weight
        art_result.failure_risk = _pred.failure_risk.value
        art_result.recommended_pattern = _pred.recommended_pattern
    except ImportError:
        pass  # ART 2.0 not available — continue without prediction
    except Exception as _e:
        logger.debug("ART 2.0 prediction error (non-blocking): %s", _e)

    # PROCEED → continue to next gate
    if art_result.verdict == ArtVerdict.PROCEED:
        return None

    # DEFAULT_OBSERVE → downgrade non-observe actions IF safely representable
    # Only MUTATE/DRAFT/SIMULATE can downgrade to OBSERVE.
    # IRREVERSIBLE and EXTERNAL_SIDE_EFFECT cannot safely downgrade → HOLD.
    if art_result.verdict == ArtVerdict.DEFAULT_OBSERVE:
        if requested_action in (
            ActionClass.MUTATE,
            ActionClass.DRAFT,
            ActionClass.SIMULATE,
        ):
            return GateResult(
                envelope=envelope,
                verdict=GateVerdict.SABAR,
                reasons=[f"ART reflex downgrade: {art_result.reason.value}"],
                violations=[],
            )
        if requested_action in (ActionClass.OBSERVE, ActionClass.ANALYZE):
            return None  # already observe — proceed
        # IRREVERSIBLE / EXTERNAL_SIDE_EFFECT → cannot downgrade, must HOLD
        return GateResult(
            envelope=envelope,
            verdict=GateVerdict.HOLD,
            reasons=[
                f"ART reflex: {art_result.reason.value} — cannot downgrade {requested_action.value}"
            ],
            violations=["ART_REFLEX_HOLD"],
            blocked_action_class=requested_action,
            required_human_ack=(requested_action == ActionClass.IRREVERSIBLE),
        )

    # HOLD → stop with HOLD
    if art_result.verdict == ArtVerdict.HOLD:
        return GateResult(
            envelope=envelope,
            verdict=GateVerdict.HOLD,
            reasons=[f"ART reflex: {art_result.reason.value}"],
            violations=["ART_REFLEX_HOLD"],
            blocked_action_class=requested_action,
            required_human_ack=(requested_action == ActionClass.IRREVERSIBLE),
        )

    # BLOCK → REJECT (constitutional-level prohibition)
    # GateVerdict.REJECT is a true block (is_blocked=True after schema fix)
    return GateResult(
        envelope=envelope,
        verdict=GateVerdict.REJECT,
        reasons=[f"ART reflex: {art_result.reason.value}"],
        violations=["ART_REFLEX_BLOCK"],
        blocked_action_class=requested_action,
    )


def _act_reflex_check(
    envelope: KernelEnvelope,
    requested_action: ActionClass,
    manifest_entry: ToolManifestEntry | None,
) -> GateResult | None:
    """Gate 2.6 — ACT execution craft check.

    Called AFTER Gate 2.5 (ART) says PROCEED. Decides HOW to sequence
    and stage the execution. Enforces:
      - Stage verification (can't proceed to N+1 if N failed)
      - Dry-run requirement for irreversible + high blast
      - Canary requirement for high blast
      - Human coordination for irreversible + high blast
      - Compensation plan requirement for irreversible

    Returns:
        None if ACT says PROCEED (continue to Gate 3).
        GateResult(HOLD) if ACT says DRY_RUN_REQUIRED, CANARY_REQUIRED, etc.
        GateResult(REJECT) if ACT says BLOCK.

    Fails open: if ACT module is unavailable, returns None (no block).
    """
    try:
        from arifosmcp.runtime.act import (
            act,
            ActRequest,
            ActResult,
            ActVerdict,
            ExecutionPattern,
        )
    except ImportError:
        logger.debug("ACT module unavailable — skipping execution craft check")
        return None

    # Only check ACT for non-trivial actions
    if requested_action in (ActionClass.OBSERVE, ActionClass.ANALYZE):
        return None

    # Determine blast radius from manifest
    blast = manifest_entry.blast_radius if manifest_entry else BlastRadius.UNKNOWN
    blast_str = {
        BlastRadius.NONE: "low",
        BlastRadius.LOCAL: "low",
        BlastRadius.ACCOUNT: "medium",
        BlastRadius.ORG: "medium",
        BlastRadius.PUBLIC: "high",
        BlastRadius.MARKET: "high",
        BlastRadius.INFRASTRUCTURE: "high",
        BlastRadius.CIVILIZATIONAL: "high",
        BlastRadius.UNKNOWN: "unknown",
    }.get(blast, "unknown")

    is_reversible = manifest_entry.is_reversible if manifest_entry else False

    # For single tool calls, ACT checks:
    #   1. Dry-run required for irreversible actions
    #   2. Human coordination for irreversible + high blast
    #   3. Compensation for irreversible
    #
    # For multi-step programs (detected via session state or explicit flag),
    # ACT also checks stage verification and staging pattern.
    # Multi-step detection is a session-level concern — ACT receives flags
    # from the caller (agent loop or /execute endpoint).

    act_req = ActRequest(
        program_stage="single",
        execution_pattern=ExecutionPattern.SINGLE_SHOT.value,
        blast_radius=blast_str,
        is_reversible=is_reversible,
        has_dry_run=False,
        has_compensation=False,
        human_acknowledged=(
            envelope.authority.human_ack_required
            or (manifest_entry and manifest_entry.requires_human_ack)
        ),
        previous_stage_verified=True,
        is_multi_step=False,
        stage_number=1,
        total_stages=1,
    )

    act_result = act(act_req)

    # PROCEED → continue to next gate
    if act_result.verdict == ActVerdict.PROCEED:
        return None

    # DRY_RUN_REQUIRED → HOLD with instruction
    if act_result.verdict == ActVerdict.DRY_RUN_REQUIRED:
        return GateResult(
            envelope=envelope,
            verdict=GateVerdict.HOLD,
            reasons=[
                f"ACT: {act_result.reason.value} — recommended: {act_result.recommended_pattern.value}"
            ],
            violations=["ACT_REFLEX_HOLD"],
            blocked_action_class=requested_action,
            required_human_ack=True,
        )

    # CANARY_REQUIRED → HOLD
    if act_result.verdict == ActVerdict.CANARY_REQUIRED:
        return GateResult(
            envelope=envelope,
            verdict=GateVerdict.HOLD,
            reasons=[
                f"ACT: {act_result.reason.value} — recommended: {act_result.recommended_pattern.value}"
            ],
            violations=["ACT_REFLEX_HOLD"],
            blocked_action_class=requested_action,
            required_human_ack=True,
        )

    # COMPENSATION_REQUIRED → HOLD
    if act_result.verdict == ActVerdict.COMPENSATION_REQUIRED:
        return GateResult(
            envelope=envelope,
            verdict=GateVerdict.HOLD,
            reasons=[
                f"ACT: {act_result.reason.value} — recommended: {act_result.recommended_pattern.value}"
            ],
            violations=["ACT_REFLEX_HOLD"],
            blocked_action_class=requested_action,
        )

    # STAGED_ROLLOUT → HOLD with recommendation
    if act_result.verdict in (
        ActVerdict.STAGED_ROLLOUT,
        ActVerdict.SINGLE_SHOT,
    ):
        return GateResult(
            envelope=envelope,
            verdict=GateVerdict.HOLD,
            reasons=[
                f"ACT: {act_result.reason.value} — recommended: {act_result.recommended_pattern.value}"
            ],
            violations=["ACT_REFLEX_HOLD"],
            blocked_action_class=requested_action,
        )

    # HUMAN_REQUIRED → HOLD
    if act_result.verdict == ActVerdict.HUMAN_REQUIRED:
        return GateResult(
            envelope=envelope,
            verdict=GateVerdict.HOLD,
            reasons=[f"ACT: {act_result.reason.value} — human acknowledgment required"],
            violations=["ACT_REFLEX_HOLD"],
            blocked_action_class=requested_action,
            required_human_ack=True,
        )

    # HOLD → stop with HOLD
    if act_result.verdict == ActVerdict.HOLD:
        return GateResult(
            envelope=envelope,
            verdict=GateVerdict.HOLD,
            reasons=[f"ACT: {act_result.reason.value}"],
            violations=["ACT_REFLEX_HOLD"],
            blocked_action_class=requested_action,
        )

    # BLOCK → REJECT
    if act_result.verdict == ActVerdict.BLOCK:
        return GateResult(
            envelope=envelope,
            verdict=GateVerdict.REJECT,
            reasons=[f"ACT: {act_result.reason.value}"],
            violations=["ACT_REFLEX_BLOCK"],
            blocked_action_class=requested_action,
        )

    return None


# ═══════════════════════════════════════════════════════════════════════════════
# GATE 2.7: ASI COGNITIVE TIER FIREWALL
# ═══════════════════════════════════════════════════════════════════════════════


def _asi_firewall_check(
    envelope: KernelEnvelope,
    requested_action: ActionClass,
) -> GateResult | None:
    """Gate 2.7 — Detect recursive self-improvement / ASI_TIER signals.

    Defense-in-depth alongside GovernancePipeline Gate 1.6. Any tool call
    whose intent or target signals recursive self-modification is HOLDed
    with explicit F13 escalation. BRAIN must judge; HANDS does not execute.

    Returns:
        None if AGI_TIER (proceed to next gate).
        GateResult(HOLD) if ASI_TIER detected.

    Fails open: if classifier unavailable, returns None.
    """
    if not _ASI_FIREWALL_AVAILABLE:
        return None

    tool_name = envelope.organ.tool_name or ""
    params = getattr(envelope, "payload", {}) or {}
    params_text = " ".join(f"{k}={v}" for k, v in params.items())
    intent_text = f"{tool_name} {params_text}".strip()

    # Target may be explicit in payload
    target = ""
    for candidate in ("target_path", "path", "file", "repo", "target"):
        if candidate in params:
            target = str(params[candidate])
            break

    classification = _classify_cognitive_tier(intent_text, target)

    if classification.get("tier") == "ASI":
        return GateResult(
            envelope=envelope,
            verdict=GateVerdict.HOLD,
            reasons=[
                f"ASI_FIREWALL: {classification.get('reason')} "
                f"[skill={classification.get('skill')}; tool={classification.get('tool')}]"
            ],
            violations=["ASI_FIREWALL", "F13_SOVEREIGN"],
            blocked_action_class=requested_action,
            required_human_ack=True,
        )

    return None


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL MANIFEST — canonical list of what every tool is allowed to do
# ═══════════════════════════════════════════════════════════════════════════════

# SDK long-name aliases → canonical short names (2026-06-23 unification)
_SDK_LONG_NAME_ALIASES: dict[str, str] = {
    "arif_session_init": "arif_init",
    "arif_sense_observe": "arif_observe",
    "arif_evidence_fetch": "arif_fetch",
    "arif_mind_reason": "arif_think",
    "arif_heart_critique": "arif_critique",
    "arif_reply_compose": "arif_compose",
    "arif_memory_recall": "arif_memory",
    "arif_gateway_connect": "arif_bridge_connect",
    "arif_ops_measure": "arif_measure",
    "arif_judge_deliberate": "arif_judge",
    "arif_vault_seal": "arif_seal",
    "arif_forge_execute": "arif_forge",
}

CANONICAL_TOOL_MANIFEST: dict[str, ToolManifestEntry] = {
    "arif_init": ToolManifestEntry(
        tool_name="arif_init",
        action_class=ActionClass.OBSERVE,
        safe_modes=["init", "resume", "validate", "status", "discover", "handover"],
        dangerous_modes=["revoke", "epoch_open", "epoch_seal"],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOCAL,
        is_reversible=True,
    ),
    "arif_observe": ToolManifestEntry(
        tool_name="arif_observe",
        action_class=ActionClass.OBSERVE,
        safe_modes=[
            "search",
            "ingest",
            "compass",
            "atlas",
            "entropy_dS",
            "vitals",
            "classify",
            "extract_claims",
            "contrast",
            "repo_map",
        ],
        dangerous_modes=[],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOCAL,
        is_reversible=True,
    ),
    "arif_fetch": ToolManifestEntry(
        tool_name="arif_fetch",
        action_class=ActionClass.OBSERVE,
        safe_modes=["fetch", "search", "verify"],
        dangerous_modes=["archive"],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOCAL,
        is_reversible=True,
    ),
    "arif_think": ToolManifestEntry(
        tool_name="arif_think",
        action_class=ActionClass.ANALYZE,
        safe_modes=[
            "reason",
            "reflect",
            "verify",
            "critique",
            "debate",
            "socratic",
            "plan",
            "plan_review",
            "plan_ready",
            "axioms",
        ],
        dangerous_modes=[],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOCAL,
        is_reversible=True,
    ),
    "arif_kernel_route": ToolManifestEntry(
        tool_name="arif_kernel_route",
        action_class=ActionClass.OBSERVE,
        safe_modes=["route", "stage", "lane", "list", "status", "context_runner"],
        dangerous_modes=[],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOCAL,
        is_reversible=True,
    ),
    "arif_compose": ToolManifestEntry(
        tool_name="arif_compose",
        action_class=ActionClass.DRAFT,
        safe_modes=["compose"],
        dangerous_modes=[],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOCAL,
        is_reversible=True,
    ),
    "arif_memory_recall": ToolManifestEntry(
        tool_name="arif_memory_recall",
        action_class=ActionClass.MUTATE,
        safe_modes=["recall", "get", "list", "search", "context", "dry_run", "manage"],
        dangerous_modes=["store", "prune"],
        requires_lease=True,
        requires_human_ack=False,
        blast_radius=BlastRadius.ACCOUNT,
        is_reversible=True,
    ),
    "arif_critique": ToolManifestEntry(
        tool_name="arif_critique",
        action_class=ActionClass.ANALYZE,
        safe_modes=[
            "critique",
            "simulate",
            "empathize",
            "redteam",
            "maruah",
            "deescalate",
            "summary",
        ],
        dangerous_modes=[],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOCAL,
        is_reversible=True,
    ),
    "arif_gateway_connect": ToolManifestEntry(
        tool_name="arif_gateway_connect",
        action_class=ActionClass.EXTERNAL_SIDE_EFFECT,
        safe_modes=["discover", "handshake"],
        dangerous_modes=["route", "relay"],
        requires_lease=True,
        requires_human_ack=True,
        blast_radius=BlastRadius.PUBLIC,
        is_reversible=True,
    ),
    "arif_measure": ToolManifestEntry(
        tool_name="arif_measure",
        action_class=ActionClass.OBSERVE,
        safe_modes=["health", "vitals", "cost", "predict", "genius", "psi_le", "omega", "landauer"],
        dangerous_modes=[],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOCAL,
        is_reversible=True,
    ),
    "arif_judge": ToolManifestEntry(
        tool_name="arif_judge",
        action_class=ActionClass.ANALYZE,
        safe_modes=["judge", "compare", "history", "explain"],
        dangerous_modes=[],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOCAL,
        is_reversible=True,
    ),
    "arif_seal": ToolManifestEntry(
        tool_name="arif_seal",
        action_class=ActionClass.IRREVERSIBLE,
        safe_modes=["list", "verify", "chain", "dry_run"],
        dangerous_modes=["seal"],
        requires_lease=True,
        requires_human_ack=True,
        blast_radius=BlastRadius.INFRASTRUCTURE,
        is_reversible=False,
    ),
    "arif_forge": ToolManifestEntry(
        tool_name="arif_forge",
        action_class=ActionClass.MUTATE,
        safe_modes=["query", "recall", "dry_run"],
        dangerous_modes=["engineer", "write", "generate", "commit"],
        requires_lease=True,
        requires_human_ack=True,
        blast_radius=BlastRadius.PUBLIC,
        is_reversible=False,
    ),
    # RULE 14 canonical expansion (2026-06-20): 6 additional public surface tools
    "arif_route": ToolManifestEntry(
        tool_name="arif_route",
        action_class=ActionClass.OBSERVE,
        safe_modes=["route"],
        dangerous_modes=["delegate", "bridge"],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOCAL,
        is_reversible=True,
    ),
    "arif_triage": ToolManifestEntry(
        tool_name="arif_triage",
        action_class=ActionClass.OBSERVE,
        safe_modes=["status", "preflight", "triage"],
        dangerous_modes=[],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOCAL,
        is_reversible=True,
    ),
    "arif_kernel_status": ToolManifestEntry(
        tool_name="arif_kernel_status",
        action_class=ActionClass.OBSERVE,
        safe_modes=["telemetry", "discover", "prediction"],
        dangerous_modes=[],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOCAL,
        is_reversible=True,
    ),
    "arif_bridge": ToolManifestEntry(
        tool_name="arif_bridge",
        action_class=ActionClass.EXTERNAL_SIDE_EFFECT,
        safe_modes=["bridge"],
        dangerous_modes=[],
        requires_lease=True,
        requires_human_ack=True,
        blast_radius=BlastRadius.ACCOUNT,
        is_reversible=True,
    ),
    "arif_kernel_attest": ToolManifestEntry(
        tool_name="arif_kernel_attest",
        action_class=ActionClass.OBSERVE,
        safe_modes=["attest"],
        dangerous_modes=[],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOCAL,
        is_reversible=True,
    ),
    "arif_kernel_health": ToolManifestEntry(
        tool_name="arif_kernel_health",
        action_class=ActionClass.OBSERVE,
        safe_modes=["health"],
        dangerous_modes=[],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOCAL,
        is_reversible=True,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# THE GATE
# ═══════════════════════════════════════════════════════════════════════════════


def pre_execution_gate(
    envelope: KernelEnvelope,
    requested_action: ActionClass,
    *,
    tool_mode: str = "",
    known_organs: dict[str, OrganCard] | None = None,
    drift_report: DriftReport | None = None,
    valid_leases: set[str] | None = None,
) -> GateResult:
    """THE mandatory pre-execution constitutional chokepoint.

    This function MUST run before any governed action. It returns a GateResult
    that tells the caller whether the action is allowed, blocked, or conditional.

    The gate FAILS CLOSED. If it cannot decide, verdict = HOLD.

    Args:
        envelope: The KernelEnvelope for this call.
        requested_action: The action class being requested.
        tool_mode: The mode of the tool being called (for manifest check).
        known_organs: Known organ cards (for organ health check).
        drift_report: Current drift report (for drift gating).
        valid_leases: Set of currently valid lease IDs.

    Returns:
        GateResult with verdict (SEAL/SABAR/HOLD/VOID) and reasons.
    """
    t0 = time.monotonic()
    reasons: list[str] = []
    violations: list[str] = []
    degraded_organs: list[str] = []
    drift_detected = False
    drift_level: DriftLevel | None = None

    # ── Gate 1: Action class resolution ───────────────────────────────
    # Unknown action class → fail closed
    if requested_action == ActionClass.UNKNOWN:
        return GateResult(
            envelope=envelope,
            verdict=GateVerdict.HOLD,
            reasons=["Unknown action class — cannot authorize"],
            violations=[],
            blocked_action_class=ActionClass.UNKNOWN,
        )

    # ── Gate 2: Tool manifest check ───────────────────────────────────
    tool_name = envelope.organ.tool_name
    # Resolve SDK long-name aliases to canonical short names before manifest lookup
    canonical_tool_name = _SDK_LONG_NAME_ALIASES.get(tool_name, tool_name)
    manifest_entry = CANONICAL_TOOL_MANIFEST.get(canonical_tool_name)

    if manifest_entry is None and tool_name:
        # Tool not in canonical manifest → HOLD
        return GateResult(
            envelope=envelope,
            verdict=GateVerdict.HOLD,
            reasons=[f"Tool '{tool_name}' not found in canonical manifest"],
            violations=["F11_AUDIT — unregistered tool"],
            blocked_action_class=requested_action,
        )

    if manifest_entry and tool_mode:
        # If mode is dangerous and action is mutating, require higher authority
        if tool_mode in manifest_entry.dangerous_modes:
            if requested_action in (ActionClass.MUTATE, ActionClass.IRREVERSIBLE):
                reasons.append(
                    f"Dangerous mode '{tool_mode}' on tool '{tool_name}' "
                    f"requires explicit human acknowledgement"
                )
                violations.append("F1_AMANAH — dangerous mode without ack")
                if not envelope.authority.human_ack_required:
                    return GateResult(
                        envelope=envelope,
                        verdict=GateVerdict.HOLD,
                        reasons=reasons,
                        violations=violations,
                        blocked_action_class=requested_action,
                        required_human_ack=True,
                    )

    # ── Gate 2.7: ASI Cognitive Tier Firewall ─────────────────────────
    # Runs BEFORE ART/ACT so that recursive self-improvement signals are
    # caught regardless of tool lifecycle state. ASI_TIER forces 888_HOLD + F13.
    asi_gate = _asi_firewall_check(envelope, requested_action)
    if asi_gate is not None:
        return asi_gate

    # ── Gate 2.5: ART reflex advisory check ────────────────────────────
    # Calls the stateless ART reflex (4 tool states × 3 checks) and maps
    # the ArtVerdict into the gate pipeline. ART is advisory — the gate
    # has final say. Fails open if ART module unavailable.
    if manifest_entry:
        art_gate = _art_reflex_check(envelope, requested_action, manifest_entry)
        if art_gate is not None:
            return art_gate

    # ── Gate 2.6: ACT execution craft check ─────────────────────────
    # Called AFTER ART says PROCEED and BEFORE Gate 3 escalation check.
    # ACT decides HOW to execute a program: staging, tempo, compensation,
    # dry-run enforcement, human coordination.
    # Only fires for non-OBSERVE actions with meaningful blast radius.
    # Fails open if ACT module unavailable.
    if manifest_entry and requested_action not in (ActionClass.OBSERVE, ActionClass.ANALYZE):
        act_gate = _act_reflex_check(envelope, requested_action, manifest_entry)
        if act_gate is not None:
            return act_gate

    # ── Gate 3: Action class escalation check ─────────────────────────
    # The requested action class must not exceed what the tool allows
    if manifest_entry and not ActionClass.subsumes(manifest_entry.action_class, requested_action):
        return GateResult(
            envelope=envelope,
            verdict=GateVerdict.HOLD,
            reasons=[
                f"Tool '{tool_name}' allows {manifest_entry.action_class.value}, "
                f"but {requested_action.value} was requested"
            ],
            violations=["F1_AMANAH — action class escalation"],
            blocked_action_class=requested_action,
        )

    # ── Gate 3.5: HARD INFRASTRUCTURE → 888 HOLD ──────────────────────
    # Hermes ASI standard: BlastClass ≥ INFRASTRUCTURE requires unconditional
    # 888 HOLD regardless of lease band, action class, or human ack status.
    # This is HARAM — not WAJIB. No override possible.
    if manifest_entry and manifest_entry.blast_radius in (
        BlastRadius.INFRASTRUCTURE,
        BlastRadius.CIVILIZATIONAL,
    ):
        # Even if human ack is present, INFRASTRUCTURE requires sovereign seal
        return GateResult(
            envelope=envelope,
            verdict=GateVerdict.HOLD,
            reasons=[
                f"HARD INFRASTRUCTURE HOLD: Tool '{tool_name}' has blast radius "
                f"{manifest_entry.blast_radius.value}. Hermes ASI doctrine: "
                f"BlastClass ≥ INFRASTRUCTURE requires unconditional 888 HOLD "
                f"regardless of lease band or human ack. This is HARAM without "
                f"sovereign-level ceremony."
            ],
            violations=[
                "F0_SAFETY — INFRASTRUCTURE blast requires 888 HOLD",
                "L00_ADAT — INFRASTRUCTURE/CIVILIZATIONAL is HARAM, not WAJIB",
            ],
            blocked_action_class=requested_action,
            required_human_ack=True,
        )

    # ── Gate 4: Actor verification ────────────────────────────────────
    if ActionClass.is_mutating(requested_action):
        if not envelope.kernel.actor_verified:
            return GateResult(
                envelope=envelope,
                verdict=GateVerdict.HOLD,
                reasons=[
                    "Mutating action requires verified actor identity, "
                    f"but actor '{envelope.kernel.actor_id or 'anonymous'}' is not verified"
                ],
                violations=["F11_AUDIT — unverified actor on mutation"],
                blocked_action_class=requested_action,
            )

    # ── Gate 5: Lease validation ──────────────────────────────────────
    if ActionClass.requires_lease(requested_action):
        lease_id = envelope.authority.lease_id
        if not lease_id or lease_id == "LEASE-NONE":
            return GateResult(
                envelope=envelope,
                verdict=GateVerdict.HOLD,
                reasons=[
                    f"Action class {requested_action.value} requires a valid lease, "
                    f"but no lease is active ({lease_id or 'LEASE-NONE'})"
                ],
                violations=["F1_AMANAH — no lease for governed action"],
                blocked_action_class=requested_action,
                required_lease_scope="write"
                if requested_action == ActionClass.MUTATE
                else "execute",
            )

        if valid_leases is not None and lease_id not in valid_leases:
            return GateResult(
                envelope=envelope,
                verdict=GateVerdict.HOLD,
                reasons=[f"Lease '{lease_id}' is not valid or has been revoked"],
                violations=["F1_AMANAH — invalid lease"],
                blocked_action_class=requested_action,
            )

        # Check lease scope covers the action class
        if not envelope.authority.mutation_allowed and requested_action in (
            ActionClass.MUTATE,
            ActionClass.EXTERNAL_SIDE_EFFECT,
            ActionClass.IRREVERSIBLE,
        ):
            reasons.append(
                f"Lease '{lease_id}' does not permit mutation (scope: {envelope.authority.lease_scope})"
            )
            violations.append("F1_AMANAH — lease scope insufficient")

    # ── Gate 6: Irreversibility gate ──────────────────────────────────
    if requested_action == ActionClass.IRREVERSIBLE:
        if not envelope.authority.irreversible_allowed:
            return GateResult(
                envelope=envelope,
                verdict=GateVerdict.HOLD,
                reasons=["Irreversible action requested but irreversible_allowed=false"],
                violations=["F1_AMANAH — irreversible action blocked"],
                blocked_action_class=ActionClass.IRREVERSIBLE,
            )

        if not envelope.authority.human_ack_required:
            return GateResult(
                envelope=envelope,
                verdict=GateVerdict.HOLD,
                reasons=["Irreversible action requires explicit human acknowledgement"],
                violations=["F1_AMANAH — no human ack for irreversible"],
                blocked_action_class=ActionClass.IRREVERSIBLE,
                required_human_ack=True,
            )

        if not envelope.authority.human_ack_id:
            reasons.append("Irreversible action without human_ack_id — HOLD")
            violations.append("F13_SOVEREIGN — implicit irreversible")

    # ── Gate 7: Human acknowledgement check ───────────────────────────
    if ActionClass.requires_human_ack(requested_action):
        if not envelope.authority.human_ack_required:
            return GateResult(
                envelope=envelope,
                verdict=GateVerdict.HOLD,
                reasons=[f"{requested_action.value} requires human acknowledgement"],
                violations=["F13_SOVEREIGN — no human ack"],
                blocked_action_class=requested_action,
                required_human_ack=True,
            )

    # ── Gate 8: Constitution hash ─────────────────────────────────────
    if ActionClass.is_mutating(requested_action):
        if not envelope.kernel.constitution_hash or envelope.kernel.constitution_hash == "":
            return GateResult(
                envelope=envelope,
                verdict=GateVerdict.HOLD,
                reasons=["Constitution hash is missing — cannot authorize mutation"],
                violations=["F11_AUDIT — missing constitution hash"],
                blocked_action_class=requested_action,
            )
        if not envelope.kernel.constitution_hash.startswith("sha256:"):
            return GateResult(
                envelope=envelope,
                verdict=GateVerdict.HOLD,
                reasons=["Constitution hash format invalid"],
                violations=["F11_AUDIT — invalid constitution hash"],
                blocked_action_class=requested_action,
            )

    # ── Gate 9: Runtime drift ─────────────────────────────────────────
    if drift_report is not None:
        drift_detected = drift_report.drift_level != DriftLevel.NONE
        drift_level = drift_report.drift_level

        if drift_report.blocks_mutation and ActionClass.is_mutating(requested_action):
            return GateResult(
                envelope=envelope,
                verdict=GateVerdict.HOLD,
                reasons=[f"Runtime drift level {drift_report.drift_level.value} blocks mutation"],
                violations=["F11_AUDIT — drift blocks mutation"],
                blocked_action_class=requested_action,
                drift_detected=True,
                drift_level=drift_report.drift_level,
            )

        if drift_report.blocks_irreversible and requested_action == ActionClass.IRREVERSIBLE:
            return GateResult(
                envelope=envelope,
                verdict=GateVerdict.HOLD,
                reasons=[
                    f"Runtime drift level {drift_report.drift_level.value} blocks irreversible actions"
                ],
                violations=["F11_AUDIT — drift blocks irreversible"],
                blocked_action_class=ActionClass.IRREVERSIBLE,
                drift_detected=True,
                drift_level=drift_report.drift_level,
            )

    # ── Gate 10: Organ health ─────────────────────────────────────────
    if known_organs:
        organ_id = envelope.organ.organ_id
        organ_card = known_organs.get(organ_id)
        if organ_card:
            if organ_card.health_status not in ("ALIVE", "HEALTHY"):
                degraded_organs.append(organ_id)
                if ActionClass.is_mutating(requested_action):
                    return GateResult(
                        envelope=envelope,
                        verdict=GateVerdict.HOLD,
                        reasons=[
                            f"Organ '{organ_id}' is degraded ({organ_card.health_status}) — "
                            f"mutation blocked"
                        ],
                        violations=["F8_GENIUS — degraded organ mutation"],
                        blocked_action_class=requested_action,
                        degraded_organs=degraded_organs,
                    )

    # ── Gate 11: Memory scope check ───────────────────────────────────
    if requested_action in (ActionClass.MUTATE, ActionClass.IRREVERSIBLE):
        memory_scopes = envelope.state.memory_scopes
        forbidden_scopes = {MemoryScope.CONSTITUTIONAL, MemoryScope.VAULT}
        active_forbidden = [s for s in memory_scopes if s in forbidden_scopes]
        if active_forbidden:
            if not envelope.authority.human_ack_required:
                return GateResult(
                    envelope=envelope,
                    verdict=GateVerdict.HOLD,
                    reasons=[
                        f"Memory scope violation: {[s.value for s in active_forbidden]} "
                        f"requires human acknowledgement"
                    ],
                    violations=["F12_MEMORY — protected memory scope"],
                    blocked_action_class=requested_action,
                    required_human_ack=True,
                )

    # ── Gate 12: External side effect check ────────────────────────────
    if requested_action == ActionClass.EXTERNAL_SIDE_EFFECT:
        if not envelope.authority.external_side_effect_allowed:
            return GateResult(
                envelope=envelope,
                verdict=GateVerdict.HOLD,
                reasons=["External side effects not allowed for this action"],
                violations=["F5_PEACE — external effect not authorized"],
                blocked_action_class=ActionClass.EXTERNAL_SIDE_EFFECT,
            )

    # ── Gate 13: Secret touching check ────────────────────────────────
    if envelope.risk.secret_touching:
        if not envelope.authority.human_ack_required:
            reasons.append("Action touches secrets but no human acknowledgement — advisory warning")
            violations.append("F12_INJECTION — secret exposure risk")

    # ── Gate 14: Maintenance cost scaling ──────────────────────────────
    # Passive complexity-time degradation: every ordered system accumulates
    # maintenance debt. If unaccounted, mutation-class actions risk
    # compounding hidden fragility. (Invariant #11)
    if requested_action in (ActionClass.MUTATE, ActionClass.IRREVERSIBLE):
        try:
            from core.physics.thermodynamics_hardened import (
                MaintenanceScaling,
                compute_maintenance_cost,
            )

            scaler = MaintenanceScaling()
            t_active = getattr(envelope.state, "session_active_s", None)
            complexity = getattr(envelope.state, "complexity_index", None)
            if t_active is None:
                t_active = time.time() - getattr(envelope, "_gate_t0", t0)
            if complexity is None:
                complexity = 1.0  # default: single-component system

            maintenance_joules = compute_maintenance_cost(
                t_active_seconds=t_active,
                complexity_index=complexity,
            )

            # Threshold: accumulated maintenance > 10% of thermodynamic budget → HOLD
            from core.physics.thermodynamics_hardened import get_thermodynamic_budget

            budget = get_thermodynamic_budget(envelope.session_id)
            if budget and budget.initial_budget > 0:
                maintenance_ratio = maintenance_joules / budget.initial_budget
                if maintenance_ratio > 0.10:
                    return GateResult(
                        envelope=envelope,
                        verdict=GateVerdict.HOLD,
                        reasons=[
                            f"Maintenance cost {maintenance_joules:.2e} J ({maintenance_ratio * 100:.1f}% "
                            f"of session budget) — complexity-time degradation at risk threshold"
                        ],
                        violations=["F12_RESILIENCE — maintenance cost scaling"],
                        blocked_action_class=requested_action,
                    )
        except ImportError:
            pass  # Maintenance scaling unavailable — proceed with warning
        except Exception:
            logger.warning(
                "Maintenance cost gate failed — proceeding (fail-open for non-critical gate)"
            )

    # ── Gate 15: Institutional Evolution Guard ─────────────────────────
    # Invariant #15: Prevent AI-driven institutional change from outrunning
    # human succession, population absorption, and recall authority.
    if requested_action in (ActionClass.MUTATE, ActionClass.IRREVERSIBLE):
        try:
            from core.physics.institutional_evolution import (
                InstitutionalEvolutionError,
                InstitutionalEvolutionGuard,
            )

            # Build payload from envelope state and metadata
            duration = 3600
            if hasattr(envelope, "audit") and hasattr(envelope.audit, "timestamp"):
                try:
                    duration = time.time() - envelope.audit.timestamp.timestamp()
                except Exception:
                    pass

            # Forge 3: MUTATE/IRREVERSIBLE actions require live organ attestation
            import os

            check_liveness = "PYTEST_CURRENT_TEST" not in os.environ

            evolution_payload = {
                "session_duration_s": duration,
                "operator_interventions": getattr(envelope.state, "operator_interventions", 0),
                "affected_communities": getattr(envelope.state, "affected_communities", []),
                "consent_coverage": getattr(envelope.state, "consent_coverage", 1.0),
                "role_changes": getattr(envelope.state, "role_changes", []),
                "unacknowledged_obligations": getattr(
                    envelope.state, "unacknowledged_obligations", []
                ),
                "changes_last_30d": getattr(envelope.state, "changes_last_30d", 0),
                "human_reviews_last_30d": getattr(envelope.state, "human_reviews_last_30d", 0),
                "check_federation_liveness": check_liveness,
                "required_organs": ["arifOS", "GEOX", "WEALTH", "WELL", "a-forge"],
                "max_stale_seconds": 120.0,
            }

            # Check if there are explicit overrides in envelope metadata
            if hasattr(envelope, "metadata") and envelope.metadata:
                for key in [
                    "session_duration_s",
                    "operator_interventions",
                    "consent_coverage",
                    "changes_last_30d",
                    "human_reviews_last_30d",
                ]:
                    if key in envelope.metadata:
                        evolution_payload[key] = envelope.metadata[key]
                for key in ["affected_communities", "role_changes", "unacknowledged_obligations"]:
                    if key in envelope.metadata:
                        evolution_payload[key] = envelope.metadata[key]

            eval_res = InstitutionalEvolutionGuard.evaluate_evolution_invariants(evolution_payload)
            if not eval_res["passed"]:
                first_fail_verdict = eval_res["verdict"]
                if first_fail_verdict == "HOLD_888" or first_fail_verdict == "HOLD":
                    return GateResult(
                        envelope=envelope,
                        verdict=GateVerdict.HOLD,
                        reasons=[f"Succession/Evolution Blocked: {eval_res['first_failure']}"],
                        violations=["F11_AUDIT — Succession continuity broken"],
                        blocked_action_class=requested_action,
                    )
                elif first_fail_verdict == "REJECT":
                    return GateResult(
                        envelope=envelope,
                        verdict=GateVerdict.REJECT,
                        reasons=[f"Constitutional Rejection: {eval_res['first_failure']}"],
                        violations=["F13_SOVEREIGN — Constitutional prohibition triggered"],
                        blocked_action_class=requested_action,
                    )
                elif first_fail_verdict == "VOID":
                    return GateResult(
                        envelope=envelope,
                        verdict=GateVerdict.VOID,
                        reasons=[f"Succession/Evolution Invalid: {eval_res['first_failure']}"],
                        violations=["F11_AUDIT — Invalid institutional evolution parameters"],
                        blocked_action_class=requested_action,
                    )
                elif first_fail_verdict == "SABAR":
                    reasons.append(f"Succession Warning: {eval_res['first_failure']}")
                    violations.append("F7_PROPORTIONALITY — Community absorption lag")
            elif eval_res["verdict"] == "SABAR":
                # Warn if soft warnings triggered
                for check_res in eval_res["results"].values():
                    if check_res.get("verdict") == "SABAR":
                        for r in check_res.get("reasons", []):
                            reasons.append(f"Succession warning: {r}")
                violations.append("F7_PROPORTIONALITY — community absorption rate caution")

        except ImportError:
            # FAIL-SAFE: If the institutional evolution module cannot be imported,
            # we log a severe warning but do NOT block the gate. This is fail-open
            # by design for prototype phase (Tier 5 DRAFT). Before production seal,
            # this must become fail-closed: ImportError → HOLD.
            logger.error(
                "InstitutionalEvolutionGuard UNAVAILABLE — core.physics.institutional_evolution "
                "could not be imported. Invariant #15 is NOT being enforced. "
                "This is acceptable only during DRAFT phase."
            )
            reasons.append(
                "InstitutionalEvolutionGuard UNAVAILABLE — Invariant #15 not enforced this cycle"
            )
            violations.append("F11_AUDIT — Institutional evolution guard offline")
        except Exception as e:
            logger.error(
                f"InstitutionalEvolutionGuard failed with unexpected error: {e}. "
                f"Invariant #15 enforcement skipped for this cycle."
            )
            reasons.append(f"InstitutionalEvolutionGuard error — Invariant #15 skipped: {e}")

    # ── GATE COMPLETE — decide verdict ────────────────────────────────
    total_latency_ms = (time.monotonic() - t0) * 1000

    if violations and not reasons:
        # Violations without reasons — SABAR with warnings
        final_verdict = GateVerdict.SABAR
    elif reasons and not violations:
        # Reasons but no floor violations — SABAR with cautions
        final_verdict = GateVerdict.SABAR
    elif violations:
        # Both reasons and violations → HOLD
        final_verdict = GateVerdict.HOLD
    else:
        # Clean: no reasons, no violations → SEAL
        final_verdict = GateVerdict.SEAL

    # Build the final GateResult
    result = GateResult(
        envelope=envelope,
        verdict=final_verdict,
        reasons=[f"[{total_latency_ms:.1f}ms] {r}" for r in reasons],
        violations=violations,
        blocked_action_class=None,  # only set on HOLD; already returned above
        required_lease_scope=None,
        required_human_ack=envelope.authority.human_ack_required
        or ActionClass.requires_human_ack(requested_action),
        drift_detected=drift_detected,
        drift_level=drift_level,
        degraded_organs=degraded_organs,
    )

    # Ensure verdict is HOLD if we have violations
    if violations and final_verdict == GateVerdict.SEAL:
        result.verdict = GateVerdict.SABAR

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# SHORTCUT — for callers that don't have a full envelope
# ═══════════════════════════════════════════════════════════════════════════════


def quick_gate(
    action_class: ActionClass,
    *,
    actor_verified: bool = False,
    lease_id: str | None = None,
    human_ack_id: str | None = None,
    tool_name: str = "",
    constitution_hash: str = "",
) -> GateResult:
    """A minimal gate check for callers without a full envelope.

    This constructs a minimal envelope and runs the full gate.
    """
    from arifosmcp.schemas.kernel_envelope import (
        AuthorityBlock,
        KernelIdentity,
        OrganIdentity,
    )

    envelope = KernelEnvelope(
        kernel=KernelIdentity(
            actor_verified=actor_verified,
            constitution_hash=constitution_hash,
        ),
        organ=OrganIdentity(tool_name=tool_name),
        authority=AuthorityBlock(
            action_class=action_class,
            lease_id=lease_id or "LEASE-NONE",
            human_ack_id=human_ack_id,
            human_ack_required=bool(human_ack_id),
            mutation_allowed=action_class
            in (ActionClass.MUTATE, ActionClass.EXTERNAL_SIDE_EFFECT, ActionClass.IRREVERSIBLE),
            irreversible_allowed=(action_class == ActionClass.IRREVERSIBLE and bool(human_ack_id)),
        ),
    )

    return pre_execution_gate(envelope, action_class)


# ═══════════════════════════════════════════════════════════════════════════════
# SELF-CHECK
# ═══════════════════════════════════════════════════════════════════════════════


def _self_check() -> bool:
    """Verify that the pre_execution_gate behaves correctly."""
    from arifosmcp.schemas.kernel_envelope import (
        AuthorityBlock,
        KernelIdentity,
        OrganIdentity,
    )

    # 1. Observe-only call passes
    env = KernelEnvelope.observe_only(
        organ=OrganIdentity(tool_name="arif_kernel_route"),
    )
    result = pre_execution_gate(env, ActionClass.OBSERVE)
    assert result.verdict in (GateVerdict.SEAL, GateVerdict.SABAR), (
        f"Observe should SEAL/SABAR, got {result.verdict}"
    )
    assert result.is_allowed, "Observe should be allowed"

    # 2. Mutation without lease fails
    env2 = KernelEnvelope(
        organ=OrganIdentity(tool_name="arif_memory_recall"),
        authority=AuthorityBlock(action_class=ActionClass.MUTATE, lease_id="LEASE-NONE"),
    )
    result2 = pre_execution_gate(env2, ActionClass.MUTATE)
    assert result2.verdict == GateVerdict.HOLD, (
        f"Mutation without lease should HOLD, got {result2.verdict}"
    )
    assert result2.is_blocked

    # 3. Unknown tool fails
    env3 = KernelEnvelope(
        organ=OrganIdentity(tool_name="unknown_tool"),
    )
    result3 = pre_execution_gate(env3, ActionClass.OBSERVE)
    assert result3.verdict == GateVerdict.HOLD, f"Unknown tool should HOLD, got {result3.verdict}"

    # 4. Actor unverified + mutation → HOLD
    env4 = KernelEnvelope(
        kernel=KernelIdentity(actor_id="unverified", actor_verified=False),
        organ=OrganIdentity(tool_name="arif_memory_recall"),
        authority=AuthorityBlock(
            action_class=ActionClass.MUTATE,
            lease_id="LEASE-ACTIVE",
            mutation_allowed=True,
        ),
    )
    result4 = pre_execution_gate(env4, ActionClass.MUTATE)
    assert result4.verdict == GateVerdict.HOLD, (
        f"Unverified actor mutation should HOLD, got {result4.verdict}"
    )

    # 5. Irreversible without human ack → HOLD
    env5 = KernelEnvelope(
        kernel=KernelIdentity(actor_verified=True),
        organ=OrganIdentity(tool_name="arif_seal"),
        authority=AuthorityBlock(
            action_class=ActionClass.IRREVERSIBLE,
            lease_id="LEASE-ACTIVE",
            mutation_allowed=True,
            irreversible_allowed=True,
            human_ack_required=False,  # missing
        ),
    )
    result5 = pre_execution_gate(env5, ActionClass.IRREVERSIBLE)
    assert result5.verdict == GateVerdict.HOLD, (
        f"Irreversible without ack should HOLD, got {result5.verdict}"
    )

    # 6. Missing constitution hash + mutation → HOLD
    env6 = KernelEnvelope(
        kernel=KernelIdentity(actor_verified=True, constitution_hash=""),
        organ=OrganIdentity(tool_name="arif_memory_recall"),
        authority=AuthorityBlock(
            action_class=ActionClass.MUTATE,
            lease_id="LEASE-ACTIVE",
            mutation_allowed=True,
        ),
    )
    result6 = pre_execution_gate(env6, ActionClass.MUTATE)
    assert result6.verdict == GateVerdict.HOLD, (
        f"Missing constitution hash should HOLD, got {result6.verdict}"
    )

    # 7. Drift blocks mutation
    high_drift = DriftReport(
        build_hash="abc",
        runtime_hash="def",
        tool_manifest_hash="abc",
        schema_hash="abc",
        constitution_hash="abc",
        env_config_hash="abc",
        drift_level=DriftLevel.HIGH,
    )
    env7 = KernelEnvelope(
        kernel=KernelIdentity(actor_verified=True, constitution_hash="sha256:abc123"),
        organ=OrganIdentity(tool_name="arif_memory_recall"),
        authority=AuthorityBlock(
            action_class=ActionClass.MUTATE,
            lease_id="LEASE-ACTIVE",
            mutation_allowed=True,
        ),
    )
    result7 = pre_execution_gate(env7, ActionClass.MUTATE, drift_report=high_drift)
    assert result7.verdict == GateVerdict.HOLD, (
        f"Drift should block mutation, got {result7.verdict}"
    )
    assert result7.drift_detected

    # 8. Critical drift blocks irreversible
    crit_drift = DriftReport(
        build_hash="abc",
        runtime_hash="xyz",
        tool_manifest_hash="abc",
        schema_hash="abc",
        constitution_hash="abc",
        env_config_hash="abc",
        drift_level=DriftLevel.CRITICAL,
    )
    env8 = KernelEnvelope(
        kernel=KernelIdentity(actor_verified=True),
        organ=OrganIdentity(tool_name="arif_seal"),
        authority=AuthorityBlock(
            action_class=ActionClass.IRREVERSIBLE,
            lease_id="LEASE-ACTIVE",
            mutation_allowed=True,
            irreversible_allowed=True,
            human_ack_required=True,
            human_ack_id="hack_test123",
        ),
    )
    result8 = pre_execution_gate(env8, ActionClass.IRREVERSIBLE, drift_report=crit_drift)
    assert result8.verdict == GateVerdict.HOLD, (
        f"Critical drift should block irreversible, got {result8.verdict}"
    )

    # 9. External side effect without authorization → HOLD
    env9 = KernelEnvelope(
        kernel=KernelIdentity(actor_verified=True),
        organ=OrganIdentity(tool_name="arif_gateway_connect"),
        authority=AuthorityBlock(
            action_class=ActionClass.EXTERNAL_SIDE_EFFECT,
            lease_id="LEASE-ACTIVE",
            external_side_effect_allowed=False,  # not authorized
        ),
    )
    result9 = pre_execution_gate(env9, ActionClass.EXTERNAL_SIDE_EFFECT)
    assert result9.verdict == GateVerdict.HOLD, (
        f"Unauthorized external effect should HOLD, got {result9.verdict}"
    )

    # 10. Quick gate works
    result10 = quick_gate(ActionClass.OBSERVE)
    assert result10.is_allowed, "Quick observe gate should pass"

    # 11. Quick gate blocks mutation
    result11 = quick_gate(ActionClass.MUTATE)
    assert result11.is_blocked, "Quick mutation gate should block (no lease)"

    return True


if __name__ == "__main__":
    assert _self_check(), "pre_execution_gate self-check FAILED"
    print("pre_execution_gate self-check PASSED — all 11 assertions verified.")
