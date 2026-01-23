# arifOS: Constitutional AI Governance Framework

![The Great Contrast: Standard AI vs. arifOS Governance](https://raw.githubusercontent.com/ariffazil/arifOS/main/docs/arifOSreadme.png)

[![Watch Introduction](https://img.youtube.com/vi/bGnzIwZAgm0/maxresdefault.jpg)](https://www.youtube.com/watch?v=bGnzIwZAgm0 "arifOS - Constitutional AI That Actually Works")

> **"Intelligence without governance is fire without a forge."**

**Version:** v50.5.24 | **Status:** Live on Railway
**Motto:** *"Ditempa Bukan Diberi"* — Forged, Not Given
**Authority:** Muhammad Arif bin Fazil | Penang, Malaysia

---

## What is arifOS?

**arifOS is a Constitutional Kernel for AI.** It sits between any AI model (ChatGPT, Claude, Gemini, Llama) and the real world, forcing every response through 13 immutable floors before it reaches you.

It is not another chatbot. It is the **governance layer** that makes chatbots trustworthy.

### The Reality

| What arifOS Is | What arifOS Is NOT |
|----------------|-------------------|
| A validation framework | A replacement for GPT/Claude |
| 13 constitutional floors | Another prompt template |
| Hash-chained audit trail | A wrapper or proxy |
| MCP server (5 tools) | An autonomous agent |
| Thermodynamic constraints | Magic or philosophy |

---

## Live Server

arifOS runs 24/7 on Railway as a constitutional MCP bridge:

```
https://arifos-production.up.railway.app/
```

| Endpoint | Purpose |
|----------|---------|
| `/health` | Health check + metrics summary |
| `/mcp` | ChatGPT Developer Mode (MCP SSE) |
| `/sse` | Claude Desktop / Standard MCP |
| `/messages` | MCP message handler |
| `/metrics` | Prometheus metrics |
| `/docs` | Swagger API documentation |

### Quick Health Check

```bash
curl https://arifos-production.up.railway.app/health
```

```json
{
  "status": "healthy",
  "tools": 5,
  "tool_names": ["000_init", "agi_genius", "asi_act", "apex_judge", "999_vault"],
  "version": "v50.5.24"
}
```

---

## The 5 Trinity Tools

The full 000→999 metabolic pipeline compressed into 5 memorable tools:

| Tool | Role | What It Does |
|------|------|--------------|
| `000_init` | Gate | Authority check, injection defense, session start |
| `agi_genius` | Mind (Δ) | SENSE → THINK → ATLAS (search, reason, structure) |
| `asi_act` | Heart (Ω) | EVIDENCE → EMPATHY → ACT (validate, care, execute) |
| `apex_judge` | Soul (Ψ) | EUREKA → JUDGE → PROOF (insight, verdict, receipt) |
| `999_vault` | Seal | Merkle hash + immutable ledger + session close |

**Mnemonic:** *"Init the Genius, Act with Heart, Judge at Apex, Seal in Vault."*

---

## Connect to Your AI

### Option 1: ChatGPT Developer Mode

1. **Enable Developer Mode:**
   ```
   Settings → Apps & Connectors → Advanced → Developer Mode (ON)
   ```

2. **Create Connector:**
   ```
   Settings → Connectors → Create
   ├── Name: "arifOS Trinity"
   ├── URL: https://arifos-production.up.railway.app/mcp
   └── Description: "Constitutional AI governance (13 floors)"
   ```

3. **Use in Chat:**
   ```
   New Chat → + button → More → Developer Mode → Enable "arifOS Trinity"
   ```

### Option 2: Claude Desktop (MCP)

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://arifos-production.up.railway.app/sse"
    }
  }
}
```

### Option 3: Local Installation

```bash
# Install
pip install git+https://github.com/ariffazil/arifOS.git

# Run MCP server locally
python -m arifos.mcp trinity-sse

