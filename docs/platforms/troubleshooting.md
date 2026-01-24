# AAA MCP Troubleshooting Guide

Common issues and solutions for AAA MCP integration.

---

## Quick Diagnostics

Run the compliance test to verify your installation:

```bash
python scripts/test_mcp_compliance.py --verbose
```

Expected: 20/20 tests pass.

---

## Common Issues

### 1. Server Not Appearing in IDE

**Symptoms:**
- MCP server list doesn't show "arifos-trinity"
- Tool calls return "server not found"

**Solutions:**

1. **Verify config file location:**
   - Claude Desktop: `%APPDATA%\Claude\claude_desktop_config.json`
   - Cursor: See [cursor.md](cursor.md) for OS-specific paths

2. **Validate JSON syntax:**
   ```bash
   python -c "import json; json.load(open('path/to/config.json'))"
   ```

3. **Check paths use correct separators:**
   - Windows: Use `\\` or `/` in JSON
   - Unix: Use `/`

4. **Restart the IDE completely** (not just reload)

---

### 2. Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'AAA_MCP'
ModuleNotFoundError: No module named 'arifos'
```

**Solutions:**

1. **Install arifOS in editable mode:**
   ```bash
   cd /path/to/arifOS
   pip install -e .
   ```

2. **Verify PYTHONPATH in config:**
   ```json
   "env": {
     "PYTHONPATH": "/path/to/arifOS"
   }
   ```

3. **Check Python version:**
   ```bash
   python --version  # Should be 3.10+
   ```

---

### 3. MCP Module Not Found

**Symptoms:**
```
ModuleNotFoundError: No module named 'mcp'
```

**Solutions:**

```bash
pip install mcp
```

Or install full arifOS dependencies:
```bash
pip install -e ".[all]"
```

---

### 4. Rate Limit Errors

**Symptoms:**
```json
{
  "status": "VOID",
  "reason": "Rate limit exceeded",
  "rate_limit": {"exceeded": true}
}
```

**Solutions:**

1. **Wait for reset** - Rate limits reset automatically
2. **Check F11 Command Authority floor settings**
3. **Use session IDs** to track per-session limits

---

### 5. Constitutional Floor Violations

**Symptoms:**
```json
{
  "verdict": "VOID",
  "floors_failed": ["F12"]
}
```

**Solutions:**

| Floor | Common Cause | Fix |
|-------|--------------|-----|
| F1 Amanah | Irreversible operation | Add rollback capability |
| F2 Truth | Unverified claim | Add evidence/sources |
| F11 Command Auth | Unauthorized operation | Get explicit user approval |
| F12 Injection | Suspicious input pattern | Sanitize input |

---

### 6. Server Crashes on Startup

**Symptoms:**
- Server exits immediately
- No banner printed
- IDE shows "server disconnected"

**Diagnostic:**

```bash
cd /path/to/arifOS
python -m AAA_MCP 2>&1 | head -50
```

**Common Causes:**

1. **Missing spec files:**
   ```
   RuntimeError: TRACK B AUTHORITY FAILURE: Constitutional floors spec not found
   ```
   Fix: Ensure `arifos/spec/v47/` exists with JSON specs

2. **Circular imports:**
   Check for import errors in output

3. **Missing dependencies:**
   ```bash
   pip install -e ".[all]"
   ```

---

### 7. SSE Mode Issues (Railway)

**Symptoms:**
- Railway deployment fails
- SSE endpoint not responding

**Solutions:**

1. **Check PORT environment variable:**
   ```bash
   export PORT=8000
   python -m AAA_MCP sse
   ```

2. **Verify health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Check Railway logs** for Python errors

---

### 8. JSON Schema Validation Errors

**Symptoms:**
```
Invalid params: 'action' is a required property
```

**Solutions:**

1. **Check tool schema:**
   ```bash
   python -c "from AAA_MCP.server import TOOL_DESCRIPTIONS; import json; print(json.dumps(TOOL_DESCRIPTIONS['000_init']['inputSchema'], indent=2))"
   ```

2. **Ensure required params are provided**

3. **Use correct enum values** (e.g., `action` must be one of allowed values)

---

## Diagnostic Commands

### Test Server Creation

```bash
python -c "from AAA_MCP.server import create_aaa_server; s = create_aaa_server(); print('OK')"
```

### Test Tool Routers

```bash
python -c "
from AAA_MCP.bridge import bridge_init_router
result = bridge_init_router(action='validate')
print(result)
"
```

### Validate Spec Files

```bash
python -c "
from arifos.core.enforcement.metrics import load_constitutional_floors_spec
spec = load_constitutional_floors_spec()
print(f'Loaded {len(spec.get(\"floors\", {}))} floors')
"
```

### Check Rate Limiter

```bash
python -c "
from arifos.core.enforcement.governance.rate_limiter import get_rate_limiter
rl = get_rate_limiter()
result = rl.check('test', 'session1')
print(f'Allowed: {result.allowed}')
"
```

---

## Getting Help

1. **Run compliance test** - provides detailed diagnostics
2. **Check GitHub issues** - [github.com/arifOS/issues](https://github.com)
3. **Review logs** - IDE-specific log locations above

---

## Log Locations

| Platform | Log Path |
|----------|----------|
| Claude Desktop | `%APPDATA%\Claude\logs\` |
| Cursor (macOS) | `~/Library/Application Support/Cursor/logs/` |
| Cursor (Linux) | `~/.config/Cursor/logs/` |
| Cursor (Windows) | `%APPDATA%\Cursor\logs\` |
| Railway | Dashboard → Deployments → Logs |

---

**F4 Clarity Floor:** Reduce confusion, provide clear solutions.
**DITEMPA BUKAN DIBERI**
