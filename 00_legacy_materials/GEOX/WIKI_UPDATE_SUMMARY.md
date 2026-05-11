# GEOX Wiki Update & Forge Status

> **Date:** 2026-04-10
> **Status:** WIKI UPDATED, FORGE HARDENED
> **Seal:** 999_VAULT

---

## Summary of Changes

### 1. Vision Intelligence Charter
**File:** `GEOX/GEOX_VISION_DEV_CHARTER.md`
**Purpose:** Canonical guidance for all GEOX Vision development

**Key Content:**
- Three non-negotiable questions for every vision feature
- Working rule: `pixels → transforms → physics → decision`
- Four capability domains (georeferencing, digitization, seismic VLM, attributes)
- AC_Risk formula and thresholds
- Transform registry with invertibility scores
- Agent briefing pattern

---

### 2. External Integration Guide
**File:** `GEOX/EXTERNAL_INTEGRATION_GUIDE.md`
**Purpose:** Map proven external codebases to GEOX needs

**Key Integrations:**
| Domain | External | GEOX Addition | Time Saved |
|--------|----------|---------------|------------|
| Georeferencing | MapWarper, GeoReferencer | GeoreferenceAuditor + AC_Risk | 3.5 months |
| Analog Digitization | WebPlotDigitizer, Geomega | Physics validation + AC_Risk | 5.5 months |
| Seismic Vision | seismiqb, Seismic-App | Multi-view + AC_Risk | 11 months |
| Attributes | seismiqb, Nature 2025 | Transform-aware metadata | 2.5 months |
| VLM Backends | GeoX, GeoGround, GeoPixel | ToAC governance layer | 5.5 months |

**Total acceleration: 28 months → 12 weeks**

---

### 3. Forge Hardened Roadmap
**File:** `GEOX/FORGE_HARDENED_VISION.md`
**Purpose:** 12-week execution plan

**Phase Breakdown:**
- Weeks 1-2: Georeferencing (MapWarper patterns + GCPDetector)
- Weeks 3-4: Analog Digitization (WebPlotDigitizer pattern + RATLAS validation)
- Weeks 5-8: Seismic Vision (seismiqb integration + multi-view consistency)
- Weeks 9-10: Attributes (Nature 2025 risk model)
- Weeks 11-12: Integration & hardening

---

### 4. AC_Risk Calculator
**File:** `GEOX/arifos/geox/ENGINE/ac_risk.py`
**Status:** ✅ TESTED AND WORKING

**Test Results:**
```
Test 1 (SEGY, minimal transforms):
  AC_Risk: 0.000 → SEAL

Test 2 (Image only, CLAHE+AGC+VLM):
  AC_Risk: 0.252 → QUALIFY

Test 3 (Georeferencing, poor OCR):
  AC_Risk: 0.138 → SEAL
```

**Components:**
- `TransformRegistry`: 10+ transforms with invertibility scores
- `ACRiskCalculator`: Formula implementation + scenario methods
- `Verdict` enum: SEAL/QUALIFY/HOLD/VOID

---

### 5. Vision Governance Module
**Directory:** `GEOX/arifos/geox/vision/`
**Status:** ✅ SCAFFOLD COMPLETE

| Component | Purpose | Lines |
|-----------|---------|-------|
| `governed_vlm.py` | ToAC-compliant VLM wrapper | 470 |
| `contrast_views.py` | 5-view Contrast Canon generator | 73 |
| `multi_view_consistency.py` | Display artifact detector | 99 |
| `ac_risk_integration.py` | Convenience wrappers | 112 |

---

### 6. Site Specification
**File:** `GEOX/SITE_GEOK_ARIF_FAZIL_COM.md`
**Purpose:** Complete specification for geox.arif-fazil.com

**Key Clarifications:**

#### MCP vs Apps
```
MCP = Machine interface (AI agents)
  - JSON schemas
  - Tool definitions
  - Structured I/O
  - Location: /mcp

Apps = Human interface (operators)
  - Web UI
  - Interactive tools
  - Visual outputs
  - Location: /apps
```

**Same governance. Different consumers.**

#### Five Core Apps (V1)
1. **Georeference Map** — Upload → GCPs → GeoTIFF + AC_Risk
2. **Analog Digitizer** — Upload → trace curves → LAS + uncertainty
3. **Seismic Vision Review** — Upload → 5 views → verdict + warning
4. **Attribute Audit** — Run attributes → compare paths → risk flags
5. **AC_Risk Console** — Inspect any workflow's risk components

#### Current MCP Tools (Existing)
- ✅ `geox_load_seismic_line`
- ✅ `geox_build_structural_candidates`
- ✅ `geox_interpret_single_line`
- ✅ `geox_feasibility_check`
- ✅ `geox_compute_ac_risk`
- 🟡 `geox_georeference_map` (scaffold)
- 🔴 `geox_digitize_analog` (planned)

#### Current Apps (Existing)
- ✅ Volume App (3D rendering)
- ✅ Prefab Views (MCP host UIs)

---

## What Is MCP vs Apps

### MCP (Model Context Protocol)
**Analogy:** API for AI agents

