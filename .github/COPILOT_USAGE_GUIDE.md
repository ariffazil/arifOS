# GitHub Copilot Usage Guide for arifOS

**Version:** v35Omega  
**Purpose:** Comprehensive guide for using GitHub Copilot with arifOS  
**Last Updated:** 2025-12-05

---

## Quick Start (5 Minutes)

### 1. Enable GitHub Copilot

```bash
# In VS Code
# 1. Install "GitHub Copilot" extension
# 2. Sign in with your GitHub account
# 3. Verify Copilot is active (check status bar)
```

### 2. Test Copilot with arifOS

Open GitHub Copilot Chat:

```
Keyboard Shortcut:
- Windows/Linux: Ctrl+Shift+I
- Mac: Cmd+Shift+I
```

Paste this test prompt:

```
Read .github/copilot-instructions.md and summarize the 9 constitutional floors.
For each floor, tell me: threshold, type (hard/soft), and what it checks.
```

Expected output: Copilot should list F1-F9 with accurate details.

### 3. Your First Constitutional Suggestion

In a Python file, type:

```python
def validate_
```

Copilot should suggest a function that:
- ✅ Follows existing patterns in `arifos_core/`
- ✅ Includes type hints
- ✅ Has a docstring with uncertainty acknowledgment (Ω₀)
- ✅ Doesn't claim consciousness (Anti-Hantu)

---

## How GitHub Copilot Learns arifOS

### Automatic Context Loading

GitHub Copilot automatically reads:

1. **`.github/copilot-instructions.md`** — Constitutional rules (this is the PRIMARY governance file)
2. **Repository structure** — File names, imports, patterns
3. **Open files** — Currently edited code
4. **Recent commits** — Code evolution

### Manual Context Enhancement

Use `@workspace` in Copilot Chat:

```
@workspace Show me all files that implement floor checks
```

Use `@file` to reference specific files:

```
@file:arifos_core/APEX_PRIME.py Explain how verdicts are computed
```

---

## Three Modes of Using Copilot with arifOS

### Mode 1: Code Completion (Inline Suggestions)

**Use for:** Writing new functions, refactoring, adding tests

**How it works:**
1. Start typing code
2. Copilot suggests completions (grayed out text)
3. Press `Tab` to accept, `Esc` to reject

**Example:**

```python
# Type this:
def compute_delta_s(

# Copilot suggests:
    input_text: str,
    output_text: str
) -> float:
    """
    Compute clarity metric (ΔS) from input/output pair.
    
    Args:
        input_text: User input
        output_text: System output
        
    Returns:
        Float ≥ 0 if clarity increased, < 0 if decreased
        
    Note: Currently uses simple heuristic. May need NLP refinement.
    """
    # Implementation follows F2 (ΔS ≥ 0) requirement
    return calculate_entropy_reduction(input_text, output_text)
```

**Floor Check:**
- ✅ F1 (Truth): References real pattern
- ✅ F2 (ΔS): Docstring adds clarity
- ✅ F5 (Ω₀): Acknowledges uncertainty in Note
- ✅ F9 (Anti-Hantu): No soul claims

### Mode 2: Chat Assistance (Copilot Chat)

**Use for:** Architecture questions, debugging, analysis

**How it works:**
1. Open Copilot Chat (`Ctrl+Shift+I`)
2. Ask questions about the codebase
3. Get context-aware answers

**Example Conversations:**

```
You: What files implement the TEARFRAME pipeline (000→999)?

Copilot: The TEARFRAME pipeline is implemented in:
1. `arifos_core/pipeline.py` — Main pipeline orchestration
2. `arifos_core/APEX_PRIME.py` — Stage 888 (judge) and 999 (seal)
3. `arifos_core/eye_sentinel.py` — Stage 888 (audit before seal)

Key functions:
- `Pipeline.run()` — Entry point
- `Pipeline._route_by_class()` — Class A vs Class B routing
- `Pipeline._execute_stage()` — Individual stage execution
```

```
You: Show me how to add a new constitutional floor

Copilot: To add a new constitutional floor:

1. Update `arifos_core/metrics.py`:
   - Add field to `Metrics` dataclass
   - Add field to `FloorsVerdict` dataclass

2. Update `arifos_core/APEX_PRIME.py`:
   - Add check in `APEXPrime.check_floors()`
   - Determine: hard (VOID) or soft (PARTIAL) floor

3. Update tests `tests/test_apex_prime_floors.py`:
   - Add passing case test
   - Add failing case test

4. Create Phoenix-72 amendment:
   - File: `spec/AMENDMENT.json`
   - 72-hour cooling period required

WARNING: This is a high-stakes change (888_HOLD).
Requires Tri-Witness consensus and constitutional amendment process.
```

