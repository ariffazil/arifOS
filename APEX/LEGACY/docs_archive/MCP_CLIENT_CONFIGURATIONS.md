# MCP Client Configuration Guide

**Version:** v60.0-FORGE  
**Purpose:** Connect any MCP-compatible AI client to arifOS

---

## Supported Clients

| Client | Transport | Status | Configuration File |
|--------|-----------|--------|-------------------|
| **Kimi** | stdio | ✅ Tested | `.kimi/mcp.json` |
| **Claude Desktop** | stdio/SSE | ✅ Tested | `claude_desktop_config.json` |
| **Claude Code** | stdio | ✅ Tested | `.claude/mcp.json` |
| **Cursor** | stdio | ✅ Tested | `.cursor/mcp.json` |
| **Codex** | stdio | ✅ Tested | `.codex/mcp.json` |
| **Generic SSE** | SSE | ✅ Standard | Custom |

---

## Kimi Configuration

### Windows

**Path:** `%USERPROFILE%\.kimi\mcp.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "mcpServers": {
    "aaa-mcp": {
      "command": "C:\\Users\\User\\arifOS\\.venv\\Scripts\\python.exe",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": "C:/Users/User/arifOS",
      "env": {
        "PYTHONPATH": "C:/Users/User/arifOS",
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1"
      },
      "disabled": false,
      "alwaysAllow": [
        "init_gate",
        "trinity_forge",
        "agi_sense",
        "agi_think",
        "agi_reason",
        "asi_empathize",
        "asi_align",
        "apex_verdict",
        "reality_search",
        "vault_seal"
      ]
    }
  }
}
```

### macOS / Linux

**Path:** `~/.kimi/mcp.json`

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "/path/to/arifOS/.venv/bin/python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": "/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/path/to/arifOS",
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA"
      },
      "alwaysAllow": [
        "init_gate",
        "trinity_forge",
        "agi_sense",
        "agi_reason",
        "asi_empathize",
        "apex_verdict",
        "vault_seal"
      ]
    }
  }
}
```

### Verification

1. Save configuration
2. Restart Kimi
3. Test with: "Use init_gate to start a session"

---

## Claude Desktop Configuration

### Windows

**Path:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arifos-local": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": "C:\\Users\\User\\arifOS",
      "env": {
        "PYTHONPATH": "C:\\Users\\User\\arifOS",
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### macOS

**Path:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arifos-local": {
      "command": "/path/to/arifOS/.venv/bin/python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": "/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/path/to/arifOS",
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA"
      }
    }
  }
}
```

### With Cloud Deployment (SSE)

```json
{
  "mcpServers": {
    "arifos-local": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": "/path/to/arifOS"
    },
    "arifos-cloud": {
      "transport": "sse",
      "url": "https://mcp.yourdomain.com/sse",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

### Verification

1. Save configuration
2. Restart Claude Desktop
3. Look for 🔨 tool icons in the interface
4. Test: "Check constitutional status with init_gate"

---

## Claude Code Configuration

**Path:** `.claude/mcp.json` (in project root)

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": ".",
      "env": {
        "PYTHONPATH": ".",
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA"
      }
    }
  }
}
```

### Verification

```bash
# In Claude Code, test with:
/mcp tool init_gate query="Hello constitutional AI"
```

---

## Cursor Configuration

**Path:** `.cursor/mcp.json` (in project root or ~/.cursor/)

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": "/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/path/to/arifOS",
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA"
      }
    }
  }
}
```

### Verification

1. Open Cursor Settings
2. Go to MCP section
3. Verify arifos appears in tools
4. Test in chat: "Run constitutional check"

---

## Codex Configuration

**Path:** `~/.codex/mcp.json`

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": "/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/path/to/arifOS",
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA"
      }
    }
  }
}
```

### Verification

```bash
codex "Check if this query is constitutional"
```

---

## Generic SSE Client

For any client that supports SSE transport:

```json
{
  "mcpServers": {
    "arifos": {
      "transport": "sse",
      "url": "http://localhost:8080/sse",
      "headers": {}
    }
  }
}
```

For production with HTTPS:

```json
{
  "mcpServers": {
    "arifos": {
      "transport": "sse",
      "url": "https://mcp.yourdomain.com/sse",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

---

## Testing Your Configuration

### Universal Test Commands

```bash
# Test 1: Health check
curl http://localhost:8080/health

# Test 2: List tools (MCP protocol)
# This depends on your MCP client

# Test 3: Direct Python
python -c "
from core.pipeline import forge
import asyncio

async def test():
    result = await forge('Test query', actor_id='test')
    print(f'Verdict: {result.verdict}')

asyncio.run(test())
"
```

### Client-Specific Tests

**Kimi:**
```
Use trinity_forge to analyze "What is constitutional AI?"
```

**Claude:**
```
Call init_gate with query "Hello constitutional system"
```

**Cursor:**
```
/constitutional status
```

---

## Troubleshooting

### Issue: "Command not found"

**Fix:** Check Python path
```bash
# Windows
where python

# macOS/Linux
which python

# Use absolute path in config
"command": "C:\\Users\\User\\arifOS\\.venv\\Scripts\\python.exe"
```

### Issue: "Module not found: aaa_mcp"

**Fix:** Install package
```bash
cd /path/to/arifOS
pip install -e .
```

### Issue: "Connection refused"

**Fix:** Check if server is running
```bash
# For stdio: Check client logs
# For SSE:
curl http://localhost:8080/health
```

### Issue: "Permission denied"

**Fix:** Check file permissions
```bash
chmod +x /path/to/arifOS/.venv/bin/python
```

---

## Advanced Configuration

### With External APIs

```json
{
  "mcpServers": {
    "arifos-full": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": "/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/path/to/arifOS",
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA",
        "BRAVE_API_KEY": "your_brave_key",
        "BROWSERBASE_API_KEY": "your_browserbase_key"
      }
    }
  }
}
```

### With Database

```json
{
  "mcpServers": {
    "arifos-prod": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": "/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/path/to/arifOS",
        "DATABASE_URL": "postgresql://user:pass@host/db",
        "REDIS_URL": "redis://localhost:6379"
      }
    }
  }
}
```

---

## Reference

### File Paths Summary

| OS | Client | Path |
|----|--------|------|
| Windows | Kimi | `%USERPROFILE%\.kimi\mcp.json` |
| Windows | Claude | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | Kimi | `~/.kimi/mcp.json` |
| macOS | Claude | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | Kimi | `~/.kimi/mcp.json` |
| Linux | Claude | `~/.config/Claude/claude_desktop_config.json` |
| All | Cursor | `.cursor/mcp.json` (project or home) |
| All | Claude Code | `.claude/mcp.json` (project) |

### Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `PYTHONPATH` | Module resolution | `/path/to/arifOS` |
| `ARIFOS_CONSTITUTIONAL_MODE` | Governance mode | `AAA` |
| `PYTHONIOENCODING` | Unicode support | `utf-8` |
| `PYTHONUNBUFFERED` | Log streaming | `1` |

---

*For deployment instructions, see `MCP_DEPLOYMENT_GUIDE_V60.md`*

**DITEMPA BUKAN DIBERI** 💎🔥🧠
