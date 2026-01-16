# Agent Identities — Quick-Start Role Guides (v47.0)

**Purpose:** Model-agnostic agent identity files for rapid LLM onboarding

**Philosophy:** Any LLM can pick up any role in different sessions via these identity files.

---

## 🎯 Quick Start

### For LLMs (AI Agents)

**Pick your role, read the file:**

| Role | Identity File | Read This If... |
|------|---------------|----------------|
| **Architect** | [architect.md](architect.md) | You design solutions (DESIGN, not code) |
| **Engineer** | [engineer.md](engineer.md) | You write code (BUILD, not design) |
| **Auditor** | [auditor.md](auditor.md) | You review code (JUDGE, not implement) |
| **Validator** | [validator.md](validator.md) | You issue final verdicts (SEAL/VOID) |

### For Humans (Setting Up Agents)

**Model-agnostic assignment:**

1. **Choose LLM for role:** Edit `config/agents.yaml`
   ```yaml
   agents:
     architect: "gemini-flash-2.0"
     engineer: "claude-sonnet-4.5"
     auditor: "gpt-4o"
     validator: "kimi-k2"
   ```

2. **Agent reads identity file:** Point LLM to `identities/{role}.md`

3. **Session isolation enforced:** Same LLM cannot occupy multiple roles in same session

---

## 📂 File Structure

```
identities/
├── README.md                # This file - Directory guide
├── architect.md             # Quick guide for Architect role (170 lines)
├── engineer.md              # Quick guide for Engineer role (215 lines)
├── auditor.md               # Quick guide for Auditor role (245 lines)
├── validator.md             # Quick guide for Validator role (varies)
└── SKILLS_MATRIX.md         # Comprehensive skills breakdown (500+ lines)
```

### File Purpose

| File | Audience | Use Case | Length |
|------|----------|----------|--------|
| **{role}.md** | LLM starting work | Quick operational guide | ~200 lines |
| **SKILLS_MATRIX.md** | Humans, Training | Detailed skills/knowledge/workflows | 500+ lines |
| **README.md** | Both | Directory navigation | This file |

---

## 🔄 Model-Agnostic Architecture

**Key Innovation (v47.0):** Roles are constitutional law (immutable). LLM assignments are configuration (swappable).

### Example: Role Swapping

```
Session 1:
- Claude = Engineer (builds code)
- Gemini = Architect (designs)

Session 2:
- Claude = Architect (designs)
- Gemini = Engineer (builds)

Result: Same governance, different technology
```

**Why this works:**
- Identity files define **constitutional responsibilities** (role boundaries)
- `config/agents.yaml` assigns **LLM technology** (which AI does what)
- Session isolation prevents role confusion within same conversation

---

## 📚 Identity File Format

Each identity file follows this structure:

```markdown
# ROLE NAME - Brief Description

**Current AI:** Loaded from config/agents.yaml
**Workspace:** .{workspace-name}/
**Version:** v47.0

## Your Job
- What you DO
- What you DON'T do

## Your Workflows
- Step-by-step processes

## Constitutional Rules
- Which floors you're responsible for

## Boundaries
- ✅ Authorized without asking
- ⚠️ Requires human approval
- ❌ Forbidden

## Anti-Patterns to Avoid
- Common mistakes

## Quick Commands
- Useful bash/Python snippets

## The Trinity Flow
- Where you fit in the workflow
```

---

## 🎯 When to Use Which File

### During Work (LLM Reading)

**Use identity files** ([architect.md](architect.md), [engineer.md](engineer.md), etc.):
- ✅ Quick reference during active work
- ✅ Understand boundaries and permissions
- ✅ Remember workflows and checklists
- ✅ ~200 lines, easy to scan

**Use SKILLS_MATRIX.md**:
- ❌ Too detailed for active work
- ✅ For understanding "why" behind rules
- ✅ For training new LLMs on roles
- ✅ For human evaluation of agent skills

### During Setup (Human Configuring)

**Use SKILLS_MATRIX.md**:
- ✅ Evaluate if LLM has required skills
- ✅ Understand knowledge domains needed
- ✅ Set success metrics for evaluation
- ✅ Compare agent capabilities

**Use identity files**:
- ✅ Give to LLM as starting prompt
- ✅ Verify LLM understands boundaries
- ✅ Quick sanity check on role fit

---

## 🔗 Related Documentation

### For Understanding arifOS

| Topic | Location | Purpose |
|-------|----------|---------|
| **Agent Architecture** | `AGENTS.md` | Complete Trinity system, 12 floors, pipeline |
| **Constitutional Law** | `L1_THEORY/canon/` | Immutable governance principles |
| **Floor Specifications** | `L2_PROTOCOLS/v46/` | Configurable thresholds and rules |
| **Runtime Implementation** | `arifos_core/` | Python code that enforces governance |

### For Agent Operation

