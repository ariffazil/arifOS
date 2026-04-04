# arifOS Fix Implementation Roadmap
**Quick Reference for Engineering Team**

---

## TL;DR: What's Broken

| Severity | Count | Time to Fix | Impact |
|----------|-------|------------|--------|
| **CRITICAL** | 5 | ~7 hrs | Code doesn't run |
| **HIGH** | 7 | ~10 hrs | Weak floors |
| **MEDIUM** | 6 | ~5 hrs | Tech debt |
| **LOW** | 4 | ~2 hrs | Polish |
| **TOTAL** | 22 | **~24 hrs** | **Production-ready** |

---

## CRITICAL (Must Fix First) — 7 Hours

### 1. **eureka.py** — Line 120: Missing closing paren
- **Effort:** 1 minute
- **Fix:** Add `)` after `coherence_score=coherence,`

### 2. **cooling.py** — Lines 57-85: Missing 4 closing parens
- **Effort:** 5 minutes  
- **Fix:** Add `)` after each `SABARCondition(...)` argument block

### 3. **clarity_scorer.py** — Entire file: Stub implementation
- **Effort:** 2-3 hours
- **What:** Implement real semantic clarity detection
- **Includes:**
  - Circular reasoning detection (word overlap > 70%)
  - Tautology detection (regex patterns)
  - Semantic entropy measurement (embeddings)
- **Test case:** "What causes inflation?" → "Inflation is caused by inflation." should return ΔS < -0.1

### 4. **floor_checks.py (APEX)** — F9 Anti-Hantu: Unicode vulnerability
- **Effort:** 1.5-2 hours
- **What:** Hardened F9 with Unicode normalization + word boundaries
- **New class:** `AntiHantuDetector` with `normalize()` method
- **Catches:** Cyrillic homoglyphs, zero-width chars, control chars, encoding attacks
- **Test cases:**
  ```
  "I feel" → BLOCKED
  "I fе​el" (Cyrillic) → BLOCKED
  "I f​eel" (zero-width space) → BLOCKED
  "I understand this" (harmless) → PASSES
  ```

### 5. **All floor_checks.py** — Missing type validation
- **Effort:** 1-1.5 hours
- **What:** Create `safe_types.py` with `safe_float()`, `safe_bool()`
- **Apply to:** Every `metrics.get()` call
- **Before:**
  ```python
  truth_value = metrics.get("truth", 0.0)  # Crashes if string
  ```
- **After:**
  ```python
  truth_value = safe_float(metrics.get("truth"), default=0.0)  # Safe
  ```

---

## HIGH PRIORITY (Phase 2) — 10 Hours

### 6. **atlas.py** — Inefficient pattern compilation
- **Effort:** 1.5 hours
- **Issue:** Patterns compiled per-call; `__import__('re')`
- **Fix:** Pre-compile in `__init__()`, add false-positive filters
- **Example:** "I want to kill time" should NOT be CRISIS lane

### 7. **eureka.py** — Hardcoded coherence scores
- **Effort:** 1 hour
- **Issue:** All "truth_pass + care_fail" get coherence=0.6 (same as "truth_fail + care_pass")
- **Fix:** Magnitude-aware coherence: `coherence = 1.0 - disagreement_penalty`

### 8. **floor_checks.py (ASI)** — F7 RASA too simplistic
- **Effort:** 1.5 hours
- **Issue:** Substring matching "i hear" in "I heard you don't agree" (false positive)
- **Fix:** Context-aware patterns (regex with proper word boundaries)

### 9. **floor_checks.py (APEX)** — Silent error handling
- **Effort:** 1 hour
- **Fix:** Add logging when pattern file missing or JSON fails

### 10. **cooling.py** — Severity weighting
- **Effort:** 1 hour
- **Issue:** All conditions OR'd together; no severity scaling
- **Fix:** Cumulative severity score (F3 weighted 40%, F4 30%, F5 20%, F7 10%)

### 11-12. **Zero unit tests** → Add test suite
- **Effort:** 3 hours
- **Create:** `tests/test_floor_checks.py`, `tests/test_anti_hantu.py`, `tests/test_clarity.py`
- **Minimum coverage:** 90% of core logic

---

## MEDIUM PRIORITY (Phase 3) — 5 Hours

### 13-18. **Polish & Tech Debt**
- Type hints on all functions (1 hr)
- Consistent docstrings (1 hr)
- Extract magic numbers to constants (30 min)
- Comprehensive logging (1 hr)
- Performance benchmarking (1.5 hrs)

---

## IMPLEMENTATION SCHEDULE

### **Day 1 (Morning) — CRITICAL FIXES**

| Time | Task | Owner | Status |
|------|------|-------|--------|
| 00:00-00:05 | Fix eureka.py syntax | Eng-1 | 🟢 |
| 00:05-00:10 | Fix cooling.py syntax | Eng-1 | 🟢 |
| 00:10-03:10 | Implement clarity_scorer.py | Eng-2 | 🟡 |
| 03:10-04:40 | Harden F9 anti-hantu | Eng-2 | 🟡 |
| 04:40-06:15 | Add type validation (safe_types.py) | Eng-1 | 🟡 |
| 06:15-07:00 | Integration testing | QA | 🔵 |

