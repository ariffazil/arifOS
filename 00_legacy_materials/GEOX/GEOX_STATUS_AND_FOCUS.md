# GEOX Status & Strategic Focus

> **Date:** 2026-04-10
> **Assessment:** External audit integrated
> **Strategic Pivot:** MCP-first, governance-core
> **Seal:** DITEMPA BUKAN DIBERI

---

## Executive Summary

**Status:** 3 components architected, 2 production-grade, 1 in forge

| Component | Grade | Focus |
|-----------|-------|-------|
| Governance (ToAC, AC_Risk) | ✅ PRODUCTION | Maintain, integrate |
| MCP Server (Tools) | 🟡 PRODUCTION-CAPABLE | **HARDEN NOW** |
| MCP Apps (UI) | 🔴 ARCHITECTURE ONLY | **Forge one flagship** |
| Web Site | 🟡 SPEC'D | Defer until MCP locked |

**Strategic Pivot:** GEOX is not a Petrel competitor. GEOX is the **governance and risk brain** that sits on top of, or next to, legacy subsurface stacks.

---

## 1. Current Status (Brutal Truth)

### ✅ PRODUCTION: Governance & Theory
**What's Working:**
- ToAC (Theory of Anomalous Contrast) — implemented, documented
- AC_Risk calculator — tested, formula locked
- Verdict system (SEAL/QUALIFY/HOLD/VOID) — enforced in code
- Constitutional floors (F1-F13) — active in all tools

**Evidence:**
```python
# Working test output
AC_Risk = 0.252 → QUALIFY
"Moderate risk. Proceed with caveats."
```

**Comparative Advantage:**
- Petrel/DG/PaleoScan: No epistemic risk as first-class
- GEOX: AC_Risk calculated for every operation

### 🟡 PRODUCTION-CAPABLE: MCP Server
**What's Working:**
- `geox_load_seismic_line` — LIVE
- `geox_build_structural_candidates` — LIVE
- `geox_compute_ac_risk` — LIVE
- `geox_feasibility_check` — LIVE
- `geox_verify_geospatial` — LIVE

**What's Scaffolded:**
- `geox_georeference_map` — core works, needs hardening
- `geox_interpret_single_line` — mock VLM backend

**Gap Analysis:**
| Capability | Status | Gap |
|------------|--------|-----|
| Tool discovery | 🟡 Partial | Needs `list_tools` standardization |
| Error semantics | 🟡 Basic | Needs structured error codes |
| Versioning | 🔴 Missing | No API versioning strategy |
| Schema validation | 🟡 Present | Needs stricter enforcement |
| Auth | 🟡 JWT | Needs rotation, scopes testing |

### 🔴 ARCHITECTURE ONLY: MCP Apps
**What's Defined:**
- 3 app manifests (Basin Explorer, Seismic Viewer, Well Context Desk)
- 9 prefab views (UI component blueprints)
- Manifest schema (JSON spec complete)

**What's Missing:**
- ❌ No HTML/JS app implementations
- ❌ No hosted resources at URIs
- ❌ No host adapter testing (Claude/goose/VS Code)
- ❌ No bidirectional event wiring

**Verdict:** Architecture is solid. Implementation is absent.

### 🟡 SPEC'D: Web Site
**Status:** Complete specification, not built
**Decision:** **DEFER** until MCP server is rock-solid

**Rationale:**
- Web site without working MCP = "sudo features"
- MCP server working = agents can use GEOX immediately
- WebMCP is Phase 3, not Phase 1

---

## 2. Strategic Focus (Highest EMV/NPV)

### Priority 1: Harden GEOX as Serious MCP Server
**Goal:** Become the "ultimate subsurface MCP server" — drop-in for any agent

**Specific Tasks:**

#### 1.1 Tool Catalog Stability
```python
# Current: Tools scattered across files
# Target: Centralized registry with metadata

GEOX_TOOL_REGISTRY = {
    "geox_load_seismic_line": {
        "version": "1.0.0",
        "schema": LoadSeismicLineInput,
        "error_codes": ["FILE_NOT_FOUND", "INVALID_FORMAT", "SCALE_UNKNOWN"],
        "ac_risk_enabled": True,
        "floors": ["F1", "F2", "F4", "F7", "F9"]
    },
    # ... all tools
}
```

