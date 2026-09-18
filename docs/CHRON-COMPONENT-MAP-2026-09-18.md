# CHRON Component Map — Gemini's 4 Wajib vs Reality

> Date: 2026-09-18
> Status: OBS audit — what exists, what's missing, what needs wiring

## The 4 Wajib Tasks

### 1. CHRON-VERIFIER (The Falsification Engine)

| Aspect | Gemini's Spec | What Exists | Gap |
|---|---|---|---|
| Script | prediction_verifier.py | ✅ 10KB, reads predictions.json | — |
| Timer | Every 15-30 min | ⚠️ Daily at 07:00 MYT | Cadence too slow |
| Prediction store | predictions.json | ✅ 5 entries | — |
| Verification receipt | Confirmed/Refuted/Superseded | ❌ No verification output found | loop_log.jsonl empty |
| Calibration | Brier score | ❌ calibration.json missing | — |
| Reality source | FRAME/GEOX/WEALTH | ⚠️ Only reads chron_events.json | No live reality probe |
| Output | Verification Receipt → loop_log | ⚠️ Loop closer service exists but inactive | Service not fired yet |

**Verdict:** Script exists. Timer exists. But no verification has ever run. First fire: tomorrow 07:00 MYT.

### 2. CHRON-METABOLISM (Agent6 Shadow Learner)

| Aspect | Gemini's Spec | What Exists | Gap |
|---|---|---|---|
| Script | Reads verification receipts, drafts lessons | ⚠️ task0_reconciliation.py (different purpose) | No metabolism script |
| Timer | Daily end of day | ⚠️ task0 fires 06:50 (morning, not end of day) | Wrong time |
| Input | Verification receipts from Task 1 | ❌ No receipts exist yet | Depends on Task 1 |
| Output | Candidate Lesson → PHOENIX-72 queue | ❌ No candidate lesson generation | — |
| F1 Safety | Never auto-updates policy | N/A | Not implemented yet |

**Verdict:** task0_reconciliation is reconciliation (declared vs observed), not metabolism (pattern extraction from verification failures). Different function.

### 3. CHRON-PHOENIX (72-Hour Consolidation)

| Aspect | Gemini's Spec | What Exists | Gap |
|---|---|---|---|
| Middleware | phoenix_72.py | ✅ 21KB, full state machine | — |
| Timer | Daily, independent | ⚠️ chron-loop-closer at 07:15 | Shares timer slot |
| Input | Candidate lessons ≥72h old | ❌ No candidate lessons exist | Depends on Task 2 |
| Output | Promote to durable memory or void | ❌ No promotions yet | — |
| Holding queue | Where candidates sit for 72h | ❌ No queue implementation | — |

**Verdict:** PHOENIX-72 middleware exists and is well-designed. But it's never been exercised — no candidate lessons have entered the queue.

### 4. CHRON-ALIGNMENT-BRIDGE (Human Sync / Alpha-Zen)

| Aspect | Gemini's Spec | What Exists | Gap |
|---|---|---|---|
| Morning render | 06:00-06:30 MYT | ⚠️ shared.py + edge_midday.py | Partial |
| Afternoon render | 13:15 MYT | ⚠️ edge_midday.py (13:15 only) | Only midday |
| Night render | 21:00+ MYT | ❌ No night renderer | Missing |
| Input | carry_forward + prediction_store + PHOENIX queue | ⚠️ carry_forward.json exists | — |
| Output | Human language per contract | ❌ Current output violates contract | Dashboard style |
| Human language | Meaning first, no raw labels | ❌ Current: "WELL DEGRADED · SELF_REPORT" | Contract violation |

**Verdict:** Partial midday renderer exists. Morning and night missing. Output style violates the Human Language Rendering Contract.

## The Shared Context Ledger

Gemini's key insight: Tasks don't talk to each other. They write to and read from the same ledger.

| Ledger | Status | Contents |
|---|---|---|
| predictions.json | ✅ Exists | 5 entries (mixed format) |
| carry_forward.json | ✅ Exists | Temporal briefing data |
| loop_log.jsonl | ❌ Empty | No verification receipts yet |
| calibration.json | ❌ Missing | No calibration data |
| chron_events.json | ✅ Exists | 5+ events |
| task0_latest.json | ✅ Exists | Last reconciliation result |

## Wiring Map

```
CHRON-VERIFIER (Task 1)
  reads: predictions.json
  reads: chron_events.json (reality)
  writes: loop_log.jsonl (verification receipts)
  writes: calibration.json (accuracy stats)

CHRON-METABOLISM (Task 2)
  reads: loop_log.jsonl (verification receipts)
  writes: candidate_lessons.json (lessons to PHOENIX)

CHRON-PHOENIX (Task 3)
  reads: candidate_lessons.json (≥72h old)
  reads: chron_events.json (reality check during cooling)
  writes: durable_memory (lessons → policy)
  writes: void_log (lessons that decayed)

CHRON-ALIGNMENT-BRIDGE (Task 4)
  reads: carry_forward.json
  reads: predictions.json
  reads: candidate_lessons.json
  writes: human-facing output (DM to Arif)
```

## What's Missing (Critical Path)

| # | Component | Why Critical |
|---|---|---|
| 1 | loop_log.jsonl (empty) | No verification has ever happened |
| 2 | calibration.json (missing) | No accuracy tracking |
| 3 | candidate_lessons.json (missing) | No lesson generation |
| 4 | Night renderer | No evening alignment |
| 5 | Agent flow (0 agents read CHRON) | CHRON is invisible to federation |
| 6 | Organ registration | CHRON not in organs.yaml |
| 7 | MCP port | No health endpoint, no tool surface |

## What's Needed to Close the Loop

1. **Tomorrow 07:00 MYT:** prediction_verifier fires → first verification receipt → loop_log gets first entry
2. **Sep 23:** fuel-price-window prediction verified → first real calibration score
3. **After first verification:** metabolism script extracts patterns → candidate lessons
4. **After 72h:** PHOENIX-72 promotes or voids first lesson
5. **After first lesson:** alignment bridge presents to Arif in human language

The loop cannot close until Task 1 fires. Everything downstream depends on it.