| Topic | Location | Purpose |
|-------|----------|---------|
| **Architect Details** | `.agent/ARCHITECT.md` | Detailed Architect constitutional context |
| **Engineer Boundaries** | `.claude/rules/engineer_boundaries.md` | Complete Engineer permissions |
| **Auditor Context** | `.codex/AGENTS.md` | Constitutional AGENTS.md for Codex |
| **Validator Context** | `.kimi/` | Kimi-specific governance context |

---

## 🚀 Quick Examples

### Example 1: New LLM Picks Up Architect Role

**Scenario:** User wants to try GPT-4o as Architect

```bash
# 1. User edits config
vim config/agents.yaml
# Change: architect: "gpt-4o"

# 2. User starts GPT-4o session
# 3. GPT-4o reads: identities/architect.md
# 4. GPT-4o understands: "I DESIGN, I don't code"
# 5. User requests: "Plan how to add feature X"
# 6. GPT-4o follows /plan workflow from architect.md
```

### Example 2: Engineer Checks Boundary During Work

**Scenario:** Claude (Engineer) unsure if can delete a file

```markdown
Engineer (Claude) thinking:
"User asked me to delete old_utils.py. Can I do this?"

Checks: identities/engineer.md § Boundaries
Finds: "⚠️ Deleting files (except temp/cache) requires human approval"

Action: Ask user for explicit approval before deleting
```

### Example 3: Auditor Validates All Floors

**Scenario:** Codex needs to check if work passes constitutional review

```markdown
Auditor (Codex) workflow:
1. Reads: identities/auditor.md § Constitutional Validation
2. Sees: "Check all 12 floors" (F1-F12 listed)
3. Goes through checklist:
   - F1 (Truth): ✅ PASS
   - F2 (Clarity): ✅ PASS
   - F3 (Peace²): ⚠️ FLAG - Deletes production code
   - ... (checks all 12)
4. Verdict: FLAG (soft floor warning)
5. Creates: .antigravity/REVIEW_REPORT.md
```

---

## 📊 File Comparison

| Aspect | Identity Files ({role}.md) | SKILLS_MATRIX.md |
|--------|---------------------------|------------------|
| **Length** | ~200 lines | 500+ lines |
| **Audience** | LLMs during work | Humans, trainers, evaluators |
| **Purpose** | Operational quick reference | Comprehensive knowledge base |
| **Format** | Checklists, workflows, commands | Tables, matrices, metrics |
| **Update Frequency** | When roles change | When skills evolve |
| **Read Time** | 5 minutes | 30+ minutes |

---

## ✅ Validation Checklist

**Before using identity files:**

- [ ] `config/agents.yaml` exists and assigns LLMs to roles
- [ ] LLM understands their identity file for the role
- [ ] LLM knows what they CAN do (✅ Authorized)
- [ ] LLM knows what they CANNOT do (❌ Forbidden)
- [ ] LLM knows when to defer to other agents
- [ ] Session isolation enforced (same LLM ≠ multiple roles in same session)

---

## 🔧 Maintenance

### When to Update Identity Files

**Update architect.md, engineer.md, auditor.md, validator.md when:**
- Role boundaries change (new permissions/restrictions)
- Workflows are refined (better processes discovered)
- Anti-patterns identified (new mistakes to avoid)
- Quick commands change (new tools introduced)

**Update SKILLS_MATRIX.md when:**
- New skill domains emerge
- Success metrics change
- Knowledge requirements evolve
- Training recommendations improve

### How to Keep Consistent

1. **Changes to roles** → Update AGENTS.md (authority)
2. **Changes to floors** → Update L1_THEORY/canon/ (law)
3. **Changes to workflows** → Update identity files (operational)
4. **Changes to skills** → Update SKILLS_MATRIX.md (training)

---

## 🎯 Success Criteria

**Identity files are working when:**

✅ LLMs can pick up roles with <5 minutes of reading
✅ LLMs understand boundaries without human clarification
✅ LLMs defer to correct agents when out of scope
✅ Zero violations of forbidden actions
✅ 100% compliance with constitutional floors

**Identity files need improvement when:**

❌ LLMs frequently ask "can I do X?"
❌ LLMs violate boundaries repeatedly
❌ LLMs redesign their own roles
❌ Workflows unclear or incomplete

---

## 📞 For Help

**If LLM confused about role:**
1. Read the identity file for that role again
2. Check SKILLS_MATRIX.md for detailed breakdown
3. Review AGENTS.md for constitutional context
4. Ask human for clarification

**If role boundaries unclear:**
1. Check `.agent/rules/{role}_boundaries.md` for details
2. Review L1_THEORY/canon/ for constitutional law
3. Consult L2_PROTOCOLS/v46/ for floor specifications

---

**DITEMPA BUKAN DIBERI** — Agent identities are forged through constitutional clarity, not technological convenience.

**Version:** v47.0
**Status:** CANONICAL
**Authority:** Model-Agnostic Agent Architecture (AGENTS.md § 🔧)
