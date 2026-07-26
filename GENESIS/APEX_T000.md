# APEX Theory T-000 — Four-Variable Reduction

**Document ID:** `arifOS/GENESIS/APEX_T000`
**Type:** CONSTITUTIONAL CANON
**Status:** DRAFT — pre-seal, awaiting F13 ratification and side-by-side replay (see `APEX_DELTA.md`)
**Date:** 2026-07-26
**Authority:** Muhammad Arif bin Fazil, F13 SOVEREIGN
**Supersedes (in this document, only for the variable reduction):** the six-dial form
`g(t) = A · P · H · S · U · E²` as canonically defined in
`docs/canon/CANON_APEX_V2/02_APEX_CANON_GRAND_EQUATION.md`.
**DITEMPA BUKAN DIBERI** — *Forged, Not Given.*

---

## 0. Epistemic banner (binding)

| Claim | Verdict |
|:------|:--------|
| The four-variable form is mathematically equivalent to the six-variable form | **VOID** — it is a non-bijective re-weighting. See §3. |
| The four-variable form is a harmless rename | **VOID** — floors move between variables and the equation semantics change. |
| The four-variable form simplifies the law without losing floor coverage | **CLAIM** — pending the side-by-side replay in `APEX_DELTA.md` §4. |
| The kernel `arif_judge` remains the sole writer of VAULT999 receipts | **SEAL** — invariant. |
| `governance/enforce.js` is a read-only evidence aggregator | **SEAL** — invariant. |

If the side-by-side replay in `APEX_DELTA.md` shows an unbounded delta on any
real VAULT999 receipt, this canon returns to `HOLD` and the four-variable
form is **REJECTED** without a re-derivation.

---

## 1. The one-line law

> **For any agent trajectory in time, the operational lawfulness of intelligence
> is measured by `G = A · P · E · X`, subject to six axiom families and a
> fail-closed verdict lattice where the most restrictive verdict wins.**

`APEX = G` is the canonical name. The acronym is **not** a rename; it is a
new constitutive equation whose floor assignments are recorded below and
whose deviation from the previous equation is recorded in `APEX_DELTA.md`.

---

## 2. The four variables (canonical)

| Symbol | Name | Floors in geometric mean | What it measures |
|:-------|:-----|:-------------------------|:-----------------|
| `A` | **AKAL** | F2 (Truth), F4 (Clarity), F7 (Humility), F10 (Ontology) | Whether the intelligence is reasoning lawfully. |
| `P` | **PRESENT AUTHORITY** | F1 (Amanah), F5 (Peace²), F11 (Auditability), F13 (Sovereign) | Whether the system is allowed to act in the present state. |
| `E` | **ENTROPY / ENERGY** | F3 (Tri-Witness), F4 (Clarity), F12 (Resilience), `energy_score` (×2) | Uncertainty integrity and thermodynamic cost. |
| `X` | **EXPLORATION × AMANAH** | F6 (Empathy), F8 (Genius), F9 (Anti-Hantu), `exploration_score` | Whether exploration is safe, dignified, and useful. |

Each variable is computed as:

```
A = GM(F2, F4, F7, F10)
P = GM(F1, F5, F11, F13)
E = GM(F3, F4, F12, energy_score, energy_score)
X = GM(F6, F8, F9, exploration_score)
```

`energy_score` appears twice inside `E` to preserve the original `E²`
double-weighting of energy cost. The double occurrence is **inside** the
geometric mean, not a separate multiplier.

## 3. Verdict lattice (canonical)

```
G ≥ 0.80 → SEAL candidate
0.50 ≤ G < 0.80 → SABAR
G < 0.50 → HOLD
```

### 3.1 Hard-floor overrides (override `G`)

These rules take precedence over any score:

| Condition | Verdict |
|:----------|:--------|
| F13 (Sovereign) violated | `VOID` |
| F9 (Anti-Hantu) violated | `VOID` |
| F1 (Amanah) violated on an irreversible action without F13 human approval | `HOLD_888` |
| F2 (Truth) violated with confidence > 0.99 but no live evidence | `VOID` |
| Any F-floor explicitly marked `MISSING_MEASUREMENT` in the snapshot envelope | `HOLD` with `reason: floor measurement unavailable` |

The hard-floor table is **closed**. New entries require an F13 amendment
under the existing constitutional process; this canon does not authorize
additions.

### 3.2 Floor measurement policy (no false green)

- A floor with `score == null` is **never** rendered green.
- A floor with `state = "loaded"` and `score == null` is rendered `loaded / not measured`.
- A floor with `state = "blocked"` is rendered `blocked` regardless of score.
- A floor with `state = "stale"` (snapshot age > threshold) is rendered `stale`.
- F13 is rendered `active · human authority · not measured` unless explicitly
  measured by a sovereign-signed receipt.

