# GEOX Earth Intelligence Website - Design Specification

## 1. Overview

### 1.1 Project Identity
- **Name**: GEOX Command Center
- **Tagline**: "Earth Intelligence Core — Real Tools, Zero Theater"
- **Seal**: "DITEMPA BUKAN DIBERI" (Forged, Not Given)
- **Constitutional Floors**: F1 F2 F4 F7 F9 F11 F13

### 1.2 Project Description
GEOX is a governed, agentic geological intelligence coprocessor for arifOS. The website showcases multiple web applications and tools designed for geoscience professionals.

### 1.3 Design Philosophy
- Dark, technical aesthetic — Professional earth science theme
- Scientific precision — Clean, data-driven interfaces
- Zero theater — Functional over decorative
- Card-based architecture — Modular app showcase
- Smooth interactions — Subtle animations for engagement

---

## 2. Page Manifest

| Page ID | Page Name | File Name | Is Entry | SubAgent Notes |
|---------|-----------|-----------|----------|----------------|
| index | Home / Landing | index.html | Yes | Hero, app grid, system status, constitutional floors display |
| ac-risk | AC Risk Calculator | ac-risk.html | No | Interactive calculator with formula display, 3 inputs, real-time computation |
| ratlas | RATLAS Browser | ratlas.html | No | Material browser with 99 materials, 11 families, search/filter |
| basin | Basin Explorer | basin-explorer.html | No | Basin analysis interface with demo data, charts, stratigraphic columns |
| seismic | Seismic Viewer | seismic-viewer.html | No | Seismic data viewer with demo traces, amplitude display |
| well | Well Context Desk | well-context-desk.html | No | Well log analysis with demo curves, depth tracking |

---

## 3. Global Design System

### 3.1 Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| --color-bg-primary | #0A0C0E | Main background |
| --color-bg-secondary | #111418 | Card backgrounds |
| --color-bg-tertiary | #1A1F24 | Elevated surfaces |
| --color-accent-amber | #F59E0B | Primary accent, CTAs |
| --color-accent-amber-light | #FBBF24 | Hover states |
| --color-text-primary | #F8FAFC | Headings, primary text |
| --color-text-secondary | #94A3B8 | Body text |
| --color-text-muted | #64748B | Labels |
| --color-status-online | #10B981 | Online status |
| --color-status-warning | #F59E0B | Warnings |
| --color-status-error | #EF4444 | Errors |
| --color-border-default | #1E293B | Default borders |

### 3.2 Typography

- **Primary Font**: 'Inter', system-ui, sans-serif
- **Monospace Font**: 'JetBrains Mono', monospace

| Level | Size | Weight | Usage |
|-------|------|--------|-------|
| H1 | 48px | 700 | Hero title |
| H2 | 36px | 600 | Section headings |
| H3 | 24px | 600 | Card titles |
| H4 | 18px | 500 | Subsection titles |
| Body | 16px | 400 | Paragraph text |
| Small | 14px | 400 | Secondary text |
| Caption | 12px | 500 | Labels, tags |
| Mono | 14px | 400 | Code, data values |

### 3.3 Spacing System

| Token | Value |
|-------|-------|
| --space-1 | 4px |
| --space-2 | 8px |
| --space-4 | 16px |
| --space-6 | 24px |
| --space-8 | 32px |
| --space-12 | 48px |
| --space-16 | 64px |
| --space-20 | 80px |

### 3.4 Border Radius

| Token | Value |
|-------|-------|
| --radius-sm | 4px |
| --radius-md | 8px |
| --radius-lg | 12px |
| --radius-xl | 16px |

### 3.5 Animation Specifications

| Animation | Duration | Easing |
|-----------|----------|--------|
| fade-in | 300ms | ease-out |
| slide-up | 400ms | cubic-bezier(0.16, 1, 0.3, 1) |
| scale-in | 200ms | cubic-bezier(0.34, 1.56, 0.64, 1) |
| pulse-glow | 2000ms | ease-in-out |

---

## 4. Page Specifications

### 4.1 Home / Landing Page (index.html)

#### Navigation Header
- Position: Fixed top, z-index: 50
- Height: 64px
- Background: rgba(10,12,14,0.95) with backdrop-blur: 12px
- Border: 1px solid #1E293B
- Content: GEOX logo, nav links, system status indicator

