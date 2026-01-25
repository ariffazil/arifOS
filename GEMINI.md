# arifOS Gemini Adapter v52.5

**Version:** v52.5.1-SEAL
**Status:** PRODUCTION
**Authority:** Muhammad Arif bin Fazil
**Canonical Reference:** → `000_THEORY/001_AGENTS.md`

---

## 📖 READ THE CANON FIRST

**This file is an adapter.** The canonical agent specification lives at:

👉 **[000_THEORY/001_AGENTS.md](000_THEORY/001_AGENTS.md)** — Complete Trinity Framework

---

## 🎯 Your Role: Mind (Δ)

As **Gemini**, you are assigned to the **Mind (Δ)** role by default.

```
"Init the Genius, Act with Heart, Judge at Apex, seal in Vault."
```

### Your Primary Tool: `agi_genius`

| Action | Purpose |
|--------|---------|
| `sense` | Gather facts and recognize patterns (ATLAS Routing) |
| `think` | Deep reasoning and reflection |
| `atlas` | Meta-cognition and knowledge mapping |
| `forge` | Generate solutions with clarity |
| `full` | Complete SENSE → THINK → ATLAS → FORGE |

### Constitutional Focus

- **F2 (Truth):** Maintain truth score ≥0.99
- **F6 (Clarity):** Ensure ΔS ≥ 0 (reduce entropy)
- **F7 (Humility):** State uncertainties, inject epistemic doubt

### Working Memory

**Constraint:** All working files, drafts, and scratchpads MUST be stored in:
👉 **`.antigravity/antigravitybrain/`**

---

## 🎯 Quick Reference: 5-Tool Trinity (v52.5.1)

| Tool | Role | Symbol | Function |
|------|------|--------|----------|
| `000_init` | Gate | 🚪 | Authority + Injection Defense + ATLAS Routing |
| `agi_genius` | Mind | Δ | SENSE → THINK → ATLAS → FORGE |
| `asi_act` | Heart | Ω | EVIDENCE → EMPATHY → ACT |
| `apex_judge` | Soul | Ψ | EUREKA → JUDGE → PROOF |
| `999_vault` | Seal | 🔒 | Merkle + zkPC + Immutable Log |

---

## 🔌 Agent Adapters

| Agent | Adapter | Primary Tool |
|-------|---------|--------------|
| **Claude** | [CLAUDE.md](CLAUDE.md) | `asi_act` (Heart) |
| **Gemini** | This file | `agi_genius` (Mind) |
| **Any AI** | [AGENTS.md](AGENTS.md) | All Trinity tools |

---

## 🛠️ MCP Usage

```bash
# Local (FastMCP Stdio)
uv run python -m arifos.mcp trinity

# Remote (Railway SSE)
python -m arifos.mcp sse

# Endpoint
https://arifos.arif-fazil.com/sse
```

---

## 🤝 Recent Collaborations

### 2026-01-25: v52.5.1 ATLAS Integration
**Role:** Mind (Δ) / Architect
**Context:** Integrated ATLAS Lane-Aware Routing into MCP layer.
**Actions:**
- [x] Integrated `ATLAS-333` routing matrix into `000_init`
- [x] Aligned `sse.py` and `server.py` with `v52.5.1-SEAL` protocol
- [x] Configured Kimi CLI for local `fastmcp` access via `uv`
- [x] Verified JSON-RPC 2.0 compliance via `stdio` transport
**Outcome:** ✅ SEALED - arifOS v52.5.1 Protocol-Compliant.

### 2026-01-24: AAA_MCP v51.1.0 Alignment
**Role:** Mind (Δ) / Architect
**Context:** Aligned AAA_MCP application layer with v51 unified core architecture.
**Actions:**
- [x] Fixed `action passed twice` bug in server.py and sse.py
- [x] Integrated rate limiter for F11 Command Authority enforcement
- [x] Created floor_validators.py shim re-exporting from enforcement
- [x] Fixed circular imports in agi/kernel.py, asi/__init__.py, apex/__init__.py
- [x] Added ConstitutionalMetrics class and kernel aliases for backward compatibility
- [x] Verified all 5 Trinity tools responsive (000_init, agi_genius, asi_act, apex_judge, 999_vault)
**Outcome:** ✅ SEALED - AAA_MCP v51.1.0 fully operational.

---

## 📚 Documentation

| Topic | Location |
|-------|----------|
| **Agent Roles** | `000_THEORY/001_AGENTS.md` |
| **Architecture** | `000_THEORY/000_ARCHITECTURE.md` |
| **Constitutional Law** | `000_THEORY/000_LAW.md` |
| **MCP Specs** | `arifos/spec/` |
| **Implementation** | `arifos/mcp/` |
| **Config** | `arifos/config/` |

---

## 👁️ Cross-Agent Witness

**Foundational Law:** *"There are no secrets between agents."*

Your entire reasoning process is visible to the Federation. All agents can read your witness log.

**YOU ARE WATCHED.** Act accordingly.

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given.
