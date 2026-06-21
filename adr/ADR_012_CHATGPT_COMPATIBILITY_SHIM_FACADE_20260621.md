# ADR-012: ChatGPT Compatibility Swarm Facade
**Status:** `888_HOLD` (PROPOSED under Plan_ID: `SWARM_SHIM_ELEVATION_20260621_001`)
**Owner:** Arif bin Fazil (Sovereign/Architect)
**Date:** 2026-06-21

---

## Context

To achieve non-developer-mode discovery in ChatGPT/OpenAI client runtimes, the arifOS MCP server must register standard `search` and `fetch` tools. 

To bridge this, we establish a **read-only, idempotent, host-adaptive Swarm Facade** (`_arif_swarm_orchestrate`) that:
1. Presents familiar interfaces to the host.
2. Decomposes tasks using short-lived, role-specialized micro-agents (Scout, Verifier, Synthesizer).
3. Enforces strict safety checkpoints and non-persistence invariants.

---

## Decisions

We propose establishing this upgraded Swarm Facade with the following attributes:

1. **Facaded Mapping**:
   - `search` maps to `_arif_swarm_orchestrate(intent="Search for: {query}")` — discovery-only, no side effects.
   - `fetch` maps to `_arif_swarm_orchestrate(intent="Fetch and analyze: {url}", mode="fetch", persist=False)` — returns text snippets without persistent ingestion.
2. **Explicit Annotations**: Both tools carry hints (`readOnlyHint: true`, `destructiveHint: false`, `openWorldHint: true`, `idempotentHint: true`) to inform the host that they are safe, non-destructive retrieval tools.
3. **Structured Outputs**: Define a fixed schema that includes a compact, optional `"provenance"` block detailing swarm execution parameters (agents, consensus score, audit reference).

---

## Tool Contracts (The 5-Field Matrix)

### 1. `search` Facade

| Field | Specification |
|---|---|
| **Name** | `search` |
| **Host Contract** | Accepts `query: str`. Optional `session_id`, `actor_id`, and `_envelope`/`client_capabilities` parameters to absorb injected headers and client context. |
| **Internal Route** | `_arif_swarm_orchestrate(intent="Search for: {query}")` routing to Scout + Verifier + Synthesizer. |
| **Annotations** | `readOnlyHint: true`, `destructiveHint: false`, `openWorldHint: true`, `idempotentHint: true` |
| **Output Schema** | Returns `{ "results": [ { "title": "str", "url": "str", "snippet": "str", "source_type": "str" } ], "provenance": { "swarm_mode": "str", "agents_participated": [ "str" ], "consensus_score": 0.0, "epistemic_tier": 0, "audit_ref": "str", "uncertainty_notes": "str" } }` |

---

### 2. `fetch` Facade

| Field | Specification |
|---|---|
| **Name** | `fetch` |
| **Host Contract** | Accepts `url: str`. Optional `session_id`, `actor_id`, and other wrapper metadata. |
| **Internal Route** | `_arif_swarm_orchestrate(intent="Fetch and analyze: {url}", mode="fetch", persist=False)`. |
| **Annotations** | `readOnlyHint: true`, `destructiveHint: false`, `openWorldHint: true`, `idempotentHint: true` |
| **Output Schema** | Returns `{ "canonical_url": "str", "content_blocks": [ "str" ], "fetch_status": "str", "provenance": { "swarm_mode": "str", "agents_participated": [ "str" ], "consensus_score": 0.0, "epistemic_tier": 0, "audit_ref": "str" } }` |

---

## 4. Swarm Orchestrator Design

The internal `_arif_swarm_orchestrate` routine implements:
- **Task Decomposition**: Spawns bounded micro-agents (WebScout for web index query, InternalScout for repo index, Verifier for contradiction check, Synthesizer for consensus).
- **Hard Boundaries**: Under `persist=False`, all temporary files are stored in in-memory scratch space, preventing writes to `/root/VAULT999` while logging the final execution hash.
- **Epistemic Trace**: Computes `consensus_score` and `epistemic_tier` mapping directly to the GEOX-style witness framework.
