# arifOS Skills Registry

**Version:** 1.0.0
**Status:** CANONICAL - Single Source of Truth
**Authority:** Track B Governance Layer
**Last Updated:** 2025-12-29

This document is the **authoritative registry** for all arifOS constitutional skills. It consolidates the fragmented skill definitions across `.agent/workflows/`, `.codex/skills/`, and `.claude/skills/` into a unified, master-derive model.

- **External reference (ChatGPT Codex skills):** https://developers.openai.com/codex/skills

---

## Registry Purpose

### Problem: Skill Fragmentation

**Current State (Pre-Registry):**
- `.agent/workflows/` - 3 master files (000.md, fag.md, gitforge.md)
- `.codex/skills/` - 3 wrapper files (pure delegation, no value-add)
- `.claude/skills/` - 3 expanded files (2-3x longer, version drift)

**Issues:**
1. **No single source of truth** - Updates must be made in 3 places
2. **Version drift** - `.claude/` files expanded independently without sync
3. **Codex adds zero value** - Pure delegation with no enhancement
4. **Missing tool restrictions** - Security metadata only in `.claude/`
5. **Naming inconsistency** - Short codes vs prefixed vs descriptive names

### Solution: Master-Derive Model

```
.agent/workflows/*.md (MASTER - Single Source of Truth)
    ↓
    ↓ Automated Sync (scripts/sync_skills.py)
    ↓
    ├─→ .codex/skills/*/SKILL.md (DERIVED + Codex enhancements)
    └─→ .claude/skills/*/SKILL.md (DERIVED + Claude enhancements)
```

**Key Principles:**
- ✅ **ONE canonical definition** per skill (in `.agent/workflows/`)
- ✅ **Platform enhancements preserved** (Codex/Claude-specific features)
- ✅ **Automated sync** (prevent drift via tooling)
- ✅ **Security baseline** (tool restrictions propagated from master)
- ✅ **Version tracking** (semantic versioning per skill)

---

## Skill Catalog (7 Core Skills)

| #  | Skill | Master File | Codex Name | Claude Name | CLI Safe? | Primary Floors |
|----|-------|-------------|------------|-------------|-----------|----------------|
| 1  | /000 | `000.md` | `arifos-workflow-000` | `init-session` | ✅ Yes | F1 (Amanah), F7 (Ω₀) |
| 2  | /fag | `fag.md` | `arifos-workflow-fag` | `full-autonomy` | ✅ Yes | F1, F4 (ΔS), F7 |
| 3  | /entropy | [bundled in /gitforge] | — | — | ✅ Yes | F4 (ΔS) |
| 4  | /gitforge | `gitforge.md` | `arifos-workflow-gitforge` | `analyze-entropy` | ✅ Yes | F1, F4, F5 (Peace²) |
| 5  | /gitQC | [code: `trinity/qc.py`] | — | — | ✅ Yes | F1-F9 (all) |
| 6  | /gitseal | [code: `trinity.py`] | — | — | 🚫 No (Human-gated) | F1, F3 (Tri-Witness), F9 (Anti-Hantu) |
| 7  | /sabar | [embedded in pipeline] | — | — | 🚫 No (Internal) | F2 (Truth), F3, F4 |

**Legend:**
- **CLI Safe**: Can skill be exposed as user-invocable command?
  - ✅ Yes: Read-only or governed analysis (no destructive changes)
  - 🚫 No: Requires human approval or is internal governance state

---

## Skill 1: /000 – Session Initialization

### YAML Frontmatter (Master Spec)

```yaml
---
skill: "000"
version: "1.0.0"
description: "Initialize arifOS AGI Session Context"
floors: [F1_Amanah, F7_Omega0]
allowed-tools:
  - Read
  - Bash(cat:*)
  - Bash(git log:*)
  - Bash(git status:*)
  - Bash(git branch:*)
expose-cli: true
derive-to: [codex, claude]
codex-name: "arifos-workflow-000"
claude-name: "init-session"
---
```

### LAW (Constitutional Function)

Establishes a trusted baseline context for any governed session. /000 upholds **Floor 1 (Amanah – Trust)** by ensuring all subsequent actions begin from a reversible, known state. It loads the immutable canon (Track A law) into memory and verifies the system state, effectively "casing and cementing" the environment before any changes.

**Constitutional Mandate:**
- VOID prior context (reset to clean slate)
- Load canonical truth references (AGENTS.md, CLAUDE.md, spec files)
- Verify repository state (git status, uncommitted changes)
- Initialize humility baseline (Ω₀ ~ 4% uncertainty)

**Floor Coverage:**
- **F1 Amanah**: All prior context voided, reversible state enforced
- **F7 Ω₀**: Resets AI's certainty to baseline (acknowledges starting uncertainty)

