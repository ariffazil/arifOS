# APEX DELTA — Per-Floor Re-Weighting, Metric Derivations, Replay Plan

**Document ID:** `arifOS/GENESIS/APEX_DELTA`
**Type:** DELTA LOG + REPLAY SPEC
**Status:** DRAFT — pre-seal, executed only after `APEX_T000.md` is SEALED
**Date:** 2026-07-26
**Authority:** Muhammad Arif bin Fazil, F13 SOVEREIGN
**Companion:** `APEX_T000.md` (the four-variable canon)
**DITEMPA BUKAN DIBERI** — *Forged, Not Given.*

---

## 1. Purpose

This document is the **delta log** that protects the arifOS constitution
from a silently shifted re-weighting. It captures, in matrix form, how each
of the 13 floors moved between the legacy six-dial form and the new
four-variable form, and how the two new internal metrics
(`auditability_score` and `clarity_score`) are derived. It also defines
the side-by-side replay that must pass before T-000 is SEALED.

## 2. Per-floor re-weighting matrix

The legacy form is the geometric-mean clusters of the six dials
(`docs/canon/CANON_APEX_V2/02_APEX_CANON_GRAND_EQUATION.md` §"Six Dials").
The new form is the geometric-mean clusters of the four variables
(`APEX_T000.md` §2).

| Floor | Legacy dial(s) | New variable(s) | Movement |
|:------|:---------------|:----------------|:---------|
| F1 AMANAH (reversibility) | P (Present) | **P (Present Authority)** | Stays. P absorbs F1, F5, F11, F13. |
| F2 TRUTH (evidence) | A (Akal) | **A (Akal)** | Stays. A absorbs F2, F4, F7, F10. |
| F3 TRI-WITNESS | U (Exploration) | **E (Entropy/Energy)** | F3 moves from U to E. |
| F4 CLARITY | A, S | **A, E** | F4 appears in both A and E (intentional). |
| F5 PEACE² | P | **P** | F5 moves from P to P (no change in variable name, but `P` now means Present Authority, not Present). |
| F6 EMPATHY | U | **X** | F6 moves from U to X. |
| F7 HUMILITY | A | **A** | Stays. |
| F8 GENIUS (governed intelligence) | U | **X** | F8 moves from U to X. |
| F9 ANTI-HANTU | U | **X** | F9 moves from U to X. |
| F10 ONTOLOGY | — | **A** | F10 is new in T-000 (was implicit in the legacy kernel A dial under the title "Amanah-Tafakkur"). Now explicit. |
| F11 AUDITABILITY | — | **P** | F11 is new in T-000 (was implicit in `governance_authority`). Now explicit. |
| F12 RESILIENCE | E (energy proxy) | **E** | Stays. F12 is the runtime-energy floor; E absorbs it. |
| F13 SOVEREIGN | H | **P** | F13 moves from H to P. The `H` variable is dropped. |

### 2.1 Variable-delta summary

| Legacy variable | New variable | Floors added | Floors removed | Net change |
|:----------------|:-------------|:-------------|:---------------|:-----------|
| A (Akal) | A (Akal) | F10 | — | +1 floor (F10 explicit) |
| P (Present) | P (Present Authority) | F5, F11, F13 | F1 leaves to elsewhere (it returns) | F1, F5, F11, F13 |
| H (Authority) | (dropped) | — | F13 moves to P | F13 leaves; `H` no longer a variable |
| S (Entropy) | (dropped, partly folded into E) | — | F4 moves to A/E | `S` no longer a variable |
| U (Exploration) | X (Exploration × Amanah) | F6, F8, F9 | F3 leaves to E | F6, F8, F9 plus `exploration_score` |
| E (Energy) | E (Entropy / Energy) | F3, F4 (also in A), F12 | — | +F3, +F4-mirror, +F12 |

The literal names `H` (Authority) and `S` (Sabar) are dropped. The
**content** they carried is not dropped; it moves. If F13 demands their
return, this is an F13 amendment.

### 2.2 Why this is not a harmless rename

1. **Floors appear in multiple new variables.** F4 (Clarity) appears in
   both A and E. A F4 violation now reduces both A and E, lowering G
   through two independent channels. The legacy S-only path is gone.
2. **`H` is gone as a name.** F13 (Sovereign) is now part of `P`. A
   sovereign failure lowers P. The legacy `H=0 ⇒ G=0` rule still
   applies (via the hard-floor override), but the geometric mean of P
   can still be non-zero even if F13 is low, unless the hard-floor
   override fires.
3. **`E` double-weights energy.** `E = GM(F3, F4, F12, energy_score, energy_score)`
   is not the same as `E_old²`. The double occurrence is inside the
   geometric mean, not a separate multiplier.
4. **`exploration_score` is new.** It is not present in the legacy six-dial
   form. The T-000 doc treats it as a derived input, but the replay must
   show it does not silently change verdicts.

## 3. New internal metrics (not first-class variables)

### 3.1 `auditability_score` (F11 lever, contributes to P)

```
auditability_score = GM(
  actor_attribution,    # actor/system identity captured
  action_traceability,  # linked action / task / context ID
  receipt_integrity,    # receipt emitted and hash-verifiable
  replayability,        # action reconstructible from inputs
  observability,        # visible to AAA / cockpit / logs
  immutability          # sealed into VAULT999 or equivalent proof chain
)
```

