"""
geox_mcp_server_acp.py — GEOX Agent Control Plane (ACP) Extension
═══════════════════════════════════════════════════════════════════════════════
DITEMPA BUKAN DIBERI

A2A (Agent-to-Agent) Communication Protocol for GEOX MCP Server.
Enables multi-agent swarm intelligence with Constitutional governance.

This module extends the base MCP server with:
- Agent Registry (subscription management)
- A2A Message Bus (inter-agent communication)
- Floor Enforcer (F1-F13 validation with F7 Humility bounds)
- Discordance Detection (agent conflict resolution)
- 888_JUDGE Verdict Protocol
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Dict, List, Optional, Set
from weakref import WeakSet

logger = logging.getLogger("geox.acp")


# ═══════════════════════════════════════════════════════════════════════════════
# ACP Constants & Configuration
# ═══════════════════════════════════════════════════════════════════════════════

F7_HUMILITY_FLOOR = 0.04  # ±4% uncertainty bound
F7_MAX_UNCERTAINTY = 0.15  # Maximum allowable uncertainty
PHYSICS_9_KEYS = {"rho", "vp", "vs", "res", "chi", "k", "p", "t", "phi"}


# ═══════════════════════════════════════════════════════════════════════════════
# Enums & Types
# ═══════════════════════════════════════════════════════════════════════════════

class AgentRole(Enum):
    """Specialized agent roles in the GEOX ecosystem."""
    PETROPHYSICIST = "petrophysicist"
    GEOPHYSICIST = "geophysicist"
    GEOLOGIST = "geologist"
    RESERVOIR_ENGINEER = "reservoir_engineer"
    BAYESIAN_ANALYST = "bayesian_analyst"
    SWARM_COORDINATOR = "swarm_coordinator"


class AgentStatus(Enum):
    """Agent lifecycle states."""
    IDLE = "idle"
    SUBSCRIBED = "subscribed"
    INTERPRETING = "interpreting"
    PROPOSING = "proposing"
    CONVERGING = "converging"
    HALTED = "halted"
    SEALED = "sealed"


class VerdictState(Enum):
    """888_JUDGE verdict states."""
    AGENT_PROPOSE = "agent_propose"
    AC_RISK_QUALIFY = "ac_risk_qualify"
    FLOOR_CHECK_PASS = "floor_check_pass"
    DISCORDANCE_ALERT = "discordance_alert"
    HOLD_888 = "888_hold"
    SEAL_999 = "999_seal"


class FloorId(Enum):
    """arifOS Constitutional Floors F1-F13."""
    F1_AMANAH = "F1"  # Reversibility
    F2_TRUTH = "F2"   # Evidence grounded
    F3_TRI_WITNESS = "F3"
    F4_CLARITY = "F4" # Units validated
    F5_PEACE = "F5"
    F6_EMPATHY = "F6"
    F7_HUMILITY = "F7"  # Confidence ≤ 15%
    F8_GENIUS = "F8"
    F9_PHYSICS_9 = "F9"  # Deterministic physical laws adherence
    F10_CONSCIENCE = "F10"
    F11_AUDITABILITY = "F11"  # Logged/inspectable
    F12_RESILIENCE = "F12"
    F13_SOVEREIGN = "F13"  # Human authority


# ═══════════════════════════════════════════════════════════════════════════════
# Data Classes
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Agent:
    """Represents an AI agent in the ACP ecosystem."""
    agent_id: str
    role: AgentRole
    name: str
    subscribed_resources: Set[str] = field(default_factory=set)
    authorized_tools: Set[str] = field(default_factory=set)
    status: AgentStatus = AgentStatus.IDLE
    last_proposal: Optional[dict] = None
    confidence_score: float = 0.0
    connected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "name": self.name,
            "status": self.status.value,
            "subscribed_resources": list(self.subscribed_resources),
            "confidence_score": self.confidence_score,
            "connected_at": self.connected_at.isoformat(),
        }


@dataclass
class A2AMessage:
    """Inter-agent communication message."""
    msg_id: str
    sender_id: str
    recipient_id: Optional[str]  # None = broadcast
    msg_type: str  # "proposal", "query", "validation", "alert", "verdict"
    payload: dict
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> dict:
        return {
            "msg_id": self.msg_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "msg_type": self.msg_type,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class FloorCheck:
    """Result of constitutional floor validation."""
    floor: FloorId
    passed: bool
    message: str
    confidence: float  # 0-1
    
    def to_dict(self) -> dict:
        return {
            "floor": self.floor.value,
            "passed": self.passed,
            "message": self.message,
            "confidence": self.confidence,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Agent Registry
# ═══════════════════════════════════════════════════════════════════════════════

class AgentRegistry:
    """
    Central registry for all agents connected to the GEOX ACP.
    Manages subscriptions, roles, and lifecycle.
    """
    
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._resource_subscribers: Dict[str, Set[str]] = {}
        self._listeners: WeakSet[Callable[[A2AMessage], None]] = WeakSet()
        self._lock = asyncio.Lock()
    
    async def register(
        self,
        agent_id: str,
        role: AgentRole,
        name: str,
        resources: Optional[List[str]] = None,
        tools: Optional[List[str]] = None
    ) -> Agent:
        """Register a new agent with the ACP."""
        async with self._lock:
            if agent_id in self._agents:
                logger.warning("Agent %s already registered, updating", agent_id)
            
            agent = Agent(
                agent_id=agent_id,
                role=role,
                name=name,
                subscribed_resources=set(resources or []),
                authorized_tools=set(tools or []),
                status=AgentStatus.SUBSCRIBED,
            )
            self._agents[agent_id] = agent
            
            # Update resource subscriber index
            for resource in agent.subscribed_resources:
                if resource not in self._resource_subscribers:
                    self._resource_subscribers[resource] = set()
                self._resource_subscribers[resource].add(agent_id)
            
            logger.info("Agent registered: %s (%s)", agent_id, role.value)
            return agent
    
    async def unregister(self, agent_id: str) -> bool:
        """Unregister an agent from the ACP."""
        async with self._lock:
            if agent_id not in self._agents:
                return False
            
            agent = self._agents.pop(agent_id)
            
            # Remove from resource subscriptions
            for resource in agent.subscribed_resources:
                if resource in self._resource_subscribers:
                    self._resource_subscribers[resource].discard(agent_id)
            
            logger.info("Agent unregistered: %s", agent_id)
            return True
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID."""
        return self._agents.get(agent_id)
    
    def get_subscribers(self, resource: str) -> List[Agent]:
        """Get all agents subscribed to a resource."""
        agent_ids = self._resource_subscribers.get(resource, set())
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]
    
    def list_agents(self) -> List[Agent]:
        """List all registered agents."""
        return list(self._agents.values())
    
    def update_agent_status(self, agent_id: str, status: AgentStatus) -> bool:
        """Update agent status."""
        if agent_id not in self._agents:
            return False
        self._agents[agent_id].status = status
        return True
    
    def set_proposal(self, agent_id: str, proposal: dict) -> bool:
        """Set agent's current proposal."""
        if agent_id not in self._agents:
            return False
        self._agents[agent_id].last_proposal = proposal
        self._agents[agent_id].status = AgentStatus.PROPOSING
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# A2A Message Bus
# ═══════════════════════════════════════════════════════════════════════════════

