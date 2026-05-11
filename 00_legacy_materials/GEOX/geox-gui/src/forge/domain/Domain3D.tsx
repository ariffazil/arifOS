/**
 * Domain3D — Volume & Basin Explorer (750-999)
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * Basin Explorer & 3D Volume Interpretation implementation.
 * Immersive, holographic, meta-dimensional aesthetic.
 *
 * Features:
 * - GemPy structural mesh visualization
 * - Regional stratigraphic hydration via Macrostrat
 * - Unified manifold views (1D/2D/3D intersection)
 * - 3D seismic volume rendering
 */

import React, { useState, useRef, useEffect, useMemo } from 'react';
import {
  Box,
  Globe,
  Layers,
  Activity,
  Maximize2,
  RotateCw,
  Move,
  ZoomIn,
  ZoomOut,
  Grid3x3,
  Target,
  MapPin,
  Database,
  Cpu,
  Eye,
  EyeOff,
} from 'lucide-react';

/**
 * 3D Volume data structure
 */
interface Volume3D {
  inlineRange: { min: number; max: number; step: number };
  xlineRange: { min: number; max: number; step: number };
  timeRange: { min: number; max: number; step: number };
  data: Float32Array; // Flattened 3D array
  cornerPoints: Array<{
    inline: number;
    xline: number;
    x: number;
    y: number;
  }>;
  crs: string;
}

/**
 * Structural surface from GemPy
 */
interface StructuralSurface {
  name: string;
  color: string;
  vertices: Array<{ x: number; y: number; z: number }>;
  indices: number[]; // Triangle indices
  visible: boolean;
  opacity: number;
}

/**
 * Well trajectory in 3D
 */
interface WellTrajectory3D {
  wellId: string;
  wellName: string;
  color: string;
  path: Array<{
    x: number;
    y: number;
    z: number;
    md: number;
    tvd: number;
  }>;
  visible: boolean;
}

/**
 * Basin information
 */
interface BasinInfo {
  name: string;
  description: string;
  location: {
    centerLat: number;
    centerLon: number;
    extent: { minX: number; maxX: number; minY: number; maxY: number };
  };
  stratigraphy: Array<{
    formation: string;
    age: number; // Ma
    lithology: string;
    thickness: { min: number; max: number };
  }>;
  resources: {
    oilInPlace: number; // MMbbl
    gasInPlace: number; // Bcf
    recoverableOil: number;
    recoverableGas: number;
  };
}

/**
 * Camera/view state
 */
interface ViewState3D {
  zoom: number;
  rotation: { x: number; y: number; z: number };
  pan: { x: number; y: number };
  slice: {
    inline: number | null;
    xline: number | null;
    time: number | null;
  };
}

type ViewMode3D = 'volume' | 'surface' | 'slice' | 'basin';

interface Domain3DProps {
  volume?: Volume3D;
  surfaces?: StructuralSurface[];
  wells?: WellTrajectory3D[];
  basin?: BasinInfo;
  onPointSelect?: (point: { x: number; y: number; z: number }) => void;
  onSliceChange?: (slice: { inline?: number; xline?: number; time?: number }) => void;
}

/**
 * Simplified 3D Canvas Renderer
 */
