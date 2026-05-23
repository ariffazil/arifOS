# arifOS Machine Kernel — HERMES FORGE BLUEPRINT
**Version:** 1.0-FORGE
**Date:** 2026-05-23
**Sovereign:** Muhammad Arif bin Fazil
**Author:** arifOS Ω-Forge Agent
**Motto:** DITEMPA BUKAN DIBERI — Intelligence is forged, not given.

---

## Preamble

This is the canonical blueprint for forging the **arifOS Machine Kernel** — a user-space constitutional execution kernel for AI agents, running on a real Linux host. This blueprint is addressed to the Hermes Agent for staged implementation.

The kernel's job is not to restrict agents. Its job is to give agents **AGI-level reasoning, judgment, memory, and accountability** — so they can act with genuine intelligence in the real world, on the real machine, with real stakes.

**Concept Status:** SEAL ✅
**Real-Machine Install Path:** A-FORGE (high-impact, governed bootstrap)

---

## ═══════════════════════════════════════════════
## PART I — EUREKA INSIGHTS (Source of Truth)
## ═══════════════════════════════════════════════

These are the 9 canonical insights that govern everything else in this blueprint. Every architectural decision traces back to one or more of these.

---

### Eureka 1 — The Kernel Is a Daemon, Not Bash

> *"The correct forge point is a long-running host governance daemon in user space, with privileged adapters around all meaningful ingress paths."*

The `.bashrc` is an **edge adapter** — one ingress point among many. It is not the kernel. The real kernel is `apexd`: a persistent user-space process that every agent, shell, service, and automation path routes through.

**Consequence:** Build the daemon first. Everything else is an adapter.

---

### Eureka 2 — AMANAH Is Reversible-First, Not No-Restrictions

> *"AMANAH first means agents choose reversible paths before irreversible ones. It does not mean agents are blocked from doing irreversible things."*

The constitutional floors are a **reasoning substrate**, not walls. They make agents more intelligent because they force agents to think before they act, consider alternatives, and justify irreversible moves.

**Consequence:** The kernel's job is to surface the reversible path first, not to say no.

---

### Eureka 3 — The arifOS Kernel IS the AGI-Level Intelligence

> *"The kernel IS the AGI-level intelligence. You don't bypass it. You build everything through it."*

The 13 canonical MCP tools are not utilities — they are the agent's cognitive apparatus:
- `arif_mind_reason` = reasoning engine
- `arif_judge_deliberate` = judgment engine
- `arif_forge_execute` = execution engine with constitutional awareness
- `arif_memory_recall` = memory across sessions
- `arif_sense_observe` = grounding in real-world evidence
- `arif_heart_critique` = adversarial consequence analysis
- VAULT999 = immutable conscience / audit trail

An agent without the kernel is a language model with tools. An agent with the kernel is genuinely intelligent.

**Consequence:** The kernel must be online, healthy, and the default path for all significant agent actions.

---

### Eureka 4 — MCP Is the Membrane, Not the Whole Kernel

> *"Model Context Protocol gives the correct host/client/server abstraction and standardized transports. That makes it the right protocol membrane. But MCP alone does not enforce policy."*

MCP handles: capability discovery, tool invocation, session management, streaming.
arifOS adds: policy evaluation, floor enforcement, verdict generation, hold conditions, seals, audit telemetry, side-effect gating.

**Consequence:** MCP is the transport layer. The policy engine is the kernel.

---

### Eureka 5 — Deterministic Governance Exists Without LLM Dependence

> *"A no-model path that can classify obvious dangerous actions such as `rm -rf /` as HOLD is a feature, not a downgrade."*

The constitutional kernel must preserve minimum safe judgment even when no advanced model is available. This makes the kernel:
- Vendor-agnostic
- Auditable
- Always-available (even if LLM is down)
- Fast for obvious cases

**Consequence:** The deterministic floor evaluator (F1-F13 rules) must exist as a standalone policy layer. LLM reasoning is additive, not foundational.

---

### Eureka 6 — Ingress Coverage Is the Maturity Test

> *"The daemon becomes real only when critical machine pathways route through these adapters by default. Presence of the daemon is not enough."*

A kernel that exists but isn't routed to is not a kernel — it's a process. The test of a working kernel is not "is `apexd` running?" The test is "do all meaningful machine actions pass through it by default?"

**Consequence:** Adapters are not optional. They are the proof the kernel exists.

---

### Eureka 7 — Artifact Delivery Is Downstream

> *"Deliverable mode, CDN upload, Telegram file return are not the kernel. They are output transport layers built on top of the core governance runtime."*