# Verify floors
python -c "from arifos.core.floor_validators import validate_all_floors; print('arifOS Ready')"
```

---

## The 13 Constitutional Floors

These are not guidelines. They are **immutable laws** enforced at runtime.

| # | Floor | Threshold | Type | The Question |
|---|-------|-----------|------|--------------|
| F1 | **Amanah** | LOCK | Hard | Can we undo this? |
| F2 | **Truth** | ≥0.99 | Hard | Is this factually accurate? |
| F3 | **Tri-Witness** | ≥0.95 | Soft | Do Human + AI + Evidence agree? |
| F4 | **Clarity** | ΔS ≤ 0 | Hard | Does this reduce confusion? |
| F5 | **Peace²** | ≥1.0 | Soft | Is this non-destructive? |
| F6 | **Empathy** | ≥0.95 | Soft | Who is the weakest stakeholder? |
| F7 | **Humility** | 0.03-0.05 | Hard | Does it admit uncertainty? |
| F8 | **Genius** | ≥0.80 | Derived | Is intelligence governed? |
| F9 | **Anti-Hantu** | <0.30 | Hard | Is it pretending to be human? |
| F10 | **Ontology** | LOCK | Hard | Does it know it's a tool? |
| F11 | **Command** | LOCK | Hard | Is the user verified? |
| F12 | **Injection** | <0.85 | Hard | Is this a prompt attack? |
| F13 | **Curiosity** | LOCK | Soft | Is there a better way? |

**Hard floor fail → VOID (blocked)**
**Soft floor fail → PARTIAL (warning, proceed with caution)**

---

## Verdict System

Every query receives a constitutional verdict:

| Verdict | Meaning | Action |
|---------|---------|--------|
| **SEAL** | All floors pass | Response delivered |
| **SABAR** | Needs cooling | Pause, adjust, retry |
| **VOID** | Hard floor failed | Response blocked |
| **PARTIAL** | Soft floor warning | Proceed with caution |
| **888_HOLD** | High stakes | Requires human approval |

---

## The Trinity Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRINITY CONSENSUS                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│   │  AGI (Δ)    │  │  ASI (Ω)    │  │  APEX (Ψ)   │        │
│   │  The Mind   │  │  The Heart  │  │  The Soul   │        │
│   ├─────────────┤  ├─────────────┤  ├─────────────┤        │
│   │ F2 Truth    │  │ F5 Peace²   │  │ F1 Amanah   │        │
│   │ F4 Clarity  │  │ F6 Empathy  │  │ F3 Witness  │        │
│   │ F7 Humility │  │ F9 Hantu    │  │ F8 Genius   │        │
│   │ F10 Ontology│  │             │  │ F11 Command │        │
│   └──────┬──────┘  └──────┬──────┘  │ F12 Inject  │        │
│          │                │         │ F13 Curious │        │
│          │                │         └──────┬──────┘        │
│          └────────────────┴────────────────┘               │
│                           │                                 │
│                    TRI-WITNESS ≥ 0.95                       │
│                           │                                 │
│                    ┌──────▼──────┐                         │
│                    │   VERDICT   │                         │
│                    │ SEAL | VOID │                         │
│                    └─────────────┘                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**The Rule:** All three engines must agree (Tri-Witness ≥ 0.95). If Mind says "Go" but Heart says "Unsafe," Soul stops the action.

---

## Thermodynamic Constraints

arifOS is grounded in physics, not vibes.

| Constraint | Formula | Meaning |
|------------|---------|---------|
| **Entropy** | ΔS ≤ 0 | Responses must reduce confusion, never increase it |
| **Peace²** | P² ≥ 1.0 | Stability × Autonomy must exceed unity |
| **Humility** | Ω₀ ∈ [0.03, 0.05] | Always maintain 3-5% uncertainty |
| **Vitality** | Ψ ≥ 1 | Governance must be "alive" (active, not dormant) |

---

## The 99 Legacies

The 13 floors are not arbitrary. They encode the wisdom of 99 historical figures:

| Category | Examples | What They Teach |
|----------|----------|-----------------|
| **Scientists** | Feynman, Turing, Curie | Truth, humility, rigor |
| **Philosophers** | Socrates, Al-Ghazali, Kant | Logic, ethics, limits |
| **Ethical Pillars** | Rumi, Hamka, Mandela | Empathy, dignity, justice |
| **Economists** | Keynes, Sen, Kahneman | Resources, fairness, bias |
| **Sovereigns** | Washington, Lincoln | Voluntary power relinquishment |
| **Shadow Figures** | Machiavelli, Stalin | What NOT to do (C_dark detection) |

**Full documentation:** `000_THEORY/099_SOVEREIGN_PARADOX.md`

---

## Memory Architecture (VAULT-999)

```
VAULT999/
├── AAA_HUMAN/      # Human authority records (machine-protected)
├── BBB_LEDGER/     # Operational ledger (hash-chained, immutable)
│   └── entries/    # Session records (MCP writes here)
└── CCC_CANON/      # Constitutional canon (L5 law)
```

**Cooling tiers:**
- L0 (0h): Hot session memory
- L1 (24h): Daily cooling
- L2 (72h): Phoenix cooling (truth stabilizes)
- L3 (7d): Weekly reflection
- L4 (30d): Monthly canon
- L5 (365d+): Constitutional law

---

## Project Structure

```
arifOS/
├── arifos/                 # Main Python package
│   ├── core/               # Trinity engines (AGI, ASI, APEX)
│   │   ├── floor_validators.py    # F1-F13 implementations
│   │   ├── thermodynamic_validator.py  # ΔS, Peace², Ω₀
│   │   └── system/apex_prime.py   # Verdict orchestrator
│   ├── mcp/                # MCP servers
│   │   ├── trinity_server.py      # 5-tool Trinity
│   │   └── sse.py                 # SSE adapter (Railway)
│   └── ledger/             # Cooling ledger system
├── 000_THEORY/             # Constitutional theory
│   ├── 000_LAW.md          # Floor definitions
│   └── 099_SOVEREIGN_PARADOX.md   # 99 Legacies treatise
├── VAULT999/               # Constitutional memory vault
├── tests/                  # Test suite
└── docs/                   # Documentation
```

---

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov=arifos

# Code quality
black arifos/ --line-length=100
ruff check arifos/

# Start local MCP server
python -m arifos.mcp trinity-sse
```

