# Phoenix-72 Protocol: Constitutional Drift & Entropy Guardrails

**Version:** v45.1
**Status:** ENFORCED (CI-gated)
**Authority:** Phoenix-72 Governance Amendment

---

## Overview

The Phoenix-72 Protocol enforces two critical invariants to prevent constitutional decay:

1. **THRESHOLD SOVEREIGNTY** — Spec is the sole authority for constitutional thresholds
2. **ENTROPY CONSTRAINT** — Net LOC cannot grow without justification (ΔS ≤ 0)

These guardrails run automatically in CI and will fail builds that violate constraints.

---

## The Two Invariants

### 1. Threshold Sovereignty

**Principle:** Constitutional thresholds must ONLY appear via spec-loaded imports, never as hardcoded literals.

**Rationale:** Hardcoded thresholds create drift between spec (canonical truth) and runtime (enforcement). When thresholds are duplicated, they diverge over time, leading to constitutional violations.

**Forbidden:**
```python
# ❌ VIOLATION - Hardcoded threshold
if metrics.truth >= 0.99:
    return "SEAL"

# ❌ VIOLATION - Magic number
G_SEAL_THRESHOLD = 0.80  # No spec reference
```

**Allowed:**
```python
# ✅ COMPLIANT - Imported from spec-loaded module
from arifos_core.enforcement.metrics import TRUTH_THRESHOLD
if metrics.truth >= TRUTH_THRESHOLD:
    return "SEAL"

# ✅ COMPLIANT - Spec anchor comment
G_SEAL_THRESHOLD = 0.80  # spec/v44/genius_law.json:22 (F8 SEAL)

# ✅ COMPLIANT - Dynamic spec loading
thresholds = load_spec("constitutional_floors.json")
if metrics.truth >= thresholds["truth"]["threshold"]:
    return "SEAL"
```

**Protected Thresholds:**
- `0.99` — F2 Truth SEAL threshold
- `0.95` — F3 Tri-Witness, F6 κᵣ thresholds
- `0.90` — Truth hallucination block
- `0.80` — F8 Genius SEAL threshold
- `0.50` — F8 Genius MIN threshold
- `0.30` — F9 C_dark SEAL threshold
- `0.60` — F9 C_dark PARTIAL threshold
- `1.0` — F5 Peace² threshold
- `0.05` — F7 Ω₀ upper band
- `0.03` — F7 Ω₀ lower band

### 2. Entropy Constraint (ΔS ≤ 0)

**Principle:** The codebase cannot grow in net lines of code without explicit justification.

**Rationale:** Entropy (disorder/complexity) naturally increases over time. The Phoenix-72 constraint enforces "replace-only" development: new features must either refactor existing code (net zero) or be explicitly justified.

**Formula:**
```
ΔS_new + ΔS_existing ≤ 0

Where:
  ΔS_new = LOC added in this change
  ΔS_existing = Cumulative justified LOC from previous changes
```

**Development Modes:**

**1. Net-Zero Development (PREFERRED):**
```bash
# Add 50 LOC of new feature
# Remove 50 LOC of redundant code
# Net: 0 LOC → Passes constraint
```

**2. Net-Negative Development (IDEAL):**
```bash
# Refactor 100 LOC into 60 LOC
# Net: -40 LOC → Passes constraint + builds credit
```

**3. Justified Growth (REQUIRES APPROVAL):**
```bash
# Add 80 LOC for new floor detector
# No equivalent removal possible
# Add justification to .phoenix_justifications.json
# Update baseline after approval
```

---

## Running the Guardrail

### Local Check (Before Commit)

```bash
# Run both checks
python scripts/phoenix_72_guardrail.py

# Run specific check
python scripts/phoenix_72_guardrail.py --check thresholds
python scripts/phoenix_72_guardrail.py --check entropy
```

### CI Integration

The guardrail runs automatically in CI via pytest:

```bash
pytest tests/test_phoenix_72_guardrail.py -v
```

**CI will fail if:**
- Hardcoded thresholds detected (exit code 1)
- Entropy growth unjustified (exit code 2)
- Both violations (exit code 3)

### Test Suite Integration

The guardrail is part of the standard test suite:

```bash
pytest  # Runs all tests including Phoenix-72 checks
```

---

## Handling Violations

### Threshold Drift Detected

**Error:**
```
❌ THRESHOLD DRIFT DETECTED: 3 violations

  arifos_core/system/apex_prime.py:347
    Threshold: 0.80 (F8 G SEAL threshold)
    Line: G_SEAL_THRESHOLD = 0.80  # Was hardcoded
```

**Fix Option 1 - Import from spec loader:**
```python
# Before
G_SEAL_THRESHOLD = 0.80

# After
from arifos_core.enforcement.genius_metrics import G_SEAL_THRESHOLD
```

**Fix Option 2 - Add spec anchor comment:**
```python
# After (if dynamic loading not available)
G_SEAL_THRESHOLD = 0.80  # spec/v44/genius_law.json:22 (F8 SEAL)
```

**Fix Option 3 - Load from spec file:**
```python
import json
spec = json.load(open("spec/v44/genius_law.json"))
G_SEAL_THRESHOLD = spec["metrics"]["G"]["thresholds"]["seal"]
```

### Entropy Growth Detected

**Error:**
```
❌ ENTROPY GROWTH DETECTED: +150 LOC without justification

  Baseline: 4500 LOC
  Current:  4650 LOC
  Delta:    +150 LOC
```

**Fix Option 1 - Refactor to net-zero:**
```bash
# Remove equivalent LOC elsewhere
# Example: Merge duplicate functions, remove dead code
# Re-run: python scripts/phoenix_72_guardrail.py
```

**Fix Option 2 - Add justification:**

