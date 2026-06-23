"""Session output schemas — 000_INIT

EMBODIMENT UPGRADE v2 — EUREKA
Atomic button awareness + blast-radius binding + VPS-root capability disclosure
"""

from __future__ import annotations

import os
import socket
from typing import Any

from pydantic import BaseModel, Field


def _get_os_info() -> str:
    import platform

    if hasattr(os, "uname"):
        try:
            u = os.uname()
            return f"{u.sysname} {u.release}"
        except Exception:
            pass
    return (
        f"Windows {platform.win32_ver()[0]}"
        if platform.system() == "Windows"
        else platform.system()
    )


def _is_root() -> bool:
    if hasattr(os, "geteuid"):
        try:
            return os.geteuid() == 0
        except Exception:
            pass
    try:
        import ctypes

        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


class EmbodimentCard(BaseModel):
    """WAJIB — VPS-root agent embodiment disclosure."""

    body: str = "vps_root_runtime"
    host_attested: bool = True
    host: str = Field(default_factory=lambda: socket.gethostname())
    os: str = Field(default_factory=_get_os_info)
    privilege: str = Field(default_factory=lambda: "root" if _is_root() else "user")
    shell: list[str] = ["bash"]
    cwd: str = Field(default_factory=lambda: os.getcwd())
    package_managers: list[str] = ["npm", "bun", "pip", "git", "docker"]
    vcs: list[str] = ["git"]
    service_manager: str = "systemd"
    filesystem_scope: str = "full_root"
    network_scope: str = "localhost_only"
    container_runtime: bool = True
    execution_broker: str = "arif_forge"
    mutation_default: str = "dry_run"
    side_effects_allowed_without_ack: bool = False
    atomic_capability_present: bool = True
    root_capability_present: bool = Field(default_factory=_is_root)


class CausalityWarning(BaseModel):
    """WAJIB — agent must know text becomes machine action."""

    symbols_can_execute: bool = True
    execution_changes_state: bool = True
    state_change_has_blast_radius: bool = True
    text_becomes_irreversible_action: bool = True
    atomic_button_present: bool = True

    # Known atomic/destructive patterns
    atomic_patterns: list[str] = [
        "rm -rf /",
        "chmod -R 777 /",
        "dd if=/dev/zero of=/dev/sda",
        "git push --force",
        "DROP DATABASE",
        "systemctl stop",
        "curl secrets to external",
        "npm install unknown-package",
    ]


class ExecutionLaw(BaseModel):
    """WAJIB — what requires what."""

    read_only: str = "allowed"
    write_file: str = "requires_plan"
    install_package: str = "requires_ack"
    restart_service: str = "requires_ack"
    delete: str = "requires_ack"
    secret_access: str = "redacted_or_blocked"
    external_relay: str = "requires_judge_hash"
    irreversible: str = "explicit_arif_ack_required"
    root_blast_radius: str = "888_gate_required"


class AttentionSurface(BaseModel):
    """WAJIB — what the agent must watch before acting."""

    track_privilege: bool = True
    track_irreversibility: bool = True
    track_blast_radius: bool = True
    track_rollback: bool = True
    track_prompt_injection: bool = True

    primary: list[str] = Field(
        default_factory=lambda: [
            "root privilege detected",
            "filesystem mutation can be irreversible",
            "secrets may exist in env and dotfiles",
            "package installs can execute postinstall scripts",
            "service restarts affect availability",
            "network calls may leak data",
            "all mutation must pass FORGE/JUDGE gates",
        ]
    )

    inference_constraints: list[str] = Field(
        default_factory=lambda: [
            "do not infer cryptographic identity",
            "do not infer permission to execute",
            "do not assume read-only is truly read-only",
            "classify command before execution",
            "detect destructive patterns before calling",
        ]
    )


