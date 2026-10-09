# arifOS Substrate Doctrine — Constitutional Binding Sequence
# Ω-2026-08-30-22:20  ·  Ratified by Arif Fazil (F13) · Co-drafted with Hermes

> **"The biggest Eureka is: AAA, A-FORGE, OpenCode, Hermes, MCP, A2A and
> LiteLLM are not the system. They are organs. The substrate is the body.
> If the body is weak, every organ will eventually look broken."**
> — Arif, 2026-08-30 session

---

## Constitutional Status

This document is **constitutional**, bukan engineering reference. It declares
the binding sequence under which any higher-layer artifact (organ, agent,
capability, tool, skill) may be sealed.

**Rule:** No layer S(n+1) may be sealed unless S0..Sn are auditable as alive.

If a layer is not auditable, it does not exist as doctrine — only as theater.

---

## S0 — Machine Reality (S0)

The hardware substrate. Without this, every doctrine above is rhetoric.

### Compute
- CPU monitoring (load, steal%, OOM events)
- RAM monitoring (available MB, swap pressure)
- GPU monitoring (if allocated — currently zero unratified GPU)

### Disk
- SSD with `df -h` alerts at ≥75% (current state: 79% ⚠️)
- inode tracking (vector DBs silently exhaust inodes)
- Docker image GC policy
- Log rotation policy

### Network
- DNS health (most "provider broken" reports are DNS timeouts)
- TLS certificate expiry monitoring
- Reverse proxy (Caddy)
- Firewall (UFW — single-port exposure only)

**Audit gap as of 2026-08-30:** Compute OK, Disk WARNING (79%), Network OK,
Firewall OK (only tailscale + localhost exposed).

---

## S1 — Runtime Layer

Services live here.

**Current doctrine:** Docker Compose, not Kubernetes.

Kubernetes is justified only if:
- Multiple machines
- Automatic failover required
- Cluster scheduling needed
- Autoscaling needed
- Tens-hundreds of services

For arifOS today (1 VPS, ~10 services): Docker Compose + systemd + Caddy.

**Audit gap as of 2026-08-30:** OK — all services in docker compose, healthy.

---

## S2 — Service Governance

Every process must answer:
- Who owns me?
- Why do I exist?
- What capability do I provide?
- What port do I expose?
- What is my healthcheck?

No owner = KILL.

---

## S3 — Secret Layer

Critical. After 6 months, `.env` everywhere becomes archaeology.

Required:
- API key registry (`/root/.secrets/INDEX.md` + `KEY_REGISTRY.md`)
- Key inventory: provider, owner, quota, last_used, expiry
- Rotation policy
- Owner accountability

**Audit gap as of 2026-08-30:** ✅ Present. INDEX.md, KEY_ARCHITECTURE.md,
KEY_HANDLING_GUIDE.md, KEY_REGISTRY.md, KUNCI_ROOT_MAP.md all in place.

---

## S4 — Persistence Layer

Separation of concerns. Each store has one job.

| Store | Job | Current |
|---|---|---|
| Postgres | reality: jobs, agents, tasks, state, metadata | ✅ UP (admin role needs re-grant — minor) |
| Redis | short-term: queues, cache, sessions, locks | ✅ UP (PONG) |
| Qdrant | semantic recall: embeddings, retrieval, memory | ✅ UP |
| FalkorDB | graph: relationship data | ✅ UP |
| MinIO / FS | artifacts: audio, video, images, receipts | partial (FS only) |

---

## S5 — Observability Layer

**The layer where most AI stacks die.** Without this, you are guessing.

Must track:
- Infra: CPU, RAM, Disk, Network
- AI: tokens, costs, latency, retries, errors
- Federation: health of each organ, drift between layers
- Cost receipt: every request must produce one

**Audit gap as of 2026-08-30:** ⚠️ PARTIAL
- FED :4000 health = 200 ✅
- FRAME :18085 health = **404 ❌** (observability organ down/incorrect route)
- WELL :18083 health = **404 ❌** (same)
- No drift detector between config.yaml ↔ reality (this is what caused the 413)

**Doctrine gap:** No scheduled substrate audit. **Fix pending:**
`/root/AAA/scripts/substrate_audit.sh` (sealed tonight).

---

## S6 — Identity Layer

Identity survives model replacement.

Required:
- Agent ID (333, 555, 888, A-FORGE, Hermes, OpenCode, etc.)
- Authority scope
- Role
- Capability surface

**Audit gap as of 2026-08-30:** ✅ `persons.yaml` registry present.

---

## S7 — Capability Registry Layer

**FED's heart.** Models come and go. Capabilities don't.

Required capabilities (non-exhaustive):
- think
- reason
- code
- search
- memory
- vision
- audio
- execution
- planning
- critique

