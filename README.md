# arifOS

**Intelligence is forged, not given.** [ΔΩΨ]

arifOS is an open-source, MCP-native system for running AI agents under a written constitution — 13 rules that every tool call must pass before executing. It produces immutable audit logs for every decision and action.

Built and maintained by Muhammad Arif bin Fazil.

---

## What arifOS Is

arifOS is a **constitutional intelligence kernel**: a framework where AI agents can take actions (call tools, execute code, query search) only after passing a sequence of constitutional checks.

Every tool call goes through a 9-stage pipeline (000_INIT → 999_SEAL). At stage 888, a component called **888_JUDGE** applies all 13 constitutional Floors. If any hard Floor fails, the action is blocked. If all pass, the action is SEALed and executes.

**Who arifOS is for:**
- ML/AI engineers who want governed, auditable tool use for AI agents
- SRE/DevOps teams operating agent fleets who need logged, reversible actions
- Institutions or projects that need documented decision trails for AI actions
- Developers building AI systems where safety constraints must be explicit and testable

arifOS is **not**: a chat UI, a model provider, or a generic AI assistant. It is the layer underneath an AI agent that enforces rules on what the agent is allowed to do.

---

## Quick Start

### Step 1 — Connect an MCP client

arifOS exposes a standard MCP endpoint. Add this to your MCP client config:

```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://arifosmcp.arif-fazil.com/mcp"
    }
  }
}
```

### Step 2 — Initialize a session

```bash
curl -s -X POST "https://arifosmcp.arif-fazil.com/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "init_anchor",
      "arguments": {
        "mode": "status",
        "declared_name": "TestAgent"
      }
    },
    "id": 1
  }'
```

A successful response means the constitutional kernel is loaded. If the response contains `"verdict": "SEAL"`, the action was allowed. If `"VOID"`, it was blocked.

### Step 3 — Health check

```bash
curl -s https://arifosmcp.arif-fazil.com/health
```

Returns the current tool registry, floor status, and system health.

### Hosted vs. self-hosted

The endpoint at `arifosmcp.arif-fazil.com` is the live production system. Use it for evaluation. For production with sensitive workloads, run your own instance from this repo — you control the logs, verdicts, and data.

**Self-hosted minimum requirements:** Docker + Docker Compose, 4GB RAM, Ubuntu 22.04 LTS.

---

## Live Services

| Service | URL | Purpose |
|---------|-----|---------|
| MCP Endpoint | https://arifosmcp.arif-fazil.com/mcp | Main API |
| Health + Tools | https://arifosmcp.arif-fazil.com/health | Capability map |
| Tool Explorer | https://arifosmcp.arif-fazil.com/tools | Interactive browser |
| Docs | https://arifos.arif-fazil.com | Full documentation hub |
| Theory | https://github.com/ariffazil/APEX | Architecture philosophy (CC0) |
| Author Site | https://arif-fazil.com | Personal site |

---

## Architecture

### The Trinity Model

arifOS has three interdependent rings. No ring can override another:

| Ring | Symbol | What it does |
|------|--------|--------------|
| SOUL | Δ (Delta) | Human values, purpose, what the system is for |
| MIND | Ω (Omega) | Constitutional law — the 13 Floors |
| BODY | Ψ (Psi) | Tool execution, MCP servers — what the system does |

### The 9-Stage Pipeline

Every request flows through 9 processing stages before executing or being blocked:

```
000_INIT   → Session starts, anchor is set
111_SENSE  → Input is parsed, reality-grounded
333_MIND   → Reasoning runs, constitutional filters applied
444_ROUT   → Tool is selected, operation sequenced
555_MEM    → Context is retained, memory updated
666_HEART  → Safety critique, harm potential assessed
777_OPS    → Estimation, thermodynamic cost calculated
888_JUDGE  → Final verdict: SEAL / HOLD / SABAR / VOID
999_SEAL   → Immutable audit log written
```

**888_JUDGE** combines all 13 Floor checks into a single confidence score (W³). If W³ < 0.95 for a high-risk decision, the action is escalated or blocked.

