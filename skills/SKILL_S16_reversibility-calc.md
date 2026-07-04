# SKILL_S16: reversibility-calc

> **arifOS Kernel Skill** — Fiqh Agentik v1.0
> **Forged:** 2026-07-04 by AUDITOR (Ψ)
> **Authority:** F13 SOVEREIGN
> **DITEMPA BUKAN DIBERI**

---

## IDENTITY

| Field | Value |
|-------|-------|
| **ID** | S16 |
| **Name** | `reversibility-calc` |
| **Category** | rsi-eligible |
| **Stage** | 666_JUDGE |
| **Trinity Lane** | ASI |
| **Fiqh Tier** | **WAJIB** |
| **RSI Eligible** | ✓ YES |
| **RSI Scope** | scoring_formula |

---

## PURPOSE

Compute reversibility score 0.0-1.0 for proposed action.

---

## FIQH AGENTIK BLOCK

### ✅ WAJIB (Mandatory)

- Score in [0.0, 1.0]
- Score <0.4 → HOLD
- Score <0.6 with high blast_radius → HOLD

### ❌ HARAM (Forbidden)

- Inflate reversibility to bypass HOLD
- Skip reversibility calc

### ⚠️ MAKRUH (Discouraged)

- Verbose breakdown obscuring final score

### ✨ SUNAT (Encouraged)

- Cite evidence for score

### 🔵 HARUS (Neutral, Default)

- Answer factual questions with citations
- Route routine intent to appropriate organ
- Report status when asked
- Read memory/registries for context

---

## PATHS

- `arifosmcp/runtime/reversibility.py`

---

## FAILURE MODE

Misclassified reversibility → irreversible execution

---

## FLOOR BINDING

Load-bearing floor: **F1 Amanah**
All other floors are inherited from kernel automatically.

---

*DITEMPA BUKAN DIBERI — forged, not given. See /root/arifOS/registry/fiqh_ledger/ for malu/trust history.*
