import React from 'react';
import { Layout, Maximize2, Download, Layers } from 'lucide-react';

export const SectionCanvas: React.FC = () => {
  return (
    <div className="h-full flex flex-col bg-[#0f172a] text-slate-300 font-sans overflow-hidden">
      {/* Toolbar */}
      <div className="h-10 border-b border-slate-800 bg-slate-900/50 flex items-center px-4 justify-between">
        <div className="flex items-center gap-4 text-xs font-bold uppercase tracking-widest text-slate-500">
          <div className="flex items-center gap-2">
            <Layout className="w-3 h-3 text-blue-400" />
            <span>Dimension_3: Section_Canvas</span>
          </div>
          <div className="flex items-center gap-2 border-l border-slate-700 pl-4">
            <span className="text-blue-400/50">Line:</span>
            <span>MY-2026-SEISMIC-01</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button className="p-1.5 hover:bg-slate-800 rounded transition-colors" title="Layers">
            <Layers className="w-4 h-4" />
          </button>
          <button className="p-1.5 hover:bg-slate-800 rounded transition-colors" title="Export">
            <Download className="w-4 h-4" />
          </button>
          <button className="p-1.5 hover:bg-slate-800 rounded transition-colors" title="Fullscreen">
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Viewport */}
      <div className="flex-1 relative overflow-hidden group">
        {/* The Grid / Fabric */}
        <div className="absolute inset-0 opacity-20 pointer-events-none"
             style={{
               backgroundImage: 'linear-gradient(#475569 1px, transparent 1px), linear-gradient(90deg, #475569 1px, transparent 1px)',
               backgroundSize: '40px 40px'
             }}>
        </div>

        {/* Placeholder Visualization */}
        <div className="absolute inset-0 flex flex-col items-center justify-center p-8 text-center bg-radial-gradient">
          <div className="w-24 h-24 mb-6 rounded-full border-4 border-blue-500/20 border-t-blue-500 animate-spin flex items-center justify-center">
             <Layout className="w-8 h-8 text-blue-400 animate-pulse" />
          </div>
          <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-2">
            Section <span className="text-blue-400">Reconstruction</span>
          </h2>
          <p className="max-w-md text-slate-500 text-sm leading-relaxed mb-6">
            Synthesizing 2D cross-section from Earth3D volume and Well context.
            Calibrating stratigraphic markers against Physics9 constraints.
          </p>
          <div className="grid grid-cols-2 gap-4 w-full max-w-sm">
            <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-lg text-left">
              <span className="block text-[10px] text-slate-500 uppercase font-black mb-1 tracking-widest">Vertical Scale</span>
              <span className="text-blue-400 font-mono text-lg">1:25,000</span>
            </div>
            <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-lg text-left">
              <span className="block text-[10px] text-slate-500 uppercase font-black mb-1 tracking-widest">Horz Resolution</span>
              <span className="text-blue-400 font-mono text-lg">12.5m</span>
            </div>
          </div>
        </div>

        {/* Side Controls Overlay */}
        <div className="absolute right-4 top-1/2 -translate-y-1/2 flex flex-col gap-2 scale-90 opacity-0 group-hover:opacity-100 transition-all">
           {[1, 2, 3, 4, 5].map(i => (
             <div key={i} className="w-2 h-12 bg-slate-800/50 rounded-full hover:bg-blue-500/50 cursor-pointer transition-colors" />
           ))}
        </div>
      </div>

      {/* Status Bar */}
      <div className="h-8 bg-black/40 border-t border-slate-800 flex items-center px-4 gap-6 text-[10px] uppercase font-black tracking-widest text-slate-600">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
          <span>Status: Syncing Fabric</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-slate-700">|</span>
          <span>SP: 4502</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-slate-700">|</span>
          <span>TWT: 2.45s</span>
        </div>
      </div>
    </div>
  );
};
