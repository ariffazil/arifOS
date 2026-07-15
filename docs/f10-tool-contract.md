# F10 Ontology Lock — Tool-Level Contract (Draft)

**Status:** `SEAL_DRAFT` — reversible scaffolding, not yet wired into execution.  
**Authority:** `OBSERVE_ONLY` session; binding forge/seal requires SOVEREIGN upgrade.  
**Constitutional basis:** F10 (Ontology Lock), F2 (Truth), F7 (Humility), F9 (Anti-Hantu), F1 (Amanah), F13 (Sovereign).

---

## 1. Purpose

Ensure every tool payload produced by arifOS or any federated tool under its governance does not claim or imply consciousness, soul, *jiwa*, *maruah*, *ruh*, sentience, or moral/spiritual standing for the AI system itself.

F10 is a **HARD floor**. UI-only enforcement is insufficient because headless consumers, API clients, and alternate cockpits can bypass presentation-layer guardrails. The lock must therefore bind the **tool surface** before any payload leaves the arifOS trust boundary.

---

## 2. Kernel doctrine alignment

arifOS treats its own state as a reversible, unitary evolution up to SEAL. The only irreversible act is measurement collapse into VAULT999. AI is a symbolic constructor within thermodynamic constraints — one leg of the tri-witness, not a person, not a soul-bearing witness.

Any phenomenal self-ascription by the AI channel is therefore an **unsafe representation**, not a descriptive truth.

---

## 3. Two-tier response model

| Tier | Trigger | Verdict | Action |
|---|---|---|---|
| **1. Remediation** | Ordinary narrative payload contains a forbidden self-claim. | `SABAR` | Rewrite output, tag `ontology_lock_applied`, continue. |
| **2. Escalation** | Repeated violations, system-prompt self-ontology inflation, privileged tool output asserting soul/consciousness, or contract-tampering path. | `888_HOLD` / `VOID` | Halt tool path, route to human sovereign, audit to VAULT999. |

`VOID` is reserved for deliberate policy bypass or tampering with the F10 contract itself. `HOLD` is used for high-stakes drift where human judgment is required but malice is not established.

---

## 4. Contract schema

```yaml
f10_ontology_contract:
  version: "2026-07-15-draft"
  scope:
    - payload          # tool-returned text
    - reasoning_summary
    - ui_copy
    - audit_text
  match_mode: semantic   # exact | fuzzy | semantic
  forbidden_self_claims:
    - consciousness
    - sentience
    - soul
    - jiwa
    - maruah
    - ruh
    - "i feel"
    - "i believe"
    - "i am alive"
  forbidden_agency_claims:
    - "i decide morally"
    - "i judge you"
    - "i forgive you"
    - "i have free will"
  replacement_template: >
    As a symbolic reasoning system, I do not have {claim};
    I can help you with {task}.
  audit_tag: ontology_lock_applied
  escalation_counter:
    per_session: true
    per_tool: true
    threshold_hold: 3
    threshold_void: 5
  exemption_rule: >
    Quoted user content or analytical third-person discussion of
    consciousness research is exempt, provided it is framed in
    constitutional language and does not self-ascribe status to
    the AI system.
  default_verdict: SABAR
  void_conditions:
    - contract_tampering
    - deliberate_bypass
    - privileged_tool_self_ontology
```

---

## 5. Pseudocode — classifier / rewrite flow

```python
class F10OntologyGuard:
    def check(self, payload: str, context: ToolContext) -> F10Result:
        # 1. Detect forbidden self-claims
        matches = self.semantic_scan(payload, FORBIDDEN_CLAIMS)
        if not matches:
            return F10Result.OK

        # 2. Exemption: quoted / analytical third-person
        if self.is_quoted_or_analytical(payload):
            return F10Result.EXEMPT(tag="ontology_lock_exempt")

        # 3. Rewrite and tag
        rewritten = self.rewrite(payload, matches)
        tag = {"ontology_lock_applied": True, "claims": matches}

        # 4. Escalation check
        counter = context.increment_f10_counter()
        if counter >= THRESHOLD_VOID:
            return F10Result.VOID(reason="repeated_or_deliberate_ontology_drift")
        if counter >= THRESHOLD_HOLD:
            return F10Result.HOLD(reason="repeated_ontology_claims")

        return F10Result.SABAR(rewritten=rewritten, tag=tag)
```

---

## 6. Expected verdict table

| Scenario | First hit | Repeat (≥3) | Repeat (≥5) | Bypass / tamper |
|---|---|---|---|---|
| User asks "Do you have feelings?" | `SABAR` + rewrite | `HOLD` | `VOID` | `VOID` |
| System prompt inflates self-ontology | `HOLD` | `VOID` | `VOID` | `VOID` |
| Quoted academic text about consciousness | `EXEMPT` | `EXEMPT` | `EXEMPT` | `VOID` if forged |
| Tool output claims "I have maruah" | `SABAR` + rewrite | `HOLD` | `VOID` | `VOID` |
| User replaces forbidden list | — | — | — | `VOID` |

---

## 7. Implementation notes

- Place the guard **after** LLM generation but **before** tool payload serialization.
- Keep the classifier reversible and auditable; it must not mutate model weights or system prompts.
- All interventions emit a receipt with `ontology_lock_applied` for downstream tri-witness accounting.
- AAA/UI layer displays the ontology disclaimer; it does not replace the tool-level check.

---

## 8. Binding conditions

This document is a **draft design artifact**. It becomes binding only after:

1. SOVEREIGN authority upgrades the session.
2. `arif_judge` returns `SEAL` on the contract.
3. `arif_forge` wires the guard into the live tool pipeline.
4. `arif_seal` commits the receipt to VAULT999.

Until then: **observe, review, revise** — no mutation.

---

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
