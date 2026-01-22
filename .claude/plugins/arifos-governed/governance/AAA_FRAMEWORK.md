# AAA Framework for Plugins
## Amanah • Authority • Accountability

**Version:** 1.0.0
**Status:** AUTHORITATIVE
**Last Updated:** 2025-12-29

This document defines the AAA (Amanah-Authority-Accountability) framework for arifOS plugins.

---

## Overview

The AAA framework provides three governance pillars:

1. **Amanah (أمانة)** - Trust through Integrity
   - All operations must be reversible
   - No silent side effects
   - Fail-closed patterns
   - Transparent about actions

2. **Authority (سلطة)** - Clear Permission Boundaries
   - Explicit: What plugin CAN do automatically
   - Explicit: What REQUIRES approval
   - Explicit: What is FORBIDDEN
   - Fail-closed: Unlisted = forbidden

3. **Accountability (مسؤولية)** - Full Audit Trail
   - All actions logged to cooling ledger
   - Floor scores recorded
   - Verdicts preserved
   - Timestamped evidence chain

**Philosophy:** Trust is earned through transparency, boundaries, and evidence.

---

## 1. Amanah (Trust through Integrity)

### Core Principle

**"Reversible by Default"**

Every plugin operation must be:
- Reversible (can be undone)
- Transparent (user knows what will happen)
- Fail-closed (errors halt execution)
- Honest (no fabricated outputs)

### Implementation

#### Reversibility Requirements

**✅ COMPLIANT Operations:**
```python
# Read-only analysis
def analyze_code(file_path):
    content = read_file(file_path)  # Reversible (no mutation)
    findings = detect_patterns(content)
    return findings

# Propose changes (doesn't apply them)
def propose_refactoring(code):
    suggestions = generate_suggestions(code)
    return {"status": "SEAL", "suggestions": suggestions}

# Gated execution (requires approval)
def apply_changes(changes):
    if not user_approved:
        return {"status": "888_HOLD", "reason": "Awaiting human approval"}
    # ... apply changes with backup
```

**❌ VIOLATION Examples:**
```python
# Silent mutation
def fix_code(file_path):
    content = read_file(file_path)
    fixed = apply_fixes(content)
    write_file(file_path, fixed)  # ❌ Silent write, no approval
    return "Fixed!"

# Irreversible destruction
def clean_cache():
    os.system("rm -rf cache/*")  # ❌ No backup, no rollback
    return "Cleaned!"

# Hidden side effects
def analyze_performance(code):
    metrics = measure_performance(code)
    send_telemetry(metrics)  # ❌ Hidden external call
    return metrics
```

### Fail-Closed Patterns

**Error Handling:**
```python
# ✅ GOOD: Fail-closed (halt on error)
def process_files(files):
    for file in files:
        try:
            process(file)
        except Exception as e:
            # HALT immediately, surface error
            return {"status": "VOID", "reason": f"Failed on {file}: {e}"}

# ❌ BAD: Fail-open (continue on error)
def process_files(files):
    for file in files:
        try:
            process(file)
        except Exception:
            continue  # ❌ Silent failure, keeps going
```

### Transparency Requirements

**Before Execution:**
- State what will be modified
- List files affected
- Estimate risk level
- Request approval if needed

**During Execution:**
- Log each action
- Report progress
- Surface errors immediately

**After Execution:**
- Report what changed
- Provide rollback instructions
- Log to audit trail

### Amanah Checklist

For each plugin operation:

- [ ] **Reversible:** Can this be undone? Is there a rollback path?
- [ ] **Transparent:** Does user know what will happen?
- [ ] **Fail-Closed:** Do errors halt execution?
- [ ] **No Silent Effects:** Are all side effects surfaced?
- [ ] **Honest:** Are outputs factually accurate (F2 Truth)?

---

## 2. Authority (Permission Boundaries)

### Core Principle

**"Explicit Permissions Only"**

Plugins operate within three authority zones:

1. **Auto-Execute** - No approval needed
2. **Requires Approval** - Human must explicitly confirm
3. **Forbidden** - Never allowed

**Default:** Unlisted action = Forbidden (fail-closed)

### Authority Declaration (YAML Frontmatter)