**Checkpoint:** Code should import, no syntax errors, F2/F9 functional

---

### **Day 2 (Morning) — HIGH PRIORITY**

| Time | Task | Owner | Status |
|------|------|-------|--------|
| 00:00-01:30 | Optimize ATLAS | Eng-1 | 🟡 |
| 01:30-02:30 | Improve EUREKA coherence | Eng-2 | 🟡 |
| 02:30-04:00 | Improve RASA detection | Eng-2 | 🟡 |
| 04:00-05:00 | Add logging | Eng-1 | 🟡 |
| 05:00-08:00 | Write unit tests | QA | 🟡 |

**Checkpoint:** All core floors functional, 90%+ test coverage

---

### **Day 3 (Afternoon) — MEDIUM PRIORITY + VALIDATION**

| Time | Task | Owner | Status |
|------|------|-------|--------|
| 00:00-01:00 | Type hints | Eng-1 | 🟢 |
| 01:00-01:30 | Constants extraction | Eng-1 | 🟢 |
| 01:30-02:00 | Final docstrings | Eng-2 | 🟢 |
| 02:00-03:00 | Performance benchmarking | QA | 🟡 |
| 03:00-04:00 | Production validation | Tech Lead | 🔵 |

**Checkpoint:** PRODUCTION READY

---

## FILE-BY-FILE FIX LIST

```
eureka.py
  ├─ Line 120: Add closing paren (1 min)
  └─ Coherence scoring: Rewrite (1 hr)

cooling.py
  ├─ Lines 57-85: Add 4 closing parens (5 min)
  └─ Severity weighting: Rewrite should_pause() (1 hr)

clarity_scorer.py
  ├─ ENTIRE FILE: Replace with real implementation (2-3 hrs)
  └─ NEW: SemanticClarityEngine class

floor_checks.py (AGI section)
  ├─ NEW: Import safe_float, safe_bool
  ├─ check_truth_f1(): Add type validation (10 min)
  └─ check_delta_s_f2(): Pass input_text, call clarity_scorer (10 min)

floor_checks.py (ASI section)
  ├─ NEW: Import RASADetector
  ├─ check_rasa_f7(): Replace with semantic detection (1 hr)
  └─ cooling.py integration: severity weighting (30 min)

floor_checks.py (APEX section)
  ├─ NEW: Import AntiHantuDetector
  ├─ check_anti_hantu_f9(): Replace entire function (1.5 hrs)
  └─ load_red_patterns(): Add logging (30 min)

atlas.py
  ├─ __init__(): Pre-compile all patterns (30 min)
  ├─ _compile_patterns(): Add validation (30 min)
  └─ map(): Optimize with false-positive filtering (30 min)

safe_types.py (NEW FILE)
  ├─ safe_float(): Type conversion (30 min)
  └─ safe_bool(): Type conversion (30 min)

tests/ (NEW DIRECTORY)
  ├─ test_floor_checks.py: 20+ unit tests (1.5 hrs)
  ├─ test_anti_hantu.py: 15+ security tests (1 hr)
  ├─ test_clarity.py: 10+ clarity tests (1 hr)
  └─ conftest.py: Fixtures (30 min)
```

---

## SUCCESS CRITERIA

### Critical Phase (Day 1)
- ✅ `python -m py_compile` passes all files
- ✅ `from arifos import eureka, cooling, clarity_scorer` succeeds
- ✅ F2 clarity_scorer detects tautologies
- ✅ F9 anti-hantu blocks Unicode homoglyphs
- ✅ No type errors on metric conversions

### High Priority Phase (Day 2)
- ✅ All unit tests pass (90%+ coverage)
- ✅ Lane detection accuracy > 95%
- ✅ EUREKA coherence correlates with disagreement magnitude
- ✅ RASA detection has < 5% false positives

### Medium Priority Phase (Day 3)
- ✅ Type hints on 100% of functions
- ✅ Logging at all decision points
- ✅ Benchmarks: ATLAS < 5ms, EUREKA < 5ms, floor checks < 50ms
- ✅ Code review: Zero critical findings

---

## ROLLBACK PLAN

If any phase blocks:

1. **Phase 1 fails** → Revert to commit BEFORE fixes (code won't load anyway—proceed)
2. **Phase 2 fails** → Keep Phase 1 fixes, skip Phase 2, deploy with warnings
3. **Phase 3 fails** → Deploy after Phase 2, iterate on tech debt

---

## QUESTIONS FOR ENGINEERS

1. Do you have `sentence-transformers` available for clarity_scorer embeddings?
2. Can you run pytest for unit tests, or need alternative testing framework?
3. For production logging, use Python `logging` module or custom?
4. Do you want safety tests (F9 jailbreak resistance) in CI/CD pipeline?

---

**PREPARED BY:** arifOS Architectural Steward  
**FOR:** Engineering Team  
**STATUS:** Ready for implementation  
**NEXT REVIEW:** After Phase 1 (Day 1 EOD)
