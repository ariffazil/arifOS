# .agent — arifOS Workflow System

**Version:** v46.1 (Sovereign Witness)
**Purpose:** Claude Code workflow definitions (skills) for arifOS governance automation
**Authority:** DERIVATIVE (implements governance defined in canon + spec)

---

## What Is This Directory?

The `.agent/` directory contains **workflow definitions** (also called "skills") that automate common arifOS governance tasks. These workflows are executed by Claude Code via the `/skill-name` command or through the Skill tool.

**Key Concept:** Workflows are **governance automation**, not governance itself. They implement the rules defined in:
- [L1_THEORY/canon/](../L1_THEORY/canon/) — Constitutional law (Track A)
- [spec/v46/](../L2_PROTOCOLS/v46/) — Thresholds & enforcement (Track B)
- [AGENTS.md](../AGENTS.md) — Multi-agent federation protocols

---

## Directory Structure

```
.agent/
├── README.md              # This file
├── ARCHITECT.md           # Architect role definition (Antigravity)
├── rules/                 # Tool restrictions and boundaries
│   ├── arifos_ontology.md
│   └── architect_boundaries.md
└── workflows/             # Workflow definitions (*.md files)
    ├── 000.md            # Session initialization
    ├── fag.md            # Full Autonomy Governance activation
    ├── gitforge.md       # Git entropy analysis
    ├── ledger.md         # THE EYE ledger operations
    ├── plan.md           # Architect planning workflow
    ├── review.md         # Architect review workflow
    └── handoff.md        # Architect handoff workflow
```

---

## Available Workflows (v46.1)

### 1. /000 — Session Initialization

**Command:** `/000` or `init-session`
**Purpose:** Load complete arifOS context at session start
**Floors enforced:** F1, F2, F4, F7

**What it does:**
1. Loads canon from [L1_THEORY/canon/](../L1_THEORY/canon/)
2. Checks current version (`pyproject.toml`)
3. Reviews recent git commits (`git log -10`)
4. Verifies Track B integrity (`python scripts/regenerate_manifest_v45.py --check`)
5. Checks Trinity Display mode (ASI/AGI/APEX)
6. Checks Phoenix-72 amendment system status
7. Loads [AGENTS.md](../AGENTS.md) federation rules
8. Reviews [CHANGELOG.md](../CHANGELOG.md)

**Expected output:**
```
- Current version: v46.1 (Sovereign Witness)
- Track B integrity: VERIFIED (SHA-256 manifest)
- Trinity Display: Ω (ASI) / Δ (AGI) / Ψ (APEX)
- Phoenix-72: ACTIVE (72h amendment cooling)
- Active branch: main
- Recent commits: [last 10 commits]
- Governance rules: LOADED
```

**When to use:** Start of EVERY new Claude Code session working on arifOS

---

### 2. /fag — Full Autonomy Governance

**Command:** `/fag` or `full-autonomy`
**Purpose:** Activate Full Autonomy Governance mode with clear boundaries
**Floors enforced:** F1, F2, F3, F4, F5, F6, F7, F8, F9 (all floors)

**What it does:**
1. Verifies `/000` was executed (context loaded)
2. Verifies `/gitforge` was executed (entropy state known)
3. Verifies Track B integrity (SHA-256 manifest)
4. Checks Phoenix-72 status (72h cooling window)
5. Verifies Trinity Display mode (ASI default)
6. Loads L2_GOVERNANCE authority matrix
7. Activates full autonomy with constitutional constraints

**Operational Parameters:**

**✅ AUTHORIZED (Auto-Execute):**
- Code edits within existing architecture
- Documentation updates
- Test creation/updates
- Bug fixes (non-breaking)
- Refactoring (behavior-preserving)
- Git operations (commit, branch, status)
- Entropy analysis

**⚠️ REQUIRES HUMAN APPROVAL:**
- Breaking API changes
- New dependencies
- Security-critical code
- Canon changes (Phoenix-72)
- Publishing/deployment
- File deletion
- New directory creation

**🚫 FORBIDDEN (Fail-Closed):**
- Bypass governance rules
- Modify fail-closed → fail-open
- Remove entropy tracking
- Disable time governor
- Commit without entropy check (ΔS > 3.0)
- Tamper with Track B without manifest regeneration
- Bypass Phoenix-72 cooling (72h)
- Modify Trinity Display defaults without PRIMARY source verification

