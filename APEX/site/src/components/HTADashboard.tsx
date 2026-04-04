import { useEffect, useState, useRef } from 'react';
import { Activity, Gauge, Crown, Zap, Eye, Heart, Lock, Shield } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
// Card imports removed - not currently used

interface SystemMetrics {
  clarity: number;
  stability: number;
  humility: number;
  genius: number;
  verdict: 'INIT' | 'SEAL' | 'SABAR' | 'VOID' | '888_HOLD';
}

interface FloorStatus {
  id: string;
  name: string;
  status: 'pass' | 'warn' | 'fail' | 'pending';
  value: number;
}

export function HTADashboard() {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    clarity: 0,
    stability: 0,
    humility: 0.04,
    genius: 0,
    verdict: 'INIT'
  });
  
  const [floorStatuses, setFloorStatuses] = useState<FloorStatus[]>([
    { id: 'F1', name: 'Amanah', status: 'pending', value: 0 },
    { id: 'F2', name: 'Truth', status: 'pending', value: 0 },
    { id: 'F3', name: 'Tri-Witness', status: 'pending', value: 0 },
    { id: 'F4', name: 'Clarity', status: 'pending', value: 0 },
    { id: 'F5', name: 'Peace²', status: 'pending', value: 0 },
    { id: 'F6', name: 'Empathy', status: 'pending', value: 0 },
    { id: 'F7', name: 'Humility', status: 'pass', value: 0.04 },
    { id: 'F8', name: 'Genius', status: 'pending', value: 0 },
    { id: 'F9', name: 'Anti-Hantu', status: 'pass', value: 1 },
    { id: 'F10', name: 'Ontology', status: 'pass', value: 1 },
    { id: 'F11', name: 'Authority', status: 'pass', value: 1 },
    { id: 'F12', name: 'Hardening', status: 'pass', value: 1 },
    { id: 'F13', name: 'Sovereign', status: 'pass', value: 1 },
  ]);

  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Boot sequence simulation
  useEffect(() => {
    const bootSequence = [
      { delay: 500, update: { clarity: -0.02 }, floors: [{ id: 'F4', status: 'pass' as const }] },
      { delay: 800, update: { stability: 1.12 }, floors: [{ id: 'F5', status: 'pass' as const }] },
      { delay: 1100, update: { genius: 0.87 }, floors: [{ id: 'F8', status: 'pass' as const }] },
      { delay: 1400, update: {}, floors: [{ id: 'F2', status: 'pass' as const }, { id: 'F3', status: 'pass' as const }] },
      { delay: 1700, update: { clarity: -0.031, verdict: 'SEAL' as const }, floors: [{ id: 'F1', status: 'pass' as const }, { id: 'F6', status: 'pass' as const }] },
    ];

    const timers: ReturnType<typeof setTimeout>[] = [];
    bootSequence.forEach(({ delay, update, floors }) => {
      timers.push(setTimeout(() => {
        setMetrics(prev => ({ ...prev, ...update }));
        if (floors) {
          setFloorStatuses(prev => prev.map(f => {
            const update = floors.find(u => u.id === f.id);
            return update ? { ...f, status: update.status } : f;
          }));
        }
      }, delay));
    });

    // Gentle oscillation after boot
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        clarity: -0.031 + (Math.random() - 0.5) * 0.005,
        stability: 1.12 + (Math.random() - 0.5) * 0.04,
        humility: 0.04 + (Math.random() - 0.5) * 0.006,
        genius: 0.87 + (Math.random() - 0.5) * 0.02,
      }));
    }, 3000);

    return () => {
      timers.forEach(clearTimeout);
      clearInterval(interval);
    };
  }, []);

  // Animated background canvas - Orthogonal (Upgraded)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio;
      canvas.height = canvas.offsetHeight * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };
    resize();

    const shapes: { x: number; y: number; w: number; h: number; vx: number; vy: number; color: string }[] = [];
    const colors = ['#FFD700', '#D4AF37', '#FFFACD'];
    
    for (let i = 0; i < 15; i++) {
      shapes.push({
        x: Math.random() * canvas.offsetWidth,
        y: Math.random() * canvas.offsetHeight,
        w: Math.random() * 40 + 10,
        h: Math.random() * 40 + 10,
        vx: (Math.random() - 0.5) * 0.2,
        vy: (Math.random() - 0.5) * 0.2,
        color: colors[Math.floor(Math.random() * colors.length)]
      });
    }

    let animationId: number;
    const animate = () => {
      ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);

      shapes.forEach((s) => {
        s.x += s.vx;
        s.y += s.vy;
        
        if (s.x < 0 || s.x > canvas.offsetWidth) s.vx *= -1;
        if (s.y < 0 || s.y > canvas.offsetHeight) s.vy *= -1;

        ctx.beginPath();
        ctx.strokeStyle = s.color;
        ctx.globalAlpha = 0.1;
        ctx.strokeRect(s.x, s.y, s.w, s.h);
        ctx.globalAlpha = 1.0;
      });

      // Draw rigid connection lines
      ctx.strokeStyle = '#FFD700';
      ctx.globalAlpha = 0.05;
      for(let i=0; i<canvas.offsetWidth; i+=100) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, canvas.offsetHeight);
        ctx.stroke();
      }
      for(let i=0; i<canvas.offsetHeight; i+=100) {
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(canvas.offsetWidth, i);
        ctx.stroke();
      }
      ctx.globalAlpha = 1.0;

      animationId = requestAnimationFrame(animate);
    };

    animate();
    return () => cancelAnimationFrame(animationId);
  }, []);

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'SEAL': return 'border-green-500 text-green-400 bg-green-500/10';
      case 'SABAR': return 'border-theory-500 text-theory-200 bg-theory-300/10';
      case 'VOID': return 'border-red-500 text-red-400 bg-red-500/10';
      case '888_HOLD': return 'border-purple-500 text-purple-400 bg-purple-500/10';
      default: return 'border-theory-300/30 text-theory-300/50';
    }
  };

  return (
    <div className="relative border border-theory-300/20 bg-black/40 p-8">
      {/* Animated Background */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full pointer-events-none"
        style={{ opacity: 0.4 }}
      />
      
      <div className="relative z-10 space-y-12">
        {/* Header */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-6">
            <div className="p-3 bg-theory-300 text-black">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-display text-sm font-bold text-white tracking-widest uppercase">
                HTA_CORE_MONITOR
              </h3>
              <p className="text-[10px] font-mono text-gray-600 mt-1 tracking-tighter uppercase">Real-time Constitutional State</p>
            </div>
          </div>
          <Badge variant="outline" className={`rounded-none px-6 py-2 text-[10px] font-display tracking-widest ${getVerdictColor(metrics.verdict)}`}>
            {metrics.verdict === 'INIT' ? 'BOOTING_SEQUENCE...' : `STATE: ${metrics.verdict}`}
          </Badge>
        </div>

        {/* Core Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-0 border border-theory-300/10">
          {/* Clarity */}
          <div className="p-8 border-r border-theory-300/10 hover:bg-theory-300/[0.02] transition-colors group">
            <div className="flex items-center gap-3 mb-6">
              <Eye className="w-4 h-4 text-theory-300/40 group-hover:text-theory-300 transition-colors" />
              <span className="text-[10px] font-display text-gray-500 tracking-wider">CLARITY (F4)</span>
            </div>
            <p className={`text-3xl font-mono font-bold ${metrics.clarity <= 0 ? 'text-white' : 'text-red-500'}`}>
              {metrics.clarity === 0 ? '0.000' : metrics.clarity.toFixed(3)}
            </p>
            <div className="mt-6 h-1 bg-gray-900 overflow-hidden">
              <div 
                className="h-full bg-theory-300 transition-all duration-500"
                style={{ width: `${Math.min(Math.abs(metrics.clarity) * 1000, 100)}%` }}
              />
            </div>
          </div>

          {/* Stability */}
          <div className="p-8 border-r border-theory-300/10 hover:bg-theory-300/[0.02] transition-colors group bg-theory-300/[0.01]">
            <div className="flex items-center gap-3 mb-6">
              <Heart className="w-4 h-4 text-theory-300/40 group-hover:text-theory-300 transition-colors" />
              <span className="text-[10px] font-display text-gray-500 tracking-wider">PEACE² (F5)</span>
            </div>
            <p className={`text-3xl font-mono font-bold ${metrics.stability >= 1.0 ? 'text-white' : 'text-red-500'}`}>
              {metrics.stability === 0 ? '0.00' : metrics.stability.toFixed(2)}
            </p>
            <div className="mt-6 h-1 bg-gray-900 overflow-hidden">
              <div 
                className="h-full bg-theory-300 transition-all duration-500"
                style={{ width: `${Math.min(metrics.stability * 50, 100)}%` }}
              />
            </div>
          </div>

          {/* Humility */}
          <div className="p-8 border-r border-theory-300/10 hover:bg-theory-300/[0.02] transition-colors group">
            <div className="flex items-center gap-3 mb-6">
              <Lock className="w-4 h-4 text-theory-300/40 group-hover:text-theory-300 transition-colors" />
              <span className="text-[10px] font-display text-gray-500 tracking-wider">HUMILITY (F7)</span>
            </div>
            <p className={`text-3xl font-mono font-bold ${metrics.humility >= 0.03 && metrics.humility <= 0.05 ? 'text-white' : 'text-red-500'}`}>
              {metrics.humility.toFixed(3)}
            </p>
            <div className="mt-6 h-1 bg-gray-900 overflow-hidden relative">
              <div 
                className="h-full bg-theory-300 transition-all duration-500"
                style={{ width: `${metrics.humility * 2000}%` }}
              />
            </div>
          </div>

          {/* Genius */}
          <div className="p-8 hover:bg-theory-300/[0.02] transition-colors group bg-theory-300/[0.01]">
            <div className="flex items-center gap-3 mb-6">
              <Zap className="w-4 h-4 text-theory-300/40 group-hover:text-theory-300 transition-colors" />
              <span className="text-[10px] font-display text-gray-500 tracking-wider">GENIUS (F8)</span>
            </div>
            <p className={`text-3xl font-mono font-bold ${metrics.genius >= 0.80 ? 'text-white' : 'text-theory-300'}`}>
              {metrics.genius === 0 ? '0.00' : metrics.genius.toFixed(2)}
            </p>
            <div className="mt-6 h-1 bg-gray-900 overflow-hidden">
              <div 
                className="h-full bg-theory-300 transition-all duration-500"
                style={{ width: `${Math.min(metrics.genius * 100, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Floor Status Grid */}
        <div className="p-8 border border-theory-300/20 bg-black/60 relative">
          <div className="absolute top-0 left-8 right-8 h-[1px] bg-theory-300/30" />
          <div className="flex items-center gap-4 mb-8">
            <Shield className="w-4 h-4 text-theory-300" />
            <h4 className="text-[10px] font-display text-white tracking-widest uppercase">CONSTITUTIONAL_FLOORS_STATE</h4>
          </div>
          
          <div className="grid grid-cols-4 sm:grid-cols-7 md:grid-cols-13 gap-4">
            {floorStatuses.map((floor) => (
              <div key={floor.id} className="flex flex-col items-center">
                <div 
                  className={`w-10 h-10 flex items-center justify-center text-[10px] font-display font-bold transition-all duration-500 ${
                    floor.status === 'pass' ? 'bg-theory-300 text-black' :
                    floor.status === 'warn' ? 'border-2 border-theory-500 text-theory-300' :
                    floor.status === 'fail' ? 'bg-red-500 text-white' :
                    'border border-theory-300/20 text-gray-700'
                  }`}
                  title={`${floor.id}: ${floor.name}`}
                >
                  {floor.id.replace('F', '')}
                </div>
                <span className="text-[8px] font-mono text-gray-600 mt-3 hidden md:block uppercase tracking-tighter">{floor.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-[10px] font-display text-gray-600 border-t border-theory-300/10 pt-8">
          <div className="flex items-center gap-4">
            <Gauge className="w-3 h-3 text-theory-300/40" />
            <span className="tracking-widest">ENFORCEMENT_PROTOCOL: ACTIVE</span>
          </div>
          <div className="flex items-center gap-4">
            <Crown className="w-3 h-3 text-theory-300" />
            <span className="tracking-widest">Sovereign: 888_JUDGE</span>
          </div>
        </div>
      </div>
    </div>
  );
}
