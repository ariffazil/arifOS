<!-- mcp-name: ariffazil/arifos -->
<!-- SOT-MANIFEST
federation_release: v2026.07.12-CONSOLIDATION-EPOCH
last_verified: 2026-07-12T23:38Z
deployed_commit: 192b20da
deployed_branch: main
dev_commit: 182266c
dev_branch: security/identity-multikey-2026-07-12
live_version: kanon-1403cac
runtime_path: /opt/arifos/app
runtime_drift: true
drift_detail: build=1403cac vs deployed=192b20da (marker corrected)
owner_summary: YELLOW (runtime drift)
tools_exposed_via_mcp: 8
canonical_tools_loaded: 8
total_declared_tools: 48
spine_p0_sct: live (sct_v1 mint; store-delete full loop; apex UNMEASURED at birth)
arif_triage: DEPRECATED_ALIAS → arif_init(mode=preflight|triage)
arif_act: internal_only (never in allowed_next_verbs)
changelog: /root/arifOS/CHANGELOG.md
p0_actor_id_binding: live (kernel reads JWT lineage first; self-report caps MEDIUM)
floor_11b_amanah_replay: live (nonce required for IRREVERSIBLE mutations; 24h cache)
a2a_agent_json: /root/arifOS/.well-known/agent.json
machine_sot: /root/.claude/jobs/5d0ce6b2/tmp/artifacts/FEDERATION-SOT-20260712/MACHINE-SOT-2026-07-12.json
maturity_pipeline: EXECUTED 2026-07-11 (promote 7, incubate 5, park 4, kill APEX as live track)
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

[![Unified CI](https://github.com/ariffazil/arifos/actions/workflows/01-unified-ci.yml/badge.svg?branch=main)](https://github.com/ariffazil/arifos/actions/workflows/01-unified-ci.yml)
[![MCP Conformance](https://github.com/ariffazil/arifos/actions/workflows/06-mcp-conformance.yml/badge.svg?branch=main)](https://github.com/ariffazil/arifos/actions/workflows/06-mcp-conformance.yml)
[![MCP Surface](https://img.shields.io/badge/MCP%20surface-12%20canonical%20tools-0a7b83)](arifosmcp/PUBLIC_SURFACE_CANON.md)
[![Federation](https://img.shields.io/badge/Federation-6%20organs-1f6feb)](#1-what-is-arifos)
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
- **An MCP server** — 12 canonical public verbs (SATU PERMUKAAN 2026-07-09 Spine P0; source: `arifosmcp/runtime/public_surface.py` CANONICAL_12). Session standing rides signed `sct_v1` capability tokens. One intent = one public tool. See `arifosmcp/PUBLIC_SURFACE_CANON.md`.
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

## 3. The 12 Canonical Public Tools (Spine P0 — 2026-07-10)

Default `tools/list` is the **12-verb public facade** (`arifosmcp/PUBLIC_SURFACE_CANON.md`).
Session standing rides signed **`sct_v1`** tokens (store = optional cache). Birth apex is **UNMEASURED**.

| # | Tool | Stage | What It Does |
|---|------|-------|---------------|
| 1 | `arif_init` | 000 | Start session + mint `session_token`. Modes: `init`, `light`, **`preflight`**, **`triage`**, `canary`. Always first. |
| 2 | `arif_observe` | 111 | Reality sensing — search, fetch, vitals, compass. (`arif_fetch` = mode, not public verb.) |
| 3 | `arif_think` | 333 | Reason, plan, reflect. (`arif_mind_reason` = internal only.) |
| 4 | `arif_route` | 444 | Route intent to federation organ. Modes: `route`, `bridge`. |
| 5 | `arif_bridge_connect` | 444-direct | Direct organ call (HIGH). Prefer `arif_route` by default. |
| 6 | `arif_critique` | 555 | Maruah / risk before irreversible action. |
| 7 | `arif_memory` | 555m | Constitutional memory governor. |
| 8 | `arif_judge` | 888 | Verdict — SEAL / HOLD / SABAR / VOID. Kernel judges; does not seal. |
| 9 | `arif_forge` | 777 | Guarded execution after SEAL. (`arif_act` internal-only — never in `allowed_next_verbs`.) |
| 10 | `arif_compose` | reply | Final human reply. Call LAST. |
| 11 | `arif_seal` | 999 | VAULT999 immutable ledger. Prefer `verify`/`dry_run` until SOVEREIGN. |
| 12 | `arif_verify` | E1 | JITU pre-execution gate — SEAL token verification for IRREVERSIBLE shell. |

```

000 → 111 → 333 → 444 → 444-direct → 555 → 555m → 777 → 888 → reply → 999 → E1
init  observe think route bridge       critique memory forge judge compose seal verify
```
**Demoted / not public:** `arif_triage` → `arif_init(mode=preflight|triage)`; `arif_fetch` → `arif_observe(mode=fetch)`; `arif_act` → `arif_forge`.

**Iron rules:**
- No action skips judge. No organ self-authorizes.
- Pass `session_token` every hop — do not re-interrogate store-only `session_id`.
- After SEAL → `arif_forge`; reply last → `arif_compose`.

**Source of truth:** `PUBLIC_SURFACE_CANON.md` → `runtime/public_surface.py` → `tool_registry.json` (`canonical_order`) → live `/health`.

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
| **arifOS** (this repo) | Constitutional kernel. 12 canonical public verbs. 13 floors. The judge. | ← you are here |
| **A-FORGE** | Executor. 98 MCP tools. Gates + A-THINK law. | [`ariffazil/A-FORGE`](https://github.com/ariffazil/A-FORGE) |
| **AAA** | Cockpit. A2A mesh. Agent registry. React 19 dashboard. | [`ariffazil/AAA`](https://github.com/ariffazil/AAA) |

---

## 🔌 MCP Connection

Connect to arifOS via the Model Context Protocol:

| Property | Value |
|----------|-------|
| **Endpoint** | `https://mcp.arif-fazil.com/mcp` |
| **Alternate** | `https://arif-fazil.com/mcp` |
| **Transport** | Streamable HTTP (JSON-RPC 2.0) |
| **Tools** | 12 canonical public verbs |
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
arifOS · Port 8088 · 12 canonical public verbs · 13 floors · 6 live organs
AGPL-3.0 · Sovereign: Arif Fazil · Federation: ALIVE
DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
```

</div>