**What it does:**
- Exposes tools as JSON-schema functions
- Agents (Claude, Cursor) call them programmatically
- Returns structured data + verdicts
- No human interaction required

**Example:**
```python
# Agent calls MCP tool
result = await mcp.geox_interpret_single_line(
    seismic_data="section.png",
    data_type="raster"
)
# result contains: hypotheses, ac_risk, verdict, warnings
```

### Apps
**Analogy:** Web applications for humans

**What they do:**
- Provide visual interfaces
- Allow upload, interaction, review
- Show images, maps, charts
- Human makes final decisions

**Example:**
```
User opens geox.arif-fazil.com/apps/georeference
→ Uploads map image
→ Clicks detected GCPs or adds manual ones
→ Reviews residuals
→ Sees AC_Risk score
→ Downloads GeoTIFF if QUALIFY
```

### The Contrast
| Aspect | MCP | Apps |
|--------|-----|------|
| **User** | AI agents | Human operators |
| **Interface** | JSON API | Web UI |
| **Speed** | Milliseconds | Seconds (human pace) |
| **Use case** | Batch processing, automation | Review, validation, decision |
| **Governance** | Automatic 888_HOLD | Human override available |

**Both use same AC_Risk engine. Both respect ToAC.**

---

## What Should Be on geox.arif-fazil.com

### Structure
```
geox.arif-fazil.com
├── /              (Hero + capabilities + honest status)
├── /apps          (5 operator tools with status badges)
├── /mcp           (Tool catalog + schemas + sample workflows)
├── /theory        (ToAC explanation + AC_Risk formula)
├── /cases         (3 real examples with outcomes)
├── /docs          (Full API reference + charter)
└── /about         (Mission + philosophy)
```

### Core Message
> "GEOX is not 'AI that sees geology.' GEOX is governed intelligence that turns pixels into constrained, auditable geoscience decisions."

### What NOT to Include
- ❌ Hype SaaS copy ("revolutionizing")
- ❌ Fake polished dashboards
- ❌ 20 tools when 5 are serious
- ❌ Black-box claims (no transform documentation)

---

## Files Updated in Wiki

```
GEOX/
├── GEOX_VISION_DEV_CHARTER.md              (NEW - Canonical guidance)
├── EXTERNAL_INTEGRATION_GUIDE.md           (NEW - External codebase map)
├── FORGE_HARDENED_VISION.md                (NEW - 12-week roadmap)
├── SITE_GEOK_ARIF_FAZIL_COM.md             (NEW - Site specification)
├── VISION_INTELLIGENCE_IMPLEMENTATION.md   (NEW - Technical summary)
└── arifos/geox/
    ├── ENGINE/
    │   └── ac_risk.py                      (NEW - AC_Risk calculator ✓)
    └── vision/                             (NEW - Governance module)
        ├── __init__.py
        ├── governed_vlm.py
        ├── contrast_views.py
        ├── multi_view_consistency.py
        └── ac_risk_integration.py
```

---

## Immediate Action Items

### Priority 0: Push to Main
```bash
cd /root/GEOX
git add -A
git commit -m "999_VAULT: Vision Intelligence stack with AC_Risk, ToAC governance, external integration roadmap"
git push origin main
```

### Priority 1: Deploy Site (This Week)
- [ ] Set up Astro/Next.js project
- [ ] Create homepage with hero + capability grid
- [ ] Deploy to geox.arif-fazil.com
- [ ] Test with mobile

### Priority 2: MCP Hardening (Next Week)
- [ ] Document all existing tools
- [ ] Add `/mcp` page with schemas
- [ ] Create sample agent workflows
- [ ] Test with Claude Desktop

### Priority 3: App Development (Week 3-4)
- [ ] Build AC_Risk Console (easiest)
- [ ] Enhance georeferencing with GCPDetector
- [ ] Add status badges to all tools

### Priority 4: External Integration (Month 2)
- [ ] Clone MapWarper, extract patterns
- [ ] Build GCPDetector
- [ ] Integrate seismiqb backend
- [ ] Multi-view consistency testing

---

## Verification Checklist

- [x] AC_Risk calculator implemented and tested
- [x] Vision governance module scaffolded
- [x] External integration guide complete
- [x] Site specification drafted
- [x] Forge roadmap hardened (12 weeks)
- [ ] Site deployed to geox.arif-fazil.com
- [ ] MCP documentation live
- [ ] Apps page with status badges
- [ ] First external integration (MapWarper)

---

## Resources for Agents

**For georeferencing agents:**
- Study: MapWarper, GeoReferencer
- Build: GCPDetector, GeoreferenceAuditor
- Test: Malay Basin maps

**For digitization agents:**
- Study: WebPlotDigitizer, Geomega
- Build: Scale detection, curve tracing
- Test: Legacy logs from backups

**For seismic vision agents:**
- Study: seismiqb, Seismic-App
- Build: Multi-view wrapper, consistency checker
- Test: Synthetic sections

**For MCP agents:**
- Study: FastMCP patterns, prefab-ui
- Build: Tool schemas, app manifests
- Test: Claude Desktop integration

---

*DITEMPA BUKAN DIBERI*
*Wiki updated. Forge hardened. Ready to push.*
*Next: Deploy site, forge MCP, build apps.*
