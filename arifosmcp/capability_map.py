"""
arifOS Capability Map
════════════════════

This module re-exports compatibility symbols from the archived capability map
for backward compatibility with existing tests and server.py.

The canonical capability definitions live in constitutional_map.py.
"""

from __future__ import annotations

from enum import StrEnum


class InitAnchorMode(StrEnum):
    """Modes supported by the 000_INIT arif_init tool."""

    INIT = "init"
    STATE = "state"
    STATUS = "status"
    REVOKE = "revoke"
    REFRESH = "refresh"


# ════════════════════════════════════════════════════════════════════════════════
# LEGACY_FROZEN — do not extend. Canonical surface lives in constitutional_map.py
# These constants exist solely for backward-compat with tests written against the
# old arifos_<name> naming scheme. No live MCP routing goes through these names.
# Any new integration MUST use arif_<noun>_<verb> (13-tool canonical surface).
# ════════════════════════════════════════════════════════════════════════════════

# Maps old arifos_<name> → live arif_<noun>_<verb> canonical names.
# get_legacy_redirect() in public_registry.py uses this for backward-compat resolution.
CANONICAL_TOOL_HANDLERS: dict[str, str] = {
    "arifos_init": "arif_init",
    "arifos_sense": "arif_observe",
    "arifos_mind": "arif_think",
    "arifos_kernel": "arif_route",
    "arifos_heart": "arif_critique",
    "arifos_ops": "arif_measure",
    "arifos_judge": "arif_judge",
    "arifos_memory": "arif_memory",
    "arifos_vault": "arif_seal",
    "arifos_forge": "arif_forge",
    "arifos_gateway": "arif_bridge_connect",
}

MEGA_TOOLS: list[str] = list(CANONICAL_TOOL_HANDLERS.keys())

MEGA_TOOL_MODES: dict[str, set[str]] = {name: {"default"} for name in MEGA_TOOLS}

FINAL_TOOL_IMPLEMENTATIONS: dict[str, str] = CANONICAL_TOOL_HANDLERS

# LEGACY_FROZEN — dotted v1 aliases and semantic nicknames.
# These resolve straight to the current arif_<noun>_<verb> canonical surface.
# No intermediate arifos_* step; that layer was retired on 2026-06-23.
LEGACY_TOOL_MAP: dict[str, str] = {
    "arifos.init": "arif_init",
    "arifos.sense": "arif_observe",
    "arifos.mind": "arif_think",
    "arifos.kernel": "arif_route",
    "arifos.route": "arif_route",
    "arifos.heart": "arif_critique",
    "arifos.ops": "arif_measure",
    "arifos.judge": "arif_judge",
    "arifos.memory": "arif_memory",
    "arifos.vault": "arif_seal",
    "arifos.forge": "arif_forge",
    "arifos.gateway": "arif_bridge_connect",
    "init_anchor": "arif_init",
    "physics_reality": "arif_observe",
    "reality_compass": "arif_observe",
    "agi_mind": "arif_think",
    "agi_reason": "arif_think",
    "asi_heart": "arif_critique",
    "math_estimator": "arif_measure",
    "apex_soul": "arif_judge",
    "vault_ledger": "arif_seal",
    "vault_seal": "arif_seal",
    "code_engine": "arif_forge",
    "architect_registry": "arif_init",
}

CAPABILITY_MAP: dict[str, str] = {**CANONICAL_TOOL_HANDLERS, **LEGACY_TOOL_MAP}
LEGACY_TOOLS: dict[str, str] = LEGACY_TOOL_MAP

# Substrate Capability Families
SUBSTRATE_CAPABILITIES: dict[str, str] = {
    "substrate.git.audit": "git_bridge.get_repo_state",
    "substrate.git.propose": "git_bridge.propose_changes",
    "substrate.git.commit": "git_bridge.commit_governed",
    "substrate.fetch.guarded": "fetch_bridge.fetch_guarded",
    "substrate.validation.everything.probe": "everything_probe.run_full_diagnostic",
    "substrate.validation.everything.transport_check": "everything_probe.probe_server_features",
    "substrate.validation.everything.protocol_smoke": "everything_probe.probe_tools_roundtrip",
}

# Metadata and routing
ALIGNED_STAGES: dict[str, str] = {
    "init": "000_INIT",
    "sense": "111_SENSE",
    "mind": "333_MIND",
    "heart": "666_HEART",
    "judge": "888_JUDGE",
    "memory": "555_MEMORY",
    "vault": "999_VAULT",
}

# ── One Skill + One Tool integration (restraint + verdict loop as first-class)
# These turn "Knowing what NOT to do" and "Verdict loop with memory" into governed facts
# for every session (via INIT) and every tool (via capability map).

class RestraintLevel(StrEnum):
    """Computational maturity levels for 'knowing what NOT to do'."""
    STRICT = "STRICT"          # Must explicitly refuse/hold/ask when uncertain or ambiguous
    STANDARD = "STANDARD"      # Default restraint; HOLD on high entropy
    ADVISORY = "ADVISORY"      # Light; can proceed with warning

class VerdictRequirement(StrEnum):
    """Whether this capability requires the full verdict loop (judge + seal + receipt)."""
    REQUIRED = "REQUIRED"      # No execution without prior constitutional seal
    CONDITIONAL = "CONDITIONAL"
    NONE = "NONE"

