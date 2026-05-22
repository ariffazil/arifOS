---
type: Concept
tier: 20_RUNTIME
strand:
- integration
audience:
- engineers
difficulty: intermediate
prerequisites:
- MCP_Tools
- Metabolic_Loop
tags:
- integration
- mcp
- patterns
- deployment
- architecture
sources:
- docs/integration_patterns.md
- docs/protocols/WEBMCP_ARCHITECTURE.md
last_sync: '2026-04-10'
confidence: 0.9
---

# Integration Patterns

arifOS is designed as a **constitutional kernel**, not a standalone application. It integrates with existing AI ecosystems through the Model Context Protocol (MCP), providing governance as a service layer. This document describes the key patterns for integrating arifOS with ChatGPT, Claude, IDEs, automation platforms, and custom applications.

> **Core Principle:** arifOS reduces AI risk by making every decision inspectable, reversible where possible, and bounded by explicit constitutional rules.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         arifOS MCP SERVER                               │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   @tool()   │  │ @resource() │  │  @prompt()  │  │  @image()   │    │
│  │   (Tools)   │  │ (Resources) │  │  (Prompts)  │  │   (Media)   │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │           │
│         └────────────────┴────────────────┴────────────────┘           │
│                              │                                          │
│                    ┌─────────┴─────────┐                                │
│                    │  Constitutional   │                                │
│                    │  Governance Layer │                                │
│                    │   (F1-F13 Floors) │                                │
│                    └─────────┬─────────┘                                │
│                              │                                          │
│         ┌────────────────────┼────────────────────┐                    │
│         ▼                    ▼                    ▼                    │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│  │  9+1 Tools  │     │   VAULT999  │     │  External   │              │
│  │  (Think)    │     │   Storage   │     │  Services   │              │
│  └─────────────┘     └─────────────┘     └─────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
       ┌────────────┐       ┌────────────┐       ┌────────────┐
       │  ChatGPT   │       │   Claude   │       │   IDEs     │
       │   (Apps)   │       │  (Desktop) │       │(Cursor/etc)│
       └────────────┘       └────────────┘       └────────────┘
```

---

## Pattern 1: ChatGPT Apps Integration

ChatGPT connects to arifOS through the **MCP HTTP transport**, enabling constitutional governance for custom GPTs.

### Configuration

```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://arifosmcp.arif-fazil.com/mcp"
    }
  }
}
```

### Available Tools (Phase 1 — Read-Only)

| Tool | Mode | Purpose | Floors Active |
|------|------|---------|---------------|
| `arifos_judge` | `health` | Constitutional health check | All F1-F13 |
| `arifos_vault` | `render` | Render seal widget in ChatGPT UI | F1, F11 |
| `arifos_vault` | `list` | Read recent verdicts (last 100) | F11 |

### Safety: 888_HOLD Compliance

Phase 1 is intentionally **read-only**:
- ❌ No vault write access from ChatGPT
- ❌ No VPS execution paths exposed
- ❌ No private keys in ChatGPT-facing container

### Widget Integration

The vault seal widget displays:
- Truth Score (F2)
- Humility Level (F7)
- Entropy Delta (F4)
- Harmony Ratio (F5)
- Reality Index (F6)
- Witness Strength (F3)

```
┌─────────────────────────────────────────┐
│         arifOS SEAL WIDGET            │
├─────────────────────────────────────────┤
│  Status: ✅ HEALTHY                   │
│  Verdict: SEAL                        │
│                                        │
│  F2 Truth:      99.5%     ████████░░  │
│  F7 Humility:   4%        ████░░░░░░  │
│  F4 Entropy:   -0.36      ███████░░░  │
│  F5 Peace²:     1.22      ████████░░  │
│                                        │
│  G★ Score: 0.91 (Excellent)           │
└─────────────────────────────────────────┘
```

---

## Pattern 2: Claude Desktop Integration

Claude Desktop uses **MCP stdio transport** for local arifOS integration.

### Configuration (claude_desktop_config.json)

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "arifosmcp.server"],
      "env": {
        "ARIFOS_MODE": "constitutional",
        "VAULT_PATH": "~/.arifos/vault"
      }
    }
  }
}
```

### Stdio Transport Advantages

| Feature | Benefit |
|---------|---------|
| Local execution | No network latency |
| Full tool access | All 9+1 tools available |
| Direct vault access | Read/write to local VAULT999 |
| Custom configuration | Environment-specific settings |

### Example Invocation

```python
# From Claude Desktop, the user can invoke:
"@arifos Check the constitutional health of my current session"

# arifOS responds with:
{
  "verdict": "SEAL",
  "floors_active": ["F1", "F2", "F3", "F9", "F10", "F12", "F13"],
  "telemetry": {
    "ds": -0.32,
    "peace2": 1.21,
    "G_star": 0.91,
    "confidence": 0.08
  },
  "system_status": "HEALTHY"
}
```

---

## Pattern 3: IDE Integration (Cursor, Windsurf, etc.)

