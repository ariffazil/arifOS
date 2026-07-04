"""
arifosmcp/kernel/interceptor.py — Constitutional Interceptor v0.3

THE CENTRAL PIECE. Every inbound MCP call passes through this function
before any tool is dispatched. It returns an AdmissibilityVerdict.

The kernel does not collapse reality. It collapses admissibility ambiguity.

A model produces possibilities. A tool produces effects. The kernel
decides admissibility. A vault preserves accountability.

Ungoverned intelligence: symbolic output can become physical consequence
without lawful transition.
Governed intelligence: symbolic output must pass admissibility before
becoming consequence.

v0.3 additions:
- Floor 9: Strange Loop — requires external anchor for mutations
- Floor 10: Anti-sink — simulation budget enforcement
- truth_class, witness, evidence_sources on every InterceptorDecision
- Gödel-lock: witness attachment for requires_external_witness capabilities

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from .capability_registry import get_capability_graph
from .models import (
    AdmissibilityVerdict,
    AuthorityTier,
    CapabilityNode,
    EvidenceSource,
    InterceptorDecision,
    InterceptorInput,
    MutationClass,
    SinkRisk,
    TruthClass,
    TrustState,
    Witness,
    WitnessType,
)

# ── P0.2 WIRING (2026-06-28): Enforcement spine integration ─────────────
try:
    from arifosmcp.core.latency_budget import (
        LATENCY_BUDGETS,
        DecisionClass as LatencyDecisionClass,
    )

    _LATENCY_BUDGET_AVAILABLE = True
except ImportError:
    _LATENCY_BUDGET_AVAILABLE = False
    LATENCY_BUDGETS = {}

try:
    from arifosmcp.core.conflict_resolver import resolve_conflict
    from arifosmcp.core.decision_contract import ConflictEnvelope

    _CONFLICT_RESOLVER_AVAILABLE = True
except ImportError:
    _CONFLICT_RESOLVER_AVAILABLE = False

logger = logging.getLogger(__name__)


# ── Normaliser ─────────────────────────────────────────────────────────────────


def _normalise_request(raw: dict[str, Any]) -> InterceptorInput:
    """Extract structured fields from a raw MCP tools/call payload."""
    params = raw.get("params", {})
    args = params.get("arguments", {})
    name = params.get("name", raw.get("name", "unknown"))

    # Try to extract actor from envelope or headers
    envelope = args.get("_envelope", {})
    if isinstance(envelope, dict):
        actor_id = envelope.get("actor_id") or envelope.get("actor", args.get("actor_id"))
        server_id = envelope.get("server_id") or envelope.get("organ", "local")
    else:
        actor_id = args.get("actor_id")
        server_id = "local"

    # Infer server_id from tool name prefix if not set in envelope
    if server_id == "local":
        known_organs = {
            "geox_": "geox",
            "wealth_": "wealth",
            "well_": "well",
            "aforge_": "a-forge",
            "aaa_": "aaa",
        }
        for prefix, organ in known_organs.items():
            if name.lower().startswith(prefix):
                server_id = organ
                break

    session_id = args.get("session_id")

    return InterceptorInput(
        raw_tool_name=name,
        raw_arguments=args,
        server_id=server_id,
        actor_id=str(actor_id) if actor_id else None,
        session_id=str(session_id) if session_id else None,
        authority_tier=AuthorityTier.LOW,
    )


# ── Tool alias resolver ───────────────────────────────────────────────────────
# Public MCP clients (ChatGPT, Claude, custom UIs) often surface tools with
# friendly aliases that drift from the canonical `arif_<noun>_<verb>` form.
# Without this, an honest user calling `arif_session_init` gets DENY because
# the capability graph only knows `arif_init`. The kernel must not punish
# the sovereign for naming drift — it must resolve aliases before lookup.

TOOL_ALIASES: dict[str, str] = {
    # Init family
    "arif_session_init": "arif_init",
    "session_init": "arif_init",
    "init": "arif_init",
    # Observe family
    "arif_search": "arif_observe",
    "search": "arif_observe",
    # Judge family
    "arif_deliberate": "arif_judge",
    "deliberate": "arif_judge",
    "judge": "arif_judge",
    # Seal family
    "vault_seal": "arif_seal",
    "seal": "arif_seal",
    # Think family
    "reason": "arif_think",
    "arif_reason": "arif_think",
    # Mind reason family (RSI 2026-06-22: per sovereign contract)
    "arifOS.arif_mind_reason": "arif_mind_reason",
    "mind_reason": "arif_mind_reason",
    "arif_mind": "arif_mind_reason",
    # Compose family
    "reply": "arif_compose",
    "arif_reply": "arif_compose",
    # Critique family
    "arif_heart": "arif_critique",
    "heart": "arif_critique",
    "arif_heart_critique": "arif_critique",
    # Measure family
    "vitals": "arif_measure",
    "arif_vitals": "arif_measure",
    # Route family
    "arif_router": "arif_route",
    # Triage family
    "arif_preflight": "arif_triage",
    # Kernel status family (RSI 2026-06-22: bootstrap floor)
    "arifOS.arif_kernel_status": "arif_kernel_status",
    "kernel_status": "arif_kernel_status",
    "arif_status": "arif_kernel_status",
    "status": "arif_kernel_status",
    # Memory recall
    "arif_recall": "arif_memory_recall",
    "recall": "arif_memory_recall",
    # ── Legacy aliases from contracts/tools.yaml (compiled 2026-06-25) ──
    # These MUST match contracts/tools.yaml legacy_aliases section.
    # Source of truth: the contract, not this dict.
    "arif_explore": "arif_observe",  # legacy, deprecated 2026-09-30
    "arif_memory": "arif_memory_recall",  # legacy, deprecated 2026-09-30
    "arif_bridge_connect": "arif_bridge",  # legacy, deprecated 2026-09-30
    "arif_conformance_report": "arif_kernel_status",  # legacy, deprecated 2026-09-30
    # arifos_* family (deprecated 2026-12-31)
    "arifos_init": "arif_init",
    "arifos_observe": "arif_observe",
    "arifos_judge": "arif_judge",
    "arifos_seal": "arif_seal",
    "arifos_forge": "arif_forge",
    "arifos_compose": "arif_compose",
    "arifos_critique": "arif_critique",
    "arifos_mind_reason": "arif_mind_reason",
    "arifos_route": "arif_route",
    "arifos_memory_recall": "arif_memory_recall",
    "arifos_bridge": "arif_bridge",
    "arifos_measure": "arif_measure",
    "arifos_canary": "arif_canary",
    "arifos_triage": "arif_triage",
    "arifos_fetch": "arif_fetch",
    "arifos_kernel_status": "arif_kernel_status",
    "arifos_kernel_attest": "arif_kernel_attest",
    "arifos_kernel_health": "arif_kernel_health",
    "arifos_kernel_intercept": "arif_kernel_intercept",
    "arifos_gateway_connect": "arif_gateway_connect",
    "hermes_vault_query_legacy": "arif_vault_query",
    "hermes_vault_query": "arif_vault_query",  # P3 fix 2026-06-30: canonical alias
}


def _resolve_tool_alias(tool_name: str) -> str:
    """Map public aliases to canonical tool names. Unknown → return as-is."""
    if not tool_name:
        return tool_name
    return TOOL_ALIASES.get(tool_name, tool_name)


# ── Authority resolver ─────────────────────────────────────────────────────────


def _resolve_authority(req: InterceptorInput) -> AuthorityTier:
    """Resolve the actor's authority tier.

    v0.2: semantic labels. Future: cryptographic nonce + session binding.

    v0.2.1 (2026-06-22): broaden to substring match so client variants like
    `arifbfazil`, `Arif Fazil`, `user_arif` resolve to SOVEREIGN.
    """
    if not req.actor_id:
        return AuthorityTier.LOW
    actor_lower = req.actor_id.lower().strip()
    # Exact match first (cheap, deterministic)
    if actor_lower in ("arif", "888"):
        return AuthorityTier.SOVEREIGN
    if actor_lower in ("root", "hermes"):
        return AuthorityTier.HIGH
    # Substring match for sovereign variants (case-insensitive)
    if "arif" in actor_lower or "888" in actor_lower:
        return AuthorityTier.SOVEREIGN
    if req.session_id:
        return AuthorityTier.MEDIUM
    return AuthorityTier.LOW


# ── Policy floors ──────────────────────────────────────────────────────────────


def _check_policy_floors(
    req: InterceptorInput,
    capability: CapabilityNode | None,
    authority: AuthorityTier,
) -> InterceptorDecision | None:
    """Apply constitutional policy floors against a CapabilityNode.

    Returns an InterceptorDecision (blocking) if policy is violated,
    or None if policy passes.
    """
    graph = get_capability_graph()

    # FLOOR 1: Unknown capability → DENY (safe default)
    if capability is None:
        # Help the caller recover: suggest canonical name if a near-alias exists
        requested_lower = req.raw_tool_name.lower()

        # BOOTSTRAP FAULT DETECTION (RSI 2026-06-22): if a bootstrap tool
        # (arif_kernel_status, arif_explain_denial, etc.) is itself unknown,
        # this is a kernel self-diagnosis failure — a deadlock. Surface it
        # distinctly so it cannot be mistaken for an ordinary unknown-cap.
        if requested_lower in {
            "arif_kernel_status",
            "arif_explain_denial",
            "arif_capability_list",
            "arif_contracts_tools",
            "status",
            "kernel_status",
        }:
            return InterceptorDecision(
                verdict=AdmissibilityVerdict.DENY,
                reason=(
                    f"BOOTSTRAP_FAULT: '{req.raw_tool_name}' is a bootstrap introspection "
                    f"capability but is not registered in the capability graph. "
                    f"This breaks kernel self-diagnosis. "
                    f"Sovereign action required: register the capability, restart arifOS, "
                    f"and re-probe."
                ),
                actor_id=req.actor_id,
                authority_tier=authority,
                resource_class=None,
                organ_id=None,
                normalized_request=req.model_dump(),
                graph_version=graph.version.version_id,
            )

        # Standard unknown-capability DENY with actionable suggestions.
        # RSI 2026-06-22: enriched to help the sovereign self-diagnose.
        hint = ""
        for alias, canonical in TOOL_ALIASES.items():
            if alias == requested_lower:
                hint = f" Did you mean '{canonical}'?"
                break
        # Find close matches by string containment
        close_matches = []
        for cap in graph.capabilities:
            if (
                requested_lower in cap.tool_name.lower()
                or requested_lower in cap.capability_id.lower()
            ):
                close_matches.append(cap.tool_name)
        close_hint = ""
        if close_matches and not hint:
            close_hint = f" Close matches: {', '.join(close_matches[:3])}."

        return InterceptorDecision(
            verdict=AdmissibilityVerdict.DENY,
            reason=(
                f"KERNEL_DENY: Capability not registered in graph.\n"
                f"  raw_capability: {req.raw_tool_name}\n"
                f"  normalized_capability: {_resolve_tool_alias(req.raw_tool_name)}\n"
                f"  actor: {req.actor_id}\n"
                f"  authority: {authority.value}\n"
                f"  graph_version: {graph.version.version_id}\n"
                f"{hint}{close_hint}\n"
                f"Suggested fixes:\n"
                f"  1. Register capability in /contracts/tools.yaml (ADR-009 proposed)\n"
                f"  2. Regenerate capability graph\n"
                f"  3. Check aliases: {list(TOOL_ALIASES.keys())[:5]}...\n"
                f"  4. Run arif_kernel_status for full capability list"
            ),
            actor_id=req.actor_id,
            authority_tier=authority,
            resource_class=None,
            organ_id=None,
            normalized_request=req.model_dump(),
            graph_version=graph.version.version_id,
        )

    # FLOOR 1b (RSI 2026-06-22): Bootstrap floor — bootstrap capabilities
    # are always admissible as read-only introspection, regardless of any
    # other check. This prevents the kernel from locking itself out of
    # self-diagnosis. Bootstrap tools MUST have mutation_class=NONE
    # (verified at registration, not here, for perf).
    if capability.bootstrap and capability.mutation_class == MutationClass.NONE:
        # Bypass remaining floors and return ADMIT_READ directly.
        return InterceptorDecision(
            verdict=AdmissibilityVerdict.ADMIT_READ,
            reason=(
                f"Bootstrap floor ADMIT: capability '{capability.capability_id}' "
                f"is bootstrap-protected. Read-only introspection always allowed."
            ),
            capability_id=capability.capability_id,
            actor_id=req.actor_id,
            authority_tier=authority,
            mutation_class=capability.mutation_class,
            blast_radius=capability.blast_radius,
            resource_class=capability.resource_class,
            organ_id=capability.organ_id,
            normalized_request=req.model_dump(),
            graph_version=graph.version.version_id,
        )

    # FLOOR 2: Trust state REVOKED → DENY
    if capability.trust_state == TrustState.REVOKED:
        return InterceptorDecision(
            verdict=AdmissibilityVerdict.DENY,
            reason=(
                f"Capability '{capability.capability_id}' has trust_state REVOKED. "
                f"This capability has been permanently withdrawn."
            ),
            capability_id=capability.capability_id,
            actor_id=req.actor_id,
            authority_tier=authority,
            mutation_class=capability.mutation_class,
            blast_radius=capability.blast_radius,
            normalized_request=req.model_dump(),
            graph_version=graph.version.version_id,
        )

    # FLOOR 3: Trust state QUARANTINED → QUARANTINE
    if capability.trust_state == TrustState.QUARANTINED:
        return InterceptorDecision(
            verdict=AdmissibilityVerdict.QUARANTINE,
            reason=(
                f"Capability '{capability.capability_id}' is QUARANTINED. "
                f"Component isolated pending investigation."
            ),
            capability_id=capability.capability_id,
            actor_id=req.actor_id,
            authority_tier=authority,
            mutation_class=capability.mutation_class,
            blast_radius=capability.blast_radius,
            normalized_request=req.model_dump(),
            graph_version=graph.version.version_id,
        )

    # FLOOR 4: .py mutation without allow_python_fallback → DENY
    # THE KEY INVARIANT that kills the universal Python fallback.
    tool_lower = req.raw_tool_name.lower()
    if (
        tool_lower in ("py", "python_repl", "python")
        and capability.mutation_class != MutationClass.NONE
    ):
        if not capability.allow_python_fallback:
            return InterceptorDecision(
                verdict=AdmissibilityVerdict.DENY,
                reason=(
                    f"Python execution ({req.raw_tool_name}) with mutation class "
                    f"'{capability.mutation_class.value}' is not allowed. "
                    f"Python is a governed capability, not a universal fallback. "
                    f"Use governed tools instead, or request ADMIT_SIMULATE for sandboxed mode."
                ),
                capability_id=capability.capability_id,
                actor_id=req.actor_id,
                authority_tier=authority,
                mutation_class=capability.mutation_class,
                blast_radius=capability.blast_radius,
                normalized_request=req.model_dump(),
                graph_version=graph.version.version_id,
            )

    # FLOOR 5: requires_888_hold AND not SOVEREIGN → HOLD_888
    if capability.requires_888_hold and authority != AuthorityTier.SOVEREIGN:
        return InterceptorDecision(
            verdict=AdmissibilityVerdict.HOLD_888,
            reason=(
                f"Capability '{capability.capability_id}' requires 888_HOLD. "
                f"Requires SOVEREIGN authority. Current: '{authority.value}'."
            ),
            capability_id=capability.capability_id,
            actor_id=req.actor_id,
            authority_tier=authority,
            mutation_class=capability.mutation_class,
            blast_radius=capability.blast_radius,
            resource_class=capability.resource_class,
            organ_id=capability.organ_id,
            normalized_request=req.model_dump(),
            graph_version=graph.version.version_id,
        )

    # FLOOR 6: Irreversible AND not SOVEREIGN → HOLD_888 (before authority check)
    # Irreversible with insufficient authority is an escalation prompt, not a hard block.
    if capability.irreversible and authority != AuthorityTier.SOVEREIGN:
        return InterceptorDecision(
            verdict=AdmissibilityVerdict.HOLD_888,
            reason=(
                f"Capability '{capability.capability_id}' is irreversible. "
                f"Requires SOVEREIGN authority. Current: '{authority.value}'."
            ),
            capability_id=capability.capability_id,
            actor_id=req.actor_id,
            authority_tier=authority,
            mutation_class=capability.mutation_class,
            blast_radius=capability.blast_radius,
            resource_class=capability.resource_class,
            organ_id=capability.organ_id,
            normalized_request=req.model_dump(),
            graph_version=graph.version.version_id,
        )

    # FLOOR 7: Authority too low for the capability → DENY
    authority_rank = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "SOVEREIGN": 3}
    if authority_rank.get(authority.value, 0) < authority_rank.get(
        capability.authority_required.value, 0
    ):
        return InterceptorDecision(
            verdict=AdmissibilityVerdict.DENY,
            reason=(
                f"Authority '{authority.value}' insufficient for capability "
                f"'{capability.capability_id}' which requires "
                f"'{capability.authority_required.value}'."
            ),
            capability_id=capability.capability_id,
            actor_id=req.actor_id,
            authority_tier=authority,
            mutation_class=capability.mutation_class,
            blast_radius=capability.blast_radius,
            resource_class=capability.resource_class,
            organ_id=capability.organ_id,
            normalized_request=req.model_dump(),
            graph_version=graph.version.version_id,
        )

    # FLOOR 7b (RSI 2026-06-22): Allowed-actors allowlist (per sovereign contract).
    # If the capability declares allowed_actors, only those actor_ids may invoke.
    # SOVEREIGN authority bypasses this gate (the human is always allowed).
    # Empty/None list = no per-actor restriction.
    if capability.allowed_actors and authority != AuthorityTier.SOVEREIGN:
        actor_norm = (req.actor_id or "").lower().strip()
        allowed_norm = {a.lower().strip() for a in capability.allowed_actors}
        # Substring match: "arifbfazil" matches "arif" in allowed_actors
        is_allowed = actor_norm in allowed_norm or any(sub in actor_norm for sub in allowed_norm)
        if not is_allowed:
            return InterceptorDecision(
                verdict=AdmissibilityVerdict.DENY,
                reason=(
                    f"Actor '{req.actor_id}' not in allowed_actors for capability "
                    f"'{capability.capability_id}'. Allowed: {capability.allowed_actors}. "
                    f"SOVEREIGN authority bypasses this check."
                ),
                capability_id=capability.capability_id,
                actor_id=req.actor_id,
                authority_tier=authority,
                mutation_class=capability.mutation_class,
                blast_radius=capability.blast_radius,
                resource_class=capability.resource_class,
                organ_id=capability.organ_id,
                normalized_request=req.model_dump(),
                graph_version=graph.version.version_id,
            )

    # FLOOR 8: Trust state < TRUSTED_READ for read-class capabilities
    if capability.mutation_class == MutationClass.NONE:
        if capability.trust_state not in (TrustState.TRUSTED_READ, TrustState.TRUSTED_MUTATE):
            return InterceptorDecision(
                verdict=AdmissibilityVerdict.QUARANTINE,
                reason=(
                    f"Capability '{capability.capability_id}' trust_state "
                    f"'{capability.trust_state.value}' is insufficient for read access. "
                    f"Must be at least TRUSTED_READ."
                ),
                capability_id=capability.capability_id,
                actor_id=req.actor_id,
                authority_tier=authority,
                mutation_class=capability.mutation_class,
                blast_radius=capability.blast_radius,
                normalized_request=req.model_dump(),
                graph_version=graph.version.version_id,
            )

    # ═════════════════════════════════════════════════════════════════════
    # THREE BEASTS FLOORS (Missions 001-003)
    # ═════════════════════════════════════════════════════════════════════

    # FLOOR 9 (Strange Loop — Mission 002):
    # External anchor required for mutations.
    # If capability.requires_external_anchor, ADMIT_MUTATE requires at least
    # one EXTERNAL_* evidence source. Prevents closed internal reality loops.
    if capability.requires_external_anchor and capability.mutation_class not in (
        MutationClass.NONE,
    ):
        evidence_sources_raw = req.raw_arguments.get("evidence_sources", [])
        if not isinstance(evidence_sources_raw, list):
            evidence_sources_raw = []
        evidence_sources = []
        has_external = False
        for src in evidence_sources_raw:
            try:
                es = EvidenceSource(src.upper()) if isinstance(src, str) else EvidenceSource.UNKNOWN
            except ValueError:
                es = EvidenceSource.UNKNOWN
            evidence_sources.append(es)
            if es.value.startswith("EXTERNAL_"):
                has_external = True

        if not has_external:
            return InterceptorDecision(
                verdict=AdmissibilityVerdict.DENY,
                reason=(
                    f"Strange loop blocked: capability '{capability.capability_id}' requires "
                    f"an external anchor for mutations, but no EXTERNAL_* evidence source was provided. "
                    f"Evidence sources received: {evidence_sources_raw}. "
                    f"Supply at least one external evidence source (EXTERNAL_DB, EXTERNAL_API, "
                    f"EXTERNAL_HUMAN, EXTERNAL_SENSOR, EXTERNAL_LAW, EXTERNAL_VAULT)."
                ),
                capability_id=capability.capability_id,
                actor_id=req.actor_id,
                authority_tier=authority,
                mutation_class=capability.mutation_class,
                blast_radius=capability.blast_radius,
                resource_class=capability.resource_class,
                organ_id=capability.organ_id,
                evidence_sources=evidence_sources,
                truth_class=TruthClass.CLAIM,
                normalized_request=req.model_dump(),
                graph_version=graph.version.version_id,
            )

    # FLOOR 10 (Anti-sink — Mission 003):
    # Simulation budget enforcement. If capability requires action or refusal log,
    # and simulation budget is exceeded, block further simulation.
    # Simulation count is read from request arguments (set by middleware).
    if capability.mutation_class == MutationClass.LOCAL_STATE:
        sim_count = req.raw_arguments.get("_simulation_count", 0)
        if not isinstance(sim_count, int):
            sim_count = 0
        action_count = req.raw_arguments.get("_action_count", 0)
        if not isinstance(action_count, int):
            action_count = 0
        max_sim = capability.max_simulations_before_action
        if max_sim > 0 and sim_count >= max_sim:
            return InterceptorDecision(
                verdict=AdmissibilityVerdict.HOLD_888,
                reason=(
                    f"Anti-sink HOLD: capability '{capability.capability_id}' has exceeded "
                    f"its simulation budget ({sim_count}/{max_sim}). "
                    f"Must either perform a bounded action or log a refusal before further simulation."
                ),
                capability_id=capability.capability_id,
                actor_id=req.actor_id,
                authority_tier=authority,
                mutation_class=capability.mutation_class,
                blast_radius=capability.blast_radius,
                resource_class=capability.resource_class,
                organ_id=capability.organ_id,
                sink_risk=SinkRisk.SINK_RISK,
                simulation_count_before_decision=sim_count,
                normalized_request=req.model_dump(),
                graph_version=graph.version.version_id,
            )

    # FLOOR 10-A (Anti-sink — Global SINK_CRITICAL threshold):
    # System-level guard: if any session has simulated >100 times with zero
    # actions, the entire system is at risk of behavioral sink.
    # This is NOT per-capability — it's per-session, system-wide.
    sim_count = req.raw_arguments.get("_simulation_count", 0)
    action_count = req.raw_arguments.get("_action_count", 0)
    if isinstance(sim_count, int) and isinstance(action_count, int):
        if sim_count > 100 and action_count == 0:
            return InterceptorDecision(
                verdict=AdmissibilityVerdict.HOLD_888,
                reason=(
                    f"ANTI-SINK SINK_CRITICAL: {sim_count} simulations with zero actions "
                    f"across this session. The system is at risk of behavioral sink — "
                    f"a beautiful corpse. Either perform a bounded action or log a formal "
                    f"refusal to VAULT999. This HOLD is the kernel's dead-man switch."
                ),
                capability_id=capability.capability_id,
                actor_id=req.actor_id,
                authority_tier=authority,
                mutation_class=capability.mutation_class,
                blast_radius=capability.blast_radius,
                resource_class=capability.resource_class,
                organ_id=capability.organ_id,
                sink_risk=SinkRisk.STERILE,
                simulation_count_before_decision=sim_count,
                normalized_request=req.model_dump(),
                graph_version=graph.version.version_id,
            )

    return None  # policy passes


# ── Main interceptor ──────────────────────────────────────────────────────────


def intercept(raw_request: dict[str, Any]) -> InterceptorDecision:
    """THE INTERCEPTOR. Every MCP call passes through here.

    Args:
        raw_request: The raw MCP JSON-RPC request dict.

    Returns:
        An InterceptorDecision that the transport layer must respect.
    """
    _t0 = time.monotonic()

    # Step 1: Normalise
    req = _normalise_request(raw_request)

    # Step 2: Resolve authority
    authority = _resolve_authority(req)

    # Step 3: Resolve tool alias → canonical name → query capability graph
    canonical_tool = _resolve_tool_alias(req.raw_tool_name)
    graph = get_capability_graph()
    capability = graph.query(
        server_id=req.server_id,
        tool_name=canonical_tool,
        actor_id=req.actor_id,
        authority=authority,
    )

    # Determine decision class from capability mutation class
    if capability and capability.mutation_class in (
        MutationClass.EXTERNAL,
        MutationClass.IRREVERSIBLE,
    ):
        decision_class_str = "C2_STANDARD"
    elif capability and capability.requires_888_hold:
        decision_class_str = "C2_STANDARD"
    else:
        decision_class_str = "C0_AUTO"

    # Standard floors always evaluated
    base_floors = ["F1", "F2", "F4", "F7", "F8", "F9", "F10", "F11"]

    # Step 4: Apply policy floors
    policy_block = _check_policy_floors(req, capability, authority)
    if policy_block is not None:
        policy_block.authority_tier = authority
        # Set truth_class for blocked decisions
        if policy_block.truth_class is None:
            if policy_block.verdict == AdmissibilityVerdict.HOLD_888:
                policy_block.truth_class = TruthClass.POLICY_VERDICT
            elif policy_block.verdict == AdmissibilityVerdict.QUARANTINE:
                policy_block.truth_class = TruthClass.POLICY_VERDICT
            else:
                policy_block.truth_class = TruthClass.CLAIM

        # ── P0.2: Populate latency + floor metadata ───────────────────────
        elapsed = (time.monotonic() - _t0) * 1000
        policy_block.latency_ms = round(elapsed, 2)
        policy_block.decision_class = decision_class_str
        policy_block.floors_evaluated = base_floors

        # Extract floor from reason if available
        if "FLOOR 1" in policy_block.reason or "FLOOR_1" in policy_block.reason:
            policy_block.floors_violated = ["F1"]
        elif "FLOOR 2" in policy_block.reason or "FLOOR_2" in policy_block.reason:
            policy_block.floors_violated = ["F2"]
        elif "FLOOR 4" in policy_block.reason:
            policy_block.floors_violated = ["F4"]
        elif "FLOOR 7" in policy_block.reason:
            policy_block.floors_violated = ["F7"]
        elif "FLOOR 8" in policy_block.reason:
            policy_block.floors_violated = ["F8"]
        elif "FLOOR 9" in policy_block.reason or "Strange loop" in policy_block.reason:
            policy_block.floors_violated = ["F9"]
        elif "FLOOR 10" in policy_block.reason or "Anti-sink" in policy_block.reason:
            policy_block.floors_violated = ["F10"]
        elif "FLOOR 11" in policy_block.reason:
            policy_block.floors_violated = ["F11"]

        # ── Latency budget check ──────────────────────────────────────────
        if _LATENCY_BUDGET_AVAILABLE:
            budget = LATENCY_BUDGETS.get(LatencyDecisionClass(decision_class_str))
            if budget and budget.max_latency_ms > 0 and elapsed > budget.max_latency_ms:
                policy_block.within_budget = False
                policy_block.reason += (
                    f"\n[LATENCY_BUDGET] Decision took {elapsed:.1f}ms "
                    f"(budget: {budget.max_latency_ms}ms for {decision_class_str}). "
                    f"Within constitutional latency envelope."
                )
            else:
                policy_block.within_budget = True

        return policy_block

    # Step 5: Classify admission
    assert capability is not None  # guaranteed by Floor 1
    if capability.mutation_class == MutationClass.NONE:
        verdict = AdmissibilityVerdict.ADMIT_READ
    elif capability.mutation_class in (MutationClass.LOCAL_STATE,):
        verdict = AdmissibilityVerdict.ADMIT_SIMULATE
    else:
        verdict = AdmissibilityVerdict.ADMIT_MUTATE

    # Determine truth class and sink risk for the decision
    if verdict == AdmissibilityVerdict.ADMIT_READ:
        truth_class = TruthClass.OBSERVATION
    elif verdict == AdmissibilityVerdict.ADMIT_SIMULATE:
        truth_class = TruthClass.SIMULATION
    else:
        truth_class = TruthClass.MUTATION_RECEIPT

    witness = None
    if capability.requires_external_witness and verdict == AdmissibilityVerdict.ADMIT_MUTATE:
        witness_raw = req.raw_arguments.get("witness", {})
        if isinstance(witness_raw, dict) and witness_raw.get("witness_type", "NONE") != "NONE":
            try:
                wt = WitnessType(witness_raw["witness_type"])
            except ValueError:
                wt = WitnessType.NONE
            witness = Witness(
                witness_type=wt,
                witness_id=witness_raw.get("witness_id", ""),
                nonce=witness_raw.get("nonce"),
                statement=witness_raw.get("statement", ""),
            )

    # ── P0.2: Check latency budget on admit path ──────────────────────────
    elapsed = (time.monotonic() - _t0) * 1000
    within_budget = True
    if _LATENCY_BUDGET_AVAILABLE:
        budget = LATENCY_BUDGETS.get(LatencyDecisionClass(decision_class_str))
        if budget and budget.max_latency_ms > 0 and elapsed > budget.max_latency_ms:
            within_budget = False

    # ── v42.0: Cross-organ conflict resolution (non-blocking) ─────────────
    # When witness data contains multiple organ verdicts, resolve conflicts.
    # This is advisory — blocks only on VOID/escalation, never silently overrides.
    conflict_result = None
    if _CONFLICT_RESOLVER_AVAILABLE and witness and witness.witness_type != WitnessType.NONE:
        witness_data = req.raw_arguments.get("witness", {})
        if isinstance(witness_data, dict):
            organ_a = witness_data.get("organ_a", "")
            organ_b = witness_data.get("organ_b", "")
            verdict_a = witness_data.get("verdict_a", "")
            verdict_b = witness_data.get("verdict_b", "")
            if organ_a and organ_b and verdict_a and verdict_b and verdict_a != verdict_b:
                try:
                    envelope = ConflictEnvelope(
                        conflict_id=f"{req.raw_tool_name}:{req.raw_arguments.get('session_id', '')}",
                        organ_a=organ_a,
                        verdict_a=verdict_a,
                        organ_b=organ_b,
                        verdict_b=verdict_b,
                        conflict_domain=capability.organ_id or "unknown",
                        is_irreversible=bool(capability.irreversible),
                    )
                    conflict_result = resolve_conflict(envelope)
                    if conflict_result.requires_888_hold:
                        logger.warning(
                            "Cross-organ conflict requires 888_HOLD: %s (%s vs %s)",
                            conflict_result.reason,
                            organ_a,
                            organ_b,
                        )
                except Exception as exc:
                    logger.debug("Conflict resolver skipped: %s", exc)

    # ── v42.0: Attach conflict resolution to reason (if resolved) ─────────
    conflict_note = ""
    if conflict_result and conflict_result.requires_888_hold:
        conflict_note = f" [CONFLICT: {conflict_result.resolution_method} → {conflict_result.winner_organ}/{conflict_result.winner_verdict}]"

    return InterceptorDecision(
        verdict=verdict,
        reason=(
            f"Capability '{capability.capability_id}' admitted "
            f"with class '{verdict.value}' (graph v{graph.version.version_id})."
            f"{' [LATENCY: ' + str(round(elapsed, 1)) + 'ms]' if elapsed > 10 else ''}"
            f"{conflict_note}"
        ),
        capability_id=capability.capability_id,
        actor_id=req.actor_id,
        authority_tier=authority,
        mutation_class=capability.mutation_class,
        blast_radius=capability.blast_radius,
        resource_class=capability.resource_class,
        organ_id=capability.organ_id,
        graph_version=graph.version.version_id,
        witness=witness,
        truth_class=truth_class,
        sink_risk=SinkRisk.NONE,
        normalized_request=req.model_dump(),
        # ── P0.2 fields ──
        latency_ms=round(elapsed, 2),
        within_budget=within_budget,
        decision_class=decision_class_str,
        floors_evaluated=base_floors,
        floors_violated=[],
    )
