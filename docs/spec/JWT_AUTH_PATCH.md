# JWT Constitutional Auth Patch — Phase 1 Spec

> **Document Type:** Normative security contract
> **Status:** Draft — pending sovereign review
> **Scope:** arifOS VAULT write path + federation identity boundary
> **Severity:** Red-zone — blocks all other governance hardening
> **Motto:** *Identity before Governance. Governance before Epistemics.*

---

## 1. Problem Statement

Current state:
- `validate_token()` returns `True` unconditionally
- `BearerAuthMiddleware` is a disabled stub
- Vault writes use `SUPABASE_SERVICE_ROLE_KEY` — direct service-role bypass
- `actor_id` is header-derived (`x-arifos-user-id`, `x-arifos-sovereign-sig`) — unverified plaintext; these headers MUST be ignored post-patch
- No JWT signature verification in runtime

Impact: Anyone with the service key can write a SEAL. Constitutional authority is not cryptographically bound to identity.

---

## 2. Trust Source

**Primary issuer:** Supabase Auth (production)
**Self-issued fallback:** `arifos-internal` — HMAC-signed tokens for background jobs only (see §7)

`TRUSTED_ISSUERS = ["https://<project>.supabase.co", "arifos-internal"]`

Rotation: `kid` in JWT header + JWKS endpoint polling (not manual key strings).

---

## 3. Required Claims

Every JWT presented to arifOS MUST contain:

| Claim | Rule |
|-------|------|
| `sub` | Sovereign actor_id. Immutable. Enforced equality with `actor_id` param. |
| `iss` | Must be in `TRUSTED_ISSUERS`. |
| `aud` | Must equal `"arifOS"` or `"arifosmcp"`. |
| `exp` | Must be in the future. Reject with 401 if expired. |
| `iat` | Must be in the past. Reject if future-dated (> 60 s clock skew allowed). |
| `kid` | Key ID for JWKS lookup. Required for issuer rotation. |

Optional (enriched but not required):

| Claim | Use |
|-------|-----|
| `role` | `"sovereign"`, `"operator"`, `"agent"` — gates tool access tiers post-Phase-1 |
| `scope` | Space-delimited — `"vault:write", "vault:read", "judge:deliberate"` |

---

## 4. Enforcement Invariants

These MUST hold on every request that reaches a constitutional boundary (vault write, judge deliberate, forge execute):

```python
# Invariant 1: JWT signature cryptographically valid
assert jwt_signature_valid(token, jwks[header.kid])

# Invariant 2: Temporal validity
assert now() < claims.exp
assert claims.iat < now() + CLOCK_SKEW_MAX

# Invariant 3: Issuer trust
assert claims.iss in TRUSTED_ISSUERS

# Invariant 4: Audience match
assert claims.aud in ["arifOS", "arifosmcp"]

# Invariant 5: Identity binding
assert actor_id == claims.sub

# Invariant 6: No service-role fallback
assert auth_method != "service_role"
```

**Violation of any invariant → 401, non-sealed log entry, request terminated.**

No fallback. No env override. No `if DEBUG: pass`.

---

## 5. Vault Write Rule

Vault write (`_arif_vault_seal`, `SupabaseVaultClient.write`, `PostgresVaultClient.write`) is allowed **only if**:

```
request.jwt_verified == True
AND actor_id == jwt.sub
AND jwt.exp > now()
```

**Service-role key is forbidden for vault writes.**

The Supabase service-role key MUST NOT be accepted by runtime HTTP endpoints.
It may exist only in infra-layer DB migration scripts and bootstrap operations (see §8).

Runtime boundary is pure: no service-role key reaches any tool, handler, or vault write path.

---

## 6. Failure Mode

| Scenario | Response | Log | VAULT |
|----------|----------|-----|-------|
| Missing JWT | 401 Unauthorized | Warning to `auth_attempts` table | ❌ No write |
| Invalid signature | 401 Unauthorized | Warning + fingerprint (kid, iss) | ❌ No write |
| Expired JWT | 401 Unauthorized | Info + `exp` timestamp | ❌ No write |
| actor_id ≠ sub | 403 Forbidden | Error + both IDs (redact sub hash) | ❌ No write |
| Service-role vault write | 403 Forbidden | Critical alert | ❌ No write |
| Valid JWT, all invariants pass | 200 / proceed | Debug | ✅ Write allowed |

**All 401/403 responses include `X-Constitutional-Status: DENIED` header.**

---

## 7. Internal Federation Identity Path

Background jobs and internal federation calls cannot present a Supabase user JWT. They use **self-issued internal tokens**:

```python
# Signed with ARIFOS_INTERNAL_SECRET_<SERVICE> (rotatable, env-only, never in repo)
internal_token = jwt.encode({
    "sub": "system:<service_name>",      # e.g. "system:sentinel-watch"
    "iss": "arifos-internal",
    "aud": "arifOS",
    "exp": now() + 300,
    "iat": now(),
    "kid": "internal-01",
    "scope": "vault:write"
}, key=ARIFOS_INTERNAL_SECRET_SENTINELWATCH, algorithm="HS256")
```

Rules:
- `sub` MUST start with `system:` — never collide with human actor IDs
- `exp` max 5 minutes — short-lived
- `scope` MUST be explicit and minimal
- Each service gets its own secret: `ARIFOS_INTERNAL_SECRET_SENTINELWATCH`, `ARIFOS_INTERNAL_SECRET_WELL`, `ARIFOS_INTERNAL_SECRET_AFORGE`  # pragma: allowlist secret
- Compromised service cannot mint tokens for another service

Services using internal tokens:
- `sentinel-watch` → vault write (governance drift alerts)
- `well` → vault write (biological substrate telemetry)
- A-FORGE bridge → vault write (terminal verdicts)

**Migration:** Each service gets its own `system:<name>` sub + scoped token. No shared `system:default`.

---

## 8. Bootstrap + Migration Strategy

### Bootstrap (cold start)
1. Deploy with per-service secrets (`ARIFOS_INTERNAL_SECRET_*`) in env
2. Start arifOS with JWT middleware in `enforce` mode
3. Internal services authenticate via self-issued tokens
4. Human operators authenticate via Supabase JWT

### Migration (from current state)
1. **Day 0:** Deploy JWT verification middleware in `observe` mode — logs violations but does not block
2. **Day 1–2:** Fix all internal callers to present valid JWT (internal tokens for services, Supabase tokens for humans)
3. **Day 3:** Switch to `enforce` mode — block service-role vault writes
4. **Day 4:** Remove `SUPABASE_SERVICE_ROLE_KEY` from vault write path entirely

### Rollback
- Env flag `JWT_ENFORCE_MODE=false` — single toggle to observe-only
- Does not re-enable service-role vault writes; only softens JWT blocking to logging
- Rollback window: 24 hours. After that, remove toggle.

---

## 9. Code Surface to Touch

| File | Change |
|------|--------|
| `arifosmcp/runtime/session.py` | Replace `validate_token()` stub with JWT verification |
| `arifosmcp/runtime/vault_postgres.py` | Reject service-role writes; require JWT in seal path |
| `arifosmcp/runtime/governance_identity.py` | Bind `actor_id` to `jwt.sub`; add `auth_method` field |
| `fastmcp_ext/transports.py` | Enable `BearerAuthMiddleware`; parse + verify JWT |
| `A-FORGE/src/vault/SupabaseVaultClient.ts` | Present internal JWT on write; remove service-role RPC |
| `core/organs/_0_init.py` | Remove hardcoded `"IM ARIF"` literal; delegate to JWT layer |
| `compose/.env` | Add `ARIFOS_INTERNAL_SECRET_*`, `JWT_ENFORCE_MODE`, `SUPABASE_JWKS_URL` |

---

## 10. Test Matrix

| Test | Expected |
|------|----------|
| Valid Supabase JWT, actor_id == sub | 200, vault write succeeds |
| Valid internal JWT, system:sentinel-watch | 200, vault write succeeds |
| Expired JWT | 401, no vault write |
| Forged JWT (wrong signature) | 401, no vault write |
| Service-role key vault write | 403, no vault write, critical alert logged |
| actor_id != sub | 403, no vault write |
| Missing `aud` claim | 401 |
| Untrusted `iss` | 401 |

## 11. Auth Lineage Snapshot

Every vault seal MUST include an `auth_lineage` snapshot:

```json
{
  "auth_lineage": {
    "sub": "Muhammad Arif bin Fazil",
    "iss": "https://<project>.supabase.co",
    "kid": "rsa-key-2026-04",
    "auth_method": "jwt_supabase"
  }
}
```

Purpose: If Supabase rotates keys later, the seal retains forensic proof of which identity and which key signed the action.

Rules:
- `sub`, `iss`, `kid` are mandatory
- `auth_method` is mandatory (`jwt_supabase`, `jwt_internal`, `jwt_legacy`)
- No PII beyond `sub` — do not include email, name, or metadata
- If JWT is internal, `sub` is `system:<name>` and `iss` is `"arifos-internal"`

---

*Approved for review. Do not implement until sovereign ACK.*
