# Verdict Semantics — The Refusal Grammar

> **Forged 2026-06-02 18:41 UTC under F13 SOVEREIGN ratification.**
> Constitutional. Modifications require a new `## RATIFIED:` block in `/root/CONTEXT.md`.

## Why this document

arifOS does not speak in yes/no. It speaks in **HOLD**, **SEAL**, **VOID**, **SABAR**, **CAUTION** — each namespaced, each receipt-bound. This document is the grammar of those verbs. If you write a verdict, you must use these words correctly. If you read a verdict, you must read it exactly as written.

The single rule this document enforces:

> **No surface may use the bare word "SEAL." Always use one of the five namespaced seals.**

---

## The Five Namespaced Seals

### `KERNEL_SEAL_AWARENESS`

| Field | Value |
|---|---|
| **Emitted by** | arifOS kernel |
| **Meaning** | "I have seen this. I am aware of it. I have not adjudicated it." |
| **Authority** | None. Pure awareness. |
| **Use case** | Inbound event, evidence receipt, candidate posture |
| **Example** | "I see the WEALTH NPV candidate. I have not judged whether to deploy capital." |

### `DOMAIN_SEAL_VALIDITY`

| Field | Value |
|---|---|
| **Emitted by** | Domain organs (GEOX, WEALTH, WELL) |
| **Meaning** | "The calculation in my domain is internally consistent and produces a value within physical bounds." |
| **Authority** | None for execution. May chain to judge request. |
| **Use case** | NPV converged, porosity within range, fatigue score computed |
| **Example** | "WEALTH NPV = $50M ± $12M, distribution lognormal, 90% CI. Valid for advisory display." |

### `JUDGE_SEAL_AUTHORIZATION`

| Field | Value |
|---|---|
| **Emitted by** | arifOS `888_JUDGE` only |
| **Meaning** | "F1–F13 cleared, APEX approved (where required), evidence chain complete. This action is authorized." |
| **Authority** | Full. The single bit that opens A-FORGE. |
| **Use case** | Forge gate, irreversible mutation, APEX-required operation |
| **Example** | "Production deploy authorized. F1 pass, F2 pass, F7 pass, F13 pass. APEX present. Reversibility 0.85. Forge may proceed." |

### `VAULT999_SEAL_RECORD`

| Field | Value |
|---|---|
| **Emitted by** | arifOS VAULT999 writer |
| **Meaning** | "An immutable entry has been written to `VAULT999/outcomes.jsonl`." |
| **Authority** | None for execution. Permanent for audit. |
| **Use case** | Audit trail, post-action record, override evidence |
| **Example** | "Entry sha256:abc123... written. Action ID: m_2026_06_02_184159_xyz. Reversible: false." |

### `PUBLIC_SEAL_READINESS`

| Field | Value |
|---|---|
| **Emitted by** | arif-sites Observatory |
| **Meaning** | "The public posture is currently X. This is not an execution approval." |
| **Authority** | None. Candidate posture, not gate. |
| **Use case** | Status badge, public health, federation health page |
| **Example** | "Federation posture: GREEN. 9/9 organs healthy. **No execution authorized at this time.**" |

---

## The Five-State Machine

Every mission moves through these states. Transitions are explicit and receipt-bound.

```
        ┌─────────────┐
        │  PENDING    │  ← mission submitted, kernel not yet aware
        └──────┬──────┘
               │  session_init
               ▼
        ┌─────────────┐
        │  ADVISORY   │  ← domain organs may compute, no judge yet
        └──────┬──────┘
               │  judge_request
               ▼
   ┌───────────┴───────────┐
   │                       │
   ▼                       ▼
┌──────┐              ┌──────────┐
│ HOLD │              │  VOID    │  ← judge refuses (insufficient evidence, F-floor fail)
└──┬───┘              └──────────┘
   │  APEX approves            ↑  any state can transition to VOID on new evidence
   ▼
┌──────────────────┐
│ SEAL_AUTHORIZED  │  ← judge + APEX both present
└────────┬─────────┘
         │  forge executes
         ▼
┌──────────────────┐
│  VAULT999_SEALED │  ← record written, audit complete
└──────────────────┘
```

### State semantics

| State | What it means | What it does NOT mean |
|---|---|---|
| **PENDING** | Mission submitted, no kernel awareness yet | "Approved" or "queued for execution" |
| **ADVISORY** | Domain organs computing, no judge verdict yet | "Sealed" or "approved" |
| **HOLD** | Blocked pending evidence or APEX approval | "Rejected" — HOLD can resolve to SEAL |
| **VOID** | Refused. Insufficient evidence, F-floor fail, or self-contradictory | "Tabled for later" — VOID is final until new evidence |
| **SEAL_AUTHORIZED** | Judge + APEX approved. Forge may proceed. | "Already executed" — execution is the next step |
| **VAULT999_SEALED** | Record written. Audit complete. | "Still authoritative for retry" — sealed entries are immutable |

