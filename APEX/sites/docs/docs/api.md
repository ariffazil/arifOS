---
id: api
title: MCP API Reference (L4 Tools)
sidebar_position: 3
description: JSON-RPC contracts, protocol negotiation, and canonical arifOS AAA MCP tool surface.
---

# MCP API Reference (The "Tools Menu")

If you are building an AI agent or connecting arifOS to an app like Claude Desktop, this page lists the 13 specific tools the AI is allowed to use. 

Unlike a normal API where tools just execute blindly, arifOS exposes a **"governed"** surface using the Model Context Protocol (MCP). This means every time the AI tries to use a tool, arifOS intercepts the request and runs it through the 13 constitutional safety gates before letting the action happen.

## Protocol versioning

- Current protocol: `2025-11-25`
- Supported versions: `2025-11-25`, `2025-03-26`
- Negotiated during `initialize`; one session must use one agreed version.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": {},
    "clientInfo": {"name": "client", "version": "1.0"}
  }
}
```

## JSON-RPC call shape

```json
{
  "jsonrpc": "2.0",
  "id": 42,
  "method": "tools/call",
  "params": {
    "name": "reason_mind",
    "arguments": {
      "query": "Is this deployment ready?",
      "session_id": "sess_abc"
    }
  }
}
```

## Canonical 13 Tools

The 13 MCP tools are organized into **8 Metabolic Tools** (core governance chain) and **5 Evidence Tools** (read-only support).

### 8 Metabolic Tools (000→999 Chain)

These tools form the constitutional metabolic loop:

| Tool | Icon | Stage | Purpose |
|:---|:---:|:---|:---|
| `anchor_session` | 🔥 | 000 INIT | Session ignition, defense scan |
| `reason_mind` | 🧠 | 333 REASON | AGI cognition, truth validation |
| `recall_memory` | 📚 | 444 PHOENIX | Memory retrieval via EUREKA Sieve |
| `simulate_heart` | ❤️ | 555 EMPATHY | Stakeholder impact analysis |
| `critique_thought` | ⚖️ | 666 ALIGN | Multi-model bias detection |
| `eureka_forge` | ⚒️ | 777 FORGE | Sandboxed execution with gates |
| `apex_judge` | 👑 | 888 APEX | Constitutional verdict synthesis |
| `seal_vault` | 🔒 | 999 SEAL | Tamper-evident ledger commitment |

> **F7 Humility Notice on VAULT999:** The ledger provides application-level tamper-evidence via Merkle chains and cryptographic hashes. It does not protect against root compromise of the database host or sovereign key theft. See [threat model](../governance#vault-security) for complete security boundaries.

### 5 Evidence Tools (Read-Only)

These tools provide evidence grounding without state changes:

| Tool | Icon | Purpose | Constitutional Role |
|:---|:---:|:---|:---|
| `search_reality` | 🔍 | Web evidence discovery | F2 Truth verification |
| `fetch_content` | 📄 | Content/document retrieval | Evidence gathering |
| `inspect_file` | 📁 | Filesystem inspection | F1 Amanah audit trail |
| `audit_rules` | 📋 | Governance health check | System verification |
| `check_vital` | 📈 | System telemetry | Operational monitoring |

## Resources and prompt

- Resource: `arifos://aaa/schemas`
- Resource: `arifos://aaa/full-context-pack`
- Prompt: `arifos.prompt.aaa_chain`

## Response envelope

All tool responses use the `UnifiedResponse` format:

### Public Fields (Always Present)

| Field | Type | Description |
|:---|:---|:---|
| `status` | string | `OK`, `ERROR`, `BLOCKED`, or `PENDING` |
| `session_id` | string | Constitutional session token |
| `stage` | string | Pipeline stage: `000`, `111`, `222`, `333`, `444`, `555`, `666`, `777`, `888`, `999` |
| `message` | string | Human-readable summary |
| `policy_verdict` | string | `SEAL`, `PARTIAL`, `SABAR`, `VOID`, or `888_HOLD` |
| `next_tool` | string \| null | Next tool to call, or `null` if complete |
| `data` | object | Stage-specific output (minimal, stable) |

### Constitutional Fields (Audit Trail)

| Field | Type | Description |
|:---|:---|:---|
| `_constitutional` | object | Governance metadata: floor scores, telemetry, tri-witness |

### Debug Fields (Optional)

| Field | Type | Description |
|:---|:---|:---|
| `_debug` | object | Full internal state (only if `debug=true`) |
| `_schema` | object | Schema versions for audit |

### Example Response

```json
{
  "status": "OK",
  "session_id": "sess_a1b2c3d4",
  "stage": "888",
  "message": "Constitutional verdict: SEAL",
  "policy_verdict": "SEAL",
  "next_tool": null,
  "data": {
    "result": "Action approved",
    "timestamp": "2026-03-01T12:00:00Z"
  },
  "_constitutional": {
    "floors": {
      "F1": 1.0,
      "F2": 0.99,
      "F4": -0.5,
      "F6": 0.72,
      "F7": 0.04
    },
    "telemetry": {
      "delta_s": -0.5,
      "peace_squared": 1.02,
      "kappa_r": 0.72
    },
    "verdict": "SEAL"
  }
}
```

### Verdict Behavior

*(Curious how these look in practice? [View the live Audit Dashboard](https://arifosmcp-truth-claim.pages.dev/))*

- **✅ `SEAL`** -> Approved (Continue)
- **🟡 `PARTIAL`** -> Approved with warnings
- **⚠️ `SABAR`** -> Blocked temporarily (AI must refine/retry)
- **❌ `VOID`** -> Blocked entirely (Rule violation)
- **🛑 `888_HOLD`** -> Blocked until a human cryptographically signs it
