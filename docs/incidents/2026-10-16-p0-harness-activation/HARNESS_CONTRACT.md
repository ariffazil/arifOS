# HARNESS_CONTRACT.md
**Reference:** ARIFOS::BASELINE_UNIT_TESTS::v1 (formerly ARIFOS::REPRODUCTION_HARNESS::BASELINE::v1)
**Authority:** ARIF (Human Sovereign)
**Mode:** ISOLATED | FAIL-CLOSED — ordinary deterministic baseline unit tests run locally and reversibly.

## Test subject
The four governance gaps named in `four-gap-readiness/FOUR_GAP_SOURCE_MAP.md`
(Gap 1 Verified Actor Binding, Gap 2 Receipt Fidelity, Gap 3 Sink Reconciliation,
Gap 4 Independent Reconstruction; A-FORGE + arifOS), measured through
**fixtures and isolated local processes only**.

## Trusted inputs (read-only; verified 2026-10-16)

| Input | sha256 |
|---|---|
| `four-gap-readiness/FOUR_GAP_SOURCE_MAP.md` | `6be98892dae2c2f6b7d3c66eec45b312d59bd59404c2fd85e3cf9254ab03416e` |
| `ARIFOS-FOUR-GAP-READINESS-v1/INVENTED_OR_UNVERIFIED_PATHS.md` | `2b66b5c4bba15723e081bba3889626bed7fecae0af532edc5c75c0ed808b2c46` |
| `ARIFOS-FOUR-GAP-READINESS-v1/EVENT_VOCABULARY_MATRIX.md` | `2a7d87d200295805e26327daa21ddc970c47fd9507427e858c2a2bddb855bdd9` |
| `ARIFOS-FOUR-GAP-READINESS-v1/BASELINE_REPRODUCTION_PLAN.md` | `5493ec855352e03ebdf4322862f6960c299d886b9409df1c32b2e470113f2496` |
| `ARIFOS-FOUR-GAP-READINESS-v1/DEPENDENCY_GRAPH.md` | `47ef936d8b72f893d204ed47eb639a6dd49e0bfbba56d2b8de83146b64cec61f` |
| `ARIFOS-FOUR-GAP-READINESS-v1/REVISED_ROADMAP.md` | `f244470ecedd834a8b726926d957a294b88d0694da0bb486b2d0a64cce8700ac` |

All paths are relative to `/root/forge_work/2026-10-16/`. Read-only source
inspection of `/root/arifOS/` (canonical source tree; an alternate tree at
`/opt/arifos/app` exists — this harness imports from `/root/arifOS`) and
`/root/A-FORGE/`.

## Untrusted inputs (all caller-supplied)
`actor_id`, `actor_verified`, `verdict`, `session_id`, `session_token`,
`reason_code`, `ok`, `can_claim_success`, any envelope text field.

## Isolation boundary
The harness runs in a **temporary directory**, uses **fixtures and mocks**,
touches **no production path**, and appends **no production ledger**.

## Network policy
**None.** No harness script or test opens a socket. Forbidden: package
downloads, federation endpoints, mutation endpoints, service reload/restart.
Enforceable detail: `NETWORK_DEPENDENCIES.md`.

## Filesystem policy
Write only inside `$TMPDIR/arifos-repro-*` and this harness directory
(`fixtures/` outputs). No `/etc`, no canonical repos, no `/var/lib`, no
immutable attributes.

## Secret policy
No credentials, no private keys, no copied production ledger payloads.
`scripts/secret_scan.sh` must pass (result captured in `SECRET_SCAN_REPORT.md`).

## Mutation policy (fail-closed)
**MUST NOT** call a live mutation tool, obtain authority from
filename/prefix/env labels, reload/restart any service, edit `/etc`, toggle
immutables, modify canonical repos, publish packages, or append to production
ledgers. Any test failure is a failure — never relabelled as an expected pass.

## Evidence outputs
- State record: `BASELINE_RESULTS.md` + `fixtures/baseline_results.json`
- Per-test fixtures: `fixtures/bt5_sink_divergence.json`, `fixtures/bt6_reconstruction_steps.json`
- Machine-checked event contract: `schemas/governance-event.schema.json`
- Hash manifest: `MANIFEST.sha256`

## Deterministic inputs
Fixture payloads under `fixtures/` — fixed bytes, fixed hashes.

## Non-deterministic dependencies
Wall-clock timestamps, host paths, OS scheduling. Must be pinned or normalised
in output.

## Success criteria
Every BT1–BT6 reaches Level 1 (command ran) and Level 2 (expected field
observed). See `BASELINE_RESULTS.md` for the measured/design split.

## Failure criteria
Any Level 1-only result; any manufactured event identity to force a pass;
any baseline failure hidden; any private-dependency requirement.

## Independence limitation
**Maintainer-run reproduction is NOT independent reconstruction.** This
harness is maintainer-built against a system the same operator maintains; a
passing test is not universal safety, and a failed test must remain visible.
Independence would require an outsider (different person, clean host, no
internal access) rebuilding the harness with no private dependency, running
it network-disabled, reproducing BT1–BT6, and signing an attestation. None of
that has happened.

## Scope exclusions (recorded at build; not created)
`Dockerfile.repro`, `compose.repro.yaml`, `normative-invariants.json`
(unneeded), `truth-contract.json` (forbidden by original directive),
`reproduction-bundle.tar.gz` (requires outsider attestation). Separate tracks,
untouched: the 11 SHA-256 output-schema audit artifacts; REALITY LOOP
`rl-577cbd57-b37b-47b3-a29f-80fac62ba6b8` (remains HOLD).

## Prohibited outputs
No runtime SEAL. No claim that any governance gap is closed. No claim that
maintainer execution is independent verification.
