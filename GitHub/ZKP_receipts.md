# zkPC Receipts — Zero-Knowledge Proof of Cognition (v33Ω)

This document describes the structure and purpose of zkPC receipts used by ArifOS to verify constitutional compliance without exposing chain-of-thought.

---

## 1. Purpose

zkPC ensures:
- Governance is **verifiable**
- Output is **accountable**
- Floors were **actually checked**
- ΔΩΨ was **actually evaluated**
- APEX PRIME **actually judged**

It is the “proof-of-law” mechanism.

---

## 2. zkPC Receipt Structure

Every high-stakes interaction produces a zkPC receipt:

```json
{
  "timestamp": 1732406400.12,
  "request_hash": "H(request)",
  "metrics_hash": "H(all ΔΩΨ metrics)",
  "floor_pass_hash": "H(floor boolean results)",
  "apex_verdict_hash": "H(verdict + reason)",
  "constitution_hash": "H(constitution.json)",
  "psi_vitality": 1.08,
  "tri_witness": 0.97
}