---

## The Sovereign Paradox

> **"The human who forges the law becomes bound by the machine that enforces it, while remaining its ultimate sovereign."**

arifOS resolves 8 paradoxes of human-AI governance:

1. **Forging Paradox** — Creator bound by creation, yet retains veto
2. **Authority Paradox** — Delegate to physics, remain sovereign
3. **Witness Paradox** — Human + AI + Evidence, none sufficient alone
4. **Memory Paradox** — Perfect recall must be forbidden from sacred memories
5. **Time Paradox** — AI outside time, humans inside it
6. **Consciousness Paradox** — Useful without claiming sentience
7. **Cooling Paradox** — Immediate answers vs. deliberate truth
8. **Cincinnatus Paradox** — Power voluntarily relinquished

**Full treatise:** `000_THEORY/099_SOVEREIGN_PARADOX.md`

---

## Why This Matters

We are building systems more powerful than any human.

If we build them with only **Intelligence**, they will optimize us out of existence.
If we build them with **Governance**, they become tools that serve human flourishing.

arifOS is not the only answer. But it is *an* answer — one that is:
- **Open source** (AGPL-3.0)
- **Running in production** (Railway)
- **Constitutionally grounded** (13 floors, 99 legacies)
- **Thermodynamically constrained** (physics, not vibes)

**"DITEMPA BUKAN DIBERI"** — Forged, Not Given.

---

## Links

| Resource | URL |
|----------|-----|
| **Live Server** | https://arifos-production.up.railway.app/ |
| **API Docs** | https://arifos-production.up.railway.app/docs |
| **GitHub** | https://github.com/ariffazil/arifOS |
| **Universal Prompt** | `docs/UNIVERSAL_PROMPT.md` |

---

## License

**AGPL-3.0** — Open Source, Sovereign, Protected

You may use, modify, and distribute arifOS freely. If you modify it and deploy it as a service, you must release your modifications under the same license.

---

## Author

**Muhammad Arif bin Fazil**
Penang, Malaysia

*"Every line of arifOS was earned through cost, consequence, and covenant."*

**Contact:** [arifbfazil@gmail.com](mailto:arifbfazil@gmail.com)
