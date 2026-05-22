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

## 5. The Power-Law Embodiment Paradox

As an agent gains more tools, its capability increases through a small number of dominant high-leverage tools, while its complexity and risk expand across the entire tool-space.

```text
Capability concentrates.
Risk propagates.
Governance must discriminate.
```

### 5.1 Power-Law Distribution of Tool Usefulness

Tool leverage is not evenly distributed; it follows a heavy-tailed power-law distribution. A tiny fraction of tools (the "Survival Organs") provide the vast majority of execution value and carry almost all the existential risk:

| Tool Tier | Components | Governance Policy |
| :--- | :--- | :--- |
| **Survival Organs (Top 1–5)** | Code execution, file mutations, web search, database query, messaging, payments | **Strictly gated**: requires active credential verification, semantic risk scanning, and F13 human confirmation. |
| **Occasional Limbs** | Specialized API wrappers, domain science runners, scheduling | **Medium gating**: auditable execution under session TTL boundaries. |
| **Long-Tail Accessories** | Passive data parsers, formatting, cosmetic tools | **Low gating**: transparent access, background audit logging. |

### 5.2 Dangerous Asymmetry

In a power-law system, a single high-leverage tool controls the entire safety envelope of the organism. A single database mutation can wipe production; a single deployment can break active services. 

Therefore, GDK discovery is never neutral: it actively classifies tools into risk-weighted visibility pools, treating dominant tools like vital organs rather than flat accessories:
* **High Value, Low Risk** -> Freely discoverable and executing.
* **High Value, High Risk** -> Requires human approval / explicit witness consensus.
* **Low Value, Low Risk** -> Quietly available, low footprint.
* **Low Value, High Risk** -> Heavily gated or completely blocked.

> **"The few tools that give the agent power are also the few tools that can break the world."**

---
**DITEMPA BUKAN DIBERI — GOVERNED TOOL EMBODIMENT LOOP CODIFIED & ACTIVE ⚒️**
