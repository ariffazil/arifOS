---
id: mcp-server
title: MCP Server
sidebar_position: 2
description: Technical reference for the 13-tool arifOS public MCP runtime.
---

# arifOS MCP Server

> Public gateway: `https://mcp.arif-fazil.com/mcp`
> arifOS service endpoint: `https://arifos.arif-fazil.com/mcp`
> Runtime module: `arifosmcp`
> Current SOT: `https://arifos.arif-fazil.com/mcp-discovery-index.json`

arifOS is model-agnostic at the transport layer. MCP transports capability; arifOS governs capability through F1-F13, session binding, risk checks, human approval boundaries, and audit.

## Contract Policy

- Public contract: 13 canonical `arif_*` tools.
- Production transport: Streamable HTTP at `/mcp`.
- Local transport: stdio.
- Discovery index: `/mcp-discovery-index.json`.
- Runtime truth: `/api/federation-probe`.

## Public Interface

| Stage | Tool | Role |
|---|---|---|
| 000 | `arif_session_init` | Session and identity binding |
| 111 | `arif_sense_observe` | Reality observation and hybrid discovery |
| 222 | `arif_evidence_fetch` | Evidence retrieval with receipts |
| 333 | `arif_mind_reason` | Reasoning, planning, verification |
| 444 | `arif_heart_critique` | Risk, empathy, red-team critique |
| 555 | `arif_kernel_route` | Intent routing and topology |
| 444r | `arif_reply_compose` | Governed response composition |
| 555m | `arif_memory_recall` | Governed memory recall/store/list |
| 666g | `arif_gateway_connect` | Federation/A2A gateway |
| 888 | `arif_judge_deliberate` | Constitutional deliberation |
| 999 | `arif_vault_seal` | VAULT999 audit/seal surface |
| 666 | `arif_forge_execute` | Bounded execution/forge action |
| 777 | `arif_ops_measure` | Health, cost, telemetry |

## Governed Discovery

For orientation before action, use:

```text
arif_sense_observe(mode="compass")
```

This is read-only. `compass` uses `hybrid_discovery` for evidence retrieval, then adds capability, authority, risk, provenance, and next safe moves. It does not store memory, seal VAULT999, or issue final truth.

## Operator URLs

- MCP endpoint: `https://mcp.arif-fazil.com/mcp`
- Service endpoint: `https://arifos.arif-fazil.com/mcp`
- Health: `https://arifos.arif-fazil.com/health`
- Tools: `https://arifos.arif-fazil.com/tools`
- Discovery index: `https://arifos.arif-fazil.com/mcp-discovery-index.json`