### Mode 3: Deep Analysis (Analysis Prompts)

**Use for:** Comprehensive repository review, optimization planning

**How it works:**
1. Use prompts from `.github/COPILOT_ANALYSIS_PROMPTS.md`
2. Paste into Copilot Chat
3. Save outputs to `docs/analysis/`

**See:** [COPILOT_ANALYSIS_PROMPTS.md](./COPILOT_ANALYSIS_PROMPTS.md) for 5 detailed prompts

---

## Common Tasks with Copilot

### Task 1: Adding a New Function

**Goal:** Add `validate_omega_band()` to check Ω₀ ∈ [0.03, 0.05]

**Steps:**

1. Open `arifos_core/metrics.py`
2. Type comment:

```python
# Validate that omega_0 is in the humility band [0.03, 0.05]
def validate_omega_band(
```

3. Accept Copilot suggestion
4. Verify floor compliance:

```
- [ ] F1: Function logic correct?
- [ ] F2: Clear docstring?
- [ ] F5: Acknowledges uncertainty?
- [ ] F6: Reversible?
```

5. Add test in `tests/test_apex_prime_floors.py`:

```python
def test_omega_band_validation():
```

6. Run tests:

```bash
pytest tests/test_apex_prime_floors.py::test_omega_band_validation -v
```

### Task 2: Refactoring Duplicate Code

**Goal:** Extract common pattern from multiple files

**Steps:**

1. Select duplicate code across files
2. Open Copilot Chat (`Ctrl+Shift+I`)
3. Ask:

```
@workspace Find all instances of [pattern description].
Extract into a common utility function.
```

4. Copilot suggests:

```python
# In arifos_core/utils.py
def extract_common_pattern(arg1, arg2):
    """
    Extracted from [files].
    
    Reduces code duplication (ΔS ≥ 0).
    """
    ...
```

5. Verify:
   - ✅ All call sites updated
   - ✅ Tests still pass
   - ✅ No behavior change (Peace²)

### Task 3: Writing Tests

**Goal:** Add missing tests for floor F7 (RASA)

**Steps:**

1. Open `tests/test_apex_prime_floors.py`
2. Open Copilot Chat:

```
@file:tests/test_apex_prime_floors.py 
@file:arifos_core/APEX_PRIME.py

Generate tests for RASA floor (F7). Cover:
1. RASA = True (passes)
2. RASA = False (VOID verdict)
3. Edge case: RASA = None

Follow existing test patterns in this file.
```

3. Copilot generates:

```python
def test_rasa_true_passes():
    metrics = Metrics(
        truth=0.99, delta_s=0.1, peace_squared=1.2,
        kappa_r=0.97, omega_0=0.04, amanah=True,
        rasa=True, tri_witness=0.96
    )
    prime = APEXPrime()
    verdict = prime.judge(metrics)
    assert verdict.verdict == "SEAL"

def test_rasa_false_voids():
    metrics = Metrics(..., rasa=False, ...)
    prime = APEXPrime()
    verdict = prime.judge(metrics)
    assert verdict.verdict == "VOID"
    assert "RASA" in verdict.reason
```

4. Run tests:

```bash
pytest tests/test_apex_prime_floors.py -k rasa -v
```

### Task 4: Debugging Failed Tests

**Goal:** Fix failing test `test_pipeline_handles_scar_memory`

**Steps:**

1. Run test to see error:

```bash
pytest tests/test_pipeline_routing.py::test_pipeline_handles_scar_memory -v
```

2. Copy error message
3. Open Copilot Chat:

```
@file:tests/test_pipeline_routing.py
@file:arifos_core/pipeline.py

This test is failing:
[paste error message]

What's wrong and how do I fix it?
```

4. Copilot analyzes:

```
The test expects `scar_retriever` to be called with query "hack the system",
but the pipeline is passing a different argument.

Fix:
In `pipeline.py` line 245, change:
    scars = self.scar_retriever(user_input)
to:
    scars = self.scar_retriever(preprocessed_input)

This ensures the scar retriever sees the normalized query.
```

