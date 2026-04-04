---
id: canon-witness
title: Tri-Witness (F3)
sidebar_position: 4
description: The F3 Tri-Witness consensus system - how three independent sources reach geometric mean agreement before any verdict is sealed.
---

# Tri-Witness - F3 Constitutional Consensus

> Canonical source: [`000_THEORY/003_WITNESS.md`](https://github.com/ariffazil/arifosmcp/blob/main/000_THEORY/003_WITNESS.md)  
> Implementation: [`core/organs/_3_apex.py`](https://github.com/ariffazil/arifosmcp/blob/main/core/organs/_3_apex.py)  
> Stage: 888 AUDIT . Motto: *Tiga Saksi Lebih Baik Dari Satu* (Three Witnesses Better Than One)

---

## What Is the Witness System?

The **Tri-Witness system** is the constitutional consensus mechanism. No verdict can be sealed unless three independent sources agree. A single dissenting witness prevents SEAL.

This is F3 in the constitutional floor system - a **Mirror** (feedback loop), not a Law. It does not block on its own (SABAR, not VOID), but no SEAL can be issued without tri-witness consensus >= 0.95.

---

## The Formula

```
W^3 = (S x S x S)^(1/3) >= 0.95
```

Where:
- **S** = Human witness score (sovereign evidence, user input quality)
- **S** = AI witness score (internal reasoning coherence, F8 Genius)
- **S** = External witness score (reality grounding, web search, external data)

The **geometric mean** is used deliberately. Unlike arithmetic mean, the geometric mean cannot be "rescued" by one very high score if another is near zero. If any witness scores  0, W^3  0 regardless of the other two.

---

## The Three Witnesses

### Witness 1 - Human (Sovereign Evidence)

The human's input quality, context richness, and explicit confirmations contribute to S. A well-specified query with clear intent raises S. An ambiguous query lowers it.

When the human provides explicit confirmation (e.g. approving an `888_HOLD` action), S approaches 1.0 for that specific decision.

### Witness 2 - AI (Internal Reasoning Coherence)

The AI engine's own consistency across stages contributes to S. This is connected to F8 Genius: `G = A x P x X x E^2`. A reasoning path that is internally contradictory, or that reaches a conclusion unsupported by its own stated premises, lowers S.

### Witness 3 - External (Reality Grounding)

External sources - web search (Brave API), citations, referenced documents - contribute to S. The `reality_search` tool exists specifically to raise S. A claim made without any external grounding has low S.

---

## The Panopticon Principle

> *There are no secrets between organs.*

All witness activity is visible across the full pipeline. The AGI Delta, ASI Omega, and APEX Psi engines each contribute their scores to the tri-witness calculation at stage 888. No engine can pass a verdict privately - every judgment is visible to the other two.

This prevents:
- Confirmation bias between engines (they are thermodynamically isolated until stage 444, then their scores are exposed to each other for the consensus calculation)
- Any single engine becoming the sole authority on a verdict
- Hidden reasoning that bypasses constitutional floors

---

## What Happens When W^3 &lt; 0.95?

| W^3 Score | Verdict | Action |
|:--|:--|:--|
| >= 0.95 | Proceed to SEAL | All three witnesses agree |
| 0.85-0.95 | PARTIAL | Proceed with documented warning |
| 0.70-0.85 | SABAR | Pause; gather more evidence; retry |
| &lt; 0.70 | VOID (escalated) | Rejected; return to earlier stage |

---

## Raising W^3 in Practice

**To raise S (external grounding):**

```bash
# Enable Brave Search API for reality grounding
export BRAVE_API_KEY=your-key
# The reality_search tool will be called automatically when F3 is weak
```

**To raise S (human witness):**

- Provide more specific queries with explicit intent
- Approve `888_HOLD` actions explicitly rather than leaving them pending
- Supply context documents or citations with the query

**To raise S (internal coherence):**

- Ensure the query does not contain contradictory premises
- Use the full pipeline (stage 000999) rather than individual tool calls
- Check that floor scores from earlier stages are not borderline

---

## Stage 888 - The AUDIT

Tri-witness consensus is computed at stage 888 (AUDIT) by the APEX Psi engine. This is the final constitutional checkpoint before stage 999 (SEAL). The verdict at 888 - `SEAL`, `SABAR`, `VOID`, or `888_HOLD` - is what gets committed to VAULT999.

Source: [`core/organs/_3_apex.py`](https://github.com/ariffazil/arifosmcp/blob/main/core/organs/_3_apex.py) . [`000_THEORY/003_WITNESS.md`](https://github.com/ariffazil/arifosmcp/blob/main/000_THEORY/003_WITNESS.md)
