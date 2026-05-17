---
id: intro
title: Introduction
slug: /intro
sidebar_position: 1
description: arifOS is a constitutional intelligence kernel with an 8-tool public MCP contract and governed 000->999 pipeline.
---

# arifOS - DITEMPA, BUKAN DIBERI

*The system that knows because it admits what it cannot know.*

arifOS is a constitutional safety kernel that sits between an LLM and real-world tools. It enforces 13 floors of law before any governed action is allowed to proceed.

## The Execution Model

When you call `bootstrap_identity` or `arifOS_kernel`, arifOS does not merely run a tool. It boots the constitutional kernel:

1. It loads floor constraints and policy guards.
2. It binds runtime state and continuity rules.
3. It routes all governed work through the 000→999 metabolic path instead of allowing direct bypass.

## Canonical Runtime

- Python: `>=3.12`
- Module: `arifosmcp.runtime`
- Transports: `stdio`, `http`
- Public MCP surface: 8 tools
- Internal stage tools: internal/dev-only
- MCP protocol: `2025-11-25`

## Public Runtime Tools

1. `arifOS_kernel`
2. `search_reality`
3. `ingest_evidence`
4. `session_memory`
5. `audit_rules`
6. `check_vital`
7. `open_apex_dashboard`
8. `bootstrap_identity`

These 8 names are the only supported public/main contract for model-agnostic clients. Legacy names and stage tools should not be treated as public API.

For the generated tool table and compatibility mapping, see [Public Contract](./public-contract).

## Quick Start

```bash
pip install arifosmcp

# Local clients
python -m arifosmcp.runtime stdio

# Production HTTP
HOST=0.0.0.0 PORT=8080 python -m arifosmcp.runtime http
```

Live endpoints:

- MCP HTTP: `https://arifosmcp.arif-fazil.com/mcp`
- Dashboard: `https://arifosmcp.arif-fazil.com/dashboard/`
- Health: `https://arifosmcp.arif-fazil.com/health`

## Governance Verdicts

- `SEAL` — Approved
- `PARTIAL` — Approved with constraints
- `SABAR` — Hold and refine
- `VOID` — Hard block
- `888_HOLD` — Human ratification required
