# Rollback Plan — Phase 1 Tool Surface Clarity

## Items Deployed

| Item | Files Changed | Reversible? |
|------|--------------|-------------|
| A — JSON Schema enums | `runtime/tools.py`, `server.py`, `constitutional_map.py` | ✅ |
| D — Auto-generated llms.txt | `scripts/generate_tool_manifest.py`, `llms.txt` | ✅ |
| V — Verification harness | `scripts/verify_tool_surface.py` | ✅ |
| Health endpoint fields | `runtime/rest_routes/rest_routes.py`, `server.py` | ✅ |

## Rollback Steps (in order)

### 1. Revert runtime/tools.py enum injection
- Remove the enum injection block (lines ~15010-15031) in `register_tools()`
- Revert: `git checkout -- arifosmcp/runtime/tools.py` (if committed)
- Or restore from `/root/arifOS/.git` stash

### 2. Revert server.py Hermes enum injection
- Remove the Hermes enum injection block (~lines 828-842)
- Revert: `git checkout -- arifosmcp/server.py`

### 3. Revert health endpoint
- Remove canonical_tools_loaded, tools_exposed_via_mcp, canonical_tools, operational_tools fields
- Remove `_count_mcp_tools()` helper
- Revert: `git checkout -- arifosmcp/runtime/rest_routes/rest_routes.py`
- Revert server.py register_rest_routes call signature

### 4. Revert llms.txt
- `git checkout -- llms.txt` (restores old static version)

### 5. Revert constitutional_map.py (if required fields were added)
- `git checkout -- arifosmcp/constitutional_map.py`

### 6. Deploy revert
```bash
rsync -av /root/arifOS/arifosmcp/ /opt/arifos/app/arifosmcp/
systemctl restart arifos
```

### 7. Verify revert
```bash
python3 scripts/verify_tool_surface.py
# Expected: C3 (enums) now FAILS, C4 (health split) now FAILS
# That confirms rollback
```

## Key Risk
Clients that started relying on `canonical_tools_loaded` or enum fields will lose them on rollback. Mitigation: announce via commit message, then restore.
