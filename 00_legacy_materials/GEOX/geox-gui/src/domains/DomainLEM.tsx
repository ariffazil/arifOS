import React, { useState } from 'react';
import { Network, ArrowRightLeft, DatabaseZap, BarChart3, AlertTriangle } from 'lucide-react';
import { useMcpTool } from '../hooks/useMcpTool';

const Badge: React.FC<{ children: React.ReactNode; color?: string }> = ({ children, color = "purple" }) => {
  const colors: Record<string, string> = {
    purple: "border-purple-500/30 text-purple-400 bg-purple-500/10",
    emerald: "border-emerald-500/30 text-emerald-500 bg-emerald-500/10",
  };
  return (
    <span className={`px-1.5 py-0.5 text-[10px] font-mono border rounded uppercase tracking-wider ${colors[color]}`}>
      {children}
    </span>
  );
};

export const DomainLEM: React.FC = () => {
  const auditTool = useMcpTool<any, string>('bridge.audit_policy_violation');
  const [isPropagating, setIsPropagating] = useState(false);

  const handleBackpropagate = async () => {
    setIsPropagating(true);
    await auditTool.call({ domain: 'physics9', user_query: 'Execute full Jacobian back-propagation audit' });
    setIsPropagating(false);
  };

  const physics9 = [
    { sym: 'ρ', name: 'Density', val: '2650', unit: 'kg/m³', color: 'text-amber-500' },
    { sym: 'Vp', name: 'P-Wave', val: '4500', unit: 'm/s', color: 'text-blue-400' },
    { sym: 'Vs', name: 'S-Wave', val: '2200', unit: 'm/s', color: 'text-blue-400' },
    { sym: 'ρₑ', name: 'Resistivity', val: '12.5', unit: 'Ω·m', color: 'text-red-400' },
    { sym: 'χ', name: 'Mag Suscept.', val: '0.002', unit: 'SI', color: 'text-gray-400' },
    { sym: 'k', name: 'Thermal Cond.', val: '2.5', unit: 'W/mK', color: 'text-orange-500' },
    { sym: 'P', name: 'Pressure', val: '45.2', unit: 'MPa', color: 'text-purple-400' },
    { sym: 'T', name: 'Temperature', val: '385', unit: 'K', color: 'text-red-500' },
    { sym: 'φ', name: 'Porosity', val: '0.18', unit: 'v/v', color: 'text-cyan-400' },
  ];

  const isBlocked = auditTool.data?.includes('HOLD');

  return (
    <div className="flex flex-col h-full gap-4 p-4">
      <div className="flex justify-between items-end mb-2 border-b border-gray-800 pb-2">
        <div>
          <h2 className="text-xl font-bold tracking-widest flex items-center gap-2">
            <Network className="w-5 h-5 text-purple-500" /> LEM METABOLIZER [1000-1249]
          </h2>
          <p className="text-xs text-gray-500 font-mono">SOVEREIGN PHYSICS_9 ENGINE</p>
        </div>
        <div className="flex gap-2">
          <Badge color="purple">MCP: {auditTool.status === 'loading' ? 'SYNCING...' : 'ONLINE'}</Badge>
          <Badge color="emerald">F2: TRUTH</Badge>
        </div>
      </div>

      <div className="flex-1 flex gap-4 overflow-hidden relative">
        <div className="w-2/3 glass-panel p-4 flex flex-col relative overflow-hidden">
          <div className="scanline" />
          <div className="text-xs font-mono text-gray-500 border-b border-gray-800 pb-2 mb-4 flex justify-between items-center z-10">
            <span>STATE VECTOR: <span className="text-amber-500">EARTH.PHYSICS_9</span></span>
          </div>

          <div className="grid grid-cols-3 gap-3 flex-1 z-10">
            {physics9.map((v, i) => (
              <div key={i} className="border border-gray-800 bg-black/40 p-3 flex flex-col justify-between hover:border-gray-600 transition-colors">
                <div className="flex justify-between items-start">
                  <span className={`text-xl font-bold font-mono ${v.color}`}>{v.sym}</span>
                  <span className="text-[9px] text-gray-600 uppercase">{v.name}</span>
                </div>
                <div className="mt-2 text-right">
                  <span className="text-lg font-mono text-gray-200">{v.val}</span>
                  <span className="text-[10px] text-gray-600 ml-1">{v.unit}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="w-1/3 glass-panel p-4 flex flex-col gap-4">
          <div className="text-xs font-mono text-gray-500 border-b border-gray-800 pb-2 flex items-center gap-2">
            <ArrowRightLeft className="w-4 h-4 text-purple-500" /> PHYSICS AUDIT SOLVER
          </div>

          <button
            onClick={handleBackpropagate}
            disabled={isPropagating || auditTool.status === 'loading'}
            className="mt-auto w-full py-3 bg-purple-500/10 border border-purple-500/50 text-purple-400 text-xs font-bold font-mono uppercase hover:bg-purple-500/20 transition-colors flex justify-center items-center gap-2 disabled:opacity-50"
          >
            {isPropagating ? <span className="animate-pulse">SOLVING JACOBIAN...</span> : <><DatabaseZap size={14}/> EXECUTE PHYSICS AUDIT</>}
          </button>

          {auditTool.data && (
            <div className={`p-3 border font-mono text-[10px] leading-relaxed flex-1 overflow-y-auto ${isBlocked ? 'border-red-500/30 bg-red-500/5 text-red-200' : 'border-purple-500/30 bg-purple-500/5 text-purple-200'}`}>
              <div className="text-[9px] mb-2 flex items-center gap-2">
                {isBlocked ? <AlertTriangle size={12} className="text-red-500" /> : <BarChart3 size={12} />}
                {isBlocked ? '888_JUDGE POLICY VIOLATION' : 'METABOLIC STATUS'}
              </div>
              <pre className="whitespace-pre-wrap">{auditTool.data}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DomainLEM;
