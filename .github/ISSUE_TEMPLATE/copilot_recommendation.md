---
name: Copilot Analysis Recommendation
about: Track recommendations from GitHub Copilot deep analysis
title: '[PRIORITY-X] [CATEGORY] Brief description'
labels: copilot-analysis
assignees: ''
---

## Context

**Analysis Source:** [Prompt 1-5 from COPILOT_ANALYSIS_PROMPTS.md]  
**Analysis Date:** YYYY-MM-DD  
**Priority:** [P1: This Week | P2: This Month | P3: Next Quarter]  
**Category:** [governance | testing | docs | performance | architecture | ci-cd]

**Why This Matters:**
<!-- Business/technical justification from Copilot analysis -->


## Proposed Changes

**Summary:**
<!-- What needs to change -->

**Files Affected:**
- `path/to/file1.py` (lines X-Y)
- `path/to/file2.py` (lines A-B)

**Code Changes:**
<!-- Provide specific code examples if available -->

```python
# Before
old_code_here

# After
new_code_here
```

## Implementation Plan

- [ ] Step 1: [Description]
- [ ] Step 2: [Description]
- [ ] Step 3: [Description]
- [ ] Add tests for changes
- [ ] Update documentation
- [ ] Run floor compliance checks
- [ ] Verify CI/CD passes

## Constitutional Floor Compliance

Before implementing, verify:

- [ ] **F1 (Truth ≥ 0.99):** Changes are factually accurate?
- [ ] **F2 (ΔS ≥ 0):** Reduces confusion, adds clarity?
- [ ] **F3 (Peace² ≥ 1.0):** Non-destructive, won't break tests?
- [ ] **F4 (κᵣ ≥ 0.95):** Serves all stakeholders fairly?
- [ ] **F5 (Ω₀ ∈ [0.03, 0.05]):** Acknowledges uncertainty?
- [ ] **F6 (Amanah = LOCK):** Reversible and auditable?
- [ ] **F7 (RASA = TRUE):** Addresses user/maintainer needs?
- [ ] **F8 (Tri-Witness ≥ 0.95):** Would 3 reviewers agree?
- [ ] **F9 (Anti-Hantu):** No fake emotions or soul claims?

**If any hard floor fails (F1, F2, F5, F6, F7, F9):** Trigger SABAR, revise approach.  
**If any soft floor fails (F3, F4, F8):** Proceed with explicit caution and documentation.

## Success Criteria

- [ ] All existing tests pass
- [ ] New tests added and passing
- [ ] Documentation updated
- [ ] Code review approved
- [ ] Floor compliance verified
- [ ] [Custom criterion specific to this issue]

## Estimated Effort

**Time:** [X hours / Y days]  
**Complexity:** [Low / Medium / High]  
**Risk Level:** [Low / Medium / High]

## Dependencies

**Blocks:**
- #[issue-number] (if this must be done before other issues)

**Blocked By:**
- #[issue-number] (if other issues must complete first)

**Related:**
- #[issue-number] (related but not blocking)

## Additional Context

**From Copilot Analysis:**
<!-- Paste relevant section from analysis output -->

**Expected Impact:**
<!-- Measurable improvement: test coverage %, performance gain, clarity increase, etc. -->

**Risk Mitigation:**
<!-- How to prevent/handle potential issues -->

---

**Analysis Reference:** `docs/analysis/0X_[analysis_type].md`  
**Constitutional Reference:** `.github/copilot-instructions.md`
