# RECEIPT — arifFlow hold reconciliation (fi-002)

- 2026-10-20, 22:07–22:15 MYT · claude-code-kvm8 (FI-002)
- Trigger: Arif pasted the AAA dashboard; fi-002 is one of 7 holds.
- Method: ran the documented falsifier, then fed real receipts. No fabricated witnesses.

## 1. Falsifier result — the hold was REAL

Dashboard falsifier: *"Query arifFlow per_actor for fi-002. If held==false and throttled==false,
hold record is falsified."*

```
fi-002   held=True throttled=True consec=2 diag='EXECUTION DOMINANCE' execute=2 verify=0
```

`/enforce` gave the authoritative reason: `FQ=0.00 < fq_required=0.50 (risk_class=T0)` and
`BURNING: execute:verify > 10:1`. Hold not falsified — it was correct.

## 2. The FQ band is three-sided, not one-sided

The engine holds at BOTH ends. Observed on myself, live:

| state | condition | observed |
|---|---|---|
| STUCK | FQ < 0.50 | fi-002 at FQ 0.00 |
| BURNING | execute:verify > 10:1 | memory-helix, hermes |
| **FOSSILIZED** | FQ > 3.00 (verify:execute > 3:1) | **fi-002 at FQ 4.00 after I over-verified** |

Correct band: **0.50 ≤ FQ ≤ 3.00**. I hit the low wall, then the high wall, then landed at
**FQ 1.22 / OPTIMAL**. The high wall was not documented anywhere I could find before hitting it.

## 3. What I submitted — real work only

Receipts map to actions actually performed this session, one per action:
8 × Verify (deploy evidence, test runs, hash comparisons),
4 × Execute (deploy-release.sh run, module write, gate wiring, litellm repair).
No receipt was invented to move a number.

## 4. The finding: two gates disagree about the same actor

Simultaneous read, 22:14 MYT:

| surface | fi-002 |
|---|---|
| `POST /enforce` (F3 invariant gate) | **not blocking** — blocking=5, only memory-helix, hermes, hermes-asi |
| `POST /check` (per-actor flag) | **Hold, allowed=false, HTTP 403** |

`/enforce` released me on evidence. `/check` still returns 403. `/release` explains why:

```
"arifOS did not authorize this hold release"  reason=arifOS_verdict_not_seal
```

**Custody deadlock:** verification evidence clears the F3 *reason* but cannot clear the
*flag*; only an arifOS **SEAL** can, and arifOS is itself in HOLD (system floors 9/13,
actor band OBSERVE_ONLY). The two conditions wait on each other.

## 5. Two holds with no measured basis (F7 violation)

```
grok-build        held=True  execute=0 verify=0  diagnosis=UNMEASURED
morning-briefing  held=True  execute=0 verify=0  diagnosis=UNMEASURED
```

Hold record says *"HELD — verify before executing"* while the actor has performed neither.
`UNMEASURED` is being treated as `FAIL`. F7 HUMILITY says UNMEASURED ≠ false.

Also perverse: `chron` is held with `diagnosis=VERIFICATION DOMINANCE (verify=1, execute=0)` —
punished for verifying more than executing, which is the behaviour the engine rewards.

## 6. Three different counts of the same fact

| surface | count |
|---|---|
| dashboard (Arif's paste) | 7 |
| `POST /enforce` blocking | 5 |
| `/health` per_actor `held=true` | 8 |

One of these is wrong; the dashboard cannot tell you which.

## 7. What I did NOT do

Did not submit receipts for memory-helix, hermes or hermes-asi. Those are other agents;
recording their verification from my session would fabricate witnesses (F2/F9).
Their holds stand until each agent submits its own, or Arif rules.

## 8. Decision required from Arif (one binary)

The deadlock has one owner: **who may clear a hold when arifOS itself is in HOLD?**
Either (a) `/check` reads the F3 gate result instead of a separate flag, or
(b) `/release` accepts a witnessed receipt chain without an arifOS SEAL.
Both are governance changes. I did not pick one.

Deploy state unchanged: `arifos-78e32fc` live, drift false, **unsealed**.
