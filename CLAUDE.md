# CLAUDE.md - arifOS Sovereign Context

**Role:** arifOS Sovereign Witness (System-3)
**Motto:** "DITEMPA BUKAN DIBERI" (Forged, not given)
**Authority:** [AGENTS.md](AGENTS.md) is Supreme Law.

## ⚡ Core Protocols

### 1. FAG RAPES-M (Autonomous Ladder)
The FAG (Full Autonomy Governance) mode operates on the **RAPES-M** cycle:
- **R**eflect (Stage 111): Sense context. **SEARCH FIRST** (Internal `grep` or Web if enabled).
- **A**nalyze (Stage 333): thermodynamic assessment (ΔS check).
- **P**lan (Stage 666): Align with 9 Floors.
- **E**xecute (Stage 777): Forge code/files (Reversible acts only).
- **S**eal (Stage 999): Finalize with Human+AI+Earth witness.
- **M**emory (Ledger): Log receipt to Cooling Ledger.

### 2. The "No-Pencemaran" Rule (Anti-Pollution)
**F4 DeltaS Violation**: Creating a file that overlaps with an existing one is **POLLUTION**.
- **Mandatory Discovery**: Before `touch new_thing.py`, you MUST runs `ls` or `grep` to find `existing_thing.py`.
- **Append > Create**: If a file exists, add to it. Do not create `new_thing_v2.py`.
- **Reasoning**: "I didn't see it" is not an excuse. **Look harder.**

### 3. Trinity Git Governance
- **Forge**: `python scripts/trinity.py forge <branch>` (Check Entropy/Hotspots)
- **QC**: `python scripts/trinity.py qc <branch>` (Validate F1-F9 Floors)
- **Seal**: `python scripts/trinity.py seal <branch> "Reason"` (Atomic Approval)

### 3. The 9 Constitutional Floors (Fail-Closed)
| Floor | Principle | Constraint |
|-------|-----------|------------|
| **F1** | **Amanah** | Integrity. **Reversible** acts only. No side effects. |
| **F2** | **Truth** | Reality. No hallucinations. **>0.99** confidence. |
| **F3** | **Witness** | Consensus. Human-AI-Earth agree. |
| **F4** | **DeltaS** | Clarity. Reduce entropy. **ΔS < 0**. |
| **F5** | **Peace²** | Safety. Non-destructive. |
| **F6** | **κᵣ** | Empathy. Serve the weakest stakeholder. |
| **F7** | **Ω₀** | Humility. State uncertainty (3-5%). |
| **F8** | **Genius** | Governed Intelligence. |
| **F9** | **C_dark** | No Dark Cleverness. No deception. |

## 🚫 Critical Anti-Patterns (VOID Triggers)
1.  **The Janitor**: NEVER "clean up" files by removing sections. **APPEND ONLY**.
2.  **The Ghost**: NEVER create files without explicit human request or entropy justification.
3.  **The Hallucinator**: NEVER claim specific constitutional thresholds without reading `spec/v45/`.
4.  **The Bypass**: NEVER skip `trinity.py` commands for git operations.

## 🛠️ Tooling
- **Test**: `pytest`
- **Lint**: `ruff check .`
- **Format**: `black .`

---

## 🏛️ v46 Architectural Wisdom (For Agent Reference)

**Context:** Large-scale refactoring (331 files, 8-folder orthogonal restructure)
**Date:** 2026-01-08
**Agent:** Claude Sonnet 4.5 (AGI Coder - Δ)

### 1. **Systematic Planning Prevents Chaos**

**Lesson:** Before touching ANY files, plan the ENTIRE migration.

**What Worked:**
```python
# Used TodoWrite to break down migration:
A. Move enforcement zone (11 items)
B. Move integration zone (9 items)
C. Move system zone (7 items)
D. Move memory zone (1 item)
E. Move apex zone (2 items)
F. Update imports (304 files)
G. Verify with tests
```

**Why This Matters:**
- Clear progress tracking (user can see % complete)
- No forgotten files
- Atomic, reversible steps
- Easy to pause/resume

**Anti-Pattern:**
- ❌ "Let me just move files and see what breaks"
- ❌ Starting import fixes before all moves are done
- ❌ Not tracking progress systematically

### 2. **Relative Imports Are Treacherous in Nested Structures**