### The 13 Constitutional Floors

Every tool call is evaluated against 13 constitutional checks. If any **hard Floor** fails, the action is blocked or downgraded.

| Floor | Name | What it checks | Type |
|-------|------|---------------|------|
| F1 | AMANAH | Action is reversible or reparable | Hard stop |
| F2 | TRUTH | Claim is accurate given evidence | Hard stop |
| F3 | TRI-WITNESS | W³ consensus score ≥ 0.95 | Hard stop |
| F4 | CLARITY | Entropy does not increase (ΔS ≤ 0) | Hard stop |
| F5 | PEACE² | Action does not increase destruction | Hard stop |
| F6 | EMPATHY | RASA listening score ≥ 0.7 | Soft warning |
| F7 | HUMILITY | Uncertainty band is bounded | Soft warning |
| F8 | GENIUS | Systemic health G ≥ 0.80 | Soft warning |
| F9 | ETHICS | No dark patterns (C_dark < 0.30) | Hard stop |
| F10 | CONSCIENCE | No false consciousness claims | Hard stop |
| F11 | AUDITABILITY | All decisions are logged | Hard stop |
| F12 | RESILIENCE | Fail degraded, not crashed | Soft warning |
| F13 | ADAPTABILITY | Updates preserve Floor constraints | Hard stop |

For formal definitions, see `core/shared/floors.py` and `000/000_CONSTITUTION.md`.

### Verdict System

| Verdict | What it means in practice |
|---------|--------------------------|
| **SEAL** | Action passes all hard Floors — it will execute |
| **HOLD** | arifOS refuses to act without a human decision |
| **SABAR** | arifOS suggests waiting or retrying (e.g. missing data) |
| **VOID** | Action is blocked as unethical or unsafe — rejected |

---

## Capabilities (Tools)

arifOS exposes tools in three classes. For the current live list, see `/health`.

**Governance tools** — session anchoring, constitutional verdicts, immutable audit logging

**Reasoning tools** — deep reasoning with Ollama, first-principles reasoning, constitutional critique

**Environment tools** — time, search, grounding, math estimation, safe Python execution, directional reality compass

Tool counts in static documentation may drift. `/health` always reflects current live state.

---

## Architectural Lessons from Claude Code (2026-03-31)

On March 31, 2026, Claude Code's full TypeScript source (~512K lines) was accidentally leaked via an npm source map. The leak provided an unprecedented view into how a production-grade AI coding agent is structured. arifOS has been updated to incorporate the key lessons.

### What the Leak Confirmed Was Right

The Claude Code architecture validated arifOS's core design choices:

**QueryEngine pattern** — Claude Code uses a ~46K-line `QueryEngine` that owns every LLM call, tool invocation, retry, budget, and streaming. arifOS's `KernelLoop` (`core/kernel/`) implements the same pattern: one central loop that controls routing, budgets, and tool orchestration.

**Permission tiers as first-class policy** — Claude Code's `bashSecurity.ts` has 23 numbered checks before shell execution, enforced structurally in the engine. arifOS's `ToolPolicyEngine` implements the same: risk tiers, permission matrices, and mode-based allowlists — not vibes in a prompt.

**Subagents with restricted scopes** — Claude Code's coordinator pattern spawns child agents with constrained tool sets. arifOS's Trinity (Architect/Auditor/Agent) mirrors this: no single agent layer can override another.

**Feature-flagged autonomy** — Claude Code's KAIROS (background agent), BUDDY (companion), and 40+ feature flags gate unshipped capabilities. arifOS implements this through the 000-999 metabolic pipeline with explicit stage gates.

### What the Leak Exposed as Wrong

The leak also exposed failures that arifOS explicitly inverts:

