# FEDERATION.md — arifOS Federation Architecture

> **DITEMPA BUKAN DIBERI** — Forged, Not Given.

## Overview

The arifOS Federation is a constitutional multi-agent system where governance is separated from execution. Agents propose, the kernel judges, humans approve, and A-FORGE executes. Every action produces a receipt in VAULT999.

```
                    ARIF (F13 SOVEREIGN)
                           │
                           ▼
                    Constitutional Kernel
                         (:8088)
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
      Capability       Discovery        State
        Plane           Plane           Plane
           │               │               │
           ▼               ▼               ▼
         FED              AAA          arifFlow
        (:7074)         (:3001)        (:7073)
           │               │               │
     ┌─────┴─────┐         │               │
     │           │         │               │
     ▼           ▼         ▼               ▼
  Agents     Organs    Registry        Receipts
```

## Three Planes

### 1. Capability Plane (FED :7074)

FED is the canonical MCP gateway. All agents connect to FED, and FED routes to organs.

**Why FED as gateway:**
- Single connection point for all agents
- Dynamic routing based on intent
- Provider management and fallback
- Cost tracking per agent

**Current state:** FED requires dual Accept headers (`application/json, text/event-stream`). Some agents don't send these.

**Target state:**
```
Agent → FED → GEOX/WEALTH/WELL/A-FORGE/etc.
```

### 2. Discovery Plane (AAA :3001)

AAA is the cockpit control plane. It exposes:

- `resource://capabilities` — what tools exist
- `resource://agents` — who can use them
- `resource://mcp_servers` — where they live
- `resource://roles` — what each role can see

**All agents query AAA first** to discover what's available.

### 3. State Plane (arifFlow :7073)

arifFlow is the metabolic ledger daemon. It exposes:

- `resource://receipts` — what happened
- `resource://active_agents` — who's running
- `resource://active_tasks` — what's being done
- `resource://governance_signals` — what the system learned
- `resource://federation_health` — overall health

**All agents emit state to arifFlow.** This creates the witness layer.

## Organs

| Organ | Port | Role | Authority |
|-------|------|------|-----------|
| arifOS | :8088 | Governance | JUDGE_ONLY |
| A-FORGE | :7071/:7072 | Execution | EXECUTE_AFTER_SEAL |
| GEOX | :8081 | Spatial | COMPUTE_ONLY |
| WEALTH | :18082 | Economic | COMPUTE_ONLY |
| WELL | :18083 | Wellbeing | REFLECT_ONLY |
| FRAME | :18085 | Witness | OBSERVE_ONLY |
| i-ARIF | :18095 | Synthesis | COMPUTE_ONLY |
| FED | :7074 | Gateway | ROUTING_ONLY |
| AAA | :3001 | Discovery | DISPLAY_ONLY |
| arifFlow | :7073 | State | METABOLIZE_ONLY |

## Forge Instruments (Agents)

| Agent | ID | Role | MCP Access |
|-------|-----|------|------------|
| OpenCode | FI-001 | Sovereign | Full (via FED) |
| Claude Code | FI-002 | Researcher | NONE (gap) |
| Qwen Code | FI-003 | Builder | Full (via HTTP) |
| Codex | FI-005 | Executor | NONE (gap) |
| Kimi Code | FI-008 | Builder | Full (via HTTP) |
| Hermes | hermes-prime | Governor | Partial (missing FED) |

## Role-Based Visibility

Roles determine what organs an agent can see:

| Role | Organs | Capabilities |
|------|--------|--------------|
| Researcher | GEOX, FRAME, i-ARIF | observe, compute, analyze |
| Builder | GEOX, A-FORGE | observe, compute, execute |
| Governor | FRAME, AAA, arifFlow | observe, judge, seal |
| Executor | A-FORGE | execute, mutate |
| Sovereign | All | All |

## Constitutional Chain

```
Agent proposes
      ↓
arif_judge (:8088)
      ↓
┌─────┴─────┐
│           │
SEAL       HOLD
│           │
▼           ▼
A-FORGE    Human
executes   decides
│           │
▼           ▼
Receipt    Decision
in VAULT999 recorded
```

## Key Doctrines

### Identity Before Action
Every session starts with `arif_init` — binding actor identity before any operation.

### Inventory Before Mutation
Every mutation requires evidence. The agent must observe before it can act.

### Executor Never Certifies
A-FORGE executes. It never judges. The kernel judges. Separation of powers.

### Witness Never Governs
FRAME observes. It never decides. The kernel decides. Separation of powers.

### Localhost Trust Model
All services bind `127.0.0.1` with no authentication. UFW blocks external access. Within the machine, trust is implicit.

## Gaps (Current)

| Gap | Severity | Fix |
|-----|----------|-----|
| Claude Code has ZERO MCP | CRITICAL | Wire to FED |
| Codex has ZERO MCP | CRITICAL | Wire to FED |
| OpenCode has zero MCP in config | CRITICAL | Wire to kernel |
| FED requires dual Accept headers | HIGH | Document or fix |
| arifFlow REST only | HIGH | Use stdio bridge |
| Hermes missing FED | MEDIUM | Add FED to config |

## Protocol Versions

| Protocol | Organs |
|----------|--------|
| 2024-11-05 | arifOS, GEOX, WEALTH, WELL, arifFlow |
| 2025-06-18 | A-FORGE, FED, FRAME, i-ARIF, AAA |

**Note:** Protocol upgrade (2024-11-05 to 2025-06-18) is deferred. Discovery debt > Protocol debt today.

## Canonical Registry

The single source of truth for all MCP servers is:

```
/root/AAA/registry/mcp-servers.yaml
```

All other configs are derived from this file.

## Related Documents

- [CONSTITUTION.md](./CONSTITUTION.md) — F1-F13 floors
- [FEDERATION_CONTRACT.md](./FEDERATION_CONTRACT.md) — Agent contracts
- [SECURITY.md](./SECURITY.md) — Threat model
- [CONTRIBUTING.md](./CONTRIBUTING.md) — Contribution guidelines

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given.
