"""
core/state/agent_registry.py — Agent Metadata, Lifecycle & Capability Tracker

Tracks active agent 'processes' within the arifOS kernel.
Provides the registry for the scheduler and recovery systems.
Supports capability discovery and inter-agent delegation.

Authority: A-ARCHITECT | Status: PROVISIONAL
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class AgentStatus(Enum):
    READY = "ready"
    RUNNING = "running"
    SUSPENDED = "suspended"
    QUARANTINED = "quarantined"
    TERMINATED = "terminated"


class AgentCapability(Enum):
    """Standard capability taxonomy for arifOS agents."""
    DESIGN = "design"                          # A-ARCHITECT
    CODE_IMPLEMENTATION = "code_implementation"  # A-ENGINEER
    CODE_REVIEW = "code_review"                # A-AUDITOR
    SECURITY_AUDIT = "security_audit"         # A-AUDITOR
    CONSTITUTIONAL_CHECK = "constitutional_check"  # A-AUDITOR
    SEAL_APPROVAL = "seal_approval"            # A-VALIDATOR
    AUDIT_TRAIL = "audit_trail"                # A-VALIDATOR
    ORCHESTRATION = "orchestration"            # A-ORCHESTRATOR
    REASONING = "reasoning"                    # AGI organs
    MEMORY = "memory"                          # engineering_memory
    EXECUTION = "execution"                    # code_engine
    REALITY_GROUNDING = "reality_grounding"    # physics_reality


@dataclass
class AgentCapability_:
    """Describes what an agent can do and what it costs."""
    name: str
    description: str
    floors_required: list[str]  # F-codes this capability needs
    priority: int = 5  # 1=highest, 5=lowest
    metadata: dict = field(default_factory=dict)


@dataclass
class AgentProcess:
    """A descriptor for an active intelligence unit."""

    pid: str
    owner_session: str
    role: str
    status: AgentStatus = AgentStatus.READY
    priority: int = 5
    created_at: datetime = field(default_factory=datetime.now)
    violation_count: int = 0
    capabilities: list[AgentCapability_] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def has_capability(self, cap: str) -> bool:
        """Check if agent has a specific capability."""
        return any(c.name == cap for c in self.capabilities)

    def supports_floor(self, floor: str) -> bool:
        """Check if agent can handle a specific constitutional floor."""
        return any(floor in c.floors_required for c in self.capabilities)


class AgentRegistry:
    """
    The 'Process Table' of the arifOS kernel.
    Enables cross-agent observability, capability discovery, and delegation.
    """

    def __init__(self):
        self._agents: dict[str, AgentProcess] = {}
        self._capability_index: dict[str, list[str]] = {}  # cap_name → [pid, ...]
        self._session_index: dict[str, list[str]] = {}    # session_id → [pid, ...]

    def register(
        self,
        pid: str,
        session_id: str,
        role: str,
        priority: int = 5,
        capabilities: list[AgentCapability_] | None = None,
    ) -> AgentProcess:
        """
        Register a new agent in the kernel table.
        
        Also indexes agent by capabilities for fast discovery.
        """
        agent = AgentProcess(
            pid=pid,
            owner_session=session_id,
            role=role,
            priority=priority,
            capabilities=capabilities or [],
        )
        self._agents[pid] = agent
        
        # Index by capability
        for cap in (capabilities or []):
            if cap.name not in self._capability_index:
                self._capability_index[cap.name] = []
            self._capability_index[cap.name].append(pid)
        
        # Index by session
        if session_id not in self._session_index:
            self._session_index[session_id] = []
        self._session_index[session_id].append(pid)
        
        return agent

    def update_status(self, pid: str, status: AgentStatus):
        """Update agent status (READY, RUNNING, SUSPENDED, QUARANTINED, TERMINATED)."""
        if pid in self._agents:
            self._agents[pid].status = status

    def get_agent(self, pid: str) -> AgentProcess | None:
        """Get agent by PID."""
        return self._agents.get(pid)

    def list_by_session(self, session_id: str) -> list[AgentProcess]:
        """List all agents in a session."""
        pids = self._session_index.get(session_id, [])
        return [self._agents[p] for p in pids if p in self._agents]

    def record_violation(self, pid: str):
        """
        P0: Increment violation count for threshold-based quarantine.
        If violation_count > 3, auto-quarantine the agent.
        """
        if pid in self._agents:
            self._agents[pid].violation_count += 1
            if self._agents[pid].violation_count > 3:
                self._agents[pid].status = AgentStatus.QUARANTINED

    def discover(
        self,
        capability: str | AgentCapability,
        floor_filter: str | None = None,
    ) -> list[AgentProcess]:
        """
        Find agents with the required capability.
        
        Args:
            capability: Name of capability needed (e.g., "code_implementation")
            floor_filter: Optional floor code (e.g., "F9") — filters to agents
                          that can handle this floor.
        
        Returns:
            List of matching agents sorted by priority (highest first).
        """
        cap_name = capability.value if isinstance(capability, AgentCapability) else capability
        pids = self._capability_index.get(cap_name, [])
        
        agents = []
        for pid in pids:
            agent = self._agents.get(pid)
            if agent and agent.status in (AgentStatus.READY, AgentStatus.RUNNING):
                if floor_filter and not agent.supports_floor(floor_filter):
                    continue
                agents.append(agent)
        
        return sorted(agents, key=lambda a: a.priority)

    def delegate(self, capability: str, payload: dict, floor_filter: str | None = None) -> dict | None:
        """
        Find best agent for a capability and delegate a task.
        
        Returns:
            Result dict from delegation, or None if no agent found.
        
        NOTE: This is a placeholder. Real delegation requires the message bus.
        """
        agents = self.discover(capability, floor_filter)
        if not agents:
            return {"error": f"No agent found with capability: {capability}"}
        
        best = agents[0]
        return {
            "delegated_to": best.pid,
            "role": best.role,
            "payload": payload,
            "status": "delegated",
        }

    def get_capabilities(self, pid: str) -> list[AgentCapability_]:
        """Get all capabilities of an agent."""
        agent = self._agents.get(pid)
        return agent.capabilities if agent else []

    def list_all_agents(self) -> list[AgentProcess]:
        """List all registered agents."""
        return list(self._agents.values())

    def get_system_status(self) -> dict:
        """Get overall system agent status for observability."""
        total = len(self._agents)
        by_status = {}
        for agent in self._agents.values():
            status = agent.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            "total_agents": total,
            "by_status": by_status,
            "capabilities_registered": len(self._capability_index),
            "active_sessions": len(self._session_index),
        }


# ─────────────────────────────────────────────────────────────
# Standard Capability Definitions (A-ARCHITECT defined)
# ─────────────────────────────────────────────────────────────

STANDARD_CAPABILITIES: dict[str, AgentCapability_] = {
    "A-ARCHITECT": AgentCapability_(
        name="design",
        description="System design, API contracts, architecture",
        floors_required=["F1", "F2", "F4", "F7", "F9", "F13"],
        priority=1,
    ),
    "A-ENGINEER": AgentCapability_(
        name="code_implementation",
        description="Code writing, testing, implementation",
        floors_required=["F1", "F2", "F5", "F9"],
        priority=1,
    ),
    "A-AUDITOR": AgentCapability_(
        name="code_review",
        description="Security audit, constitutional compliance review",
        floors_required=["F2", "F4", "F7", "F8", "F9", "F10"],
        priority=1,
    ),
    "A-VALIDATOR": AgentCapability_(
        name="seal_approval",
        description="Final approval, vault sealing, immutable records",
        floors_required=["F1", "F3", "F11", "F12", "F13"],
        priority=1,
    ),
    "A-ORCHESTRATOR": AgentCapability_(
        name="orchestration",
        description="Task routing, workflow coordination",
        floors_required=["F1", "F4", "F7"],
        priority=1,
    ),
}


# ─────────────────────────────────────────────────────────────
# Global singleton
# ─────────────────────────────────────────────────────────────

agent_registry = AgentRegistry()

# Pre-register standard agents
for agent_role, cap in STANDARD_CAPABILITIES.items():
    agent_registry.register(
        pid=agent_role,
        session_id="system",
        role=agent_role,
        priority=cap.priority,
        capabilities=[cap],
    )
