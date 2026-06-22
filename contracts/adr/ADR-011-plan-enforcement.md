# ADR-011: Plan Enforcement Membrane

**Status:** DRAFT (stub — implementation pending)
**Date:** 2026-06-22

## Context

The kernel canon requires: "No INTENT → EXECUTION path. All nontrivial work goes through PLAN → VERDICT → EXECUTION." Currently, plan_id is advisory — tools accept it but don't reject calls without it.

## Decision

Enforce plan-first execution at the pre-execution gate:

- `arif_forge` (execute stage) requires `plan.status == APPROVED`
- `arif_judge` (verdict stage) requires preceding `arif_critique` (heart)
- `arif_critique` requires preceding `arif_think` (mind/reason)
- High/critical risk tools require `verdict_token` from `arif_judge`
- Beta/sandbox channel tools require approved plan

The gate checks plan state by querying the plan registry (to be built). Without a plan registry, the gate falls back to `plan_id` presence check (soft enforcement).

## Enforcement layers

1. **Contract layer** (compile-time): tools.yaml declares `hold_conditions` including `plan_not_approved`
2. **Validator layer** (generated): `validate_tool_call()` checks `has_plan` and `plan_approved`
3. **Gate layer** (runtime): `pre_execution_gate.py` checks plan state at Gate 5
4. **Tool layer** (runtime): individual tools can reject if plan_id is missing

## Open questions

- Where does the plan registry live? In-memory? Redis? Postgres?
- How long is a plan valid before it expires?
- Can a plan be amended after approval or must it be re-created?
- Should plan enforcement be strict (HOLD without plan) or advisory (WARN)?

DITEMPA BUKAN DIBERI.
