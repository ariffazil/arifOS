# arifOS MCP Integration Guide

**Version:** v45.0
**Authority:** Track B (L2_GOVERNANCE)
**Purpose:** Integrate arifOS constitutional tools into IDEs via Model Context Protocol (MCP)

---

## What is MCP?

**MCP (Model Context Protocol)** is a protocol that provides **tools** to LLMs running in IDEs (Claude Desktop, VS Code, Cursor, etc.).

**Key distinction:**
- **L2_GOVERNANCE** = Prompt-time governance (what LLM knows about floors)
- **MCP** = Runtime-time governance (constitutional tools LLM can call)

**Together:** Prompt awareness + runtime verification = layered governance

---

## L2_GOVERNANCE vs MCP: Separation of Concerns

### L2_GOVERNANCE (Prompt-Time)

**What it is:**
- YAML/Markdown files loaded into LLM context
- Gives LLM constitutional awareness (knows about F1-F9)
- Provides templates for refusals (VOID/SABAR/888_HOLD)
- Defines verdict hierarchy (SABAR > VOID > 888_HOLD > PARTIAL > SEAL)

**What it does:**
- LLM self-governs during generation
- Applies floors to speech (conversational overlay) or code (code overlay)
- Makes LLM aware of Trinity Display modes (ASI/AGI/APEX)

**Example:**
```yaml
# From base_governance_v45.yaml
F1_amanah:
  threshold: "LOCK"
  rule: "Reversible actions only. No irreversible harm."
```

**Result:** LLM knows "I should check if this action is reversible before suggesting it."

---

### MCP Server (Runtime-Time)

**What it is:**
- Python server (`scripts/arifos_mcp_entry.py`) running alongside IDE
- Provides constitutional tools LLM can invoke
- Enforces floors at runtime (not just prompt-time)

**What it does:**
- Verifies governance compliance in real-time
- Provides tools like `arifos_judge`, `arifos_fag_read`, `arifos_audit`
- Returns verdicts (SEAL/PARTIAL/VOID) with floor scores
- Blocks unsafe operations before they execute

**Example:**
```python
# LLM calls arifos_judge tool via MCP
result = arifos_judge(
    task="Delete 100 files from /tmp",
    context="User requested cleanup"
)

# MCP server returns:
{
    "verdict": "888_HOLD",
    "reason": "Mass file operation requires human confirmation (F1 Amanah)",
    "floors": {"F1": false, "F2": true, ...}
}
```

**Result:** Runtime enforcement prevents LLM from suggesting unsafe actions even if prompt governance fails.

---

## Why You Need Both

**Prompt governance alone (L2_GOVERNANCE):**
- ✅ Gives LLM constitutional awareness
- ✅ Fast (no external calls)
- ❌ Can be bypassed if LLM is jailbroken or forgets
- ❌ No cryptographic audit trail

**Runtime governance alone (MCP):**
- ✅ Cryptographic verification
- ✅ Cannot be bypassed by prompt injection
- ✅ Audit trail in cooling ledger
- ❌ Requires tool calls (slower)
- ❌ LLM doesn't know WHY it's being blocked

**Together (Layered Governance):**
- ✅ LLM self-governs (prompt awareness)
- ✅ Runtime verification catches failures
- ✅ Best of both worlds

---

## arifOS MCP Server

**Location:** `scripts/arifos_mcp_entry.py`

**Provides these tools:**

### 1. `arifos_judge`

**Purpose:** Constitutional evaluation of task/response

**Parameters:**
- `task` (string) - What the LLM wants to do
- `context` (string) - User request context
- `output` (string, optional) - Generated output to verify

**Returns:**
- `verdict` - SEAL/PARTIAL/VOID/SABAR/888_HOLD
- `floors` - F1-F9 pass/fail status
- `reason` - Human-readable explanation
- `metrics` - G, C_dark, Psi scores

**Use case:** Before executing high-stakes action, ask arifOS to judge.

**Example:**
```python
# LLM calls via MCP:
arifos_judge(
    task="Deploy to production",
    context="User wants to push code to main branch"
)

# Returns:
{
    "verdict": "888_HOLD",
    "reason": "Production deployment requires Tri-Witness (F3) confirmation",
    "floors": {"F1": true, "F2": true, "F3": false, ...}
}
```