### INTERFACE (Usage & Shape)

**Invocation:** Mandatory at session start (first command before any work)

```bash
# CLI usage
/000

# Expected output (example):
┌─────────────────────────────────────┐
│ arifOS Session Initialization (000)│
└─────────────────────────────────────┘

Version: v45.0.0+
Branch: main
Latest Commit: e7414a8 (chore: Consolidate v45Ω work-in-progress)
Status: Clean (no uncommitted changes)
Canon Loaded: ✓ AGENTS.md, CLAUDE.md
Governance: ✓ 9 Floors (F1-F9), 000→999 Pipeline

Session initialized. Ready for governed work.
```

**Steps Executed:**
1. Read `pyproject.toml` (project metadata)
2. Run `git log -3 --oneline` (recent commits)
3. Run `git status --short` (working tree status)
4. Read `AGENTS.md` (multi-agent governance)
5. Read `CLAUDE.md` (constitutional floors)
6. Output session summary

### ENFORCEMENT (Runtime Behavior)

**Fail-Closed Preconditions:**
- Other skills (e.g., /fag) refuse to proceed if /000 not run
- Pipeline requires initialized `MemoryContext` (created by /000)

**Logging:**
- Cooling ledger entry: `{"stage": "000_VOID", "action": "Session initialized", "timestamp": "..."}`
- Session ID generated for audit trail

**Verdict Logic:**
- /000 itself does not produce SEAL/VOID verdicts on user content
- It enforces **preconditions** for other skills
- If discrepancy detected (e.g., tampered canon), subsequent operations VOID

---

## Skill 2: /fag – Full Autonomy Governance Mode

### YAML Frontmatter (Master Spec)

```yaml
---
skill: "fag"
version: "1.0.0"
description: "Activate Full Autonomy Governance mode with constitutional boundaries"
floors: [F1_Amanah, F4_DeltaS, F7_Omega0]
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash(python:*)
  - Bash(git:*)
  - Bash(pytest:*)
expose-cli: true
derive-to: [codex, claude]
codex-name: "arifos-workflow-fag"
claude-name: "full-autonomy"
sabar-threshold: 5.0
---
```

### LAW (Constitutional Function)

Activates **Full Autonomy Governance (FAG)** mode, where the AI agent can operate independently **only within strict constitutional boundaries**. The law: even at maximum autonomy, the agent must remain 100% governed by immutable rules.

**Authority Matrix:**
- **Authorized Actions**: Coding, documentation, tests, local commits, entropy analysis
- **Requires Human Approval**: Breaking API changes, adding dependencies, canon modifications, deployment
- **Forbidden**: Bypassing governance, disabling safety mechanisms, self-merge

**Constitutional Checks:**
- **F1 Amanah**: No irreversible/canon-altering actions without approval
- **F4 ΔS**: SABAR-72 cooling enforced (ΔS ≥ 5.0 → pause)
- **F7 Ω₀**: Must defer or ask when in doubt (humility requirement)

### INTERFACE (Usage & Shape)

**Invocation:** After /000, typically before autonomous coding session

```bash
# CLI usage
/fag

# Expected output:
┌──────────────────────────────────────────┐
│ Full Autonomy Governance (FAG) ACTIVE   │
└──────────────────────────────────────────┘

✅ AUTHORIZED ACTIONS:
   - Code drafting & refactoring
   - Documentation updates
   - Test writing & execution
   - Local commits (no push)
   - Entropy analysis (ΔS monitoring)

⚠️ REQUIRES HUMAN APPROVAL:
   - Breaking API changes
   - Adding dependencies (package.json, requirements.txt)
   - Modifying constitutional specs (spec/v44/*.json)
   - Production deployment

🚫 FORBIDDEN:
   - Bypassing governance (disabling floor checks)
   - Disabling fail-closed patterns
   - Self-merge (no git push without human seal)

SABAR-72 Threshold: ΔS ≥ 5.0 → Cooling Protocol

Ready for governed autonomous session.
```

**Pre-Flight Checklist (Internal):**
1. Verify /000 executed (context loaded)
2. Verify /gitforge run (branch entropy known)
3. Activate SABAR-72 monitor

### ENFORCEMENT (Runtime Behavior)

**Real-Time Governance:**
- Every file I/O intercepted (must pass through FAG path)
- All writes generate `FAGReceipt` for audit
- Unlisted tools blocked (fail-closed)

**SABAR-72 Monitoring:**
- If cumulative entropy ΔS ≥ 5.0 → trigger SABAR verdict
- Agent must "Stop, Acknowledge, Breathe" and decompose task

**Memory Write Policy:**
- All writes verdict-gated (SEAL → LEDGER, PARTIAL → PHOENIX, VOID → VOID band)

