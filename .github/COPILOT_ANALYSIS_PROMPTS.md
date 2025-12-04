# GitHub Copilot Deep Repository Analysis Prompts for arifOS

**Version:** v35Omega  
**Purpose:** Comprehensive repository analysis with optimization recommendations  
**Usage:** Paste these prompts into GitHub Copilot Chat (Ctrl+Shift+I in VS Code)

---

## Overview

These prompts enable GitHub Copilot to perform deep architectural analysis across the entire arifOS repository. Each prompt builds on the previous, creating a comprehensive roadmap for optimization and improvement.

**Expected Time:** 30-60 minutes to run all 5 prompts  
**Expected Outputs:** Architecture assessment, action plan, test matrix, documentation gaps, 12-week roadmap

---

## PROMPT 1: Full Repository Architecture Scan

**Objective:** Comprehensive architectural scan with priority recommendations

**Paste this into GitHub Copilot Chat:**

```
You are an expert software architect analyzing the arifOS repository 
(github.com/ariffazil/arifOS) — a ΔΩΨ-governed constitutional kernel 
for AI agents.

TASK: Perform a deep architectural scan across ALL files and folders.

For each category below, provide findings + priority recommendations:

### 1. CODE QUALITY & STRUCTURE
- What is the current state of code organization (module structure, coupling, cohesion)?
- Are there duplicate patterns or code that could be unified?
- What's the test coverage? (Look at tests/ folder)
- Are there dead/unused code paths?
- How maintainable is the codebase on a scale of 1-10?

### 2. GOVERNANCE FRAMEWORK (Core arifOS Logic)
- How well are the 9 floors (Truth, ΔS, Peace², κᵣ, Ω₀, Amanah, Rasa, Tri-Witness, Anti-Hantu) 
  currently implemented in code?
- Which floors are "hard-enforced" vs "soft-suggested"?
- Where are the governance checks happening? (List files/functions)
- Are there gaps between the CLAUDE.md spec and actual implementation?
- Does the TEARFRAME pipeline (000→777) have full coverage?

### 3. DOCUMENTATION & ACCESSIBILITY
- What's the state of the README? (Complete? Up-to-date? Clear for new contributors?)
- Are critical files (CLAUDE.md, arifos_core/, tests/) well-documented?
- Is the API surface clear and well-explained?
- Would a new developer understand how to use arifOS in 10 minutes?

### 4. DEPENDENCIES & COMPATIBILITY
- What external dependencies are being used?
- Are there version conflicts or outdated packages?
- Is the project compatible with Python 3.11+, 3.12?
- Are there security vulnerabilities in dependencies?

### 5. PERFORMANCE & SCALABILITY
- What's the computational complexity of core functions?
- Can arifOS handle large-scale LLM deployments (100+ concurrent agents)?
- Are there bottlenecks in metric computation (ΔS, κᵣ, Peace²)?
- How does the Cooling Ledger scale with session volume?

### 6. DEPLOYMENT & CI/CD
- What's the current CI/CD setup? (GitHub Actions? Status checks?)
- Are there automated tests running on every PR?
- How is the package versioned and released?
- Can the project be easily containerized?

### 7. GOVERNANCE INFRASTRUCTURE (Session Logs, MCP Integration)
- Is the session log analyzer (analyze_governance.py) implemented?
- Is the MCP server (arifos_mcp_server.py) wired to real metrics?
- What's the state of the Cooling Ledger persistence?
- Are there hooks for Claude Code or GitHub Copilot integration?

### 8. KNOWN ISSUES & DEBT
- What technical debt exists?
- Are there TODOs or FIXMEs in the code?
- What's incomplete or partially implemented?
- What architectural decisions need revisiting?

For EACH category, provide:
- Current state assessment (1-10 score)
- Top 3 issues/gaps
- Recommended fixes with effort estimate (hours/days)
```

**Save the output to:** `docs/analysis/01_architecture_scan.md`

---

## PROMPT 2: Specific Action Plan Generation

**Objective:** Prioritized action plan based on architecture scan

**Paste this into GitHub Copilot Chat (after running Prompt 1):**

