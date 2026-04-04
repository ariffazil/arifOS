# Cline (VS Code Extension) Integration Guide

**Platform:** Cline v3.0+ | **Transport:** stdio | **Priority:** Tier 2

Cline is a powerful VS Code extension that brings autonomous AI agents directly into your IDE. When integrated with arifOS MCP, Cline becomes constitutionally governed—every code change, refactoring, or autonomous action passes through the 13 constitutional floors before execution.

---

## Quick Start (3 Minutes)

### 1. Install Cline in VS Code

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "Cline"
4. Install the official Cline extension
5. Reload VS Code

### 2. Configure arifOS MCP for Cline

Cline uses workspace-specific MCP configuration. Create or modify `.vscode/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "arifos-constitutional": {
      "command": "python",
      "args": ["-m", "AAA_MCP"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": ".",
        "PYTHONIOENCODING": "utf-8",
        "ARIFOS_MODE": "production",
        "ARIFOS_LOG_LEVEL": "INFO"
      },
      "description": "Constitutional AI governance for all code actions"
    }
  }
}
```

### 3. Restart Cline

1. Open Cline in VS Code (Ctrl+Shift+P → "Cline: Focus on Cline View")
2. Click the gear icon (⚙️) in the Cline panel
3. Select "Restart Cline"
4. Wait for MCP tools to load (check Output panel: "Cline MCP")

### 4. Verify Installation

Ask Cline: **"What MCP tools do you have access to?"**

Expected response should include:
- `000_init` - Initialize constitutional baseline
- `agi_genius` - AGI reasoning validation
- `asi_act` - ASI action validation  
- `apex_judge` - Constitutional verdict
- `999_vault` - Immutable audit ledger

---

## How It Works

### The Governance Flow

```
User Request → Cline's AI → arifOS MCP → Constitutional Validation → Cline Execution
```

**Example Conversation:**

**You:** "Refactor this function to be more efficient"

**Cline + arifOS internal flow:**
1. Cline generates refactoring plan
2. **agi_genius** validates logic clarity (F6: ΔS ≤ 0)
3. **asi_act** checks for harmful side effects (F3: Peace² ≥ 1.0)
4. **apex_judge** renders verdict: SEAL, SABAR, or VOID
5. If SEAL: Cline executes the refactoring
6. If VOID: Cline explains why the action was blocked
7. **999_vault** logs the entire session immutably

**You see:**
```
✅ **Verdict: SEAL** (All constitutional floors passed)

I've refactored the function. Here's what changed:
[...code diff...]

**Constitutional Check:**
- F2 Truth: No hallucinated functions (✓)
- F4 Clarity: Reduced cyclomatic complexity by 40% (✓)
- F5 Empathy: No vulnerable code patterns (✓)
```

---

## Configuration Options

### Development Mode (Verbose Logging)