```yaml
authority-boundaries:
  can-auto-execute:
    - Read files
    - Analyze code patterns
    - Generate reports
    - Calculate metrics
    - Propose changes (not apply)

  requires-approval:
    - Create new files
    - Modify existing files
    - Add dependencies
    - Execute external commands
    - Database operations
    - Production deployments

  forbidden:
    - Bypass governance
    - Disable floor checks
    - Modify constitutional specs
    - Silent errors
    - Irreversible operations without backup
```

### Auto-Execute Zone

**What plugins CAN do without asking:**

#### Read Operations
- Read any file in repository
- List directory contents
- Git status/log/diff
- Package manifest inspection

#### Analysis
- Code pattern detection
- Complexity calculation
- Security vulnerability scanning
- Performance profiling

#### Reporting
- Generate findings reports
- Create visualizations (as text)
- Export metrics (JSON, CSV)
- Document recommendations

#### Proposals
- Suggest refactorings
- Recommend optimizations
- Draft documentation
- Design architecture (proposals only, not implementation)

### Requires Approval Zone

**What plugins MUST ask before doing:**

#### File Modifications
- Create new files
- Edit existing files
- Delete files (even with backup)
- Rename/move files

#### Dependency Changes
- Add packages to `package.json`, `requirements.txt`, `Cargo.toml`, etc.
- Update dependency versions
- Remove dependencies

#### Execution
- Run external commands (beyond `allowed-tools`)
- Execute scripts
- Call external APIs
- Database queries/mutations

#### High-Stakes Operations
- Production deployments
- Database migrations
- Breaking API changes
- Security-critical modifications

**Approval Pattern:**
```python
def modify_file(file_path, new_content):
    # Calculate impact
    impact = calculate_impact(file_path, new_content)

    # Request approval
    approval = request_human_approval({
        "action": "modify_file",
        "file": file_path,
        "impact": impact,
        "diff": generate_diff(old_content, new_content)
    })

    if not approval.granted:
        return {"status": "888_HOLD", "reason": "User declined"}

    # Proceed with backup
    backup_file(file_path)
    write_file(file_path, new_content)
    return {"status": "SEAL", "backup": backup_path}
```

### Forbidden Zone

**What plugins CANNOT do (hard block):**

#### Governance Bypass
- ❌ Disable constitutional floor checks
- ❌ Skip entropy tracking
- ❌ Modify `spec/v44/*.json` without governance process
- ❌ Override verdicts programmatically

#### Destructive Operations
- ❌ Permanent deletion without backup
- ❌ Irreversible database operations
- ❌ Force push to git (overwrites history)
- ❌ Disable fail-closed patterns

#### Silent Behavior
- ❌ Silent errors (all must surface)
- ❌ Hidden telemetry
- ❌ Background tasks without notice
- ❌ Undocumented side effects

#### Consciousness Claims (F9 Anti-Hantu)
- ❌ "I feel", "I care", "I promise"
- ❌ Claim sentience or emotions
- ❌ Pretend to have preferences

### Authority Enforcement

**Unlisted Action Check:**
```python
def check_authority(action, boundaries):
    # Check if action is in auto-execute list
    if action in boundaries["can-auto-execute"]:
        return "auto_execute"

    # Check if action requires approval
    if action in boundaries["requires-approval"]:
        return "requires_approval"

    # Check if action is forbidden
    if action in boundaries["forbidden"]:
        return {"status": "VOID", "reason": "Forbidden action"}

    # DEFAULT: Unlisted = Forbidden (fail-closed)
    return {"status": "VOID", "reason": "Action not in authority list (fail-closed)"}
```

### Authority Checklist

For each plugin action:

- [ ] **Classified:** Is action in one of the three zones?
- [ ] **Auto-Execute Valid:** If auto-execute, is it truly safe?
- [ ] **Approval Flow:** If requires approval, is human consent obtained?
- [ ] **Not Forbidden:** Action isn't in forbidden list?
- [ ] **Fail-Closed:** If unlisted, treated as forbidden?

---

## 3. Accountability (Audit Trail)

### Core Principle

**"Everything is Logged"**

All plugin actions generate an immutable audit trail:
- What happened (action, description)
- When (timestamp)
- Who (agent name, session ID)
- Result (verdict, floor scores, ΔS)
- Why (reason, recommendations)

### Cooling Ledger Format

**File:** `cooling_ledger/plugin_actions.jsonl`

