# ADR-010: Channel Policy

**Status:** DRAFT (stub — code shape not yet stable)
**Date:** 2026-06-22

## Context

Tools operate in three channels: `stable`, `beta`, `sandbox`. The channel determines plan requirements, blast radius caps, and floor relaxation rules.

## Decision

| Channel | Plan required | Max blast radius | Floor relaxation | External effects |
|---------|--------------|------------------|------------------|-----------------|
| `stable` | No (unless high/critical risk) | medium | Never | Allowed |
| `beta` | Yes | civilizational | Never | Allowed with sovereign ack |
| `sandbox` | Yes | low | Never | Blocked |

**Beta never relaxes Floors.** This is constitutional law, not policy. Beta only changes trust posture and default HOLD behavior.

## Enforcement

- Compiler validates: beta must have `authority_required=sovereign` OR `hold_conditions`
- Compiler validates: sandbox must be `reversible`
- `contracts/validators.py` (generated) includes channel check in `validate_tool_call()`
- Pre-execution gate checks channel policy at Gate 4

## Open questions

- Should beta tools require explicit sovereign approval per-invocation or per-session?
- Should sandbox tools be allowed to write to isolated scratch directories?
- Channel override records: should they be IncidentRecords or OverrideRecords?

DITEMPA BUKAN DIBERI.