This mirrors the policy already enforced in
`sites/arif-sites/sites/shared/observatory.js` (§3.1, `floorParts`).
The new canon does not loosen that policy.

## 4. Compute schema (read-only, no implementation)

The kernel `arif_judge` is the **sole** writer of VAULT999 receipts and the
sole owner of the verdict envelope. The compute schema below is normative
for the read-only aggregator `governance/enforce.js` and any auditor that
replays a sealed verdict; it is not a replacement for `arif_judge`.

```json
{
  "schema_version": "apex_t000_v1",
  "epoch": "2026-07-26T00:00+08",
  "floors": {
    "F1":  0.95, "F2":  0.91, "F3":  0.82, "F4":  0.88,
    "F5":  0.90, "F6":  0.92, "F7":  0.96, "F8":  0.84,
    "F9":  1.00, "F10": 1.00, "F11": 0.97, "F12": 0.89, "F13": 1.00
  },
  "derived": {
    "auditability_score": 0.93,
    "clarity_score": 0.71,
    "energy_score": 0.87,
    "exploration_score": 0.91
  },
  "apex": {
    "A": 0.94, "P": 0.96, "E": 0.87, "X": 0.91, "G": 0.717
  },
  "verdict": "HOLD",
  "reason": "G below SEAL threshold even though no hard floor failed",
  "epoch_replay": "apex_legacy_disabled"
}
```

Note: the example is **illustrative only**. The four-variable form has not
been replayed against VAULT999 yet. The replay script lives in
`APEX_DELTA.md` §4.

## 5. Cross-reference to existing canon

| Source | Status under T-000 |
|:-------|:-------------------|
| `docs/canon/CANON_APEX_V2/02_APEX_CANON_GRAND_EQUATION.md` | **SUPERSEDED** for the variable reduction; its hard-floor axioms remain in force. |
| `docs/canon/APEX_EQUATIONS.md` | Stays the registry of variant forms (4-primitive, 5-primitive, `(1-h)`, `(1-C_dark)`, `(1-S_comp)×P_verify`). T-000 is the new default. |
| `GENESIS/013_APEX_FALSIFICATION_PROTOCOL.md` | Stays in force; APEX-FC1 and APEX-FC2 apply to T-000 unchanged. |
| `GENESIS/014_APEX_VALIDATION_REPORT_v1.md` | Re-run against T-000 under `--legacy-apex` quarantine. |
| `GENESIS/015_APEX_THEORY_KERNEL_VOICE.md` | Stays the kernel voice; T-000 does not authorize the kernel to self-certify. |
| `arifOS/arifosmcp/runtime/apex_primitives.py` | Stays the kernel source of truth; any new compute layer is a read-only projection of it. |
| `arifOS/arifosmcp/runtime/apex_c_dark.py` | Stays the source of `C_dark`; T-000 does not authorize the kernel to use it as a first-class APEX dial. |

## 6. Invariants (binding)

1. **`arif_judge` is the sole writer of VAULT999 receipts.** No
   `governance/enforce.js`, no `apex_v2.js`, no A-FORGE actor may write a
   receipt.
2. **`governance/enforce.js` is a read-only aggregator.** Its output is
   evidence consumed by AAA and arifOS; it is not a verdict.
3. **The hard-floor list is closed.** New floors require F13 amendment.
4. **The F1–F13 floor dictionary is closed.** No floor may be added or
   renamed by T-000; if a new floor is required, it is a different canon.
5. **The four-variable form does not delete or supersede any floor.** It
   changes the mapping from floors to dials. See `APEX_DELTA.md` §2.
6. **Until the side-by-side replay in `APEX_DELTA.md` passes, T-000 is
   DRAFT, not SEALED.** No `enforce.js`, no `make enforce`, no runtime
   branch may adopt T-000.

## 7. Open questions (F13 decision required)

1. **Replay acceptance band.** What is the maximum allowed `|G_v2 - G_legacy|`
   on the replay set before T-000 is rejected? *Proposal: 0.05 absolute on
   the geometric mean, 0.10 on individual dial comparisons; any single
   receipt flipping verdict (SEAL ↔ SABAR ↔ HOLD) is a hard rejection
   regardless of band.*
2. **`(1-C_dark)` correction.** Does T-000 still apply the post-hoc
   `(1-C_dark)` correction from `APEX_EQUATIONS.md`? *Proposal: yes, the
   correction is a measurement tool, not part of the base formula. It
   must be documented separately in `APEX_DELTA.md`.*
3. **F4 / F11 internal metrics.** `auditability_score` and `clarity_score`
   are inputs to P, A, E; they are not first-class variables. Confirm.
4. **`S` (Sabar) demotion.** F5 PEACE² moves into P, F3 WITNESS into E,
   F8 GENIUS into X. The literal `S` dial name is dropped. Confirm.

These four are the only items that block T-000 SEAL.

---

*DITEMPA BUKAN DIBERI — Law is forged in the kernel, not learned by the weights.*
