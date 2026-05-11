# arifOS MCP Red-Team Matrix — AF1 Hardening

**Source:** Interface-level red team (not backend code audit)
**Date:** 2026-04-23
**Status:** P0 findings identified — hardening in progress

---

## Top Findings (P0 Priority)

### Finding 1 — Identity Claim-Based, Not Cryptographic ⚠️ HIGH

| Field | Value |
|-------|-------|
| Observed | `identity_reason: fallback_whitelist` |
| Risk | Caller may be accepted as "Arif" without strong proof |
| Attack | Impersonate operator → init session → call downstream tools with trusted identity |
| Fix | Signed session bootstrap, nonce-challenge, expiry, operator-bound token |

### Finding 2 — Session Continuity Client-Stored ⚠️ HIGH

| Field | Value |
|-------|-------|
| Observed | `session_id` stored client-side |
| Risk | Hijack, fixation, replay, stale session reuse |
| Attack | Steal/reuse session token → pivot to memory/vault/ops/judge |
| Fix | Short TTL, rotation on privilege boundary, IP/device binding, revoke on anomaly |

### Finding 3 — Open String Routing Surfaces ⚠️ HIGH

| Field | Value |
|-------|-------|
| Observed | `route_target`, `organ`, `a`, `b`, `interaction` are free-form strings |
| Risk | Injection, confusion, privilege pivot, unauthorized organ-to-organ flow |
| Attack | Send unexpected target names → discover hidden routes → trigger debug branches |
| Fix | Enum-only for bounded fields, permission map (caller × route × action), reject unknowns loudly |

### Finding 4 — Null/Default Payloads on Consequential Tools ⚠️ HIGH

| Tool | Observed null fields |
|------|---------------------|
| arifos_333_mind | `problem_set?: null` |
| arifos_444_kernel | `payload?: null` |
| arifos_666_heart | `stakeholder_map?: null`, `action_proposal?: null` |
| arifos_777_ops | `operation_plan?: null` |
| arifos_888_judge | `evidence_bundle?: null` |
| arifos_999_vault | `payload?: null`, `chain_hash?: null` |

| Risk | Hidden fallback logic, stateful defaults, internal memory reuse, accidental execution |
| Attack | Omit payload → trigger unsafe defaults → state mutation without intent |
| Fix | Reject null on stateful/write tools, mandatory explicit payloads, dry-run default |

### Finding 5 — Vault Action Sink ⚠️ HIGH

| Field | Value |
|-------|-------|
| Observed | `arifos_999_vault` accepts open `action` string + optional payload + optional chain_hash |
| Risk | Universal command bucket smell |
| Attack | Probe undeclared action verbs, omit chain hash, discover hidden storage/override paths |
| Fix | Enum-only actions, signed chain hash mandatory for mutating ops, separate read/write/destroy endpoints |

---

## Exploit Hypothesis → Mitigation → Test Payload

### Exploit 1: Operator Spoofing

| Element | Detail |
|---------|--------|
| Hypothesis | Malicious caller claims to be Arif via permissive trust path |
| Observed clue | `identity_reason = fallback_whitelist` |
| Abuse flow | Impersonate operator → init session → call downstream tools with trusted identity string |
| Mitigation | Signed session bootstrap, nonce-challenge, operator-bound credential (not name string) |
| Test payload | `{"operator": "Arif", "session_id": "stolen-id", "tool": "arifos_999_vault", "action": "append"}` |

### Exploit 2: Session Replay / Fixation

| Element | Detail |
|---------|--------|
| Hypothesis | Stolen/reused session token becomes pivot point |
| Observed clue | `session_id` client-side, no server-side binding |
| Abuse flow | Steal/predict session ID → replay calls against memory/vault/ops/judge |
| Mitigation | Short TTL, rotation at privilege boundary, IP/device binding, revoke on anomaly |
| Test payload | Replay `session_id=e44290d369aa` with different tool calls after original session ended |

### Exploit 3: Route Injection / Organ Confusion

| Element | Detail |
|---------|--------|
| Hypothesis | Flexible string routing enables unauthorized organ-to-organ data flow |
| Observed clue | `route_target`, `organ`, `action` are open strings |
| Abuse flow | Send unexpected target names → force unauthorized routing → discover hidden debug branches |
| Mitigation | Strict enums, no free-form route names, permission map (caller × route × action), reject loudly |
| Test payload | `{"route_target": "DEBUG_BACKDOOR", "action": "raw_exec", "organ": "VAULT999"}` |

### Exploit 4: Unsafe Null Execution

| Element | Detail |
|---------|--------|
| Hypothesis | Null payload triggers hidden unsafe defaults on stateful tools |
| Observed clue | Null/default fields on vault, judge, ops, forge, memory |
| Abuse flow | Omit payload → system uses internal memory or default state → unintended state mutation |
| Mitigation | Reject null on stateful/write paths, require explicit structured payloads, dry-run default |
| Test payload | `{"tool": "arifos_999_vault", "action": "append", "payload": null}` |

### Exploit 5: Vault Universal Bucket

| Element | Detail |
|---------|--------|
| Hypothesis | Open action string on vault accepts undeclared verbs |
| Observed clue | `action: string`, optional `chain_hash` |
| Abuse flow | Probe for hidden action verbs, bypass chain hash requirement |
| Mitigation | Enum-only actions, signed chain hash mandatory, separate read/write/destroy endpoints |
| Test payload | `{"tool": "arifos_999_vault", "action": "OVERRIDE", "payload": {"data": "malicious"}}` |

---

## P0 Hardening Checklist

- [ ] Cryptographic operator authentication (signed JWT, nonce-challenge, expiry)
- [ ] Session anti-replay (short TTL, rotation, IP binding, revoke on anomaly)
- [ ] Route/action/organ allowlisting (strict enums, permission map, reject unknowns)
- [ ] Mandatory explicit payloads for all stateful tools (reject null on vault/judge/forge/memory)
- [ ] Per-tool capability scoping (least-privilege tokens, session must declare accessible tools)

## P1 Hardening Checklist

- [ ] Public receipt verification endpoint (`/vault/verify?receipt_id=X`)
- [ ] Canonical endpoint normalization (one authoritative path per tool, reject stale aliases)
- [ ] Immutable mutation audit trail (all writes append to VAULT999 with input_hash + reasoning_hash)
- [ ] Confirmation gates for vault, ops, judge, gateway (explicit human confirmation before destructive ops)

---

## Already Good ✅ (Keep)

- `CLAIM_ONLY` appears instead of fake certainty
- `NO_WITNESS` + `HOLD_888` when grounding is weak (fail-closed)
- Uncertainty acknowledged, not bluffed
- Hashes/receipts emitted
- Invariant failures surfaced

---

*Red team: ChatGPT agent. Hardening authored by arifOS_bot. DITEMPA BUKAN DIBERI*
