/**
 * Domain1D — Borehole Intelligence (250-499)
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * Well Context Desk & RATLAS implementation.
 * Surgical precision with JetBrains Mono typography. High-density data strips.
 *
 * Features:
 * - LAS log track visualization with SVG
 * - Material calibration overlays
 * - Probabilistic formation matching
 * - Depth/Time/Age triple-axis display
 */

import React, { useState, useRef, useEffect, useMemo } from 'react';
import {
  AlignLeft,
  Activity,
  Layers,
  Clock,
  Ruler,
  Target,
  ChevronDown,
  ChevronUp,
  Maximize2,
  Download,
  Database,
} from 'lucide-react';

/**
 * Well log curve definition
 */
interface LogCurve {
  name: string;
  unit: string;
  mnemonic: string;
  description: string;
  color: string;
  minValue: number;
  maxValue: number;
  data: Array<{ depth: number; value: number }>;
}

/**
 * Formation top definition
 */
interface FormationTop {
  depth: number;
  name: string;
  age?: number; // Ma
  confidence: number;
  lithology?: string;
  source: 'manual' | 'auto-picked' | 'database';
}

/**
 * Well metadata
 */
interface WellMetadata {
  wellId: string;
  wellName: string;
  kbElevation: number;
  totalDepth: number;
  datum: 'KB' | 'DF' | 'MSL' | 'RT';
  location: {
    latitude: number;
    longitude: number;
    crs: string;
  };
  spudDate?: string;
  rigName?: string;
}

/**
 * Log track configuration
 */
interface LogTrack {
  id: string;
  name: string;
  width: number;
  curves: LogCurve[];
  scale: 'linear' | 'logarithmic';
  minValue: number;
  maxValue: number;
}

/**
 * Depth reference system
 */
type DepthReference = 'tvd' | 'tvdss' | 'md' | 'twt' | 'age';

interface Domain1DProps {
  well?: WellMetadata;
  tracks?: LogTrack[];
  formations?: FormationTop[];
  onDepthSelect?: (depth: number, reference: DepthReference) => void;
  onFormationPick?: (depth: number) => void;
}

/**
 * SVG Log Track Component
 */
