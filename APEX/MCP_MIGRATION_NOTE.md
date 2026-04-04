# MCP_MIGRATION_NOTE.md — openclaw_ASI → main OpenClaw

Purpose: Port the *jernih* (good) MCP wiring patterns from `/root/openclaw_ASI` into the main OpenClaw stack under `~/.openclaw`, without importing old/broken keys or redundant bots.

## Source

File: `/root/openclaw_ASI/config/mcp-kimi-arifos.json`

Key patterns worth reusing:

1. **context7 MCP**
   - HTTP MCP at `https://mcp.context7.com/mcp`
   - Header: `CONTEXT7_API_KEY`
   - Role: F2 Truth external documentation witness

2. **perplexity MCP**
   - HTTP MCP at `https://mcp.perplexity.ai/mcp`
   - Header: `PERPLEXITY_API_KEY`
   - Role: F8 Genius research amplification

3. **github MCP (read‑heavy, write‑guarded)**
   - HTTP MCP at `https://api.github.com/mcp`
   - OAuth `clientId: ${GITHUB_OAUTH_CLIENT}`
   - `alwaysAllow`: read ops (get_file_contents, list_commits, etc.)
   - `dangerous`: write ops (create_or_update_file, create_pr, merge_pr, create_issue)

4. **filesystem MCP with blocked paths**
   - Transport: stdio
   - Command: `npx -y @modelcontextprotocol/server-filesystem@latest ${HOME}`
   - `blockedPaths`: `~/.ssh`, `~/.kimi`, `~/.config`, `/etc`, `/usr`, `${ARIFOS_VAULT}`

5. **memory MCP (graph)**
   - Transport: stdio
   - Command: `npx -y @modelcontextprotocol/server-memory@latest`
   - Env: `MEMORY_FILE_PATH=${ARIFOS_VAULT}/mcp-memory.json`

6. **sequential-thinking MCP**
   - Transport: stdio
   - Command: `npx -y @modelcontextprotocol/server-sequential-thinking@latest`
   - Max iterations: 10 (in the ASI config)

7. **playwright MCP (browser)**
   - Transport: stdio
   - Command: `npx -y @playwright/mcp@latest`
   - Env: `PLAYWRIGHT_HEADLESS=true`
   - `alwaysAllow`: navigate/snapshot/evaluate
   - `dangerous`: click/fill/type

8. **desktop-commander MCP**
   - Transport: stdio
   - Command: `npx -y @wonderwhy-er/desktop-commander@latest`
   - Env caps: `ALLOWED_COMMANDS` (git,python,node,...) and `BLOCKED_COMMANDS` (rm,sudo,chmod,...)
   - All commands require approval (no auto‑allow)

9. **git-local MCP**
   - Transport: stdio
   - Command: `uvx mcp-server-git --repository ${ARIFOS_REPO}`
   - `alwaysAllow`: status/log/diff/branch
   - `dangerous`: commit/push/pull

## Target

Main stack lives under:

- Config: `~/.openclaw/openclaw.json`
- Agent models/tools: `~/.openclaw/agents/main/agent/models.json`
- Skills: `~/.openclaw/skills/*`

## Migration Plan (Applied)

1. **Do not import any API keys from `openclaw_ASI`.**
   - All live keys stay in `/root/.env.openclaw`.

2. **Ensure main OpenClaw already has equivalent MCPs where needed.**
   - Main stack already has `context7`, `perplexity`, `github`, `filesystem`, `sequential-thinking`, `playwright`, `git` tools configured via skills and MCP.
   - The ASI config adds useful *governance patterns* (alwaysAllow vs dangerous, blockedPaths) which should be mirrored conceptually, not copied verbatim.

3. **Adopt governance patterns, not duplicate stacks.**

   - Filesystem:
     - Keep existing main filesystem tool, but ensure it respects blocked paths similar to:
       - `~/.ssh`, `~/.config`, `/etc`, `/usr`, `${ARIFOS_VAULT}`.

   - Git:
     - Maintain current read‑heavy default.
     - Treat `git commit/push/pull` as elevated/dangerous operations (needs 888 Judge).

   - Browser (Playwright):
     - Separate “safe” actions (navigate, snapshot, evaluate) from “dangerous” (click, type, fill) and gate the latter via elevated/approval where OpenClaw supports it.

   - Desktop commander:
     - Only introduce this inside **Agent Zero / containers** in future, not on host, unless explicitly approved.

4. **No direct changes to `openclaw.json` made yet.**
   - This note is a reference for future config edits.

## Status

- Scan of `/root/openclaw_ASI` complete.
- No API key set in `openclaw_ASI` is "better" or more current than what lives in `/root/.env.openclaw`.
- `openclaw_ASI` is primarily an alternate wiring/prompt experiment, not the authoritative key vault.

*Next step (only when requested):* apply these governance patterns directly into `~/.openclaw/openclaw.json` and related skill configs, then retire ASI_bot processes entirely.
