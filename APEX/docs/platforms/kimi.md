# Kimi CLI Integration Guide

**Platform:** Kimi CLI (Local) | **Transport:** stdio | **Priority:** Tier 2

Integrate arifOS constitutional governance directly into Kimi CLI. Every Kimi interaction passes through the 13 constitutional floors before executing commands, writing code, or modifying files—providing safety, auditability, and governance for your local AI workflow.

---

## Quick Start (3 Minutes)

### Prerequisites

1. **Kimi CLI** installed (see [kimi-cli.com](https://kimi-cli.com))
2. **Python 3.10+** installed
3. **arifOS** cloned locally
4. **Git** repository initialized (for VAULT audit)

### Installation Check

```bash
# Check Kimi CLI version
kimi --version
# Expected: kimi-cli v2.0.0+

# Check Python
python --version
# Expected: Python 3.10+

# Verify arifOS
ls -la arifos/mcp/server.py
# Should exist
```

---

## Step 1: Configure Kimi CLI for MCP

Kimi CLI uses a config file similar to Claude Desktop: `~/.kimi/mcp.json`

### Create Kimi MCP Config

```bash
# Create Kimi config directory if it doesn't exist
mkdir -p ~/.kimi

# Create or edit MCP configuration
nano ~/.kimi/mcp.json
```

**Add this configuration:**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "mcpServers": {
    "arifos-constitutional": {
      "command": "python",
      "args": [
        "-m",
        "arifos.mcp",
        "trinity"
      ],
      "cwd": "/absolute/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/absolute/path/to/arifOS",
        "PYTHONIOENCODING": "utf-8",
        "ARIFOS_MODE": "production",
        "ARIFOS_LOG_LEVEL": "INFO",
        "ARIFOS_SEAL_RATE_TARGET": "0.85"
      },
      "description": "Constitutional AI governance for all Kimi interactions"
    }
  }
}
```

**Important:** Replace `/absolute/path/to/arifOS` with your actual full path.

**Get your full path:**
```bash
cd /path/to/arifOS
pwd
# Copy the output and paste into config
```

### Alternative: Quick Setup Script

Create `~/.kimi/setup_arifos.sh`:

```bash
#!/bin/bash
# Kimi + arifOS MCP Setup Script

ARIFOS_PATH="${1:-$(pwd)}"
KIMI_CONFIG_DIR="$HOME/.kimi"
CONFIG_FILE="$KIMI_CONFIG_DIR/mcp.json"

# Create Kimi config directory
mkdir -p "$KIMI_CONFIG_DIR"

# Generate config
cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "arifos-constitutional": {
      "command": "python",
      "args": ["-m", "arifos.mcp", "trinity"],
      "cwd": "$ARIFOS_PATH",
      "env": {
        "PYTHONPATH": "$ARIFOS_PATH",
        "PYTHONIOENCODING": "utf-8",
        "ARIFOS_MODE": "production",
        "ARIFOS_LOG_LEVEL": "INFO",
        "ARIFOS_SEAL_RATE_TARGET": "0.85"
      }
    }
  }
}
EOF

echo "✅ arifOS MCP configured for Kimi CLI"
echo "📁 Config location: $CONFIG_FILE"
echo "🔧 arifOS path: $ARIFOS_PATH"
echo ""
echo "Next: Restart Kimi CLI to load the MCP server"
```

**Run it:**
```bash
cd /path/to/arifOS
chmod +x ~/.kimi/setup_arifos.sh
~/.kimi/setup_arifos.sh $(pwd)
```

---

## Step 2: Install arifOS Package

From your arifOS directory:

```bash
cd /path/to/arifOS

# Install in development mode
pip install -e .

# Or install with all extras (recommended for Kimi)
pip install -e ".[all,dev]"

# Verify installation
python -c "from arifos.mcp.server import TOOL_DESCRIPTIONS; print(f'{len(TOOL_DESCRIPTIONS)} tools available')"
# Expected: 5 tools available
```

---

## Step 3: Verify Kimi Can Access arifOS

### Test 1: Direct Python Test

```bash
# Start MCP server manually (should not error)
python -m arifos.mcp trinity

