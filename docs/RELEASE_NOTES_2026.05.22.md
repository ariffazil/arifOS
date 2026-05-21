# RELEASE NOTES - arifOS v2026.05.22-pre

> **Pre-release date:** 2026-05-22  
> **Evidence date:** 2026-05-21  
> **Status:** PRE-RELEASE / PR REVIEW  
> **Authority:** Arif final judgment, arifOS constitutional governance

## Purpose

This pre-release lowers repo entropy and keeps arifOS honest as the constitutional governance kernel. It preserves the fail-closed ZKPC quarantine boundary instead of overstating proof authority.

## Changed

- Shared federation layout contract repaired and normalized in `docs/AGENT_LAYOUT_CONTRACT.md`.
- Repo hygiene audit ledger added at `docs/REPO_HYGIENE_AUDIT_2026-05-21.md`.
- Future Hermes session briefing files ignored by default.
- MSAP/ZKPC tests updated to assert the current toy-circuit quarantine contract:
  - cryptographic toy proofs may verify structurally.
  - quarantined toy circuits carry zero constitutional authority.
  - irreversible flows remain `888_HOLD` unless production ZKPC authority is deployed.

## Verification

```txt
git diff --check: PASS
pytest tests/runtime/test_msap_ack.py tests/runtime/test_zkpc_v2.py -q: PASS (31/31)
python -m pytest tests/ -q --tb=short: PASS (1939 passed, 18 skipped)
```

## Boundary

arifOS owns constitutional law, governance, judgment routing, and audit semantics. It does not own the UI cockpit, general execution runtime, Earth evidence, or capital evidence.

## Release Note

This is a pre-release branch, not a direct push to `main`. It does not lift ZKPC quarantine.

Ditempa Bukan Diberi.