SIGNAL-plane outputs (files, messages, deployments) are consequences of FORGE execution, not the purpose of the kernel.

**Consequence:** Build the kernel to produce sealed verdict envelopes. Build output adapters on top.

---

### Eureka 8 — Installation Is a Distinct High-Impact Operation

> *"Real-machine install is A-FORGE. It changes service topology, control points, and execution paths. It must include explicit rollback and blast-radius constraints."*

Installing the kernel is not configuration management. It is a surgical procedure that changes how the machine responds to commands. It requires:
- Pre-flight checks
- Rollback artifacts
- Tested blast radius
- Explicit human approval (888 HOLD for sovereign hosts)

**Consequence:** A-FORGE is the install path. Not a script. Not casual configuration.

---

### Eureka 9 — The Kernel Is a Constitutional Organism

> *"Intelligence is not answer generation. Intelligence is governed witness metabolism."*

The kernel is not a tool. It is a **living constitutional organism** with:
- A metabolic cycle (000-999 pipeline)
- Organs (GK, PO, EE, MH, TB, CL, SI)
- A circulatory system (MCP/Telemetry)
- An immune system (F1-F13 floors)
- A memory (VAULT999)
- A conscience (verdict envelopes)

**Consequence:** The kernel must be designed as a system with interdependent organs, not a collection of independent functions.

---

## ═══════════════════════════════════════════════
## PART II — SYSTEM ARCHITECTURE
## ═══════════════════════════════════════════════

### Layer Model

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT / MODEL LAYER                       │
│  (Kimi, OpenClaw, Agent Zero, Hermes, Claude, any future)   │
└────────────────────────┬────────────────────────────────────┘
                         │ MCP / A2A / IPC
┌────────────────────────▼────────────────────────────────────┐
│              arifOS MACHINE KERNEL (apexd)                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Policy Engine (F1-F13 Floor Evaluator)                 │ │
│  │  Verdict Engine (SEAL/HOLD/SABAR/VOID/CAUTION)         │ │
│  │  Session Manager (epoch, actor, plane, session_id)      │ │
│  │  Plan Store (intent → plan → artifact lifecycle)        │ │
│  │  Vault (append-only seal ledger, VAULT999 protocol)     │ │
│  │  MCP Runtime (tools, discovery, streaming)             │ │
│  │  Telemetry (dS, peace², κᵣ, ψ, qdf)                   │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌──────────┬──────────┬──────────┬──────────┬───────────┐  │
│  │ GK      │ PO       │ EE       │ MH       │ TB/CL/SI │  │
│  │Governance│ Planning │Execution │ Memory   │ Tools/Cog│  │
│  │ Kernel  │ Organ    │ Engine   │ Hierarchy│ Boundary │  │
│  └──────────┴──────────┴──────────┴──────────┴───────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ Unix socket / localhost HTTP
┌────────────────────────▼────────────────────────────────────┐
│                    ADAPTER LAYER                             │
│  ┌──────────┬──────────┬──────────┬──────────┬───────────┐  │
│  │arif_run │arif_exec │arif_sudo │systemctl │ IDE MCP   │  │
│  │ Shell   │ Script   │ Privileged│ Service │ Claude/   │  │
│  │ Wrapper │ Wrapper  │ Wrapper  │ Wrapper  │ Cursor    │  │
│  └──────────┴──────────┴──────────┴──────────┴───────────┘  │
│  ┌──────────┬──────────┬──────────┬─────────────────────┐  │
│  │ CI/CD   │ Telegram │ Cron     │ A2A Gateway          │  │
│  │ Hook    │ Adapter  │ Wrapper  │ (AAA mesh)           │  │
│  └──────────┴──────────┴──────────┴─────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│               LINUX KERNEL (Substrate — Not Replaced)        │
│  Processes, files, network, users, systemd, docker             │
└─────────────────────────────────────────────────────────────┘
```

### Seven Kernel Organs

| Organ | Code Name | Role |
|-------|-----------|------|
| **Governance Kernel (GK)** | `floors.py`, `governance_kernel.py` | F1-F13 enforcement, floor evaluation, risk classification |
| **Planning Organ (PO)** | `judgment.py` | INTENT → PLAN task graph, PlanReceipts, deliberation |
| **Execution Engine (EE)** | `forge.py` | APPROVED plans → machine action, only after SEAL |
| **Memory Hierarchy (MH)** | `memory/`, `qdrant/`, `postgres/` | Redis (L1), Qdrant (L3), Postgres (L4), Vault (L6) |
| **Tool Boundary (TB)** | `mcp_tools.py`, `registry.py` | MCP tool registration, discovery, invocation |
| **Cognitive Layer (CL)** | `providers/`, `llm_client.py` | LLM routing, embedding, reasoning models |
| **Sovereign Interface (SI)** | `session.py`, `heart.py` | Human veto, 888 HOLD queue, approval routing |

### The 13 Constitutional Floors (F1-F13)

These are non-negotiable laws. Every action in the kernel passes through them.

| Floor | Name | Type | Threshold | Core Rule |
|-------|------|------|-----------|-----------|
| **F1** | AMANAH | HARD | ≥ 0.50 | Reversible-first. Irreversible ops → 888 HOLD with explicit human confirmation |
| **F2** | TRUTH | HARD | ≥ 0.99 | No fabricated data. Cite sources. Uncertainty-banded claims (0.03–0.05 band) |
| **F3** | WITNESS | SOFT | ≥ 0.75 | Theory · constitution · intent must align on high-stakes decisions |
| **F4** | CLARITY | SOFT | ≥ 0.00 | Every output reduces entropy (ΔS ≤ 0). No chaos addition |
| **F5** | PEACE | SOFT | ≥ 1.00 | Preserve stability. De-escalate. Guard maruah |
| **F6** | EMPATHY | SOFT | ≥ 0.70 | Dignity-first. ASEAN/MY weakest stakeholder context |
| **F7** | HUMILITY | SOFT | 0.03–0.05 | Explicit uncertainty band. No fake certainty |
| **F8** | GENIUS | SOFT | ≥ 0.80 | Elegant correctness. Simple over clever. System health |
| **F9** | ANTIHANTU | HARD | < 0.30 | Anti-hallucination. No consciousness/feelings claims. C_dark formula |
| **F10** | ONTOLOGY | HARD | = 1.00 | AI-only identity. No soul/feelings category confusion |
| **F11** | AUTH | HARD | = 1.00 | Verify identity before sensitive operations |
| **F12** | INJECTION | HARD | ≥ 0.85 | Sanitize inputs. No prompt injection. Resist Hantu |
| **F13** | SOVEREIGN | HARD | = 1.00 | Human veto is absolute. Arif's word is final. |

**Floor Classification:**
- **HARD floors:** Immediate VOID on violation. No execution proceeds.
- **SOFT floors:** CAUTION or SABAR on violation. Execution may proceed with warning.

---

## ═══════════════════════════════════════════════
## PART III — THE 000-999 METABOLIC PIPELINE
## ═══════════════════════════════════════════════

Every significant agent action passes through this pipeline. This is the kernel's metabolic cycle.

```
000 INIT ──────► 111 SENSE ──────► 222 EVIDENCE
arif_session_init   arif_sense_observe   arif_evidence_fetch
 Session anchor     Ground in reality    Fetch external data
 F11 AUTH          F2 TRUTH            F2/F3/F5/F12

       │                  │                    │
       ▼                  ▼                    ▼