const VolumeCanvas3D: React.FC<{
  volume?: Volume3D;
  surfaces: StructuralSurface[];
  wells: WellTrajectory3D[];
  viewState: ViewState3D;
  viewMode: ViewMode3D;
  width: number;
  height: number;
}> = ({ volume, surfaces, wells, viewState, viewMode, width, height }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear
    ctx.fillStyle = '#0A0C0E';
    ctx.fillRect(0, 0, width, height);

    // Draw gradient background for depth effect
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, '#0D1013');
    gradient.addColorStop(0.5, '#0A0C0E');
    gradient.addColorStop(1, '#07090A');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    const centerX = width / 2 + viewState.pan.x;
    const centerY = height / 2 + viewState.pan.y;
    const scale = viewState.zoom;

    // Project 3D to 2D (isometric-ish)
    const project = (x: number, y: number, z: number) => {
      const rotX = viewState.rotation.x * (Math.PI / 180);
      const rotY = viewState.rotation.y * (Math.PI / 180);

      // Simple rotation
      const x1 = x * Math.cos(rotY) - z * Math.sin(rotY);
      const z1 = x * Math.sin(rotY) + z * Math.cos(rotY);
      const y1 = y * Math.cos(rotX) - z1 * Math.sin(rotX);

      return {
        x: centerX + x1 * scale,
        y: centerY + y1 * scale,
      };
    };

    // Draw volume bounding box
    if (volume && viewMode === 'volume') {
      ctx.strokeStyle = 'rgba(90, 103, 115, 0.3)';
      ctx.lineWidth = 1;
      ctx.setLineDash([5, 5]);

      const { inlineRange, xlineRange, timeRange } = volume;
      const w = (inlineRange.max - inlineRange.min) * 10;
      const h = (xlineRange.max - xlineRange.min) * 10;
      const d = (timeRange.max - timeRange.min) * 0.5;

      // Draw wireframe box
      const corners = [
        { x: -w/2, y: -h/2, z: -d/2 },
        { x: w/2, y: -h/2, z: -d/2 },
        { x: w/2, y: h/2, z: -d/2 },
        { x: -w/2, y: h/2, z: -d/2 },
        { x: -w/2, y: -h/2, z: d/2 },
        { x: w/2, y: -h/2, z: d/2 },
        { x: w/2, y: h/2, z: d/2 },
        { x: -w/2, y: h/2, z: d/2 },
      ];

      const edges = [
        [0, 1], [1, 2], [2, 3], [3, 0], // Bottom face
        [4, 5], [5, 6], [6, 7], [7, 4], // Top face
        [0, 4], [1, 5], [2, 6], [3, 7], // Vertical edges
      ];

      ctx.beginPath();
      edges.forEach(([a, b]) => {
        const p1 = project(corners[a].x, corners[a].y, corners[a].z);
        const p2 = project(corners[b].x, corners[b].y, corners[b].z);
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
      });
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // Draw structural surfaces
    surfaces.filter(s => s.visible).forEach((surface) => {
      ctx.strokeStyle = surface.color;
      ctx.lineWidth = 1.5;
      ctx.globalAlpha = surface.opacity;

      // Draw as wireframe mesh
      ctx.beginPath();
      for (let i = 0; i < surface.indices.length; i += 3) {
        const v1 = surface.vertices[surface.indices[i]];
        const v2 = surface.vertices[surface.indices[i + 1]];
        const v3 = surface.vertices[surface.indices[i + 2]];

        const p1 = project(v1.x, v1.y, v1.z);
        const p2 = project(v2.x, v2.y, v2.z);
        const p3 = project(v3.x, v3.y, v3.z);

        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.lineTo(p3.x, p3.y);
        ctx.closePath();
      }
      ctx.stroke();
      ctx.globalAlpha = 1;
    });

    // Draw well trajectories
    wells.filter(w => w.visible).forEach((well) => {
      ctx.strokeStyle = well.color;
      ctx.lineWidth = 2;
      ctx.beginPath();

      well.path.forEach((point, idx) => {
        const p = project(point.x, point.y, point.z);
        if (idx === 0) {
          ctx.moveTo(p.x, p.y);
        } else {
          ctx.lineTo(p.x, p.y);
        }
      });
      ctx.stroke();

      // Well head marker
      if (well.path.length > 0) {
        const head = project(well.path[0].x, well.path[0].y, well.path[0].z);
        ctx.fillStyle = well.color;
        ctx.beginPath();
        ctx.arc(head.x, head.y, 4, 0, Math.PI * 2);
        ctx.fill();
      }
    });

    // Draw axis indicators
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.5)';
    ctx.lineWidth = 2;
    const axisLen = 50;
    const origin = project(0, 0, 0);

    // X axis (red)
    ctx.strokeStyle = '#EF4444';
    ctx.beginPath();
    ctx.moveTo(origin.x, origin.y);
    const xEnd = project(axisLen, 0, 0);
    ctx.lineTo(xEnd.x, xEnd.y);
    ctx.stroke();

    // Y axis (green)
    ctx.strokeStyle = '#10B981';
    ctx.beginPath();
    ctx.moveTo(origin.x, origin.y);
    const yEnd = project(0, axisLen, 0);
    ctx.lineTo(yEnd.x, yEnd.y);
    ctx.stroke();

    // Z axis (blue)
    ctx.strokeStyle = '#3B82F6';
    ctx.beginPath();
    ctx.moveTo(origin.x, origin.y);
    const zEnd = project(0, 0, axisLen);
    ctx.lineTo(zEnd.x, zEnd.y);
    ctx.stroke();

  }, [volume, surfaces, wells, viewState, viewMode, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="cursor-move"
    />
  );
};

