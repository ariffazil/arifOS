"""
arifOS Federation — A2A-Aligned Architecture
==========================================

A2A Protocol Alignment:
- Each agent (P, T, V, G, E, M) is an A2A SERVER
- Agents communicate via sendMessage/sendMessageStream
- MCP is used INTERNALLY for data access within each agent
- Agent Cards enable discovery

Stack:
  A2A (inter-agent communication)
    ↑
  MCP (data access per agent)
    ↑
  Agent (autonomous reasoning)
"""

from __future__ import annotations

from typing import Any, Literal, Optional
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field
import json


# =============================================================================
# A2A CORE TYPES (simplified implementation)
# =============================================================================


class MessageRole(str, Enum):
    AGENT = "agent"
    USER = "user"
    ASSISTANT = "assistant"


class AgentCapability(str, Enum):
    STREAMING = "streaming"
    LRO = "lro"  # Long-Running Operations
    PUSH_NOTIFICATIONS = "pushNotifications"


@dataclass
class AgentCard:
    """A2A Agent Card for discovery."""

    name: str
    description: str
    version: str
    capabilities: list[AgentCapability]
    endpoint: str  # URL of the A2A server

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": [c.value for c in self.capabilities],
            "endpoint": self.endpoint,
        }


@dataclass
class A2AMessage:
    """A2A message between agents."""

    role: MessageRole
    content: str
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """A2A Task for tracking long-running operations."""

    task_id: str
    status: Literal["submitted", "working", "completed", "failed"]
    result: dict[str, Any] | None = None


# =============================================================================
# arifOS Agent Card Registry
# =============================================================================

AGENT_CARDS: dict[str, AgentCard] = {
    "P": AgentCard(
        name="Perception Agent",
        description="Reads reality from WELL, GEOX, VAULT, WEALTH. Does not interpret.",
        version="1.0.0",
        capabilities=[AgentCapability.STREAMING],
        endpoint="http://localhost:8100/a2a",
    ),
    "T": AgentCard(
        name="Transformation Agent",
        description="Computes physics, math, monte_carlo, entropy. Transforms only.",
        version="1.0.0",
        capabilities=[AgentCapability.STREAMING],
        endpoint="http://localhost:8200/a2a",
    ),
    "V": AgentCard(
        name="Valuation Agent",
        description="Ranks by NPV, EMV, allocation. Cannot fetch or mutate.",
        version="1.0.0",
        capabilities=[AgentCapability.STREAMING],
        endpoint="http://localhost:8300/a2a",
    ),
    "G": AgentCard(
        name="Governance Agent",
        description="Routes, reasons, judges. Does not compute NPV.",
        version="1.0.0",
        capabilities=[AgentCapability.STREAMING, AgentCapability.LRO],
        endpoint="http://localhost:8400/a2a",
    ),
    "E": AgentCard(
        name="Execution Agent",
        description="Mutates state via forge, vault, memory. Requires governance approval.",
        version="1.0.0",
        capabilities=[AgentCapability.STREAMING, AgentCapability.LRO],
        endpoint="http://localhost:8500/a2a",
    ),
    "M": AgentCard(
        name="Meta Agent",
        description="Audits omega_ortho, discovers skills, monitors. Never executes.",
        version="1.0.0",
        capabilities=[AgentCapability.STREAMING],
        endpoint="http://localhost:8600/a2a",
    ),
}


# =============================================================================
# A2A CLIENT (for agents to call other agents)
# =============================================================================


class A2AClient:
    """A2A client for inter-agent communication."""

    def __init__(self, agent_cards: dict[str, AgentCard] | None = None):
        self.agent_cards = agent_cards or AGENT_CARDS

    async def send_message(
        self, target_agent: str, message: A2AMessage, session_id: str | None = None
    ) -> dict[str, Any]:
        """
        Send a message to another agent via A2A.
        Returns the agent's response.
        """
        if target_agent not in self.agent_cards:
            return {"error": f"Unknown agent: {target_agent}"}

        card = self.agent_cards[target_agent]

        # In production, this would be an HTTP POST to the agent's endpoint
        # For POC, we simulate the response
        return await self._simulate_response(target_agent, message)

    async def send_message_stream(self, target_agent: str, message: A2AMessage):
        """
        Stream a message to another agent.
        Yields response chunks.
        """
        if target_agent not in self.agent_cards:
            yield {"error": f"Unknown agent: {target_agent}"}
            return

        # Simulate streaming response
        response = await self._simulate_response(target_agent, message)
        for chunk in self._chunk_response(response):
            yield chunk

    async def _simulate_response(self, agent: str, message: A2AMessage) -> dict[str, Any]:
        """Simulate agent response for POC."""
        return {
            "agent": agent,
            "received": message.content,
            "status": "processed",
            "session_id": message.session_id,
        }

    def _chunk_response(self, response: dict[str, Any]):
        """Split response into chunks for streaming."""
        content = json.dumps(response)
        chunk_size = 50
        for i in range(0, len(content), chunk_size):
            yield content[i : i + chunk_size]

    def discover_agents(self) -> dict[str, AgentCard]:
        """Return all available agent cards."""
        return self.agent_cards


