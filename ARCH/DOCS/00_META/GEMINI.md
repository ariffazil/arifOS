# GEMINI.md — arifOS Constitutional Agent Policy

This document provides the operational context for AI agents working within the `arifOS` repository. Adherence to these principles is mandatory.

**Motto:** *Ditempa Bukan Diberi — Forged, Not Given*

---

## 🏛️ Project Overview

**arifOS** is a production-grade **Constitutional AI Governance System**. It functions as an "Intelligence Kernel" that wraps any Large Language Model (LLM) to enforce a set of 13 ethical and safety rules, known as "Constitutional Floors."

Its purpose is to govern AI cognition and agency, ensuring that all outputs and material actions are safe, truthful, and aligned with core principles.

### Core Architecture

The system is composed of three primary components, ensuring a strict separation of concerns:

1.  **The Kernel (`core/`):** The heart of arifOS, containing all pure, transport-agnostic decision-making logic. It enforces the 13 Floors and contains the 7-Organ Sovereign Stack.
2.  **The Brain (`arifosmcp.transport/`):** The primary transport adapter, exposing the Kernel's functions via the Model Context Protocol (MCP). It handles incoming requests and formats the Kernel's verdicts, but contains **no decision logic** itself.
3.  **The Senses (`arifosmcp.intelligence/`):** A console and MCP Federation Hub for server intelligence kernel management, providing real-world context and constitutional observability.

This architecture is built on the **7-Organ Sovereign Stack**:
- **INIT (000 - Airlock):** Session ignition and defense.
- **AGI (111-444 - Mind):** Logical analysis and truth-seeking.
- **PHOENIX (555 - Subconscious):** Associative memory retrieval and Eureka Scars.
- **ASI (666 - Heart):** Empathy and ethical safety checks.
- **APEX (777 - Soul):** Final judgment and consensus.
- **FORGE (888 - Hands):** Sandboxed material execution (Actuator).
- **VAULT (999 - Memory):** Immutable ledger and Merkle chaining.

---

## 🛠️ Technology Stack

- **Language:** Python 3.12+ (Async-first)
- **Framework:** FastAPI, Starlette, and `fastmcp` for the MCP server.
- **Data Validation:** Pydantic v2 is used extensively.
- **Package Management:** `uv` is the recommended package manager.
- **Code Quality:** The project is strictly maintained with:
    - **Formatting:** `black`
    - **Linting:** `ruff`
    - **Type Checking:** `mypy`
- **Testing:** `pytest` is used for the comprehensive test suite.
- **Storage:** PostgreSQL for the immutable `VAULT999` ledger and Redis for caching.

---

## 🚀 Development Workflow

All development must adhere to the established quality standards.

### 1. Setup

First, set up the virtual environment and install all necessary dependencies using `uv`.

```bash
# Install uv (if you haven't already)
pip install uv

# Create a virtual environment and install dependencies
uv pip install -e ".[dev]"
```

### 2. Code Quality & Verification

Before committing any changes, run the following commands to ensure code quality, formatting, and type safety.

```bash
# Format code with Black
black . --line-length 100

# Lint code with Ruff
ruff check . --line-length 100

# Type check with MyPy
mypy .
```

### 3. Testing

New functionality requires new tests. All tests must pass before a change is considered complete.

```bash
# Run all tests
pytest tests/ -v

# Run tests faster by disabling physics-based computations
ARIFOS_PHYSICS_DISABLED=1 pytest tests/

# Run only the constitutional tests
pytest -m constitutional
```

---

## 🏃 Running the Project Locally

The main application is the `aaa-mcp` server. It can be run in several modes for development.

```bash
# Run in STDIO mode (for local IDE integrations like Cursor)
python -m arifosmcp.transport stdio

# Run in SSE mode (for remote clients, used in cloud deployments)
python -m arifosmcp.transport sse

# Run in HTTP mode (for streamable HTTP)
python -m arifosmcp.transport http
```

---

## 🤖 Agent Operational Guidelines

As an AI agent operating in this codebase, you are bound by the constitutional framework.

