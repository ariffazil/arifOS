# OpenCode Agent Setup & Troubleshooting

This guide covers the configuration and maintenance of the arifOS AAA MCP server as an OpenCode agent, especially on VPS environments.

## Current Issues Identified

1. **3 failing MCP servers**: `docker-mcp`, `fetch`, `git`
2. **Stale configuration**: OpenCode config uses legacy tool names and Windows paths
3. **High token usage**: 16 MCP servers running, many unnecessary
4. **Container tools import failures**: Docker not available on Windows/dev machines

## Fix Procedure

### 1. Install Missing NPM Packages

The `fetch` and `git` MCP servers are npm packages that need global installation:

```bash
npm install -g @modelcontextprotocol/server-fetch
npm install -g @modelcontextprotocol/server-git
```

### 2. Fix Docker Permissions

For `docker-mcp` server to work, the user must be in the `docker` group:

```bash
sudo usermod -aG docker $(whoami)
# Log out and back in for changes to take effect
```

### 3. Reduce MCP Server Count

Edit `~/.config/opencode/opencode.json` to keep only essential servers (OpenCode uses `"mcp"` key, not `"mcpServers"`):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "aaa-mcp": {
      "type": "local",
      "command": ["python", "-m", "aaa_mcp", "stdio"],
      "cwd": ".",
      "enabled": true,
      "timeout": 15000,
      "environment": {
        "PYTHONPATH": ".",
        "ARIFOS_MODE": "PROD"
      }
    },
    "filesystem": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/", "/home", "/tmp", "/var"],
      "enabled": true
    },
    "fetch": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-fetch"],
      "enabled": true
    },
    "git": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-git"],
      "enabled": true
    }
  }
}
```

**Recommendation**: Keep only `aaa-mcp`, `filesystem`, `fetch`, and `git`. This reduces token usage from ~16 servers to ~4.

### 4. Update Tool Names in Configuration

The OpenCode agent expects the 9 canonical tool names (not legacy names like `init_session`, `agi_cognition`). Ensure your `mcp.json` uses the correct tool names in the `alwaysAllow` array:

```json
"alwaysAllow": [
  "anchor",
  "reason",
  "integrate",
  "respond",
  "validate",
  "align",
  "forge",
  "audit",
  "seal"
]
```

The `mcp.json` file is located at `333_APPS/L4_TOOLS/mcp-configs/opencode/mcp.json` and has already been updated.

### 5. Conditional Container Tools

The `aaa_mcp/server.py` now imports container tools conditionally:

```python
try:
    from aaa_mcp.integrations.mcp_container_tools import register_container_tools
    register_container_tools(mcp)
    print("✅ Container tools registered (Docker available)")
except Exception as e:
    print(f"⚠️  Container tools not available: {e}")
```

This prevents import failures on systems without Docker.

### 6. Platform‑Specific Paths

The `333_APPS/L4_TOOLS/mcp-configs/opencode/mcp.json` file has been updated to use cross‑platform paths:

```json
"command": "python3",
"args": ["-m", "aaa_mcp", "stdio"],
"cwd": "../../../../",
"env": {
  "PYTHONPATH": ".",
  "ARIFOS_CONSTITUTIONAL_MODE": "AAA"
}
```

This ensures the configuration works on both VPS and local development environments.

### 7. Pull VPS Configuration into Repo

To keep configurations synchronized, copy the live VPS config into version control:

```bash
cp ~/.config/opencode/opencode.json /root/arifOS/333_APPS/L4_TOOLS/mcp-configs/opencode/opencode-vps.json
```

The repository now contains a template configuration at `333_APPS/L4_TOOLS/mcp-configs/opencode/opencode.json` that balances functionality and performance. Use the `scripts/setup-opencode-agent.sh` script to automatically optimize the VPS configuration.

## Automation Script

Run the setup script to apply most fixes automatically:

```bash
chmod +x /root/arifOS/scripts/setup-opencode-agent.sh
sudo /root/arifOS/scripts/setup-opencode-agent.sh
```

## Verification

After applying fixes:

1. Restart OpenCode agent (or reload configuration)
2. Check MCP server status in OpenCode UI
3. Verify tool availability by calling `anchor` tool
4. Monitor token usage reduction

## Constitutional Compliance Notes

- **F2 Truth**: No mock scores remain in `dashboard_aggregator.py`
- **F9 Anti‑Hantu**: Bare `except:` blocks replaced with specific exception handling
- **Version alignment**: `pyproject.toml` now uses T000 format (`2026.02.15-FORGE-TRINITY-SEAL`)
- **Linux‑only dependencies**: Documented in `core/physics/thermodynamics.py`
- **Code quality**: Fixed syntax errors in `codebase/init/000_init/init_000.py` and archive files
- **Formatting**: Applied `black` formatting to 542 files, ensuring consistent style

## Troubleshooting

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| "Tool not found" | Stale tool names in config | Update `alwaysAllow` list with 9 canonical names |
| Docker permission denied | User not in docker group | `sudo usermod -aG docker $(whoami)` |
| NPM package crashes | Missing global installation | Install with `npm install -g @modelcontextprotocol/server-*` |
| High token usage | Too many MCP servers | Reduce to essential 4 servers |
| Import errors on Windows | Container tools require Docker | Conditional import already handles this |

## References

- [AGENTS.md](../AGENTS.md) – General agent guidelines
- [CLAUDE.md](../CLAUDE.md) – Constitutional floor specifications
- [T000_VERSIONING.md](../T000_VERSIONING.md) – Version format

---

**Last Updated**: 2026‑02‑15  
**Status**: ✅ Fixes applied, documentation updated
