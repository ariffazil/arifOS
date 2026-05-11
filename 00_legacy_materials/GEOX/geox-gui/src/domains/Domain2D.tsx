import React, { useState, useEffect, useRef } from 'react';
import { Layers, CheckCircle2, ScanFace, Zap, Crosshair, BarChart3, AlertTriangle } from 'lucide-react';
import { useMcpTool } from '../hooks/useMcpTool';

const Badge: React.FC<{ children: React.ReactNode; color?: string }> = ({ children, color = "amber" }) => {
  const colors: Record<string, string> = {
    amber: "border-amber-500/30 text-amber-500 bg-amber-500/10",
    cyan: "border-cyan-500/30 text-cyan-400 bg-cyan-500/10",
    crimson: "border-red-500/30 text-red-500 bg-red-500/10",
    purple: "border-purple-500/30 text-purple-400 bg-purple-500/10",
    emerald: "border-emerald-500/30 text-emerald-500 bg-emerald-500/10",
  };
  return (
    <span className={`px-1.5 py-0.5 text-[10px] font-mono border rounded uppercase tracking-wider ${colors[color]}`}>
      {children}
    </span>
  );
};

export const Domain2D: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const interpretTool = useMcpTool<any, string>('bridge.interpret_causal_scene');
  const [gcpScanned, setGcpScanned] = useState(false);
  const [isScanning, setIsScanning] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const w = canvas.offsetWidth || 800;
    const h = canvas.offsetHeight || 600;
    canvas.width = w;
    canvas.height = h;

    const renderSeismic = () => {
      const imgData = ctx.createImageData(w, h);
      const data = imgData.data;
      const getHorizonDepth = (x: number, type: number) => {
        const nx = x / w;
        if (type === 1) return h * 0.3 + Math.sin(nx * 10) * 30 + nx * 50;
        if (type === 2) return h * 0.6 + Math.cos(nx * 8) * 40 - nx * 20;
        return h * 0.8 + Math.sin(nx * 5) * 20;
      };

      for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
          let fx = x, fy = y;
          if (x > w * 0.4 && x < w * 0.6) fy -= (x - w * 0.4) * 0.5;
          const d1 = fy - getHorizonDepth(fx, 1);
          const wavelet = Math.sin(fy * 0.5) * Math.cos(fx * 0.05);
          let amp = wavelet + (Math.random() - 0.5) * 0.5;
          if (Math.abs(d1) < 20) amp += Math.cos(d1 * 0.2) * 2.0;

          let r = 20, g = 20, b = 20;
          if (amp > 1.0) r = Math.min(255, 100 + amp * 50);
          else if (amp < -1.0) b = Math.min(255, 100 + Math.abs(amp) * 50);
          else { const i = 50 + amp * 20; r = i; g = i; b = i; }
          const idx = (y * w + x) * 4;
          data[idx] = r; data[idx+1] = g; data[idx+2] = b; data[idx+3] = 255;
        }
      }
      ctx.putImageData(imgData, 0, 0);
    };
    renderSeismic();
  }, [gcpScanned]);

  const triggerGCPScan = () => {
    setIsScanning(true); setTimeout(() => { setIsScanning(false); setGcpScanned(true); }, 2000);
  };

  const handleSeismicAnalysis = async () => {
    await interpretTool.call({ domain: 'dim2', user_query: 'Structural & Fault Audit' });
  };

  const isBlocked = interpretTool.data?.includes('HOLD');

  return (
    <div className="flex flex-col h-full gap-4 p-4">
      <div className="flex justify-between items-end mb-2 border-b border-gray-800 pb-2">
        <div>
          <h2 className="text-xl font-bold tracking-widest flex items-center gap-2">
            <Layers className="w-5 h-5 text-blue-500" /> THE 2D INTERFACE [500-749]
          </h2>
          <p className="text-xs text-gray-500 font-mono">SOVEREIGN SEISMIC INTERPRETATION</p>
        </div>
        <div className="flex gap-2">
          {gcpScanned ? <Badge color="cyan">EARTH SCALE LOCKED</Badge> : <Badge color="crimson">UNSCALED</Badge>}
          <Badge color="purple">MCP: {interpretTool.status === 'loading' ? 'SYNCING...' : 'ONLINE'}</Badge>
          <Badge color="emerald">F8: GENIUS</Badge>
        </div>
      </div>

      <div className="flex-1 flex gap-4 overflow-hidden relative">
        <div className={`flex-1 glass-panel relative overflow-hidden flex flex-col ${isScanning ? 'gcp-active' : ''}`}>
          <div className="h-10 bg-black/60 border-b border-gray-800 flex items-center px-4 gap-4 justify-between">
            <button className="text-gray-400 hover:text-white transition-colors"><Crosshair size={16}/></button>
            <span className="text-[10px] font-mono text-gray-400">RENDER: SOVEREIGN_VOXEL_GRID</span>
          </div>
          <div className="flex-1 relative bg-black">
            <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />
            <div className="scanline" />
          </div>
        </div>

        <div className="w-64 glass-panel p-4 flex flex-col gap-4">
          <div className="text-xs font-mono text-gray-500 border-b border-gray-800 pb-2 flex justify-between items-center">
            VISION INTEL <ScanFace className="w-4 h-4 text-cyan-500" />
          </div>
          <button
            onClick={triggerGCPScan}
            disabled={isScanning || gcpScanned}
            className={`w-full py-2 border text-[10px] font-mono uppercase flex justify-center items-center gap-2 ${
              gcpScanned ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400' : 'bg-gray-800/50 border-gray-700 text-gray-400'
            }`}
          >
            {isScanning ? 'DETECTING...' : gcpScanned ? 'GCP LOCKED' : 'DETECT GCPs'}
          </button>

          {gcpScanned && (
            <div className="mt-2 flex-1 flex flex-col gap-3">
              <button
                onClick={handleSeismicAnalysis}
                disabled={interpretTool.status === 'loading'}
                className="w-full py-2 bg-purple-500/10 border border-purple-500/30 text-purple-400 text-[10px] font-mono uppercase hover:bg-purple-500/20 transition-colors flex justify-center items-center gap-2"
              >
                {interpretTool.status === 'loading' ? 'TRACING...' : '✨ ANALYZE TRAPS'}
              </button>

              {interpretTool.data && (
                <div className={`p-3 border font-mono text-[11px] leading-relaxed flex-1 ${isBlocked ? 'border-red-500/30 bg-red-500/5 text-red-200' : 'border-purple-500/30 bg-purple-500/5 text-purple-200'}`}>
                  <div className="text-[9px] mb-2 flex items-center gap-2">
                    {isBlocked ? <AlertTriangle size={12} className="text-red-500" /> : <BarChart3 size={12} />}
                    {isBlocked ? '888_JUDGE HOLD' : 'SOVEREIGN REPORT'}
                  </div>
                  <pre className="whitespace-pre-wrap">{interpretTool.data}</pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Domain2D;
