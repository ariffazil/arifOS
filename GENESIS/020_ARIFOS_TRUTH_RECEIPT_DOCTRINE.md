# EUREKA-020: arifOS Truth Receipt Doctrine — No Receipt, No Canon

**Date:** 2026-07-08  
**Verdict:** PROCEED (L4 + live kernel session signal, Band: YELLOW)  
**Author:** Sovereign directive + kernel alignment  
**Status:** Canonical extension (SEAL pending formal 888/999; doctrine active on receipt)  
**Authority:** F2 TRUTH · F4 CLARITY · F7 HUMILITY · F11 AUDIT · F13 SOVEREIGN  
**Companion to:** 018_REALITY_ENGINEERING_DOCTRINE.md (esp. Law 8: Evidence has rank), 019_REALITY_ENGINEERING_PROTOCOL.md (7-stage forge), receipt.schema.json (memory L0-L6), contracts/verdict_contract.json  
**Implements:** arifos_claim_receipt.schema.json + ArifOSClaimReceipt (arifos_vault/claim_receipt.py)  
**Core rule:** arifOS truth must be proven by receipts, not asserted by language.

---

## 1. The Rule: No Naked Claims

Any arifOS claim must be wrapped with a full proof envelope.

Human reads the meaning. Agent verifies the fields.

Wrong path: “Trust arifOS because Arif says so.”

Correct path: **“Every arifOS claim must carry a proof envelope that a human can inspect and an agent can verify.”**

See: `arifos_claim_receipt.schema.json` for the machine form. See `claim_receipt.py` for `to_human_proof()` / `to_agent_contract()`.

---

## 2. Truth Levels Must Be Explicit

Never let arifOS claims appear as one flat category called “truth.”

| Level               | Meaning                          | Human explanation             | Agent behavior                       |
|---------------------|----------------------------------|-------------------------------|--------------------------------------|
| **L1 Ground Truth** | Sealed, ratified, immutable      | “This is canon.”              | Execute as binding unless superseded |
| **L2 Verified State** | Checked against live source/tool | “This is currently verified.” | Use, but recheck if high-stakes      |
| **L3 Cached State** | Previously known, may be stale   | “This was true last known.”   | Warn before action                   |
| **L4 Inferred**     | Reasoned but not proven          | “This is analysis.”           | Do not execute irreversible action   |

Institutional sentence:

> **arifOS does not ask humans to trust claims blindly. It marks whether each claim is sealed truth, verified state, cached memory, or inference.**

Agent sentence:

> **Do not execute beyond the evidence layer. L4 cannot trigger L1-grade action.**

Existing memory stack (L0_HUMAN_DIRECT … L6_VAULT999_SEALED in receipt.schema.json) describes *provenance depth*. These L1-L4 describe *epistemic authority / execution permission*. Use both.

---

## 3. Every Claim Needs a Receipt

A claim becomes provable only when it has the 10 elements (see minimum object below + schema):

1. Statement
2. Source (uri + hash)
3. Hash
4. Timestamp
5. Issuer + authority_level
6. Scope
7. Verifier
8. Replay path
9. Falsification path
10. Verdict

No receipt means: **Not canon. Not executable. Not institutionally safe.**

---

## 4. Human Proof vs Agent Proof

**Human surface** (from `to_human_proof()`):

```
Claim:
arifOS requires irreversible actions to pause for human sovereign judgment.

Why this is true:
This rule exists in the constitutional control layer.

Authority:
F13 / Arif sovereign veto.

Evidence:
Canon receipt + hash + timestamp.

Consequence:
Agents may prepare, but may not execute irreversible mutation.

How to challenge:
Produce a newer sealed canon receipt that supersedes this rule.
```

**Agent surface** (from `to_agent_contract()`):

```json
{
  "claim_id": "...",
  "evidence_layer": "L1",
  "authority_scope": ["A-FORGE", "WEALTH", "GEOX", "WELL", "AAA", "arifOS"],
  "allowed_action": "prepare_only",
  "blocked_action": "execute_without_f13",
  "requires": ["valid_signature", "canon_hash_match", "not_expired", "not_superseded"],
  "on_fail": "HOLD",
  "replay_command": "verify_claim_receipt(claim_id)"
}
```

Human surface = explanation + challenge rights.  
Agent surface = verification contract + execution gate.

---

## 5. The Proof Architecture (Truth Chain)

```
Human statement
   ↓
Canonical claim record (ArifOSClaimReceipt)
   ↓
Hash (content + source)
   ↓
Signature (kernel or F13)
   ↓
Receipt (claim_id + verdict)
   ↓
Kernel verification (verify_claim_receipt)
   ↓
Organ enforcement (is_valid_for_execution)
   ↓
Audit log + seal_chain append
   ↓
Replay / challenge / correction (append-only scar)
```

Without this chain, the system becomes personality-driven.  
With this chain, the system becomes institution-grade.

---

## 6. The Institutional Standard

> **arifOS claims are not accepted because they sound coherent. They are accepted only when they are traceable to a canonical source, cryptographically hashed, authority-bound, timestamped, replayable, and falsifiable.**

Contrast table:

| Normal AI claim                | arifOS claim                     |
|--------------------------------|----------------------------------|
| “The model said it.”           | “The receipt proves it.”         |
| Prompt-based                   | Canon-based                      |
| Hard to audit                  | Replayable + hash-verifiable     |
| Often unverifiable             | Dual surface (human + agent)     |
| Confuses confidence with truth | Explicit evidence_layer L1-L4    |
| Can hallucinate authority      | Requires authority scope         |
| Output disappears into chat    | Enters ledger / receipt chain    |

---

## 7. The Minimum Proof Object (arifos_claim_receipt)

