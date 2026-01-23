---
name: arifos-architect-handoff
master-version: "1.0.0"
master-source: .agent/workflows/handoff.md
description: Architect handoff workflow (Codex CLI). Use after plan approval to write .antigravity/HANDOFF_FOR_CLAUDE.md.
allowed-tools:
  - Read
  - Bash(cat:*)
  - Bash(mkdir:*)
  - Bash(tee:*)
---

# arifos-architect-handoff

This Codex skill derives from `.agent/workflows/handoff.md`.

## When To Use

- Use for Architect (Δ) work: design, planning, orchestration, review.
- Do not implement production code here; hand off to Engineer (Ω).

## Workflow

- Read `.agent/workflows/handoff.md` and follow it step-by-step.


