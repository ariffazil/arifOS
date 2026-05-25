# REPO_ROLE_MAP.md — arifOS Federation Canonical Role Map
> **Canonical Source of Truth:** `ariffazil/arifOS`
> **Authority:** arifOS F13 SOVEREIGN (Muhammad Arif bin Fazil)
> **Purpose:**消除命名混沌 / Remove naming chaos. Every agent and repo must use canonical names.

---

## Canonical Repository Table

| Display Name | GitHub Repo | Runtime Path | Role | Does NOT Own |
|-------------|-------------|-------------|------|--------------|
| **arifOS** | `ariffazil/arifOS` | `/root/arifOS` | Constitutional Kernel — F1-F13, 888_JUDGE, VAULT999, floors, memory, A2A routing | Execution, earth evidence, capital logic, vitality |
| **AAA** | `ariffazil/AAA` | `/root/AAA` | Control Plane — cockpit, A2A mesh, operator visibility, agent registry | Constitutional judgment, execution engine |
| **A-FORGE** | `ariffazil/A-FORGE` | `/root/A-FORGE` | Execution Shell — vision, build, deploy, artifact forging | Constitutional judgment, sovereign veto |
| **GEOX** | `ariffazil/geox` | `/root/geox` | Earth Intelligence — geoscience, petrophysics, seismic, physics evidence | Final policy judgment, seal authority |
| **WEALTH** | `ariffazil/wealth` | `/root/WEALTH` | Capital Intelligence — financial logic, resource allocation, thermodynamic scoring | Constitutional judgment |
| **WELL** | `ariffazil/well` | `/root/WELL` | Vitality Intelligence — human bio-telemetry, machine substrate, coupled readiness | Constitutional judgment |
| **APEX** | `ariffazil/arifOS` (subdir) | `/root/APEX` | Verdict Engine — 888_JUDGE deliberation, cross-organ consensus | Tool execution, earth evidence |
| **HERMES** | `ariffazil/AAA` (agent) | — | ASI Relay — deliberative agent judgment | — |

## Naming Rules

| Form | Use For | Example |
|------|---------|---------|
| `arifOS` | Display name, docs, human-facing | "arifOS constitutional kernel" |
| `arifOS` (capital OS) | Brand, titles | "arifOS Federation" |
| `arifOS` | Package imports, Python | `import arifosmcp` |
| `arifOS` | MCP server name | `arifOS MCP Server` |
| `arifOS` | GitHub org | `https://github.com/ariffazil/arifOS` |
| `/root/arifOS` | Local runtime path | `cd /root/arifOS` |

### Case Variations to Avoid

| ❌ Wrong | ✅ Correct |
|---------|-----------|
| `arifos` (lowercase) | `arifOS` |
| `ARIFOS` (all caps) | `arifOS` |
| `/root/arifOS` in code vs `/root/arifOS` | Always `/root/arifOS` |
| `WEALTH` in docs | `WEALTH` (all caps is fine for organ name) |
| `well` | `WELL` (organ name, all caps) |
| `geox` (lowercase) | `GEOX` |

## Protocol Authority Boundaries

```
Arif (F13 SOVEREIGN)
    └── arifOS (Constitutional Kernel)
            ├── AAA (Control Plane — cockpit, not constitution)
            ├── A-FORGE (Execution — builds, does not judge)
            ├── GEOX (Earth Evidence — prepares, does not verdict)
            ├── WEALTH (Capital — tracks, does not spend irreversibly)
            └── WELL (Vitality — measures, does not decide)
```

## Key Invariants

1. **arifOS is the only repo that defines F1-F13 floors.**
2. **arifOS is the only repo with 888_JUDGE, VAULT999, and memory layers.**
3. **No repo may claim to be "the constitution" or "sovereign" unless it is arifOS.**
4. **A-FORGE REPO_CONSTITUTION.md is a FEDERATION_EXECUTION_CHARTER — not the sovereign constitution.**
5. **WELL server.py is operational. arifOS README "WELL → disabled" claim is stale. See FEDERATION_STATUS.md.**

## Alias Registry (Known)

| Alias | Points To | Class | Notes |
|-------|----------|-------|-------|
| `hermes-workspace` | `AAA/agents/hermes-asi` | INTERNAL | Hermes deliberative agent runtime |
| `openclaw-workspace` | `AAA/workspace` | INTERNAL | OpenClaw operator workspace |
| `arif-identity-broker` | experimental | NOT CANONICAL | Untracked experiment |

## Multi-Client MCP Session Rule

> **CRITICAL (PHOENIX-73C):**
> The MCP SDK `streamable-http` transport uses a singleton SSE stream key.
> Only ONE SSE client can hold the `/mcp` GET stream at a time per server instance.
> - Kimi + OpenCode simultaneous connect → 409 Conflict
> - Fix: Use POST-based JSON-RPC, or implement reconnection with backoff
> - arifOS runs `stateless_http=True` — GET SSE is disabled by design in stateless mode
> - MCP clients that auto-negotiate SSE may still attempt GET
