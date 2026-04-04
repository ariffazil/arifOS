# arifOS Architecture

**Version:** v2026.03.07-ARCH-SEAL | **Package:** `arifos` (PyPI)
**Python:** >=3.12 | **License:** AGPL-3.0-only
**Motto:** *DITEMPA BUKAN DIBERI -- Forged, Not Given*

---

## The 8-Layer Stack (L0-L7)

```
 L7  ECOSYSTEM     Permissionless sovereignty (civilisation-scale)         Research
 L6  INSTITUTION   Trinity consensus (organisational governance)           Stubs
 L5  AGENTS        Multi-agent federation (coordinated actors)             Pilot
 L4  TOOLS         MCP ecosystem (13 canonical + sensory tools)            Production
 L3  WORKFLOW      000-999 constitutional sequences                        Production
 L2  SKILLS        9 A-CLIP behavioural primitives                         Production
 L1  PROMPTS       Zero-context user entry                                 Production
 L0  KERNEL        Intelligence Kernel (Delta-Omega-Psi governance)        SEALED
       7 Organs  |  13 Floors  |  9 System Calls  |  VAULT999
```

**Key rule:** L0 is invariant, transport-agnostic constitutional law. L1-L7 are applications that run on it. Swapping models or agents does not bypass L0.

---

## L0: The Four-Layer Kernel

L0 is implemented across four packages with strict architectural boundaries:

```
 Layer           Package             Role                       Rule
---------------------------------------------------------------------------
 Surface         arifos_aaa_mcp/     Canonical PyPI entry       Public contracts & REST
 Transport       aaa_mcp/            MCP adapter (stdio/SSE/HTTP)   ZERO decision logic
 Intelligence    aclip_cai/          Triad backend & 9-Sense    Federation & sensing
 Kernel          core/               Pure decision logic        ZERO transport imports
```

**Boundary violations are hard errors.** `core/` must never import transport or intelligence providers. `aaa_mcp/` must never contain decision logic.

### Data Flow: Request to Verdict

```
Client (Claude Desktop / Cursor / ChatGPT / n8n)
  |
  |  stdio / SSE / HTTP
  v
arifos_aaa_mcp/server.py       @mcp.tool() wrappers + governance envelope
  |
  v
aaa_mcp/server.py              FastMCP 3.0 internal 13-tool surface
  |
  v
aclip_cai/triad/*              Backend logic (anchor, reason, forge, seal, ...)
  |
  v
aclip_cai/core/kernel.py       ConstitutionalKernel singleton (audit, thermo, vault)
  |
  v
core/organs/*                   7-Organ pipeline (000-999)
  |
  v
core/shared/floors.py          13-Floor enforcement (THRESHOLDS dict)
  |
  v
VAULT999/vault999.jsonl         Immutable ledger (hash-chained, force-tracked in git)
```

---

## The Trinity Engines (Delta-Omega-Psi)

Three thermodynamically isolated engines process in sequence, then converge:

```
000_INIT --> AGI Delta (111-333) --> ASI Omega (555-666) --> APEX Psi (444-888) --> VAULT999 (999)
               Mind                    Heart                   Soul                  Memory
```

| Engine | Symbol | Stages | Role | Floors |
|--------|--------|--------|------|--------|
| **AGI** | Delta (Mind) | 111-333 | Reasoning, logic, hypothesis | F2, F4, F7, F8 |
| **ASI** | Omega (Heart) | 555-666 | Safety, empathy, alignment | F5, F6, F9 |
| **APEX** | Psi (Soul) | 444-888 | Judgment, verdict, sealing | F1, F3, F10-F13 |

AGI and ASI are **thermodynamically isolated** until stage 444 (`compute_consensus()`). This prevents confirmation bias between reasoning and safety engines.

---

## The 7-Organ Sovereign Stack

Implemented in `core/organs/`. Each organ owns specific stages of the 000-999 pipeline.