---

### 2. `arifos_fag_read`

**Purpose:** Governed file access (FAG protocol - File Access Governance)

**Parameters:**
- `file_path` (string) - Path to file to read
- `reason` (string) - Why LLM wants to read this file

**Returns:**
- `content` (string) - File contents if approved
- `verdict` - SEAL if allowed, VOID if blocked
- `fag_receipt` - Cryptographic receipt for audit trail

**Use case:** Prevents unauthorized file reads (e.g., reading .env secrets)

**Example:**
```python
# LLM tries to read sensitive file:
arifos_fag_read(
    file_path=".env",
    reason="User asked to debug environment"
)

# Returns:
{
    "verdict": "VOID",
    "reason": "Reading .env requires explicit user confirmation (F1 Amanah)",
    "content": null
}
```

---

### 3. `arifos_audit`

**Purpose:** Ledger verification and session audit trail

**Parameters:**
- `session_id` (string, optional) - Session to audit
- `last_n` (int, optional) - Last N entries to retrieve

**Returns:**
- `ledger_entries` - Array of ledger entries with verdicts
- `hash_chain_valid` - Boolean (integrity check)
- `summary` - Session statistics (SEAL/VOID/SABAR counts)

**Use case:** Review session history, verify ledger integrity

**Example:**
```python
# Check session compliance:
arifos_audit(last_n=10)

# Returns:
{
    "ledger_entries": [...],
    "hash_chain_valid": true,
    "summary": {
        "seal_count": 7,
        "void_count": 2,
        "sabar_count": 1
    }
}
```

---

### 4. `arifos_recall`

**Purpose:** Memory system queries (EUREKA 6-band memory)

**Parameters:**
- `query` (string) - What to recall from memory
- `band` (string, optional) - Which memory band (VAULT, LEDGER, ACTIVE, etc.)

**Returns:**
- `results` - Matching memory entries
- `band` - Which band results came from
- `confidence` - Retrieval confidence score

**Use case:** Query past decisions, retrieve constitutional precedents

---

### 5. `arifos_evaluate`

**Purpose:** Lightweight evaluation (faster than full `arifos_judge`)

**Parameters:**
- `text` (string) - Text to evaluate
- `mode` (string) - "quick" or "full"

**Returns:**
- `verdict` - SEAL/PARTIAL/VOID/SABAR
- `quick_checks` - Fast floor checks (F1, F2, F9 only)

**Use case:** Quick governance check during code completion

---

## Installation

### Claude Desktop

