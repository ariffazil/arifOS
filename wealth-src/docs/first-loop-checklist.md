# First Governed Loop — Current Acceptance Checklist

> **Target:** One end-to-end WEALTH decision using the current packaged kernel (`server.py`).  
> **Epistemic:** CLAIM for structure, ESTIMATE for thresholds  
> **Status:** Phase A runtime checklist  
> **DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

---

## Pre-flight

- [ ] `python server.py` starts cleanly
- [ ] `WEALTH/data/vault999.jsonl` exists and remains append-only
- [ ] `npm test` passes
- [ ] No missing imports block `host/` runtime modules

---

## Step-by-step verification

### 1. Anchor session
- [ ] `wealth_init` returns a session anchor, runtime posture, or equivalent initialization payload
- [ ] Session metadata is explicit before downstream valuation work

### 2. Sense external state
- [ ] `wealth_ingest_sources` lists available source adapters
- [ ] `wealth_ingest_snapshot` or `wealth_ingest_fetch` returns a usable signal set for the target jurisdiction / series
- [ ] If source quality is weak, `wealth_ingest_health` or `wealth_ingest_reconcile` surfaces that weakness instead of hiding it

### 3. Establish baseline position
- [ ] `wealth_networth_state` returns a coherent balance-sheet view
- [ ] `wealth_cashflow_flow` returns coherent liquidity / runway state

### 4. Price the opportunity
- [ ] `wealth_npv_reward` returns NPV-style reward outputs
- [ ] `wealth_emv_risk` returns probability-weighted expected value
- [ ] `wealth_dscr_leverage` returns debt service coverage with clear flags where leverage is unsafe
- [ ] `wealth_payback_time` or `wealth_growth_velocity` can be used where temporal recovery matters

### 5. Audit entropy and governance
- [ ] `wealth_audit_entropy` surfaces non-normal flows, multiple-IRR risk, or other instability
- [ ] `wealth_check_floors` evaluates F1-F13 constraints on the candidate decision
- [ ] `wealth_policy_audit` applies explicit policy constraints without silent override

### 6. Form decision
- [ ] `wealth_score_kernel` returns a final WEALTH-side allocation verdict
- [ ] If multiple candidate actions exist, `wealth_allocate_optimize` ranks them coherently under constraints

### 7. Persist evidence
- [ ] `wealth_record_transaction` can append a transaction-style evidence record to VAULT999
- [ ] `wealth_snapshot_portfolio` can persist a snapshot of the evaluated result

---

## Failure-mode acceptance

| Failure | Expected behavior | Pass / Fail |
|---|---|---|
| Weak or stale external data | Ingest layer exposes health / reconciliation warnings | |
| Multiple IRR / unstable series | `wealth_audit_entropy` flags instability instead of pretending certainty | |
| Unsafe leverage | `wealth_dscr_leverage` escalates via flags / hold posture | |
| Policy breach | `wealth_policy_audit` or `wealth_check_floors` blocks or downgrades decision | |
| Missing evidence persistence | Transaction / snapshot tools refuse to imply durable recording | |

---

## Sign-off

Once the steps above pass on the **current** packaged kernel:

**Phase A runtime loop:** validated against repo SOT  
**Next move:** prove `Δbps_proven > 0` with a real capital decision

---

*Checklist v1.5.0 | Repo SOT aligned*
