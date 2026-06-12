# arifOS Context Engine — Audit Policy v1

> **Authority:** F13 SOVEREIGN · **Status:** RATIFIED 2026-06-12 (provisional, F13 ed25519 pending)  
> **Source of truth:** This document. The code in `arifosmcp/runtime/context_audit.py` references this; the string `context_policy.v1` is the version identifier.

## Root Invariant

```
Retrieval is observation.
Compaction is transformation.
Canonical memory mutation is state mutation.
```

Therefore:

```
observe   → trace
transform → seal
mutate    → hold
```

100% of context decisions are **traceable**.  
Not 100% of context decisions are **sealed** — selective sealing prevents VAULT999 obesity while preserving reconstructability.

## The 4 Audit Modes

| Mode | Storage | When | Reversibility |
|------|---------|------|---------------|
| **TRACE** | L2 session log (in-memory + L4 ephemeral) | Routine retrieval that informs a response but doesn't change memory | Reversible — L2 can be GC'd |
| **DIGEST** | Batched hash to VAULT999 at session close or every N events | Normal context packets that were used in final answer | Reversible — digest can be re-computed from session log |
| **SEAL** | Immediate VAULT999 append | Compaction, high-risk retrieval, canonical memory writes | One-way — hash chain extends |
| **HOLD** | Requires F13 ed25519 signature via `arif_vault_seal` with `ack_irreversible=true` | Canonical overwrite, memory deletion, VAULT999 mutation, policy change, threshold change, summarizer-prompt change, authority upgrade | One-way — full sovereign approval |

## Audit Mode Assignment

