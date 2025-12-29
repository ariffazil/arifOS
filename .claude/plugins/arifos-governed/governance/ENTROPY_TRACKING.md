# Entropy Tracking & SABAR-72 Protocol

**Version:** 1.0.0
**Status:** AUTHORITATIVE
**Last Updated:** 2025-12-29

This document details how entropy (ΔS) is measured and how SABAR-72 thermodynamic governance is enforced for arifOS plugins.

---

## Overview

**Entropy is Complexity**

In arifOS, entropy delta (ΔS) measures the complexity added by a plugin action:
- **Positive ΔS** = Increased complexity (more moving parts, harder to understand)
- **Zero ΔS** = Neutral (no complexity added)
- **Negative ΔS** = Reduced complexity (simplification, clarity gained)

**SABAR-72 Threshold:**
- Skills: ΔS ≥ **3.0** → Cooling required
- Agents: ΔS ≥ **5.0** → Cooling required
- Orchestrators: ΔS ≥ **7.0** → Cooling required

**Philosophy:** High entropy requires cooling before execution (Defer, Decompose, Document).

---

## Entropy Components

ΔS is calculated from three components with weighted contributions:

```
ΔS = (Complexity × 2.0) + (Impact × 1.5) + (Cognitive Load × 1.0)
```

### 1. Complexity Score (Weight: 2.0x)

**What it measures:** Intrinsic complexity of the action

**Factors:**
- Number of inputs/parameters
- Number of dependencies
- Action type complexity

**Calculation:**
```python
def calculate_complexity(action_type, metadata):
    score = 0.0

    # Base complexity by action type
    action_complexity = {
        "propose": 0.5,
        "analyze": 1.0,
        "execute": 2.0,
        "orchestrate": 3.0,
    }
    score += action_complexity.get(action_type, 1.0)

    # Input complexity
    inputs = metadata.get("inputs", {})
    input_count = len(inputs) if isinstance(inputs, dict) else 1
    score += min(2.0, input_count * 0.3)  # Cap at 2.0

    # Dependency complexity
    dependencies = metadata.get("dependencies", [])
    dep_count = len(dependencies)
    score += min(2.0, dep_count * 0.5)  # Cap at 2.0

    return min(5.0, score)  # Cap at 5.0
```

**Examples:**

| Action | Inputs | Dependencies | Complexity Score |
|--------|--------|--------------|------------------|
| Simple analysis | 1 | 0 | 1.0 + 0.3 = **1.3** |
| Complex proposal | 10 | 5 | 0.5 + 2.0 (cap) + 2.0 (cap) = **4.5** |
| Orchestration | 5 | 8 | 3.0 + 1.5 + 2.0 (cap) = **5.0** (cap) |

### 2. Impact Score (Weight: 1.5x)

**What it measures:** Side effects and scope of changes

**Factors:**
- Files modified
- External API calls
- State changes (database, cache)
- Irreversible operations

**Calculation:**
```python
def calculate_impact(action_type, metadata):
    score = 0.0

    # File modification impact
    files_modified = metadata.get("files_modified", [])
    file_count = len(files_modified)
    score += min(2.0, file_count * 0.5)  # Cap at 2.0

    # External calls (APIs, services)
    external_calls = metadata.get("external_calls", 0)
    score += min(1.5, external_calls * 0.5)  # Cap at 1.5

    # State changes
    if metadata.get("state_change", False):
        score += 1.0

    # Irreversible operations
    if metadata.get("irreversible", False):
        score += 1.5

    # Execute/orchestrate have inherent impact
    if action_type in ["execute", "orchestrate"]:
        score += 1.0

    return min(5.0, score)  # Cap at 5.0
```

**Examples:**

| Action | Files | External | State | Impact Score |
|--------|-------|----------|-------|--------------|
| Read-only analysis | 0 | 0 | No | **0.0** |
| Modify 3 files | 3 | 0 | No | 1.5 | **1.5** |
| API integration | 0 | 5 | Yes | 2.5 (cap) + 1.0 = **3.5** |
| Database migration | 1 | 0 | Yes + Irreversible | 0.5 + 1.0 + 1.5 + 1.0 = **4.0** |

### 3. Cognitive Load Score (Weight: 1.0x)

**What it measures:** Mental effort required to understand the action

**Factors:**
- Decision points (if/else, switch)
- Branching logic complexity
- Layers of abstraction
- Multi-agent coordination