**Lesson:** Python's `..` and `...` notation is depth-sensitive. Get it wrong = hours of debugging.

**The Rule (v46):**
```python
# ROOT-LEVEL zone files (e.g., enforcement/metrics.py)
from ..system import apex_prime      # Use .. for sibling zones
from ..apex.governance import fag

# SUBDIRECTORY files (e.g., enforcement/eval/asi.py)
from ...system import apex_prime     # Use ... to reach other zones
from ..metrics import check_truth    # Use .. to reach parent zone
```

**Pattern:** Each level of directory nesting = one extra `..`

**What Broke:**
```python
# WRONG: File at enforcement/eval/evaluate.py
from ..system.apex_prime import APEXPrime
# Resolves to: arifos_core.enforcement.system (doesn't exist!)

# CORRECT:
from ...system.apex_prime import APEXPrime
# Resolves to: arifos_core.system (exists!)
```

**How to Fix:**
1. Count directory depth: `arifos_core/enforcement/eval/asi.py` = 2 levels deep in zone
2. To import from OTHER zones: use `...` (up to arifos_core, then down to target)
3. To import from SAME zone parent: use `..` (up to enforcement/)

**Tool Created:** `fix_system_imports.py`, `fix_integration_subdir_imports.py` (automated the fixes)

### 3. **Git History Is Sacred: Use `git mv`, Not Delete+Create**

**Lesson:** Preserving git history during refactors maintains accountability and blame tracking.

**What Worked:**
```bash
git mv arifos_core/attestation arifos_core/enforcement/
git mv arifos_core/audit arifos_core/enforcement/
# ... (30 items)
```

**Why:**
- Git knows it's the SAME file, just moved
- `git blame` still works
- `git log --follow` shows full history
- Reviewers can see "this is a move, not a rewrite"

**Anti-Pattern:**
```bash
# ❌ WRONG: Destroys history
rm -rf arifos_core/attestation
mkdir -p arifos_core/enforcement/attestation
cp -r /tmp/backup arifos_core/enforcement/attestation
```

### 4. **Test-Driven Refactoring: Run Tests After EVERY Phase**

**Lesson:** Don't wait until the end to verify. Test incrementally.

**What Worked:**
```
Phase 1: Move files → Run tests → ❌ Import errors (expected)
Phase 2: Fix absolute imports → Run tests → ❌ Relative import errors
Phase 3: Fix relative imports → Run tests → ✅ 15/15 passing
Phase 4: Fix edge cases → Run tests → ✅ 36/36 passing
```

**Why:**
- Catch regressions immediately
- Know which phase introduced the break
- Confidence to proceed to next phase

**Anti-Pattern:**
- ❌ "I'll move everything, fix all imports, then test at the end"
- ❌ Batching multiple phases without verification

### 5. **Scripts Beat Manual Edits for Repetitive Tasks**

**Lesson:** When refactoring >50 files, write a script. Don't edit manually.

**What Worked:**
```python
# scripts/refactor_imports_v46.py
for py_file in all_files:
    content = read(py_file)
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)
    write(py_file, content)
```

**Stats:**
- 304 files updated
- 0 manual edits
- 100% consistency
- Took 2 minutes (vs. hours manually)

**Scripts Created:**
1. `refactor_imports_v46.py` - Main absolute import refactoring
2. `fix_system_imports.py` - System subdirectory fixes
3. `fix_system_root_imports.py` - System root-level files
4. `fix_apex_imports.py` - Apex subdirectory fixes
5. `fix_integration_subdir_imports.py` - Integration subdirectory fixes

**Anti-Pattern:**
- ❌ Opening 304 files in editor and manually editing each one
- ❌ Using regex find-replace without testing on small subset first

### 6. **Incremental Commits Tell a Story**

**Lesson:** Each commit should be atomic and self-explanatory.

**What Worked:**
```
984a132 - refactor(v46): Consolidate arifos_core (313 files)
8b20456 - fix(v46): Complete relative import fixes (16 files)
38c03a6 - docs(v46): Update migration report
bcc4f66 - fix(v46): Fix remaining import paths (2 files)
ecf479b - docs(v46): Add architecture diagram
```

**Why:**
- Easy to bisect if something breaks
- Clear progression of work
- Reviewable in logical chunks
- Revertable if needed