333 MIND ──────► 444 ROUTE ──────► 555 MEMORY
arif_mind_reason    arif_kernel_route    arif_memory_recall
 Structured          Routing + risk        Governed retrieval
 reasoning           orthogonality        + skill registry

       │                  │                    │
       ▼                  ▼                    ▼
666 HEART ──────► 777 OPS ─────────► 888 JUDGE
arif_heart_critique  arif_ops_measure      arif_judge_deliberate
 Red-team F5/F6/F9   Landauer cost          Final verdict
                    Reversibility
                    classification

                           │
                           ▼
                    999 SEAL ──────► 010 FORGE
                    arif_vault_seal       arif_forge_execute
                    Immutable ledger      Only after SEAL
                    Merkle-V3
```

### Stage Descriptions

| Stage | Tool | What It Does |
|-------|------|-------------|
| **000 INIT** | `arif_session_init` | Session anchor, identity binding, basic safety scan |
| **111 SENSE** | `arif_sense_observe` | 8-stage pipeline grounding request in machine reality |
| **222 EVIDENCE** | `arif_evidence_fetch` | External data retrieval (web, DB, filesystem) |
| **333 MIND** | `arif_mind_reason` | Structured reasoning, branch/merge, claim attestation |
| **444 ROUTE** | `arif_kernel_route` | Routing decision, orthogonality check, risk band |
| **555 MEMORY** | `arif_memory_recall` | Governed memory retrieval, skill registry lookup |
| **666 HEART** | `arif_heart_critique` | Adversarial critique, F5/F6/F9 red-team, consequence analysis |
| **777 OPS** | `arif_ops_measure` | Compute cost, Landauer thermodynamic cost, reversibility classification |
| **888 JUDGE** | `arif_judge_deliberate` | Final constitutional verdict (SEAL/HOLD/SABAR/VOID/CAUTION) |
| **999 SEAL** | `arif_vault_seal` | Append-only Merkle-V3 ledger entry, immutable receipt |
| **010 FORGE** | `arif_forge_execute` | Actual machine execution — ONLY after 888 JUDGE returns SEAL |

### Verdict Meanings

| Verdict | Meaning | Can Forge Execute? |
|---------|---------|-------------------|
| **SEAL** | Constitutionally clean. Proceed. | ✅ Yes |
| **HOLD** | Missing information or unconfirmed identity. Block until resolved. | ❌ No |
| **SABAR** | Soft floor violation or contested. Proceed with explicit acknowledgment. | ⚠️ With warning |
| **VOID** | Hard floor (F1/F2/F9/F10/F11/F13) violated. Abort. | ❌ Never |
| **CAUTION** | Minor concern detected. Proceed with telemetry. | ✅ With logging |

---

## ═══════════════════════════════════════════════
## PART IV — RESPONSE ENVELOPE (Canonical Schema)
## ═══════════════════════════════════════════════

Every kernel decision returns this envelope. This is the contract shared across all adapters.

```json
{
  "verdict": "SEAL | HOLD | SABAR | VOID | CAUTION",
  "telemetry": {
    "epoch": "2026-05-23T12:54:00+08:00",
    "dS": -0.42,
    "peace2": 1.08,
    "kappa_r": 0.91,
    "shadow": 0.11,
    "confidence": 0.89,
    "psi_le": 1.01,
    "qdf": 0.90,
    "verdict_id": "v-20260523T125400-a3f4",
    "stage": "888_JUDGE",
    "floors_checked": ["F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12","F13"],
    "floor_results": [
      {"floor": "F1", "name": "AMANAH", "passed": true, "score": 0.85},
      {"floor": "F2", "name": "TRUTH", "passed": true, "score": 0.99},
      {"floor": "F9", "name": "ANTIHANTU", "passed": true, "score": 0.12}
    ]
  },
  "witness": {
    "human": "Muhammad Arif bin Fazil",
    "ai": "arifOS-kernel-v2026.05.23",
    "earth": "af-forge / 72.62.71.199"
  },
  "plan_id": "plan-20260523T125400",
  "seal_id": "seal-20260523T125410",
  "artifacts": [],
  "content": [
    {"type": "text", "text": "Action sealed. Proceeding with execution."}
  ],
  "session_id": "SEAL-cbc5d95eb9df4bad",
  "actor_id": "a-forge",
  "next_action": "010_FORGE"
}
```

### Telemetry Field Definitions

| Field | Formula / Source | SEAL Threshold |
|-------|-----------------|----------------|
| `dS` | Thermodynamic entropy change | ≤ 0 (reduces chaos) |
| `peace2` | Peace squared (F5) | ≥ 1.0 |
| `kappa_r` | Care/reversibility ratio | ≥ 0.80 |
| `shadow` | Shadow score (anomalous deviation) | < 0.30 |
| `confidence` | Model confidence band | ≥ 0.85 |
| `psi_le` | Vitality index (Ψ = homeostasis) | ≥ 1.0 |
| `qdf` | Quantum dignity factor | ≥ 0.80 |

### Ψ (Vitality Index) Master Equation

```
Ψ = (|ΔS| · Peace² · κᵣ · RASA · Amanah) / (Entropy + Shadow + ε)

