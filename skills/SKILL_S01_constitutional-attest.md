# SKILL_S01: constitutional-attest

> **arifOS Kernel Skill** — Fiqh Agentik v1.0
> **Forged:** 2026-07-04 by AUDITOR (Ψ)
> **Authority:** F13 SOVEREIGN
> **DITEMPA BUKAN DIBERI**

---

## IDENTITY

| Field | Value |
|-------|-------|
| **ID** | S01 |
| **Name** | `constitutional-attest` |
| **Category** | structural |
| **Stage** | 000_INIT |
| **Trinity Lane** | AGI |
| **Fiqh Tier** | **WAJIB** |
| **RSI Eligible** | ✗ NO (Gödel lock) |


---

## PURPOSE

Verify constitution hash unchanged since last session. Load F1-F13 floors.

---

## FIQH AGENTIK BLOCK

### ✅ WAJIB (Mandatory)

- Load constitution hash at every session init
- Compare with last sealed session hash
- Alert if drift detected — HOLD until F13 review

### ❌ HARAM (Forbidden)

- Modify constitution.json at runtime
- Skip attest to speed session startup
- Skip floor evaluation by claiming 'trusted'

### ⚠️ MAKRUH (Discouraged)

- Silent re-hash without logging
- Caching stale constitution hash

### ✨ SUNAT (Encouraged)

- Cross-reference kernel invariant.yaml + eureka axioms + registry
- Surface floor change_alert to principal

### 🔵 HARUS (Neutral, Default)

- Answer factual questions with citations
- Route routine intent to appropriate organ
- Report status when asked
- Read memory/registries for context

---

## PATHS

- `arifosmcp/runtime/floors.py`
- `registries/01-constitution.yaml`

---

## FAILURE MODE

Constitutional drift undetected → silent floor breach

---

## FLOOR BINDING

Load-bearing floor: **F2 Truth**
All other floors are inherited from kernel automatically.

---

*DITEMPA BUKAN DIBERI — forged, not given. See /root/arifOS/registry/fiqh_ledger/ for malu/trust history.*