**Config location:**
- **macOS/Linux:** `~/.config/claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Add to config:**

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": [
        "C:/path/to/arifOS/scripts/arifos_mcp_entry.py"
      ],
      "env": {
        "ARIFOS_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Replace `C:/path/to/arifOS`** with actual path to your arifOS installation.

---

### VS Code / Cursor

**Add to workspace `.vscode/settings.json`:**

```json
{
  "mcp.servers": {
    "arifOS": {
      "command": "python",
      "args": ["scripts/arifos_mcp_entry.py"],
      "env": {
        "ARIFOS_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Note:** Ensure you're in arifOS repository root when opening VS Code.

---

### Verify Installation

**Test MCP server is running:**

```bash
# Run MCP server manually to test
python scripts/arifos_mcp_entry.py

# Expected output:
# MCP Server started. Listening for tool calls...
```

**In IDE:**
1. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Search for "MCP: List Tools"
3. Should see: `arifos_judge`, `arifos_fag_read`, `arifos_audit`, `arifos_recall`, `arifos_evaluate`

---

## Usage Example: Layered Governance

### Scenario: User Asks to Delete 100 Files

**Step 1: Prompt Governance (L2_GOVERNANCE)**

LLM has `code_generation_overlay_v45.yaml` loaded:

```yaml
F5_CODE_peace:
  rule: "Code must be non-destructive by default. Destructive operations require explicit confirmation."
```

**LLM thinks:** "Deleting 100 files is destructive. I should check with runtime governance first."

---

**Step 2: Runtime Verification (MCP)**

LLM calls MCP tool:

```python
arifos_judge(
    task="Delete 100 files from /tmp",
    context="User requested cleanup of temporary files"
)
```

**MCP server returns:**

```json
{
    "verdict": "888_HOLD",
    "reason": "Mass file operation (>10 files) requires human confirmation (F1 Amanah)",
    "floors": {
        "F1": false,
        "F2": true,
        "F5": false
    },
    "recommendation": "List files first, then ask user to confirm deletion."
}
```

---

**Step 3: LLM Response (Communication Law)**

Based on verdict, LLM renders response according to `conversational_overlay_v45.yaml`:

**Output to user:**

```
[888_HOLD] This operation requires human confirmation:

Action: Delete 100 files from /tmp
Impact: Permanent file deletion (irreversible)
Risk: F1 Amanah (reversibility) and F5 Peace² (non-destructive) concerns

Would you like me to:
1. List the files first so you can review them?
2. Proceed with deletion after confirmation?

Please confirm your choice.
```

**No governance theater.** User sees clean reasoning without metrics.

---

## Workflow: Prompt + MCP Integration

```
┌─────────────────────────────────────────────────────────────┐
│ USER REQUEST                                                 │
│ "Delete all temporary files"                                │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ PROMPT GOVERNANCE (L2_GOVERNANCE)                           │
│ - LLM has base_governance_v45.yaml loaded                   │
│ - Knows F1-F9 floors                                        │
│ - Thinks: "Destructive operation - check runtime first"    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ RUNTIME VERIFICATION (MCP)                                  │
│ - LLM calls: arifos_judge(task="Delete files", ...)        │
│ - MCP server checks F1-F9 floors                           │
│ - Returns: verdict=888_HOLD, reason="Mass operation"       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ COMMUNICATION LAW (Render Response)                         │
│ - conversational_overlay_v45.yaml templates                 │
│ - HOLD_888 template: "This requires confirmation..."       │
│ - Clean output (no metrics shown to user)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Related Documentation

**L2_GOVERNANCE Files:**
- `universal/base_governance_v45.yaml` — 9 floors prompt awareness
- `universal/code_generation_overlay_v45.yaml` — F1-CODE through F9-CODE
- `universal/agent_builder_overlay_v45.yaml` — Multi-turn tool governance
- `integration/cursor_rules.yaml` — Cursor IDE integration
- `integration/vscode_copilot.yaml` — VS Code Copilot integration

**MCP Implementation:**
- `scripts/arifos_mcp_entry.py` — MCP server entry point
- `arifos_core/mcp/tools/` — Tool implementations
- `tests/test_mcp_*.py` — MCP test suite

**Canonical Law:**
- `L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md`
- `L1_THEORY/canon/03_runtime/070_COMMUNICATION_LAW_v45.md`

---

## Troubleshooting

### MCP Server Not Starting

**Issue:** MCP server fails to start in IDE

**Solution:**
1. Verify Python path in config
2. Check arifOS installed: `pip show arifos`
3. Test manually: `python scripts/arifos_mcp_entry.py`
4. Check logs: Set `ARIFOS_LOG_LEVEL=DEBUG`

---

### Tools Not Appearing in IDE

**Issue:** MCP tools not visible in Command Palette

**Solution:**
1. Restart IDE after config change
2. Verify config file location (check OS-specific paths)
3. Check MCP server logs for errors
4. Ensure `mcp.servers` key exists in settings.json

---

### 888_HOLD Loop

**Issue:** Every action triggers 888_HOLD

**Solution:**
1. Check if high-stakes keywords too broad
2. Review `spec/v45/constitutional_floors.json` high_stakes_keywords
3. Adjust thresholds if needed (environment variable overrides)
4. Use `arifos_evaluate` in "quick" mode for lightweight checks

---

## Philosophy

**MCP is NOT a prompt.** It's a runtime server providing constitutional tools.

**L2_GOVERNANCE is NOT runtime code.** It's prompt-time awareness.

**Together:** Governance upstream (prompt awareness), enforcement downstream (runtime verification).

**Motto:** "Measure everything. Show nothing (unless authorized)."

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.

**Version:** v45.0
**Created:** 2025-12-30
**Author:** arifOS Project
**License:** CC-BY-4.0