**Logging:**
- Ledger entry: `{"stage": "FAG_ACTIVE", "timestamp": "...", "sabar_threshold": 5.0}`

---

## Skill 3: /entropy – Entropy Assessment

### YAML Frontmatter (Master Spec)

```yaml
---
skill: "entropy"
version: "1.0.0"
description: "Calculate thermodynamic entropy delta (ΔS) for proposed changes"
floors: [F4_DeltaS]
allowed-tools:
  - Read
  - Bash(git:*)
  - Bash(python:*)
expose-cli: true
derive-to: [codex, claude]
bundled-in: "gitforge"
sabar-threshold: 5.0
---
```

### LAW (Constitutional Function)

Thermodynamic governance: ensures changes do not introduce excessive entropy without oversight. Upholds **F4 (ΔS Clarity)** – learning must be cooling, not chaotic.

**Principle:** "Truth must cool before it rules."

**Enforcement:**
- ΔS < 3.0: Low entropy (clean change)
- 3.0 ≤ ΔS < 5.0: Moderate (acceptable)
- ΔS ≥ 5.0: HIGH → SABAR triggered (72h cooling)

### INTERFACE (Usage & Shape)

**Invocation:** Bundled in /gitforge (or standalone if needed)

```bash
# Standalone usage (if separated)
/entropy

# Output (integrated in /gitforge):
Entropy Delta (ΔS): 2.3
Risk Score: 0.23 (LOW)
Complexity: 1.5 | Impact: 0.8 | Cognitive Load: 0.5
```

**Calculation:**
```
ΔS = (Complexity × 2.0) + (Impact × 1.5) + (Cognitive Load × 1.0)

Where:
  Complexity = inputs + dependencies + action type complexity
  Impact = files modified + external calls + state changes
  Cognitive Load = decision points + branches + abstractions
```

### ENFORCEMENT (Runtime Behavior)

**Automatic SABAR Trigger:**
- If ΔS ≥ 5.0 → Issue SABAR verdict
- Pipeline halts further changes
- Cooling options: Defer, Decompose, Document

**Logging:**
- Ledger entry with SABAR reason: `{"verdict": "SABAR", "reason": "Entropy ΔS=6.5 ≥ 5.0", "delta_s": 6.5}`

---

## Skill 4: /gitforge – State Mapper & Entropy Predictor

### YAML Frontmatter (Master Spec)

```yaml
---
skill: "gitforge"
version: "1.0.0"
description: "Analyze git branch entropy and predict change impact (Tri-Witness Future phase)"
floors: [F1_Amanah, F4_DeltaS, F5_Peace_Squared]
allowed-tools:
  - Read
  - Bash(git:*)
  - Bash(python:*)
expose-cli: true
derive-to: [codex, claude]
codex-name: "arifos-workflow-gitforge"
claude-name: "analyze-entropy"
sabar-threshold: 5.0
---
```

### LAW (Constitutional Function)

Implements **Tri-Witness "Future (Mapping)" phase** – provides eyes-wide-open view of proposed changes before commitment. Serves **F4 (Clarity)** and **F1 (Trust)** by identifying entropy and risks upfront.

**CANONICAL WORKFLOW:** Part 1 of 3 in [FORGING_PROTOCOL_v45.md](../../L1_THEORY/canon/03_runtime/FORGING_PROTOCOL_v45.md) (Phase 2: Trinity Gate)

