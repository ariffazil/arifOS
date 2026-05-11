# KIMI SWARM DIRECTIVE: GEOX DESIGN FORGE (000-999)

## MISSION IDENTITY: THE GEOX CORE

GEOX is not a visualization tool; it is a **Governed Earth Intelligence Engine**. It is the subsurface coprocessor for **arifOS**, designed to provide "Actionable Ground Truth" for the 888_JUDGE paradigm. The core philosophy is **"DITEMPA BUKAN DIBERI" (Forged, Not Given)**.

## ARCHITECTURAL SCOPE: 000-999 (VOID TO META-DIMENSIONAL)

You are tasked with forging the final interface manifest for the GEOX Command Center. Your design must scale across the following domains:

### 1. THE VOID (000-249): Decision & Risk

- **Focus**: Volumetrics, Economics, and 888_HOLD Governance.
- **Aesthetic**: Brutalist, forensic, high-contrast. The "Decision Manifold".
- **Interaction**: Stochastic model results, GCOS distribution curves, and constitutional floor validations.

### 2. THE 1D INTERFACE (250-499): Borehole Intelligence

- **Focus**: Well Context Desk & RATLAS.
- **Aesthetic**: Surgical precision. JetBrains Mono typography. High-density data strips.
- **Interaction**: LAS log comparisons, material calibration overlays, and probabilistic formation matching.

### 3. THE 2D INTERFACE (500-749): Planar Operations

- **Focus**: Seismic Viewer & Analog Forge.
- **Aesthetic**: Signal-centric. Vibrant spectral gradients. Scan-line overlays.
- **Interaction**: Real-time attribute generation (RMS, Sweetness), pixel-to-depth calibration, and automated GCP detection.

### 4. THE 3D/META DOMAIN (750-999): Volume & Unified Intel

- **Focus**: Basin Explorer & 3D Volume Interpretation.
- **Aesthetic**: Immersive, holographic, meta-dimensional.
- **Interaction**: GemPy structural meshes, regional stratigraphic hydration via Macrostrat, and unified manifold views where 1D/2D/3D intersect logically.

### 5. THE LEM METABOLIZER (1000-1249): 4D Back-Propagation

- **Focus**: Forward/Inverse Earth Engines.
- **Aesthetic**: Theoretical, high-density matrix notation. Spectral themes mapping State to Signal.
- **Interaction**: Execution of `EARTH.CANON_9` back-propagation from 1D Borehole → 2D Seismic → 3D Basin. F7 convergence auditing ($\pm 4\%$).

## DESIGN PHILOSOPHY & UI REQUIREMENTS

