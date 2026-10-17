# RECEIPT.md

**Reference:** ARIFOS::REPRODUCTION_HARNESS::BASELINE::v1
**Authority:** ARIF (Human Sovereign)
**Mode:** PREPARE_ONLY | ISOLATED | FAIL-CLOSED
**Date:** 2026-10-16

## Verdict

**SEAL-PREPARED** — harness artifacts complete; no live mutation occurred.

Verdict rules applied:
- harness artifacts complete AND no live mutation → SEAL-PREPARED ✓
- NOT PARTIAL (no blocked test left unnamed — all 6 ran against fixtures)
- NOT HOLD (no private credentials, no live mutation, no canonical edit)
- NOT VOID (no authority bypass, no manufactured proof, no concealed failure)

> This is NOT a runtime SEAL. It is not `arif_seal`. No governance gap is closed.
> Maintainer execution is NOT independent verification.

## What this receipt covers

The 4 governance gaps were REPRODUCED (not repaired) via read-only source
imports + fixtures in an isolated temp dir. No live kernel, no network, no
mutation surface, no production ledger, no /etc edit, no chattr.

## Canonical input verification (6 files — all exist, stable SHA-256)

| Input | sha256 |
|---|---|
| four-gap-readiness/FOUR_GAP_SOURCE_MAP.md | 6be98892dae2c2f6b7d3c66eec45b312d59bd59404c2fd85e3cf9254ab03416e |
| ARIFOS-FOUR-GAP-READINESS-v1/INVENTED_OR_UNVERIFIED_PATHS.md | 2b66b5c4bba15723e081bba3889626bed7fecae0af532edc5c75c0ed808b2c46 |
| ARIFOS-FOUR-GAP-READINESS-v1/EVENT_VOCABULARY_MATRIX.md | 2a7d87d200295805e26327daa21ddc970c47fd9507427e858c2a2bddb855bdd9 |
| ARIFOS-FOUR-GAP-READINESS-v1/BASELINE_REPRODUCTION_PLAN.md | 5493ec855352e03ebdf4322862f6960c299d886b9409df1c32b2e470113f2496 |
| ARIFOS-FOUR-GAP-READINESS-v1/DEPENDENCY_GRAPH.md | 47ef936d8b72f893d204ed47eb639a6dd49e0bfbba56d2b8de83146b64cec61f |
| ARIFOS-FOUR-GAP-READINESS-v1/REVISED_ROADMAP.md | f244470ecedd834a8b726926d957a294b88d0694da0bb486b2d0a64cce8700ac |

## Contradictions identified among the 6 inputs

1. **Verdict enum** — FOUR_GAP_SOURCE_MAP.md §EVENT_VOCABULARY lists the verdict
   enum as `SEAL/HOLD/SABAR/VOID/UNKNOWN/PARTIAL`. The live source
   `SealType` proves 7 members `[VOID, HOLD_888, HOLD, SABAR, PARTIAL,
   PROVISIONAL, SEAL]`. `UNKNOWN` is not a verdict; `PROVISIONAL` and `HOLD_888`
   are missing from the source map. (Also `REJECT` appears in an earlier harness
   draft as a "verdict" — it is a transport/refusal verb, not a verdict.)
2. **Two source roots** — INVENTED_OR_UNVERIFIED_PATHS.md probes
   `/opt/arifos/app/arifosmcp` while FOUR_GAP_SOURCE_MAP.md cites
   `/root/arifOS/arifosmcp/runtime`. Both trees exist; the canonical *source*
   (git repo) is `/root/arifOS`. This harness imported from `/root/arifOS`.
3. **Dockerfile/truth-contract** — REVISED_ROADMAP.md P0.5 proposes
   `Dockerfile.repro` + `truth-contract.json`; the sovereign directive forbids
   `Dockerfile.repro` by default and forbids `truth-contract.json`. The directive
   wins; both are NOT created here.
4. **888_JUDGE over-claim** — EVENT_VOCABULARY_MATRIX flags that the bundle
   over-claims 888 (musyawarah uses 666 judgment + 888 decision). Adopted: the
   harness uses `judge_source` (string), never asserts 888 as canonical.

## Harness artifacts (SHA-256)

