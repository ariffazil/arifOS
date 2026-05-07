# GEOX Geologist GUI — Implementation Architecture

**DITEMPA BUKAN DIBERI**

A governed geologist cockpit with constitutional governance (F1-F13) integration.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           GEOX GUI ARCHITECTURE                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        REACT + TYPESCRIPT FRONTEND                       │   │
│  │  (aligned with waw/ architecture pattern)                                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                            │
│         ┌──────────────────────────┼──────────────────────────┐                 │
│         ▼                          ▼                          ▼                 │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐            │
│  │   EARTH      │         │   SEISVIEW   │         │  LOGDOCK     │            │
│  │   CANVAS     │         │   (WebGL)    │         │  (Canvas)    │            │
│  │              │         │              │         │              │            │
│  │ • MapLibre   │         │ • Custom     │         │ • D3.js      │            │
│  │   GL JS      │         │   WebGL      │         │ • Canvas API │            │
│  │ • CesiumJS   │         │ • Seismic    │         │ • Sync       │            │
│  │   (3D)       │         │   rendering  │         │   cursor     │            │
│  └──────┬───────┘         └──────┬───────┘         └──────┬───────┘            │
│         │                        │                        │                    │
│         └────────────────────────┼────────────────────────┘                    │
│                                  ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      GOVERNANCE LAYER (F1-F13)                           │   │
│  │  • WitnessBadges component                                               │   │
│  │  • Measurement grounding checks                                          │   │
│  │  • Uncertainty enforcement                                               │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                  │                                              │
│                                  ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      GEOX MCP CLIENT                                     │   │
│  │  • HTTP transport to Horizon/VPS                                         │   │
│  │  • Tool invocation: geox_verify_geospatial, geox_evaluate_prospect       │   │
│  │  • VAULT999 audit logging                                                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Core Framework
| Layer | Technology | Reason |
|-------|------------|--------|
| **Framework** | React 19 + TypeScript | Aligns with waw/ architecture |
| **Build** | Vite 7 | Fast HMR, aligned with waw |
| **State** | Zustand | Lightweight, TypeScript-first |
| **Styling** | Tailwind CSS 3.4 | Consistent with waw |
| **UI Components** | Radix UI + CVA | Accessible, composable |

### Map & Visualization
| Component | Library | License |
|-----------|---------|---------|
| **2D Map** | MapLibre GL JS | BSD-3 (Open source) |
| **3D Terrain** | CesiumJS | Apache 2.0 |
| **Seismic** | Custom WebGL | arifOS |
| **Well Logs** | D3.js + Canvas | BSD-3 |
| **Image Viewer** | OpenSeadragon | BSD-3 |

### Backend Integration
| Service | Protocol | Endpoint |
|---------|----------|----------|
| **GEOX MCP** | HTTP/SSE | `https://geoxarifOS.fastmcp.app/mcp` |
| **VAULT999** | REST | `http://localhost:8080/vault` |
| **arifOS Kernel** | WebSocket | `ws://localhost:8080/ws` |

---

## Component Architecture

### 1. EarthCanvas (Map + 3D)

```typescript
// src/components/EarthCanvas/EarthCanvas.tsx
interface EarthCanvasProps {
  mode: '2d' | '3d';
  layers: MapLayer[];
  selection: GeoSelection;
  onCoordinateSelect: (coord: Coordinate) => void;
  governance: GovernanceState; // F4 grounding status
}

// Features:
// - MapLibre GL JS for 2D (ArcGIS-style)
// - CesiumJS for 3D (Google Earth-like)
// - Layer tree with checkboxes
// - Coordinate inspection with datum/CRS
// - QC flags (yellow/red for unverified)
```

**Key Libraries:**
- `maplibre-gl`: 2D vector maps
- `cesium`: 3D globe with terrain
- ` turf.js`: Geospatial operations

### 2. SeisView (Seismic Viewer)

```typescript
// src/components/SeisView/SeisView.tsx
interface SeisViewProps {
  lineId: string;
  data: SeismicData;
  displayMode: 'wiggle' | 'variable-area' | 'grayscale';
  candidates: StructuralCandidate[]; // F7: multiple models
  grounding: SeismicGrounding; // F4: scale/datum status
  onPick: (pick: HorizonPick) => void;
}

// Features:
// - WebGL rendering for performance
// - Pan, zoom, amplitude scaling
// - Horizon picks with uncertainty
// - Multiple candidate overlays (A/B/C)
// - Warning ribbon if scale unknown
```

