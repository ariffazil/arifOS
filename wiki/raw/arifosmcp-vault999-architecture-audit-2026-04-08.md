# arifosmcp VAULT999 Architecture Audit

Audit date: 2026-04-08
Scope: `arifOS/arifosmcp/VAULT999/` and runtime vault implementations

## Source excerpts

- `arifosmcp/README.md`
  - Describes `vault_ledger` as stage `999_SEAL`, the immutable ledger, and Merkle chain.
  - States that `VAULT999` stores governance decisions and exposes verification through `verify_vault_ledger`.

- `arifosmcp/constitutional_map.py`
  - Defines `seal_999` as the immutable vault and Merkle commit engine.
  - States that sealing without prior `apex_888 judge=SEAL` should hold.

- `arifosmcp/runtime/bridge.py`
  - Sets `DEFAULT_VAULT_PATH = Path(__file__).parents[2] / "VAULT999" / "vault999.jsonl"`.
  - Prefers Redis-backed vault storage when available, with file initialization as fallback.

- `arifosmcp/runtime/vault_postgres.py`
  - Declares PostgreSQL-backed `VAULT999` as the primary source of truth with filesystem mirror.
  - Uses `SEALED_EVENTS.jsonl` and `SEAL_CHAIN.txt` as mirror files under `VAULT999_PATH`.
  - Computes `merkle_leaf`, chains it with `prev_hash`, and persists `chain_hash`.

- `arifosmcp/VAULT999/vault999.jsonl`
  - Contains JSONL records with `ledger_id`, `summary`, `verdict`, `seal_hash`, and nested `chain` metadata.

- `arifosmcp/VAULT999/SEALED_EVENTS.jsonl`
  - Contains event records with `event_id`, `stage`, `verdict`, `payload`, `merkle_leaf`, `prev_hash`, and `chain_hash`.

- `arifosmcp/VAULT999/SEAL_CHAIN.txt`
  - Stores a top-level chain hash plus event metadata.

- `arifosmcp/VAULT999/outcomes.jsonl`
  - Tracks post-decision outcomes, including `SUCCESS`, `FAILURE`, `harm_detected`, and `calibration_delta`.

## Audit findings

1. `VAULT999` is implemented as a multi-backend audit system, not just a single file ledger.
2. At least three storage stories are present in code:
   - Redis-first runtime access in `runtime/bridge.py`.
   - PostgreSQL canonical store with filesystem mirror in `runtime/vault_postgres.py`.
   - Direct filesystem artifacts already populated in `arifosmcp/VAULT999/`.
3. The file-backed layer itself is segmented by function.
   - `vault999.jsonl` stores compact ledger records.
   - `SEALED_EVENTS.jsonl` stores richer event logs.
   - `SEAL_CHAIN.txt` stores chain-head metadata.
   - `outcomes.jsonl` stores calibration and real-world result tracking.

## Contradictions to surface

- Backend authority is not perfectly unified across sources.
  - `runtime/bridge.py` frames Redis as the primary backend with file fallback.
  - `runtime/vault_postgres.py` frames PostgreSQL as the primary source of truth with filesystem mirror.
  - The checked-in `VAULT999/` directory proves active filesystem persistence regardless of the preferred online backend.
- Terminology varies between `vault_ledger`, `vault_seal`, `seal_999`, and `VAULT999`, even when all point to the same stage-band.

## Working interpretation

Use `Vault999 Architecture` to mean the full sealing and audit subsystem at stage `999`, consisting of verdict-gated event creation, hash chaining, backend persistence, and later verification or calibration. Treat the checked-in filesystem artifacts as the most directly inspectable evidence, while acknowledging backend drift between Redis-first and PostgreSQL-first code paths.
