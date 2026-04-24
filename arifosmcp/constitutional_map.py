"""
ARIFOS CONSTITUTIONAL MAP (v2026.04.24-KANON)
═══════════════════════════════════════════════

Single source of truth for the 13-tool canonical surface.
Ditempa Bukan Diberi.
"""
from enum import Enum
from typing import Any


class Floor(str, Enum):
    F01_AMANAH = "F01"
    F02_TRUTH = "F02"
    F03_WITNESS = "F03"
    F04_CLARITY = "F04"
    F05_PEACE = "F05"
    F06_EMPATHY = "F06"
    F07_HUMILITY = "F07"
    F08_GENIUS = "F08"
    F09_ANTIHANTU = "F09"
    F10_ONTOLOGY = "F10"
    F11_AUTH = "F11"
    F12_INJECTION = "F12"
    F13_SOVEREIGN = "F13"


class TrinityLane(str, Enum):
    AGI = "AGI"   # Tactical — stages 000–777
    ASI = "ASI"   # Strategic — stage 888
    APEX = "APEX" # Authority — stage 999


class ToolStage(str, Enum):
    INIT = "000"
    SENSE = "111"
    MIND = "333"
    HEART = "666"
    KERNEL = "444"
    FORGE = "010"
    JUDGE = "888"
    VAULT = "999"
    OPS = "777"
    MEMORY = "555"
    FETCH = "222"
    REPLY = "444r"
    GATEWAY = "666g"


CANONICAL_TOOLS: dict[str, dict[str, Any]] = {
    "arif_session_init": {
        "name": "arif_session_init",
        "description": "000_INIT: Session bootstrap + identity binding. Constitutional ignition sequence.",
        "access": "public",
        "stage": ToolStage.INIT,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F01_AMANAH, Floor.F11_AUTH, Floor.F12_INJECTION],
        "risk_tier": "critical",
        "irreversible": False,
        "hold_condition": "Unverified actor on irreversible mode, or injection detected.",
        "modes": ["init", "status", "discover", "handover", "revoke", "refresh"],
    },
    "arif_sense_observe": {
        "name": "arif_sense_observe",
        "description": "111_SENSE: Reality-grounded observation. Evidence-preserving web ingestion and telemetry.",
        "access": "public",
        "stage": ToolStage.SENSE,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F02_TRUTH, Floor.F04_CLARITY, Floor.F07_HUMILITY],
        "risk_tier": "low",
        "irreversible": False,
        "output_contract": "Reality-grounded payload with confidence band Omega_0 in [0.03,0.05].",
        "modes": ["search", "ingest", "compass", "atlas", "entropy_dS", "vitals"],
    },
    "arif_mind_reason": {
        "name": "arif_mind_reason",
        "description": "333_MIND: Inductive reasoning engine. First-principles synthesis and QTT-enabled reflection.",
        "access": "public",
        "stage": ToolStage.MIND,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F02_TRUTH, Floor.F04_CLARITY, Floor.F07_HUMILITY, Floor.F08_GENIUS],
        "risk_tier": "medium",
        "irreversible": False,
        "output_contract": "Tagged CLAIM | PLAUSIBLE | HYPOTHESIS | ESTIMATE | UNKNOWN.",
        "modes": ["reason", "reflect", "forge", "debate", "socratic"],
    },
    "arif_heart_critique": {
        "name": "arif_heart_critique",
        "description": "666_HEART: Thermodynamic vitality monitor. Safety, empathy, and consequence modeling.",
        "access": "authenticated",
        "stage": ToolStage.HEART,
        "lane": TrinityLane.ASI,
        "floors": [Floor.F05_PEACE, Floor.F06_EMPATHY, Floor.F09_ANTIHANTU],
        "risk_tier": "high",
        "irreversible": False,
        "orthogonality": "Omega_ortho >= 0.95 vs arif_mind_reason.",
        "modes": ["critique", "simulate", "redteam", "maruah", "deescalate", "empathy"],
    },
    "arif_kernel_route": {
        "name": "arif_kernel_route",
        "description": "444_KERNEL: Kernel syscall and telemetry. Primary metabolic conductor and route dispatcher.",
        "access": "public",
        "stage": ToolStage.KERNEL,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F01_AMANAH, Floor.F04_CLARITY, Floor.F11_AUTH, Floor.F13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": False,
        "hold_condition": "risk_tier=critical requires F11 verified ID before execution.",
        "modes": ["route", "kernel", "triage", "delegate", "status", "telemetry"],
    },
    "arif_forge_execute": {
        "name": "arif_forge_execute",
        "description": "010_FORGE: Execution substrate dispatch. Signed manifest bridge to A-FORGE.",
        "access": "sovereign",
        "stage": ToolStage.FORGE,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F02_TRUTH, Floor.F04_CLARITY, Floor.F08_GENIUS, Floor.F13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": True,
        "output_contract": "Generated artifact + delta_S reduction metric.",
        "modes": ["engineer", "query", "recall", "write", "generate", "commit"],
    },
    "arif_judge_deliberate": {
        "name": "arif_judge_deliberate",
        "description": "888_JUDGE: Constitutional verdict engine. Sovereign judgment layer (ASI strategic).",
        "access": "authenticated",
        "stage": ToolStage.JUDGE,
        "lane": TrinityLane.ASI,
        "floors": [Floor.F01_AMANAH, Floor.F02_TRUTH, Floor.F08_GENIUS, Floor.F11_AUTH, Floor.F12_INJECTION, Floor.F13_SOVEREIGN],
        "risk_tier": "sovereign",
        "irreversible": False,
        "hold_condition": "Irreversible action, injection detected, or F13 veto required.",
        "modes": ["judge", "validate", "hold", "rules", "armor", "probe", "notify"],
    },
    "arif_vault_seal": {
        "name": "arif_vault_seal",
        "description": "999_VAULT: Immutable ledger. Merkle-hashed recording and audit engine.",
        "access": "authenticated",
        "stage": ToolStage.VAULT,
        "lane": TrinityLane.APEX,
        "floors": [Floor.F01_AMANAH, Floor.F02_TRUTH, Floor.F13_SOVEREIGN],
        "risk_tier": "sovereign",
        "irreversible": True,
        "hold_condition": "Any seal without prior arif_judge_deliberate verdict=SEAL.",
        "modes": ["seal", "verify", "ledger", "changelog", "audit"],
    },
    "arif_ops_measure": {
        "name": "arif_ops_measure",
        "description": "777_OPS: Operations and economic thermodynamics (WEALTH). Capacity and cost estimation.",
        "access": "public",
        "stage": ToolStage.OPS,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F02_TRUTH, Floor.F07_HUMILITY, Floor.F08_GENIUS],
        "risk_tier": "low",
        "irreversible": False,
        "output_contract": "JSON telemetry block compatible with arif_vault_seal footer.",
        "modes": ["health", "vitals", "cost", "genius", "psi_le", "omega", "landauer"],
    },
    "arif_memory_recall": {
        "name": "arif_memory_recall",
        "description": "555_MEMORY: Vector memory and context retrieval. Governed recall and engineering context.",
        "access": "public",
        "stage": ToolStage.MEMORY,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F04_CLARITY, Floor.F05_PEACE, Floor.F10_ONTOLOGY],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": ["recall", "store", "search", "prune", "context"],
    },
    "arif_evidence_fetch": {
        "name": "arif_evidence_fetch",
        "description": "222_FETCH: Evidence-preserving web ingestion. Reality-grounded fetch with data fencing.",
        "access": "public",
        "stage": ToolStage.FETCH,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F02_TRUTH, Floor.F03_WITNESS, Floor.F12_INJECTION],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": ["fetch", "search", "archive", "verify"],
    },
    "arif_reply_compose": {
        "name": "arif_reply_compose",
        "description": "444r_REPLY: Governed response compositor. Formats output with constitutional metadata.",
        "access": "public",
        "stage": ToolStage.REPLY,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F04_CLARITY, Floor.F05_PEACE, Floor.F10_ONTOLOGY],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["compose", "format", "nudge", "cite"],
    },
    "arif_gateway_connect": {
        "name": "arif_gateway_connect",
        "description": "666g_GATEWAY: Cross-agent routing (A2A). Federation hub for agent-to-agent protocol.",
        "access": "authenticated",
        "stage": ToolStage.GATEWAY,
        "lane": TrinityLane.ASI,
        "floors": [Floor.F01_AMANAH, Floor.F11_AUTH, Floor.F13_SOVEREIGN],
        "risk_tier": "high",
        "irreversible": False,
        "modes": ["route", "discover", "handshake", "seal"],
    },
}