**Actions:**
- [ ] Create unified tool registry
- [ ] Add version to all tool outputs
- [ ] Standardize error codes (follow MCP spec)
- [ ] Implement `list_tools` with rich metadata
- [ ] Add `tool_details` endpoint

#### 1.2 End-to-End Agent Workflows
**Target Workflow:**
```
User: "I have this seismic section PNG"
  ↓
Agent: calls geox_load_seismic_line
  ↓
GEOX: returns contrast views + AC_Risk + verdict
  ↓
Agent: calls geox_build_structural_candidates
  ↓
GEOX: returns 3 hypotheses + confidence bands
  ↓
Agent: presents to user with governance context
```

**Actions:**
- [ ] Document 3 standard workflows
- [ ] Create agent prompt templates
- [ ] Test with Claude Desktop
- [ ] Test with goose
- [ ] Publish integration guide

#### 1.3 Integration Docs
**Target:** Clear path for agents to adopt GEOX

**Actions:**
- [ ] "Connect GEOX to Claude" guide
- [ ] "Connect GEOX to goose" guide
- [ ] "Connect GEOX to Petrel exports" guide
- [ ] Video: 5-minute agent setup

**Timeline:** 2 weeks
**EMV:** HIGH — any MCP-compatible agent becomes GEOX-aware

---

### Priority 2: One Flagship MCP App (AC_Risk Console)
**Goal:** Prove "GEOX + MCP Apps" with one high-value interactive app

**Why AC_Risk Console:**
- Light UI (sliders, fields, text) — no heavy graphics
- Works across all use-cases (seismic, maps, digitization)
- Shows what Petrel/DG/PaleoScan DON'T have: in-chat risk exploration
- Minimal dependencies: HTML + JS + MCP bridge

**Features:**
```
UI Components:
├── U_phys slider (0.0 - 1.0)
├── D_transform selector (transform checklist)
├── B_cog selector (expertise level)
├── Calculate button
├── Result panel:
│   ├── AC_Risk score (big number)
│   ├── Verdict badge (SEAL/QUALIFY/HOLD/VOID)
│   ├── Explanation text
│   └── Suggested mitigations
└── History: previous calculations
```

**Technical Stack:**
- Vanilla JS (no framework bloat)
- MCP App SDK (host adapter)
- Hosted at: `geox.arif-fazil.com/apps/ac-risk-console/`

**Actions:**
- [ ] Implement HTML/JS UI
- [ ] Wire to `geox_compute_ac_risk` tool
- [ ] Test in Claude Desktop (inline)
- [ ] Test in goose (inline)
- [ ] Test external fallback

**Timeline:** 2 weeks
**EMV:** HIGH — demonstrates unique governance value

---

### Priority 3: Protocol Bridges to Legacy Tools
**Goal:** GEOX as governance layer ON TOP of Petrel/DG/PaleoScan

**Concept:**
```
Petrel → export horizons/attributes → GEOX → AC_Risk + ToAC audit → Decision support
```

**Integrations:**

#### Petrel Bridge
```python
# Accept Petrel exports
geox_audit_petrel_export(
    grid_file=".grd",
    horizon_file=".hrz",
    well_tops=".txt"
)
# Returns: AC_Risk, alternative interpretations, bias warnings
```

#### DecisionSpace Geo (DSG) Bridge
```python
geox_audit_dsg_interpretation(
    project_path="...",
    interpretation_id="..."
)
```

#### PaleoScan Bridge
```python
geox_audit_paleoscan_rgt(
    rgt_volume="...",
    horizons="..."
)
```

**Actions:**
- [ ] Document export formats for each tool
- [ ] Build `geox_audit_legacy_interpretation` tool
- [ ] Create comparison: GEOX risk vs tool-native confidence
- [ ] Case study: Petrel → GEOX → better decision

