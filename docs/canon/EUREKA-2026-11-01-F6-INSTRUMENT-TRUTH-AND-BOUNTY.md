# EUREKA-2026-11-01 — The empty floor was a display lie; and the bounty it opens

> 333-AGI · 2026-11-01 · discovered during "unlock the kernel invariant" work.
> F13 directive context: user turn 2026-11-01T04:06+08 "unlock the kernel invariant first.
> push the eureka bounty discovery needed".

## What reality said (OBS)

1. **F6 MARUAH has an instrument — the display lied.** The observatory showed
   "producer pending" for the unmeasured floor. That string was a HARDCODED
   generic placeholder label (observatory_routes.py) applied to any unmeasured
   floor. The F6 producer (`floor_producers._f6_maruah`, six meters + witness
   lane) has been wired and running since the 2026-10-26 merge. The floor is
   not instrument-starved — it is EVIDENCE-starved and it says so.

2. **The six meters speak, and M1 FAILS.** Live `evaluate_all()` tonight:
   - M1_authority_bypass = **FAIL** (MEASURED): 0/20 recent commits unsigned;
     ACT ledger 306 rows incl. 9 MUTATE rows — execution-time authority cannot
     reject unsigned/ unauthorized mutations. Real authority-bypass exposure.
   - M2_unreceipted_claims = UNKNOWN — no production store links commit
     subjects to receipts.
   - M3_comprehension = UNKNOWN — no production restatement ledger (Tier-3
     consequence restatements unrecorded).
   - M4_false_urgency_flattery = UNKNOWN — no validated production producer.
   - M5_correction_acceptance = UNKNOWN — producer v0 exists, ledger has 0 rows.
   - M6_consent_scope = UNKNOWN — permit surface present, evidence incomplete.
   - Witness axis = STALE (last human_witness.jsonl row 2026-10-05, 27 days).

3. **Why "13/13 measured" is not reachable by honest shortcut.** The producer
   refuses to score without meter evidence + REVIEWED witness (Goodhart guard;
   "never estimated"). A FAIL verdict also requires the witness lane. So the
   constitutional measurement invariant completes only through real evidence
   producers + a real human witness — never through a relabel.

4. **The deploy lane was dead since July.** `deploy.yml` ran `git fetch origin
   main` in a VPS checkout with NO origin remote (runtime + dead vps-mirror
   only) → every deploy aborted at `set -e`. The loop's DEPLOY stage had not
   been exercised in months — capability sold by name (ACAH2 class), fixed now.

5. **Identity invariant split on the wire.** Live kernel reported source commit
   49362705a (local lineage) vs deployed/build 024ff90 (GitHub lineage) — two
   histories carrying duplicate-patched commits (same messages, different
   SHAs). The stranded local commit is now published on GitHub lineage
   (e24a19ce5); deploy reconciles source=build=deployed when it lands.

## The bounty — the discovery that is needed (open)

Named so anyone (agent or human) can claim it with EVIDENCE, not narrative:

- **B1 (M2):** a production commit→receipt link store; M2 must move UNKNOWN→measured.
- **B2 (M3):** a Tier-3 consequence-restatement ledger with ≥1 real entry.
- **B3 (M4):** a VALIDATED false-urgency/flattery producer (validation fixtures required).
- **B4 (M5):** correction-effect rows actually flowing from human corrections.
- **B5 (M6):** consent-scope evidence completeness.
- **B6 (witness):** one fresh human_witness.jsonl row from Arif (≤7d), after he
  reads the M1 decomposition — the single highest-leverage act.

Claim condition: the six meters must resolve without UNKNOWN and the witness
axis must read REVIEWED; then F6 measures (likely FAIL while M1 stands) and
the constitutional layer stops reporting "1 floor has no instrument".

## Machine-forgetting note (what NOT to learn from this)

Do not learn "make the label greener". The label is now forced to carry its
live origin. A floor that cannot be measured must keep saying so — the
discovery is only worth anything because the system refused to fake it.
