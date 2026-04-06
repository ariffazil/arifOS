# arifOS MCP GUI Mode - 000-999 Implementation Plan

## 000 - INIT: Understand the Current Structure

### Current Tools to Modify:
1. `init_anchor` — `/workspace/repos/arifosmcp/runtime/megaTools/tool_01_init_anchor.py`
2. `apex_judge` — `/workspace/repos/arifosmcp/runtime/tools.py` (line ~412)
3. `vault_ledger` — needs check

### Current Response Format:
```python
return {
    "verdict": "SEAL",
    "reasoning": "...",
    "telemetry": {...}
}
```

### Target Format (GUI Mode):
```python
return {
    "verdict": "SEAL",
    "system": "Operational",
    "_meta": {
        "outputType": "response",
        "outputTemplate": {...}
    }
}
```

---

## 111 - SENSE: Identify Files to Modify

| Step | File | Action |
|------|------|--------|
| 111.1 | `runtime/tools.py` | Add `mode` param to `apex_judge` |
| 111.2 | `runtime/megaTools/tool_01_init_anchor.py` | Add `mode` param |
| 111.3 | `core/kernel/mcp_tool_service.py` | Register GUI widgets |
| 111.4 | `server.py` | Add widget serving endpoint |

---

## 333 - MIND: Design the GUI Output Template

### Components to Support:
```python
GUI_COMPONENTS = {
    "header": {"type": "text", "font": {"size": "xl", "weight": "bold"}},
    "kpi_grid": {"type": "grid", "columns": 3, "children": ["stat", "stat", "stat"]},
    "stat": {"type": "stat", "title": str, "value": str},
    "badge": {"type": "badge", "label": str, "status": "success|warning|error"},
    "progress": {"type": "progress", "labels": [str], "values": [int]},
    "table": {"type": "table", "columns": [dict], "rows": [dict]},
}
```

### Dashboard Structure:
```python
{
    "type": "container",
    "kind": "vstack", 
    "children": [
        # Header
        {"type": "component", "kind": "text", "text": "🧠 arifOS APEX"},
        # Status badges
        {"type": "component", "kind": "hstack", "children": [...]},
        # KPIs
        {"type": "component", "kind": "grid", "columns": 3, "children": [...]},
        # Progress bars
        {"type": "component", "kind": "progress", "labels": [...], "values": [...]},
        # Verdicts table
        {"type": "component", "kind": "table", "columns": [...], "rows": [...]},
    ]
}
```

---

## 444 - ROUT: Implementation Order

### Phase 1: Core Infrastructure
1. Create `core/gui/dashboard_builder.py` — reusable UI builder
2. Create `core/gui/widgets.py` — widget definitions
3. Create `core/gui/__init__.py` — module init

### Phase 2: Tool Modification
4. Modify `apex_judge` in `runtime/tools.py` — add `mode="gui"`
5. Modify `init_anchor` — add GUI mode for session status
6. Modify `vault_ledger` — add GUI for audit log

### Phase 3: Server Integration
7. Add widget assets to `static/`
8. Add `_meta` to tool response schemas
9. Test with ChatGPT Apps SDK

---

## 555 - MEM: Store Implementation Notes

- GUI mode only active when `mode="gui"` passed
- Default behavior unchanged (`mode="text"`)
- Dashboard data fetched fresh from arifOS state
- Fallback to text if `_meta` not supported

---

## 666 - HEART: Safety Considerations

- **F2 (Truth)**: Dashboard shows real-time data, not cached/fake
- **F11 (Audit)**: GUI doesn't bypass audit logging
- **F12 (Resilience)**: If widget render fails, fallback to text

---

## 777 - OPS: Resource Estimation

- **Build**: ~50 lines for dashboard builder
- **Modify**: ~30 lines per tool (add mode param + GUI branch)
- **Test**: Need ChatGPT Plus to test Apps SDK
- **Deploy**: Push to GitHub, then pull on VPS

---

## 888 - JUDGE: Final Verdict

| Check | Status |
|-------|--------|
| Reversible? Yes — can rollback | ✅ |
| Grounded in evidence? Yes — uses real data | ✅ |
| W³ consensus? Need to verify | ⏳ |
| Clear? Yes — pattern is simple | ✅ |
| Not destructive? Yes — adds feature only | ✅ |

**Verdict**: SEAL ✅ — Proceed with implementation

---

## 999 - SEAL: Implementation Tasks

### Task List:
- [ ] Create `core/gui/dashboard_builder.py`
- [ ] Create `core/gui/widgets.py`
- [ ] Modify `apex_judge` — add `mode` param
- [ ] Modify `init_anchor` — add `mode` param  
- [ ] Test locally
- [ ] Push to GitHub
- [ ] Pull on VPS and restart

---

## Files to Create/Modify

```
arifOS/
├── core/
│   └── gui/
│       ├── __init__.py
│       ├── widgets.py        # NEW
│       └── dashboard_builder.py  # NEW
├── runtime/
│   ├── megaTools/
│   │   └── tool_01_init_anchor.py  # MODIFY
│   └── tools.py  # MODIFY
└── server.py  # MODIFY (if needed)
```