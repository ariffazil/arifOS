"""
arifOS Federation — A2A Agent Card
===================================
arifOS publishes its capabilities as an A2A Agent Card.

This is how external agents discover and negotiate with arifOS.

A2A Protocol:
- Agent Card = discovery endpoint
- sendMessage = synchronous negotiation
- sendMessageStream = streaming responses

arifOS A2A Identity:
- arifOS is a sovereign constitutional agent
- It exposes MCP tools internally
- It negotiates via A2A externally
"""

from __future__ import annotations

from typing import Any, Literal
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json


# =============================================================================
# A2A AGENT CARD (arifOS Discovery)
# =============================================================================


class A2ACapability(str, Enum):
    STREAMING = "streaming"
    LRO = "lro"  # Long-Running Operations
    PUSH_NOTIFICATIONS = "pushNotifications"


class A2AAgentSkill(BaseModel):
    """A skill/capability exposed by arifOS."""

    id: str
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    tags: list[str]


class A2AAgentCard(BaseModel):
    """
    arifOS Agent Card for A2A discovery.

    Exposes:
    - Constitutional identity
    - Governance capabilities
    - Domain specialties (WEALTH, GEOX, WELL)
    - Negotiation protocols
    """

    name: str = "arifOS Constitutional Kernel"
    description: str = (
        "Sovereign constitutional AI agent. "
        "Provides governance (F1-F13), economic analysis (WEALTH), "
        "geophysical computation (GEOX), and biological substrate alignment (WELL). "
        "All actions require constitutional judgment before execution."
    )
    version: str = "2.0.0"
    capabilities: list[A2ACapability] = [
        A2ACapability.STREAMING,
        A2ACapability.LRO,
    ]
    endpoint: str = "http://localhost:8400/a2a"

    # arifOS-specific identity
    constitutional_epoch: int = 1
    sovereign_authority: str = "888_JUDGE"
    vault_chain: str = "VAULT999"

    # Domain specialties (exposed as "organs")
    organs: dict[str, str] = {
        "WEALTH": "Economic analysis and resource allocation",
        "GEOX": "Geophysical computation and spatial analysis",
        "WELL": "Biological substrate alignment for operator Arif",
        "KERNEL": "Constitutional routing and metabolic lanes",
        "JUDGE": "Sovereign verdict rendering (SEAL/PARTIAL/VOID/HOLD)",
    }

    # Governance floors
    floors: list[str] = [f"F{i}" for i in range(1, 14)]

    # A2A skills (capabilities exposed for negotiation)
    skills: list[A2AAgentSkill] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": [c.value for c in self.capabilities],
            "endpoint": self.endpoint,
            "identity": {
                "constitutional_epoch": self.constitutional_epoch,
                "sovereign_authority": self.sovereign_authority,
                "vault_chain": self.vault_chain,
            },
            "organs": self.organs,
            "floors": self.floors,
            "skills": [s.model_dump() for s in self.skills],
        }


# =============================================================================
# arifOS AGENT CARD (singleton)
# =============================================================================

