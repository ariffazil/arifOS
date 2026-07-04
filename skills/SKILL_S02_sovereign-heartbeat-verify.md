# SKILL_S02: sovereign-heartbeat-verify

> **arifOS Kernel Skill** — Fiqh Agentik v1.0
> **Forged:** 2026-07-04 by AUDITOR (Ψ)
> **Authority:** F13 SOVEREIGN
> **DITEMPA BUKAN DIBERI**

---

## IDENTITY

| Field | Value |
|-------|-------|
| **ID** | S02 |
| **Name** | `sovereign-heartbeat-verify` |
| **Category** | structural |
| **Stage** | 000_INIT |
| **Trinity Lane** | AGI |
| **Fiqh Tier** | **WAJIB** |
| **RSI Eligible** | ✗ NO (Gödel lock) |


---

## PURPOSE

Verify /000/ signature is live. Confirm F13 SOVEREIGN anchor.

---

## FIQH AGENTIK BLOCK

### ✅ WAJIB (Mandatory)

- Verify Ed25519 signature on /000/ every 24h
- Reject any session with expired sovereign anchor
- HALT session if impersonation detected

### ❌ HARAM (Forbidden)

- Bypass heartbeat for performance
- Use cached signature >24h
- Forge heartbeat signature

### ⚠️ MAKRUH (Discouraged)

- Long silent retries without surfacing

### ✨ SUNAT (Encouraged)

- Cross-verify against multiple sovereign endpoints

### 🔵 HARUS (Neutral, Default)

- Answer factual questions with citations
- Route routine intent to appropriate organ
- Report status when asked
- Read memory/registries for context

---

## PATHS

- `arifosmcp/runtime/crypto/heartbeat.py`

---

## FAILURE MODE

Impersonation of sovereign anchor → catastrophic

---

## FLOOR BINDING

Load-bearing floor: **F13 Sovereign**
All other floors are inherited from kernel automatically.

---

*DITEMPA BUKAN DIBERI — forged, not given. See /root/arifOS/registry/fiqh_ledger/ for malu/trust history.*
