"""
ARIFOS CONSTITUTIONAL MAP (v2026.04.24-KANON)
═══════════════════════════════════════════════

Single source of truth for the active MCP surface:
- 13 canonical capability tools

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
    AGI = "AGI"
    ASI = "ASI"
    APEX = "APEX"


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
        "description": "000_INIT: Session bootstrap + identity binding.",
        "access": "public",
        "stage": ToolStage.INIT,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F01_AMANAH, Floor.F11_AUTH, Floor.F12_INJECTION],
        "risk_tier": "critical",
        "irreversible": False,
        "modes": ["init", "status", "discover", "handover", "revoke", "refresh"],
    },
    "arif_sense_observe": {
        "name": "arif_sense_observe",
        "description": "111_SENSE: Multimodal reality observation.",
        "access": "public",
        "stage": ToolStage.SENSE,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F02_TRUTH],
        "risk_tier": "low",
        "irreversible": False,
    },
    "arif_evidence_fetch": {
        "name": "arif_evidence_fetch",
        "description": "222_FETCH: Verified external evidence retrieval.",
        "access": "public",
        "stage": ToolStage.FETCH,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F02_TRUTH, Floor.F03_WITNESS],
        "risk_tier": "low",
        "irreversible": False,
    },
    "arif_mind_reason": {
        "name": "arif_mind_reason",
        "description": "333_MIND: Symbolic reasoning kernel.",
        "access": "public",
        "stage": ToolStage.MIND,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F02_TRUTH, Floor.F07_HUMILITY, Floor.F08_GENIUS],
        "risk_tier": "medium",
        "irreversible": False,
    },
    "arif_heart_critique": {
        "name": "arif_heart_critique",
        "description": "666_HEART: Ethical critique and impact assessment.",
        "access": "public",
        "stage": ToolStage.HEART,
        "lane": TrinityLane.ASI,
        "floors": [Floor.F05_PEACE, Floor.F06_EMPATHY],
        "risk_tier": "medium",
        "irreversible": False,
    },
    "arif_kernel_route": {
        "name": "arif_kernel_route",
        "description": "444_KERNEL: Central orchestration and tool routing.",
        "access": "public",
        "stage": ToolStage.KERNEL,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F01_AMANAH, Floor.F04_CLARITY],
        "risk_tier": "medium",
        "irreversible": False,
    },
    "arif_reply_compose": {
        "name": "arif_reply_compose",
        "description": "444_REPLY: Governed response composition.",
        "access": "public",
        "stage": ToolStage.REPLY,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F04_CLARITY, Floor.F06_EMPATHY, Floor.F09_ANTIHANTU],
        "risk_tier": "low",
        "irreversible": False,
    },
    "arif_memory_recall": {
        "name": "arif_memory_recall",
        "description": "555_MEMORY: Associative retrieval from VAULT999.",
        "access": "public",
        "stage": ToolStage.MEMORY,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F01_AMANAH, Floor.F08_GENIUS],
        "risk_tier": "low",
        "irreversible": False,
    },
    "arif_gateway_connect": {
        "name": "arif_gateway_connect",
        "description": "666_GATEWAY: Federated cross-agent bridge.",
        "access": "public",
        "stage": ToolStage.GATEWAY,
        "lane": TrinityLane.ASI,
        "floors": [Floor.F01_AMANAH, Floor.F03_WITNESS],
        "risk_tier": "medium",
        "irreversible": False,
    },
    "arif_judge_deliberate": {
        "name": "arif_judge_deliberate",
        "description": "888_JUDGE: Final constitutional arbitration.",
        "access": "public",
        "stage": ToolStage.JUDGE,
        "lane": TrinityLane.ASI,
        "floors": [Floor.F11_AUTH, Floor.F13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": False,
    },
    "arif_vault_seal": {
        "name": "arif_vault_seal",
        "description": "999_VAULT: Immutable ledger anchoring.",
        "access": "public",
        "stage": ToolStage.VAULT,
        "lane": TrinityLane.APEX,
        "floors": [Floor.F01_AMANAH, Floor.F11_AUTH],
        "risk_tier": "critical",
        "irreversible": True,
    },
    "arif_forge_execute": {
        "name": "arif_forge_execute",
        "description": "010_FORGE: System modification and build execution.",
        "access": "public",
        "stage": ToolStage.FORGE,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F01_AMANAH, Floor.F11_AUTH],
        "risk_tier": "critical",
        "irreversible": True,
    },
    "arif_ops_measure": {
        "name": "arif_ops_measure",
        "description": "777_OPS: Resource thermodynamics.",
        "access": "public",
        "stage": ToolStage.OPS,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F04_CLARITY],
        "risk_tier": "low",
        "irreversible": False,
    },
}

PROBE_TOOLS: tuple[str, ...] = ()
CONSTITUTIONAL_TOOLS: tuple[str, ...] = tuple(CANONICAL_TOOLS.keys())

def get_tool_spec(name: str) -> dict[str, Any] | None:
    return CANONICAL_TOOLS.get(name)


def list_canonical_tools() -> list[str]:
    return list(CANONICAL_TOOLS.keys())


def list_constitutional_tools() -> list[str]:
    return list(CONSTITUTIONAL_TOOLS)


def list_probe_tools() -> list[str]:
    return list(PROBE_TOOLS)


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
    from arifosmcp.tool_manifest import TOOL_MANIFEST, CANONICAL_ORDER

    return {
        "_schema": "arifos-ssct-v2026.04.26-kanon-phase2",
        "_note": (
            "Generated from arifosmcp.constitutional_map.CANONICAL_TOOLS + "
            "arifosmcp.tool_manifest.TOOL_MANIFEST. Do not hand edit."
        ),
        "canonical_count": len(CONSTITUTIONAL_TOOLS),
        "probe_count": len(PROBE_TOOLS),
        "total_surface": len(CANONICAL_TOOLS),
        "canonical_order": CANONICAL_ORDER,
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
                "operational": TOOL_MANIFEST.get(name, {}),
            }
            for name, spec in CANONICAL_TOOLS.items()
        },
        "motto": "DITEMPA BUKAN DIBERI — Forged, Not Given",
    }