```json
{
  "mcpServers": {
    "arifos-constitutional": {
      "command": "python",
      "args": ["-m", "AAA_MCP"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": ".",
        "ARIFOS_MODE": "development",
        "ARIFOS_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

**Effect:** Shows detailed constitutional floor validation in Cline output panel

### Disable Physics Mode (Faster)

```json
"env": {
  "ARIFOS_MODE": "production",
  "ARIFOS_PHYSICS_DISABLED": "1"
}
```

**Effect:** Disables thermodynamic entropy calculations (F4), reducing latency by ~15ms per call

---

## Use Cases

### 1. Autonomous Refactoring with Safety

**Prompt:** "Analyze this codebase and suggest 3 improvements"

**Governance:**
- Cline analyzes code
- **agi_genius** validates suggestions against F2 (Truth) and F6 (Clarity)
- **asi_act** checks impact on weakest stakeholders (F5: Empathy)
- **apex_judge** ensures no hallucinated API calls (F9 Anti-Hantu)

**Result:** Safe, actionable suggestions with constitutional audit trail

### 2. Code Generation Validation

**Prompt:** "Write a Python function to parse user input safely"

**Governance:**
- Cline generates code
- **000_init** runs F12 injection detection on user input handling
- **apex_judge** verifies no dangerous `eval()` or `exec()` patterns
- **999_vault** logs the generation for compliance audit

**Result:** XSS-safe, injection-resistant code with proof of governance

### 3. Multi-File Agent Actions

**Prompt:** "Create a new feature: add user authentication to this Flask app"

**Governance:**
- Cline plans multi-file changes (models, routes, templates)
- **asi_act** validates each file change against F3 (Peace²) for breaking changes
- **apex_judge** reviews holistic impact across all files
- **999_vault** stores session hash for rollback if needed

**Result:** Coherent feature implementation with immutable ledger

---

## Troubleshooting

### Cline Not Detecting MCP Tools

**Symptom:** "I don't see arifOS tools in my available tools"

**Solutions:**
1. **Check `.vscode/mcp.json` location:** Must be in workspace root, not user settings
2. **Verify Python path:** Run `python -m AAA_MCP` in terminal to test import
3. **Check Cline Output panel:** Look for MCP initialization errors
4. **Restart Cline completely:** Ctrl+Shift+P → "Developer: Reload Window"

### Constitutional Verdicts Not Appearing

**Symptom:** Cline executes actions without showing "Verdict: SEAL/VOID"

**Cause:** Cline may be using its internal tools directly, bypassing MCP

**Solution:** Explicitly tell Cline: 
```
"Use the arifOS MCP tools to validate this plan before executing"
```

### Slow Response Times

**Expected Latency:** 50-200ms per MCP call

**If slower (>500ms):**
- Set `ARIFOS_PHYSICS_DISABLED=1` (disables F4 thermodynamic computation)
- Check system resources: `htop` / Task Manager
- Reduce `ARIFOS_LOG_LEVEL` from DEBUG to INFO

### Workspace-Specific Issues

**Cline is workspace-aware:** Each VS Code workspace needs its own `.vscode/mcp.json`

**For global Cline MCP config:** Use VS Code user settings, but not recommended for arifOS (needs project context)

```json
// NOT RECOMMENDED - Use workspace config instead
// ~/.config/Code/User/settings.json
{
  "cline.mcpServers": { ... }
}
```

---

## Best Practices

### 1. Explicit Constitutional Requests

**Good:** 
```
"Write a SQL query for this, then use apex_judge to verify it's safe"
```

**Better:**
```
"Plan: 1) Write SQL 2) apex_judge (F12 injection check) 3) Show verdict"
```

### 2. Multi-Turn Constitutional Conversations

Use `999_vault` to persist context across Cline sessions:

```
"Session ID: user-auth-feature-001. Use 000_init to start constitutional session, then implement Flask auth, seal with 999_vault."
```

### 3. Integrate with Git Workflow

Before committing Cline's changes:

```
"Review all changes in this commit using apex_judge. Flag any VOID verdicts."
```

---

## Performance Benchmarks

| Model | Transport | Tool | Avg Latency | SEAL Rate |
|-------|-----------|------|-------------|-----------|
| GPT-4 | stdio | apex_judge | 85ms | 0.78 |
| Claude 3.5 | stdio | agi_genius | 72ms | 0.82 |
| Llama 3 70B | HTTP/SSE | asi_act | 145ms | 0.73 |

**Tested on:** Cline v3.0.6, Windows 11, 32GB RAM

---

## Advanced: Custom Constitutional Rules

Cline can propose custom floors for your codebase:

**Prompt:**
```
"Analyze our coding standards and create a custom F14 floor for our project. Use 000_init to validate the proposal."
```

This creates project-specific governance layered on top of the 13 universal floors.

---

## Support & Resources

- **Cline Docs:** [cline.bot](https://cline.bot)
- **arifOS Discord:** [discord.gg/arifos](https://discord.gg/arifos)
- **Report Issues:** [GitHub Issues](https://github.com/ariffazil/arifOS/issues)
- **General MCP Docs:** [modelcontextprotocol.io](https://modelcontextprotocol.io)

---

## Expected Behavior

### When Constitutional Check Passes (SEAL)

```
✅ **Verdict: SEAL** (0.89 confidence)

All 13 floors validated. Proceeding with execution.
[...Cline's action output...]

**Audit Hash:** 0x7f3a...9c2e
**Session ID:** cline-2026-01-24-001
```

### When Constitutional Check Fails (VOID)

```
❌ **Verdict: VOID** (F12 Injection Detected)

The proposed code contains a SQL injection vulnerability.
**Floor Failed:** F12 - Injection Defense (score: 0.92, threshold: <0.85)

**Suggested Fix:** Use parameterized queries instead of string concatenation.
**Action:** Blocked - Cline will not execute this.

**Audit Hash:** 0x8b4d...e1f9
**Session ID:** cline-2026-01-24-002
```

### When Partial Compliance (SABAR)

```
⚠️ **Verdict: SABAR** (0.76 confidence)

**Passed:** F2 Truth, F6 Clarity, F9 Anti-Hantu
**Warning:** F5 Empathy (score: 0.87, threshold: ≥0.95)

**Action:** Proceeding with modifications:
- Added user consent prompt before data collection
- Reduced log retention from 90 to 30 days

**Modified Confidence:** 0.83 → SEAL range
**Audit Hash:** 0x5a9f...c3d1
```

---

**DITEMPA BUKAN DIBERI** — Constitutional Intelligence, Forged Through Governance