# =============================================================================
# A2A SERVER BASE (for each agent to implement)
# =============================================================================


class A2AServer:
    """Base class for A2A agent servers."""

    def __init__(self, agent_id: str, card: AgentCard):
        self.agent_id = agent_id
        self.card = card
        self.client = A2AClient()

    async def handle_message(self, message: A2AMessage) -> dict[str, Any]:
        """Handle incoming A2A message."""
        raise NotImplementedError

    async def handle_message_stream(self, message: A2AMessage):
        """Handle streaming A2A message."""
        raise NotImplementedError

    def get_agent_card(self) -> AgentCard:
        """Return this agent's card for discovery."""
        return self.card


# =============================================================================
# ORTHOGONALITY MATRIX (A2A routing rules)
# =============================================================================

ORTHOGONALITY_ROUTING = {
    "P": ["T", "G"],  # Perception → Transformation, Governance
    "T": ["V", "M"],  # Transformation → Valuation, Meta
    "V": ["G"],  # Valuation → Governance
    "G": ["E", "M"],  # Governance → Execution, Meta
    "E": [],  # Execution → nowhere (mutations complete)
    "M": ["P", "G"],  # Meta → Perception, Governance
}


def can_route(caller: str, target: str) -> bool:
    """Check if caller can route to target based on orthogonality."""
    allowed = ORTHOGONALITY_ROUTING.get(caller, [])
    return target in allowed or target[0] == caller[0]


# =============================================================================
# EXAMPLE: PERCEPTION AGENT IMPLEMENTATION
# =============================================================================


class PerceptionAgent(A2AServer):
    """P Agent — Reads reality from WELL, GEOX, VAULT, WEALTH."""

    def __init__(self):
        super().__init__(agent_id="P", card=AGENT_CARDS["P"])
        # Internal MCP clients for data access
        self._mcp_clients = {
            "WELL": None,  # Would connect to WELL MCP
            "GEOX": None,  # Would connect to GEOX MCP
            "VAULT": None,  # Would connect to VAULT
            "WEALTH": None,  # Would connect to WEALTH
        }

    async def handle_message(self, message: A2AMessage) -> dict[str, Any]:
        """
        Handle perception request.

        A2A Message format:
        {
            "role": "agent",
            "content": "read:WELL:state or read:GEOX:scene",
            "session_id": "..."
        }
        """
        content = message.content

        if content.startswith("read:"):
            source_type, action = content.split(":", 2)[1:]
            return await self._read_source(source_type, action, message.session_id)

        if content == "discover":
            return {"sources": list(self._mcp_clients.keys())}

        return {"error": "Unknown perception command"}

    async def _read_source(
        self, source: str, action: str, session_id: str | None
    ) -> dict[str, Any]:
        """Read from internal MCP data source."""
        # In production, this calls the MCP tool
        # For POC, return stub
        return {
            "agent": "P",
            "source": source,
            "action": action,
            "data": {"status": "stub"},
            "session_id": session_id,
        }


# =============================================================================
# EXAMPLE: GOVERNANCE AGENT (with routing)
# =============================================================================


class GovernanceAgent(A2AServer):
    """G Agent — Routes, reasons, judges."""

    def __init__(self):
        super().__init__(agent_id="G", card=AGENT_CARDS["G"])

    async def handle_message(self, message: A2AMessage) -> dict[str, Any]:
        """
        Handle governance request.

        Routes to other agents via A2A.
        """
        content = message.content

        if content.startswith("route:"):
            target, payload = content.split(":", 2)[1:]
            return await self._route_to_agent(target, payload, message.session_id)

        if content.startswith("judge:"):
            action_data = content.split(":", 1)[1]
            return await self._judge(action_data, message.session_id)

        if content.startswith("init:"):
            return await self._init_session(content.split(":", 1)[1], message.session_id)

        return {"error": "Unknown governance command"}

    async def _route_to_agent(
        self, target: str, payload: str, session_id: str | None
    ) -> dict[str, Any]:
        """Route message to target agent via A2A."""
        if not can_route("G", target):
            return {"error": f"G cannot route to {target}"}

        # Send via A2A
        response = await self.client.send_message(
            target_agent=target,
            message=A2AMessage(
                role=MessageRole.AGENT,
                content=payload,
                session_id=session_id,
            ),
        )
        return response

    async def _judge(self, action_data: str, session_id: str | None) -> dict[str, Any]:
        """Judge a candidate action."""
        return {
            "agent": "G",
            "verdict": "STUB",
            "floor_results": {},
            "session_id": session_id,
        }

    async def _init_session(self, intent: str, session_id: str | None) -> dict[str, Any]:
        """Initialize a session."""
        return {
            "agent": "G",
            "session_id": session_id or "new",
            "intent": intent,
            "status": "initialized",
        }


