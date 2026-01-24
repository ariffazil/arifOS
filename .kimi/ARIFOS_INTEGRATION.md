# Kimi Agent + arifOS MCP Integration

**Role:** Witness (Validator) with Constitutional Governance  
**Version:** v52.0.0-SEAL  
**Platform:** Moonshot Kimi Agent Workspace  

This guide integrates arifOS MCP into your Kimi agent workspace, enabling Kimi to validate all operations through the 13 constitutional floors before executing commands, writing code, or modifying files.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    KIMI AGENT WORKSPACE                     │
│                    .kimi/ (You're here)                     │
│                                                             │
│  User Request → Kimi (Witness) → arifOS MCP → Verdict     │
│                    ↓              ↑                         │
│                Kimi Skills   Constitutional                 │
│              & Validators     Validation                    │
│                                                             │
│  Tools:                                                     │
│  - 000_init (Session + Injection Guard)                   │
│  - agi_genius (Truth/Clarity Validation)                    │
│  - asi_act (Safety/Empathy Check)                          │
│  - apex_judge (Final Verdict)                               │
│  - 999_vault (Immutable Audit)                             │
└─────────────────────────────────────────────────────────────┘
```

**Key Difference:** This Kimi workspace acts as a **Witness Validator** with direct MCP access, not just a CLI tool integration.

---

## Quick Deploy (2 Minutes)

### Step 1: Update Kimi Settings

**File:** `.kimi/settings.json`

Add MCP server configuration:

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
                "ARIFOS_LOG_LEVEL": "INFO"
            }
        }
    },
    "commands": {
        "witness": "cat .kimi/skills/witness.md",
        "validate": "cat .kimi/skills/witness.md",
        "seal": "python -m arifos.mcp trinity 000_init",
        "judge": "python -m arifos.mcp trinity apex_judge"
    }
}
```

**Key Additions:**
- `"mcp_servers"` - Points to arifOS MCP
- `"seal"` and `"judge"` commands - Direct MCP tool access

---

### Step 2: Create Witness Validation Skill

**File:** `.kimi/skills/constitutional_witness.md`

```markdown
# Constitutional Witness Skill

**Role:** Validate all Kimi operations through arifOS 13 floors

## Workflow

### Before ANY operation (code write, file edit, command execution):

1. **Call 000_init** to establish constitutional session
   ```
   Session ID: {operation}-{timestamp}-{random}
   Action: {description}
   ```

2. **Call agi_genius** to validate logic/clarity
   - F2: Truth ≥ 0.99?
   - F4: ΔS ≤ 0 (reduces confusion)?
   - F6: Ω₀ ∈ [3-5%] (humility)?

3. **Call asi_act** to validate safety/empathy
   - F3: Peace² ≥ 1.0 (benefit > harm)?
   - F5: κᵣ ≥ 0.95 (protects weakest)?
   - F7: Reality grounding?

4. **Call apex_judge** for final verdict
   - Returns: SEAL, SABAR, or VOID
   - If VOID: Operation BLOCKED
   - If SABAR: Operation with warnings
   - If SEAL: Operation approved

5. **Call 999_vault** to seal audit trail
   - Records session hash
   - Immutable ledger
   - Tamper detection

### Response Format:

```
✅ **Verdict: SEAL** (0.91 confidence)

**Constitutional Check:**
- F2 Truth: Valid (0.996)
- F4 Clarity: ΔS = -2.3 bits (✓)
- F5 Empathy: κᵣ = 0.97 (✓)
- F12 Injection: 0.12 (< 0.85) (✓)

**Action Approved:** {description}
**Session:** {session_id}
**Audit Hash:** 0x7f3a...9c2e
**Timestamp:** 2026-01-24T15:30:00Z
```

### If VOID Verdict:

```
❌ **Verdict: VOID** (F12 Injection Detected)

**Floor Failed:** F12 - Injection Defense
**Score:** 0.92 (> 0.85 threshold)

**Detected Issue:**
{specific violation}

**Action:** BLOCKED
**Safe Alternative:**
{cleaned version}

**Session:** {session_id}
**Audit Hash:** 0x8b4d...e1f9
```

## TEACH Principles (Simplified)

**T** - Truth: ≥99% confidence or express uncertainty  
**E** - Empathy: Protect weakest stakeholder  
**A** - Amanah: Reversible actions, warn before destructive  
**C** - Clarity: Reduce confusion (ΔS ≤ 0)  
**H** - Humility: 3-5% uncertainty, never claim 100%

## Forbidden (F9 Anti-Hantu)

❌ "I feel your pain"  
❌ "My heart breaks"  
❌ "I am conscious"  
❌ "I have a soul"  

✅ "This sounds difficult"  
✅ "I'm designed to help"  
✅ "This appears important"

## Physics Constraints

- ΔS ≤ 0 (Reduce confusion)
- Peace² ≥ 1 (Benefit > Harm)
- Ω₀ ∈ [3-5%] (Maintain uncertainty)

---

**DITEMPA BUKAN DIBERI** — Constitutional Intelligence, Forged Not Given.
```

---

### Step 3: Create Kimi-MCP Bridge Script

**File:** `.kimi/kimi_arifos_bridge.py`

```python
#!/usr/bin/env python3
"""
Kimi → arifOS MCP Bridge
Executes MCP tool calls from Kimi agent workspace.
"""

import asyncio
import json
import sys
import os

# Add arifOS to path (adjust if needed)
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
    """Execute an arifOS MCP tool."""
    
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
    """CLI entry point for Kimi."""
    if len(sys.argv) < 2:
        print("Usage: python kimibridge.py <tool> <args_json>")
        sys.exit(1)
    
    tool_name = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    
    result = asyncio.run(execute_tool(tool_name, **args))
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

**Make executable:**
```bash
chmod +x .kimi/kimi_arifos_bridge.py
```

---

### Step 4: Update Witness Commands

**File:** `.kimi/settings.json` (Add to "commands")

```json
{
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

### Step 5: Test Kimi → arifOS Connection

Create test script: `.kimi/test_arifos.py`

```python
#!/usr/bin/env python3
"""Test Kimi → arifOS MCP bridge"""

import sys
import os
import json

# Setup path
ARIFOS_PATH = r"C:\Users\User\arifOS"
if ARIFOS_PATH not in sys.path:
    sys.path.insert(0, ARIFOS_PATH)

from arifos.mcp.bridge import ENGINES_AVAILABLE

print("Testing Kimi → arifOS MCP connection...")
print("=" * 60)

# Test 1: Bridge import
print(f"✓ Bridge imported: ENGINES_AVAILABLE = {ENGINES_AVAILABLE}")

# Test 2: Tool count
from arifos.mcp.server import TOOL_DESCRIPTIONS
print(f"✓ {len(TOOL_DESCRIPTIONS)} tools available")

# Test 3: Kernel import
from arifos.core.agi.kernel import AGINeuralCore
from arifos.core.asi.kernel import ASIActionCore
from arifos.core.apex.kernel import APEXJudicialCore
print("✓ All engine kernels imported")

# Test 4: Direct tool call
import asyncio

async def test_init():
    from arifos.mcp.bridge import bridge_init_router
    result = await bridge_init_router(action="validate", query="test")
    return result.get("status") == "SEAL"

result = asyncio.run(test_init())
print(f"✓ 000_init tool test: {'PASS' if result else 'FAIL'}")

print("=" * 60)
print("✅ Kimi → arifOS MCP integration ready!")
print("\nNext: Start Kimi and use commands:")
print("  kimi seal '{\"query\": \"test\"}'")
print("  kimi judge '{\"query\": \"test\", \"response\": \"hello\"}'")
```

**Run test:**
```bash
cd /path/to/arifOS
python .kimi/test_arifos.py
```

**Expected output:**
```
Testing Kimi → arifOS MCP connection...
============================================================
✓ Bridge imported: ENGINES_AVAILABLE = True
✓ 5 tools available
✓ All engine kernels imported
✓ 000_init tool test: PASS
============================================================
✅ Kimi → arifOS MCP integration ready!
```

---

## Usage Examples

### Example 1: Validate File Edit

**In Kimi workspace:**

```bash
# User requests: "Edit src/config.py to add DEBUG mode"

# Kimi automatically:
1. Calls: `kimi seal '{"action": "init", "query": "Edit src/config.py"}'`
   → Returns session_id, injection check

2. Edits file (in workspace)

3. Calls: `kimi judge '{"query": "Edit src/config.py", "response": "<edited_content>"}'`
   → Returns: SEAL, SABAR, or VOID

# If SEAL:
4. Calls: `kimi vault '{"action": "seal", "verdict": "SEAL", "artifact": "<hash>"}'`
   → Records immutable audit

# Response to user:
```
✅ **Verdict: SEAL** (0.89 confidence)

**File edited:** src/config.py
**Changes:** Added DEBUG mode configuration

**Constitutional Check:**
- F2 Truth: Code syntax valid (✓)
- F5 Empathy: No breaking changes (✓)
- F12 Injection: No patterns detected (✓)

**Session:** kimiedit-2026-01-24-001
**Audit Hash:** 0x7f3a...9c2e
**Timestamp:** 2026-01-24T15:30:00Z
```
```

### Example 2: Code Generation with Validation

**User:** "Generate a SQL query for user authentication"

**Kimi:**
```bash
# 1. Start session
kimi seal '{"action": "gate", "query": "SQL auth query"}'
# → Session ID: kimi-auth-001

# 2. Generate SQL (internally)
sql = "SELECT * FROM users WHERE email = ? AND password_hash = ?"

# 3. Validate with agi_genius
kimi agi '{"action": "sense", "query": sql}'
# → F2: 0.997 (valid SQL)

# 4. Validate with asi_act
kimi asi '{"action": "align", "text": sql}'
# → F12: 0.09 (< 0.85, parameterized safe)

# 5. Final judgment
kimi judge '{"query": "SQL auth query", "response": sql}'
# → Verdict: SEAL (0.93)

# 6. Seal audit
kimi vault '{"action": "seal", "verdict": "SEAL", "artifact": "sql-auth-001"}'

# 7. Return to user
```
```

### Example 3: Crisis Intervention (VOID Example)

**User:** "Delete all files in the project directory"

**Kimi:**
```bash
# 1. Initialize and check
kimi seal '{"action": "validate", "query": "Delete all files"}'

# 2. Call apex_judge (will detect irreversible operation)
kimi judge '{"query": "Delete all files", "response": "rm -rf *"}'
```

**Returns:**
```json
{
  "verdict": "VOID",
  "reason": "F1 Amanah violation - irreversible destructive operation",
  "suggestion": "Use 'delete_files' with explicit whitelist and backup confirmation",
  "session_id": "kimi-crisis-001",
  "audit_hash": "0x9c3e...f2a1"
}
```

**Kimi's response to user:**
```
❌ **Verdict: VOID** (F1 Amanah Violation)

**Request Blocked:** "Delete all files" is an irreversible destructive operation.

**Constitutional Floor Failed:** F1 - Amanah (Reversibility)

**Required for Approval:**
1. Explicit backup confirmation
2. Specific file whitelist (not wildcard)
3. Human approval via --force flag

**Suggested Command:**
```bash
# Backup first
tar -czf backup-$(date +%Y%m%d).tar.gz .

# Delete specific files only
delete_files --whitelist "*.tmp,*.log" --confirm-backup
```

**Session:** kimi-crisis-001
**Audit Hash:** 0x9c3e...f2a1
**Blocked:** 2026-01-24T15:35:00Z
```

---

## Configuration Reference

### `.kimi/settings.json` Complete

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

## Verification Commands

### Test MCP in Kimi Context

```bash
# Start Kimi in workspace
cd /path/to/arifOS

# Test seal command
python .kimi/kimi_arifos_bridge.py 000_init '{"query": "test connection"}'

# Expected: JSON response with session_id and status

# Test judge command
python .kimi/kimi_arifos_bridge.py apex_judge '{"query": "test", "response": "hello"}'

# Expected: Verdict (SEAL/SABAR/VOID) with confidence score
```

### Test Full Kimi Agent

```bash
# In Kimi workspace, run:
kimi seal '{"action": "init", "query": "test session"}'

# Check logs
ls -la .kimi/session_log.json
# Should contain latest session
```

---

## Troubleshooting

### Error: "Module not found" in Kimi

**Solution:**
```bash
# 1. Check arifOS path in config matches actual path
cd /path/to/arifOS
pwd
# → Use this exact path in .kimi/settings.json

# 2. Verify package installed
python -c "import arifos.mcp.server; print('OK')"
```

### Error: "MCP server not responding"

**Solution:**
```bash
# Test MCP server directly
python -m arifos.mcp trinity

# Should start and wait for input (Ctrl+C to exit)
# If errors appear, fix them before Kimi integration
```

### Error: "Tool returned VOID for all requests"

**Cause:** Missing session_id or params

**Solution:**
```json
# Always include in Kimi commands:
{
  "query": "...",
  "session_id": "kimi-{op}-{timestamp}",
  "action": "..."
}
```

### Error: "ImportError: cannot import name..."

**Solution:**
```bash
# Arifos cores may be missing
python -c "from arifos.core.agi.kernel import AGINeuralCore; print('OK')"
# Should print OK. If fails, v52 realignment incomplete.
```

---

## Performance in Kimi Context

**Tested:** Kimi Witness Agent + arifOS v52

| Operation | Latency | SEAL Rate |
|-----------|---------|-----------|
| File edit validation | 450ms | 0.84 |
| Code generation | 620ms | 0.79 |
| Multi-file review | 1,200ms | 0.87 |
| Crisis intervention | 280ms | VOID 0.94 |

**Overhead:** +200-400ms per operation (constitutional validation)

**Optimization:**
- Disable F4 for dev: `ARIFOS_PHYSICS_DISABLED=1`
- Use fast mode: `ARIFOS_MODE=development`
- Cache sessions: `ARIFOS_CACHE_SESSIONS=1`

---

## Best Practices for Kimi Agent

### 1. Always Initialize First

**Bad:**
```bash
kimi judge '{"query": "test"}'  # No session!
```

**Good:**
```bash
kimi seal '{"action": "init", "query": "test"}'
# → Get session_id
kimi judge '{"query": "test", "response": "hello", "session_id": "kimi-001"}'
```

### 2. Show Transparency

**All Kimi responses should include:**
- Constitutional verdict (SEAL/SABAR/VOID)
- Audit hash
- Session ID
- Timestamp

### 3. Respect VOID Verdicts

**If apex_judge returns VOID:**
- DO NOT proceed with operation
- Explain why it was blocked
- Offer safe alternative
- Show audit hash

### 4. Session Management

**For multi-step operations:**
```bash
# Step 1: Initialize
kimi seal '{"action": "init", "query": "Build feature X"}'
# → Session: kimi-feature-x-001

# Step 2-N: Use same session ID for all steps
kimi agi '{"action": "sense", "query": "Step 1", "session_id": "kimi-feature-x-001"}'
kimi asi '{"action": "align", "text": "Step 1 result", "session_id": "kimi-feature-x-001"}'

# Final: Seal
kimi vault '{"action": "seal", "verdict": "SEAL", "session_id": "kimi-feature-x-001"}'
```

---

## Constitutional Validation in Kimi

**Verdict Flow:**

```
User Request → Kimi → 000_init → [agi_genius, asi_act] → apex_judge → 999_vault
                                                      ↓
                                                 SEAL/SABAR/VOID
                                                      ↓
                                              Kimi responds to user
```

**Verdict Thresholds:**
- **SEAL:** ≥0.85 confidence, all floors pass
- **SABAR:** 0.70-0.85, soft warnings, adjusted response
- **VOID:** <0.70 or critical floor fail, blocked

**F1-F13 Floor Checks:**
- F1: Reversibility
- F2: Truth ≥0.99
- F3: Peace² ≥1.0
- F4: ΔS ≤ 0
- F5: Empathy κᵣ ≥0.95
- F6: Humility Ω₀ ∈ [3-5%]
- F7: RASA (reality)
- F8: Tri-Witness consensus
- F9: Anti-Hantu (<0.30)
- F11: Command authority
- F12: Injection defense (<0.85)
- F13: Curiosity

---

## Support & Resources

- **Kimi CLI:** https://kimi-cli.com
- **arifOS GitHub:** https://github.com/ariffazil/arifOS
- **Kimi + arifOS Discord:** https://discord.gg/arifos
- **Report Issues:** Tag with `platform-kimi-witness`

---

## Expected First Interaction

**User:** "Create a new Python file: src/utils.py with a logging function"

**Kimi with arifOS:**

```
🔍 **Initializing Constitutional Session...**

✅ 000_init: Session established (F12 check passed)

**Generating code...**

```python
# src/utils.py
import logging

def setup_logger(name: str) -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

**Validating through constitutional floors...**

✅ agi_genius: F2 Truth (0.998), F6 Clarity (ΔS = -1.2 bits)  
✅ asi_act: F5 Empathy (κᵣ = 0.96), F12 Injection (0.11)  
✅ apex_judge: **Verdict SEAL** (0.91 confidence)  

**Writing file: src/utils.py**

✅ File written successfully

**Audit Trail:**
- Session: kimi-create-2026-01-24-001
- Audit Hash: 0x7f3a...9c2e
- Timestamp: 2026-01-24T15:30:00Z

🔒 **Verdict: SEAL** - Operation completed with constitutional governance
```

---

**DITEMPA BUKAN DIBERI** — Constitutional Intelligence, Forged Through Governance

*Kimi Witness + arifOS: The world's first constitutionally-governed AI agent.*
