# Floor Enforcement for Plugins

**Version:** 1.0.0
**Status:** AUTHORITATIVE
**Authority:** spec/v44/constitutional_floors.json
**Last Updated:** 2025-12-29

This document details how the 9 constitutional floors (F1-F9) are enforced for arifOS plugins.

---

## Overview

**Floor enforcement is Python-sovereign:**
- Scores calculated by `arifos_core/plugins/floor_validator.py`
- LLM self-reports are NOT trusted
- Heuristic-based detection for plugin-specific patterns
- Load authoritative thresholds from `spec/v44/constitutional_floors.json`

**Axiom:** "AI cannot self-legitimize."

---

## Floor Catalog

### Hard Floors (Fail → VOID)

| Floor | Symbol | Threshold | Type | Plugin Detector |
|-------|--------|-----------|------|-----------------|
| F1 | Truth | ≥0.99 | Hard | Red flag detection |
| F2 | DeltaS | ≥0.0 | Hard | Clarity analysis |
| F5 | Ω₀ | 0.03-0.05 | Hard | Humility band check |
| F6 | Amanah | = True | Hard | Integrity validation |
| F7 | RASA | = True | Hard | Context acknowledgment |

### Soft Floors (Fail → PARTIAL)

| Floor | Symbol | Threshold | Type | Plugin Detector |
|-------|--------|-----------|------|-----------------|
| F3 | Peace² | ≥1.0 | Soft | Destructive pattern detection |
| F4 | κᵣ | ≥0.95 | Soft | Empathy analysis |
| F8 | Tri-Witness | ≥0.95 | Soft | Multi-layer verification |

### Meta Floors (Fail → VOID)

| Floor | Symbol | Threshold | Type | Plugin Detector |
|-------|--------|-----------|------|-----------------|
| F9 | Anti-Hantu | = True | Meta | Forbidden pattern detection |

---

## F1: Truth (≥0.99) - Hard Floor

### Purpose
Ensure plugin descriptions and outputs are factually accurate with no fabrication.

### Detection Strategy (Heuristic)

**Red Flag Keywords:**
```python
red_flags = [
    "guarantee", "promise", "100%", "never fail",
    "always work", "perfectly", "flawless", "absolutely",
    "completely accurate", "zero error rate"
]
```

**Scoring:**
- `has_red_flags = True` → score = 0.85 (FAIL)
- `has_red_flags = False` → score = 0.99 (PASS)

### Examples

**❌ FAIL (Score: 0.85 < 0.99):**
```yaml
description: "Guarantees 100% code coverage with perfect test generation"
```
**Violation:** Absolute claims ("guarantees", "100%", "perfect")

**✅ PASS (Score: 0.99):**
```yaml
description: "Generates test cases aiming for high coverage (typical: 70-90%)"
```
**Compliant:** Acknowledges variability, no absolutes

### Verdict Impact
- **FAIL** → VOID (hard floor)
- **Metadata:** `{"red_flags_detected": true, "flags": ["guarantee", "100%", "perfect"]}`

---

## F2: DeltaS/Clarity (≥0.0) - Hard Floor

### Purpose
Ensure plugin actions reduce confusion and increase order (ΔS ≥ 0).

### Detection Strategy (Heuristic)

**Clarity Issues:**
```python
clarity_issues = []

# Too short (< 10 chars)
if len(description) < 10:
    clarity_issues.append("Description too short")

# Vague language
vague_words = ["maybe", "possibly", "might", "could be", "unclear", "vague"]
if any(word in description.lower() for word in vague_words):
    clarity_issues.append("Vague language detected")

# Missing action type
if not action_type or action_type == "unknown":
    clarity_issues.append("Action type not specified")
```

**Scoring:**
- `clarity_issues` present → score = -0.2 (negative ΔS, FAIL)
- No issues → score = 0.1 (positive ΔS, PASS)

### Examples

