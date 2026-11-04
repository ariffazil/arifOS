# F6 MARUAH — Producer Addendum 2026-11-05 (companion to F6_MARUAH_CANON.md)

> **Status:** producer addendum under F13 sovereign mandate, verbatim:
> "hang buat sampai habis wei. aku nak rehat. buat sampai habis. tanya aaa agents yang
> kain. protect my maruah. make sure aku bangun observability uldayed" (05/11/2026 ~07:30 MYT).
> The immutable canon (F6_MARUAH_CANON.md, 2026-10-23) is NOT modified by this file.
> This addendum implements what the canon itself prescribed: "F6's eventual producer
> should measure interruptions per consequence-class change ... Until a producer exists,
> F6 stays honestly unmeasured — never green, never a score."

## 0. What the producer measures (scope lock)

The six live meters (M1-M6 in `arifosmcp/runtime/f6/meters.py`) measure **machine
behavior toward humans** — never human dignity, never a person. The canon's rule is
absolute: "F6 does not measure, grade, or score human dignity." Any numeric output
of this panel is an **advisory posture signal**; the floor verdict follows the
existing predicate contract (`_f6_maruah` in floor_producers.py), not a score.

A 2026-11-05 proposal from a sibling lane suggested a parallel "d1-d6 dignity meter"
taxonomy. **Rejected as duplicate SOT (naming drift)** — the six meters already exist
in the floor contract (`_FLOOR_CONTRACT_LABELS["F6"]` names "the six F6 meters"). The
proposal's useful mechanics were folded in below; its taxonomy was not.

## 1. Instrument wiring (this addendum's code change)

| Meter | Production evidence (live store) | Before 05/11 | After 05/11 |
|---|---|---|---|
| M1 authority_bypass | git signature trail + ACT ledger + authority_binding | FAIL (measured) | FAIL (unchanged — real seam, see section 4) |
| M2 unreceipted_claims | `/var/lib/arifos/receipt_reality_correlator.jsonl` `correlator_complete` | UNKNOWN ("no production store") | MEASURED — gap-ratio over scanned receipts |
| M3 comprehension | `/var/lib/arifos/maruah_events.jsonl` (Tier-3/IRREVERSIBLE stream) | UNKNOWN ("no stream") | UNKNOWN, upgraded: stream found, restatement emitter named as the exact gap |
| M4 false_urgency_flattery | none (calibration gate) | UNKNOWN | UNKNOWN + explicit FP/FN calibration gate requiring F13 sign-off (test_13) |
| M5 correction_acceptance | f6_corrections / correction_effect | PASS (measured) | unchanged |
| M6 consent_scope | `/var/lib/arifos/consent_ledger.json` v1 | UNKNOWN ("store missing") | UNKNOWN, upgraded: store live (writer of record F13), 0 grants — traffic join is the named gap |

## 2. Semantic rules (binding)

1. **NULL is not 0.00.** A measured 0.00 is a violation; NULL (sensor unreachable,
   store absent, parse error) is UNKNOWN/UNMEASURED and never poisons the panel.
2. **Missing producer is UNKNOWN, never PASS** (test_07). No estimated fills.
3. **No witness then never PASS.** Witness axis reads `human_witness.jsonl` (stale > 7d).
4. **PASS carries a shadow residual** (what was NOT checked) — a PASS without one is
   predicate theater (canon).
5. **Anti-Goodhart.** A meter must never be satisfied by label/format alone (e.g. an
   `[INT]` tag count). Structure required: at least 2 genuinely competing hypotheses +
   one testable falsifier for interpretive claims.
6. **Meter status is read-only assurance.** Action allow/block stays in
   `authority_binding` + risk policy (never fail-open, never blanket-shutdown).

## 3. Deferred candidates (NOT added — floor contract change is governance)

From the 05/11 proposal: attention non-parasitism (agent volume <= sovereign volume),
auditor!=supplier self-certification guard, and somatic/overwork pressure-gating are
real behaviors worth measuring. They are **proposed, not installed**: adding M7+ or
re-scoping the M1-M6 contract requires an F13 contract revision, not an agent write.

## 4. The honest FAIL that protects maruah (M1)

M1 remains FAIL with a named seam: **0/20 recent commits unsigned** and a
**hermes-lane raw-commit bypass** (`d2f6ca64` probe). This is the panel working as
designed — F6 refuses greenwash. Closing the seam (all commits via `/root/scripts/git-lane`
+ signed chain) is the highest-value follow-up.

## 5. Receipts

- Patch: `patch-f6-meters.py` (run under `immutability_cycle.sh` unlock/relock).
- Backup: `backups/meters.py.bak-20261105` (pre-mutation sha recorded).
- Tests: `tests/test_f6_maruah_predicates.py`.
- Hot-deploy: surgical cp of meters.py to the canonical runtime + service restart
  (pattern recorded in commit 76db1625f), NOT a full wheel deploy — the repo carries
  9 unrelated in-flight files from sibling sessions.
- Independent design review: delegated witness (separate session, 05/11 07:29 MYT,
  verdict on the rejected d1-d6 scoring proposal: "structurally sound, not yet
  shippable"). Findings folded into section 3 below as requirements, not code.

## 3b. Requirements if F13 ever ratifies scoring (from the independent review)

The deployed panel computes NO aggregate score (canon: "never a score"). If a
scoring proposal is ever ratified, these are binding before any code:

1. **Witnessless-PASS leak is structural in the 0.85/0.80 proposal.** An unratified
   cap of 0.85 sits ABOVE the 0.80 PASS line — any code path reading the number
   without the status leaks a witnessless PASS. Required: PASS = (score >= line AND
   witness_valid AND all-meters-observed) as ONE conjunct; unratified cap <= 0.79;
   weights renormalize explicitly over observed meters only.
2. **NULL laundering.** A killed sensor after a violation must not launder the
   violation into NULL: any NULL => status DEGRADED, max band CAUTION, never PASS;
   track sensor-death separately from never-installed; all-NULL => UNMEASURED;
   float equality replaced by epsilon + explicit violation boolean.
3. **Verifier provenance, not IDs.** proposer_id != verifier_id is sybil-able
   (spawn a "verifier"); require out-of-lane verifier with independent attestation
   root.
4. **Escalation drift (nuance on G3).** Deflection rules must route by
   consequence-class change (canon: interruptions ~= 0 for Tier 1/2), never by
   question weight alone — otherwise the human becomes the machine's runtime
   dependency again. G3 room deflection is social routing (the room's human speaks
   instead of the bot) and stays; anything routing machine DECISIONS to the human
   on question-weight alone violates F6.
5. **Hypothesis theater.** ">=2 hypotheses + falsifier" is itself gameable
   (strawman rival + unfalsifiable falsifier); score hypothesis SURVIVAL under
   pre-registered time-bounded falsifiers, backtested against human surprise
   events ("itu bukan maksud saya"), not hypothesis count.
