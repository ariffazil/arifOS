# Memory Rotation Policy
**Authority:** 888_JUDGE | **Floor:** F4 Clarity (ΔS ≤ 0) | **Sealed:** 2026-04-08

## Rule
Memory files in `memory/` are **session-scoped operational context**.

| State | Condition | Action |
|---|---|---|
| `active` | File date = today | Keep in `memory/` |
| `expired` | File date < today | Archive to `archive/memory/YYYY/MM/` |
| `compress` | Monthly accumulation | Synthesize into `wiki/log.md` session summary |

## TTL
**1 session = 1 day.** Previous day's file expires at next session open.

## Rotation trigger
At each new session init (`000_INIT`/`arifos_init`), archive all `memory/*.md` where
filename date < today.

## Destination
```
archive/memory/YYYY/MM/<filename>.md
```

## Synthesis cadence
At month boundary: compress `archive/memory/YYYY/MM/*.md` into a single
`wiki/log.md` monthly-summary entry.
