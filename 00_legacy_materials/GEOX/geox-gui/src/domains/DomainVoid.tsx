import React, { useState, useEffect } from 'react';
import { Activity, Zap, Sliders, Shield, BarChart3, AlertTriangle } from 'lucide-react';
import { useMcpTool } from '../hooks/useMcpTool';

const Badge: React.FC<{ children: React.ReactNode; color?: string }> = ({ children, color = "amber" }) => {
  const colors: Record<string, string> = {
    amber: "border-amber-500/30 text-amber-500 bg-amber-500/10",
    emerald: "border-emerald-500/30 text-emerald-500 bg-emerald-500/10",
    purple: "border-purple-500/30 text-purple-400 bg-purple-500/10",
    red: "border-red-500/30 text-red-500 bg-red-500/10",
  };
  return (
    <span className={`px-1.5 py-0.5 text-[10px] font-mono border rounded uppercase tracking-wider ${colors[color]}`}>
      {children}
    </span>
  );
};

export const DomainVoid: React.FC = () => {
  const interpretTool = useMcpTool<any, string>('bridge.interpret_causal_scene');
  const stoiipTool = useMcpTool<any, any>('prospect.compute_stoiip');

  const [rw, setRw] = useState(0.04);
  const [archieM, setArchieM] = useState(2.0);
  const [phiCut, setPhiCut] = useState(0.10);

  const canonPhi = 0.18;
  const canonRes = 12.5;
  const area = 5000;
  const grossH = 250;
  const bo = 1.25;

  const derivedSw = Math.min(1.0, Math.max(0.0, Math.sqrt(rw / (Math.pow(canonPhi, archieM) * canonRes))));
  const derivedNTG = canonPhi >= phiCut ? 0.75 - ((phiCut - 0.05) * 2) : 0.0;

  // Deterministic STOIIP call to backend
  useEffect(() => {
    stoiipTool.call({
      area: area * 10000, // example scaling
      thickness: grossH,
      phi: canonPhi,
      sw: derivedSw,
      fvf: bo
    });
  }, [rw, archieM, phiCut]);

  const computedSTOIIP = stoiipTool.data?.stoiip_stb ? stoiipTool.data.stoiip_stb / 1000000 : 0;

  const bins = Array.from({ length: 40 }, (_, i) => Math.exp(-Math.pow((i/40) - 0.5, 2) / 0.05) * 100 + Math.random() * 5);
  const maxBin = Math.max(...bins);

  const handleGenerateVerdict = async () => {
    await interpretTool.call({ domain: 'prospect', user_query: 'Assess volumetric risk' });
  };

  const isBlocked = interpretTool.data?.includes('HOLD') || stoiipTool.status === 'error';

  return (
    <div className="flex flex-col h-full gap-4 p-4">
      <div className="flex justify-between items-end mb-2 border-b border-gray-800 pb-2">
        <div>
          <h2 className="text-xl font-bold tracking-widest flex items-center gap-2">
            <Activity className="w-5 h-5 text-amber-500" /> THE VOID [000-249]
          </h2>
          <p className="text-xs text-gray-500 font-mono">SOVEREIGN PROSPECT ENGINE</p>
        </div>
        <div className="flex gap-2">
          {stoiipTool.data?.status === 'VERIFIED' ? <Badge color="emerald">VERIFIED TRUTH</Badge> : <Badge color="amber">SIMULATED</Badge>}
          <Badge color="purple">MCP: {interpretTool.status === 'loading' ? 'SYNCING...' : 'ONLINE'}</Badge>
          <Badge color="amber">F7: HUMILITY</Badge>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 h-full">
        <div className="col-span-2 glass-panel p-4 flex flex-col relative">
          <div className="absolute top-4 right-4 text-xs font-mono text-gray-500 flex items-center gap-2">
            <Zap className="w-3 h-3 text-cyan-500"/> DETERMINISTIC VOLUMETRICS (MMstb)
          </div>

          <div className="flex-1 flex items-end gap-1 pt-12 pb-4 border-b border-gray-800 relative">
            <div className={`absolute top-8 left-1/2 -translate-x-1/2 text-black text-xs font-bold px-2 py-1 z-10 font-mono ${isBlocked ? 'bg-red-500' : 'bg-amber-500'}`}>
              P50: {computedSTOIIP.toFixed(1)} MMstb
            </div>
            {bins.map((val, i) => (
              <div key={i} className={`flex-1 border-t transition-all duration-300 ${isBlocked ? 'bg-red-500/20 border-red-500/50' : 'bg-amber-500/20 border-amber-500/50'}`} style={{ height: `${(val / maxBin) * 100}%` }} />
            ))}
          </div>

          <div className="mt-4 grid grid-cols-4 gap-2 text-[10px] font-mono text-gray-400 bg-gray-900/50 p-2 border border-gray-800">
             <div className="flex flex-col"><span>CANON_9 φ:</span><span className="text-cyan-400 font-bold">0.18 v/v</span></div>
             <div className="flex flex-col"><span>CANON_9 ρₑ:</span><span className="text-cyan-400 font-bold">12.5 Ω·m</span></div>
             <div className="flex flex-col border-l border-gray-700 pl-2"><span>DERIVED Sw:</span><span className="text-amber-500 font-bold">{(derivedSw * 100).toFixed(1)} %</span></div>
             <div className="flex flex-col border-l border-gray-700 pl-2"><span>AUTHORITY:</span><span className="text-emerald-500 font-bold">{stoiipTool.data?.status || 'UNKNOWN'}</span></div>
          </div>

          {interpretTool.data && (
            <div className={`mt-2 p-3 border font-mono text-xs ${isBlocked ? 'border-red-500/30 bg-red-500/5 text-red-200' : 'border-purple-500/30 bg-purple-500/5 text-purple-200'}`}>
              <div className="text-[9px] mb-2 flex items-center gap-2">
                {isBlocked ? <AlertTriangle size={12} className="text-red-500" /> : <BarChart3 size={12} />}
                {isBlocked ? '888_JUDGE HOLD REPORT' : 'SOVEREIGN SYNTHESIS'}
              </div>
              <pre className="whitespace-pre-wrap">{interpretTool.data}</pre>
            </div>
          )}
        </div>

        <div className="flex flex-col gap-4">
          <div className="glass-panel p-4 flex-1 flex flex-col">
            <div className="text-xs font-mono text-gray-500 mb-4 border-b border-gray-800 pb-1 flex justify-between">
              CONSTITUTIVE LEVERS <Sliders size={14}/>
            </div>

            <div className="space-y-5 flex-1">
              <div className="flex flex-col gap-2">
                <div className="flex justify-between text-[10px] font-mono">
                  <span className="text-gray-300">Form. Water (Rw)</span>
                  <span className="text-amber-500">{rw.toFixed(3)} Ωm</span>
                </div>
                <input type="range" min="0.01" max="0.15" step="0.005" value={rw} onChange={(e) => setRw(parseFloat(e.target.value))} className="w-full accent-amber-500" />
              </div>

              <div className="flex flex-col gap-2">
                <div className="flex justify-between text-[10px] font-mono">
                  <span className="text-gray-300">Cementation (m)</span>
                  <span className="text-amber-500">{archieM.toFixed(2)}</span>
                </div>
                <input type="range" min="1.5" max="2.5" step="0.05" value={archieM} onChange={(e) => setArchieM(parseFloat(e.target.value))} className="w-full accent-amber-500" />
              </div>

              <div className="flex flex-col gap-2">
                <div className="flex justify-between text-[10px] font-mono">
                  <span className="text-gray-300">φ Cut-off (NTG)</span>
                  <span className="text-amber-500">{(phiCut*100).toFixed(0)}%</span>
                </div>
                <input type="range" min="0.05" max="0.18" step="0.01" value={phiCut} onChange={(e) => setPhiCut(parseFloat(e.target.value))} className="w-full accent-amber-500" />
              </div>
            </div>
          </div>

          <div className="glass-panel p-4 flex flex-col justify-center items-center relative overflow-hidden gap-3 shrink-0">
             <div className="absolute opacity-5"><Shield size={80}/></div>
             <div className="text-xs font-mono text-gray-500 z-10">DECISION VERDICT</div>
             <button
               onClick={handleGenerateVerdict}
               disabled={interpretTool.status === 'loading'}
               className="w-full py-2 bg-purple-500/10 border border-purple-500/30 text-purple-400 text-[10px] font-mono uppercase hover:bg-purple-500/20 transition-colors z-10 flex justify-center items-center gap-2 disabled:opacity-50"
             >
                {interpretTool.status === 'loading' ? 'SYNTHESIZING...' : '✨ INTERPRET CAUSAL SCENE'}
             </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DomainVoid;
