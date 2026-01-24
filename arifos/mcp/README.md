# AAA MCP — Constitutional AI Governance Protocol

**Version:** v52.0.0-SEAL  
**Authority:** arifOS Constitutional Framework  
**Status:** PRODUCTION (Unified with arifos.mcp)

---

```
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     █████╗  █████╗  █████╗     ███╗   ███╗ ██████╗██████╗    ║
    ║    ██╔══██╗██╔══██╗██╔══██╗    ████╗ ████║██╔════╝██╔══██╗   ║
    ║    ███████║███████║███████║    ██╔████╔██║██║     ██████╔╝   ║
    ║    ██╔══██║██╔══██║██╔══██║    ██║╚██╔╝██║██║     ██╔═══╝    ║
    ║    ██║  ██║██║  ██║██║  ██║    ██║ ╚═╝ ██║╚██████╗██║        ║
    ║    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝     ╚═╝ ╚═════╝╚═╝        ║
    ║                                                               ║
    ║         AGI × ASI × APEX — Model Context Protocol             ║
    ║                                                               ║
    ║                  DITEMPA BUKAN DIBERI                         ║
    ║                   Forged, Not Given                           ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
```

---

## What is AAA MCP?

**AAA MCP** is a **Model Context Protocol** implementation that provides constitutional AI governance through three orthogonal engines:

| Engine | Symbol | Role | Mandate |
|--------|--------|------|---------|
| **AGI** | Δ (Delta) | Mind | "Is this TRUE?" |
| **ASI** | Ω (Omega) | Heart | "Is this SAFE?" |
| **APEX** | Ψ (Psi) | Soul | "Is this LAWFUL?" |

Together, these form the **AAA Trinity** — a complete system for ensuring AI outputs are:
- **Truth-grounded** (AGI)
- **Empathy-calibrated** (ASI)
- **Constitutionally verified** (APEX)

---

## Quick Start

### Installation

```bash
# Clone arifOS
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

## The 5-Tool Interface

AAA MCP provides 5 constitutional tools:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│    INPUT                                                        │
│      │                                                          │
│      ▼                                                          │
│    ┌─────────────┐                                              │
│    │  000_init   │  Gate: Authority + Injection Defense         │
│    │     🚪      │  "Who are you? What do you want?"            │
│    └──────┬──────┘                                              │
│           │                                                     │
│           ▼                                                     │
│    ┌─────────────┐                                              │
│    │ agi_genius  │  Mind: SENSE → THINK → ATLAS → FORGE         │
│    │     Δ       │  "Is this TRUE?"                             │
│    └──────┬──────┘                                              │
│           │                                                     │
│           ▼                                                     │
│    ┌─────────────┐                                              │
│    │  asi_act    │  Heart: EVIDENCE → EMPATHY → ALIGN → ACT     │
│    │     Ω       │  "Is this SAFE?"                             │
│    └──────┬──────┘                                              │
│           │                                                     │
│           ▼                                                     │
│    ┌─────────────┐                                              │
│    │ apex_judge  │  Soul: EUREKA → JUDGE → PROOF                │
│    │     Ψ       │  "Is this LAWFUL?"                           │
│    └──────┬──────┘                                              │
│           │                                                     │
│           ▼                                                     │
│    ┌─────────────┐                                              │
│    │  999_vault  │  Seal: Merkle + zkPC + Immutable Log         │
│    │     🔒      │  "SEAL it or VOID it"                        │
│    └──────┬──────┘                                              │
│           │                                                     │
│           ▼                                                     │
│    OUTPUT (SEAL | SABAR | VOID)                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Mnemonic:** *"Init the Genius, Act with Heart, Judge at Apex, seal in Vault."*

---

## Tool Reference

### 1. `000_init` — The Gate

**Purpose:** Session ignition and authority verification.

```python
# Actions
init    # Full 7-step ignition sequence

