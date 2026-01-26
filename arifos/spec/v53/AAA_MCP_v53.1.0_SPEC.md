# AAA MCP Architecture v53.1.0-CODEBASE

**Authority:** Δ Antigravity
**Status:** SEALED (Production)
**Protocol:** JSON-RPC 2.0 via HTTP/SSE
**Date:** 2026-01-26

## 1. Overview (Hybrid Architecture)
v53 introduces the **Codebase Microservices** architecture, enabling modular, independent execution while verified by the Constitutional Monolith.

- **Frontend:** Codebase MCP (`codebase/mcp/`)
- **Backend:** Proxy Kernels (`codebase/engines/`) -> Monolith (`arifos/core/`)
- **Transport:** Railway HTTP/SSE (`codebase/mcp/sse.py`)

## 2. Trinity Triad (Standardized Interface)
All engines (AGI/ASI/APEX) now implement the **Physics-Math-Language** triad.

| Capability | Intent key | Description |
| :--- | :--- | :--- |
| **Physics** | `physics` | **Reasoning & Modelling.** Understanding the causal reality of a query. |
| **Math** | `math` | **Measurement & Scoring.** Quantifying truth, ethics, and confidence (0-1). |
| **Language** | `language` | **Action & Projection.** Executing the will or rendering a verdict. |

## 3. Tool Specifications

### 3.1 AGI Genius (The Mind)
**Endpoint:** `agi_genius`
**Actions:**
*   `sense` (Input Classification)
*   `think` (Deep Reasoning)
*   `predict` / `physics` (Modeling Reality)
*   `measure` / `math` (Truth Scoring)
*   `forge` / `language` (Response Generation)

### 3.2 ASI Act (The Heart)
**Endpoint:** `asi_act`
**Actions:**
*   `evidence` (Fact Checking)
*   `empathize` / `physics` (Emotional Modeling)
*   `measure` / `math` (Empathy/Peace Scoring)
*   `act` / `language` (Safe Execution)
*   `harmonize` (Conflict Resolution)

### 3.3 APEX Judge (The Soul)
**Endpoint:** `apex_judge`
**Actions:**
*   `eureka` / `redeem` (Insight/Redemption)
*   `judge` / `physics` / `language` (Verdict Rendering)
*   `entropy` / `measure` / `math` (Confidence Scoring)

## 4. Constitutional Physics (Quantum Layer)
The system enforces **Kimi's Orthogonal Directive**:
> "Physics, Math, and Language are the orthogonal basis vectors of Intelligence."

Every action is decomposed into these three components before execution.

## 5. Deployment
- **Command:** `codebase-mcp-sse`
- **Env:** `ARIFOS_VERSION=v53.1.0-CODEBASE`
- **Port:** 8000

---
*DITEMPA BUKAN DIBERI*