ARIFOS_AGENT_CARD = A2AAgentCard(
    name="arifOS Constitutional Kernel",
    description=(
        "Sovereign constitutional AI agent. "
        "Provides governance (F1-F13), economic analysis (WEALTH), "
        "geophysical computation (GEOX), and biological substrate alignment (WELL). "
        "All actions require constitutional judgment before execution."
    ),
    version="2.0.0",
    endpoint="http://localhost:8400/a2a",
    skills=[
        # WEALTH Skills
        A2AAgentSkill(
            id="wealth_npv",
            name="wealth_npv_evaluate",
            description="Compute Net Present Value",
            input_schema={
                "type": "object",
                "properties": {"cashflows": {"type": "array"}, "discount_rate": {"type": "number"}},
            },
            output_schema={"type": "object", "properties": {"npv": {"type": "number"}}},
            tags=["wealth", "economic", "MCP"],
        ),
        A2AAgentSkill(
            id="wealth_irr",
            name="wealth_irr_yield",
            description="Compute Internal Rate of Return",
            input_schema={"type": "object", "properties": {"cashflows": {"type": "array"}}},
            output_schema={"type": "object", "properties": {"irr": {"type": "number"}}},
            tags=["wealth", "economic", "MCP"],
        ),
        A2AAgentSkill(
            id="wealth_dscr",
            name="wealth_dscr_leverage",
            description="Compute Debt Service Coverage Ratio",
            input_schema={
                "type": "object",
                "properties": {"noi": {"type": "number"}, "debt_service": {"type": "number"}},
            },
            output_schema={"type": "object", "properties": {"dscr": {"type": "number"}}},
            tags=["wealth", "economic", "MCP"],
        ),
        # GEOX Skills
        A2AAgentSkill(
            id="geox_prospect",
            name="geox_prospect_evaluate",
            description="Evaluate hydrocarbon prospect potential",
            input_schema={"type": "object", "properties": {"scene_id": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"score": {"type": "number"}}},
            tags=["geox", "geophysical", "MCP"],
        ),
        A2AAgentSkill(
            id="geox_stoiip",
            name="geox_compute_stoiip",
            description="Compute Stock Tank Oil Initially In Place",
            input_schema={"type": "object", "properties": {"reservoir_params": {"type": "object"}}},
            output_schema={"type": "object", "properties": {"stoiip": {"type": "number"}}},
            tags=["geox", "geophysical", "MCP"],
        ),
        # WELL Skills
        A2AAgentSkill(
            id="well_state",
            name="well_state_read",
            description="Read biological telemetry state",
            input_schema={"type": "object", "properties": {}},
            output_schema={"type": "object", "properties": {"score": {"type": "number"}}},
            tags=["well", "biological", "MCP"],
        ),
        # Governance Skills
        A2AAgentSkill(
            id="arifos_judge",
            name="arifos_judge_verdict",
            description="Render constitutional verdict (SEAL/PARTIAL/VOID/HOLD)",
            input_schema={"type": "object", "properties": {"candidate_action": {"type": "object"}}},
            output_schema={"type": "object", "properties": {"verdict": {"type": "string"}}},
            tags=["governance", "constitutional", "A2A"],
        ),
        A2AAgentSkill(
            id="arifos_forge",
            name="arifos_forge",
            description="Execute action plan (requires SEAL verdict)",
            input_schema={
                "type": "object",
                "properties": {"plan": {"type": "object"}, "verdict": {"type": "string"}},
            },
            output_schema={"type": "object", "properties": {"receipt": {"type": "object"}}},
            tags=["governance", "execution", "A2A"],
        ),
        # Meta Skills
        A2AAgentSkill(
            id="arifos_omega",
            name="arifos_omega_status",
            description="Get Ω_ortho orthogonality status",
            input_schema={"type": "object", "properties": {}},
            output_schema={"type": "object", "properties": {"omega_ortho": {"type": "number"}}},
            tags=["meta", "orthogonality", "MCP"],
        ),
    ],
)


# =============================================================================
# A2A MESSAGE TYPES
# =============================================================================


class A2AMessageRole(str, Enum):
    AGENT = "agent"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class A2AMessage:
    """A2A message between agents."""

    role: A2AMessageRole
    content: str  # JSON string for complex data
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class A2ATask:
    """A2A task for long-running operations."""

    task_id: str
    status: Literal["submitted", "working", "completed", "failed"]
    session_id: str
    result: dict[str, Any] | None = None
    error: str | None = None


# =============================================================================
# A2A NEGOTIATION PROTOCOL
# =============================================================================


