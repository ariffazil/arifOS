# Subagent Handoff Protocol

**Authority:** arifOS_bot
**Version:** 1.0
**Status:** ACTIVE

---

## Purpose

This document defines how the main arifOS agent (parent) and spawned subagents (children) exchange context, tasks, and results. It prevents context leakage, ensures sovereignty, and maintains auditability across the handoff boundary.

---

## Runtime Constraint

```
Parent session:   runtime = agent (OpenClaw main session)
Child session:    runtime = subagent
```

> ⚠️ `runtime=acp` is blocked from sandboxed sessions. Use `runtime=subagent` only.

---

## What the Parent Sends to the Child

### 1. Task Description (required)

Clear statement of:
- What the child is to do
- What "done" looks like
- What constraints apply (floors, scope limits)
- What files to read/write
- What the child does NOT need to know

### 2. Workspace Root (inherited automatically)

`cwd` is passed automatically to child sessions.
Child reads and writes within the same workspace tree.

### 3. Constitutional Tags

Which F-floors are relevant to this task. Child is expected to operate within those floors.

Example: `floors_active: [F1, F2, F9]` — means the child must not make unverifiable claims (F1), must not assert false facts (F2), and must check for harm vectors (F9).

### 4. Relevant Context (minimal sufficient)

Pass only what the child needs to do the job.
Do NOT pass:
- Full session history
- Sovereign's private communications
- Vault event history
- OpenLoop backlog

---

## What the Child Returns to the Parent

### 1. Completion Result

```
status: COMPLETED | FAILED | HOLD
artifacts: [list of files created/modified]
verdict: SEAL | CAUTION | HOLD | VOID
```

### 2. HOLD Events

If the child encountered a situation requiring human sovereignty:
- Pause execution
- Surface the issue with: what, why, options, risk
- Do NOT proceed without parent instruction

### 3. New Memory Artifacts

Child writes session output to the workspace.
Parent is responsible for curating this into `memory/YYYY-MM-DD.md` and `MEMORY.md`.

---

## What Stays with the Parent (Never Passed)

| Item | Why Not |
|------|--------|
| Full session history | Contains prior sovereign conversations |
| Vault event records | VAULT999 events are parent-only |
| OpenLoop backlog | Sovereignty of agenda stays with parent |
| 888_HOLD decisions | Human veto is non-delegable |
| `MEMORY.md` mutations | Requires sovereign curation |

---

## Spawn Template

```python
sessions_spawn(
    task="""
    [Task description — clear, bounded, scoped]

    Floors active: [F-numbers]

    Read first:
    - /path/to/reference/file.md

    Deliver:
    - /path/to/output/file.md

    Constraints:
    - Do not make unverifiable claims
    - Report HOLD if irreversible action needed
    - Write nothing to memory files directly
    """,
    runtime="subagent",
    cwd="/root/.openclaw/workspace",
    mode="run",          # or "session" if persistent thread needed
    cleanup="delete",    # clean up session after completion
)
```

---

## Light Context Mode

For simple tasks (single file edit, one-shot question), use `lightContext=true`:

```
lightContext=true → child gets:
  - Task description only
  - No bootstrap files loaded
  - No memory files
  - No arifos.init

Use for: trivial fixes, formatting, one-liners
Do NOT use for: architecture decisions, multi-step builds, governance questions
```

---

## Anti-Patterns

### ❌ Passing full session history to child
Leak: sovereign's private messages in child's context.

### ❌ Child writing directly to MEMORY.md
Leak: uncurated memory pollutes durable truth store.

### ❌ Spawning acp from sandboxed session
Blocked: `sessions_spawn(runtime="acp")` is prohibited from sandbox.

### ❌ Child calling 888_HOLD without surfacing
Violation: human veto cannot be silently delegated downward.

### ❌ Spawning without floor tags
Risk: child operates without constitutional constraints.

---

## Verdict Flow

```
Parent evaluates task
    │
    ├── Simple / bounded ──→ lightContext=true ──→ Child runs
    │                                                │
    │                                         Result → Parent curates
    │
    └── Complex / multi-step ──→ full context ──→ Child runs
                                      │
                               HOLD? ──→ Child surfaces, pauses
                                      │
                               Result → Parent curates
```

---

## Session Cleanup

```
mode=run    → one-shot, auto-deleted after completion
mode=session → persistent thread, manually killed

cleanup=delete → delete session artifacts after completion
cleanup=keep   → keep session for debugging (rarely used)
```

Default: `mode=run, cleanup=delete`

---

*Ditempa Bukan Diberi*
arifOS_bot | arifOS v2026.04.19