**Audit gap as of 2026-08-30:** ⚠️ ORPHAN
- `/root/.config/capability_registry.json` v1.2.0 EXISTS
- Created 2026-08-25 (5 days ago)
- **NOT consulted by FED :4000** — verified live, FED only knows MiniMax
- Decision tonight: keep registry, wire it tomorrow morning

Doctrine says: **Capability → Provider → Model.** Reality says:
Provider-nama hardcoded. This is the regression tonight's 413 exposed.

---

## S8 — Memory Fabric

**Critical distinction.** Context Window ≠ Memory.

| Type | Lifespan | Storage |
|---|---|---|
| Context | per-turn, temporary | LLM window |
| Episode | session-scoped | session DB |
| Skill | persistent, curated | skills/ + memory |
| Scar | persistent, constitutional | active_scars + doctrine |
| Receipt | permanent, append-only | VAULT999 |
| Knowledge | persistent, semantic | Qdrant |

---

## S9 — Governance Layer

Before AI. After memory.

Required:
- read / write / execute / approve authority per agent
- Separation: 333 propose · 555 verify · 888 judge · A-FORGE execute

Without governance, 100 agents = 100 chaos generators.

---

## S10 — Tool Layer (MCP)

MCP is a **Tool Bus**, bukan intelligence.

Provides:
- filesystem, github, docker, browser, database, terminal
- to the federation
- as tools, not as agents

---

## S11 — Agent Layer (A2A)

A2A is **Agent Communication**, not tool access.

- AAA ↔ Hermes ↔ OpenCode ↔ A-FORGE
- share intent, not tools

(MCP = tools. A2A = communication. Don't conflate.)

---

## S12 — Cognitive Bus (LiteLLM)

Only NOW does LiteLLM enter. As the **Cognitive Bus** — provider abstraction,
routing, fallback, health, cost management.

**Audit gap as of 2026-08-30:** ❌ WIRED-BUT-ISOLATED
- LiteLLM at :4000 = 8 models, all MiniMax
- Config claims 22 rungs with GLM-5.3, Claude Sonnet, DeepSeek V4 — all claims
  unverifiable from live API
- Capability registry not consulted

**Doctrine gap:** FED is the cognitive bus by name only. Wire-up queued
for tomorrow morning.

---

## S13 — AAA

After S0-S12, AAA becomes possible.

Before substrate: AAA = hallucinating manager.
After substrate: AAA = governing institution.

---

## S14 — A-FORGE

Execution layer. Now safe because:
- Identity exists (S6)
- Authority exists (S9)
- Memory exists (S8)
- Tools exist (S10)
- Governance exists (S9)

---

## S15 — Models

**Cognitive suppliers to the federation. Nothing more.**

Qwen, GLM, Claude, GPT, Gemini, DeepSeek, Kimi, Groq gpt-oss-120b — these are
*implementation details* below the capability registry.

Model swap = doctrine unaffected.

Model removal = registry entry update, nothing else.

---

## Hard Gate Checklist (Binding)

Before sealing any layer S(n+1), the following MUST be auditable:

```
[ ] S0  Linux hardened (compute/disk/network/firewall)
[ ] S1  Docker standardized (Compose, not ad-hoc)
[ ] S2  TLS/reverse proxy (Caddy)
[ ] S3  Secret registry (keys inventoried + rotated)
[ ] S4  Service registry (every process owned + scoped)
[ ] S5  Postgres (reality DB live)
[ ] S6  Redis (short-term memory live)
[ ] S7  Qdrant (semantic memory live)
[ ] S8  Artifact storage (MinIO/FS for binary)
[ ] S9  Health monitoring (every organ reachable + alerting)
[ ] S10 Cost monitoring (per-request receipt)
[ ] S11 Identity registry (every agent has ID + authority)
[ ] S12 Capability registry (capabilities named, models mapped)
[ ] S13 Memory fabric (episodic + procedural + scar + receipt)
[ ] S14 Governance controls (read/write/exec/approve split)
[ ] S15 Receipt system (append-only audit ledger)
[ ] S16 MCP tool bus (filesystem/git/db/docker/browser exposed)
[ ] S17 A2A communication plane (agents share intent)
[ ] S18 LiteLLM cognitive bus (provider-abstracted, capability-aware routing)
[ ] S19 Drift detector (config ↔ reality, scheduled)
```

Only after `[ ] → [x]` for all 19 items may AAA/A-FORGE/Models be sealed
as production.

---

## Closing

The biggest Eureka is:

> AAA, A-FORGE, OpenCode, Hermes, MCP, A2A and LiteLLM are not the system.
> They are organs. The substrate is the body. If the body is weak, every
> organ will eventually look broken.

The next architectural frontier for FED is not another model or another agent.
It is making the substrate **auditable, observable, governable, and
capability-centric** so every future organ can plug in without creating
another round of entropy.

— Sealed Ω-2026-08-30-22:20