/**
 * Basin Info Panel
 */
const BasinInfoPanel: React.FC<{ basin: BasinInfo }> = ({ basin }) => (
  <div className="geox-card">
    <div className="geox-card__header">
      <div className="flex items-center gap-2">
        <Globe className="w-4 h-4 text-emerald-500" />
        <span className="geox-card__title">{basin.name}</span>
      </div>
    </div>
    <div className="geox-card__body space-y-4">
      <p className="text-xs text-slate-400 leading-relaxed">{basin.description}</p>

      <div className="grid grid-cols-2 gap-3">
        <div className="p-2 bg-slate-950/50 rounded">
          <span className="text-[10px] text-slate-500 uppercase block">Oil in Place</span>
          <span className="text-lg font-mono font-bold text-emerald-400">
            {basin.resources.oilInPlace}
            <span className="text-xs text-slate-500 ml-1">MMbbl</span>
          </span>
        </div>
        <div className="p-2 bg-slate-950/50 rounded">
          <span className="text-[10px] text-slate-500 uppercase block">Gas in Place</span>
          <span className="text-lg font-mono font-bold text-cyan-400">
            {basin.resources.gasInPlace}
            <span className="text-xs text-slate-500 ml-1">Bcf</span>
          </span>
        </div>
        <div className="p-2 bg-slate-950/50 rounded">
          <span className="text-[10px] text-slate-500 uppercase block">Recoverable Oil</span>
          <span className="text-lg font-mono font-bold text-amber-400">
            {basin.resources.recoverableOil}
            <span className="text-xs text-slate-500 ml-1">MMbbl</span>
          </span>
        </div>
        <div className="p-2 bg-slate-950/50 rounded">
          <span className="text-[10px] text-slate-500 uppercase block">Recoverable Gas</span>
          <span className="text-lg font-mono font-bold text-violet-400">
            {basin.resources.recoverableGas}
            <span className="text-xs text-slate-500 ml-1">Bcf</span>
          </span>
        </div>
      </div>

      <div>
        <span className="text-[10px] text-slate-500 uppercase block mb-2">Stratigraphy</span>
        <div className="space-y-1">
          {basin.stratigraphy.map((layer, idx) => (
            <div key={idx} className="flex items-center justify-between text-xs p-1.5 bg-slate-950/30 rounded">
              <span className="text-slate-300">{layer.formation}</span>
              <div className="flex items-center gap-3">
                <span className="font-mono text-slate-500">{layer.age} Ma</span>
                <span className="text-[10px] text-slate-600">{layer.lithology}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

/**
 * Layer Control Panel
 */
const LayerControlPanel: React.FC<{
  surfaces: StructuralSurface[];
  wells: WellTrajectory3D[];
  onSurfaceToggle: (name: string) => void;
  onWellToggle: (id: string) => void;
}> = ({ surfaces, wells, onSurfaceToggle, onWellToggle }) => (
  <div className="geox-card">
    <div className="geox-card__header">
      <div className="flex items-center gap-2">
        <Layers className="w-4 h-4 text-emerald-500" />
        <span className="geox-card__title">Layers</span>
      </div>
    </div>
    <div className="geox-card__body">
      <div className="mb-4">
        <span className="text-[10px] font-mono text-slate-500 uppercase block mb-2">Surfaces</span>
        <div className="space-y-1">
          {surfaces.map((surface) => (
            <label
              key={surface.name}
              className="flex items-center gap-2 p-1.5 rounded hover:bg-slate-800/50 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={surface.visible}
                onChange={() => onSurfaceToggle(surface.name)}
                className="rounded border-slate-600"
              />
              <div
                className="w-3 h-3 rounded"
                style={{ backgroundColor: surface.color }}
              />
              <span className="text-xs text-slate-300">{surface.name}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <span className="text-[10px] font-mono text-slate-500 uppercase block mb-2">Wells</span>
        <div className="space-y-1">
          {wells.map((well) => (
            <label
              key={well.wellId}
              className="flex items-center gap-2 p-1.5 rounded hover:bg-slate-800/50 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={well.visible}
                onChange={() => onWellToggle(well.wellId)}
                className="rounded border-slate-600"
              />
              <div
                className="w-3 h-3 rounded"
                style={{ backgroundColor: well.color }}
              />
              <span className="text-xs text-slate-300">{well.wellName}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  </div>
);

/**
 * View Controls Component
 */
const ViewControls: React.FC<{
  viewState: ViewState3D;
  viewMode: ViewMode3D;
  onViewStateChange: (state: Partial<ViewState3D>) => void;
  onViewModeChange: (mode: ViewMode3D) => void;
}> = ({ viewState, viewMode, onViewStateChange, onViewModeChange }) => (
  <div className="geox-card">
    <div className="geox-card__header">
      <div className="flex items-center gap-2">
        <Box className="w-4 h-4 text-emerald-500" />
        <span className="geox-card__title">View Controls</span>
      </div>
    </div>
    <div className="geox-card__body space-y-3">
      <div>
        <label className="text-[10px] font-mono text-slate-500 uppercase block mb-1">Mode</label>
        <div className="grid grid-cols-2 gap-2">
          {(['volume', 'surface', 'slice', 'basin'] as ViewMode3D[]).map((mode) => (
            <button
              key={mode}
              onClick={() => onViewModeChange(mode)}
              className={`geox-btn text-[10px] py-1 ${
                viewMode === mode ? 'geox-btn--primary' : 'geox-btn--ghost'
              }`}
            >
              {mode.charAt(0).toUpperCase() + mode.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="text-[10px] font-mono text-slate-500 uppercase block mb-1">
          Zoom: {viewState.zoom.toFixed(1)}x
        </label>
        <input
          type="range"
          min={0.1}
          max={3}
          step={0.1}
          value={viewState.zoom}
          onChange={(e) => onViewStateChange({ zoom: Number(e.target.value) })}
          className="w-full"
        />
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="text-[10px] font-mono text-slate-500 uppercase block mb-1">Rot X</label>
          <input
            type="range"
            min={-180}
            max={180}
            value={viewState.rotation.x}
            onChange={(e) => onViewStateChange({
              rotation: { ...viewState.rotation, x: Number(e.target.value) }
            })}
            className="w-full"
          />
        </div>
        <div>
          <label className="text-[10px] font-mono text-slate-500 uppercase block mb-1">Rot Y</label>
          <input
            type="range"
            min={-180}
            max={180}
            value={viewState.rotation.y}
            onChange={(e) => onViewStateChange({
              rotation: { ...viewState.rotation, y: Number(e.target.value) }
            })}
            className="w-full"
          />
        </div>
      </div>

      {viewMode === 'slice' && (
        <div>
          <label className="text-[10px] font-mono text-slate-500 uppercase block mb-1">Time Slice</label>
          <input
            type="range"
            min={0}
            max={3000}
            step={10}
            value={viewState.slice.time || 0}
            onChange={(e) => onViewStateChange({
              slice: { ...viewState.slice, time: Number(e.target.value) }
            })}
            className="w-full"
          />
        </div>
      )}
    </div>
  </div>
);

/**
 * Main Domain3D Component
 */
export const Domain3D: React.FC<Domain3DProps> = ({
  volume = defaultVolume,
  surfaces: initialSurfaces = defaultSurfaces,
  wells: initialWells = defaultWells,
  basin = defaultBasin,
  onPointSelect = () => {},
  onSliceChange = () => {},
}) => {
  const [viewState, setViewState] = useState<ViewState3D>({
    zoom: 0.8,
    rotation: { x: -30, y: 45, z: 0 },
    pan: { x: 0, y: 0 },
    slice: { inline: null, xline: null, time: 1500 },
  });
  const [viewMode, setViewMode] = useState<ViewMode3D>('surface');
  const [surfaces, setSurfaces] = useState<StructuralSurface[]>(initialSurfaces);
  const [wells, setWells] = useState<WellTrajectory3D[]>(initialWells);

  const containerRef = useRef<HTMLDivElement>(null);
  const [canvasSize, setCanvasSize] = useState({ width: 800, height: 600 });

  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        setCanvasSize({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight,
        });
      }
    };
    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, []);

  const toggleSurface = (name: string) => {
    setSurfaces((prev) =>
      prev.map((s) => (s.name === name ? { ...s, visible: !s.visible } : s))
    );
  };

  const toggleWell = (id: string) => {
    setWells((prev) =>
      prev.map((w) => (w.wellId === id ? { ...w, visible: !w.visible } : w))
    );
  };

  return (
    <div className="h-full flex flex-col bg-[#0A0C0E] geox-root">
      {/* Domain Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-900/50">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-sm font-bold text-white tracking-tight">Domain3D</span>
          <span className="text-xs font-mono text-emerald-500">750-999</span>
          <span className="geox-domain-indicator geox-domain-indicator--3d">Volume</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs">
            <Database className="w-3 h-3 text-slate-500" />
            <span className="text-slate-500">Volume:</span>
            <span className="font-mono text-emerald-400">
              {volume.inlineRange.max - volume.inlineRange.min} ×{' '}
              {volume.xlineRange.max - volume.xlineRange.min} ×{' '}
              {volume.timeRange.max - volume.timeRange.min}ms
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <div className="w-72 border-r border-slate-800 bg-slate-900/30 overflow-auto geox-scroll p-4 space-y-4">
          <BasinInfoPanel basin={basin} />
          <ViewControls
            viewState={viewState}
            viewMode={viewMode}
            onViewStateChange={(update) => setViewState((prev) => ({ ...prev, ...update }))}
            onViewModeChange={setViewMode}
          />
          <LayerControlPanel
            surfaces={surfaces}
            wells={wells}
            onSurfaceToggle={toggleSurface}
            onWellToggle={toggleWell}
          />
        </div>

        {/* 3D Viewport */}
        <div className="flex-1 flex flex-col">
          {/* Toolbar */}
          <div className="h-10 border-b border-slate-800 bg-slate-900/50 flex items-center px-4 gap-2">
            <button
              onClick={() => setViewState((prev) => ({ ...prev, zoom: prev.zoom * 1.2 }))}
              className="geox-btn geox-btn--ghost p-1.5"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewState((prev) => ({ ...prev, zoom: prev.zoom / 1.2 }))}
              className="geox-btn geox-btn--ghost p-1.5"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <div className="h-4 w-px bg-slate-700 mx-1" />
            <button
              onClick={() => setViewState((prev) => ({
                ...prev,
                rotation: { x: -30, y: prev.rotation.y + 15, z: 0 }
              }))}
              className="geox-btn geox-btn--ghost p-1.5"
            >
              <RotateCw className="w-4 h-4" />
            </button>
            <div className="h-4 w-px bg-slate-700 mx-1" />
            <button className="geox-btn geox-btn--ghost p-1.5">
              <Grid3x3 className="w-4 h-4" />
            </button>
            <div className="flex-1" />
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <MapPin className="w-3 h-3" />
              <span className="font-mono">
                {basin.location.centerLat.toFixed(4)}°N, {basin.location.centerLon.toFixed(4)}°E
              </span>
            </div>
          </div>

          {/* 3D Canvas */}
          <div ref={containerRef} className="flex-1 relative overflow-hidden">
            <VolumeCanvas3D
              volume={volume}
              surfaces={surfaces}
              wells={wells}
              viewState={viewState}
              viewMode={viewMode}
              width={canvasSize.width}
              height={canvasSize.height}
            />

            {/* Corner info */}
            <div className="absolute top-4 left-4 geox-glass px-3 py-2 rounded-lg">
              <div className="text-[10px] font-mono text-slate-500 uppercase mb-1">View</div>
              <div className="text-xs font-mono text-emerald-400">
                {viewMode.toUpperCase()}
              </div>
            </div>

            <div className="absolute bottom-4 right-4 geox-glass px-3 py-2 rounded-lg">
              <div className="text-[10px] font-mono text-slate-500 uppercase mb-1">Rotation</div>
              <div className="text-xs font-mono text-slate-300">
                X:{viewState.rotation.x}° Y:{viewState.rotation.y}°
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Default data
const defaultVolume: Volume3D = {
  inlineRange: { min: 1000, max: 1500, step: 1 },
  xlineRange: { min: 2000, max: 2500, step: 1 },
  timeRange: { min: 0, max: 3000, step: 4 },
  data: new Float32Array(500 * 500 * 750),
  cornerPoints: [
    { inline: 1000, xline: 2000, x: 0, y: 0 },
    { inline: 1000, xline: 2500, x: 5000, y: 0 },
    { inline: 1500, xline: 2500, x: 5000, y: 5000 },
    { inline: 1500, xline: 2000, x: 0, y: 5000 },
  ],
  crs: 'EPSG:4326',
};

const defaultSurfaces: StructuralSurface[] = [
  {
    name: 'Seabed',
    color: '#10B981',
    vertices: Array.from({ length: 100 }, (_, i) => ({
      x: (i % 10) * 500 - 2500,
      y: Math.floor(i / 10) * 500 - 2500,
      z: 100 + Math.sin(i * 0.5) * 20,
    })),
    indices: Array.from({ length: 162 }, (_, i) => i), // Simplified mesh
    visible: true,
    opacity: 0.8,
  },
  {
    name: 'Top Reservoir',
    color: '#F59E0B',
    vertices: Array.from({ length: 100 }, (_, i) => ({
      x: (i % 10) * 500 - 2500,
      y: Math.floor(i / 10) * 500 - 2500,
      z: 800 + Math.sin(i * 0.3) * 100,
    })),
    indices: Array.from({ length: 162 }, (_, i) => i),
    visible: true,
    opacity: 0.9,
  },
  {
    name: 'Base Reservoir',
    color: '#8B5CF6',
    vertices: Array.from({ length: 100 }, (_, i) => ({
      x: (i % 10) * 500 - 2500,
      y: Math.floor(i / 10) * 500 - 2500,
      z: 1200 + Math.sin(i * 0.3) * 80,
    })),
    indices: Array.from({ length: 162 }, (_, i) => i),
    visible: true,
    opacity: 0.9,
  },
];

const defaultWells: WellTrajectory3D[] = [
  {
    wellId: 'W-001',
    wellName: 'Pilot-1',
    color: '#06B6D4',
    path: Array.from({ length: 50 }, (_, i) => ({
      x: Math.sin(i * 0.1) * 100,
      y: Math.cos(i * 0.1) * 50,
      z: i * 50,
      md: i * 50,
      tvd: i * 48,
    })),
    visible: true,
  },
  {
    wellId: 'W-002',
    wellName: 'Pilot-2',
    color: '#F97316',
    path: Array.from({ length: 50 }, (_, i) => ({
      x: 200 + Math.sin(i * 0.08) * 150,
      y: 100 + Math.cos(i * 0.08) * 30,
      z: i * 50,
      md: i * 50,
      tvd: i * 48,
    })),
    visible: true,
  },
];

const defaultBasin: BasinInfo = {
  name: 'Malay Basin',
  description: 'Tertiary rift basin in the South China Sea. Proven petroleum system with multiple play types including syn-rift clastics and post-rift carbonates.',
  location: {
    centerLat: 5.4321,
    centerLon: 104.5678,
    extent: { minX: 103, maxX: 106, minY: 4, maxY: 7 },
  },
  stratigraphy: [
    { formation: 'Miri Fm', age: 15, lithology: 'Shale', thickness: { min: 200, max: 500 } },
    { formation: 'Belait Fm', age: 20, lithology: 'Sandstone', thickness: { min: 100, max: 400 } },
    { formation: 'Setap Fm', age: 35, lithology: 'Shale', thickness: { min: 300, max: 800 } },
    { formation: 'Temburong Fm', age: 50, lithology: 'Limestone', thickness: { min: 50, max: 200 } },
    { formation: 'Meligan Fm', age: 65, lithology: 'Sandstone', thickness: { min: 100, max: 300 } },
  ],
  resources: {
    oilInPlace: 12500,
    gasInPlace: 45000,
    recoverableOil: 3750,
    recoverableGas: 31500,
  },
};

export default Domain3D;