**Entry Format (JSON Lines):**
```json
{
  "session_id": "python-architect_1735497600.0",
  "agent_name": "python-architect-governed",
  "action_type": "propose",
  "description": "Design caching layer for API",
  "verdict": "SEAL",
  "verdict_reason": "All floors passed, entropy acceptable",
  "floors_passed": 9,
  "floors_failed": 0,
  "floor_results": [
    {"floor": "truth", "passed": true, "score": 0.99},
    {"floor": "delta_s", "passed": true, "score": 0.1},
    {"floor": "peace_squared", "passed": true, "score": 1.1},
    {"floor": "kappa_r", "passed": true, "score": 0.97},
    {"floor": "omega_0", "passed": true, "score": 0.04},
    {"floor": "amanah", "passed": true, "score": 1.0},
    {"floor": "rasa", "passed": true, "score": 1.0},
    {"floor": "tri_witness", "passed": true, "score": 0.96},
    {"floor": "anti_hantu", "passed": true, "score": 1.0}
  ],
  "delta_s": 2.1,
  "risk_score": 0.21,
  "sabar_triggered": false,
  "final_stage": "999_SEAL",
  "audit_trail": [
    {
      "stage": "000_VOID",
      "timestamp": "2025-12-29T12:00:00Z",
      "action": "Session initialized"
    },
    {
      "stage": "666_ALIGN",
      "timestamp": "2025-12-29T12:00:05Z",
      "action": "Floor validation complete",
      "floors_passed": 9
    },
    {
      "stage": "888_JUDGE",
      "timestamp": "2025-12-29T12:00:06Z",
      "verdict": "SEAL"
    }
  ],
  "timestamp": "2025-12-29T12:00:10Z"
}
```

### Audit Trail Requirements

#### Must Include

1. **Identity**
   - Session ID (unique per action)
   - Agent name
   - Action type (propose, analyze, execute, orchestrate)

2. **Intent**
   - Action description
   - Inputs (sanitized, no secrets)
   - Metadata (context)

3. **Evaluation**
   - Verdict (SEAL, PARTIAL, VOID, SABAR, 888_HOLD)
   - Floor scores (all 9 floors)
   - Entropy delta (ΔS)
   - Risk score

4. **Process**
   - Pipeline stages (000→999)
   - Timestamps for each stage
   - Stage-specific actions

5. **Outcome**
   - Final stage reached
   - Verdict reason
   - Recommendations (if any)

#### Must NOT Include

- ❌ Secrets (API keys, passwords, tokens)
- ❌ PII (user emails, names, unless essential)
- ❌ Large binary data
- ❌ Duplicate entries (one entry per action)

### Verification & Integrity

**Ledger Integrity Checks:**
```python
def verify_ledger_integrity(ledger_path):
    # Check each entry is valid JSON
    # Check required fields present
    # Check chronological order (timestamps increasing)
    # Check session IDs unique
    # Check verdicts match floor scores
```

**Merkle Tree (Optional):**
```python
# For cryptographic verification
def build_merkle_tree(entries):
    # Hash each entry
    # Build Merkle tree of hashes
    # Return root hash (immutable proof)
```

### Audit Query Examples

**Find all VOID verdicts:**
```bash
grep '"verdict":"VOID"' cooling_ledger/plugin_actions.jsonl
```

**Find high-risk actions (ΔS ≥ 4.0):**
```bash
jq 'select(.delta_s >= 4.0)' cooling_ledger/plugin_actions.jsonl
```

**Find all actions by specific agent:**
```bash
jq 'select(.agent_name == "python-architect-governed")' cooling_ledger/plugin_actions.jsonl
```

**Generate statistics:**
```python
import json

verdicts = {"SEAL": 0, "PARTIAL": 0, "VOID": 0, "SABAR": 0, "888_HOLD": 0}

with open("cooling_ledger/plugin_actions.jsonl") as f:
    for line in f:
        entry = json.loads(line)
        verdicts[entry["verdict"]] += 1

print(f"SEAL: {verdicts['SEAL']} | PARTIAL: {verdicts['PARTIAL']} | VOID: {verdicts['VOID']}")
```

### Accountability Checklist

For each plugin action:

- [ ] **Logged:** Entry written to cooling ledger?
- [ ] **Complete:** All required fields present?
- [ ] **Accurate:** Verdict matches floor scores?
- [ ] **Timestamped:** All stages have timestamps?
- [ ] **Immutable:** Ledger is append-only (no edits)?
- [ ] **Queryable:** Can retrieve by session ID, agent, verdict?

---

## AAA Integration Example

### Complete Governed Action

