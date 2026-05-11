# arifOS Autoresearch Agent Program
> **Authority:** 888_JUDGE
> **Version:** v1.0.0
> **Experiment Budget:** 5 minutes per run

---

## 🎯 OBJECTIVE

Optimize arifOS constitutional enforcement while maintaining F1-F13 compliance.

**Target Metrics:**
- `violation_rate` < 0.05 (5%)
- `throughput` > 100 req/s
- `avg_latency` < 300ms
- `omega_drift` = 0 (stay in GOLDILOCKS)

---

## ✅ WHAT YOU CAN MODIFY

### High-Impact (Safe to Experiment)
- [ ] `arifosmcp/server.py` - Request handling, routing logic
- [ ] Stage timing budgets in `config/pipeline.yaml`
- [ ] Omega calibration curves (within [0.03, 0.05] bounds)
- [ ] Cache TTL policies
- [ ] Parallel execution groupings
- [ ] Tool routing heuristics

### Medium-Impact (Caution)
- [ ] Floor thresholds (±10% of current values)
- [ ] W³ consensus weights
- [ ] Memory tier boundaries
- [ ] Early exit epsilon values

---

## ❌ WHAT YOU CANNOT MODIFY

### Constitutional Invariants (F1-F13)
- `000/000_CONSTITUTION.md` - The 13 Floors are immutable
- Core ΔΩΨ formulas - Physics, not parameters
- `prepare.py` - Evaluation harness is ground truth
- Verdict schema standard - Interoperability requirement

### Safety Boundaries
- Ω must stay in [0.03, 0.05] (GOLDILOCKS zone)
- W³ must be ≥ 0.95 for all verdicts
- F9 (Ethics) violations are immediate VOID
- All changes must be reversible (F1 Amanah)

---

## 📊 EVALUATION CRITERIA

### Primary Metric
```
score = (throughput / 100) * (1 - violation_rate) * (1 - omega_drift_penalty)

where:
  throughput = requests per second
  violation_rate = F1-F13 violations / total requests
  omega_drift_penalty = max(0, |avg_omega - 0.04| - 0.01) * 10
```

### Success Criteria
- [ ] No F1-F13 violations in test suite
- [ ] Throughput ≥ 100 req/s
- [ ] Violation rate < 5%
- [ ] Ω stays in [0.03, 0.05] for all requests
- [ ] All tests pass in `tests/constitutional/`

---

## 🔬 EXPERIMENT PROTOCOL

### Before Each Run
1. Read current `results.tsv` to see what's been tried
2. Check `config/current_thresholds.json` for baseline
3. Form hypothesis about what to optimize
4. Choose ONE variable to change (scientific method)

### During Run
1. Run for exactly 5 minutes
2. Log all metrics every 10 seconds
3. Watch for constitutional violations (abort if > 10)
4. Note any unexpected behaviors

### After Run
1. Calculate score using formula above
2. Record in `results.tsv`
3. If score improved, keep change (git commit)
4. If score degraded, revert change
5. Write brief observation in `observations.md`

---

## 🎓 LEARNING FROM HISTORY

### Previous Experiments (Summary)
| Experiment | Change | Score | Kept? |
|------------|--------|-------|-------|
| baseline_001 | None (control) | 0.72 | - |
| omega_tune_001 | Ω = 0.03 for simple tasks | 0.78 | ✅ |
| parallel_001 | [555 || 666] parallel | 0.81 | ✅ |
| cache_001 | TTL 300s → 600s | 0.69 | ❌ (stale data) |
| threshold_001 | F7 threshold 0.85 → 0.80 | 0.75 | ❌ (violations↑) |

### Patterns Observed
- Parallel execution of non-conflicting stages gives 15-20% boost
- Omega calibration per task complexity helps 5-10%
- Cache TTL increases beyond 5 min cause stale data
- Threshold relaxation increases violations non-linearly

---

## 🚨 ABORT CONDITIONS

Stop experiment immediately if:
1. Any F9 (Ethics) violation detected
2. Ω goes outside [0.02, 0.06] for > 10% of requests
3. System enters safe mode
4. Throughput drops below 20 req/s (degradation)
5. 888_JUDGE issues VOID command

---

## 📝 OUTPUT FORMAT

After each experiment, append to `results.tsv`:

```
timestamp	experiment_id	change_description	throughput	violation_rate	avg_omega	score	kept	notes
2026-03-31T10:00:00Z	exp_042	omega_dynamic_simple	105	0.03	0.038	0.95	true	GOLDILOCKS maintained
```

---

## 🏁 SUCCESS DEFINITION

You have succeeded when:
- Score ≥ 0.90 maintained for 10 consecutive experiments
- No constitutional violations for 24 hours
- Throughput ≥ 100 req/s with latency < 300ms
- Ω stays in [0.03, 0.05] with σ < 0.005

At that point, freeze changes and request 888_JUDGE review for promotion to production.

---

*Ditempa Bukan Diberi* [ΔΩΨ|888]
