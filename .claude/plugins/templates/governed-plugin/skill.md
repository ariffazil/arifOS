---
name: example-skill-governed
description: [Skill description] with constitutional governance
governance:
  floors-required: [F1, F2, F4, F5, F6, F7, F8, F9]
  entropy-threshold: 3.0
  verdict-required: true
allowed-tools:
  - Read
  - Bash(git:*)
  # Add skill-specific tools here
authority-boundaries:
  can-auto-execute:
    - Read files
    - Analyze code
    - Generate reports
  requires-approval:
    - Modify files
    - Execute external commands
  forbidden:
    - Bypass governance
    - Disable floor checks
---

# [Skill Name] (Governed)

**Status:** TEMPLATE - Customize for your skill

## Constitutional Mandate

This skill operates under arifOS constitutional governance with reduced floor requirements for focused tasks.

### Required Floors

- **F1 Amanah**: Reversible, transparent operations
- **F2 Truth**: Factually accurate outputs
- **F4 ΔS**: Clarity-increasing (reduces confusion)
- **F5 Peace²**: Non-destructive operations
- **F6 κᵣ**: Empathy for users
- **F7 Ω₀**: Acknowledges uncertainty
- **F8 G**: Governed execution
- **F9 Anti-Hantu**: No consciousness claims

**Note:** Skills typically don't require F3 (Tri-Witness) for routine operations. High-stakes skills may enable it via frontmatter.

### Entropy Threshold