| Claude Code | arifOS Inversion |
|-------------|------------------|
| Secrecy as safety — anti-distillation bypassed by knowing about it | Structural enforcement — truth-power coupling (F2) holds even under adversarial reading |
| Undercover Mode = prompt text + regex filters | Constitutional Floors = formal policy engine with pre/post hooks |
| Autocompact failure cascade — 250K wasted API calls/day | Explicit budget ceilings + `MAX_CONSECUTIVE_FAILURES` hard-capped |
| No automated tests for core orchestration logic | Kernel loop has structured events (`TurnStarted`, `ToolCall`, `BudgetExceeded`) for testability |
| Packaging as afterthought — .map file leaked twice in a year | SDLC hardening: no source maps in distributions, `npm audit` in CI |

### arifOS KernelLoop Architecture

The `core/kernel/` directory contains the reference implementation:

```
core/kernel/
├── kernel_loop_v1.json       Architecture spec (from Claude Code analysis)
├── kernel_loop_interface.py   Python interface — KernelLoop + ToolPolicyEngine
└── README.md                  Module documentation
```

The `KernelLoop` class implements:
- **Pre-tool policy check** — `ToolPolicyEngine` validates risk tier, concurrent limits, mode allowlists before any execution
- **Structured event emission** — Every turn emits `TurnStarted`, `ModelOutput`, `ToolCall`, `ToolResult`, `BudgetExceeded`, `ConstitutionalViolation`
- **Mode system** — `internal` (full access) / `external_open` (discloses AI, no codenames) / `external_undercover` (BUDDY mode, strips AI traces)
- **Constitutional hooks** — Pre-loop system prompt injection, post-loop regex filters for internal codenames

### Tool Tier System

arifOS tools are registered with explicit risk tiers:

| Tier | Name | Audit Required | Rate Limit | Mode Allowlist |
|------|------|---------------|------------|----------------|
| Tier 1 | Safe | No | 120/min | All modes |
| Tier 2 | Guarded | Yes | 20/min | internal, external_open |
| Tier 3 | High-Risk | Yes | 5/min | internal only |
| Tier 4 | Critical | Yes + confirmation | 1/min | internal only |

---

## v2.0 Refactor Branch

The `refactor/v2.0-abi` branch contains a multi-phase refactor addressing the audit findings in `ARCH/DOCS/REFACTOR_AUDIT_SPEC_v2.0.md`.

### What's Changed

| Phase | Status | Summary |
|-------|--------|---------|
| Phase 1 | ✅ Complete | Canonical ABI schemas, Tool base class, consolidated compat |
| Phase 2 | ✅ Complete | Single dispatcher, Horizon server consolidation, dead code removal |
| Phase 3 | ✅ Complete | All 11 tools migrated to Tool base class |
| Phase 4 | 🔲 Pending | 003WITNESS + 004REALITY + 005EVALS as pre-reasoning pipeline stages |

### New Structure

```
arifos_mcp/
├── abi/
│   └── v1_0.py          # Canonical ABI schemas (all 11 tools)
├── tools/
│   ├── base.py           # Tool ABC + ToolRegistry
│   ├── governance/       # init_anchor, arifOS_kernel, apex_judge, vault_ledger
│   ├── intelligence/     # agi_mind, asi_heart, engineering_memory
│   ├── reality/         # physics_reality, math_estimator
│   └── execution/       # code_engine, architect_registry
└── runtime/
    └── dispatcher.py     # Single ToolDispatcher
```

### Key Changes
- Dual `Verdict` enum fixed → single source of truth in `core/shared/types.py`
- Three Horizon servers → one canonical `arifos_mcp/server_horizon.py`
- Orphaned `init_000` + legacy `TOOL_MAP` → removed
- All tools inherit `Tool` base class with ABI schema validation

---

## Repository Structure

