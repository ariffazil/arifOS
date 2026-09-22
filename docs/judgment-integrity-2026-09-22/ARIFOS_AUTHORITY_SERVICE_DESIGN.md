# arifOS Authority Service — Design
## 2026-09-22 — from paste 9 (Copilot SEAL with HOLD-CHRON)

---

### Purpose

Replace the implicit "verdict == execute" assumption with an explicit, transaction-bound authority service. Today, `next_safe_action` says "Proceed to arif_seal(...)" after crack #7 was fixed; that's still not authority — it's an instruction to the model. **The model can fabricate it.** Authority must be: actor-bound, transaction-bound, state-bound, scope-bound, fresh, single-use, server-enforced.

This service sits between `arif_judge` and the executor (A-FORGE `arif_forge` / `forge_execute`). It mints a **single-use grant** that the executor must verify before any irreversible mutation.

---

### Architecture (per paste 9)

```
PROPOSE
  ↓
CANONICAL JUDGMENT
  ↓
RECONCILE STATE
  ├── mismatch → HOLD (no grant)
  └── consistent
        ↓
PREPARE TRANSACTION
  ↓
HUMAN WITNESS + INTENT  ← typed phrase + visible state hash + decision_id
  ↓
MINT SINGLE-USE GRANT
  ↓
RECHECK CURRENT STATE  ← at execution time, not at grant time
  ↓
COMMIT
  ↓
RECEIPT + VAULT RECORD
```

Two separate "state hashes" — one at human-witness time, one at execution time — with a recheck between them. **That is the TOCTOU defense.**

---

### The Grant Payload (minimum)

```json
{
  "grant_id": "unique-single-use-id",          // server-generated UUID v7
  "decision_id": "canonical-decision-id",       // from arif_judge
  "actor_id": "verified-human-identity",         // F13 SOVEREIGN or OPERATOR
  "transaction_hash": "sha256 of canonical-transition",  // exact proposed mutation
  "state_hash_witnessed": "sha256 of state at human-witness time",
  "scope": ["operation-name", "target-id"],
  "issued_at": "2026-09-22T16:30:00Z",
  "expires_at": "2026-09-22T16:31:00Z",          // 60-90 seconds, not hours
  "nonce": "single-use-random-value",
  "policy_version": "authority-policy-2026-09-22",
  "signature_chain": ["arifOS-issuer", "human-acknowledger"]
}
```

**Identity chain (8 properties — server checks all 8):**

The minting service is NOT callable by any agent tool — including MCP Apps widgets. Negative test: a widget calling `sendPrompt` to "approve" must fail. Only a direct human call path (the `authority_service.prepare` endpoint) may produce a grant.

**actor-bound = Ed25519 signature**, not a string. The actor signs `(transaction_hash + state_hash + nonce)` using the sovereign signing lane (localhost:18900). The server verifies the signature against the actor's registered public key before binding the grant.

1. `grant_id` not seen before (replay defense)
2. `expires_at > now()` (freshness — 60-90 seconds, not hours)
3. **Ed25519 signature over `(transaction_hash || state_hash || nonce)` is valid against actor's registered public key**
4. `actor_id` has authority for `scope`
5. `transaction_hash` matches what executor is about to do (no scope creep)
6. `state_hash_witnessed` matches current state at execution time (recheck)
7. `policy_version` matches current authority policy
8. Signature chain is intact (issuer → human acknowledger → executor)

**Failure on any one of 8 = reject + log to VAULT999 with reason.**

### Write-Ahead Receipts (not optional)

Three receipts, written in this order:

1. **Intent receipt** — written BEFORE the commit, contains: actor_id, decision_id, transaction_hash, state_hash_witnessed, scope. If the system crashes here, the receipt exists; the commit can be replayed or rejected on next boot.
2. **Commit receipt** — written AFTER the mutation succeeds, contains: intent_receipt_id, post_commit_state_hash, mutation_proof.
3. **Outcome receipt** — written AFTER the vault persists the commit receipt. Contains: commit_receipt_id, vault_entry_id.