| Event | Mode |
|-------|------|
| Routine vector retrieval (Qdrant similarity search) | TRACE |
| Routine retrieval used in final answer | DIGEST |
| Retrieval involving private memory (WELL substrate, identity, F13 territory) | SEAL |
| Retrieval involving financial decisions (WEALTH) | SEAL |
| Retrieval involving legal/canonical claims (GEOX material claims) | SEAL |
| Retrieval involving user commitments (open loops, promises) | SEAL |
| Retrieval involving F8/F13 workflow context | SEAL |
| Retrieval involving external action planning | SEAL |
| Prompt compaction (Phase 2, off by default) | SEAL |
| Summary replacing working context (Phase 4, off by default) | SEAL |
| Canonical memory write (L4/L5) | SEAL or HOLD (depends on blast radius) |
| Memory deletion (any tier) | HOLD |
| VAULT999 mutation | HOLD |
| Context policy change (this document) | SEAL |
| Pressure threshold change | SEAL |
| LLM summarizer prompt change | SEAL |
| Relevance scoring policy change | SEAL |
| Authority boundary change (what's L2 vs L4 vs L6) | HOLD |

## SEAL Manifest Schema (Compaction)

Every SEAL for a compaction event must include:

```json
{
  "event_type": "CONTEXT_COMPACTION",
  "policy_version": "context_policy.v1",
  "session_id": "<canonical session id>",
  "actor_id": "<sovereign or claimed>",
  "ts_utc": "<ISO 8601 UTC>",
  "pressure_before": 0.88,
  "pressure_after": 0.52,
  "pressure_band_before": "COMPACT",
  "pressure_band_after": "WARN",
  "raw_context_hash": "<sha256 of pre-compaction context>",
  "summary_hash": "<sha256 of post-compaction summary>",
  "source_pointers": ["L2:redis:session:abc", "L4:postgres:memory_records:..."],
  "dropped_segments": [
    {
      "reason": "low_relevance",
      "hash": "<sha256 of dropped segment>",
      "tier_origin": "L2|L3|L4|L5",
      "reversible_pointer": "<where to re-fetch if needed>"
    }
  ],
  "kept_segments": [
    {
      "type": "recent_turns|retrieved_memory|system",
      "hash": "<sha256>",
      "tier_origin": "L2|L3|L4",
      "priority": 100
    }
  ],
  "summarizer": "deterministic|llm:v1",
  "verifier": "deterministic_hash_check|llm:verify:v1",
  "reversible": true,
  "constitutional_compliance": {
    "F1_amanah": "raw preserved in L2/L4/L6; pointer in seal",
    "F2_truth": "summary marked as compression, not truth",
    "F4_clarity": "delta_s measured before/after",
    "F8_genius": "policy version pinned",
    "F11_audit": "this seal IS the audit",
    "F13_sovereign": "raw canonical mutation requires HOLD"
  }
}
```

**Do NOT seal full raw text** unless required. Seal hashes + pointers.

## SEAL Manifest Schema (High-Risk Retrieval)

```json
{
  "event_type": "CONTEXT_RETRIEVAL_HIGH_RISK",
  "policy_version": "context_policy.v1",
  "session_id": "<id>",
  "ts_utc": "<ISO 8601>",
  "query_hash": "<sha256 of query>",
  "retrieved_memory_ids": ["L4:...", "L5:..."],
  "selected_ids": ["L4:..."],
  "dropped_count": 7,
  "risk_class": "private|financial|legal|identity|commitment|external_action",
  "rationale": "why this retrieval was high-risk",
  "actor_id": "<who triggered>",
  "reversible": true
}
```

## TRACE Schema (Routine Retrieval, in-memory)

```json
{
  "event_type": "CONTEXT_RETRIEVAL_TRACE",
  "policy_version": "context_policy.v1",
  "session_id": "<id>",
  "ts_utc": "<ISO 8601>",
  "query_hash": "<sha256>",
  "retrieved_memory_ids": ["L3:..."],
  "selected_ids": ["L3:..."],
  "dropped_count": 3,
  "tier_origin": "L3",
  "ttl_seconds": 3600
}
```

## DIGEST Schema (Batched, Periodic Flush)

```json
{
  "event_type": "CONTEXT_DIGEST",
  "policy_version": "context_policy.v1",
  "session_id": "<id>",
  "ts_utc": "<ISO 8601>",
  "window_start": "<ISO 8601>",
  "window_end": "<ISO 8601>",
  "n_traces": 47,
  "trace_digest": "<sha256 of concatenated trace_hashes>",
  "first_trace_hash": "...",
  "last_trace_hash": "..."
}
```

## F-Boundary Map

| Audit operation | Floor | Sovereignty |
|-----------------|-------|-------------|
| Writing TRACE to L2 | F1 AMANAH (reversible) | Agent |
| Writing DIGEST to VAULT999 | F11 AUDITABILITY | Agent (rate-limited) |
| Writing SEAL to VAULT999 (compaction) | F1 + F11 | Agent IF policy_version pinned; HOLD if policy changed |
| Writing SEAL to VAULT999 (high-risk retrieval) | F11 | Agent |
| Writing HOLD to VAULT999 (canonical mutation) | F13 | Sovereign only |
| Changing this policy | F8 GENIUS | F13 ed25519 signature required |
| Changing pressure thresholds | F8 GENIUS | F13 ed25519 signature required |
| Changing summarizer prompt | F8 + F9 | F13 ed25519 signature required |

## Reversibility Test

For every context operation, the agent must be able to answer:

> "Can I reconstruct the pre-operation state from post-operation state plus audit log?"

If NO → operation is HOLD territory.  
If YES → operation is SEAL-able.  
If obviously recoverable (e.g. vector search is in L3, can be re-run) → TRACE is sufficient.

## What is NOT a context operation

- Normal LLM inference (model call) — audited via existing Langfuse, not via context_audit
- Tool execution (e.g. arif_forge_execute) — audited via VAULT999 + arif_vault_seal, not via context_audit
- System calls (Caddy restart, systemctl, etc.) — out of scope
- User input — out of scope

The context audit covers **only** the operations of the context engine: retrieval, compaction, memory shaping, and policy application.

## Versioning

This is `context_policy.v1`. Any change increments to `v1.1`, `v2`, etc. and requires:
1. New seal in VAULT999 referencing the old version
2. Reason for change
3. F13 ed25519 signature on the new doc

The code's `POLICY_VERSION` constant must match the canonical version string. Mismatch = circuit breaker (refuse operation until aligned).

---

**DITEMPA BUKAN DIBERI** — context is forged, not given, and every context decision leaves a trace.

**Provisional, awaiting F13 ed25519 signature to upgrade to CANON.**
