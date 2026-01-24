# Migration Guide: arifos/mcp → AAA_MCP (v51.1.0)

**The Great Decoupling** — Migrating from the old monolithic bridge to the new thin routing layer.

---

## Overview

**v51.0.0** introduced `AAA_MCP/` as a standalone MCP package, decoupled from the core `arifos/mcp/` module. This guide helps you migrate existing integrations.

### Key Changes

| Aspect | OLD (`arifos/mcp/`) | NEW (`AAA_MCP/`) |
|--------|---------------------|------------------|
| **Entry Point** | `python -m arifos.mcp trinity` | `python -m AAA_MCP` |
| **Bridge** | Fat (492 LOC, business logic) | Thin (210 LOC, routing only) |
| **Philosophy** | Bridge makes decisions | "I do not think, I only wire" |
| **Import Path** | `from arifos.mcp import ...` | `from AAA_MCP import ...` |

---

## Quick Migration

### 1. Update MCP Configuration

**Before (v50.x):**
```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "arifos.mcp", "trinity"]
    }
  }
}
```

**After (v51.1.0):**
```json
{
  "mcpServers": {
    "arifos-trinity": {
      "command": "python",
      "args": ["-m", "AAA_MCP"],
      "env": {
        "PYTHONPATH": ".",
        "ARIFOS_MODE": "production"
      }
    }
  }
}
```

### 2. Update Import Statements

**Before:**
```python
from arifos.mcp.bridge import MCPCoreBridge
from arifos.mcp.tools.mcp_trinity import TrinityMCP

bridge = MCPCoreBridge(session_id)
result = bridge.execute_agi(query, context)
```

**After:**
```python
from AAA_MCP.bridge import bridge_agi_router

# Direct function call - no class instantiation needed
result = bridge_agi_router(action="full", query=query, session_id=session_id)
```

### 3. Update SSE Mode

**Before:**
```bash
python -m arifos.mcp trinity-sse --port 8000
```

**After:**
```bash
python -m AAA_MCP sse --port 8000
```

---

## API Changes

### Removed Classes

| Class | Migration Path |
|-------|----------------|
| `MCPCoreBridge` | Use `bridge_*_router()` functions |
| `ToolRegistry` | Not needed (MCP handles tool registration) |
| `ToolLink` | Not needed |

### New Functions

```python
# AAA_MCP/bridge.py

def bridge_init_router(action: str, query: str, session_id: str = None, **kw) -> Dict:
    """Route to 000_init tool."""

def bridge_agi_router(action: str, query: str, session_id: str = None, **kw) -> Dict:
    """Route to agi_genius tool."""

def bridge_asi_router(action: str, text: str, session_id: str = None, **kw) -> Dict:
    """Route to asi_act tool."""

def bridge_apex_router(action: str, query: str, response: str, session_id: str = None, **kw) -> Dict:
    """Route to apex_judge tool."""

def bridge_vault_router(action: str, session_id: str = None, **kw) -> Dict:
    """Route to 999_vault tool."""
```

### Tool Names (Unchanged)

The 5 constitutional tools remain the same:

1. `000_init` — Constitutional gate (authority + injection defense)
2. `agi_genius` — Mind engine (search → think → atlas → forge)
3. `asi_act` — Heart engine (evidence → empathy → align → act)
4. `apex_judge` — Soul engine (eureka → judge → proof)
5. `999_vault` — Seal (Merkle + zkPC + immutable log)

---

## Configuration Migration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ARIFOS_MODE` | `production` | Operating mode |
| `ARIFOS_MCP_MODE` | `stdio` | Transport mode (`stdio` or `sse`) |
| `ARIFOS_SEAL_RATE_TARGET` | `0.85` | Target SEAL rate |
| `ARIFOS_LOG_LEVEL` | `INFO` | Logging level |

### Platform-Specific Configs

**Claude Desktop (Windows):**
```json
// %APPDATA%\Claude\claude_desktop_config.json
{
  "mcpServers": {
    "arifos-trinity": {
      "command": "python",
      "args": ["-m", "AAA_MCP"],
      "cwd": "C:\\Users\\User\\arifOS",
      "env": {
        "ARIFOS_MODE": "production"
      }
    }
  }
}
```

**Cursor IDE:**
```json
// ~/.cursor/mcp.json
{
  "mcpServers": {
    "arifos-constitutional": {
      "name": "arifOS Constitutional AI",
      "command": "python -m AAA_MCP",
      "cwd": "${workspaceFolder}"
    }
  }
}
```

