# arifos.sense — Governed Sensing Protocol

**Constitutional Seal:** 999_VALIDATOR  
**Author:** Arif (Sovereign Architect)  
**Date:** 2026-04-07

---

## Executive Summary

`arifos.sense` has been upgraded from a **bare web search tool** to a **constitutional intake layer** for reality claims.

**Before:** "Go search the internet"  
**After:** "Classify, decide, plan, then retrieve only what is needed"

---

## New Mode: `governed`

The `governed` mode implements the 8-stage constitutional sensing protocol:

```
PARSE → CLASSIFY → DECIDE → PLAN → SENSE → NORMALIZE → GATE → HANDOFF
```

### Usage

```python
# Governed sensing (NEW — constitutional protocol)
result = await arifos.sense(
    mode="governed",
    query="Who is the current CEO of OpenAI?"
)

# Legacy modes (still available)
result = await arifos.sense(mode="search", query="...")   # Bare web search
result = await arifos.sense(mode="ingest", query="...")   # URL fetch
result = await arifos.sense(mode="compass", query="...")  # Auto-detect
result = await arifos.sense(mode="time")                  # Temporal grounding
```

---

## 8-Stage Protocol

### Stage 1: PARSE
Extract structured fields from the query:
- **entity**: What is being asked about
- **claim_type**: definition | status | prediction | comparison | instruction
- **time_class**: timeless | dated | live | recent
- **domain**: physics | law | finance | software | geopolitics
- **risk_class**: low | medium | high | critical
- **decision_proximity**: informative | decision_critical

### Stage 2: CLASSIFY
Route to truth-class lane:

| Lane | Truth Class | Handling |
|------|-------------|----------|
| A | `absolute_invariant` | Offline reasoning only (math, logic, physics) |
| B | `conditional` | Frame-dependent (jurisdiction, version) |
| C | `operational` | Principles + selective evidence (strategy) |
| D | `time_sensitive` | Live search required (events, prices) |
| E | `hold` | Too ambiguous — requires narrowing |

### Stage 3: DECIDE
Determine if search is needed:
- **Invariant queries** → No search (first principles suffice)
- **Live queries** → Search with freshness constraints
- **Ambiguous queries** → HOLD (no search until clarified)

### Stage 4: PLAN
Build evidence hierarchy:

| Rank | Evidence Type | Use Case |
|------|--------------|----------|
| 1 | Direct measurement / primary data | Strongest grounding |
| 2 | Official source / issuer | Laws, releases, policies |
| 3 | Technical documentation / standards | Specs, methods |
| 4 | Reputable secondary reporting | Summaries |
| 5 | Social chatter / SEO pages | Weak signal only |

### Stage 5: SENSE
Execute constrained retrieval based on plan:
- Respect `minimum_rank`
- Apply `freshness_hours` limits
- Use `preferred_sources` only

### Stage 6: NORMALIZE
Convert raw results to structured claims with provenance.

### Stage 7: GATE
Assess uncertainty: `low` | `moderate` | `high` | `unknown`

### Stage 8: HANDOFF
Determine next stage based on packet state.

---

## Output: SensePacket

```json
{
  "query": "Who is the current CEO of OpenAI?",
  "truth_class": "time_sensitive",
  "search_required": true,
  "time_class": "live",
  "evidence_plan": {
    "preferred_sources": ["official company site", "stock exchange filing"],
    "minimum_rank": 2,
    "freshness_hours": 1
  },
  "evidence_bundle": [...],
  "grounded_facts": [...],
  "ambiguity": {"detected": false},
  "conflict_check": {"status": "none"},
  "uncertainty": "low",
  "handoff": {
    "next": "synthesize",
    "target": "arifos.mind",
    "reason": "Grounded evidence ready for synthesis"
  }
}
```

---

## Five Invariants

1. **Classify before searching** — Never search by reflex
2. **Evidence has hierarchy** — Rank 1 > Rank 5 always
3. **Time matters only for moving targets** — No freshness for timeless truths
4. **Ambiguity must be resolved or contained** — Surface uncertainty explicitly
5. **Conflict is signal** — Detect frame mismatches, don't average blindly

---

## Files Modified

| File | Change |
|------|--------|
| `sensing_protocol.py` | **NEW** — Full 8-stage governed sensing implementation |
| `tools_internal.py` | Added `governed` mode to `physics_reality_dispatch_impl` |
| `tool_08_physics_reality.py` | Updated docstring with governed mode documentation |
| `arifos.sense.json` | Added `governed` mode to schema, updated default mode |

---

## Bug Fix: compass Mode

Fixed `BundleInput(type="auto", ...)` → now correctly uses `type="query"` or `type="url"` with mode="auto".

---

## Design Principle

> **The invariant is not the source. The invariant is the protocol.**

Sources can change:
- Google today
- Some API tomorrow  
- Internal database later
- GEOX sensor feed next year

But `arifos.sense` remains stable if its governing law is stable:
- Classify truth type
- Determine whether freshness matters
- Rank evidence by grounding
- Contain ambiguity
- Preserve uncertainty
- Hand off only normalized observations

---

## One-Line Answer

**Web search is only a sensor. `arifos.sense` is the invariant constitutional protocol that decides whether search is even allowed, what counts as evidence, and how uncertainty is carried forward.**

🔐 **DITEMPA BUKAN DIBERI — Forged, Not Given**
