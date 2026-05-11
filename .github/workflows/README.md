# MCP Registry Publishing

This workflow automatically publishes `arifos` to the [MCP Registry](https://registry.modelcontextprotocol.io) whenever a GitHub release is published.

## How It Works

| Trigger | Action |
|---------|--------|
| **Release published** | Auto-publishes to MCP Registry |
| **Manual (workflow_dispatch)** | Publish specific version on demand |

## Automatic Publishing (Recommended)

1. Create a new release on GitHub
2. The workflow triggers automatically
3. Server appears in MCP Registry within minutes

## Manual Publishing

If you need to publish without creating a release:

1. Go to **Actions** → **Publish to MCP Registry**
2. Click **Run workflow**
3. Enter version (e.g., `2026.2.22`)
4. Click **Run workflow**

## Namespace

- **MCP Name**: `io.github.ariffazil/arifos-mcp`
- **Authentication**: GitHub OIDC (uses `GITHUB_TOKEN`)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Permission denied" | Check `GITHUB_TOKEN` has `id-token: write` permission |
| "Server already exists" | Bump version in `server.json` and `pyproject.toml` |
| "Invalid server.json" | Run `python -c "import json; json.load(open('server.json'))"` locally |

## Links

- [MCP Registry](https://registry.modelcontextprotocol.io)
- [Publishing Docs](https://modelcontextprotocol.io/registry/quickstart)
- [Your Server](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.ariffazil/arifos-mcp) (after publish)
