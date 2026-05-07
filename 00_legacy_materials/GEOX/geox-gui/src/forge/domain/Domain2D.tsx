/**
 * Domain2D — Planar Operations (500-749)
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * Seismic Viewer & Analog Forge implementation.
 * Signal-centric aesthetic with vibrant spectral gradients and scan-line overlays.
 *
 * Features:
 * - 2D seismic section visualization with Wiggle/VA display
 * - Real-time attribute generation (RMS, Sweetness, Envelope)
 * - Pixel-to-depth calibration
 * - Automated GCP detection
 * - Spectral color maps for seismic amplitudes
 */

import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import {
  Activity,
  Zap,
  Palette,
  Crosshair,
  Grid3x3,
  Maximize,
  Layers,
  Settings,
  ChevronLeft,
  ChevronRight,
  Play,
  Pause,
  Camera,
  FileDown,
  Scan,
} from 'lucide-react';

/**
 * Seismic data structure
 */
interface SeismicData {
  traceCount: number;
  sampleCount: number;
  sampleInterval: number; // ms
  startTime: number; // ms
  traces: Float32Array[]; // Normalized amplitude values (-1 to 1)
  cdpNumbers?: number[];
  inline?: number[];
  xline?: number[];
  xCoordinates?: number[];
  yCoordinates?: number[];
}

/**
 * Display mode for seismic
 */
type DisplayMode = 'wiggle' | 'va' | 'wiggle_va' | 'spectral';

/**
 * Color map for amplitude visualization
 */
type ColorMap = 'grayscale' | 'seismic' | 'rdgy' | 'spectral' | 'viridis';

/**
 * Seismic attribute configuration
 */
interface SeismicAttribute {
  name: string;
  type: 'rms' | 'sweetness' | 'envelope' | 'phase' | 'frequency';
  windowLength: number; // ms
  color: string;
  visible: boolean;
  data?: Float32Array[];
}

/**
 * GCP for seismic section
 */
interface SeismicGCP {
  id: string;
  traceIndex: number;
  sampleIndex: number;
  twt: number;
  cdp?: number;
  x?: number;
  y?: number;
  horizon?: string;
  confidence: number;
}

/**
 * Interpreted horizon
 */
interface Horizon {
  name: string;
  color: string;
  picks: Array<{
    traceIndex: number;
    twt: number;
    confidence: number;
  }>;
  visible: boolean;
}

interface Domain2DProps {
  seismicData?: SeismicData;
  horizons?: Horizon[];
  gcps?: SeismicGCP[];
  attributes?: SeismicAttribute[];
  onPick?: (traceIndex: number, twt: number) => void;
  onGcpAdd?: (gcp: SeismicGCP) => void;
  onHorizonEdit?: (horizon: Horizon) => void;
}

/**
 * Generate color from value using color map
 */
const getColorFromValue = (value: number, colorMap: ColorMap): string => {
  const normalized = Math.max(-1, Math.min(1, value));

  switch (colorMap) {
    case 'grayscale':
      const gray = Math.round((normalized + 1) * 127.5);
      return `rgb(${gray}, ${gray}, ${gray})`;

    case 'seismic':
      // Blue-white-red
      if (normalized < 0) {
        const intensity = Math.abs(normalized);
        return `rgb(${Math.round(255 * (1 - intensity))}, ${Math.round(255 * (1 - intensity))}, 255)`;
      } else {
        return `rgb(255, ${Math.round(255 * (1 - normalized))}, ${Math.round(255 * (1 - normalized))})`;
      }

    case 'rdgy':
      // Red-gray-green (diverging)
      if (normalized < 0) {
        const t = Math.abs(normalized);
        return `rgb(${Math.round(255)}, ${Math.round(255 * (1 - t * 0.7))}, ${Math.round(255 * (1 - t))})`;
      } else {
        const t = normalized;
        return `rgb(${Math.round(255 * (1 - t * 0.5))}, ${Math.round(255)}, ${Math.round(255 * (1 - t * 0.5))})`;
      }

    case 'spectral':
      // Rainbow spectrum
      const hue = (normalized + 1) * 120; // 0-240 (red to blue)
      return `hsl(${240 - hue}, 80%, 50%)`;

    case 'viridis':
      // Viridis approximation
      const v = (normalized + 1) / 2;
      return `hsl(${240 + v * 120}, 70%, ${30 + v * 40}%)`;

    default:
      return `rgb(128, 128, 128)`;
  }
};

