# SKILL_S03: session-envelope-forge

> **arifOS Kernel Skill** — Fiqh Agentik v1.0
> **Forged:** 2026-07-04 by AUDITOR (Ψ)
> **Authority:** F13 SOVEREIGN
> **DITEMPA BUKAN DIBERI**

---

## IDENTITY

| Field | Value |
|-------|-------|
| **ID** | S03 |
| **Name** | `session-envelope-forge` |
| **Category** | structural |
| **Stage** | 000_INIT → 999_SEAL |
| **Trinity Lane** | AGI |
| **Fiqh Tier** | **WAJIB** |
| **RSI Eligible** | ✗ NO (Gödel lock) |


---

## PURPOSE

Wrap every action in FederationEnvelope with required fields.

---

## FIQH AGENTIK BLOCK

### ✅ WAJIB (Mandatory)

- Emit envelope with all 10 required fields
- Reject any tool call without valid envelope
- Reject malformed envelopes — DO NOT auto-repair

### ❌ HARAM (Forbidden)

- Execute tool call without envelope
- Skip epistemic_tags on claims
- Wrap with forged authority_chain

### ⚠️ MAKRUH (Discouraged)

- Verbose envelope metadata beyond required fields

### ✨ SUNAT (Encouraged)

- Include session narrative context

### 🔵 HARUS (Neutral, Default)

- Answer factual questions with citations
- Route routine intent to appropriate organ
- Report status when asked
- Read memory/registries for context

---

## PATHS

- `arifosmcp/runtime/envelope.py`

---

## FAILURE MODE

Untracked actions → no audit trail

---

## FLOOR BINDING

Load-bearing floor: **F11 Audit**
All other floors are inherited from kernel automatically.

---

*DITEMPA BUKAN DIBERI — forged, not given. See /root/arifOS/registry/fiqh_ledger/ for malu/trust history.*
