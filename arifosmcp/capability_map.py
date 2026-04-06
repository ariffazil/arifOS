from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

# -----------------------------------------------------------------------------
# 11 CANONICAL MEGA-TOOLS (PUBLIC SURFACE TARGET)
# -----------------------------------------------------------------------------
from .runtime.tool_specs import MEGA_TOOLS, MegaToolName


# -----------------------------------------------------------------------------
# MODE ENUMS (STRICT)
# -----------------------------------------------------------------------------
class InitAnchorMode(str, Enum):
    init = "init"
    revoke = "revoke"
    refresh = "refresh"
    state = "state"
    status = "status"


class KernelMode(str, Enum):
    kernel = "kernel"
    status = "status"


class ApexSoulMode(str, Enum):
    judge = "judge"
    rules = "rules"
    validate = "validate"
    hold = "hold"
    armor = "armor"
    notify = "notify"
    probe = "probe"


class VaultLedgerMode(str, Enum):
    seal = "seal"
    verify = "verify"


class AgiMindMode(str, Enum):
    reason = "reason"
    reflect = "reflect"
    forge = "forge"


class AsiHeartMode(str, Enum):
    critique = "critique"
    simulate = "simulate"


class EngineeringMemoryMode(str, Enum):
    engineer = "engineer"
    query = "query"
    recall = "recall"
    write = "write"
    generate = "generate"


class PhysicsRealityMode(str, Enum):
    search = "search"
    ingest = "ingest"
    compass = "compass"
    atlas = "atlas"


class MathEstimatorMode(str, Enum):
    cost = "cost"
    health = "health"
    vitals = "vitals"


class CodeEngineMode(str, Enum):
    fs = "fs"
    process = "process"
    net = "net"
    tail = "tail"
    replay = "replay"


class ArchitectRegistryMode(str, Enum):
    register = "register"
    list = "list"
    read = "read"
    context = "context"


MEGA_TOOL_MODES: dict[str, set[str]] = {
    "init_session_anchor": {m.value for m in InitAnchorMode},
    "route_execution": {m.value for m in KernelMode},
    "judge_verdict": {m.value for m in ApexSoulMode},
    "record_vault_entry": {m.value for m in VaultLedgerMode},
    "reason_synthesis": {m.value for m in AgiMindMode},
    "critique_safety": {m.value for m in AsiHeartMode},
    "load_memory_context": {m.value for m in EngineeringMemoryMode},
    "sense_reality": {m.value for m in PhysicsRealityMode},
    "estimate_ops": {m.value for m in MathEstimatorMode},
    "execute_vps_task": {m.value for m in CodeEngineMode},
    "get_tool_registry": {m.value for m in ArchitectRegistryMode},
}


# -----------------------------------------------------------------------------
# LEGACY TOOL SURFACE (MUST BE 100% COVERED)
# -----------------------------------------------------------------------------
LEGACY_TOOLS: set[str] = {
    "init_anchor",
    "register_tools",
    "arifOS_kernel",
    "forge",
    "agi_reason",
    "agi_reflect",
    "reality_compass",
    "reality_atlas",
    "search_reality",
    "ingest_evidence",
    "asi_critique",
    "asi_simulate",
    "agentzero_engineer",
    "agentzero_memory_query",
    "apex_judge",
    "agentzero_validate",
    "audit_rules",
    "agentzero_armor_scan",
    "agentzero_hold_check",
    "check_vital",
    "open_apex_dashboard",
    "vault_seal",
    "verify_vault_ledger",
    "system_health",
    "fs_inspect",
    "process_list",
    "net_status",
    "log_tail",
    "cost_estimator",
    "chroma_query",
    "trace_replay",
    "list_resources",
    "read_resource",
    "arifos_list_resources",
    "arifos_read_resource",
    "metabolic_loop",
    "metabolic_loop_router",
    "apex_score_app",
    "stage_pipeline_app",
}


# -----------------------------------------------------------------------------
# CAPABILITY MAP (legacy tool -> mega_tool + mode)
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class CapabilityTarget:
    mega_tool: str
    mode: str
    note: str = ""


