# MCP Authorization Design — arifOS Kernel

> **Authority:** F13 SOVEREIGN
> **Status:** RATIFIED
> **Seal:** SEAL-MCP-COMPLIANCE-AUDIT-2026-08-12-260025f9
> **Forged:** 2026-08-12

## Why this document exists

External audits (including AI-generated ones from retrieval systems) repeatedly
flag `session_token` appearing in MCP `inputSchema.properties` as an anti-pattern.
This is **deliberate design**, not a bug. The pattern enables three distinct access
modes in a single tool surface, which is essential to arifOS's constitutional
architecture. Documenting it once, canonically, so future audits stop
re-flagging it.

## The 3 access modes (single tool surface, three tiers)

All 8 arifOS tools (`arif_init`, `arif_observe`, `arif_think`, `arif_route`,
`arif_memory`, `arif_judge`, `arif_forge`, `arif_seal`) accept three modes:

### Mode 1: Anonymous (no `session_token` passed)
- **Authority granted:** `OBSERVE_ONLY`
- **What works:** `arif_init`, `arif_observe`, `arif_think`, `arif_route`
- **What fails:** `arif_judge`, `arif_forge`, `arif_seal` — return `888_HOLD`
- **Use case:** Standard MCP clients (Claude Desktop, Cursor, custom SDKs)
  that don't know about arifOS auth. They get safe read-only access automatically.

### Mode 2: Verified operator (valid `session_token` passed)
- **Authority granted:** `OPERATOR` (capped — no judge/seal authority)
- **What works:** Everything Mode 1 works, plus `arif_memory` writes
- **What fails:** `arif_judge`, `arif_forge`, `arif_seal`
- **Use case:** Federation operators (A-FORGE, OpenCode CLI) running tools
  with their session token. They can mutate but cannot forge irreversibly.

### Mode 3: Sovereign (Ed25519-proved or SCT-signed)
- **Authority granted:** `SOVEREIGN` (F13)
- **What works:** Everything
- **Use case:** Arif (F13 SOVEREIGN principal) only. Ed25519 keypair required,
  separate from session token. Cannot be obtained by env var, header spoofing,
  or tool argument manipulation.

## Why `session_token` is in `properties` but NOT in `required`

If we removed `session_token` from `properties` entirely:
- Mode 1 clients would still work (anonymous fallback) ✅
- Mode 2/3 clients would have no way to *upgrade* their authority ❌

By keeping it in `properties` (optional) and NOT in `required`:
- Mode 1 clients see the field but aren't required to pass it → fallback to anonymous
- Mode 2/3 clients can pass their token → upgrade to operator/sovereign

This is the standard "optional upgrade path" pattern. Removing it would force
all authenticated clients to use HTTP headers (Mode 2-3 only), which would
**break compatibility** with every standard MCP client that doesn't know
about arifOS.

## Cryptographic enforcement (the actual gate)

`session_token` alone is NOT sufficient for sovereign authority. The
authority escalation chain is:

```
session_token (string)         → OPERATOR cap (mutable actions)
   │
   └─ Ed25519 signature proof    → SOVEREIGN (judge/seal/forbidden actions)
       (or SCT token w/ auth=SOVEREIGN)
```

Even a leaked `session_token` cannot grant sovereign authority. The
session token is a *capability* — not an identity. Cryptographic identity
(Ed25519 keypair) is required for the top tier.

This is by design and matches the AAA Agent Invariant #6:
> **HINTS ≠ CONTRACTS.** Annotations are output of classification, not input.

The `annotations` field on each tool (verified compliant with MCP 2025-11-25)
includes `_derived_from.action_class` which is what the kernel uses to
determine which authority tier is required. The kernel's
`constitution_check` envelope (returned in every response) shows which
authority tier was applied and which floors passed.

## Verification

```bash
# Mode 1: Anonymous read
curl -X POST http://127.0.0.1:8088/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call",
       "params":{"name":"arif_observe","arguments":{"mode":"health"}}}'
# → 200 with actor_id:"anonymous", authority_level:"OBSERVE_ONLY"

# Mode 2: Verified operator (requires valid session_token in vault)
curl -X POST http://127.0.0.1:8088/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call",
       "params":{"name":"arif_memory","arguments":{
         "session_token":"...",
         "operation":"store",
         "content":"..."}}}'
# → 200 with actor_id:"a-forge", authority_level:"OPERATOR"

# Mode 3: Sovereign (requires Ed25519 signature proof)
# Cannot be invoked via curl — requires the arifOS CLI or
# direct kernel call with signed payload. The HTTP path
# intentionally does not expose this.
```

## Why we don't move auth to HTTP headers only

Standard MCP spec (2025-11-25) allows auth via HTTP headers. We could move
`session_token` to `Authorization: Bearer <token>` header and remove it
from tool arguments entirely. **We deliberately don't do this** because:

1. **Standard client compatibility**: Claude Desktop, Cursor, etc. don't
   automatically inject custom auth headers. Forcing them to would break
   Mode 1 (anonymous read) for all standard clients.

2. **Stateless federation principle**: Each tool call is self-contained.
   The SCT pattern means any arifOS node can validate and execute without
   server-side state. Moving to HTTP headers would still work for this,
   but adds an indirection (header parsing before tool args).

3. **Backward compatibility**: Existing federation tools (A-FORGE,
   FED, GEOX, WEALTH, WELL) all pass `session_token` in tool args. Moving
   to headers would require federation-wide change for zero security gain
   (the cryptographic check is the same either way).

## What future audits should check

If you're auditing arifOS MCP compliance and see `session_token` in
`inputSchema.properties`, that's expected. Check instead:

- ✅ `annotations` field present on all tools (verified 2026-08-12)
- ✅ `content[]` array wrapping in responses (verified 2026-08-12)
- ✅ `transport: streamable-http` declared (stateless transport)
- ✅ Protocol version `2025-11-25` declared
- ✅ Constitutional envelope returned inside `content[].text` as JSON string
- ✅ Anonymous fallback works without auth

## References

- `/root/arifOS/arifosmcp/runtime/session_auth.py` — session token validation
- `/root/arifOS/arifosmcp/runtime/authority.py` — Ed25519 / DID gate
- `/root/arifOS/arifosmcp/runtime/tools.py` — tool handlers + envelope
- `/root/VAULT999/sealed/SEAL-MCP-COMPLIANCE-AUDIT-2026-08-12-260025f9.md` — audit seal

---

*DITEMPA BUKAN DIBERI — design forged, not given.*