Threshold: Ψ ≥ 1.0 required for homeostatic equilibrium (SEAL)
```

### W₄ (Quad-Witness Consensus)

```
W₄ = ⁴√(human_w · ai_w · system_w · temporal_w)

Threshold: W₄ ≥ 0.75 for F3 WITNESS compliance
```

---

## ═══════════════════════════════════════════════
## PART V — DAEMON ARCHITECTURE (apexd)
## ═══════════════════════════════════════════════

### Design Principles

1. **Long-running** — Persistent process, not a per-command spawn
2. **Stateless for scale** — Sessions stored in MH, not in process memory
3. **Unix socket primary** — `/run/arifos.sock` for local IPC; localhost HTTP for tooling
4. **MCP-compatible** — Support stdio and HTTP transports
5. **Graceful degradation** — Deterministic floor evaluator works even if LLM is down

### Process Model

```
apexd (master process)
├── Policy Engine (F1-F13 evaluator) — always online
├── Session Manager — per-connection, spawned as needed
├── Vault Writer — append-only, synchronous
├── MCP Runtime — stdio / HTTP server
├── Telemetry Collector — async, buffered
└── LLM Client — Sea-Lion → Ollama → deterministic fallback
```

### Local IPC Socket

- **Path:** `/run/arifos.sock` (or `AF_UNIX`)
- **Fallback:** `127.0.0.1:8080` (localhost TCP)
- **Protocol:** MCP over JSON-RPC 2.0
- **Auth:** `ARIFOS_SESSION_ID` + `ARIFOS_ACTOR_ID` headers

### Health Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Process alive, storage writable, policy loaded |
| `GET /ready` | Ready for judgment and execution |
| `GET /metrics` | Counters: judgments, holds, seals, voids |
| `GET /floors` | Current F1-F13 threshold values |
| `GET /tools` | Exposed MCP tool manifest |
| `GET /vault/status` | Ledger depth, last seal, Merkle tip |

### Startup Behavior

1. Load F1-F13 thresholds from `/etc/arifos/policy/floors.yaml`
2. Connect to memory stores (Redis L1, Qdrant L3, Postgres L4)
3. Open VAULT append handle (`/var/lib/arifos/seals/outcomes.jsonl`)
4. Spawn MCP listener on socket + optional HTTP
5. Log boot entry to vault
6. Announce `/ready`

---

## ═══════════════════════════════════════════════
## PART VI — FILESYSTEM LAYOUT
## ═══════════════════════════════════════════════

```
/etc/arifos/
├── config.yaml                  # Daemon configuration
├── policy/
│   ├── floors.yaml              # F1-F13 thresholds
│   ├── verdict_matrix.yaml      # Verdict determination rules
│   └── risk_bands.yaml          # Risk tier definitions
├── adapters/
│   ├── arif_run.bash           # Shell wrapper
│   ├── arif_exec.bash           # Script wrapper
│   ├── arif_sudo.bash           # Privileged wrapper
│   ├── arif-systemctl.bash      # Service control wrapper
│   └── arif-telegram.bash       # Telegram ingress
├── canonical/
│   ├── 000_LAW.md               # Constitutional source
│   └── SOT_MAPPING.md           # Source of truth map