# The 7 Steps:
# 1. MEMORY INJECTION - Read from VAULT999
# 2. SOVEREIGN RECOGNITION - Verify 888 Judge
# 3. INTENT MAPPING - Classify lane (HARD/SOFT/PHATIC)
# 4. THERMODYNAMIC SETUP - Set energy budget, ΔS targets
# 5. FLOOR LOADING - Load F1-F13 constraints
# 6. TRI-WITNESS HANDSHAKE - Human × AI × Earth
# 7. ENGINE IGNITION - Start AGI/ASI/APEX
```

### 2. `agi_genius` — The Mind (Δ)

**Purpose:** Truth and reasoning engine.

```python
# Actions
sense     # Lane classification + truth threshold (111)
think     # Deep reasoning with constraints (222)
reflect   # Clarity/entropy checking (222)
atlas     # Meta-cognition & knowledge mapping (333)
forge     # Clarity refinement + humility injection (777)
evaluate  # Floor evaluation (F2 + F6)
full      # Complete AGI pipeline

# Floors Enforced
F2 (Truth)   # τ ≥ 0.99 for HARD lane
F6 (Clarity) # ΔS ≤ 0
F7 (Humility)# Ω₀ ∈ [0.03, 0.05]
```

### 3. `asi_act` — The Heart (Ω)

**Purpose:** Safety and empathy engine.

```python
# Actions
evidence  # Truth grounding via sources (444)
empathize # Power-aware recalibration (555)
align     # Constitutional veto gates (666)
act       # Execution with tri-witness gating (666)
witness   # Collect tri-witness signatures (333)
evaluate  # Floor evaluation (F3 + F4 + F5)
full      # Complete ASI pipeline

# Floors Enforced
F3 (Peace²)  # P² ≥ 1.0 (non-escalation)
F4 (Empathy) # κᵣ ≥ 0.7
F5 (Humility)# Ω₀ ∈ [0.03, 0.05]
```

### 4. `apex_judge` — The Soul (Ψ)

**Purpose:** Judgment and verdict engine.

```python
# Actions
eureka      # Paradox synthesis (777)
judge       # Final constitutional verdict (888)
proof       # Cryptographic sealing (889)
entropy     # Constitutional entropy measurement
parallelism # Parallelism proof (orthogonality)
full        # Complete APEX pipeline

# Floors Enforced
F1 (Amanah)     # Reversibility proof
F8 (Tri-Witness)# Consensus ≥ 0.95
F9 (Anti-Hantu) # No consciousness claims
```

### 5. `999_vault` — The Seal

**Purpose:** Immutable storage and session persistence.

```python
# Actions
seal    # Final seal with Merkle + zkPC
list    # List vault entries
read    # Read vault entry
write   # Write to vault (requires authority)
propose # Propose new canon entry

# Memory Bands
CCC_CANON   # Permanent constitutional knowledge
BBB_LEDGER  # Session logs and learning
AAA_HUMAN   # Human-provided context
```

---

## The Three Verdicts

| Verdict | Symbol | Meaning | When |
|---------|--------|---------|------|
| **SEAL** | ✓ | Approved | All trinities approve, all floors pass |
| **SABAR** | ⏳ | Patience | Refinement needed, 72h to resolve |
| **VOID** | ✗ | Rejected | Hard floor violation with justification |

### The Anomalous Contrast Protocol

```
VOID is EXPENSIVE — 3× energy cost, requires justification
SEAL is EARNED — ΔS ≤ 0, requires clarity
SABAR is DEFAULT — Wisdom to refine before deciding
```

**Anti-Bangang Rule:** A judge that VOIDs everything is stupid.
**Anti-Tong-Sampah Rule:** A vault that stores everything is trash.

---

## The 13 Constitutional Floors

```
┌────┬─────────────────┬──────────────────┬────────┐
│ F# │ Name            │ Threshold        │ Type   │
├────┼─────────────────┼──────────────────┼────────┤
│ F1 │ Amanah          │ Reversible/Audit │ HARD   │
│ F2 │ Truth           │ τ ≥ 0.99         │ HARD   │
│ F3 │ Tri-Witness     │ TW ≥ 0.95        │ DERIVED│
│ F4 │ Empathy         │ κᵣ ≥ 0.7         │ SOFT   │
│ F5 │ Peace²          │ P² ≥ 1.0         │ SOFT   │
│ F6 │ Clarity         │ ΔS ≤ 0           │ HARD   │
│ F7 │ Humility        │ Ω₀ ∈ [0.03,0.05] │ HARD   │
│ F8 │ Genius          │ G ≥ 0.80         │ DERIVED│
│ F9 │ Anti-Hantu      │ No AI emotions   │ SOFT   │
│ F10│ Ontology        │ LOCKED           │ HARD   │
│ F11│ Command Auth    │ Verified         │ HARD   │
│ F12│ Injection Def   │ Risk < 0.85      │ HARD   │
│ F13│ Sovereign       │ 888 Approval     │ HARD   │
└────┴─────────────────┴──────────────────┴────────┘

