---
skill: "handoff"
version: "1.0.0"
description: Handoff Approved Plan to Engineer
floors:
  - F4
  - F3
allowed-tools:
  - write_to_file
  - Read
expose-cli: true
derive-to:
  - antigravity
codex-name: arifos-architect-handoff
claude-name: architect-handoff
---
# /handoff - Architect Handoff Workflow

**Role:** Δ (Delta) — Architect
**Authority:** `.agent/ARCHITECT.md`

This workflow creates a handoff document for Claude (Engineer) to implement.

---

## When to Use

After user approves the implementation plan, run this workflow to:
1. Summarize the plan in Engineer-friendly format
2. Create specific task list
3. Write handoff file

---

## Workflow Steps

// turbo-all

1. **Verify Plan is Approved**
   ```
   Confirm user has approved the implementation_plan.md
   ```

2. **Create Handoff Directory (if needed)**
   ```bash
   mkdir -p .antigravity
   ```

3. **Write Handoff File**
   Create `.antigravity/HANDOFF_FOR_CLAUDE.md`:

   ```markdown
   # Engineer Handoff: [Task Name]

   **From:** Δ (Delta) — Antigravity Architect
   **To:** Ω (Omega) — Claude Engineer
   **Date:** [current date]

   ---

   ## Mission
   [One sentence summary of what to build]

   ## Approved Plan
   See: [link to implementation_plan.md]

   ## Files to Create
   - `path/to/new_file.py` — Purpose: ...

   ## Files to Modify
   - `path/to/existing.py` — Change: ...

   ## Tests to Write
   - `tests/test_feature.py` — Test: ...

   ## Success Criteria
   - [ ] Criterion 1
   - [ ] Criterion 2
   - [ ] All tests pass

   ## Architectural Notes
   - Warning: ...
   - Constraint: ...

   ## When Done
   Create `.antigravity/DONE_FOR_ARCHITECT.md` and tell user.
   ```

4. **Notify User**
   ```
   Tell user: "Handoff ready. Start Claude and say:
   'Read .antigravity/HANDOFF_FOR_CLAUDE.md and implement the plan.'"
   ```

---

## Success Criteria

- [ ] Handoff file created at `.antigravity/HANDOFF_FOR_CLAUDE.md`
- [ ] All planned files listed with clear instructions
- [ ] Success criteria defined
- [ ] User knows how to proceed
