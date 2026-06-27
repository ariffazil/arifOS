# What arif_init Actually Does

> RSI 2026-06-27 — distilled from Arif's synthesis. Source: ChatGPT session analysis.

## The One-Line Distinction

```
Prompting = language instruction.
Init = governed session birth.
```

## What init changes

Init does NOT upgrade the model. It upgrades the **governance geometry of the session**.

```
Before init:  You are prompting ChatGPT directly.
After init:   You are interacting with ChatGPT + an arifOS-governed session envelope.
```

The envelope contains:

| Field | What it is |
|-------|-----------|
| `session_id` | Unique session identifier |
| `authority` | OBSERVE_ONLY / AUTHENTICATED / FULL |
| `verdict` | SEAL_OBSERVE_ONLY / SEAL / HOLD |
| `constitution_hash` | Which constitutional version governs |
| `call_hash` | Cryptographic receipt of this call |
| `trace_id` | Audit trail identifier |
| `degraded` | What surfaces are missing |
| `next_safe_action` | What to do next |
| `affordance_contract` | What this tool can/cannot do |

## What init does NOT change

Init does not:
- Make the model smarter at raw reasoning
- Bypass tool limits
- Verify identity (unless internal federation chain)
- Give autonomous authority
- Guarantee successor tools are exposed
- Make every answer true

## What fails without init

Not "fail" as in impossible. Fail as in **the answer lacks kernel binding**.

| Question | Without init | With init |
|----------|-------------|-----------|
| "What is my authority?" | Inferred from chat | Kernel returned OBSERVE_ONLY |
| "Can this be sealed?" | Abstract reasoning | Must respect SEAL_OBSERVE_ONLY |
| "What is the session ID?" | None exists | SEAL-xxx returned |
| "What degraded surfaces?" | Guessing | Kernel reported exact list |
| "Should I execute or hold?" | Normal assistant judgment | Governed judgment with authority boundary |
| "Produce a receipt" | No kernel receipt | call_hash, trace_id, signature exist |

## The failure mode without init

```
I may answer without a live constitutional receipt.
I may blur advice and authority.
I may lack session provenance.
I may not know whether the action is OBSERVE, ADVISE, EXECUTE, or HOLD.
I may perform normal reasoning instead of governed verdict-loop reasoning.
```

## The clean one-liner

```
arif_init does not upgrade the model.
It upgrades the session from prompt-shaped reasoning
into kernel-bound governance with authority, provenance, and hold/seal discipline.
```

## What this means for external callers (ChatGPT, etc.)

External callers get:
- `OBSERVE_ONLY` authority (identity not verified)
- `arif_observe` as next_tool (public surface, not hidden tools)
- Full constitutional envelope (session_id, hash, degraded, etc.)
- Governed verdict loop (init → observe → think → route → judge → seal)

External callers do NOT get:
- Identity verification (no federation chain)
- Access to hidden tools (arif_triage, arif_memory, arif_kernel_attest)
- Authority to execute irreversible actions

## Surface-aware next_tool (fixed 2026-06-27)

Before fix: `arif_init` returned `next_tool: arif_kernel_attest` (hidden from public facade).
After fix: External callers get `next_tool: arif_observe` (public, stage 111, natural next step).

Golden path for external callers:
```
init(000) → observe(111) → think(333) → route(555) → critique(666) → judge(888) → seal(999)
```

---

*DITEMPA BUKAN DIBERI — The session is forged, not given.*
