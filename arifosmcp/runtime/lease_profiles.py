"""
lease_profiles.py
═══════════════════════════════════════════════════════════════
Pre-built lease profiles for arifOS agents and organs.

Each profile maps a role to a bounded scope of capabilities
and a max_action_class ceiling. Profiles use capability paths
from capability_taxonomy.py — NOT fragile tool-name strings.

Profiles:
    OBSERVER   — Read-only across all safe domains. No mutation.
    DEVELOPER  — Read + dry-run. Shell previews, git status, FS reads.
    OPERATOR   — Full mutation within safe domains. No sealing.
    SOVEREIGN  — Full access including irreversible + external.

Usage:
    from arifosmcp.runtime.lease_profiles import get_profile, LEASE_PROFILES

ADR-003 (2026-08-04): Pre-built profiles for defense-in-depth.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from .capability_taxonomy import resolve_tools_for_capability


# ── Profile definition ──────────────────────────────────────


@dataclass
class LeaseProfile:
    """A pre-built lease profile with capability-based scope."""

    name: str
    description: str
    capability_scopes: list[str]  # e.g. ["capability:shell/dryrun", "capability:*/read"]
    max_action_class: str  # OBSERVE | DRY_RUN | MUTATE | IRREVERSIBLE
    forbidden_capabilities: list[str] = field(default_factory=list)  # Hard deny
    ttl_seconds: int = 300  # Default 5 minutes

    # ── Classical constants ─────────────────────────────────

    ELEVATED_MUTATE_CLASSES: ClassVar[list[str]] = [
        "EXTERNAL",
        "IRREVERSIBLE",
    ]

    OBSERVE_ONLY_CLASSES: ClassVar[list[str]] = [
        "OBSERVE",
        "REASON",
        "CRITIQUE",
    ]

    # ────────────────────────────────────────────────────────

    def expand_to_tool_names(self) -> list[str]:
        """Resolve capability paths to actual tool names."""
        tools: set[str] = set()
        for cap_path in self.capability_scopes:
            resolved = resolve_tools_for_capability(cap_path)
            tools.update(resolved)
        return sorted(tools)

    def expand_forbidden_to_tool_names(self) -> list[str]:
        """Resolve forbidden capability paths to tool names."""
        tools: set[str] = set()
        for cap_path in self.forbidden_capabilities:
            resolved = resolve_tools_for_capability(cap_path)
            tools.update(resolved)
        return sorted(tools)

    def to_lease_scope(self) -> list[str]:
        """Return scope entries for LeaseRecord.scope.

        Uses capability: prefix for semantic resolution.
        Falls back to plain tool names if legacy compatibility needed.
        """
        # Preferred: semantic capability paths
        return list(self.capability_scopes)

    def to_lease_forbidden(self) -> list[str]:
        """Return forbidden entries."""
        return list(self.forbidden_capabilities)


# ── Pre-built profiles ──────────────────────────────────────

LEASE_PROFILES: dict[str, LeaseProfile] = {
    # ── OBSERVER — Read-only, audit-safe ────────────────────
    "observer": LeaseProfile(
        name="observer",
        description=(
            "Read-only access to all safe domains. Can observe filesystem, "
            "git, vault, probes, VPS metrics, monitoring, and governance. "
            "NO mutation, NO shell execution, NO browser interaction, "
            "NO external communication."
        ),
        capability_scopes=[
            "capability:filesystem/read",
            "capability:git/inspect",
            "capability:github/read",
            "capability:fetch/read",
            "capability:fetch/search",
            "capability:fetch/docs",
            "capability:browser/read",
            "capability:vault/read",
            "capability:governance/inspect",
            "capability:governance/check",
            "capability:forge_meta/read",
            "capability:probe/read",
            "capability:vps/read",
            "capability:security/read",
            "capability:execution/read",
            "capability:execution/verify",
            "capability:monitoring/read",
            "capability:document/read",
            "capability:chart/generate",
        ],
        max_action_class="OBSERVE",
        forbidden_capabilities=[
            "capability:shell/*",
            "capability:execution/sandbox",
            "capability:browser/interact",
            "capability:browser/navigate",
            "capability:google/*",
            "capability:forge_meta/write",
            "capability:forge_meta/seal",
            "capability:forge_meta/generate",
        ],
    ),
    # ── DEVELOPER — Read + dry-run, no live mutation ────────
    "developer": LeaseProfile(
        name="developer",
        description=(
            "Read access + dry-run capabilities. Can preview shell commands, "
            "inspect git state, read files, search docs and web. "
            "NO live shell execution, NO file writes, NO docker mutation, "
            "NO database writes, NO sealing."
        ),
        capability_scopes=[
            # All read capabilities from observer
            "capability:*/read",
            "capability:*/inspect",
            "capability:*/search",
            "capability:*/docs",
            "capability:*/check",
            "capability:*/verify",
            # Dry-run only
            "capability:shell/dryrun",
            # Safe execution
            "capability:execution/read",
            "capability:execution/verify",
            "capability:execution/encode",  # Planning only
            "capability:execution/predict",  # Simulation only
            # Safe forge meta
            "capability:forge_meta/read",
            "capability:forge_meta/evaluate",
            "capability:forge_meta/witness",
            # Chart + document
            "capability:chart/generate",
            "capability:document/read",
            "capability:monitoring/read",
            # Governance
            "capability:governance/inspect",
            "capability:governance/check",
            "capability:governance/review",
        ],
        max_action_class="DRY_RUN",
        forbidden_capabilities=[
            "capability:shell/execute",
            "capability:filesystem/write",
            "capability:filesystem/delete",
            "capability:git/write",
            "capability:docker/*",
            "capability:database/*",
            "capability:google/*",
            "capability:vault/write",
            "capability:forge_meta/seal",
            "capability:forge_meta/generate",
            "capability:forge_meta/register",
            "capability:execution/manage",
            "capability:execution/seal",
            "capability:execution/sandbox",
            "capability:execution/orchestrate",
            "capability:browser/interact",
            "capability:browser/navigate",
            "capability:browser/execute",
        ],
    ),
    # ── OPERATOR — Full mutation within safe domains ────────
    "operator": LeaseProfile(
        name="operator",
        description=(
            "Full mutation access within safe domains. Can execute shell, "
            "write files, commit git, run docker, query DB, manage execution "
            "pipelines, generate tools, and route to organs. "
            "NO irreversible actions, NO VAULT999 sealing, NO external "
            "communication (Google), NO financial transfers."
        ),
        capability_scopes=[
            "capability:*",  # All capabilities...
        ],
        max_action_class="MUTATE",
        forbidden_capabilities=[
            # Hard blocks even for operators
            "capability:forge_meta/seal",  # Sealing is irreversible
            "capability:execution/seal",  # Visual seal
            "capability:google/*",  # External communication
            "capability:org_bridge/*",  # Cross-organ routing (domain organs judge themselves)
        ],
        ttl_seconds=600,  # 10 minutes for operators
    ),
    # ── SOVEREIGN — Full access, F13-gated ──────────────────
    "sovereign": LeaseProfile(
        name="sovereign",
        description=(
            "Full access — all tools, all domains, irreversible action permitted. "
            "REQUIRES F13 SOVEREIGN authority. Must be explicitly issued by Arif. "
            "This is the nuclear option — use with extreme care."
        ),
        capability_scopes=[
            "capability:*",
        ],
        max_action_class="IRREVERSIBLE",
        forbidden_capabilities=[
            # Even sovereign cannot self-authorize around F9 ANTI-HANTU
            # (tools that claim consciousness or fabricate reality are never callable)
        ],
        ttl_seconds=900,  # 15 minutes — short leash
    ),
    # ── AUDITOR — Read-only + drift detection ───────────────
    "auditor": LeaseProfile(
        name="auditor",
        description=(
            "Read-only access with additional drift/security scanning. "
            "Can surface-audit, security scan, entropy sweep, fingerprint check. "
            "NO mutation of any kind."
        ),
        capability_scopes=[
            "capability:*/read",
            "capability:*/inspect",
            "capability:*/search",
            "capability:*/check",
            "capability:*/verify",
            "capability:security/*",
            "capability:forge_meta/read",
            "capability:monitoring/read",
            "capability:probe/read",
            "capability:vps/read",
            "capability:document/read",
        ],
        max_action_class="OBSERVE",
        ttl_seconds=600,
    ),
    # ── GEOX_WORKER — Earth intelligence only ───────────────
    "geox_worker": LeaseProfile(
        name="geox_worker",
        description=(
            "Earth intelligence compute only. Can route to GEOX, read files, "
            "generate charts and documents, predict/evaluate models. "
            "NO shell, NO git mutation, NO browser, NO external comms."
        ),
        capability_scopes=[
            "capability:filesystem/read",
            "capability:fetch/*",
            "capability:chart/generate",
            "capability:document/read",
            "capability:execution/read",
            "capability:execution/predict",
            "capability:execution/verify",
            "capability:execution/encode",
            "capability:forge_meta/read",
            "capability:forge_meta/evaluate",
            "capability:forge_meta/witness",
            "capability:monitoring/read",
            "capability:governance/route",
        ],
        max_action_class="REASON",
        ttl_seconds=600,
    ),
}


# ── API ─────────────────────────────────────────────────────


def get_profile(name: str) -> LeaseProfile | None:
    """Look up a pre-built lease profile by name."""
    return LEASE_PROFILES.get(name)


def list_profiles() -> list[dict]:
    """Return summary of all available lease profiles."""
    return [
        {
            "name": p.name,
            "description": p.description,
            "max_action_class": p.max_action_class,
            "scope_count": len(p.capability_scopes),
            "tool_count": len(p.expand_to_tool_names()),
            "forbidden_count": len(p.forbidden_capabilities),
            "ttl_seconds": p.ttl_seconds,
        }
        for p in LEASE_PROFILES.values()
    ]


def resolve_profile_scope(profile_name: str) -> list[str] | None:
    """Resolve a profile's capability scopes to actual tool names.

    Returns None if profile not found.
    """
    profile = get_profile(profile_name)
    if profile is None:
        return None
    return profile.expand_to_tool_names()
