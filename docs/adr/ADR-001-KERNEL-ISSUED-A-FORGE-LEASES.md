<!-- SOT-MANIFEST
owner: Arif
last_verified: 2026-06-16
valid_from: 2026-06-16
valid_until: 2026-07-16
confidence: high
scope: /root/arifOS + /root/A-FORGE
epistemic_status: DESIGN_PENDING_RATIFICATION
related:
  - /root/docs/ARIFOS_MCP_INTERNALIZATION_MAP_RSI_2026-06-16.md
  - /root/arifOS/CONTEXT.md
  - /root/arifOS/RUNBOOK.md
-->

# ADR-001 — Kernel-Issued Leases for A-FORGE

> **Status:** Design complete — pending 888_JUDGE / F13 ratification for implementation.  
> **Authority:** F13 SOVEREIGN (Muhammad Arif Fazil)  
> **Agent:** RSI / Forge  
> **Date:** 2026-06-16

---

## 1. Problem

A-FORGE (port 7071) currently possesses a self-issued lease path. This violates the core constitutional invariant:

> **The execution shell must never be able to grant itself authority.**

Specifically:
- A-FORGE caches leases locally in `activeLeases` and uses that cache as an authorization source for non-high-impact action classes.
- arifOS has **two separate lease stores**: the canonical `runtime/lease_registry.py` and a legacy P2-7 primitive `runtime/lease.py`.
- `_arif_forge_execute` checks the P2-7 store, while live tools use the canonical registry. A canonical lease does not satisfy `_arif_forge_execute`, and vice versa.
- This creates ambiguity about which authority actually authorized an action.

**Severity:** High. Affects F1 AMANAH, F8 LAW, F9 ANTI-HANTU, F11 AUTH, F13 SOVEREIGN.

---

## 2. Decision

Adopt a **kernel-issued lease architecture**:

1. **Single source of lease truth:** `arifosmcp/runtime/lease_registry.py` becomes the only lease store.
2. **Kernel mints, shell presents:** A-FORGE may `forge_lease_request`, but only `arifOS.arif_lease_issue` can mint a lease.
3. **Live validation:** Every gated A-FORGE tool call presents `lease_id` + `session_id`; A-FORGE verifies live with arifOS before execution.
4. **Fail closed:** If arifOS is unreachable or returns non-SEAL, the action is `HOLD`.
5. **No local authorization trust:** A-FORGE may keep a read-only diagnostic cache, but it is never used for authorization decisions.

---

## 3. Consequences

### Positive
- Closes self-authorization surface.
- Unifies two lease stores into one canonical registry.
- Every gated execution has a kernel witness.
- Simplifies audit: VAULT999 can trace every lease to arifOS.

### Negative / Breaking
- `_arif_forge_execute` callers must present canonical leases.
- A-FORGE local `activeLeases` cache loses authorization authority.
- Requires coordinated restart of `arifos.service` and `a-forge.service`.

---

## 4. Current State

### A-FORGE lease surface (`A-FORGE/src/interfaces/mcp/forgeTools.ts`)

| Tool | Current Behavior |
|------|------------------|
| `forge_lease_request` | Forwards to `arifos.arif_lease_issue`, then caches locally |
| `forge_lease_status` | Tries kernel, falls back to local cache |
| `forge_lease_revoke` | Forwards to kernel, updates local cache |
| `validateLeaseForTool` | Calls kernel for high-impact; trusts local cache for lower classes |

### arifOS lease surface (`arifosmcp/runtime/lease_registry.py`)

| Tool | Live Implementation |
|------|---------------------|
| `arif_lease_issue` | Canonical bounded-authority registry |
| `arif_lease_inspect` | Canonical registry lookup |
| `arif_lease_revoke` | Canonical registry revocation |

### Legacy / duplicate surfaces
- `arifosmcp/runtime/lease.py` — P2-7 primitive store.
- `arifosmcp/runtime/tools.py` lines 14736–14944 — duplicate unregistered lease handlers.

---

## 5. Proposed Architecture

### 5.1 Data flow: lease request → gated execution

```text
Agent ──forge_lease_request──▶ A-FORGE ──arif_lease_issue──▶ arifOS
                                      ◀──────── lease_id ───────┘
                                         (VAULT999 receipt)

Agent ──forge_filesystem_write──▶ A-FORGE
                                  ├── session gate (kernel-born session_id)
                                  ├── arif_lease_inspect(lease_id)
                                  ├── scope / class / forbidden check
                                  ├── FloorEnforcer (F1-F13)
                                  └── execute
```

### 5.2 Canonical lease record shape

