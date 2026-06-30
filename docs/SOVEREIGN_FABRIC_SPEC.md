# Sovereign Fabric Specification — arifOS Wajib Layers
> **Ratified:** 2026-06-30 by F13 SOVEREIGN directive "execute the wajib"
> **Status:** IMPLEMENTED (5 of 8 wajib layers built)
> **Location:** `/root/arifOS/arifosmcp/core/`

---

## What This Is

The **Sovereign Fabric** is the governed execution membrane between "agent wants to do something" and "agent is allowed to do it." It consists of 5 wajib (mandatory) protocol layers that every MCP tool call passes through.

**One-line instruction:** `from arifosmcp.core.sovereign_fabric import govern` — then call `govern()` before any tool execution.

---

## The 5 Implemented Wajib Layers

### Layer 6: Agent Authorization Envelope
**File:** `authorization_envelope.py`

Every MCP tool call carries a signed intent packet containing:
- `actor_id` — Who is acting
- `session_id` — Constitutional session from arif_init
- `tool_name` — Which tool is being called
- `action_class` — OBSERVE / REASON / SUGGEST / DRAFT / MUTATE / EXECUTE / SEAL / DELEGATE
- `reversibility` — FULL / PARTIAL / NONE / UNKNOWN
- `blast_radius` — NONE / LOCAL / ORGAN / FEDERATION / EXTERNAL / IRREVERSIBLE
- `evidence_floor` — NONE / INFERRED / OBSERVED / VERIFIED / GROUND_TRUTH
- `confidence` — 0.0–1.0 (F7 cap at 0.90)
- `intent_hash` — SHA-256 tamper detection
- `trace_id` + `span_id` — For reality replay

### Layer 11: Policy Engine
**File:** `policy_engine.py`

Constitutional floors (F1–F13) become executable rules:
- F1 AMANAH: Irreversible requires human ack
- F2 TRUTH: Execute/Seal requires evidence
- F4 CLARITY: Mutate/Execute/Seal requires intent description
- F7 HUMILITY: Confidence capped at 0.90
- F8 LAW: Execute/Mutate requires lease
- F11 AUTH: Actor must be identified
- F13 SOVEREIGN: High-blast irreversible requires sovereign ack

Returns: PROCEED / HOLD / SABAR / VOID with violated floors and next step.

### Layer 12: OpenTelemetry Trace Context
**File:** `trace_context.py`

Every action gets a trace that follows it through the federation:
- `trace_id` — Unique per action chain
- `span_id` — Unique per step in the chain
- `parent_span_id` — Links nested calls
- W3C Trace Context compatible (`traceparent` header)
- JSONL persistence for VAULT999 sealing

### Layer 2: OAuth/OIDC Identity Binding
**File:** `identity_binding.py`

Session identity binding — "who is allowed to touch the tools":
- `IdentityBinding` — actor_id ↔ session_id with auth method
- Auth methods: NONE / SESSION / TOKEN / MTLS / DPOP / DID / SOVEREIGN
- Scope-based access control
- Expiry support
- Registry with verify/revoke

### Layer ∞: Integration Layer
**File:** `sovereign_fabric.py`

One function to rule them all:
```python
from arifosmcp.core.sovereign_fabric import govern

result = govern(
    actor_id="opencode-333-agi",
    session_id="SEAL-abc123",
    tool_name="arif_observe",
    intent="Search for seismic data",
)
if result.proceed:
    # execute
elif result.hold:
    # handle HOLD — result.required_next_step tells you what to do
elif result.void:
    # reject — constitutionally forbidden
```

---

## What's NOT Built Yet (Frontier Layers)

| Layer | Status | Priority |
|-------|--------|----------|
| mTLS/DPoP (Layer 3) | Stub only | Medium — needed for external MCP clients |
| DID Identity (Layer 4) | Not started | Low — internal federation uses session binding |
| Verifiable Credentials (Layer 5) | Not started | Low — authority envelope covers this |
| Event Bus / CloudEvents (Layer 8) | NATS exists but not integrated | Medium |
| Policy Engine OPA/Cedar (Layer 11 advanced) | Python rules only | Low — current rules are sufficient |
| ZKPC (Layer 14) | Frontier | Low |
| P2P/CRDT (Layer 15) | Frontier | Low |

---

## How It Works — The Flow

```
Agent wants to call tool
        │
        ▼
┌─────────────────────┐
│ 1. Create Envelope  │  actor_id, tool, action_class, risk
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. Verify Identity  │  F11: Is this actor who they claim?
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. Policy Engine    │  F1-F13: Is this action constitutional?
└──────────┬──────────┘
           │
     ┌─────┼─────┐
     ▼     ▼     ▼
  PROCEED  HOLD  VOID
     │     │     │
     ▼     ▼     ▼
  Execute  Wait  Reject
     │
     ▼
┌─────────────────────┐
│ 4. Record Trace     │  trace_id + span_id for replay
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 5. VAULT999 Receipt │  If mutation — seal the evidence
└─────────────────────┘
```

---

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `authorization_envelope.py` | ~250 | Layer 6: Agent Authorization Envelope |
| `policy_engine.py` | ~220 | Layer 11: Constitutional Policy Engine |
| `trace_context.py` | ~180 | Layer 12: OpenTelemetry Trace Context |
| `identity_binding.py` | ~140 | Layer 2: OAuth/OIDC Identity Binding |
| `sovereign_fabric.py` | ~230 | Integration: One `govern()` function |

**Total: ~1,020 lines of governed substrate code.**

---

## Next Steps

1. **Wire into arifOS kernel** — Make `arif_init` return a `govern()`-compatible session
2. **Wire into A-FORGE** — Make `forge_execute` pass through `govern()` before execution
3. **Wire into MCP servers** — Each organ's MCP server calls `govern()` on every tool call
4. **Add mTLS/DPoP** — For external MCP clients (ChatGPT, Claude, etc.)
5. **Integrate NATS** — Event bus for cross-organ signals

---

*DITEMPA BUKAN DIBERI — The substrate is forged. The wajib is executed.*