**Key Implementation:**
- Custom WebGL shader for seismic display
- Texture-based amplitude rendering
- Overlay system for candidates

### 3. LogDock (Well Log Viewer)

```typescript
// src/components/LogDock/LogDock.tsx
interface LogDockProps {
  wellId: string;
  logs: WellLog[];
  tracks: LogTrack[];
  tieStatus: SeismicLogTie; // Sync with seismic
  cursor: DepthCursor;
  onCursorMove: (depth: number) => void;
}

// Features:
// - Multi-track display (GR, RES, DEN, NPHI, Sonic)
// - Linked cursor with SeisView
// - Tops/contacts markers
// - Tie confidence meter
// - Depth-time uncertainty ribbon
```

**Key Libraries:**
- `d3-scale`: Log scales
- Canvas API for rendering

### 4. OutcropLens (Image Analysis)

```typescript
// src/components/OutcropLens/OutcropLens.tsx
interface OutcropLensProps {
  image: ImageData;
  annotations: Annotation[];
  aiSuggestions: Observation[]; // AI-assisted, not definitive
  onAnnotate: (annotation: Annotation) => void;
}

// Features:
// - Deep zoom (OpenSeadragon)
// - Annotation tools
// - AI suggestions with confidence
// - Comparison with subsurface
```

### 5. ProspectDesk (Decision Panel)

```typescript
// src/components/ProspectDesk/ProspectDesk.tsx
interface ProspectDeskProps {
  prospect: Prospect;
  evidence: EvidenceStack;
  riskMatrix: RiskMatrix;
  decision: DecisionGate; // Approved/Partial/Hold/Void
  onDecision: (decision: Decision) => void;
}

// Features:
// - Evidence stack (linked to map/seismic/logs)
// - Risk matrix (reservoir/seal/trap/charge)
// - Missing constraints list
// - Human decision zone (explicit)
```

### 6. WitnessBadges (Governance)

```typescript
// src/components/WitnessBadges/WitnessBadges.tsx
interface WitnessBadgesProps {
  floors: ConstitutionalFloor[];
  status: FloorStatus; // green/amber/red/grey
}

// Features:
// - F1, F4, F7, F9, F11, F13 badges
// - Color-coded status
// - Hover details
// - Action required indicators
```

---

## State Management (Zustand)

```typescript
// src/store/geoxStore.ts
interface GEOXState {
  // View state
  activeTab: Tab;
  mapView: MapViewState;
  seismicView: SeismicViewState;
  logView: LogViewState;

  // Data
  layers: MapLayer[];
  wells: Well[];
  seismicLines: SeismicLine[];
  prospects: Prospect[];

  // Selection (synchronized)
  selectedCoordinate: Coordinate | null;
  selectedLine: string | null;
  selectedWell: string | null;
  cursor: CursorState;

  // Governance (F1-F13)
  governance: GovernanceState;
  groundingStatus: GroundingStatus;
  uncertainty: UncertaintyState;

  // Actions
  setActiveTab: (tab: Tab) => void;
  selectCoordinate: (coord: Coordinate) => void;
  syncCursor: (position: CursorPosition) => void;
  updateGovernance: (update: GovernanceUpdate) => void;
}
```

---

## Synchronization System

### Cross-Panel Sync

```typescript
// src/hooks/useSync.ts
export function useCrossPanelSync() {
  const { syncCursor, selectCoordinate } = useGEOXStore();

  // When user clicks on map:
  // 1. Update map selection
  // 2. Find nearest seismic line
  // 3. Update seismic cursor
  // 4. Find nearest well
  // 5. Update log cursor
  // 6. Update prospect evidence

  const handleMapClick = useCallback((coord: Coordinate) => {
    selectCoordinate(coord);

    // Sync to seismic
    const nearestLine = findNearestLine(coord);
    if (nearestLine) {
      syncCursor({
        panel: 'seismic',
        lineId: nearestLine.id,
        position: projectToLine(coord, nearestLine),
      });
    }

    // Sync to logs
    const nearestWell = findNearestWell(coord);
    if (nearestWell) {
      syncCursor({
        panel: 'log',
        wellId: nearestWell.id,
        position: inferDepthFromSeismic(),
      });
    }
  }, [selectCoordinate, syncCursor]);

  return { handleMapClick };
}
```

