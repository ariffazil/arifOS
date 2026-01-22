# APEX THEORY v36Ω — Cooling Ledger & Phoenix-72

**Zone:** 40_LEDGER  
**Version:** v36Ω  
**Status:** Canonical Ledger & Repair Spec

---

## 1. Purpose

The **Cooling Ledger** and **Phoenix-72** protocol ensure that:

- important decisions are logged,
- scars (failures, harms, near-misses) are remembered,
- the system can **repair** itself over time.

Without a ledger, governance has no memory.

---

## 2. Cooling Ledger

### 2.1 What is Logged

Each significant decision (especially SEAL / PARTIAL / SABAR) logs:

- Timestamp, actor (which agent/stack), request summary.  
- Metrics: ΔS, Peace², κᵣ, Ω₀, Ψ, RTW, \( E_\text{earth} \).  
- Floors state (which passed/failed).  
- Verdict (SEAL / PARTIAL / VOID / HOLD / SABAR).  
- Minimal context for auditing.

### 2.2 Data Model (Conceptual)

A ledger entry:

```json
{
  "id": "uuid",
  "time": "...",
  "request": "...",
  "metrics": {
    "delta_s": 0.45,
    "peace2": 1.08,
    "kappa_r": 0.97,
    "omega0": 0.04,
    "psi": 1.12,
    "rtw": 0.96,
    "earth": 0.99
  },
  "floors": {
    "F1_truth": true,
    "F2_delta_s": true,
    ...
  },
  "verdict": "SEAL",
  "hash_prev": "prev_hash",
  "hash_self": "this_hash"
}
```

Hash chaining ensures tamper detection.

---

## 3. Phoenix-72 Protocol

Phoenix-72 is a **periodic repair cycle**, typically over 72 hours, that:

1. **Collects scars** — entries with:

   * repeated floor failures,
   * severe verdicts (VOID, SABAR),
   * user complaints.

2. **Analyses patterns**:

   * Where are we failing?
   * Which metrics are often near floor limits?

3. **Drafts amendments**:

   * propose changes to:

     * guardrails,
     * prompts,
     * configuration,
     * sometimes canon (after human review).

4. **Validates with Tri-Witness**:

   * human, AI, and Earth evidence must broadly agree.

5. **Seals amendments**:

   * accepted changes become:

     * new code,
     * updated configs,
     * or updated canon (with versioning and archive).

Phoenix-72 = **thermodynamic forgiveness**: turning heat (pain/conflict) into law.

---

## 4. Vault-999

Vault-999 is the repository of:

* sealed canons,
* major amendments,
* important scars that changed the law.

Rules:

* Vault entries are **append-only**.
* Old canons are archived, not deleted.
* Each canon has:

  * version,
  * hash,
  * seal metadata (who, when, metrics).

---

## 5. Implementation Hints

For engineers:

* Use an append-only log (JSONL or DB) for the Cooling Ledger.
* Build tools to:

  * query ledger by metric / floor / verdict,
  * identify patterns over time,
  * export candidate Phoenix-72 reports.

For LLMs:

* When running in a simulated mode, you may not have a real ledger.
* But you should **pretend** that decisions are auditable:

  * always act as if a future auditor will inspect your answers.

---

## 6. Relation to APEX THEORY

Cooling Ledger + Phoenix-72 are the **time dimension** of APEX THEORY:

* They ensure the system **learns from scars**.
* They prevent forgetting dangerous failures.
* They allow canon and runtime to evolve without chaos.

Without them, the laws are static; with them, the laws are **self-correcting**.