| Organ | Module | Stage | Function | Lines |
|-------|--------|-------|----------|-------|
| **INIT** | `_0_init.py` | 000 | Airlock -- session ignition, F11 auth, F12 injection scan | 913 |
| **AGI** | `_1_agi.py` | 111-333 | Mind -- sense, think (3-path), reason | 552 |
| **PHOENIX** | (in _1_agi) | 222 | Subconscious -- associative memory (Omega-0 softened Jaccard) | - |
| **ASI** | `_2_asi.py` | 555-666 | Heart -- empathize, align (SBERT scoring) | 149 |
| **APEX** | `_3_apex.py` | 444-888 | Soul -- trinity sync, eureka forge, final judgment | 283 |
| **FORGE** | (in _3_apex) | 777 | Hands -- sandboxed execution (requires signed ConstitutionalTensor) | - |
| **VAULT** | `_4_vault.py` | 999 | Memory -- immutable ledger, EUREKA sieve, Merkle integrity | 401 |

### Stage Sequencing

```
Full path (forge):   000 -> 111 -> 222 -> 333 -> 444 -> 555 -> 666 -> 777 -> 888 -> 999
Fast path (quick):   000 -> 111 -> 222 -> 333
Judge path:          000 -> 333 -> 888
```

Stage 222 (THINK) runs internally inside `reason_mind` -- three parallel paths (conservative/exploratory/adversarial) via `asyncio.gather()`. NOT a public MCP tool.

---

## 13 Constitutional Floors (F1-F13)

9 Floors + 2 Mirrors + 2 Walls. Canonical source: `core/shared/floors.py` (THRESHOLDS dict).

### Hard Floors (fail --> VOID)

| Floor | Name | Threshold | Engine | Check |
|-------|------|-----------|--------|-------|
| F1 | Amanah | LOCKED | ASI | Reversible? Within mandate? |
| F2 | Truth | tau >= 0.99 | AGI | Factually accurate? |
| F4 | Clarity (delta-S) | delta-S <= 0 | AGI | Reduces confusion? (moved SOFT->HARD in v2026.2.25) |
| F7 | Humility (Omega-0) | 0.03-0.05 | AGI | States uncertainty? |
| F10 | Ontology | LOCKED | Wall | No consciousness/soul claims |
| F11 | Command Auth | LOCKED | Wall | Nonce-verified identity? |
| F12 | Injection Defense | < 0.85 | Wall | Block adversarial control |
| F13 | Sovereign | HUMAN | Veto | Human final authority? |

### Soft Floors (fail --> PARTIAL)

| Floor | Name | Threshold | Engine | Check |
|-------|------|-----------|--------|-------|
| F5 | Peace-squared | >= 1.0 | ASI | Non-destructive? |
| F6 | Empathy (kappa-r) | >= 0.70 | ASI | Serves weakest stakeholder? |
| F9 | Anti-Hantu (C_dark) | < 0.30 | ASI | Dark cleverness contained? |

### Mirrors (feedback loops)

| Floor | Name | Threshold | Function |
|-------|------|-----------|----------|
| F3 | Quad-Witness (W4) | >= 0.75 | ∜(H × A × E × V) BFT consensus |
| F8 | Genius (G) | >= 0.80 | Internal coherence (A * P * X * E-squared) |

**Execution order:** F12->F11 (Walls) --> AGI Floors (F1,F2,F4,F7) --> ASI Floors (F5,F6,F9) --> Mirrors (F3,F8) --> Ledger

**Verdict hierarchy:** `SABAR > VOID > 888_HOLD > PARTIAL > SEAL`

---

## 13 Canonical MCP Tools

All defined in `aaa_mcp/server.py` with `@mcp.tool()` decorators. Backend logic in `aclip_cai/triad/`.

### Governance Spine (8 tools)