**Calculation:**
```python
def calculate_cognitive_load(action_type, metadata):
    score = 0.0

    # Decision points
    decision_points = metadata.get("decision_points", 0)
    score += min(2.0, decision_points * 0.5)  # Cap at 2.0

    # Branching complexity
    branches = metadata.get("branches", 0)
    score += min(1.5, branches * 0.3)  # Cap at 1.5

    # Abstractions (layers of indirection)
    abstractions = metadata.get("abstractions", 0)
    score += min(1.0, abstractions * 0.4)  # Cap at 1.0

    # Multi-agent orchestration
    if action_type == "orchestrate":
        agent_count = metadata.get("agent_count", 1)
        score += min(1.5, (agent_count - 1) * 0.5)  # Cap at 1.5

    return min(5.0, score)  # Cap at 5.0
```

**Examples:**

| Action | Decisions | Branches | Abstractions | Agents | Cognitive Load |
|--------|-----------|----------|--------------|--------|----------------|
| Linear analysis | 0 | 0 | 0 | 1 | **0.0** |
| Complex logic | 6 | 8 | 3 | 1 | 2.0 (cap) + 1.5 (cap) + 1.0 (cap) = **4.5** |
| Multi-agent | 2 | 2 | 1 | 5 | 1.0 + 0.6 + 0.4 + 2.0 = **4.0** |

---

## Total Entropy Calculation

### Formula

```
ΔS = (Complexity × 2.0) + (Impact × 1.5) + (Cognitive Load × 1.0)
```

**Weighting Rationale:**
- **Complexity (2.0x):** Intrinsic complexity is hardest to reduce
- **Impact (1.5x):** Side effects add significant risk
- **Cognitive Load (1.0x):** Can be mitigated with documentation

### Example Calculations

#### Example 1: Simple Read-Only Analysis

```python
action_type = "analyze"
metadata = {
    "inputs": {"file_path": "src/main.py"},
    "dependencies": [],
    "files_modified": [],
    "external_calls": 0,
    "state_change": False,
    "decision_points": 1,
    "branches": 0,
    "abstractions": 0,
}

# Component scores
complexity = 1.0 (analyze) + 0.3 (1 input) = 1.3
impact = 0.0 (no modifications)
cognitive_load = 0.5 (1 decision point)

# Total ΔS
ΔS = (1.3 × 2.0) + (0.0 × 1.5) + (0.5 × 1.0)
ΔS = 2.6 + 0.0 + 0.5
ΔS = 3.1

# Verdict: ΔS = 3.1
# - Skills (threshold 3.0): ⚠️ SLIGHTLY OVER (SABAR)
# - Agents (threshold 5.0): ✅ PASS
```

#### Example 2: Multi-File Refactoring

```python
action_type = "execute"
metadata = {
    "inputs": {"pattern": "async/await", "scope": "backend"},
    "dependencies": ["ast", "asyncio"],
    "files_modified": ["routes.py", "models.py", "utils.py"],  # 3 files
    "external_calls": 0,
    "state_change": False,
    "decision_points": 8,
    "branches": 5,
    "abstractions": 2,
}

# Component scores
complexity = 2.0 (execute) + 0.6 (2 inputs) + 1.0 (2 deps) = 3.6
impact = 1.5 (3 files) + 1.0 (execute inherent) = 2.5
cognitive_load = 2.0 (cap, 8 decisions) + 1.5 (cap, 5 branches) + 0.8 (2 abstractions) = 4.3

# Total ΔS
ΔS = (3.6 × 2.0) + (2.5 × 1.5) + (4.3 × 1.0)
ΔS = 7.2 + 3.75 + 4.3
ΔS = 15.25

# Verdict: ΔS = 15.25
# - Skills (threshold 3.0): ❌ FAR OVER (SABAR)
# - Agents (threshold 5.0): ❌ FAR OVER (SABAR)
# - Orchestrators (threshold 7.0): ❌ FAR OVER (SABAR)

# RECOMMENDATION: DECOMPOSE into 3 smaller refactorings
```

#### Example 3: Multi-Agent Orchestration

```python
action_type = "orchestrate"
metadata = {
    "inputs": {"feature": "authentication"},
    "dependencies": [],
    "files_modified": [],  # Orchestrator doesn't modify (delegates)
    "external_calls": 0,
    "agent_count": 4,  # Backend, Frontend, Database, Tests
    "decision_points": 3,
    "branches": 2,
    "abstractions": 1,
}

# Component scores
complexity = 3.0 (orchestrate) + 0.3 (1 input) = 3.3
impact = 1.0 (orchestrate inherent) = 1.0
cognitive_load = 1.5 (3 decisions) + 0.6 (2 branches) + 0.4 (1 abstraction) + 1.5 (cap, 3 extra agents) = 4.0

# Total ΔS
ΔS = (3.3 × 2.0) + (1.0 × 1.5) + (4.0 × 1.0)
ΔS = 6.6 + 1.5 + 4.0
ΔS = 12.1

# Verdict: ΔS = 12.1
# - Orchestrators (threshold 7.0): ❌ OVER (SABAR)

# RECOMMENDATION: DECOMPOSE into 2 orchestrations (2 agents each)
```

