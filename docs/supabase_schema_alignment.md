# Supabase Schema Alignment — P3-01

**Audit status:** `FAIL — schema drift found`

**Audit revision:** `bc44f8843f8ba743216c4ff13ccef8c2138ebc46` (`main`)

**Audit timestamp:** `2026-07-15T04:40:27Z`

**Bug report:** [#584 — [BUG] Supabase schema drift](https://github.com/ariffazil/arifos/issues/584) (`supabase-alignment`)

## Scope and method

This is a source audit of Supabase write paths reachable from `/root/arifOS/arifosmcp/`, plus the shared VAULT999 client used by `core/shared/governed_tool.py`. The audit searched for Supabase client construction, PostgREST writes, and `arifOS.supabase_adapter` calls, then compared each VAULT999 seal payload with the P3-01 contract below.

No Supabase write, VAULT999 seal, or schema migration was executed. A live `GET /health` probe returned `status: healthy`; that health response does not prove that the Supabase seal adapter is callable or schema-aligned. The requested `git pull --rebase` could not run because the pre-existing worktree contained unstaged changes; those changes were not modified.

## Expected VAULT999 Supabase event contract

Each seal event must emit these top-level fields:

```json
{
  "session_id": "string",
  "tool_name": "string",
  "stage": 999,
  "verdict": "SEAL|HOLD|VOID|SABAR",
  "floor_compliance": {
    "F1": true,
    "F2": true,
    "F3": true,
    "F4": true,
    "F5": true,
    "F6": true,
    "F7": true,
    "F8": true,
    "F9": true,
    "F10": true,
    "F11": true,
    "F12": true,
    "F13": true
  },
  "epistemic_snapshot": {
    "confidence": 0.0,
    "uncertainty_band": 0.0
  },
  "vault_seq": 0,
  "timestamp_utc": "2026-01-01T00:00:00+00:00",
  "actor_hash": "<HMAC-SHA256; never plaintext>"
}
```

`stage` is an integer in the inclusive range `0..999`; `999` is the VAULT999 stage. `verdict` is an enum, not an unconstrained string. `floor_compliance` must be a complete `F1..F13` boolean map. `actor_hash` must be an HMAC-derived identity reference; an actor ID, name, or JWT subject is not a substitute.

## Supabase write inventory

| Source | Table / target | Operation | Classification | Alignment |
|---|---|---|---|---|
| `arifosmcp/runtime/vault_postgres.py:122` | `arifosmcp_vault_seals` | `.insert(data)` | VAULT999 seal mirror | **FAIL** |
| `core/shared/vault_client.py:60` | `arifosmcp_vault_seals` | `.insert(record)` | Shared VAULT999 seal client | **FAIL** |
| `arifosmcp/runtime/tools.py:17968-17991` | `arifOS.supabase_adapter.seal_vault999` | async adapter call | Canonical `arif_vault_seal` Supabase hook | **UNVERIFIABLE / FAIL CLOSED** |
| `arifosmcp/runtime/tools.py:16525-16554` | `arifOS.supabase_adapter.record_judge_verdict` | async adapter call | Judge receipt, not itself a VAULT999 seal | Adapter unavailable in checkout |
| `arifosmcp/runtime/kernel.py:545-610` | `arifOS.supabase_adapter.record_tool_call` | async adapter call | Tool-call receipt, not a VAULT999 seal | Adapter unavailable in checkout |
| `arifosmcp/runtime/ingress_middleware.py:287-329` | `arifOS.supabase_adapter.record_tool_call` | async adapter call | Tool-call receipt, not a VAULT999 seal | Adapter unavailable in checkout |
| `arifosmcp/runtime/supabase_receipts.py:32,53` | `arifosmcp_tool_calls` | HTTP `POST` | Tool-call receipt, not a VAULT999 seal | N/A to seal contract |
| `arifosmcp/runtime/vault_postgres.py:388` | `arifosmcp_well_states` | `.upsert(...)` | WELL state, not a VAULT999 seal | N/A to seal contract |
| `arifosmcp/runtime/vault_postgres.py:472` | `arifosmcp_sessions` | `.insert(...)` | Session row, not a VAULT999 seal | N/A to seal contract |
| `arifosmcp/runtime/vault_postgres.py:483` | `arifosmcp_sessions` | `.update(...)` | Session row, not a VAULT999 seal | N/A to seal contract |
| `arifosmcp/runtime/vault_postgres.py:510` | `arifosmcp_tool_calls` | `.insert(...)` | Tool-call receipt, not a VAULT999 seal | N/A to seal contract |
| `arifosmcp/runtime/vault_postgres.py:534` | `arifosmcp_canon_records` | `.insert(...)` | Canon record, not a VAULT999 seal | N/A to seal contract |
| `arifosmcp/runtime/vault_postgres.py:575` | `arifosmcp_agent_telemetry` | `.insert(...)` | Telemetry, not a VAULT999 seal | N/A to seal contract |
| `arifosmcp/core/kernel_state.py:126` | `arifosmcp_kernel_state` | `.upsert(...)` | Kernel health state, not a VAULT999 seal | N/A to seal contract |

The `supabase_receipts.py` and other operational rows are intentionally not scored against the VAULT999 seal contract. They are recorded here to make the Supabase write inventory complete.

## Seal emitter field audit

### `arifosmcp/runtime/vault_postgres.py:107-122`

`SupabaseVaultStore.seal()` emits:

```python
{
    "seal_id": event.event_id,
    "agent_id": event.actor_id,
    "action": event.event_type,
    "payload": event.payload,
    "confidence": 1.0,
    "epoch": event.sealed_at.isoformat(),
    "prev_hash": event.prev_hash,
    "chain_hash": event.chain_hash,
    "auth_lineage": event.auth_lineage,
}
```

Findings:

- **Missing:** top-level `session_id`, `tool_name`, `stage`, `verdict`, `floor_compliance`, `epistemic_snapshot`, `vault_seq`, `timestamp_utc`, and `actor_hash`.
- **Mis-typed / unconstrained:** `VaultEvent.stage` is declared as `str`, and `VaultEvent.verdict` is an unconstrained `str`. `event_type` is emitted as `action`, not `tool_name`.
- **Identity exposure:** `event.actor_id` is emitted as plaintext `agent_id`. `auth_lineage` is not an HMAC actor hash.
- **Partial but non-compliant:** scalar `confidence` is not the required `epistemic_snapshot` object; `epoch` is an ISO-8601 value under the wrong field name; `payload` may contain nested context but does not satisfy required top-level fields.
- **Delivery risk:** `VaultManager.seal()` schedules this write fire-and-forget at `:261-268`, and returns success based on the local PostgreSQL write. A Supabase insert failure therefore does not fail the seal result.

### `core/shared/vault_client.py:44-60`

`VaultClient.seal()` emits:

```python
{
    "organ": self.organ_id,
    "tool_name": tool_name,
    "session_id": session_id,
    "actor_id": actor_id,
    "verdict": verdict,
    "payload": payload,
    "law_results": law_results,
    "g_star": g_star,
    "prev_hash": prev_hash,
    "timestamp": datetime.utcnow().isoformat(),
    "hash": ...,
}
```

Findings:

- **Present:** `session_id`, `tool_name`, and `verdict` (but without enum validation).
- **Missing:** `stage`, `floor_compliance`, `epistemic_snapshot`, `vault_seq`, `timestamp_utc`, and `actor_hash`.
- **Mis-typed / wrong shape:** `law_results` is not a `F1..F13 -> bool` map; `timestamp` is a naive UTC string under the wrong field name; `actor_id` is plaintext rather than HMAC-hashed identity.
- **Hash mismatch:** `hash` is a Merkle hash of the emitted record, not the required HMAC actor identity.

### Canonical `arif_vault_seal` hook

The successful `arif_vault_seal` path calls `seal_vault999(...)` from `arifOS.supabase_adapter` at `arifosmcp/runtime/tools.py:17973`. There is no `arifOS/supabase_adapter.py` in this checkout; importing `arifOS.supabase_adapter` from the repository fails with `ModuleNotFoundError`. The call is inside a broad exception handler at `:17992-17993`, so the kernel can return its local seal result while the Supabase event is absent. The adapter's emitted schema cannot be verified from this source tree and is therefore not an alignment pass.

## Migration alignment

`supabase/migrations/20260417100348_initial_arifosmcp_schema.sql:6-17` defines `arifosmcp_vault_seals` with `id`, `record_id`, `seal_id`, `prev_hash`, `agent_id`, `action`, `payload`, `confidence`, `epoch`, and `created_at`.

The migration does **not** define the required `tool_name`, `stage`, `verdict`, `floor_compliance`, `epistemic_snapshot`, `vault_seq`, `timestamp_utc`, or `actor_hash` columns. The later AAA namespace migration (`20260602000000_aaa_namespace_receipt_fields.sql:44-58`) adds namespace metadata only; it does not close these contract gaps. No migration in this checkout adds the missing seal-event fields.

This report does not modify any migration or live Supabase schema. The schema decision is left for human review under issue #584.

## Verdict

`VOID` for the alignment claim: the repository does not demonstrate that every VAULT999 seal event writes the expected Supabase record. The two inspectable seal emitters fail the required contract, the canonical adapter import is absent from this checkout, and the declared `arifosmcp_vault_seals` migration lacks the required columns.

This is an audit finding, not a proposed schema patch. Remediation should first select one canonical seal adapter and table contract, then add typed emission and tests for all required fields, including HMAC actor hashing and explicit failure handling for Supabase write failures.
