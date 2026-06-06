"""
arifosmcp/runtime/substrate_policy.py — The Intelligence Mapping for AAA Wire

This policy defines the Substrate Capability Class, Risk Tier, and Constitutional
Floors for every mode in the M-11 Mega-Tool surface.
"""

from dataclasses import dataclass
from enum import StrEnum


class SubstrateClass(StrEnum):
    INSPECT = "inspect"
    READ = "read"
    RECALL = "recall"
    WRITE = "write"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    COMMIT = "commit"
    COMMUNICATE = "communicate"


class RiskTier(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ModePolicy:
    substrate: SubstrateClass
    risk: RiskTier
    organ_stage: str
    floors: list[str]  # Explicit Floor Mapping
    description: str


# The Canonical AAA Tool Policy Matrix
AAA_SUBSTRATE_POLICY = {
    "arifos.init": {
        "init": ModePolicy(
            SubstrateClass.WRITE,
            RiskTier.LOW,
            "000_INIT",
            ["F1", "L11", "L12"],
            "Bind session identity",
        ),
        "state": ModePolicy(
            SubstrateClass.INSPECT,
            RiskTier.LOW,
            "000_INIT",
            ["L11"],
            "Check session status",
        ),
        "refresh": ModePolicy(
            SubstrateClass.UPDATE, RiskTier.MEDIUM, "000_INIT", ["L11"], "Rotate tokens"
        ),
        "revoke": ModePolicy(
            SubstrateClass.DELETE,
            RiskTier.HIGH,
            "000_INIT",
            ["L11", "L13"],
            "Kill session authority",
        ),
    },
    "arifos.sense": {
        "search": ModePolicy(
            SubstrateClass.READ,
            RiskTier.MEDIUM,
            "111_OBSERVE",
            ["F2", "F3"],
            "Web grounding",
        ),
        "ingest": ModePolicy(
            SubstrateClass.WRITE,
            RiskTier.MEDIUM,
            "111_OBSERVE",
            ["F2", "L10"],
            "Evidence creation",
        ),
        "compass": ModePolicy(
            SubstrateClass.READ,
            RiskTier.LOW,
            "111_OBSERVE",
            ["F2"],
            "Directional grounding",
        ),
        "atlas": ModePolicy(
            SubstrateClass.UPDATE,
            RiskTier.MEDIUM,
            "111_OBSERVE",
            ["F2", "F3"],
            "Multi-source mapping",
        ),
    },
    "arifos.mind": {
        "reason": ModePolicy(
            SubstrateClass.READ,
            RiskTier.MEDIUM,
            "333_REASON",
            ["F2", "F4", "F7", "F8"],
            "First-principles logic",
        ),
        "reflect": ModePolicy(
            SubstrateClass.INSPECT,
            RiskTier.MEDIUM,
            "333_REASON",
            ["F4", "F7"],
            "Self-audit loop",
        ),
        "forge": ModePolicy(
            SubstrateClass.WRITE,
            RiskTier.MEDIUM,
            "333_REASON",
            ["F1", "F8"],
            "Artifact synthesis",
        ),
    },
    "arifos.heart": {
        "critique": ModePolicy(
            SubstrateClass.READ,
            RiskTier.MEDIUM,
            "444_CRITIQUE",
            ["F5", "F6", "F9"],
            "Adversarial safety audit",
        ),
        "simulate": ModePolicy(
            SubstrateClass.READ,
            RiskTier.MEDIUM,
            "444_CRITIQUE",
            ["F5", "F6"],
            "Stakeholder impact modeling",
        ),
    },
    "arifos.memory": {
        "vector_query": ModePolicy(
            SubstrateClass.RECALL,
            RiskTier.MEDIUM,
            "555m_MEMORY",
            ["L10"],
            "Semantic retrieval",
        ),
        "vector_store": ModePolicy(
            SubstrateClass.WRITE,
            RiskTier.MEDIUM,
            "555m_MEMORY",
            ["L10"],
            "Memory commit",
        ),
        "engineer": ModePolicy(
            SubstrateClass.EXECUTE,
            RiskTier.HIGH,
            "555m_MEMORY",
            ["F1", "L11", "L13"],
            "High-stakes tool generation",
        ),
    },
    "arifos.forge": {
        "fs": ModePolicy(
            SubstrateClass.INSPECT,
            RiskTier.MEDIUM,
            "M-3_EXEC",
            ["L11", "L12"],
            "Filesystem inspection",
        ),
        "process": ModePolicy(
            SubstrateClass.INSPECT,
            RiskTier.MEDIUM,
            "M-3_EXEC",
            ["L11", "L12"],
            "Process monitoring",
        ),
        "run": ModePolicy(
            SubstrateClass.EXECUTE,
            RiskTier.HIGH,
            "M-3_EXEC",
            ["L11", "L12", "L13"],
            "Sandboxed script execution",
        ),
    },
    "arifos.kernel": {
        "list": ModePolicy(
            SubstrateClass.INSPECT,
            RiskTier.LOW,
            "M-4_ARCH",
            ["L11"],
            "Resource discovery",
        ),
        "read": ModePolicy(
            SubstrateClass.READ,
            RiskTier.LOW,
            "M-4_ARCH",
            ["L11"],
            "Resource inspection",
        ),
        "register": ModePolicy(
            SubstrateClass.WRITE,
            RiskTier.HIGH,
            "M-4_ARCH",
            ["F1", "L11", "L13"],
            "Component registration",
        ),
    },
    "arifos.judge": {
        "judge": ModePolicy(
            SubstrateClass.INSPECT,
            RiskTier.MEDIUM,
            "888_JUDGE",
            ["L13"],
            "Final verdict",
        ),
        "rules": ModePolicy(
            SubstrateClass.READ, RiskTier.LOW, "888_JUDGE", ["L13"], "Floor inspection"
        ),
        "validate": ModePolicy(
            SubstrateClass.READ,
            RiskTier.MEDIUM,
            "888_JUDGE",
            ["L13"],
            "Action validation",
        ),
        "armor": ModePolicy(
            SubstrateClass.INSPECT, RiskTier.MEDIUM, "888_JUDGE", ["L12"], "Shield scan"
        ),
    },
    "arifos.vault": {
        "seal": ModePolicy(
            SubstrateClass.COMMIT,
            RiskTier.HIGH,
            "999_SEAL",
            ["F1", "F3", "L13"],
            "Immutable audit seal",
        ),
        "verify": ModePolicy(
            SubstrateClass.READ, RiskTier.MEDIUM, "999_SEAL", ["F3"], "Integrity check"
        ),
    },
    "arifos.ops": {
        "estimate": ModePolicy(
            SubstrateClass.READ,
            RiskTier.LOW,
            "M-2_OPS",
            ["F8"],
            "Operational feasibility",
        )
    },
}


def get_policy(tool: str, mode: str) -> ModePolicy | None:
    return AAA_SUBSTRATE_POLICY.get(tool, {}).get(mode)