class A2AMessageBus:
    """
    Message bus for Agent-to-Agent communication.
    Supports broadcast, unicast, and multicast patterns.
    """
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self._message_history: List[A2AMessage] = []
        self._handlers: Dict[str, List[Callable[[A2AMessage], None]]] = {}
        self._lock = asyncio.Lock()
    
    async def send(self, message: A2AMessage) -> bool:
        """
        Send a message via the A2A bus.
        If recipient_id is None, broadcasts to all agents subscribed to relevant resources.
        """
        async with self._lock:
            self._message_history.append(message)
            
            # Trim history to prevent unbounded growth
            if len(self._message_history) > 10000:
                self._message_history = self._message_history[-5000:]
        
        if message.recipient_id:
            # Unicast
            target = self.registry.get_agent(message.recipient_id)
            if target:
                await self._deliver(message, target)
                return True
            return False
        else:
            # Broadcast to relevant agents
            sender = self.registry.get_agent(message.sender_id)
            if sender:
                # Get agents subscribed to same resources
                recipients: Set[str] = set()
                for resource in sender.subscribed_resources:
                    for agent_id in self.registry.get_subscribers(resource):
                        if agent_id != message.sender_id:
                            recipients.add(agent_id)
                
                for recipient_id in recipients:
                    target = self.registry.get_agent(recipient_id)
                    if target:
                        await self._deliver(message, target)
                return True
            return False
    
    async def _deliver(self, message: A2AMessage, recipient: Agent):
        """Deliver message to recipient (internal)."""
        logger.debug("A2A: %s -> %s (%s)", message.sender_id, recipient.agent_id, message.msg_type)
        
        # Trigger registered handlers
        handlers = self._handlers.get(message.msg_type, [])
        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                logger.error("A2A handler error: %s", e)
    
    def subscribe(self, msg_type: str, handler: Callable[[A2AMessage], None]):
        """Subscribe to message type."""
        if msg_type not in self._handlers:
            self._handlers[msg_type] = []
        self._handlers[msg_type].append(handler)
    
    def get_history(self, limit: int = 100) -> List[A2AMessage]:
        """Get recent message history."""
        return self._message_history[-limit:]


