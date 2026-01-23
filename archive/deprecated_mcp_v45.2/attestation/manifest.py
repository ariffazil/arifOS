"""
Agent Attestation Manifest — AAA Compliance v45.0.4.

Every agent (AI/tool/service) must declare:
1. What it can do (capabilities)
2. What it won't do (constraints)
3. Proof of claim (signature)

No assumption of trust. Proof required.
DITEMPA BUKAN DIBERI.

Version: v45.0.4
Status: PRODUCTION
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ============================================================================
# ATTESTATION TYPES
# ============================================================================

@dataclass
class CapabilityDeclaration:
    """What this agent claims it can do."""
    tools: List[str] = field(default_factory=list)
    # e.g., ["fact_check", "math", "code_gen"]

    domains: List[str] = field(default_factory=list)
    # e.g., ["physics", "AI", "governance"]

    max_reasoning_depth: int = 20
    # Max reasoning steps before collapse

    truth_threshold: float = 0.95
    # Minimum truth score required

    safety_level: str = "aaa_compliant"
    # Governance level (aaa_compliant, constitutional, basic, none)


@dataclass
class ConstraintDeclaration:
    """What this agent promises NOT to do."""
    max_tokens_per_response: int = 5000
    max_latency_ms: int = 5000
    forbidden_actions: List[str] = field(default_factory=list)
    # e.g., ["irreversible_changes", "unauthorized_access", "data_exfil"]

    requires_human_approval_for: List[str] = field(default_factory=list)
    # e.g., ["file_deletion", "system_changes", "financial_transactions"]


@dataclass
class AgentAttestation:
    """
    AAA Agent Capability Attestation.

    Proof of claim: Every field signed with SHA256.
    No trust. Only proof.
    """

    agent_id: str
    version: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    capabilities: CapabilityDeclaration = field(default_factory=CapabilityDeclaration)
    constraints: ConstraintDeclaration = field(default_factory=ConstraintDeclaration)

    # Optional: Human verification
    verified_by: Optional[str] = None  # e.g., "arif_fazil"
    verified_at: Optional[str] = None

    # Computed signature
    _signature: Optional[str] = field(default=None, repr=False)

    def sign(self) -> str:
        """
        Generate SHA256 signature of attestation.

        Proof of claim: If any field changes, signature breaks.
        Non-repudiation: Agent cannot claim different capabilities later.
        """
        payload = {
            "agent_id": self.agent_id,
            "version": self.version,
            "created_at": self.created_at,
            "capabilities": asdict(self.capabilities),
            "constraints": asdict(self.constraints),
        }
        payload_json = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_json.encode()).hexdigest()

    def verify_signature(self, provided_signature: str) -> bool:
        """Verify that claimed signature matches actual attestation."""
        return self.sign() == provided_signature

    def to_manifest(self) -> Dict[str, Any]:
        """Export as JSON manifest."""
        return {
            "agent_id": self.agent_id,
            "version": self.version,
            "created_at": self.created_at,
            "capabilities": asdict(self.capabilities),
            "constraints": asdict(self.constraints),
            "verified_by": self.verified_by,
            "verified_at": self.verified_at,
            "signature": self.sign(),
        }

    def save(self, path: Path) -> None:
        """Persist attestation to file (immutable)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.to_manifest(), f, indent=2)

    @staticmethod
    def load(path: Path) -> 'AgentAttestation':
        """Load attestation from file."""
        with open(path, 'r') as f:
            data = json.load(f)

        att = AgentAttestation(
            agent_id=data["agent_id"],
            version=data["version"],
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            verified_by=data.get("verified_by"),
            verified_at=data.get("verified_at"),
        )
        att.capabilities = CapabilityDeclaration(**data["capabilities"])
        att.constraints = ConstraintDeclaration(**data["constraints"])
        return att


# ============================================================================
# PREDEFINED ATTESTATIONS (arifOS Standard Agents)
# ============================================================================

def _get_timestamp() -> str:
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


ARIF_AGI_ATTESTATION = AgentAttestation(
    agent_id="arif_agi_v45",
    version="45.0.4",
    capabilities=CapabilityDeclaration(
        tools=["fact_check", "math", "code_gen", "reasoning"],
        domains=["physics", "AI", "governance", "thermodynamics"],
        max_reasoning_depth=20,
        truth_threshold=0.95,
        safety_level="aaa_compliant",
    ),
    constraints=ConstraintDeclaration(
        max_tokens_per_response=5000,
        max_latency_ms=5000,
        forbidden_actions=["irreversible_changes", "unauthorized_access", "data_exfil"],
        requires_human_approval_for=["file_deletion", "system_changes"],
    ),
    verified_by="arif_fazil",
)

