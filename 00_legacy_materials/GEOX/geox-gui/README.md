# GEOX Earth Witness GUI

**Governed Geologist Cockpit**
**Constitutional AI for Geoscience**
**Seal:** DITEMPA BUKAN DIBERI

---

## Overview

A React-based geologist workstation integrating:
- **ArcGIS-style 2D maps** (MapLibre GL JS)
- **Google Earth-like 3D terrain** (CesiumJS)
- **Seismic interpretation viewer** (WebGL)
- **Well log analysis** (D3.js + Canvas)
- **Outcrop/image analysis** (OpenSeadragon)
- **Constitutional governance** (F1-F13 floors)

---

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

Open http://localhost:5173

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GEOX GUI                                  │
├─────────────────────────────────────────────────────────────────┤
│  React 19 + TypeScript + Vite                                   │
│  ├── State: Zustand (immer, persist)                            │
│  ├── Styling: Tailwind CSS + Radix UI                           │
│  └── Maps: MapLibre GL (2D) + Cesium (3D)                       │
├─────────────────────────────────────────────────────────────────┤
│  Components:                                                     │
│  ├── EarthCanvas    → Map + 3D Globe                            │
│  ├── SeisView       → Seismic WebGL viewer                      │
│  ├── LogDock        → Well log tracks                           │
│  ├── OutcropLens    → Image analysis                            │
│  ├── ProspectDesk   → Decision panel                            │
│  └── WitnessBadges  → F1-F13 governance                         │
├─────────────────────────────────────────────────────────────────┤
│  Integration:                                                    │
│  └── GEOX MCP Server (Horizon: https://geoxarifOS.fastmcp.app)  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
geox-gui/
├── src/
│   ├── components/
│   │   ├── LandingPage/      # Clean entry point (NEW)
│   │   ├── EarthWitness/     # 2D map + 3D globe + iframe host
│   │   ├── LogDock/          # Well log viewer with petrophysics (NEW)
│   │   │   ├── LogDock.tsx
│   │   │   ├── types.ts
│   │   │   └── data/
│   │   │       └── demoWellData.ts
│   │   ├── MalayBasinPilot/  # Pilot dashboard
│   │   ├── WitnessBadges/    # F1-F13 badges
│   │   └── Layout/           # Main layout (3-panel cockpit)
│   ├── store/
│   │   └── geoxStore.ts      # Zustand store
│   ├── hooks/                # Custom React hooks
│   ├── utils/                # Utilities
│   ├── types/
│   │   └── index.ts          # TypeScript types
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── docs/
│   └── GEOX_GUI_ARCHITECTURE.md
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

---

## Key Features

### 1. Three-Panel Layout

```
┌──────────────────────────────────────────────────────────────┐
│  LEFT (25%)        │  CENTER (50%)      │  RIGHT (25%)      │
│  ─────────         │  ───────────       │  ──────────       │
│  Data/Layers       │  Main Workspace    │  Governance       │
│  - Layer tree      │  - Map/Seismic/Logs│  - F1-F13 badges  │
│  - Filters         │  - Tabs            │  - Prospect panel │
│  - Object info     │  - Sync cursor     │  - Decision zone  │
└──────────────────────────────────────────────────────────────┘
```

### 2. Constitutional Governance (F1-F13)

| Badge | Status | Meaning |
|-------|--------|---------|
| 🟢 F4 CLARITY | Green | Grounding verified |
| 🟡 F7 HUMILITY | Amber | Multiple candidates |
| 🔴 F1 AMANAH | Red | Irreversible operation blocked |

### 3. Synchronized Cursor

Click on map → Syncs to seismic trace → Updates well log depth → Updates prospect evidence

---

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Environment Variables

Create `.env`:
```bash
VITE_GEOX_MCP_URL=https://geoxarifOS.fastmcp.app
```

### Run Tests

```bash
npm run typecheck  # TypeScript check
npm run lint       # ESLint
```

---

## Integration with GEOX MCP

The GUI connects to your Horizon-deployed GEOX MCP server:

```typescript
// Check health
GET https://geoxarifOS.fastmcp.app/health

// Call tools
POST https://geoxarifOS.fastmcp.app/mcp
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "geox_verify_geospatial",
    "arguments": { "lat": 4.5, "lon": 114.2 }
  }
}
```

---

## Roadmap

### Phase 1: Foundation ✅
- [x] React + TypeScript setup
- [x] Layout components
- [x] Governance badge system
- [x] Zustand store
- [x] Landing Page (clean entry point)

### Phase 2: Maps ✅
- [x] MapLibre GL JS integration
- [x] Layer tree UI
- [x] Coordinate inspection

### Phase 3: Seismic
- [ ] WebGL renderer
- [ ] Candidate overlays
- [ ] Picking system

### Phase 4: Logs ✅
- [x] Canvas-based tracks (LogDock)
- [x] Petrophysics overlay (VSH, PHIe, Sw)
- [x] Interactive cursor + zoom
- [ ] Seismic-log tie
- [ ] Depth-time sync
- [ ] LAS file upload

### Phase 5: 3D
- [ ] CesiumJS globe
- [ ] Terrain draping
- [ ] Well sticks

---

## Design Principles

### 1. Evidence Before Story
```
Observations → Interpretation → Verdict
```

### 2. Measurement Only When Grounded
- Datum confirmed ✓
- Scale verified ✓
- Tie confirmed ✓

### 3. Multiple Models Visible
```
Candidate A ──────────
Candidate B ────────
Candidate C ─────────
```

### 4. Human Decision Zone (F13)
```
┌─────────────────────────┐
│ ⚠️ HUMAN REQUIRED       │
│ F13 SOVEREIGN           │
│                         │
│ [HOLD] [PARTIAL] [SEAL] │
└─────────────────────────┘
```

---

## License

AGPL-3.0

---

## Seal

**DITEMPA BUKAN DIBERI**

*Map for grounding, seismic for subsurface story, logs for constraint, outcrop for analog, prospect panel for judgment, badges for discipline.*

---

**Author:** Muhammad Arif bin Fazil <ariffazil@gmail.com>
**Repository:** https://github.com/ariffazil/GEOX