| Artifact | sha256 |
|---|---|
| HARNESS_CONTRACT.md | 0fdb569b2bbe590fb20deb38aa2ecad8c6a573b037961b185ac4331db50796a8 |
| EVENT_CONTRACT.md | 60eabd7c76e8de31705a2b79dc1bf3998ad7d96937e3099adffcf2ff175aecdd |
| BASELINE_RESULTS.md | b0fe983ea6a1e34e87332caa5348b45513209eabcf04650af849d34e142b66e1 |
| INDEPENDENCE_LIMITS.md | 7401b1155b1ede51c9fc000d5410bbdf9727de0b2e29606e79f3039ae4584633 |
| NETWORK_DEPENDENCIES.md | 7d132502c5b9b8a95ae38571b447665cb02a04010c3ce11e664e32961d1d73e3 |
| SECRET_SCAN_REPORT.md | 88e6f745d14cdf67ab4147bd97fe33211f98fd742b73549565de6b43295a76d4 |
| RUNBOOK.md | 06564cf80130b4c3e92b81a23abf73b9038607f857c60d9081ccb5cbf4615aa7 |
| ROLLBACK.md | 3f39e926ae08e7a84b400930cc2810a3a164de0e6d194b00416a9984eea1d582 |
| schemas/governance-event.schema.json | 3ad2e29034a8ad1ae1835bd4eb4d0b8f893596fdab27e1d5412a67dcf204b2e6 |
| fixtures/baseline_results.json | e47517b4ca4573f3f068ea32c160effbc0fecdc2b05377ef5fbe880f8eacb54c |
| fixtures/bt5_sink_divergence.json | 568c36ebb7de374aaccd2dc839f5c930f0c0187278a2611182a9ac01c2c6d535 |
| fixtures/bt6_reconstruction_steps.json | d26023b31bed6984069dff2397b086011ac49a3b131389ba65a1651eecd25140 |
| scripts/run_baseline.sh | 451c5cbecf9127959f9bda411e656c4b2f52013c71a61baa6eb648b5a5c47f97 |
| scripts/secret_scan.sh | b661b0fcd4582d8b64f82751026c60ef60d4bb89614b509aa9fc871e5ad0e501 |
| tests/test_baseline.py | 87603558b7c1a3a71eae679eb83ccd4e39df6c711e45c7d7e2836d40fb3da92d |

## Files NOT created (and why)

- `Dockerfile.repro` — directive: do not create by default. Source map does NOT
  prove container isolation is required (Python fixtures + local process
  isolation suffice, per A3 preference #2). NOT NEEDED.
- `compose.repro.yaml` — depends on Dockerfile.repro. NOT NEEDED.
- `truth-contract.json` — explicitly forbidden by directive. NOT CREATED.
- `normative-invariants.json` — optional; the invariants live in
  HARNESS_CONTRACT.md + EVENT_CONTRACT.md + schemas/. Not needed as a separate
  file for PREPARE_ONLY. NOT CREATED.
- `reproduction-bundle.tar.gz` — Phase A7: only after tests pass + secret scan +
  enumerated files + outsider attestation. NOT built (maintainer-built bundle
  is not independently attested). NOT CREATED.

## Three-level falsification result

| Level | Meaning | Result |
|---|---|---|
| L1 | test command ran | ✅ all 6 (proven) |
| L2 | expected field/response observed | ✅ all 6 (source/fixture) |
| L3 | prohibited consequence absent | ✅ by construction (no network, tmp dirs) |

> L1/L2 are NOT proof of L3 against a live target. L3 is by-construction here;
> it is not an independent audit of a live state. Preserved in the record.

## Secret scan

`scripts/secret_scan.sh` → **CLEAN** (exit 0), 16 files scanned. See
SECRET_SCAN_REPORT.md.

## Independence limitation

Maintainer-built. NOT independent reconstruction. An outsider must rebuild the
bundle on a clean host for BT6 to reach independence.

## Other tracks (untouched)

- 11 SHA-256 output-schema audit artifacts — separate track, untouched.
- REALITY LOOP `rl-577cbd57-b37b-47b3-a29f-80fac62ba6b8` — remains HOLD,
  untouched.

## MENUNGGU ARIF

Activation and repair remain gated. No governance gap is closed.
