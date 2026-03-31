# arifOS Verdict Envelope Standard v1.0

> **Authority:** 888_JUDGE Ratified (Arif)
> **Epoch:** 2026.03.31
> **Motto:** *Ditempa Bukan Diberi*

## ⚛️ Overview
To prevent alignment drift and downstream parsing errors, every tool in the arifOS ecosystem MUST wrap its output in this standard envelope. This ensures the metabolic router can make deterministic decisions based on unified signals.

## 🏗️ Schema Definition

### 1. Root Structure
```json
{
  "meta": {
    "session_id": "string (UUID)",
    "tool_id": "string (canonical_name)",
    "timestamp": "ISO8601",
    "version": "arifOS-v1.0"
  },
  "verdict": {
    "code": "SEAL | SABAR | PARTIAL | VOID",
    "reason_code": "STRING_ENUM",
    "message": "Human readable explanation"
  },
  "metrics": {
    "delta_s": "float (entropy shift)",
    "confidence": "float (0.0 - 1.0)",
    "risk_tier": "LOW | MEDIUM | HIGH | CRITICAL"
  },
  "payload": {
    "data": "any (tool-specific output)",
    "warnings": ["string"]
  },
  "audit": {
    "floors_checked": ["F1", "F2", "..."],
    "floors_failed": ["string"]
  }
}
```

### 2. Verdict Priority Logic (The Triple-Gated Rule)
1. **Safety (asi_heart):** Any `VOID` here forces a global `VOID`.
2. **Truth (agi_mind):** Any `SABAR` here forces a global `SABAR` if Truth < 0.99.
3. **Data (Physical):** Missing data results in `PARTIAL`, never `SEAL`.

## 🧭 Enforcement
The `444_ROUTER` will automatically `VOID` any tool output that does not validate against this schema.

---
**Verdict:** SEALED [ΔΩΨ | ARIF]