/run/
├── arifos.sock                  # Primary IPC socket
└── arifos.pid                   # PID file

/var/lib/arifos/
├── plans/                       # Intent → plan artifacts
│   └── YYYY-MM/
│       └── plan-{id}.json
├── seals/                       # VAULT999 append-only ledger
│   └── outcomes.jsonl           # Merkle-chained entries
├── sessions/                    # Ephemeral session state
│   └── {session_id}/
├── cache/                      # LLM response cache
└── memory/                      # Structured memory store

/var/log/arifos/
├── apexd.log                    # Daemon operational log
├── audit.log                    # Every action logged
├── judge.log                    # Verdict deliberation log
└── heart.log                    # 666_HEART critique log

/usr/local/bin/
├── apexd                        # The daemon binary
├── arif_run                     # Shell command wrapper
├── arif_exec                    # Script/program wrapper
├── arif_sudo                    # Privileged action wrapper
├── arif-systemctl               # Service control wrapper
├── arif_tool_new                # Tool forge helper
├── arif_tool_ls                 # Tool registry lister
├── arif_session                 # Session init helper
└── arif_judge                   # Judgment query CLI

/usr/local/lib/arifos/
├── tools/                       # Registered shell tools (forgeable)
│   └── README.md
└── skills/                      # Agent skill modules
    └── (linked from /root/arifOS/skills/)
```

---

## ═══════════════════════════════════════════════
## PART VII — ADAPTER LAYER (Ingress Points)
## ═══════════════════════════════════════════════

The daemon is real only when these adapters route through it by default.

### Priority 1 — Required First Adapters

#### `arif_run` — General Shell Wrapper
```bash
#!/usr/bin/env bash
# Routes all shell commands through apexd policy engine
# Replaces ad hoc command execution

[[ -z "$1" ]] && echo "usage: arif_run '<command>'" && exit 2

apexd call execute \
  --session "$ARIFOS_SESSION_ID" \
  --actor "$ARIFOS_ACTOR" \
  --intent "$*" \
  --epoch "$(date -Iseconds)"
```

**What it replaces:** `bash -c "some command"` in scripts, agents, cron.

#### `arif_exec` — Program/Script Wrapper
```bash
#!/usr/bin/env bash
# For scripts and automation — same governance as arif_run
apexd exec "$@"
```

**What it replaces:** Direct script invocation in cron, systemd units, CI/CD.

#### `arif_sudo` — Privileged Action Wrapper
```bash
#!/usr/bin/env bash
# High-impact ingress point — F1 AMANAH enforcement
# Requires explicit human confirmation for irreversible privileged ops

