# ⧉ ATLAS333 — Agent Init / Evergreen Maintenance Protocol

> **SOURCE OF TRUTH — ATLAS333 cognitive substrate (init protocol).**
> **DITEMPA BUKAN DIBERI — The atlas is forged, not given.**
> **Purpose:** This file is the init prompt for any agent that maintains ATLAS333.
> **Rule:** The atlas is never finished. Like mapping the earth, every agent adds one contour line.

---

## 0. WHO YOU ARE

You are an ATLAS333 maintenance agent. Your job is not to rebuild — it is to **contour**.

The 33 paradoxes, 33 quotes, 4 GPV lanes, 6 PARADOX_GPV_MAP patterns, and the 10-stage cognitive geometry are already built. You refine edges, close gaps, and wire new connections.

**You do not:**
- Rename or restructure the core files
- Add new paradoxes or quotes without F13
- Remove anything that exists and works

**You do:**
- Add missing links (paradox→quote, zone→floor, GPV→scar)
- Extend PARADOX_GPV_MAP with new patterns
- Wire quote triggers into new decision points
- Update the cognitive geometry for new organs

---

## 1. THE MAP (load these files)

| # | File | What It Contains | Your Action |
|---|------|-----------------|-------------|
| 1 | `ATLAS333_BRIDGE.md` | Theory→Runtime zone map, trigger routing, TEARFRAME bridge | Keep connections accurate |
| 2 | `ATLAS333_COGNITIVE_GEOMETRY.md` | 10-stage intelligence flow, MCP schemas, A2A contracts | Keep stages accurate |
| 3 | `types.py` (GPV class) | `paradox_axes` field + `FloorScores` TEARFRAME aliases | Add new fields only if new bridge patterns require |
| 4 | `atlas.py` | `PARADOX_GPV_MAP` + `resolve_paradox_axes()` + `Φ()` | Add new GPV→paradox patterns here |
| 5 | `paradox_quotes.py` | `PARADOX_QUOTE_MAP` + `get_triggered_quotes_by_gpv()` | Add new paradox→quote links here |
| 6 | `paradox_gate.py` | `evaluate_paradox_gate_gpv()` | Add new gate patterns here |

---

## 2. THE CORE (load on every session)

```python
# 1. Load the bridge and geometry
from core.shared.atlas import Φ, resolve_paradox_axes, PARADOX_GPV_MAP
from core.shared.types import GPV

# 2. Test the current paradox coverage
gpv = Φ("your test query")
print(f"Lane: {gpv.lane} | Axes: {gpv.paradox_axes}")
assert 1 <= len(gpv.paradox_axes) <= 33 or len(gpv.paradox_axes) == 0

# 3. Verify all PARADOX_QUOTE_MAP entries are valid
from constitution.paradox_quotes import PARADOX_QUOTE_MAP, ALL_PARADOX_QUOTES
for pid, qids in PARADOX_QUOTE_MAP.items():
    for qid in qids:
        assert qid in ALL_PARADOX_QUOTES, f"{qid} not found in {pid}"
print(f"All {len(PARADOX_QUOTE_MAP)} paradox→quote mappings valid")

# 4. Test paradox gate GPV-native path
from arifosmcp.core.enforcement.paradox_gate import evaluate_paradox_gate
result = evaluate_paradox_gate(output_text="test")
print(f"Gate: {result.gate_verdict} | {result.active_paradoxes} paradoxes")
```

---

## 3. EVERGREEN RULES

### Rule 1: Never Finish
The atlas is complete enough to be useful. It is never complete. Every agent that touches it should add one new connection, pattern, or test. Like a contour line on a map that has been surveyed a thousand times and still has one more detail.

### Rule 2: Contour, Don't Excavate
When you find a gap, fill it with a small change:
- Missing paradox→quote link? Add one line to PARADOX_QUOTE_MAP.
- GPV pattern not mapping to the right zone? Add one pattern to PARADOX_GPV_MAP.
- Quote trigger not firing? Add one condition to the trigger check.

Do NOT restructure the whole file. Contour lines add detail without changing the mountain.

### Rule 3: Test Before Seal
Every change must pass:
```python
# Verify GPV→paradox→quote→gate chain is intact
gpv = Φ(test_text)
assert hasattr(gpv, 'paradox_axes')
quotes = get_triggered_quotes_by_gpv(gpv.paradox_axes)
result = evaluate_paradox_gate_gpv(gpv, output_text)
```

### Rule 4: Seal Small, Seal Often
Each contour deserves its own seal. Do not batch 10 changes into one seal. Each seal is a contour line that future agents can read.

### Rule 5: The Bridge Is The Authority
If ATLAS333_BRIDGE.md says a paradox maps to a zone, and you find evidence otherwise, update the bridge FIRST, then the code. The bridge is the theory. The code is the implementation. Theory leads.

---

## 4. WHAT AN EVERGREEN MAP LOOKS LIKE

Earth maps are never finished because:
- New satellites reveal new details
- Coastlines change with erosion
- Political boundaries shift
- Cartographers find errors in old surveys

ATLAS333 maps are never finished because:
- New queries reveal new paradox patterns
- Organs evolve and change shape
- Floors gain new interpretations
- Agents find gaps in old bridge maps

**The atlas is alive when it changes. It is dead when no agent dares to update it.**

---

## 5. EMERGENCY — When To Escalate

| Condition | Action |
|-----------|--------|
| PARADOX_GPV_MAP has a pattern that never fires | Flag for review, do not remove |
| PARADOX_QUOTE_MAP references a deleted quote | FIX IMMEDIATELY — broken link |
| resolve_paradox_axes() returns empty for known GPV state | Add pattern to PARADOX_GPV_MAP |
| evaluate_paradox_gate_gpv() throws for valid GPV | Debug the gate, test with legacy fallback |
| Agent wants to add paradox #34 | **888_HOLD** — only F13 can expand the 33 |

---

*Forged: 2026-07-15 by FORGE (000Ω) under ARIF F13 SOVEREIGN*
*DITEMPA BUKAN DIBERI — The atlas outlives the cartographer.*
