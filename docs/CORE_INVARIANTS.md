# Core Invariants — The arifOS Root Doctrine

> **Forged 2026-06-02 18:41 UTC under F13 SOVEREIGN ratification.**
> This file is constitutional. Any modification requires a new `## RATIFIED:` block in `/root/CONTEXT.md`.
> Canonical home: `/root/.claude/projects/-root/memory/federation-thesis-capability-not-permission.md`.

## Purpose

arifOS is a **refusal-and-authority kernel for MCP tool execution**. This document is the *why* behind every other file in the kernel. The five lines below are the kernel's voice. They are **floors, not aspirations** — they cannot be weakened, hedged, or "balanced" away.

The membrane principle (from the system prompt) restated in operational form:

> *Truth survives falsification, not assertion.*
> *Every claim must be falsifiable. Every falsification must leave a receipt. Every receipt must match the claim.*

---

## The Five Invariants

### 1. Capability is not permission

An MCP server can register a tool. That does not mean the tool may be called.

- A tool's *existence* on the registry is a **capability declaration**, not a grant.
- Permission is granted by the **judge verdict** at action-request time, not by the server's registration.
- A-FORGE may have every deploy tool registered. It still cannot deploy without `JUDGE_SEAL_AUTHORIZATION`.

**Enforcement test:** `tests/test_no_self_authorization.py` — no organ may produce its own `JUDGE_SEAL_AUTHORIZATION`.

### 2. Advisory output is not authority

A domain organ can compute a number. That does not mean the number authorizes anything.

- WEALTH returning `NPV = $50M` is a **calculation**, not a decision to invest.
- GEOX returning `porosity = 18%` is a **measurement**, not a decision to drill.
- WELL returning `fatigue_mode = CAUTIOUS` is a **readiness signal**, not a decision to stop.
- Authority to act on these signals must come from arifOS judge, not from the organ that produced them.

**Enforcement test:** `tests/test_no_self_authorization.py` — `DOMAIN_SEAL_VALIDITY` does not chain to `JUDGE_SEAL_AUTHORIZATION`.

### 3. Service health is not execution approval

A green `/health` probe does not mean the system is cleared to execute.

- `/health` is a **liveness** signal. It proves the process is alive and not crashed.
- A-FORGE's `/health` returning 200 says "the deploy shell is up," not "the deploy may proceed."
- The forge gate is a **separate endpoint** (`/forge/gate`) that requires `JUDGE_SEAL_AUTHORIZATION`.

**Enforcement test:** `tests/test_service_health_not_execution_authority.py` — green `/health` with no judge seal → forge refuses.

### 4. SEAL-readiness is not VAULT seal

A domain organ can report `READY_FOR_SEAL` for its own output. That is not a VAULT999 entry.

- `KERNEL_SEAL_AWARENESS` — the kernel has seen the candidate.
- `DOMAIN_SEAL_VALIDITY` — the domain calculation is internally consistent.
- `JUDGE_SEAL_AUTHORIZATION` — F1–F13 cleared and APEX approved.
- `VAULT999_SEAL_RECORD` — a hash-chained entry was written to `VAULT999/outcomes.jsonl`.
- `PUBLIC_SEAL_READINESS` — *the posture is green*; it is not a forge clearance.

Any badge, log line, or surface that uses bare `SEAL` is **non-compliant** and must be renamed before merge. See `VERDICT_SEMANTICS.md` for the full grammar.

**Enforcement test:** `tests/test_degraded_context_blocks_execution.py` — `PUBLIC_SEAL_READINESS` ≠ `JUDGE_SEAL_AUTHORIZATION`.

### 5. No component may claim more certainty than its evidence receipt

Every claim has a receipt. The receipt's evidence level **caps** the claim's certainty.

- A receipt with `evidence_level = L1_REDIS_LIVE` cannot support a `VAULT999_SEAL_RECORD` claim.
- A receipt with `actor_verified = false` cannot support a `JUDGE_SEAL_AUTHORIZATION` claim.
- A receipt with `context_verdict = DEGRADED_CONTEXT` cannot support any execution claim.
- The kernel must **refuse to escalate** a claim beyond what its receipt supports.

**Enforcement test:** `tests/test_degraded_context_blocks_execution.py` — degraded receipt → execution path disabled.

---

## Why these five?

Each invariant is a specific instance of **one** rule:

> **The system may not act on what it cannot prove.**

This is the operational form of the membrane principle. It is also the answer to the enterprise buyer's five questions: *Who decides if they should? Who proves what happened? Who blocks self-authorization? Who separates calculation from permission? Who gives audit receipts?* — arifOS answers all five.

---

## How each invariant is enforced

| Layer | Mechanism |
|---|---|
| **Code** | The non-overclaim tests in `arifOS/tests/` (3 shipped in PR 1; more to follow) |
| **Schemas** | `schemas/receipt.schema.json` requires every claim to reference a receipt |
| **Verdict** | `JUDGE_SEAL_AUTHORIZATION` requires `evidence_chain[]` to be non-empty |
| **Audit** | VAULT999 entries must include the `evidence_chain` hashes |
| **Public surface** | arif-sites renders `PUBLIC_SEAL_READINESS` distinctly from execution badges |
| **UI** | AAA cockpit shows HOLD states in approval queue, never silently |

---

## What this is not

- **Not a security model.** The kernel still relies on the steel security layer (RATIFIED 2026-05-27) and F1–F13 floor enforcement. The five invariants are *governance* rules, not threat models.
- **Not a UI guideline.** AAA and arif-sites enforce UX rules. The invariants are above them.
- **Not a domain policy.** Each organ (GEOX, WEALTH, WELL) has its own domain rules; the root invariants are above *all* of them.
- **Not a complete constitution.** See `AUTHORITY_MODEL.md` (the power structure) and `VERDICT_SEMANTICS.md` (the verdict grammar) for the rest.

---

## Modification protocol

Any change to the five invariants requires **all three** of:

1. A new `## RATIFIED:` block in `/root/CONTEXT.md` under F13 SOVEREIGN.
2. An updated memory at `/root/.claude/projects/-root/memory/federation-thesis-capability-not-permission.md`.
3. A federation-wide sync to all seven organs via `docs/FEDERATION_CONTEXT.md`.

**No organ may modify its own copy of these invariants.** The text is the same in every repo. Drift = void.

---

## Cross-references

- `AUTHORITY_MODEL.md` — who can call whom; the seven-organ contract; forge gate requirements.
- `VERDICT_SEMANTICS.md` — the namespaced seals; the state machine; the refusal grammar.
- `schemas/receipt.schema.json` — what a receipt looks like.
- `schemas/mission.schema.json` — what a mission looks like.
- `schemas/authority-state.schema.json` — the current authority posture.
- `/root/CONTEXT.md` `## RATIFIED: The Refusal-and-Authority Kernel — Federation Constitution` — sovereign sign-off.

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