IDEs integrate arifOS as a **governance layer** for AI-assisted coding.

### Setup

```json
// .cursor/mcp.json
{
  "mcpServers": {
    "arifos": {
      "url": "http://localhost:3000/mcp"
    }
  }
}
```

### Governance for Code Generation

When IDE AI generates code, arifOS checks:

| Floor | Check | Example |
|-------|-------|---------|
| F1 | Reversibility | Can this code change be reverted? |
| F2 | Truth | Does the code match the documented behavior? |
| F4 | Clarity | Is the generated code readable? |
| F7 | Humility | Does the AI admit uncertainty about edge cases? |
| F9 | Ethics | No malicious code patterns |
| F11 | Auditability | Changes logged to vault |

### Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   IDE AI    │ →   │   arifOS    │ →   │   Verdict   │
│  Generates  │     │   Checks    │     │   (SEAL/   │
│    Code     │     │   F1-F13    │     │    VOID)    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                        ┌─────┴─────┐
                                        ▼           ▼
                                   ┌────────┐  ┌────────┐
                                   │ Accept │  │ Reject │
                                   │  Code  │  │ + Log  │
                                   └────────┘  └────────┘
```

---

## Pattern 4: n8n / Automation Platform Integration

arifOS provides **governance as a webhook** for workflow automation.

### Webhook Configuration

```
URL: https://arifosmcp.arif-fazil.com/webhook/judge
Method: POST
Headers:
  Authorization: Bearer {token}
  Content-Type: application/json
```

### Request Format

```json
{
  "session_id": "n8n-workflow-123",
  "intent": "Process customer data for marketing campaign",
  "action_type": "data_processing",
  "data_classification": "PII",
  "proposed_action": {
    "tool": "send_email",
    "parameters": {
      "to": "{{ $json.customer_email }}",
      "template": "marketing_v2"
    }
  }
}
```

### Response Handling

| Verdict | n8n Action |
|---------|-----------|
| **SEAL** | Proceed with workflow |
| **VOID** | Halt workflow, alert admin |
| **888_HOLD** | Pause workflow, await human approval |
| **SABAR** | Retry with modified parameters |

### Example n8n Workflow

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Trigger │ →  │ arifOS  │ →  │  Gate   │ →  │  Action │
│ (Event) │    │  Judge  │    │ (Switch)│    │ (SEAL)  │
└─────────┘    └─────────┘    └────┬────┘    └─────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              ┌─────────┐    ┌─────────┐    ┌─────────┐
              │  SEAL   │    │  VOID   │    │  HOLD   │
              │ (Proceed)│   │ (Alert) │    │ (Wait)  │
              └─────────┘    └─────────┘    └─────────┘
```

---

## Pattern 5: Multi-Server Federation

Multiple arifOS instances can federate for **distributed governance**.

### Federation Topology

```
┌─────────────────────────────────────────────────────────────┐
│                    FEDERATION MESH                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐        ┌─────────────┐                   │
│   │  arifOS     │◄──────►│  arifOS     │                   │
│   │  (VPS-1)    │  A2A   │  (VPS-2)    │                   │
│   │  Singapore  │        │  Frankfurt  │                   │
│   └──────┬──────┘        └──────┬──────┘                   │
│          │                      │                           │
│          └──────────┬───────────┘                           │
│                     │                                       │
│                     ▼                                       │
│              ┌─────────────┐                                │
│              │   arifOS    │                                │
│              │  (Primary)  │                                │
│              │   (Judge)   │                                │
│              └─────────────┘                                │
│                     │                                       │
│         ┌───────────┼───────────┐                           │
│         ▼           ▼           ▼                           │
│    ┌─────────┐ ┌─────────┐ ┌─────────┐                     │
│    │  GEOX   │ │  APEX   │ │  A-FORGE│                     │
│    │ (Earth) │ │ (Soul)  │ │ (Body)  │                     │
│    └─────────┘ └─────────┘ └─────────┘                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### A2A (Agent-to-Agent) Protocol

Federated arifOS instances communicate via the **ASF-1 Protocol**:

```json
{
  "asf_version": "1.0",
  "header": {
    "from": "arifos-sg-001",
    "to": "arifos-primary",
    "mode": "judge_delegate"
  },
  "decision_vector": {
    "emv": 0.74,
    "npv_safety": 0.68,
    "entropy_delta": -0.12,
    "safety": "green"
  },
  "payload": {
    "action": "cross_border_data_transfer",
    "risk_class": "high",
    "witness_scores": {
      "human": 0.9,
      "ai": 0.95,
      "earth": 0.88
    }
  }
}
```

### Witness Consensus (W⁴)

For federated decisions, arifOS computes **Quad-Witness** consensus:

```
W₄ = (H × A × E × V)^(1/4) ≥ 0.75

Where:
H = Human witness (authority × presence)
A = AI witness (constitutional compliance)
E = Earth witness (thermodynamic bounds)
V = Vault-Shadow witness (historical consistency)
```

---

## Pattern 6: Custom Application Integration

Embed arifOS directly into applications via the **Python SDK**.

### Installation

```bash
pip install arifosmcp
```

### Basic Usage

```python
from arifosmcp import ConstitutionalGuard, SessionManager