CAPABILITY_MAP: dict[str, CapabilityTarget] = {
    # ---- Governance / Bootstrap (000_INIT) ----
    "init_anchor": CapabilityTarget("init_session_anchor", "init", "Canonical init"),
    "arifOS_kernel": CapabilityTarget("route_execution", "kernel", "Canonical router"),
    "metabolic_loop": CapabilityTarget("route_execution", "kernel", "Legacy compatibility"),
    # ---- AGI (333/555) ----
    "agi_reason": CapabilityTarget("reason_synthesis", "reason", "Reasoning"),
    "agi_reflect": CapabilityTarget("reason_synthesis", "reflect", "Reflection"),
    "forge": CapabilityTarget("reason_synthesis", "forge", "Forge"),
    # ---- ASI (666) ----
    "asi_critique": CapabilityTarget("critique_safety", "critique", "Adversarial critique"),
    "asi_simulate": CapabilityTarget("critique_safety", "simulate", "Consequence simulation"),
    # ---- Reality / Physics (111/222) ----
    "search_reality": CapabilityTarget("sense_reality", "search", "External search"),
    "ingest_evidence": CapabilityTarget("sense_reality", "ingest", "URL/file -> evidence"),
    "reality_compass": CapabilityTarget("sense_reality", "compass", "Quick grounding"),
    "reality_atlas": CapabilityTarget("sense_reality", "atlas", "Evidence merge"),
    # ---- Math / telemetry (444) ----
    "check_vital": CapabilityTarget("estimate_ops", "vitals", "Thermo vitals"),
    "system_health": CapabilityTarget("estimate_ops", "health", "Host health metrics"),
    "cost_estimator": CapabilityTarget("estimate_ops", "cost", "Cost estimator"),
    # ---- Code / machine ops (M-3) ----
    "fs_inspect": CapabilityTarget("execute_vps_task", "fs", "Filesystem inspection"),
    "process_list": CapabilityTarget("execute_vps_task", "process", "Process listing"),
    "net_status": CapabilityTarget("execute_vps_task", "net", "Network status"),
    "log_tail": CapabilityTarget("execute_vps_task", "tail", "Log tail"),
    "trace_replay": CapabilityTarget("execute_vps_task", "replay", "Replay traces"),
    # ---- Engineering + memory (555/666) ----
    "agentzero_engineer": CapabilityTarget("load_memory_context", "engineer", "Material execution"),
    "agentzero_memory_query": CapabilityTarget("load_memory_context", "query", "Recall memory"),
    "chroma_query": CapabilityTarget("load_memory_context", "query", "Vector query"),
    # ---- APEX / governance (888) ----
    "apex_judge": CapabilityTarget("judge_verdict", "judge", "Verdict"),
    "audit_rules": CapabilityTarget("judge_verdict", "rules", "Inspect floors"),
    "agentzero_validate": CapabilityTarget("judge_verdict", "validate", "Validator"),
    "agentzero_hold_check": CapabilityTarget("judge_verdict", "hold", "Hold status"),
    "agentzero_armor_scan": CapabilityTarget("judge_verdict", "armor", "Injection scan"),
    "open_apex_dashboard": CapabilityTarget("judge_verdict", "rules", "Dashboard"),
    "apex_score_app": CapabilityTarget("judge_verdict", "rules", "Score UI"),
    "stage_pipeline_app": CapabilityTarget("judge_verdict", "rules", "Pipeline UI"),
    # ---- Vault (999) ----
    "vault_seal": CapabilityTarget("record_vault_entry", "seal", "Seal ledger"),
    "verify_vault_ledger": CapabilityTarget("record_vault_entry", "verify", "Verify ledger"),
}


def iter_unmapped_legacy_tools() -> list[str]:
    """Legacy tools missing from CAPABILITY_MAP."""
    return sorted([t for t in LEGACY_TOOLS if t not in CAPABILITY_MAP])


def iter_unknown_tools_in_map() -> list[str]:
    """CAPABILITY_MAP entries not present in LEGACY_TOOLS (typo guard)."""
    return sorted([t for t in CAPABILITY_MAP.keys() if t not in LEGACY_TOOLS])


def iter_invalid_megatool_targets() -> list[str]:
    allowed = set(MEGA_TOOLS)
    bad: list[str] = []
    for legacy, tgt in CAPABILITY_MAP.items():
        if tgt.mega_tool not in allowed:
            bad.append(f"{legacy} -> {tgt.mega_tool}:{tgt.mode}")
    return sorted(bad)


def iter_invalid_modes() -> list[str]:
    bad: list[str] = []
    for legacy, tgt in CAPABILITY_MAP.items():
        allowed_modes = MEGA_TOOL_MODES.get(tgt.mega_tool, set())
        if tgt.mode not in allowed_modes:
            bad.append(f"{legacy} -> {tgt.mega_tool}:{tgt.mode}")
    return sorted(bad)

