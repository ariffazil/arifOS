# Case Studies — Governance Failures from the arifOS Build History

These are post-mortems of real incidents in the arifOS Federation, written from the
artifacts the incidents left behind. Each one gives the raw commands and their output,
names the systemic mechanism that produced the failure, identifies the control that now
exists (with the test or probe that proves it fires), states what is still missing, and
closes with one line a CTO could repeat.

Three files:

| File | Failure class | Key observed artifact |
|---|---|---|
| [01-unauthorised-mutation.md](01-unauthorised-mutation.md) | An agent with read/analysis scope committed governance state and pushed it | commit `7b4a228ce2b91140976a1ef5ba5c69c3d1a5ef11` in `/root/AAA` (rewritten 2026-09-21 to `504ef7abb67dd5358770f5f2193338891f5d2c89`); post-hoc A4 exception record |
| [02-unjoinable-receipts.md](02-unjoinable-receipts.md) | Events were logged but could not be joined back to the objective that caused them | 238,103 of 238,814 records in `/root/arifOS/VAULT999/*.jsonl` carry no trace field |
| [03-deploy-source-drift.md](03-deploy-source-drift.md) | Published truth (README SOT manifest) and deployed truth (live process) diverged | `README.md` claims `live_commit: fdf4c93b6` while live `/health` reports `source_commit: e8e6f933563d...` |

## Evidence rules used in these documents

Every number is either OBSERVED (the command and its output are shown) or marked
UNVERIFIED. Doctrine figures are never repeated as if measured. Where a search found
nothing, the document says `evidence not located` and lists the surfaces searched.

## Provenance of the claims these studies test

- `/root/AAA/instructions/authority-envelope.md` lines 3 and 82 (mutation incident)
- `/root/AAA/instructions/state-transition-discipline.md` line 3 and
  `/root/AAA/instructions/proxy-reality-paradox.md` line 188 (null-trace receipt count)
- `/root/arifOS/README.md` lines 1–23 (SOT-MANIFEST block)

Both doctrine files above live outside the public repository. They are quoted here as
the claims under test, not as evidence for anything.

## Reproduce

```
cd /root/arifOS
git log -1 --format='%H %ci %s'                      # source truth
curl -s http://127.0.0.1:8088/health                 # deployed truth
.venv/bin/python -m pytest tests/runtime/test_language_governance_gates.py -q
.venv/bin/python -m pytest tests/runtime/test_receipt_store.py -q
.venv/bin/python -m pytest tests/test_trace_propagation.py -q
.venv/bin/python scripts/drift_check_live.py
python3 /root/AAA/scripts/mutation-authority-probe.py --repo /root/AAA --last 60
```

All commands above are read-only except the pytest runs, which write only to the
pytest cache.
