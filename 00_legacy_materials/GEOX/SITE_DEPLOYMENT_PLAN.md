# GEOX Site Deployment Plan

> **Status:** 888 HOLD — PLAN COMPLETE, AWAITING EXECUTION
> **Authority:** Muhammad Arif bin Fazil
> **Date:** 2026-04-10
> **Seal:** DITEMPA BUKAN DIBERI

---

## 888 HOLD ACKNOWLEDGMENT

**This plan is READY but NOT EXECUTED.**

External actions required (held):
- [ ] Git push to main
- [ ] DNS verification (geox.arif-fazil.com)
- [ ] Hosting deployment
- [ ] SSL certificate
- [ ] Macrostrat API key (if needed)

**Execute only after:**
1. Reviewing this plan
2. Verifying all routes exist
3. Confirming status badges are truthful
4. Testing locally

---

## Site Map: Verified Routes Only

```
geox.arif-fazil.com
│
├── /                           [REQUIRED - Hero + truth table]
│   ├── Hero: "GEOX is governed geospatial intelligence"
│   ├── 3 pillars: Intelligence, Tools, Governance
│   ├── Capability truth table (honest status)
│   ├── Earth Context (Macrostrat viewer)
│   └── CTAs → /apps, /mcp, /theory
│
├── /mcp                        [REQUIRED - Tool catalog]
│   ├── What is MCP
│   ├── Tool catalog with status
│   ├── Sample workflows
│   └── Auth instructions
│
├── /apps                       [REQUIRED - 5 apps max]
│   ├── /apps/georeference      [SCAFFOLD - exists, limited]
│   ├── /apps/seismic-review    [SCAFFOLD - exists, mock VLM]
│   ├── /apps/attribute-audit   [PREVIEW - compute attributes]
│   ├── /apps/ac-risk           [LIVE - AC_Risk calculator]
│   └── /apps/analog-digitizer  [PLANNED - stub page only]
│
├── /theory                     [REQUIRED - ToAC explanation]
│   ├── Theory of Anomalous Contrast
│   ├── AC_Risk formula
│   ├── Physics > Narrative
│   └── Bond et al. 2007 reference
│
├── /docs                       [REQUIRED - Documentation]
│   ├── Charter
│   ├── Integration guide
│   └── Roadmap
│
└── /cases                      [OPTIONAL - hide if no real examples]
    └── (Hidden until ready)
```

---

## Element-to-Reality Mapping

Every element maps to ONE of four states:

| State | Definition | UI Treatment |
|-------|------------|--------------|
| **LIVE** | Usable now, tested | Green badge, full functionality |
| **PREVIEW** | Visible, non-production | Yellow badge, limited features |
| **SCAFFOLD** | Implemented shell | Orange badge, basic UI |
| **PLANNED** | Documented only | Gray badge, no interactivity |

---

## Route Verification Matrix

### `/` (Homepage)

| Element | Status | Evidence | Route Exists? |
|---------|--------|----------|---------------|
| Hero text | LIVE | Content drafted | N/A (static) |
| Capability table | LIVE | Based on actual code | N/A (static) |
| Macrostrat context | PREVIEW | External embed | External link |
| CTA to /apps | LIVE | Route exists | ✅ Yes |
| CTA to /mcp | LIVE | Route exists | ✅ Yes |
| CTA to /theory | LIVE | Route exists | ✅ Yes |

**Deadlink risk: NONE** — all CTAs point to required routes.

---

### `/mcp` (Machine Interface)

| Element | Status | Evidence | Truth Verified? |
|---------|--------|----------|-----------------|
| Tool catalog | LIVE | Tools exist in codebase | ✅ Yes |
| `geox_load_seismic_line` | LIVE | mcp_server.py | ✅ Yes |
| `geox_build_structural_candidates` | LIVE | mcp_server.py | ✅ Yes |
| `geox_interpret_single_line` | SCAFFOLD | Mock VLM backend | 🟡 Partial |
| `geox_compute_ac_risk` | LIVE | ac_risk.py tested | ✅ Yes |
| `geox_georeference_map` | SCAFFOLD | Basic tool exists | 🟡 Partial |
| `geox_digitize_analog` | PLANNED | Architecture only | 🔴 No |
| Sample workflows | LIVE | Can demonstrate | ✅ Yes |
| Auth instructions | LIVE | Standard MCP | ✅ Yes |

