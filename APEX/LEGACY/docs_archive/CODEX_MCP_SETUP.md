# Codex MCP Setup (GitHub / Brave / Perplexity / Sequential Thinking / Context7)

This repo ships a ready-to-edit Codex MCP config at `.codex/mcp_config.json`.

## Required environment variables

- `GITHUB_PERSONAL_ACCESS_TOKEN`
- `BRAVE_API_KEY`
- `PERPLEXITY_API_KEY` (optional: `PERPLEXITY_TIMEOUT_MS`)
- `CONTEXT7_API_KEY`

## Codex CLI add commands (optional alternative to editing JSON)

```bash
codex mcp add github --env GITHUB_PERSONAL_ACCESS_TOKEN="..." -- npx -y @modelcontextprotocol/server-github
codex mcp add brave-search --env BRAVE_API_KEY="..." -- npx -y @modelcontextprotocol/server-brave-search
codex mcp add perplexity-ask --env PERPLEXITY_API_KEY="..." -- npx -y @perplexity-ai/mcp-server
codex mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking
codex mcp add context7 --env CONTEXT7_API_KEY="..." -- npx -y @upstash/context7-mcp
```

## Notes

- Windows: if `npx` isn’t found, replace `npx` with `npx.cmd`.
- `.codex/mcp_config.json` currently pins `cwd`/`PYTHONPATH` to `C:\\Users\\User\\OneDrive\\Documents\\GitHub\\arifOS`; change if your path differs.
