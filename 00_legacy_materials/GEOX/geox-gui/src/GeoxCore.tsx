import React, { useState, useEffect, useRef } from 'react';
import {
  Activity, Layers, Box, Terminal, Shield, Zap, Target,
  Cpu, Database, Clock, Globe, Network, Settings,
  ChevronLeft, ChevronRight, AlignLeft, MapPin, Gauge
} from 'lucide-react';
import { DomainVoid } from './domains/DomainVoid';
import { Domain1D } from './domains/Domain1D';
import { Domain2D } from './domains/Domain2D';
import { Domain3D } from './domains/Domain3D';
import { DomainLEM } from './domains/DomainLEM';
import { useMcpTool } from './hooks/useMcpTool';
import './styles/designSystem.css';

const Badge: React.FC<{ children: React.ReactNode; color?: string }> = ({ children, color = "amber" }) => {
  const colors: Record<string, string> = {
    amber: "border-amber-500/30 text-amber-500 bg-amber-500/10",
    emerald: "border-emerald-500/30 text-emerald-500 bg-emerald-500/10",
    slate: "border-slate-500/30 text-slate-400 bg-slate-500/10",
    cyan: "border-cyan-500/30 text-cyan-400 bg-cyan-500/10",
  };
  return (
    <span className={`px-1.5 py-0.5 text-[10px] font-mono border rounded uppercase tracking-wider ${colors[color]}`}>
      {children}
    </span>
  );
};