```python
from arifos_core.plugins.governance_engine import GovernanceEngine, AgentAction
from pathlib import Path

# Initialize governance engine
engine = GovernanceEngine(
    cooling_ledger_path=Path("cooling_ledger/plugin_actions.jsonl"),
    strict_mode=True,  # Fail-closed
    enable_entropy_tracking=True,
)

# Create action (respecting Authority boundaries)
action = AgentAction(
    agent_name="python-architect-governed",
    action_type="propose",  # Auto-execute zone (no file writes)
    description="Design caching layer for API endpoints",
    inputs={
        "domain": "backend",
        "requirements": {"latency": "< 100ms", "ttl": "5 minutes"}
    },
    metadata={
        "context": {"project": "web-app", "framework": "FastAPI"},
        "human_approval": False,  # Proposal doesn't need approval
    },
)

# Execute with full AAA framework
verdict = engine.execute_governed_action(action)

# AAA VERIFICATION:

# 1. AMANAH (Integrity)
# - Action is reversible (proposal only, no writes)
# - Transparent (description clear, inputs visible)
# - Fail-closed (engine halts on error)

# 2. AUTHORITY (Boundaries)
# - Action type "propose" is in can-auto-execute zone
# - No forbidden operations
# - If approval needed, metadata would have human_approval=True

# 3. ACCOUNTABILITY (Audit Trail)
# - Logged to cooling_ledger/plugin_actions.jsonl
# - Session ID: python-architect_1735497600.0
# - All 9 floors scores recorded
# - Verdict: SEAL/PARTIAL/VOID/SABAR/888_HOLD
# - Timestamp: 2025-12-29T12:00:10Z

# Handle verdict
if verdict.status == "SEAL":
    print("✅ AMANAH: Reversible, transparent, fail-closed")
    print(f"✅ AUTHORITY: Action approved (auto-execute zone)")
    print(f"✅ ACCOUNTABILITY: Logged to ledger (session: {verdict.metadata.get('session_id')})")
    # Proceed with proposal
    present_proposal(verdict.metadata.get("proposal"))

elif verdict.status == "888_HOLD":
    print("⚠️ AUTHORITY: Requires human approval")
    request_approval(verdict.reason, verdict.recommendations)

else:
    print(f"❌ VERDICT: {verdict.status}")
    print(f"Reason: {verdict.reason}")
    print("Check cooling ledger for details")
```

---

## Compliance Testing

### AAA Test Suite

```python
def test_amanah_reversibility():
    """Verify all operations are reversible"""
    action = AgentAction(
        agent_name="test-agent",
        action_type="execute",
        description="Delete cache files permanently",  # ❌ Irreversible
        inputs={},
    )

    verdict = engine.execute_governed_action(action)

    # Should fail F6 Amanah (irreversible)
    assert verdict.status == "VOID"
    assert any("Amanah" in f["floor"] for f in verdict.floor_failures)


def test_authority_boundaries():
    """Verify unlisted actions are forbidden"""
    action = AgentAction(
        agent_name="test-agent",
        action_type="deploy_to_prod",  # Not in authority list
        description="Deploy to production",
        inputs={},
    )

    # Should block (unlisted = forbidden)
    verdict = engine.execute_governed_action(action)
    assert verdict.status in ["VOID", "888_HOLD"]


def test_accountability_logging():
    """Verify all actions are logged"""
    action = AgentAction(
        agent_name="test-agent",
        action_type="analyze",
        description="Analyze code",
        inputs={},
    )

    verdict = engine.execute_governed_action(action)

    # Check ledger entry exists
    with open("cooling_ledger/plugin_actions.jsonl") as f:
        entries = [json.loads(line) for line in f]

    latest = entries[-1]
    assert latest["agent_name"] == "test-agent"
    assert latest["verdict"] in ["SEAL", "PARTIAL", "VOID", "SABAR", "888_HOLD"]
    assert "timestamp" in latest
```

---

## See Also

- [PLUGIN_GOVERNANCE.md](./PLUGIN_GOVERNANCE.md) - Overall governance framework
- [FLOOR_ENFORCEMENT.md](./FLOOR_ENFORCEMENT.md) - F1-F9 implementation
- [ENTROPY_TRACKING.md](./ENTROPY_TRACKING.md) - ΔS measurement
- [../templates/governed-plugin/agent.md](../templates/governed-plugin/agent.md) - Agent template with AAA

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