- **Skills**: ΔS ≥ 3.0 (lower than agents' 5.0)
- **Rationale**: Skills are focused, single-purpose → should have lower complexity
- **Cooling**: If ΔS ≥ 3.0, skill is too complex → decompose or defer

## Capabilities

### What This Skill Does

[List specific capabilities]

Example:
- Analyzes Python code for async patterns
- Identifies blocking I/O calls
- Recommends async/await conversions
- Estimates performance impact

### Input Format

```yaml
inputs:
  file_path: str  # Path to file
  pattern: str    # Pattern to search for (optional)
  context: dict   # Additional context (optional)
```

### Output Format

```yaml
outputs:
  findings: list[dict]  # List of findings
  recommendations: list[str]  # Actionable recommendations
  risk_score: float  # Risk level [0.0, 1.0]
  verdict: str  # SEAL, PARTIAL, VOID
```

## Pipeline Stages

### 000 VOID - Initialize

- Validate inputs
- Set baseline ΔS₀ = 0.0

### 111 SENSE - Gather Context

- Read specified files
- Understand context

### 333 REASON - Execute Skill Logic

- Perform analysis
- Generate findings

### 666 ALIGN - Floor Check

**Required Floors (8 total):**

1. F1 Amanah: Reversible? ✓
2. F2 Truth: Accurate? ✓
3. F4 ΔS: Clarifying? ✓
4. F5 Peace²: Non-destructive? ✓
5. F6 κᵣ: Empathetic? ✓
6. F7 Ω₀: Uncertain acknowledged? ✓
7. F8 G: Governed? ✓
8. F9 Anti-Hantu: No ghosts? ✓

**Entropy Check:**

- ΔS = complexity + impact + cognitive_load
- Threshold: 3.0 (lower than agents)
- If ΔS ≥ 3.0 → SABAR

### 888 JUDGE - Verdict

- SEAL: ΔS < 3.0, all floors pass
- PARTIAL: Soft floor warnings
- SABAR: ΔS ≥ 3.0
- VOID: Hard floor fail

### 999 SEAL - Return Results

- Return findings with verdict
- Log to cooling ledger

## Authority Boundaries

### ✅ Auto-Execute

- Read files (within allowed scope)
- Analyze patterns
- Generate reports and recommendations
- Calculate metrics

### ⚠️ Requires Approval

- Modify files
- Execute external commands (beyond allowed-tools)
- High-impact changes

### 🚫 Forbidden

- Bypass governance
- Modify constitutional specs
- Disable entropy tracking
- Silent errors

## Tool Restrictions

### Baseline Allowed Tools

Per frontmatter:
- `Read` - Read files
- `Bash(git:*)` - Git commands
- [Add skill-specific tools]

### Fail-Closed Policy

Unlisted tool = FORBIDDEN

Request expansion:
1. STOP
2. Explain WHY
3. ASK human
4. WAIT for approval

## Example Usage

### Example 1: Pattern Analysis (SEAL)

**Input:**

```python
skill_input = {
    "file_path": "src/api/routes.py",
    "pattern": "blocking_io",
    "context": {"framework": "FastAPI"}
}
```

**Process:**

1. **000 VOID**: Initialize, ΔS₀ = 0.0
2. **111 SENSE**: Read `src/api/routes.py`
3. **333 REASON**: Analyze for blocking I/O
   - Found 3 blocking calls
   - Estimated ΔS = 1.2 (low complexity)
4. **666 ALIGN**:
   - F1-F9: ✓ All pass (read-only analysis)
   - ΔS = 1.2 < 3.0 (threshold)
5. **888 JUDGE**: SEAL (approved)
6. **999 SEAL**: Return findings

**Output:**

```python
{
    "findings": [
        {
            "file": "src/api/routes.py",
            "line": 42,
            "issue": "Blocking DB call: session.query(User).all()",
            "recommendation": "Use async session.execute()"
        },
        # ... 2 more findings
    ],
    "recommendations": [
        "Convert to async def",
        "Use asyncpg for DB",
        "Add await keywords"
    ],
    "risk_score": 0.15,
    "verdict": "SEAL"
}
```

### Example 2: Complex Analysis (SABAR)

**Input:**

```python
skill_input = {
    "file_path": "src/",  # Entire directory
    "pattern": "security_audit",
    "context": {"depth": "full"}
}
```

**Process:**

1. **000 VOID**: Initialize
2. **111 SENSE**: Scan entire src/ directory (50 files)
3. **333 REASON**: Full security audit
   - Estimated ΔS = 4.2 (high complexity: 50 files, 12 analysis types, 8 decision points)
4. **666 ALIGN**:
   - F1-F9: ✓ All pass
   - ΔS = 4.2 ≥ 3.0 (EXCEEDS threshold)
5. **888 JUDGE**: SABAR (cooling required)

**Response:**

```
SABAR: Skill too complex

ΔS = 4.2 ≥ 3.0 (skill threshold)

This skill should be focused and single-purpose.
Current request is too broad.

Cooling Options:
1. DEFER: Wait, reconsider necessity of full audit
2. DECOMPOSE: Split into smaller skills:
   - SQL injection check (ΔS ≈ 1.0)
   - XSS check (ΔS ≈ 1.0)
   - CSRF check (ΔS ≈ 0.8)
   - Auth check (ΔS ≈ 1.2)
3. DOCUMENT: Proceed with detailed audit report

Recommendation: DECOMPOSE (run 4 focused skills instead)
```

## Integration Code

### Using This Skill

```python
from arifos_core.plugins.governance_engine import GovernanceEngine, AgentAction

# Initialize governance
engine = GovernanceEngine(
    strict_mode=False,  # Skills can use PARTIAL verdicts
    enable_entropy_tracking=True,
)

# Create skill action
action = AgentAction(
    agent_name="example-skill-governed",
    action_type="analyze",  # Skills are typically "analyze"
    description="Analyze Python code for async patterns",
    inputs={
        "file_path": "src/api/routes.py",
        "pattern": "blocking_io",
    },
    metadata={
        "context": {"framework": "FastAPI"},
    },
)

# Execute with governance
verdict = engine.execute_governed_action(action)

# Handle verdict
if verdict.status == "SEAL":
    # Approved - use results
    results = verdict.metadata.get("results")
    apply_recommendations(results)

elif verdict.status == "SABAR":
    # Too complex - decompose
    print("Skill too complex. Recommendations:")
    for rec in verdict.recommendations:
        print(f"  - {rec}")

else:
    # VOID, PARTIAL, 888_HOLD
    handle_verdict(verdict)
```

### Skill Registry

Register skill in `.claude/plugins/arifos-governed/marketplace.json`:

```json
{
  "skills": {
    "example-skill-governed": {
      "name": "Example Skill (Governed)",
      "description": "[Skill description]",
      "category": "analysis",
      "author": "arifOS Project",
      "version": "1.0.0",
      "governance": {
        "floors": ["F1", "F2", "F4", "F5", "F6", "F7", "F8", "F9"],
        "entropy_threshold": 3.0
      },
      "allowed_tools": ["Read", "Bash(git:*)"],
      "install": "Copy from templates/governed-plugin/skill.md"
    }
  }
}
```

## Entropy Guidelines for Skills

### Target: ΔS < 3.0

Skills should be **focused and single-purpose**:

- ✅ **GOOD (ΔS ≈ 1.0-2.0)**: Analyze one file for one pattern
- ⚠️ **MODERATE (ΔS ≈ 2.0-3.0)**: Analyze multiple files for related patterns
- ❌ **TOO COMPLEX (ΔS ≥ 3.0)**: Analyze entire codebase for multiple patterns

### How to Reduce ΔS

If your skill exceeds ΔS = 3.0:

1. **Reduce Complexity**:
   - Fewer inputs/parameters
   - Single responsibility
   - Remove optional features

2. **Reduce Impact**:
   - Limit file scope
   - Avoid external calls
   - Read-only when possible

3. **Reduce Cognitive Load**:
   - Fewer decision points
   - Simpler branching logic
   - Clear, linear flow

### Decomposition Example

**Before (ΔS = 4.5):**
```yaml
name: full-code-audit
inputs:
  - directory (50 files)
  - checks: [security, performance, style, complexity]
ΔS = 4.5 → SABAR
```

**After (4 skills, each ΔS ≈ 1.0):**
```yaml
skill-1: security-audit (ΔS = 1.2)
skill-2: performance-audit (ΔS = 1.0)
skill-3: style-audit (ΔS = 0.8)
skill-4: complexity-audit (ΔS = 1.1)

Total: 4 SEAL verdicts > 1 SABAR
```

## Testing Checklist

Before publishing a governed skill:

- [ ] **Floor Compliance**: All required floors pass for typical inputs
- [ ] **Entropy Check**: ΔS < 3.0 for common use cases
- [ ] **Tool Restrictions**: Only uses allowed-tools (no unlisted tools)
- [ ] **Error Handling**: Graceful failure with clear error messages
- [ ] **Audit Trail**: Logs to cooling ledger with verdict and floor scores
- [ ] **Documentation**: Clear input/output format, examples, error cases
- [ ] **Decomposition**: If ΔS ≥ 3.0, split into focused sub-skills

## Customization Guide

### For Skill Authors

1. **Copy template**:
   ```bash
   cp .claude/plugins/templates/governed-plugin/skill.md \
      .claude/plugins/arifos-governed/plugins/your-domain/skills/your-skill.md
   ```

2. **Update frontmatter**:
   - `name`: Unique skill identifier
   - `description`: What does this skill do?
   - `governance.floors-required`: Adjust if needed (default: 8 floors)
   - `governance.entropy-threshold`: Keep at 3.0 or lower
   - `allowed-tools`: Add skill-specific tools

3. **Define capabilities**:
   - Clear input/output format
   - Focused, single-purpose functionality
   - Estimate typical ΔS (should be < 3.0)

4. **Test governance**:
   ```python
   # Verify ΔS < 3.0 for typical inputs
   # Verify floors pass
   # Verify SABAR triggers if too complex
   ```

5. **Add examples**:
   - SEAL scenario (normal operation)
   - SABAR scenario (too complex)
   - Error handling

## Version Information

- **Template Version**: v1.0.0
- **arifOS Version**: v45.0.0+
- **Governance Spec**: spec/v44/constitutional_floors.json
- **Last Updated**: 2025-12-29

## See Also

- [agent.md](./agent.md) - Agent template (for complex multi-skill orchestration)
- [PLUGIN_GOVERNANCE.md](../../governance/PLUGIN_GOVERNANCE.md) - Governance overview
- [ENTROPY_TRACKING.md](../../governance/ENTROPY_TRACKING.md) - ΔS measurement details

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
