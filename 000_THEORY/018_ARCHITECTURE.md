---
title: "018_ARCHITECTURE.md"
version: "v52.5.1-SEAL"
epoch: "2026-01-25"
sealed_by: "888_Judge"
authority: "Constitutional Core"
status: "PRODUCTION"
---

# arifOS ARCHITECTURE: Kernel vs. Drivers

**Motto:** *Separation of Powers is an Engineering Constraint.*

This document defines the structural topology of arifOS, explicitly separating the immutable **Constitutional Kernel** from the mutable **Application Drivers**.

---

## 1. THE HIGH-LEVEL TOPOLOGY

```mermaid
graph TD
    subgraph "AAA: APPLICATION LAYER (Mutable Drivers)"
        CLI[Kimi/Gemini CLI]
        WEB[Dashboard UI]
        AGENTS[Custom Agents]
    end

    subgraph "BBB: PROTOCOL LAYER (The Bridge)"
        MCP[MCP Server (sse.py)]
        ROUTER[ATLAS-333 Router]
        API[FastAPI Gateway]
    end

    subgraph "CCC: CONSTITUTIONAL KERNEL (Immutable Core)"
        TRINITY[Trinity Engines (AGI/ASI/APEX)]
        FLOORS[13 Floor Validators]
        METABOLISM[000-999 Loop]
    end

    subgraph "L0: STORAGE (The Anchor)"
        VAULT[VAULT-999 Ledger]
        DB[Postgres/Vector]
    end

    CLI --> MCP
    WEB --> API
    MCP --> ROUTER
    ROUTER --> TRINITY
    TRINITY --> FLOORS
    FLOORS --> METABOLISM
    METABOLISM --> VAULT
```

---

## 2. THE LAYERS (Separation of Concerns)

### LAYER CCC: The Constitutional Kernel (Immutable)
*   **Role:** The Physics Engine of Governance.
*   **Components:**
    *   **The 13 Floors:** Hard-coded validation logic (`floor_validators.py`).
    *   **The Trinity:** AGI (Mind), ASI (Heart), APEX (Soul) logic (`core/engines/`).
    *   **The Metabolic Loop:** The fixed state machine (000 → 999).
*   **Mutability:** **FROZEN.** Can only be changed via "Phoenix-72" constitutional amendment process (requires 168h cooling).
*   **Analogy:** The CPU microcode + Kernel space.

### LAYER BBB: The Protocol Bridge (Stable)
*   **Role:** The Translation Layer. Connects the outside world to the Kernel.
*   **Components:**
    *   **MCP Server:** (`sse.py`, `server.py`). Implements JSON-RPC 2.0 / SSE.
    *   **ATLAS Router:** Routes intent (HARD/SOFT/CRISIS).
    *   **API Routes:** (`routes/`). Exposes health, metrics.
*   **Mutability:** **STABLE.** Updates require standard PR review (F1/F8 checks).
*   **Analogy:** Operating System Drivers / HAL (Hardware Abstraction Layer).

### LAYER AAA: The Application (Fluid)
*   **Role:** The Interface. How humans and agents interact with the system.
*   **Components:**
    *   **Dashboard:** HTML/JS UI.
    *   **CLI Tools:** Kimi/Gemini adapters.
    *   **Prompts:** `SYSTEM_PROMPT.md` (The "Software" running on the OS).
*   **Mutability:** **FLUID.** Can be updated daily/hourly based on user needs.
*   **Analogy:** Userland Applications.

---

## 3. THE KERNEL BOUNDARY (The Air Gap)

There is a logical "Air Gap" between BBB and CCC.

1.  **Input Sanitation:** No raw data reaches CCC without passing through `000_init` (Gate).
2.  **Unidirectional Control:** AAA can *request* action from CCC, but CCC *commands* AAA.
    *   AAA says: "I want to delete this file."
    *   CCC says: "VOID (F1 Violation)." -> AAA *must* obey.
3.  **Sovereign Injection:** The 888 Judge (Human) has a direct line to CCC (bypassing AAA/BBB) for emergency overrides.

---

## 4. DATA FLOW & TRANSFORMATION

Data changes state as it moves down the layers (The Cooling Process).

| Layer | State | Entropy | Nature |
|-------|-------|---------|--------|
| **AAA (User)** | `Raw` | High | Chaotic, Intent-based |
| **BBB (Bridge)** | `Parsed` | Medium | Structured JSON-RPC |
| **CCC (Kernel)** | `Metabolized` | Low | Constitutional, Validated |
| **L0 (Vault)** | `Sealed` | Zero | Immutable, Hash-chained |

---

## 5. THE TRINITY ENGINE SPECS

### AGI (Mind / Δ)
*   **Input:** Parsed Query.
*   **Function:** `maximize(Truth, Clarity)`.
*   **Output:** `Reasoning_Tree`, `Delta_Bundle`.

### ASI (Heart / Ω)
*   **Input:** Reasoning Tree + Action Proposal.
*   **Function:** `maximize(Safety, Empathy)`.
*   **Output:** `Impact_Analysis`, `Omega_Bundle`.

### APEX (Soul / Ψ)
*   **Input:** Delta + Omega Bundles.
*   **Function:** `maximize(Consensus, Alignment)`.
*   **Output:** `Verdict`, `zkPC_Receipt`.

---

**Status:** SOVEREIGNLY_SEALED (v52.5.1)
**Authority:** System Architect
**Reference:** Defines the `arifOS` repository structure.
