# MCP Housekeeping — Legacy Removal / Archive Note
Date: 2026-01-31
Author: Codex (at user request)
Scope: Removal of legacy MCP v53 artifacts superseded by v55 architecture.

## Removed (working tree deletes)
- codebase/mcp/mode_selector.py
- codebase/mcp/sse_simple.py
- codebase/mcp/server.py (legacy root)
- mcp/ legacy files:
  - mcp/HUMAN_GUIDE.md
  - mcp/MCP_FORGE_COMPLETE.md
  - mcp/README.md
  - mcp/kimi/KIMI_ARCHITECTURE.txt
  - mcp/kimi/KIMI_FORGE_SUMMARY.md
  - mcp/kimi/KIMI_INTEGRATION_GUIDE*.md
  - mcp/kimi/KIMI_PROMPT_*.txt
  - mcp/kimi/kimi_adapter.py
  - mcp/kimi/kimi_config.yaml
  - mcp/mcp_config.json
  - mcp/system_prompts/AI_CONSTITUTIONAL_PROMPT.txt

## Replacements in-tree
- New structured layout under `codebase/mcp/`:
  - config/, core/, transports/, archive/
- Streamlined tool stack in `codebase/mcp/tools/` (canonical_trinity, vault_tool, etc.)

## Rationale
- Remove deprecated HTTP+SSE and mode selector; superseded by v55 layout and LoopBridge wiring.
- Reduce ambiguity with duplicate entry points; align to current architecture docs.

## Notes
- Tests pass after changes (`pytest` → 63 passed, 2 skipped).
- This file documents the removals for audit trace (F1 Amanah).