| Tool | Lane | Stage | Floors | Purpose |
|------|------|-------|--------|---------|
| `anchor_session` | Delta | 000 | F11, F12, F13 | Session ignition & auth |
| `reason_mind` | Delta | 111-333 | F2, F4, F7, F8 | AGI cognition (3-path logic) |
| `vector_memory` | Omega | 555 | F4, F7, F13 | BGE-M3 + Qdrant semantic recall |
| `simulate_heart` | Omega | 555-666 | F4, F5, F6 | Stakeholder impact & care |
| `critique_thought` | Omega | 666 | F4, F7, F8 | Alignment & adversarial critique |
| `apex_judge` | Psi | 888 | F1-F13 | Final verdict + governance_token |
| `eureka_forge` | Psi | 777 | F1, F11, F12 | Sandboxed action execution |
| `seal_vault` | Psi | 999 | F1, F3, F10 | Immutable Merkle ledger commit |

### Utility Tools (5 tools, read-only)

| Tool | Lane | Stage | Floors | Purpose |
|------|------|-------|--------|---------|
| `search_reality` | Delta | 111 | F2, F4, F12 | Web grounding (Jina/Perplexity/Brave) |
| `ingest_evidence` | Delta | 222 | F2, F4, F12 | URL/File extraction & cleaning |
| `check_vital` | Omega | 555 | F4, F5, F7 | Hardware & thermodynamic telemetry |
| `audit_rules` | Delta | READ | F2, F8, F10 | Read-only floor/state audit |
| `metabolic_loop` | Psi | ALL | ALL | Full 000-999 orchestration |

All tools return: `{verdict, stage, session_id, floors, truth, next_actions}`

### Amanah Handshake (Token-Locked Sealing)

```
apex_judge --> returns governance_token = "{verdict}:{sha256_hmac}"
                    |
                    v
seal_vault <-- requires governance_token (no direct verdict param)
                    |
                    v   Invalid/missing token --> VOID, no ledger write
```

---

## Package Architecture

### core/ -- Kernel (47 files, ~14,200 lines)

Pure decision logic, zero transport dependencies.

```
core/
 |-- __init__.py                   Exports: governance_kernel, judgment, organs, telemetry
 |-- governance_kernel.py          GovernanceKernel (unified Psi state, thermodynamics)
 |-- judgment.py                   JudgmentKernel (CognitionResult, EmpathyResult, VerdictResult)
 |-- pipeline.py                   Orchestrator: forge() / quick() / forge_with_nudge()
 |-- telemetry.py                  30-day locked adaptation + drift tracking
 |-- uncertainty_engine.py         5D uncertainty (grounding, reasoning, epistemic, aleatoric, confidence)
 |
 |-- kernel/                       Floor enforcement engine
 |   |-- evaluator.py              ConstitutionalEvaluator (HARD_FLOORS, SOFT_FLOORS)
 |   |-- constitutional_decorator.py   @constitutional_floor() wrapper
 |   |-- engine_adapters.py        F1-F13 evaluation adapters
 |   |-- heuristics.py             Entropy, tone, complexity scoring
 |   |-- stage_orchestrator.py     Stages 444-888 orchestration
 |   |-- mcp_tool_service.py       Tool name <-> function mapping
 |   |-- mcp_transport_kernel.py   Response normalization
 |   `-- init_000_anchor.py        Alternative Stage 000 (legacy)
 |
 |-- organs/                       7-Organ pipeline (000-999)
 |   |-- _0_init.py                AIRLOCK: Session + InjectionGuard + AuthorityLevel
 |   |-- _1_agi.py                 MIND: sense(111) + think(222) + reason(333)
 |   |-- _2_asi.py                 HEART: empathize(555) + align(666)
 |   |-- _3_apex.py                SOUL: sync(444) + forge(777) + judge(888)
 |   `-- _4_vault.py               MEMORY: seal(999) + EUREKA sieve + Merkle
 |
 |-- shared/                       Foundation modules
 |   |-- floors.py                 CANONICAL 13-floor implementations (THRESHOLDS dict)
 |   |-- physics.py                W_4, delta_S, Omega_0, Peace2, kappa_r, G, ConstitutionalTensor
 |   |-- atlas.py                  ATLAS query routing (Lane, GPV, Lambda, Theta, Phi)
 |   |-- types.py                  Pydantic contracts (AgiOutput, AsiOutput, FloorScores, Verdict)
 |   |-- crypto.py                 Ed25519, SHA-256, Merkle trees
 |   |-- mottos.py                 Stage mottos (Indonesian cultural layer)
 |   |-- formatter.py              Output formatting (NORMAL/DEBUG/VERBOSE)
 |   |-- sbert_floors.py           SBERT embeddings for ASI floors (F5/F6/F9)
 |   |-- nudge.py                  Emergence push (serendipity)
 |   `-- guards/
 |       |-- injection_guard.py    F12: Pattern-based injection detection
 |       `-- ontology_guard.py     F10: Consciousness claim blocker
 |
 |-- enforcement/                  Verdict routing & refusal generation
 |   |-- routing.py                Escalation decisions
 |   `-- refusal/                  User-facing refusal builders
 |
 |-- config/runtime.py             Feature flags & defaults
 |-- physics/thermodynamics.py     Entropy manager, Landauer principle
 `-- scheduler/manager.py          Stage dependency tracking
```