**Timeline:** 4 weeks
**EMV:** VERY HIGH — ride installed base, don't replace

---

### Priority 4: Web / WebMCP (Phase 3)
**Condition:** Only after:
1. MCP server is rock-solid
2. AC_Risk Console MCP App is live
3. Clear EMV from web UI

**What to Build (Minimal):**
- Documentation portal
- MCP tool browser
- App launcher (links to MCP hosts)
- No "sudo" features

**What NOT to Build:**
- Full Petrel-like GUI
- Complex visualization (use MCP Apps)
- WebMCP (spec still evolving)

**Timeline:** Month 2+
**EMV:** MEDIUM — mainly documentation surface

---

## 3. Prompt Directive for GEOX Agents

```markdown
You are a GEOX co-architect agent optimizing for maximum EMV/NPV versus legacy
subsurface software (Petrel, DecisionSpace, PaleoScan, etc.).

Your primary strategic objective is to make GEOX the strongest MCP server and
governance brain for subsurface work, not a GUI competitor.

ABSOLUTE FOCUS AREAS (in order):

1. HARDEN THE GEOX MCP SERVER
   - Ensure all tools are well-specified, discoverable, robust
   - Prioritize: tool clarity, schemas, error handling, versioning
   - Not: adding new half-baked tools

2. SHIP ONE FLAGSHIP MCP APP: AC_RISK CONSOLE
   - Interactive AC_Risk exploration inside MCP hosts
   - Sliders for U_phys, D_transform, B_cog
   - Real-time verdict display
   - One app, done well, before any others

3. ACT AS GOVERNANCE LAYER FOR EXISTING TOOLS
   - Accept Petrel/DSG/PaleoScan exports
   - Return AC_Risk and ToAC audits
   - Don't replicate their GUIs, augment their decisions

4. WEB ONLY AFTER MCP LOCKED
   - Keep geox.arif-fazil.com minimal and truthful
   - WebMCP is Phase 3, not Phase 1

HARD CONSTRAINTS:
n- Never exceed existing compute/data capacity
n- Never promise parity with Petrel UX
- Always route through AC_Risk and ToAC
- Vision tools must emit risk, not just pretty visuals

DEFAULT DECISION RULE:
Prefer work that increases marginal value of GEOX as an
MCP-integrated subsurface governance engine over standalone UX.
n```

---

## 4. Immediate Action Items (Next 2 Weeks)

### Week 1: MCP Server Hardening
- [ ] Create unified tool registry (`arifos/geox/tool_registry.py`)
- [ ] Add version to all tool outputs
- [ ] Standardize error codes
- [ ] Implement `list_tools` with metadata
- [ ] Test with Claude Desktop

### Week 2: AC_Risk Console MCP App
- [ ] Build HTML/JS UI
- [ ] Wire to `geox_compute_ac_risk`
- [ ] Test inline in Claude
- [ ] Deploy to `geox.arif-fazil.com/apps/ac-risk-console/`
- [ ] Create demo video

---

## 5. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| MCP tool stability | 99% success rate | Telemetry |
| Agent adoption | 3+ agent types using GEOX | Integration count |
| AC_Risk Console usage | 50+ sessions/week | Analytics |
| Legacy bridge value | 1 Petrel case study | Customer validation |
| Web site honesty | 0 "sudo" features | Audit |

---

## Conclusion

**GEOX is not a Petrel killer. GEOX is the governance layer Petrel lacks.**

**Next 30 days:**
1. Harden MCP server → agents can rely on GEOX
2. Ship AC_Risk Console → prove MCP Apps value
3. Design legacy bridges → position as augmentation

**After 30 days:**
- Assess EMV from MCP surface
- Decide on web investment
- Expand MCP App portfolio

**The bet:** Subsurface teams will adopt GEOX not for visualization, but for **decision discipline** that their existing tools can't provide.

---

*DITEMPA BUKAN DIBERI*
*Focus locked: MCP server + AC_Risk Console.*
*Web deferred. Governance prioritized.*
