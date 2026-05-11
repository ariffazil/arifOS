---
description: Unified Global MCP Stack Governance — F4 Clarity [Alignment]
---

**Motto:** *One Global Surface | Tiered Order | Verified Packages Only*

### 1. Purpose
This workflow defines the single approved MCP stack for `ariffazil`. The source of truth is `C:\Users\User\.gemini\antigravity\mcp_config.json`.

### 2. Canonical Shape
- Antigravity uses one flat `mcpServers` map.
- The 3-tier model is expressed by server order plus workflow policy, not a nested JSON schema.
- All workspaces inherit the same global stack unless the user explicitly authorizes an exception.

### 3. Approved Global Stack
- **KERNEL**: `arifos`, `memory`, `sequential-thinking`, `filesystem`, `meyhem`
- **OPS**: `github-official`, `PostgresMCP`, `playwright`, `cloudflare-workers`, `desktop-commander`
- **INTELLIGENCE**: `brave-search`, `context7`, `perplexity`, `exa-search`, `notion`

### 4. Consolidation Rules
- One shared server name and one shared config entry per capability.
- `arifos` resolves from `C:\ariffazil\arifOS\arifosmcp`.
- Overlapping or dead package entries are removed instead of carried forward.

### 5. Deferred or Removed Surface
- `supabase` removed as overlapping DB capability.
- `DockerMCP`, `JinaMCP`, `openapi-swagger`, and `telegram` are deferred until a verified package or endpoint is explicitly approved.

### 6. Execution Rules
- No auto-install, auto-mount, auto-enable, or auto-call from discovery tools.
- Any MCP surface change must update this workflow set and the global config in the same change.
- Secrets stay in environment variables or redacted placeholders only.
- `filesystem` stays scoped to approved roots; `desktop-commander` stays approval-gated for config and system-adjacent work.

### 7. Drift Rules
- Workspace-specific `mcp_config.json` files are prohibited unless explicitly authorized.
- If local and global MCP definitions conflict, the global config wins.

*Ditempa Bukan Diberi — [ARIF OS KERNEL]*
