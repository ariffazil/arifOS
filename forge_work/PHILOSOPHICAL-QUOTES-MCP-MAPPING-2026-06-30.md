# Philosophical Quotes MCP Mapping — arifOS

**Date:** 2026-06-30
**Verdict:** YES, but quotes must be metadata, not reasoning engine
**Evidence:** L2 from MCP llms.txt, L4 architecture synthesis
**Band:** YELLOW

## Executive Summary

Philosophical quotes in arifOS are wired to MCP as **non-contaminating metadata**.
They ride in the `philosophical_anchor` envelope for human resonance.
They NEVER enter reasoning, logic, 888_JUDGE deliberation, or VAULT999 sealing criteria.

## Current Quote System Architecture

### Quote Sources

| Source | Count | Location | Purpose |
|--------|-------|----------|---------|
| `_WISDOM_QUOTES` | 40 entries | `arifosmcp/runtime/tools.py:4586` | Tool-specific quotes (3 per tool) |
| `QUOTES_CANON.md` | 33 quotes | `arifosmcp/core/QUOTES_CANON.md` | Canonical reference document |
| `unified_quotes_registry.json` | 132 quotes | `data/unified_quotes_registry.json` | Full quote database with dimensions |
| `philosophy_registry.py` | Loader | `arifosmcp/runtime/philosophy_registry.py` | Context-aware quote selection |

### Tool-Quote Mapping

```
arif_session_init      → 3 quotes (Marcus Aurelius, JFK, Socrates)
arif_sense_observe     → 3 quotes (Krishnamurti, Huxley x2)
arif_evidence_fetch    → 3 quotes (Hume, Huxley, Bacon)
arif_mind_reason       → 3 quotes (Fitzgerald, Mauriac, Plato)
arif_kernel_route      → 3 quotes (Sophocles, Descartes, Emerson)
arif_reply_compose     → 3 quotes (Goethe, MLK Jr., Russell)
arif_memory_recall     → 3 quotes (Emerson x3)
arif_heart_critique    → 3 quotes (Proverbs, Huxley x2)
arif_gateway_connect   → 3 quotes (Emerson, Pericles, Marcus Aurelius)
arif_ops_measure       → 3 quotes (Huxley, Delphi, Einstein)
arif_judge_deliberate  → 3 quotes (Quinet, Russell, Sowell)
arif_vault_seal        → 3 quotes (Kant, Pericles, Huxley)
arif_forge_execute     → 3 quotes (Helvétius, Buffon, Curie)
```

**Total:** 13 tools × 3 quotes = 39 entries (canonical count: 33)

### Quote Injection Flow

```
Tool Call → tools.py → _wrap_call()
    ↓
philosophy_registry.inject_philosophy(envelope)
    ↓
lookup_tool_quote(tool_name, context)
    ↓
compute_match_score(quote, context_keywords)
    ↓
Quote metadata → envelope.philosophy
    ↓
Output envelope (quotes ride as metadata, NOT reasoning)
```

## Implemented Invariants (I1-I8)

### I1: Reversibility
**Rule:** Thinking is reversible. Execution is not.
**Enforcement:** `arif_think` may advise, compare, critique, and hypothesize, but must not execute, seal, delete, deploy, or approve.

### I2: Authority Separation
**Rule:** Mind does not judge. Judge does not execute. Vault does not think.
**Mapping:**
- `arif_think` → reason
- `arif_judge` → verdict
- `arif_vault` → seal
- `arif_forge` → execute

### I3: Evidence Honesty
**Rule:** No evidence, no verified claim.
**Allowed without evidence:** conceptual reasoning, hypothesis, architecture design, critique
**Forbidden without evidence:** verified fact, final verdict, seal, execution approval

### I4: Entropy Minimization
**Rule:** Return only what changes the decision.
**Remove by default:** decorative quotes, nine_signal, philosophical_anchor, full affordance contract, stage theater

### I5: Lifecycle Discipline
**Rule:** Respect initialize → initialized → tools/list → tools/call → result.
**Meaning:** MCP is protocol flow, not magic plugin access.

### I6: Schema Truth
**Rule:** If the schema lies, the tool lies.
**Meaning:** Inputs, outputs, enums, errors, and degraded states must be explicit.

### I7: Degraded Is Not Success
**Rule:** Empty HOLD is DEGRADED, not OK.
**Meaning:** No useful reasoning means no success claim.

