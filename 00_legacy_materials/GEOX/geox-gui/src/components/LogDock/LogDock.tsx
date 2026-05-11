/**
 * LogDock — Well Log Viewer with Petrophysical Interpretation
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * Canvas-based multi-track well log visualization.
 * Renders GR, resistivity, density/neutron, and computed curves (VSH, PHIe, Sw).
 *
 * Physics models rendered:
 * - GR → Vsh (Clavier-Fertl 1974)
 * - NPHI + RHOB → PHIe (neutron-density crossover)
 * - ILD + PHIe + Rw → Sw (Archie)
 * - DT → PHI (Wyllie time-average)
 */

import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import * as d3 from 'd3';
import {
  ZoomIn, ZoomOut, MoveVertical, Eye, EyeOff,
  Activity, AlignLeft, ChevronDown, ChevronUp,
  FlaskConical, Gauge, Droplets, Layers
} from 'lucide-react';
import { demoWellData } from './data/demoWellData';
import type { LogCurve, WellLogData, TrackConfig } from './types';

// ─────────────────────────────────────────────────────────────────────────────
// Track Renderer — Canvas-based log track
// ─────────────────────────────────────────────────────────────────────────────

interface TrackRendererProps {
  track: TrackConfig;
  data: WellLogData;
  depthRange: [number, number];
  width: number;
  height: number;
  cursorDepth: number | null;
  onCursorMove: (depth: number | null) => void;
}