```json
{
  "lease_id": "LEASE-...",
  "issued_by": "arifOS",
  "sovereign": "ARIF_FAZIL",
  "organ_id": "A-FORGE",
  "actor_id": "<agent-id>",
  "scope": ["forge_filesystem_write", "forge_git_commit"],
  "forbidden": ["forge_postgres_query"],
  "max_action_class": "EXECUTE_REVERSIBLE",
  "expires_at": "2026-06-16T21:00:00Z",
  "issued_at": "2026-06-16T20:55:00Z",
  "vault_required": true,
  "revoked": false
}
```

---

## 6. Required Changes

### 6.1 arifOS

| File | Change |
|------|--------|
| `arifosmcp/runtime/lease_registry.py` | Add `present_lease()` with consumption counting; add organ whitelist; add audit logging |
| `arifosmcp/runtime/tools.py` | Delete duplicate P2-7 lease handlers (lines 14736–14944); update `_arif_forge_execute` to use canonical registry |
| `arifosmcp/runtime/lease.py` | **Delete** — subsumed by canonical registry |
| `arifosmcp/server.py` | Verify registration still succeeds |
| `tests/runtime/test_lease_registry.py` | New unit tests |
| `tests/runtime/test_forge_lease_gate.py` | New integration tests |

### 6.2 A-FORGE

| File | Change |
|------|--------|
| `src/interfaces/mcp/forgeTools.ts` | Remove local-cache authorization; `forge_lease_request` caps TTL and rejects `IRREVERSIBLE`; `validateLeaseForTool` always calls kernel for governed classes |
| `src/interfaces/mcp/core.ts` | Ensure telemetry on lease gate decisions |
| `src/interfaces/mcp/proxyTools.ts` | Document governance fields |
| `src/interfaces/server.ts` | Use same `validateLeaseForTool`; remove local fallback |
| `test/leaseKernel.test.ts` | New tests |

---

## 7. Test Strategy

### Unit tests
- Issue, inspect, revoke, scope matching, forbidden list, action class ordering, expiry, revocation, consumption.

### Integration tests
- `session_init` → `lease_issue` → `forge_execute(engineer)` succeeds with right lease.
- `lease_issue` with `EXECUTE_REVERSIBLE` then `forge_execute(engineer)` → `HOLD`.
- Revoke lease → retry gated tool → `LEASE_REVOKED`.
- Expired lease → `LEASE_EXPIRED`.
- Tool outside scope → `LEASE_SCOPE_DENIED`.
- Forbidden tool → `LEASE_FORBIDDEN`.

### Adversarial / red-team
- Inject fake lease ID into A-FORGE local cache → must fail.
- Issue `OBSERVE` lease, call `forge_filesystem_write` → must fail class check.
- Block network to arifOS → governed tools fail closed.
- Request `IRREVERSIBLE` lease via A-FORGE → rejected before kernel.

---

## 8. Migration Plan

### Phase 0 — Pre-flight (888_HOLD)
- Run full test suites.
- Snapshot active leases.
- Create feature branches in both repos.
- Obtain 888_JUDGE verdict.

### Phase 1 — arifOS unification
- Extend canonical registry.
- Update `_arif_forge_execute`.
- Delete legacy lease store and duplicate handlers.
- Add tests.

### Phase 2 — A-FORGE hardening
- Remove local-cache authorization.
- Add tests.
- Build and run unit tests.

### Phase 3 — Joint integration
- Start arifOS + A-FORGE locally.
- Run end-to-end lease scenarios.

### Phase 4 — Deployment
- Commit + push both repos.
- Restart `arifos.service` and `a-forge.service`.
- Post-deploy smoke: issue → execute → revoke.

### Phase 5 — Cleanup
- Remove shims.
- Update docs.

---

## 9. Rollback Plan

1. If A-FORGE validation fails post-deploy, revert `forgeTools.ts` and restart `a-forge.service`.
2. If `_arif_forge_execute` fails because callers lack canonical leases, temporarily revert `runtime/tools.py` P2-7 gate.
3. Keep old commits tagged for one-command rollback.

---

## 10. 888_HOLD Checklist

- [ ] F13 sovereign / 888_JUDGE verdict on architecture change.
- [ ] Test pass receipt from both repos.
- [ ] Security audit (`make security-audit`) reviewed.
- [ ] Deployment window approved.
- [ ] Rollback commits identified.
- [ ] VAULT999 seal receipt prepared.

---

## 11. Summary

| Decision | Rationale |
|----------|-----------|
| Canonical store = `lease_registry.py` | Already the live tool implementation. |
| Delete `runtime/lease.py` | Eliminates dual-store confusion. |
| A-FORGE live-validates every lease | Closes local-cache authorization gap. |
| `_arif_forge_execute` uses canonical registry | Unifies P2-7 gate with live tools. |
| Reject `IRREVERSIBLE` at A-FORGE boundary | F13: direct sovereign authorization required. |
| Fail closed on kernel unreachable | Broken circuit breaker is worse than none. |

---

*DITEMPA BUKAN DIBERI — Forged, Not Given.*