**Cline (VS Code):**
```json
// .vscode/mcp.json
{
  "mcpServers": {
    "arifos": {
      "command": "python -m AAA_MCP",
      "cwd": "${workspaceFolder}",
      "description": "Constitutional AI governance"
    }
  }
}
```

---

## Breaking Changes

### 1. `MCPCoreBridge` Removed

**Impact:** Code that instantiates `MCPCoreBridge` will fail.

**Migration:**
```python
# OLD
from arifos.mcp.bridge import MCPCoreBridge
bridge = MCPCoreBridge(session_id)
result = bridge.execute_agi(query, {})

# NEW
from AAA_MCP.bridge import bridge_agi_router
result = bridge_agi_router(action="full", query=query, session_id=session_id)
```

### 2. `ToolRegistry` Removed

**Impact:** Custom tool registration via `ToolRegistry` no longer works.

**Migration:** Use MCP native tool registration in `server.py` instead:

```python
# AAA_MCP/server.py already registers all 5 tools via @mcp.tool() decorator
```

### 3. Import Path Changed

**Impact:** All `from arifos.mcp import ...` statements need updating.

**Migration:**
```python
# OLD
from arifos.mcp.bridge import MCPCoreBridge
from arifos.mcp.tools.mcp_trinity import TrinityMCP

# NEW
from AAA_MCP.bridge import bridge_agi_router, bridge_asi_router
from AAA_MCP.server import serve  # For programmatic server start
```

### 4. Entry Point Changed

**Impact:** Scripts calling `python -m arifos.mcp trinity` will fail.

**Migration:**
```bash
# OLD
python -m arifos.mcp trinity
python -m arifos.mcp trinity-sse

# NEW
python -m AAA_MCP          # stdio mode
python -m AAA_MCP sse      # SSE mode
```

---

## Backward Compatibility

The old `arifos/mcp/` module is **NOT removed** but is considered **deprecated**.

### Deprecation Timeline

| Version | Status |
|---------|--------|
| v51.0.0 | AAA_MCP introduced, arifos/mcp deprecated |
| v52.0.0 | arifos/mcp will emit deprecation warnings |
| v53.0.0 | arifos/mcp will be removed |

### Using Old Module (Not Recommended)

If you must use the old module temporarily:

```bash
# Still works (deprecated)
python -m arifos.mcp trinity

# Recommended
python -m AAA_MCP
```

---

## Testing Your Migration

### 1. Verify Installation

```bash
# Check AAA_MCP loads
python -c "from AAA_MCP import serve; print('OK')"

# Check version
python -m AAA_MCP --version
# Expected: v51.1.0
```

### 2. Test Tool Invocation

```bash
# Start server
python -m AAA_MCP &

# Test with MCP client (e.g., mcp-cli)
mcp call 000_init '{"action": "init", "query": "test"}'
```

### 3. Verify Health (SSE Mode)

```bash
# Start SSE server
python -m AAA_MCP sse --port 8000 &

# Check health
curl http://localhost:8000/health
# Expected: {"status": "healthy", "version": "v51.1.0", ...}
```

---

## Troubleshooting

### "Module 'AAA_MCP' not found"

```bash
# Ensure you're in the arifOS directory
cd /path/to/arifOS

# Set PYTHONPATH
export PYTHONPATH=.

# Or install as package
pip install -e .
```

### "Tools not appearing in Claude Desktop"

1. Check config path: `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
2. Verify JSON syntax (no trailing commas)
3. Restart Claude Desktop completely
4. Check logs: `claude_desktop.log`

### "Rate limit exceeded"

The new rate limiter uses centralized governance:

```python
# Rate limiting now comes from arifos.core.enforcement.governance
from arifos.core.enforcement.governance.rate_limiter import get_rate_limiter

limiter = get_rate_limiter()
result = limiter.check("agi_genius", session_id)
if not result.allowed:
    print(f"Rate limited: {result.reason}")
```

### "FloorCheckResult 'is_hard' error"

This was a bug in v51.0.0, fixed in v51.1.0. Update to latest:

```bash
git pull origin main
```

---

## Summary

| Step | Action |
|------|--------|
| 1 | Update MCP config: `arifos.mcp trinity` → `AAA_MCP` |
| 2 | Update imports: `arifos.mcp.bridge` → `AAA_MCP.bridge` |
| 3 | Replace `MCPCoreBridge` class with `bridge_*_router()` functions |
| 4 | Update SSE entry point: `trinity-sse` → `sse` |
| 5 | Test all 5 tools work correctly |
| 6 | Remove deprecated imports after verification |

---

**Version:** v51.1.0 | **Status:** SEALED | **Date:** 2026-01-24

*DITEMPA BUKAN DIBERI — Forged, Not Given*