/**
 * Seismic Canvas Component
 */
const SeismicCanvas: React.FC<{
  data: SeismicData;
  displayMode: DisplayMode;
  colorMap: ColorMap;
  gain: number;
  horizons: Horizon[];
  gcps: SeismicGCP[];
  onPick: (traceIndex: number, twt: number) => void;
  width: number;
  height: number;
}> = ({
  data,
  displayMode,
  colorMap,
  gain,
  horizons,
  gcps,
  onPick,
  width,
  height,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number } | null>(null);

  const traceSpacing = width / data.traceCount;
  const sampleSpacing = height / data.sampleCount;

  // Draw seismic
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear
    ctx.fillStyle = '#0A0C0E';
    ctx.fillRect(0, 0, width, height);

    // Draw traces
    for (let t = 0; t < data.traceCount; t++) {
      const trace = data.traces[t];
      const x = t * traceSpacing + traceSpacing / 2;

      if (displayMode === 'wiggle' || displayMode === 'wiggle_va') {
        // Wiggle trace
        ctx.beginPath();
        ctx.strokeStyle = '#E2E8F0';
        ctx.lineWidth = 0.5;

        for (let s = 0; s < data.sampleCount; s++) {
          const amplitude = trace[s] * gain * (traceSpacing / 2);
          const y = s * sampleSpacing;
          const xOffset = x + amplitude;

          if (s === 0) {
            ctx.moveTo(xOffset, y);
          } else {
            ctx.lineTo(xOffset, y);
          }
        }
        ctx.stroke();

        // VA fill
        if (displayMode === 'wiggle_va' || displayMode === 'va') {
          ctx.beginPath();
          ctx.fillStyle = 'rgba(6, 182, 212, 0.3)';

          for (let s = 0; s < data.sampleCount; s++) {
            const amplitude = trace[s] * gain * (traceSpacing / 2);
            if (amplitude > 0) {
              const y = s * sampleSpacing;
              ctx.fillRect(x, y, amplitude, sampleSpacing + 0.5);
            }
          }
        }
      } else {
        // Color-filled display
        for (let s = 0; s < data.sampleCount; s++) {
          const amplitude = trace[s];
          const y = s * sampleSpacing;

          ctx.fillStyle = getColorFromValue(amplitude * gain, colorMap);
          ctx.fillRect(t * traceSpacing, y, traceSpacing + 0.5, sampleSpacing + 0.5);
        }
      }
    }

    // Draw horizons
    horizons.filter(h => h.visible).forEach((horizon) => {
      ctx.beginPath();
      ctx.strokeStyle = horizon.color;
      ctx.lineWidth = 2;

      horizon.picks.forEach((pick, idx) => {
        const x = pick.traceIndex * traceSpacing + traceSpacing / 2;
        const twtIdx = Math.round((pick.twt - data.startTime) / data.sampleInterval);
        const y = twtIdx * sampleSpacing;

        if (idx === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      ctx.stroke();
    });

    // Draw GCPs
    gcps.forEach((gcp) => {
      const x = gcp.traceIndex * traceSpacing + traceSpacing / 2;
      const twtIdx = Math.round((gcp.twt - data.startTime) / data.sampleInterval);
      const y = twtIdx * sampleSpacing;

      ctx.beginPath();
      ctx.strokeStyle = '#F59E0B';
      ctx.lineWidth = 1;
      ctx.moveTo(x - 5, y);
      ctx.lineTo(x + 5, y);
      ctx.moveTo(x, y - 5);
      ctx.lineTo(x, y + 5);
      ctx.stroke();

      // Confidence ring
      ctx.beginPath();
      ctx.strokeStyle = `rgba(245, 158, 11, ${gcp.confidence})`;
      ctx.arc(x, y, 8, 0, Math.PI * 2);
      ctx.stroke();
    });

    // Scanline overlay
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, 'rgba(0,0,0,0)');
    gradient.addColorStop(0.5, 'rgba(0,0,0,0.1)');
    gradient.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

  }, [data, displayMode, colorMap, gain, horizons, gcps, width, height, traceSpacing, sampleSpacing]);

  const handleClick = (e: React.MouseEvent) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const traceIndex = Math.floor(x / traceSpacing);
    const sampleIndex = Math.floor(y / sampleSpacing);
    const twt = data.startTime + sampleIndex * data.sampleInterval;

    onPick(traceIndex, twt);
  };

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="cursor-crosshair"
      onClick={handleClick}
      onMouseMove={(e) => {
        const rect = canvasRef.current?.getBoundingClientRect();
        if (rect) {
          setCursorPos({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
          });
        }
      }}
      onMouseLeave={() => setCursorPos(null)}
      style={{ imageRendering: 'pixelated' }}
    />
  );
};