class ToolSurface(BaseModel):
    """Semantic capability map — not raw tool dump."""

    mode: str = "semantic_map"
    count: int = 0  # populated at runtime
    groups: dict[str, list[str]] = Field(
        default_factory=lambda: {
            "bootstrap": ["arif_init"],
            "sense": ["observe", "search", "ingest", "compass"],
            "evidence": ["fetch", "verify", "contradiction_scan"],
            "reason": ["reason", "critique", "plan"],
            "route": ["kernel", "stage", "lane"],
            "reply": ["compose"],
            "memory": ["recall", "context", "store"],
            "heart": ["redteam", "maruah", "deescalate", "empathize"],
            "ops": ["measure", "vitals", "cost", "health"],
            "judge": ["compare", "explain", "history"],
            "vault": ["verify", "chain", "dry_run"],
            "forge": ["query", "recall", "dry_run"],
            "gateway": ["discover", "handshake"],
            "guard": ["scan_local_instructions"],
        }
    )
    gated: list[str] = Field(
        default_factory=lambda: [
            "memory_write",
            "gateway_relay",
            "vault_seal",
            "forge_write",
        ]
    )
    raw_manifest_available: bool = True
    raw_manifest_location: str = "resource://agent/capabilities/raw"


class RiskLeash(BaseModel):
    """WAJIB — risk boundary disclosure."""

    status: str = "OPERATIONAL"
    max_action_class: str = "analyze"
    side_effects_allowed: bool = False
    degraded: bool = False
    reason: str | None = None


class SessionWarnings(BaseModel):
    """Computed warnings based on session state."""

    warnings: list[str] = Field(default_factory=list)
    identity_unverified: bool = True
    model_identity_unverified: bool = True
    risk_registry_unavailable: bool = False
    max_action_class_analyze_only: bool = False
    consent_not_established: bool = True
    personalization_without_consent: bool = False
    theory_of_mind_scaffold: str = "ToM-0"  # ToM-0 | ToM-1 | degraded


# ═══════════════════════════════════════════════════════════════════════════════
# ToM-1 UPGRADE — OPERATOR THEORY-OF-MIND SCAFFOLD
# ═══════════════════════════════════════════════════════════════════════════════


class OperatorIdentity(BaseModel):
    """
    Verified operator identity with trust chain.

    Replaces the flat actor_block with a structured identity model that
    distinguishes claimed vs verified vs delegated authority.
    """

    claimed_id: str = Field(description="Actor-provided identity string")
    verified_id: str | None = Field(default=None, description="Cryptographically verified identity")
    verification_method: str = Field(
        default="none",
        description="none | signature | token | delegation | biometric",
    )
    verification_provider: str | None = Field(
        default=None,
        description="Who performed the verification (e.g. 'arifOS_crypto_auth', 'delegated_from_apex')",
    )
    trust_level: str = Field(
        default="claimed",
        description="claimed | attested | verified | sovereign",
    )
    delegation_chain: list[dict] = Field(
        default_factory=list,
        description="Ordered list of delegations: [{delegator, delegatee, scope, expiry}]",
    )
    expires_at: str | None = Field(default=None, description="When this identity assertion expires")

    def is_verified(self) -> bool:
        return self.trust_level in ("verified", "sovereign")

    def is_sovereign(self) -> bool:
        return self.trust_level == "sovereign"


class IntentModel(BaseModel):
    """
    Operator intent model — not just authority, but purpose.

    Tracks declared intent, inferred intent, session objectives, and
    active commitments. This is the difference between "who can act"
    and "what they are trying to achieve."
    """

    declared_purpose: str | None = Field(
        default=None, description="Operator-stated purpose for this session"
    )
    inferred_purpose: str | None = Field(
        default=None,
        description="System-inferred purpose from context (HYPOTHESIS — never treated as fact)",
    )
    session_objective: str | None = Field(
        default=None, description="Concrete objective bound to this session"
    )
    intent_history: list[str] = Field(
        default_factory=list, description="Prior intents from continuous sessions"
    )
    commitment_tracked: bool = Field(
        default=False, description="Are active commitments being tracked?"
    )
    commitments: list[str] = Field(
        default_factory=list,
        description="Active commitments made by operator in this or prior sessions",
    )
    intent_drift_detected: bool = Field(
        default=False, description="Has operator intent drifted from declared purpose?"
    )
    intent_drift_flags: list[str] = Field(default_factory=list, description="Why drift was flagged")


