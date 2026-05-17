---
id: api
title: MCP API Reference (L4 Tools)
sidebar_position: 3
description: JSON-RPC contracts, protocol negotiation, and the unified 8-tool arifOS public MCP surface.
---

# MCP API Reference

This page describes the public/main MCP contract. For the generated source-of-truth tool table and compatibility map, see [Public Contract](./public-contract).

## Protocol Versioning

- Current protocol: `2025-11-25`
- Supported versions: `2025-11-25`
- Negotiated during `initialize`

## JSON-RPC Call Shape

```json
{
  "jsonrpc": "2.0",
  "id": 42,
  "method": "tools/call",
  "params": {
    "name": "arifOS_kernel",
    "arguments": {
      "query": "Is this deployment ready?",
      "risk_tier": "medium",
      "actor_id": "operator"
    }
  }
}
```

## Tool Surface Is Layered

- Public profile (`ARIFOS_PUBLIC_TOOL_PROFILE=chatgpt` or `agnostic_public`): 8-tool model-facing contract
- Full profile (`ARIFOS_PUBLIC_TOOL_PROFILE=full`): internal/dev-only stage tools for diagnostics and orchestration

## Public Tool Interface

| Tool | Role |
|------|------|
| `arifOS_kernel` | One-call governed constitutional execution entrypoint |
| `search_reality` | External grounding and source discovery |
| `ingest_evidence` | Fetch/read evidence from URL sources |
| `session_memory` | Session context and reasoning artifact memory |
| `audit_rules` | Read-only constitutional audit surface |
| `check_vital` | Read-only runtime health surface |
| `open_apex_dashboard` | Opens the APEX Sovereign Dashboard |
| `bootstrap_identity` | Explicit onboarding and identity declaration |

## Internal / Dev-only Stage Tools

These names remain available only in internal/dev profiles:

- `init_anchor_state`
- `integrate_analyze_reflect`
- `reason_mind_synthesis`
- `assess_heart_impact`
- `critique_thought_audit`
- `quantum_eureka_forge`
- `apex_judge_verdict`
- `seal_vault_commit`

## Resources and Prompts

The server also exposes read-only resources and orchestration prompts. Use the generated contract page for the full list:

- [Public Contract](./public-contract)

## Response Envelope

Every public tool returns a `RuntimeEnvelope` carrying the stage, verdict, authority state, metrics, payload, errors, and meta blocks.