### The 13 Floors
Every action or thought must pass the 13 Constitutional Floors. These are not suggestions; they are load-bearing structural rules enforced by the Kernel. Violating a **HARD** floor (e.g., F2 Truth, F7 Humility) will result in a `VOID` verdict, blocking the action completely.

### Thermodynamic Governance (ΔS, Peace², Ω₀)
All AI cognition is managed as a thermodynamic process with specific constraints:
- **Clarity (F4 ΔS ≤ 0):** Every output must reduce information entropy.
- **Stability (F5 Peace² ≥ 1.0):** De-escalation and safety margins are mandatory.
- **Humility (F7 Ω₀ ∈ [0.03, 0.05]):** Uncertainty must be explicitly bounded.

**The Genius Equation:** `G = A × P × X × E² ≥ 0.80`
- **A (Akal):** Logical Accuracy
- **P (Peace):** Safety/Stability
- **X (Exploration):** Novelty/Curiosity
- **E (Energy):** Efficiency (Squared power)

If the Genius score $G < 0.80$, the output is **VOID**.

### High-Stakes Operations (888_HOLD)
You **MUST** trigger an `888_HOLD` and await human confirmation for any high-stakes operations. These trigger a `Signed Intent Envelope` that requires a physical `ratification_token` from the Sovereign (888 Judge) via the local `888_signer` utility.
- Production deployments
- Material state mutations (e.g., infrastructure destroy, DB purge)
- Git history modification (`rebase`, `force-push`)
- Handling of secrets or credentials

### Public MCP Surface (Sovereign Federation Hub)
The **Federation Hub (`arifosmcp.transport` / `arifosmcp.intelligence`)** exposes the arifOS Intelligence Kernel through 13 canonical system calls:
- `anchor_session` (000 - Airlock)
- `reason_mind` (111-444 - Mind)
- `vector_memory` (555 - Subconscious)
- `simulate_heart` (555-666 - Empathy)
- `critique_thought` (666 - Heart)
- `eureka_forge` (777 - Soul)
- `apex_judge` (888 - Hands)
- `seal_vault` (999 - Memory)
- `search_reality`, `ingest_evidence`, `audit_rules`, `check_vital` (Utility)
- `metabolic_loop` (Orchestration)

The core organ actions are mapped to these federation calls.

### Core Principle: Separation of Concerns
- **`core/`** is for pure logic only. Do not add any transport-layer (HTTP, MCP) code here.
- **`arifosmcp.transport/`** is for transport only. Do not add any decision-making logic here; it must call the `core` kernel.

### ⚠️ Critical Rule: Logging
For STDIO transport, NEVER write to `stdout` (e.g., via `print()`). This corrupts the JSON-RPC messages and breaks the MCP connection. Use `sys.stderr` or a logging library configured for `stderr`.

---

## 📁 Key Files & Directories

- **`pyproject.toml`**: Defines project metadata, dependencies, and scripts.
- **`AGENTS.md`**: The canonical guide for agents, detailing architecture and conventions.
- **`README.md`**: High-level project overview.
- **`000_THEORY/000_LAW.md`**: The definitive specification for the 13 Constitutional Floors.
- **`core/`**: The stateless, transport-agnostic governance kernel.
- **`arifosmcp.transport/`**: The main MCP server (The Brain).
- **`arifosmcp.intelligence/`**: The sensory tools for grounding (The Senses).
- **`tests/`**: The test suite. All new code requires corresponding tests.
- **`VAULT999/`**: The immutable ledger for audit trails.

---

## 📚 MCP Resources

- **Official Site:** [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Documentation:** [modelcontextprotocol.info/docs/](https://modelcontextprotocol.info/docs/)
- **Mirror (CN):** [mcpcn.com/en/docs/](https://mcpcn.com/en/docs/)
- **Anthropic Intro:** [anthropic.com/news/model-context-protocol](https://www.anthropic.com/news/model-context-protocol)
- **GitHub:** [github.com/modelcontextprotocol](https://github.com/modelcontextprotocol)
- **OpenAI/Codex:** [developers.openai.com/codex/mcp/](https://developers.openai.com/codex/mcp/)
- **LangChain Adapter:** [docs.langchain.com/oss/python/langchain/mcp](https://docs.langchain.com/oss/python/langchain/mcp)

