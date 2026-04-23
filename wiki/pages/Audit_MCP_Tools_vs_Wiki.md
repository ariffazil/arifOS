---
type: Synthesis
tier: 50_AUDITS
strand:
- operations
audience:
- engineers
difficulty: intermediate
prerequisites:
- MCP_Tools
tags:
- audit
- MCP
- tools
- wiki
- alignment
- drift
sources:
- APEX/ASF1/tool_registry.json
- tool_specs.py
- tools.py
- public_registry.py
- server.py
- resources.py
- kernel_runtime.py
- wiki/raw/mcp_naming_migration_audit_directive_2026-04-11.md
last_sync: '2026-04-11'
confidence: 0.97
---

# Audit: MCP Tools vs Ω-Wiki Alignment

> **Auditor**: Copilot CLI  
> **Date**: 2026-04-11  
> **Motto**: *DITEMPA BUKAN DIBERI*  
> **Review Status**: ⚠️ CONTRAST ACTIVE — full deployment audit still required

---

## 1. Current Verdict

The wiki can now reflect the **current repo truth**, but the naming migration cannot yet be treated as sealed.

**Registry truth** and **runtime truth** are still different:

- the registry target is a **10-tool public canon**
- the runtime still carries older public/transitional surfaces
- the wiki should document that contrast instead of pretending it is resolved

---

## 2. Registry Truth vs Runtime Truth

| Layer | Evidence | Finding | Severity |
|------|----------|---------|----------|
| Registry | `APEX/ASF1/tool_registry.json` | Declares exactly 10 public canonical tools and 5 internal folded tools | INFO |
| Runtime spec | `arifosmcp/runtime/tool_specs.py` → `PUBLIC_TOOL_SPECS = TOOLS` | Runtime export still follows full tuple, not the 10-tool registry split | HIGH |
| Public registry | `arifosmcp/runtime/public_registry.py` → `EXPECTED_TOOL_COUNT = 11` | Discovery contract still expects older count | HIGH |
| Server instructions | `arifosmcp/runtime/server.py` docstring + instructions | Server narrative still advertises 11 canonical tools, dotted ids, and `arifos_reply` | HIGH |
| Runtime handlers | `arifosmcp/runtime/tools.py` | Legacy/transitional handlers and aliases still present for `arifos_reply`, `arifos_vps_monitor`, `arifos_route`, dotted names | WARN |
| Resource discovery | `arifosmcp/runtime/resources.py` | Public/internal surface still organized around `arifos_route` and `arifos_vps_monitor` | WARN |

**Finding**: the migration is **not yet runtime-coherent**.

---

## 3. Canonical Public Target

| Canonical public tool |
|-----------------------|
| `arifos_init` |
| `arifos_sense` |
| `arifos_mind` |
| `arifos_kernel` |
| `arifos_heart` |
| `arifos_ops` |
| `arifos_judge` |
| `arifos_memory` |
| `arifos_vault` |
| `arifos_forge` |

Everything else should be treated as alias, internal-only, deprecated, dead, substrate mode, or unresolved ambiguity until the audit proves otherwise.

---

## 4. Transitional Surfaces Still Requiring Classification

| Surface | Evidence | Current Classification |
|--------|----------|------------------------|
| `arifos_reply` | `tool_specs.py`, `tools.py`, `server.py` | internal-only candidate / fold into `arifos_kernel(mode="reply")` |
| `arifos_vps_monitor` | `tool_specs.py`, `tools.py`, `resources.py`, `server.py` | internal-only candidate / fold into `arifos_ops(mode="monitor")` |
| `arifos_route` | `tools.py`, `kernel_runtime.py`, `server.py`, `rest_routes.py` | alias or compatibility surface for `arifos_kernel` |
| dotted `arifos_*` tool names | `tools.py`, `kernel_router.py`, `server.py` | legacy alias layer |

---

## 5. Wiki Position After This Update

The wiki should now say:

1. the intended public canon is 10 tools
2. the repo runtime still contains legacy/transitional surfaces
3. a master audit must prove registry/runtime/deployment truth before seal

That is a better F2 posture than declaring the migration done.

---

## 6. Proposed Next Action

Run one **constitutional deployment audit** with five explicit truth lanes:

1. registry truth
2. runtime truth
3. reachability truth
4. deployment truth
5. client-surface truth

The audit should answer:

- are the 10 canonical public tools real in runtime
- what is still alias-only or internal-only
- what is orphaned, duplicated, or stale
- whether deployment matches repo truth

If deployment cannot be verified, the audit must say:

`DEPLOYMENT STATUS: CANNOT VERIFY FROM CURRENT EVIDENCE`

---

## 7. Proposed Long-Term Doctrine (Not Yet Sealed)

The most coherent target public architecture remains **Machine Governance Intelligence 3x3 + 1**:

| Stage / Lane | Reality | Intelligence | Governance |
|--------------|---------|--------------|------------|
| Ingest | `arifos_init` | `arifos_memory` | `arifos_sense` |
| Deliberate | `arifos_ops` | `arifos_mind` | `arifos_heart` |
| Act | `arifos_forge` | `arifos_kernel` | `arifos_judge` |

Plus one sovereign boundary:

- `arifos_vault`

But this is **target doctrine**, not current verified deployment truth.

---

## 8. Seal State

| Question | Answer |
|---------|--------|
| Wiki aligned to current repo contrast? | ✅ |
| Registry/runtime fully aligned? | ❌ |
| Deployment verified? | ❌ not from current evidence in this page |
| Naming migration seal-ready? | ❌ HOLD |

**Blockers**:

- runtime export still diverges from registry target
- discovery count still reflects older public surface
- transport/server narrative still leaks legacy assumptions
- deployment truth still requires explicit verification

---

## 9. Audit Trail

| Date | Auditor | Action |
|------|---------|--------|
| 2026-04-08 | Ω-Auditor Agent | Earlier alignment audit page created |
| 2026-04-11 | Copilot CLI | Rewrote page to document migration contrast and audit-first next step |

---

> [!NOTE]
> Do not propose architectural redesign until current-state truth is proven with evidence.

**F11**: Logged in `wiki/log.md`  
**F2**: Claims traceable to registry/runtime files and the ingested audit directive