const TrackRenderer: React.FC<TrackRendererProps> = ({
  track, data, depthRange, width, height, cursorDepth, onCursorMove
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Margin for track header/footer
  const margin = { top: 30, right: 10, bottom: 20, left: 40 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Handle high-DPI displays
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.scale(dpr, dpr);

    // Clear
    ctx.clearRect(0, 0, width, height);

    // Background
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, width, height);

    // Track border
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 1;
    ctx.strokeRect(margin.left, margin.top, plotWidth, plotHeight);

    // Scales
    const yScale = d3.scaleLinear()
      .domain(depthRange)
      .range([margin.top, margin.top + plotHeight]);

    // Draw depth grid (every 50m)
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 0.5;
    const depthStep = 50;
    for (let d = Math.ceil(depthRange[0] / depthStep) * depthStep; d <= depthRange[1]; d += depthStep) {
      const y = yScale(d);
      ctx.beginPath();
      ctx.moveTo(margin.left, y);
      ctx.lineTo(margin.left + plotWidth, y);
      ctx.stroke();

      // Depth label on left
      ctx.fillStyle = '#64748b';
      ctx.font = '10px monospace';
      ctx.textAlign = 'right';
      ctx.fillText(d.toString(), margin.left - 4, y + 3);
    }

    // Draw each curve in this track
    track.curves.forEach((curveName) => {
      const curve = data.curves.find((c) => c.name === curveName);
      if (!curve || !curve.visible) return;

      const minVal = curve.min ?? 0;
      const maxVal = curve.max ?? 100;

      let xScale: d3.ScaleLinear<number, number>;
      if (curve.scale === 'log') {
        const logMin = Math.max(minVal, 0.01);
        const logMax = Math.max(maxVal, logMin * 10);
        xScale = d3.scaleLog()
          .domain([logMin, logMax])
          .range([margin.left + 5, margin.left + plotWidth - 5]);
      } else {
        xScale = d3.scaleLinear()
          .domain([minVal, maxVal])
          .range([margin.left + 5, margin.left + plotWidth - 5]);
      }

      // Draw fill (if specified)
      if (curve.fill) {
        ctx.beginPath();
        const baselineX = xScale(curve.fill.baseline);
        let first = true;

        for (let i = 0; i < curve.depth.length; i++) {
          const d = curve.depth[i];
          if (d < depthRange[0] || d > depthRange[1]) continue;
          const val = curve.values[i];
          if (val == null) continue;
          const y = yScale(d);
          const x = xScale(val);

          if (first) {
            ctx.moveTo(baselineX, y);
            first = false;
          }
          ctx.lineTo(x, y);
        }

        for (let i = curve.depth.length - 1; i >= 0; i--) {
          const d = curve.depth[i];
          if (d < depthRange[0] || d > depthRange[1]) continue;
          const y = yScale(d);
          ctx.lineTo(baselineX, y);
        }

        ctx.closePath();
        ctx.fillStyle = curve.fill.color;
        ctx.globalAlpha = curve.fill.opacity ?? 0.2;
        ctx.fill();
        ctx.globalAlpha = 1;
      }

      // Draw line
      ctx.beginPath();
      ctx.strokeStyle = curve.color;
      ctx.lineWidth = curve.lineWidth ?? 1.5;
      let started = false;

      for (let i = 0; i < curve.depth.length; i++) {
        const d = curve.depth[i];
        if (d < depthRange[0] || d > depthRange[1]) continue;

        const y = yScale(d);
        const val = curve.values[i];
        if (val == null || isNaN(val)) {
          started = false;
          continue;
        }

        const x = xScale(val);
        if (!started) {
          ctx.moveTo(x, y);
          started = true;
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();

      // Draw min/max labels
      ctx.fillStyle = curve.color;
      ctx.font = 'bold 9px sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(`${minVal}`, margin.left + 5, margin.top - 8);
      ctx.textAlign = 'right';
      ctx.fillText(`${maxVal}`, margin.left + plotWidth - 5, margin.top - 8);
    });

    // Track title
    ctx.fillStyle = '#e2e8f0';
    ctx.font = 'bold 11px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(track.title, margin.left + plotWidth / 2, 18);

    // Draw cursor line
    if (cursorDepth != null && cursorDepth >= depthRange[0] && cursorDepth <= depthRange[1]) {
      const y = yScale(cursorDepth);
      ctx.strokeStyle = '#fbbf24';
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(margin.left, y);
      ctx.lineTo(margin.left + plotWidth, y);
      ctx.stroke();
      ctx.setLineDash([]);

      // Cursor depth label
      ctx.fillStyle = '#fbbf24';
      ctx.font = 'bold 10px monospace';
      ctx.textAlign = 'left';
      ctx.fillText(`${cursorDepth.toFixed(1)}m`, margin.left + plotWidth + 4, y + 3);
    }
  }, [track, data, depthRange, width, height, cursorDepth, margin.left, margin.top, plotWidth, plotHeight]);

  useEffect(() => {
    draw();
  }, [draw]);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const y = e.clientY - rect.top;
    const yScale = d3.scaleLinear()
      .domain([margin.top, margin.top + plotHeight])
      .range(depthRange);
    const depth = yScale(y) as number;
    if (depth >= depthRange[0] && depth <= depthRange[1]) {
      onCursorMove(depth);
    }
  };

  const handleMouseLeave = () => {
    onCursorMove(null);
  };

  return (
    <div
      ref={containerRef}
      className="relative flex-shrink-0"
      style={{ width: `${track.width}px`, height: `${height}px` }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <canvas
        ref={canvasRef}
        className="cursor-crosshair"
        style={{ width: `${width}px`, height: `${height}px` }}
      />
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// Depth Track (shared depth axis)
// ─────────────────────────────────────────────────────────────────────────────

const DepthTrack: React.FC<{
  depthRange: [number, number];
  height: number;
  cursorDepth: number | null;
  onCursorMove: (depth: number | null) => void;
}> = ({ depthRange, height, cursorDepth, onCursorMove }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const width = 60;
  const margin = { top: 30, bottom: 20 };
  const plotHeight = height - margin.top - margin.bottom;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.scale(dpr, dpr);

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, width, height);

    const yScale = d3.scaleLinear()
      .domain(depthRange)
      .range([margin.top, margin.top + plotHeight]);

    // Border
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 1;
    ctx.strokeRect(0, margin.top, width, plotHeight);

    // Depth ticks (every 10m, label every 50m)
    const minorStep = 10;
    const majorStep = 50;

    for (let d = Math.ceil(depthRange[0] / minorStep) * minorStep; d <= depthRange[1]; d += minorStep) {
      const y = yScale(d);
      const isMajor = d % majorStep === 0;

      ctx.strokeStyle = isMajor ? '#475569' : '#1e293b';
      ctx.lineWidth = isMajor ? 1 : 0.5;
      ctx.beginPath();
      ctx.moveTo(isMajor ? 0 : 20, y);
      ctx.lineTo(width, y);
      ctx.stroke();

      if (isMajor) {
        ctx.fillStyle = '#94a3b8';
        ctx.font = 'bold 10px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(d.toString(), 4, y + 3);
      }
    }

    // Title
    ctx.fillStyle = '#e2e8f0';
    ctx.font = 'bold 11px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('DEPTH', width / 2, 18);
    ctx.font = '9px sans-serif';
    ctx.fillText('(m)', width / 2, 28);

    // Cursor
    if (cursorDepth != null) {
      const y = yScale(cursorDepth);
      ctx.strokeStyle = '#fbbf24';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
  }, [depthRange, height, cursorDepth, margin.top, plotHeight]);

  const handleMouseMove = (e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const y = e.clientY - rect.top;
    const yScale = d3.scaleLinear()
      .domain([margin.top, margin.top + plotHeight])
      .range(depthRange);
    const depth = yScale(y) as number;
    if (depth >= depthRange[0] && depth <= depthRange[1]) {
      onCursorMove(depth);
    }
  };

  return (
    <canvas
      ref={canvasRef}
      className="flex-shrink-0 cursor-crosshair"
      style={{ width: `${width}px`, height: `${height}px` }}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => onCursorMove(null)}
    />
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// Curve Legend Panel
// ─────────────────────────────────────────────────────────────────────────────

const CurveLegend: React.FC<{
  curves: LogCurve[];
  onToggle: (name: string) => void;
}> = ({ curves, onToggle }) => (
  <div className="p-3 space-y-2">
    <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Curves</h4>
    {curves.map((curve) => (
      <button
        key={curve.name}
        onClick={() => onToggle(curve.name)}
        className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-all ${
          curve.visible ? 'bg-slate-800 text-slate-200' : 'bg-transparent text-slate-600'
        }`}
      >
        {curve.visible ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
        <div
          className="w-3 h-0.5 rounded"
          style={{ backgroundColor: curve.visible ? curve.color : '#475569' }}
        />
        <span className="font-mono">{curve.name}</span>
        <span className="text-slate-600 ml-auto">{curve.unit}</span>
      </button>
    ))}
  </div>
);

// ─────────────────────────────────────────────────────────────────────────────
// Petrophysics Summary Panel
// ─────────────────────────────────────────────────────────────────────────────

const PetrophysicsSummary: React.FC<{
  data: WellLogData;
  cursorDepth: number | null;
}> = ({ data, cursorDepth }) => {
  const interp = useMemo(() => {
    if (cursorDepth == null) return null;

    const vshCurve = data.curves.find((c) => c.name === 'VSH');
    const phieCurve = data.curves.find((c) => c.name === 'PHIE');
    const swCurve = data.curves.find((c) => c.name === 'SW');

    const vsh = vshCurve ? interpolateCurve(vshCurve, cursorDepth) : null;
    const phie = phieCurve ? interpolateCurve(phieCurve, cursorDepth) : null;
    const sw = swCurve ? interpolateCurve(swCurve, cursorDepth) : null;

    // Zone classification
    let zone = 'Unknown';
    let zoneColor = 'text-slate-400';
    if (vsh != null && phie != null) {
      if (vsh < 0.3 && phie > 0.15) {
        zone = sw != null && sw < 0.5 ? 'Pay Zone' : 'Water Zone';
        zoneColor = sw != null && sw < 0.5 ? 'text-green-400' : 'text-blue-400';
      } else if (vsh > 0.5) {
        zone = 'Shale';
        zoneColor = 'text-amber-400';
      } else {
        zone = 'Transition';
        zoneColor = 'text-slate-300';
      }
    }

    return { vsh, phie, sw, zone, zoneColor };
  }, [data, cursorDepth]);

  if (!interp) {
    return (
      <div className="p-3">
        <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Petrophysics</h4>
        <p className="text-xs text-slate-600 italic">Hover over the log to see interval properties</p>
      </div>
    );
  }

  return (
    <div className="p-3">
      <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Petrophysics @ {cursorDepth?.toFixed(1)}m</h4>

      <div className={`text-sm font-bold mb-3 ${interp.zoneColor}`}>
        <Layers className="w-3 h-3 inline mr-1" />
        {interp.zone}
      </div>

      <div className="space-y-2">
        <MetricRow label="Vsh (Clay Volume)" value={interp.vsh} unit="v/v" color="#f59e0b" icon={FlaskConical} />
        <MetricRow label="PHIe (Eff. Porosity)" value={interp.phie} unit="v/v" color="#3b82f6" icon={Gauge} />
        <MetricRow label="Sw (Water Saturation)" value={interp.sw} unit="v/v" color="#06b6d4" icon={Droplets} />
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800">
        <div className="text-[10px] text-slate-600 space-y-1">
          <p><span className="text-slate-500">GR→Vsh:</span> Clavier-Fertl 1974</p>
          <p><span className="text-slate-500">NPHI+RHOB→PHIe:</span> Neutron-Density crossover</p>
          <p><span className="text-slate-500">ILD→Sw:</span> Archie equation (a=1, m=2, n=2)</p>
        </div>
      </div>
    </div>
  );
};

const MetricRow: React.FC<{
  label: string;
  value: number | null;
  unit: string;
  color: string;
  icon: React.ElementType;
}> = ({ label, value, unit, color, icon: Icon }) => (
  <div className="flex items-center justify-between text-xs">
    <div className="flex items-center gap-1.5 text-slate-400">
      <Icon className="w-3 h-3" style={{ color }} />
      <span>{label}</span>
    </div>
    <div className="font-mono font-bold" style={{ color }}>
      {value != null ? value.toFixed(3) : '--'} <span className="text-slate-600 font-normal">{unit}</span>
    </div>
  </div>
);

function interpolateCurve(curve: LogCurve, depth: number): number | null {
  const idx = curve.depth.findIndex((d) => d >= depth);
  if (idx === 0) return curve.values[0];
  if (idx === -1) return curve.values[curve.values.length - 1];
  if (idx < 0) return null;

  const d0 = curve.depth[idx - 1];
  const d1 = curve.depth[idx];
  const v0 = curve.values[idx - 1];
  const v1 = curve.values[idx];

  if (v0 == null || v1 == null) return null;

  const t = (depth - d0) / (d1 - d0);
  return v0 + t * (v1 - v0);
}

// ─────────────────────────────────────────────────────────────────────────────
// Main LogDock Component
// ─────────────────────────────────────────────────────────────────────────────

const DEFAULT_TRACKS: TrackConfig[] = [
  {
    id: 'track-gr',
    title: 'GR / VSH',
    width: 140,
    curves: ['GR', 'VSH'],
  },
  {
    id: 'track-res',
    title: 'Resistivity',
    width: 140,
    curves: ['ILD', 'LLD'],
  },
  {
    id: 'track-nd',
    title: 'Density / Neutron',
    width: 160,
    curves: ['RHOB', 'NPHI', 'DT'],
  },
  {
    id: 'track-computed',
    title: 'Petrophysics',
    width: 160,
    curves: ['PHIE', 'SW'],
  },
];

export const LogDock: React.FC = () => {
  const [data, setData] = useState<WellLogData>(() => demoWellData());
  const [depthRange, setDepthRange] = useState<[number, number]>(() => {
    const depths = data.curves.find((c) => c.name === 'DEPT')?.depth || [1000, 2000];
    return [depths[0], depths[depths.length - 1]];
  });
  const [cursorDepth, setCursorDepth] = useState<number | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [tracks] = useState<TrackConfig[]>(DEFAULT_TRACKS);

  const trackHeight = 600;

  const toggleCurve = useCallback((name: string) => {
    setData((prev) => ({
      ...prev,
      curves: prev.curves.map((c) =>
        c.name === name ? { ...c, visible: !c.visible } : c
      ),
    }));
  }, []);

  const zoomIn = () => {
    const mid = (depthRange[0] + depthRange[1]) / 2;
    const half = (depthRange[1] - depthRange[0]) / 2;
    setDepthRange([mid - half * 0.7, mid + half * 0.7]);
  };

  const zoomOut = () => {
    const mid = (depthRange[0] + depthRange[1]) / 2;
    const half = (depthRange[1] - depthRange[0]) / 2;
    const maxDepth = data.depthRange[1];
    const minDepth = data.depthRange[0];
    setDepthRange([
      Math.max(minDepth, mid - half * 1.4),
      Math.min(maxDepth, mid + half * 1.4),
    ]);
  };

  const resetZoom = () => {
    setDepthRange([data.depthRange[0], data.depthRange[1]]);
  };

  const totalTrackWidth = 60 + tracks.reduce((sum, t) => sum + t.width, 0);

  return (
    <div className="h-full flex flex-col bg-slate-950">
      {/* Toolbar */}
      <div className="h-10 bg-slate-900 border-b border-slate-800 flex items-center px-3 gap-2 flex-shrink-0">
        <AlignLeft className="w-4 h-4 text-blue-400" />
        <span className="text-sm font-bold text-slate-200">LogDock</span>
        <span className="text-xs text-slate-600 font-mono ml-1">{data.wellName}</span>

        <div className="w-px h-5 bg-slate-700 mx-2" />

        <button onClick={zoomIn} className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white" title="Zoom In">
          <ZoomIn className="w-4 h-4" />
        </button>
        <button onClick={zoomOut} className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white" title="Zoom Out">
          <ZoomOut className="w-4 h-4" />
        </button>
        <button onClick={resetZoom} className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white" title="Reset Zoom">
          <MoveVertical className="w-4 h-4" />
        </button>

        <div className="w-px h-5 bg-slate-700 mx-2" />

        <span className="text-xs text-slate-500 font-mono">
          {depthRange[0].toFixed(0)}m – {depthRange[1].toFixed(0)}m
        </span>

        {cursorDepth != null && (
          <>
            <div className="w-px h-5 bg-slate-700 mx-2" />
            <Activity className="w-3 h-3 text-amber-400" />
            <span className="text-xs font-mono text-amber-400">
              {cursorDepth.toFixed(1)}m
            </span>
          </>
        )}

        <div className="flex-1" />

        <button
          onClick={() => setShowSidebar(!showSidebar)}
          className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white"
          title="Toggle Sidebar"
        >
          {showSidebar ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Track Canvas Area */}
        <div className="flex-1 overflow-x-auto overflow-y-hidden">
          <div className="flex" style={{ minWidth: `${totalTrackWidth}px` }}>
            {/* Depth Track */}
            <DepthTrack
              depthRange={depthRange}
              height={trackHeight}
              cursorDepth={cursorDepth}
              onCursorMove={setCursorDepth}
            />

            {/* Data Tracks */}
            {tracks.map((track) => (
              <TrackRenderer
                key={track.id}
                track={track}
                data={data}
                depthRange={depthRange}
                width={track.width}
                height={trackHeight}
                cursorDepth={cursorDepth}
                onCursorMove={setCursorDepth}
              />
            ))}
          </div>
        </div>

        {/* Sidebar */}
        {showSidebar && (
          <div className="w-56 bg-slate-900 border-l border-slate-800 overflow-y-auto flex-shrink-0">
            <PetrophysicsSummary data={data} cursorDepth={cursorDepth} />
            <div className="border-t border-slate-800" />
            <CurveLegend curves={data.curves} onToggle={toggleCurve} />
          </div>
        )}
      </div>

      {/* Bottom Info Bar */}
      <div className="h-8 bg-slate-950 border-t border-slate-800 flex items-center px-3 gap-4 text-[10px] text-slate-500 font-mono flex-shrink-0">
        <span>Curves: {data.curves.filter((c) => c.visible).length}/{data.curves.length}</span>
        <span>Depth Step: ~0.5m</span>
        <span>Rw: {data.parameters.rw} Ω·m</span>
        <span>Bit Size: {data.parameters.bitSize}\"</span>
        <div className="flex-1" />
        <span className="text-amber-500/70">DITEMPA BUKAN DIBERI</span>
      </div>
    </div>
  );
};

export default LogDock;
