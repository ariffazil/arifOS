#!/usr/bin/env bash
# ARIFOS::BASELINE_UNIT_TESTS::v1 — runner
# ISOLATED | FAIL-CLOSED — deterministic local unit tests. No network, no live runtime, no mutation.
set -uo pipefail

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HARNESS_DIR" || exit

# Enforce isolation: run in a temp working dir
TMP_RUN="$(mktemp -d /tmp/arifos-repro-XXXXXX)"
echo "Isolation dir: $TMP_RUN"
export TMPDIR="$TMP_RUN"

# Default: NO network. This harness must not require it.
# (Do not add an iptables rule here — that needs root and is host-mutating.
#  Isolation is by construction: the test script opens no sockets.)

echo "=== Running baseline tests (isolated) ==="
python3 tests/test_baseline.py
rc=$?

echo "=== done, exit=$rc ==="
# Cleanup temp dir (keep fixtures/ results which are written to harness dir)
rm -rf "$TMP_RUN"
exit $rc