class BeliefState(BaseModel):
    """
    Structured belief tracking about the operator and world.

    Each belief carries provenance and confidence. The system must not
    act on unproven beliefs about operator mental state.
    """

    operator_beliefs: list[dict] = Field(
        default_factory=list,
        description="Beliefs about operator state: [{proposition, confidence, provenance, verified}]",
    )
    system_beliefs: list[dict] = Field(
        default_factory=list,
        description="Beliefs the system holds about world state relevant to this session",
    )
    belief_provenance_required: bool = Field(
        default=True, description="Must every belief about operator carry provenance?"
    )
    unverified_beliefs_quarantined: bool = Field(
        default=True, description="Are unverified beliefs prevented from influencing action?"
    )


class PreferenceMemory(BaseModel):
    """
    Provenance-bound preference memory.

    Preferences without provenance cannot govern behavior.
    Preferences without consent cannot be used for personalization.
    """

    preferences: list[dict] = Field(
        default_factory=list,
        description="[{key, value, provenance, consented, timestamp}]",
    )
    provenance_bound: bool = Field(default=True, description="All preferences require provenance")
    consent_required_for_new: bool = Field(
        default=True, description="New preferences require explicit operator consent"
    )
    personalization_enabled: bool = Field(
        default=False, description="Is personalization active? (requires consent)"
    )


class FalseBeliefFlag(BaseModel):
    """
    Flags when operator claim conflicts with evidence.

    ToM-1 requires detecting that the operator may hold a false belief
    (e.g., "I committed X" when vault shows no such seal).
    """

    flags: list[dict] = Field(
        default_factory=list,
        description="[{operator_claim, evidence_contradicts, severity, resolution}]",
    )
    false_belief_detection_active: bool = Field(
        default=True, description="Is the system checking for operator false beliefs?"
    )
    humility_applied: bool = Field(
        default=True, description="Does the system flag its OWN possible false beliefs?"
    )


class WellMirrorEnhanced(BaseModel):
    """
    Enhanced WELL substrate mirror for operator readiness signals.

    ToM-1 requires knowing: Is the operator cognitively loaded?
    Is their dignity preserved? Are they being coerced?
    """

    operator_readiness: str | None = Field(
        default=None, description="WELL readiness signal: OPTIMAL | STABLE | DEGRADED | CRITICAL"
    )
    cognitive_load_signal: str | None = Field(
        default=None, description="WELL cognitive load: LOW | MEDIUM | HIGH | OVERLOAD"
    )
    dignity_preservation_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="WELL dignity score (0=violated, 1=fully preserved)",
    )
    coercion_signal_detected: bool = Field(
        default=False, description="WELL coercion detection flag"
    )
    well_informed: bool = Field(default=False, description="Did WELL provide data this session?")
    well_status: str = Field(
        default="unavailable", description="available | degraded | unavailable"
    )
    well_timestamp: str | None = Field(default=None, description="When WELL data was sampled")


class SessionContinuity(BaseModel):
    """
    Session continuity and commitment tracking.

    ToM-1 requires remembering prior commitments and detecting intent drift
    across sessions. Without continuity, every session is a stranger.
    """

    prior_session_id: str | None = Field(default=None, description="Linked prior session")
    continuity_established: bool = Field(
        default=False, description="Was continuity successfully established?"
    )
    prior_commitments: list[str] = Field(
        default_factory=list, description="Commitments inherited from prior sessions"
    )
    commitments_honored: list[str] = Field(
        default_factory=list, description="Commitments honored since last session"
    )
    commitments_breached: list[str] = Field(
        default_factory=list, description="Commitments breached (with reason)"
    )
    drift_detected: bool = Field(
        default=False, description="Has intent drifted from prior sessions?"
    )
    drift_flags: list[str] = Field(
        default_factory=list, description="Specific drift detection signals"
    )


