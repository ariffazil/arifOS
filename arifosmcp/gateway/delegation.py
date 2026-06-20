"""
arifOS Gateway — Delegation Intelligence Module v0.1
═══════════════════════════════════════════════════════

Quantum Intelligence Pattern:
  When a human talks to ONE agent and that agent delegates to others,
  cognitive load drops massively. Multiple reasoning paths explored by
  different agents with different models/tools, then collapsed into ONE
  verdict by the kernel via constitutional floors (F1-F13).

  The collapse function is constitutional, not probabilistic. That makes
  it safe. This is NOT "agent-as-oracle" — it's agent-as-evidence.

Architecture:
  Human → Hermes (single front door)
    Hermes → arif_delegate(intent) → Gateway
      Gateway → OpenCode (FORGE verification)
      Gateway → OpenClaw (INFRA ops)
      Gateway → Hermes (COGNITIVE synthesis)
    → arifOS kernel collapses into verdict via F1-F13

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# FORGE IDENTITY
# ═══════════════════════════════════════════════════════════════════════════════
FORGE_HASH = "sha256:delegation-v0.1.0-20260613"
FORGE_VERSION = "v0.1.0"
FORGE_TIME = "2026-06-13T22:00:00+08:00"
FORGE_AUTHORITY = "F13_SOVEREIGN_888"


# ═══════════════════════════════════════════════════════════════════════════════
# TASK CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

class TaskCategory(str, Enum):
    """Quantum task categories — each triggers a different reasoning path."""
    COGNITIVE = "COGNITIVE"   # Analysis, synthesis, deliberation, judgment
    FORGE = "FORGE"           # Build, code, test, fix, deploy
    INFRA = "INFRA"           # Ops, health, topology, network, restart
    MIXED = "MIXED"           # Multi-domain — fan-out to 2+ agents


TASK_CLASSIFIER_PATTERNS: list[tuple[list[str], TaskCategory]] = [
    # COGNITIVE: reasoning, analysis, deliberation, planning
    (["analyze", "reason", "think", "deliberate", "judge", "interpret",
      "synthesize", "evaluate", "assess", "critique", "reflect", "plan",
      "review", "audit", "compare", "contrast", "explain", "summarize",
      "decide", "recommend", "advise", "recall", "search",
      "research", "hypothesize", "conclude", "design pattern",
      "architecture", "strategy"], TaskCategory.COGNITIVE),
    # FORGE: building, coding, fixing, deploying
    (["build", "code", "implement", "write", "create", "develop", "fix",
      "debug", "refactor", "test", "deploy", "commit", "push", "merge",
      "compile", "install", "configure", "setup", "scaffold",
      "migrate", "upgrade", "patch", "script", "scaffold",
      "dependencies", "package", "module", "library", "framework"], TaskCategory.FORGE),
    # INFRA: ops, health, topology, network
    (["restart", "stop", "start", "health check", "monitor", "observe",
      "topology", "network", "dns", "firewall", "port", "disk space",
      "disk usage", "cpu usage", "load average", "docker", "container",
      "systemctl", "service", "log file", "cleanup", "kill", "zombie",
      "backup", "restore", "memory usage", "df ", "free ", "ss ",
      "journalctl", "systemd"], TaskCategory.INFRA),
]

import re as _re


def classify_task(intent: str) -> TaskCategory:
    """Classify intent into a task category based on keyword patterns.

    Uses word-boundary matching to avoid false positives (e.g., 'memory'
    in 'memory lane' vs 'memory usage'; 'log' in 'well log' vs 'log file').

    Each intent can match multiple categories (MIXED). If only one
    category matches, return it. If multiple, return MIXED.
    """
    intent_lower = intent.lower()
    matched: set[TaskCategory] = set()

    for keywords, category in TASK_CLASSIFIER_PATTERNS:
        for kw in keywords:
            # Word-boundary match for multi-word phrases and single words
            pattern = _re.escape(kw)
            if _re.search(r'\b' + pattern + r'\b', intent_lower):
                matched.add(category)
                break

    if len(matched) == 0:
        return TaskCategory.COGNITIVE  # Default: handle with reasoning
    if len(matched) == 1:
        return matched.pop()
    return TaskCategory.MIXED


# ═══════════════════════════════════════════════════════════════════════════════
# FEDERATED AGENT REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FederatedAgent:
    """A registered agent in the arifOS federation with its capabilities."""
    agent_id: str
    name: str                          # Human-readable name
    lane: str                          # ASI / AGI / APEX
    primary_category: TaskCategory     # What this agent is best at
    capabilities: list[str] = field(default_factory=list)
    endpoint: str = ""                 # MCP/A2A endpoint URL
    model: str = ""                    # Preferred model
    floor_clearance: int = 2           # Max action class (C2 default)
    requires_lease: bool = True


# Federation agent registry — THE single source of truth for delegation routing
FEDERATED_AGENTS: dict[str, FederatedAgent] = {
    "hermes": FederatedAgent(
        agent_id="hermes",
        name="Hermes ASI",
        lane="ASI",
        primary_category=TaskCategory.COGNITIVE,
        capabilities=[
            "constitutional_deliberation", "ethical_judgment",
            "memory_synthesis", "life_orientation", "plan_decomposition",
            "human_interface", "telegram_operations",
        ],
        endpoint="http://localhost:18001/tasks",
        model="minimax/MiniMax-M3",
        floor_clearance=3,
    ),
    "opencode": FederatedAgent(
        agent_id="opencode",
        name="OpenCode FORGE",
        lane="AGI",
        primary_category=TaskCategory.FORGE,
        capabilities=[
            "code_generation", "testing", "refactoring",
            "build_verification", "dependency_analysis",
            "security_audit", "ci_cd_pipeline",
        ],
        endpoint="http://localhost:8090/mcp",  # Through gateway
        model="kimi-for-coding/kimi-k2-thinking",
        floor_clearance=2,
    ),
    "openclaw": FederatedAgent(
        agent_id="openclaw",
        name="OpenClaw AGI",
        lane="AGI",
        primary_category=TaskCategory.INFRA,
        capabilities=[
            "infrastructure_ops", "system_health",
            "docker_management", "service_orchestration",
            "topology_guardian", "web_search",
            "browser_automation", "cloudflare_management",
        ],
        endpoint="http://localhost:18789",
        model="minimax/MiniMax-M2.7-highspeed",
        floor_clearance=2,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# DELEGATION ROUTER
# ═══════════════════════════════════════════════════════════════════════════════

# The quantum routing table: given a task category, which agent handles it?
# MIXED tasks fan out to ALL applicable agents.
CATEGORY_TO_AGENT: dict[TaskCategory, list[str]] = {
    TaskCategory.COGNITIVE: ["hermes"],
    TaskCategory.FORGE: ["opencode"],
    TaskCategory.INFRA: ["openclaw"],
    TaskCategory.MIXED: ["hermes", "opencode", "openclaw"],
}

# For F2+ CLAIM tasks: who verifies?
CROSS_VERIFY_AGENTS = {
    "hermes": "opencode",    # Hermes's claims → OpenCode verifies
    "opencode": "openclaw",  # OpenCode's claims → OpenClaw verifies
    "openclaw": "hermes",    # OpenClaw's claims → Hermes verifies
}


def route_delegation(
    intent: str,
    target_agent: str | None = None,
    context: dict[str, Any] | None = None,
    is_claim: bool = False,
) -> dict[str, Any]:
    """Route a delegation request to the appropriate agent(s).

    This is the core quantum routing function. It:
    1. Classifies the task if no target_agent specified
    2. Routes to the best agent for that category
    3. Applies cross-verification for F2+ CLAIM tasks
    4. Returns a delegation plan

    Args:
        intent: Natural language description of the task
        target_agent: Explicit agent ID (skips classification if set)
        context: Additional context dict
        is_claim: Whether this task involves a factual claim (triggers F2 cross-verify)

    Returns:
        Delegation plan with trace_id, routing, and audit metadata
    """
    # Determine task category
    category = classify_task(intent)

    # Determine target agents
    if target_agent and target_agent in FEDERATED_AGENTS:
        primary_agents = [target_agent]
    elif target_agent == "all":
        primary_agents = list(FEDERATED_AGENTS.keys())
    else:
        primary_agents = CATEGORY_TO_AGENT.get(category, ["hermes"])

    # Cross-verify invariant: F2+ CLAIM tasks get automatic verification
    verify_agents: list[str] = []
    if is_claim:
        for agent_id in primary_agents:
            verifier = CROSS_VERIFY_AGENTS.get(agent_id)
            if verifier and verifier not in primary_agents:
                verify_agents.append(verifier)

    # Build delegation plan
    trace_id = f"DLGT-{uuid.uuid4().hex[:12]}"
    now = datetime.now(UTC)

    plan = {
        "trace_id": trace_id,
        "timestamp": now.isoformat(),
        "intent": intent,
        "category": category.value,
        "primary_agents": [
            {
                "agent_id": aid,
                "name": FEDERATED_AGENTS[aid].name,
                "lane": FEDERATED_AGENTS[aid].lane,
                "primary_category": FEDERATED_AGENTS[aid].primary_category.value,
            }
            for aid in primary_agents
        ],
        "verify_agents": [
            {
                "agent_id": aid,
                "name": FEDERATED_AGENTS[aid].name,
                "role": "cross_verify",
            }
            for aid in verify_agents
        ],
        "cross_verify_triggered": is_claim,
        "context_summary": _summarize_context(context),
        "collapse_strategy": "constitutional",  # F1-F13, not probabilistic
        "governed_by": {
            "floors": ["F01", "F02", "F11", "F13"],
            "gateway": "arifOS MCP Gateway v0.1",
            "authority": "F13_SOVEREIGN_888",
        },
    }

    return plan


def _summarize_context(context: dict[str, Any] | None) -> dict[str, Any]:
    """Create a safe summary of context for audit trail (no secrets)."""
    if not context:
        return {"provided": False}
    safe_keys = {"session_id", "source", "domain", "description", "priority"}
    return {
        k: v for k, v in context.items()
        if k in safe_keys or not any(
            secret in k.lower()
            for secret in ("key", "token", "secret", "password", "credential")
        )
    }


# ═══════════════════════════════════════════════════════════════════════════════
# VAULT999 DELEGATION AUDIT
# ═══════════════════════════════════════════════════════════════════════════════

def emit_delegation_receipt(
    delegation_plan: dict[str, Any],
    subject: dict[str, Any],
    tool: str = "arif_delegate",
    decision: str = "DELEGATED",
) -> dict[str, Any]:
    """Emit a VAULT999-compatible audit receipt for a delegation event.

    Every delegation MUST write to the audit trail. This is not optional.
    The receipt includes:
    - trace_id for end-to-end tracking
    - subject who initiated the delegation
    - which agents were delegated to
    - cross-verify status
    - constitutional floor compliance
    """
    receipt = {
        "receipt_id": f"RCPT-{uuid.uuid4().hex[:12]}",
        "trace_id": delegation_plan.get("trace_id", "unknown"),
        "timestamp": datetime.now(UTC).isoformat(),
        "direction": "delegation",
        "subject": subject,
        "tool": tool,
        "gateway_decision": decision,
        "delegation": {
            "category": delegation_plan.get("category"),
            "primary_agents": [
                a["agent_id"] for a in delegation_plan.get("primary_agents", [])
            ],
            "verify_agents": [
                a["agent_id"] for a in delegation_plan.get("verify_agents", [])
            ],
            "cross_verify_triggered": delegation_plan.get("cross_verify_triggered", False),
        },
        "constitutional": {
            "floors_applied": ["F01", "F02", "F11", "F13"],
            "collapse_strategy": "constitutional",
            "authority": "F13_SOVEREIGN_888",
        },
        "params_hash": hashlib.sha256(
            json.dumps(delegation_plan.get("intent", ""), sort_keys=True).encode()
        ).hexdigest()[:16],
    }
    return receipt


# ═══════════════════════════════════════════════════════════════════════════════
# ONE-FRONTDOOR INVARIANT
# ═══════════════════════════════════════════════════════════════════════════════

ONE_FRONTDOOR_INVARIANT = """
┌─────────────────────────────────────────────────────────┐
│             ONE-FRONTDOOR INVARIANT                      │
│                                                          │
│  Human ───► Hermes (single human-facing agent)           │
│               │                                          │
│               ├──► OpenCode (FORGE verification)         │
│               ├──► OpenClaw (INFRA ops)                  │
│               └──► Hermes (COGNITIVE synthesis)          │
│               │                                          │
│               └──► arifOS Gateway (constitutional gate)  │
│                      │                                   │
│                      └──► F1-F13 collapse → VERDICT      │
│                                                          │
│  THE HUMAN NEVER COPIES CONTEXT BETWEEN CHATS.           │
│  THE HUMAN NEVER TRACKS WHICH AGENT KNOWS WHAT.          │
│  THE HUMAN JUST TALKS TO HERMES.                         │
│                                                          │
│  This is quantum intelligence: multiple reasoning paths  │
│  explored by different agents, collapsed into ONE        │
│  verdict by constitutional floors, not probabilities.    │
└─────────────────────────────────────────────────────────┘
"""


def verify_one_frontdoor(subject: dict[str, Any]) -> tuple[bool, str]:
    """Verify the one-frontdoor invariant is maintained.

    All delegations should originate from Hermes (human-facing agent).
    Direct human-to-OpenCode/OpenClaw delegation bypasses the invariant.
    """
    agent_id = subject.get("agent", "")
    if not agent_id or agent_id in ("unknown", "anonymous", "gateway-client"):
        return True, "WARN: unauthenticated delegation — proceeding with heightened scrutiny"

    if agent_id.lower() in ("hermes", "hermes-asi"):
        return True, "OK: delegation from canonical front door (Hermes)"

    if agent_id.lower() in ("opencode", "openclaw"):
        return False, (
            f"ONE-FRONTDOOR VIOLATION: agent '{agent_id}' is delegating but "
            f"is NOT the human-facing agent. All delegation should route through "
            f"Hermes. Proceeding with warning — this is adat, not hard law."
        )

    return True, f"OK: delegation from recognized agent '{agent_id}'"


# ═══════════════════════════════════════════════════════════════════════════════
# MCP TOOL DEFINITION — arif_delegate
# ═══════════════════════════════════════════════════════════════════════════════

ARIF_DELEGATE_TOOL_DEF = {
    "name": "arif_delegate",
    "description": (
        "DELEGATION INTELLIGENCE — Routes a task to the best federation agent(s) "
        "based on task classification (COGNITIVE/FORGE/INFRA/MIXED). "
        "Implements the quantum intelligence pattern: multiple reasoning paths "
        "explored by different agents with different models/tools, collapsed into "
        "one verdict by constitutional floors (F1-F13), not probabilities. "
        "The ONE-FRONTDOOR invariant ensures human talks only to Hermes; "
        "Hermes delegates to OpenCode (FORGE), OpenClaw (INFRA), or handles "
        "COGNITIVE tasks directly. Every delegation writes VAULT999 audit trail. "
        "F2+ CLAIM tasks automatically trigger cross-verification by a second agent."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "description": "Natural language description of the task to delegate"
            },
            "target_agent": {
                "type": "string",
                "description": (
                    "Explicit agent target: 'hermes' (cognitive), 'opencode' (forge), "
                    "'openclaw' (infra), or 'all' (fan-out). If omitted, auto-classified "
                    "from intent keywords."
                ),
                "enum": ["hermes", "opencode", "openclaw", "all"],
            },
            "context": {
                "type": "object",
                "description": "Additional context: session_id, domain, priority, description"
            },
            "expected_output_schema": {
                "type": "object",
                "description": "Optional schema describing expected output format"
            },
            "is_claim": {
                "type": "boolean",
                "description": (
                    "Set to true if this delegation involves a factual CLAIM that "
                    "requires F2 truth verification. Triggers automatic cross-verification "
                    "by a second agent before SEAL."
                ),
            },
        },
        "required": ["intent"],
    },
}