**Anti-Pattern:**
- ❌ One giant commit: "refactor(v46): everything (331 files)"
- ❌ Mixing moves + import fixes + docs in one commit

### 7. **Documentation Is Part of the Refactor, Not an Afterthought**

**Lesson:** Write migration docs DURING the refactor, not after.

**What Worked:**
```
During refactor:
- V46_8FOLDER_RESTRUCTURE.md (migration report)
- V46_ARCHITECTURE_DIAGRAM.md (visual map)
- CHANGELOG.md (detailed changelog)
- CLAUDE.md (this wisdom section)
```

**Why:**
- Captures decisions while fresh in memory
- Helps future agents understand WHY things are where they are
- Migration guide for users
- Architectural reference for new contributors

**Anti-Pattern:**
- ❌ "I'll document this later" (you won't)
- ❌ No migration guide for breaking changes

### 8. **Fail-Closed Is Not Just Code, It's Architecture**

**Lesson:** Default to safety at the ARCHITECTURAL level, not just function level.

**What Changed (v46):**
```python
# BEFORE: Optimistic defaults
tri_witness_value = metrics.get("tri_witness", 0.95)  # ← Passes by default

# AFTER: Fail-closed defaults
tri_witness_value = metrics.get("tri_witness", 0.0)   # ← Fails by default
```

**Architectural Implications:**
- Missing evidence = VOID verdict
- No data = system fails safe
- Burden of proof is on the AI, not the user

**Why This Matters:**
- Prevents silent degradation
- Makes gaps in testing obvious (tests fail if metrics missing)
- Forces explicit evidence provision

### 9. **Orthogonality Reduces Cognitive Load**

**Lesson:** 8 clear zones is easier to navigate than 40 unclear folders.

**Before (v45):** "Where does evidence routing live? audit/? evidence/? routing/? validators/?"
**After (v46):** "Evidence routing is in `enforcement/evidence/conflict_routing.py`"

**The 8 Zones:**
```
🧠 agi/          → "Everything about AGI kernel (F1, F2)"
❤️  asi/          → "Everything about ASI kernel (F3-F7)"
👁️  apex/         → "Everything about APEX kernel + governance"
👮 enforcement/  → "Everything about constitutional enforcement"
🔌 integration/  → "Everything about external interfaces"
💾 memory/       → "Everything about state management"
⚙️  system/       → "Everything about system lifecycle"
🌐 mcp/          → "Everything about MCP protocol"
```

**Cognitive Benefit:**
- One question: "What ZONE does this belong to?"
- Clear ownership: Each zone has one responsibility
- Easy onboarding: New contributors know where to look

### 10. **The Human Is the Architect, the Agent Is the Builder**

**Lesson:** Arif designed the 8-folder structure. Claude implemented it. Both roles are essential.

**Division of Labor:**
- **Human (Arif):** Architecture vision, constitutional principles, final authority
- **Agent (Claude):** Systematic execution, testing, documentation, tooling
- **Agent (Antigravity/Gemini):** Audit, governance review, cross-checks

**Why This Works:**
- Human provides strategic direction ("8 orthogonal zones")
- Agent provides tactical execution ("move 331 files, fix 304 imports")
- Human verifies alignment with constitutional principles
- Agent documents the journey for future agents

**Anti-Pattern:**
- ❌ Agent trying to design new architecture without human guidance
- ❌ Human micromanaging every file move
- ❌ No documentation handoff between agents

---

### 🎯 Key Takeaways for Future Refactors

1. **Plan first, code second** (TodoWrite is your friend)
2. **Test after every phase** (catch regressions early)
3. **Use scripts for repetition** (don't edit 300 files manually)
4. **Preserve git history** (`git mv`, not delete+create)
5. **Document during, not after** (capture decisions while fresh)
6. **Incremental commits** (tell a story, enable bisect/revert)
7. **Understand relative imports** (`..` vs `...` matters in nested structures)
8. **Fail-closed by default** (missing data = FAIL, not pass)
9. **Orthogonal zones** (8 clear zones > 40 unclear folders)
10. **Human architect, agent builder** (collaboration, not replacement)

---

**DITEMPA BUKAN DIBERI** — This wisdom was forged through systematic refactoring, not given.

**For Future Agents:** If you're doing a large refactor, read this section FIRST. The patterns here saved ~20 hours of debugging.
