import React, { useState } from 'react';
import { Target, CheckCircle2, AlertCircle, Zap, ScanFace, Ruler, BarChart3, AlertTriangle } from 'lucide-react';
import { useMcpTool } from '../hooks/useMcpTool';

const Badge: React.FC<{ children: React.ReactNode; color?: string }> = ({ children, color = "amber" }) => {
  const colors: Record<string, string> = {
    amber: "border-amber-500/30 text-amber-500 bg-amber-500/10",
    emerald: "border-emerald-500/30 text-emerald-500 bg-emerald-500/10",
    cyan: "border-cyan-500/30 text-cyan-400 bg-cyan-500/10",
    crimson: "border-red-500/30 text-red-500 bg-red-500/10",
    purple: "border-purple-500/30 text-purple-400 bg-purple-500/10",
  };
  return (
    <span className={`px-1.5 py-0.5 text-[10px] font-mono border rounded uppercase tracking-wider ${colors[color]}`}>
      {children}
    </span>
  );
};

export const Domain1D: React.FC = () => {
  const interpretTool = useMcpTool<any, string>('bridge.interpret_causal_scene');
  const [isCalibrating, setIsCalibrating] = useState(false);
  const [calibrated, setCalibrated] = useState(false);

  const depthPoints = 120;
  const trackHeight = 600;
  const trackWidth = 150;

  const syntheticLogs = Array.from({ length: depthPoints }, (_, i) => {
    let gr, resDeep, resShal, den, neu;
    const noise = () => (Math.random() - 0.5) * 0.1;

    if (i >= 40 && i < 60) {
      gr = 30 + noise() * 50;
      resDeep = 200 + noise() * 500;
      resShal = 180 + noise() * 400;
      den = 2.05 + noise() * 0.1;
      neu = 0.12 + noise() * 0.05;
    } else if (i >= 60 && i < 80) {
      gr = 35 + noise() * 50;
      resDeep = 2 + noise() * 5;
      resShal = 1.5 + noise() * 3;
      den = 2.25 + noise() * 0.1;
      neu = 0.28 + noise() * 0.05;
    } else {
      gr = 110 + noise() * 100;
      resDeep = 3 + noise() * 8;
      resShal = 3 + noise() * 8;
      den = 2.55 + noise() * 0.1;
      neu = 0.35 + noise() * 0.05;
    }
    return { gr, resDeep, resShal, den, neu, depth: i };
  });

  const getPoints = (dataKey: keyof typeof syntheticLogs[0], minX: number, maxX: number, isLog = false) => {
    return syntheticLogs.map((p, i) => {
      const y = (i / (depthPoints - 1)) * trackHeight;
      const val = p[dataKey] as number;
      let x = isLog
        ? ((Math.log10(val) - Math.log10(minX)) / (Math.log10(maxX) - Math.log10(minX))) * trackWidth
        : ((val - minX) / (maxX - minX)) * trackWidth;
      x = Math.max(0, Math.min(trackWidth, x));
      return `${x},${y}`;
    }).join(' ');
  };

  const crossoverPaths = (() => {
    const polygonPoints: { xNeu: number; xDen: number; y: number }[] = [];
    let isCrossover = false;
    const paths: string[] = [];
    const denMin = 1.95, denMax = 2.95;
    const neuMin = 0.45, neuMax = -0.15;

    syntheticLogs.forEach((p, i) => {
      const y = (i / (depthPoints - 1)) * trackHeight;
      const denX = ((p.den - denMin) / (denMax - denMin)) * trackWidth;
      const neuX = ((p.neu - neuMin) / (neuMax - neuMin)) * trackWidth;

      if (neuX < denX) {
        if (!isCrossover) { isCrossover = true; polygonPoints.length = 0; }
        polygonPoints.push({ xNeu: neuX, xDen: denX, y });
      } else {
        if (isCrossover) {
          isCrossover = false;
          const r = [...polygonPoints].reverse().map(pt => `${pt.xDen},${pt.y}`);
          const l = polygonPoints.map(pt => `${pt.xNeu},${pt.y}`);
          paths.push([...l, ...r].join(' '));
        }
      }
    });
    return paths;
  })();

  const handleAutoInterpret = async () => {
    await interpretTool.call({ domain: 'dim1', user_query: 'Phase tie analysis' });
  };

  const simulateCalibration = () => {
    setIsCalibrating(true);
    setTimeout(() => { setIsCalibrating(false); setCalibrated(true); }, 1500);
  };

  const isBlocked = interpretTool.data?.includes('HOLD');

  return (
    <div className="flex flex-col h-full gap-4 p-4">
      <div className="flex justify-between items-end mb-2 border-b border-gray-800 pb-2">
        <div>
          <h2 className="text-xl font-bold tracking-widest flex items-center gap-2">
            <Target className="w-5 h-5 text-emerald-500" /> THE 1D INTERFACE [250-499]
          </h2>
          <p className="text-xs text-gray-500 font-mono">SOVEREIGN BOREHOLE INTEL</p>
        </div>
        <div className="flex gap-2">
          {calibrated ? <Badge color="cyan">TRUE SCALE LOCKED</Badge> : <Badge color="crimson">UNSCALED</Badge>}
          <Badge color="purple">MCP: {interpretTool.status === 'loading' ? 'SYNCING...' : 'ONLINE'}</Badge>
          <Badge color="emerald">F2: TRUTH</Badge>
        </div>
      </div>

      <div className="flex-1 flex gap-4 overflow-hidden relative">
        <div className={`flex-1 glass-panel p-2 flex gap-1 relative h-full ${isCalibrating ? 'gcp-active' : ''}`}>
          <div className="scanline" />

          <div className="flex-1 border-r border-gray-800 flex flex-col">
             <div className="h-12 border-b border-gray-800 flex flex-col justify-between p-1 bg-black/40">
                <div className="text-[10px] font-mono text-center text-green-500 font-bold">GR (API)</div>
                <div className="flex justify-between text-[9px] font-mono text-gray-500"><span>0</span><span>150</span></div>
             </div>
             <div className="flex-1 relative overflow-hidden bg-[#050505]">
                <svg width="100%" height="100%" preserveAspectRatio="none" viewBox={`0 0 ${trackWidth} ${trackHeight}`}>
                   <polyline points={getPoints('gr', 0, 150)} fill="none" stroke="#22c55e" strokeWidth="1.5" />
                </svg>
             </div>
          </div>

          <div className="w-16 border-r border-gray-800 flex flex-col bg-gray-900/80 z-10 shadow-lg">
             <div className="h-12 border-b border-gray-800 flex flex-col justify-center items-center bg-black/40 gap-1">
                <div className="flex flex-col text-[9px] font-mono text-gray-400 items-center"><Ruler size={12} className="text-cyan-500 mb-1"/> MD(m)</div>
             </div>
             <div className="flex-1 flex flex-col justify-between py-2 text-[10px] font-mono text-center text-gray-500 relative">
                {isCalibrating && <div className="absolute inset-0 bg-cyan-500/10 radar-sweep" />}
                {[...Array(13)].map((_, i) => <div key={i} className="px-1"><span className={calibrated ? "text-cyan-500 font-bold" : "text-gray-600"}>{calibrated ? 1500 + i * 10 : '----'}</span></div>)}
             </div>
          </div>

          <div className="flex-1 border-r border-gray-800 flex flex-col">
             <div className="h-12 border-b border-gray-800 flex flex-col justify-between p-1 bg-black/40">
                <div className="text-[10px] font-mono text-center text-red-500 font-bold">RES (Ωm)</div>
                <div className="flex justify-between text-[9px] font-mono text-gray-500"><span>0.2</span><span>2000</span></div>
             </div>
             <div className="flex-1 relative overflow-hidden bg-[#050505]">
                <svg width="100%" height="100%" preserveAspectRatio="none" viewBox={`0 0 ${trackWidth} ${trackHeight}`}>
                   <polyline points={getPoints('resDeep', 0.2, 2000, true)} fill="none" stroke="#ef4444" strokeWidth="2" />
                </svg>
             </div>
          </div>

          <div className="flex-1 flex flex-col">
             <div className="h-12 border-b border-gray-800 flex flex-col justify-between p-1 bg-black/40">
                <div className="flex justify-between w-full px-1"><span className="text-[10px] font-mono text-blue-400 font-bold">NPHI</span><span className="text-[10px] font-mono text-amber-500 font-bold">RHOB</span></div>
             </div>
             <div className="flex-1 relative overflow-hidden bg-[#050505]">
                <svg width="100%" height="100%" preserveAspectRatio="none" viewBox={`0 0 ${trackWidth} ${trackHeight}`}>
                   {crossoverPaths.map((d, i) => <polygon key={i} points={d} fill="rgba(245, 158, 11, 0.3)" />)}
                   <polyline points={getPoints('den', 1.95, 2.95)} fill="none" stroke="#f59e0b" strokeWidth="2" />
                   <polyline points={getPoints('neu', 0.45, -0.15)} fill="none" stroke="#60a5fa" strokeWidth="1.5" strokeDasharray="4,4" />
                </svg>
             </div>
          </div>
        </div>

        <div className="w-64 glass-panel p-4 flex flex-col gap-4">
          <div className="text-xs font-mono text-gray-500 border-b border-gray-800 pb-2 flex justify-between items-center">
            SCALE INTELLIGENCE <ScanFace className="w-4 h-4 text-cyan-500" />
          </div>
          <button
            onClick={simulateCalibration}
            disabled={isCalibrating || calibrated}
            className={`w-full py-2 border text-[10px] font-mono uppercase flex justify-center items-center gap-2 ${
              calibrated ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400' : 'bg-gray-800/50 border-gray-700 text-gray-400'
            }`}
          >
            {isCalibrating ? 'EXTRACTING...' : calibrated ? 'GEOREFERENCED' : 'CALIBRATE'}
          </button>

          <button
            onClick={handleAutoInterpret}
            disabled={interpretTool.status === 'loading' || !calibrated}
            className="w-full py-2 bg-purple-500/10 border border-purple-500/30 text-purple-400 text-[10px] font-mono uppercase flex justify-center items-center gap-2"
          >
            {interpretTool.status === 'loading' ? 'ANALYZING...' : '✨ SOVEREIGN INTERPRET'}
          </button>

          {interpretTool.data && (
            <div className={`mt-2 p-3 border font-mono text-[11px] leading-relaxed ${isBlocked ? 'border-red-500/30 bg-red-500/5 text-red-200' : 'border-purple-500/30 bg-purple-500/5 text-purple-200'}`}>
              <div className="text-[9px] mb-2 flex items-center gap-2">
                {isBlocked ? <AlertTriangle size={12} className="text-red-500" /> : <BarChart3 size={12} />}
                {isBlocked ? '888_JUDGE HOLD' : 'INTERPRETATION'}
              </div>
              <pre className="whitespace-pre-wrap">{interpretTool.data}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Domain1D;
