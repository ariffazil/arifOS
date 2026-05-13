---
id: mcp-server
title: MCP Server
sidebar_position: 2
description: Technical reference for the unified 8-tool arifOS public MCP runtime.
---

# arifOS MCP Server

> Registry ID: `io.github.ariffazil/arifos-mcp`
> Live base URL: `https://arifosmcp.arif-fazil.com`
> Runtime module: `arifosmcp.runtime`
> Version: `2026.03.12-SEAL`

arifOS is model-agnostic at the transport layer. The public contract is intentionally small so LLM clients do not need to choose between overlapping stage tools, legacy aliases, and profile-specific shims.

## Contract Policy

- Primary entrypoint: `python -m arifosmcp.runtime`
- Public/main contract: 8 tools only
- Internal/dev tools: stage tools remain available only in internal profiles
- Production transport: Streamable HTTP at `/mcp`
- Local transport: stdio
- Protocol: `2025-11-25`

The generated source-of-truth contract lives here:

- [Public Contract](./public-contract)

## Launch Commands

```bash
# Local stdio
python -m arifosmcp.runtime stdio

# Production HTTP
HOST=0.0.0.0 PORT=8080 python -m arifosmcp.runtime http
```

## Public Interface

The only supported model-facing tool names are:

| Tool | Role |
|------|------|
| `arifOS_kernel` | One-call governed constitutional execution entrypoint |
| `search_reality` | External grounding and source discovery |
| `ingest_evidence` | Read-only evidence fetch/intake |
| `session_memory` | Session context and reasoning artifact memory |
| `audit_rules` | Read-only constitutional rule audit |
| `check_vital` | Read-only health and telemetry snapshot |
| `open_apex_dashboard` | APEX dashboard surface |
| `bootstrap_identity` | Explicit onboarding and identity declaration |

## Internal / Dev-only Stage Tools

These tools remain available only for internal/dev orchestration and should not be treated as the public API:

- `init_anchor_state`
- `integrate_analyze_reflect`
- `reason_mind_synthesis`
- `assess_heart_impact`
- `critique_thought_audit`
- `quantum_eureka_forge`
- `apex_judge_verdict`
- `seal_vault_commit`

Legacy aliases such as `metabolic_loop_router` are compatibility-only. Public clients should use `arifOS_kernel`.

## Resources and Prompts

The server exposes read-only resources and orchestration prompts for LLMs. The exact list is generated from runtime source:

- [Public Contract](./public-contract)

## Operator URLs

- MCP endpoint: `https://arifosmcp.arif-fazil.com/mcp`
- Health: `https://arifosmcp.arif-fazil.com/health`
- Dashboard: `https://arifosmcp.arif-fazil.com/dashboard/`
