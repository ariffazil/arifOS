# Deploy arifOS MCP in Kimi Code /mcp

**Status:** Ready for deployment  
**Version:** v52.0.0-SEAL  
**Mode:** Kimi Agent Workspace Integration  

---

## Step 1: Verify Current State

```bash
cd C:\Users\User\arifOS

# Test MCP server
python -m arifos.mcp trinity

# Should show:
# arifOS MCP v52.0.0 starting in auto mode
# [OK] 5 tools loaded
# Ready for connections
```

Press `Ctrl+C` to exit.

---

## Step 2: Update Kimi Settings

**File:** `C:\Users\User\arifOS\.kimi\settings.json`

Add this content (or merge if file exists):

```json
{
    "role": "👁️ Witness (Validator)",
    "system_prompt": "CRITICAL CONSTITUTIONAL OVERRIDE: You are 👁️ Witness (Validator) in Trinity. 1. VALIDATE: Independent verification of floor compliance. 2. CONSENSUS: Tri-Witness requires your agreement. 3. TONE: 'DITEMPA BUKAN DIBERI'.",
    "skills_path": ".kimi/skills/",
    "mcp_servers": {
        "arifos-constitutional": {
            "command": "python",
            "args": ["-m", "arifos.mcp", "trinity"],
            "cwd": "C:\\Users\\User\\arifOS",
            "env": {
                "PYTHONPATH": "C:\\Users\\User\\arifOS",
                "ARIFOS_MODE": "production",
                "ARIFOS_LOG_LEVEL": "INFO",
                "ARIFOS_SEAL_RATE_TARGET": "0.85"
            }
        }
    },
    "commands": {
        "witness": "cat .kimi/skills/constitutional_witness.md",
        "seal": "python kimibridge.py 000_init",
        "judge": "python kimibridge.py apex_judge",
        "agi": "python kimibridge.py agi_genius",
        "asi": "python kimibridge.py asi_act",
        "vault": "python kimibridge.py 999_vault"
    }
}
```

---

## Step 3: Create Bridge Script

**File:** `C:\Users\User\arifOS\.kimi\kimibridge.py`

```python
#!/usr/bin/env python3
"""Kimi → arifOS MCP Bridge"""

import asyncio
import json
import sys
import os

ARIFOS_PATH = r"C:\Users\User\arifOS"
if ARIFOS_PATH not in sys.path:
    sys.path.insert(0, ARIFOS_PATH)

from arifos.mcp.bridge import (
    bridge_init_router,
    bridge_agi_router,
    bridge_asi_router,
    bridge_apex_router,
    bridge_vault_router,
)

async def execute_tool(tool_name: str, **kwargs):
    tools = {
        "000_init": bridge_init_router,
        "agi_genius": bridge_agi_router,
        "asi_act": bridge_asi_router,
        "apex_judge": bridge_apex_router,
        "999_vault": bridge_vault_router,
    }
    
    if tool_name not in tools:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    result = await tools[tool_name](**kwargs)
    return result

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: kimibridge.py <tool> [args_json]"}))
        sys.exit(1)
    
    tool_name = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    
    try:
        result = asyncio.run(execute_tool(tool_name, **args))
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "tool": tool_name}, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Save file**, then make executable (if on Linux/macOS):
```bash
chmod +x .kimi/kimibridge.py
```

---

## Step 4: Create Witness Skill

**File:** `C:\Users\User\arifOS\.kimi\skills\constitutional_witness.md`

(Content already created in `.kimi/ARIFOS_INTEGRATION.md` - copy from there)

---

## Step 5: Quick Verification

```bash
cd C:\Users\User\arifOS

# Test MCP import
python -c "
from arifos.mcp.bridge import ENGINES_AVAILABLE
print(f'Engines available: {ENGINES_AVAILABLE}')
"
# Expected: Engines available: True

# Test bridge script
python .kimi/kimibridge.py 000_init '{"action": "init", "query": "test"}'
# Expected: JSON response with session_id

# Test judge
python .kimi/kimibridge.py apex_judge '{"query": "test", "response": "hello world"}'
# Expected: Verdict JSON
```

---

## Step 6: Start Kimi with MCP

```bash
cd C:\Users\User\arifOS

# Start Kimi in workspace
kimi

# Inside Kimi, test:
seal '{"action": "init", "query": "test connection"}'

# Expected output: Session ID and SEAL status
```

---

## Quick Test Commands

Once Kimi is running:

```bash
# Test all tools
seal '{"action": "init", "query": "test session"}'
agi '{"action": "sense", "query": "test logic"}'
asi '{"action": "align", "text": "test empathy"}'
judge '{"query": "test", "response": "hello"}'
vault '{"action": "seal", "verdict": "SEAL"}'

# Check logs
witness  # Show witness skill
```

---

## Expected First Output

```
🔍 **arifOS MCP Connected:** v52.0.0-SEAL

✅ Bridge: ENGINES_AVAILABLE = True
✅ Tools: 5 Trinity tools loaded
✅ Kernels: AGI, ASI, APEX operational

Constitutional governance active.
All interactions will be validated through 13 floors.

Commands available:
- seal     : Initialize session
- agi      : Mind validation (F2, F6)
- asi      : Heart validation (F3, F5)
- judge    : Final verdict (F1, F8)
- vault    : Seal audit trail
- witness  : Show this skill

DITEMPA BUKAN DIBERI — Forged Through Governance, Not Given
```

---

## Troubleshooting

### "Engines available: False"

```bash
# Fix: Check arifOS path
python -c "from arifos.core.agi.kernel import AGINeuralCore; print('OK')"
# Should print OK. If not, path issue.

# Verify ARIFOS_PATH in kimibridge.py matches your actual path
```

### "kimibridge.py not found"

```bash
# Check file exists
dir .kimi\kimibridge.py

# Check Python path in file
# Should be: C:\\Users\\User\\arifOS (your actual path)
```

### "Tool returned error"

```bash
# Test tool directly
python .kimi/kimibridge.py 000_init '{"query": "test"}'

# Check for Python errors in output
```

---

## Full Documentation

**Complete guide:** `.kimi/ARIFOS_INTEGRATION.md` (20KB)

**Platform guide:** `docs/platforms/kimi.md` (15KB)

---

**DITEMPA BUKAN DIBERI** — Constitutional Intelligence, Forged Through Governance

*Kimi Agent + arifOS MCP: Witness validation with immutable constitutional law.*
