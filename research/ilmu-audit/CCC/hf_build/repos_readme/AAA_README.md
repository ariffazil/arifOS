# AAA — Reality Engineering Console + Agent Operations Cockpit

> **AAA is the control plane for the arifOS federation — the cockpit where human operators see every agent, every verdict, and every sealed decision in real time.** It enforces the separation of cognitive powers (Mind proposes, Heart judges, Soul authorizes) through structured protocols rather than prompts. It is the parliament and the air traffic control tower of the constitutional AI system.

> **Repository:** https://github.com/ariffazil/AAA  
> **Purpose:** The mission control room for your AI agent federation.  
> **Protocol:** AREP v1.0 — Arif Reality Engineering Protocol (forged 2026-06-04)

[![A2A Protocol](https://img.shields.io/badge/A2A-v1.0.0-8b5cf6?logo=google&logoColor=white)](https://aaa.arif-fazil.com/.well-known/agent-card.json)
[![Node](https://img.shields.io/badge/node-22-339933?logo=node.js&logoColor=white)](package.json)
[![React](https://img.shields.io/badge/react-19-61DAFB?logo=react&logoColor=black)](package.json)
[![Vite](https://img.shields.io/badge/vite-8-646CFF?logo=vite&logoColor=white)](package.json)
[![Port](https://img.shields.io/badge/port-3001-64748b?logo=express&logoColor=white)](deploy/Caddyfile)
[![License](https://img.shields.io/badge/license-AGPL--3.0-ef4444?logo=gnu)](LICENSE)

<!-- SOT-MANIFEST
owner: Arif
last_verified: 2026-06-04
valid_from: 2026-06-04
valid_until: 2026-09-04
confidence: high
scope: /root/AAA
-->

---

## AREP — The Protocol That Replaces Prompts

AAA is no longer just a dashboard. It is now the **Reality Engineering Console** — the place where you declare intent, the machine verifies reality, and the federation executes.

**Prompt engineering is dead.** AREP replaces it with a four-layer truth stack and reality gating:

```
Human: "forge all organ with deepseek integration"
         │
         ▼
   POST /api/arep/submit
         │
    AREP Task Manager:
     1. Validate declaration (schema check)
     2. Reality gates (6-organ health probe)
     3. If HALT → VOID. If ESCALATE → HOLD.
     4. All gates pass → execute → VAULT999 seal
         │
         ▼
   RealityConsole (3-pane cockpit):
     PANE 1: INTENT BOARD   — active tasks, delegation chains
     PANE 2: REALITY FEED   — live health probes, evidence layers
     PANE 3: VERDICT QUEUE  — HOLDs awaiting human, floor vetoes
```

**The prompt was never visible. The reality was.**

> Read the full article: [I Stopped Writing Prompts. Here's What Replaces Them: AREP](https://medium.com/@arifbfazil/i-stopped-writing-prompts-heres-what-replaces-them-8fc445f02732)

### The Four-Layer Truth Stack

| Layer | Anchor | Verification |
|-------|--------|-------------|
| **GROUND_TRUTH** | VAULT999 sealed events | Merkle chain integrity |
| **VERIFIED_STATE** | Live health probe, model registry | curl /health + passport check |
| **CACHED_STATE** | L3 Qdrant, session memory | Freshness timestamp |
| **INFERRED** | Agent reasoning | Bounded by constitutional floors |

An agent cannot claim a higher layer than its evidence supports. You cannot infer your way to ground truth.

---

## The Simplest Explanation

AAA is the **control tower** for your AI agents.

It does not fly the plane. It does not write the law. It does not build the engine. It knows which plane is where, who is piloting, what route they are on, and who should receive the next instruction.

In human terms, AAA is:

- **Airport control tower** — sees all agents, their status, their routes
- **Company org chart** — who exists, what their role is, who reports to whom
- **Employee directory** — agent cards, permissions, capabilities
- **Task dispatch desk** — where does this task go next?
- **Mission dashboard** — what is the current federation map?

---

## What AAA Answers

| Question | AAA's Answer |
|----------|--------------|
| Which agents exist? | `a2a/registry/`, `agents/`, `registries/agents.yaml` |
| What is each agent allowed to do? | Agent cards, permission profiles, contracts |
| Which agent should handle this task? | Routing rules, domain-plane matching, handoff protocols |
| How do agents talk to each other? | A2A protocol, federation bridge, message types |
| Where does a task go next? | Workflow contracts, escalation paths, org topology |
| Who is responsible for this handoff? | Separation-of-duties rules, signer roles, audit trails |
| What is the current federation map? | Registries, observability dashboard, health endpoints |
| **How do I declare intent without prompts?** | **`POST /api/arep/submit` — AREP task declaration** |
| **Is reality verified before execution?** | **Reality gates: 6-organ health probe + evidence floor check** |
| **What truth layer is this task at?** | **RealityConsole — 4-layer stack from GROUND_TRUTH to INFERRED** |

---

## What AAA Is NOT

| Boundary | Reason |
|----------|--------|
| **NOT** the constitutional authority | F1-F13, 888_JUDGE, 999_VAULT live in `arifOS` |
| **NOT** an MCP server | Canonical 13-tool surface is `arifOS` port 8088 |
| **NOT** a domain calculator | GEOX, WEALTH, WELL own their own domains |
| **NOT** the execution engine | A-FORGE builds, deploys, and executes |
| **NOT** a workspace or dumping ground | Runtime files, backups, and experiments belong elsewhere |

> **MCP is a toolbox. AAA is the manager who knows which worker should use which toolbox.**

---


---

## Directory Structure

```
AAA/
├── src/                        # React 19 cockpit UI (Vite 8, TS 6, Tailwind 4)
│   ├── App.tsx                 # Root + hash router
│   ├── Cockpit.tsx             # Main dashboard — live floor grid, mission intake
│   ├── main.tsx                # React entry (+ webmcp init)
│   ├── gateway/                # A2A TypeScript server (v0.3.0) + AREP types
│   │   └── arep-types.ts       # AREP TypeScript definitions — RealityLayer, DelegationLink, AREPTask
│   ├── components/cockpit/
│   │   └── RealityConsole.tsx  # AREP 3-pane cockpit — Intent Board, Reality Feed, Verdict Queue
│   ├── adapter/                # Governance adapter (A-FORGE bridge)
│   ├── ai/                     # AI chat panel (Ollama / arifOS / OpenRouter)
│   ├── components/             # shadcn/ui + TrinityNav + SessionConsent
│   ├── seed/                   # Control-plane seed data
│   ├── hooks/                  # React hooks
│   └── lib/                    # cn() + utilities
├── a2a/                        # A2A design surface (specs, doctrine)
│   ├── agent-cards/            # Per-agent capability cards (design)
│   ├── registry/               # Consolidated registry YAML
│   ├── policies/               # Auth and trust policies
│   ├── federation-bridge.yaml  # Inter-organ routing
│   ├── A2A_DIALOGUE.md         # Protocol dialogue spec
│   └── AAA_TREATY_LAW.md       # Treaty-level contract
├── a2a-server/                 # Standalone A2A gateway (Node.js/Express) + AREP runtime
│   ├── server.js               # HTTP bridge (port 3001) + /api/arep/* endpoints
│   ├── arep-task-manager.js    # AREP engine — reality gates, task lifecycle, vault sealing
│   ├── agent-cards/            # Runtime agent cards
│   ├── vault.js                # VAULT999 integration client
│   └── Dockerfile              # Container for A2A gateway
├── public/                     # Static-served assets (mirrored to dist/)
│   └── a2a/                    # Live A2A surface — agent-card, agents.json
│       ├── agent-card.json     # Canonical A2A card (protocol_version 0.3.0)
│       ├── agents.json         # Live runtime agent registry
│       ├── status.json         # Gateway health
│       └── index.html          # Static A2A info page
├── agents/                     # Per-agent identity directories
│   ├── hermes-asi/             # Hermes ASI config + runtime
│   ├── hermes-ops/             # Hermes ops config
│   ├── openclaw/               # OpenClaw agent identity
│   ├── opencode/               # OpenCode agent identity
│   ├── apex/                   # APEX agent card (read-only)
│   ├── antigravity/            # [staging] Antigravity test bed
│   └── maxhermes/              # [staging] MaxHermes variant
├── contracts/                  # YAML governance contracts
├── registries/                 # Canonical YAML registries (agents/skills/tools)
├── schemas/                    # JSON/YAML schemas + AREP contracts
│   ├── arep-task.schema.json  # Canonical AREP task contract (JSON Schema 2020-12)
│   ├── arep-reality-layers.schema.json  # Four-layer truth stack specification
│   ├── SCHEMA_REGISTRY.json   # Schema index for agent discovery
│   └── arep-example-forge-integration.json  # Validating example
├── services/a2a-gateway/       # Service definition for A2A gateway
├── observability/              # Grafana + Prometheus configs (Nine-Signal)
├── deploy/                     # Docker + Caddy configs
├── ops/                        # Runbooks and workflows
├── docs/                       # Architecture + federation docs
├── wiki/                       # Operational wiki
├── tests/                      # Test suite (test_contract_parity.py)
├── dist/                       # Build output (`npm run build` → dist/)
├── .well-known/                # A2A discovery surface
├── FEDERATION_COCKPIT.md       # Internal federation contract (SOT)
├── AGENTS.md                   # Repo boot protocol
└── ADR/                        # Architecture Decision Records
```

---

## Agent Registry

**HEXAGON — 6 agents (3 primary + 3 support)** — canonical source: `agents/HEXAGON.yaml`, live registry: `public/a2a/agents.json`. Renamed from PENTAGON 2026-06-04.

### 3 PRIMARY agents (active decision triangle)

| Agent | Class | Role | Stage / Ring | Host Organs |
|-------|------|------|---|---|
| `333-AGI` | AGI | General Intelligence + Execution (FORGE subsumed) | 333 MIND | arifOS + GEOX + WEALTH + WELL + A-FORGE |
| `555-ASI` | ASI | Watcher — ethical + memory + audit lineage | 555 MEMORY | arifOS + WELL |
| `888-APEX` | APEX | Constitutional judge — F1–F13 arbitration | 888 JUDGE | arifOS |

### 2 SUPPORT agents (kinda like support agents — parallel, not in active decision flow)

| Agent | Class | Role | Stage / Ring | Host |
|-------|------|------|---|---|
| `A-AUDIT` | APEX oversight | Continuous ethical + safety monitor | [oversight] HEART | arifOS + WELL |
| `A-ARCHIVE` | ASI service | Immutable ledger keeper + audit trail | 999 SEAL | VAULT999 |

**Organs are infrastructure** — the 7 federated organs (Hermes, OpenClaw, A-FORGE, arifOS, GEOX, WEALTH, WELL) host the 6 HEXAGON agents but are no longer in the A2A agent registry. **Sovereign (000-SALAM)** is above the registry. **3 sub-routines** (111-SENSE, 444-KERNEL, 555-MEMORY) are internal arifOS tools called by the 5 agents.

> APEX (888_JUDGE) is a constitutional organ of arifOS, not an agent managed by AAA.  
> AAA holds APEX's **agent card** for discovery purposes only. Verdict authority stays in arifOS.

Full agent cards: `a2a/agent-cards/`  
Design registry: `a2a/registry/agents.yaml`  
**Live runtime registry** (what Cockpit actually queries): `public/a2a/agents.json`

---

## A2A Protocol

**Protocol version:** `v0.3.0` (canonical — see `public/a2a/agent-card.json` → `protocol_version`)  
**MCP protocol:** `v1.0.0-FORGED` (canonical — see `arifOS/CLAUDE.md`)

The federated A2A protocol defines how agents communicate. Key message types:

| Type | Purpose | Gate |
|------|---------|------|
| `task_request` | Request task execution | Routing rules |
| `skill_advert` | Broadcast capabilities | AUTO |
| `handoff_request` | Transfer task between agents | F2 authority check |
| `memory_share` | Share session context | F9_VAL gate |

Protocol spec: `a2a/federated_a2a_protocol.md`  
Federation bridge: `a2a/federation-bridge.yaml`

---

## Validation

```bash
cd /root/AAA

# Install
npm install

# Build
npm run build

# Validate contracts and registry consistency
npm run validate:aaa
```

---


---

## Canonical Authority Notice

AAA is the **control plane / cockpit** — not a constitutional authority.  
The sovereign constitution and F1–F13 floors live in `ariffazil/arifOS`.  
888_JUDGE, 999_VAULT, and constitutional law are **not** owned here.

For live federation status, see `ariffazil/arifOS/FEDERATION_STATUS.md`.

---

## AAA Namespace Disambiguation

**This repo is `AAA-Cockpit`** — the operations control plane and A2A gateway.

AAA is polymorphic by design. There are multiple valid surfaces:

| Term | Surface | Role |
|------|---------|------|
| **AAA-HF** | Hugging Face dataset [`ariffazil/AAA`](https://hf.co/datasets/ariffazil/AAA) | Doctrine corpus, F1–F13 floors, verdicts, schemas, gold eval records |
| **AAA-Cockpit** | **This repo** (`ariffazil/AAA`) | Control plane, A2A gateway, agent registry, routing dashboard |
| **AAA-Doctrine** | Conceptual layer | Constitutional principle: alignment, authority, accountability |
| **AAA-Interface** | Operator surface | Human visibility — inspect actions, approvals, seals |
| **AAA-Eval** | Benchmark layer | Gold records and evaluation harness |

**What this repo (AAA-Cockpit) does NOT do:**
- Own F1–F13 constitutional judgment (that is `arifOS`)
- Define the doctrine corpus (that is `AAA-HF` on Hugging Face)
- Execute irreversible actions unilaterally
- Replace VAULT999 as the sealed archive

**The invariant chain:**

```
AAA-HF       defines doctrine.
arifOS       applies doctrine.
MCP tools    execute only if allowed.
Supabase     records constitutional receipts.
VAULT999     seals final artifacts.
AAA-Cockpit  displays the governed state to Arif.   ← THIS REPO
Arif         remains F13 final sovereign authority.
```

> "AAA is polymorphic by design. When precision matters, qualify the surface."
 — Intelligence is forged, not given.

## 🏛️ Federation

| Organ | Repository | Role | Port |
|-------|-----------|------|------|
| **arifOS** | [ariffazil/arifOS](https://github.com/ariffazil/arifOS) | Constitutional Kernel · F1-F13 | 8088 |
| **AAA** | [ariffazil/AAA](https://github.com/ariffazil/AAA) | Reality Console · A2A Gateway | 3001 |
| **A-FORGE** | [ariffazil/A-FORGE](https://github.com/ariffazil/A-FORGE) | Execution Shell | 7071 |
| **GEOX** | [ariffazil/geox](https://github.com/ariffazil/geox) | Earth Intelligence | 8081 |
| **WEALTH** | [ariffazil/wealth](https://github.com/ariffazil/wealth) | Capital Intelligence | 18082 |
| **WELL** | [ariffazil/well](https://github.com/ariffazil/well) | Human Readiness | 18083 |
| **arif-sites** | [ariffazil/arif-sites](https://github.com/ariffazil/arif-sites) | Public Surfaces | 443 |

> **Constitutional authority:** F1-F13 floors, 888_JUDGE, and VAULT999 live in `ariffazil/arifOS`.  
> **Live federation status:** See `ariffazil/arifOS/FEDERATION_STATUS.md`.
## 📄 Contributing

This repository operates under the arifOS Federation constitution (F1–F13).  
See [AGENTS.md](AGENTS.md) for the canonical boot sequence and agent operating rules.

## 📜 License

AGPL-3.0. See [LICENSE](LICENSE).

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given.



> **Evidence Contract.** This organ emits the standard envelope (epistemic_tag, evidence_quality, source_attribution, uncertainty_band, delta_S) per [arifOS 000_CONSTITUTION.md](../../arifOS/static/arifos/theory/000/000_CONSTITUTION.md) Appendix B. arifOS reads the envelope and applies L01–L13. This organ does not self-judge.


## Changelog

- **v2026.06.06-LAW-SEAL** (2026-06-06): Constitution pointer added to arifOS canonical 000_CONSTITUTION.md. AAA emits Evidence Contract; does not self-judge. AGENTS.md updated.