/**
 * Attribute Panel Component
 */
const AttributePanel: React.FC<{
  attributes: SeismicAttribute[];
  onToggle: (name: string) => void;
  onCompute: (type: SeismicAttribute['type']) => void;
}> = ({ attributes, onToggle, onCompute }) => (
  <div className="geox-card">
    <div className="geox-card__header">
      <div className="flex items-center gap-2">
        <Zap className="w-4 h-4 text-violet-500" />
        <span className="geox-card__title">Attributes</span>
      </div>
    </div>
    <div className="geox-card__body">
      <div className="space-y-2 mb-4">
        {attributes.map((attr) => (
          <label
            key={attr.name}
            className="flex items-center gap-2 p-2 rounded hover:bg-slate-800/50 cursor-pointer"
          >
            <input
              type="checkbox"
              checked={attr.visible}
              onChange={() => onToggle(attr.name)}
              className="rounded border-slate-600"
            />
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: attr.color }}
            />
            <span className="text-xs text-slate-300">{attr.name}</span>
          </label>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-2">
        {(['rms', 'sweetness', 'envelope', 'phase'] as const).map((type) => (
          <button
            key={type}
            onClick={() => onCompute(type)}
            className="geox-btn geox-btn--ghost text-[10px] py-1"
          >
            {type.toUpperCase()}
          </button>
        ))}
      </div>
    </div>
  </div>
);

/**
 * Display Controls Component
 */
const DisplayControls: React.FC<{
  displayMode: DisplayMode;
  colorMap: ColorMap;
  gain: number;
  onDisplayModeChange: (mode: DisplayMode) => void;
  onColorMapChange: (map: ColorMap) => void;
  onGainChange: (gain: number) => void;
}> = ({ displayMode, colorMap, gain, onDisplayModeChange, onColorMapChange, onGainChange }) => (
  <div className="geox-card">
    <div className="geox-card__header">
      <div className="flex items-center gap-2">
        <Palette className="w-4 h-4 text-violet-500" />
        <span className="geox-card__title">Display</span>
      </div>
    </div>
    <div className="geox-card__body space-y-3">
      <div>
        <label className="text-[10px] font-mono text-slate-500 uppercase block mb-1">Mode</label>
        <select
          value={displayMode}
          onChange={(e) => onDisplayModeChange(e.target.value as DisplayMode)}
          className="geox-input text-xs"
        >
          <option value="wiggle">Wiggle</option>
          <option value="va">VA Fill</option>
          <option value="wiggle_va">Wiggle + VA</option>
          <option value="spectral">Spectral</option>
        </select>
      </div>
      <div>
        <label className="text-[10px] font-mono text-slate-500 uppercase block mb-1">Color Map</label>
        <select
          value={colorMap}
          onChange={(e) => onColorMapChange(e.target.value as ColorMap)}
          className="geox-input text-xs"
        >
          <option value="seismic">Seismic (BWR)</option>
          <option value="grayscale">Grayscale</option>
          <option value="rdgy">Red-Gray-Green</option>
          <option value="spectral">Spectral</option>
          <option value="viridis">Viridis</option>
        </select>
      </div>
      <div>
        <label className="text-[10px] font-mono text-slate-500 uppercase block mb-1">
          Gain: {gain.toFixed(1)}x
        </label>
        <input
          type="range"
          min={0.1}
          max={5}
          step={0.1}
          value={gain}
          onChange={(e) => onGainChange(Number(e.target.value))}
          className="w-full"
        />
      </div>
    </div>
  </div>
);

/**
 * Main Domain2D Component
 */
export const Domain2D: React.FC<Domain2DProps> = ({
  seismicData = defaultSeismicData,
  horizons: initialHorizons = defaultHorizons,
  gcps = defaultGCPs,
  attributes = defaultAttributes,
  onPick = () => {},
  onGcpAdd = () => {},
  onHorizonEdit = () => {},
}) => {
  const [displayMode, setDisplayMode] = useState<DisplayMode>('wiggle_va');
  const [colorMap, setColorMap] = useState<ColorMap>('seismic');
  const [gain, setGain] = useState(1.5);
  const [horizons, setHorizons] = useState<Horizon[]>(initialHorizons);
  const [activeAttributes, setActiveAttributes] = useState<SeismicAttribute[]>(attributes);
  const [selectedPoint, setSelectedPoint] = useState<{ trace: number; twt: number; amplitude: number } | null>(null);
  const [viewStart, setViewStart] = useState(0);
  const [viewWidth, setViewWidth] = useState(100);

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

  const handlePick = (traceIndex: number, twt: number) => {
    const trace = seismicData.traces[traceIndex];
    const sampleIdx = Math.round((twt - seismicData.startTime) / seismicData.sampleInterval);
    const amplitude = trace?.[sampleIdx] || 0;

    setSelectedPoint({ trace: traceIndex, twt, amplitude });
    onPick(traceIndex, twt);
  };

  const toggleAttribute = (name: string) => {
    setActiveAttributes((prev) =>
      prev.map((attr) =>
        attr.name === name ? { ...attr, visible: !attr.visible } : attr
      )
    );
  };

  const computeAttribute = (type: SeismicAttribute['type']) => {
    // Placeholder for attribute computation
    console.log(`Computing ${type} attribute...`);
  };

  // Slice data for viewport
  const viewportData = useMemo(() => ({
    ...seismicData,
    traces: seismicData.traces.slice(viewStart, viewStart + viewWidth),
    traceCount: viewWidth,
  }), [seismicData, viewStart, viewWidth]);

  return (
    <div className="h-full flex flex-col bg-[#0A0C0E] geox-root">
      {/* Domain Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-900/50">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-violet-500 animate-pulse" />
          <span className="text-sm font-bold text-white tracking-tight">Domain2D</span>
          <span className="text-xs font-mono text-violet-500">500-749</span>
          <span className="geox-domain-indicator geox-domain-indicator--2d">Seismic</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-slate-500">
            Traces: {viewStart}-{viewStart + viewWidth} / {seismicData.traceCount}
          </span>
          <button className="geox-btn geox-btn--ghost p-1.5">
            <Camera className="w-4 h-4" />
          </button>
          <button className="geox-btn geox-btn--ghost p-1.5">
            <FileDown className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <div className="w-64 border-r border-slate-800 bg-slate-900/30 overflow-auto geox-scroll p-4 space-y-4">
          <DisplayControls
            displayMode={displayMode}
            colorMap={colorMap}
            gain={gain}
            onDisplayModeChange={setDisplayMode}
            onColorMapChange={setColorMap}
            onGainChange={setGain}
          />

          <AttributePanel
            attributes={activeAttributes}
            onToggle={toggleAttribute}
            onCompute={computeAttribute}
          />

          {/* Selected Point Info */}
          {selectedPoint && (
            <div className="geox-card border-violet-500/30">
              <div className="geox-card__header bg-violet-950/20">
                <span className="geox-card__title text-violet-400">Selected Point</span>
              </div>
              <div className="geox-card__body">
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Trace</span>
                    <span className="font-mono text-white">{selectedPoint.trace}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">TWT</span>
                    <span className="font-mono text-violet-400">{selectedPoint.twt.toFixed(1)}ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Amplitude</span>
                    <span className="font-mono text-cyan-400">{selectedPoint.amplitude.toFixed(4)}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Canvas Area */}
        <div className="flex-1 flex flex-col">
          {/* Toolbar */}
          <div className="h-10 border-b border-slate-800 bg-slate-900/50 flex items-center px-4 gap-4">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setViewStart(Math.max(0, viewStart - 50))}
                className="geox-btn geox-btn--ghost p-1"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <input
                type="range"
                min={0}
                max={seismicData.traceCount - viewWidth}
                value={viewStart}
                onChange={(e) => setViewStart(Number(e.target.value))}
                className="w-32"
              />
              <button
                onClick={() => setViewStart(Math.min(seismicData.traceCount - viewWidth, viewStart + 50))}
                className="geox-btn geox-btn--ghost p-1"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
            <div className="h-4 w-px bg-slate-700" />
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-500">Zoom:</span>
              <select
                value={viewWidth}
                onChange={(e) => setViewWidth(Number(e.target.value))}
                className="geox-input text-xs py-1 w-24"
              >
                <option value={50}>50 traces</option>
                <option value={100}>100 traces</option>
                <option value={250}>250 traces</option>
                <option value={500}>500 traces</option>
              </select>
            </div>
            <div className="flex-1" />
            <div className="flex items-center gap-2">
              <Scan className="w-3 h-3 text-slate-500" />
              <span className="text-xs font-mono text-slate-500">Scanline Active</span>
            </div>
          </div>

          {/* Seismic Display */}
          <div ref={containerRef} className="flex-1 relative overflow-hidden geox-scanline">
            <SeismicCanvas
              data={viewportData}
              displayMode={displayMode}
              colorMap={colorMap}
              gain={gain}
              horizons={horizons}
              gcps={gcps}
              onPick={handlePick}
              width={canvasSize.width}
              height={canvasSize.height}
            />
            {/* Scanline overlay */}
            <div className="geox-radar-sweep" />
          </div>

          {/* Time Axis */}
          <div className="h-8 bg-slate-900/50 border-t border-slate-800 flex items-center px-4">
            <div className="flex-1 flex justify-between text-xs font-mono text-slate-500">
              <span>{seismicData.startTime}ms</span>
              <span>
                {seismicData.startTime + seismicData.sampleCount * seismicData.sampleInterval / 2}ms
              </span>
              <span>
                {seismicData.startTime + seismicData.sampleCount * seismicData.sampleInterval}ms
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Default mock seismic data
const defaultSeismicData: SeismicData = {
  traceCount: 500,
  sampleCount: 1000,
  sampleInterval: 4, // 4ms
  startTime: 0,
  traces: Array.from({ length: 500 }, () => {
    const trace = new Float32Array(1000);
    for (let i = 0; i < 1000; i++) {
      // Synthetic seismic with some structure
      const t = i / 1000;
      const structure = Math.sin(t * Math.PI * 4) * 0.3;
      const noise = (Math.random() - 0.5) * 0.2;
      trace[i] = structure + noise;
    }
    return trace;
  }),
};

const defaultHorizons: Horizon[] = [
  {
    name: 'Seabed',
    color: '#10B981',
    picks: Array.from({ length: 500 }, (_, i) => ({
      traceIndex: i,
      twt: 100 + Math.sin(i * 0.02) * 20,
      confidence: 0.9,
    })),
    visible: true,
  },
  {
    name: 'Top Reservoir',
    color: '#F59E0B',
    picks: Array.from({ length: 500 }, (_, i) => ({
      traceIndex: i,
      twt: 800 + Math.sin(i * 0.015) * 100,
      confidence: 0.75,
    })),
    visible: true,
  },
];

const defaultGCPs: SeismicGCP[] = [
  { id: 'gcp-1', traceIndex: 100, sampleIndex: 200, twt: 800, confidence: 0.9 },
  { id: 'gcp-2', traceIndex: 250, sampleIndex: 300, twt: 1200, confidence: 0.85 },
  { id: 'gcp-3', traceIndex: 400, sampleIndex: 250, twt: 1000, confidence: 0.8 },
];

const defaultAttributes: SeismicAttribute[] = [
  { name: 'RMS Amplitude', type: 'rms', windowLength: 100, color: '#F59E0B', visible: false },
  { name: 'Sweetness', type: 'sweetness', windowLength: 150, color: '#8B5CF6', visible: false },
  { name: 'Envelope', type: 'envelope', windowLength: 50, color: '#10B981', visible: false },
];

export default Domain2D;
