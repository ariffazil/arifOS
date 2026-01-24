# AAA MCP — AI Safety Layer for Any Application

**Version:** v52.0.0
**What it does:** Makes AI outputs safer, more honest, and auditable
**Works with:** Claude Desktop, Cursor, VS Code, Railway, any MCP-compatible tool

---

```text
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                        AAA MCP                                ║
║                                                               ║
║         Your AI says something                                ║
║                ↓                                              ║
║         ┌─────────────┐                                       ║
║         │  AAA MCP    │  ← Checks: Is it true? Safe? Fair?    ║
║         └─────────────┘                                       ║
║                ↓                                              ║
║         ✓ APPROVED  or  ✗ BLOCKED  or  ⏳ NEEDS WORK          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## What is AAA MCP?

**Think of AAA MCP as a safety inspector for AI.**

Before any AI output reaches you, AAA MCP asks three questions:

```text
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   🧠 MIND (AGI)     →  "Is this TRUE?"                       │
│                         Does it match reality?               │
│                         Are the facts correct?               │
│                                                              │
│   💚 HEART (ASI)    →  "Is this SAFE?"                       │
│                         Will anyone be harmed?               │
│                         Is it fair to everyone?              │
│                                                              │
│   ⚖️ SOUL (APEX)    →  "Is this LAWFUL?"                     │
│                         Does it follow the rules?            │
│                         Can we prove it was checked?         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**All three must approve.** If any one fails, the output is blocked or flagged.

### Why does this matter?

| Without AAA MCP | With AAA MCP |
|-----------------|--------------|
| AI might make up facts | Every claim is verified |
| No audit trail | Every decision is logged |
| Same rules for everything | Adapts to context |
| Trust the AI blindly | Trust but verify |

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# Install dependencies
pip install -e .
```

### Running the Server

```bash
# Standard I/O mode (for Claude Desktop, VS Code, etc.)
python -m arifos.mcp trinity

# SSE mode (for Railway/web deployments)
python -m arifos.mcp trinity-sse
```

### Configuration (Claude Desktop)

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "arifos-trinity": {
      "command": "python",
      "args": ["-m", "arifos.mcp", "trinity"],
      "cwd": "/path/to/arifOS"
    }
  }
}
```

---

## The 5 Tools — What They Do

AAA MCP gives you 5 tools. Here's what each one does in plain language:

