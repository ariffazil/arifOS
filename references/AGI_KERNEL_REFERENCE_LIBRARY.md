# arifOS AGI Kernel — External Reference Library

> **Purpose:** Curated external resources for arifOS forging agents (Hermes, OpenCode, A-FORGE) to study and extract patterns from — not to adopt wholesale, but to *steal from* under arifOS constitutional law.
>
> **DITEMPA BUKAN DIBERI** — Every pattern here must be re-forged through F1-F13 floors before it touches arifOS kernel code.

---

## How to Use This Library

This is organised by **capability layer**, not by repo. Your forging agent should:

1. Read the **Priority column** — Tier 1 first, Tier 2 second, Tier 3 for context
2. Look at the **What to steal** column — this tells you the *pattern*, not the code
3. Check the **Map to arifOS** column — this tells you which repo/component should absorb it
4. Never copy. Always **re-implement** under arifOS constitutional floors

---

## Layer 1 — MCP Substrate (The Protocol)

*What it gives you: Standard wire format for tools/resources/prompts, transport boundaries, auth patterns.*

### Tier 1 — Must Ingest First

| Resource | Type | Stars | What to Steal | Map to arifOS |
|----------|------|-------|---------------|---------------|
| [MCP Canonical Docs](https://modelcontextprotocol.io/docs/getting-started/intro) | Docs | — | Tool/resource/prompt surface semantics, transport patterns (stdio vs HTTP/SSE), auth boundaries | arifOS kernel (keep MCP spec compliant on external surface) |
| [MCP Draft Spec](https://modelcontextprotocol.io/specification/draft) | Spec | — | Transport auth, extension points, capability negotiation | arifOS kernel (spec edge cases) |
| [FastMCP](https://gofastmcp.com/getting-started/welcome) | Framework | — | Clean MCP server/client ergonomics, tool registration patterns, lifecycle management | arifOS (use for MCP server scaffolding, not kernel logic) |
| [awesome-mcp](https://github.com/abordage/awesome-mcp) | List | ~7 | Continuous discovery of MCP servers/clients/frameworks. Run weekly scan. | A-FORGE (discovery pipeline) |

### Tier 2 — Useful Pattern Mining

| Resource | Type | Stars | What to Steal | Map to arifOS |
|----------|------|-------|---------------|---------------|
| Graphiti MCP server | Code | 27.4k | Temporal knowledge graph as MCP surface — exposes graph queries as MCP tools | arifOS (MCP memory tools pattern) |

---

## Layer 2 — Governance & Control Plane

*What it gives you: Identity enforcement, permission gating, audit trails, human-in-the-loop, rate limiting.*

### Tier 1 — Must Ingest First

| Resource | Type | Stars | What to Steal | Map to arifOS |
|----------|------|-------|---------------|---------------|
| [Agentic Control Plane](https://agenticcontrolplane.com/product) | SaaS+OSS | — | Identity propagation per tool call, deny-by-default policies, PII detection on tool I/O, budget caps, per-user audit trail | AAA + A-FORGE (policy enforcement patterns, not the SaaS) |
| [Temporal](https://github.com/temporalio/temporal) | Platform | 21k | Durable execution — workflows that survive crashes, replay, retries, checkpoints. The gold standard for "code that must not lose state." | A-FORGE + arifOS (durable forge pipelines, long-running agents) |
| [Sovereign-OS (Paper)](https://arxiv.org/abs/2603.14011) | Paper | — | Charter-governed architecture: YAML mission scope, fiscal boundaries, TrustScore earned autonomy, SHA-256 audit receipts | arifOS (theoretical comparison. Your E7 is more nuanced than TrustScore) |

### Tier 2 — Useful Pattern Mining

| Resource | Type | Stars | What to Steal | Map to arifOS |
|----------|------|-------|---------------|---------------|
| [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) | Framework | 11.3k | Declarative agent definitions, multi-agent workflows, A2A+MCP interop patterns, thread persistence | AAA (A2A patterns, agent card specs) |
| [GitHub Enterprise AI Control Plane](https://github.blog/changelog/2026-02-26-enterprise-ai-controls-agent-control-plane-now-generally-available/) | Enterprise | — | Language of production governance: approvals, rate limits, audit-ready routes | AAA (vocabulary alignment for docs/specs) |
| [LangGraph Durable Execution](https://langchain-ai.github.io/langgraph/concepts/durable_execution/) | Framework | — | Stateful graph workflows, checkpoints, human-review nodes, branching | A-FORGE (agent loop patterns, not framework) |

---

## Layer 3 — Graph Memory (Temporal + Episodic)

*What it gives you: Memory that knows *when* something happened, not just *what*.*

### Tier 1 — Must Ingest First

| Resource | Type | Stars | What to Steal | Map to arifOS |
|----------|------|-------|---------------|---------------|
| [Graphiti](https://github.com/getzep/graphiti) | Framework | 27.4k | Temporal context graphs: facts with validity windows, episodic provenance, hybrid retrieval (semantic + BM25 + graph), community summaries, entity clustering | arifOS L5 memory — your Graphiti layer should study this for fact invalidation, temporal query, hybrid retrieval patterns |
| [Awesome GraphMemory Survey](https://github.com/DEEP-PolyU/Awesome-GraphMemory) | Survey | 292 | Taxonomy of graph-based agent memory: 5 design dimensions, 8 memory modules, survey of 50+ papers | arifOS (library-wide memory architecture reference) |

### Tier 2 — Useful Pattern Mining

| Resource | Type | Stars | What to Steal | Map to arifOS |
|----------|------|-------|---------------|---------------|
| Zep paper (arXiv 2501.13956) | Paper | — | Temporal knowledge graph architecture for agent memory — the theory behind Graphiti | arifOS (memory theory) |

---

## Layer 4 — Event Mesh (Inter-Agent Communication)

*What it gives you: Reliable publish/subscribe between organs, replay, backpressure, durable consumers.*

### Tier 2 — Useful Pattern Mining

| Resource | Type | Stars | What to Steal | Map to arifOS |
|----------|------|-------|---------------|---------------|
| [nats.py](https://github.com/nats-io/nats.py) | Client | 1.2k | Python NATS client — JetStream publish/consume, KV store, Object Store, WebSocket support | arifOS + A-FORGE (transport mechanics only — your envelope stays native) |
| [NATS JetStream gist](https://gist.github.com/aladagemre/41dd5a35ac2da585d4cd54d895326064) | Example | — | Lightweight publish/consume pattern, stream config, durable consumer setup | arifOS (quick reference for JetStream wiring) |

**Key rule for NATS:** Your subject taxonomy, envelope schema, and governance metadata must stay arifOS-native. Only steal transport mechanics.

---

## Layer 5 — Multi-Agent Orchestration

*What it gives you: Agent decomposition, handoffs, tracing, guardrails, observability.*

### Tier 2 — Useful Pattern Mining

| Resource | Type | Stars | What to Steal | Map to arifOS |
|----------|------|-------|---------------|---------------|
| [Mastra](https://github.com/mastra-ai/mastra) | Framework | 25k | TS agent framework: MCP tool support, observability, context management, agent-to-agent handoffs, workflow definitions | AAA (operator-side UX, MCP authoring, TS agent interfaces) |
| [OpenAI Agents JS](https://github.com/openai/openai-agents-js) | Framework | 3.2k | Guardrails, handoffs, tracing, workflow observability patterns | AAA (guardrail patterns, tracing hooks — not the runtime) |
| [OpenAI Agents Python](https://github.com/openai/openai-agents-python) | Framework | — | Sandbox agents, durable work, human-in-the-loop patterns | A-FORGE (sandbox agent patterns for safe execution) |
| [CrewAI](https://crewai.com/open-source) | Framework | — | Role-based multi-agent decomposition, task routing | A-FORGE (role decomposition patterns — not the governance model) |

### Tier 3 — Optional Comparative Context

| Resource | Type | Stars | What to Steal | Map to arifOS |
|----------|------|-------|---------------|---------------|
| PraisonAI MCP examples | Framework | — | Simple multi-agent patterns exposed as MCP | A-FORGE (quick reference for MCP tool wrapping patterns) |

---

## Layer 6 — Durable Execution & Self-Modification

*What it gives you: Code that survives crashes, self-improvement pipelines that are replayable, safe to mutate.*

### Tier 1 — Must Ingest First

| Resource | Type | Stars | What to Steal | Map to arifOS |
|----------|------|-------|---------------|---------------|
| [Temporal Python SDK](https://github.com/temporalio/sdk-python) | SDK | — | Workflow-as-code, activity retries, saga patterns, async activities | A-FORGE (durable forge pipelines — deploy, test, mutate under E7) |
| [DuraLang concept](https://temporal.io/code-exchange/duralang-durable-stochastic-ai-agents-with-one-decorator) | Concept | — | Making LLM/tool/MCP/agent calls durable with one decorator — replayable, checkpointed | A-FORGE (safe self-modification where code changes are replayable and reversible) |

---

## Tier Ranking Summary

| Tier | Meaning | Which to Start With |
|------|---------|---------------------|
| **Tier 1** | Must ingest — foundational patterns the kernel needs | MCP docs → Temporal → Graphiti → Agentic Control Plane → Sovereign-OS paper |
| **Tier 2** | Useful pattern mining — study, don't adopt | Mastra → OpenAI Agents → LangGraph → Microsoft Agent Framework |
| **Tier 3** | Optional context — comparative only | CrewAI → PraisonAI → awesome lists |

---

## Library Stack Summary

```
arifOS AGI Kernel Reference Stack

Layer 1: MCP Substrate
├── MCP Canonical Docs — protocol truth
├── MCP Draft Spec — transport/auth edge cases
├── FastMCP — implementation ergonomics
└── awesome-mcp — continuous discovery

Layer 2: Governance & Control Plane
├── Agentic Control Plane — identity, policy, audit patterns
├── Temporal — durable execution gold standard
├── Sovereign-OS — theoretical charter governance
├── Microsoft Agent Framework — A2A/MCP interop at scale
└── LangGraph — stateful graph orchestration

Layer 3: Graph Memory
├── Graphiti — temporal knowledge graphs (closest to your L5)
└── Awesome GraphMemory — survey taxonomy

Layer 4: Event Mesh
└── nats.py + JetStream examples — transport mechanics only

Layer 5: Multi-Agent Orchestration
├── Mastra — TS agent framework patterns
├── OpenAI Agents JS/Python — guardrails, tracing, sandbox
└── CrewAI — role decomposition

Layer 6: Durable Execution
├── Temporal Python SDK — crash-safe workflows
└── DuraLang concept — durable agent calls
```

---

## Per-Repo Mapping for Forging Agents

### For arifOS kernel (Python)

| What to Study | Why It Matters |
|---------------|----------------|
| MCP canonical docs + spec | Keep external surface standards-compliant |
| Temporal concepts | Durable execution patterns for long-running kernel operations |
| Graphiti | Temporal memory architecture — fact invalidation, hybrid retrieval |
| Agentic Control Plane | Policy enforcement at the dispatch layer (not in prompts) |
| GraphMemory survey | Memory architecture design dimensions |

### For AAA (TypeScript, port 3001)

| What to Study | Why It Matters |
|---------------|----------------|
| Mastra | Operator-side UX, MCP authoring, TS agent patterns |
| OpenAI Agents JS | Guardrail UI, tracing dashboards, handoff visualization |
| Microsoft Agent Framework | A2A patterns, agent card specs, thread persistence |
| Agentic Control Plane docs | Policy enforcement UI patterns |

### For A-FORGE (TypeScript, port 7071)

| What to Study | Why It Matters |
|---------------|----------------|
| Temporal + SDK | Durable forge pipelines — executions that survive crashes |
| OpenAI Agents Python | Sandbox patterns for safe code execution |
| CrewAI | Role decomposition patterns |
| DuraLang | Safe self-modification — replayable code changes |
| awesome-mcp | Continuous MCP server discovery |

### For GEOX / WEALTH / WELL (Python domain organs)

| What to Study | Why It Matters |
|---------------|----------------|
| MCP canonical docs | Tool surface standards |
| Graphiti | Temporal context for domain evidence |

---

## How to Ingest (Instructions for Forging Agent)

When I say "study X":

1. **Clone the repo** into `/root/references/<name>/` for quick access
2. **Read the README and architecture docs** — understand what problem it solves
3. **Extract ONE pattern** that maps to an arifOS gap — not the whole framework
4. **Write a thin reference** in `/root/arifOS/references/patterns/<name>/` — what it does, what to steal, what to ignore
5. **Never import their code** — always re-implement under arifOS constitutional floors
6. **Tag with epistemic band** — is this a PROVEN pattern, a HYPOTHESIS, or COMPARATIVE_CONTEXT?

Example pattern extraction:

```python
# Pattern: Temporal fact invalidation (from Graphiti)
# Map to: arifOS L5 memory
# Implementation note: Instead of DELETE, set valid_until timestamp
# Constitutional check: F2 TRUTH (must preserve history, not rewrite it)
```

---

*DITEMPA BUKAN DIBERI — Forged, Not Given*
*Compiled: 2026-06-14 by Hermes ASI*
*For: arifOS federation forging agents (OpenCode, A-FORGE, Hermes)*
