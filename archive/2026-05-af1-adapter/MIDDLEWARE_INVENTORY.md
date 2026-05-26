# Phase 1: Middleware Inventory — arifOS MCP

**Purpose:** Map the repo before changing anything.
**Date:** 2026-04-23
**Rule:** If the agent cannot produce this map, it should not refactor yet.

---

## Middleware / Handler Chain (as-is)

```
HTTP Request
    ↓
1. Starlette CORS Middleware
    ↓
2. GlobalPanicMiddleware — catches kernel panics, returns error JSON
    ↓
3. SSEKeepAliveMiddleware — SSE keepalive heartbeats
    ↓
4. Router dispatch (Starlette)
    → /health    → horizon_health
    → /metadata  → horizon_metadata
    → /tools/*   → FastMCP tool handlers
    → /mcp       → MCP STDIO bridge
    ↓
5. Tool dispatch (FastMCP → CANONICAL_TOOL_HANDLERS)
    → arifos_init, arifos_sense, arifos_mind, arifos_heart,
      arifos_judge, arifos_memory, arifos_vault, arifos_math,
      arifos_kernel, arifos_code, arifos_architect
    ↓
6. ABI v1_0 BaseRequest schema validation (Pydantic)
    → risk_tier, dry_run, allow_execution, request_id
    ↓
7. Tool handler execution
    ↓
8. ResponseEnvelope wrapping
    → ExecutionStatus, GovernanceStatus, ArtifactStatus,
      IdentityContext, ContinuityState, Artifact
```

---

## Existing Contract Schemas

| File | Purpose | AF1 Overlap |
|------|---------|-------------|
| `abi/v1_0.py` | BaseRequest (risk_tier, dry_run, allow_execution, request_id) | PARTIAL — AF1 fields exist but scope, ttl, confirmation gate missing |
| `contracts/verdicts.py` | GovernanceStatus (APPROVED, HOLD, VOID, PARTIAL, PAUSE) | STRONG — AF1 verdict maps to this |
| `contracts/identity.py` | IdentityContext (declared/verified actor, session_id, approval_scope) | STRONG — AF1 operator_id maps here |
| `contracts/artifacts.py` | Artifact, AnswerBasis, Claim | PARTIAL — AF1 envelope enriches this |
| `contracts/envelopes.py` | ResponseEnvelope (all transports: STDIO, HTTPS, SSE) | STRONG — AF1 receipt attaches here |
| `contracts/continuity.py` | ContinuityState | PARTIAL |
| `runtime/sessions.py` | Session registry, _SOVEREIGN_IDENTITY_MAP | STRONG — session binding exists |
| `runtime/arifos_runtime_envelope.py` | AGI Mind Pipeline (sense→mind→heart→judge→forge→vault), Hypothesis, Provenance | STRONG — packet pipeline concept matches |
| `capability_map.py` | CANONICAL_TOOL_HANDLERS (11 tools), LEGACY_TOOL_MAP | STRONG — AF1 tool registry should align here |

---

## Tool Registry (11 Canonical Tools)

| Tool | Handler | Risk (ABI) | Scope | AF1 Classification |
|------|---------|-----------|-------|---------------------|
| arifos_init | init | low | session_init | LOW — read-only setup |
| arifos_sense | sense | low | time_ground, reality_check | LOW |
| arifos_mind | mind | medium | reason_synthesize | MEDIUM |
| arifos_heart | heart | medium | stakeholder_critique | MEDIUM |
| arifos_judge | judge | high | verdict_evaluate, floor_audit | HIGH |
| arifos_memory | memory | medium | memory_read, memory_query | MEDIUM |
| arifos_vault | vault | high | vault_append, vault_seal | HIGH |
| arifos_math | math | low | compute | LOW |
| arifos_kernel | kernel | high | kernel_route, tool_dispatch | HIGH |
| arifos_code | code | medium | code_generate | MEDIUM |
| arifos_architect | architect | medium | registry_query | MEDIUM |

---

## AF1 Gap Analysis

### What Already Exists ✅
- `BaseRequest.risk_tier` — risk classification
- `BaseRequest.dry_run` — dry-run mode
- `BaseRequest.allow_execution` — execution gate
- `GovernanceStatus` — APPROVED/HOLD/VOID verdict
- `IdentityContext` — operator/session binding
- `ResponseEnvelope` — unified response wrapper
- Session registry with `_SOVEREIGN_IDENTITY_MAP`
- Pydantic schema validation at ABI layer

### What AF1 Adds That's Missing ❌
1. **AF1 Gate middleware** — not yet a middleware layer
2. **scope field** — minimal capability list per call (not in BaseRequest)
3. **requires_human_confirmation** — explicit confirmation gate (separate from allow_execution)
4. **input_hash** — hash of inputs for tamper evidence
5. **packet_id** — formal governed packet lifecycle ID
6. **chain_hash** — propagation through pipeline stages
7. **packet state machine** — RAW→FRAMED→SENSED→WITNESSED→ENRICHED→ROUTED→HELD→APPROVED→EXECUTED→COMMITTED→RETURNED
8. **AF1 receipt logging** — every validated call emits a receipt
9. **Tool risk registry with confirmation/null-safety rules**
10. **Bounded field enforcement** — route_target, action, mode enum-only

---

## Phase 2 Plan — Strangler Refactor

### Step 1: Wrap AF1 Gate in front (do NOT delete existing middleware yet)

```
Current:  Request → ABI BaseRequest → Tool Handler → ResponseEnvelope
Target:   Request → AF1 Gate → ABI BaseRequest → Tool Handler → ResponseEnvelope → AF1 Receipt
```

### Step 2: AF1 Gate responsibilities
- Validate AF1 object from request headers or first-class field
- Enforce tool risk map
- Enforce null-safety on sensitive tools
- Enforce confirmation gate for medium/high risk
- Emit AF1 receipt to log
- Pass through to existing middleware (no breaking change)

### Step 3: Migrate one responsibility at a time
1. Tool risk registry → already in af1_validator.py (committed)
2. Confirmation gate → add to AF1 Gate
3. Receipt logging → add to AF1 Gate
4. Bounded field enforcement → add to AF1 Gate
5. Scope enforcement → add to AF1 Gate

### Step 4: Delete old middleware only after parity proven

---

## Existing Files to Keep

- `abi/v1_0.py` — keep, AF1 enriches not replaces
- `contracts/verdicts.py` — keep, GovernanceStatus is canonical
- `contracts/identity.py` — keep, IdentityContext is canonical
- `contracts/envelopes.py` — keep, ResponseEnvelope is canonical
- `runtime/sessions.py` — keep, session registry is canonical
- `capability_map.py` — keep, CANONICAL_TOOL_HANDLERS is canonical

## New Files to Create

- `af1/af1_gate.py` — AF1 Gate middleware (NEW)
- `af1/af1_receipt.py` — AF1 receipt schema and logger (NEW)
- `af1/packet_state.py` — packet state machine enum (NEW)

## Files NOT to Touch This Phase

- `server.py` — wrap not replace
- `runtime/arifos_runtime_envelope.py` — pipeline already defined, AF1 Gate sits in front
- `contracts/artifacts.py` — enrich later

---

*Phase 1 complete. Awaiting sovereign confirmation before Phase 2.*
