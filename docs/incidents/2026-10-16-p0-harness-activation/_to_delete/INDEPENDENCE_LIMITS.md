# INDEPENDENCE_LIMITS.md

**Status:** PREPARE_ONLY. ARIFOS::REPRODUCTION_HARNESS::BASELINE::v1.
**Date:** 2026-10-16.

## What this file does NOT claim
- The harness is NOT independently reconstructed
- Containerization alone does NOT establish independence
- The harness author is the same operator who maintains the system under test
- No outsider has built the harness from scratch yet

## Why this file exists
The directive requires the harness to declare its independence limitations explicitly. Per `feedback/feedback-f13-apply-all-sibling-report-needs-independent-audit-2026-10-13.md` — sibling reports and maintainer-built artifacts are NOT independent by default.

## Independence criterion (per directive)
- Maintainer-run reproduction is NOT independent reconstruction
- A clean environment must attempt the 10 BT6 steps; if any requires private federation access, the independence criterion FAILS
- An outsider has not yet built the harness from scratch
- The bundle does NOT include a third-party signature

## What would establish independence
1. An outsider (different person, different machine, no internal access) builds the harness from scratch
2. The outsider's build is checksum-verified
3. The outsider's build uses no private dependency
4. The outsider's build runs with network disabled after dependency preparation
5. The outsider reproduces BT1-BT5
6. The outsider signs an attestation: "I, <outsider>, ran the reproduction harness and confirmed the consequence chain matches the published narrative"

None of the above has happened yet.

## Known limitations
1. The harness is a maintainer-built artifact
2. The source map was produced by the maintainer's T1 PREPARE_ONLY audit (and a sibling agent that the maintainer co-ordinated with)
3. The fixtures are the maintainer's choice
4. The output schemas reflect the maintainer's understanding of arifOS vocabulary
5. The 3-of-8 tools that have defensible output schemas in the sibling's T1 audit are not yet verified against the actual runtime

## What is established
- The harness design is self-consistent (F13 doctrine: bounded 7-phase pattern)
- The vocabulary freeze derives from live source probes (not invented)
- The independence limitation is acknowledged in the harness, not concealed
- The activation is MENUNGGU ARIF (not granted)

## Per `feedback/sibling-snapshot-dirname-may-be-literal-placeholder-2026-10-13.md`
The sibling T1 audit's worktree path `/root/forge_work/2026-10-16/four-gap-readiness/` has been verified to exist with the claimed SHA256 (`6be98892dae2c2f6b7d3c66eec45b312d59bd59404c2fd85e3cf9254ab03416e`). The path is not a placeholder.

## What this means for downstream
- The harness CAN be activated by the maintainer, but that does not establish independence
- An outsider's reproduction of this harness is the only path to independence
- Until then, the harness is a maintainer-built description of the system under test, not an independent verification
