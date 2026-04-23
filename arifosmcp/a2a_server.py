"""
arifOS Federation — A2A Server Implementation
=============================================
Each agent runs as an independent A2A server.

A2A Endpoints per agent:
- GET  /.well-known/agent-card     → Agent discovery
- POST /sendMessage                → Synchronous message
- POST /sendMessageStream          → Streaming message

Usage:
    # Start Perception agent
    python a2a_server.py P

    # Start all agents
    python a2a_server.py all
"""

from __future__ import annotations

import json
import uuid
from typing import Any, AsyncGenerator, Literal
from dataclasses import dataclass, field
from enum import Enum
from aiohttp import web

from a2a_aligned import (
    AGENT_CARDS,
    ORTHOGONALITY_ROUTING,
    A2AMessage,
    MessageRole,
    can_route,
)


# =============================================================================
# AGENT IMPLEMENTATIONS
# =============================================================================


class Agent:
    """Base agent implementation."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.card = AGENT_CARDS[agent_id]

    async def handle(self, message: A2AMessage) -> dict[str, Any]:
        """Handle incoming message."""
        raise NotImplementedError

    async def handle_stream(self, message: A2AMessage) -> AsyncGenerator[str, None]:
        """Handle streaming message."""
        result = await self.handle(message)
        yield json.dumps(result)


class PerceptionAgent(Agent):
    """P Agent — Reads from WELL, GEOX, VAULT, WEALTH."""

    def __init__(self):
        super().__init__("P")
        self.sources = ["WELL", "GEOX", "VAULT", "WEALTH"]

    async def handle(self, message: A2AMessage) -> dict[str, Any]:
        content = message.content

        if content.startswith("read:"):
            parts = content.split(":")
            if len(parts) == 3:
                source, action = parts[1], parts[2]
            else:
                source, action = parts[1], "state"
            return await self._read(source, action, message.session_id)

        if content == "sources":
            return {"agent": "P", "sources": self.sources}

        return {"agent": "P", "error": "unknown command", "content": content}

    async def _read(self, source: str, action: str, session_id: str | None) -> dict[str, Any]:
        if source not in self.sources:
            return {"agent": "P", "error": f"unknown source: {source}"}
        return {
            "agent": "P",
            "source": source,
            "action": action,
            "data": {"status": "stub", "session_id": session_id},
        }


class TransformationAgent(Agent):
    """T Agent — Computes physics, math, monte_carlo."""

    def __init__(self):
        super().__init__("T")

    async def handle(self, message: A2AMessage) -> dict[str, Any]:
        content = message.content

        if content.startswith("compute:"):
            parts = content.split(":")
            computation = parts[1] if len(parts) > 1 else "unknown"
            params = json.loads(parts[2]) if len(parts) > 2 else {}
            return await self._compute(computation, params, message.session_id)

        return {"agent": "T", "error": "unknown command", "content": content}

    async def _compute(
        self, computation: str, params: dict, session_id: str | None
    ) -> dict[str, Any]:
        valid = ["physics", "math", "monte_carlo", "entropy"]
        if computation not in valid:
            return {"agent": "T", "error": f"unknown computation: {computation}"}
        return {
            "agent": "T",
            "computation": computation,
            "result": {"status": "stub", "params": params, "session_id": session_id},
        }


class ValuationAgent(Agent):
    """V Agent — Ranks by NPV, EMV, allocation."""

    def __init__(self):
        super().__init__("V")

    async def handle(self, message: A2AMessage) -> dict[str, Any]:
        content = message.content

        if content.startswith("rank:"):
            parts = content.split(":")
            ranking = parts[1] if len(parts) > 1 else "unknown"
            candidates = json.loads(parts[2]) if len(parts) > 2 else []
            return await self._rank(ranking, candidates, message.session_id)

        return {"agent": "V", "error": "unknown command", "content": content}

    async def _rank(self, ranking: str, candidates: list, session_id: str | None) -> dict[str, Any]:
        valid = ["NPV", "EMV", "allocation", "personal"]
        if ranking not in valid:
            return {"agent": "V", "error": f"unknown ranking: {ranking}"}
        return {
            "agent": "V",
            "ranking": ranking,
            "rankings": [{"id": c.get("id", i), "score": 0.0} for i, c in enumerate(candidates)],
            "session_id": session_id,
        }


class GovernanceAgent(Agent):
    """G Agent — Routes, judges, enforces orthogonality."""

    def __init__(self):
        super().__init__("G")
        self.router = A2ARouterClient()

    async def handle(self, message: A2AMessage) -> dict[str, Any]:
        content = message.content

        if content.startswith("route:"):
            parts = content.split(":", 3)
            target = parts[1] if len(parts) > 1 else ""
            payload = json.loads(parts[2]) if len(parts) > 2 else {}
            return await self._route(target, payload, message.session_id)

        if content.startswith("judge:"):
            action_data = content.split(":", 1)[1]
            return await self._judge(action_data, message.session_id)

        if content.startswith("init:"):
            intent = content.split(":", 1)[1]
            return await self._init(intent, message.session_id)

        if content.startswith("orthogonality:"):
            return await self._check_orthogonality(content.split(":", 1)[1])

        return {"agent": "G", "error": "unknown command", "content": content}

    async def _route(self, target: str, payload: dict, session_id: str | None) -> dict[str, Any]:
        result = await self.router.route(self.agent_id, target, payload, session_id)
        return {"agent": "G", "routing": result}

    async def _judge(self, action_data: str, session_id: str | None) -> dict[str, Any]:
        return {
            "agent": "G",
            "verdict": "SEAL",
            "floor_results": {},
            "session_id": session_id,
        }

    async def _init(self, intent: str, session_id: str | None) -> dict[str, Any]:
        return {
            "agent": "G",
            "session_id": session_id or str(uuid.uuid4()),
            "intent": intent,
            "status": "initialized",
        }

    async def _check_orthogonality(self, check_str: str) -> dict[str, Any]:
        parts = check_str.split("->")
        if len(parts) == 2:
            caller, target = parts[0], parts[1]
            allowed = can_route(caller, target)
            return {
                "agent": "G",
                "check": f"{caller} -> {target}",
                "allowed": allowed,
                "omega_ortho": 1.0 if allowed else 0.0,
            }
        return {"agent": "G", "error": "invalid orthogonality check format"}


class ExecutionAgent(Agent):
    """E Agent — Mutates state via forge, vault, memory."""

    def __init__(self):
        super().__init__("E")

    async def handle(self, message: A2AMessage) -> dict[str, Any]:
        content = message.content

        if content.startswith("forge:"):
            plan = content.split(":", 1)[1]
            return await self._forge(plan, message.session_id)

        if content.startswith("vault:"):
            record = content.split(":", 1)[1]
            return await self._vault(record, message.session_id)

        if content.startswith("memory:"):
            memory = content.split(":", 1)[1]
            return await self._memory(memory, message.session_id)

        return {"agent": "E", "error": "unknown command", "content": content}

    async def _forge(self, plan: str, session_id: str | None) -> dict[str, Any]:
        return {
            "agent": "E",
            "operation": "forge",
            "manifest": {"status": "stub"},
            "receipt": {"id": str(uuid.uuid4())},
            "session_id": session_id,
        }

    async def _vault(self, record: str, session_id: str | None) -> dict[str, Any]:
        return {
            "agent": "E",
            "operation": "vault",
            "merkle_hash": "stub_hash",
            "seal_id": str(uuid.uuid4()),
            "session_id": session_id,
        }

    async def _memory(self, memory: str, session_id: str | None) -> dict[str, Any]:
        return {
            "agent": "E",
            "operation": "memory",
            "result": {"status": "stored"},
            "session_id": session_id,
        }


class MetaAgent(Agent):
    """M Agent — Audits omega, discovers, monitors."""

    def __init__(self):
        super().__init__("M")

    async def handle(self, message: A2AMessage) -> dict[str, Any]:
        content = message.content

        if content.startswith("omega"):
            return await self._omega()

        if content.startswith("discover:"):
            query = content.split(":", 1)[1]
            return await self._discover(query)

        if content.startswith("monitor:"):
            return await self._monitor()

        return {"agent": "M", "error": "unknown command", "content": content}

    async def _omega(self) -> dict[str, Any]:
        return {
            "agent": "M",
            "omega_ortho": 1.0,
            "threshold": 0.95,
            "matrix": ORTHOGONALITY_ROUTING,
        }

    async def _discover(self, query: str) -> dict[str, Any]:
        return {
            "agent": "M",
            "query": query,
            "skills": [],
        }

    async def _monitor(self) -> dict[str, Any]:
        return {
            "agent": "M",
            "floors": {f"F{i}": "active" for i in range(1, 14)},
            "thermodynamics": {"delta_S": 0.0, "peace_squared": 1.0, "omega_0": 1.0},
        }


# =============================================================================
# AGENT REGISTRY
# =============================================================================

AGENTS: dict[str, Agent] = {
    "P": PerceptionAgent(),
    "T": TransformationAgent(),
    "V": ValuationAgent(),
    "G": GovernanceAgent(),
    "E": ExecutionAgent(),
    "M": MetaAgent(),
}


def get_agent(agent_id: str) -> Agent | None:
    return AGENTS.get(agent_id)


# =============================================================================
# A2A CLIENT (for inter-agent routing)
# =============================================================================


class A2ARouterClient:
    """Client for routing to other agents."""

    def __init__(self, base_port: int = 8100):
        self.base_port = base_port
        self.ports = {"P": 8100, "T": 8200, "V": 8300, "G": 8400, "E": 8500, "M": 8600}

    async def route(
        self, caller: str, target: str, payload: dict[str, Any], session_id: str | None = None
    ) -> dict[str, Any]:
        """Route message to target agent via HTTP."""
        if not can_route(caller, target):
            return {
                "error": f"Orthogonality violation: {caller} cannot route to {target}",
                "allowed": ORTHOGONALITY_ROUTING.get(caller, []),
            }

        port = self.ports.get(target, 8100)
        url = f"http://localhost:{port}/sendMessage"

        message = {
            "role": "agent",
            "content": json.dumps(payload),
            "sessionId": session_id,
        }

        try:
            async with web.ClientSession() as session:
                async with session.post(url, json=message) as resp:
                    return await resp.json()
        except Exception as e:
            return {"error": str(e), "target": target}


# =============================================================================
# A2A SERVER (aiohttp)
# =============================================================================


async def agent_card_handler(request: web.Request) -> web.Response:
    """Handle GET /.well-known/agent-card"""
    agent_id = request.match_info.get("agent_id")
    agent = get_agent(agent_id)

    if not agent:
        return web.json_response({"error": "Agent not found"}, status=404)

    return web.json_response(agent.card.to_dict())


async def send_message_handler(request: web.Request) -> web.Response:
    """Handle POST /sendMessage"""
    agent_id = request.match_info.get("agent_id")
    agent = get_agent(agent_id)

    if not agent:
        return web.json_response({"error": "Agent not found"}, status=404)

    body = await request.json()
    message = A2AMessage(
        role=body.get("role", "agent"),
        content=body.get("content", ""),
        session_id=body.get("sessionId"),
    )

    result = await agent.handle(message)
    return web.json_response(result)


async def send_message_stream_handler(request: web.Request) -> web.Response:
    """Handle POST /sendMessageStream (SSE)"""
    agent_id = request.match_info.get("agent_id")
    agent = get_agent(agent_id)

    if not agent:
        return web.json_response({"error": "Agent not found"}, status=404)

    body = await request.json()
    message = A2AMessage(
        role=body.get("role", "agent"),
        content=body.get("content", ""),
        session_id=body.get("sessionId"),
    )

    async def event_stream():
        async for chunk in agent.handle_stream(message):
            yield f"data: {chunk}\n\n"

    return web.Response(text=event_stream(), content_type="text/event-stream")


def create_app(agent_id: str) -> web.Application:
    """Create aiohttp app for an agent."""
    app = web.Application()
    app.router.add_get("/.well-known/agent-card", agent_card_handler)
    app.router.add_get(f"/{agent_id}/.well-known/agent-card", agent_card_handler)
    app.router.add_post("/sendMessage", send_message_handler)
    app.router.add_post(f"/{agent_id}/sendMessage", send_message_handler)
    app.router.add_post("/sendMessageStream", send_message_stream_handler)
    app.router.add_post(f"/{agent_id}/sendMessageStream", send_message_stream_handler)
    return app


# =============================================================================
# PORTS
# =============================================================================

AGENT_PORTS = {
    "P": 8100,
    "T": 8200,
    "V": 8300,
    "G": 8400,
    "E": 8500,
    "M": 8600,
}


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import sys

    agent_id = sys.argv[1] if len(sys.argv) > 1 else "P"

    if agent_id == "all":
        print("Starting all A2A agents...")
        for aid, port in AGENT_PORTS.items():
            print(f"  {aid}: http://localhost:{port}")
        print("Use 'python a2a_server.py <P|T|V|G|E|M>' to start individual agent")
    else:
        if agent_id not in AGENTS:
            print(f"Unknown agent: {agent_id}")
            print(f"Available: {list(AGENTS.keys())}")
            sys.exit(1)

        port = AGENT_PORTS[agent_id]
        app = create_app(agent_id)
        print(f"Starting {agent_id} agent on port {port}")
        print(f"  Agent Card: http://localhost:{port}/.well-known/agent-card")
        print(f"  SendMessage: http://localhost:{port}/sendMessage")
        web.run_app(app, host="0.0.0.0", port=port)