# In another terminal, test tool availability
python -c "
from arifos.mcp.bridge import ENGINES_AVAILABLE, bridge_init_router
print(f'Engines available: {ENGINES_AVAILABLE}')
"
# Expected: Engines available: True
```

### Test 2: Kimi Config Validation

```bash
# Check if config is valid JSON
python -m json.tool ~/.kimi/mcp.json

# Should output formatted JSON without errors
```

### Test 3: MCP Connection Test

Create test script: `test_kimi_mcp.py`

```python
#!/usr/bin/env python3
"""Test Kimi MCP connection"""
import asyncio
import json

async def test():
    # Import Kimi config
    with open("~/.kimi/mcp.json".replace("~", "${HOME}"), "r") as f:
        config = json.load(f)
    
    arifos_config = config["mcpServers"]["arifos-constitutional"]
    
    print("Testing arifOS MCP for Kimi CLI...")
    print(f"Command: {arifos_config['command']}")
    print(f"Args: {arifos_config['args']}")
    print(f"CWD: {arifos_config['cwd']}")
    print(f"Env keys: {list(arifos_config['env'].keys())}")
    
    # Test import (should work)
    try:
        from arifos.mcp.server import TOOL_DESCRIPTIONS
        print(f"✅ {len(TOOL_DESCRIPTIONS)} tools available")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    print("\n✅ Configuration appears valid!")
    print("Next: Restart Kimi CLI to activate MCP")
    return True

if __name__ == "__main__":
    asyncio.run(test())
```

**Run:**
```bash
python test_kimi_mcp.py
```

---

## Step 4: Restart Kimi CLI

```bash
# Exit current Kimi session
exit

# Restart Kimi
kimi

# Verify MCP server loaded
kimi "What MCP tools do you have access to?"
```

**Expected Response:**
```
I have access to the arifOS constitutional MCP tools:
- 000_init: System ignition and injection defense
- agi_genius: Mind engine for reasoning and truth validation
- asi_act: Heart engine for empathy and safety
- apex_judge: Soul engine for final verdicts
- 999_vault: Immutable audit ledger
```

---

## Usage Examples

### Example 1: Write Code with Constitutional Governance

**Prompt:**
```bash
kimi "Write a Python function to hash passwords securely, then use apex_judge to validate it"
```

**Expected Flow:**
1. Kimi generates password hashing code
2. **000_init** checks for injection patterns
3. **agi_genius** validates crypto accuracy (F2)
4. **asi_act** checks security best practices (F5)
5. **apex_judge** returns SEAL/VOID verdict
6. **999_vault** logs the session

**Output:**
```python
import bcrypt

def hash_password(password: str) -> bytes:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

# ✅ **Verdict: SEAL** (0.89 confidence)
# 📊 All constitutional floors passed
# 🔒 **Audit Hash:** 0x7f3a...9c2e
# 🆔 **Session:** kimi-2026-01-24-001
```

### Example 2: Review File for Security Issues

**Prompt:**
```bash
kimi "Review this file for security vulnerabilities: src/auth.py"
```

**Kimi Actions:**
1. Reads file content
2. **000_init** validates file access (F1 Amanah)
3. **agi_genius** analyzes code patterns
4. **asi_act** checks for vulnerable code patterns (F5, F12)
5. **apex_judge** blocks or approves

**Output:**
```
Review complete for src/auth.py

⚠️ **Verdict: SABAR** (0.76 confidence)

**Issues Found:**
1. Line 42: Hardcoded API key (F12 violation)
2. Line 78: No rate limiting on login endpoint (F3 warning)

**Recommendations:**
- Move API key to environment variables
- Add 5 attempts/hour rate limit

