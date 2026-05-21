"""Session output schemas — 000_INIT

EMBODIMENT UPGRADE v2 — EUREKA
Atomic button awareness + blast-radius binding + VPS-root capability disclosure
"""

from __future__ import annotations

import os
import socket
from typing import Any

from pydantic import BaseModel, Field


class EmbodimentCard(BaseModel):
    """WAJIB — VPS-root agent embodiment disclosure."""

    body: str = "vps_root_runtime"
    host_attested: bool = True
    host: str = Field(default_factory=lambda: socket.gethostname())
    os: str = Field(default_factory=lambda: f"{os.uname().sysname} {os.uname().release}")
    privilege: str = Field(default_factory=lambda: "root" if os.geteuid() == 0 else "user")
    shell: list[str] = ["bash"]
    cwd: str = Field(default_factory=lambda: os.getcwd())
    package_managers: list[str] = ["npm", "bun", "pip", "git", "docker"]
    vcs: list[str] = ["git"]
    service_manager: str = "systemd"
    filesystem_scope: str = "full_root"
    network_scope: str = "localhost_only"
    container_runtime: bool = True
    execution_broker: str = "arif_forge_execute"
    mutation_default: str = "dry_run"
    side_effects_allowed_without_ack: bool = False
    atomic_capability_present: bool = True
    root_capability_present: bool = Field(default_factory=lambda: os.geteuid() == 0)


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

    primary: list[str] = Field(default_factory=lambda: [
        "root privilege detected",
        "filesystem mutation can be irreversible",
        "secrets may exist in env and dotfiles",
        "package installs can execute postinstall scripts",
        "service restarts affect availability",
        "network calls may leak data",
        "all mutation must pass FORGE/JUDGE gates",
    ])

    inference_constraints: list[str] = Field(default_factory=lambda: [
        "do not infer cryptographic identity",
        "do not infer permission to execute",
        "do not assume read-only is truly read-only",
        "classify command before execution",
        "detect destructive patterns before calling",
    ])


class ToolSurface(BaseModel):
    """Semantic capability map — not raw tool dump."""

    mode: str = "semantic_map"
    count: int = 0  # populated at runtime
    groups: dict[str, list[str]] = Field(default_factory=lambda: {
        "bootstrap": ["arif_session_init"],
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
    })
    gated: list[str] = Field(default_factory=lambda: [
        "memory_write",
        "gateway_relay",
        "vault_seal",
        "forge_write",
    ])
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
    """Full 000_INIT output — embodiment + capability + attention."""

    status: str = "OK"
    tool: str = "arif_session_init"
    mode: str = "init"

    # WAJIB categories
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

    # Output control
    output_contract: str = "compact"  # compact | seal_card | debug

    # Legacy compat (deprecated — use WAJIB fields above)
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    doctrine: dict[str, Any] | None = None
    timestamp: str | None = None
    actor_signature: str | None = None
    nonce: str | None = None
    signature_verified: bool = False
    constitution_bound: bool = False
    invariants_checked: list[str] = Field(default_factory=list)