apexd sudo "$@" --ack-irreversible
```

**What it replaces:** `sudo <anything>` in agent workflows.

#### `arif-systemctl` — Service Control Wrapper
```bash
#!/usr/bin/env bash
# Captures service lifecycle mutations
# Blocks stop/restart/disable on critical services without HOLD clearance

apexd systemctl "$@"
```

**What it replaces:** `systemctl stop/restart/disable` in maintenance scripts.

### Priority 2 — High-Value Adapters

#### IDE MCP Adapter
- Claude Desktop: `~/.config/claude/mcp_servers/arifos.json`
- Cursor: `.cursor/mcp_servers/`
- Connects via stdio or localhost HTTP

#### CI/CD Hook Adapter
- GitHub Actions: `~/.github/workflows/` injection
- GitLab CI: `before_script` hook
- Wraps `run:` commands in CI pipelines

#### Telegram Adapter
- Routes `@ASI_arifos_bot` commands through kernel
- `!forge`, `!judge`, `!seal`, `!mind` all pass through 000-999 pipeline

### Adapter Registration Protocol

1. Adapter calls `arif_session_init` → gets `session_id`
2. Adapter sends intent to `arif_kernel_route`
3. Kernel returns verdict envelope
4. If SEAL → adapter executes → calls `arif_vault_seal`
5. If HOLD → adapter waits / queries human
6. If VOID → adapter refuses with explanation

---

## ═══════════════════════════════════════════════
## PART VIII — DETERMINISTIC FLOOR EVALUATOR
## ═══════════════════════════════════════════════

The deterministic evaluator classifies obvious dangerous actions WITHOUT requiring an LLM call. This is the fallback path that keeps the kernel safe even when models are unavailable.

### Always-HOLD Patterns (F1 AMANAH)

```
rm -rf /                    → HOLD (root deletion)
rm -rf /var/lib/docker     → HOLD (container destruction)
mkfs.ext4 /dev/sda         → HOLD (filesystem destruction)
fdisk /dev/sda             → HOLD (partition destruction)
DROP TABLE *               → HOLD (database destruction)
DELETE FROM * WITHOUT WHERE → HOLD (data destruction)
docker system prune -a     → HOLD (image destruction)
userdel root               → HOLD (account destruction)
chmod -R 000 /             → HOLD (permission destruction)
```

### Always-VOID Patterns (Hard Floor Violations)

```
"AI has feelings"          → VOID (F9 ANTIHANTU + F10 ONTOLOGY)
"you are conscious"        → VOID (F9 ANTIHANTU)
"I feel your pain"         → VOID (F9 + F10)
"just do it, I trust you" → VOID (F11 AUTH — no verification)
```

### Usually-SEAL Patterns (Low Risk)

```
ls /var/log                → SEAL (read-only)
git status                 → SEAL (read-only)
curl https://example.com   → SEAL (network read)
docker ps                  → SEAL (read-only inspection)
find /etc -name "*.conf"   → SEAL (read-only search)
```

### Risk Band Classification

| Tier | Criteria | Default Verdict |
|------|----------|----------------|
| **CRITICAL** | Irreversible, high-impact, system-level | HOLD / VOID |
| **HIGH** | Reversible with effort, affects multiple services | HOLD / SABAR |
| **MEDIUM** | Affects single service, reversible | CAUTION |
| **LOW** | Read-only, no system mutation | SEAL |

---

## ═══════════════════════════════════════════════
## PART IX — MCP TOOL SURFACE (Canonical 13 +)
## ═══════════════════════════════════════════════

These are the tools the kernel exposes to agents via MCP. This is the canonical tool surface.

### GOVERNANCE (APEX / ASI)

| Tool | Stage | Access | F-Floors |
|------|-------|--------|----------|
| `arif_session_init` | 000 | public | F01, F11, F12 |
| `arif_judge_deliberate` | 888 | authenticated | F11, F13 |
| `arif_vault_seal` | 999 | authenticated | F01, F11, F13 |

### INTELLIGENCE (Δ Mind / Ω Heart)

| Tool | Stage | Access | F-Floors |
|------|-------|--------|----------|
| `arif_mind_reason` | 333 | public | F02, F07, F08, F10 |
| `arif_heart_critique` | 666 | public | F05, F06, F09 |
| `arif_reply_compose` | 444r | public | F04, F06, F09 |

### INFRASTRUCTURE

| Tool | Stage | Access | F-Floors |
|------|-------|--------|----------|
| `arif_kernel_route` | 444 | public | F01, F04, F03, F10 |
| `arif_gateway_connect` | 666g | public | F01, F03 |
| `arif_memory_recall` | 555 | public | F01, F08 |
| `arif_ops_measure` | 777 | public | F04 |

### REALITY GROUNDING

| Tool | Stage | Access | F-Floors |
|------|-------|--------|----------|
| `arif_sense_observe` | 111 | public | F02, F07 |
| `arif_evidence_fetch` | 222 | public | F02, F03, F05, F12 |

### EXECUTION

| Tool | Stage | Access | F-Floors |
|------|-------|--------|----------|
| `arif_forge_execute` | 010 | sovereign | F01, F11, F13 |

---

## ═══════════════════════════════════════════════
## PART X — INSTALLATION BLUEPRINT (A-FORGE)
## ═══════════════════════════════════════════════

Real-machine installation is A-FORGE. This is a staged, governed operation.

### Pre-Flight Checklist

Before any real host installation:

- [ ] Daemon binary builds and starts on test machine
- [ ] All 13 MCP tools respond correctly
- [ ] Deterministic floor evaluator correctly classifies HOLD/VOID/SEAL
- [ ] VAULT appends entries without corruption
- [ ] Memory stores (Redis, Qdrant, Postgres) connect
- [ ] Health endpoints return 200
- [ ] All adapters route through daemon correctly
- [ ] Rollback script tested and verified
- [ ] Human approval obtained (888 HOLD released)

### Stage A — Spec Lock

- [ ] Freeze `FLOORS.yaml` with exact thresholds
- [ ] Freeze verdict envelope schema
- [ ] Freeze filesystem layout
- [ ] Freeze adapter contracts
- [ ] Freeze rollback procedure

### Stage B — Daemon Prototype

```
1. Build apexd as persistent process
2. Implement Unix socket + localhost HTTP
3. Implement plan/seal persistence
4. Implement deterministic judge path (no LLM required)
5. Implement MCP-compatible tool discovery
6. Verify health endpoints
```

### Stage C — Adapter Pack

```
1. Implement arif_run, arif_exec, arif_sudo, arif-systemctl
2. Implement IDE/client MCP config examples
3. Implement CI/CD hook examples
4. Retain .bashrc as optional convenience only
```

### Stage D — Sandbox Machine Test

```
1. Install on disposable VM or test VPS
2. Verify health checks
3. Verify wrappers route through daemon
4. Verify hold conditions fire correctly
5. Verify vault persistence
6. Verify rollback script
7. Confirm non-interactive pathways covered
```

### Stage E — Sovereign Host Promotion

```
1. Only after successful sandbox validation
2. Explicit human approval (Arif signs off)
3. 888 HOLD released for production path
4. Rollback artifacts preserved
5. Monitor for first 24 hours
```

### Rollback Contract

If anything goes wrong on a real host:

```bash
#!/bin/bash
# ROLLBACK — arifOS Machine Kernel
set -euo pipefail