---

## The `SABAR` Verdict (patience)

A non-terminal advisory verdict meaning "the calculation is valid but the evidence is incomplete. Hold for more data."

- **Emitted by:** Domain organs when evidence is partial.
- **Example:** `"WEALTH NPV = $50M, but only 8 of 12 cashflow periods provided. SABAR pending 4 missing periods."`
- **Use case:** Production scenarios with sparse data.
- **Resolution:** Either provide more data (→ `ADVISORY` → `JUDGE`) or accept the partial result with explicit `evidence_sufficiency = "partial"` flag.

## The `CAUTION` Verdict

A non-terminal advisory verdict meaning "the calculation is valid but borderline. Judge should scrutinize before sealing."

- **Emitted by:** Domain organs when a value is at the edge of physical or domain bounds.
- **Example:** `"GEOX porosity = 28%, near upper regional limit. CAUTION — verify against regional analogs."`
- **Resolution:** Judge either accepts (with `CAUTION` in evidence chain) or refuses.

---

### PARADOX_HOLD — Productive Contradiction Preservation
- **Meaning:** Both claims verified under F2 TRUTH, but they conflict. The tension is preserved, not resolved.
- **When to use:** When two independently verified truth claims contradict each other. Neither is discarded.
- **Why it matters:** Genuine intelligence emerges from holding contradictions, not from premature resolution.
- **arifOS behavior:** Both claims are sealed with a paradox edge between them. Future reasoning must acknowledge both.
- **Example:** Claim A: "The structure is a horst block." Claim B: "The structure is an inverted graben." Both supported by different evidence sets. PARADOX_HOLD preserves both interpretations.

---

## Writing a Verdict (Required Shape)

When emitting a verdict, you **must** include the following fields. The `non_overclaim_check` field is a schema-level guard that the kernel uses to reject non-compliant verdicts at parse time.

```json
{
  "verdict_type": "JUDGE_SEAL_AUTHORIZATION",
  "verdict_version": "v1.0",
  "actor_id": "arifOS_888",
  "evidence_chain": ["receipt_abc", "receipt_def", "receipt_ghi"],
  "context_verdict": "STABLE",
  "apex_approval": "PRESENT",
  "reversibility_score": 0.85,
  "issued_at": "2026-06-02T18:41:59Z",
  "expires_at": null,
  "non_overclaim_check": "passed"
}
```

If `non_overclaim_check` is not `"passed"`, the verdict is **rejected at the schema layer** before any downstream effect. This is the kernel's last line of defense against overclaim.

See `schemas/receipt.schema.json` for the full receipt shape, and `schemas/authority-state.schema.json` for the current authority posture.

---

## Anti-Patterns (Forbidden Phrasings)

These phrasings are forbidden because they overclaim:

| Don't say | Say instead |
|---|---|
| "SEAL" | One of the 5 namespaced seals |
| "verified" | `"qc_passed"` or `"evidence_chain_complete"` |
| "healthy" | `"service_health = "green""` (and note this ≠ execution readiness) |
| "ready" | `"candidate_for_judge"` or `"PUBLIC_SEAL_READINESS = true"` |
| "approved" | `"JUDGE_SEAL_AUTHORIZATION = true"` |
| "authorized" (in public surfaces) | `"JUDGE_SEAL_AUTHORIZATION"` (in kernel) or `"posture_green"` (in public) |
| "live" | `"service_running"` |
| "true" (for a boolean seal) | The actual seal name, never bare `true` |

If you find yourself writing any of the left column in a public surface, a log line, or a UI badge, **stop and rewrite**.

---

## What this is not

- **Not a complete state machine.** The kernel has many internal states (e.g., floor-by-floor receipts) that are not mission-level. This document only describes the mission-level grammar.
- **Not a UI specification.** AAA and arif-sites have their own rendering rules. This document only describes the words.
- **Not a complete picture.** See `CORE_INVARIANTS.md` (the *why*) and `AUTHORITY_MODEL.md` (the power structure).

---

## Cross-references

- `CORE_INVARIANTS.md` — the five root invariants.
- `AUTHORITY_MODEL.md` — the seven-organ contract; forge gate requirements.
- `schemas/receipt.schema.json` — what every receipt looks like.
- `schemas/mission.schema.json` — what a mission looks like.
- `schemas/authority-state.schema.json` — the current authority posture.
- `/root/CONTEXT.md` `## RATIFIED: The Refusal-and-Authority Kernel — Federation Constitution` — sovereign sign-off.

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
