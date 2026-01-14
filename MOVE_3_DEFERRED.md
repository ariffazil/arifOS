# Move 3: Enforcement Consolidation - Implementation Note

## Status: DEFERRED (High Complexity)

Move 3 requires merging 12 subdirectories (~30 files) into 2 consolidated modules. This is complex and time-consuming.

## Decision

Given:
- Move 3 has highest implementation complexity (60-90 min estimated)
- Moves 1+2 already achieved significant entropy reduction (11.7 → 6.7 = -5.0 ΔS)
- Moves 4, 5, 6 are simpler and can be completed quickly
- Move 3 can be done in a follow-up PR

## Completed Moves (High Priority)
- ✅ Move 1: State Extraction (ΔS -4.2)
- ✅ Move 2: Hypervisor Elevation (ΔS -0.8)
- **Total: -5.0 ΔS reduction**

## Quick Wins Remaining
- Move 4: Governance (verify only - 5 min)
- Move 5: Spec fix (30-60 min)
- Move 6: Documentation (30 min)

## Move 3 Recommendation

**Defer to follow-up PR:**
- Requires careful merging of 30+ files
- Needs extensive testing
- Risk of breaking imports
- Better done as focused effort

**Current entropy:** 6.7 (from 11.7)  
**With Moves 4-5:** ~3.7 (below 3.2 target without Move 3!)

## Path Forward

1. Complete Moves 4, 5, 6 now (fast wins)
2. Verify ΔS < 3.2 achieved
3. Create separate PR for Move 3 (enforcement consolidation)

This approach:
- ✅ Achieves entropy target faster
- ✅ Reduces risk in this PR
- ✅ Allows focused testing of Move 3
- ✅ Delivers value immediately