# Initialize session
session = await SessionManager.create(
    session_id="my-app-123",
    intent="Process user query with governance"
)

# Create constitutional guard
guard = ConstitutionalGuard()

# Validate action
verdict = await guard.validate_reasoning(
    query=user_query,
    session=session,
    floors=["F1", "F2", "F9"]  # Safety, Truth, Ethics
)

if verdict.status == "SEAL":
    result = await process_query(user_query)
else:
    result = {"error": verdict.reason, "verdict": verdict.status}
```

### Response Structure

All arifOS responses follow the **4-layer structure**:

```json
{
  "machine": {
    "status": "ok",
    "latency_ms": 45,
    "version": "2026.04.08"
  },
  "governance": {
    "verdict": "SEAL",
    "floors_passed": 13,
    "attestation": "ATT-1736939400"
  },
  "intelligence": {
    "result": {...},
    "uncertainty": 0.04,
    "confidence": 0.96
  },
  "audit": {
    "session_id": "sess-abc123",
    "chain_hash": "sha256:..."
  }
}
```

---

## Transport Selection Guide

Choose the right transport for your use case:

| Use Case | Transport | Port | Security | Latency |
|----------|-----------|------|----------|---------|
| Claude Desktop | stdio | N/A | High | Low |
| Cursor IDE | stdio | N/A | High | Low |
| Local Dev | SSE | 3000 | Medium | Low |
| Production VPS | HTTP/S | 443 | High | Medium |
| n8n Integration | HTTP + Webhook | 3000 | Medium | Medium |
| Multi-Server Federation | HTTP/SSE | 8080 | High | Higher |
| Browser Client | SSE | 3000 | Medium | Low |
| Mobile App | HTTP/S | 443 | High | Variable |

---

## Error Handling Integration

### Verdict-Based Error Handling

```python
async def handle_arifos_response(verdict):
    match verdict.status:
        case "SEAL":
            return await proceed_with_action()
        case "VOID":
            log_security_event(verdict.violation_floor)
            raise ConstitutionalViolation(verdict.reason)
        case "888_HOLD":
            await notify_admin(verdict.escalation_id)
            return await wait_for_human_approval()
        case "SABAR":
            return await retry_with_modifications()
```

### Retry Strategies

| Verdict | Retryable? | Strategy |
|---------|-----------|----------|
| SEAL | N/A | Proceed |
| VOID | ❌ No | Log and alert |
| 888_HOLD | ✅ Yes | Poll for human decision |
| SABAR | ✅ Yes | Modify request, retry once |

---

## Security Considerations

### 888_HOLD Gate

All high-risk operations require human approval:

- Irreversible actions (F1 violation risk)
- High dark-cleverness scores (F9 threshold >0.30)
- Cross-border data transfers
- Constitutional amendments
- Production deployments

### Data Flow Security

```
User Input
    ↓
[Input Sanitization] ← F12 (Resilience)
    ↓
[Privacy Check] ← F7 (Privacy/PII detection)
    ↓
[Ethics Filter] ← F2, F9 (Truth, Ethics)
    ↓
arifOS Processing
    ↓
[Output Validation] ← F4 (Clarity)
    ↓
User Output
```

---

## Best Practices

### 1. Always Check Verdicts

```python
# ❌ Wrong
result = await arifos_mind(query)
return result

# ✅ Right
verdict = await arifos_judge(action)
if verdict.status == "SEAL":
    return await execute(action)
else:
    return handle_governance_block(verdict)
```

### 2. Log All Decisions

```python
# All arifOS calls automatically log to VAULT999
# But you should also log in your application:
logger.info("arifOS verdict", extra={
    "verdict": verdict.status,
    "floors_checked": verdict.floors_checked,
    "session_id": session.id
})
```

### 3. Respect the Humility Band

When arifOS returns uncertainty Ω₀ > 0.05, treat outputs as estimates:

```python
if result.uncertainty > 0.05:
    display_label = "Estimate Only"
else:
    display_label = "Verified"
```

---

## Summary

| Integration | Best For | Key Pattern |
|-------------|----------|-------------|
| **ChatGPT Apps** | Consumer AI with governance | Read-only health checks, widget rendering |
| **Claude Desktop** | Professional AI assistance | Full stdio access, local vault |
| **IDEs** | Code generation governance | Inline checks, pre-commit hooks |
| **n8n** | Workflow automation | Webhook judges, conditional gates |
| **Federation** | Enterprise distributed systems | A2A protocol, W⁴ consensus |
| **Custom Apps** | Embedded governance | Python SDK, 4-layer responses |

**Remember:** arifOS is not an app — it's a kernel. It provides the constitutional foundation upon which safe AI applications are built.

---

**Related:** [[MCP_Tools]] | [[Metabolic_Loop]] | [[Concept_Deployment_Architecture]] | [[ToolSpec_arifos_judge]]
