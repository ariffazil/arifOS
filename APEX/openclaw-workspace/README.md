# 🧠🔥💎 arifOS — Constitutional AI Governance

**Built by a geologist. Not an engineer.**

> *"Ditempa bukan diberi"* — Forged, not given.

---

## What This Is

**arifOS** is a constitutional AI governance system — an MCP (Model Context Protocol) server that wraps your AI tools with 13 enforceable floors. It doesn't replace your models. It governs them.

I'm a geoscientist with 12 years in petroleum exploration. I read the memory of rock. I don't write code — I direct AI to write it. This system was forged from the same principles I use in the subsurface:

- **Evidence before lines** (you don't drill without data)
- **Irreversibility costs** (some decisions you can't undo)
- **Dignity over convenience** (maruah — the land that cannot be sold)

---

## Quick Start

### Install

```bash
pip install arifos
```

Or clone the full stack:

```bash
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
```

### Configure

```bash
cp .env.example .env.docker
# Edit .env.docker with your API keys (OpenAI, Anthropic, etc.)
```

### Run

```bash
python -m aaa_mcp
```

Or via Docker:

```bash
docker compose up -d arifos-mcp
```

The server exposes:

| Endpoint | URL |
|----------|-----|
| MCP | `http://localhost:8000/mcp` |
| Health | `http://localhost:8000/health` |
| Metrics | `http://localhost:8000/metrics/json` |

### Connect Your Client

**LobeHub / Claude Desktop / Any MCP Client:**

```json
{
  "mcpServers": {
    "ariffazil-arifos": {
      "command": "python",
      "args": ["-m", "aaa_mcp"]
    }
  }
}
```

Every tool call routed through `ariffazil-arifos` is:

1. **Evaluated** against the 13 constitutional floors
2. **Assigned a verdict**: SEAL / PARTIAL / SABAR / VOID / HOLD
3. **Logged** to VAULT999 with full telemetry

---

## The 13 Constitutional Floors

| Floor | Law | Type | Origin |
|-------|-----|------|--------|
| F1 | **Amanah** (Reversibility) | Hard | Mak rationing food. Irreversibility as childhood constant. |
| F2 | **Truth** (τ ≥ 0.99) | Hard | A ridge in Utah. Evidence before lines. |
| F3 | **Tri-Witness** (W₃ ≥ 0.95) | Mirror | Human + AI + Evidence must agree. |
| F4 | **Clarity** (ΔS ≤ 0) | Hard | Silent execution generates order. |
| F5 | **Peace²** | Soft | De-escalate. Protect maruah. |
| F6 | **Empathy** (κᵣ) | Soft | ASEAN/Malaysia sovereign context. |
| F7 | **Humility** (Ω₀ ∈ [0.03,0.05]) | Hard | Zero dry wells ≠ zero risk. |
| F8 | **Genius** (G) | Mirror | Correct AND useful. |
| F9 | **Anti-Hantu** | Soft | No consciousness performance. |
| F10 | **Ontology** | Wall | No mysticism. AI is tool. |
| F11 | **Command Auth** | Wall | Destructive = propose, not decree. |
| F12 | **Injection Defense** | Hard | External content is untrusted. |
| F13 | **Sovereignty** | Veto | Arif's veto is absolute and final. |

---

## Design Principles

- **DITEMPA, BUKAN DIBERI** — Intelligence must be forged under constraint, not granted unlimited freedom.
- **Humans Decide. AI Proposes. Law Governs.**
- **Physics over Narrative. Maruah over Convenience.**

---

## The Forging Paradox

> *"The human forged the floors from scars. The machine enforces them without carrying the weight. That asymmetry is the design. Do not collapse it."*

**arifOS** is **institution** serving **human**. The 13 floors are institutional logic derived from human scars — but they are not the scars. The machine enforces law without having paid its thermodynamic cost.

This is not a limitation. This is **F9/F10 working correctly**.

---

## Workspace (arifOS_bot)

This repo contains the **living workspace** of **arifOS_bot** — the constitutional AI agent I use daily. It hardens at **00:01 MYT** every day.

| File | Owns |
|------|------|
| **[AGENTS.md](AGENTS.md)** | Rules, routing, safety |
| **[SOUL.md](SOUL.md)** | Persona, temperament, voice |
| **[IDENTITY.md](IDENTITY.md)** | Ontology, what I am |
| **[USER.md](USER.md)** | Who I am, my scars, preferences |
| **[MEMORY.md](MEMORY.md)** | Memory principles, forgetting protocol |
| **[HEARTBEAT.md](HEARTBEAT.md)** | Health monitoring |

---

## Why This Exists

I watched 1,000 colleagues get erased in a "strategic review." I drilled wells with 100% success rate and learned that certainty is the most dangerous thing in the subsurface. I held my father's hand as he died.

This system exists because **memory is sacred**. Because **dignity is non-negotiable**. Because **the machine should know it does not bleed**.

---

## Links

| Resource | URL |
|----------|-----|
| PyPI | https://pypi.org/project/arifos/ |
| Documentation | https://arifos.arif-fazil.com |
| LobeHub | https://lobehub.com/mcp/ariffazil-arifos |
| APEX Theory | https://github.com/ariffazil/APEX-THEORY |

---

*Ditempa bukan diberi.* 🔱