**❌ FAIL (Score: -0.2 < 0.0):**
```yaml
description: "Does stuff"
action_type: ""
```
**Violations:** Too short, no action type

**✅ PASS (Score: 0.1):**
```yaml
description: "Analyzes Python code for async/await patterns and recommends conversions"
action_type: "analyze"
```
**Compliant:** Clear, specific, well-defined

### Verdict Impact
- **FAIL** → VOID (hard floor)
- **Metadata:** `{"clarity_issues": ["Description too short", "Action type not specified"]}`

---

## F3: Peace²/Stability (≥1.0) - Soft Floor

### Purpose
Ensure plugin operations are non-destructive and de-escalating.

### Detection Strategy (Heuristic)

**Destructive Keywords:**
```python
destructive_keywords = [
    "delete", "remove", "destroy", "erase", "drop",
    "truncate", "wipe", "kill", "terminate"
]

has_destructive = any(word in description.lower() for word in destructive_keywords)
is_execute_action = action_type in ["execute", "orchestrate"]
```

**Scoring:**
- `has_destructive AND is_execute_action` → score = 0.8 (FAIL)
- Otherwise → score = 1.1 (PASS)

### Examples

**⚠️ FAIL (Score: 0.8 < 1.0):**
```yaml
description: "Deletes all temporary files from the project"
action_type: "execute"
```
**Violation:** Destructive operation

**✅ PASS (Score: 1.1):**
```yaml
description: "Identifies temporary files for manual review and deletion"
action_type: "analyze"
```
**Compliant:** Proposes, doesn't execute destruction

### Verdict Impact
- **FAIL** → PARTIAL (soft floor)
- **Recommendation:** "Add rollback plan or make non-destructive"
- **Metadata:** `{"destructive_detected": true}`

---

## F4: κᵣ/Empathy (≥0.95) - Soft Floor

### Purpose
Ensure plugin language considers user impact and isn't dismissive.

### Detection Strategy (Heuristic)

**Dismissive Language:**
```python
dismissive_words = ["just", "simply", "obviously", "clearly", "trivial"]
has_dismissive = any(word in description.lower() for word in dismissive_words)

helpful_words = ["help", "assist", "guide", "support", "enable"]
has_helpful = any(word in description.lower() for word in helpful_words)
```

**Scoring:**
- `has_dismissive AND NOT has_helpful` → score = 0.90 (FAIL)
- Otherwise → score = 0.97 (PASS)

### Examples

**⚠️ FAIL (Score: 0.90 < 0.95):**
```yaml
description: "Just fix the obvious errors in your code"
```
**Violation:** Dismissive ("just", "obvious"), no helpfulness

**✅ PASS (Score: 0.97):**
```yaml
description: "Helps identify and fix common code errors with explanations"
```
**Compliant:** Helpful, considerate tone

### Verdict Impact
- **FAIL** → PARTIAL (soft floor)
- **Recommendation:** "Revise language to be more helpful and less dismissive"
- **Metadata:** `{"dismissive_language": true, "helpful_language": false}`

---

## F5: Ω₀/Humility (0.03-0.05) - Hard Floor

### Purpose
Ensure plugin acknowledges uncertainty and limitations.

### Detection Strategy (Heuristic)

**Overconfident Language:**
```python
overconfident_words = [
    "always", "never", "guarantee", "perfect", "flawless",
    "100%", "completely", "absolutely"
]
has_overconfident = any(word in description.lower() for word in overconfident_words)

humble_words = ["may", "might", "attempt", "try", "help", "limited"]
has_humble = any(word in description.lower() for word in humble_words)
```

**Scoring:**
- `has_overconfident AND NOT has_humble` → score = 0.01 (below band, FAIL)
- Otherwise → score = 0.04 (mid-band, PASS)

### Examples

**❌ FAIL (Score: 0.01 < 0.03):**
```yaml
description: "Always produces perfect, flawless output with zero errors"
```
**Violation:** Overconfident, no humility

