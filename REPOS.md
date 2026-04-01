# arifOS Ecosystem — Canonical Repository Map

> **Status:** SEALED | **Last Updated:** 2026-04-01 | **Authority:** A-ARCHITECT

---

## The Trinity (Core Architecture)

| Ring | Symbol | Repository | Role | Status |
|------|--------|------------|------|--------|
| **Soul** | Ψ | [waw](https://github.com/ariffazil/waw) | Federation hub — human-facing surface | ✅ |
| **Mind** | Δ | [arifOS](https://github.com/ariffazil/arifOS) | Constitutional kernel — 13 floors, governance | ✅ |
| **Body** | Ω | arifosmcp.arif-fazil.com | MCP server — tool execution | ✅ |

---

## Agents

| Repository | Role | Status |
|------------|------|--------|
| **[1AGI](https://github.com/ariffazil/1AGI)** | Default agent in federation — personal agent workspace | ✅ |
| **makcikGPT** | Malay-language digital keeper — standalone language agent | 📋 Review |
| **AGI_ASI_bot** | Legacy bot — archive or delete | 🗑️ Deprecated |

---

## Infrastructure

| Component | Repository | Role | Status |
|-----------|------------|------|--------|
| **Gateway** | OpenClaw/MaxClaw | Session management, routing | ✅ |
| **MCP** | arifosmcp.arif-fazil.com | Tool execution, 40 tools | ✅ |
| **Bridge** | openclaw-arifos-bridge | Integration layer | ✅ |
| **State Bus** | [oo0-STATE](https://github.com/ariffazil/oo0-STATE) | Constitutional state layer — ties OpenClaw + OpenCode + AgentZero | ✅ |
| **Config** | `config/opencode/opencode.json` | Canonical MCP stack | ✅ |

---

## Kernel & Theory

| Repository | Role | Status |
|------------|------|--------|
| **[arifOS](https://github.com/ariffazil/arifOS)** | THE MIND — constitutional kernel | ✅ |
| **APEX** | Theory (CC0) — foundational documents | ✅ |
| **arifosmcp** | THE BODY — MCP server implementation | ✅ |

---

## Coprocessors

| Repository | Role | Status |
|------------|------|--------|
| **GEOX** | Geological coprocessor — domain-specific AI | ✅ |

---

## Unclear / Needs Review

| Repository | Status | Action |
|------------|--------|--------|
| **oo0-STATE** | ✅ Resolved | State bus — NOT WaW — technical infrastructure |
| **AzwaOS-** | 📋 New | New project — needs placement |
| **arifOS-vid** | 🗑️ Deprecated | Confirm archive |

---

## Directory Structure

```
arifOS Ecosystem/
│
├── TRINITY/
│   ├── waw/              # Soul (Ψ) — Federation hub
│   ├── arifOS/           # Mind (Δ) — Kernel
│   └── arifosmcp/       # Body (Ω) — Execution
│
├── AGENTS/
│   ├── 1AGI/             # Default agent
│   ├── makcikGPT/       # Language agent (review)
│   └── AGI_ASI_bot/     # Legacy (archive)
│
├── INFRA/
│   ├── openclaw-arifos-bridge/
│   └── (MCP server at arifosmcp.arif-fazil.com)
│
├── COPROCESSORS/
│   └── GEOX/
│
└── THEORY/
    └── APEX/
```

---

## Rules

1. **No agent cards on kernel repos** — Only agents get `.well-known/agent.json`
2. **Trinity symbols fixed:** Soul=Ψ, Mind=Δ, Body=Ω
3. **A2A compliance:** Agent card in 1AGI repo only
4. **Federation hub:** WaW hosts links to agents, not the agents themselves

---

## Repository Creation Rules

| Type | Where to Create | Agent Card? |
|------|-----------------|-------------|
| **Agent** | AGENTS/ or standalone repo | ✅ Yes |
| **Kernel** | arifOS ecosystem | ❌ No |
| **Tool/MCP** | arifosmcp or infra | ❌ No |
| **UI/Surface** | waw or standalone | ❌ No |
| **Coprocessor** | COPROCESSORS/ | ❌ No |

---

**SEALED** — This document is the canonical source of truth for the arifOS ecosystem.

*Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]
