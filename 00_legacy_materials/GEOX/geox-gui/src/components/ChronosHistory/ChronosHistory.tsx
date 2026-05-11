import React from 'react';
import { Clock, Play, SkipBack, SkipForward, BarChart2, Activity } from 'lucide-react';

export const ChronosHistory: React.FC = () => {
  return (
    <div className="h-full flex flex-col bg-[#020617] text-slate-300 font-sans overflow-hidden">
      {/* Timeline Header */}
      <div className="h-14 border-b border-slate-800 bg-slate-900/30 flex items-center px-6 justify-between">
        <div>
           <div className="flex items-center gap-2 text-xs font-black text-blue-500 uppercase tracking-[0.2em] mb-0.5">
             <Clock className="w-3 h-3" />
             <span>Dimension_5: Chronos_4D</span>
           </div>
           <h2 className="text-lg font-black text-white leading-none uppercase tracking-tighter italic">Active_Sequence_001</h2>
        </div>

        {/* Playback Controls */}
        <div className="flex items-center gap-3 bg-slate-900/80 border border-slate-800 rounded-full px-4 py-1.5 shadow-xl shadow-blue-500/5">
           <button className="text-slate-500 hover:text-white transition-colors"><SkipBack className="w-4 h-4" /></button>
           <button className="w-8 h-8 flex items-center justify-center bg-blue-600 rounded-full text-white hover:bg-blue-500 transition-all hover:scale-110 shadow-lg shadow-blue-600/20">
             <Play className="w-4 h-4 fill-current ml-0.5" />
           </button>
           <button className="text-slate-500 hover:text-white transition-colors"><SkipForward className="w-4 h-4" /></button>
        </div>

        <div className="flex items-center gap-4">
           <div className="text-right">
             <span className="block text-[10px] text-slate-500 uppercase font-black tracking-widest leading-none">Simulation Epoch</span>
             <span className="text-blue-400 font-mono text-sm">2026.Q4.V3</span>
           </div>
           <BarChart2 className="w-5 h-5 text-slate-600" />
        </div>
      </div>

      {/* Timeline Visualization Area */}
      <div className="flex-1 relative flex flex-col items-center justify-center bg-radial-dark">
         {/* Waveform / Activity Mock */}
         <div className="w-full max-w-2xl h-32 flex items-end gap-1 mb-8">
            {[...Array(40)].map((_, i) => (
              <div
                key={i}
                className="flex-1 bg-blue-500/20 rounded-t-sm hover:bg-blue-500/40 transition-all cursor-crosshair"
                style={{ height: `${Math.random() * 100 + 10}%` }}
              />
            ))}
         </div>

         <div className="text-center">
            <Activity className="w-12 h-12 text-blue-500/20 mx-auto mb-4 animate-pulse" />
            <h3 className="text-xl font-bold text-white uppercase tracking-wider">Temporal <span className="text-blue-500">Flux Registry</span></h3>
            <p className="text-slate-500 text-sm max-w-xs mx-auto mt-2 font-mono">
              Monitoring 4D seismic attribute variance across production lifecycle.
            </p>
         </div>

         {/* Time Axis */}
         <div className="absolute bottom-10 left-10 right-10 h-1 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full w-1/3 bg-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.5)]" />
         </div>
         <div className="absolute bottom-4 left-10 right-10 flex justify-between text-[10px] font-mono text-slate-600">
            <span>2020.01.01</span>
            <span>2022.06.12</span>
            <span>2024.12.31</span>
            <span>PRESENT</span>
         </div>
      </div>

      {/* Stats Overlay */}
      <div className="absolute bottom-20 left-6 flex flex-col gap-2">
         <StatCard label="Phase" value="Calibrating" />
         <StatCard label="Drift" value="0.04s" />
         <StatCard label="Samples" value="1.2M" />
      </div>
    </div>
  );
};

const StatCard: React.FC<{label: string, value: string}> = ({label, value}) => (
  <div className="bg-slate-900/60 backdrop-blur-md border border-white/5 p-2 px-3 rounded flex items-center gap-3">
    <span className="text-[10px] text-slate-500 font-black uppercase tracking-widest">{label}</span>
    <span className="text-blue-400 font-mono text-xs">{value}</span>
  </div>
);
