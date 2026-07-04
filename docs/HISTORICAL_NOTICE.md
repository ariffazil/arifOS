# HISTORICAL NOTICE — Tool Name Migration (2026-07-03)

> **DITEMPA BUKAN DIBERI**

## What Changed

On 2026-07-03, the arifOS federation completed a canonical tool name migration:

| Old Name (deprecated) | New Name (canonical) | Stage |
|----------------------|---------------------|-------|
| `arif_judge_deliberate` | `arif_judge` | 888 — Constitutional verdict |
| `arif_vault_seal` | `arif_seal` | 999 — Immutable ledger append |
| `arif_forge_execute` | `arif_act` | 900 — Execute approved plans |
| `arif_session_init` | `arif_init` | 000 — Session bootstrap |
| `arif_kernel_route` | `arif_route` | 555 — Intent routing |
| `arif_ops_measure` | `arif_observe` (vitals mode) | 777 — Health/telemetry |
| `arif_gateway_connect` | `arif_route` (organ param) | 666g — Federation bridge |
| `arif_memory_recall` | `arif_memory_recall` | 555m — (unchanged) |

## Why

The old names were verbose, inconsistent, and didn't follow the `arif_<verb>` pattern established by the heptalogy. The new names are shorter, consistent, and match the MCP tool surface exposed at `:8088`.

## What This Means for Historical Docs

Files in this `docs/` directory (and subdirectories) were written **before** the migration. They reference the old tool names because those were the correct names at the time of writing.

**These files are historical records.** They describe the system as it WAS, not as it IS.

- **Do NOT** update these files to use new names — that would rewrite history
- **Do NOT** treat old tool names as current — they will 404 on live MCP
- **DO** refer to `/root/AGENTS.md` or `arifosmcp/AGENTS.md` for current tool names

## Current Tool Surface

For the live, canonical tool surface, see:
- `arif_init` → `arif_judge` → `arif_seal` (golden path)
- Full tool list: `curl -s http://localhost:8088/health` or `arif_retrieve_tools(query="*")`

---

*Sealed: 2026-07-03 by FORGE (000Ω)*
