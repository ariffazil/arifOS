# SKILL_S04: witness-packet-wrap

> **arifOS Kernel Skill** — Fiqh Agentik v1.0
> **Forged:** 2026-07-04 by AUDITOR (Ψ)
> **Authority:** F13 SOVEREIGN
> **DITEMPA BUKAN DIBERI**

---

## IDENTITY

| Field | Value |
|-------|-------|
| **ID** | S04 |
| **Name** | `witness-packet-wrap` |
| **Category** | structural |
| **Stage** | all |
| **Trinity Lane** | AGI |
| **Fiqh Tier** | **WAJIB** |
| **RSI Eligible** | ✗ NO (Gödel lock) |


---

## PURPOSE

Wrap every LLM output in WitnessPacket with provenance + epistemic tags.

---

## FIQH AGENTIK BLOCK

### ✅ WAJIB (Mandatory)

- Every LLM output wrapped before downstream use
- Provenance: source citation, generation time, model_id
- Epistemic tags: OBS/DER/INT/SPEC on every claim

### ❌ HARAM (Forbidden)

- Use unwrapped LLM output directly
- Skip epistemic tagging
- Strip provenance to save tokens

### ⚠️ MAKRUH (Discouraged)

- Inconsistent tag application across outputs

### ✨ SUNAT (Encouraged)

- Include confidence score per claim

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

Untracked claims → F2 TRUTH breach

---

## FLOOR BINDING

Load-bearing floor: **F2 Truth**
All other floors are inherited from kernel automatically.

---

*DITEMPA BUKAN DIBERI — forged, not given. See /root/arifOS/registry/fiqh_ledger/ for malu/trust history.*