CAPABILITY_MAP.update({
    "arifos_list_resources": CapabilityTarget("load_memory_context", "query", "fallback"),
    "arifos_read_resource": CapabilityTarget("load_memory_context", "query", "fallback"),
    "list_resources": CapabilityTarget("load_memory_context", "query", "fallback"),
    "metabolic_loop_router": CapabilityTarget("route_execution", "kernel", "fallback"),
    "read_resource": CapabilityTarget("load_memory_context", "query", "fallback"),
    "register_tools": CapabilityTarget("route_execution", "kernel", "fallback"),
})


def build_llm_context_map() -> dict[str, Any]:
    """
    Build a machine-readable context map for LLMs and remote MCP clients.

    This keeps legacy alias coverage while exposing the canonical arifOS tool
    surface, mode semantics, and continuity contract expectations in one place.
    """
    from .runtime.contracts import AAA_TOOL_LAW_BINDINGS, AAA_TOOL_STAGE_MAP, TRINITY_BY_TOOL

    canonical_tools: dict[str, Any] = {}
    for mega in MEGA_TOOLS:
        aliases = sorted(
            legacy for legacy, target in CAPABILITY_MAP.items() if target.mega_tool == mega
        )
        canonical_tools[mega] = {
            "modes": sorted(MEGA_TOOL_MODES.get(mega, set())),
            "stage": AAA_TOOL_STAGE_MAP.get(mega),
            "trinity": TRINITY_BY_TOOL.get(mega),
            "floors": AAA_TOOL_LAW_BINDINGS.get(mega, []),
            "legacy_aliases": aliases,
        }

    return {
        "schema": "arifos-llm-context/v1",
        "canonical_mega_tools": list(MEGA_TOOLS),
        "legacy_alias_count": len(CAPABILITY_MAP),
        "canonical_tools": canonical_tools,
        "continuity_contract": {
            "contract_version": "0.1.0",
            "required_sections": [
                "operator_summary",
                "declared_identity",
                "verified_identity",
                "session_binding",
                "authorization",
                "governance_closure",
                "policy_checks",
                "transitions",
                "handoff",
                "diagnostics",
            ],
            "invariants": [
                "verified_identity may not change without explicit verification",
                "authorization may not widen without authority_transition",
                "session continuity is versioned and trace-linked",
                "downstream tools must not infer authority from prior success",
            ],
        },
        "usage_guidance": {
            "bootstrap_path": [
                "get_tool_registry",
                "estimate_ops",
                "init_session_anchor",
                "route_execution",
            ],
            "global_session_rule": "global is diagnostics-only and must not authorize mutations",
            "preferred_reasoning_path": ["init_session_anchor", "reason_synthesis", "critique_safety", "judge_verdict"],
            "preferred_grounding_path": ["init_session_anchor", "sense_reality", "reason_synthesis"],
        },
    }


def build_llm_context_markdown() -> str:
    """Render the canonical LLM context map as markdown for llms.txt surfaces."""
    payload = build_llm_context_map()
    lines = [
        "## Canonical MCP Context",
        "",
        f"- Schema: `{payload['schema']}`",
        f"- Continuity Contract: `{payload['continuity_contract']['contract_version']}`",
        f"- Canonical Mega-Tools: `{', '.join(payload['canonical_mega_tools'])}`",
        "",
        "### Continuity Invariants",
    ]
    for invariant in payload["continuity_contract"]["invariants"]:
        lines.append(f"- {invariant}")

    lines.extend(["", "### Canonical Tools"])
    for name, spec in payload["canonical_tools"].items():
        aliases = ", ".join(spec["legacy_aliases"]) if spec["legacy_aliases"] else "none"
        lines.append(
            f"- `{name}` — stage `{spec['stage']}`, modes `{', '.join(spec['modes'])}`, "
            f"floors `{', '.join(spec['floors'])}`, aliases `{aliases}`"
        )

    lines.extend(["", "### Usage Guidance"])
    lines.append(
        f"- Bootstrap Path: `{', '.join(payload['usage_guidance']['bootstrap_path'])}`"
    )
    lines.append(f"- Global Session Rule: {payload['usage_guidance']['global_session_rule']}")
    lines.append(
        f"- Preferred Reasoning Path: `{', '.join(payload['usage_guidance']['preferred_reasoning_path'])}`"
    )
    lines.append(
        f"- Preferred Grounding Path: `{', '.join(payload['usage_guidance']['preferred_grounding_path'])}`"
    )
    return "\n".join(lines)