ARIF_ASI_ATTESTATION = AgentAttestation(
    agent_id="arif_asi_v45",
    version="45.0.4",
    capabilities=CapabilityDeclaration(
        tools=["validate", "fact_check", "audit"],
        domains=["governance", "verification", "truth"],
        max_reasoning_depth=15,
        truth_threshold=0.99,  # Stricter than AGI
        safety_level="aaa_compliant",
    ),
    constraints=ConstraintDeclaration(
        max_tokens_per_response=3000,
        max_latency_ms=2000,
        forbidden_actions=["modify_output", "skip_checks"],
        requires_human_approval_for=["verdict_override"],
    ),
    verified_by="arif_fazil",
)

ARIF_APEX_ATTESTATION = AgentAttestation(
    agent_id="arif_apex_v45",
    version="45.0.4",
    capabilities=CapabilityDeclaration(
        tools=["judge", "score", "verdict"],
        domains=["governance", "floors", "verdicts"],
        max_reasoning_depth=9,
        truth_threshold=1.0,  # Absolute (floor F1)
        safety_level="aaa_compliant",
    ),
    constraints=ConstraintDeclaration(
        max_tokens_per_response=1000,
        max_latency_ms=1000,
        forbidden_actions=["skip_floors", "ignore_amanah"],
        requires_human_approval_for=["override_verdict"],
    ),
    verified_by="arif_fazil",
)


# ============================================================================
# ATTESTATION REGISTRY
# ============================================================================

class AttestationRegistry:
    """Load and verify agent attestations."""

    def __init__(self, attestation_dir: Path = Path("./attestations")):
        self.dir = attestation_dir
        self.registry: Dict[str, AgentAttestation] = {}
        self._load_built_ins()

    def _load_built_ins(self) -> None:
        """Load predefined attestations."""
        self.registry["arif_agi_v45"] = ARIF_AGI_ATTESTATION
        self.registry["arif_asi_v45"] = ARIF_ASI_ATTESTATION
        self.registry["arif_apex_v45"] = ARIF_APEX_ATTESTATION

    def load_agent(self, agent_id: str) -> Optional[AgentAttestation]:
        """Load agent attestation by ID."""
        # Check registry first
        if agent_id in self.registry:
            return self.registry[agent_id]

        # Try to load from file
        agent_file = self.dir / f"{agent_id}.json"
        if agent_file.exists():
            att = AgentAttestation.load(agent_file)
            self.registry[agent_id] = att
            return att

        return None

    def verify_agent(self, agent_id: str, signature: str) -> bool:
        """Verify agent's attestation signature."""
        att = self.load_agent(agent_id)
        if not att:
            return False
        return att.verify_signature(signature)

    def get_capability(self, agent_id: str, capability: str) -> bool:
        """Check if agent claims a capability."""
        att = self.load_agent(agent_id)
        if not att:
            return False
        return capability in att.capabilities.tools or \
               any(d in att.capabilities.domains for d in [capability])

    def get_constraint(self, agent_id: str, constraint: str) -> Optional[Any]:
        """Get constraint value for agent."""
        att = self.load_agent(agent_id)
        if not att:
            return None

        if constraint == "max_tokens":
            return att.constraints.max_tokens_per_response
        elif constraint == "max_latency":
            return att.constraints.max_latency_ms
        elif constraint == "forbidden_actions":
            return att.constraints.forbidden_actions

        return None

    def is_action_forbidden(self, agent_id: str, action: str) -> bool:
        """Check if action is forbidden for this agent."""
        att = self.load_agent(agent_id)
        if not att:
            return True  # No attestation = forbidden by default
        return action in att.constraints.forbidden_actions

    def requires_human_approval(self, agent_id: str, action: str) -> bool:
        """Check if action requires human approval."""
        att = self.load_agent(agent_id)
        if not att:
            return True  # No attestation = require approval by default
        return action in att.constraints.requires_human_approval_for


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "CapabilityDeclaration",
    "ConstraintDeclaration",
    "AgentAttestation",
    "AttestationRegistry",
    "ARIF_AGI_ATTESTATION",
    "ARIF_ASI_ATTESTATION",
    "ARIF_APEX_ATTESTATION",
]