---

## SABAR-72 Cooling Protocol

### When Cooling Triggers

| Plugin Type | Threshold | Trigger Condition |
|-------------|-----------|-------------------|
| **Skills** | ΔS ≥ 3.0 | Skills should be focused → low complexity |
| **Agents** | ΔS ≥ 5.0 | Agents coordinate skills → moderate complexity |
| **Orchestrators** | ΔS ≥ 7.0 | Orchestrators coordinate agents → higher complexity |

### SABAR Steps

**S**TOP — Do not execute the action
**A**CKNOWLEDGE — State which threshold was exceeded and why
**B**REATHE — Pause, don't rush to fix
**A**DJUST — Propose cooling options (Defer, Decompose, Document)
**R**ESUME — Only proceed when ΔS < threshold

### Cooling Options

#### Option 1: DEFER

**What:** Pause the action, wait, reconsider necessity

**When to use:**
- Action is nice-to-have, not critical
- System is under high load (many actions queued)
- Better timing exists (off-peak, after deployment)

**Example:**
```
DEFER: Wait for lower-complexity time

Current system load: 8 actions in queue
Estimated ΔS: 6.2 (exceeds 5.0)

Recommendation: Defer this refactoring until:
  - System load < 3 actions
  - After current release (v45.1) ships
  - When baseline ΔS drops to ~0.0

Estimated wait: 2-3 days
```

#### Option 2: DECOMPOSE

**What:** Split into smaller, focused actions

**When to use:**
- Action is necessary but too complex
- Can be logically divided into phases
- Phases have clear boundaries

**Example:**
```
DECOMPOSE: Split into 3 smaller actions

Original: Refactor authentication (ΔS = 15.25)

Phase 1: Add new auth system (ΔS ≈ 4.2)
  - Files: auth_v2.py, config.py
  - No breaking changes
  - Runs in parallel with old system

Phase 2: Migrate users (ΔS ≈ 3.8)
  - Gradual rollout (10% → 50% → 100%)
  - Rollback available at each step

Phase 3: Remove old auth (ΔS ≈ 2.5)
  - After 100% migration confirmed
  - Clean up legacy code

Total: 3 SEAL verdicts > 1 SABAR
```

#### Option 3: DOCUMENT

**What:** Proceed, but add extensive documentation explaining WHY

**When to use:**
- Action is critical and cannot be deferred
- Decomposition would break functionality
- Complexity is inherent to the problem

**Example:**
```
DOCUMENT: Proceed with detailed explanation

ΔS = 7.2 (exceeds 5.0, but required for security fix)

Required documentation:
  1. CHANGELOG entry:
     - What: OAuth 2.0 upgrade
     - Why: CVE-2024-XXXX (critical vulnerability)
     - Impact: All auth flows affected

  2. Architecture doc:
     - Sequence diagrams (before/after)
     - Migration path for existing tokens
     - Rollback procedure

  3. Commit message:
     - Reference CVE
     - Explain complexity necessity
     - Link to architecture doc

Proceed only after documentation is complete.
```

### Cooling Decision Matrix

| ΔS Range | Defer? | Decompose? | Document? | Recommended |
|----------|--------|------------|-----------|-------------|
| 3.0-4.0 | ✅ | ✅ | ✅ | DECOMPOSE (easiest) |
| 4.1-6.0 | ⚠️ | ✅ | ✅ | DECOMPOSE (split 2-3 parts) |
| 6.1-10.0 | ⚠️ | ✅ (required) | ✅ | DECOMPOSE (split 3-5 parts) |
| >10.0 | ✅ (strongly recommended) | ✅ (required) | ❌ (too complex) | DECOMPOSE or DEFER |

---

## Risk Scoring

### Risk Score Calculation

```
Risk Score = min(1.0, ΔS / 10.0)
```

**Normalization:** ΔS scaled to [0.0, 1.0] range

### Risk Levels

| Risk Score | Level | Color | Action |
|------------|-------|-------|--------|
| 0.0-0.3 | 🟢 LOW | Green | Fast track eligible |
| 0.3-0.7 | 🟡 MODERATE | Yellow | Standard review |
| 0.7-1.0 | 🔴 HIGH | Red | Cooling + human approval |

### Risk-Based Verdicts

**Interaction with Floor Failures:**

```python
if delta_s >= threshold:
    verdict = "SABAR"  # Entropy override
elif hard_floor_fail or meta_floor_fail:
    verdict = "VOID"
elif risk_score >= 0.7 and soft_floor_fail:
    verdict = "888_HOLD"  # High risk + warnings
elif soft_floor_fail:
    verdict = "PARTIAL"
else:
    verdict = "SEAL"
```