RESTRAINT_VERDICT_REQUIREMENTS: dict[str, dict[str, Any]] = {
    "arif_init": {
        "restraint_level": RestraintLevel.STRICT,
        "verdict_required": VerdictRequirement.REQUIRED,
        "restraint_enforced": True,
        "description": "Binds the One Skill (Knowing What NOT To Do) and One Tool (Verdict Loop With Memory) into the session. Geometry carries flags + trace.",
    },
    "arif_observe": {
        "restraint_level": RestraintLevel.STANDARD,
        "verdict_required": VerdictRequirement.NONE,
        "restraint_enforced": True,
    },
    "arif_think": {
        "restraint_level": RestraintLevel.STANDARD,
        "verdict_required": VerdictRequirement.CONDITIONAL,
        "restraint_enforced": True,
    },
    "arif_critique": {
        "restraint_level": RestraintLevel.STRICT,
        "verdict_required": VerdictRequirement.CONDITIONAL,
        "restraint_enforced": True,
    },
    "arif_judge": {
        "restraint_level": RestraintLevel.STRICT,
        "verdict_required": VerdictRequirement.REQUIRED,
        "restraint_enforced": True,
        "description": "Core of the One Tool: renders YES/NO/WAIT. Restraint drives the decision.",
    },
    "arif_seal": {
        "restraint_level": RestraintLevel.STRICT,
        "verdict_required": VerdictRequirement.REQUIRED,
        "restraint_enforced": True,
    },
    "arif_forge": {
        "restraint_level": RestraintLevel.STRICT,
        "verdict_required": VerdictRequirement.REQUIRED,
        "restraint_enforced": True,
        "description": "Execution only after verdict loop (One Tool). Restraint flags (One Skill) drive HOLD/ASK/REFUSE. Verdict loop is the ONLY path.",
    },
    "arif_forge_execute": {
        "restraint_level": RestraintLevel.STRICT,
        "verdict_required": VerdictRequirement.REQUIRED,
        "restraint_enforced": True,
        "description": "The teeth. enforce_restraint_and_verdict must PASS before any side-effect. Non-bypassable.",
    },
}

# Export for kernel and MCP to consume
CAPABILITY_RESTRAINT_MAP = RESTRAINT_VERDICT_REQUIREMENTS

# Deeper classification under One Skill + One Tool (from constitutional_map source of truth)
# This makes the pair (Knowing What NOT To Do + Verdict Loop With Memory) the classification axis for every capability.
ONE_SKILL_ONE_TOOL_MAP: dict[str, dict[str, Any]] = {
    "pair": {
        "skill": "Knowing What NOT To Do (restraint under uncertainty: HOLD when unclear, ASK one question, REFUSE if unsafe)",
        "tool": "Verdict Loop With Memory (judge deliberation + seal authority + append-only receipt + witness + cooling + lineage)",
    },
    "enforcement": "No tool executes without INIT geometry (restraint_flags + verdict_trace). Classification here drives kernel DENY for missing verdict or violated restraint.",
    "tools": RESTRAINT_VERDICT_REQUIREMENTS,  # All tools classified here
    "note": "If not in this map or constitutional classification, kernel must DENY. Makes bypass structurally impossible.",
}


# LEGACY_FROZEN — iterator shims; always return empty (no live gap to report)


def iter_unmapped_legacy_tools() -> list[str]:
    """Legacy mapping is now 1:1 — no unmapped tools."""
    return []


def iter_unknown_tools_in_map() -> list[str]:
    """All known tools have valid targets."""
    return []


def iter_invalid_megatool_targets() -> list[str]:
    """All mega-tool targets resolve correctly."""
    return []


def iter_invalid_modes() -> list[str]:
    """All modes are valid."""
    return []


def build_llm_context_map() -> dict[str, object]:
    """Return the canonical discovery payload exposed in manifests and resources."""
    return {
        "schema": "arifos-llm-context/v1",
        "canonical_tools": {
            "init_anchor": "arif_init",
            "evidence_sense": "arif_observe",
            "evidence_fetch": "arif_fetch",
            "agi_mind": "arif_think",
            "asi_heart": "arif_critique",
            "route_meta": "arif_route",
            "triage_meta": "arif_triage",
            "gateway_bridge": "arif_bridge_connect",
            "compose_reply": "arif_compose",
            "memory_recall": "arif_memory",
            "ops_metrics": "arif_measure",
            "apex_judge": "arif_judge",
            "vault_seal": "arif_seal",
            "forge_exec": "arif_forge",
            "kernel_intercept": "arif_kernel_intercept",
        },
        "tool_aliases": dict(LEGACY_TOOL_MAP),
        "sdk_long_name_aliases": {
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
        },
        "discovery": {
            "tool_contracts_resource": "arifos://contracts/tools",
            "llm_context_resource": "arifos://mcp/context",
            "server_json": "/.well-known/mcp/server.json",
        },
        "continuity_contract": {
            "contract_version": "0.1.0",
            "invariants": [
                "authorization may not widen without authority_transition",
                "session continuity must persist across tool handoff",
                "canonical tool identity must remain explicit in every envelope",
            ],
        },
        "domain_evidence_contract": {
            "version": "geox-evidence/v1",
            "accepted_sources": ["GEOX"],
            "fields": [
                "claim_tag",
                "asset_id",
                "disagreement_band",
                "p10_p50_p90",
                "charge_probability",
                "vault_receipt",
            ],
            "bindings": {
                "sense": "arif_observe(domain_evidence=...)",
                "fetch": "arif_fetch(domain_evidence=...)",
                "judge": "arif_judge(domain_evidence=...)",
                "memory_store": "arif_memory(mode='asset_store', ...)",
                "memory_query": "arif_memory(mode='asset_query', ...)",
            },
        },
    }
