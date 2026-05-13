---
id: architecture
title: Architecture
sidebar_position: 6
description: The L0-L7 stack, 8-tool public MCP contract, internal/dev-only stage tools, Trinity engines, 13 constitutional floors, and the 000-999 metabolic loop.
---

# Architecture

arifOS keeps one public MCP contract and one internal execution layer:

- Public/main contract: 8 tools from `arifosmcp.runtime.public_registry`
- Internal/dev tools: stage tools used for orchestration, diagnostics, and compatibility profiles

This split keeps the system model-agnostic without forcing LLM clients to pick between overlapping names for the same operation.

## The 8-Layer Stack

```text
L7: ECOSYSTEM   - permissionless sovereignty
L6: INSTITUTION - organizational governance
L5: AGENTS      - role-based orchestration
L4: TOOLS       - 8 public MCP tools + internal stage tools
L3: WORKFLOW    - 000-999 metabolic workflows
L2: SKILLS      - ARIF-aligned verbs
L1: PROMPTS     - entry surfaces and orchestration prompts
L0: KERNEL      - Delta/Omega/Psi governance + 13 floors + VAULT999
```

## Public/main Contract

| Tool | Role |
|:--|:--|
| `arifOS_kernel` | One-call governed constitutional execution entrypoint |
| `search_reality` | External grounding and source discovery |
| `ingest_evidence` | Evidence fetch and intake |
| `session_memory` | Governed memory operations |
| `audit_rules` | Constitutional audit |
| `check_vital` | Runtime health and telemetry |
| `open_apex_dashboard` | Observability dashboard |
| `bootstrap_identity` | Explicit onboarding and identity declaration |

For the generated tool table and compatibility map, see [Public Contract](./public-contract).

## Internal / Dev-only Stage Tools

These tools remain available only for internal/dev profiles:

- `init_anchor_state`
- `integrate_analyze_reflect`
- `reason_mind_synthesis`
- `assess_heart_impact`
- `critique_thought_audit`
- `quantum_eureka_forge`
- `apex_judge_verdict`
- `seal_vault_commit`

## Boundary Rule

- `core/` contains decision logic and floors
- `arifosmcp.runtime/` exposes the public contract
- `arifosmcp.transport/` handles transport mechanics only

The public contract must stay stable even when internal stage tools evolve.

## Transports

| Transport | Command | Best for |
|:--|:--|:--|
| `stdio` | `python -m arifosmcp.runtime stdio` | Local IDE and desktop clients |
| `http` | `python -m arifosmcp.runtime http` | Production and hosted MCP clients |

## Metabolic Loop

The public kernel still executes the governed 000→999 path internally:

`000_INIT -> 111_SENSE -> 222_REALITY -> 333_MIND -> 555_MEMORY -> 666_HEART/CRITIQUE -> 777_FORGE -> 888_JUDGE -> 999_VAULT`

The point of the reduced public contract is not to remove these stages. It is to stop exposing every internal stage as a separate public choice.
