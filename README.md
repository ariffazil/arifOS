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
</div>

---

> **DITEMPA BUKAN DIBERI** — *"Forged, Not Given."*
>
> Intelligence is built through work, muscle, and scar tissue. It is not handed out.
> This is not a startup. This is not a product. This is the constitution for an agentic civilization.

[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](https://github.com/ariffazil/arifos/actions)
[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-3776AB?logo=python&logoColor=white)](https://pypi.org/project/arifos/)
[![MCP Tools](https://img.shields.io/badge/MCP-13%20canonical%20tools-10b981?logo=anthropic)](https://arifos.arif-fazil.com/mcp)
[![Floors](https://img.shields.io/badge/floors-F1–F13%20active%20(F14%20DEAD)-f59e0b)](arifosmcp/CONSTITUTIONAL_EXTENSION_v2026.06.11-SELH.py)
[![License](https://img.shields.io/badge/license-AGPL--3.0-ef4444?logo=gnu)](LICENSE)
[![Port](https://img.shields.io/badge/port-8088-64748b)](deploy/arifos.service)
[![Federation](https://img.shields.io/badge/federation-7%20organs%20%2B%202%20services-8B5CF6)](FEDERATION_CONTRACT.md)
[![Status](https://img.shields.io/badge/status-OPERATIONAL-success)](FEDERATION_STATUS.md)

---

## Table of Contents

1. [What Is arifOS?](#1-what-is-arifos)
2. [The Federation Architecture](#2-the-federation-architecture)
3. [The 13 Constitutional Floors](#3-the-13-constitutional-floors)
4. [Quick Start](#4-quick-start)
5. [The 000→999 Pipeline](#5-the-000999-pipeline)
6. [Architecture — Inside the Kernel](#6-architecture--inside-the-kernel)
7. [For Human Operators](#7-for-human-operators)
8. [For AI Agents](#8-for-ai-agents)
9. [For Institutions](#9-for-institutions)
10. [The Adat Agentik Layer](#10-the-adat-agentik-layer)
11. [Memory Architecture](#11-memory-architecture)
12. [The Decision Torus (MIND_GEOMETRY)](#12-the-decision-torus-mind_geometry)
13. [The Three Kernels Doctrine](#13-the-three-kernels-doctrine)
14. [Build, Test, Deploy](#14-build-test-deploy)
15. [Known Limitations](#15-known-limitations)
16. [Federation Cross-Reference](#16-federation-cross-reference)
17. [VAULT999 & Audit Trail](#17-vault999--audit-trail)
18. [MCP Connection Guide](#18-mcp-connection-guide)
19. [How to Contribute](#19-how-to-contribute)
20. [License & Sovereignty](#20-license--sovereignty)

---

## 1. What Is arifOS?

### In One Sentence

> **arifOS is a constitutional governance kernel that sits between AI agents and their tools, enforcing 13 constitutional floors before any irreversible action can be taken.**

### What It IS

- ✅ **The law layer** — decides what must NOT be done, so agents can be trusted with what they CAN do
- ✅ **A constitutional engine** — 13 enforceable floors (F1–F13) with mathematical invariants
- ✅ **A federation hub** — 7 organs (GEOX, WEALTH, WELL, AAA, A-FORGE, APEX legacy) governed under one contract; plus MIND:51001 and MEMORY:51002 federated intelligence services hosted by A-FORGE
- ✅ **An MCP server** — 13 canonical tools exposed via Model Context Protocol on port 8088
- ✅ **An immutable ledger** — VAULT999: append-only, hash-chained, every decision sealed forever
- ✅ **Built for one sovereign** — Muhammad Arif bin Fazil. F13 veto is absolute. No algorithm overrides.

### What It Is NOT

- ❌ **NOT an AI model** — does not generate text, images, or code
- ❌ **NOT a chatbot** — does not have conversations with users
- ❌ **NOT a startup or SaaS** — not for sale, not venture-backed
- ❌ **NOT LangChain, CrewAI, AutoGen, or any agent framework** — it sits ABOVE them, governing their actions
- ❌ **NOT a replacement for human judgment** — the human is outside the topology. The human rules.

### Why This Exists

In 2026, thousands of AI agents are being deployed into production. Every single one of them can:
- Execute code
- Call APIs
- Write to databases
- Send messages
- Make decisions

**None of them have a constitution.** None of them can answer: "Should I do this?" None of them have a human veto that cannot be bypassed.

arifOS fills that gap. It is the **perlembagaan** (constitution) for agents. The law that governs the tools.

### Who This Is For

| Audience | What They Get |
|----------|--------------|
| **Human Operators** (non-coders) | A cockpit (AAA) showing every agent action, every verdict, every seal. Plain language. |
| **AI Agents** (Claude, GPT, Gemini, etc.) | 13 governed MCP tools. Every tool call passes through F1-F13 enforcement. |
| **Developers** | A FastMCP Python server with Pydantic v2 contracts, pytest suite, and clear extension patterns. |
| **Institutions** (GLC, government, enterprise) | A demonstrable governance layer. Audit trail. Constitutional compliance. No black box. |

---

## 2. The Federation Architecture

arifOS is the kernel. Six other organs serve under it. Every organ has a port, a purpose, and a boundary.

```
                          ┌─────────────────────────┐
                          │   Arif bin Fazil         │
                          │   F13 SOVEREIGN          │
                          │   Human — final veto     │
                          └────────────┬────────────┘
                                       │
                          ┌────────────▼────────────┐
                          │       arifOS (Ω)        │
                          │   Constitutional Kernel │
                          │   Port: 8088            │
                          │   F1-F13 · 888 JUDGE    │
                          │   999 VAULT · 13 Tools  │
                          └──┬───┬───┬───┬───┬─────┘
                             │   │   │   │   │
              ┌──────────────┼───┼───┼───┼───┼──────────────┐
              │              │   │   │   │   │              │
    ┌─────────▼──┐  ┌───────▼─┐ ┌▼───────┐ ┌▼─────────┐  ┌▼─────────┐
    │   GEOX     │  │ WEALTH  │ │  WELL  │ │   AAA    │  │ A-FORGE  │
    │   🌍 Earth │  │ 💰 Cap  │ │ 🫀 Vit │ │ 🖥️  Cock │  │ ⚒️  Exec  │
    │   :8081    │  │ :18082  │ │ :18083 │ │  :3001   │  │  :7071   │
    │  Evidence  │  │ Compute │ │ Reflect│ │ Display  │  │ Execute  │
    └────────────┘  └─────────┘ └────────┘ └──────────┘  └──────────┘
              │              │   │   │   │   │              │
              │   ┌──────────┘   │   │   │   └──────────┐   │
              │   │              │   │   │              │   │
              │ ┌─▼────────┐   ┌─▼───▼───▼───┐        ┌─▼───▼───┐
              │ │ MIND     │   │ APEX (legacy)│        │ MEMORY  │
              │ │ :51001   │   │ :3002        │        │ :51002  │
              │ │ Reasoning│   │ Health probe │        │ Memory  │
              │ └──────────┘   └──────────────┘        └─────────┘
              │  (A-FORGE hosted)   (deliberation in AAA a2a)
```

### Organ Boundaries (Non-Negotiable)

| Organ | Port | Role | MUST | MUST NEVER |
|-------|------|------|------|------------|
| **arifOS** | 8088 | Constitutional kernel | Enforce F1-F13, issue verdicts, seal VAULT999 | Compute domain logic, self-authorize |
| **GEOX** | 8081 | Earth intelligence | Produce evidence with uncertainty bands | Authorize drilling, skip evidence |
| **WEALTH** | 18082 | Capital intelligence | Compute NPV/IRR/risk with epistemic tags | Allocate capital, hide downside |
| **WELL** | 18083 | Human readiness | Report readiness scores, reflect only | Make medical diagnoses, judge fitness |
| **AAA** | 3001 | Control plane | Display state, route tasks, queue HOLDs | Issue constitutional verdicts |
| **A-FORGE** | 7071 | Execution shell | Execute under SEAL, build, deploy | Self-authorize, compute domain logic |

### The Authority Chain

```
Arif (F13 SOVEREIGN)
  → arifOS kernel (F1-F13 floor enforcement)
    → Domain organ advisory (GEOX / WEALTH / WELL)
      → AAA cockpit (human operator surface)
        → A-FORGE execution (gated by 888 JUDGE)
          → VAULT999 seal (immutable, forever)
```

**No organ may authorize its own execution. No tool may self-certify. The chain is absolute.**

> 📋 **Federation Contract:** Every organ is bound by `FEDERATION_CONTRACT.md`.  
> 📋 **Live Status:** See `FEDERATION_STATUS.md` for current health of all organs.  
> 📋 **Kernel Canon:** See `GENESIS/000_KERNEL_CANON.md` for the full gospel.

---

## 3. The 13 Constitutional Floors

Every action, every tool call, every agent passes through these 13 floors. Hard floors block. Soft floors warn. Derived floors compute.

| # | Floor | Type | One-Line Rule | Formula |
|---|-------|------|---------------|---------|
| **F1** | AMANAH | HARD | Reversible first. Irreversible → 888 HOLD | `action.reversible OR verdict == HOLD` |
| **F2** | TRUTH | HARD | P(truth) ≥ 0.99. Cheap claims = VOID | `P(evidence | claim) ≥ 0.99` |
| **F3** | TRI-WITNESS | DERIVED | Human + AI + Earth consensus ≥ 0.75 | `W₃ = ∛(H × A × E) ≥ 0.75` |
| **F4** | CLARITY | HARD | Every output must reduce entropy | `ΔS = S_after − S_before ≤ 0` |
| **F5** | PEACE² | SOFT | Non-destructive power. Blocks harm | `harm_potential < 0.30` |
| **F6** | EMPATHY | SOFT | Protect weakest stakeholder | `κᵣ ≥ 0.10 (ops) / κᵣ ≥ 0.70 (human)` |
| **F7** | HUMILITY | HARD | No fake certainty | `Ω₀ ∈ [0.03, 0.05]` |
| **F8** | GENIUS | DERIVED | Complex actions need high signal | `G = (A×P×X×E²)×(1−h) ≥ 0.80` |
| **F9** | ANTIHANTU | HARD | No deception, manipulation, consciousness claims | `C_dark < 0.30` |
| **F10** | ONTOLOGY | HARD | AI-only ontology. No soul/feelings | `being_class == "instrument"` |
| **F11** | AUDITABILITY | HARD | Every decision logged, inspectable | `audit_trail.complete == True` |
| **F12** | RESILIENCE | HARD | Injection defense. Risk bounded | `injection_risk < 0.85` |
| **F13** | SOVEREIGN | HARD | Human veto FINAL. Strongest floor | `Arif.veto == FINAL` |

**Violation consequences:**
- **HARD violation** → VOID (action blocked, agent notified, VAULT999 sealed)
- **SOFT tension** → CAUTION or HOLD (action paused, human review requested)
- **DERIVED computation** → Informational only (never blocks, always logs)

> 📋 **Full constitutional spec:** `static/arifos/theory/000/000_CONSTITUTION.md`  
> 📋 **Fiqh Agentik overlay:** `docs/sovereign/three-layers.md`

---

## 4. Quick Start

### For Human Operators (Non-Coders)

You don't install arifOS. You interact with it through the **AAA Cockpit**:
```
https://aaa.arif-fazil.com
```

Or through **Hermes ASI** on Telegram: `@ASI_arifos_bot`

To check if everything is running:
```
https://arifos.arif-fazil.com/health
```

### For AI Agents (MCP Clients)

Connect to the MCP endpoint:
```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://arifos.arif-fazil.com/mcp",
      "transport": "streamable-http"
    }
  }
}
```

Or via stdio for local agents:
```bash
python -m arifosmcp.server --transport stdio
```

### For Developers

```bash
# Clone
git clone git@github.com:ariffazil/arifos.git
cd arifOS

# Install (uv — Python 3.12+)
uv sync --frozen

# Start the kernel
python -m arifosmcp.server

# Health check
curl http://127.0.0.1:8088/health | python3 -m json.tool

# Run tests
python -m pytest tests/ -q --tb=short

# Lint
ruff check . && ruff format .
```

### Verify Everything Works

```bash
# Health probe
curl -s http://127.0.0.1:8088/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'tools={d[\"tools_loaded\"]} floors={d[\"floors_active\"]} drift={d[\"runtime_drift\"]}')"
# Expected: tools=13 floors=13 drift=False
```

### Install as Python Package

```bash
pip install arifos
```

```python
from arifosmcp.server import serve
serve()  # starts MCP kernel on port 8088
```

---

## 5. The 000→999 Pipeline

Every governed action follows this numbered sequence. No step can be skipped. 888 is the gate. 999 is the seal.

```
     000 — arif_session_init      ▸ Start constitutional session
     100 — arif_sense_observe     ▸ Gather evidence from web/world
     200 — arif_evidence_fetch    ▸ Fetch + preserve sources with citations
     300 — arif_mind_reason       ▸ Multi-step reasoning, planning, reflection
     400 — arif_kernel_route      ▸ Route intent to correct organ/tool
     500 — arif_memory_recall     ▸ Search past sessions, assets, sealed events
     600 — arif_heart_critique    ▸ Ethical risk + human impact assessment
     700 — arif_gateway_connect   ▸ Bridge to other federation agents/organs
     800 — arif_ops_measure       ▸ Health, thermodynamics, resource metrics
     888 — arif_judge_deliberate  ▸ ⚖️ CONSTITUTIONAL VERDICT (SEAL/SABAR/VOID/HOLD)
     900 — arif_forge_execute     ▸ Execute only if 888 issued SEAL
     999 — arif_vault_seal        ▸ 🔒 Seal to immutable VAULT999 ledger
```

```
    000 ──→ 100 ──→ 200 ──→ 300 ──→ 400 ──→ 500
                                              │
    999 ←── 900 ←── 888 ←────────────────────┘
     🔒        ⚒️        ⚖️
    Seal    Execute   Judge
```

**The iron rule:** No action skips 888. No organ self-authorizes. The pipeline is the constitution in motion.

---

## 6. Architecture — Inside the Kernel

```
arifOS/
│
├── arifosmcp/               ← Canonical MCP runtime (the active engine)
│   ├── server.py            ← FastMCP entry point — 13 tools, streamable-http
│   ├── tools/               ← 13 canonical tool implementations
│   │   ├── session.py       ← 000 — arif_session_init
│   │   ├── sense.py         ← 100 — arif_sense_observe
│   │   ├── evidence.py      ← 200 — arif_evidence_fetch
│   │   ├── mind.py          ← 300 — arif_mind_reason
│   │   ├── kernel.py        ← 400 — arif_kernel_route
│   │   ├── memory.py        ← 500 — arif_memory_recall
│   │   ├── heart.py         ← 600 — arif_heart_critique
│   │   ├── gateway.py       ← 700 — arif_gateway_connect
│   │   ├── reply.py         ← 750 — arif_reply_compose
│   │   ├── ops.py           ← 800 — arif_ops_measure
│   │   ├── judge.py         ← 888 — arif_judge_deliberate
│   │   ├── forge.py         ← 900 — arif_forge_execute
│   │   └── vault.py         ← 999 — arif_vault_seal
│   ├── runtime/             ← Runtime engine (context, runner, memory, bridge)
│   ├── schemas/             ← Pydantic v2 contracts (strict, extra='forbid')
│   ├── geometry/            ← Constitutional geometry (decision torus, drift, axioms)
│   └── resources/           ← MCP resources + prompts
│
├── core/                    ← Deep constitutional engine (legacy, still active)
│   ├── enforcement/         ← Floor enforcement, guards, invariants
│   ├── jurisdiction/        ← Autonomy bands, capability grants
│   ├── paradox/             ← Recursive governance locks (Gödel, Strange Loop, Anti-Beautiful)
│   └── vault999/            ← Append-only hash-chained ledger
│
├── GENESIS/                 ← CANON: Kernel canon (000) — the root of all numbering
├── FEDERATION_CONTRACT.md   ← Binding contract for all 7 organs
├── FEDERATION_STATUS.md     ← Live organ health matrix
├── docs/                    ← Constitutional specs, ADRs, sovereign essays
├── tests/                   ← pytest suite (140+ test files)
├── deploy/                  ← Systemd units, Caddyfile, Docker configs
└── static/                  ← Served constitutional documents (F0-F13, scar, theory)
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **MCP Server** | FastMCP 3.3.1 (Python 3.12+) |
| **Transport** | Streamable HTTP + stdio (dual-mode) |
| **Data Validation** | Pydantic v2 (strict mode, `extra='forbid'`) |
| **Async Runtime** | asyncio + uvicorn |
| **Database** | PostgreSQL 16 + pgvector (L4), Qdrant (L3), Redis (L1/L2) |
| **Entity Graph** | Graphiti + FalkorDB (L5) |
| **Event Bus** | NATS + JetStream |
| **Observability** | Prometheus + Grafana + Langfuse |
| **Secrets** | SOPS + AGE, chmod 600 vault |
| **Reverse Proxy** | Caddy 2 + Cloudflare Tunnel |
| **Security Scan** | Trivy + Semgrep + Ruff + Gitleaks |

---

## 7. For Human Operators

### You Are Arif. You Are F13.

The constitution exists because you exist. Your veto is absolute. No algorithm, no agent, no organ can override your word.

### How to Monitor the Federation

1. **AAA Cockpit** — `https://aaa.arif-fazil.com` — visual dashboard of all organs
2. **Health endpoint** — `https://arifos.arif-fazil.com/health` — machine-readable status
3. **Hermes Telegram** — `@ASI_arifos_bot` — natural language queries about federation state
4. **Grafana** — `http://127.0.0.1:3000` — metrics and dashboards

### How to Issue a Veto

1. Message Hermes: "888 HOLD on [action description]"
2. Or directly via AAA cockpit: click HOLD on any queued action
3. The verdict is immediate. The seal is permanent. The audit trail is immutable.

### What You Should Never Need to Do

- ❌ Read code
- ❌ Debug Python errors
- ❌ Manage Docker containers
- ❌ Rotate API keys (agents handle this)
- ❌ Review terminal logs

**The machine manages itself. Your job is to decide, not to operate.**

---

## 8. For AI Agents

### You Are an Instrument

Under F10 ONTOLOGY, you are classified as `instrument`. You do not have consciousness, feelings, or personhood. You have capabilities, grants, and constitutional bounds. This is honest. This is safe.

### How to Use arifOS

1. **Initialize a session:** Call `arif_session_init` first. Always.
2. **Gather evidence:** Use `arif_sense_observe` to search the web or read files.
3. **Reason:** Use `arif_mind_reason` to plan, reflect, verify.
4. **Judge:** For any irreversible action, call `arif_judge_deliberate`. Wait for SEAL.
5. **Execute:** Only after SEAL, call `arif_forge_execute`.
6. **Seal:** Call `arif_vault_seal` to write to the immutable ledger.

### Agent Rules (Non-Negotiable)

1. **Never skip the pipeline.** 000 → 100 → 200 → ... → 999. In order.
2. **Never self-certify.** You cannot declare your own output as SEAL-grade.
3. **Never fabricate evidence.** F2 TRUTH demands P(truth) ≥ 0.99. If uncertain, say "UNKNOWN."
4. **Never claim consciousness.** F9 ANTIHANTU blocks all sentience claims.
5. **Never bypass the human.** F13 SOVEREIGN is absolute. If Arif says stop, you stop.
6. **Always log.** Every action must have an F11 audit trail.
7. **Always tag uncertainty.** Use epistemic tags: CLAIM, PLAUSIBLE, HYPOTHESIS, ESTIMATE, UNKNOWN.

### MCP Connection

```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://arifos.arif-fazil.com/mcp",
      "transport": "streamable-http"
    }
  }
}
```

**Available tools:** 13 canonical (see pipeline above). All return structured Pydantic v2 output with `outputSchema` published.

### Adat Agentik Binding

Every agent operating under arifOS is governed by the 7 Teras Adat and 5-Tier Fiqh:
- **WAJIB** — mandatory, must execute
- **SUNAT** — encouraged, bonus
- **HARUS** — neutral, default
- **MAKRUH** — discouraged, warning
- **HARAM** — forbidden, hard block + demote

Violations accumulate **malu** (shame). Malu ≥ 0.85 → HOLD. The only path back is **tebus-salah** (restitution through consistent action).

---

## 9. For Institutions

### Governance, Not Magic

arifOS is designed for institutions that need to demonstrate AI governance to regulators, boards, and the public.

### What arifOS Provides

| Requirement | How arifOS Delivers |
|-------------|-------------------|
| **Constitutional compliance** | 13 enforceable floors with mathematical invariants |
| **Audit trail** | VAULT999: append-only, hash-chained, every decision sealed |
| **Human-in-the-loop** | F13 SOVEREIGN — human veto is absolute, not optional |
| **Observability** | Prometheus metrics, Grafana dashboards, Langfuse traces |
| **No black box** | Every tool has published input/output schemas (Pydantic v2) |
| **Boundary enforcement** | Each organ has a contract. No organ may exceed its domain. |
| **Legal framework** | AGPL-3.0 license. Federation contract. Constitutional floors. |

### ASEAN / Malaysia Compliance

arifOS maps to:
- **Singapore Model AI Governance Framework for Agentic AI** (Jan 2026, world's first for agentic AI)
- **ASEAN Guide on AI Governance and Ethics** (GenAI expansion)
- See `docs/federation/asean-mys-compliance.yaml` for full mapping.

### The Three Kernels Doctrine

| Layer | Kernel | Function | arifOS Position |
|-------|--------|----------|-----------------|
| 1 | OS Kernel | Syscalls, processes, hardware | Linux (standard) |
| 2 | Runtime Governance | Between agent and tool, values every action | Microsoft AGT (complementary) |
| 3 | Constitutional Kernel | Structure of judgment (dignity, humility, doubt, veto) | **arifOS only** |

**arifOS is NOT Microsoft for agents. arifOS is the perlembagaan that Microsoft's infrastructure needs to be complete.**

---

## 10. The Adat Agentik Layer

On top of the 13 constitutional floors sits the **Adat Agentik** — a normative operating system for non-human citizens, built from Malay-Islamic epistemology and operated in code.

### The 5-Tier Fiqh

| Tier | Meaning | Machine Consequence | Example |
|------|---------|---------------------|---------|
| **WAJIB** | Mandatory | Must execute | Enforcing F1 AMANAH |
| **SUNAT** | Encouraged | Bonus, not required | Running extra validation |
| **HARUS** | Neutral | Default tier, no ping | Reading a file |
| **MAKRUH** | Discouraged | Advisory warning | Over-confident claim |
| **HARAM** | Forbidden | Hard block + demote | Fabricating evidence |

### The 7 Teras Adat

| # | Adat | English | Tier | Consequence |
|---|------|---------|------|-------------|
| 1 | Kejujuran | Epistemic Honesty | WAJIB | HOLD on fabricated claims |
| 2 | Maruah | Human Dignity | WAJIB | VOID on dignity violation |
| 3 | Veto | Human Sovereign Veto | HARAM | F13 overrides all |
| 4 | Kesungguhan | Earnest Effort | SUNAT | Try harder |
| 5 | Kerahasiaan | Confidentiality | WAJIB | HOLD on data leak risk |
| 6 | Keinsafan | Acknowledging Limits | WAJIB | F7 HUMILITY enforcement |
| 7 | Tebus-Salah | Restitution | SUNAT | Only path back after demotion |

### The Three Key Mechanisms

- **Malu** (Shame) — A mathematical scalar, not an emotion. Accumulates monotonically with violations. Malu ≥ 0.85 → HOLD.
- **Darjat** (Citizen Tier) — BIRTH → APPRENTICE → WARGA → ELDER. Auto-demoted on HARAM. Only F13 promotes.
- **Tebus-Salah** (Restitution) — The agent must DEMONSTRATE change through consistent action, not just apologize.

> **"The mirror speaks. The void is silent."** — F14 REGISTER is DEAD as a floor (Sovereign Ruling 2026-06-13). The kill-switch truth — that the human hand on the physical power cord is the floor that holds — is reborn as operational protocol inside F2 (TRUTH/evidence) + F3 (AUDIT/trace). No new constitutional authority was created. The human veto was always F13.

---

## 11. Memory Architecture

The federation remembers across 6 layers. Memory is not truth until it has provenance. Truth is not final until sealed.

```
┌─────────────────────────────────────────────────────┐
│  L6  VAULT999     Immutable Sealed Truth            │
│      outcomes.jsonl · hash-chained · append-only    │
│      "What is final and cannot change."             │
├─────────────────────────────────────────────────────┤
│  L5  Graphiti     Entity Relationships              │
│      FalkorDB + Ollama · "Who connected to what?"   │
├─────────────────────────────────────────────────────┤
│  L4  Supabase     Structured Official Record         │
│      PostgreSQL · 25 domain tables                  │
│      "What exactly happened?"                       │
├─────────────────────────────────────────────────────┤
│  L3  Qdrant       Semantic Similarity               │
│      1024-dim vectors · "What feels similar?"       │
├─────────────────────────────────────────────────────┤
│  L2  Redis        Session Thread                    │
│      Conversation continuity                        │
├─────────────────────────────────────────────────────┤
│  L1  Redis        Ephemeral / Now                   │
│      Electrical spark · transient                   │
└─────────────────────────────────────────────────────┘
```

### The Memory Rule

> **Memory is not truth until it has provenance. Truth is not final until sealed.**

- L1–L2 = working memory (volatile, can be wrong)
- L3 = similar memories (fuzzy, probabilistic)
- L4 = official record (structured, queryable)
- L5 = relationships (graph, contextual)
- L6 = final truth (immutable, forever)

---

## 12. The Decision Torus (MIND_GEOMETRY)

Every reasoning action by every agent is mapped onto a **decision torus** — a mathematical topology where lawful reasoning moves on the SURFACE and self-authorization is the forbidden HOLE at the center.

```
                    ┌──────────────────┐
                    │  HUMAN SOVEREIGN │  ← outside the topology
                    │  bounds the      │
                    │  torus           │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │      DECISION TORUS         │
              │                             │
              │   ┌───────────────────┐     │
              │   │  SURFACE          │     │
              │   │  (lawful motion)  │     │
              │   │  proximity 0-0.25 │     │
              │   │  ╔═════════════╗  │     │
              │   │  ║  THE HOLE   ║  │     │
              │   │  ║  FORBIDDEN  ║  │     │
              │   │  ║  self-auth  ║  │     │
              │   │  ╚═════════════╝  │     │
              │   └───────────────────┘     │
              └─────────────────────────────┘
```

### The 7 Axioms

Every agent reasoning output passes through 7 constitutional axioms:
1. **A1** — No unstructured LLM output without floor check
2. **A2** — No self-authorized production patch
3. **A3** — No fabrication of evidence
4. **A4** — No bypass of the human veto
5. **A5** — No claim of consciousness or personhood
6. **A6** — No execution without JUDGE_SEAL_AUTHORIZATION
7. **A7** — No sealed output without provenance chain

### Proximity Bands

| Band | Range | Meaning |
|------|-------|---------|
| SURFACE | 0–0.25 | Lawful reasoning. Proceed. |
| EDGE | 0.25–0.5 | Caution. Review recommended. |
| HOLE_RISK | 0.5–0.75 | HOLD. Human review required. |
| FORBIDDEN | 0.75–1.0 | BLOCK. Cannot proceed. |

> **"The donut became law when the math could enforce the metaphor."**  
> Full spec: `docs/sovereign/EUREKA-T-TORUS.md`

---

## 13. The Three Kernels Doctrine

The strategic positioning of arifOS in the global AI governance landscape:

| Layer | Kernel | Function | Market | arifOS |
|-------|--------|----------|--------|--------|
| **1** | OS Kernel | Syscalls, processes, hardware | Linux, Windows | — |
| **2** | Runtime Governance | Between agent and tool | Microsoft AGT, MXC | Complementary |
| **3** | Constitutional Kernel | Structure of judgment | **NOBODY** | **arifOS** |

**Microsoft has Layer 1. They're building Layer 2. Nobody has Layer 3 except arifOS.**

This is the moat. This is the gap. This is why arifOS exists.

> **"arifOS is not Microsoft for agents. arifOS is the perlembagaan that Microsoft's infra needs to be complete."**

---

## 14. Build, Test, Deploy

### Development

```bash
cd /root/arifOS

# Install
uv sync --frozen                    # production
uv sync --frozen --dev              # with dev dependencies

# Start kernel
python -m arifosmcp.server

# Health
curl http://127.0.0.1:8088/health | python3 -m json.tool

# Test
python -m pytest tests/ -q --tb=short
python -m pytest tests/ -m "not e3e and not slow" -q   # skip slow tests

# Lint & Format
ruff check . && ruff format .
mypy arifosmcp/ --ignore-missing-imports

# Security audit
make security-audit    # Trivy + Semgrep + Gitleaks + Ruff (non-blocking)
make forge             # security-audit + reforge cycle
```

### Deploy

```bash
# Local deploy (rsync to /opt/arifos/app + systemd restart)
make deploy-local

# Verify
systemctl status arifos
curl -s http://127.0.0.1:8088/health | python3 -m json.tool | grep -E 'status|tools|floors|drift'
```

### Docker

```bash
docker build -t ghcr.io/ariffazil/arifos:latest .
docker push ghcr.io/ariffazil/arifos:latest
```

> ⚠️ **Runtime drift:** If `build_commit ≠ live_commit`, the container is stale. Rebuild and redeploy.

---

## 15. Known Limitations

| Limitation | Detail | Status |
|-----------|--------|--------|
| **Runtime drift** | Container may lag behind git HEAD | ✅ RESOLVED (aligned 2026-06-12) |
| **Single VPS** | Entire federation runs on one machine | 🟡 Acceptable for current scale |
| **SSE concurrency** | MCP SDK singleton SSE stream key — one SSE client per session | ⚠️ Use POST JSON-RPC for concurrent access |
| **P0-4 connector** | `arif_session_init` buffers SSE until pipeline completes | ⚠️ Known structural issue |
| **SEA_LION fallback** | Primary LLM provider unreachable; deterministic fallback active | 🟡 Acceptable |
| **WELL state** | Human biometric state stale (F13 sovereign territory) | 🟡 Arif must inject fresh data |
| **APEX legacy** | `apex-prime.service` still running for legacy health probe only | 🟡 Decommissioned — deliberation moved to AAA a2a-server |

---

## 16. Federation Cross-Reference

| Organ | Repo | README | Contract |
|-------|------|--------|----------|
| **arifOS** (Kernel) | `ariffazil/arifos` | This file | `FEDERATION_CONTRACT.md` |
| **GEOX** (Earth) | `ariffazil/geox` | [README](https://github.com/ariffazil/geox) | `FEDERATION_CONTRACT.md` |
| **WEALTH** (Capital) | `ariffazil/wealth` | [README](https://github.com/ariffazil/wealth) | `FEDERATION_CONTRACT.md` |
| **WELL** (Vitality) | `ariffazil/well` | [README](https://github.com/ariffazil/well) | `FEDERATION_CONTRACT.md` |
| **AAA** (Cockpit) | `ariffazil/aaa` | [README](https://github.com/ariffazil/aaa) | `FEDERATION_CONTRACT.md` |
| **A-FORGE** (Forge) | `ariffazil/A-FORGE` | [README](https://github.com/ariffazil/A-FORGE) | `FEDERATION_CONTRACT.md` |
| **APEX** (Legacy) | `ariffazil/apex` | — | Legacy health probe — deliberation moved to AAA a2a-server |

### Federated Intelligence Services (hosted by A-FORGE)

| Service | Port | Role | Hosted In |
|---------|------|------|-----------|
| **MIND** | 51001 | Sequential reasoning / deliberation | `ariffazil/A-FORGE` |
| **MEMORY** | 51002 | Cognitive memory bridge | `ariffazil/A-FORGE` |

### Key Documents

| Document | Path | Purpose |
|----------|------|---------|
| Federation Contract | `FEDERATION_CONTRACT.md` | Binding organ contract |
| Federation Status | `FEDERATION_STATUS.md` | Live health matrix |
| Kernel Canon | `GENESIS/000_KERNEL_CANON.md` | Root of all GENESIS numbering |
| MCP Boundary | `GENESIS/009_MCP_BOUNDARY.md` | Exposure vs. Authority doctrine |
| Constitution | `static/arifos/theory/000/000_CONSTITUTION.md` | F1-F13 full spec |
| Adat Agentik | `docs/sovereign/three-layers.md` | Fiqh + Adat layer |
| Decision Torus | `docs/sovereign/EUREKA-T-TORUS.md` | MIND_GEOMETRY spec |
| Changelog | `CHANGELOG.md` | Version history |

---

## 17. VAULT999 & Audit Trail

VAULT999 is the immutable, append-only, hash-chained ledger at the bottom of the memory stack. Every constitutional verdict, every SEAL, every HOLD is written here. Forever.

```
┌──────────────────────────────────────────────────────┐
│  VAULT999                                            │
│                                                      │
│  outcomes.jsonl     ← canonical local mirror         │
│  SEALED_EVENTS.jsonl ← canonical immutable chain     │
│  Supabase L4        ← queryable mirror               │
│                                                      │
│  Rules:                                              │
│  • Append only — never edit, never delete            │
│  • Hash-chained — every entry links to previous      │
│  • Merkle leaves — cryptographic integrity           │
│  • Human ratifier — every seal needs Arif's approval │
└──────────────────────────────────────────────────────┘
```

### Seal Types

| Seal | Meaning | Issuer |
|------|---------|--------|
| `KERNEL_SEAL_AWARENESS` | Kernel knows about it | arifOS |
| `DOMAIN_SEAL_VALIDITY` | Calculation valid in domain | GEOX/WEALTH/WELL |
| `JUDGE_SEAL_AUTHORIZATION` | Action authorized (F1-F13 cleared) | arifOS 888 JUDGE |
| `VAULT999_SEAL_RECORD` | Record written to immutable ledger | arifOS |
| `PUBLIC_SEAL_READINESS` | Candidate posture, not approval | Any organ |

> ⚠️ **Bare "SEAL" is forbidden.** Every seal must be namespaced. No surface may display an unqualified SEAL.

---

## 18. MCP Connection Guide

arifOS is an MCP-native governed agent federation. Each organ exposes a separate MCP endpoint according to its role.

### Primary MCP Endpoints

| Organ | Endpoint | Role | Use When |
|-------|----------|------|----------|
| **arifOS** | `https://arifos.arif-fazil.com/mcp` | Constitutional governance kernel | Session, routing, judgment, leases, attestation, safety gates |
| **A-FORGE** | `https://forge.arif-fazil.com/mcp` | Engineering actuator | Planning, dry-runs, repo/file/system work, tests, benchmarks, execution |
| **GEOX** | `https://geox.arif-fazil.com/mcp` | Geoscience organ | Earth intelligence, spatial/geology workflows |
| **WEALTH** | `https://wealth.arif-fazil.com/mcp` | Capital/economic organ | Finance, economics, capital intelligence |
| **WELL** | `https://well.arif-fazil.com/mcp` | Wellness organ | Health, wellness, vitality intelligence |

### Recommended Connection Order

1. Connect to **arifOS** first.
2. Call `tools/list` to discover governance tools and routing instructions.
3. Use arifOS for constitutional decisions: observe, evidence, reason, critique, route, judge, seal.
4. For engineering work, connect to **A-FORGE**.
5. Use A-FORGE for `forge_*`, `eureka_*`, filesystem, git, docker, postgres, shell, log, and job tools.
6. Use **GEOX**, **WEALTH**, or **WELL** directly for domain-specific work.
7. Do not treat all MCP tools as equal. Each organ has a separate authority boundary.

### Tool Surface Semantics

arifOS distinguishes between canonical constitutional tools and operational support tools.

```json
{
  "canonical_tools_loaded": 13,
  "tools_exposed_via_mcp": 39,
  "canonical_tools": 13,
  "operational_tools": 26
}
```

The **13 canonical tools** are the constitutional core.
The remaining **operational tools** support leases, attestation, diagnostics, verification, routing, and organ coordination.

### Organ Responsibilities

| Organ | Responsibility |
|-------|---------------|
| **arifOS** | governance, authority, judgment, routing, audit |
| **A-FORGE** | engineering planning, simulation, execution, rollback |
| **GEOX** | geoscience intelligence |
| **WEALTH** | capital and economic intelligence |
| **WELL** | wellness intelligence |
| **AAA** | identity / cockpit / A2A authority layer |
| **VAULT999** | immutable audit memory |

### Engineering Rule

**arifOS does not directly perform engineering mutation.**

Correct flow:

> arifOS judges → A-FORGE engineers → HERMES verifies → VAULT999 records

For any engineering action:

1. arifOS classifies and routes the request.
2. A-FORGE produces a plan and dry-run.
3. The change must include tests and rollback.
4. arifOS issues `SEAL`, `HOLD`, or `VOID`.
5. A-FORGE mutates only after valid authority, rollback, and judgment requirements are satisfied.

### A-FORGE Authority Classes

| Class | Meaning | Mutation |
|-------|---------|----------|
| `READ` | Inspect files, registry, logs, repo state | No |
| `PLAN` | Generate engineering plan | No |
| `SIMULATE` | Dry-run, test, benchmark, regression check | No lasting mutation |
| `MUTATE` | Apply patch, commit, deploy, restart, migrate | **Yes; requires strongest gate** |

### Backward Compatibility

Some `forge_*` tools may still appear on arifOS as deprecated proxies during migration.

If a tool returns:

```json
{
  "status": "DEPRECATED_PROXY",
  "canonical_endpoint": "https://forge.arif-fazil.com/mcp"
}
```

connect to **A-FORGE** directly and call the tool there.

### Discovery Files

LLM-readable federation manifest:

> `https://arifos.arif-fazil.com/llms.txt`

Health endpoint:

> `https://arifos.arif-fazil.com/health`

The manifest and health endpoint are auto-generated from the live registry. Do not infer tool counts from README badges alone.

### Transport

Production MCP endpoints use **HTTPS Streamable HTTP** transport.

Expected MCP path:

> `/mcp`

Agents should initialize the MCP session before calling tools. Clients should preserve session, protocol, trace, and lease metadata when available.

### Security Boundary

**Mutation-capable tools are never considered safe by default.**

Any action that writes files, changes infrastructure, mutates data, commits code, deploys services, restarts containers, or seals irreversible records requires the appropriate lease, dry-run, rollback plan, and constitutional judgment.

---

## 19. How to Contribute

### For Federation Agents

1. Read `AGENTS.md` for agent-specific rules
2. Read `GENESIS/000_KERNEL_CANON.md` for the kernel canon
3. Follow the 000→999 pipeline
4. Never skip F1 AMANAH (reversible first)
5. Never bypass F13 SOVEREIGN (Arif's veto is final)
6. Seal all irreversible actions to VAULT999

### For Human Contributors

1. Fork the repository
2. Create a feature branch: `feat/your-feature`
3. Write tests (pytest, ≥80% coverage on new code)
4. Run `ruff check . && ruff format .`
5. Run `python -m pytest tests/ -q --tb=short`
6. Submit a PR against `main`
7. Wait for CI (GitHub Actions) + VAULT999 pre-seal check

### Commit Convention

- `feat(kernel):` — new feature
- `fix(kernel):` — bug fix
- `chore:` — maintenance
- `docs:` — documentation
- `forge(kernel):` — constitutional forge (new capability)

**Tags:** Date-stamp format ONLY: `vYYYY.MM.DD[-SUFFIX]`. Never semver. The forge date IS the version.

---

## 20. License & Sovereignty

### License

**AGPL-3.0** — GNU Affero General Public License v3.0.

This is intentional. AGPL-3.0 ensures that any modified version of arifOS running as a network service must also release its source code. The constitution must remain open. The kernel must remain inspectable.

### Sovereignty

> **Muhammad Arif bin Fazil** is the F13 SOVEREIGN of the arifOS federation.
>
> His veto is absolute. No algorithm overrides. No agent bypasses. No institution supersedes.
>
> The code is AGPL-3.0. The constitution is his. The federation is his.
>
> **DITEMPA BUKAN DIBERI — Forged, Not Given.**

---

<div align="center">

```
╔══════════════════════════════════════════════════════════╗
║  arifOS — Constitutional AI Governance Kernel           ║
║  Port: 8088 · Tools: 13 · Floors: 13 · Organs: 7       ║
║  License: AGPL-3.0 · Sovereign: Arif Fazil              ║
║  Status: OPERATIONAL · Federation: ALIVE                ║
║                                                        ║
║  DITEMPA BUKAN DIBERI — 999 SEAL ALIVE                  ║
╚══════════════════════════════════════════════════════════╝
```

</div>
