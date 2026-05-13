---
id: advanced-roadmap
title: Advanced Roadmap
sidebar_position: 50
description: Horizon 2/3 architecture concepts (Research/Planned) that are not part of the current mainline runtime enforcement path.
---

# Advanced Roadmap (Horizon 2/3)

This page isolates advanced architecture concepts that may appear in research notes or older documents.
They are intentionally separated from the operator docs because they are not guaranteed to be active runtime
enforcement in the current `main` branch serving path.

Status tags used here:

- `[Status: Research]` - explored, prototypes may exist, not enforced by default
- `[Status: Planned]` - design intent only

---

## Concrete-ML / FHE / zkPC proofs

[Status: Research]

Goal: cryptographically verifiable enforcement of F9 Anti-Hantu (and related floors) without exposing raw prompts.

Reality today:

- Mainline docs treat zkPC as a governance concept and (where present) an audit receipt model.
- Do not assume Fully Homomorphic Encryption circuits or zero-knowledge compliance proofs are enforced in production by default.

---

## Postgres.ai Database Lab Engine (DLE) thin-clone rollbacks

[Status: Planned]

Goal: zero-cost rollback sandboxes to strengthen F1 Amanah for high-stakes database operations.

Reality today:

- Postgres is supported and recommended for durable VAULT999 persistence.
- Do not assume ZFS thin clones or DLE orchestration is integrated into the default pipeline.

---

## AutoGen Trinity consensus

[Status: Research]

Goal: multi-agent deliberation loops for capability exploration, with APEX veto preserved.

Reality today:

- arifOS architecture documents reference multi-engine separation (AGI/ASI/APEX) and tri-witness checks.
- Do not treat AutoGen as a required runtime dependency or an always-on enforcement component.

---

## Prefect ControlFlow / long-running workflows

[Status: Planned]

Goal: deterministic orchestration and human-in-the-loop pausing for `888_HOLD` and long-running governance flows.

Reality today:

- `888_HOLD` is a documented governance state.
- Do not assume ControlFlow orchestration is present unless your deployment explicitly includes it.