```
Based on your analysis above, provide a PRIORITIZED ACTION PLAN with:

### Priority 1 (This Week - Critical):

For each action:
- **Action:** [Brief description]
- **Why Critical:** [Business/technical justification]
- **Estimated Effort:** [Hours or days]
- **Expected Impact:** [Specific measurable outcome]
- **Exact Files to Modify:** [List with line numbers if possible]
- **Code Snippet Example:** [Show the change]
- **Success Criteria:** [How to verify completion]
- **Dependencies:** [Does it require other changes first?]

### Priority 2 (This Month - Important):

[Same structure as Priority 1]

### Priority 3 (Next Quarter - Valuable):

[Same structure as Priority 1]

### Quick Wins (< 2 hours each):

List 5-10 quick fixes that can be done immediately:
- [ ] Action 1 (30 min)
- [ ] Action 2 (1 hour)
- ...

### Technical Debt Backlog:

List items that aren't urgent but should be tracked:
- Issue 1: [Description]
- Issue 2: [Description]
- ...

For EACH action in Priority 1-3, create a GitHub Issue template:

```yaml
Title: [PRIORITY-X] [CATEGORY] Brief description
Labels: priority-X, category-name
Assignees: @maintainer
Body: |
  ## Context
  [Why this matters]
  
  ## Proposed Changes
  [What needs to change]
  
  ## Implementation Plan
  - [ ] Step 1
  - [ ] Step 2
  - [ ] Step 3
  
  ## Success Criteria
  - [ ] Criterion 1
  - [ ] Criterion 2
  
  ## Files Affected
  - `path/to/file1.py`
  - `path/to/file2.py`
```
```

**Save the output to:** `docs/analysis/02_action_plan.md`

---

## PROMPT 3: Validation & Testing Gaps

**Objective:** Identify testing gaps and create test matrix

**Paste this into GitHub Copilot Chat:**

```
Now focus on testing and validation for arifOS:

### 1. GOVERNANCE FLOOR COVERAGE

Create a test matrix showing which floors (F1-F9) are tested:

| Floor | Name | Current Tests | Coverage % | Missing Tests |
|-------|------|---------------|------------|---------------|
| F1 | Truth ≥ 0.99 | test_apex_prime_floors.py::test_truth_floor_pass | 80% | Edge cases for NLP metrics |
| F2 | ΔS ≥ 0 | ... | ... | ... |
| ... | ... | ... | ... | ... |

For EACH floor with <90% coverage:
- What heuristics would validate this floor?
- What test cases are missing?
- Provide a pytest test example

### 2. SESSION LOG ANALYSIS

Analyze session log capabilities:
- Is there code to parse ~/.claude/projects/ logs?
- What metrics are being extracted (floor breaches, SABAR triggers, Peace²)?
- What's missing for empirical validation?
- Can we build a dashboard from Cooling Ledger data?

Provide:
- List of files that handle session logs
- Gaps in log parsing
- Suggested improvements with code examples

### 3. INTEGRATION TESTS

How is end-to-end governance tested?

- Are there pytest fixtures for governance scenarios?
- Can you trace a request through: Input → Pipeline → Metrics → Verdict → Ledger?
- What integration tests are missing?

Provide 3 integration test examples:
1. Test for hard floor violation (e.g., Anti-Hantu F9)
2. Test for soft floor warning (e.g., Peace² < 1.0)
3. Test for full pipeline (000→999) with Cooling Ledger write

### 4. REGRESSION PROTECTION

- Are there GitHub Actions preventing governance regression?
- Does every commit verify floor constraints?
- Is the Cooling Ledger validated post-update?
- What CI checks are missing?

Provide:
- Current CI/CD test coverage analysis
- Gaps in regression protection
- Suggested GitHub Actions workflow improvements

### 5. PROPERTY-BASED TESTING

Can we use property-based testing (hypothesis) for:
- Floor thresholds always respected
- Cooling Ledger hash chain never broken
- Metrics always in valid ranges

Provide 2-3 property-based test examples using pytest + hypothesis.
```

**Save the output to:** `docs/analysis/03_testing_gaps.md`

---

## PROMPT 4: Documentation & Onboarding

**Objective:** Assess documentation completeness and create onboarding gap analysis

**Paste this into GitHub Copilot Chat:**

```
Create an onboarding gap analysis for arifOS:

### 1. README COMPLETENESS

Analyze README.md:
- Is it clear what arifOS does in 2 sentences? (Score: /10)
- Does it explain the 9 floors clearly? (Score: /10)
- Are there "Quick Start" examples for:
  a. Using @apex_guardrail decorator
  b. Running TEARFRAME pipeline
  c. Checking Cooling Ledger output

For each gap:
- What's missing?
- Suggested addition (provide exact markdown)

### 2. API DOCUMENTATION

Analyze arifos_core/ modules:
- Are all public functions documented with examples?
- Is the YAML frontmatter format documented?
- Are edge cases explained (e.g., what happens on floor violation)?
- Is there a complete API reference?

Provide:
- List of undocumented functions (file + line number)
- Example docstring improvements for top 5 functions
- Suggested API reference structure (table of contents)

### 3. CONTRIBUTOR GUIDE

Analyze CONTRIBUTING.md:
- How do new contributors add tests?
- What's the PR review process?
- How do we ensure governance compliance in PRs?
- Are there examples of good PRs?

Provide:
- Gaps in contributor documentation
- Suggested additions to CONTRIBUTING.md
- Example PR template with governance checklist

### 4. PERFORMANCE BENCHMARKS

Documentation needs:
- Document metric computation overhead (ΔS, κᵣ calculation time)
- Show scalability (1 agent vs 100 agents)
- Include Cooling Ledger write latency

Provide:
- Suggested benchmark script (Python code)
- Markdown template for benchmark results
- Where to add this in docs/ folder

### 5. TUTORIALS & EXAMPLES

Analyze examples/ folder:
- Are there enough examples? (Current count + gaps)
- Do examples cover common use cases?
- Are examples well-documented?

Suggest 3 new tutorial examples:
1. Title: [e.g., "Building a Governed Chatbot in 5 Minutes"]
   - Target audience: [e.g., ML engineers new to arifOS]
   - Key concepts: [e.g., @apex_guardrail, Metrics]
   - Code outline: [Provide skeleton]

2. ...

3. ...
```