def get_tool_spec(name: str) -> dict[str, Any] | None:
    return CANONICAL_TOOLS.get(name)


def list_canonical_tools() -> list[str]:
    return list(CANONICAL_TOOLS.keys())


def _list_tools_by_access(access: str) -> list[str]:
    return [name for name, spec in CANONICAL_TOOLS.items() if spec.get("access") == access]


def list_public_tools() -> list[str]:
    return _list_tools_by_access("public")


def list_authenticated_tools() -> list[str]:
    return _list_tools_by_access("authenticated")


def list_sovereign_tools() -> list[str]:
    return _list_tools_by_access("sovereign")


def get_floor_bindings() -> dict[str, list[Floor]]:
    return {name: data["floors"] for name, data in CANONICAL_TOOLS.items()}


def build_tool_registry_manifest() -> dict[str, Any]:
    return {
        "_schema": "arifos-ssct-v2026.04.24-kanon-phase1",
        "_note": (
            "Generated from arifosmcp.constitutional_map.CANONICAL_TOOLS. "
            "Do not hand edit."
        ),
        "canonical_count": len(CANONICAL_TOOLS),
        "total_surface": len(CANONICAL_TOOLS),
        "tools": {
            name: {
                "stage": spec["stage"].value,
                "lane": spec["lane"].value,
                "floors": [floor.value for floor in spec["floors"]],
                "risk_tier": spec["risk_tier"],
                "irreversible": spec["irreversible"],
                "access": spec["access"],
                "requires_auth": spec["access"] != "public",
                "tags": ["canonical"],
            }
            for name, spec in CANONICAL_TOOLS.items()
        },
        "motto": "DITEMPA BUKAN DIBERI — Forged, Not Given",
    }
