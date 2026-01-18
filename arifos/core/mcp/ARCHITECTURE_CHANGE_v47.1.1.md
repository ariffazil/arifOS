# MCP Architecture v47.1.1: Pydantic Serialization Boundary

**Quick Reference:** Architectural change enforcing JSON serialization at MCP server boundary.

## Change Summary

**File:** `arifos_core/mcp/unified_server.py:1298-1318`
**Pattern:** Serialize Pydantic → JSON at MCP transport boundary
**Impact:** All 17 MCP tools

## Code Change

```python
@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]):
    result = run_tool(name, arguments)

    # NEW: Serialize Pydantic models to dicts
    from pydantic import BaseModel
    if isinstance(result, BaseModel):
        return result.model_dump() if hasattr(result, 'model_dump') else result.dict()

    return result
```

## Why This Matters

**Before:** MCP clients (Antigravity, Claude) received tuples `[('verdict', 'ERROR')]`
**After:** MCP clients receive proper dicts `{"verdict": "ERROR"}`

**Root Cause:** Pydantic models weren't serialized before crossing MCP wire protocol.

## Architectural Pattern

```
Tool (Pydantic) → Server (Serialize) → Client (JSON)
                        ▲
                 Boundary enforcement
```

Tools use rich types internally, server ensures wire compliance.

---

**See:** `docs/EUREKA_MCP_PYDANTIC_SERIALIZATION_FIX_20260118.md` for full analysis.
