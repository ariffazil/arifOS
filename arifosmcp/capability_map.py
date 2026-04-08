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
    probe = "probe"


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
    vector_query = "vector_query"
    vector_store = "vector_store"


class PhysicsRealityMode(str, Enum):
    search = "search"
    ingest = "ingest"
    compass = "compass"
    atlas = "atlas"
    time = "time"
    governed = "governed"


class MathEstimatorMode(str, Enum):
    cost = "cost"
    health = "health"
    vitals = "vitals"
    entropy = "entropy"


class CodeEngineMode(str, Enum):
    shell = "shell"
    api_call = "api_call"
    contract = "contract"
    compute = "compute"
    container = "container"
    vm = "vm"
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

class VpsMonitorMode(str, Enum):
    get_telemetry = "get_telemetry"
    get_zram_status = "get_zram_status"
    get_disk_usage = "get_disk_usage"


MEGA_TOOL_MODES: dict[str, set[str]] = {
    "arifos_init": {m.value for m in InitAnchorMode},
    "arifos_route": {m.value for m in KernelMode},
    "arifos_judge": {m.value for m in ApexSoulMode},
    "arifos_vault": {m.value for m in VaultLedgerMode},
    "arifos_mind": {m.value for m in AgiMindMode},
    "arifos_heart": {m.value for m in AsiHeartMode},
    "arifos_memory": {m.value for m in EngineeringMemoryMode},
    "arifos_sense": {m.value for m in PhysicsRealityMode},
    "arifos_ops": {m.value for m in MathEstimatorMode},
    "arifos_forge": {m.value for m in CodeEngineMode},
    "arifos_vps_monitor": {m.value for m in VpsMonitorMode},
}


# -----------------------------------------------------------------------------
# LEGACY TOOL SURFACE (MUST BE 100% COVERED)
# -----------------------------------------------------------------------------
LEGACY_TOOLS: set[str] = {
    "init_anchor",
    "arifOS_kernel",
    "apex_soul",
    "vault_ledger",
    "agi_mind",
    "asi_heart",
    "engineering_memory",
    "physics_reality",
    "math_estimator",
    "code_engine",
    "architect_registry",
    "system_health",
    "check_vital",
}


@dataclass
class CapabilityTarget:
    mega_tool: str
    mode: str
    description: str


CAPABILITY_MAP: dict[str, CapabilityTarget] = {
    # ---- Governance (000/444) ----
    "init_anchor": CapabilityTarget("arifos_init", "init", "Session ignition"),
    "architect_registry": CapabilityTarget("arifos_init", "init", "Registry fallback"),
    "arifOS_kernel": CapabilityTarget("arifos_route", "kernel", "Central kernel"),
    "route_intent": CapabilityTarget("arifos_route", "kernel", "Routing intent"),
    # ---- Intelligence (111/333) ----
    "physics_reality": CapabilityTarget("arifos_sense", "search", "Reality grounding"),
    "reality_search": CapabilityTarget("arifos_sense", "search", "Web search"),
    "agi_mind": CapabilityTarget("arifos_mind", "reason", "Structured reasoner"),
    "asi_heart": CapabilityTarget("arifos_heart", "critique", "Safety critique"),
    "asi_empathize": CapabilityTarget("arifos_heart", "critique", "Safety critique"),
    "asi_align": CapabilityTarget("arifos_heart", "critique", "Safety critique"),
    # ---- Machine (777/Vitals) ----
    "math_estimator": CapabilityTarget("arifos_ops", "cost", "Cost estimation"),
    "check_vital": CapabilityTarget("arifos_ops", "vitals", "Thermo vitals"),
    "system_health": CapabilityTarget("arifos_ops", "health", "Host health metrics"),
    "cost_estimator": CapabilityTarget("arifos_ops", "cost", "Cost estimator"),
    # ---- Code / machine ops (M-3) ----
    "fs_inspect": CapabilityTarget("arifos_forge", "fs", "Filesystem inspection"),
    "process_list": CapabilityTarget("arifos_forge", "process", "Process listing"),
    "net_status": CapabilityTarget("arifos_forge", "net", "Network status"),
    "log_tail": CapabilityTarget("arifos_forge", "tail", "Log tail"),
    "trace_replay": CapabilityTarget("arifos_forge", "replay", "Replay traces"),
    # ---- Engineering + memory (555/666) ----
    "agentzero_engineer": CapabilityTarget("arifos_memory", "engineer", "Material execution"),
    "agentzero_memory_query": CapabilityTarget("arifos_memory", "query", "Recall memory"),
    "chroma_query": CapabilityTarget("arifos_memory", "query", "Vector query"),
    # ---- APEX / governance (888) ----
    "apex_judge": CapabilityTarget("arifos_judge", "judge", "Verdict"),
    "audit_rules": CapabilityTarget("arifos_judge", "rules", "Inspect floors"),
    "agentzero_validate": CapabilityTarget("arifos_judge", "validate", "Validator"),
    "agentzero_hold_check": CapabilityTarget("arifos_judge", "hold", "Hold status"),
    "agentzero_armor_scan": CapabilityTarget("arifos_judge", "armor", "Injection scan"),
    "open_apex_dashboard": CapabilityTarget("arifos_judge", "rules", "Dashboard"),
    "apex_score_app": CapabilityTarget("arifos_judge", "rules", "Score UI"),
    "stage_pipeline_app": CapabilityTarget("arifos_judge", "rules", "Pipeline UI"),
    # ---- Vault (999) ----
    "vault_seal": CapabilityTarget("arifos_vault", "seal", "Seal ledger"),
    "verify_vault_ledger": CapabilityTarget("arifos_vault", "verify", "Verify ledger"),
}


