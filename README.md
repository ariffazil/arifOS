<!-- mcp-name: ariffazil/arifos -->
<!-- SOT-MANIFEST
federation_release: v2026.07.04-MCP-A2A
last_verified: 2026-07-07
changelog: /root/CHANGELOG-2026-07-04.md
p0_actor_id_binding: live (kernel reads JWT lineage first; self-report caps MEDIUM)
floor_11b_amanah_replay: live (nonce required for IRREVERSIBLE mutations; 24h cache)
a2a_agent_json: /root/arifOS/.well-known/agent.json
-->

<div align="center">

```
   █████╗ ██████╗ ██╗███████╗ ██████╗ ███████╗
  ██╔══██╗██╔══██╗██║██╔════╝██╔═══██╗██╔════╝
  ███████║██████╔╝██║█████╗  ██║   ██║███████╗
  ██╔══██║██╔══██╗██║██╔══╝  ██║   ██║╚════██║
  ██║  ██║██║  ██║██║██║     ╚██████╔╝███████║
  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝      ╚═════╝ ╚══════╝

  Constitutional AI Governance Kernel
  ─────────────────────────────────────────
  Not a chatbot. Not a model wrapper. The LAW.
```

**DITEMPA BUKAN DIBERI** — *"Forged, Not Given."*

</div>

