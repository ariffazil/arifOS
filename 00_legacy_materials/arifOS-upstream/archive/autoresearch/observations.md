# Observations Log

> All experiment learnings, patterns, and insights.

---

## Patterns Observed

| Pattern | Evidence | Implication |
|---------|----------|-------------|
| Parallel [555 \|\| 666] gives 15-20% throughput boost | floor_opt_004 | Enable by default |
| Omega calibration per task complexity helps 5-10% | omega_tune_001 | Implement dynamic Ω |
| Cache TTL > 5 min causes stale data violations | cache_001 (reverted) | Keep TTL short |
| F7 band [0.015, 0.20] wider than original [0.03, 0.05] reduces false Godellocks | floor_opt_004 | Adopt wider band |
| Threshold relaxation increases violations non-linearly | threshold_001 | Keep thresholds tight |

---

## Experiment Log

_Append new experiments above this line as they run._

---

*Ditempa Bukan Diberi* [ΔΩΨ|888]