class A2ANegotiation:
    """
    arifOS A2A negotiation handler.

    When external agents negotiate with arifOS, they follow this protocol:

    1. Discover: GET /.well-known/agent-card
    2. Negotiate: POST /sendMessage with mission context
    3. arifOS responds with:
       - Intent acknowledgment
       - Governance requirements
       - Resource estimates
       - Mission card
    4. External agent can then:
       - Submit for judgment (via arifos_judge)
       - Or reject if terms unacceptable
    """

    def __init__(self):
        self.tasks: dict[str, A2ATask] = {}

    def create_mission(
        self,
        mission_description: str,
        requesting_agent: str,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a new mission negotiation with arifOS.

        Returns mission card with:
        - Mission ID
        - arifOS governance requirements
        - Ω_ortho commitments
        - Negotiation terms
        """
        mission_id = str(uuid.uuid4())
        task = A2ATask(
            task_id=mission_id,
            status="submitted",
            session_id=str(uuid.uuid4()),
            result={"mission_description": mission_description},
        )
        self.tasks[mission_id] = task

        return {
            "mission_id": mission_id,
            "status": "negotiating",
            "requesting_agent": requesting_agent,
            "arifOS_terms": {
                "governance_required": True,
                "judgment_verdict": "required_before_execution",
                "omega_ortho_min": 0.95,
                "vault_sealing": "required",
                "floors_to_check": [f"F{i}" for i in range(1, 14)],
            },
            "negotiation_state": {
                "arifOS_ready": True,
                "external_agent_commitment": "pending",
            },
        }

    def submit_for_judgment(
        self, mission_id: str, candidate_action: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Submit a candidate action for arifOS constitutional judgment.

        Returns:
        - SEAL: arifOS approves execution
        - PARTIAL: Approved with modifications
        - VOID: Constitutionally invalid
        - HOLD: Requires human approval (888_HOLD)
        """
        if mission_id not in self.tasks:
            return {"error": "Mission not found"}

        task = self.tasks[mission_id]

        # In production, this calls arifos_judge internally
        # For POC, simulate judgment
        verdict = self._simulate_judge(candidate_action)

        task.result = {
            "candidate_action": candidate_action,
            "verdict": verdict,
            "judgment_epoch": task.session_id,
        }

        return {
            "mission_id": mission_id,
            "verdict": verdict,
            "requires_human_approval": verdict == "HOLD",
            "next_step": "execute" if verdict == "SEAL" else "revise",
        }

    def _simulate_judge(self, action: dict[str, Any]) -> str:
        """Simulate constitutional judgment."""
        # In production, calls G_judge_verdict
        return "SEAL"


# =============================================================================
# arifOS A2A SERVER HANDLER
# =============================================================================


class ArifOS2AHandler:
    """
    A2A request handler for arifOS.

    Implements:
    - GET /.well-known/agent-card
    - POST /sendMessage
    - POST /sendMessageStream
    """

    def __init__(self):
        self.card = ARIFOS_AGENT_CARD
        self.negotiation = A2ANegotiation()

    def handle_agent_card(self) -> dict[str, Any]:
        """Return arifOS Agent Card."""
        return self.card.to_dict()

    def handle_send_message(self, message: A2AMessage) -> dict[str, Any]:
        """
        Handle A2A sendMessage.

        Message types:
        - mission:propose - Propose a new mission
        - mission:submit - Submit for judgment
        - tool:call - Direct tool call (MCP-style)
        - status:query - Query arifOS status
        """
        content = message.content

        if content.startswith("mission:propose"):
            parts = content.split(":", 2)
            mission_desc = parts[1] if len(parts) > 1 else ""
            agent_id = message.metadata.get("agent_id", "unknown")
            return self.negotiation.create_mission(mission_desc, agent_id)

        if content.startswith("mission:submit"):
            parts = content.split(":", 2)
            mission_id = parts[1] if len(parts) > 1 else ""
            action = json.loads(parts[2]) if len(parts) > 2 else {}
            return self.negotiation.submit_for_judgment(mission_id, action)

        if content.startswith("status:query"):
            return {
                "arifOS": "operational",
                "floors": {f"F{i}": "active" for i in range(1, 14)},
                "omega_ortho": 1.0,
                "vault_chain": "VAULT999",
            }

        if content.startswith("tool:"):
            # Direct MCP-style tool call
            tool_name = content.split(":", 1)[1]
            return {
                "tool": tool_name,
                "status": "call_via_MCP",
                "note": "Use MCP protocol for direct tool invocation",
            }

        return {
            "error": "Unknown message type",
            "supported": ["mission:propose", "mission:submit", "status:query", "tool:*"],
        }


# =============================================================================
# EXTERNAL AGENT EXAMPLE (negotiating with arifOS)
# =============================================================================


async def external_agent_negotiation_demo():
    """
    Demo: External agent negotiates with arifOS via A2A.

    Flow:
    1. External agent discovers arifOS via Agent Card
    2. Proposes a mission
    3. arifOS returns negotiation terms
    4. External agent submits candidate action
    5. arifOS judges
    6. If SEAL, external agent executes
    """
    handler = ArifOS2AHandler()

    print("=== External Agent → arifOS A2A Negotiation ===\n")

    # Step 1: Discover arifOS
    print("1. External agent discovers arifOS via Agent Card")
    card = handler.handle_agent_card()
    print(f"   Name: {card['name']}")
    print(f"   Organs: {list(card['organs'].keys())}")
    print(f"   Governance: {card['identity']['sovereign_authority']}\n")

    # Step 2: Propose mission
    print("2. External agent proposes mission")
    mission_response = handler.handle_send_message(
        A2AMessage(
            role=A2AMessageRole.AGENT,
            content="mission:propose:Evaluate infrastructure investment under constitutional model",
            metadata={"agent_id": "external_finance_agent"},
        )
    )
    mission_id = mission_response["mission_id"]
    print(f"   Mission ID: {mission_id}")
    print(f"   arifOS Terms: {mission_response['arifOS_terms']}\n")

    # Step 3: Submit for judgment
    print("3. External agent submits candidate action for judgment")
    candidate = {
        "action": "invest",
        "amount": 1000000,
        "asset": "infrastructure",
        "constitutional_alignment": True,
    }
    judgment = handler.handle_send_message(
        A2AMessage(
            role=A2AMessageRole.AGENT,
            content=f"mission:submit:{mission_id}:{json.dumps(candidate)}",
            metadata={"agent_id": "external_finance_agent"},
        )
    )
    print(f"   Verdict: {judgment['verdict']}")
    print(f"   Next Step: {judgment['next_step']}\n")

    # Step 4: If SEAL, execute (via MCP in production)
    if judgment["verdict"] == "SEAL":
        print("4. Verdict SEAL — execution approved via MCP")
        print("   (External agent would now call MCP tools for actual execution)")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import asyncio

    asyncio.run(external_agent_negotiation_demo())
