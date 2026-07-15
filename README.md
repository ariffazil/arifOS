<!-- mcp-name: ariffazil/arifos -->
<!-- SOT-MANIFEST
federation_release: v2026.07.15-SURFACE-HARDENING
last_verified: 2026-07-15T09:35Z
deployed_commit: 192b20da
deployed_branch: main
dev_commit: ef9d328c
dev_branch: surface/audit-fix-2026-07-15
live_version: kanon-ef9d328
runtime_path: /opt/arifos/app
runtime_drift: false
drift_detail: surface audit applied — all manifests synced
owner_summary: GREEN
tools_exposed_via_mcp: 8
canonical_tools_loaded: 8
kernel_abi_capabilities: 8
chatgpt_compatible: true
claude_desktop_compatible: true
total_declared_tools: 48
tool_count_note: 8 canonical public tools on wire. Diagnostic, alias, canary, entropy mesh filtered from tools/list by default.
spine_p0_sct: live (sct_v1 mint; store-delete full loop)
arif_triage: DEPRECATED_ALIAS -> arif_init(mode=preflight|triage)
arif_act: internal_only (never in allowed_next_verbs)
arif_critique: internal -> arif_think(mode=critique)
arif_compose: internal -> arif_forge(mode=compose)
arif_bridge_connect: internal -> arif_route(mode=bridge)
changelog: /root/arifOS/CHANGELOG.md
p0_actor_id_binding: live (kernel reads JWT lineage first; self-report caps MEDIUM)
floor_11b_amanah_replay: live (nonce required for IRREVERSIBLE mutations; 24h cache)
a2a_agent_json: https://aaa.arif-fazil.com/.well-known/agent.json (AAA owns canonical A2A card per FEDERATION_CONTRACT §5.4.5)
mcp_server_card: https://mcp.arif-fazil.com/.well-known/mcp/server.json
claude_desktop_config: /root/arifOS/claude_desktop_config.json
truth_rule: /health + MCP tools/list beat any static count in prose
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

> **New agents:** Read `ZEN.md` first — it is the minimum viable context.