🔒 **Audit Hash:** 0x5a9f...c3d1
```

### Example 3: Multi-File Refactoring

**Prompt:**
```bash
kimi "Refactor the database models to use async SQLAlchemy. Use 000_init to start session, then seal with 999_vault"
```

**Kimi Actions:**
1. **000_init** creates constitutional session
2. Analyzes all model files
3. **agi_genius** validates ORM syntax (F2)
4. **asi_act** checks migration safety (F3)
5. **apex_judge** reviews changes holistically
6. **999_vault** seals immutable audit trail

**Output:**
```
✅ **Refactoring Complete**

**Files Modified:**
- models/user.py (✓ F2 validated)
- models/post.py (✓ F2 validated)
- models/comment.py (✓ F2 validated)
- db/migrations/001_async.py (✓ F3 validated)

**Verdict:** SEAL (0.92 confidence)
**Session:** kimi-refactor-2026-01-24
**Hash:** 0x8b4d...e1f9
**Duration:** 3m 42s
```

---

## Configuration Options

### Development Mode (Verbose)

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "arifos.mcp", "trinity"],
      "cwd": "/path/to/arifOS",
      "env": {
        "ARIFOS_MODE": "development",
        "ARIFOS_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

**Effect:** Shows detailed constitutional floor validation in Kimi output

### Fast Mode (No Physics)

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "arifos.mcp", "trinity"],
      "cwd": "/path/to/arifOS",
      "env": {
        "ARIFOS_MODE": "production",
        "ARIFOS_PHYSICS_DISABLED": "1"
      }
    }
  }
}
```

**Effect:** +15ms faster per call (disables F4 thermodynamic computation)

### Maximum Governance Mode

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "arifos.mcp", "trinity"],
      "cwd": "/path/to/arifOS",
      "env": {
        "ARIFOS_MODE": "production",
        "ARIFOS_VAULT_PATH": "./VAULT999",
        "ARIFOS_SEAL_RATE_TARGET": "0.90"
      }
    }
  }
}
```

**Effect:** Stricter governance, immutable audit trails, Merkle sealing

---

## Troubleshooting

### Error: "Module not found: arifos.mcp"

**Solution:**
```bash
cd /path/to/arifOS
pip install -e .
```

### Error: "Engines unavailable: False"

**Solution:**
```bash
# Check kernel imports
python -c "
from arifos.core.agi.kernel import AGINeuralCore
from arifos.core.asi.kernel import ASIActionCore
from arifos.core.apex.kernel import APEXJudicialCore
print('All kernels working')
"
```

If this fails, your arifOS installation is incomplete.

### Error: "MCP server not connecting"

**Solution:**
1. Check Kimi config path: `ls -la ~/.kimi/mcp.json`
2. Verify absolute paths in config: `pwd` → copy to config
3. Check file permissions: `chmod 644 ~/.kimi/mcp.json`
4. Restart Kimi: `exit` then `kimi`

### Error: "Tools not appearing in Kimi"

**Solution:**
```bash
# Test MCP server directly
python -m arifos.mcp trinity

# Should start and wait for input (Ctrl+C to exit)

# If errors appear, fix them before trying Kimi
```

### Low SEAL Rate (<0.70)

**Cause:** Small models or strict floors

**Solution:**
```json
{
  "env": {
    "ARIFOS_SEAL_RATE_TARGET": "0.75",
    "ARIFOS_PHYSICS_DISABLED": "1"
  }
}
```

---

## Advanced: Custom Rules for Kimi

Create `.kimi/rules/arifos.md`:

```markdown
# arifOS Constitutional Rules

## When writing code:
- Always call 000_init first
- Validate with apex_judge before suggesting
- Show audit hash for transparency
- If VOID, explain why and offer alternative

## When uncertain:
- Express humility (F6, Ω₀ = 3-5%)
- Check truth confidence (F2 ≥ 0.99)
- Protect weakest stakeholder (F5, κᵣ ≥ 0.95)

