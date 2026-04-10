---
type: Concept
tier: 20_RUNTIME
strand:
- architecture
audience:
- engineers
difficulty: advanced
prerequisites:
- Concept_Architecture
tags:
- architecture
- runtime
- audit
- ledger
- vault
sources:
- arifosmcp-vault999-architecture-audit-2026-04-08.md
last_sync: '2026-04-10'
confidence: 0.9
---

# Concept: Vault999 Architecture

## Definition

**Vault999 Architecture** is the stage-`999` sealing and audit subsystem in `arifosmcp`. It records governed decisions, chains them with hash-linked integrity data, mirrors or persists them across available backends, and exposes the evidence needed for later verification. #audit #ledger #runtime

## Observable Components

| Component | Function | Evidence |
| --- | --- | --- |
| `vault999.jsonl` | Compact ledger entries with verdict and chain payload | checked-in `VAULT999/` file |
| `SEALED_EVENTS.jsonl` | Rich event log with stage, actor, payload, and chain hashes | checked-in `VAULT999/` file |
| `SEAL_CHAIN.txt` | Chain-head snapshot metadata | checked-in `VAULT999/` file |
| `outcomes.jsonl` | Post-verdict calibration and outcome tracking | checked-in `VAULT999/` file |
| `runtime/vault_postgres.py` | PostgreSQL-led dual-write implementation | runtime audit source |
| `runtime/bridge.py` | Redis-first access path with file fallback | runtime audit source |

## Storage Model

The audited code shows Vault999 as a **multi-backend architecture**:

1. A runtime path that prefers Redis-backed vault access when available.
2. A PostgreSQL vault store that describes itself as the primary source of truth with filesystem mirroring.
3. A checked-in filesystem ledger under `arifosmcp/VAULT999/` that provides directly inspectable audit evidence.

This is not a bug by itself, but it is a real architectural drift that matters for F2 and F11.

## Seal Mechanics

The runtime sources show a common sealing pattern:

- Create an event payload.
- Compute a leaf hash from canonical fields.
- Read the previous chain hash.
- Compute a new chain hash from `prev_hash + merkle_leaf`.
- Persist the event and update the mirrored chain artifacts.

That pattern matches the filesystem evidence in `SEALED_EVENTS.jsonl`, `SEAL_CHAIN.txt`, and `vault999.jsonl`.

## Constitutional Position

`seal_999` is described as the immutable vault and Merkle commit engine, with a hold condition if sealing happens without prior `apex_888 judge=SEAL`. That makes Vault999 both a storage subsystem and a governance boundary, not just an append-only log.

## Contradictions and Drift

> [!NOTE]
> F9 contradiction surfaced: backend authority differs by file.

- `runtime/bridge.py` implies **Redis-primary** with file fallback.
- `runtime/vault_postgres.py` implies **PostgreSQL-primary** with file mirror.
- The repository snapshot proves **filesystem persistence is active** regardless of which online backend is preferred.

The most defensible wiki position is that Vault999 is a **federated sealing architecture** whose backend preference is still settling.

## Relation to Other Pages

- `[[Concept_Metabolic_Pipeline]]` explains how requests arrive at the seal stage.
- `[[Changelog]]` and `[[Roadmap]]` provide broader program context, but the vault mechanics here are grounded in runtime code and checked-in ledger artifacts.

## Audit Summary

Vault999 should be understood as the full stage-`999` audit system: verdict-gated seal logic, chain integrity material, and post-outcome calibration files. The current repo presents a stable filesystem evidence layer, with some unresolved drift about whether Redis or PostgreSQL is the canonical online backend.