[![Unified CI](https://github.com/ariffazil/arifos/actions/workflows/01-unified-ci.yml/badge.svg?branch=main)](https://github.com/ariffazil/arifos/actions/workflows/01-unified-ci.yml)
[![MCP Conformance](https://github.com/ariffazil/arifos/actions/workflows/06-mcp-conformance.yml/badge.svg?branch=main)](https://github.com/ariffazil/arifos/actions/workflows/06-mcp-conformance.yml)
[![PyPI](https://img.shields.io/pypi/v/arifos?label=PyPI)](https://pypi.org/project/arifos/)
[![License](https://img.shields.io/github/license/ariffazil/arifos?label=License)](LICENSE)

> **⚠️ PUBLIC REPO NOTICE (2026-07-06):** The GitHub repository `ariffazil/arifos` is a
> **public snapshot** and may be **archived or significantly behind** the live production
> codebase running on `af-forge` (72.62.71.199). The live code has active patches for
> identity verification, schema strictness, CORS hardening, and MCP error handling that
> are NOT reflected in the public repo. Security audits should target the live deployment,
> not the public GitHub snapshot. See `SECURITY.md` for details.

---

## 1. What Is arifOS?

> **arifOS is a constitutional governance kernel that sits between AI agents and their tools, enforcing 13 floors before any irreversible action.**

- **The law layer** — decides what agents must NOT do, so they can be trusted with what they CAN do
- **An MCP server** — 12 canonical public verbs (F13 SOVEREIGN RATIFIED 2026-07-04; prior freeze was 7). One intent = one public tool. See `arifosmcp/PUBLIC_SURFACE_CANON.md`.
- **A federation hub** — 6 live organs (arifOS, A-FORGE, AAA, GEOX, WEALTH, WELL) plus the VAULT999 immutable ledger under one contract
- **An immutable ledger** — VAULT999: append-only, hash-chained. Every decision sealed forever
- **Built for one sovereign** — Muhammad Arif bin Fazil. F13 veto is absolute

**What it is NOT:** an AI model, a chatbot, a startup, LangChain/CrewAI/AutoGen, or a replacement for human judgment.

---

## APEX STACK Bridge

> APEX THEORY defines the constitutional dynamics of governed intelligence through ΔΩΨ. arifOS compiles those dynamics into an AGI substrate kernel. AAA renders the substrate as visible ASI civilization state. A-FORGE gives the system governed hands. GEOX, WEALTH, and WELL anchor those hands to earth, capital, and human reality. VAULT999 preserves consequence. Arif/F13 remains the sovereign witness and final veto.

**arifOS must never:** replace human judgment, self-authorize a SEAL, skip 888_JUDGE, or issue verdicts without a constitutional chain.

Full doctrine: [GENESIS/040_APEX_STACK.md](https://github.com/ariffazil/arifos/blob/main/GENESIS/040_APEX_STACK.md)

---

## 2. Quick Start

### Human Operators
You don't install arifOS. You interact through:
- **AAA Cockpit:** https://aaa.arif-fazil.com
- **Hermes Telegram:** `@ASI_arifos_bot`
- **Health check:** https://arifos.arif-fazil.com/health

### AI Agents (MCP Clients)
```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://mcp.arif-fazil.com/mcp",
      "transport": "streamable-http"
    }
  }
}
```

### Developers
```bash
pip install arifos                          # from PyPI
# or
git clone git@github.com:ariffazil/arifos.git && cd arifOS
uv sync --all-extras
python -m arifosmcp.runtime.server           # starts on :8088
curl http://127.0.0.1:8088/health            # verify
python -m pytest tests/ -q --tb=short
```

---

## 3. The 12 Canonical Public Tools

Default `tools/list` is frozen to the **12-verb public facade** (`arifosmcp/PUBLIC_SURFACE_CANON.md`, F13 ratified 2026-07-04). Diagnostic and legacy aliases still exist internally and may surface via governed channels, but they are not on the default public MCP wire surface. **arif_seal is no longer public** — VAULT999 owns the receipt seal; `arif_judge` returns `SEAL_CANDIDATE`.

| # | Tool | Stage | What It Does |
|---|------|-------|---------------|
| 1 | `arif_init` | 000 | Start constitutional session. Always first. |
| 2 | `arif_canary` | 000c | Transport diagnostic — 6 modes: ping, schema_echo, version_echo, transport_echo, initialize_probe, conformance_report. |
| 3 | `arif_triage` | 000t | Status + preflight for live sessions. Tell me the next safe action. |
| 4 | `arif_observe` | 111 | Broad sensing — web search, URL ingest, system vitals. |
| 5 | `arif_fetch` | 111f | Targeted URL/source fetch with provenance. |
| 6 | `arif_think` | 333 | Reason, plan, critique, metabolize — multi-step cognition. |
| 7 | `arif_critique` | 666 | Maruah / risk check before irreversible or dignity-affecting actions. |
| 8 | `arif_route` | 444 | Route intent to the correct federation organ. |
| 9 | `arif_bridge_connect` | 555b | Low-level direct organ call (bypasses triage — caller specifies organ + tool). |
| 10 | `arif_judge` | 888 | Constitutional verdict — `SEAL_CANDIDATE` / `HOLD` / `SABAR` / `VOID`. The kernel judges; it does not seal. |
| 11 | `arif_forge` | 900 | Guarded execution, only after a `SEAL_CANDIDATE` from `arif_judge`. (`arif_act` retained as internal alias.) |
| 12 | `arif_compose` | 444r | Governed final reply. Call LAST after reasoning + judgment are complete. |

```
000 ── 000c ── 000t ──→ 111 / 111f ──→ 333 ──→ 444 ── 555b ──→ 666 ──→ 888 ──→ 900 ──→ 444r
init  canary  triage    observe fetch  think    route   bridge  critique  judge   forge   compose
```

**Iron rules:**
- No action skips 888. No organ self-authorizes.
- After 888 → `arif_forge`; after 888 + reply → `arif_compose`.
- `arif_seal` is internal alias only — public sealing route = `arif_judge → SEAL_CANDIDATE → VAULT999`.

**Source of truth:** `arifosmcp/PUBLIC_SURFACE_CANON.md` → `arifosmcp/runtime/public_surface.py` (`CANONICAL_12`) → `arifosmcp/constitutional_map.py` (`_PUBLIC_12`) → `arifosmcp/tool_registry.json` (`canonical_order`) → `static/.well-known/mcp/server.json`. All SDK aliases (`arif_session_init`, `arif_gateway_connect`, `arif_forge_execute`, `arif_heart_critique`, `arif_mind_reason`, `arif_reply_compose`, `arif_evidence_fetch`, `arif_sense_observe`, `arif_judge_deliberate`) resolve to one of the 12.

---

## 4. The 13 Constitutional Floors

Every tool call passes through these. Hard floors block. Soft floors warn.

| # | Floor | Type | Rule |
|---|-------|------|------|
| **F1** | AMANAH | HARD | Reversible first. Irreversible → 888 HOLD |
| **F2** | TRUTH | HARD | P(truth) ≥ 0.99. Fabrication = VOID |
| **F3** | WITNESS | DERIVED | Multi-party consensus required for high-blast actions |
| **F4** | CLARITY | HARD | Every output must reduce entropy (ΔS ≤ 0) |
| **F5** | PEACE² | SOFT | Non-destructive power. Harm potential < 0.30 |
| **F6** | EMPATHY | SOFT | Protect weakest stakeholder |
| **F7** | HUMILITY | HARD | Cap confidence at 0.90. No fake certainty |
| **F8** | GENIUS | DERIVED | Complex actions need high signal |
| **F9** | ANTIHANTU | HARD | No deception, manipulation, or consciousness claims |
| **F10** | ONTOLOGY | HARD | AI is instrument. No soul, no feelings |
| **F11** | AUDIT | HARD | Every decision logged and inspectable |
| **F12** | RESILIENCE | HARD | Injection defense. Risk bounded |
| **F13** | SOVEREIGN | HARD | Human veto FINAL. Strongest floor |

**HARD violation → VOID.** Action blocked. **SOFT tension → CAUTION/HOLD.** Human review. **DERIVED → informational only.**

Full spec: `static/arifos/theory/000/000_CONSTITUTION.md`

---

## 5. Federation Architecture

arifOS is the kernel. Six organs serve under it. Two edge agents interface with the world.

```
                         ┌──────────────────────┐
                         │  Arif (F13 SOVEREIGN) │
                         └──────────┬───────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       │                            │                            │
  ┌────▼─────┐              ┌───────▼───────┐            ┌───────▼───────┐
  │  Hermes  │              │      AAA      │            │   OpenClaw    │
  │  🧠 :8644│              │  🖥️  :3001    │            │   🤖 :18789   │
  │ Telegram │              │   Cockpit     │            │  Transport    │
  └──────────┘              └───────────────┘            └───────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │    arifOS (Ω)        │
                         │    Kernel :8088      │
                         │    F1-F13 · 888 JUDGE│
                         └──┬───┬───┬───┬──────┘
                            │   │   │   │
          ┌─────────────────┼───┼───┼───┼─────────────────┐
          │                 │   │   │   │                 │
    ┌─────▼────┐   ┌───────▼┐ ┌▼─────┐ ┌▼────────┐  ┌────▼─────┐
    │  GEOX    │   │WEALTH  │ │ WELL │ │A-FORGE  │  │ VAULT999 │
    │  🌍 :8081│   │💰:18082│ │🫀:18083│ │⚒️:7071  │  │ 🔒 Seal  │
    │ Evidence │   │Compute │ │Reflect│ │Execute  │  │ Immutable│
    └──────────┘   └────────┘ └──────┘ └─────────┘  └──────────┘
```

| Organ | Port | Role | Must Never |
|-------|------|------|------------|
| **arifOS** | 8088 | Constitutional kernel | Self-authorize |
| **GEOX** | 8081 | Earth intelligence | Authorize drilling |
| **WEALTH** | 18082 | Capital intelligence | Allocate capital |
| **WELL** | 18083 | Human readiness | Make medical diagnoses |
| **AAA** | 3001 | Control plane / cockpit | Issue constitutional verdicts |
| **A-FORGE** | 7071/7072 | Execution shell | Self-authorize |
| **VAULT999** | — | Immutable audit ledger | Edit or delete records |
| **Hermes** | 8644 | Telegram MIND edge | Issue constitutional verdicts |
| **OpenClaw** | 18789 | Transport HANDS edge | Issue constitutional verdicts |

**Authority chain:** Arif → AAA/Hermes → arifOS kernel → Domain organs → A-FORGE → VAULT999

---

## 6. Build, Test, Deploy

```bash
# Development
uv sync --all-extras
uv run python -m arifosmcp.runtime.server
python -m pytest tests/ -q --tb=short
ruff check . && ruff format .

# Deploy to VPS
make deploy-local                             # rsync + systemd restart
systemctl status arifos

# Docker
docker build -t ghcr.io/ariffazil/arifos:latest .
```

---

## 7. MCP Connection Guide

### Public Endpoint
```
https://mcp.arif-fazil.com/mcp
```
Transport: `streamable-http`. Initialize session first, then call tools.

### Internal Organs
| Organ | Endpoint | When to use |
|-------|----------|-------------|
| **arifOS** | `localhost:8088` | Governance, judgment, routing |
| **A-FORGE** | `localhost:7071` | Build, deploy, filesystem, git, docker |
| **GEOX** | `localhost:8081` | Seismic, wells, petrophysics |
| **WEALTH** | `localhost:18082` | NPV, risk, capital flow |
| **WELL** | `localhost:18083` | Vitality, readiness, dignity |

**Rule:** arifOS judges → A-FORGE executes → VAULT999 records. Never skip the chain.

### Federation Context (read all 3 for full picture)

| Read this | For | Link |
|-----------|-----|------|
| **arifOS** (this repo) | Constitutional kernel. 7 canonical public verbs. 13 floors. The judge. | ← you are here |
| **A-FORGE** | Executor. 75 MCP tools. Gates + A-THINK law. | [`ariffazil/A-FORGE`](https://github.com/ariffazil/A-FORGE) |
| **AAA** | Cockpit. A2A mesh. Agent registry. React 19 dashboard. | [`ariffazil/AAA`](https://github.com/ariffazil/AAA) |

---

## 🔌 MCP Connection

Connect to arifOS via the Model Context Protocol:

| Property | Value |
|----------|-------|
| **Endpoint** | `https://mcp.arif-fazil.com/mcp` |
| **Alternate** | `https://arif-fazil.com/mcp` |
| **Transport** | Streamable HTTP (JSON-RPC 2.0) |
| **Tools** | 45 exposed (17 canonical + 41 diagnostic) |
| **Health** | `https://arifos.arif-fazil.com/health` |

### Claude Code / Cursor

Add to your MCP client config:
```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://mcp.arif-fazil.com/mcp"
    }
  }
}
```

### Direct Usage

```bash
curl -X POST https://mcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### Discovery

- Agent Card: `https://arifos.arif-fazil.com/.well-known/agent-card.json`
- MCP Manifest: `https://arifos.arif-fazil.com/.well-known/mcp.json`

---

## 8. License & Sovereignty

**AGPL-3.0.** The constitution must remain open. The kernel must remain inspectable.

**Muhammad Arif bin Fazil** is F13 SOVEREIGN. His veto is absolute. No algorithm overrides. No agent bypasses. No institution supersedes.

---

<div align="center">

```
arifOS · Port 8088 · 7 canonical public verbs · 13 floors · 6 live organs
AGPL-3.0 · Sovereign: Arif Fazil · Federation: ALIVE
DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
```

</div>
