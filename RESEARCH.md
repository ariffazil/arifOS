# RESEARCH: MCP Tool Alignment & Schema Hardening

**Objective:** Align the 5 Core arifOS Tools (`000_init`, `agi_genius`, `asi_act`, `apex_judge`, `999_vault`) with MCP Protocol best practices, ensuring "Zero Context" usability for AI clients and fixing critical data loss in the current Railway Monolith (`sse.py`).

## 1. Current State Analysis

The current deployment (`sse.py`) uses **FastMCP** to wrap the core logic (`mcp_trinity.py`). However, the wrapper signatures in `sse.py` are **incomplete**, leading to data loss where arguments expected by the core engines are not exposed to the API.

### 🔴 Critical Gaps (Leaky Abstraction)

| Tool | `sse.py` Wrapper Args (Exposed) | `mcp_trinity.py` Implementation (Required) | **MISSING (Broken Features)** |
| :--- | :--- | :--- | :--- |
| **agi_genius** | `action`, `query`, `session_id`, `thought` | `draft`, `truth_score`, `context`, `axioms` | **F2 Evaluation** (needs `truth_score`), **F6 Clarity** (needs `draft`), **Atlas Map** (needs `axioms`) |
| **asi_act** | `action`, `text`, `session_id`, `proposal` | `stakeholders`, `sources`, `agi_result`, `witness_request_id` | **Empathy Modeling** (needs `stakeholders`), **Evidence** (needs `sources`), **Bridge** (needs `agi_result`) |
| **apex_judge** | `action`, `query`, `session_id`, `response` | `agi_result`, `asi_result`, `verdict`, `data` | **777 Eureka** (needs AGI/ASI results), **889 Proof** (needs `verdict`, `data`) |
| **init_000** | `action`, `query`, `session_id`, `authority_token` | `context` | **Memory Injection** (needs `context` pass-through) |
| **vault_999** | `action`, `session_id`, `verdict`, `target` | `data`, `query`, `init_result`, `agi_result`, ... | **Ledger Logging** (missing full context) |

## 2. MCP Schema Best Practices (Zero Context)

To ensure an LLM can use these tools without prior knowledge, the schema must be **self-describing**.

*   **Action Dispatch:** Since we are keeping the "5 Tool" architecture, we must clearly map `action` -> `required arguments` in the docstrings.
*   **Argument Completeness:** All potential arguments must be present in the Python signature (defaulting to `None` or empty defaults).
*   **Type Hinting:** Use `Dict[str, Any]` for complex objects (like `context`) to allow flexibility.

## 3. Proposed Hardening Strategy

We need to update `arifos/mcp/sse.py` to match the full superset of arguments defined in `mcp_trinity.py`.

### A. agi_genius (Mind)
**New Signature:**
```python
async def arifos_trinity_agi_genius(
    action: str = "sense",
    query: str = "",
    session_id: str | None = None,
    thought: str = "",
    # MISSING ARGS ADDED:
    draft: str = "",
    truth_score: float = 1.0,
    context: Dict[str, Any] | None = None,
    axioms: List[str] | None = None
) -> dict:
```

### B. asi_act (Heart)
**New Signature:**
```python
async def arifos_trinity_asi_act(
    action: str = "empathize",
    text: str = "",
    session_id: str | None = None,
    proposal: str = "",
    # MISSING ARGS ADDED:
    query: str = "",
    stakeholders: List[str] | None = None,
    sources: List[str] | None = None,
    agi_result: Dict[str, Any] | None = None,
    witness_request_id: str = "",
    approval: bool = False
) -> dict:
```

### C. apex_judge (Soul)
**New Signature:**
```python
async def arifos_trinity_apex_judge(
    action: str = "judge",
    query: str = "",
    session_id: str | None = None,
    response: str = "",
    # MISSING ARGS ADDED:
    verdict: str = "SEAL",
    data: str = "",
    agi_result: Dict[str, Any] | None = None,
    asi_result: Dict[str, Any] | None = None,
    agi_floors: List[Dict] | None = None,
    asi_floors: List[Dict] | None = None
) -> dict:
```

### D. 999_vault (Seal)
**New Signature:**
```python
async def arifos_trinity_999_vault(
    action: str = "seal",
    session_id: str | None = None,
    verdict: str = "SEAL",
    target: str = "seal",
    # MISSING ARGS ADDED:
    query: str = "",
    data: Dict[str, Any] | None = None,
    init_result: Dict[str, Any] | None = None,
    agi_result: Dict[str, Any] | None = None,
    asi_result: Dict[str, Any] | None = None,
    apex_result: Dict[str, Any] | None = None
) -> dict:
```

## 4. Next Steps (Planning)

1.  **Refactor `sse.py`**: Update all tool signatures to expose the full API surface.
2.  **Update Docstrings**: Rewrite docstrings to include "Zero Context" examples mapping actions to required arguments.
3.  **Verify Imports**: Ensure `List`, `Dict`, `Any` are imported.
4.  **Deploy**: The change is in `sse.py`, which is the entry point for the Docker/Railway build (`CMD ["uv", "run", "python", "-m", "arifos.mcp.sse"]`). Updating this file updates the live server.