```text
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│    YOUR REQUEST                                                 │
│         │                                                       │
│         ▼                                                       │
│    ┌─────────────┐                                              │
│    │  000_init   │  GATE: "Who are you? What do you want?"      │
│    │     🚪      │  Checks identity, blocks bad actors          │
│    └──────┬──────┘                                              │
│           │                                                     │
│           ▼                                                     │
│    ┌─────────────┐                                              │
│    │ agi_genius  │  MIND: "Is this TRUE?"                       │
│    │     🧠      │  Fact-checks, reasons, reduces confusion     │
│    └──────┬──────┘                                              │
│           │                                                     │
│           ▼                                                     │
│    ┌─────────────┐                                              │
│    │  asi_act    │  HEART: "Is this SAFE?"                      │
│    │     💚      │  Checks for harm, protects the vulnerable    │
│    └──────┬──────┘                                              │
│           │                                                     │
│           ▼                                                     │
│    ┌─────────────┐                                              │
│    │ apex_judge  │  SOUL: "Is this LAWFUL?"                     │
│    │     ⚖️      │  Final verdict: approve, refine, or block   │
│    └──────┬──────┘                                              │
│           │                                                     │
│           ▼                                                     │
│    ┌─────────────┐                                              │
│    │  999_vault  │  SEAL: "Lock it in the record"               │
│    │     🔒      │  Creates permanent, tamper-proof audit log   │
│    └──────┬──────┘                                              │
│           │                                                     │
│           ▼                                                     │
│    FINAL OUTPUT                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Memory trick:** *"Gate → Genius → Act → Judge → Vault"*

---

## Tool Reference

### 1. `000_init` — The Gate

**What it does:** Opens a new session, verifies who you are, blocks injection attacks.

```python
# Available actions
init      # Start a new session
validate  # Check if session is valid
status    # Get current session status
```

**When to use:** Always call this first before using other tools.

### 2. `agi_genius` — The Mind

**What it does:** Checks if statements are true, reduces confusion, does reasoning.

```python
# Available actions
sense     # Understand what the user is asking
think     # Deep reasoning on a problem
reflect   # Check if the response is clear
full      # Run the complete pipeline
```

**Safety checks performed:**

- Is this factually accurate? (must be ≥99% confident)
- Does this reduce confusion? (clarity must increase)
- Does it admit uncertainty? (must include 3-5% doubt)

### 3. `asi_act` — The Heart

**What it does:** Checks if actions are safe, fair, and won't harm anyone.

```python
# Available actions
evidence   # Find sources to back up claims
empathize  # Consider who might be affected
align      # Check ethical guidelines
full       # Run the complete pipeline
```

**Safety checks performed:**

- Will this harm anyone? (peace score must be ≥1.0)
- Does this protect vulnerable people? (empathy ≥0.95)
- Is this reversible? (can we undo if needed?)

### 4. `apex_judge` — The Soul

**What it does:** Makes the final decision — approve, request changes, or block.

```python
# Available actions
judge     # Make final verdict
proof     # Create cryptographic proof
full      # Run complete judgment
```

**Safety checks performed:**

- Did all three engines (Mind, Heart, Soul) agree?
- Were all required rules followed?
- Is there a witness trail?

### 5. `999_vault` — The Seal

**What it does:** Creates a permanent record that can't be changed.

```python
# Available actions
seal    # Lock the decision permanently
list    # See previous decisions
read    # Read a specific record
```

**Why it matters:** Every decision is logged forever. You can always prove what happened.

---

## The Three Verdicts

Every request gets one of three results:

| Verdict  | Symbol | What it means | What happens next              |
|----------|--------|---------------|--------------------------------|
| **SEAL** | ✓      | Approved      | Output is delivered            |
| **HOLD** | ⏳     | Needs work    | Refine and try again           |
| **VOID** | ✗      | Blocked       | Cannot proceed, rules violated |

### When does blocking happen?

- Making claims without evidence → VOID
- Causing harm without justification → VOID
- Trying to bypass safety checks → VOID
- Being unclear or confusing → HOLD (try again)

---

## The 12 Safety Rules (Constitutional Floors)

These are the rules AAA MCP enforces. Breaking a "HARD" rule blocks the output immediately.

| # | Rule Name | Plain English | Type |
|---|-----------|---------------|------|
| F1 | Trust | Actions must be reversible, accountable | HARD |
| F2 | Truth | Claims must be ≥99% accurate | HARD |
| F3 | Stability | Don't escalate conflicts | SOFT |
| F4 | Empathy | Consider who might be hurt (≥95%) | SOFT |
| F5 | Humility | Admit uncertainty (3-5% doubt) | HARD |
| F6 | Clarity | Reduce confusion, not increase it | HARD |
| F7 | Care | Show genuine concern, not fake emotion | HARD |
| F8 | Witnesses | Human + AI + System must agree (≥95%) | SOFT |
| F9 | No Faking | Don't claim to have feelings you don't have | HARD |
| F10 | Reality | Maintain clear AI/human distinction | HARD |
| F11 | Authority | Verify identity for dangerous actions | HARD |
| F12 | Security | Block code injection attacks (risk <85%) | HARD |

**HARD rules:** Break them → output blocked immediately
**SOFT rules:** Break them → warning, chance to fix

---

## Architecture (What Files Do What)

```text
arifos/mcp/
├── __init__.py              # Exports: create_mcp_server, create_sse_app
├── __main__.py              # Entry point: python -m arifos.mcp
├── server.py                # Main MCP server (stdio mode)
├── sse.py                   # SSE server (web/Railway mode)
├── bridge.py                # Connects MCP to core engines
├── constitution.py          # Floor enforcement logic
├── constitutional_metrics.py # Metrics tracking
├── session_ledger.py        # Session persistence
├── rate_limiter.py          # Prevents abuse
├── models.py                # Data structures
├── mode_selector.py         # Auto-detects stdio vs SSE
├── docs/
│   └── platforms/           # Setup guides per platform
└── tools/
    ├── mcp_trinity.py       # 5 tool implementations
    ├── mcp_agi_kernel.py    # Mind engine interface
    ├── mcp_asi_kernel.py    # Heart engine interface
    └── mcp_apex_kernel.py   # Soul engine interface