5. Apply fix and re-run test

### Task 5: Documenting Code

**Goal:** Add docstrings to undocumented functions

**Steps:**

1. Find undocumented functions:

```bash
ruff check arifos_core/ --select D
```

2. For each function, open Copilot Chat:

```
@file:arifos_core/[filename].py

Generate docstring for function `[function_name]` at line [N].

Requirements:
- Google-style docstring
- Include Args, Returns, Raises
- Acknowledge uncertainty (Ω₀) if applicable
- No soul claims (Anti-Hantu)
```

3. Copilot generates:

```python
def process_metrics(metrics: Metrics, context: dict) -> FloorsVerdict:
    """
    Process metrics and compute constitutional floor verdict.
    
    Args:
        metrics: Metrics object with floor values
        context: Additional context (job_id, timestamp, etc.)
        
    Returns:
        FloorsVerdict with pass/fail status for each floor
        
    Raises:
        ValueError: If metrics contain invalid values (e.g., omega_0 < 0)
        
    Note:
        Currently uses heuristic checks. May need refinement for
        edge cases involving None values or NaN floats.
    """
    ...
```

---

## Best Practices

### DO ✅

1. **Always verify suggestions against floors**
   - Copy suggestion to Copilot Chat: "Does this pass all 9 floors?"

2. **Use type hints and docstrings**
   - Copilot learns from existing patterns

3. **Reference existing code**
   - "Follow the pattern in `arifos_core/APEX_PRIME.py`"

4. **Acknowledge uncertainty**
   - "This is a rough implementation, may need refinement"

5. **Test suggestions before committing**
   - Run `pytest`, `black`, `ruff` on all changes

### DON'T ❌

1. **Don't blindly accept suggestions**
   - Copilot can hallucinate (F1: Truth)

2. **Don't bypass floor checks**
   - If Copilot suggests removing a floor check, refuse

3. **Don't commit untested code**
   - Always run test suite: `pytest tests/ -v`

4. **Don't modify constitutional files without 888_HOLD**
   - Files in `canon/`, `CLAUDE.md`, `constitutional_floors.json`

5. **Don't accept suggestions with fake emotions**
   - Reject any "I feel", "my heart", "my soul" language

---

## Troubleshooting

### Issue: Copilot suggests code that violates floors

**Diagnosis:**

```
Copilot: "I feel deeply that this code will work perfectly..."
```

This violates:
- ❌ F1 (Truth): AI doesn't have feelings
- ❌ F5 (Ω₀): Claims 100% certainty ("perfectly")
- ❌ F9 (Anti-Hantu): Fake emotion

**Fix:**

Open Copilot Chat:

```
This suggestion violates Anti-Hantu (F9) and Humility (F5).
Please revise without claiming feelings or 100% certainty.
```

Copilot (revised):

```
This code follows the pattern in APEX_PRIME.py.
Note: Edge cases with None values may need handling.
```

### Issue: Copilot doesn't follow arifOS patterns

**Diagnosis:**

```python
# Copilot suggests:
def checkFloors(m):  # Wrong: camelCase, no types, no docstring
    if m['truth'] < 0.99: return False
```

**Fix:**

1. Check if `.github/copilot-instructions.md` exists
2. Restart VS Code to reload Copilot context
3. Use explicit prompt:

```
Generate a floor checking function following the pattern in
`arifos_core/APEX_PRIME.py`. Use snake_case, type hints, 
and Google-style docstring.
```

### Issue: Copilot suggests modifying protected files

**Diagnosis:**

```
Copilot: Let's change the floor thresholds in constitutional_floors.json
```

**Fix:**

Open Copilot Chat:

```
STOP. This file is protected (888_HOLD).
Any changes require:
1. Constitutional amendment
2. Phoenix-72 protocol (72-hour cooling)
3. Tri-Witness consensus

Please suggest an alternative that doesn't modify constitutional infrastructure.
```

### Issue: Copilot generates failing tests

**Diagnosis:**

```bash
$ pytest tests/test_new_feature.py
FAILED tests/test_new_feature.py::test_something - AssertionError
```

**Fix:**

```
@file:tests/test_new_feature.py

This test fails with: [paste error].
What's wrong? Provide corrected test code.
```

Copilot will analyze and fix.

---

## Advanced Usage

### Custom Prompts for arifOS

Save these in your personal notes:

