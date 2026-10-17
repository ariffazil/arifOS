# NETWORK_DEPENDENCIES.md

**Reference:** ARIFOS::BASELINE_UNIT_TESTS::v1

## Constraint (enforced)
The harness makes **no network calls**. `scripts/run_baseline.sh`,
`scripts/secret_scan.sh`, and `tests/test_baseline.py` open no sockets and
fetch nothing; tests run against local source imports and fixtures only.

## Forbidden (fail-closed)
- Package installs/downloads (`apt`, `pip`, `npm`, …)
- Any federation or private endpoint
- Any mutation endpoint
- Any service reload/restart command

## Future use
Any test that needs network must be added explicitly here, be read-only, and
justify itself. Nothing currently qualifies.