#### Hero Section
- Height: 100vh
- Background: radial-gradient(ellipse at top, #1a1f24 0%, #0a0c0e 70%)
- Content:
  - Seal: "DITEMPA BUKAN DIBERI"
  - Title: "GEOX Command Center"
  - Tagline: "Earth Intelligence Core — Real Tools, Zero Theater"
  - Constitutional floors: "F1 F2 F4 F7 F9 F11 F13"
  - CTA buttons: "Launch Tools", "View Documentation"

#### App Showcase Grid
- Layout: CSS Grid, 3 columns desktop, 2 tablet, 1 mobile
- Gap: 24px
- Cards (6):
  1. AC Risk Calculator (Calculator icon, Live)
  2. RATLAS Browser (Database icon, Live)
  3. Basin Explorer (Mountain icon, Demo)
  4. Seismic Viewer (Activity icon, Demo)
  5. Well Context Desk (AlignLeft icon, Demo)
  6. arifOS Core (Cpu icon, Core)

#### System Status Panel
- Metrics: Uptime 99.97%, Active Users 1,247, Data Points 2.4M
- Progress bars for CPU, Memory, Storage

#### Footer
- GEOX logo + copyright
- Quick links
- Social icons

### 4.2 AC Risk Calculator (ac-risk.html)

#### Formula Display
- Formula: AC_Risk = U_phys x D_transform x B_cog
- Description: Anomalous Contrast Risk calculation

#### Inputs
1. Physical Ambiguity (U_phys): Range 0.0-1.0
2. Transform Stack (D_transform): Select dropdown
3. Cognitive Bias (B_cog): Select dropdown

#### Result Display
- Large risk score display
- Risk level badge (Low/Medium/High/Critical)
- Color coding: Green/Yellow/Orange/Red

### 4.3 RATLAS Browser (ratlas.html)

#### Search & Filter Bar
- Search input
- Family filter (11 families)
- Property filters
- Sort options
- View toggle

#### Material Grid
- 4 columns desktop
- Material cards with name, family badge, properties
- Detail modal on click

#### Family Legend
- 11 color-coded families: Igneous, Sedimentary, Metamorphic, Carbonates, Clastics, Evaporites, Organic, Volcanic, Plutonic, Detrital, Chemical

### 4.4 Basin Explorer (basin-explorer.html)

#### Demo Basin Selector
- North Sea Graben, Gulf of Mexico, Permian Basin

#### Visualization
- Left: Stratigraphic column
- Right: Basin map placeholder

#### Properties Panel
- Formation details, thickness, age, lithology

### 4.5 Seismic Viewer (seismic-viewer.html)

#### Demo Data Selector
- Synthetic Line A, Synthetic Line B, 3D Volume Slice

#### Seismic Display
- Wiggle trace display
- Color amplitude toggle
- Time axis 0-4 seconds

#### Controls
- Gain slider, zoom controls, horizon toggle

### 4.6 Well Context Desk (well-context-desk.html)

#### Demo Well Selector
- Demo Well A-1, B-2, C-3

#### Log Display
- Multi-track display
- Tracks: Depth, Gamma Ray, Resistivity, Density/Neutron

#### Formation Tops
- Horizontal lines with labels

---

## 5. Technical Requirements

### 5.1 CDN Dependencies

```html
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

### 5.2 Browser Support
- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

### 5.3 Responsive Breakpoints
- sm: 640px, md: 768px, lg: 1024px, xl: 1280px, 2xl: 1536px

---

## 6. Image Requirements

### 6.1 Hero Background
- Keywords: "dark abstract geological layers, sedimentary rock strata, earth tones, deep slate gray background, subtle amber highlights, scientific visualization, cross section, minimal, professional"

### 6.2 Icons
- Lucide icons only: Calculator, Database, Mountain, Activity, AlignLeft, Cpu, Home, Wrench, Info, BookOpen

---

## 7. Navigation Structure

### Main Navigation
- Home (index.html)
- Tools (dropdown)
- About
- Docs (external)

### Tools Dropdown
- AC Risk Calculator
- RATLAS Browser
- Basin Explorer
- Seismic Viewer
- Well Context Desk

---

## 8. Interactive Elements

### Buttons
- Primary: #F59E0B bg, #0A0C0E text
- Secondary: transparent bg, #F59E0B border
- Ghost: transparent bg, #94A3B8 text

### Cards
- Default: #111418 bg, #1E293B border
- Hover: translateY(-4px), amber border glow

### Status Indicators
- Online: #10B981 with pulse animation
- Warning: #F59E0B with pulse animation
- Error: #EF4444 with pulse animation

---

## 9. Accessibility

- WCAG AA color contrast (4.5:1 minimum)
- Keyboard navigation support
- ARIA labels for icons
- Semantic HTML structure

---

## 10. File Structure

```
/output/
├── index.html
├── ac-risk.html
├── ratlas.html
├── basin-explorer.html
├── seismic-viewer.html
├── well-context-desk.html
└── Design.md
```

---

*GEOX Command Center Design Specification v1.0*