export const GeoxCore: React.FC = () => {
  const [activeDomain, setActiveDomain] = useState('prospect');
  const [time, setTime] = useState('');
  const interpretTool = useMcpTool<any, string>('bridge.interpret_causal_scene');
  const [terminalInput, setTerminalInput] = useState('');
  const [terminalLog, setTerminalLog] = useState([
    { sender: 'sys', text: '> PHYSICS_9 Initialized...' },
    { sender: 'sys', text: '> Inverse Mapping Ready...' },
    { sender: 'sys', text: '> 888 Judge Acknowledged.' }
  ]);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const int = setInterval(() => {
      const d = new Date();
      setTime(`${d.getUTCHours().toString().padStart(2,'0')}${d.getUTCMinutes().toString().padStart(2,'0')}Z`);
    }, 1000);
    return () => clearInterval(int);
  }, []);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [terminalLog, interpretTool.status]);

  const handleTerminalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!terminalInput.trim() || interpretTool.status === 'loading') return;

    const userText = terminalInput.trim();
    setTerminalInput('');
    setTerminalLog(prev => [...prev, { sender: 'user', text: `> USER: ${userText}` }]);

    try {
      const response = await interpretTool.call({ domain: 'bridge', user_query: userText });
      setTerminalLog(prev => [...prev, { sender: 'geox', text: `> GEOX: ${response}` }]);
    } catch (err) {
      setTerminalLog(prev => [...prev, { sender: 'sys', text: `> ERROR: ${err}` }]);
    }
  };

  const domains = [
    { id: 'prospect', label: 'PROSPECT [000]', icon: Gauge },
    { id: 'well', label: 'WELL_DESK [250]', icon: AlignLeft },
    { id: 'section', label: 'SECTION [500]', icon: Globe },
    { id: 'earth3d', label: 'EARTH_VOL [750]', icon: Activity },
    { id: 'time4d', label: 'CHRONOS [999]', icon: Clock },
    { id: 'physics', label: 'JUDGE_CORE', icon: Shield },
    { id: 'map', label: 'MAP_LAYER', icon: MapPin },
  ];

  return (
    <div className="h-screen w-full flex flex-col overflow-hidden bg-[#0A0C0E] text-slate-200">
      <header className="h-12 border-b border-gray-800 bg-black/50 flex items-center justify-between px-4 z-10 shrink-0">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-amber-500" />
            <h1 className="font-bold tracking-[0.2em] text-sm">GEOX // CORE</h1>
          </div>
          <div className="h-4 w-px bg-gray-800" />
          <div className="hidden md:flex items-center gap-3 text-[10px] font-mono">
            <div className="flex items-center gap-1 text-emerald-500">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>SOVEREIGN MCP LINKED</span>
            </div>
            <span className="text-gray-600">|</span>
            <span className="text-gray-400">STATE: <span className="text-emerald-400">SYNCHRONIZED</span></span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden md:flex gap-1">
            <Badge color="cyan">999_SEAL ACTIVE</Badge>
            <Badge color="slate">F9: PHYSICS-9</Badge>
            <Badge color="emerald">F11: COMMAND AUTH</Badge>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 bg-gray-900 border border-gray-700 rounded-sm">
            <Shield className="w-3 h-3 text-amber-500" />
            <span className="text-[11px] font-mono text-amber-500 font-bold tracking-widest">888_JUDGE</span>
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <aside className="w-16 md:w-64 border-r border-gray-800 bg-black/30 flex flex-col shrink-0 z-10 overflow-hidden">
          <div className="flex-1 py-4 flex flex-col gap-2 overflow-y-auto">
            {domains.map((d) => {
              const Icon = d.icon;
              const isActive = activeDomain === d.id;
              return (
                <button
                  key={d.id}
                  onClick={() => setActiveDomain(d.id)}
                  className={`flex items-center gap-3 px-4 py-3 border-l-2 transition-all shrink-0 ${
                    isActive
                      ? 'border-amber-500 bg-amber-500/10 text-amber-500 glow-amber'
                      : 'border-transparent text-gray-500 hover:bg-gray-800/50 hover:text-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5 shrink-0" />
                  <span className="text-xs font-mono tracking-wider hidden md:block text-left">{d.label}</span>
                </button>
              );
            })}
          </div>

          <div className="h-64 border-t border-gray-800 p-4 flex-col gap-2 bg-[#050608] hidden md:flex shrink-0">
            <div className="text-[10px] font-mono text-gray-600 flex items-center gap-2 border-b border-gray-800 pb-2">
              <Zap className="w-3 h-3 text-amber-500" /> SOVEREIGN TERMINAL
            </div>

            <div className="flex-1 overflow-y-auto text-[9px] font-mono flex flex-col gap-1 pr-1">
              {terminalLog.map((log, i) => (
                <div key={i} className={`leading-relaxed ${
                  log.sender === 'user' ? 'text-gray-400' :
                  log.sender === 'geox' ? 'text-amber-500 glow-amber' : 'text-emerald-700'
                }`}>
                  {log.text}
                </div>
              ))}
              {interpretTool.status === 'loading' && <div className="text-purple-500 animate-pulse">{'>'} SYNTHESIZING...</div>}
              <div ref={terminalEndRef} />
            </div>

            <form onSubmit={handleTerminalSubmit} className="mt-auto flex items-center gap-2 border border-gray-800 bg-black/60 p-1.5 focus-within:border-amber-500/50 transition-colors">
              <Terminal className="w-3 h-3 text-gray-500 shrink-0" />
              <input
                type="text"
                value={terminalInput}
                onChange={(e) => setTerminalInput(e.target.value)}
                placeholder="✨ QUERY MCP..."
                disabled={interpretTool.status === 'loading'}
                className="bg-transparent border-none outline-none text-[9px] font-mono text-amber-100 w-full placeholder-gray-700 disabled:opacity-50"
              />
            </form>
            <div className="flex items-center gap-2 mt-1">
               <Clock className="w-3 h-3 text-gray-600"/>
               <span className="text-[9px] font-mono text-gray-500">{time}</span>
            </div>
          </div>
        </aside>

        <main className="flex-1 relative overflow-hidden bg-gradient-to-br from-[#0A0C0E] to-[#0d1117]">
          {activeDomain === 'prospect' && <DomainVoid />}
          {activeDomain === 'well' && <Domain1D />}
          {activeDomain === 'section' && <Domain2D />}
          {activeDomain === 'earth3d' && <Domain3D />}
          {activeDomain === 'physics' && <DomainLEM />}
          {activeDomain === 'time4d' && (
            <div className="flex flex-col gap-6 p-8 h-full overflow-y-auto">
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <h2 className="text-3xl font-light tracking-wider text-orange-400">4D DYNAMIC EVOLUTION</h2>
                <div className="rounded-full bg-orange-400/20 px-4 py-1 text-xs font-bold text-orange-400">TIME MANIFOLD</div>
              </div>

              <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                <div className="rounded-xl border border-white/5 bg-white/5 p-6 backdrop-blur-md">
                  <h3 className="mb-4 text-xl font-medium text-white/80">Basin Maturation Curve</h3>
                  <div className="flex h-48 items-center justify-center rounded-lg border border-white/10 bg-black/40">
                    <span className="text-white/40 italic">Syncing with Thermal Maturity Model...</span>
                  </div>
                </div>

                <div className="rounded-xl border border-white/5 bg-white/5 p-6 backdrop-blur-md">
                  <h3 className="mb-4 text-xl font-medium text-white/80">Dynamic State Vector (vₜ)</h3>
                  <p className="text-white/60 leading-relaxed text-sm">
                    Real-time monitoring of reservoir depletion and pressure transients.
                    Governed by the <strong>Physics9 Meta-Kernel</strong> to ensure mass balance integrity.
                  </p>
                  <div className="mt-4 flex flex-col gap-2">
                    <div className="h-2 rounded-full bg-orange-400/20"><div className="h-full w-2/3 rounded-full bg-orange-400 shadow-[0_0_10px_rgba(251,146,60,0.5)]"></div></div>
                    <div className="h-2 rounded-full bg-orange-400/10"><div className="h-full w-1/3 rounded-full bg-orange-400/60 transition-all hover:w-1/2"></div></div>
                  </div>
                </div>
              </div>

              <div className="mt-4 rounded-lg border border-white/10 bg-orange-900/10 p-4">
                <p className="text-sm font-light text-orange-200/70">
                  <span className="font-bold text-orange-400 uppercase">Status:</span> Calibrating 4D vintage correlation... F9 Physics Lock Active.
                </p>
              </div>
            </div>
          )}
          {activeDomain === 'map' && (
             <div className="flex flex-col gap-6 p-8 h-full overflow-y-auto">
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <h2 className="text-3xl font-light tracking-wider text-emerald-400">GEOSPATIAL REFERENCE FABRIC</h2>
                <div className="rounded-full bg-emerald-400/20 px-4 py-1 text-xs font-bold text-emerald-400">GLOBAL MAP</div>
              </div>

              <div className="relative flex-1 min-h-[400px] w-full overflow-hidden rounded-2xl border border-white/10 bg-black/40 backdrop-blur-lg">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(52,211,153,0.1)_0,transparent_70%)]"></div>
                <div className="flex h-full flex-col items-center justify-center gap-4">
                  <div className="h-24 w-24 animate-pulse rounded-full border-2 border-emerald-400/30"></div>
                  <p className="text-lg font-light tracking-widest text-emerald-400/80">IGNITING EARTHWITNESS ENGINE</p>
                  <div className="flex gap-4">
                    <span className="text-xs text-white/40 font-mono">LAT: 5.5000°N</span>
                    <span className="text-xs text-white/40 font-mono">LON: 104.5000°E</span>
                    <span className="text-xs text-white/40 font-mono">CRS: WGS84</span>
                  </div>
                </div>

                <div className="absolute bottom-4 right-4 flex flex-col gap-2">
                   <button className="h-10 w-10 border border-white/20 bg-black/60 text-white backdrop-blur-md hover:bg-emerald-400/20 text-xl flex items-center justify-center shadow-lg">+</button>
                   <button className="h-10 w-10 border border-white/20 bg-black/60 text-white backdrop-blur-md hover:bg-emerald-400/20 text-xl flex items-center justify-center shadow-lg">-</button>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 shrink-0">
                {['CONCESSIONS', 'INFRASTRUCTURE', 'SURFACE_GEOLOGY'].map(layer => (
                  <div key={layer} className="flex items-center gap-3 rounded-lg border border-white/5 bg-white/5 p-3 text-xs text-white/60 hover:border-emerald-500/30 transition-colors cursor-pointer group">
                     <div className="h-2 w-2 rounded-full bg-emerald-400 group-hover:shadow-[0_0_8px_rgba(52,211,153,0.8)]"></div>
                     {layer}
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>

      <footer className="h-8 border-t border-gray-800 bg-[#050608] flex items-center justify-between px-4 shrink-0 z-10">
        <span className="text-[9px] font-mono text-gray-600 tracking-[0.3em]">
          GEOX_CORE_v2026.04.11 // SOVEREIGN_MCP_GATEWAY
        </span>
        <span className="text-[9px] font-mono font-bold text-amber-600/80 tracking-widest uppercase">
          DITEMPA BUKAN DIBERI // 999_SEAL
        </span>
      </footer>
    </div>
  );
};

export default GeoxCore;
