# RUNBOOK.md

**Reference:** ARIFOS::BASELINE_UNIT_TESTS::v1

## Purpose
Run the baseline unit tests from a clean directory without federation
credentials. Behavioral contract: `HARNESS_CONTRACT.md`.

## Prerequisites
- `python3` (3.10+) and `bash`
- NO federation credentials, NO API keys, NO network needed

## Steps

```bash
# 0. Set up clean directory and copy the harness
WORKDIR=/tmp/ARIFOS-BASELINE-$(date +%Y%m%dT%H%M%SZ)
mkdir -p "$WORKDIR"
cp -r /root/forge_work/2026-10-16/ARIFOS-REPRO-HARNESS/. "$WORKDIR/"
cd "$WORKDIR"

# 1. Verify artifact integrity against the hash manifest
sha256sum -c MANIFEST.sha256

# 2. Secret scan (must be CLEAN)
bash scripts/secret_scan.sh

# 3. Run the baseline unit tests (BT1–BT6)
bash scripts/run_baseline.sh
```

Entry points: `scripts/run_baseline.sh` runs `tests/test_baseline.py`, which
executes BT1–BT6 and writes `fixtures/baseline_results.json` (plus the BT5/BT6
record fixtures). Tests read `/root/arifOS` source read-only; if that tree is
absent, BT0/BT1/BT4 report BLOCKED instead of guessing.

## Expected outputs
- BT1: `actor_verified` is a plain bool, default False (L1/L2 measured)
- BT2: spoofed `actor_verified:true` is not re-derived by any signature gate (L1/L2)
- BT3: `verdict=HOLD`, `can_claim_success=false`, `transport.response_completed=true` coexist in the event (L1/L2)
- BT4: `reason_code` vocabulary enumerated; nullable cause gap recorded (L1/L2)
- BT5: sink set-divergence detected despite equal counts (L1/L2)
- BT6: steps 5–9 fixture-reproduced; steps 1–4, 10 deferred to an outsider (L1/L2)
- No mutation of any target — design invariant, see `BASELINE_RESULTS.md`

## Failure modes
- Any BT requiring private federation access: the BT fails and the independence
  criterion fails.
- Any BT requiring a live mutation: the BT is invalid.
- A baseline test that passes while the current substrate is known broken: the
  test is invalid.
- Non-zero exit from `run_baseline.sh`: fail-closed — treat as failure.