Create/update `.phoenix_justifications.json`:
```json
[
  {
    "date": "2025-12-26",
    "delta_loc": 150,
    "reason": "Added F10 Dignity floor detector (new constitutional requirement)",
    "approved_by": "human",
    "commit": "abc123f"
  }
]
```

**Fix Option 3 - Update baseline (REQUIRES APPROVAL):**
```bash
# After justification approved
python scripts/phoenix_72_guardrail.py --update-baseline
```

⚠️ **Warning:** Updating baseline without justification bypasses the constraint. Only do this after explicit approval.

---

## Baseline Management

### Initial Baseline

The first time the guardrail runs, it creates `.phoenix_baseline.json`:
```json
{
  "loc": 4500,
  "date": "2025-12-26T10:00:00",
  "note": "Phoenix-72 entropy baseline"
}
```

### Updating Baseline

After justified growth is approved:
```bash
python scripts/phoenix_72_guardrail.py --update-baseline
```

This updates `.phoenix_baseline.json` to the current LOC count.

### Version Control

**Committed to repo:**
- `.phoenix_baseline.json` — LOC baseline (committed)
- `.phoenix_justifications.json` — Growth justifications (committed)

**Ignored:**
- None (all Phoenix-72 files are tracked)

---

## Justification Format

`.phoenix_justifications.json` structure:
```json
[
  {
    "date": "2025-12-26",
    "delta_loc": 150,
    "reason": "Added new floor detector for F10 Dignity",
    "approved_by": "human",
    "commit": "abc123f",
    "files_added": [
      "arifos_core/floor_detectors/dignity_detector.py"
    ],
    "notes": "Required by constitutional amendment Phoenix-73"
  },
  {
    "date": "2025-12-20",
    "delta_loc": 200,
    "reason": "Trinity git governance system",
    "approved_by": "human",
    "commit": "def456a"
  }
]
```

**Required fields:**
- `date` — ISO date of change
- `delta_loc` — LOC increase justified by this entry
- `reason` — Short explanation of why growth is necessary
- `approved_by` — Who approved this growth (usually "human")

**Optional fields:**
- `commit` — Git commit hash
- `files_added` — List of new files
- `notes` — Additional context

---

## Philosophy: Replace-Only Development

Phoenix-72 enforces a **replace-only** development philosophy:

### The Problem: Entropy Growth

```
Traditional Development:
  Year 1: 1000 LOC
  Year 2: 2000 LOC (added features)
  Year 3: 4000 LOC (added more features)
  Year 5: 10000 LOC (unmaintainable)
```

Every line of code is a liability:
- More code = more bugs
- More code = slower compilation/testing
- More code = higher cognitive load
- More code = more attack surface

### The Phoenix-72 Solution

```
Phoenix-72 Development:
  Year 1: 1000 LOC
  Year 2: 1000 LOC (refactored, net zero)
  Year 3: 1000 LOC (replaced old with new)
  Year 5: 1000 LOC (still maintainable)
```

**Rules:**
1. **Default: Refactor** — New feature? Refactor old code to make room
2. **Exception: Justify** — Truly new capability? Document why growth is necessary
3. **Discipline: Review** — Baseline updates require explicit approval

### Benefits

- **Maintainability:** Codebase stays compact and comprehensible
- **Quality:** Forces regular refactoring and consolidation
- **Focus:** Prevents feature creep and scope expansion
- **Security:** Smaller attack surface, easier to audit

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -e .
      - name: Run tests (includes Phoenix-72)
        run: pytest -v
```

The Phoenix-72 guardrail runs automatically as part of `pytest`.

### Pre-Commit Hook (Optional)

```bash
# .git/hooks/pre-commit
#!/bin/bash
python scripts/phoenix_72_guardrail.py
if [ $? -ne 0 ]; then
    echo "Phoenix-72 guardrail failed. Commit blocked."
    exit 1
fi
```

---

## FAQ

### Q: Why enforce ΔS ≤ 0 so strictly?

**A:** Entropy is the silent killer of software projects. By the time you realize the codebase is unmaintainable, it's too late. Phoenix-72 prevents this by enforcing discipline from day one.

### Q: What if I need to add a genuinely new feature?

**A:** Add it! But either:
1. Refactor existing code to net-zero growth (preferred), OR
2. Document the justification in `.phoenix_justifications.json`

### Q: Can I update the baseline without justification?

**A:** Technically yes (with `--update-baseline`), but this bypasses the constraint. Only do this after explicit human approval and documentation.

### Q: What about test files?

**A:** Test files are excluded from LOC counting. Only `arifos_core/` production code is measured.

### Q: How do I justify growth?

**A:** Add an entry to `.phoenix_justifications.json` explaining:
- What was added
- Why it couldn't be achieved via refactoring
- Who approved it

Then run `--update-baseline` to reset the constraint.

### Q: What if CI fails on my PR?

**A:** Either:
1. Remove equivalent LOC to achieve net-zero
2. Add justification and get approval
3. Fix threshold drift by using spec imports

---

## Spec Authority Chain

```
spec/v44/constitutional_floors.json (CANONICAL SOURCE)
    ↓
arifos_core/enforcement/metrics.py (SPEC LOADER)
    ↓ TRUTH_THRESHOLD = spec["floors"]["truth"]["threshold"]
    ↓
arifos_core/system/apex_prime.py (ENFORCEMENT)
    ↓ TRUTH_MIN = TRUTH_THRESHOLD  # Import, not hardcode
    ↓
if metrics.truth >= TRUTH_MIN: SEAL
```

**Key Principle:** Spec file is the single source of truth. All runtime constants must trace back to spec.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v45.1 | 2025-12-26 | Initial Phoenix-72 implementation |

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
