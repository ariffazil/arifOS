# arifos_route_query — Integration Patch Guide

**Author:** OMEGA (Ω) — 2026-06-08
**Status:** 4 source files forged, integration pending F13 audit

## Files Created (4 new files, 0 modifications to existing)

### 1. `route_policy.py` (380 lines)
Deterministic routing engine. No LLM. Pure rules.
- QueryLane enum: EXPLOIT / EXPLORE / HYBRID
- RouteReason enum: 5 priority-ordered rules
- RoutePolicyEngine: `decide()` method with classification + fallback
- DualLaneBudget with hard floor enforcement
- RouteAuditEntry: structured audit per decision

### 2. `route_query_handler.py` (227 lines)
FastMCP-compatible handler with Pydantic v2 I/O schemas.
- RouteQueryInput / RouteQueryOutput models
- `arifos_route_query()` async handler
- Session management: `reset_route_session()`, `get_route_status()`

### 3. `route_audit.py` (221 lines)
F11-compliant structured audit logger.
- RouteAuditRecord: full provenance fields
- RouteAuditLogger: thread-safe, JSONL output, memory ring buffer
- Hash-chained audit entries (VAULT999-style)
- `log_route_decision()` convenience function

### 4. `route_guard_middleware.py` (208 lines)
Pre-retrieval enforcement gate.
- GATED_TOOLS: 14 tools require prior routing
- PASSTHROUGH_TOOLS: 9 tools always allowed
- RouteGuardState: per-session tracking with TTL
- `create_route_guard_middleware()` factory
- Integration hooks: `mark_session_routed()`, `on_arifos_route_query_complete()`

## Integration Steps (for constitutional_map.py)

### A. Add to CANONICAL_TOOLS (after line ~540)

```python
    "arifos_route_query": {
        "name": "arifos_route_query",
        "description": (
            "000_PRE_ROUTE: Mandatory pre-retrieval routing gate. "
            "Call this BEFORE any search/discovery tool. Determines "
            "exploit/explore/hybrid lane via deterministic rules, "
            "enforces dual-lane budget floors, and ensures contradiction "
            "quota compliance. F2 TRUTH: deterministic, no LLM. "
            "F4 CLARITY: structured routing plan output. "
            "Parameters: query, mode (exploit|explore|hybrid), "
            "session_id, actor_id, require_contradiction."
        ),
        "access": "public",
        "stage": ToolStage.INIT,        # Runs at session start, like session_init
        "lane": TrinityLane.AGI,
        "floors": [
            Law.L01_AMANAH,
            Law.L02_TRUTH,
            Law.L04_CLARITY,
            Law.L07_HUMILITY,
            Law.L11_AUDIT,
        ],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["exploit", "explore", "hybrid"],
        "eureka_insight": (
            "Contrast primitive: every query needs both exploit and explore lanes. "
            "F2: deterministic routing, no LLM vibes. "
            "F4: structured output with target tools + budgets. "
            "F11: every routing decision logged with full provenance."
        ),
        "cognitive_axis": "route",
        "expose": True,
    },
```

### B. Add to _TOOL_ANNOTATIONS (after line ~826)

```python
    "arifos_route_query": {
        "title": "Route Query",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
```

## Integration Steps (for tools.py)

### C. Add handler import (after existing imports)

```python
from .route_query_handler import arifos_route_query as _arifos_route_query
```

### D. Add to _CANONICAL_HANDLERS (line ~12882)

```python
    "arifos_route_query": _arifos_route_query,
```

### E. Update handler count check

Change:
```python
if len(_CANONICAL_HANDLERS) != 13:
    raise RuntimeError(f"Expected 13 canonical handlers, found {len(_CANONICAL_HANDLERS)}")
```
To:
```python
if len(_CANONICAL_HANDLERS) != 14:
    raise RuntimeError(f"Expected 14 canonical handlers, found {len(_CANONICAL_HANDLERS)}")
```

## Runtime Wiring

### F. In server.py or tools.py main execution path:

After successful `arifos_route_query` call, invoke the guard hook:
```python
from arifosmcp.runtime.route_guard_middleware import on_arifos_route_query_complete
# After handler returns:
if tool_name == "arifos_route_query" and result.get("next_action") == "proceed":
    on_arifos_route_query_complete(result)
```

### G. Wire route guard middleware into tool dispatch:

```python
from arifosmcp.runtime.route_guard_middleware import create_route_guard_middleware

def get_session_id():
    return current_session_id  # from request context

route_guard = create_route_guard_middleware(get_session_id)

# In tool dispatch:
def dispatch_tool(tool_name, args):
    block = route_guard(tool_name, args)
    if block:
        return block  # HOLD — routing not performed
    return actual_handler(tool_name, args)
```

## Verification

```bash
# 1. Check all files compile:
python3 -c "import ast; [ast.parse(open(f'/root/arifOS/arifosmcp/runtime/{f}').read()) for f in ['route_policy.py','route_audit.py','route_query_handler.py','route_guard_middleware.py']]"

# 2. After integration, verify tool count:
curl -s http://localhost:8088/tools | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Tools: {len(d[\"tools\"])}')"
# Expected: 14

# 3. Test routing:
curl -s -X POST http://localhost:8088/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"arifos_route_query","arguments":{"query":"find evidence that contradicts our Malay Basin depth model"}}}'
```

## DITEMPA BUKAN DIBERI