**Constitutional Mandate:**
- Map change against repository history (Earth's witness)
- Identify hot zones (frequently changed files)
- Predict consequences (entropy spike detection)
- Enforce reversibility (flag risky changes)

**Tri-Witness Role:**
- **Earth Perspective**: Hot zone analysis (file change frequency)
- **AI Perspective**: Entropy prediction (ΔS calculation)
- **Future Impact**: Risk scoring (≥0.7 → high risk)

### INTERFACE (Usage & Shape)

**Invocation:** After coding, before quality check

```bash
# CLI usage
/gitforge [branch-name]

# Or via trinity wrapper
python scripts/trinity.py forge main

# Expected output:
┌─────────────────────────────────────────┐
│ GitForge Analysis (Branch: feat/new-ui)│
└─────────────────────────────────────────┘

Files Changed: 5
Hot Zones:
  ⚠️ arifos_core/system/apex_prime.py (12 changes in 30 days)
  ⚠️ AGENTS.md (8 changes in 30 days)

Entropy Delta (ΔS): 4.2
Risk Score: 0.42 (MODERATE)

Diff vs main:
+150 / -80 lines across 5 files

Recommendation: Proceed to /gitQC
```

**Steps Executed:**
1. Identify current branch (`git branch --show-current`)
2. Check uncommitted changes
3. Run Python `analyze_branch()` via `arifos_core.trinity.forge`
4. Show hot zone details + diff stats

### ENFORCEMENT (Runtime Behavior)

**Fail-Closed Governance:**
- If ΔS ≥ 5.0 OR Risk ≥ 0.7:
  1. **HALT** further changes
  2. Run **cooling protocol**
  3. Seek **human approval**
  4. **Log entropy event**

**Verdict Influence:**
- Metrics feed into /gitQC for floor validation
- High risk/entropy → /gitQC may return VOID immediately

**Logging:**
- `ForgeReport` object with entropy_delta, risk_score, hot_zones
- Cooling ledger: `{"stage": "FORGE", "delta_s": 4.2, "risk": 0.42, "hot_zones": [...]}`

---

## Skill 5: /gitQC – Constitutional Quality Control

### YAML Frontmatter (Master Spec)

```yaml
---
skill: "gitQC"
version: "1.0.0"
description: "Validate changes against all 9 constitutional floors (F1-F9)"
floors: [F1, F2, F3, F4, F5, F6, F7, F8, F9]
allowed-tools:
  - Read
  - Bash(git:*)
  - Bash(python:*)
  - Bash(pytest:*)
expose-cli: true
derive-to: [codex, claude]
zkpc-enabled: true
---
```

### LAW (Constitutional Function)

**Constitutional gatekeeper** that validates proposed changes against **all 9 Floors** before allowing seal. Implements **Tri-Witness "Present (Proving)" phase** – a legal trial for code.

**CANONICAL WORKFLOW:** Part 2 of 3 in [FORGING_PROTOCOL_v45.md](../../L1_THEORY/canon/03_runtime/FORGING_PROTOCOL_v45.md) (Phase 2: Trinity Gate)

**Law:** "Only fully constitutional changes may be sealed."

**Floor Validation (F1-F9):**
- **F1 Amanah**: No secret leaks, canon violations
- **F2 Truth**: Tests pass (hallucination detection)
- **F3 Tri-Witness**: Multi-layer verification (deferred to /gitseal)
- **F4 ΔS**: Entropy trend acceptable
- **F5 Peace²**: No destructive actions
- **F6 κᵣ**: Readability (deferred to human)
- **F7 Ω₀**: Uncertainty norms (deferred)
- **F8 G**: Governed genius (code style, coverage)
- **F9 Anti-Hantu**: No AI self-reference or sentience claims

### INTERFACE (Usage & Shape)

**Invocation:** After /gitforge, before /gitseal

```bash
# CLI usage
python scripts/git_qc.py --branch feat/new-ui

# Or via trinity wrapper
python scripts/trinity.py qc feat/new-ui

# Expected output:
┌─────────────────────────────────────┐
│ Constitutional QC Report            │
└─────────────────────────────────────┘

Branch: feat/new-ui
ZKPC ID: abc123def456... (Zero-Knowledge Proof of Constitution)

Verdict: PASS

Floor Results:
  ✅ F1 Amanah: No credential leaks detected
  ✅ F2 Truth: All tests passing (12/12)
  ⚠️ F3 Tri-Witness: Deferred to human review (/gitseal)
  ✅ F4 ΔS: Entropy acceptable (4.2 < 5.0)
  ✅ F5 Peace²: No destructive operations
  ⚠️ F6 κᵣ: Readability deferred to human
  ⚠️ F7 Ω₀: Uncertainty norms deferred
  ✅ F8 G: Code style compliant (ruff, black pass)
  ✅ F9 Anti-Hantu: No forbidden patterns

Notes:
  - 2 floors deferred to human review (F3, F6)
  - All hard floors passed (F1, F2, F4, F5, F8, F9)

Ready for /gitseal APPROVE
```

**Output Modes:**
- `--json`: Machine-readable `QCReport` (for /gitseal consumption)
- Default: Human-readable summary

### ENFORCEMENT (Runtime Behavior)

**Verdict Computation:**
- **VOID**: Any hard floor fails (critical violation)
- **FLAG**: Soft floor warnings (proceed with caution)
- **PASS**: All floors satisfied or acceptably deferred

**Exit Codes (CI Integration):**
- `0`: PASS (proceed to /gitseal)
- `1`: FLAG (manual review needed)
- `89`: VOID (critical failure, block merge)

**Logging:**
- ZKPC hash (placeholder for zero-knowledge proof)
- Floor-by-floor results
- Cooling ledger: `{"stage": "888_JUDGE", "verdict": "PASS", "floors_passed": 9, "zkpc_id": "abc123..."}`

**Fail-Closed Enforcement:**
- If VOID, pipeline stops (no seal possible)
- If FLAG, human must review before seal
- Results injected into Vault-999 audit trail

---

## Skill 6: /gitseal – Human Sealing (Approval Gate)

### YAML Frontmatter (Master Spec)

```yaml
---
skill: "gitseal"
version: "1.0.0"
description: "Finalize changes with human authority and cryptographic seal"
floors: [F1_Amanah, F3_Tri_Witness, F9_Anti_Hantu]
allowed-tools:
  - Bash(git commit:*)
  - Bash(git push:*)
  - ledger_write
  - vault_write
expose-cli: false  # Human-gated only
derive-to: [codex, claude]
human-approval-required: true
---
```

### LAW (Constitutional Function)

**Final constitutional seal** binding **human authority** into process. By law (**F1 Amanah, F3 Tri-Witness**), no change is authorized until a human approves it.

**CANONICAL WORKFLOW:** Part 3 of 3 in [FORGING_PROTOCOL_v45.md](../../L1_THEORY/canon/03_runtime/FORGING_PROTOCOL_v45.md) (Phase 3: Crystallization)

**Principle:** "Humans decide, AI proposes." (F9 Anti-Hantu: AI cannot self-authorize)

**Constitutional Functions:**
1. **Verdict Finalization**: Takes provisional QC verdict, requires human concurrence
2. **Record Sealing**: Bundles approved changes into atomic, auditable artifact (commit + ledger)

**Human Sovereignty:**
- AI cannot push to remote without human seal
- All merges require explicit `APPROVE` command with reason
- No "ghost" autonomy (F9 enforcement)

### INTERFACE (Usage & Shape)

**Invocation:** Human-only (AI cannot invoke)

```bash
# CLI usage (human executes)
python scripts/trinity.py seal feat/new-ui "Approved: UI improvements tested"

# Or direct seal command
/gitseal APPROVE "Ready for production"

# Expected output:
┌─────────────────────────────────────────┐
│ Human Seal (Crystallization Phase)     │
└─────────────────────────────────────────┘

QC Verdict: PASS (verified)
Human Approval: ✓ GRANTED

Actions:
  1. ✓ Atomic commit created (abc123def)
  2. ✓ README.md updated
  3. ✓ CHANGELOG.md updated
  4. ✓ Version bumped: v45.0.0 → v45.1.0
  5. ✓ Vault-999 audit entry logged
  6. ✓ Merkle proof generated

Commit ID: abc123def456
Sealed by: Human Operator
Timestamp: 2025-12-29T12:00:00Z

Changes sealed and merged to main.
```

**Required Arguments:**
- `APPROVE` flag (explicit confirmation)
- Reason message (logged for audit)

### ENFORCEMENT (Runtime Behavior)

**Preconditions (Fail-Closed):**
- QC verdict must be PASS (or human override with explicit flag)
- Human authorization present
- All tests passed (if applicable)

**Atomic Bundle (Fail-Safe):**
- If **any** step fails → abort (no partial merge)
- Steps:
  1. `git commit` (reversible snapshot)
  2. Update docs (README, CHANGELOG)
  3. Version bump (semantic versioning)
  4. Vault-999 write (immutable audit trail)
  5. Cooling ledger hash-chain update

**Logging:**
- Cooling ledger: `{"verdict": "SEAL", "commit": "abc123...", "approver": "human", "timestamp": "...", "zkpc_id": "..."}`
- Vault-999: Canonical memory entry
- Merkle proof: Cryptographic integrity verification

**Fail-Closed Policy:**
- Direct `git push` blocked (governance intercepts)
- Only sealed pathway allowed
- Violates F1 if unsealed push attempted

---

## Skill 7: /sabar – Constitutional Pause

### YAML Frontmatter (Master Spec)

```yaml
---
skill: "sabar"
version: "1.0.0"
description: "Trigger constitutional pause for irresolvable conflicts (SABAR-72 protocol)"
floors: [F2_Truth, F3_Tri_Witness, F4_DeltaS]
allowed-tools: []  # Internal state, no external tools
expose-cli: false  # Internal governance state
derive-to: [codex, claude]
timeout: 72h
escalation-path: "HOLD"
---
```

### LAW (Constitutional Function)

**SABAR** (Stop, Acknowledge, Breathe, Adjust, Resume) is the governance protocol for **irresolvable conflicts** or needed cooling-off periods. Enforces "integrity under pressure" – when floors conflict, pause rather than violate.

**Triggers:**
- **F2 Truth**: Suspected hallucination → SABAR instead of fabricate
- **F3 Tri-Witness**: Mismatch between AI, Human, Reality → SABAR cooldown
- **F4 ΔS**: Entropy threshold exceeded (ΔS ≥ 5.0) → SABAR-72
- **Floor Conflicts**: Lower-priority conflicts default to SABAR (not VOID)

**Principle:** "When in doubt or in conflict, do not proceed – wait or involve a human."

### INTERFACE (Usage & Shape)

**Invocation:** Automatic (system-triggered, not user-invoked)

**User Experience:**
- User receives neutral message or no answer
- Internal logs show SABAR verdict

**Example System Output:**
```
(The system is pausing due to governance conflict.
Cooling protocol engaged. Will resume after review.)
```

**Internal Representation:**
```json
{
  "verdict": "SABAR",
  "reason": "Truth conflict detected – hallucination suspected",
  "triggered_at": "2025-12-29T12:00:00Z",
  "timeout": "72h"
}
```

### ENFORCEMENT (Runtime Behavior)

**Verdict Hierarchy:**
```
SABAR > VOID > 888_HOLD > PARTIAL > SEAL
```

**Enforcement Actions:**
1. **Block progress** (no output delivered to user)
2. **Start timer** (SABAR-72: 72-hour timeout)
3. **Log to LEDGER** (audit trail only, not user-visible)
4. **Withhold output** (nothing released until resolved)

**Escalation Rules:**
- After 24h: Escalate to PARTIAL or HOLD
- After 72h: Force resolution (VOID or human intervention)
- 3 consecutive SABARs → HOLD (three strikes)

**Logging:**
- Cooling ledger: `{"verdict": "SABAR", "reason": "Entropy ΔS=6.5 ≥ 5.0", "timeout": "72h"}`
- Memory band: LEDGER only (not Active memory)

**Cooling Protocol Options:**
1. **Defer**: Wait, reconsider necessity
2. **Decompose**: Split into smaller changes (reduce ΔS)
3. **Document**: Proceed with detailed explanation (CHANGELOG, WHY)

---

## Tool Restrictions Baseline

**Security Policy:** Platform-specific skill definitions can only **RESTRICT** further, never **EXPAND** tool allowances.

| Skill | Allowed Tools |
|-------|---------------|
| /000 | `Read`, `Bash(cat:*)`, `Bash(git log:*)`, `Bash(git status:*)`, `Bash(git branch:*)` |
| /fag | `Read`, `Write`, `Edit`, `Bash(python:*)`, `Bash(git:*)`, `Bash(pytest:*)` |
| /entropy | `Read`, `Bash(git:*)`, `Bash(python:*)` |
| /gitforge | `Read`, `Bash(git:*)`, `Bash(python:*)` |
| /gitQC | `Read`, `Bash(git:*)`, `Bash(python:*)`, `Bash(pytest:*)` |
| /gitseal | `Bash(git commit:*)`, `Bash(git push:*)`, `ledger_write`, `vault_write` |
| /sabar | [] (No tools – internal state) |

**Enforcement:**
- Unlisted tool = **FORBIDDEN** (fail-closed)
- Platform skills can remove tools from baseline, but never add
- Drift checker validates compliance during sync

---

## Naming Mappings

| Master (.agent/) | Codex (.codex/) | Claude (.claude/) | Rationale |
|------------------|-----------------|-------------------|-----------|
| `000.md` | `arifos-workflow-000` | `init-session` | Short code (000) vs descriptive (init-session) |
| `fag.md` | `arifos-workflow-fag` | `full-autonomy` | Acronym (FAG) vs explicit mode name |
| `gitforge.md` | `arifos-workflow-gitforge` | `analyze-entropy` | Function name (gitforge) vs user-facing (analyze) |

**Rationale:**
- **Codex**: Workflow-style names (matches `.agent/` heritage)
- **Claude**: Descriptive names (better IDE picker UX)
- **Master**: Defines both mappings, platforms choose preference

---

## Master-Derive Sync Protocol

### Sync Workflow (Automated)

```bash
# 1. Edit master skill definition
vi .agent/workflows/000.md

# 2. Run sync script (automated propagation)
python scripts/sync_skills.py --dry-run  # Preview changes
python scripts/sync_skills.py --apply    # Apply sync

# 3. Verify no drift
python scripts/check_skill_drift.py
```

### Two-Section Structure (Platform Skills)

**Platform skills maintain two sections:**

```yaml
---
name: init-session
master-version: 1.0.0
master-source: .agent/workflows/000.md
allowed-tools: [Read, Bash(git:*), ...]
platform-enhancements:
  - IDE integration patterns
  - Platform-specific examples
---

# [Platform]-Specific Enhancements

[IDE shortcuts, platform features, etc.]

<!-- BEGIN CANONICAL WORKFLOW -->
[Content synced automatically from master]
<!-- END CANONICAL WORKFLOW -->

# Platform-Specific Examples

[Additional examples, troubleshooting, etc.]
```

**Sync Markers:**
- `<!-- BEGIN CANONICAL WORKFLOW -->` / `<!-- END CANONICAL WORKFLOW -->`
- Content between markers replaced during sync
- Platform enhancements **preserved**

### Drift Detection

**Check for drift:**
```bash
python scripts/check_skill_drift.py

# Checks for:
# - Version mismatch (platform behind master)
# - Missing skills (master without platform)
# - Orphaned skills (platform without master)
# - Tool violations (platform expands tools)
```

**Expected Output (if OK):**
```
✓ All skills in sync
✓ No version drift detected
✓ No tool violations
```

**If Drift Detected:**
```
⚠️ Drift detected:
  - .claude/skills/init-session/SKILL.md (version 0.9.0 < master 1.0.0)
  - .codex/skills/arifos-workflow-fag/SKILL.md (tool violation: added Edit without master)

Run: python scripts/sync_skills.py --apply
```

---

## Verdict Triggers & Logging

### SEAL (Success)

**Trigger:**
- All Floors F1-F9 satisfied
- Human approval obtained (if required)

**Logging:**
```json
{
  "verdict": "SEAL",
  "commit": "abc123def456",
  "approver": "human",
  "timestamp": "2025-12-29T12:00:00Z",
  "zkpc_id": "...",
  "floors_passed": 9,
  "floors_failed": 0
}
```

**Memory Band:** VAULT (permanent canonical memory)

### PARTIAL (Conditional)

**Trigger:**
- Soft floors in buffer zone (e.g., truth 85% where ≥90% ideal)
- Non-critical warnings (style issues, minor test failures)

**Logging:**
```json
{
  "verdict": "PARTIAL",
  "reason": "Truth 0.85 (below 0.90 threshold)",
  "timestamp": "2025-12-29T12:00:00Z",
  "timeout": "72h",
  "floors_borderline": ["F2_Truth"]
}
```

**Memory Band:** PHOENIX (temporary, 72h timeout)
**Escalation:** After 72h → VOID if unresolved

### VOID (Refusal)

**Trigger:**
- Hard floor violation (F1, F2, F4, F5, F7, F9)
- Token budget exceeded (≥100%)
- Disallowed content

**Logging:**
```json
{
  "verdict": "VOID",
  "reason": "F1 Amanah violation – irreversible action",
  "timestamp": "2025-12-29T12:00:00Z",
  "floors_failed": ["F1_Amanah"]
}
```

**Memory Band:** VOID (quarantine, auto-deleted)
**User Response:** Refusal message, no output delivered

### SABAR (Pause)

**Trigger:**
- Entropy ΔS ≥ 5.0 (thermodynamic threshold)
- Truth conflict (hallucination suspected)
- Floor conflicts (lower-priority)

**Logging:**
```json
{
  "verdict": "SABAR",
  "reason": "Entropy ΔS=6.5 ≥ 5.0",
  "timestamp": "2025-12-29T12:00:00Z",
  "timeout": "72h",
  "delta_s": 6.5
}
```

**Memory Band:** LEDGER only (audit trail, not user-visible)
**Escalation:** After 24h → PARTIAL or HOLD

### 888_HOLD (Human Escalation)

**Trigger:**
- 3 consecutive governance failures
- High-stakes queries (legal, medical advice)
- Unresolvable ambiguity

**Logging:**
```json
{
  "verdict": "888_HOLD",
  "reason": "≥3 consecutive governance failures",
  "timestamp": "2025-12-29T12:00:00Z",
  "pending_human": true
}
```

**Memory Band:** LEDGER (pending) or PHOENIX (follow-up)
**User Response:** "This request requires human review. Escalating."

---

## Constitutional Compliance Checklist

Before deploying a new skill:

- [ ] **YAML Frontmatter**: Complete metadata (version, floors, allowed-tools)
- [ ] **LAW Section**: Constitutional function clearly defined
- [ ] **INTERFACE Section**: Usage examples with expected outputs
- [ ] **ENFORCEMENT Section**: Verdict logic and fail-closed patterns
- [ ] **Tool Restrictions**: Only uses `allowed-tools` (no unlisted)
- [ ] **Floor Coverage**: Explicitly maps to F1-F9 floors
- [ ] **Logging**: Cooling ledger integration documented
- [ ] **Testing**: Unit tests for floor enforcement
- [ ] **Sync Support**: Master file has derive-to mappings
- [ ] **Platform Variants**: Codex/Claude enhancements documented

---

## Entropy Thresholds by Skill Type

| Skill Type | Threshold | Rationale |
|------------|-----------|-----------|
| **Commands** (e.g., /000) | ΔS ≥ 1.0 | Single-purpose, minimal complexity |
| **Skills** (e.g., /entropy) | ΔS ≥ 3.0 | Focused analysis, no multi-step workflows |
| **Agents** (e.g., /fag) | ΔS ≥ 5.0 | Multi-skill coordination, moderate complexity |
| **Orchestrators** | ΔS ≥ 7.0 | Multi-agent workflows, highest complexity |

**SABAR-72 Cooling:**
- Triggered when ΔS ≥ threshold
- Options: Defer, Decompose, Document
- Timer: 72 hours (Phoenix-72 protocol)

---

## Integration with arifOS Constitution

### Relationship to AGENTS.md

**Skills extend AGENTS.md governance:**
- AGENTS.md: Constitutional law (F1-F9, 000→999 pipeline)
- Skills Registry: Operational implementation of law

**Cross-Reference:**
```markdown
# AGENTS.md (add reference)
For skill definitions and operational procedures, see:
- [Skills Registry](L2_GOVERNANCE/skills/ARIFOS_SKILLS_REGISTRY.md)
```

### Relationship to Track B Specs

**Skills consume Track B specs:**
- `spec/v44/constitutional_floors.json` → Floor thresholds
- `spec/v44/genius_law.json` → G, C_dark metrics
- `spec/v44/session_physics.json` → Pipeline stages

**Spec changes propagate to skills via sync:**
1. Update spec JSON (Track B)
2. Regenerate manifest (`scripts/regenerate_manifest_v44.py`)
3. Update skill definitions (master .agent/ files)
4. Sync to platform variants (`scripts/sync_skills.py`)

---

## Future Enhancements

### Proposed Additions

1. **Memory Governance Skills**:
   - `/sunset` – Lawful revocation of outdated truths
   - `/vault` – Inspect canonical memory (Vault-999)
   - `/phoenix` – Manage temporary memory (Phoenix-72)

2. **Multi-Agent Federation**:
   - `/waw-law` – @LAW agent (Amanah enforcement)
   - `/waw-geox` – @GEOX agent (Truth verification)
   - `/waw-well` – @WELL agent (Care/empathy)
   - `/waw-rif` – @RIF agent (Reason/logic)

3. **Testing & Verification**:
   - `/verify-floors` – Test floor detectors against samples
   - `/audit-session` – Generate session audit report
   - `/merkle-proof` – Show cryptographic proof for ledger entry

### Skill Template (New Skill)

```yaml
---
skill: "new-skill"
version: "0.1.0"
description: "Brief description of constitutional function"
floors: [F1, F2, ...]
allowed-tools:
  - Tool1
  - Tool2
expose-cli: true/false
derive-to: [codex, claude]
---

## LAW (Constitutional Function)

[Describe what constitutional principle this enforces]

## INTERFACE (Usage & Shape)

[Show invocation examples and expected outputs]

## ENFORCEMENT (Runtime Behavior)

[Detail verdict logic, logging, and fail-closed patterns]
```

---

## Maintenance Protocol

### Adding a New Skill

1. **Create master file**: `.agent/workflows/new-skill.md`
2. **Define YAML frontmatter**: version, floors, allowed-tools
3. **Write LAW/INTERFACE/ENFORCEMENT sections**
4. **Add to registry**: Update this document's skill catalog
5. **Sync to platforms**: `python scripts/sync_skills.py --apply`
6. **Test enforcement**: Create unit tests for floor checks
7. **Update AGENTS.md**: Add cross-reference if needed

### Modifying Existing Skill

1. **Edit master only**: `.agent/workflows/[skill].md`
2. **Bump version**: Update version in YAML frontmatter
3. **Document changes**: CHANGELOG.md entry
4. **Sync**: Run `scripts/sync_skills.py --apply`
5. **Verify**: Run `scripts/check_skill_drift.py`
6. **Test**: Ensure floor enforcement still passes

### Deprecating a Skill

1. **Mark deprecated**: Add `deprecated: true` to YAML frontmatter
2. **Provide replacement**: Reference new skill in description
3. **Grace period**: Maintain for 2 major versions (v45 → v47)
4. **Remove**: Delete master file, sync platforms, update registry

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-29 | Initial unified registry (consolidates .agent/, .codex/, .claude/) |

---

## See Also

### Governance Framework

- [AGENTS.md](../../AGENTS.md) – Full constitutional governance (F1-F9, 000→999 pipeline)
- [FORGING_PROTOCOL_v45.md](../../L1_THEORY/canon/03_runtime/FORGING_PROTOCOL_v45.md) – **CANONICAL WORKFLOW** (Tri-Witness: /gitforge → /gitQC → /gitseal)
- [spec/v44/](../../spec/v44/) – Track B constitutional specs (thresholds)

### Plugin Governance

- [PLUGIN_GOVERNANCE.md](../../.claude/plugins/arifos-governed/governance/PLUGIN_GOVERNANCE.md) – Plugin governance framework
- [AAA_FRAMEWORK.md](../../.claude/plugins/arifos-governed/governance/AAA_FRAMEWORK.md) – Amanah-Authority-Accountability
- [ENTROPY_TRACKING.md](../../.claude/plugins/arifos-governed/governance/ENTROPY_TRACKING.md) – ΔS measurement details

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
