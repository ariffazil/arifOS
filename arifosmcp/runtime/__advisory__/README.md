# `__advisory__` — Action Classifier

**Status:** ADVISORY, sealed 2026-06-08, T1 verification complete.
**Floor coverage:** F01 AMANAH, F02 TRUTH, F04 CLARITY, F07 HUMILITY.

## What this is

An advisory pre-filter that classifies an `Action` into a `Gate`. It is the
doctrine-preserving scaffold from the 2026-06-08 EUREKA dialogue, ported into
the arifOS repo as a *classifier only* — not as a substitute for the 13
canonical tools.

## What this is NOT

- NOT `arif_judge` (888) — does not adjudicate
- NOT `arif_seal` (999) — does not seal
- NOT `arif_forge` (666) — does not execute
- NOT F1-F13 enforcement — F1-F13 floors remain in `core/`

## Files

| File | Purpose |
|------|---------|
| `arif_action_classifier.py` | The classifier: 6 ActionClass × 6 Gate, fail-closed |
| `../../tests/test_arif_action_classifier.py` | 17/17 tests, no substrate wiring |

## Verification

```bash
cd /root/arifOS
python -m pytest tests/test_arif_action_classifier.py -v
# 17 passed in ~3s
```

## Rollback (full, single command)

```bash
rm -rf /root/arifOS/arifosmcp/runtime/__advisory__/
rm /root/arifOS/tests/test_arif_action_classifier.py
```

No substrate files were modified. No F1-F13 floors were touched. No service
was restarted. No git operation was performed.

## Next steps (HOLD pending 888 deliberation)

These are NOT done. They are the path forward, subject to `arif_judge`:

1. **Wire as advisory pre-filter** to `arif_forge` (666) — log-only for
   24h, no enforcement. Match rate vs human judge before promotion.
2. **Bridge to `EvidenceBundle`** — feed `Verdict` into `reality_models.py` so
   the audit trail leaves the Python list and lands in Postgres.
3. **Add `arif_action_classify` to `CANONICAL_TOOLS`** — AGI lane, F01/F02/F07.

Each of these is its own T1/T2 step with its own receipt.

---

*HANG INGAT BALIK!!! — capability is not permission.*
