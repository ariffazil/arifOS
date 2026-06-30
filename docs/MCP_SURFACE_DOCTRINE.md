# MCP Surface Doctrine — One Capability, One Canonical Tool

> **Ratified 2026-06-30 by F13 SOVEREIGN.**
> **DITEMPA BUKAN DIBERI** — Forged, Not Given.

## The Rule

SDK aliases are for builders. MCP tools are for agents. Never expose builder convenience as agent affordance unless it reduces decision entropy.

## Why

Coder tools optimize for developer productivity. Agentic tools must optimize for machine decision clarity. These are opposite pressures.

- Inside SDK: `arif_forge_execute` → calls `arif_forge`. Useful. Harus.
- On agent-facing MCP: `arif_forge_execute` → appears as separate reality action. Dangerous. Makruh/haram depending on blast radius.

An agent seeing both `arif_forge` and `arif_forge_execute` must ask: Which is canonical? Which bypasses judgment? That is cognitive debt, not intelligence.

## Public Surface (Canonical 7)

| Tool | Stage | Role |
|------|-------|------|
| `arif_init` | 000 | Session bootstrap + identity |
| `arif_observe` | 111 | Evidence, vitals, repo map |
| `arif_think` | 333 | Reason, plan, critique |
| `arif_route` | 555 | Select organ/tool |
| `arif_judge` | 888 | Constitutional verdict |
| `arif_act` | 900 | Execute (requires SEAL) |
| `arif_seal` | 999 | Permanent VAULT999 record |

## Diagnostic Tools (expanded45 mode only)

Available when `ARIFOS_MCP_EXPOSE_DEV_TOOLS=true`:

- `arif_conformance_report` — 9-check substrate proof
- `arif_canary` — transport diagnostic
- `arif_ping`, `arif_schema_echo`, `arif_version_echo`, `arif_transport_echo`, `arif_initialize_probe`

## Hidden Aliases (callable, never advertised)

These remain dispatchable via `_CANONICAL_HANDLERS` for backward compatibility but are filtered from `tools/list`:

| Hidden Alias | Canonical Target |
|-------------|-----------------|
| `arif_session_init` | `arif_init` |
| `arif_sense_observe` | `arif_observe` |
| `arif_evidence_fetch` | `arif_fetch` |
| `arif_mind_reason` | `arif_think` |
| `arif_heart_critique` | `arif_critique` |
| `arif_reply_compose` | `arif_compose` |
| `arif_memory_recall` | `arif_memory` |
| `arif_gateway_connect` | `arif_bridge_connect` |
| `arif_ops_measure` | `arif_measure` |
| `arif_judge_deliberate` | `arif_judge` |
| `arif_vault_seal` | `arif_seal` |
| `arif_forge_execute` | `arif_forge` |
| `arif_explore` | `arif_observe` |
| `arif_kernel_intercept` | `arif_judge` |

## Agentic Fitness Formula

```
F = (Value × Adoption) / (Entropy × BlastRadius × CognitiveCost)
```

For exposed aliases:
- Value: low or duplicate
- Adoption: confusing split
- Entropy: high
- Fitness: poor

Aliases die from natural selection. Canonical tools survive.

## Implementation

- `arifosmcp/runtime/__main__.py` — `tools/list` handler filters by public surface + alias blocklist
- `arifosmcp/runtime/public_surface.py` — `CANONICAL_LONG_NAME_ALIASES` is the single source of truth
- `arifosmcp/runtime/pre_execution_gate.py` — `_SDK_LONG_NAME_ALIASES` resolves aliases to canonical names for `tools/call`
- `arifosmcp/runtime/tools.py` — `_CANONICAL_HANDLERS` contains both canonical and alias handlers (internal)

## Enforcement

- `tools/list` returns only public surface tools
- `tools/call` still resolves aliases via handler lookup (backward compat)
- New aliases must not be added to public surface without F13 ratification
- Execution aliases (blast_radius ≥ MEDIUM) are haram on public surface

---

**DITEMPA BUKAN DIBERI — The coder wants more handles; the agent needs fewer doors.**
