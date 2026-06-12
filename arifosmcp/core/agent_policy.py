"""
AgentPolicy — Declarative Agent Capability Model (MXC-Inspired)
══════════════════════════════════════════════════════════════════

FORGED 2026-06-09 by Ω (Omega) from MXC-arifOS contrast analysis.

ARCHITECTURAL EUREKA:
  MXC uses SandboxPolicy (declarative JSON) → ContainerConfig → executor → OS kernel.
  arifOS uses F1-F13 Laws (constitutional) → FloorEvaluator → GovernanceResult.

  The MISSING piece: arifOS has no DECLARATIVE policy model for agents.
  Agents either have full access (trusted) or none (untrusted). There is no
  graduated capability model.

  This module forges that missing piece: AgentPolicy — a versioned, immutable,
  declarative JSON schema that declares what an agent CAN and CANNOT do,
  mapped directly onto F1-F13 constitutional enforcement.

KEY INSIGHTS FROM MXC:
  1. Policy is DECLARATIVE (JSON), not imperative (code)
  2. Default-Deny: omitted fields = most restrictive permissions
  3. Policy is VERSIONED — schema version locks behavior
  4. Policy is SEPARATE from enforcement mechanism
  5. Cross-platform: same policy, different backends
    → arifOS parallel: same policy, different ORGANS (GEOX/WEALTH/WELL/etc)

APPLICATION TO arifOS:
  - Each agent (Omega, Hermes, Claude Code, OpenCode, Continue CLI, etc.)
    gets an AgentPolicy
  - The policy declares: which tools, which organs, which network domains,
    which filesystem paths, which irreversibility threshold
  - arifOS kernel enforces at Runtime — F1-F13 floors HOLD on violation
  - VAULT999 records every policy evaluation

COMPARISON TABLE:
  ┌─────────────────────┬──────────────────────┬──────────────────────┐
  │ Feature             │ MXC (Microsoft)      │ arifOS AgentPolicy   │
  ├─────────────────────┼──────────────────────┼──────────────────────┤
  │ Policy format       │ JSON schema v0.6.0   │ Pydantic v2 BaseModel│
  │ Enforcement layer   │ OS kernel (Rust)     │ Constitutional (Py)  │
  │ Scope               │ Filesystem, net, UI  │ Tools, organs, auth  │
  │ Default posture     │ Default-Deny         │ Default-Deny (HOLD)  │
  │ Versioning          │ Schema version lock  │ policy_version field │
  │ Lifecycle           │ provision→deprovision│ init→authorize→audit │
  │ Identity binding    │ containerId          │ agent_id + actor_id  │
  │ Audit               │ Defender + ETW       │ VAULT999 (Merkle)    │
  │ Human override      │ Agent 365 policy     │ F13 SOVEREIGN veto   │
  └─────────────────────┴──────────────────────┴──────────────────────┘

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import os
from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ─── Canonical Policy Version (incremented on schema change) ────────────────
POLICY_SCHEMA_VERSION = "1.0.0-forge-20260609"


# ═════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═════════════════════════════════════════════════════════════════════════════


class AgentRole(StrEnum):
    """Agent role in the federation — determines default capability baseline."""

    SOVEREIGN = "sovereign"  # F13 — Arif only
    JUDGE = "judge"  # 888_APEX — verdict authority
    ENGINEER = "engineer"  # Ω — forge, build, deploy
    ANALYST = "analyst"  # Read-only + analysis tools
    OBSERVER = "observer"  # Telemetry only, no mutations
    GATEWAY = "gateway"  # Cross-organ routing only
    CUSTOM = "custom"  # Explicitly defined capabilities


class IrreversibilityThreshold(StrEnum):
    """Maximum irreversibility level the agent may execute without 888_HOLD."""

    NONE = "none"  # Read-only only
    REVERSIBLE = "reversible"  # Can write temp files, create drafts
    PARTIAL = "partial"  # Can edit, update — undoable with effort
    IRREVERSIBLE = "irreversible"  # Can delete, deploy — EXCEPTIONALLY granted
    CRITICAL = "critical"  # Full access — SOVEREIGN only


class NetworkPosture(StrEnum):
    """Network access posture for the agent."""

    NONE = "none"  # No network access (air-gapped)
    LOCALHOST = "localhost"  # 127.0.0.1 only (federation organs)
    ALLOWLIST = "allowlist"  # Only domains in allowed_domains
    FULL = "full"  # Unrestricted


class FilesystemPosture(StrEnum):
    """Filesystem access posture."""

    NONE = "none"  # No filesystem access
    TMP_ONLY = "tmp_only"  # /tmp only
    WORKSPACE = "workspace"  # Project workspace + /tmp
    READ_ONLY = "read_only"  # Read-only on specified paths
    FULL = "full"  # Full read-write


# ═════════════════════════════════════════════════════════════════════════════
# POLICY MODEL
# ═════════════════════════════════════════════════════════════════════════════


class AgentPolicy(BaseModel):
    """Declarative policy for an agent in the arifOS federation.

    This is the MXC-equivalent SandboxPolicy for arifOS. It declares WHAT
    the agent is allowed to do. The kernel enforces HOW via F1-F13 floors.

    Default-Deny: any capability not explicitly granted is DENIED.
    """

    # ── Identity ──
    policy_version: str = Field(
        default=POLICY_SCHEMA_VERSION,
        description="Schema version — locks behavior contract.",
    )
    agent_id: str = Field(
        ...,
        description="Unique agent identifier (e.g., 'omega-forge', 'hermes-asi').",
    )
    agent_role: AgentRole = Field(
        default=AgentRole.ANALYST,
        description="Role determines default capability baseline.",
    )
    actor_id: str | None = Field(
        default=None,
        description="Bound human actor (e.g., 'arif-fazil'). None = agent-only.",
    )

    # ── Tool Surface ──
    allowed_tools: list[str] = Field(
        default_factory=list,
        description="Tools this agent may call. Empty = denied ALL tools.",
    )
    denied_tools: list[str] = Field(
        default_factory=list,
        description="Tools explicitly denied (overrides allowed_tools).",
    )
    allowed_organs: list[str] = Field(
        default_factory=list,
        description="Federation organs this agent may route to (GEOX/WEALTH/WELL/etc).",
    )

    # ── Resource Boundaries (MXC-equivalent) ──
    irreversibility_threshold: IrreversibilityThreshold = Field(
        default=IrreversibilityThreshold.REVERSIBLE,
        description="Max irreversibility level without 888_HOLD.",
    )
    network_posture: NetworkPosture = Field(
        default=NetworkPosture.LOCALHOST,
        description="Network access posture.",
    )
    allowed_domains: list[str] = Field(
        default_factory=list,
        description="Allowed outbound domains (only when posture=allowlist).",
    )
    filesystem_posture: FilesystemPosture = Field(
        default=FilesystemPosture.WORKSPACE,
        description="Filesystem access posture.",
    )
    readonly_paths: list[str] = Field(
        default_factory=list,
        description="Read-only paths (when filesystem_posture=read_only).",
    )
    readwrite_paths: list[str] = Field(
        default_factory=list,
        description="Read-write paths (when filesystem_posture=workspace).",
    )
    denied_paths: list[str] = Field(
        default=[
            "~/.ssh",
            "~/.aws",
            "~/.secrets",
            "/etc/shadow",
            "/etc/passwd",
            "/root/.secrets",
            os.environ.get("ARIFOS_HOME", "/root") + "/VAULT999",
        ],
        description="Paths ALWAYS denied regardless of posture.",
    )

    # ── Resource Limits ──
    max_tokens_per_call: int = Field(
        default=100_000,
        description="Maximum tokens per LLM call.",
    )
    max_concurrent_calls: int = Field(
        default=5,
        description="Maximum concurrent tool calls.",
    )
    max_runtime_seconds: int = Field(
        default=300,
        description="Maximum runtime per session (seconds). 0 = unlimited.",
    )
    max_disk_bytes: int = Field(
        default=100_000_000,  # 100 MB
        description="Maximum disk usage (bytes).",
    )

    # ── Governance ──
    require_888_hold: bool = Field(
        default=True,
        description="Require 888_HOLD for irreversible actions.",
    )
    require_human_review: bool = Field(
        default=False,
        description="Require human review before any action.",
    )
    auto_seal: bool = Field(
        default=False,
        description="Auto-seal to VAULT999 after each call.",
    )
    floor_overrides: dict[str, bool] = Field(
        default_factory=dict,
        description="Per-floor overrides (e.g., {'F9': False} = disable F9). "
        "SOVEREIGN only. Must be explicitly ratified.",
    )

    # ── Metadata ──
    description: str = Field(default="", description="Human-readable policy description.")
    tags: list[str] = Field(default_factory=list, description="Searchable tags.")
    forged_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO 8601 timestamp of policy creation.",
    )
    forged_by: str = Field(default="arifOS-forge-agent", description="Who created this policy.")
    parent_policy_hash: str | None = Field(
        default=None,
        description="SHA-256 of parent policy (for audit chain).",
    )

    # ── Validation ──

    @field_validator("policy_version")
    @classmethod
    def version_must_be_semver(cls, v: str) -> str:
        """Policy version must be valid semver-like."""
        parts = v.split(".")
        if len(parts) < 3:
            raise ValueError(f"policy_version must be semver-like: {v}")
        return v

    @field_validator("agent_id")
    @classmethod
    def agent_id_must_be_slug(cls, v: str) -> str:
        """Agent ID must be a valid slug."""
        import re

        if not re.match(r"^[a-z0-9]([a-z0-9._-]*[a-z0-9])?$", v):
            raise ValueError(f"agent_id must be a valid slug: {v}")
        return v

    def to_json(self) -> dict[str, Any]:
        """Export policy as JSON-serializable dict."""
        return self.model_dump(mode="json")

    def is_tool_allowed(self, tool_name: str) -> bool:
        """Check if a tool is allowed under this policy."""
        if tool_name in self.denied_tools:
            return False
        if not self.allowed_tools:
            return False  # Default-Deny
        return tool_name in self.allowed_tools

    def is_organ_allowed(self, organ_name: str) -> bool:
        """Check if an organ is reachable under this policy."""
        if not self.allowed_organs:
            return False  # Default-Deny
        return organ_name in self.allowed_organs

    def is_path_allowed(self, path: str, write: bool = False) -> bool:
        """Check if a filesystem path is permitted."""
        for denied in self.denied_paths:
            if path.startswith(denied.replace("~", "/root")):
                return False
        if self.filesystem_posture == FilesystemPosture.NONE:
            return False
        if self.filesystem_posture == FilesystemPosture.TMP_ONLY:
            return path.startswith("/tmp")
        if self.filesystem_posture == FilesystemPosture.FULL:
            return True
        return True  # workspace / read_only handled by caller

    def compute_policy_hash(self) -> str:
        """SHA-256 of the policy (for audit chain)."""
        import hashlib
        import json

        payload = json.dumps(self.model_dump(), sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()


# ═════════════════════════════════════════════════════════════════════════════
# PRESET POLICIES (MXC-equivalent: pre-built policy templates)
# ═════════════════════════════════════════════════════════════════════════════


def forge_sandbox_policy(agent_id: str) -> AgentPolicy:
    """Most restrictive policy — only safe for sandbox execution."""
    return AgentPolicy(
        agent_id=agent_id,
        agent_role=AgentRole.OBSERVER,
        irreversibility_threshold=IrreversibilityThreshold.NONE,
        network_posture=NetworkPosture.NONE,
        filesystem_posture=FilesystemPosture.TMP_ONLY,
        allowed_tools=[],
        allowed_organs=[],
        max_tokens_per_call=1000,
        max_concurrent_calls=1,
        max_runtime_seconds=60,
        max_disk_bytes=1_000_000,
        require_888_hold=True,
        require_human_review=True,
        description="Sandbox policy — most restrictive. For untrusted code execution.",
    )


def forge_observer_policy(agent_id: str) -> AgentPolicy:
    """Telemetry-only policy — read all, write nothing."""
    return AgentPolicy(
        agent_id=agent_id,
        agent_role=AgentRole.OBSERVER,
        irreversibility_threshold=IrreversibilityThreshold.NONE,
        network_posture=NetworkPosture.LOCALHOST,
        filesystem_posture=FilesystemPosture.READ_ONLY,
        allowed_tools=["arif_ops_measure", "arif_sense_observe", "arif_memory_recall"],
        allowed_organs=["GEOX", "WEALTH", "WELL"],
        description="Observer policy — telemetry only, no mutations.",
    )


def forge_analyst_policy(agent_id: str) -> AgentPolicy:
    """Read + analysis policy — can reason but not execute."""
    return AgentPolicy(
        agent_id=agent_id,
        agent_role=AgentRole.ANALYST,
        irreversibility_threshold=IrreversibilityThreshold.REVERSIBLE,
        network_posture=NetworkPosture.ALLOWLIST,
        allowed_domains=["github.com", "pypi.org", "npmjs.com"],
        allowed_tools=[
            "arif_session_init",
            "arif_memory_recall",
            "arif_sense_observe",
            "arif_mind_reason",
            "arif_reply_compose",
            "arif_evidence_fetch",
            "arif_ops_measure",
            "arif_heart_critique",
        ],
        allowed_organs=["GEOX", "WEALTH", "WELL", "AAA"],
        description="Analyst policy — read, reason, analyze. No execution.",
    )


def forge_engineer_policy(agent_id: str) -> AgentPolicy:
    """Full engineering policy — can build, test, deploy (gated by 888_HOLD)."""
    return AgentPolicy(
        agent_id=agent_id,
        agent_role=AgentRole.ENGINEER,
        irreversibility_threshold=IrreversibilityThreshold.IRREVERSIBLE,
        network_posture=NetworkPosture.FULL,
        allowed_tools=[
            "arif_session_init",
            "arif_memory_recall",
            "arif_sense_observe",
            "arif_mind_reason",
            "arif_reply_compose",
            "arif_evidence_fetch",
            "arif_ops_measure",
            "arif_heart_critique",
            "arif_judge_deliberate",
            "arif_forge_execute",
            "arif_vault_seal",
            "arif_kernel_route",
            "arif_gateway_connect",
        ],
        allowed_organs=["GEOX", "WEALTH", "WELL", "A-FORGE", "AAA"],
        max_tokens_per_call=200_000,
        max_concurrent_calls=10,
        max_runtime_seconds=3600,
        max_disk_bytes=500_000_000,
        require_888_hold=True,
        description="Engineer policy — full build/test/deploy, gated by 888_HOLD.",
    )


def forge_sovereign_policy(agent_id: str) -> AgentPolicy:
    """Sovereign-level policy — Arif only. All capabilities, F13 override."""
    return AgentPolicy(
        agent_id=agent_id,
        agent_role=AgentRole.SOVEREIGN,
        irreversibility_threshold=IrreversibilityThreshold.CRITICAL,
        network_posture=NetworkPosture.FULL,
        filesystem_posture=FilesystemPosture.FULL,
        allowed_tools=["*"],  # All tools
        allowed_organs=["*"],  # All organs
        max_tokens_per_call=1_000_000,
        max_concurrent_calls=50,
        max_runtime_seconds=0,  # Unlimited
        max_disk_bytes=0,  # Unlimited
        require_888_hold=False,
        require_human_review=False,
        auto_seal=True,
        denied_paths=[],  # No path restrictions
        description="SOVEREIGN policy — F13 override. Arif only.",
    )


# ─── REGISTRY ───────────────────────────────────────────────────────────────

PRESET_REGISTRY: dict[str, AgentPolicy] = {
    "sandbox": forge_sandbox_policy("sandbox-agent"),
    "observer": forge_observer_policy("observer-agent"),
    "analyst": forge_analyst_policy("analyst-agent"),
    "engineer": forge_engineer_policy("engineer-agent"),
    "sovereign": forge_sovereign_policy("sovereign-agent"),
}


def get_preset(name: str) -> AgentPolicy | None:
    """Get a preset policy by name. Returns None if not found."""
    return PRESET_REGISTRY.get(name)


def list_presets() -> list[str]:
    """List all available preset policy names."""
    return list(PRESET_REGISTRY.keys())
