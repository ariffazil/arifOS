---
id: governance
title: Governance & Floors
sidebar_position: 4
description: The 13 Constitutional Floors, the 000999 metabolic loop, verdict system, and the 888_HOLD human override.
---

# Governance & Floors

arifOS enforces 13 constitutional floors before governed work is allowed to proceed. The public contract is intentionally smaller than the internal stage graph: public clients use 8 tools, while the kernel still executes the full 000→999 path internally.

## The 13 Constitutional Floors

Hard floors return `VOID`; softer constraints return `PARTIAL` or `SABAR`; high-stakes operations escalate to `888_HOLD`.

## Public Tool Classification

| Public tool | Constitutional focus |
|:---|:---|
| `bootstrap_identity` | F11 onboarding and identity declaration |
| `check_vital` | F4/F5/F7 telemetry and capability reporting |
| `search_reality` | F2/F12 grounding |
| `ingest_evidence` | F2/F11/F12 evidence intake |
| `audit_rules` | Floor inspection and governance review |
| `session_memory` | F4/F7/F13 continuity |
| `arifOS_kernel` | Full governed execution path across 000→999 |
| `open_apex_dashboard` | Observability and human-in-the-loop visibility |

Old names such as `anchor_session`, `reason_mind`, `apex_judge`, and `seal_vault` are no longer the public/main contract. They should be treated as compatibility history or internal/dev-only stages.

## Verdict System

| Verdict | Meaning |
|:--|:--|
| `SEAL` | Approved |
| `PARTIAL` | Approved with constraints |
| `SABAR` | Hold and refine |
| `VOID` | Hard block |
| `888_HOLD` | Human ratification required |

## 888_HOLD

`888_HOLD` is the required human gate for irreversible or high-stakes operations such as production deploys, secret handling, destructive data operations, and mass changes.

## Source of Truth

For the generated public tool table and compatibility map, see [Public Contract](./public-contract).