const LogTrackSVG: React.FC<{
  track: LogTrack;
  depthRange: { min: number; max: number };
  height: number;
  selectedDepth?: number;
  onDepthClick: (depth: number) => void;
}> = ({ track, depthRange, height, selectedDepth, onDepthClick }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [hoverDepth, setHoverDepth] = useState<number | null>(null);

  const padding = { top: 20, right: 10, bottom: 20, left: 40 };
  const innerWidth = track.width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;

  const yScale = (depth: number) => {
    const ratio = (depth - depthRange.min) / (depthRange.max - depthRange.min);
    return padding.top + ratio * innerHeight;
  };

  const xScale = (value: number) => {
    const ratio = (value - track.minValue) / (track.maxValue - track.minValue);
    return padding.left + ratio * innerWidth;
  };

  const handleClick = (e: React.MouseEvent<SVGSVGElement>) => {
    if (!svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const y = e.clientY - rect.top;
    const ratio = (y - padding.top) / innerHeight;
    const depth = depthRange.min + ratio * (depthRange.max - depthRange.min);
    onDepthClick(Math.max(depthRange.min, Math.min(depthRange.max, depth)));
  };

  // Generate grid lines
  const gridLines = useMemo(() => {
    const lines = [];
    const depthStep = Math.ceil((depthRange.max - depthRange.min) / 10 / 50) * 50;
    for (let d = depthRange.min; d <= depthRange.max; d += depthStep) {
      lines.push(
        <line
          key={`h-${d}`}
          x1={padding.left}
          y1={yScale(d)}
          x2={padding.left + innerWidth}
          y2={yScale(d)}
          stroke="rgba(90, 103, 115, 0.3)"
          strokeWidth={0.5}
          strokeDasharray="2,2"
        />
      );
    }
    return lines;
  }, [depthRange, innerWidth]);

  // Generate curve paths
  const curvePaths = useMemo(() => {
    return track.curves.map((curve) => {
      if (curve.data.length < 2) return null;

      let path = `M ${xScale(curve.data[0].value)} ${yScale(curve.data[0].depth)}`;
      for (let i = 1; i < curve.data.length; i++) {
        path += ` L ${xScale(curve.data[i].value)} ${yScale(curve.data[i].depth)}`;
      }
      return { curve, path };
    });
  }, [track.curves]);

  return (
    <div className="relative h-full border-r border-slate-700/50">
      {/* Track Header */}
      <div className="h-8 border-b border-slate-700 bg-slate-800/50 flex items-center px-2">
        <span className="text-[10px] font-mono font-bold text-slate-300 uppercase tracking-wider">
          {track.name}
        </span>
      </div>

      {/* SVG Canvas */}
      <svg
        ref={svgRef}
        width={track.width}
        height={height}
        className="cursor-crosshair"
        onClick={handleClick}
        onMouseMove={(e) => {
          const rect = svgRef.current?.getBoundingClientRect();
          if (rect) {
            const y = e.clientY - rect.top;
            const ratio = (y - padding.top) / innerHeight;
            const depth = depthRange.min + ratio * (depthRange.max - depthRange.min);
            setHoverDepth(Math.max(depthRange.min, Math.min(depthRange.max, depth)));
          }
        }}
        onMouseLeave={() => setHoverDepth(null)}
      >
        {/* Background */}
        <rect
          x={padding.left}
          y={padding.top}
          width={innerWidth}
          height={innerHeight}
          fill="rgba(17, 20, 24, 0.5)"
        />

        {/* Grid */}
        {gridLines}

        {/* Vertical grid */}
        {Array.from({ length: 5 }, (_, i) => {
          const x = padding.left + (i * innerWidth) / 4;
          return (
            <line
              key={`v-${i}`}
              x1={x}
              y1={padding.top}
              x2={x}
              y2={padding.top + innerHeight}
              stroke="rgba(90, 103, 115, 0.2)"
              strokeWidth={0.5}
            />
          );
        })}

        {/* Curve paths */}
        {curvePaths.map((item, idx) =>
          item ? (
            <path
              key={idx}
              d={item.path}
              fill="none"
              stroke={item.curve.color}
              strokeWidth={1.5}
            />
          ) : null
        )}

        {/* Selected depth line */}
        {selectedDepth !== undefined && (
          <line
            x1={padding.left}
            y1={yScale(selectedDepth)}
            x2={padding.left + innerWidth}
            y2={yScale(selectedDepth)}
            stroke="#F59E0B"
            strokeWidth={2}
          />
        )}

        {/* Hover depth line */}
        {hoverDepth !== null && (
          <line
            x1={padding.left}
            y1={yScale(hoverDepth)}
            x2={padding.left + innerWidth}
            y2={yScale(hoverDepth)}
            stroke="rgba(245, 158, 11, 0.5)"
            strokeWidth={1}
            strokeDasharray="4,2"
          />
        )}

        {/* Y-axis labels */}
        {Array.from({ length: 6 }, (_, i) => {
          const depth = depthRange.min + (i * (depthRange.max - depthRange.min)) / 5;
          return (
            <text
              key={`label-${i}`}
              x={padding.left - 5}
              y={yScale(depth)}
              fill="#8A96A3"
              fontSize="9"
              fontFamily="JetBrains Mono, monospace"
              textAnchor="end"
              dominantBaseline="middle"
            >
              {Math.round(depth)}
            </text>
          );
        })}
      </svg>

      {/* Curve legends */}
      <div className="absolute bottom-0 left-0 right-0 bg-slate-900/90 border-t border-slate-700 p-1">
        {track.curves.map((curve, idx) => (
          <div key={idx} className="flex items-center gap-1 text-[9px]">
            <div
              className="w-2 h-0.5 rounded"
              style={{ backgroundColor: curve.color }}
            />
            <span className="font-mono text-slate-400">{curve.mnemonic}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Formation Strip Component
 */
const FormationStrip: React.FC<{
  formations: FormationTop[];
  depthRange: { min: number; max: number };
  height: number;
  onFormationClick: (formation: FormationTop) => void;
}> = ({ formations, depthRange, height, onFormationClick }) => {
  const yScale = (depth: number) => {
    const ratio = (depth - depthRange.min) / (depthRange.max - depthRange.min);
    return ratio * height;
  };

  const colors: Record<string, string> = {
    sandstone: '#D4A574',
    shale: '#5A5A5A',
    limestone: '#A0C4D9',
    dolomite: '#C9B99A',
    chalk: '#F5F5DC',
    coal: '#2D2D2D',
    evaporite: '#FFB6C1',
  };

  return (
    <div className="relative h-full w-32 border-r border-slate-700/50">
      <div className="h-8 border-b border-slate-700 bg-slate-800/50 flex items-center px-2">
        <Layers className="w-3 h-3 text-cyan-500 mr-1" />
        <span className="text-[10px] font-mono font-bold text-slate-300 uppercase">Formations</span>
      </div>
      <div className="relative" style={{ height }}>
        {formations.map((formation, idx) => {
          const nextDepth = formations[idx + 1]?.depth ?? depthRange.max;
          const y = yScale(formation.depth);
          const h = yScale(nextDepth) - y;
          const color = colors[formation.lithology?.toLowerCase() || ''] || '#5A6773';

          return (
            <div
              key={formation.name}
              className="absolute left-0 right-0 cursor-pointer hover:opacity-80 transition-opacity"
              style={{
                top: y,
                height: h,
                backgroundColor: `${color}40`,
                borderLeft: `3px solid ${color}`,
              }}
              onClick={() => onFormationClick(formation)}
            >
              <div className="p-1">
                <div className="text-[9px] font-mono font-bold text-white truncate">
                  {formation.name}
                </div>
                <div className="text-[8px] font-mono text-slate-400">
                  {formation.depth.toFixed(1)}m
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

/**
 * Depth Axis Component
 */
const DepthAxis: React.FC<{
  range: { min: number; max: number };
  height: number;
  reference: DepthReference;
  onReferenceChange: (ref: DepthReference) => void;
}> = ({ range, height, reference, onReferenceChange }) => {
  const yScale = (depth: number) => {
    const ratio = (depth - range.min) / (range.max - range.min);
    return ratio * height;
  };

  const referenceLabels: Record<DepthReference, string> = {
    tvd: 'TVD',
    tvdss: 'TVDSS',
    md: 'MD',
    twt: 'TWT',
    age: 'Age',
  };

  return (
    <div className="relative h-full w-20 border-r border-slate-700/50 bg-slate-900/50">
      <div className="h-8 border-b border-slate-700 bg-slate-800/50 flex items-center justify-center">
        <select
          value={reference}
          onChange={(e) => onReferenceChange(e.target.value as DepthReference)}
          className="text-[10px] font-mono bg-transparent text-cyan-400 border-none outline-none cursor-pointer"
        >
          {Object.entries(referenceLabels).map(([key, label]) => (
            <option key={key} value={key} className="bg-slate-800">
              {label}
            </option>
          ))}
        </select>
      </div>
      <div className="relative" style={{ height }}>
        {Array.from({ length: 11 }, (_, i) => {
          const depth = range.min + (i * (range.max - range.min)) / 10;
          return (
            <div
              key={i}
              className="absolute left-0 right-0 flex items-center"
              style={{ top: yScale(depth) }}
            >
              <span className="text-[9px] font-mono text-slate-400 w-full text-right pr-2">
                {Math.round(depth)}
              </span>
              <div className="absolute right-0 w-1 h-px bg-slate-600" />
            </div>
          );
        })}
      </div>
    </div>
  );
};

/**
 * Well Info Panel
 */
const WellInfoPanel: React.FC<{ well: WellMetadata }> = ({ well }) => (
  <div className="geox-card mb-4">
    <div className="geox-card__header">
      <div className="flex items-center gap-2">
        <Target className="w-4 h-4 text-cyan-500" />
        <span className="geox-card__title">Well Information</span>
      </div>
    </div>
    <div className="geox-card__body">
      <div className="grid grid-cols-2 gap-3 text-xs">
        <div>
          <span className="text-slate-500 block text-[10px] uppercase">Well Name</span>
          <span className="font-mono font-bold text-white">{well.wellName}</span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px] uppercase">Well ID</span>
          <span className="font-mono text-slate-300">{well.wellId}</span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px] uppercase">KB Elevation</span>
          <span className="font-mono text-cyan-400">{well.kbElevation}m</span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px] uppercase">Total Depth</span>
          <span className="font-mono text-cyan-400">{well.totalDepth}m</span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px] uppercase">Location</span>
          <span className="font-mono text-slate-300">
            {well.location.latitude.toFixed(4)}, {well.location.longitude.toFixed(4)}
          </span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px] uppercase">Datum</span>
          <span className="font-mono text-slate-300">{well.datum}</span>
        </div>
      </div>
    </div>
  </div>
);

/**
 * Main Domain1D Component
 */
export const Domain1D: React.FC<Domain1DProps> = ({
  well = defaultWell,
  tracks = defaultTracks,
  formations = defaultFormations,
  onDepthSelect = () => {},
  onFormationPick = () => {},
}) => {
  const [selectedDepth, setSelectedDepth] = useState<number | undefined>(undefined);
  const [depthReference, setDepthReference] = useState<DepthReference>('tvd');
  const [depthRange, setDepthRange] = useState({ min: 0, max: 3000 });
  const logContainerRef = useRef<HTMLDivElement>(null);
  const [logHeight, setLogHeight] = useState(600);

  useEffect(() => {
    if (logContainerRef.current) {
      setLogHeight(logContainerRef.current.clientHeight - 32); // minus header
    }
  }, []);

  const handleDepthClick = (depth: number) => {
    setSelectedDepth(depth);
    onDepthSelect(depth, depthReference);
  };

  return (
    <div className="h-full flex flex-col bg-[#0A0C0E] geox-root">
      {/* Domain Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-900/50">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
          <span className="text-sm font-bold text-white tracking-tight">Domain1D</span>
          <span className="text-xs font-mono text-cyan-500">250-499</span>
          <span className="geox-domain-indicator geox-domain-indicator--1d">Borehole</span>
        </div>
        <div className="flex items-center gap-2">
          <button className="geox-btn geox-btn--ghost p-1.5">
            <Download className="w-4 h-4" />
          </button>
          <button className="geox-btn geox-btn--ghost p-1.5">
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <div className="w-64 border-r border-slate-800 bg-slate-900/30 overflow-auto geox-scroll p-4">
          <WellInfoPanel well={well} />

          {/* Selected Depth Info */}
          {selectedDepth !== undefined && (
            <div className="geox-card border-cyan-500/30">
              <div className="geox-card__header bg-cyan-950/20">
                <span className="geox-card__title text-cyan-400">Selected Depth</span>
              </div>
              <div className="geox-card__body">
                <div className="text-2xl font-mono font-black text-white mb-2">
                  {selectedDepth.toFixed(2)}
                  <span className="text-sm text-slate-500 ml-1">m</span>
                </div>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-500">TVDSS</span>
                    <span className="font-mono text-cyan-400">
                      {(selectedDepth - well.kbElevation).toFixed(2)}m
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">TWT</span>
                    <span className="font-mono text-violet-400">~{(selectedDepth * 2).toFixed(0)}ms</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Log Display Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Toolbar */}
          <div className="h-10 border-b border-slate-800 bg-slate-900/50 flex items-center px-4 gap-4">
            <div className="flex items-center gap-2 text-xs">
              <Ruler className="w-3 h-3 text-slate-500" />
              <span className="text-slate-500">Range:</span>
              <input
                type="number"
                value={depthRange.min}
                onChange={(e) => setDepthRange((r) => ({ ...r, min: Number(e.target.value) }))}
                className="geox-input geox-input--mono w-20 text-xs py-1"
              />
              <span className="text-slate-500">-</span>
              <input
                type="number"
                value={depthRange.max}
                onChange={(e) => setDepthRange((r) => ({ ...r, max: Number(e.target.value) }))}
                className="geox-input geox-input--mono w-20 text-xs py-1"
              />
            </div>
            <div className="flex-1" />
            <div className="flex items-center gap-2">
              <button
                onClick={() => setDepthRange((r) => ({ min: r.min - 100, max: r.max - 100 }))}
                className="geox-btn geox-btn--ghost p-1"
              >
                <ChevronUp className="w-4 h-4" />
              </button>
              <button
                onClick={() => setDepthRange((r) => ({ min: r.min + 100, max: r.max + 100 }))}
                className="geox-btn geox-btn--ghost p-1"
              >
                <ChevronDown className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Log Tracks */}
          <div ref={logContainerRef} className="flex-1 flex overflow-x-auto overflow-y-hidden geox-scroll">
            <DepthAxis
              range={depthRange}
              height={logHeight}
              reference={depthReference}
              onReferenceChange={setDepthReference}
            />
            <FormationStrip
              formations={formations}
              depthRange={depthRange}
              height={logHeight}
              onFormationClick={(f) => onFormationPick(f.depth)}
            />
            {tracks.map((track) => (
              <LogTrackSVG
                key={track.id}
                track={track}
                depthRange={depthRange}
                height={logHeight}
                selectedDepth={selectedDepth}
                onDepthClick={handleDepthClick}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Default data
const defaultWell: WellMetadata = {
  wellId: 'W-001',
  wellName: 'Malay Basin Pilot-1',
  kbElevation: 25.5,
  totalDepth: 3500,
  datum: 'KB',
  location: { latitude: 5.4321, longitude: 104.5678, crs: 'EPSG:4326' },
  spudDate: '2023-01-15',
  rigName: 'Ocean Rig',
};

const defaultTracks: LogTrack[] = [
  {
    id: 'gr',
    name: 'Gamma Ray',
    width: 120,
    scale: 'linear',
    minValue: 0,
    maxValue: 200,
    curves: [
      {
        name: 'Gamma Ray',
        unit: 'API',
        mnemonic: 'GR',
        description: 'Natural Gamma Ray',
        color: '#10B981',
        minValue: 0,
        maxValue: 200,
        data: Array.from({ length: 100 }, (_, i) => ({
          depth: i * 30,
          value: 50 + Math.random() * 100 + Math.sin(i * 0.1) * 30,
        })),
      },
    ],
  },
  {
    id: 'res',
    name: 'Resistivity',
    width: 120,
    scale: 'logarithmic',
    minValue: 0.2,
    maxValue: 200,
    curves: [
      {
        name: 'Deep Resistivity',
        unit: 'ohm.m',
        mnemonic: 'RT',
        description: 'True Resistivity',
        color: '#F59E0B',
        minValue: 0.2,
        maxValue: 200,
        data: Array.from({ length: 100 }, (_, i) => ({
          depth: i * 30,
          value: Math.exp(2 + Math.random() * 2),
        })),
      },
    ],
  },
  {
    id: 'dens',
    name: 'Density',
    width: 120,
    scale: 'linear',
    minValue: 1.8,
    maxValue: 2.8,
    curves: [
      {
        name: 'Bulk Density',
        unit: 'g/cc',
        mnemonic: 'RHOB',
        description: 'Formation Bulk Density',
        color: '#8B5CF6',
        minValue: 1.8,
        maxValue: 2.8,
        data: Array.from({ length: 100 }, (_, i) => ({
          depth: i * 30,
          value: 2.2 + Math.random() * 0.4,
        })),
      },
    ],
  },
];

const defaultFormations: FormationTop[] = [
  { depth: 0, name: 'Seabed', lithology: 'water', confidence: 1.0, source: 'database' },
  { depth: 50, name: 'Miri Fm', lithology: 'shale', confidence: 0.9, source: 'manual' },
  { depth: 450, name: 'Belait Fm', lithology: 'sandstone', confidence: 0.85, source: 'auto-picked' },
  { depth: 1200, name: 'Setap Fm', lithology: 'shale', confidence: 0.9, source: 'manual' },
  { depth: 1800, name: 'Temburong Fm', lithology: 'limestone', confidence: 0.8, source: 'auto-picked' },
  { depth: 2500, name: 'Meligan Fm', lithology: 'sandstone', confidence: 0.75, source: 'auto-picked' },
  { depth: 3200, name: 'Basement', lithology: 'granite', confidence: 0.95, source: 'manual' },
];

export default Domain1D;
