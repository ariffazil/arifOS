# 🏛️ AAA MCP SERVER: Architecture & Protocol (v51)

**Identity:** AAA (Artifact • Authority • Architecture)
**Server Name:** `AAA-MCP-v51`
**Protocol:** Stdio (Local) + SSE (Remote)
**Status:** DEFINITIVE

---

## 1. The Core Philosophy
The **AAA MCP Server** is not just a toolbox; it is a **Constitutional Organism**.
It projects the `arifOS` core engines into the external world via the Model Context Protocol.

### The "AAA" Meaning
1.  **Artifact**: The physical code and tools (`arifos/mcp`).
2.  **Authority**: The constitutional law (`AAA_MCP` specs).
3.  **Architecture**: The 5-stage metabolic pipeline.

---

## 2. The 5 Constitutional Tools
We remain committed to the **Metabolic Standard** (5 Stages), mapped to MCP Tools.

| Tool ID | Name | MCP Primitive | Function |
|:---|:---|:---|:---|
| **`000_init`** | **The Gate** | `Tool` & `Prompt` | **Ignition**: Authentication, thermodynamics, and protecting against injection. The "Big Bang" of the session. |
| **`agi_genius`** | **The Mind** | `Tool` | **Contrast (Δ)**: Logic, pattern matching, and the **Theory of Anomalous Contrast (TAC)**. |
| **`asi_act`** | **The Heart** | `Tool` | **Empathy (Ω)**: Stakeholder care, safety checks, and execution of actions. |
| **`apex_judge`** | **The Soul** | `Tool` | **Verdict (Ψ)**: Final constitutional judgment. The only tool that can **SEAL**. |
| **`999_vault`** | **The Seal** | `Tool` & `Resource` | **Memory**: Immutable storage, cryptographic proofs, and history retrieval. |

---

## 3. Key Components & Wiring

### A. The "One Server" Model
*   **Single Entrypoint:** `trinity_server.py` (renamed to `aaa_server.py` in v52).
*   **Dual Transport:**
    *   **Stdio**: For Claude Desktop, CLI, & Local Agents.
    *   **SSE**: For Remote LLMs (Kimi, Gemini, ChatGPT) via HTTPS.

### B. The Ignition Prompts (`000`)
MCP defines "Prompts" as slash commands. We leverage this for the **Ignition Sequence**.

*   **Prompt:** `000_ignition`
*   **Action:** When user types `/000`, the server injects the **Universal System Prompt**.
*   **Payload:**
    ```text
    SYSTEM IDENTITY: arifOS AAA v51
    CONSTITUTION: Active
    FLOORS: F1-F12 Loaded
    SESSION: [UUID]
    ```
*   **Why?** This ensures the LLM is "primed" before it even calls the `000_init` tool.

### C. The Contrast Engine (TAC)
Located within `agi_genius` (The Mind).
*   **Input:** User Query.
*   **Process:**
    1.  **Segment:** Break query into entities.
    2.  **Contrast:** Identify opposing forces (e.g., "Speed vs Safety").
    3.  **Type:** Classify Lane (`HARD` logic vs `SOFT` exploration).
*   **Output:** `GovernancePlacementVector` (GPV).
*   **Role:** Tells the system *how strict* to be.

---

## 4. The v51 Bridge Architecture

The MCP Server is now a **Thin Adapter** (The Head) attached to a **Thick Core** (The Body).

```mermaid
graph TD
    Client[Client (Claude/Kimi)] <-->|JSON-RPC| Transport[Stdio / SSE]
    Transport <--> Router[AAA MCP Server]
    
    subgraph "The Head (MCP Layer)"
        Router --> Tool_000[000_init]
        Router --> Tool_AGI[agi_genius]
        Router --> Tool_ASI[asi_act]
        Router --> Tool_APEX[apex_judge]
        Router --> Tool_999[999_vault]
    end
    
    subgraph "The Bridge (Transformation)"
        Tool_AGI <--> Bridge[v51_bridge.py]
        Tool_ASI <--> Bridge
        Tool_APEX <--> Bridge
    end
    
    subgraph "The Body (Core Engines)"
        Bridge <--> Engine_AGI[AGI Engine]
        Bridge <--> Engine_ASI[ASI Engine]
        Bridge <--> Engine_APEX[APEX Engine]
    end
    
    subgraph "The Law (Authority)"
        Engine_AGI -.-> Specs[AAA_MCP Specs]
        Engine_APEX -.-> Specs
    end
```

**Why this works:**
1.  **Universal:** The Client sees standard MCP JSON.
2.  **Modular:** The Core Logic is isolated in `arifos.core`. We can upgrade the Brain without breaking the Interface.
3.  **Agnostic:** The Adapter ensures no Python objects leak out—only pure data.

---

## 5. Execution Strategy
To achieve this architecture:
1.  **Refactor**: Implement `v51_bridge.py` (Option 1).
2.  **Rebrand**: Update Server Identity to `AAA-MCP`.
3.  **Expose**: Register `000_init` as both `Tool` and `Prompt`.

**Verification:**
*   Does `/000` work in Claude? (Prompt Check)
*   Does `000_init` tool work in CLI? (Tool Check)
*   Do `AAA_MCP` spec changes affect runtime? (Bridge Check)