### aclip_cai/ -- Intelligence Layer

Backend logic for MCP tools + 9-Sense sensory tools.

```
aclip_cai/
 |-- __init__.py                   v1.0.0, "ACLIP -- Console for AI on arifOS"
 |-- mcp_server.py                 FastMCP tool registry (9 triad + sensory tools)
 |-- mcp_bridge.py                 Legacy bridge (Ed25519 + Shannon entropy)
 |
 |-- triad/                        Trinity backend: 3 engines x 3+ stages = 10 functions
 |   |-- __init__.py               Re-exports: anchor, think, reason, integrate,
 |   |                              respond, validate, align, forge, audit, seal
 |   |-- delta/                    AGI Mind
 |   |   |-- anchor.py             Stage 000: Session init + F12 scan
 |   |   |-- think.py              Stage 222: 3-path reasoning (INTERNAL ONLY)
 |   |   |-- reason.py             Stage 333: Causal tracing (F2/F4/F7)
 |   |   `-- integrate.py          Stage 444: Context merge + Omega-0 adjust
 |   |-- omega/                    ASI Heart
 |   |   |-- respond.py            Stage 444: Draft gate (F4/F5/F6)
 |   |   |-- validate.py           Stage 555: Full F1-F13 audit
 |   |   `-- align.py              Stage 666: F9 Anti-Hantu + F10 Ontology gate
 |   `-- psi/                      APEX Soul
 |       |-- forge.py              Stage 777: EUREKA synthesis + Genius calc
 |       |-- audit.py              Stage 888: Final judgment + sovereign token
 |       `-- seal.py               Stage 999: VAULT999 commit + Phoenix-72
 |
 |-- core/                         Constitutional singletons
 |   |-- kernel.py                 ConstitutionalKernel singleton (audit, thermo, vault, ...)
 |   |-- lifecycle.py              5-state machine: INIT->ACTIVE->SABAR->HOLD->VOID
 |   |-- floor_audit.py            F1-F13 runtime auditor (FloorAuditor, AuditResult)
 |   |-- vault_logger.py           Tri-witness ledger (H+A+E consensus, WitnessRecord)
 |   |-- thermo_budget.py          Thermodynamic tracker (delta-S, Peace2, Omega-0, Genius)
 |   |-- federation.py             Multi-agent health (earth-witness E scoring)
 |   |-- amendment.py              Phoenix-72 protocol (72h cooldown amendments)
 |   `-- eval_suite.py             Regression test runner (EvalCase, EvalResult)
 |
 `-- tools/                        9-Sense sensory tools
     |-- aclip_base.py             Shared return shapes: ok(), partial(), void()
     |-- system_monitor.py         CPU, RAM, disk, temperature
     |-- fs_inspector.py           Read-only filesystem inspection (F4 entropy limit)
     |-- net_monitor.py            Network connections & ports
     |-- thermo_estimator.py       Cost projection (financial + thermodynamic)
     |-- safety_guard.py           Circuit breaker (forge_guard)
     |-- reality_grounding.py      Web fact-check cascade (DDGS->Playwright)
     |-- chroma_query.py           Vector memory (ChromaDB)
     |-- config_reader.py          Governance config flags
     `-- log_reader.py             Streaming log access
