# README Reality Audit — 2026-07-13

## Scope

This audit validates README operational claims against live arifOS endpoints and live MCP discovery behavior.

## Evidence Sources

- Live health: https://arifos.arif-fazil.com/health
- Live MCP gateway: https://mcp.arif-fazil.com/mcp
- Live tools list (JSON-RPC `tools/list` at gateway)
- Observatory MCP manifest: https://arifos.arif-fazil.com/.well-known/mcp.json
- Observatory agent card: https://arifos.arif-fazil.com/.well-known/agent-card.json
- Public repos: arifOS, A-FORGE, AAA

## Validation Results

### PASS (validated against live runtime)

1. Live kernel health endpoint is reachable and healthy.
   - Evidence: `/health` reports `status=healthy`.
2. Live transport endpoint is streamable HTTP at `https://mcp.arif-fazil.com/mcp`.
3. Live default MCP wire surface currently exposes 8 tools.
   - Evidence from live `tools/list`: `arif_forge`, `arif_init`, `arif_judge`, `arif_memory`, `arif_observe`, `arif_route`, `arif_seal`, `arif_think`.
4. Runtime branch/release indicators align with live service state.
   - Evidence: `/health` reports `git_branch=main`, `release_nam=v2026.07.09-SPINE-P0`.
5. Critical public links are reachable (`200`):
   - `https://arifos.arif-fazil.com/health`
   - `https://mcp.arif-fazil.com/mcp`
   - `https://arifos.arif-fazil.com/.well-known/mcp.json`
   - `https://arifos.arif-fazil.com/.well-known/agent-card.json`
   - `https://aaa.arif-fazil.com`
   - `https://github.com/ariffazil/arifos`
   - `https://github.com/ariffazil/A-FORGE`
   - `https://github.com/ariffazil/AAA`
   - `https://pypi.org/project/arifos/`

### DRIFT (live mismatch found)

1. Manifest vs live wire tool count mismatch.
   - `/health` and live `tools/list`: 8 tools.
   - `/.well-known/mcp.json`: `tools_summary.total=7`.

### DOCTRINAL / NOT DIRECTLY MACHINE-VERIFIABLE

The following claim classes are philosophical/constitutional declarations and were preserved but not machine-proved in this audit:

- Sovereign doctrine and constitutional narrative language.
- Semantic interpretation claims about APEX/AGI substrate role boundaries.
- Normative policy statements (must/never) that require governance review rather than endpoint probing.

## README Changes Applied

README was updated to reflect live runtime truth while preserving doctrine:

1. Added a Reality Context section with operator/institution links.
2. Declared live default wire surface as 8 tools (verified 2026-07-13).
3. Reframed tool-surface section to distinguish:
   - Live wire truth (`/health` + `tools/list`)
   - Canonical doctrine file (`PUBLIC_SURFACE_CANON.md`)
4. Removed contradictory numeric claims (7/45/75 counts).
5. Updated final summary line to live 8-tool wire state.

## Residual Recommendation

To fully close drift, update observatory discovery metadata so `/.well-known/mcp.json` tool totals match the current live wire mode.