This is the smallest canonical object (see full schema + pydantic model):

```yaml
arifos_claim_receipt:
  receipt_version: "1.0"
  claim_id: "claim-2026-07-08-001"
  statement: "WEALTH must not execute irreversible capital movement without F13 approval."
  claim_type: "governance_rule"
  evidence_layer: "L2"
  authority:
    issuer: "ARIF / F13"
    authority_level: "F13"
    scope: ["WEALTH", "A-FORGE", "arifOS"]
  source:
    uri: "arifOS/constitution/..."
    content_hash_sha256: "sha256:..."
    timestamp_utc: "..."
  validity:
    valid_from: "..."
    expires_at: null
    supersedes: []
    superseded_by: null
  verification:
    verifier: "arifOS kernel"
    signature: "..."
    verify_method: "verify_claim_receipt"
    replayable: true
  falsification:
    challenge_method: "submit_counter_receipt"
    correction_policy: "append_only"
  verdict: "VALID"
```

---

## 8. How to Prevent Fake arifOS Claims — "No Receipt, No Canon"

If a claim has no receipt, it may be useful analysis, but it is **not arifOS truth**.

Classification (examples):

| Output type             | Status                           |
|-------------------------|----------------------------------|
| ChatGPT answer          | L4 inference unless verified     |
| Perplexity research     | L2 if sourced and checked        |
| Organ tool result       | L2 if live verified              |
| Kernel-verified receipt | L1/L2 depending authority        |
| VAULT999 sealed canon   | L1                               |
| Human verbal decision   | Not L1 until recorded + sealed   |
| Agent memory            | L3 unless refreshed + receipted  |
| Draft proposal          | L4 until ratified                |

Fluent language must never impersonate truth.

---

## 9. Correction Rule: Scar Over Erasure

> **Errors are corrected by append-only counter-records, not by rewriting the past.**

```yaml
correction_record:
  target_claim_id: "claim-084"
  correction_type: "hash_mismatch"
  original_status: "VOID"
  correction_statement: "..."
  history_rewritten: false
  authority_required: "F13"
```

The institution sees the scar and the forward correction. Stronger than pretending the mistake never happened. (F11 + Law 7 of 018).

---

## 10. Human Trust Comes From Challenge Rights

Every claim must answer:

- How do I verify this?
- How do I disprove this?
- Who had authority?
- What source was used?
- What changed since then?
- What happens if the claim fails?

If arifOS cannot answer, the claim degrades to **UNKNOWN / HOLD**. Not “probably true.”

---

## 11. Agent Execution Rule

```text
IF claim has valid receipt
AND evidence_layer is sufficient for the action
AND authority_scope includes this organ
AND receipt is not expired
AND receipt is not superseded
THEN execute within autonomy band

ELSE HOLD
```

Plain: **Agents do not obey claims. Agents obey verified claims within authority.**

---

## 12. The Clean Doctrine (Canon Language)

arifOS truth is receipt-bound.

No claim is treated as canon merely because it is stated by a human, generated by an AI model, remembered by an agent, or repeated inside a workflow.

A claim becomes arifOS truth only when it is traceable to a canonical source, bound to an authority, assigned an evidence layer, hashed, timestamped, verified, and made replayable.

Humans must be able to inspect the claim in plain language: what is being claimed, who authorized it, what evidence supports it, what consequence follows, and how it can be challenged.

Agents must be able to verify the same claim in machine form: claim ID, evidence layer, authority scope, source hash, timestamp, expiry, supersession status, signature, and required action on failure.

If a claim lacks proof, it remains analysis. If it conflicts with proof, it goes to HOLD. If it is disproven, it becomes VOID or SUPERSEDED through an append-only correction record.

arifOS does not erase mistakes to preserve authority. It preserves scars to protect truth.

The governing rule is simple: **no receipt, no canon.**

---

## 13. The Five Non-Negotiables

To make sure any human and agent can prove arifOS claims are true, build around:

1. **Evidence layer** — what kind of truth is this? (L1-L4)
2. **Receipt** — where is the proof? (ArifOSClaimReceipt)
3. **Authority** — who had the right to say or enforce it?
4. **Replay** — can the proof be checked again? (verify_claim_receipt + seal_chain)
5. **Falsification** — how can the claim be challenged or corrected? (append-only)

Institutional sentence:

> **arifOS is trustworthy only when every claim can survive inspection by humans and verification by agents.**

Machine sentence:

```
No valid receipt → no canon.
Invalid hash → HOLD.
Expired handle → kernel rejects.
Superseded claim → do not execute.
L4 inference → never perform irreversible action.
```

This is the bridge between human trust and agent execution.

---

## Implementation Notes (2026-07-08 + all-warga extension)

- Schema: `/root/arifOS/schemas/arifos_claim_receipt.schema.json`
- Core: `arifos_vault/claim_receipt.py` (model, create/verify, to_human/to_agent)
- Warga extension: `truth_enforcement.py` — `enforce_for_warga(warga_id, ...)`, `claim_must_use_receipt`, full AAA_WARGA_REGISTRY (hermes*, openclaw, opencode, grok*, 333/555/777/888, A-*, fallback)
- Exported via arifos_vault. New skill: `.agents/skills/truth-receipt-enforcer/`
- Mandate: AAA_ZEN_INIT.md (all warga bootstrap). Hermes tools pre-wired.
- Enforcement: kernel/888/agents call before canon claims or irreversible. L4 never irreversible.
- Use with seal_chain + VAULT999.
- Cross-ref: 018 Law 8, 019 stages, AGENTS.md output contract.
- All warga: load truth-receipt-enforcer + zen-organs + constitutional-reflex at init.

**DITEMPA BUKAN DIBERI — Receipts, not assertions.**