**Constraints:**
- **SABAR Protocol:** ΔS ≥ 5.0 → COOL DOWN
- **Phoenix-72:** Constitutional amendments → 72h cooling window
- **Track B Integrity:** SHA-256 manifest must verify
- **Trinity Display:** ASI mode default (Ω)

**When to use:** After `/000` when starting autonomous development work

---

### 3. /gitforge — Git Entropy Analysis

**Command:** `/gitforge` or `analyze-entropy`
**Purpose:** Analyze git branch entropy and predict change impact
**Floors enforced:** F1, F4, F5

**What it does:**
1. Gets current branch name
2. Checks uncommitted changes (`git status --short`)
3. Analyzes branch history for hot zones (files changed ≥3 times)
4. Computes entropy delta (ΔS)
5. Calculates risk score (0.0-1.0)
6. Compares with main branch

**Interpretation:**

**Entropy Delta (ΔS):**
- ΔS < 3.0 → 🟢 Low entropy (clean, focused change)
- 3.0 ≤ ΔS < 5.0 → 🟡 Moderate entropy (acceptable with review)
- ΔS ≥ 5.0 → 🔴 HIGH ENTROPY (SABAR threshold exceeded, requires cooling)

**Risk Score:**
- 0.0-0.3 → 🟢 LOW RISK (fast track eligible)
- 0.4-0.6 → 🟡 MODERATE RISK (standard review)
- 0.7-1.0 → 🔴 HIGH RISK (full cooling + human review required)

**Hot Zones:**
Files appearing ≥3 times in last 30 commits. Touching hot zones increases risk.

