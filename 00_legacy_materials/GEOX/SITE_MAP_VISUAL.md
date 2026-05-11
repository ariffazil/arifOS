# GEOX Site Map — Visual Reference

> **Status:** 888 HOLD
> **Purpose:** Quick reference for site structure

---

## Site Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           geox.arif-fazil.com                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  HERO                                                                │   │
│  │  "GEOX is governed geospatial and subsurface intelligence"           │   │
│  │  Physics > Narrative                                                │   │
│  │                                                                     │   │
│  │  [Open Apps]  [Use MCP]  [Read Theory]                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  3 PILLARS                                                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │ Intelligence│  │    Tools    │  │  Governance │                  │   │
│  │  │ Models      │  │ MCP + Apps  │  │ ToAC        │                  │   │
│  │  │ Vision      │  │             │  │ AC_Risk     │                  │   │
│  │  │ Reasoning   │  │             │  │ 888_HOLD    │                  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  CAPABILITY TRUTH TABLE                                              │   │
│  │  ┌─────────────────────────┬──────────┬─────────────────────────────┐│   │
│  │  │ Feature                 │ Status   │ Note                        ││   │
│  │  ├─────────────────────────┼──────────┼─────────────────────────────┤│   │
│  │  │ Seismic interpretation  │ ✅ LIVE  │ Contrast canon, multi-view  ││   │
│  │  │ Structural candidates   │ ✅ LIVE  │ Non-unique models           ││   │
│  │  │ AC_Risk calculation     │ ✅ LIVE  │ Tested and working          ││   │
│  │  │ Map georeferencing      │ 🟡 SCAF  │ Core working, AC_Risk next  ││   │
│  │  │ Analog digitization     │ 🔴 PLAN  │ Architecture defined        ││   │
│  │  └─────────────────────────┴──────────┴─────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  EARTH CONTEXT (Macrostrat)                                          │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │  [MAP: Regional geology from Macrostrat]                        │ │   │
│  │  │                                                                 │ │   │
│  │  │  Geologic basemap / stratigraphic context                       │ │   │
│  │  │  External reference — not subsurface certainty                  │ │   │
│  │  │                                                                 │ │   │
│  │  │  [Explore at macrostrat.org]                                    │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  HOW GEOX WORKS                                                      │   │
│  │  pixels → transforms → physics → decision                            │   │
│  │                                                                     │   │
│  │  AC_Risk = U_phys × D_transform × B_cog                              │   │
│  │                                                                     │   │
│  │  SEAL / QUALIFY / HOLD / VOID                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