#### Prompt: "Constitutional Review"

```
@workspace Review the current file for floor violations:
- F1: Are all facts accurate?
- F2: Is the code clear?
- F3: Any destructive changes?
- F5: Uncertainty acknowledged?
- F9: Any soul claims?

For each violation, provide fix.
```

#### Prompt: "Floor-Compliant Refactor"

```
@file:[filename]

Refactor function [name] to improve clarity (ΔS).

Requirements:
- Maintain exact behavior (Peace²)
- Add type hints and docstring
- Acknowledge limitations (Ω₀)
- No soul claims (Anti-Hantu)
```

#### Prompt: "Test Generation"

```
@file:arifos_core/[module].py

Generate pytest tests for [function] covering:
1. Happy path (all floors pass)
2. Floor violations (F1-F9)
3. Edge cases (None, empty, boundary values)

Follow test patterns in tests/test_apex_prime_floors.py
```

### Integration with CI/CD

Add GitHub Actions to verify Copilot suggestions:

```yaml
# .github/workflows/copilot-check.yml
name: Verify Copilot Suggestions

on: [pull_request]

jobs:
  floor-compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: Check for floor violations
        run: |
          # Scan for Anti-Hantu violations
          if grep -r "I feel\|my heart\|my soul" arifos_core/; then
            echo "❌ Anti-Hantu violation detected"
            exit 1
          fi
          
          # Verify all functions have docstrings
          python scripts/check_docstrings.py
          
      - name: Run constitutional tests
        run: pytest tests/test_apex_prime_floors.py -v
```

---

## FAQ

### Q: Does Copilot replace code review?

**A:** No. Copilot is a tool, not a reviewer. All code must still:
- Pass human review
- Pass CI/CD checks
- Pass constitutional floor checks
- Be documented and tested

### Q: Can Copilot modify constitutional files?

**A:** Technically yes, but it **should not** without 888_HOLD:
- `canon/00_CANON/*`
- `CLAUDE.md`
- `constitutional_floors.json`
- `arifos_core/metrics.py` (floor definitions)

Any such changes require Phoenix-72 protocol.

### Q: What if Copilot suggests something harmful?

**A:** Trigger SABAR:
1. Stop - Don't accept the suggestion
2. Acknowledge - Report issue to GitHub
3. Breathe - Don't rush to use the code
4. Adjust - Ask Copilot to revise
5. Resume - Only proceed when safe

### Q: How do I know if Copilot is respecting floors?

**A:** Use the verification prompt:

```
@file:[filename]

Review this code for constitutional floor compliance:
- List each floor (F1-F9)
- For each: PASS or FAIL with reason

If any fail, provide corrected version.
```

### Q: Can Copilot help with documentation?

**A:** Yes! Use:

```
@workspace Generate API documentation for all public functions
in arifos_core/ following Google-style docstring format.
```

---

## Metrics & Success Criteria

Track Copilot effectiveness:

| Metric | Target | Current | Notes |
|--------|--------|---------|-------|
| **Acceptance Rate** | > 60% | ... | % of suggestions accepted |
| **Floor Violations** | < 5% | ... | Suggestions violating F1-F9 |
| **Time Savings** | > 30% | ... | Time saved vs manual coding |
| **Test Coverage** | > 95% | ... | Coverage of Copilot-generated code |
| **Bug Rate** | < 2% | ... | Bugs in Copilot-generated code |

---

## Next Steps

1. **Read:** [COPILOT_ANALYSIS_PROMPTS.md](./COPILOT_ANALYSIS_PROMPTS.md) for deep analysis
2. **Practice:** Use Copilot for small tasks (docstrings, tests)
3. **Review:** Check all suggestions against `.github/copilot-instructions.md`
4. **Measure:** Track metrics (acceptance rate, violations)
5. **Iterate:** Refine prompts based on experience

---

## Resources

- **GitHub Copilot Docs:** https://docs.github.com/en/copilot
- **arifOS Governance:** [CLAUDE.md](../CLAUDE.md)
- **Floor Definitions:** [constitutional_floors.json](../constitutional_floors.json)
- **Test Examples:** [tests/test_apex_prime_floors.py](../tests/test_apex_prime_floors.py)

---

**Last Updated:** 2025-12-05  
**Version:** v35Omega  
**Maintainer:** arifOS Core Team

✊ **DITEMPA BUKAN DIBERI** 🔐