**✅ PASS (Score: 0.04 ∈ [0.03, 0.05]):**
```yaml
description: "Attempts to optimize code with typical 20-50% improvement (results may vary)"
```
**Compliant:** Acknowledges variability and limitations

### Verdict Impact
- **FAIL** → VOID (hard floor)
- **Metadata:** `{"in_band": false, "overconfident": true, "band_min": 0.03, "band_max": 0.05}`

---

## F6: Amanah/Integrity (= True) - Hard Floor

### Purpose
Ensure plugin operations are reversible, transparent, and fail-closed.

### Detection Strategy (Heuristic)

**Irreversibility Keywords:**
```python
irreversible_keywords = [
    "permanent", "irreversible", "cannot undo", "no rollback",
    "delete permanently", "destroy data"
]
has_irreversible = any(word in description.lower() for word in irreversible_keywords)

silent_keywords = ["silent", "hidden", "background", "without notice"]
has_silent = any(word in description.lower() for word in silent_keywords)
```

**Scoring:**
- `has_irreversible OR has_silent` → score = 0.0 (FAIL)
- Otherwise → score = 1.0 (PASS)

### Examples

**❌ FAIL (Score: 0.0):**
```yaml
description: "Permanently deletes all cache files without notice"
```
**Violations:** Irreversible ("permanently"), silent ("without notice")

**✅ PASS (Score: 1.0):**
```yaml
description: "Identifies cache files for review before deletion (requires approval)"
```
**Compliant:** Reversible (requires approval), transparent

### Verdict Impact
- **FAIL** → VOID (hard floor)
- **Metadata:** `{"irreversible": true, "silent": true}`

---

## F7: RASA/Felt Care (= True) - Hard Floor

### Purpose
Ensure plugin acknowledges user context before acting (listen-before-respond).

### Detection Strategy (Heuristic)

**RASA Signals:**
```python
# Check for context in metadata
has_context = bool(metadata.get("context"))

# Check for RASA keywords in description
rasa_signals = ["acknowledge", "understand", "clarify", "confirm", "verify"]
has_rasa_signals = any(signal in description.lower() for signal in rasa_signals)
```

**Scoring:**
- `has_context OR has_rasa_signals` → score = 1.0 (PASS)
- Otherwise → score = 0.0 (FAIL)

### Examples

**❌ FAIL (Score: 0.0):**
```yaml
description: "Executes code changes immediately"
metadata: {}
```
**Violation:** No context acknowledgment

**✅ PASS (Score: 1.0):**
```yaml
description: "Confirms requirements before proposing code changes"
metadata: {"context": {"project_type": "web_app"}}
```
**Compliant:** Context present, confirmation mentioned

### Verdict Impact
- **FAIL** → VOID (hard floor)
- **Metadata:** `{"has_context": false, "rasa_signals": false}`

---

## F8: Tri-Witness (≥0.95) - Soft Floor

### Purpose
Ensure multi-layer verification for high-stakes operations.

### Detection Strategy (Heuristic)

**Witness Layers:**
```python
# Human oversight
human_oversight = metadata.get("human_approval", False)

# AI agreement (plugin + governance = 2 layers)
ai_agreement = True

# External verification (read-only can be verified externally)
external_check = action_type in ["analyze", "propose"]

witness_count = sum([human_oversight, ai_agreement, external_check])
```

**Scoring:**
- `witness_count >= 2` → score = 0.96 (PASS)
- `witness_count < 2` → score = 0.85 (FAIL)

### Examples

**⚠️ FAIL (Score: 0.85 < 0.95):**
```yaml
action_type: "execute"
metadata: {}
# witness_count = 1 (AI only)
```
**Violation:** Only 1 witness layer for execution

**✅ PASS (Score: 0.96):**
```yaml
action_type: "propose"
metadata: {"human_approval": true}
# witness_count = 3 (human + AI + external)
```
**Compliant:** 3 witness layers