---

## Governance Integration (F1-F13)

### F4 CLARITY — Measurement Grounding

```typescript
// src/utils/grounding.ts
export function checkMeasurementGrounding(
  tool: MeasurementTool,
  context: GeospatialContext
): GroundingStatus {
  // Check datum
  if (!context.datum) {
    return {
      floor: 'F4',
      status: 'red',
      message: 'Datum unknown — measurement disabled',
      action: () => disableTool(tool),
    };
  }

  // Check scale
  if (!context.scaleVerified) {
    return {
      floor: 'F4',
      status: 'amber',
      message: 'Scale unverified — interpretive only',
      action: () => showWarningRibbon(),
    };
  }

  return { floor: 'F4', status: 'green' };
}
```

### F7 HUMILITY — Multiple Candidates

```typescript
// src/components/SeisView/CandidateOverlay.tsx
export function CandidateOverlay({
  candidates,
  selectedCandidate,
  onSelect,
}: CandidateOverlayProps) {
  // Always show all candidates
  // Don't auto-promote one to truth

  return (
    <div className="candidate-overlay">
      {candidates.map((candidate, idx) => (
        <CandidateLine
          key={candidate.id}
          candidate={candidate}
          isSelected={selectedCandidate === candidate.id}
          label={`Candidate ${String.fromCharCode(65 + idx)}`}
          onClick={() => onSelect(candidate.id)}
        />
      ))}

      {candidates.length === 1 && (
        <F7Warning message="Only one candidate — add alternatives or constrain with data" />
      )}
    </div>
  );
}
```

### F13 SOVEREIGN — Human Decision Zone

```typescript
// src/components/ProspectDesk/HumanDecisionZone.tsx
export function HumanDecisionZone({ prospect }: { prospect: Prospect }) {
  return (
    <div className="human-decision-zone border-2 border-red-500 bg-red-50 p-4">
      <h3 className="text-red-700 font-bold flex items-center gap-2">
        <ShieldIcon />
        HUMAN DECISION REQUIRED — F13 SOVEREIGN
      </h3>

      <p className="text-sm text-red-600 mt-2">
        This prospect evaluation requires human judgment.
        AI can provide evidence, but the final decision is yours.
      </p>

      <div className="flex gap-2 mt-4">
        <Button
          variant="destructive"
          onClick={() => submitDecision('HOLD')}
        >
          HOLD — Insufficient Grounding
        </Button>
        <Button
          variant="default"
          onClick={() => submitDecision('PARTIAL')}
        >
          PARTIAL — Bounded Evaluation
        </Button>
        <Button
          variant="outline"
          onClick={() => submitDecision('SEAL')}
          disabled={!allConstraintsMet()}
        >
          SEAL — Approved (Requires sign-off)
        </Button>
      </div>
    </div>
  );
}
```

---

## MCP Integration

### GEOX Client