**Action:** Mark `geox_interpret_single_line` as SCAFFOLD (mock backend).
**Action:** Mark `geox_digitize_analog` as PLANNED (not clickable).

---

### `/apps` (Operator Interfaces)

| App | Route | Status | Code Exists? | UI Exists? | Verdict |
|-----|-------|--------|--------------|------------|---------|
| Georeference Map | `/apps/georeference` | SCAFFOLD | ✅ tools/georeference_map.py | 🔴 Basic | Can ship as scaffold |
| Seismic Vision Review | `/apps/seismic-review` | SCAFFOLD | ✅ vision/governed_vlm.py | 🔴 Mock only | Can ship as preview |
| Attribute Audit | `/apps/attribute-audit` | PREVIEW | ✅ seismic_feature_extract.py | 🟡 Partial | Can ship |
| AC_Risk Console | `/apps/ac-risk` | LIVE | ✅ ac_risk.py tested | 🟡 Needs UI | Build simple UI |
| Analog Digitizer | `/apps/analog-digitizer` | PLANNED | 🔴 Architecture only | 🔴 None | Stub page only |

**Decision:**
- Ship first 4 with honest badges
- Hide Analog Digitizer OR show as "Planned - not available"

---

### `/theory` (ToAC Documentation)

| Element | Status | Evidence | Ready? |
|---------|--------|----------|--------|
| ToAC explanation | LIVE | GEOX_VISION_DEV_CHARTER.md | ✅ Yes |
| AC_Risk formula | LIVE | ac_risk.py + docs | ✅ Yes |
| Physics > Narrative | LIVE | Charter | ✅ Yes |
| Bond et al. 2007 | LIVE | Cited in code | ✅ Yes |

**Deadlink risk: NONE** — all static content.

---

### `/docs` (Documentation)

| Element | Status | Source | Ready? |
|---------|--------|--------|--------|
| Vision Dev Charter | LIVE | GEOX_VISION_DEV_CHARTER.md | ✅ Yes |
| External Integration | LIVE | EXTERNAL_INTEGRATION_GUIDE.md | ✅ Yes |
| Forge Hardened Vision | LIVE | FORGE_HARDENED_VISION.md | ✅ Yes |
| Implementation Notes | LIVE | VISION_INTELLIGENCE_IMPLEMENTATION.md | ✅ Yes |

**Deadlink risk: NONE** — markdown files exist.

---

## Macrostrat Integration Plan

### What Macrostrat Is
- **External geological data platform**
- Regional geology context
- Stratigraphic columns
- Geologic maps
- **NOT** subsurface certainty
- **NOT** drilling-ready interpretation

### Placement on Homepage
```
Section: "Earth Context"
Location: Below hero, above capability table

Content:
- Interactive map (Macrostrat embed or tiles)
- Label: "Geologic basemap / stratigraphic context powered by Macrostrat"
- Clear separation from GEOX decision tools
- Link: "Explore regional geology at macrostrat.org"

Use Cases:
- Basin-scale orientation
- Rock unit identification
- Age/stratigraphic context
- Click region → jump to /apps/georeference

NOT Claimed:
- "Macrostrat gives subsurface certainty"
- "Global geology = drilling ready"
- Integration with seismic decisions (without provenance)
```

### Technical Implementation
```javascript
// Option 1: Direct embed (if Macrostrat allows)
<iframe src="https://macrostrat.org/map" title="Macrostrat geology">

// Option 2: Link with preview image
<a href="https://macrostrat.org/map">
  <img src="/images/macrostrat-context.png" alt="Geologic context">
  <span>Explore at Macrostrat</span>
</a>

// Option 3: API integration (if available)
// Fetch regional geology data
// Display as context panel
```