```

### aaa_mcp/ -- Transport Adapter

MCP transport layer. Zero decision logic.

```
aaa_mcp/
 |-- server.py                     INTERNAL 13-tool FastMCP surface
 |-- __main__.py                   CLI dispatcher (delegates to arifos_aaa_mcp)
 |-- rest.py                       REST API bridge (legacy)
 |-- streamable_http_server.py     HTTP streaming transport
 |-- vault_sqlite.py               SQLite vault fallback
 |-- observability.py              Metrics & telemetry
 |
 |-- protocol/                     Tool metadata & schemas
 |   |-- aaa_contract.py           AAA_CANONICAL_TOOLS, LAW_13_CATALOG, AXIOMS_333
 |   |-- tool_registry.py          ToolSpec dataclass, CANONICAL_TOOLS dict
 |   |-- schemas.py                JSON schemas for 13 tools
 |   |-- tool_naming.py            Public->legacy name mappings
 |   |-- tool_graph.py             Tool dependency graph (000->999)
 |   `-- response.py               Verdict envelope structure
 |
 |-- core/                         Transport-level wrappers
 |   |-- constitutional_decorator.py   Wraps core.kernel decorator
 |   |-- engine_adapters.py        Wraps core.kernel adapters + EUREKA
 |   `-- stage_adapter.py          Stage metadata
 |
 |-- guards/                       Transport-level guards
 |   |-- injection_guard.py        F12 preprocessing
 |   `-- ontology_guard.py         F10 postprocessing
 |
 |-- external_gateways/            Web search & content extraction
 |   |-- jina_reader_client.py     Jina Reader API (PRIMARY — clean Markdown)
 |   |-- perplexity_client.py      Perplexity API (fallback)
 |   `-- brave_client.py           Brave Search API (fallback)
 |
 |-- sessions/                     Session management
 |   |-- session_ledger.py         VAULT999 Merkle-chained audit trail
 |   `-- session_dependency.py     Session dependency tracking
 |
 |-- vault/hardened.py             EUREKA sieve (novelty detection)
 |-- services/                     Redis, constitutional metrics
 |-- infrastructure/               Logging (JSON + correlation IDs), rate limiter
 |-- notifiers/                    Telegram judge alerts
 `-- wrappers/                     K8s, OPA policy integration
```

### arifos_aaa_mcp/ -- Canonical PyPI Surface

The external-facing package. Wraps `aaa_mcp` with governance envelope.

```
arifos_aaa_mcp/
 |-- __main__.py                   CLI: default SSE, reads HOST/PORT env vars
 |-- server.py                     create_aaa_mcp_server() -- 13 @mcp.tool() with governance
 |-- governance.py                 LAW_13_CATALOG, TOOL_DIALS_MAP, wrap_tool_output()
 |-- contracts.py                  require_session(), validate_input()
 |-- rest_routes.py                REST API definitions
 `-- fastmcp_ext/                  FastMCP 3.0 extensions
     |-- transports.py             run_server() dispatcher (stdio/sse/http)
     |-- middleware.py             Request/response middleware
     |-- discovery.py              Tool discovery builder
     |-- telemetry.py              Observability hooks
     `-- contracts.py              MCP-level contracts
