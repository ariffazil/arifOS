# arifOS Agent Wire Protocol
## Inter-Agent Communication Standard

**Authority:** A-ARCHITECT  
**Version:** 1.0  
**Status:** PROVISIONAL — Requires A-VALIDATOR review

---

## Overview

The Wire Protocol defines how agents communicate within arifOS. It enables:
- **Message passing** between A-ARCHITECT, A-ENGINEER, A-AUDITOR, A-VALIDATOR
- **Task delegation** with constitutional tagging
- **Audit trail** of all inter-agent communication

---

## Message Schema

```python
@dataclass
class AgentMessage:
    """Standard inter-agent message envelope."""
    
    # Identity
    sender: str              # Agent ID (e.g., "A-ARCHITECT", "A-ENGINEER")
    receiver: str            # Target agent ID or "BROADCAST"
    
    # Message content
    action: MessageAction     # TASK | QUERY | RESPONSE | NOTIFY | ERROR
    payload: dict           # Arbitrary payload (action-specific)
    
    # Constitutional context
    floors_active: list[str]     # F1-F13 floors relevant to this message
    constitutional_tags: list[str]  # e.g., ["F1_AMANAH", "F9_TAQWA"]
    
    # Routing
    session_id: str          # Associated session
    correlation_id: str     # For tracing request chains
    reply_to: str | None    # Set if this is a response to a prior message
    
    # Metadata
    timestamp: str          # ISO-8601
    ttl_seconds: int = 300  # Message expiry


class MessageAction(Enum):
    TASK = "task"           # "Do this and report back"
    QUERY = "query"         # "Answer this question"
    RESPONSE = "response"   # "Here is the answer to your query"
    NOTIFY = "notify"       # "FYI, something happened"
    ERROR = "error"         # "Something went wrong"
    APPROVE = "approve"     # "This looks good, proceed"
    REJECT = "reject"       # "This violates a floor, do not proceed"
```

---

## Communication Flows

### Flow 1: Design → Implementation

```
A-ORCHESTRATOR
    │
    ├──► A-ARCHITECT (design task)
    │         │
    │         │ TASK: "Design safe code execution for X"
    │         ▼
    │    A-ARCHITECT returns design spec
    │         │
    ▼         ▼
    A-ENGINEER (implement)
          │
          │ TASK: "Build according to spec"
          │ RESPONSE: Implementation complete
          ▼
       A-AUDITOR (review)
          │
          │ APPROVE/REJECT
          ▼
       A-VALIDATOR (seal)
```

### Flow 2: Multi-Agent Query

```
User Query
    │
    ▼
A-ARCHITECT ──► A-ARCHITECT.QUERY("What tool for X?")
    │                    │
    │                    ▼
    │               A-ARCHITECT.RESPONSE(tool="agi_mind")
    │
    ▼
A-ENGINEER ──► A-ENGINEER.TASK("Call agi_mind for query X")
    │
    ▼
A-AUDITOR ──► A-AUDITOR.QUERY("Is this output safe?")
    │
    ▼
A-VALIDATOR ─► A-VALIDATOR.NOTIFY("SEAL confirmed")
```

### Flow 3: Error Escalation

```
A-ENGINEER
    │
    │ ERROR: "F9 violation in proposed code"
    ▼
A-AUDITOR ──► A-AUDITOR.REJECT("Cannot proceed: F9_TAQWA violated")
    │
    ▼
A-ARCHITECT ──► A-ARCHITECT.NOTIFY("Design rejected, revise")
```

---

## Wire Protocol: Message Examples

### TASK Message

```json
{
  "sender": "A-ORCHESTRATOR",
  "receiver": "A-ENGINEER",
  "action": "TASK",
  "payload": {
    "task_id": "task_042",
    "description": "Implement tool finder by category",
    "design_doc": "See ARCH/DOCS/TOOL_FINDER.md",
    "constraints": {
      "max_tools": 25,
      "must_support": ["governance", "intelligence", "reality"]
    }
  },
  "floors_active": ["F1", "F2", "F4", "F9"],
  "session_id": "session_001",
  "correlation_id": "corr_042",
  "timestamp": "2026-04-01T01:00:00Z",
  "ttl_seconds": 3600
}
```