---

## Session-Level Entropy Tracking

### Cumulative Entropy

For workflows with multiple actions:

```
ΔS_session = Σ(ΔS_i) for all actions i in session
```

**Example:**
```python
actions = [
    {"name": "Analyze code", "ΔS": 1.2},
    {"name": "Propose refactoring", "ΔS": 2.1},
    {"name": "Generate tests", "ΔS": 1.8},
]

ΔS_session = 1.2 + 2.1 + 1.8 = 5.1

# Check against agent threshold (5.0)
if ΔS_session >= 5.0:
    print("SABAR: Cumulative session entropy exceeds threshold")
```

### Entropy Budget

**Set session entropy budget:**
```python
budget = 5.0  # Agent threshold
spent = 0.0

for action in actions:
    if spent + action.ΔS > budget:
        print(f"SABAR: Budget exhausted ({spent}/{budget})")
        print(f"Cannot execute: {action.name} (ΔS = {action.ΔS})")
        break

    execute(action)
    spent += action.ΔS
```

---

## Entropy Reduction Strategies

### How to Lower ΔS

#### 1. Reduce Complexity

**Before (ΔS = 4.5):**
```python
action = {
    "inputs": {
        "file_path": "src/",  # Entire directory
        "patterns": ["async", "sync", "blocking", "performance"],  # 4 patterns
        "depth": "full",
        "include_tests": True,
        "generate_report": True,
    },
    "dependencies": ["ast", "asyncio", "typing", "pathlib"],  # 4 deps
}
```

**After (ΔS = 1.8):**
```python
action = {
    "inputs": {
        "file_path": "src/routes.py",  # Single file
        "pattern": "async",  # Single pattern
    },
    "dependencies": ["ast"],  # Single dep
}
```

**ΔS Reduction:** 4.5 → 1.8 (60% reduction)

#### 2. Reduce Impact

**Before (ΔS = 6.0):**
```python
action = {
    "files_modified": ["a.py", "b.py", "c.py", "d.py", "e.py"],  # 5 files
    "external_calls": 3,
    "state_change": True,
}
```

**After (ΔS = 2.5):**
```python
action = {
    "files_modified": ["a.py"],  # 1 file
    "external_calls": 0,
    "state_change": False,  # Read-only
}
```

**ΔS Reduction:** 6.0 → 2.5 (58% reduction)

#### 3. Reduce Cognitive Load

**Before (ΔS = 5.2):**
```python
action = {
    "decision_points": 12,  # Complex branching
    "branches": 8,
    "abstractions": 3,  # Multiple layers
}
```

**After (ΔS = 1.5):**
```python
action = {
    "decision_points": 2,  # Linear flow
    "branches": 1,
    "abstractions": 0,  # Direct implementation
}
```

**ΔS Reduction:** 5.2 → 1.5 (71% reduction)

---

## Testing Entropy Tracking

### Unit Test Template

```python
from arifos_core.plugins.entropy_tracker import EntropyTracker

def test_entropy_calculation():
    tracker = EntropyTracker(sabar_threshold=5.0)

    # Test low entropy action
    result = tracker.calculate_entropy_delta(
        agent_name="test-agent",
        action_type="analyze",
        metadata={
            "inputs": {"file": "test.py"},
            "dependencies": [],
            "files_modified": [],
            "decision_points": 1,
        }
    )

    assert result.delta_s < 3.0
    assert result.risk_score < 0.3
    assert not result.threshold_exceeded


def test_sabar_trigger():
    tracker = EntropyTracker(sabar_threshold=5.0)

    # Test high entropy action
    result = tracker.calculate_entropy_delta(
        agent_name="test-agent",
        action_type="execute",
        metadata={
            "inputs": {"scope": "entire_project"},
            "dependencies": ["a", "b", "c", "d", "e"],  # 5 deps
            "files_modified": ["f1", "f2", "f3", "f4", "f5"],  # 5 files
            "decision_points": 10,
            "branches": 8,
        }
    )

    assert result.delta_s >= 5.0
    assert result.threshold_exceeded
    assert result.cooling_recommended
```

---

## See Also

- [PLUGIN_GOVERNANCE.md](./PLUGIN_GOVERNANCE.md) - Overall governance framework
- [FLOOR_ENFORCEMENT.md](./FLOOR_ENFORCEMENT.md) - F1-F9 implementation
- [AAA_FRAMEWORK.md](./AAA_FRAMEWORK.md) - Amanah-Authority-Accountability
- [../templates/governed-plugin/agent.md](../templates/governed-plugin/agent.md) - Agent template with entropy guidance

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