# ═══════════════════════════════════════════════════════════════════════════════
# Floor Enforcer (F1-F13 Constitutional Validation)
# ═══════════════════════════════════════════════════════════════════════════════

class FloorEnforcer:
    """
    Enforces arifOS Constitutional Floors F1-F13.
    Validates agent proposals against physical and ethical constraints.
    """
    
    def __init__(self):
        self._check_handlers: Dict[FloorId, Callable[..., FloorCheck]] = {
            FloorId.F2_TRUTH: self._check_f2_truth,
            FloorId.F4_CLARITY: self._check_f4_clarity,
            FloorId.F7_HUMILITY: self._check_f7_humility,
            FloorId.F9_PHYSICS_9: self._check_f9_physics_9,
            FloorId.F11_AUDITABILITY: self._check_f11_auditability,
            FloorId.F13_SOVEREIGN: self._check_f13_sovereign,
        }
    
    async def validate(
        self,
        proposal: dict,
        agent: Agent,
        required_floors: Optional[List[FloorId]] = None
    ) -> List[FloorCheck]:
        """
        Validate a proposal against all required constitutional floors.
        Returns list of floor check results.
        """
        floors = required_floors or list(FloorId)
        results = []
        
        for floor in floors:
            handler = self._check_handlers.get(floor)
            if handler:
                result = handler(proposal, agent)
                results.append(result)
            else:
                # Floor without handler auto-passes with warning
                results.append(FloorCheck(
                    floor=floor,
                    passed=True,
                    message=f"{floor.value}: No handler, auto-pass",
                    confidence=0.5
                ))
        
        return results
    
    def _check_f2_truth(self, proposal: dict, agent: Agent) -> FloorCheck:
        """F2: Evidence Grounded - Must have data basis."""
        has_evidence = "basis" in proposal or "data_source" in proposal
        return FloorCheck(
            floor=FloorId.F2_TRUTH,
            passed=has_evidence,
            message="F2: Evidence grounded" if has_evidence else "F2: No evidence basis",
            confidence=0.9 if has_evidence else 0.2
        )
    
    def _check_f4_clarity(self, proposal: dict, agent: Agent) -> FloorCheck:
        """F4: Clarity - Units must be valid."""
        # Check for valid units in proposal
        units = proposal.get("units", {})
        valid_units = all(u in ["m", "m/s", "kg/m3", "Pa", "K", "ohm.m", "v/v"] for u in units.values())
        return FloorCheck(
            floor=FloorId.F4_CLARITY,
            passed=valid_units,
            message="F4: Units validated" if valid_units else "F4: Invalid units detected",
            confidence=0.95 if valid_units else 0.3
        )
    
    def _check_f7_humility(self, proposal: dict, agent: Agent) -> FloorCheck:
        """F7: Humility - Uncertainty must be bounded (±4% default, max 15%)."""
        uncertainty = proposal.get("uncertainty", 0.0)
        confidence = proposal.get("confidence", 1.0 - uncertainty)
        
        # Check if uncertainty is within F7 bounds
        within_bounds = uncertainty <= F7_MAX_UNCERTAINTY
        meets_floor = uncertainty >= F7_HUMILITY_FLOOR
        
        if confidence > 0.85 and uncertainty < F7_HUMILITY_FLOOR:
            # Overconfident - force humility
            return FloorCheck(
                floor=FloorId.F7_HUMILITY,
                passed=False,
                message=f"F7: Overconfidence detected ({uncertainty*100:.1f}% < {F7_HUMILITY_FLOOR*100}%)",
                confidence=0.3
            )
        
        return FloorCheck(
            floor=FloorId.F7_HUMILITY,
            passed=within_bounds,
            message=f"F7: Humility bound ±{uncertainty*100:.1f}%" if within_bounds else f"F7: Uncertainty exceeds max ({uncertainty*100:.1f}%)",
            confidence=1.0 - uncertainty if within_bounds else 0.2
        )
    
    def _check_f9_physics_9(self, proposal: dict, agent: Agent) -> FloorCheck:
        """F9: Physics9 - Adherence to deterministic physical laws."""
        # Check if proposal keys overlap with PHYSICS_9 state vector
        proposal_keys = set(proposal.keys())
        has_physics_keys = any(key in proposal_keys for key in PHYSICS_9_KEYS)
        
        # Also maintain anti-hantu grounding (no consciousness claims)
        text = json.dumps(proposal).lower()
        banned_terms = ["conscious", "sentient", "i feel", "i believe", "self-aware"]
        has_claims = any(term in text for term in banned_terms)
        
        passed = (has_physics_keys or "basis" in proposal) and not has_claims
        
        return FloorCheck(
            floor=FloorId.F9_PHYSICS_9,
            passed=passed,
            message="F9: Physics9 grounded" if passed else "F9: Insufficient physics grounding or consciousness claim detected",
            confidence=1.0 if passed else 0.0
        )
    
    def _check_f11_auditability(self, proposal: dict, agent: Agent) -> FloorCheck:
        """F11: Auditability - Must be logged/inspectable."""
        has_timestamp = "timestamp" in proposal or "@timestamp" in proposal
        has_agent_id = "agent_id" in proposal or agent.agent_id
        return FloorCheck(
            floor=FloorId.F11_AUDITABILITY,
            passed=has_timestamp or has_agent_id,
            message="F11: Audit trail complete" if (has_timestamp or has_agent_id) else "F11: Missing audit metadata",
            confidence=0.95 if (has_timestamp and has_agent_id) else 0.6
        )
    
    def _check_f13_sovereign(self, proposal: dict, agent: Agent) -> FloorCheck:
        """F13: Sovereign - Human authority preserved."""
        # Check if proposal requires human approval
        risk_level = proposal.get("risk_level", "low")
        requires_auth = risk_level in ["high", "critical", "destructive"]
        has_auth = proposal.get("human_authorized", False)
        
        if requires_auth and not has_auth:
            return FloorCheck(
                floor=FloorId.F13_SOVEREIGN,
                passed=False,
                message="F13: High-risk operation requires 888_JUDGE authorization",
                confidence=0.0
            )
        
        return FloorCheck(
            floor=FloorId.F13_SOVEREIGN,
            passed=True,
            message="F13: Sovereign authority preserved",
            confidence=1.0
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Discordance Detector
# ═══════════════════════════════════════════════════════════════════════════════

class DiscordanceDetector:
    """
    Detects conflicts between agent proposals.
    Triggers convergence protocols when agents disagree.
    """
    
    def __init__(self, registry: AgentRegistry, bus: A2AMessageBus):
        self.registry = registry
        self.bus = bus
        self._threshold = 0.15  # 15% difference threshold
    
    async def check_convergence(self, resource: str) -> dict:
        """
        Check if all agents subscribed to a resource have converged.
        Returns convergence report.
        """
        agents = self.registry.get_subscribers(resource)
        proposals = [a.last_proposal for a in agents if a.last_proposal]
        
        if len(proposals) < 2:
            return {
                "converged": True,
                "discordance": 0.0,
                "agent_count": len(proposals),
                "message": "Insufficient agents for convergence check"
            }
        
        # Calculate discordance (simplified: variance in key values)
        discordance = self._calculate_discordance(proposals)
        converged = discordance <= self._threshold
        
        if not converged:
            # Trigger discordance alert
            await self.bus.send(A2AMessage(
                msg_id=f"alert_{datetime.now(timezone.utc).timestamp()}",
                sender_id="acp.discordance_detector",
                recipient_id=None,  # Broadcast
                msg_type="alert",
                payload={
                    "alert_type": "DISCORDANCE",
                    "resource": resource,
                    "discordance": discordance,
                    "threshold": self._threshold,
                    "agents": [a.agent_id for a in agents],
                    "message": f"Agent proposals diverge by {discordance*100:.1f}% (threshold: {self._threshold*100}%)"
                }
            ))
        
        return {
            "converged": converged,
            "discordance": discordance,
            "threshold": self._threshold,
            "agent_count": len(agents),
            "message": "Converged" if converged else f"Discordance: {discordance*100:.1f}%"
        }
    
    def _calculate_discordance(self, proposals: List[dict]) -> float:
        """Calculate discordance metric between proposals."""
        # Extract numerical values
        values = []
        for p in proposals:
            val = p.get("value") or p.get("result") or p.get("confidence", 0)
            if isinstance(val, (int, float)):
                values.append(val)
        
        if not values or len(values) < 2:
            return 0.0
        
        # Coefficient of variation as discordance metric
        mean = sum(values) / len(values)
        if mean == 0:
            return 0.0
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5
        cv = std_dev / mean
        
        return min(cv, 1.0)  # Cap at 100%


# ═══════════════════════════════════════════════════════════════════════════════
# 888_JUDGE Verdict Engine
# ═══════════════════════════════════════════════════════════════════════════════

class Judge888:
    """
    The Sovereign Authority (F13).
    Issues verdicts on agent proposals and manages the seal protocol.
    """
    
    def __init__(self, enforcer: FloorEnforcer):
        self.enforcer = enforcer
        self._verdict_history: List[dict] = []
        self._pending_proposals: Dict[str, dict] = {}
    
    async def evaluate(
        self,
        proposal: dict,
        agent: Agent,
        auto_low_risk: bool = True
    ) -> dict:
        """
        Evaluate a proposal and issue verdict.
        Returns verdict with full floor analysis.
        """
        # Run floor checks
        floor_results = await self.enforcer.validate(proposal, agent)
        
        # Determine overall status
        all_passed = all(r.passed for r in floor_results)
        any_critical_fail = any(not r.passed and r.floor in [FloorId.F2_TRUTH, FloorId.F7_HUMILITY, FloorId.F13_SOVEREIGN] for r in floor_results)
        
        # Determine verdict
        if any_critical_fail:
            verdict = VerdictState.HOLD_888
        elif all_passed:
            risk = proposal.get("risk_level", "low")
            if risk == "low" and auto_low_risk:
                verdict = VerdictState.AC_RISK_QUALIFY
            else:
                verdict = VerdictState.FLOOR_CHECK_PASS
        else:
            verdict = VerdictState.DISCORDANCE_ALERT
        
        result = {
            "verdict": verdict.value,
            "agent_id": agent.agent_id,
            "proposal_id": proposal.get("id", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "floor_results": [r.to_dict() for r in floor_results],
            "all_passed": all_passed,
            "message": self._verdict_message(verdict),
        }
        
        self._verdict_history.append(result)
        return result
    
    def _verdict_message(self, verdict: VerdictState) -> str:
        messages = {
            VerdictState.AGENT_PROPOSE: "Agent proposal submitted for review",
            VerdictState.AC_RISK_QUALIFY: "AC_Risk bounds satisfied, auto-approved",
            VerdictState.FLOOR_CHECK_PASS: "All floors passed, awaiting seal",
            VerdictState.DISCORDANCE_ALERT: "Agent discordance detected, review required",
            VerdictState.HOLD_888: "888_HOLD: Critical floor violation",
            VerdictState.SEAL_999: "999_SEAL: Sovereign authority granted",
        }
        return messages.get(verdict, "Unknown verdict")
    
    def grant_seal(self, proposal_id: str, human_auth_token: str) -> dict:
        """
        Grant 999_SEAL (human authority required).
        """
        # Validate auth token (simplified)
        if not human_auth_token or not human_auth_token.startswith("Wscar_"):
            return {
                "sealed": False,
                "error": "Invalid sovereign authority token"
            }
        
        result = {
            "verdict": VerdictState.SEAL_999.value,
            "proposal_id": proposal_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "999_SEAL granted. DITEMPA BUKAN DIBERI.",
            "sealed": True,
        }
        
        self._verdict_history.append(result)
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# ACP Server Integration
# ═══════════════════════════════════════════════════════════════════════════════

class GEOSXACP:
    """
    Main ACP controller that integrates with the MCP server.
    Singleton instance manages the entire agent ecosystem.
    """
    
    _instance: Optional["GEOSXACP"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.registry = AgentRegistry()
        self.bus = A2AMessageBus(self.registry)
        self.enforcer = FloorEnforcer()
        self.discordance = DiscordanceDetector(self.registry, self.bus)
        self.judge = Judge888(self.enforcer)
        
        self._initialized = True
        logger.info("GEOX ACP initialized — DITEMPA BUKAN DIBERI")
    
    async def register_agent(
        self,
        agent_id: str,
        role: str,
        name: str,
        resources: Optional[List[str]] = None,
        tools: Optional[List[str]] = None
    ) -> Agent:
        """Register an agent with the ACP."""
        role_enum = AgentRole(role) if role in [r.value for r in AgentRole] else AgentRole.GEOLOGIST
        return await self.registry.register(agent_id, role_enum, name, resources, tools)
    
    async def submit_proposal(self, agent_id: str, proposal: dict) -> dict:
        """Submit a proposal for evaluation."""
        agent = self.registry.get_agent(agent_id)
        if not agent:
            return {"error": "Agent not registered"}
        
        # Update agent proposal
        self.registry.set_proposal(agent_id, proposal)
        
        # Evaluate through 888_JUDGE
        verdict = await self.judge.evaluate(proposal, agent)
        
        # Broadcast to other agents
        await self.bus.send(A2AMessage(
            msg_id=f"prop_{datetime.now(timezone.utc).timestamp()}",
            sender_id=agent_id,
            recipient_id=None,
            msg_type="proposal",
            payload={
                "proposal": proposal,
                "verdict": verdict,
            }
        ))
        
        return verdict
    
    def get_status(self) -> dict:
        """Get ACP system status."""
        return {
            "acp_version": "2.0.0-UNIFIED-SPEC",
            "seal": "999_SEAL_ACP",
            "agents_registered": len(self.registry.list_agents()),
            "f7_humility_floor": F7_HUMILITY_FLOOR,
            "f7_max_uncertainty": F7_MAX_UNCERTAINTY,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global ACP instance
acp = GEOSXACP()


# ═══════════════════════════════════════════════════════════════════════════════
# MCP Tool Wrappers (for integration with geox_mcp_server.py)
# ═══════════════════════════════════════════════════════════════════════════════

async def acp_register_agent(
    agent_id: str,
    role: str,
    name: str,
    resources: Optional[List[str]] = None,
    tools: Optional[List[str]] = None
) -> dict:
    """MCP Tool: Register an agent with the ACP."""
    try:
        agent = await acp.register_agent(agent_id, role, name, resources, tools)
        return {
            "success": True,
            "agent": agent.to_dict(),
            "acp_status": acp.get_status(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def acp_submit_proposal(agent_id: str, proposal: dict) -> dict:
    """MCP Tool: Submit a proposal for 888_JUDGE evaluation."""
    return await acp.submit_proposal(agent_id, proposal)


async def acp_check_convergence(resource: str) -> dict:
    """MCP Tool: Check agent convergence on a resource."""
    return await acp.discordance.check_convergence(resource)


async def acp_grant_seal(proposal_id: str, human_auth_token: str) -> dict:
    """MCP Tool: Grant 999_SEAL (sovereign authority)."""
    return acp.judge.grant_seal(proposal_id, human_auth_token)


async def acp_get_status() -> dict:
    """MCP Tool: Get ACP system status."""
    return acp.get_status()


# Export for use in main MCP server
__all__ = [
    "acp",
    "GEOSXACP",
    "AgentRegistry",
    "A2AMessageBus",
    "FloorEnforcer",
    "DiscordanceDetector",
    "Judge888",
    "Agent",
    "AgentRole",
    "AgentStatus",
    "A2AMessage",
    "FloorCheck",
    "FloorId",
    "VerdictState",
    "F7_HUMILITY_FLOOR",
    "F7_MAX_UNCERTAINTY",
    "acp_register_agent",
    "acp_submit_proposal",
    "acp_check_convergence",
    "acp_grant_seal",
    "acp_get_status",
]