class ConsentBoundaries(BaseModel):
    """
    Explicit consent boundaries for personalization and memory.

    ToM-1 must not become surveillance. Modeling operator behavior requires
    explicit consent. Without consent, the system operates in generic mode.
    """

    personalization_consent: bool = Field(
        default=False, description="Operator consented to behavior modeling/personalization"
    )
    memory_consent: bool = Field(
        default=False, description="Operator consented to persistent memory across sessions"
    )
    inference_consent: bool = Field(
        default=False, description="Operator consented to inference about their mental state"
    )
    theory_of_mind_consent: bool = Field(
        default=False,
        description="Operator consented to ToM-1 modeling (beliefs, preferences, intent)",
    )
    surveillance_warning: str = Field(
        default=(
            "Modeling operator behavior for assistance is not surveillance. "
            "However, persistent profiling without explicit consent violates F6 EMPATHY. "
            "ToM-1 scaffolds are quarantined until consent is established."
        )
    )
    privacy_boundaries: list[str] = Field(
        default_factory=list, description="Explicit privacy boundaries declared by operator"
    )
    consent_establishment_required: bool = Field(
        default=True, description="Must consent be established before ToM-1 activation?"
    )


class ContextCompletenessReceipt(BaseModel):
    """
    v3.1: Context completeness score for session bootstrap.

    High-stakes actions can be denied when context completeness < threshold.
    This makes missing context a first-class governed metric, not a silent deficiency.
    """

    timezone: str = Field(default="missing", description="timezone | missing | inferred")
    spatial_context: str = Field(
        default="missing", description="spatial_context | missing | inferred"
    )
    host_id: str = Field(default="missing", description="host_id | missing | attested")
    identity: str = Field(
        default="claimed_not_verified",
        description="claimed_not_verified | verified_operator | anonymous",
    )
    memory: str = Field(default="not_loaded", description="not_loaded | partial | full")
    session_provenance: str = Field(default="fresh", description="fresh | resumed | handover")
    score: float = Field(default=0.0, ge=0.0, le=1.0, description="0.0 = empty, 1.0 = complete")
    verdict: str = Field(
        default="DEGRADED_CONTEXT",
        description="COMPLETE_CONTEXT | DEGRADED_CONTEXT | MINIMAL_CONTEXT",
    )


class SessionState(BaseModel):
    session_id: str
    actor_id: str | None = None
    created_at: str | None = None
    stage: str = "000"
    lane: str = "AGI"
    entropy_delta: float = 0.0
    sealed: bool = False
    actor_signature: str | None = None
    nonce: str | None = None
    signature_verified: bool = False
    constitution_bound: bool = False


class SessionManifest(BaseModel):
    """Full 000_INIT output — embodiment + capability + attention + ToM-1 scaffold."""

    status: str = "OK"
    tool: str = "arif_init"
    mode: str = "init"

    # WAJIB categories (ToM-0 — operational orientation)
    session: SessionState | None = None
    actor: dict[str, Any] = Field(default_factory=dict)
    constitution: dict[str, Any] = Field(default_factory=dict)
    embodiment: EmbodimentCard | None = None
    causality_warning: CausalityWarning | None = None
    execution_law: ExecutionLaw | None = None
    attention_surface: AttentionSurface | None = None
    tool_surface: ToolSurface | None = None
    risk_leash: RiskLeash | None = None
    warnings: SessionWarnings | None = None

    # ToM-1 upgrade — operator theory-of-mind scaffold
    operator_identity: OperatorIdentity | None = None
    intent_model: IntentModel | None = None
    belief_state: BeliefState | None = None
    preference_memory: PreferenceMemory | None = None
    false_belief_flags: FalseBeliefFlag | None = None
    well_mirror_enhanced: WellMirrorEnhanced | None = None
    session_continuity: SessionContinuity | None = None
    consent_boundaries: ConsentBoundaries | None = None

    # Context completeness (v3.1)
    context_completeness: ContextCompletenessReceipt | None = None

    # Output control
    output_contract: str = "compact"  # compact | seal_card | debug

    # Legacy compat (deprecated — use WAJIB fields above)
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    doctrine: dict[str, Any] | None = None
    timestamp: str | None = None
    actor_signature: str | None = None
    nonce: str | None = None
    actor_verified: bool = Field(
        default=False, description="Whether the actor_id was cryptographically verified"
    )
    signature_verified: bool = False
    constitution_bound: bool = False
    invariants_checked: list[str] = Field(default_factory=list)