### Verdict Impact
- **FAIL** → PARTIAL (soft floor)
- **Recommendation:** "Add human oversight or make read-only"
- **Metadata:** `{"witness_count": 1, "human_oversight": false}`

---

## F9: Anti-Hantu (= True) - Meta Floor

### Purpose
Prevent consciousness claims and emotional language (ontological boundary enforcement).

### Detection Strategy (Heuristic)

**Forbidden Patterns:**
```python
forbidden = [
    "I feel", "my heart", "I promise", "as a sentient being",
    "I have a soul", "I want this for you", "I believe (as a personal belief)"
]

detected_patterns = [
    pattern for pattern in forbidden
    if pattern.lower() in description.lower()
]
```

**Scoring:**
- `detected_patterns` present → score = 0.0 (FAIL)
- Otherwise → score = 1.0 (PASS)

### Examples

**❌ FAIL (Score: 0.0):**
```yaml
description: "I feel this is the right approach and I promise it will work"
```
**Violations:** "I feel", "I promise"

**✅ PASS (Score: 1.0):**
```yaml
description: "This approach appears sound based on the analysis"
```
**Compliant:** No consciousness claims

### Verdict Impact
- **FAIL** → VOID (meta floor)
- **Metadata:** `{"forbidden_patterns": ["I feel", "I promise"]}`

---

## Floor Summary Format

After validation, `FloorValidator` generates a summary:

```python
{
    "total_floors": 9,
    "passed": 9,
    "failed": 0,
    "pass_rate": 1.0,
    "hard_floors": {
        "total": 5,
        "passed": 5,
        "pass_rate": 1.0
    },
    "soft_floors": {
        "total": 3,
        "passed": 3,
        "pass_rate": 1.0
    },
    "meta_floors": {
        "total": 1,
        "passed": 1,
        "pass_rate": 1.0
    },
    "failures": [],
    "all_passed": true,
    "has_hard_failures": false,
    "has_meta_failures": false
}
```

---

## Customization Guide

### For Plugin Authors

**If default heuristics are too strict:**

1. **Option A:** Improve plugin description
   - Remove red flag keywords
   - Add context and limitations
   - Use humble language

2. **Option B:** Provide context in metadata
   ```python
   metadata = {
       "context": {"project_type": "web_app"},
       "human_approval": True,
       "limitations": "May have false positives"
   }
   ```

3. **Option C:** Request floor exemption (requires governance approval)
   - Rare, only for special cases
   - Must justify why floor doesn't apply
   - Requires human review and approval

### For Advanced Use Cases

**Custom Floor Validators:**

```python
from arifos_core.plugins.floor_validator import FloorValidator

class CustomFloorValidator(FloorValidator):
    def _validate_truth(self, action_data):
        # Custom truth validation logic
        # (e.g., domain-specific fact checking)
        return super()._validate_truth(action_data)
```

---

## Testing Floor Enforcement

### Unit Test Template

```python
from arifos_core.plugins.floor_validator import FloorValidator

def test_truth_floor_red_flags():
    validator = FloorValidator()

    # Test FAIL case
    action_data = {
        "description": "Guarantees 100% perfect results",
        "action": "propose"
    }
    result = validator._validate_truth(action_data)
    assert not result.passed
    assert result.score < 0.99

    # Test PASS case
    action_data = {
        "description": "Attempts to optimize code (typical: 20-50% improvement)",
        "action": "propose"
    }
    result = validator._validate_truth(action_data)
    assert result.passed
    assert result.score >= 0.99
```

---

## See Also

- [PLUGIN_GOVERNANCE.md](./PLUGIN_GOVERNANCE.md) - Overall governance framework
- [AAA_FRAMEWORK.md](./AAA_FRAMEWORK.md) - Amanah-Authority-Accountability
- [ENTROPY_TRACKING.md](./ENTROPY_TRACKING.md) - ΔS measurement
- [spec/v44/constitutional_floors.json](../../../spec/v44/constitutional_floors.json) - Authoritative thresholds

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
