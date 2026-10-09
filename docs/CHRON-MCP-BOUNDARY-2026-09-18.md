# CHRON Organ ≠ CHRON MCP — Boundary Decision

> Author: ARIF (F13 sovereign)
> Date: 2026-09-18 12:40 MYT
> Status: REFERENCE (not ratified)
> Refines: CHRON-LAYER-ARCHITECTURE-2026-09-18.md

## Decision

CHRON starts as an organ, not an MCP.

Same pattern as GEOX ≠ GEOX MCP, WELL ≠ WELL MCP, WEALTH ≠ WEALTH MCP.

## CHRON Organ (continuous process)

Runs continuously, observing and metabolizing:

```
NATS signal → Observer → ChronEpisode Store → Prediction Store → Calibration Store
```

Lifecycle: observe → predict → verify → learn (always running)

## CHRON MCP (query interface, separate)

Provides read access to other organs:

```
CHRON Organ → Chron Store → CHRON MCP (query API)
```

Example queries:
- What changed since yesterday?
- Show open predictions.
- What lessons came from GEOX?
- What prediction failed last month?
- What was believed on date T?

## Test: If MCP dies, does capability die?

- GEOX: Yes (MCP is the access layer)
- WELL: Yes
- GitHub: Yes
- CHRON: No — capability lives in episodes/predictions/verification/calibration, not in transport

## Key Metaphor

arifFLOW = circulation (moves things)
CHRON = digestion (transforms things)

CHRON is downstream. It takes events and metabolizes them.

## Anti-Pattern Avoided

If CHRON starts as MCP, it absorbs: memory + prediction + learning + temporal reasoning + calibration → "everything server."

Starting as organ keeps the boundary clean and entropy low.