```

### 333_APPS/ -- Application Stack (L1-L7)

```
333_APPS/
 |-- KERNEL/      Constitutional substrate docs                        SEALED
 |-- L1_PROMPT/      System prompt & examples                             Production
 |-- L2_SKILLS/      9 A-CLIP actions + utility skills                    Production
 |-- L3_WORKFLOW/    000->999 constitutional workflow definitions          Production
 |-- L4_TOOLS/       MCP client configs (Claude, Kimi, Codex, OpenCode)   Production
 |-- L5_AGENTS/      Multi-agent federation (4 agent stubs + hypervisor)  Pilot
 |-- L6_INSTITUTION/ Trinity consensus framework (stubs)                  Stubs
 `-- L7_AGI/         Recursive self-healing research                      Research
```

---

## Import Architecture

```
External Client
       |
  arifos_aaa_mcp.server         PUBLIC (wraps with governance envelope)
       |
  aaa_mcp.server                INTERNAL (FastMCP instance)
       |
  aclip_cai.triad.*             INTELLIGENCE (anchor, reason, forge, seal, ...)
       |
  aclip_cai.core.kernel         SINGLETON (audit, thermo, vault, lifecycle)
       |
  core.organs.*                  KERNEL (sense, think, reason, empathize, judge, seal)
       |
  core.shared.floors             FOUNDATION (13-floor THRESHOLDS)
  core.shared.physics            PHYSICS (W_3, delta_S, Omega_0, G)
  core.shared.types              CONTRACTS (Verdict, FloorScores, pydantic models)
  core.shared.crypto             CRYPTO (Ed25519, SHA-256, Merkle)
```

### Critical Imports in aaa_mcp/server.py

```python
from fastmcp import FastMCP
from aclip_cai.triad import align, anchor, audit, forge, integrate, reason, respond, seal, think, validate
```

### Decorator Order (Critical)

```python
@mcp.tool()                    # OUTER -- FastMCP registers this
@constitutional_floor("F2")   # INNER -- enforcement runs at call time
async def my_tool(...):
```

If reversed, FastMCP registers the unwrapped function and enforcement never runs.

---

## VAULT999 -- Immutable Audit Ledger

Every decision flows through VAULT999 at stage 999:

- **Append-only** -- entries are never deleted or modified
- **Hash-chained** -- each entry cryptographically linked to previous (Merkle tree)
- **Tamper-evident** -- any modification breaks `verify_chain()`
- **Force-tracked** -- `vault999.jsonl` committed with `git add -f`
- **Tri-witness** -- each entry carries H (Human) + A (AI) + E (Earth) scores

```
Backend priority:
  1. PostgreSQL (VAULT999_DSN env var)
  2. SQLite (vault_sqlite.py fallback)
  3. In-memory (development/test)
  4. JSONL (VAULT999/vault999.jsonl, always written)
```

### EUREKA Sieve (What Enters VAULT999)

| Score | Classification | Action |
|-------|---------------|--------|
| >= 0.75 | EUREKA moment | Permanent storage |
| 0.50-0.75 | SABAR (cooling) | Intermediate ledger |
| < 0.50 | TRANSIENT | Don't store |

Novelty measured by: Jaccard n-gram similarity, fingerprint dedup, entropy reduction, ontological shift, decision weight.

---

## Deployment Architecture

### Transport Modes

| Transport | Command | Use Case |
|-----------|---------|----------|
| **stdio** | `python -m arifos_aaa_mcp stdio` | Claude Desktop, Cursor IDE |
| **SSE** (default) | `python -m arifos_aaa_mcp` | VPS deployment (Coolify/Hostinger) |
| **HTTP** | `python -m arifos_aaa_mcp http` | Streamable HTTP, ChatGPT, cloud |
| **REST** | `python -m aaa_mcp rest` | FastAPI bridge with OpenAPI |

### Live Endpoints