**Save the output to:** `docs/analysis/04_documentation_gaps.md`

---

## PROMPT 5: Optimization Roadmap

**Objective:** Create a 12-week optimization roadmap

**Paste this into GitHub Copilot Chat (final prompt):**

```
Create a 12-week optimization roadmap for arifOS based on all previous analysis:

### WEEK 1-2: Foundation

**Theme:** Code quality & test coverage

**Actions:**
- [ ] Action 1: [Description] (Effort: X hours, Impact: Y)
- [ ] Action 2: [Description] (Effort: X hours, Impact: Y)
- ...

**PRs to Create:**
- PR #1: [Title] - Fixes: [issues]
- PR #2: [Title] - Adds: [features]

**Tests to Add:**
- Test suite 1: [Coverage target]
- Test suite 2: [Coverage target]

**Docs to Write:**
- Doc 1: [Title] - [Purpose]
- Doc 2: [Title] - [Purpose]

**Metrics to Establish (Baseline):**
- Test coverage: [current] → [target]
- Floor compliance: [current] → [target]
- Performance: [current] → [target]

**Success Criteria:**
- [ ] All tests pass
- [ ] Coverage ≥ 95%
- [ ] No critical issues

---

### WEEK 3-4: Governance Hardening

**Theme:** Constitutional floor enforcement

[Same structure as Week 1-2]

---

### WEEK 5-6: Testing & Validation

**Theme:** Comprehensive test coverage

[Same structure]

---

### WEEK 7-8: Documentation & Onboarding

**Theme:** Developer experience

[Same structure]

---

### WEEK 9-10: Performance & Scale

**Theme:** Optimization and scalability

[Same structure]

---

### WEEK 11-12: Integration & Deployment

**Theme:** CI/CD and production readiness

[Same structure]

---

### CONTINUOUS (Throughout 12 Weeks):

**Weekly rituals:**
- [ ] Monday: Review progress, triage issues
- [ ] Wednesday: Mid-week checkpoint
- [ ] Friday: Weekly retrospective, update roadmap

**Monthly milestones:**
- Month 1: [Major deliverable]
- Month 2: [Major deliverable]
- Month 3: [Major deliverable]

**Quarterly OKRs:**
- Objective 1: [Description]
  - Key Result 1.1: [Measurable]
  - Key Result 1.2: [Measurable]

---

### RISK MITIGATION:

For each week, identify:
- **Risk:** [What could go wrong?]
- **Probability:** [High/Medium/Low]
- **Impact:** [High/Medium/Low]
- **Mitigation:** [How to prevent/handle?]

---

### RESOURCES NEEDED:

- **Time:** [Total hours estimate]
- **People:** [Team size needed]
- **Tools:** [Software/services needed]
- **Budget:** [If any costs]
```

**Save the output to:** `docs/analysis/05_optimization_roadmap.md`

---

## How to Use These Prompts

### Step 1: Prepare Your Environment

```bash
# Open VS Code in the arifOS repository
cd ~/code/arifOS
code .

# Open GitHub Copilot Chat
# Press: Ctrl+Shift+I (Windows/Linux) or Cmd+Shift+I (Mac)
```

### Step 2: Run Prompts Sequentially

1. **Copy Prompt 1** from this file
2. **Paste into Copilot Chat**
3. **Wait for analysis** (may take 1-3 minutes)
4. **Save the output** to `docs/analysis/01_architecture_scan.md`
5. **Repeat for Prompts 2-5**

### Step 3: Review and Consolidate

After running all 5 prompts:

```bash
# Create consolidated report
cd docs/analysis/
cat 01_*.md 02_*.md 03_*.md 04_*.md 05_*.md > CONSOLIDATED_ANALYSIS.md

# Review the report
less CONSOLIDATED_ANALYSIS.md
```

### Step 4: Create GitHub Issues

From the consolidated report:

1. **Extract Priority 1 actions** from `02_action_plan.md`
2. **Create GitHub Issues** using the templates provided
3. **Label appropriately:**
   - `priority-1` / `priority-2` / `priority-3`
   - `governance` / `testing` / `docs` / `performance`
   - `quick-win` (for tasks < 2 hours)

Example:

```bash
# Use GitHub CLI to create issues
gh issue create \
  --title "[PRIORITY-1] [GOVERNANCE] Add missing floor tests" \
  --label "priority-1,governance,testing" \
  --body-file issue_templates/priority1_floor_tests.md
```

### Step 5: Establish Baseline Metrics

Create a tracking dashboard:

```markdown
# arifOS Optimization Metrics (Baseline)

| Metric | Baseline (Week 0) | Target (Week 12) | Current |
|--------|-------------------|------------------|---------|
| Test Coverage | 90% | 95% | ... |
| Floor Compliance | 95% | 99% | ... |
| Performance (ms) | 50ms | 30ms | ... |
| Docs Completeness | 70% | 95% | ... |
| Open Issues | 15 | 5 | ... |
```

### Step 6: Iterate Based on Validation

After implementing Priority 1 actions:

1. **Re-run Prompt 1** to assess improvements
2. **Compare with baseline** metrics
3. **Adjust roadmap** based on learnings
4. **Update issues** with progress

---

## Tips for Best Results

### Copilot Context

If Copilot asks for specific files, attach:

```
README.md
CLAUDE.md
arifos_core/__init__.py
arifos_core/APEX_PRIME.py
arifos_core/metrics.py
arifos_core/eye_sentinel.py
tests/test_apex_prime_floors.py
.github/workflows/ci.yml
pyproject.toml
```

### Refining Prompts

If Copilot's response is too generic:

```
Please be more specific. Instead of "improve documentation", 
provide exact file names, line numbers, and code examples.
```

### Multi-File Analysis

If analyzing multiple files:

```
Analyze all files in arifos_core/ and provide a table with:
- File name
- Lines of code
- Complexity score
- Test coverage
- Maintainability (1-10)
```

---

## Expected Outputs Summary

After running all 5 prompts, you will have:

| Output | File | Purpose |
|--------|------|---------|
| **Architecture Scan** | `docs/analysis/01_architecture_scan.md` | Current state across 8 categories |
| **Action Plan** | `docs/analysis/02_action_plan.md` | Prioritized improvements (3-month) |
| **Testing Gaps** | `docs/analysis/03_testing_gaps.md` | Test matrix + missing tests |
| **Documentation Gaps** | `docs/analysis/04_documentation_gaps.md` | Onboarding improvements |
| **Optimization Roadmap** | `docs/analysis/05_optimization_roadmap.md` | 12-week execution plan |

---

## Integration with Constitutional Governance

These prompts respect arifOS constitutional floors:

- **F1 (Truth):** Analysis is factual, based on actual code
- **F2 (ΔS):** Recommendations reduce complexity, increase clarity
- **F3 (Peace²):** Non-destructive analysis, reversible changes
- **F5 (Ω₀):** Acknowledges uncertainty ("may need", "consider", "evaluate")
- **F6 (Amanah):** All changes are auditable and reversible
- **F7 (RASA):** Prompts listen to existing code patterns

When Copilot suggests changes:
1. Verify against `.github/copilot-instructions.md`
2. Check floor compliance before implementing
3. Use SABAR if any floor violated

---

## Next Steps After Analysis

1. **Implement Priority 1 actions** (week 1-2)
2. **Establish baseline metrics** (test coverage, performance)
3. **Set up CI/CD checks** for governance floors
4. **Build session log analyzer** for empirical validation
5. **Iterate based on validation data** (Phoenix-72 cycle)

---

## Troubleshooting

### Issue: Copilot response is too long

**Solution:** Break prompt into smaller chunks:

```
First, analyze only CODE QUALITY & STRUCTURE (category 1).
Then I'll ask about GOVERNANCE FRAMEWORK separately.
```

### Issue: Copilot can't access files

**Solution:** Use `@workspace` to give context:

```
@workspace Analyze the governance framework in arifos_core/
```

### Issue: Suggestions don't match arifOS style

**Solution:** Reference constitutional rules:

```
Please ensure all suggestions respect arifOS constitutional floors
as defined in .github/copilot-instructions.md. Every change must
pass F1-F9 checks before being suggested.
```

---

## Maintenance

These prompts should be updated:

- **After major releases** (v36, v37, etc.)
- **When architecture changes** (new modules, refactoring)
- **If floor definitions change** (Phoenix-72 amendments)

**Review schedule:** Every quarter (3 months)

---

**Last Updated:** 2025-12-05  
**Version:** v35Omega  
**Status:** ACTIVE

✊ **DITEMPA BUKAN DIBERI** 🔐