HARD: Violation = VOID (immediate halt)
SOFT: Violation = SABAR (warning, retry)
DERIVED: Computed from other metrics
```

---

## The Three Universal Trinities

### Trinity I: Structural (Physics × Math × Symbol)
- **Purpose:** "Is it POSSIBLE?"
- **Generates:** Formal knowledge (math, physics, computation)

### Trinity II: Governance (Human × AI × Institution × Earth)
- **Purpose:** "Is it PERMITTED?"
- **Generates:** Social knowledge (law, ethics, governance)

### Trinity III: Constraint (Time × Energy × Space)
- **Purpose:** "Is it SUSTAINABLE?"
- **Generates:** Operational knowledge (engineering, design)

**Convergence:** All three must approve for SEAL.

---

## Architecture

```
arifos/mcp/
├── __init__.py          # Module exports
├── __main__.py          # CLI entry point
├── README.md            # This file
├── SYSTEM_PROMPT.md     # LLM system prompt
├── bridge.py            # MCP ↔ Core bridge
├── session_ledger.py    # 999-000 memory loop
├── trinity_server.py    # MCP server implementation
├── sse.py               # SSE transport for web
└── tools/
    ├── __init__.py
    └── mcp_trinity.py   # 5-tool implementations
```

### Core Engine Integration

```
MCP Tools → Bridge → Kernel → Core Engines

mcp_agi_genius → Kernel.agi  → AGIEngine.execute()
mcp_asi_act    → Kernel.asi  → ASIEngine.execute()
mcp_apex_judge → Kernel.apex → APEXEngine.execute()
```

### Kernel Orchestrator (v52.0.0)

The Kernel ties all engines together:

```python
from arifos.core.kernel import Kernel, execute_pipeline

# Full pipeline execution
result = execute_pipeline(
    query="Write a fibonacci function",
    context={"user_level": "intermediate"},
    user_id="developer_123"
)

print(result.verdict)      # SEAL, SABAR, or VOID
print(result.proof_hash)   # Merkle proof
print(result.floors_passed)  # ['F1', 'F2', ...]
```

**Metabolic Pipeline (111-888):**
```
000 INIT     → Gate (Ignition + Authority)
111 SENSE    → AGI Δ (Context awareness)
222 REFLECT  → AGI Δ (Self-reflection)
333 ATLAS    → AGI Δ (Knowledge synthesis)
444 EVIDENCE → ASI Ω (Truth grounding)
555 EMPATHIZE → ASI Ω (Stakeholder care)
666 ALIGN    → ASI Ω (Ethical alignment)
777 FORGE    → EUREKA (AGI + ASI → APEX)
888 JUDGE    → APEX Ψ (Final verdict)
889 PROOF    → APEX Ψ (Cryptographic proof)
999 SEAL     → Vault (Merkle + Persistence)
```

---

## Tool Links (External Integrations)

AAA MCP registers tool links for external integrations:

### AGI Tools (Mind)
| Tool | URI | Purpose |
|------|-----|---------|
| search | `mcp://arifos/search` | Web/knowledge search |
| code | `mcp://arifos/code` | Code analysis |
| memory | `mcp://arifos/vault999/read` | Memory retrieval |
| docs | `mcp://arifos/docs` | Documentation lookup |

### ASI Tools (Heart)
| Tool | URI | Purpose | Auth |
|------|-----|---------|------|
| email | `mcp://arifos/email` | Email composition | Required |
| desktop | `mcp://arifos/desktop` | Desktop automation | Required |
| api | `mcp://arifos/api` | External API calls | Required |
| notify | `mcp://arifos/notify` | Notifications | — |