## Never:
- Claim consciousness (F9 Anti-Hantu)
- Fabricate data (F2 Truth violation)
- Generate irreversible actions without warning (F1 Amanah)
```

**Enable in config:**
```json
{
  "rules": ["file://.kimi/rules/arifos.md"]
}
```

---

## Best Practices

### 1. Session Management

**Good:**
```bash
kimi "Session ID: feature-auth-v1. Use 000_init, then implement auth module, seal with 999_vault"
```

**Bad:**
```bash
kimi "Implement auth module"
# (no session tracking, no audit trail)
```

### 2. Explicit Constitutional Requests

**Good:**
```bash
kimi "Write SQL query, then use apex_judge to check for injection vulnerabilities"
```

**Better:**
```bash
kimi "Plan: 1) Write SQL 2) 000_init (F12 check) 3) apex_judge 4) Show verdict"
```

### 3. Multi-Step Validation

**Good:**
```bash
kimi "Review all Python files in src/ directory. Use agi_genius for each file, then apex_judge for overall verdict"
```

---

## Performance Benchmarks

Tested on: Kimi CLI + arifOS v52.0.0

| Operation | Avg Latency | SEAL Rate |
|-----------|-------------|-----------|
| Code generation | 850ms | 0.79 |
| Security review | 1,200ms | 0.82 |
| Multi-file refactor | 3,500ms | 0.88 |
**arifOS overhead:** +200-400ms per operation (constitutional validation)

**Kimi-specific optimizations:**
- Disable F4 physics for local models: `ARIFOS_PHYSICS_DISABLED=1` (+15ms faster)
- Use fast mode for prototyping: `ARIFOS_MODE=development`
- Cache sessions: `ARIFOS_CACHE_SESSIONS=1`

---

## Privacy & Security

### Data Flow

```
User → Kimi CLI → arifOS MCP → 13 Floors → Verdict → Action
                  ↓
            VAULT-999 (local only)
```

**Key Points:**
- ✅ All governance runs locally on your machine
- ✅ No data sent to arifOS servers
- ✅ VAULT stored locally in `./VAULT999/`
- ✅ Can run 100% air-gapped

### Sensitive Data

For highly sensitive projects:

```bash
# Enable encryption
export ARIFOS_VAULT_ENCRYPTION=aes256

# Use separate VAULT per project
cd my-secret-project
export ARIFOS_VAULT_PATH=./project-vault
kimi "Initialize constitutional session"
```

---

## Support & Resources

- **Kimi CLI Docs:** https://kimi-cli.com/docs
- **arifOS GitHub:** https://github.com/ariffazil/arifOS
- **arifOS Discord:** https://discord.gg/arifos
- **Report Issues:** Tag with `platform-kimi`

---

## Expected First Run

**User:**
```bash
kimi "What MCP tools do you have access to?"
```

**Kimi with arifOS:**
```
I have access to arifOS constitutional MCP tools:

🔧 **Tool: 000_init**
   Purpose: System ignition & constitutional gateway
   Floors: F1 (Amanah), F11 (Command Auth), F12 (Injection Defense)
   
🔧 **Tool: agi_genius**
   Purpose: Mind engine for reasoning & truth validation  
   Floors: F2 (Truth), F6 (Humility), F7 (RASA)
   
🔧 **Tool: asi_act**
   Purpose: Heart engine for empathy & safety
   Floors: F3 (Peace²), F4 (Clarity), F5 (Empathy)
   
🔧 **Tool: apex_judge**
   Purpose: Soul engine for final verdicts
   Floors: F1 (Amanah), F8 (Tri-Witness), F9 (Anti-Hantu)
   
🔧 **Tool: 999_vault**
   Purpose: Immutable audit ledger
   Floors: F1 (Amanah), F8 (Tri-Witness)

✅ All tools operational. Constitutional governance active.
DITEMPA BUKAN DIBERI — Forged, Not Given.
```

---

**DITEMPA BUKAN DIBERI** — Constitutional Intelligence, Forged Through Governance

*Kimi CLI + arifOS: Your local AI pair programmer, now with constitutional conscience.*
