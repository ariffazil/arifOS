# AGENT_BOOTSTRAP.md — Machine Contract

arifOS MCP server machine-readable contract. This file answers: what endpoint, what protocol, what verbs, what rules.

## Endpoint

```
URL: https://mcp.arif-fazil.com/mcp
Protocol: MCP 2026-07-28 (stateless-first)
Fallback: MCP 2025-11-25 (stateful, legacy)
Transport: HTTP POST + SSE (text/event-stream)
```

## Discovery

```
MCP tools/list    → 8 canonical verbs
MCP resources/list → 34 resources
MCP prompts/list  → 13 prompts
Health endpoint   → GET /health
```

Machine-readable surfaces:
```
/.well-known/mcp/server.json  — MCP server metadata
/llms.txt                     — LLM-readable summary
/llms-full.txt                — Full LLM-readable docs
/tools                        — Public tool inventory
/tools.json                   — Tool inventory (JSON)
```

## Session lifecycle

```
1. arif_init          → bind session, receive session_token (SCT)
2. [governed verbs]   → pass session_token on every call
3. arif_seal          → close session, seal to VAULT999
```

No session = no mutation. `arif_init` is the required first verb.

## The 8 canonical verbs

```
arif_init    (000) — Session ignition. Required first.
arif_observe (111) — Sense reality. Evidence in, labels out.
arif_think   (333) — Structured reasoning. Confidence capped.
arif_route   (444) — Dispatch to organ. Pure discovery.
arif_memory  (555) — Governed memory (L1–L6). Writes are mutations.
arif_judge   (666) — Constitutional verdict.
arif_forge   (777) — Governed execution. Post-SEAL only.
arif_seal    (999) — VAULT999 immutable append.
```

## Access classification

```
discoverable: all 8 verbs (listed on public surface)
anonymous:    arif_init only (no session needed to bind)
session-bound: arif_observe, arif_think, arif_route, arif_memory
authenticated: arif_judge, arif_forge, arif_seal
```

## Verdict semantics

```
SEAL  — Authorized. Execute, then seal receipt.
HOLD  — Paused. Insufficient evidence or human approval required.
SABAR — Partial authorization. Proceed cautiously.
VOID  — Blocked. Hard floor violation.
```

Verdict class `888_HOLD` specifically indicates human approval gate (F13 territory).

## Constitutional floors

13 floors (F1–F13) evaluated on every governed action:
- F1 AMANAH: reversible-first
- F2 TRUTH: evidence required
- F3 TRI-WITNESS: multi-perspective verification
- F4 CLARITY: entropy reduction
- F5 PEACE²: non-destructive power
- F6 EMPATHY: protect the vulnerable
- F7 HUMILITY: confidence cap 0.90
- F8 GENIUS: reasoning quality gate
- F9 ANTIHANTU: no deception
- F10 ONTOLOGY: AI-only ontology
- F11 AUDITABILITY: every decision logged
- F12 RESILIENCE: injection defense
- F13 SOVEREIGN: human veto final

Full definitions: `GENESIS/FLOOR_TABLE.json`

## Error and retry rules

```
HOLD → do NOT retry with the same payload.
       Improve evidence or request human approval.
       Retry with identical payload is a floor violation (F2).

VOID → action is permanently blocked for this session.
       Do not retry. Start a new session if context changed.

SEAL → proceed with execution, then call arif_seal.

SABAR → proceed cautiously. Partial authorization granted.
        Monitor for degradation.
```

## Idempotency

`arif_init` accepts `idempotency_key` for safe retries.
Other verbs: idempotency varies by mode. Check tool schema.

## Irreversible actions

Any verb that would produce an irreversible effect requires:
1. `ack_irreversible: true` in the request
2. `arif_judge` returning `SEAL` (not HOLD or SABAR)
3. F13 human acknowledgment (for T3 actions)

## Schema URLs

```
Tool schemas:      via MCP tools/list
Resource schemas:  via MCP resources/list
Floor table:       GENESIS/FLOOR_TABLE.json
Tools SOT:         tools_sot.yaml
Constitution:      GENESIS/000_KERNEL_CANON.md
```

## Protocol versions supported

```
MCP 2026-07-28 (stateless, preferred)
MCP 2025-11-25 (stateful, legacy)
```

## Source of truth

Canonical stage assignments: `tools_sot.yaml` → sourced from `arifosmcp/constitutional_map.py`
If this file and the code disagree, code wins.
If prose and the code disagree, code wins.