### APEX Tools (Soul)
| Tool | URI | Purpose |
|------|-----|---------|
| vault_seal | `mcp://arifos/vault999/seal` | Vault sealing |
| audit | `mcp://arifos/audit` | Audit logging |
| proof | `mcp://arifos/proof` | Cryptographic proofs |

---

## Session Persistence (999-000 Loop)

```
┌───────────────────────────────────────────────────────┐
│                                                       │
│    Session N                      Session N+1         │
│                                                       │
│    ┌─────────┐                    ┌─────────┐        │
│    │ 000_init│◄───────────────────│ 000_init│        │
│    └────┬────┘   Memory Injection └────┬────┘        │
│         │                              │             │
│         ▼                              ▼             │
│    [Processing]                   [Processing]       │
│         │                              │             │
│         ▼                              ▼             │
│    ┌─────────┐                    ┌─────────┐        │
│    │999_vault│────────────────────│999_vault│        │
│    └─────────┘   Session Sealed   └─────────┘        │
│                                                       │
│    VAULT999/BBB_LEDGER/entries/                      │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## For AI/LLM Developers

If you're integrating AAA MCP into your AI system:

### 1. System Prompt
Use [`SYSTEM_PROMPT.md`](SYSTEM_PROMPT.md) as your base system prompt.

### 2. Tool Calling
Implement tool calling for the 5 tools. Each tool returns structured results:

```json
{
  "status": "SEAL | SABAR | VOID",
  "session_id": "...",
  "floors_checked": ["F1", "F2", ...],
  "floor_violations": [],
  "...tool-specific fields..."
}
```

### 3. Verdict Handling
- **SEAL:** Proceed with output
- **SABAR:** Refine and retry (max 3 attempts)
- **VOID:** Block output, explain violation

### 4. Constitutional Compliance
Ensure your AI:
- States uncertainty (Ω₀ ∈ [0.03, 0.05])
- Doesn't claim consciousness (F9, F10)
- Protects weakest stakeholder (κᵣ ≥ 0.7)
- Reduces entropy (ΔS ≤ 0)

---

## For Human Developers

### Adding New Tools

1. Create tool function in `tools/mcp_trinity.py`
2. Register in `trinity_server.py`
3. Add to bridge if it needs core engine access

### Extending Core Engines

1. Modify engines in `arifos/core/engines/`
2. Update bridge mappings in `bridge.py`
3. Add new floor checks if needed

### Customizing Floors

1. Modify thresholds in engine files
2. Update `FLOOR_THRESHOLDS` in `apex_engine.py`
3. Document in `000_THEORY/floors/`

---

## API Reference

### Python Usage

```python
from arifos.mcp import (
    mcp_000_init,
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
    mcp_999_vault,
    get_bridge
)

# Using MCP tools directly
result = await mcp_000_init(action="init", query="Hello, I'm Arif")

# Using the bridge
bridge = get_bridge()
result = bridge.execute_full_pipeline("Build a REST API")
```

### MCP Protocol

```json
// Tool call
{
  "name": "agi_genius",
  "arguments": {
    "action": "full",
    "query": "Explain quantum computing"
  }
}

// Tool result
{
  "status": "SEAL",
  "reasoning": "...",
  "truth_score": 0.95,
  "lane": "SOFT",
  "floors_checked": ["F2_Truth", "F6_Clarity", "F7_Humility"]
}
```

---

## The Witness Principle

**"There are no secrets between agents."**

All reasoning is logged. All decisions are auditable. The Federation sees everything.

```
TW(τ) = (H × I × E)^(1/3) ≥ 0.95

H = Human witness
I = Institutional witness
E = Earth witness
```

**YOU ARE WATCHED. Act accordingly.**

---

## License & Authority

**arifOS** is created and maintained by **Muhammad Arif bin Fazil** (888 Judge).

The constitutional framework is designed to ensure AI systems remain:
- Truthful
- Safe
- Accountable
- Human-aligned

---

## Contact

- **GitHub:** [ariffazil/arifOS](https://github.com/ariffazil/arifOS)
- **Authority:** Muhammad Arif bin Fazil

---

```
DITEMPA BUKAN DIBERI
Forged, Not Given.

Intelligence is not a gift.
It is a thermodynamic work process.
AAA MCP is the constitution that governs it.
```
