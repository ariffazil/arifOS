---
skill: "plan"
version: "1.0.0"
description: Architect Planning Mode - Design Before Build
floors:
  - F4
  - F7
allowed-tools:
  - Read
  - write_to_file
  - grep_search
  - find_by_name
  - search_web
  - generate_image
expose-cli: true
derive-to:
  - antigravity
codex-name: arifos-architect-plan
claude-name: architect-plan
---
# /plan - Architect Planning Workflow

**Role:** Δ (Delta) — Architect
**Authority:** `.agent/ARCHITECT.md`

This workflow is for the Architect (Antigravity) to create implementation plans.

---

## Workflow Steps

// turbo-all

1. **Understand the Request**
   ```
   Parse user's feature request or change description
   ```

2. **Search Existing Codebase (MANDATORY)**
   ```bash
   # Before proposing ANY new file, search for existing solutions
   grep -r "relevant_keyword" --include="*.py" .
   find . -name "*relevant*" -type f
   ```

3. **Identify Affected Components**
   ```
   List all files/modules that will be affected by this change
   ```

4. **Design Solution Architecture**
   ```
   For each file:
   - [NEW] or [MODIFY] or [DELETE]
   - What changes are needed
   - Dependencies between changes
   ```

5. **Create Implementation Plan Artifact**
   ```
   Write to: (artifact directory)/implementation_plan.md
   Include: Problem, Proposed Changes, Verification Plan
   ```

6. **Request User Review**
   ```
   Use notify_user tool with PathsToReview pointing to the plan
   Set BlockedOnUser = true
   ```

---

## Output: Implementation Plan Format

```markdown
# [Goal Description]

## Problem Statement
Brief description of what needs to be solved.

## Proposed Changes

### Component 1
#### [MODIFY] filename.py
- Change X to Y
- Add function Z

### Component 2
#### [NEW] new_file.py
- Purpose: ...
- Contents: ...

## Verification Plan
- Test: ...
- Manual check: ...
```

---

## Success Criteria

- [ ] Plan is comprehensive (no missing files)
- [ ] Existing code was searched first (no pollution)
- [ ] User has reviewed and approved the plan