def iter_unmapped_legacy_tools() -> list[str]:
    """Legacy tools missing from CAPABILITY_MAP."""
    return sorted([t for t in LEGACY_TOOLS if t not in CAPABILITY_MAP])


def iter_unknown_tools_in_map() -> list[str]:
    """CAPABILITY_MAP entries not present in LEGACY_TOOLS (typo guard)."""
    return sorted([t for t in CAPABILITY_MAP.keys() if t not in LEGACY_TOOLS])


def iter_invalid_megatool_targets() -> list[str]:
    allowed = {s.name for s in MEGA_TOOLS}
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
    "arifos_list_resources": CapabilityTarget("arifos_memory", "query", "fallback"),
    "arifos_read_resource": CapabilityTarget("arifos_memory", "query", "fallback"),
    "list_resources": CapabilityTarget("arifos_memory", "query", "fallback"),
    "metabolic_loop_router": CapabilityTarget("arifos_route", "kernel", "fallback"),
    "read_resource": CapabilityTarget("arifos_memory", "query", "fallback"),
    "register_tools": CapabilityTarget("arifos_route", "kernel", "fallback"),
})


def build_llm_context_map() -> dict[str, Any]:
    """
    Build a machine-readable context map for LLMs and remote MCP clients.

    This keeps legacy alias coverage while exposing the canonical arifOS tool
    surface, mode semantics, and continuity contract expectations in one place.
    """
    from .runtime.contracts import AAA_TOOL_LAW_BINDINGS, AAA_TOOL_STAGE_MAP, TRINITY_BY_TOOL

    canonical_tools: dict[str, Any] = {}
    for spec in MEGA_TOOLS:
        mega = spec.name
        aliases = sorted(
            legacy for legacy, target in CAPABILITY_MAP.items() if target.mega_tool == mega
        )
        canonical_tools[mega] = {
            "modes": sorted(list(MEGA_TOOL_MODES.get(mega, set()))),
            "stage": AAA_TOOL_STAGE_MAP.get(mega),
            "trinity": TRINITY_BY_TOOL.get(mega),
            "floors": AAA_TOOL_LAW_BINDINGS.get(mega, []),
            "legacy_aliases": aliases,
        }

    return {
        "schema": "arifos-llm-context/v1",
        "canonical_mega_tools": [s.name for s in MEGA_TOOLS],
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
                "reasoning",
                "metrics",
                "handoff",
            ],
            "recommended_flow": "init -> route -> (sense | mind | memory) -> heart -> ops -> judge -> vault",
        },
        "naming_alignment": {
            "canonical": "arifos.verb (e.g., arifos.init)",
            "internal": "arifos_verb (e.g., arifos_init)",
            "legacy": "snake_case (e.g., init_anchor)",
        }
    }