**Fail-Closed Governance:**
If ΔS ≥ 5.0 OR Risk Score ≥ 0.7 OR modifying PRIMARY sources:
1. HALT further changes
2. Run cooling protocol (defer, decompose, or document)
3. **Phoenix-72:** If modifying spec/v46/*.json or canon/*.md → 72h cooling window
4. Seek human approval before proceeding
5. Log entropy event to cooling_ledger/

**v46.1 Integration:**
- **Track B Integrity:** Verify SHA-256 manifest after spec changes
- **Phoenix-72:** Constitutional amendments require 72h cooling
- **Trinity Display:** Entropy analysis can trigger AGI/APEX mode (forensic review)

**When to use:** Before making significant changes, before committing, during code review

---

### 4. /plan — Architect Planning Mode

**Command:** `/plan` or `architect-plan`
**Purpose:** Create implementation plans (Architect role - Antigravity)
**Floors enforced:** F4, F7

**What it does:**
1. Understands user's feature request
2. Searches existing codebase (MANDATORY discovery before creating files)
3. Identifies affected components
4. Designs solution architecture with file-by-file changes
5. Creates `implementation_plan.md` artifact
6. Requests user review

**Who uses this:** Antigravity (Architect Δ) when designing solutions

---

### 5. /review — Architect Review

**Command:** `/review` or `architect-review`
**Purpose:** Validate Engineer's completed work (Architect role - Antigravity)
**Floors enforced:** F4, F8

**What it does:**
1. Loads the original approved plan
2. Reviews changes made by Engineer (Claude)
3. Verifies implementation matches architectural intent
4. Checks for F4 violations (entropy increase)
5. Issues decision: APPROVED / CHANGES REQUESTED / VOID

**Who uses this:** Antigravity (Architect Δ) after Claude implements

---

### 6. /handoff — Architect Handoff

**Command:** `/handoff` or `architect-handoff`
**Purpose:** Hand off approved plan to Engineer (Architect role - Antigravity)
**Floors enforced:** F4, F3

**What it does:**
1. Verifies plan is approved by human
2. Creates handoff directory (`.antigravity/`)
3. Writes `HANDOFF_FOR_CLAUDE.md` with:
   - Approved plan summary
   - Files to create/modify
   - Tests to write
   - Success criteria
4. Notifies user how to proceed

**Who uses this:** Antigravity (Architect Δ) to delegate implementation

---

## Agent Roles (v46.1)

arifOS uses a **Trinity governance model** with four specialized participants:

| Role | Agent | Symbol | Config File | Canonical Stages |
|------|-------|--------|-------------|------------------|
| **Architect** | Antigravity (Gemini) | Δ (Delta) | [.agent/ARCHITECT.md](.agent/ARCHITECT.md) | 000–444 |
| **Engineer** | Claude Code | Ω (Omega) | [CLAUDE.md](../CLAUDE.md) | 444–888 |
| **Auditor** | Codex (ChatGPT) | Ψ (Psi) | [.codex/](../.codex/) | 888–999 |
| **Meta APEX** | KIMI | Κ (Kappa) | [.kimi/](../.kimi/) | 999 |

**Separation of Powers:**
- **Architect (Δ)** designs and plans (stage 444)
- **Engineer (Ω)** builds and tests (stages 666–888)
- **Auditor (Ψ)** validates and prepares verdict (stage 888–999)
- **KIMI (Κ)** Meta APEX PRIME — issues final SEAL/VOID (stage 999)
- **Human (Arif)** has ultimate authority → ratifies or rejects

**No agent can both propose AND seal their own work.**

---

## Agent Alignment (v46.1 "Sovereign Witness")

### Canonical AClip Spine (v46)

arifOS uses a **five-stage canonical governance pipeline** (000→444→666→888→999) with sub-phases for detailed workflow documentation.

| Canonical Stage | Role(s) | Action | Floors |
|---|---|---|---|
| **000** | ARCHITECT | Load canonical sources (AGENTS.md, spec/v46, L1_THEORY/canon/) | F1, F2 |
| **444** | ARCHITECT | Plan & seal (draft→review→seal handoff) | F2, F3 |
| **666** | ENGINEER | Implement changes (code, test, iterate) | F2, F4, F5 |
| **888** | ENGINEER + AUDITOR | Review (self-review + constitutional audit) | F5, F1, F3, F6 |
| **999** | KIMI | Final seal (SEAL/VOID/HOLD-888 authority) | F1–F12 |

### Roles & Separation of Powers

| Role | Symbol | Stages | Key Responsibility | Floors |
|---|---|---|---|---|
| **ARCHITECT** | Δ (Delta) | 000–444 | Plan changes; ensure Truth + Clarity | F1, F2 |
| **ENGINEER** | Ω (Omega) | 444–888 | Implement; ensure Clarity + Iteration + Craft | F2, F4, F5 |
| **AUDITOR** | Ψ (Psi/Codex) | 888–999 | Audit; ensure Truth + Stability + Amanah | F1, F3, F6 |
| **KIMI** | Κ (Kappa) | 999 | Meta APEX PRIME; final governance authority | F1–F12 |

### Handoff Documents

- **Stage 444 → 666**: `.antigravity/HANDOFF_FOR_CLAUDE.md` (ARCHITECT to ENGINEER)
- **Stage 888 → 999**: AUDITOR verdicts (ENGINEER/AUDITOR to KIMI)
- **Session Ledger**: `.arifos_clip/session_ROLE_STAGE_TIMESTAMP.json`

### Canonical Sources (v46)

- **AGENTS.md** (repo root): Roles, stages, governance framework
- **spec/v46** (L2_PROTOCOLS/v46/): Thresholds, floors (F1–F12), enforcement
- **L1_THEORY/canon/**: Canonical philosophy (Track A) — immutable without Phoenix-72 amendment
- **L2_PROTOCOLS/v46/**: Operational protocols (Track B) — version-controlled
- **L2_GOVERNANCE/skills/ARIFOS_SKILLS_REGISTRY.md**: Skill source of truth (all platforms derive)

### Platform Derivatives

Each platform surface is a **derivative** of canonical sources:

| Platform | Role | Canonical Source |
|---|---|---|
| **.agent/** | ARCHITECT | AGENTS.md, spec/v46 |
| **.claude/** | ENGINEER | AGENTS.md, spec/v46, L2_GOVERNANCE/skills/ |
| **.codex/** | AUDITOR | AGENTS.md, spec/v46, L2_GOVERNANCE/skills/ |
| **.kimi/** | Meta APEX PRIME | AGENTS.md, spec/v46 (exclusive skills) |
| **.cursor/** | ARCHITECT surface | spec/v46, AGENTS.md |
| **.gemini/** | Specialist research | spec/v46, AGENTS.md |

### Sub-Phases (Detailed Workflows)

Within each canonical stage, sub-phases provide workflow detail:

**Stage 000 (ARCHITECT Init)**
- Load AGENTS.md + spec/v46
- Verify canonical sources readable
- Check for conflicts/amendments

**Stage 444 (ARCHITECT Plan & Seal)**
- 044: READ (survey existing code)
- 066: DRAFT (create implementation plan)
- 088: REVIEW (validate plan)
- 099: SEAL (handoff to ENGINEER)

**Stage 666 (ENGINEER Implement)**
- 300: INIT (load handoff, read plan)
- 444: READ (understand requirements)
- 666: IMPL (write code, test)
- 699: REVIEW (self-review before seal)

**Stage 888 (Review)**
- 700: AUDITOR init (load output)
- 744: AUDITOR read (analyze changes)
- 766: AUDITOR audit (check floors F1, F3, F6)
- 888: ENGINEER review (self-review) + AUDITOR verdict (prepare summary)

**Stage 999 (KIMI Final Seal)**
- Receive verdicts from stage 888
- Check all floors (F1–F12)
- Issue SEAL, VOID, HOLD-888, or SABAR
- Log to session ledger with reasoning

---

## Workflow Metadata Format

Workflows are defined in Markdown files with YAML frontmatter:

```yaml
---
skill: "workflow-name"
version: "1.0.0"
description: Short description for tool listings
floors:
  - F1
  - F2
  - F4
allowed-tools:
  - Read
  - Bash(git:*)
  - Bash(python:*)
expose-cli: true
derive-to:
  - codex
  - claude
codex-name: alternative-command-name
claude-name: another-alternative-name
sabar-threshold: 5.0  # Optional: ΔS threshold for SABAR
---
# /workflow-name - Workflow Title

[Markdown documentation of the workflow]
```

**Fields:**

- **skill** — Primary command name (used as `/skill-name`)
- **version** — Workflow version (semver)
- **description** — Short description for skill listings
- **floors** — Which constitutional floors this workflow enforces
- **allowed-tools** — Tools the workflow can use (security constraint)
- **expose-cli** — Whether to expose as CLI command
- **derive-to** — Platform aliases (codex, claude, etc.)
- **codex-name** / **claude-name** — Alternative command names
- **sabar-threshold** — Optional ΔS threshold for SABAR protocol

---

## Usage Examples

### Starting a New Session

```bash
# 1. Initialize context
/000

# 2. Check entropy state
/gitforge

# 3. Activate full autonomy
/fag

# 4. Start development work with governance active
```

### Before Making Changes

```bash
# Check current entropy state
/gitforge

# If ΔS < 5.0 and Risk < 0.7 → proceed
# If ΔS ≥ 5.0 or Risk ≥ 0.7 → decompose or defer
```

### Before Committing

```bash
# Verify entropy is acceptable
/gitforge

# If ΔS ≥ 5.0 → run cooling protocol:
# - Defer: Wait, reconsider
# - Decompose: Split into smaller commits
# - Document: Add context to CHANGELOG
```

---

## v46.1 Integration Points

**Workflows now enforce v46.1 governance:**

### 1. Track B Integrity (SHA-256 Manifest)
All workflows verify `L2_PROTOCOLS/v46/` integrity:
```bash
python scripts/regenerate_manifest_v45.py --check
```

### 2. Phoenix-72 Amendment System
Constitutional changes trigger 72h cooling window:
- Modifying `L2_PROTOCOLS/v46/*.json` → Phoenix-72 cooling
- Modifying `L1_THEORY/canon/*.md` → Phoenix-72 cooling

### 3. Trinity Display Architecture
Workflows respect ASI/AGI/APEX display modes:
- **ASI (Ω)** — Default public mode (clean output)
- **AGI (Δ)** — Developer mode (pipeline + ΔΩΨ Trinity)
- **APEX (Ψ)** — Auditor mode (full forensic + F1-F9 floors)

### 4. Constitutional Floors (F1-F12)
All workflows enforce floors with v46.1 thresholds:
- F1 Truth (≥0.99) — Factual accuracy
- F2 Clarity (≥0) — Transparency
- F3 Stability (LOCK) — Reversibility
- F4 Iteration (ΔS ≥ 0) — Clarity gain
- F5 Craft (LOCK) — Quality gates
- F6 Amanah (LOCK) — Governance respect
- F7 Humility (0.03–0.05) — Uncertainty quantification
- F8–F12 — Hypervisor layer (see spec/v46)

---

## Relationship to Other Governance Files

```
PRIMARY (Authoritative):
├── L1_THEORY/canon/ (Track A - Constitutional law)
├── spec/v46/ (L2_PROTOCOLS/v46/ - Thresholds, SHA-256 verified)
└── arifos_core/ (Track C - Runtime enforcement)

DERIVATIVE (Implements governance):
└── .agent/ (Workflow automation - NOT authoritative)
```

**Data Flow:**
```
Canon + Spec (PRIMARY)
    ↓ defines rules
Workflows (.agent/)
    ↓ automates
Claude Code execution
    ↓ produces
Git commits (sealed artifacts)
```

**Rule:** Workflows derive from PRIMARY sources. Never modify canon/spec based on workflow behavior alone. Always verify against PRIMARY sources.

---

## Adding New Workflows

**Process:**

1. **Identify repetitive governance task** (e.g., ledger verification, test running)

2. **Design workflow steps:**
   - What context needs loading?
   - Which floors must be enforced?
   - What tools are required?
   - What's the expected output?

3. **Create `workflows/new-workflow.md`:**
   ```yaml
   ---
   skill: "new-workflow"
   version: "1.0.0"
   description: Brief description
   floors:
     - F1
     - F2
   allowed-tools:
     - Read
     - Bash(git:*)
   expose-cli: true
   derive-to:
     - claude
   claude-name: alternative-name
   ---
   # /new-workflow - Workflow Title

   [Documentation here]
   ```

4. **Test workflow:**
   ```bash
   /new-workflow
   # Verify it executes correctly
   ```

5. **Update this README:**
   - Add workflow to "Available Workflows" section
   - Document usage examples

6. **Commit with governance:**
   ```bash
   git add .agent/workflows/new-workflow.md .agent/README.md
   git commit -m "feat(agent): Add /new-workflow skill

   Tests: X/X passing
   Floors: F1=LOCK F2≥0.99
   Verdict: SEAL"
   ```

---

## Anti-Patterns (What NOT to Do)

❌ **DON'T modify workflows to bypass governance:**
```yaml
# WRONG - Weakening floor enforcement
floors:
  - F1  # Removed F2 Truth to avoid verification
```

❌ **DON'T use workflows as authoritative sources:**
```python
# WRONG - Citing workflow as PRIMARY source
claim = "F2 Truth threshold is 0.99"
source = ".agent/workflows/000.md"  # NOT PRIMARY

# CORRECT - Verify against spec
claim = "F2 Truth threshold is 0.99"
source = "spec/v46/constitutional_floors.json"  # PRIMARY
```

❌ **DON'T create workflows that modify canon directly:**
```bash
# WRONG - Direct canon modification
echo "New rule" >> L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v46.md

# CORRECT - Use Phoenix-72 amendment system
python scripts/propose_amendment.py --file "..." --rationale "..."
# Wait 72h cooling window
# Verify consensus
# Seal amendment
```

---

## Common Issues & Debugging

### Workflow Fails to Execute

**Symptom:** `/workflow-name` does nothing or errors

**Check:**
1. Is YAML frontmatter valid? (no syntax errors)
2. Is `expose-cli: true` set?
3. Is skill name correct in frontmatter?
4. Are required tools allowed in `allowed-tools`?

### Track B Verification Fails

**Symptom:** `python scripts/regenerate_manifest_v45.py --check` fails

**Fix:**
```bash
# Regenerate manifest if specs were legitimately changed
python scripts/regenerate_manifest_v45.py

# If unauthorized change, restore from git
git checkout spec/v46/
```

### Phoenix-72 Cooling Window Not Respected

**Symptom:** Constitutional changes committed without 72h wait

**Fix:**
```bash
# Revert commit
git revert HEAD

# Propose amendment properly
# Wait 72h
# Re-commit with cooling evidence
```

### High Entropy Warning Ignored

**Symptom:** Committed changes with ΔS ≥ 5.0

**Fix:**
```bash
# Decompose commit into smaller changes
git reset --soft HEAD~1
git add <file1>
git commit -m "Part 1: ..."
git add <file2>
git commit -m "Part 2: ..."
```

---

## Session Workflow (Recommended)

### Daily Development Session

```bash
# 1. SESSION START
/000                    # Load context
/gitforge              # Check entropy state
/fag                   # Activate full autonomy

# 2. DEVELOPMENT WORK
# ... code, test, document ...

# 3. BEFORE COMMIT
/gitforge              # Verify ΔS < 5.0
git status             # Review changes
git add <files>        # Stage intentional changes

# 4. COMMIT
git commit -m "type(scope): description

Tests: X/X passing
Floors: F1=LOCK F2≥0.99 F4≥0
Verdict: SEAL"

# 5. SESSION CLOSE
git log -5             # Review commits
git push origin main   # Push if ready
```

---

## DITEMPA BUKAN DIBERI

Workflows are **forged, not given**. They automate governance but are NOT governance themselves.

**Philosophy:**
- Canon (L1_THEORY/) = Eternal (SEALED until Phoenix-72 amendment)
- Spec (spec/v46/) = Semi-eternal (SHA-256 locked, version-controlled)
- Code (arifos_core/) = Runtime (tested, released)
- Workflows (.agent/) = **Automation** (derives from PRIMARY sources)

**Forged, not given.** Workflows cool into git commits, which cool into ledger entries, which inform future canon amendments. But workflows themselves are NOT law.

**Akal Memerintah. Amanah Mengunci.**

---

**Last Updated:** 2026-01-12 (v46.1 Agent Alignment)
**Maintainer:** Human (Arif) + Trinity (Δ, Ω, Ψ, Κ)
**License:** AGPL-3.0 (same as repo)

---

## Agent Alignment (v46 AClip)

### Canonical Sources
- `AGENTS.md` (root): Roles, floors (v46) and separation of powers
- `spec/v46/*`: Floor thresholds, AClip stages, governance JSON
- `L2_GOVERNANCE/skills/ARIFOS_SKILLS_REGISTRY.md`: Skill source of truth

### AClip Pipeline (normalized)
`000 (init) → 444 (read) → 666 (act) → 888 (review) → 999 (seal)`

*Crosswalk:* bundle shorthand (044/066/088/099/300/699/700/744) maps onto the canonical spine above; use canonical numbering in this file and note the shorthand only when mirroring bundle text.

### Role Stage Expectations
- Architect (Δ): 000 before planning, 444 governed reads, 666 draft/plan, 888 self-check, 999 handoff to Engineer.
- Engineer (Ω): 000 before implementation, 444 governed reads of plan, 666 implement/tests, 888 self-review, 999 handoff to Auditor.
- Auditor (Ψ): 000 before audit, 444 governed reads of changes + plan, 666 audit actions (non-code), 888 verdict prep, 999 verdict handoff to KIMI/human.
- KIMI (Κ Meta APEX PRIME): 000 before constitutional sweep, 444 reads, 666 audit tools, 888 final check, 999 SEAL/VOID/PARTIAL/SABAR/888_HOLD.

### Mandatory Skills (all surfaces)
- `/000-init`, `/fag-read` (governed read with receipt), `/plan`, `/handoff`, `/review`, `/cool` (SABAR-72), `/ledger` view, `/gitforge` / `/gitQC` / `/gitseal`, `/websearch-grounding` (when allowed), `/999-seal`.

### Alignment Notes
- Use canonical floors F1–F12 per `spec/v46/constitutional_floors.json` (RASA=F7, Tri-Witness=F8, Anti-Hantu=F9, Symbolic Guard=F10, Command Auth=F11, Injection Defense=F12).
- Separation of powers: no self-seal; Architect ≠ Engineer ≠ Auditor ≠ KIMI.
- Read-before-write; append/surgical edits only; no new files without mandate/entropy reduction.

### Verification Commands
```bash
rg --hidden -n "v45" .agent .codex .claude .kimi .cursor .gemini
rg --hidden -n "000|999" .agent .codex .claude .kimi .cursor .gemini
python scripts/sync_skills.py --check
python scripts/trinity.py forge main
```
