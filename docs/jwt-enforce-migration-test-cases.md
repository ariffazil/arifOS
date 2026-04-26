# Golden End-to-End Test: JWT Observe → Enforce Migration

**Document type:** migration gate
**Author:** arifOS_bot / Federation v2
**Date:** 2026-04-26
**Phase:** Phase 1 complete → Phase 2 enforce transition

---

## Test Philosophy

> "Red-team discipline: test the break before you need it to hold."
> Ditempa Bukan Diberi.

We test the boundary, not the happy path. Every test case probes a failure mode.
The goal is to confirm that `enforce` mode **blocks what it should** and **passes what it should**.

---

## Vault Seal Contract (mandatory fields)

Every sealed entry must carry these 10 fields:

| Field | Source | Notes |
|-------|--------|-------|
| `seal_id` | System | UUID, generated at write time |
| `actor_id` | Caller | Who initiated the write |
| `jwt_sub` | JWT `sub` claim | Must match `actor_id` — **this is the core contract** |
| `tool_name` | Caller | Which tool performed the write |
| `tool_version` | Caller | From `tool_versions.json` |
| `claim_state` | Caller | From `claim_tag_registry` (37 tags) |
| `escalation_tier` | System | 0–3, from federation manifest |
| `input_hash` | System | Hash of input payload |
| `output_hash` | System | Hash of output/result |
| `timestamp_utc` | System | ISO-8601 UTC |

---

## JWT Enforcement Policy

**Observe mode (current):** Log violations. Do not block.
**Enforce mode (target):** Block missing/invalid JWT. Reject `actor_id` mismatch. Block service-role writes.

**Internal writers:** Valid short-lived JWT with `arifOS-internal` issuer.
**External clients:** Valid Supabase OAuth JWT with verified `sub` claim.
**Actor ID policy:** `jwt sub` claim MUST match `actor_id` in payload.

---

## Test Case Matrix

### Tier 0 — No JWT (anonymous)

| Test ID | Case | Expected (observe) | Expected (enforce) |
|---------|------|--------------------|--------------------|
| T0-01 | Call `vault_ledger` with no `Authorization` header | `ERROR` log — missing token | `403 Forbidden` — blocked |
| T0-02 | Call with `Authorization: Bearer invalidtoken` | `ERROR` log — malformed JWT | `401 Unauthorized` — rejected |
| T0-03 | Call with `Authorization: Bearer expired.jwt.token` | `ERROR` log — expired token | `401 Unauthorized` — rejected |

### Tier 1 — JWT present but invalid contract

| Test ID | Case | Expected (observe) | Expected (enforce) |
|---------|------|--------------------|--------------------|
| T1-01 | Valid JWT but `jwt_sub != actor_id` | `ERROR` log — actor mismatch | `403 Forbidden` — mismatch blocked |
| T1-02 | Valid JWT, correct sub, but missing `tool_version` | `ERROR` log — missing required field | `400 Bad Request` — missing field |
| T1-03 | Valid JWT, correct sub, `escalation_tier` out of range | `ERROR` log — invalid tier | `400 Bad Request` — invalid tier |
| T1-04 | Valid JWT, `claim_state` not in registry | `ERROR` log — unknown claim tag | `400 Bad Request` — unknown tag |

### Tier 2 — JWT valid, contract valid, but writer class violation

| Test ID | Case | Expected (observe) | Expected (enforce) |
|---------|------|--------------------|--------------------|
| T2-01 | Internal service uses `Supabase` external JWT | `WARN` log — wrong issuer for writer class | `403 Forbidden` — wrong issuer |
| T2-02 | External client uses `arifOS-internal` JWT | `WARN` log — wrong issuer for client class | `403 Forbidden` — wrong issuer |
| T2-03 | `actor_id` is `system`, not a real user UUID | `ERROR` log — system actor on write | `403 Forbidden` — system actor blocked on write |

### Tier 3 — Valid flow (should pass both modes)

| Test ID | Case | Expected (observe) | Expected (enforce) |
|---------|------|--------------------|--------------------|
| T3-01 | Internal service writes with valid internal JWT, correct `actor_id == jwt_sub` | `OK` log, entry sealed | `200 OK`, entry sealed |
| T3-02 | External read-only query with valid Supabase OAuth | `OK` log, result returned | `200 OK`, result returned |
| T3-03 | All 10 required fields present, correct types, `claim_state` in registry | `OK` log, entry sealed | `200 OK`, entry sealed |
| T3-04 | `seal_id` is a valid UUID v4 | `OK` log | `200 OK` |
| T3-05 | `timestamp_utc` is valid ISO-8601 | `OK` log | `200 OK` |
| T3-06 | `input_hash` and `output_hash` are valid SHA-256 | `OK` log | `200 OK` |

### Boundary / Edge Cases

| Test ID | Case | Expected (observe) | Expected (enforce) |
|---------|------|--------------------|--------------------|
| E-01 | `JWT_ENFORCE_MODE` env var is unset → defaults to `observe` | Logs warning, runs observe | — |
| E-02 | `JWT_ENFORCE_MODE=invalidvalue` | `WARN` — falls back to `observe` | `WARN` — falls back to `observe` |
| E-03 | `vault_ledger seal` called twice with same `seal_id` | `WARN` duplicate seal_id | `409 Conflict` — duplicate rejected |
| E-04 | Payload truncated mid-read | `ERROR` — incomplete write | `400 Bad Request` — incomplete |
| E-05 | `X-Forwarded-For` spoofed actor_id | `ERROR` — actor_id from payload, not header | `403 Forbidden` — header cannot set actor |

---

## Migration Checklist

Before flipping to `enforce`, confirm:

- [ ] All internal writers have valid short-lived `arifOS-internal` JWTs
- [ ] All external clients have valid Supabase OAuth tokens
- [ ] 24h observe telemetry shows **zero** `T0-01` violations (or they're all authorized + logged)
- [ ] 24h observe telemetry shows **zero** `T1-01` violations (all `jwt_sub == actor_id`)
- [ ] `vault_seal_contract` required fields enforced at the tool layer
- [ ] `claim_tag_registry` enforced at seal time
- [ ] Health endpoints respond correctly under load

---

## Flip Command

```bash
# In /root/compose/.env or container environment
JWT_ENFORCE_MODE=enforce
```

Then restart: `docker compose restart arifosmcp`

---

## Recovery (if enforce breaks something)

```bash
# Roll back to observe
JWT_ENFORCE_MODE=observe
docker compose restart arifosmcp
```

> **Note:** Observe mode does NOT block. If violations appear in logs during observe, they will become blocking errors in enforce. Treat observe telemetry as your pre-flight checklist.

---

*Canonical source: `federation_manifest.json` commit `395f3e36`
*Federation Constitution v2 — arifOS Federation*
