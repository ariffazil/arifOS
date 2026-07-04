# A-FORGE — Governed Agent Execution Runtime

> **A constitutional kernel without a governed execution shell is just a PDF.**
>
> A-FORGE receives approved plans from arifOS, applies constitutional gates inline,
> executes across 5+ MCP organs, and produces telemetry for the AAA cockpit.

[![Node](https://img.shields.io/badge/node-22-339933?logo=node.js&logoColor=white)](package.json)
[![TypeScript](https://img.shields.io/badge/typescript-6.0-3178C6?logo=typescript&logoColor=white)](package.json)
[![License](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](LICENSE)
[![Port](https://img.shields.io/badge/port-7071-64748b?logo=express&logoColor=white)](deploy/Caddyfile)
[![Federation](https://img.shields.io/badge/federation-arifOS-8B5CF6)](https://github.com/ariffazil/arifOS)

---

## What Is A-FORGE?

A-FORGE is the **execution body** of the [arifOS Federation](https://github.com/ariffazil/arifOS). It is not a general-purpose agent framework. It is a governed runtime that applies constitutional law (L1–L13) at every execution boundary.

```
arifOS  = constitutional kernel  → can it be done?
AAA     = control plane          → what should be done?  
A-FORGE = execution shell        → do it, safely, with evidence
```

### Constitutional Boundary (Critical)

> **A-FORGE NEVER computes constitutional verdicts.** It ONLY verifies the cryptographic proof of a verdict issued by arifOS.

- The constitutional judge lives in  (port 8088).
- A-FORGE has a  middleware that verifies, never invents.
-  calls from A-FORGE are proxied to arifOS kernel (see commit `18b6187`).
- No  enum exists in A-FORGE `src/`. If you need a verdict, ask arifOS.

**Do not add verdict logic to A-FORGE.** Doing so creates a second constitutional kernel and breaks the doctrine (one kernel, one constitution).

### The Forge Gate

Every execution passes through 4 constitutional gates **before** any tool runs:

| Layer | Gate | What It Checks |
|-------|------|---------------|
| 1 | **F1 AMANAH** | Catastrophic action detection (`rm -rf /`, `DROP TABLE`, etc.) |
| 2 | **ModelCapabilityGate** | Spine-check against arifOS registry `model_governance_card` |
| 3 | **Governance Bridge** | F3 Witness · F6 Empathy · F9 Anti-Hantu · F11 Coherence |
| 4 | **ApprovalBoundary** | Irreversibility threshold → 888_HOLD escalation |

A-FORGE cannot self-authorize. Every forge requires `JUDGE_SEAL_AUTHORIZATION` from arifOS.

---

## Federation Architecture

```
┌────────────────────────────────────────────┐
│                arifOS (judge)              │
│    L1–L13 · SEAL/SABAR/VOID · VAULT999     │
└────────────────┬───────────────────────────┘
                 │ JUDGE_SEAL_AUTHORIZATION
                 ▼
┌────────────────────────────────────────────┐
│              A-FORGE (execute)             │
│  4-layer forge gate · 62+ tools · telemetry│
└──┬──────────┬──────────┬───────────────────┘
   │          │          │
   ▼          ▼          ▼
┌──────┐ ┌────────┐ ┌──────┐
│ GEOX │ │WEALTH  │ │ WELL │
│earth │ │capital │ │human │
└──────┘ └────────┘ └──────┘
```

On startup, A-FORGE auto-discovers 62+ tools from 5 organs via MCP/A2A bridges. Health probe at `/api/federation-probe`.

---

## Quick Start

```bash
# Clone
git clone https://github.com/ariffazil/A-FORGE.git
cd A-FORGE

# Install & build
npm install
npm run build

# Start
node dist/src/server.js

# Verify
curl http://localhost:7071/health | python3 -m json.tool
# → {"ok": true, "service": "A-FORGE", "version": "2026.06.05"}

# Federation status
curl http://localhost:7071/api/federation-probe | python3 -m json.tool
# → { "verdict": "GREEN", "up": 5, "total": 5, ... }
```

See [QUICKSTART.md](QUICKSTART.md) for detailed setup, standalone mode, and stdio MCP configuration.

---

## Key Capabilities

### Governed Execution Pipeline
- 4-layer constitutional gate chain (F1 → ModelCapabilityGate → Governance → ApprovalBoundary)
- [PlanValidator](src/planner/PlanValidator.ts) with `verifyGovernanceCard()` and reversibility scoring
- 888_HOLD escalation with Postgres-backed approval tickets

### Federation MCP Bridge
- 62+ tools auto-discovered from 5 organs (arifOS, GEOX, WEALTH, WELL, A-FORGE)
- Graceful degradation when organs are unavailable
- `/api/federation-probe` endpoint for live status

### Terminal Forge
- Interactive terminal with streaming LLM (SSE parsing, token-by-token)
- Session persistence (`/save`, `/load`, `/sessions`)
- Federation commands: `/tools`, `/federation`, `/status`, `/retry`

### Multi-Provider LLM
- [BudgetAwareRouter](src/llm/BudgetAwareRouter.ts) — cheapest capable model
- [FallbackProvider](src/llm/FallbackProvider.ts) — graceful degradation on outage
- Providers: MiniMax-M3, SEA_LION, Ollama, OpenAI-compatible

### Observability
- Prometheus metrics (port 7071)
- Supabase tool call receipts
- Langfuse session traces
- VAULT999 escalation records

---

## Repository Map

| File | Purpose |
|------|---------|
| [CONSTITUTION.md](CONSTITUTION.md) | A-FORGE's constitutional role and boundaries |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Full module architecture (150 files, 16 modules) |
| [INVARIANTS.md](INVARIANTS.md) | Live ports, federation topology, forbidden assumptions |
| [QUICKSTART.md](QUICKSTART.md) | 15-minute local setup |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [AGENTS.md](AGENTS.md) | Agent operating rules and boundary contract |

### Source Modules

```
src/
├── engine/         Core agent loop (AgentEngine, PipelineCoordinator, IntentRouter)
├── governance/     Constitutional floor enforcement (16 files, F1–F11)
├── planner/        Plan validation (PlanValidator, ParallelPlannerContract)
├── approval/       Approval & escalation (ApprovalBoundary, 888_HOLD routing)
├── mcp/            MCP server implementation (Express, stdio, HTTP transports)
├── bridges/        Organ MCP bridges (GEOX, WEALTH)
├── llm/            Multi-provider LLM (streaming SSE, budget routing, fallback)
├── tools/          Tool registry & implementations (FileTools, ShellTools, etc.)
├── memory/         Layered memory (ShortTermMemory → LongTermMemory)
├── vault/          VAULT999 integration (Postgres, Supabase, Merkle)
├── cli/            Terminal forge (interactive session, federation commands)
├── a2a/            A2A protocol (agent card, task routing)
└── types/          Type contracts (16 files)
```

---

## Federation Organs

A-FORGE is one of **7 organs** in the arifOS Federation, running on VPS `af-forge` (72.62.71.199):

| Organ | Repository | Role | Port |
|-------|-----------|------|------|
| **arifOS** | [ariffazil/arifOS](https://github.com/ariffazil/arifOS) | Constitutional Kernel · L1–L13 | 8088 |
| **A-FORGE** | [ariffazil/A-FORGE](https://github.com/ariffazil/A-FORGE) | Execution Shell | 7071 |
| **AAA** | [ariffazil/AAA](https://github.com/ariffazil/AAA) | Control Plane · Cockpit | 3001 |
| **GEOX** | [ariffazil/geox](https://github.com/ariffazil/geox) | Earth Intelligence | 8081 |
| **WEALTH** | [ariffazil/wealth](https://github.com/ariffazil/wealth) | Capital Intelligence | 18082 |
| **WELL** | [ariffazil/well](https://github.com/ariffazil/well) | Human Readiness | 18083 |
| **arif-sites** | [ariffazil/arif-sites](https://github.com/ariffazil/arif-sites) | Public Surfaces | 443 |

> **Constitutional authority:** L1–L13 floors, 888_JUDGE, and VAULT999 live in [ariffazil/arifOS](https://github.com/ariffazil/arifOS).
> **Live status:** See [FEDERATION_STATUS.md](https://github.com/ariffazil/arifOS/blob/main/FEDERATION_STATUS.md).

---

## Boundary Contract

A-FORGE **does not**:
- Issue constitutional verdicts (SEAL/SABAR/VOID) → arifOS
- Perform geoscience computation (Vsh, PHIE, Sw) → GEOX
- Run economic evaluation (NPV, IRR, EMV) → WEALTH
- Self-authorize any irreversible action

A-FORGE **does**:
- Route intents to the correct organ
- Apply constitutional gates at every execution boundary
- Execute approved plans with full telemetry
- Handle orchestration, retries, and escalation

**Rule:** If code needs NumPy / Pandas / reservoir physics → wrong layer. If code judges constitutionality → wrong layer.

---

## License

AGPL-3.0. See [LICENSE](LICENSE).

The governed execution runtime is free software. The constitutional authority (arifOS) remains the sole arbiter of its lawful use.

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**



> **Evidence Contract.** This organ emits the standard envelope (epistemic_tag, evidence_quality, source_attribution, uncertainty_band, delta_S) per [arifOS 000_CONSTITUTION.md](../../arifOS/static/arifos/theory/000/000_CONSTITUTION.md) Appendix B. arifOS reads the envelope and applies L01–L13. This organ does not self-judge.


## Changelog

- **v2026.06.06-LAW-SEAL** (2026-06-06): Constitution unified. arifOS canonical 000_CONSTITUTION.md. 13 Laws (L01-L13) live in arifOS only. Evidence Contract line added. AGENTS.md updated.
