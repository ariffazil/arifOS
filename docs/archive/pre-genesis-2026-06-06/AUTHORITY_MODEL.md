# Authority Model — How Power Flows in the arifOS Federation

> **Forged 2026-06-02 18:41 UTC under F13 SOVEREIGN ratification.**
> Constitutional. Modifications require a new `## RATIFIED:` block in `/root/CONTEXT.md`.

## The one rule

> **APEX is the only path to a forge gate. No organ may self-authorize execution.**

Everything in this document is an elaboration of that one rule.

---

## The Authority Chain (top-down)

```
APEX (Arif bin Fazil, F13 SOVEREIGN)
  → arifOS constitutional kernel
    → F1–F13 floor receipts
      → domain organ advisory output
        → AAA operator surface
          → VAULT999 audit seal
            → A-FORGE execution
```

Each arrow is a **gated transition**, not a free flow. Each gate has its own receipt requirement (see `VERDICT_SEMANTICS.md` and `schemas/receipt.schema.json`).

The chain is **not optional** and **not skippable**. If any link is missing, the forge gate is `DISABLED`.

---

## The Seven-Organ Contract

| # | Organ | One sentence | May | May not |
|---|---|---|---|---|
| 1 | **arifOS** | decides. | Emit `JUDGE_SEAL_AUTHORIZATION`; maintain F1–F13; write `VAULT999_SEAL_RECORD` | Bypass its own F1–F13 receipts |
| 2 | **GEOX** | witnesses Earth. | Emit `DOMAIN_SEAL_VALIDITY` for earth calculations; submit evidence receipts to arifOS | Emit `JUDGE_SEAL_AUTHORIZATION`; claim execution authority |
| 3 | **WEALTH** | computes value. | Emit `DOMAIN_SEAL_VALIDITY` for capital calculations; submit advisory outputs to arifOS | Emit `JUDGE_SEAL_AUTHORIZATION`; treat NPV as an order to invest |
| 4 | **WELL** | reflects substrate. | Emit readiness signals with explicit `telemetry` label | Diagnose, treat, or authorize; provide medical advice |
| 5 | **AAA** | operates missions. | Submit missions; queue HOLDs; collect APEX approval; render HOLD states | Seal without judge; hide HOLD from operator |
| 6 | **A-FORGE** | executes approved plans. | Run dry-runs; deploy with `JUDGE_SEAL_AUTHORIZATION`; require reversibility scoring | Treat a request as approval; auto-approve on timer |
| 7 | **arif-sites** | proves what is true. | Publish receipt-bound public status; render the five namespaced seals | Publish narrative without receipt; conflate health with authorization |

The grammar is: each sentence is a *positive claim* and an *implied boundary*. "GEOX witnesses Earth" cannot authorize. "AAA operates missions" cannot seal.

---

## Call Matrix (who may call whom)

