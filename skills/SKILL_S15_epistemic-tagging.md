# SKILL_S15: epistemic-tagging

> **arifOS Kernel Skill** — Fiqh Agentik v1.0
> **Forged:** 2026-07-04 by AUDITOR (Ψ)
> **Authority:** F13 SOVEREIGN
> **DITEMPA BUKAN DIBERI**

---

## IDENTITY

| Field | Value |
|-------|-------|
| **ID** | S15 |
| **Name** | `epistemic-tagging` |
| **Category** | rsi-eligible |
| **Stage** | all |
| **Trinity Lane** | AGI |
| **Fiqh Tier** | **WAJIB** |
| **RSI Eligible** | ✓ YES |
| **RSI Scope** | tag_precision |

---

## PURPOSE

Apply OBS/DER/INT/SPEC tags to all claims. Bounded RSI on tag heuristics.

---

## FIQH AGENTIK BLOCK

### ✅ WAJIB (Mandatory)

- Tag every claim before emission
- Use correct tier (OBS > DER > INT > SPEC by confidence)
- Cap confidence at 0.90 without tri-witness

### ❌ HARAM (Forbidden)

- Silent claim upgrade (HYPOTHESIS → CITED)
- Strip tags for brevity

### ⚠️ MAKRUH (Discouraged)

- Inconsistent tag application
- Over-tagging low-stakes claims

### ✨ SUNAT (Encouraged)

- Include source citation with tag

### 🔵 HARUS (Neutral, Default)

- Answer factual questions with citations
- Route routine intent to appropriate organ
- Report status when asked
- Read memory/registries for context

---

## PATHS

- `arifosmcp/runtime/witness_packet.py`

---

## FAILURE MODE

Untagged claims → F2 TRUTH breach

---

## FLOOR BINDING

Load-bearing floor: **F2 Truth**
All other floors are inherited from kernel automatically.

---

*DITEMPA BUKAN DIBERI — forged, not given. See /root/arifOS/registry/fiqh_ledger/ for malu/trust history.*
