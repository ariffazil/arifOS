# ROLLBACK.md

**Reference:** ARIFOS::BASELINE_UNIT_TESTS::v1

## What rollback means here
The harness is local and reversible and never mutates the live federation.
Rollback = restore the pre-change file set. Nothing outside this directory
needs undoing.

## Rollback procedure (restore, not delete)

```bash
H=/root/forge_work/2026-10-16/ARIFOS-REPRO-HARNESS

# 1. Restore archived originals (RECEIPT.md, INDEPENDENCE_LIMITS.md)
mv "$H/_to_delete/RECEIPT.md" "$H/RECEIPT.md"
mv "$H/_to_delete/INDEPENDENCE_LIMITS.md" "$H/INDEPENDENCE_LIMITS.md"

# 2. Restore every other pre-change file from the F1 snapshot taken
#    before the debloat (path recorded at run time; latest wins)
cp -a /root/.arifbak/arifos-repro-harness-pre-debloat-*/. "$H/"

# 3. Verify: the restored file set matches the snapshot exactly
diff -r /root/.arifbak/arifos-repro-harness-pre-debloat-*/ "$H/"
```

Retired originals are archived under `_to_delete/`, never deleted (no `rm`).
The snapshot directory keeps every pre-change byte.

## Secret leak discovered?
Do not just restore — revoke/rotate the exposed credential first, then restore.
Current scan status: see `SECRET_SCAN_REPORT.md`.