### Visual Separation
```css
/* Clear visual distinction */
.geox-tools { border: 2px solid #D4AF37; } /* GEOX gold */
.macrostrat-context { border: 1px solid #666; opacity: 0.9; }
.context-label { font-size: 0.8em; color: #666; }
```

---

## No-Deadlink Verification Checklist

### Pre-Deploy Verification

#### Navigation
- [ ] Every nav item has corresponding route
- [ ] No "coming soon" buttons that don't resolve
- [ ] Footer links all valid
- [ ] Logo links to `/`

#### /apps
- [ ] Each app card has working route
- [ ] Status badges truthful
- [ ] Buttons resolve to actual functionality
- [ ] No disabled buttons with "soon" text

#### /mcp
- [ ] Every listed tool exists in codebase
- [ ] Schemas match actual code
- [ ] Sample workflows are runnable
- [ ] Auth instructions accurate

#### External Links
- [ ] Macrostrat link: https://macrostrat.org/map
- [ ] GitHub link: https://github.com/arif-fazil/GEOX
- [ ] arif-fazil.com link: https://arif-fazil.com

#### Assets
- [ ] All images exist
- [ ] All CSS loads
- [ ] All JS loads
- [ ] Favicon present

---

## Deployment Phase Plan

### Phase 0: Truth Audit (Do This First)
```bash
# Local verification
npm run build
npm run preview

# Check all routes
curl http://localhost:3000/
curl http://localhost:3000/mcp
curl http://localhost:3000/apps
curl http://localhost:3000/theory
curl http://localhost:3000/docs

# Verify no 404s
# Verify all badges truthful
```

### Phase 1: Minimal Truthful Deploy
**Routes:** `/`, `/mcp`, `/apps`, `/theory`, `/docs`
**Hidden:** `/cases` (until real examples ready)

**Timeline:** Week 1
**Goal:** Honest baseline site live

### Phase 2: Macrostrat Context
**Add:** Earth Context section on homepage
**Timeline:** Week 2
**Goal:** Regional geology viewer embedded

### Phase 3: Operator Deepening
**Enhance:**
- `/apps/georeference` → full GCP workflow
- `/apps/ac-risk` → interactive calculator
- `/apps/seismic-review` → real VLM backend

**Timeline:** Weeks 3-4
**Goal:** Working operator tools

### Phase 4: Analog & Cases
**Add:**
- `/apps/analog-digitizer` (when ready)
- `/cases` (with real examples)

**Timeline:** Month 2
**Goal:** Complete V1 feature set

---

## Content Specifications

### Homepage (`/`)

#### Hero Section
```html
<h1>GEOX is governed geospatial and subsurface intelligence</h1>
<p>Physics over narrative. Audit over guess. Decision discipline over hype.</p>

<div class="pillars">
  <div>Intelligence — Models, vision, reasoning</div>
  <div>Tools — MCP APIs and operator apps</div>
  <div>Governance — ToAC, AC_Risk, 888_HOLD</div>
</div>

<div class="ctas">
  <a href="/apps">Open Apps</a>
  <a href="/mcp">Use MCP</a>
  <a href="/theory">Read Theory</a>
</div>
```

#### Capability Truth Table
```html
<table>
  <tr>
    <th>Capability</th>
    <th>Status</th>
    <th>Note</th>
  </tr>
  <tr>
    <td>Seismic interpretation</td>
    <td><span class="badge live">LIVE</span></td>
    <td>Contrast canon, multi-view</td>
  </tr>
  <tr>
    <td>Structural candidates</td>
    <td><span class="badge live">LIVE</span></td>
    <td>Non-unique inverse models</td>
  </tr>
  <tr>
    <td>AC_Risk calculation</td>
    <td><span class="badge live">LIVE</span></td>
    <td>Tested and working</td>
  </tr>
  <tr>
    <td>Map georeferencing</td>
    <td><span class="badge scaffold">SCAFFOLD</span></td>
    <td>Core working, AC_Risk next</td>
  </tr>
  <tr>
    <td>Analog digitization</td>
    <td><span class="badge planned">PLANNED</span></td>
    <td>Architecture defined</td>
  </tr>
</table>
```