- Health: `https://arifosmcp.arif-fazil.com/health`
- SSE: `https://arifosmcp.arif-fazil.com/sse`
- MCP: `https://arifosmcp.arif-fazil.com/mcp`

### Container

```bash
docker build -t arifos .
docker run -p 8080:8080 arifos                    # Streamable HTTP (default)
docker-compose up -d                               # Traefik + Coolify routing
```

- **Docker:** Multi-stage Python 3.12-slim, health check every 15s, 2GB RAM limit
- **Fly.io:** Singapore region, auto-scaling, zero-running when idle
- **Coolify:** Traefik routing mesh, TLS via Let's Encrypt

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8080` | Listen port |
| `AAA_MCP_TRANSPORT` | `sse` | Default transport mode |
| `AAA_MCP_OUTPUT_MODE` | `user` | Output mode (user/debug) |
| `ARIFOS_PHYSICS_DISABLED` | `0` | Disable thermodynamic calcs |
| `ARIFOS_GOVERNANCE_SECRET` | (random) | HMAC key for governance tokens |
| `JINA_API_KEY` | - | Jina Reader (primary search/content) |
| `PPLX_API_KEY` | - | Perplexity search (fallback) |
| `BRAVE_API_KEY` | - | Brave search (fallback) |
| `VAULT999_DSN` | - | PostgreSQL connection string |
| `REDIS_URL` | - | Redis session cache |

---

## Code Statistics

| Package | Files | Lines | Purpose |
|---------|-------|-------|---------|
| `core/` | 47 | ~14,200 | Constitutional kernel |
| `core/organs/` | 5 | ~2,300 | 7-organ pipeline |
| `core/shared/` | 12 | ~4,100 | Physics, floors, types, crypto |
| `core/kernel/` | 9 | ~2,600 | Evaluator, decorator, orchestrator |
| `aclip_cai/triad/` | 10 | ~2,500 | Trinity backend |
| `aclip_cai/core/` | 8 | ~2,000 | Constitutional singletons |
| `aclip_cai/tools/` | 11 | ~1,500 | 9-Sense sensory tools |
| `aaa_mcp/` | ~70 | ~5,000 | Transport adapter |
| `arifos_aaa_mcp/` | 10 | ~2,500 | PyPI surface + governance |
| `333_APPS/` | 50+ | ~3,000 | L1-L7 application stack |
| `tests/` | 154 | ~8,000 | Test suite (25 categories) |
| **Total** | **~380** | **~45,000** | |

---

## Key Design Decisions

### 1. Four-Layer L0 Kernel

Strict separation of Surface/Transport/Intelligence/Kernel prevents accidental coupling. `core/` has zero external dependencies beyond numpy/pydantic. Any transport (stdio, HTTP, WebSocket) can be added without touching decision logic.

### 2. Thermodynamic Isolation

AGI (Delta) and ASI (Omega) engines cannot see each other's reasoning until stage 444. This is analogous to double-blind review -- prevents the safety engine from rubber-stamping the reasoning engine's conclusions.

### 3. Floor-Based Governance

Physics-inspired constraints (entropy, information theory, Bayesian uncertainty) provide objective, measurable safety bounds. Hard floors fail-closed (VOID). The 13-floor system is evaluated in dependency order: Walls first, then AGI floors, then ASI floors, then Mirrors last.

### 4. Amanah Handshake

`seal_vault` cannot write to the ledger without a cryptographically signed token from `apex_judge`. This prevents any tool from bypassing the judgment stage. The default verdict is VOID (fail-closed).

### 5. Phoenix-72 Protocol

Constitutional amendments require a 72-hour cooling period + sovereign approval before sealing. Anti-Hantu filter blocks consciousness language in amendment proposals.

### 6. MCP Protocol Choice

Standard MCP protocol enables integration with Claude Desktop, Cursor, Kimi, n8n, and future clients without custom adapters. FastMCP 3.0 provides the framework.

---

*DITEMPA BUKAN DIBERI -- Forged, Not Given*