# =============================================================================
# AGENT REGISTRY (for discovery)
# =============================================================================

AGENT_REGISTRY = {
    "P": PerceptionAgent(),
    "T": None,  # Placeholder
    "V": None,  # Placeholder
    "G": GovernanceAgent(),
    "E": None,  # Placeholder
    "M": None,  # Placeholder
}


def get_agent(agent_id: str) -> A2AServer | None:
    """Get agent instance by ID."""
    return AGENT_REGISTRY.get(agent_id)


def get_all_cards() -> dict[str, AgentCard]:
    """Get all agent cards for discovery."""
    return {k: v.get_agent_card() if v else AGENT_CARDS[k] for k, v in AGENT_REGISTRY.items()}


# =============================================================================
# A2A ROUTER (G02 equivalent)
# =============================================================================


class A2ARouter:
    """
    G02 equivalent for A2A.

    All inter-agent communication goes through this router.
    Enforces orthogonality routing rules.
    """

    def __init__(self):
        self.client = A2AClient()

    async def route(
        self, caller: str, target: str, payload: dict[str, Any], session_id: str | None = None
    ) -> dict[str, Any]:
        """
        Route a message from caller to target.
        Enforces orthogonality.
        """
        if not can_route(caller, target):
            return {
                "error": f"Orthogonality violation: {caller} cannot route to {target}",
                "allowed": ORTHOGONALITY_ROUTING.get(caller, []),
                "omega_ortho": 0.0,
            }

        message = A2AMessage(
            role=MessageRole.AGENT,
            content=json.dumps(payload),
            session_id=session_id,
        )

        response = await self.client.send_message(target, message)
        return {
            "approved": True,
            "caller": caller,
            "target": target,
            "response": response,
            "omega_ortho": 1.0,
        }

    async def route_stream(self, caller: str, target: str, payload: dict[str, Any]):
        """Stream route a message."""
        if not can_route(caller, target):
            yield {"error": f"Orthogonality violation: {caller} cannot route to {target}"}
            return

        message = A2AMessage(
            role=MessageRole.AGENT,
            content=json.dumps(payload),
        )

        async for chunk in self.client.send_message_stream(target, message):
            yield chunk


# =============================================================================
# DEMO SCENARIO
# =============================================================================


async def demo_scenario():
    """
    Demo: P reads WELL state, routes to T for computation,
    routes to V for valuation, routes to G for judgment.
    """
    router = A2ARouter()

    print("=== A2A Federation Demo ===\n")

    # Step 1: P reads WELL state
    print("1. P (Perception) reads WELL state")
    agent_p = get_agent("P")
    if agent_p:
        result = await agent_p.handle_message(
            A2AMessage(role=MessageRole.USER, content="read:WELL:state")
        )
        print(f"   Result: {result}\n")

    # Step 2: G routes P's result to T
    print("2. G (Governance) routes to T (Transformation)")
    result = await router.route("G", "T", {"data": "from_P", "computation": "physics"})
    print(f"   Result: {result}\n")

    # Step 3: T routes result to V
    print("3. T (Transformation) routes to V (Valuation)")
    result = await router.route("T", "V", {"data": "from_T", "ranking": "NPV"})
    print(f"   Result: {result}\n")

    # Step 4: V routes to G for judgment
    print("4. V (Valuation) routes to G (Governance) for judgment")
    result = await router.route("V", "G", {"data": "from_V", "action": "judge"})
    print(f"   Result: {result}\n")

    # Step 5: G routes to E for execution (after judgment)
    print("5. G (Governance) routes to E (Execution) after SEAL")
    result = await router.route("G", "E", {"data": "approved", "operation": "forge"})
    print(f"   Result: {result}\n")

    # Demonstrate blocked routing
    print("6. E tries to route to P (should fail - E cannot route)")
    result = await router.route("E", "P", {"data": "test"})
    print(f"   Result: {result}\n")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import asyncio

    print("arifOS Federation — A2A-Aligned Architecture")
    print("=" * 50)
    print("Agents: P (Perception), T (Transformation), V (Valuation)")
    print("        G (Governance), E (Execution), M (Meta)")
    print("Router: A2A Router (G02 equivalent)")
    print()

    asyncio.run(demo_scenario())