[![Unified CI](https://github.com/ariffazil/arifos/actions/workflows/01-unified-ci.yml/badge.svg?branch=main)](https://github.com/ariffazil/arifos/actions/workflows/01-unified-ci.yml)
[![MCP Conformance](https://github.com/ariffazil/arifos/actions/workflows/06-mcp-conformance.yml/badge.svg?branch=main)](https://github.com/ariffazil/arifos/actions/workflows/06-mcp-conformance.yml)
[![Kernel ABI](https://img.shields.io/badge/Kernel%20ABI-8%20capabilities-0a7b83)](docs/KERNEL_CAPABILITY_ABI.md)
[![Federation](https://img.shields.io/badge/Federation-6%20organs-1f6feb)](#1-what-is-arifos)
[![ChatGPT Compat](https://img.shields.io/badge/ChatGPT-✔-brightgreen)](#connecting-from-chatgpt)
[![Claude Desktop](https://img.shields.io/badge/Claude%20Desktop-✔-brightgreen)](#connecting-from-claude-desktop)
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
- **A constitutional kernel with adapters** — 8 stable semantic capabilities, projected through profile-specific MCP bindings. The generated `public_agent` profile exposes 6 governed tools; executor and sovereign profiles add action and finality without changing capability meaning. See `docs/KERNEL_CAPABILITY_ABI.md`.
- **A federation hub** — 6 live organs (arifOS, A-FORGE, AAA, GEOX, WEALTH, WELL) plus the VAULT999 immutable ledger under one contract
- **An immutable ledger** — VAULT999: append-only, hash-chained. Every decision sealed forever
- **Built for one sovereign** — Muhammad Arif bin Fazil. F13 veto is absolute

**What it is NOT:** an AI model, a chatbot, a startup, LangChain/CrewAI/AutoGen, or a replacement for human judgment.

---

## APEX STACK Bridge

> APEX is the admissibility framework for decisions under uncertainty (ΔΩΨ). arifOS compiles those dynamics into a constitutional orchestration substrate. AAA renders federation-state and coordination (display layer — not ASI-civilisation claims). A-FORGE gives the system governed hands. GEOX, WEALTH, and WELL anchor those hands to earth, capital, and human reality. VAULT999 preserves consequence. Arif/F13 remains the sovereign witness and final veto.

**arifOS must never:** replace human judgment, self-authorize a SEAL, skip 888_JUDGE, or issue verdicts without a constitutional chain.

### Trinity Orthogonal Role (SATU PERMUKAAN)
**arifOS = LAW / JUDGMENT**
- Primary question: **"Can this be allowed?"**
- Owns: F1–F13 floors, verdicts (SEAL/HOLD/VOID), boundary enforcement, evidence standards.
- Must not: execute, display state to operator, route tasks.
- See also: AAA (STATE/ROUTING/VISIBILITY), A-FORGE (EXECUTION/MUTATION)
- One-line: arifOS is the judge; AAA is the cockpit; A-FORGE is the hand.

Full doctrine: [GENESIS/040_APEX_STACK.md](https://github.com/ariffazil/arifos/blob/main/GENESIS/040_APEX_STACK.md)

**Orthogonal CANON:** [ariffazil/CANON.md](https://github.com/ariffazil/ariffazil/blob/main/CANON.md) — this repo owns **ART + KERNEL + VAULT999 write**. A-FORGE owns APA + ACT. AAA owns doctrine + TREE777. Product space: ART × KERNEL × APA × ACT → VAULT999.

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

## 3. The 8 Canonical Public Tools (2026-07-15)

All tools use `arif_<verb>` naming. Internal aliases are absorbed as modes on canonical tools.
The surface is exactly 8 tools on the wire — diagnostic tools, aliases, and the entropy mesh are filtered from `tools/list` by default.

| # | Tool | Stage | What It Does | Modes |
|---|------|-------|--------------|-------|
| 1 | `arif_init` | 000 | Session ignition. Binds actor identity, floors, audit. Always first. | `init`, `light`, `resume`, `validate`, `canary`, `preflight`, `triage` |
| 2 | `arif_observe` | 111 | Sense reality into evidence. Returns OBS/DER/INT/SPEC labels. | `search`, `fetch`, `ingest`, `vitals`, `compass`, `atlas`, `entropy_dS` |
| 3 | `arif_think` | 333 | Structured reasoning. Plan, reflect, verify, critique. | `reason`, `reflect`, `verify`, `plan`, `critique`, `metabolize`, `axioms` |
| 4 | `arif_route` | 444 | Route intent to federation organ. Optional governed bridge call. | `route`, `bridge` |
| 5 | `arif_memory` | 555 | Constitutional memory governor. L1-L6 stack. | `recall`, `inspect`, `attest`, `remember`, `promote`, `revise`, `forget` |
| 6 | `arif_judge` | 888 | Constitutional verdict — SEAL/HOLD/SABAR/VOID. | `judge`, `compare`, `history`, `explain`, `floor_status`, `witness_consensus` |
| 7 | `arif_forge` | 777 | Guarded execution gate. REQUIRES prior arif_judge SEAL + lease. | `dry_run`, `engineer`, `query`, `write`, `generate`, `commit`, `recall` |
| 8 | `arif_seal` | 999 | VAULT999 immutable append. Irreversible. Needs `ack_irreversible`. | `seal`, `verify`, `chain`, `list`, `dry_run` |

```
000 → 111 → 333 → 444 → 555 → 888 → 777 → 999
init  observe think  route memory judge forge seal
```

**Internal aliases (absorbed into canonical modes):**
| Old name | Now | Via |
|----------|-----|-----|
| `arif_triage` | `arif_init(mode=preflight\|triage)` | mode |
| `arif_critique` | `arif_think(mode=critique)` | mode |
| `arif_bridge_connect` | `arif_route(mode=bridge)` | mode |
| `arif_compose` | `arif_forge(mode=compose)` | mode |
| `arif_act` | `arif_forge` | rename |
| `arif_fetch` | `arif_observe(mode=fetch)` | mode |
| `arif_verify` | `arif_seal(mode=verify)` | mode |

**Iron rules:**
- No action skips judge. No organ self-authorizes.
- Pass `session_id` / `session_token` every hop.
- After SEAL → `arif_forge`.
- `arif_forge` requires `seal_verdict_id` from prior `arif_judge` SEAL.

**Source of truth:** `server.py` → `tools/list` (runtime) beats any static manifest. `mcp.json` and `fastmcp.json` are documentation mirrors.

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
| **arifOS** (this repo) | Constitutional kernel. 8 semantic capabilities, profile-specific adapters, 13 floors. | ← you are here |
| **A-FORGE** | Executor. 52 MCP tools. Gates + A-THINK law. | [`ariffazil/A-FORGE`](https://github.com/ariffazil/A-FORGE) |
| **AAA** | Cockpit. A2A mesh. Agent registry. React 19 dashboard. | [`ariffazil/AAA`](https://github.com/ariffazil/AAA) |

---

## 🔌 MCP Connection

Connect to arifOS via the Model Context Protocol. Two transports are supported:

### Streamable HTTP (Public)

| Property | Value |
|----------|-------|
| **Endpoint** | `https://mcp.arif-fazil.com/mcp` |
| **Alternate** | `https://arif-fazil.com/mcp` |
| **Transport** | Streamable HTTP (JSON-RPC 2.0) |
| **Protocol** | MCP 2025-11-25 |
| **Kernel ABI** | 8 canonical tools |
| **Health** | `https://arifos.arif-fazil.com/health` |
| **Auth** | None required for init/observe/think/route. Judge/forge/seal need session+authority. |

### STDIO (Local)

```bash
npx -y arifos-mcp
```

### Claude Code / Cursor

```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://mcp.arif-fazil.com/mcp"
    }
  }
}
```

### Connecting from ChatGPT

arifOS exposes `arif_search` and `arif_fetch` for ChatGPT MCP discovery (always on — set by `ARIFOS_CHATGPT_COMPAT=true`). ChatGPT clients will auto-discover search + fetch capabilities.

### Connecting from Claude Desktop

Copy the config from `claude_desktop_config.json` in this repo, or use stdio:

```json
{
  "mcpServers": {
    "arifOS": {
      "command": "npx",
      "args": ["-y", "arifos-mcp"],
      "autoApprove": ["arif_init", "arif_observe", "arif_think", "arif_route", "arif_memory", "arif_canary"]
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

- MCP Server Card: `.well-known/mcp/server.json` — MCP Inspector / Smithery discovery
- Agent Card: `https://aaa.arif-fazil.com/.well-known/agent-card.json` (AAA owns the canonical A2A card)
- MCP Manifest: `https://arifos.arif-fazil.com/.well-known/mcp.json`

---

## 8. License & Sovereignty

**AGPL-3.0.** The constitution must remain open. The kernel must remain inspectable.

**Muhammad Arif bin Fazil** is F13 SOVEREIGN. His veto is absolute. No algorithm overrides. No agent bypasses. No institution supersedes.

---

<div align="center">

```
arifOS · Port 8088 · 8 canonical tools · 13 floors · 6 live organs
AGPL-3.0 · Sovereign: Arif Fazil · Federation: ALIVE
ChatGPT ✓ · Claude Desktop ✓ · Streamable HTTP + STDIO
DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
```

</div>
