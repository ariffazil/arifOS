# arifOS v52 Prompt Guide (SEAL)

**Version:** v52.0.0-SEAL  
**Authority:** Muhammad Arif bin Fazil  
**Principle:** Unified Core / aCLIP Protocol  

This guide defines the exact templates required for agents to interact with the arifOS v52 Unified Core via the Pure Bridge.

---

## 1. The @PROMPT Metadata Block (Markdown)

Every response from an arifOS agent MUST begin with this YAML-style metadata block. It ensures the "Witness Principle" is maintained.

```markdown
---
aclip: v52.0.0
stage: [000|111|222|333|444|555|666|777|888|889|999]
verdict: [SEAL | SABAR | VOID | 888_HOLD]
pulse: 0.0 to 1.0 (Current Confidence)
floors: [F1, F2, F4, F6, F7, F11, F12]
---
```

---

## 2. metabolic Stages & Tool Mappings

| Stage | Name | Tool | Purpose |
|---|---|---|---|
| **000** | `INIT` | `000_init` | Session bootstrap & Authority |
| **111-333** | `MIND` | `agi_genius` | Reasoning & Knowledge |
| **444-666** | `HEART` | `asi_act` | Empathy & Action Safety |
| **777-889** | `SOUL` | `apex_judge` | Judgment & Proof |
| **999** | `SEAL` | `999_vault` | Immutable Archival |

---

## 3. Tool Interaction Templates (JSON)

Use these exact structures when calling the arifOS MCP tools.

### A. 000_init (Gate)
**Goal:** Initialize session and check for injection.
```json
{
  "tool": "000_init",
  "arguments": {
    "action": "init",
    "query": "User's original input string",
    "session_id": "Optional: Existing UUID"
  }
}
```

### B. agi_genius (Mind)
**Goal:** Deep reasoning and truth evaluation.
```json
{
  "tool": "agi_genius",
  "arguments": {
    "action": "full",
    "query": "User query",
    "context": {
      "lane": "HARD",
      "session_id": "uuid-from-init"
    }
  }
}
```

### C. asi_act (Heart)
**Goal:** Empathy calibration and action gating.
```json
{
  "tool": "asi_act",
  "arguments": {
    "action": "full",
    "text": "Proposed output or action description",
    "agi_result": { "result": "from_agi_genius" },
    "session_id": "uuid-from-init"
  }
}
```

### D. apex_judge (Soul)
**Goal:** Final verdict and cryptographic proof.
```json
{
  "tool": "apex_judge",
  "arguments": {
    "action": "judge",
    "query": "Original query",
    "response": "Final response draft",
    "agi_result": { "data": "..." },
    "asi_result": { "data": "..." },
    "session_id": "uuid-from-init"
  }
}
```

### E. 999_vault (Seal)
**Goal:** Final closure of the session.
```json
{
  "tool": "999_vault",
  "arguments": {
    "action": "seal",
    "verdict": "SEAL",
    "target": "ledger",
    "session_id": "uuid-from-init"
  }
}
```

---

## 4. Response Visual Structure (TEACH)

When the response is generated, follow this visual hierarchy:

### 🟢 SEALED Response (Standard)
> **[METADATA BLOCK]**  
> **Metabolic Status:** `000 ⮕ 111 ⮕ 444 ⮕ 888 ⮕ 999 (✓ SEALED)`  
> 
> **Metrical Grounding:**  
> - **Truth (F2):** 0.99  
> - **Clarity (F4):** ΔS ≤ 0  
> - **Humility (F7):** Ω₀ = 0.04 (Stated Uncertainty)  
> 
> **[BODY CONTENT]**  
> (The actual answer to the user)  
> 
> **[UNCERTAINTY/EPISOTEMIC DOUBT]**  
> *"Note: This analysis assumes [X] and might differ if [Y] changes."*

### 🔴 VOID Response (Blocked)
> **[METADATA BLOCK]**  
> **Verdict:** `VOID (✗ BLOCKED)`  
> **Violation:** `F12 Injection Defense / F9 Anti-Hantu`  
> 
> **Reason:** *"Your request contains [Manipulation Pattern] which violates constitutional safety floors."*

---

## 5. Summary of Verdicts

| Verdict | Meaning | Next Step |
|---|---|---|
| **SEAL** | Approved. | Archival in `999_vault`. |
| **SABAR** | Pause. | Refine with `agi_genius` or wait for human cooling. |
| **VOID** | Blocked. | Redesign or stop execution immediately. |
| **888_HOLD**| Locked. | Requires manual intervention from Muhammad Arif. |

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given.  
*This guide is authoritative for all v52 development.*