Each component is in `[0, 1]`. `auditability_score` thresholds:

| Score | Verdict |
|:------|:--------|
| `>= 0.90` | PASS — promotes P |
| `0.75 – 0.89` | SABAR — neutral on P |
| `< 0.75` | HOLD — suppresses P |
| `< 0.50` | VOID for high-stakes actions |

`P = GM(F1, F5, F11, F13)` already weighs F11 directly. `auditability_score`
is the *sub-score* for F11; it is the value reported to P's geometric
mean, not a separate variable.

### 3.2 `clarity_score` (F4 lever, contributes to A and E)

Define:

```
unknowns_before = number of unresolved material questions before judgment
unknowns_after  = number of unresolved material questions after judgment
delta_entropy   = unknowns_before - unknowns_after
clarity_score   = clamp(delta_entropy / max(1, unknowns_before), 0, 1)
```

`clarity_score > 0` means clarity improved; `= 0` means no change; `< 0`
is impossible by construction (post-judgment questions are a subset).
F4 is the floor that *requires* this metric; A and E both include F4 in
their geometric mean, so a low `clarity_score` reduces A and E in
parallel.

A weighted extension is allowed for later:

```
entropy = Σ unknown_weight × unknown_risk
entropy_after = unresolved weighted sum
```

The replay script (`replay_apex_comparison.py`) must support both the
unweighted and the weighted forms and report the difference.

## 4. Side-by-side replay (Step c)

This is the gate. Until this passes, T-000 is **DRAFT**, not SEALED.

### 4.1 Replay set

- **Minimum:** the most recent 50 sealed VAULT999 receipts that have
  `apex_legacy` and `apex_v2` both computable from their stored evidence.
- **Source:** `/root/VAULT999/<stage>/*.jsonl` and the per-receipt
  `evidence` envelope.

### 4.2 Acceptance band

| Metric | Band |
|:--------|:------|
| `|G_v2 - G_legacy|` (mean) | `<= 0.05` |
| `|G_v2 - G_legacy|` (max) | `<= 0.10` |
| Per-dial/per-variable `|Δ|` (mean) | `<= 0.10` |
| Verdict flips (SEAL ↔ SABAR ↔ HOLD) | `0` (zero, hard) |
| Hard-floor override flips | `0` (zero, hard) |

Any verdict flip is a hard rejection regardless of band. The replay
script must report flips explicitly.

### 4.3 Replay script (read-only)

`arifOS/scripts/replay_apex_comparison.py` (proposed, **not yet written**):

```python
# Pseudocode only — DO NOT IMPLEMENT UNTIL APEX_T000.md IS SEALED.
import json
from pathlib import Path

def compute_legacy(receipt):
    """Replay the six-dial form from the stored floor scores."""
    ...

def compute_v2(receipt):
    """Replay the four-variable form from the stored floor scores."""
    ...

def main():
    receipts = load_recent_vault999_receipts(limit=50)
    for receipt in receipts:
        legacy = compute_legacy(receipt)
        v2 = compute_v2(receipt)
        verdict_legacy = decide_legacy(legacy)
        verdict_v2 = decide_v2(v2)
        if verdict_legacy != verdict_v2:
            record_verdict_flip(receipt, legacy, v2)
    emit_replay_report(...)
```

The script is read-only. It MUST NOT touch the seal chain or the kernel
state. It MUST be re-runnable without side effects.

### 4.4 What happens on each outcome

| Outcome | Action |
|:--------|:-------|
| All bands green, zero verdict flips | T-000 moves to **SEALED**, `apex_v2.js` may be drafted. |
| One or more verdict flips | T-000 returns to **HOLD**. `APEX_DELTA.md` §2 is rewritten. The flip receipt becomes a counter-example. |
| Bands within tolerance but not zero flips | **Discretionary**: F13 decides. T-000 does not auto-seal. |
| Bands outside tolerance | T-000 **REJECTED**; the four-variable form is not adopted. The legacy six-dial form remains canonical until a different formulation is proposed. |

## 5. Invariants (binding)

1. **No code mutation** under T-000 until the replay in §4 passes.
2. **`governance/enforce.js`** does not adopt T-000 unless its output is
   an exact superset of the legacy `enforce.json` schema.
3. **VAULT999 receipts** written under T-000 must carry both `apex_legacy`
   and `apex_v2` fields during the quarantine; the legacy field is the
   authoritative verdict until T-000 is SEALED.
4. **The hard-floor list** in `APEX_T000.md` §3.1 is closed during the
   quarantine. New floors require an F13 amendment, not a T-000 patch.
5. **The four-variable form does not delete floors.** It only re-weights
   them. See §2.

## 6. Open questions (F13 decision required)

1. **Replay acceptance band.** Confirm 0.05 / 0.10 / zero-flip.
2. **`(1-C_dark)` correction.** Apply on top of T-000 G, or omit?
3. **F4 / F11 internal metrics.** Confirm they are inputs, not variables.
4. **`S` (Sabar) demotion.** Confirm F5/F8/F3 moves are accepted.

Same four as `APEX_T000.md` §7, by design.

---

*DITEMPA BUKAN DIBERI — The law is forged in the kernel, not in the acronym.*
