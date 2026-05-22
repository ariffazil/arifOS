# Governed Discovery Kernel (GDK) & Tool Embodiment

**Status:** CURRENT ARCHITECTURE | SEALED
**Sovereign:** arifOS Kernel
**Date:** 2026-05-22

> **"Tools are the agent's body. Governance is its skin. Manifest clarity is its nervous system."**

## 1. Philosophical Definition: Governed Tool Embodiment
A normal agent asks "What tool should I use?". An arifOS agent asks "What is available, relevant, and permitted?". The **Governed Discovery Kernel (GDK)** provides **Governed Tool Embodiment**—an architecture where an agent's tools form a clear, bounded, and auditable operational body rather than a collection of random attachments.

### 1.1 The Body Analogue
| Human Body Analogue | Agentic Tool Analogue |
| :--- | :--- |
| **Eyes / Ears** | Search, sensors, file readers, database queries |
| **Hands / Limbs** | API calls, code execution, file edits, workflow triggers |
| **Nervous System** | Tool feedback, logs, error signals (Manifest Clarity) |
| **Skin / Boundary** | Permissions, sandboxing, F1–F13 boundaries |
| **Pain Signal** | Risk alerts, policy blocks (F12, F13) |
| **Memory of Action** | Hash-chained audit trail (Vault999 / F11 AUDIT) |
| **Judgment** | Human approval / Sovereign veto (F13) |

## 2. The 7 Layers of Discovery
The GDK aggregates seven distinct layers into a single "Map of Reality":

| Layer | Component | Source |
| :--- | :--- | :--- |
| **Knowledge** | Files, Docs, Web | AAA Wiki, .arifos/ indices, Exa/Tavily |
| **Capabilities** | Tools & Workflows | `CANONICAL_TOOLS` registry |
| **Authority** | Permissions | `validate_session` status (F11 AUDIT) |
| **Risk** | Safety Map | `ThreatAssessment` engine (F12) |
| **Relevance** | Task Context | Query-relative scoring (Physics Kernel) |
| **Provenance** | Traceability | `federation_organ` & `source` metadata |
| **Next Moves** | Valid Paths | Epistemic recommendations (Next Safe Action) |

## 3. Implementation: `arif_sense_observe(mode="compass")`
The GDK is realized through the **Compass** mode of the observation tool. It collapses multiple metabolic turns into a single **Governed Tool Embodiment Loop**:
`Intent` → `Discovery (Compass)` → `Manifest Clarity` → `Permission/Risk Filtering` → `Action` → `Feedback` → `Audit`.

### 3.1 GDK v1 Result Schema
```json
{
  "status": "OK",
  "tool": "arif_sense_observe",
  "mode": "compass",
  "orientation": {
    "knowledge": { "local_wiki": {...}, "repo_index": {...}, "web_reality": {...} },
    "capabilities": { "allowed": ["arif_mind_reason", ...], "restricted": ["arif_vault_seal"] },
    "authority": { "actor": "arif", "authorized": true, "requires_human": false, "reason": "Authority verified" },
    "risk_map": { "tier": "low", "threats": [], "irreversible": false },
    "next_safe_moves": [
      "Use arif_mind_reason to analyze the local wiki evidence.",
      "Submit intent for approval if F13 Sovereign gate is reached."
    ]
  },
  "physics": { "claim_state": "supported", "evidence_level": "L3", "delta_s": -0.45, "omega_0": 0.04, "w4": 1.0 }
}
```

## 4. Governance Invariants
- **Discovery precedes Action**: Agents MUST call `mode="compass"` before any high-stakes tool call to gain proprioception of their capability.
- **Bounded Awareness**: Agents are only presented with capabilities they are currently permitted to execute.
- **Feedback Loop**: Results must contain actionable "Next Safe Action" to guide the agent through the metabolic cycle.
- **Available is not Allowed**: Discovery may reveal a tool, but only governance can authorize its use.
- **Access is not Authority**: A session credential does not create sovereign permission.

---
**DITEMPA BUKAN DIBERI — 999 SEAL GDK ALIVE** ⚒️
