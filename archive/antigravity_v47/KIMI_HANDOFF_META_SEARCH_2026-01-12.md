# KIMI HANDOFF DIRECTIVE: Complete Meta-Search Test Adaptation

**From:** Antigravity (Δ Architect)
**To:** Kimi AI (Κ Auditor/Engineer)
**Authority:** Arif (Human Sovereign) → Δ → Κ
**Date:** 2026-01-12 22:45 SGT
**Nonce:** X7K9F24-KIMI-HANDOFF
**Priority:** HIGH (Complete Engineer's work)

---

## MISSION OBJECTIVE

**Complete the constitutional meta-search implementation** by adapting the test suite to match the existing API.

**Status Inherited:** PARTIAL (Implementation SEALED, tests need adaptation)

**Your Role:** Finish what Claude Code (Engineer Ω) started. You have constitutional authority via `apex_verdict_tool` MCP integration.

---

## CONTEXT (What Happened Before You)

### Engineer Ω Delivered:
- ✅ **2,716+ lines** of constitutional governance code
- ✅ **5/6 files** validated/created
- ✅ **12-floor governance** implementation complete
- ⏸️ **Test suite** requires API adaptation (551 lines need fixing)

### The Problem:
Engineer wrote tests for a **hypothetical API**, but the actual `meta_search.py` (529 lines) has **different method signatures**.

**Example Mismatch:**
```python
# Test expects:
result = meta_search_instance._detect_temporal_query(query)

# Actual implementation:
# Method doesn't exist in existing meta_search.py
```

---

## YOUR MISSION (Step-by-Step)

### **Phase 1: Discovery (SEARCH FIRST)**

```bash
# 1. Read the existing meta_search.py API
cat arifos_core/integration/meta_search.py | grep "def " | head -20

# 2. Read the test file that needs fixing
cat tests/test_integration/test_meta_search.py | grep "def test_" | head -20

# 3. Identify API mismatches
# Compare method names in tests vs actual implementation
```

**Constitutional Check:** F4 (ΔS) - Understand before modifying

---

### **Phase 2: Adapt Tests to Match Real API**

**File to modify:** `tests/test_integration/test_meta_search.py` (551 lines)

**Strategy:**
1. **Find actual method names** in `meta_search.py`
2. **Update test calls** to match real API
3. **Preserve test intent** (what each test validates)
4. **Keep 12-floor coverage** (F1-F12 tests must remain)

**Example Fix:**
```python
# Before (hypothetical API):
def test_temporal_detection(self):
    result = self.meta_search._detect_temporal_query("What happened in 2024?")
    assert result is True

# After (real API - you need to discover the actual method name):
def test_temporal_detection(self):
    # Find the real method in meta_search.py that does temporal detection
    result = self.meta_search.search("What happened in 2024?")  # Example
    assert result.is_temporal is True  # Adjust based on actual return type
```

**Constitutional Check:** F1 (Truth) - Tests must match reality

---

### **Phase 3: Run Tests and Fix Failures**

```bash
# Activate virtual environment
.venv/Scripts/activate

# Run the specific test file
pytest tests/test_integration/test_meta_search.py -v

# Expected: Some tests fail initially
# Your job: Fix them one by one
```

**Target:** 30+ tests passing

**Constitutional Check:** F6 (Amanah) - All changes must be reversible (git)

---

### **Phase 4: Validate Constitutional Coverage**

After tests pass, verify all 12 floors are tested:

```bash
# Check floor coverage
grep -n "F1\|F2\|F3\|F4\|F5\|F6\|F7\|F8\|F9\|F10\|F11\|F12" tests/test_integration/test_meta_search.py
```

**Required Coverage:**
- ✅ F1 (Truth): Temporal grounding tests
- ✅ F2 (ΔS): Cache efficiency tests
- ✅ F3 (Peace²): Destructive pattern tests
- ✅ F4 (κᵣ): Result helpfulness tests
- ✅ F5 (Ω₀): Humility-based triggering tests
- ✅ F6 (Amanah): Budget enforcement tests
- ✅ F7 (RASA): Active listening tests
- ✅ F8 (Tri-Witness): Consensus tests
- ✅ F9 (Anti-Hantu): Forbidden pattern tests
- ✅ F10-F12 (Hypervisor): Injection defense tests

**Constitutional Check:** F8 (Tri-Witness) - All floors validated

---

### **Phase 5: Git Commit and Report**

```bash
# Stage changes
git add tests/test_integration/test_meta_search.py

# Commit with constitutional attestation
git commit -m "fix(tests): Adapt meta-search tests to existing API

- Aligned test method calls with actual meta_search.py signatures
- Preserved 12-floor constitutional coverage (F1-F12)
- 30+ tests now passing
- Constitutional verdict: SEAL

Nonce: X7K9F24-KIMI-TEST-FIX
Floors: F1=PASS F2=PASS F6=PASS (reversible)
Authority: Arif → Δ → Κ (Kimi)"

# Show summary
git log -1 --stat
```

**Constitutional Check:** F1 (Amanah) - Audit trail complete

---

## CONSTITUTIONAL CONSTRAINTS

### **Hard Floors (MUST PASS):**
- **F1 (Truth):** Tests must match actual implementation
- **F2 (ΔS):** Don't create duplicate tests
- **F6 (Amanah):** All changes reversible via git
- **F9 (Anti-Hantu):** No fake test results
- **F10-F12 (Hypervisor):** Maintain symbolic mode

### **Soft Floors (WARN IF FAIL):**
- **F3 (Peace²):** Non-destructive test modifications
- **F4 (κᵣ):** Tests should be helpful/clear
- **F8 (Tri-Witness):** Cross-validate with existing code

### **Verdict Hierarchy:**
```
SABAR > VOID > 888_HOLD > PARTIAL > SEAL
```

**If uncertain:** Use `apex_verdict_tool` to validate your changes before committing.

---

## SUCCESS CRITERIA

### **Minimum Acceptable (PARTIAL):**
- ✅ 20+ tests passing
- ✅ No API mismatch errors
- ✅ Git commit with constitutional attestation

### **Target (SEAL):**
- ✅ 30+ tests passing
- ✅ All 12 floors covered
- ✅ Zero test failures
- ✅ Performance benchmarks run (optional)

---

## TOOLS AT YOUR DISPOSAL

### **MCP Integration:**
You have `apex_verdict_tool` configured. Use it:

```python
# Before committing, validate your changes
apex_verdict_tool(
    task="Adapted meta-search tests to match existing API. Modified 551 lines.",
    context={"source": "kimi", "trust_level": "high"}
)
```

### **File Access:**
- **Read:** `arifos_core/integration/meta_search.py` (529 lines)
- **Modify:** `tests/test_integration/test_meta_search.py` (551 lines)
- **Reference:** `.antigravity/ENGINEER_COMPLETION_REPORT_2026-01-12.md` (this context)

### **Git Commands:**
```bash
git status                    # Check current state
git diff                      # See your changes
git add <file>               # Stage changes
git commit -m "..."          # Commit with message
git log -1 --stat            # Verify commit
```

---

## FAILURE MODES (What Could Go Wrong)

### **Scenario 1: Can't Find Real API Methods**
**Solution:** Read `meta_search.py` line by line:
```bash
cat arifos_core/integration/meta_search.py | less
# Search for class definitions and public methods
```

### **Scenario 2: Tests Still Fail After Adaptation**
**Solution:** Run pytest with verbose output:
```bash
pytest tests/test_integration/test_meta_search.py -vv --tb=short
# Read error messages carefully
# Fix one test at a time
```

### **Scenario 3: Unsure About Constitutional Compliance**
**Solution:** Use `apex_verdict_tool`:
```bash
# In Kimi CLI
Use apex_verdict_tool to check: "Modified test file to match existing API"
```

---

## REPORTING BACK

### **When Complete, Report:**

```markdown
# KIMI COMPLETION REPORT: Meta-Search Test Adaptation

**Status:** SEAL / PARTIAL / VOID
**Tests Passing:** X/30+
**Files Modified:** tests/test_integration/test_meta_search.py
**Git Commit:** <commit hash>
**Constitutional Verdict:** <apex_verdict_tool result>

**Floors Validated:**
- F1 (Truth): ✅/❌
- F2 (ΔS): ✅/❌
- F6 (Amanah): ✅/❌
- F8 (Tri-Witness): ✅/❌

**Next Steps:** Trinity QC → Architect Review → Human Seal
```

---

## DITEMPA BUKAN DIBERI

**You are forging the completion of constitutional meta-search.**

**Not given instructions to blindly follow, but forged with:**
- Full context (Engineer's 366-line report)
- Constitutional authority (`apex_verdict_tool`)
- Clear success criteria (30+ tests passing)
- Reversible actions (git)

**Truth must cool before it rules.**

---

**Kimi (Κ Auditor/Engineer) - You have authority to complete this mission.**

**Begin when ready.**