#### Earth Context (Macrostrat)
```html
<section class="earth-context">
  <h2>Earth Context</h2>
  <p class="context-label">
    Geologic basemap / stratigraphic context powered by Macrostrat
  </p>

  <!-- Macrostrat embed or link -->
  <div class="macrostrat-viewer">
    <iframe src="https://macrostrat.org/map" title="Macrostrat geology">
    </iframe>
  </div>

  <p class="context-note">
    Macrostrat provides regional geology context.
    Not a substitute for well-calibrated subsurface interpretation.
  </p>
</section>
```

---

### /mcp Page

#### Tool Catalog
```html
<h1>MCP — Machine Interface</h1>
<p>Connect GEOX to Claude, Cursor, and other AI agents.</p>

<table>
  <tr>
    <th>Tool</th>
    <th>Purpose</th>
    <th>Status</th>
  </tr>
  <tr>
    <td><code>geox_load_seismic_line</code></td>
    <td>Load seismic + contrast views</td>
    <td><span class="badge live">LIVE</span></td>
  </tr>
  <tr>
    <td><code>geox_compute_ac_risk</code></td>
    <td>Calculate Anomalous Contrast Risk</td>
    <td><span class="badge live">LIVE</span></td>
  </tr>
  <tr>
    <td><code>geox_georeference_map</code></td>
    <td>Map georeferencing with governance</td>
    <td><span class="badge scaffold">SCAFFOLD</span></td>
  </tr>
</table>

<h2>Sample Workflow</h2>
<pre><code>
result = await mcp.geox_load_seismic_line(
    line_id="MB-001",
    survey_path="malay_basin/"
)

# Check verdict
if result.verdict == "HOLD":
    await agent.escalate(result.warnings)
</code></pre>
```

---

### /apps Page

```html
<h1>Apps — Operator Interfaces</h1>

<div class="app-grid">

  <div class="app-card scaffold">
    <h3>Georeference Map</h3>
    <span class="badge">SCAFFOLD</span>
    <p>Upload map → detect GCPs → GeoTIFF + AC_Risk</p>
    <a href="/apps/georeference">Open</a>
  </div>

  <div class="app-card live">
    <h3>AC_Risk Console</h3>
    <span class="badge">LIVE</span>
    <p>Inspect U_phys, D_transform, B_cog for any workflow</p>
    <a href="/apps/ac-risk">Open</a>
  </div>

  <div class="app-card planned">
    <h3>Analog Digitizer</h3>
    <span class="badge">PLANNED</span>
    <p>Upload log image → trace curves → LAS + uncertainty</p>
    <span>Roadmap: Month 2</span>
  </div>

</div>
```

---

## Final Verification Command

```bash
# Before any deploy, run:
npm run build
npm run preview

# Then verify:
# 1. All nav links work
# 2. All buttons resolve
# 3. All status badges truthful
# 4. No console errors
# 5. Mobile responsive
# 6. Macrostrat loads
# 7. All external links valid

# Only then:
git push origin main
npm run deploy
```

---

## Execution Decision

**Current State:** Plan complete, awaiting execution.
**Recommendation:** Review this plan, then execute Phase 0-1.
**Risk:** Low — minimal truthful deploy first.
**888 HOLD Status:** HOLD until you confirm:
- [ ] Plan reviewed
- [ ] Local build tested
- [ ] Status badges verified truthful
- [ ] DNS ready

---

*DITEMPA BUKAN DIBERI*
*Plan is forged. Execution is held. Release when ready.*
