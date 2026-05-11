import React from 'react';
import { Box, Globe, BarChart3, AlertTriangle } from 'lucide-react';
import { useMcpTool } from '../hooks/useMcpTool';

const Badge: React.FC<{ children: React.ReactNode; color?: string }> = ({ children, color = "emerald" }) => {
  const colors: Record<string, string> = {
    cyan: "border-cyan-500/30 text-cyan-400 bg-cyan-500/10",
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

export const Domain3D: React.FC = () => {
  const interpretTool = useMcpTool<any, string>('bridge.interpret_causal_scene');

  const handleBasinSynthesis = async () => {
    await interpretTool.call({ domain: 'dim3', user_query: 'Malay Basin regional synthesis' });
  };

  const isBlocked = interpretTool.data?.includes('HOLD');

  return (
    <div className="flex flex-col h-full gap-4 p-4">
      <div className="flex justify-between items-end mb-2 border-b border-gray-800 pb-2">
        <div>
          <h2 className="text-xl font-bold tracking-widest flex items-center gap-2">
            <Box className="w-5 h-5 text-purple-500" /> THE META DOMAIN [750-999]
          </h2>
          <p className="text-xs text-gray-500 font-mono">SOVEREIGN BASIN ENGINE</p>
        </div>
        <div className="flex gap-2">
          <Badge color="cyan">EARTH TRUE SCALE</Badge>
          <Badge color="purple">MCP: {interpretTool.status === 'loading' ? 'SYNCING...' : 'ONLINE'}</Badge>
        </div>
      </div>

      <div className="flex-1 flex gap-4 overflow-hidden relative">
        <div className="flex-1 glass-panel relative overflow-hidden bg-[#050608]">
          <div className="absolute top-2 left-2 z-20 flex items-center gap-2 px-3 py-1.5 bg-black/80 border border-purple-500/30 text-purple-400 text-[10px] font-mono shadow-lg backdrop-blur-md rounded-sm">
            <Globe className="w-3 h-3 animate-pulse" /> LIVE TELEMETRY // LNG: 103.0 LAT: 5.0 (MALAY BASIN)
          </div>
          <iframe
            src="https://macrostrat.org/map/#/z=5.0/x=103.0/y=5.0/bedrock/lines/"
            title="Macrostrat Reality Bridge"
            className="absolute inset-0 w-full h-full border-0 opacity-80 mix-blend-screen"
            style={{ filter: 'invert(1) hue-rotate(180deg) contrast(1.2)' }}
          />
          <div className="absolute inset-0 shadow-[inset_0_0_100px_rgba(10,12,14,1)] pointer-events-none z-10" />
        </div>

        <div className="w-64 glass-panel p-4 flex flex-col gap-4 z-20">
          <div className="text-xs font-mono text-gray-500 border-b border-gray-800 pb-2 flex justify-between items-center">
            BASIN INTELLIGENCE <Globe className="w-4 h-4 text-purple-500" />
          </div>
          <button
            onClick={handleBasinSynthesis}
            disabled={interpretTool.status === 'loading'}
            className="w-full py-2 bg-purple-500/10 border border-purple-500/30 text-purple-400 text-[10px] font-mono uppercase hover:bg-purple-500/20 transition-colors flex justify-center items-center gap-2"
          >
            {interpretTool.status === 'loading' ? 'SYNTHESIZING...' : '✨ GENERATE BASIN REPORT'}
          </button>

          {interpretTool.data && (
            <div className={`mt-2 p-3 border font-mono text-[11px] leading-relaxed flex-1 overflow-y-auto ${isBlocked ? 'border-red-500/30 bg-red-500/5 text-red-200' : 'border-purple-500/30 bg-purple-500/5 text-purple-200'}`}>
              <div className="text-[9px] mb-2 flex items-center gap-2">
                {isBlocked ? <AlertTriangle size={12} className="text-red-500" /> : <BarChart3 size={12} />}
                {isBlocked ? '888_JUDGE HOLD' : 'SOVEREIGN SYNTHESIS'}
              </div>
              <pre className="whitespace-pre-wrap">{interpretTool.data}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Domain3D;