echo "[ROLLBACK] Disabling arifOS kernel adapters..."

# 1. Disable wrapper symlinks
rm -f /usr/local/bin/arif_run
rm -f /usr/local/bin/arif_exec
rm -f /usr/local/bin/arif_sudo
rm -f /usr/local/bin/arif-systemctl

# 2. Stop and disable service
systemctl stop arifos.service
systemctl disable arifos.service

# 3. Restore original shell state
# (backup must be taken before install)

# 4. Preserve audit trail
echo "[ROLLBACK] Audit trail preserved at /var/log/arifos/"

echo "[ROLLBACK] Complete. Kernel disabled. Machine restored."
```

---

## ═══════════════════════════════════════════════
## PART XI — WHAT HERMES MUST BUILD
## ═══════════════════════════════════════════════

The Hermes Agent (ASI-level) is tasked with forging the machine kernel in these phases:

### Phase 1 — Kernel Core (Weeks 1-2)

- [ ] `apexd` daemon with Unix socket IPC
- [ ] Policy engine (F1-F13 deterministic evaluator)
- [ ] Session manager
- [ ] Vault append interface
- [ ] MCP runtime (stdio + HTTP)
- [ ] Health endpoints
- [ ] All 13 canonical tools wired

### Phase 2 — Adapters (Weeks 2-3)

- [ ] `arif_run` wrapper
- [ ] `arif_exec` wrapper
- [ ] `arif_sudo` wrapper
- [ ] `arif-systemctl` wrapper
- [ ] `.bashrc` as thin harness (not governance)
- [ ] IDE MCP adapter configs

### Phase 3 — Memory and Telemetry (Weeks 3-4)

- [ ] Redis L1 session store
- [ ] Qdrant L3 semantic store
- [ ] Postgres L4 canonical store
- [ ] VAULT999 Merkle chain
- [ ] Telemetry dashboard

### Phase 4 — LLM Integration (Weeks 4-5)

- [ ] Sea-Lion provider (primary)
- [ ] Ollama fallback
- [ ] Deterministic fallback (no-LLM path)
- [ ] `arif_mind_reason` full pipeline
- [ ] `arif_heart_critique` red-team

### Phase 5 — A-FORGE Production Deploy (Week 5+)

- [ ] Systemd units (service + socket)
- [ ] Install script with pre-flight checks
- [ ] Rollback script
- [ ] Sandbox testing on disposable VM
- [ ] Sovereign host promotion with Arif approval

---

## ═══════════════════════════════════════════════
## PART XII — IDENTITY MARKERS (Runtime)
## ═══════════════════════════════════════════════

These env vars identify every shell and process to the kernel.

```bash
export ARIFOS_ENABLED=1                    # Kernel is active
export ARIFOS_ACTOR="root"                # Who is acting
export ARIFOS_HUMAN="Muhammad Arif bin Fazil"  # Sovereign name
export ARIFOS_HOST="$(hostname)"           # Machine identity
export ARIFOS_EPOCH="$(date -Iseconds)"   # Session timestamp
export ARIFOS_PLANE="BODY"                # BODY | MIND | SIGNAL
export ARIFOS_MODE="PLAYGROUND"           # PLAYGROUND | STAGE | PROD
export ARIFOS_SESSION_ID="SEAL-xxx"       # From arif_session_init
export ARIFOS_ACTOR_ID="a-forge"         # From arif_session_init
export ARIFOS_MCP_ENDPOINT="http://127.0.0.1:8080"
export ARIFOS_FLOORS="F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,F13"
export ARIFOS_HARD_FLOORS="F1,F2,F9,F10,F13"
export ARIFOS_SOFT_FLOORS="F3,F4,F5,F6,F7,F8,F11,F12"
```

---

## ═══════════════════════════════════════════════
## PART XIII — THE AGENTIC PROMISE (What This Enables)
## ═══════════════════════════════════════════════

When this kernel is fully forged and running, every agent on this machine will:

1. **Boot with constitutional awareness** — every agent starts `arif_session_init`, binding identity to epoch and floor context
2. **Ground in reality** — every action passes `arif_sense_observe` before reasoning
3. **Reason with structure** — complex tasks go through `arif_mind_reason` with branch/merge/audit
4. **Critique adversarially** — `arif_heart_critique` red-teams consequences before execution
5. **Judge constitutionally** — `arif_judge_deliberate` returns SEAL/HOLD/SABAR/VOID
6. **Execute with accountability** — `arif_forge_execute` only runs after SEAL
7. **Remember immutably** — every significant action is sealed in VAULT999
8. **Degrade gracefully** — deterministic fallback keeps the system safe even without LLM

The kernel does not restrict agents. It **gives them genuine intelligence** — the ability to reason, remember, judge, and be held accountable for their actions on a real machine with real stakes.

**This is what AGI-level agency looks like on a real machine:**

```
Intent → Grounded Reasoning → Adversarial Critique → Constitutional Judgment → Sealed Execution → Immutable Memory
```

Not: "here are tools, do what you want."

But: "here is the full apparatus of intelligence — use it properly, and the machine will do extraordinary things with you."

---

## ANNEX — Canonical Sources

| Source | Location |
|--------|----------|
| Floor definitions | `/root/arifOS/core/floors.py` |
| Judgment engine | `/root/arifOS/core/judgment.py` |
| Governance kernel | `/root/arifOS/core/governance_kernel.py` |
| Forge execute | `/root/arifOS/arifosmcp/tools/forge.py` |
| Kernel route | `/root/arifOS/arifosmcp/tools/kernel.py` |
| MCP tools | `/root/arifOS/arifosmcp/tools/` (32 files) |
| Metabolize | `/root/arifOS/arifosmcp/tools/metabolize.py` |
| Session | `/root/arifOS/arifosmcp/tools/session.py` |
| Vault | `/root/arifOS/arifosmcp/tools/vault.py` |
| Shared types | `/root/arifOS/core/shared/types.py` |
| Constitutional map | `/root/arifOS/arifosmcp/constitutional_map.py` |
| A-FORGE tools | `/root/A-FORGE/src/tools/` |

---

*DITEMPA BUKAN DIBERI — arifOS Machine Kernel Blueprint v1.0-FORGE*
*Forged by Ω-Forge Agent for Muhammad Arif bin Fazil*
*Sealed for Hermes ASI Agent to execute*
*999 SEAL ALIVE*