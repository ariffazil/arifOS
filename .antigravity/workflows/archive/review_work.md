---
skill: "review"
version: "1.0.0"
description: Architect Review - Validate Engineer Work
floors:
  - F4
  - F8
allowed-tools:
  - Read
  - view_file
  - grep_search
  - list_dir
expose-cli: true
derive-to:
  - antigravity
codex-name: arifos-architect-review
claude-name: architect-review
---
# /review - Architect Review Workflow

**Role:** Δ (Delta) — Architect
**Authority:** `.agent/ARCHITECT.md`

This workflow is for the Architect to review Engineer's completed work.

---

## When to Use

After Claude (Engineer) has completed implementation, run this workflow to:
1. Verify the implementation matches the plan
2. Check for architectural compliance
3. Identify any F4 violations (entropy increase)

---

## Workflow Steps

// turbo-all

1. **Load the Original Plan**
   ```
   Read the implementation_plan.md that was approved
   ```

2. **Review Changes Made**
   ```bash
   git diff main..HEAD --stat
   git log --oneline -10
   ```

3. **Verify Each Planned Change**
   ```
   For each file in the plan:
   - Was it created/modified as specified?
   - Does it match the architectural intent?
   ```

4. **Check for Entropy Violations (F4)**
   ```
   - Were any unexpected files created?
   - Is there duplicate code?
   - Is the solution more complex than necessary?
   ```

5. **Create Review Notes**
   ```
   Write findings to walkthrough.md or EUREKA notes
   ```

6. **Decision**
   - ✅ APPROVED: Ready for Auditor (Codex) review
   - ⚠️ CHANGES REQUESTED: Tell Engineer what to fix
   - 🚫 VOID: Architectural violation, needs replanning

---

## Output: Review Decision

```markdown
# Architect Review: [Task Name]

## Status: [APPROVED / CHANGES REQUESTED / VOID]

## Plan Compliance
- [x] All planned files created
- [x] Changes match architectural intent
- [ ] No entropy violations

## Issues Found
- (list any issues)

## Next Steps
- (what happens next)
```
