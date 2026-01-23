# arifOS Infrastructure & Architecture Reference

**Version:** v50.5.4 (Production Sovereign)
**Authority:** Muhammad Arif bin Fazil
**Last Updated:** January 23, 2026

---

## 1. System Identity: What is arifOS?

arifOS is not just a framework; it is a **Constitutional AI Operating System**. Unlike traditional AI agents that optimize for utility or speed, arifOS optimizes for **Governance** and **Wisdom**.

It implements a "Metabolic" runtime where raw intelligence (LLM tokens) is "digested" through strict constitutional floors before becoming action or truth.

**Motto:** *Ditempa Bukan Diberi* (Forged, Not Given)

---

## 2. Core Architecture: The 3 Pillars

The system is built on three non-negotiable foundations.

### 🏛️ Pillar I: The Trinity Engines (Separation of Powers)
We separate concerns into three distinct runtime engines to prevent any single point of failure or hallucination.

| Engine | Symbol | Role | Code Path | Responsibility |
|:---:|:---:|:---|:---|:---:|
| **AGI** | **Δ** | **Mind** | `arifos/core/agi/` | Reasoning, Logic, Planning, Truth Verification. |
| **ASI** | **Ω** | **Heart** | `arifos/core/asi/` | Empathy, Stakeholder Impact, Safety Gates. |
| **APEX** | **Ψ** | **Soul** | `arifos/core/apex/` | Final Judgment, Cryptographic Sealing, Entropy Control. |

### 🔄 Pillar II: The 000-999 Metabolic Loop
Information flows sequentially through 11 stages. It cannot skip stages. This ensures every thought is "cooled" and validated.

**The Pipeline:**
1.  **000 INIT** (Gate): Identity check, Injection Defense (F12).
2.  **111 SENSE** (AGI): Input parsing, Context enrichment.
3.  **222 THINK** (AGI): Hypothesis generation, Fact-checking (F2).
4.  **333 ATLAS** (AGI): Meta-cognition, Paradox detection (F7).
5.  **444 EVIDENCE** (APEX): Tri-Witness aggregation (Human/AI/Nature).
6.  **555 EMPATHY** (ASI): Impact simulation on weakest stakeholders (F6).
7.  **666 ACT** (ASI): Neuro-symbolic bridge, Execution safeguards.
8.  **777 EUREKA** (APEX): Novelty detection, Entropy extraction.
9.  **888 JUDGE** (APEX): **The Constitutional Verdict**. All floors checked.
10. **889 PROOF** (APEX): zkPC Receipt generation, Merkle hashing.
11. **999 VAULT** (Seal): Immutable storage, Cooling tower placement.

### ⚖️ Pillar III: The 13 Constitutional Floors
Every output must pass these mathematical/logic gates.

-   **F1 Amanah**: Auditability (Reversible?).
-   **F2 Truth**: Confidence ≥ 0.99.
-   **F3 Peace²**: Non-destructive (≥ 1.0).
-   **F4 Clarity**: Entropy Reduction (ΔS ≤ 0).
-   **F5-F13**: Empathy, Humility, Genius, Anti-Hantu, Ontology, Authority, Injection, Curiosity.

---

## 3. Codebase Anatomy & Infrastructure

### Directory Structure Mapping

```text
C:\Users\User\arifOS\
├── arifos/                      # SOURCE CODE (The Runtime)
│   ├── core/                    # The Brain
│   │   ├── metabolizer.py       # MAIN STATE MACHINE (Executes stages)
│   │   ├── floor_validators.py  # F1-F13 Logic
│   │   ├── memory/              # L0-L5 Storage (Cooling Tower)
│   │   └── [000-999]_stage/     # Individual Stage Implementations
│   │
│   ├── mcp/                     # The Interface (Model Context Protocol)
│   │   ├── trinity_server.py    # Exposes 5-Tool Trinity (The API)
│   │   └── tools/               # Standard MCP Tools
│   │
│   └── servers/                 # Standalone Uvicorn/FastAPI runners
│
├── 000_THEORY/                  # THE CONSTITUTION (Immutable Specs)
│   ├── 000_LAW.md               # The 13 Floors defined
│   ├── 000_ARCHITECTURE.md      # Topology Map
│   └── 001_AGENTS.md            # Agent Roles
│
├── AAA_MCP/                     # JSON Specs for MCP Tools
├── .antigravity/                # Agent Workspace (Gemini/Mind)
├── .claude/                     # Agent Workspace (Claude/Heart)
└── .codex/                      # Agent Workspace (Codex/Soul)
```

### Runtime Infrastructure

1.  **Language**: Python 3.10+ (Strict Type Checking)
2.  **Interface**: **MCP (Model Context Protocol)**
    *   **Stdio**: For local agent integration (Cursor, Windsurf).
    *   **SSE**: For remote connections (`python -m arifos.mcp trinity-sse`).
3.  **Deployment**:
    *   **Container**: Docker (optimized for Railway).
    *   **Orchestration**: `docker-compose` or Railway.toml.
4.  **Storage (The Cooling Tower)**:
    *   **L5 (Hot)**: Redis (Session State).
    *   **L3 (Warm)**: PostgreSQL / Supabase (Operational Logs).
    *   **L0 (Cold)**: Local Ledger / Git / Immutable Append-Only Logs.

---

## 4. Operational Flows (How it works)

### The "5-Tool Trinity" Workflow
External agents (like Gemini or Claude) do not need to know the complex 000-999 loop. They use 5 simplified tools that map to the underlying complexity:

1.  **`000_init`**: Starts a session, validates user authority.
2.  **`agi_genius`**: Triggers SENSE → THINK → ATLAS. Returns reasoning & plan.
3.  **`asi_act`**: Triggers EVIDENCE → EMPATHY → ACT. Validates safety & executes.
4.  **`apex_judge`**: Triggers EUREKA → JUDGE → PROOF. Renders the final verdict.
5.  **`999_vault`**: Commits the result to history.

### The "Sovereign" Check
Before any action is taken, the **Metabolizer** (`arifos.core.metabolizer`) checks:
1.  **Is F11 Valid?** (Command Authority)
2.  **Is F12 Clear?** (No Injection Attacks)
3.  **Is Sequence Correct?** (Cannot jump from 111 to 999)

---

## 5. Changelog & Current Status (v50.5)

### v50.5 (Current - Jan 2026)
*   **Feature**: **Trinity Consolidation**. Merged complex toolsets into the "5-Tool" standard.
*   **Fix**: **Metabolizer Execution**. `metabolizer.py` now dynamically imports and *executes* stage logic, rather than just tracking state.
*   **Infra**: Added `trinity-sse` support for remote MCP access.

### v50.0 (Major Milestone)
*   **Architecture**: Introduced the **AHA Principle** (Akal, Haluan, Hikmah) and **APEX Telemetry** (Akal, Present, Energy, Exploration).
*   **Governance**: Sealed the "Three Foundations of Governed Intelligence".

### Upcoming (Roadmap)
*   **v51**: **zkPC** (Zero-Knowledge Proof of Cognition).
*   **v52**: **Phoenix-72 Automation**.

---

**For Developers:**
*   **Start Here**: `python -m arifos.mcp trinity` (Runs the server)
*   **Debug**: Check `metabolizer.py` for pipeline logic.
*   **Config**: See `constitutional_constants.py` for floor thresholds.