**Crash mid-commit**: the intent receipt exists, the commit may have partially completed, but there is NO outcome receipt. On next boot, the reconciler detects "intent exists, outcome missing" → replay or reject based on idempotency_key. **The system never silently loses an irreversible action.**

---

### Execution Order (3 tiers)

#### Tier 1: Truth before interface

1. **Fix crack #6 + #2** — establish one canonical verdict field, add HOLD/INCONSISTENT machine state, disable authorization on disagreement.
2. **Complete Tier 2 contract** — version the decision schema, bind evidence/policy/state hashes, define deterministic reconciliation.

#### Tier 2: Authority before execute UI

1. **Build the authority service** — prepare → review → grant → commit → receipt.
2. **Test negative paths first** — stale state, replayed grant, changed target, changed parameters, expired grant, mismatched verdict, ambiguous actor, duplicate commit.
3. **NO execute control in the UI yet** — only review/witness.

#### Tier 3: Minimum visual surfaces

1. **Consolidate GEOX** — keep seismic, well/depth, map/cross-section witnesses; eliminate overlapping presentation layers.
2. **Build arifOS read-only decision surface** — canonical verdict, effective verdict, evidence, contradictions, state hash, alternatives, reversibility, freshness. Render HOLD/INCONSISTENT prominently.
3. **Enable authority controls only after adversarial tests pass** — UI submits intent, authority service mints grant, A-FORGE independently verifies.
4. **Build WEALTH scenario comparison** — only with proven common axes.
5. **Keep CHRON on HOLD** — verify runtime identity, event schema, outcome source, calibration contract first.

---

### Reconcile Verdict — the executable stop condition

```python
def reconcile_verdict(decision: dict) -> dict:
    """Return reconciled state for the authority service.
    
    NEVER silently normalize a disagreement. Mismatch is HOLD.
    """
    fields = [
        decision.get("decision_id"),
        decision.get("state_hash"),
        decision.get("policy_version"),
        decision.get("evidence_version"),
        decision.get("verdict"),
        decision.get("effective_verdict"),
        decision.get("unresolved_contradictions", []),
        decision.get("expiry"),
        decision.get("freshness"),
    ]
    
    # Collect mismatches against a canonical reference set
    mismatches = []
    for f in fields:
        if f is None:
            mismatches.append("missing_field")
    
    if decision.get("verdict") != decision.get("effective_verdict"):
        mismatches.append("verdict_divergence")
    
    if decision.get("unresolved_contradictions"):
        mismatches.append("unresolved_contradiction")
    
    if mismatches:
        return {
            "status": "HOLD",
            "reason": "INCONSISTENT_STATE",
            "mismatches": mismatches,
            "authority_enabled": False,
            "execution_enabled": False,
            "observed_verdict": decision.get("verdict"),
            "effective_verdict": decision.get("effective_verdict"),
        }
    
    return {
        "status": decision["verdict"],
        "reason": None,
        "mismatches": [],
        "authority_enabled": decision["verdict"] in {"PARTIAL", "SEAL"},
        "execution_enabled": False,  # Always False until grant + recheck
    }
```

**The key rule**: `authority_enabled=True` requires ALL 9 fields consistent AND verdict in {PARTIAL, SEAL} AND no unresolved contradiction. `execution_enabled=False` ALWAYS — that requires a grant + recheck at execution time.

---

### What I Build Next (after this design)

This PR will land the **reconciliation function** as part of crack #6+#2 fix. The authority service (separate service, separate PR) lands after the canonical verdict contract is sealed.

**This PR** = canonical verdict + reconcile function + reconciliation tests + HOLD/INCONSISTENT as machine state.

**Next PR** = authority service (mint grant, verify grant, recheck state, persist receipt).

**PR after that** = arifOS read-only decision surface (no execute button).

---

### Do Not Build (yet)

- Authority control in any UI
- WEALTH scenario comparison dashboard
- CHRON GUI
- Federation-wide dashboard
- "Single pane of glass"
- Typed-phrase confirmation (proves intent only, not authority)
