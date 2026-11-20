# W3 Honest Investigation — 2026-11-20

## Current W3 Value: 0.5291

### Formula
```
W3 = ∛(Earth × AI × Human)
```
Where:
- **Earth** = organ port reachability (15/15 = 1.0)
- **AI** = fraction of tools passing fresh capability tests (6/9 = 0.6667)
- **Human** = fraction of JSONL rows with `human_witness: true` (2/9 = 0.2222)

```
W3 = ∛(1.0 × 0.6667 × 0.2222) = ∛(0.1481) = 0.5291
```

Threshold: **0.75** (constitutional — NEVER lower)

---

## Leg-by-Leg Analysis

### Earth Witness: 1.0 (MAXED)
- **What it measures**: All 15 registered organ ports return 200 on `/health`
- **Current state**: 15/15 up
- **Can it improve?**: NO — already at ceiling. 1.0 is the hard maximum.
- **Evidence**: `probe_earth_witness()` in `witness_producers.py` scans `ORGANS_SOT`

### AI Witness: 0.6667 (6/9 tools passing fresh)
- **What it measures**: Tools in `capability-test-cache.json` with `outcome: "PASSED"` and `last_pass: true` within freshness window (default 24h)
- **Current breakdown**:
  - PASSED (6): arif_forge, arif_init, arif_observe, arif_route, arif_seal, arif_think
  - HELD_BY_AUTHORITY (3): arif_judge, arif_memory, arif_report — correctly refused unverified actors, NOT counted as passes
  - Total: 9 tools
- **Can it improve?**: YES — if the 3 held tools are invoked with verified actors and return PASSED, AI → 1.0
- **Legitimate lever**: Fix upstream callers to present verified bindings; the tools themselves work correctly
- **What would be cheating**: Count HELD_BY_AUTHORITY as passes (the code explicitly excludes them with a comment explaining why)

### Human Witness: 0.2222 (2/9 rows in JSONL)
- **What it measures**: Rows in `human_witness.jsonl` (or configured sources) with `human_witness: true`
- **Current state**: 2 witnessed rows out of 9 total rows
- **Source file**: `/var/lib/arifos/human_witness.jsonl` (configured in `HUMAN_WITNESS_SOURCES`)
- **Can it improve?**: **FUNDAMENTAL PROBLEM** — the instrument is a manual JSONL file with 9 entries, 2 marked true. This is NOT a live human witness instrument.
- **Root cause**: `probe_human_witness()` reads a static file. No biometric inject, no sensor-verified data, no live human-in-the-loop.
- **What would be cheating**:
  - Adding fake `human_witness: true` rows to the JSONL
  - Hardcoding a higher value
  - Using a proxy (e.g., "human is alive" = 1.0)
  - Changing the formula to not require all three legs

---

## Legitimate Levers to Raise W3

| Lever | Current | Potential | Effort | Honest? |
|-------|---------|-----------|--------|---------|
| Fix AI witness (verified actor calls) | 0.6667 | 1.0 | Medium | ✅ Yes — tools work, callers need verified bindings |
| Build REAL human witness instrument | 0.2222 | 1.0 | High | ✅ Yes — requires biometric/sensor pipeline |
| Earth witness | 1.0 | 1.0 | N/A | Already maxed |

### Best-Case Honest W3
If AI → 1.0 and Human → 1.0 (real instrument built):
```
W3 = ∛(1.0 × 1.0 × 1.0) = 1.0
```

### Realistic Near-Term W3
If AI → 1.0 (verified actor calls fixed) but Human stays at 0.2222 (fake instrument):
```
W3 = ∛(1.0 × 1.0 × 0.2222) = 0.605
```
**Still below 0.75 threshold.**

### Conclusion
**W3 cannot honestly pass 0.75 until a REAL human witness instrument exists.** The current JSONL file is a placeholder, not an instrument. No code change can fix this — it requires a new organ/pipeline for sensor-verified human biometric/state injection.

---

## What I Did NOT Implement (And Why)

1. **Auto-increment human witness from JSONL** — Would be fabricating evidence. The 2/9 ratio reflects reality: only 2 manual entries exist.

2. **Proxy human witness from "human is present"** — Would be cheating. Presence ≠ witnessed verification.

3. **Lower W3 threshold** — Constitutional prohibition. Threshold is 0.75.

4. **Change formula to geometric mean of 2 legs** — Would violate tri-witness architecture (Earth, AI, Human).

5. **Count HELD_BY_AUTHORITY as AI passes** — Code explicitly documents why this is dishonest: a correct refusal is not a demonstrated capability.

---

## Recommendation

**ANALYSIS ONLY** — No code changes for W3. The bottleneck is the human witness instrument, which requires a new pipeline (biometric inject → ledger → witness probe), not a code tweak.

The AI witness (0.6667 → 1.0) is fixable by ensuring verified actors call the 3 held tools, but even that alone only raises W3 to 0.605 — still failing.

**Honest path forward**: Build the human witness instrument (WELL biometric pipeline → human_witness ledger → probe reads ledger). Until then, W3 honestly reports 0.5291.