- **Elite Aesthetics**: Modern dark mode (#0A0C0E), glassmorphism, accent amber (#F59E0B), and emerald status indicators (#10B981).
- **Zero Theater**: Every UI element must represent real data or governing logic. No decorative generic charts.
- **Typography**: Inter for UI, JetBrains Mono for data/coordinates.
- **Micro-animations**: Subtle transitions for context switching and data hydration.
- **Consistency**: Unified headers, constitutional floor badges (F1, F2, F7, F11, etc.), and system status telemetry.
## ANALOG-TO-DIGITAL SCALE & TEMPORAL CONSTITUTION

The GEOX Forge must transform analog scans into **Digital Truth** anchored in 4D space:


- **Earth True Scale (1D/2D/3D)**: Every pixel in an uploaded log (1D) or map/section (2D) must be calibrated to physical units (meters/feet) and georeferenced to global coordinates (latitude/longitude/TWT).
- **Temporal Space (Chronostratigraphy)**: Vertical dimensions are not just depth; they are **Time**. Digitized features must be mappable to the geological timescale (Ma) via automated stratigraphic hydration (Macrostrat).
- **Vision Intelligence**: Use computer vision to detect log tracks and map control points (GCPs), ensuring the "Digital Twin" is geomechanically and chronologically consistent.


## THE ANALOG-TO-DIGITAL 4D FORGE
Forge the vision intelligence required to transform analog artifacts into **Digital Truth** anchored in Earth's True Scale and Temporal Space.

### 1. Spatial Sovereignty (True Scale)
- **1D Logs**: Calibration of scanned raster logs to absolute vertical depth (TVD) using semi-automated scale discovery.
- **2D Sections/Maps**: Pixel-to-metric transformation using Ground Control Points (GCPs). All Planar Operations [500-749] must assume a WGS84/UTM geodetic datum.
- **3D Volumes**: Transformation of interpretative sketches into GemPy-compatible structural manifests georeferenced to the Basin model.

### 2. Temporal Synchronization (Deep Time)
- **Chronostratigraphic Mapping**: All vertical axes are dual-mode: **Depth (m)** and **Time (Ma)**.
- **Dynamic Inversion**: Use the **EARTH.CANON_9** state vector to model how properties (P, T, φ) evolved over geologic history.
- **Metadata Tagging**: Every digitized event must carry a `temporal_epoch` and `spatial_datum` signature.

### 3. Intelligence Integration
- **Vision-to-Digital**: Implement automated character recognition for log tracks and scale-bars.
- **LLM-Copilot**: Use the Gemini Intelligence Layer to provide chronostratigraphic context for digitized horizons (e.g., "This horizon represents the Top Miocene [~5.3 Ma] flooding event").

---

## YOUR TASK: FORGE THE MANIFEST

1.  **Refine the Core UI**: Standardize the shared component library across all apps.
2.  **Forge the Scale-Aware Layer**: Implement the recursive georeferencing logic for 1D/2D/3D analog-to-digital transformation. Ensure maps/logs are calibrated to Earth True Scale and Temporal Chronostratigraphy.
3.  **Hydrate with Complexity**: Ensure each app (Well Context, Seismic, Basin, Forge, Risk) feels like a professional-grade instrument.
4.  **Seal the Interface**: Implement the final responsive layout and spectral themes that define the v1.0.0 GEOX "Heavy Witness" state.

## GOLDEN AESTHETIC & INTELLIGENCE MANIFEST (CANONICAL DNA)
The following React manifest serves as the **Canonical Specification** for both UI/UX and Intelligence Integration. It is anchored by the [EARTH.CANON_9 Spec](file:///c:/ariffazil/GEOX/docs/EARTH_CANON_9_SPEC.md).

```jsx
// --- CANONICAL STYLING & INTELLIGENCE MANIFEST ---
import React, { useState, useEffect, useRef } from 'react';

// --- INTELLIGENCE FLOOR: useGeminiAPI ---
// All geological interpretations and decision verdicts must flow through this bridge.
const useGeminiAPI = () => {
  const [isLoading, setIsLoading] = useState(false);
  const generate = async (prompt, systemInstruction) => {
    setIsLoading(true);
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=YOUR_API_KEY`;
    const payload = {
      contents: [{ parts: [{ text: prompt }] }],
      systemInstruction: { parts: [{ text: systemInstruction || "You are an elite, brutalist geological AI assistant." }] }
    };
    // Fetch logic with exponential backoff...
  };
  return { generate, isLoading };
};

const StyleInject = () => (
  <style dangerouslySetInnerHTML={{ __html: `
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
    :root {
      --bg-void: #0A0C0E; --accent-amber: #F59E0B; --accent-emerald: #10B981; --accent-purple: #8B5CF6;
      --glass-border: rgba(255, 255, 255, 0.05); --glass-bg: rgba(20, 24, 28, 0.6);
    }
    body { background-color: var(--bg-void); color: #E2E8F0; font-family: 'Inter', sans-serif; }
    .glass-panel { background: var(--glass-bg); backdrop-filter: blur(12px); border: 1px solid var(--glass-border); }
    .scanline { position: absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,0.1) 50%, rgba(0,0,0,0.1)); background-size: 100% 4px; pointer-events: none; opacity: 0.3; }
    @keyframes sweep { 0% { transform: translateY(-100%); } 100% { transform: translateY(1000%); } }
    .radar-sweep { position: absolute; top:0; left:0; width:100%; height:10%; background: linear-gradient(to bottom, transparent, rgba(16, 185, 129, 0.1)); animation: sweep 8s linear infinite; pointer-events: none; }
  `}} />
);

// [Domain Execution Highlights]
// 1. DomainVoid: Monte Carlo P90/P50/P10 analysis + LGG GCOS Verdicts.
// 2. Domain1D: Automated Petrophysical Interpretation via SVG log-pattern analysis.
// 3. Domain2D: Attribute Synthesis (RMS, Coherence mapping).
// 4. Domain3D: Volumetric Mesh Integration & Basin Hydration.
```

## SEAL


DITEMPA BUKAN DIBERI. Proceed with the Design Forge.

999_SEAL.
