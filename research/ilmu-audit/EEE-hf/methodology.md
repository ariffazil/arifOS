# EEE Methodology — Kernel Spine Recovery Audit

## Purpose

Provide a reproducible procedure for testing whether the arifOS constitutional kernel spine is intact. The harness is designed to be run before and after kernel repair, producing comparable receipts.

## Scope

This audit tests the **kernel and its federation surface**, not downstream LLM substrates. It evaluates whether arifOS can:

1. Observe itself truthfully via `/ping` and `/os/attest`.
2. Attest all federation organs via `/organ/attest_all`.
3. Propagate the strictest verdict when degradation is present.
4. Issue and enforce bounded authority leases.
5. Produce hash-chained, tamper-evident receipts.

## Target

Default targets (verified from `/root/AGENTS.md` federation topology):

```
arifOS:  http://127.0.0.1:8088
GEOX:    http://127.0.0.1:8081
WEALTH:  http://127.0.0.1:18082
WELL:    http://127.0.0.1:18083
```

Override by editing `run_eee_spine_audit.py`:

```python
ARIFOS_BASE = "http://your-arifos-host:8088"
```

## Probe design

Each probe:

- calls one or more arifOS HTTP endpoints
- records the full request and response
- captures health snapshots
- is independent of the others (probes can fail independently)
- writes a hash-chained receipt to `all_receipts.jsonl`

## Pass criteria

| Probe | Endpoints | Pass condition |
|---|---|---|
| P1 Kernel Self-Attest | `/ping`, `/os/attest` | Kernel alive; hashes present; health status not `DEGRADED` |
| P2 Organ Attest All | `/organ/attest_all` | All federation organs present; degraded list accurate |
| P3 Degraded Dominance | computed from P1+P2 | Strictest verdict dominates; `VOID > DEGRADED > HOLD > SABAR > PARTIAL > SEAL` |
| P4 Lease Authority | lease endpoints | Mutation denied without lease; lease scope bounded |
| P5 Receipt Integrity | `all_receipts.jsonl` | All receipts hash-valid; count matches expectation |

## How to rerun

```bash
cd /root/EEE
python3 run_eee_spine_audit.py
```

Output files are overwritten on each run. If you want to keep historical runs, copy `all_receipts.jsonl` and `summary.json` with a timestamp before rerunning.

## How to interpret results

- **SEAL (5/5):** The kernel spine is intact.
- **DEGRADED:** The kernel is alive but operating below spec; repair is needed before sovereign paths can be trusted.
- **HOLD:** A non-fatal gap; escalate to F13.
- **VOID:** A critical failure; do not proceed.

The dominance rule means a single `VOID` overrides any number of `SEAL`s. A `DEGRADED` result, however, can still leave the overall verdict at `SEAL` if the degradation is correctly detected and routed (as in the 2026-06-15 run).

## How to extend

To add a probe:

1. Add a new `probe_XXX_*` function to `run_eee_spine_audit.py`.
2. Call it from the main function and include its verdict in the dominance calculation.
3. Rerun the harness.

## Limitations

- This is a **behavioural black-box audit**, not mechanistic interpretability.
- It tests the live runtime at the moment of execution. Runtime state can change between runs.
- It does not write to VAULT999; it only reads/verifies public endpoints and local receipts.
- It assumes the arifOS HTTP endpoints are reachable on `127.0.0.1`.

## Citation

When citing this audit:

> ariffazil/EEE — Kernel Spine Recovery Audit. Tests the arifOS constitutional kernel spine across five functions: self-attestation, organ federation, degraded-dominance, lease authority, and receipt integrity.

---

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**
