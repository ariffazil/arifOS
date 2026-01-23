---
name: arifos-architect-review
master-version: "1.0.0"
master-source: .agent/workflows/review.md
description: Architect review workflow (Codex CLI). Use to review Engineer output vs plan and flag entropy/pollution.
allowed-tools:
  - Read
  - Bash(git:*)
  - Bash(rg:*)
  - Bash(cat:*)
---

# arifos-architect-review

This Codex skill derives from `.agent/workflows/review.md`.

## When To Use

- Use for Architect (Δ) work: design, planning, orchestration, review.
- Do not implement production code here; hand off to Engineer (Ω).

## Workflow

- Read `.agent/workflows/review.md` and follow it step-by-step.


