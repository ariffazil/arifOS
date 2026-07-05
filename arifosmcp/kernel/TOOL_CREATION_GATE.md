# TOOL CREATION GATE — Mandatory Pre-Flight

> **Rule:** No agent may create a new tool without proving it doesn't already exist.
> **Enforced by:** YAML invariants + scar consultation + retrieval check.
> **Forged:** 2026-07-05 by FORGE (000Ω)

## The Gate (3 checks, all must pass)

### 1. RETRIEVAL CHECK
```
arif_retrieve_tools(query="<what the new tool would do>")
```
If any result has BM25 score > 5.0 → **STOP. That tool exists.**

### 2. YAML CHECK
```
check_registry_against_invariants(registered_names)
```
If `in_registered_not_yaml` is non-empty → **STOP. Unregistered tools already exist. Fix drift first.**

### 3. SCAR CONSULTATION
```
forge_scar(mode="consult", fingerprint="<new_tool_name>")
```
If a scar exists for this tool → **STOP. This tool was killed before. Read why.**

## Only After All 3 Pass

The agent may proceed to `forge_skill` or `forge_register` with:
- `intent` — why the new tool is needed
- `evidence` — what existing tools were checked
- `justification` — why none of them suffice

## Anti-Patterns

- ❌ "I need a tool for X" without searching
- ❌ Creating a tool that wraps an existing tool
- ❌ Creating a tool because the agent forgot the name of an existing one
- ❌ Creating a tool because the agent didn't read the description

## Where This Lives

- **AGENTS.md** — referenced in tool creation section
- **BOOTSTRAP.md** — loaded at session init
- **forge_skill** — enforced as pre-check
- **TOOL_INVARIANTS.yaml** — the source of truth for "what exists"

DITEMPA BUKAN DIBERI — The gate is forged, not assumed.
