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

import hashlib
import logging
import time
from typing import Any, Callable, Optional

from arifosmcp.schemas.kernel_envelope import (
    ActionClass,
    AuditEvent,
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
# TOOL MANIFEST — canonical list of what every tool is allowed to do
# ═══════════════════════════════════════════════════════════════════════════════

CANONICAL_TOOL_MANIFEST: dict[str, ToolManifestEntry] = {
    "arif_session_init": ToolManifestEntry(
        tool_name="arif_session_init",
        action_class=ActionClass.OBSERVE,
        safe_modes=["init", "resume", "validate", "status", "discover", "handover"],
        dangerous_modes=["revoke", "epoch_open", "epoch_seal"],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOW,
        is_reversible=True,
    ),
    "arif_sense_observe": ToolManifestEntry(
        tool_name="arif_sense_observe",
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
        blast_radius=BlastRadius.LOW,
        is_reversible=True,
    ),
    "arif_evidence_fetch": ToolManifestEntry(
        tool_name="arif_evidence_fetch",
        action_class=ActionClass.OBSERVE,
        safe_modes=["fetch", "search", "verify"],
        dangerous_modes=["archive"],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOW,
        is_reversible=True,
    ),
    "arif_mind_reason": ToolManifestEntry(
        tool_name="arif_mind_reason",
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
        blast_radius=BlastRadius.LOW,
        is_reversible=True,
    ),
    "arif_kernel_route": ToolManifestEntry(
        tool_name="arif_kernel_route",
        action_class=ActionClass.OBSERVE,
        safe_modes=["route", "stage", "lane", "list", "status", "context_runner"],
        dangerous_modes=[],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOW,
        is_reversible=True,
    ),
    "arif_reply_compose": ToolManifestEntry(
        tool_name="arif_reply_compose",
        action_class=ActionClass.DRAFT,
        safe_modes=["compose"],
        dangerous_modes=[],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOW,
        is_reversible=True,
    ),
    "arif_memory_recall": ToolManifestEntry(
        tool_name="arif_memory_recall",
        action_class=ActionClass.MUTATE,
        safe_modes=["recall", "get", "list", "search", "context", "dry_run", "manage"],
        dangerous_modes=["store", "prune"],
        requires_lease=True,
        requires_human_ack=False,
        blast_radius=BlastRadius.MEDIUM,
        is_reversible=True,
    ),
    "arif_heart_critique": ToolManifestEntry(
        tool_name="arif_heart_critique",
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
        blast_radius=BlastRadius.LOW,
        is_reversible=True,
    ),
    "arif_gateway_connect": ToolManifestEntry(
        tool_name="arif_gateway_connect",
        action_class=ActionClass.EXTERNAL_SIDE_EFFECT,
        safe_modes=["discover", "handshake"],
        dangerous_modes=["route", "relay"],
        requires_lease=True,
        requires_human_ack=True,
        blast_radius=BlastRadius.HIGH,
        is_reversible=True,
    ),
    "arif_ops_measure": ToolManifestEntry(
        tool_name="arif_ops_measure",
        action_class=ActionClass.OBSERVE,
        safe_modes=["health", "vitals", "cost", "predict", "genius", "psi_le", "omega", "landauer"],
        dangerous_modes=[],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOW,
        is_reversible=True,
    ),
    "arif_judge_deliberate": ToolManifestEntry(
        tool_name="arif_judge_deliberate",
        action_class=ActionClass.ANALYZE,
        safe_modes=["judge", "compare", "history", "explain"],
        dangerous_modes=[],
        requires_lease=False,
        requires_human_ack=False,
        blast_radius=BlastRadius.LOW,
        is_reversible=True,
    ),
    "arif_vault_seal": ToolManifestEntry(
        tool_name="arif_vault_seal",
        action_class=ActionClass.IRREVERSIBLE,
        safe_modes=["list", "verify", "chain", "dry_run"],
        dangerous_modes=["seal"],
        requires_lease=True,
        requires_human_ack=True,
        blast_radius=BlastRadius.CRITICAL,
        is_reversible=False,
    ),
    "arif_forge_execute": ToolManifestEntry(
        tool_name="arif_forge_execute",
        action_class=ActionClass.MUTATE,
        safe_modes=["query", "recall", "dry_run"],
        dangerous_modes=["engineer", "write", "generate", "commit"],
        requires_lease=True,
        requires_human_ack=True,
        blast_radius=BlastRadius.HIGH,
        is_reversible=False,
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
    manifest_entry = CANONICAL_TOOL_MANIFEST.get(tool_name)

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
        organ=OrganIdentity(tool_name="arif_vault_seal"),
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
        organ=OrganIdentity(tool_name="arif_vault_seal"),
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