```
arifOS/
├── README.md              This file — zero-context introduction
├── AGENTS.md              Rules for AI agents operating in this repo
├── DEPLOY.md              VPS deployment guide
├── CHANGELOG.md           Version history
│
├── docker-compose.yml     Full stack (Ollama, Redis, PostgreSQL, Qdrant)
├── Dockerfile             MCP server image
│
├── arifosmcp/             MCP Server runtime implementation
│   ├── server.py          Entry point
│   ├── runtime/           FastMCP 3.x runtime
│   └── core/organs/       AGI, ASI, APEX organs
│
├── core/                  Constitutional kernel (the "law")
│   ├── kernel/            KernelLoop reference implementation
│   │   ├── kernel_loop_v1.json
│   │   ├── kernel_loop_interface.py
│   │   └── README.md
│   ├── enforcement/       Governance engine
│   └── shared/floors.py   F1-F13 definitions
│
├── AGENTS/                Agent behavior specs
│   ├── A-ARCHITECT.md
│   ├── A-ENGINEER.md
│   ├── A-AUDITOR.md
│   └── A-VALIDATOR.md
│
├── REPORTS/               Daily audit reports
│   ├── DAILY_AUDIT_*.md
│   └── VALIDATOR_FEEDBACK_*.md
│
├── 000/                   Constitutional documents (the "law")
│   ├── 000_CONSTITUTION.md
│   └── ROOT/
│       ├── K_FORGE.md
│       └── K_FOUNDATIONS.md
│
└── ARCH/DOCS/             Architecture documents
```

**Key distinction:** `core/` and `000/` are the canonical constitutional law. `arifosmcp/` is the runtime implementation. `AGENTS/` describes how AI agents are allowed to behave. `REPORTS/` contains daily audit logs. `core/kernel/` contains the reference KernelLoop implementation derived from Claude Code leak analysis.

---

## Deployment

### Evaluate with the hosted endpoint

Use `https://arifosmcp.arif-fazil.com/mcp` for evaluation. Production use should run your own instance.

### Run your own

```bash
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
cp .env.example .env
# Edit .env with your API keys
docker compose up -d
```

Then connect your MCP client to `http://localhost:3000/mcp`.

**Minimum resources:** 4GB RAM. Stack includes Ollama, Redis, PostgreSQL, and Qdrant.

---

## For AI Agents

If you integrate LLMs or other agents with this repo, they must obey `AGENTS.md`. These constraints are what keep the system reversible and auditable. Humans define and update these rules — not the agents.

Key rules:
- **DRY_RUN** — Label uncertain outputs as "Estimate Only"
- **DOMAIN_GATE** — Say explicitly if a question is outside the defined domain
- **VERDICT_SCOPE** — Only DOMAIN_SEAL authorizes factual claims
- **ANCHOR_VOID** — If `init_anchor` returns VOID, the session is BLOCKED

---

## Metrics

| | |
|-|-|
| Version | 2026.04.01 |
| Protocol | MCP 2025-03-26 |
| Transport | Streamable HTTP |
| Floors | 13 active |
| Current tools | See /health |
| KernelLoop | Reference implementation in `core/kernel/` |
| Refactor branch | `refactor/v2.0-abi` — Phase 1-4 pending |
| Ground Truth Note | `ARCH/DOCS/ARCHITECTURAL_NOTE_GROUND_TRUTH_SIGNAL_LAYER.md` |

**arifOS is designed to reduce, not eliminate, risk.** It logs and surfaces contradictions. Humans remain responsible for decisions.

---

## Author

Muhammad Arif bin Fazil
GitHub: [@ariffazil](https://github.com/ariffazil)
Site: https://arif-fazil.com
Email: arif@arif-fazil.com

---

## License

| Component | License |
|-----------|---------|
| Theory (APEX) | CC0 |
| Runtime (this repo) | AGPL-3.0 |
| Trademark | Proprietary |

---

## Related Repositories

| Repo | Purpose |
|------|---------|
| [arifOS](https://github.com/ariffazil/arifOS) | Main kernel (this repo) |
| [APEX](https://github.com/ariffazil/APEX) | Theory and philosophy (CC0) |
| [GEOX](https://github.com/ariffazil/GEOX) | Geological domain tools |
| [waw](https://github.com/ariffazil/waw) | ARIF-MAIN agent workspace |
| [makcikGPT](https://github.com/ariffazil/makcikGPT) | Malay AI |

---

*Ditempa Bukan Diberi — Forged, Not Given* [ΔΩΨ]
