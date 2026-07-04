# Architecture Separation — Protocol vs. Governance

> **Blindspot #5 response.** MCP and A2A are protocols. Governance is policy. Different layers.
> Updated: 2026-06-30 by FORGE (000Ω).

## The Clean Architecture

```
┌─────────────────────────────────────────────┐
│           APPLICATION LAYER                 │
│   (what you want to do — your business      │
│    logic, agents, user interfaces)          │
└─────────────────────┬───────────────────────┘
                      │ uses
                      ▼
┌─────────────────────────────────────────────┐
│           GOVERNANCE LAYER                  │
│   arifOS: 13 floors, 7 tools, audit log     │
│   (this is the ONLY part that's opinionated)│
└─────────────────────┬───────────────────────┘
                      │ enforces
                      ▼
┌─────────────────────────────────────────────┐
│           PROTOCOL LAYER                    │
│   MCP (tool discovery/call)                 │
│   A2A (agent-to-agent)                      │
│   (these are replaceable — protocols evolve)│
└─────────────────────┬───────────────────────┘
                      │ transports on
                      ▼
┌─────────────────────────────────────────────┐
│           TRANSPORT LAYER                   │
│   HTTP, stdio, Streamable HTTP, WebSockets  │
│   (network concerns only)                   │
└─────────────────────┬───────────────────────┘
                      │ runs on
                      ▼
┌─────────────────────────────────────────────┐
│           EXECUTION LAYER                   │
│   Python, Docker, VPS, your infra           │
└─────────────────────────────────────────────┘
```

## What This Means in Practice

### Protocols Evolve. Governance Shouldn't.

- MCP spec went from 2024 draft → 2025-11-25 stable.
- A2A spec went from 2024 → 2025 + working groups.
- New protocols WILL emerge (file uploads, events, registry cards).

**arifOS governance should work on top of ANY protocol.** If tomorrow we move to a new protocol, the 13 floors should still apply.

### The Separation Test

Ask: *"Does this code care about the specific protocol, or does it care about the rule?"*

**Protocol-aware code (replaceable):**
- `mcp_gate_v0.py` — knows MCP wire format
- `a2a_bridge.py` — knows Agent Card schema
- `transport/conformance_spine.py` — knows Streamable HTTP quirks

**Protocol-agnostic code (governance, keep forever):**
- `session.py` — actor binding
- `vault.py` — audit trail
- `gate.py` — irreversibility enforcement
- Floors F1-F13 definitions

### Current Leakages (needs fixing)

| Leakage | Location | Fix |
|---|---|---|
| Floor enforcement checks MCP-specific fields | `mcp_gate_v0.py` line 340+ | Extract to generic `check_floor(action_dict)` |
| `arif_judge` output format assumes MCP content[] | `tools/kernel_canonical.py` | Standardize on `verdict_dict` returned, format applied at protocol layer |
| `vault.py` stores MCP-specific metadata | `agents_66.py` | Generalize to `{action, actor, result, trace}` |
| 888 JUDGE has MCP-only error codes | `tools/` | Error codes in governance dict; protocol layer maps to JSON-RPC/HTTP |

### Protocol Plugability Test (not yet implemented)

After cleanup, arifOS should pass this test:

```python
# If we can swap MCP for Protocol X without touching governance code,
# the separation is clean.

from arifos.governance import check_floor, bind_session, seal_action
from arifos.protocol.mcp import mcp_adapter
from arifos.protocol.a2a import a2a_adapter

# Both adapters produce the same governance input shape
def handle_request(protocol_request, adapter):
    action = adapter.to_governance_shape(protocol_request)
    session = bind_session(action["actor_id"])
    verdict = check_floor(action, session)
    if verdict["status"] == "SEAL":
        result = execute(action)
        seal_action(action, result)
    return adapter.from_governance_shape(verdict, result)
```

If this test fails, fix the leakage first.

## Why This Matters

**Today's protocols (MCP, A2A) will be succeeded**, but good governance is timeless. Building governance coupled to protocol = rebuilding governance every time the protocol evolves.

Build governance ONCE. Plug it into any protocol.

---

**DITEMPA BUKAN DIBERI** — protocol is transport, governance is trust.
