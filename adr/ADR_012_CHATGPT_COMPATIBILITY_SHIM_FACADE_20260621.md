# ADR-012: ChatGPT Compatibility Shim Facade
**Status:** `888_HOLD` (PROPOSED / AWAITING SOVEREIGN VETO OR RATIFICATION)
**Owner:** Arif bin Fazil (Sovereign/Architect)
**Date:** 2026-06-21

---

## Context

To achieve non-developer-mode discovery in ChatGPT/OpenAI client runtimes, the arifOS MCP server must register standard `search` and `fetch` tools. 

However, direct mapping to side-effectful or mutating actions (such as `mode="ingest"`) violates the separation between read-only (OBSERVE) actions and persistent/mutating (MUTATE) actions. Furthermore, ChatGPT utilizes tool annotations (`readOnlyHint`, `destructiveHint`, etc.) to structure its confirmation modals and execution policies. 

---

## Decisions

We propose establishing a **read-only, idempotent, host-adaptive facade** that exposes familiar interfaces to the host while routing requests safely underneath.

1. **Facaded Mapping**:
   - `search` maps to `_arif_route(intent="Search for: {query}")` — discovery-only, no side effects.
   - `fetch` maps to `_arif_sense_observe(mode="fetch", url=url, persist=False)` — returns text snippets without persistent ingestion.
2. **Explicit Annotations**: Both tools will carry explicit metadata hints (`readOnlyHint: true`, `destructiveHint: false`, `openWorldHint: true`, `idempotentHint: true`) to inform the host that they are safe, non-destructive, and idempotent retrieval tools.
3. **Structured Outputs**: Define a fixed `outputSchema` to satisfy ChatGPT client expectation of predictable return types.

---

## Tool Contracts (The 5-Field Matrix)

### 1. `search` Facade

| Field | Specification |
|---|---|
| **Name** | `search` |
| **Host Contract** | Accepts `query: str`. Optional `session_id` and `actor_id` parameters to absorb injected headers. |
| **Internal Route** | [arif_route](file:///root/arifOS/arifosmcp/runtime/tools.py#L16208) (or `_arif_route`) with intent: `"Search for: {query}"`. |
| **Annotations** | `readOnlyHint: true`, `destructiveHint: false`, `openWorldHint: true`, `idempotentHint: true` |
| **Output Schema** | Returns `{ "results": [ { "title": "str", "url": "str", "snippet": "str" } ] }` |

---

### 2. `fetch` Facade

| Field | Specification |
|---|---|
| **Name** | `fetch` |
| **Host Contract** | Accepts `url: str`. Optional `session_id` and `actor_id` parameters. |
| **Internal Route** | [arif_sense_observe](file:///root/arifOS/arifosmcp/runtime/tools.py#L5924) (or `_arif_sense_observe`) with mode `"fetch"`, `persist=False`. |
| **Annotations** | `readOnlyHint: true`, `destructiveHint: false`, `openWorldHint: true`, `idempotentHint: true` |
| **Output Schema** | Returns `{ "canonical_url": "str", "content_blocks": [ "str" ], "fetch_status": "str" }` |