NAVIGATION: / | /apps | /mcp | /theory | /docs
```

---

## Apps Page (`/apps`)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  APPS — Operator Interfaces                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ 🟡 Georeference  │  │ ✅ AC_Risk       │  │ 🔴 Analog        │          │
│  │    Map           │  │    Console       │  │    Digitizer     │          │
│  │                  │  │                  │  │                  │          │
│  │ SCAFFOLD         │  │ LIVE             │  │ PLANNED          │          │
│  │                  │  │                  │  │                  │          │
│  │ Upload map →     │  │ Inspect any      │  │ Upload log →     │          │
│  │ GCPs → GeoTIFF   │  │ workflow's       │  │ trace → LAS      │          │
│  │ + AC_Risk        │  │ risk components  │  │ + uncertainty    │          │
│  │                  │  │                  │  │                  │          │
│  │ [Open]           │  │ [Open]           │  │ Roadmap: M2      │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐                                │
│  │ 🟡 Seismic       │  │ 🟡 Attribute     │                                │
│  │    Vision        │  │    Audit         │                                │
│  │    Review        │  │                  │                                │
│  │                  │  │                  │                                │
│  │ SCAFFOLD         │  │ PREVIEW          │                                │
│  │                  │  │                  │                                │
│  │ 5 contrast views │  │ Run attributes   │                                │
│  │ → verdict +      │  │ Compare image vs │                                │
│  │   warnings       │  │ physics path     │                                │
│  │                  │  │                  │                                │
│  │ [Open]           │  │ [Open]           │                                │
│  └──────────────────┘  └──────────────────┘                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## MCP Page (`/mcp`)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  MCP — Machine Interface                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  GEOX exposes tools to AI agents via Model Context Protocol.                │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ TOOL CATALOG                                                         │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │ Core Geospatial:                                                     │   │
│  │   geox_georeference_raster     🟡 SCAFFOLD                           │   │
│  │   geox_detect_gcp_candidates   🟡 SCAFFOLD                           │   │
│  │                                                                      │   │
│  │ Seismic:                                                             │   │
│  │   geox_load_seismic_line       ✅ LIVE                               │   │
│  │   geox_build_structural_       ✅ LIVE                               │   │
│  │            candidates                                                │   │
│  │   geox_interpret_single_line   🟡 SCAFFOLD                           │   │
│  │   geox_generate_contrast_canon ✅ LIVE                               │   │
│  │                                                                      │   │
│  │ Governance:                                                          │   │
│  │   geox_compute_ac_risk         ✅ LIVE                               │   │
│  │   geox_emit_verdict            ✅ LIVE                               │   │
│  │   geox_get_transform_log       ✅ LIVE                               │   │
│  │                                                                      │   │
│  │ Petrophysics:                                                        │   │
│  │   geox_digitize_chart          🔴 PLANNED                            │   │
│  │   geox_compute_petrophysics    🟡 BETA                               │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SAMPLE WORKFLOW                                                      │   │
│  │                                                                      │   │
│  │  result = await mcp.geox_load_seismic_line(                          │   │
│  │      line_id="MB-001"                                                │   │
│  │  )                                                                   │   │
│  │                                                                      │   │
│  │  if result.verdict == "HOLD":                                        │   │
│  │      await agent.escalate(result.warnings)                           │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Status Badge System

```
┌─────────────┬──────────┬────────────────────────────────────────────────────┐
│ Badge       │ Color    │ Meaning                                            │
├─────────────┼──────────┼────────────────────────────────────────────────────┤
│ ✅ LIVE     │ Green    │ Usable now, tested                                 │
│ 🟡 PREVIEW  │ Yellow   │ Visible, non-production                            │
│ 🟡 SCAFFOLD │ Orange   │ Implemented shell, limited utility                 │
│ 🔴 PLANNED  │ Gray     │ Documented, not interactive                        │
└─────────────┴──────────┴────────────────────────────────────────────────────┘
```

---

## Route Existence Matrix

| Route | Must Exist | Current State | Action |
|-------|------------|---------------|--------|
| `/` | ✅ Yes | Content drafted | Build |
| `/mcp` | ✅ Yes | Content drafted | Build |
| `/apps` | ✅ Yes | Content drafted | Build |
| `/apps/georeference` | ✅ Yes | Scaffold exists | Ship as scaffold |
| `/apps/ac-risk` | ✅ Yes | Code exists | Build UI |
| `/apps/seismic-review` | ✅ Yes | Scaffold exists | Ship as preview |
| `/apps/attribute-audit` | ✅ Yes | Code exists | Ship |
| `/apps/analog-digitizer` | 🟡 Optional | Planned only | Stub or hide |
| `/theory` | ✅ Yes | Content drafted | Build |
| `/docs` | ✅ Yes | Content exists | Build |
| `/cases` | 🔴 No | No real examples | Hide for now |

---

## Macrostrat Integration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  EARTH CONTEXT SECTION                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │                    [MACROSTRAT MAP VIEW]                            │   │
│  │                                                                     │   │
│  │    ┌─────────────────────────────────────────────────────────┐     │   │
│  │    │  🗺️  Interactive geological map                        │     │   │
│  │    │                                                         │     │   │
│  │    │  • Regional geology context                             │     │   │
│  │    │  • Stratigraphic columns                                │     │   │
│  │    │  • Rock unit identification                             │     │   │
│  │    │                                                         │     │   │
│  │    │  External reference — not subsurface certainty          │     │   │
│  │    └─────────────────────────────────────────────────────────┘     │   │
│  │                                                                     │   │
│  │    Geologic basemap / stratigraphic context powered by Macrostrat   │   │
│  │                                                                     │   │
│  │    [Explore at macrostrat.org]  [Use in GEOX tools →]               │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  VISUAL SEPARATION:                                                         │
│  - GEOX tools: Gold border (#D4AF37)                                       │
│  - Macrostrat: Gray border (#666), subtle opacity                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## No-Deadlink Checklist

### Navigation
- [ ] Logo → `/`
- [ ] Nav items: `/apps`, `/mcp`, `/theory`, `/docs`
- [ ] All nav items have working routes

### CTAs
- [ ] "Open Apps" → `/apps`
- [ ] "Use MCP" → `/mcp`
- [ ] "Read Theory" → `/theory`

### Apps
- [ ] Each app card links to existing route
- [ ] Status badges truthful
- [ ] No "Coming soon" buttons

### MCP
- [ ] All listed tools exist in codebase
- [ ] Sample workflow is runnable
- [ ] Schemas match actual code

### External
- [ ] Macrostrat → https://macrostrat.org/map
- [ ] GitHub → https://github.com/arif-fazil/GEOX
- [ ] arif-fazil.com → https://arif-fazil.com

---

*Visual reference complete. Use for implementation.*
