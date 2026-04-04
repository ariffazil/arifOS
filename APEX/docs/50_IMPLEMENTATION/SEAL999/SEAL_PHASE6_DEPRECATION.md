# Phase 6 Seal — Deprecation Cutover

Date: 2026-02-23
Branch: `forge/aaa-mcp-v13-safe`

## Outcome

Legacy public entrypoints are deprecated; canonical AAA surface is authoritative.

## Changes

1. FastMCP project config now targets AAA surface
   - `fastmcp.json` source path → `arifos_aaa_mcp/server.py`
   - `prod.fastmcp.json` source path → `arifos_aaa_mcp/server.py`
   - `dev.fastmcp.json` source path → `arifos_aaa_mcp/server.py`

2. Legacy package reduced to compatibility facade
   - `aaa_mcp/__init__.py` exports only `mcp` eagerly.
   - Legacy tool symbols are available via `__getattr__` with DeprecationWarning.
   - Prevented circular imports with lazy resolution.

3. Verification
   - Full AAA verification matrix still passes.

## Verified Commands

```bash
.venv/bin/pytest tests/test_aaa_mcp_contract.py tests/test_aaa_phase3_flow.py tests/test_aaa_phase5_runtime.py tests/test_fastmcp_config_contract.py -v
```

Result: **13 passed**.

## Next

- Prepare final merge to `main` and run 999 seal handoff.