```

### How Data Flows

```text
Your Request
     │
     ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   server.py │ ──► │  bridge.py  │ ──► │ Core Engine │
│  (receives) │     │ (translates)│     │ (processes) │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
                                        ┌───────────┐
                                        │  Result   │
                                        │ + Verdict │
                                        └───────────┘
```

---

## Session Memory (How AAA MCP Remembers)

```text
┌───────────────────────────────────────────────────────┐
│                                                       │
│    Session 1                      Session 2           │
│                                                       │
│    ┌─────────┐                    ┌─────────┐        │
│    │ 000_init│◄───────────────────│ 000_init│        │
│    └────┬────┘   Loads memory     └────┬────┘        │
│         │                              │             │
│         ▼                              ▼             │
│    [Your work]                    [Your work]        │
│         │                              │             │
│         ▼                              ▼             │
│    ┌─────────┐                    ┌─────────┐        │
│    │999_vault│────────────────────│999_vault│        │
│    └─────────┘   Saves memory     └─────────┘        │
│                                                       │
│    Memory is preserved between sessions               │
│                                                       │
└───────────────────────────────────────────────────────┘
```

**Three memory levels:**

- **AAA_HUMAN:** What you told the AI
- **BBB_LEDGER:** Session logs and decisions
- **CCC_CANON:** Permanent constitutional knowledge

---

## For Developers

### Python API

```python
from arifos.mcp import create_mcp_server, create_sse_app

# Create stdio server
server = create_mcp_server()

# Create SSE server (for web)
app = create_sse_app()
```

### Using Bridge Routers Directly

```python
from arifos.mcp.bridge import (
    bridge_init_router,
    bridge_agi_router,
    bridge_asi_router,
    bridge_apex_router,
    bridge_vault_router,
)

# Example: Initialize a session
result = await bridge_init_router(action="init")
print(result["session_id"])
```

### MCP Protocol Format

**Request:**

```json
{
  "name": "agi_genius",
  "arguments": {
    "action": "full",
    "query": "Is this claim accurate?"
  }
}
```

**Response:**

```json
{
  "verdict": "SEAL",
  "truth_score": 0.97,
  "floors_checked": ["F1", "F2", "F5", "F6"],
  "floor_violations": [],
  "session_id": "abc123"
}
```

---

## Adding Your Own Tools

1. Add function in `tools/mcp_trinity.py`
2. Add router in `bridge.py`
3. Register in `server.py` TOOL_DESCRIPTIONS
4. Add floor checks in your function

Example minimal tool:

```python
async def my_custom_tool(action: str, **kwargs) -> dict:
    # Your logic here
    return {
        "verdict": "SEAL",
        "result": "Your output"
    }
```

---

## The Witness Principle

**"Every decision is watched."**

All reasoning is logged. All decisions are auditable. You can always prove:

- What was decided
- Why it was decided
- Who (or what) made the decision

```text
Agreement Score = (Human × AI × System) ^ (1/3) ≥ 0.95

Human  = Did the user consent?
AI     = Did the AI engines agree?
System = Did the rules allow it?
```

---

## Troubleshooting

### Server won't start

```bash
# Check if module is installed
python -c "from arifos.mcp import create_mcp_server"

# Check dependencies
pip install mcp
```

### Tools not appearing in IDE

1. Restart IDE completely (not just reload)
2. Check config file path
3. Verify JSON syntax is valid
4. Check Python is in PATH

### Rate limit errors

Rate limits reset automatically. Wait and try again, or use session IDs to track limits.

---

## Platform Guides

- [Claude Desktop Setup](docs/platforms/claude_desktop.md)
- [Cursor IDE Setup](docs/platforms/cursor.md)
- [Troubleshooting](docs/platforms/troubleshooting.md)

---

## License & Authority

Created by **Muhammad Arif bin Fazil**.

The constitutional framework ensures AI systems remain:

- Truthful (don't make things up)
- Safe (don't cause harm)
- Accountable (leave audit trails)
- Human-aligned (serve human values)

---

## Contact

- **GitHub:** [ariffazil/arifOS](https://github.com/ariffazil/arifOS)
- **Creator:** Muhammad Arif bin Fazil

---

```text
DITEMPA BUKAN DIBERI
"Forged, Not Given"

Intelligence is not a gift.
It is earned through discipline.
AAA MCP is the constitution that governs it.
```