```typescript
// src/utils/geoxMCP.ts
export class GEOXMCPClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'https://geoxarifOS.fastmcp.app') {
    this.baseUrl = baseUrl;
  }

  async verifyGeospatial(
    lat: number,
    lon: number,
    radiusM: number = 1000
  ): Promise<GeospatialVerification> {
    const response = await fetch(`${this.baseUrl}/mcp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'tools/call',
        params: {
          name: 'geox_verify_geospatial',
          arguments: { lat, lon, radius_m: radiusM },
        },
      }),
    });

    return response.json();
  }

  async evaluateProspect(
    prospectId: string,
    interpretationId: string
  ): Promise<ProspectEvaluation> {
    const response = await fetch(`${this.baseUrl}/mcp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'tools/call',
        params: {
          name: 'geox_evaluate_prospect',
          arguments: { prospect_id: prospectId, interpretation_id: interpretationId },
        },
      }),
    });

    return response.json();
  }

  async healthCheck(): Promise<HealthStatus> {
    const response = await fetch(`${this.baseUrl}/health/details`);
    return response.json();
  }
}
```

---

## Project Structure

```
geox-gui/
├── src/
│   ├── components/
│   │   ├── EarthCanvas/           # 2D/3D map
│   │   │   ├── EarthCanvas.tsx
│   │   │   ├── Map2D.tsx          # MapLibre
│   │   │   ├── Globe3D.tsx        # Cesium
│   │   │   └── LayerTree.tsx
│   │   ├── SeisView/              # Seismic viewer
│   │   │   ├── SeisView.tsx
│   │   │   ├── WebGLRenderer.ts
│   │   │   ├── CandidateOverlay.tsx
│   │   │   └── PickOverlay.tsx
│   │   ├── LogDock/               # Well logs
│   │   │   ├── LogDock.tsx
│   │   │   ├── LogTrack.tsx
│   │   │   └── TieIndicator.tsx
│   │   ├── OutcropLens/           # Image analysis
│   │   │   ├── OutcropLens.tsx
│   │   │   └── AnnotationTool.tsx
│   │   ├── ProspectDesk/          # Decision panel
│   │   │   ├── ProspectDesk.tsx
│   │   │   ├── EvidenceStack.tsx
│   │   │   ├── RiskMatrix.tsx
│   │   │   └── HumanDecisionZone.tsx
│   │   ├── WitnessBadges/         # Governance
│   │   │   ├── WitnessBadges.tsx
│   │   │   ├── FloorBadge.tsx
│   │   │   └── StatusRibbon.tsx
│   │   └── Layout/                # Main layout
│   │       ├── MainLayout.tsx
│   │       ├── Sidebar.tsx
│   │       └── Toolbar.tsx
│   ├── hooks/
│   │   ├── useGEOXMCP.ts          # MCP client
│   │   ├── useSync.ts             # Cross-panel sync
│   │   ├── useGovernance.ts       # F1-F13 checks
│   │   └── useSeismic.ts          # Seismic data
│   ├── store/
│   │   └── geoxStore.ts           # Zustand store
│   ├── utils/
│   │   ├── geospatial.ts          # Coordinate ops
│   │   ├── grounding.ts           # F4 checks
│   │   ├── seismic.ts             # Seismic math
│   │   └── vault.ts               # VAULT999 logging
│   ├── types/
│   │   └── index.ts               # TypeScript types
│   ├── App.tsx
│   └── main.tsx
├── public/
│   └── data/                      # Sample data
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Set up React + Vite + Tailwind project
- [ ] Integrate MapLibre GL JS (2D map)
- [ ] Basic layout (left/center/right panels)
- [ ] Zustand state management
- [ ] GEOX MCP client

### Phase 2: Core Visualization (Week 3-4)
- [ ] Seismic WebGL renderer
- [ ] Well log viewer (Canvas)
- [ ] Coordinate sync system
- [ ] Layer tree UI

### Phase 3: Governance (Week 5)
- [ ] WitnessBadges component
- [ ] F4 grounding checks
- [ ] F7 multiple candidate enforcement
- [ ] F13 human decision zone

### Phase 4: 3D & Polish (Week 6)
- [ ] CesiumJS 3D globe
- [ ] OutcropLens image viewer
- [ ] ProspectDesk decision panel
- [ ] VAULT999 integration

### Phase 5: Integration (Week 7)
- [ ] Connect to Horizon GEOX
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Documentation

---

## Package.json

```json
{
  "name": "geox-gui",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "maplibre-gl": "^4.0.0",
    "cesium": "^1.114.0",
    "d3": "^7.8.5",
    "zustand": "^4.5.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-tooltip": "^1.0.7",
    "lucide-react": "^0.344.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.1"
  },
  "devDependencies": {
    "@types/react": "^18.2.55",
    "@types/react-dom": "^18.2.19",
    "@types/d3": "^7.4.3",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.2.2",
    "vite": "^5.1.0",
    "vite-plugin-cesium": "^1.2.22",
    "tailwindcss": "^3.4.1",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.35"
  }
}
```

---

## Key Design Principles

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
┌─────────────────────┐
│ ⚠️ HUMAN REQUIRED   │
│ F13 SOVEREIGN       │
│                     │
│ [HOLD] [PARTIAL]    │
│ [SEAL - requires    │
│  human sign-off]    │
└─────────────────────┘
```

---

## Seal

**DITEMPA BUKAN DIBERI**

*Map for grounding, seismic for subsurface story, logs for constraint, outcrop for analog, prospect panel for judgment, badges for discipline.*