### I8: Quotes Do Not Reason
**Rule:** A quote can anchor meaning, but cannot carry proof.
**Meaning:** Quotes are metadata for human resonance, not reasoning inputs.

## Entropy Policy

### Lower Entropy When:
- Answer becomes shorter
- Uncertainty is clearer
- Next action is obvious
- False authority is removed
- Reversible vs irreversible is separated

### Higher Entropy When:
- Wrapper grows
- Quote appears but changes nothing
- Confidence drops without reason
- Tool returns SEAL for advisory thinking
- JSON contains more ceremony than answer

**Operational Test:** If output does not reduce confusion, arif_think failed.

## Reality Stack

| Layer | Name | Confidence Cap | Source |
|-------|------|----------------|--------|
| L1 | Ground Truth | 1.0 | Sealed, ratified, immutable receipt |
| L2 | Verified State | 0.90 | Live tool result, source, log, probe |
| L3 | Cached State | 0.75 | Memory or prior session |
| L4 | Inferred | 0.60 | Reasoning only |

**Default for arif_think:** L4_INFERRED
**Upgrade path:** Only with attached evidence, logs, source text, or tool results

## Math Axioms

### Confidence
```
C = f(E, R, U, X)
C = 0.4*E + 0.3*R - 0.2*U - 0.1*X
```
Where: E=evidence strength, R=reasoning coherence, U=uncertainty penalty, X=execution risk penalty

### Entropy
```
ΔS = S_after - S_before
Rule: Prefer ΔS < 0
```

### Risk
```
Risk = Impact × Irreversibility × Uncertainty
Rule: High risk routes to guarded lane
```

### Confidence Cap
```
C_final <= C_evidence
Rule: Verified claims cannot exceed evidence quality
```

### Path Selection
```
BestPath = argmax(clarity + reversibility + evidence_fit - risk)
```

## Symbolic Code

### Verdict Symbols
- `THINK` — advisory reasoning
- `HOLD` — cannot proceed safely or honestly
- `VOID` — request or output violates boundary
- `ADVISORY` — useful but non-binding reasoning
- `DEGRADED` — tool returned but did not complete useful cognition
- `SEAL` — owner: VAULT999 / judge path only — forbidden in arif_think

**Most Important Rule:** THINK ≠ JUDGE ≠ SEAL ≠ EXECUTE

### Linguistic Labels
- `CLAIM` — supported by evidence
- `HYPOTHESIS` — possible explanation
- `INFERENCE` — reasoned from available input
- `UNKNOWN` — not known
- `ASSUMPTION` — accepted temporarily
- `NEXT_ACTION` — one reversible move

### Banned Default Language
- `SEAL` — unless actual seal path occurred
- `VERIFIED_FACT` — without evidence
- `SOVEREIGN` — unless authority context matters
- Decorative quotes
- Philosophical anchors
- Fake precision complexity scores

## Quote Metadata Schema

```json
{
  "id": "Q01",
  "quote": "",
  "author": "",
  "function": "humility | uncertainty | reversibility | evidence | restraint | courage",
  "use_when": [],
  "must_not_be_used_when": []
}
```

## Quote Placement Rules

```yaml
philosophical_quotes:
  allowed: true
  count: 33
  storage: "resource or metadata table"
  default_output: false
  trigger_only_when:
    - user asks for philosophy
    - mode = reflect
    - mode = teaching
    - debug = true
    - quote has functional role
  forbidden_when:
    - debugging production failure
    - compact mode
    - evidence verification
    - timeout recovery
    - security/governance decision
```

## Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `arifosmcp/core/arif_think_kernel.py` | Created | I1-I8 invariants, entropy policy, reality stack, math axioms |
| `arifosmcp/runtime/philosophy_registry.py` | Modified | Added `inject_philosophy()` function |
| `arifosmcp/core/QUOTES_CANON.md` | Modified | Added quote metadata schema and placement rules |
| `tests/test_arif_think_kernel.py` | Created | 32 tests for all invariants |

## Test Results

```
32 passed, 0 failed
All I1-I8 invariants verified
Entropy policy validated
Reality stack layers confirmed
Math axioms tested
Quote metadata schema verified
```

## Conclusion

Philosophical quotes in arifOS are properly wired to MCP as **metadata-only** resources.
They provide human resonance through the `philosophical_anchor` envelope but never
enter reasoning chains, judgment deliberation, or sealing criteria.

The implementation follows the verdict: **YES, but quotes must be metadata, not reasoning engine.**

---

**DITEMPA BUKAN DIBERI — Forged, Not Given**
