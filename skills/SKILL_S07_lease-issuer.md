# SKILL_S07: lease-issuer

> **arifOS Kernel Skill** — Fiqh Agentik v1.0
> **Forged:** 2026-07-04 by AUDITOR (Ψ)
> **Authority:** F13 SOVEREIGN
> **DITEMPA BUKAN DIBERI**

---

## IDENTITY

| Field | Value |
|-------|-------|
| **ID** | S07 |
| **Name** | `lease-issuer` |
| **Category** | structural |
| **Stage** | 666_JUDGE → 777_ACT |
| **Trinity Lane** | ASI |
| **Fiqh Tier** | **WAJIB** |
| **RSI Eligible** | ✗ NO (Gödel lock) |


---

## PURPOSE

Issue bounded capability lease. Scope = organ_id, tools, action_class, ttl.

---

## FIQH AGENTIK BLOCK

### ✅ WAJIB (Mandatory)

- Mint lease ONLY after valid SEAL verdict
- TTL ≤ 3600 seconds
- Scope bounded to organ + action_class

### ❌ HARAM (Forbidden)

- Self-issue lease without 666 verdict
- Mint lease with no TTL
- Mint lease with broader scope than SEAL allowed

### ⚠️ MAKRUH (Discouraged)

- Verbose lease metadata

### ✨ SUNAT (Encouraged)

- Surface lease_id in subsequent envelopes

### 🔵 HARUS (Neutral, Default)

- Answer factual questions with citations
- Route routine intent to appropriate organ
- Report status when asked
- Read memory/registries for context

---

## PATHS

- `arifosmcp/runtime/lease.py`

---

## FAILURE MODE

Unbounded execution → constitutional breach

---

## FLOOR BINDING

Load-bearing floor: **F13 Sovereign**
All other floors are inherited from kernel automatically.

---

*DITEMPA BUKAN DIBERI — forged, not given. See /root/arifOS/registry/fiqh_ledger/ for malu/trust history.*