### RESPONSE Message

```json
{
  "sender": "A-ENGINEER",
  "receiver": "A-ORCHESTRATOR",
  "action": "RESPONSE",
  "payload": {
    "task_id": "task_042",
    "status": "COMPLETED",
    "artifacts": {
      "file": "docs/TOOL_FINDER.md",
      "lines": 163
    },
    "constitutional_check": {
      "violations": [],
      "verdict": "SEAL"
    }
  },
  "reply_to": "corr_042",
  "floors_active": ["F1", "F2", "F4", "F9", "F11"],
  "session_id": "session_001",
  "correlation_id": "corr_042_response",
  "timestamp": "2026-04-01T01:05:00Z",
  "ttl_seconds": 300
}
```

### QUERY Message

```json
{
  "sender": "A-AUDITOR",
  "receiver": "A-ARCHITECT",
  "action": "QUERY",
  "payload": {
    "query": "Does F13 require human approval for tool generation?",
    "context": {
      "proposed_action": "agentzero_engineer",
      "risk_tier": "P0"
    }
  },
  "floors_active": ["F7", "F13"],
  "session_id": "session_001",
  "correlation_id": "corr_043",
  "timestamp": "2026-04-01T01:10:00Z",
  "ttl_seconds": 60
}
```

### REJECT Message

```json
{
  "sender": "A-AUDITOR",
  "receiver": "A-ENGINEER",
  "action": "REJECT",
  "payload": {
    "task_id": "task_042",
    "reason": "F9_TAQWA violation: proposed code allows shell injection",
    "floor": "F9",
    "suggestion": "Add input sanitization before code_engine call"
  },
  "floors_active": ["F9"],
  "session_id": "session_001",
  "correlation_id": "corr_044",
  "timestamp": "2026-04-01T01:15:00Z",
  "ttl_seconds": 300
}
```

---

## Constitutional Tagging

Every message MUST carry `floors_active` — the floors this message touches.

| Floor | When Active | Example |
|-------|-------------|---------|
| F1 AMANAH | Reversibility concerns | "This action cannot be undone" |
| F2 SIDDIQ | Truth/fact claims | "This implementation is verified" |
| F4 CLARITY | Entropy/reasoning | "Reasoning chain attached" |
| F7 HUMILITY | Uncertainty | "Confidence 0.6, needs review" |
| F9 TAQWA | Ethics/safety | "Checked for harm vectors" |
| F13 KHILAFAH | Human authority | "Requires human veto approval" |

---

## Delivery Guarantees

| Priority | Guarantee | Use Case |
|----------|-----------|----------|
| HIGH | At-least-once + retry | TASK, QUERY (need response) |
| MEDIUM | At-most-once | NOTIFY (informational) |
| LOW | Best-effort | ERROR (already failing) |

---

## Agent Registry Integration

The Wire Protocol uses `AgentRegistry` for routing:

```python
# Discover agent by capability
agents = agent_registry.discover(capability="code_implementation")

# Delegate task to specific agent
result = agent_registry.delegate(task=payload, to="A-ENGINEER")

# Register agent capability
agent_registry.register_capability(
    agent_id="A-ENGINEER",
    capability="code_implementation",
    floors=["F1", "F2", "F9"]
)
```

---

## Next Steps

1. **A-VALIDATOR** review and seal this protocol
2. **A-ENGINEER** implements `AgentMessageBus` in `core/state/`
3. **A-ARCHITECT** defines `capability` taxonomy for all agents
4. **A-ORCHESTRATOR** wired to use wire protocol for all delegation

---

**SEAL:** Provisional. Requires A-VALIDATOR review before execution.

*Ditempa Bukan Diberi* [ΔΩΨ|A-ARCHITECT]
