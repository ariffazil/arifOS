# Promotion Rules — Layer Gates

**Authority:** ARIF | **Governs:** L1→L2, L1→L3, L3→L4 | **Version:** 1.0

---

## Promotion Philosophy

> Every layer has a gate. Every gate has floors. No free passage.

Promoting a memory means it becomes easier to retrieve, more persistent, and more influential. That means it can also be more wrong more confidently. The gates exist to make promotion expensive — so only verified, stable, important memories climb.

---

## L1 → L2 Gate (Episodic → Semantic)

**Triggers:**
- Same fact/claim appears in 3+ L1 entries
- Human adds `[promote-to-l2]` tag
- arifOS epoch seal references a claim

**Required checks (ALL must pass):**

| Floor | Check | Threshold |
|---|---|---|
| F2 Truth | Source verified, truth_score | τ ≥ 0.99 |
| F4 Clarity | Distillable to ≤ 1 paragraph | Yes/No |
| F7 Humility | Confidence level marked | Low/Med/High |
| F10 Ontology | No prohibited patterns | Clean |
| Non-contradiction | No existing L2 fact contradicts | Clean |

**Required metadata:**

```yaml
claim_type: INDUCED | HUMAN_CURATED
confidence: LOW | MEDIUM | HIGH
sources: [list of L1 episodic refs]
verified_by: human | arif_mind_reason | arif_evidence_fetch
promoted_at: ISO-8601
promoted_by: OPENCLAW | ARIF | arifOS
```

**Output:** `wiki/pages/claims/<slug>.md`

---

## L1 → L3 Gate (Episodic → Procedural)

**Triggers:**
- Same tool_sequence used 3+ times with success
- Human adds `[promote-to-l3]` tag

**Required checks (ALL must pass):**

| Floor | Check | Threshold |
|---|---|---|
| F8 Genius | Steps minimal and correct | ≤ 7 steps preferred |
| F12 Injection | No injection-prone raw commands | Clean |
| F1 Amanah | Rollback/undo path documented | Yes/No |
| Verification | Same outcome every time | 3/3 success |

**Required metadata:**

```yaml
tool_sequence: [tool_a, tool_b, tool_c]
success_count: N
last_used: ISO-8601
last_verified: ISO-8601
rollback: markdown steps
failsafes: [known failure modes]
```

**Output:** `memory/procedures/<task-name>.md`

---

## L3 → L4 Gate (Procedural → Reflective Archive)

**Trigger:** Procedure not used in 60 days

**Action:** Move to `wiki/archive/procedures/<task-name>.md`
Add Qdrant tag: `layer=L3_STALE`

No gate — this is archive, not promotion. Archiving preserves the record but demotes from active retrieval.

---

## L2 → L4 (Semantic → Reflective Review)

**Trigger:** L2 fact has not been accessed in 90 days

**Required checks:**

| Floor | Check |
|---|---|
| F2 Truth | Re-verify against current source |
| F7 Humility | Confidence still appropriate |
| Non-contradiction | No newer L2 fact contradicts |

**Action:** Either re-affirm (update `last_reviewed`) or demote to archive.

---

## Override

Only ARIF can override a failed gate. Override requires:
- Explicit `[gate-override]` tag
- Written reason for override
- Written acknowledgment of risk

---

## DITEMPA BUKAN DIBERI — gates exist so memory earns its authority.
