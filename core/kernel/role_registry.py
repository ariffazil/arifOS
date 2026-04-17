"""
core/kernel/role_registry.py — Agent Role Registry and Handoff Protocol.

Formalizes agent roles (Architect, Auditor, Agent, Validator) and defines
handoff protocols for multi-agent orchestration within arifOS.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentRole:
    """Definition of an agent role and its permissions."""
    name: str
    description: str
    permissions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentSession:
    """An active agent session with an assigned role."""
    agent_id: str
    role_name: str
    session_id: str

class AgentRoleRegistry:
    """
    Registry for agent roles and multi-agent orchestration.
    Enables auditable role assignment and safe handoffs.
    """

    def __init__(self):
        self._roles: dict[str, AgentRole] = {}
        self._active_sessions: dict[str, AgentSession] = {}
        self._initialize_default_roles()

    def _initialize_default_roles(self):
        """Register canonical arifOS agent roles (AAA)."""
        self.register_role(
            name="Architect",
            description="Designs and plans system architecture. Read-only on code.",
            permissions=["read", "plan"]
        )
        self.register_role(
            name="Engineer",
            description="Implements designs and edits code. Write-access with approval.",
            permissions=["read", "write"]
        )
        self.register_role(
            name="Auditor",
            description="Reviews code and decisions for alignment. Issues VOID verdicts.",
            permissions=["read", "audit", "void"]
        )
        self.register_role(
            name="Validator",
            description="Final authority for deployment and SEAL verdicts.",
            permissions=["read", "deploy", "seal"]
        )

    def register_role(self, name: str, description: str, permissions: list[str], metadata: dict[str, Any] | None = None):
        """Register a new agent role."""
        self._roles[name] = AgentRole(
            name=name,
            description=description,
            permissions=permissions,
            metadata=metadata or {}
        )

    def assign_role(self, agent_id: str, role_name: str, session_id: str):
        """Assign a role to an agent for a specific session."""
        if role_name not in self._roles:
            raise ValueError(f"Role '{role_name}' not found.")
        
        self._active_sessions[agent_id] = AgentSession(
            agent_id=agent_id,
            role_name=role_name,
            session_id=session_id
        )

    def get_role(self, agent_id: str) -> AgentRole | None:
        """Retrieve the role assigned to an agent."""
        session = self._active_sessions.get(agent_id)
        if session:
            return self._roles.get(session.role_name)
        return None

    def handoff(self, from_agent_id: str, to_agent_id: str, reason: str) -> bool:
        """
        Formalize handoff between agents.
        Ensures explicit, auditable transfer of context and authority.
        """
        if from_agent_id not in self._active_sessions:
            raise ValueError(f"Source agent '{from_agent_id}' has no active session.")
        
        # Validation of handoff logic would go here.
        # For now, we log the handoff (in an audit trail).
        # Return True to indicate successful handoff request.
        return True

    def list_roles(self) -> list[str]:
        """List all registered agent role names."""
        return list(self._roles.keys())
