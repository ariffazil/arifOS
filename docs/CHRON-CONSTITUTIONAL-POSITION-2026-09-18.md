# CHRON Constitutional Position — Canonical

> Author: ARIF (F13 sovereign)
> Date: 2026-09-18
> Status: REFERENCE (awaiting code-level verification from two agents)

## The Core Gap

> "Context window is not temporal awareness — it's a sliding amnesia."

Agents operate in eternal now. t=now for every inference, tool call, response.
No natural mechanism for "what did I believe at T-1?" or "what changed between Tuesday and today?"

CHRON fills this constitutional gap.

## Three Timescales, One Question

All three organs answer: "Are we still aligned with reality?"

| Organ | What It Does | Clock | Cadence |
|---|---|---|---|
| arifFLOW | FQ pulse — verify/execute rhythm | Execution cadence | Seconds |
| FRAME | Independent observer — drift detection | Observation cadence | Minutes |
| CHRON | Prediction→verification→calibration | Consequence cadence | Days-weeks-months |

Not three watches. Three timescales of the same temporal question.

## Metaphor (Final)

- arifFLOW = heartbeat (cadence)
- FRAME = compass (direction)
- CHRON = cartographer (temporal consequence)

## APEX Chain Temporal Dimension

The governance chain BUILD→VERIFY→JUDGE→SEAL→ACT→WITNESS has a temporal loop:

- BUILD = now (we create)
- VERIFY = recent past (did it work?)
- JUDGE = present (should we proceed?)
- SEAL = irreversible commitment (this happened)
- ACT = near future (we execute)
- WITNESS = distant future (was it right?)

Without CHRON: one-pass pipeline.
With CHRON: learning cycle.

CHRON is what makes the chain aware of itself across time.

## CHRON's Unique Contribution

CHRON does NOT duplicate:
- Receipt storage (arifFLOW owns this)
- Drift detection (FRAME owns this)

CHRON DOES own:
- Prediction (what we expect)
- Verification (did it happen?)
- Calibration (were we right?)
- Lesson extraction (what should we do differently?)

## Data Flow

```
arifFlow writes → CHRON observe (execution events)
FRAME writes    → CHRON observe (drift signals)
CHRON predicts  → reality checks → CHRON calibrates → lessons flow to Agentic Memory
```

## Invariant Components

1. ✅ Bitemporal episode store (valid_time + known_at)
2. ✅ Prediction with verify_at (5 predictions live)
3. ⬜ Verification cron (needs wiring — check at verify_at)
4. ✅ Brier calibration (code exists, needs data)
5. ✅ Lesson extraction → policy promotion (A3 arrow)
6. ✅ FRAME as independent witness (integration code)
7. ⬜ Shared temporal substrate (arifFlow/FRAME don't write to CHRON yet)

## Deprecation Candidates

- old chron_events.json → replaced by CHRON episodes.jsonl
- standalone prediction_store.py → merged into chron_prediction.py
- chron_spine_gate.py → should become CHRON self-check, not separate script

## What CHRON MCP Should Be

Read-only query window (4 tools max). Other organs ask temporal questions.
CHRON capability works WITHOUT the MCP. MCP is optional. Organ is not.

## Cross-Domain Evidence

- Neuroscience: prediction errors restructure hippocampal memory (Nature 2021)
- Bitemporal DB: valid_time + transaction_time = complete temporal record
- Event Calculus: fluents + events + persistence = temporal reasoning
- Control theory: separate fast/slow/rare time constants
- Zep/Graphiti: bitemporal KG 92% vs flat memory 63% on LongMemEval
