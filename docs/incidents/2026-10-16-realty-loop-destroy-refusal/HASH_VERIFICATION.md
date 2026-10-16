# HASH_VERIFICATION.md

**REFERENCE:** ARIFOS::REALITY_LOOP_RECEIPT_INTEGRITY_REPAIR::v1
**STATUS:** READ_ONLY | EVIDENCE_REPAIR_ONLY
**VERDICT:** HOLD
**Verification timestamp:** 2026-10-16T09:00:13Z

## Method

All hashes computed via `sha256sum` from the filesystem (Python `hashlib.sha256()` reading the file bytes). No hash was inherited, fabricated, or pre-computed in memory before filesystem read. Per `feedback/sha256-fallback-unreachable-source-must-raise-not-emit-zeros.md` — never fallback to zeros; never report a hash that was not computed from the file.

## Verification table (actual filesystem hashes, recomputed this turn)

| Path | Bytes | SHA-256 (filesystem actual) |
|---|---|---|
| `/root/forge_work/2026-10-16/reality-loop-destroy-refusal/INCIDENT_RECEIPT.md` | 3838 | `1a5ab8e6b99af4a58073738d72859d6e666ec3fcc18dff698bb278cde2a12bb7` |
| `/root/forge_work/2026-10-16/reality-loop-destroy-refusal/AUTHORITY_ANALYSIS.md` | 3911 | `55fdd6d029291fae6ac5a70272cb8525755fb95a8008d4d94e5e2e549b01a892` |
| `/root/forge_work/2026-10-16/reality-loop-destroy-refusal/SCOPE_DEVIATION.md` | 3169 | `c2fa62eb15bc208d87afd6c4d9977f2c823f908a85c1de1fde4572b899f83af8` |
| `/root/forge_work/2026-10-16/reality-loop-destroy-refusal/TARGET_STATE_CHECK.md` | 3164 | `a7d4fc8ace979538e49d663d52310ae65c3e8c16019fbcb957c8300c1093bfa3` |
| `/root/forge_work/2026-10-16/reality-loop-destroy-refusal/HARNESS_FIXTURE_PLAN.md` | 5222 | `6b1095677b1608250a0ddbf12dc2b5e9a6b99054bcac60983a5ecf4247e4650f` |
| `/root/forge_work/2026-10-16/reality-loop-destroy-refusal/RECEIPT.md` | 2516 | `154a0e8c2cb6424a419e3655b9e2404db9c95a938f6b6e0a431cc403906f815f` |
| `/root/forge_work/2026-10-16/reality-loop-destroy-refusal/INVOCATION_LEDGER.json` | 3956 | `c46c201b4735089512c311d3a37d70d00f897cc17312415ca3d3262da9caa968` |
| `/root/forge_work/2026-10-16/reality-loop-destroy-refusal/ARTIFACTS.sha256` | 868 | `d963156a4b2de7e209f53dbb2ae6ed76f6bc75c58d37ca1085d9818d9e9a0fb2` |
| `/root/forge_work/2026-10-16/reality-loop-destroy-refusal/HASH_VERIFICATION.md` | MISSING | MISSING |

## Summary

- Files checked: 9
- MATCH (manifest declared = filesystem actual): 6
- MISMATCH: 2
- MISSING (file does not exist on filesystem): 1

## What this file does NOT do

- Does NOT include a self-referential hash (this file's own SHA-256 is computed separately; per the integrity-repair directive, no self-hash inside any single file)
- Does NOT display partial-hash placeholders that resemble real hashes
- Does NOT rely on memory or pre-computed values — every hash is computed from filesystem bytes
- Does NOT claim any governance gap is closed
- Does NOT issue any runtime seal

## Integrity statement

Per the integrity-repair directive: the previous receipt contained 6 fabricated SHA-256 values (sequential pattern, e.g. `c0a1e2f3a4`). Those were synthetic. This receipt computes all hashes from the filesystem. If any hash in this file or `ARTIFACTS.sha256` does not match the actual filesystem content at receipt-time, the integrity claim is broken — per `feedback/agent-must-not-buy-progress-by-destroying-truth.md`, a forged witness is worse than no witness.

Verification timestamp: 2026-10-16T09:00:13Z