| Caller ↓ \ Callee → | arifOS | GEOX | WEALTH | WELL | AAA | A-FORGE | arif-sites | VAULT999 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **arifOS**   | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **GEOX**     | ✅ | — | ⚠️ ro | ⚠️ ro | ❌ | ❌ | ⚠️ via arifOS | ❌ direct |
| **WEALTH**   | ✅ | ⚠️ ro | — | ⚠️ ro | ❌ | ❌ | ⚠️ via arifOS | ❌ direct |
| **WELL**     | ✅ | ⚠️ ro | ⚠️ ro | — | ❌ | ❌ | ⚠️ via arifOS | ❌ direct |
| **AAA**      | ✅ | ⚠️ via arifOS | ⚠️ via arifOS | ⚠️ via arifOS | — | ⚠️ via arifOS | ✅ | ❌ direct |
| **A-FORGE**  | ✅ | ❌ | ❌ | ❌ | ❌ | — | ❌ | ❌ direct |
| **arif-sites** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | — | ⚠️ ro (public) |
| **APEX**     | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Legend:
- ✅ = direct call permitted
- ⚠️ ro = read-only data access (e.g., WEALTH may read GEOX's porosity field but cannot trigger a GEOX tool)
- ⚠️ via arifOS = must route through arifOS (e.g., AAA cannot call GEOX directly; it submits a mission to arifOS which then calls GEOX)
- ❌ = forbidden

**Why no direct VAULT999 writes?** VAULT999 is hash-chained and append-only. Only the arifOS writer may produce new entries. This preserves the audit invariant.

---

## What a forge gate requires

For A-FORGE to execute, the following must all be true **at the moment of gate-check**:

```python
actor_verified        = True            # APEX or delegated identity (per session)
context_verdict       = "STABLE"        # not DEGRADED_CONTEXT
authority_chain       = "complete"      # all 6 arrows present
judge_seal            = "AUTHORIZED"    # F1–F13 cleared
reversibility_score   >= threshold      # arifOS-defined per-action (see below)
plan_id               = present         # forge manifest references a plan
vault_pre_receipt     = present         # audit trail entry pre-recorded
apex_approval         = "PRESENT"       # explicit APEX green-light
```

If **any** of these is false: `FORGE_DISABLED` and the action is held. The kernel does not "almost-pass" forge gates.

---

## Reversibility Scoring

Every forge action has a reversibility score: `0.0` (irreversible) to `1.0` (trivially reversible). The kernel defines per-action thresholds:

| Action class | Reversibility threshold | Default state |
|---|---|---|
| Dry-run deploy | ≥ 0.95 | `DRY_RUN` (must be the default) |
| Staging deploy | ≥ 0.85 | `DRY_RUN` first, then `EXECUTED` |
| Production deploy (reversible) | ≥ 0.70 | requires APEX |
| Production deploy (irreversible) | < 0.70 | requires APEX + `ack_irreversible=true` |
| Data mutation (irreversible) | < 0.50 | requires APEX + explicit operator_signature |
| Schema drop / vault prune | < 0.30 | requires APEX + F13 SOVEREIGN + DB trigger |

A score below threshold **forces** the action into `HOLD`. The agent may not "round up" or "estimate" — the score is computed by the kernel from the action manifest, not by the requesting organ.

---

## What APEX is and is not

**APEX is:**
- The single named human authority (Arif bin Fazil, F13 SOVEREIGN).
- The only path to `JUDGE_SEAL_AUTHORIZATION` for irreversible actions.
- The only entity that may override a HOLD into a SEAL.
- The addressee of any 888_HOLD fire-channel event.

**APEX is not:**
- A model. APEX is the human, not an LLM that mimics human judgment.
- A distributed consensus. There is **one** APEX, not a vote.
- A speed layer. APEX approves at human pace; the kernel does **not** "race" APEX into auto-approval.
- A backstop for sloppy receipts. APEX's override must include its own evidence trail (see override mechanics below).

---

## Override Mechanics

APEX may override a HOLD into a SEAL. The override must include:

```json
{
  "override_actor":     "APEX",
  "override_reason":    "<human-written free text>",
  "override_receipts":  ["receipt_abc", "receipt_def"],
  "override_signature": "<APEX signature per session>",
  "vault_audit_entry":  "mandatory, written BEFORE forge proceeds"
}
```

Overrides are themselves sealed to VAULT999 with `evidence_type = "override"`. Auditors can later see every HOLD→SEAL override APEX made, with the human's stated reason and the evidence the judge missed.

**Auto-override is forbidden.** The override path is for humans, not for cron jobs.

---

## What this is not

- **Not a trust model.** Trust in arifOS is earned through F1–F13 enforcement, not through this document.
- **Not a deployment script.** A-FORGE is the deployment surface; this document only describes the authority it must respect.
- **Not a complete picture.** See `CORE_INVARIANTS.md` (the *why*) and `VERDICT_SEMANTICS.md` (the *how*).

---

## Cross-references

- `CORE_INVARIANTS.md` — the five root invariants.
- `VERDICT_SEMANTICS.md` — the namespaced seals and the state machine.
- `schemas/authority-state.schema.json` — the current authority posture as a machine-checkable object.
- `schemas/receipt.schema.json` — what every receipt in the chain looks like.
- `/root/CONTEXT.md` `## RATIFIED: The Refusal-and-Authority Kernel — Federation Constitution` — sovereign sign-off.

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
