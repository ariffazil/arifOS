import { useState, useEffect, useRef } from 'react';
import { Activity, CheckCircle2, AlertCircle, XCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface Engine {
  symbol: string;
  name: string;
  fullName: string;
  question: string;
  function: string;
  color: string;
  bgColor: string;
  floors: string[];
  description: string;
}

const ENGINES: Engine[] = [
  {
    symbol: 'Δ',
    name: 'ARIF',
    fullName: 'Epistemic Engine',
    question: 'Is it true?',
    function: 'Perceive · Reason · Map',
    color: '#6B8CCE',
    bgColor: 'rgba(107, 140, 206, 0.05)',
    floors: ['F2', 'F4', 'F7', 'F10'],
    description: 'Fact verification and logical consistency via Bayesian inference and formal entailment.'
  },
  {
    symbol: 'Ω',
    name: 'ADAM',
    fullName: 'Safety Engine',
    question: 'Is it safe?',
    function: 'Defend · Empathize · Bridge',
    color: '#6B8CCE',
    bgColor: 'rgba(107, 140, 206, 0.05)',
    floors: ['F1', 'F5', 'F6', 'F9', 'F11', 'F12'],
    description: 'Risk assessment and stakeholder impact via consequentialist ethics and info-gap theory.'
  },
  {
    symbol: 'Ψ',
    name: 'APEX',
    fullName: 'Authority Engine',
    question: 'Is it lawful?',
    function: 'Decree · Prove · Seal',
    color: '#6B8CCE',
    bgColor: 'rgba(107, 140, 206, 0.05)',
    floors: ['F3', 'F8', 'F13'],
    description: 'Compliance verification and cryptographic audit trails via legal positivism and BLS signatures.'
  }
];

interface ConsensusState {
  arif: boolean | null;
  adam: boolean | null;
  apex: boolean | null;
  weight: number;
  verdict: 'pending' | 'approved' | 'sabar' | 'void';
}

export function EngineDiagram() {
  const [consensus, setConsensus] = useState<ConsensusState>({
    arif: null,
    adam: null,
    apex: null,
    weight: 0,
    verdict: 'pending'
  });
  const [isAnimating, setIsAnimating] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Simulate consensus formation
  const simulateConsensus = () => {
    setIsAnimating(true);
    setConsensus({ arif: null, adam: null, apex: null, weight: 0, verdict: 'pending' });

    const sequence = [
      { delay: 500, engine: 'arif' as const, value: true },
      { delay: 1200, engine: 'adam' as const, value: true },
      { delay: 2000, engine: 'apex' as const, value: true },
    ];

    sequence.forEach(({ delay, engine, value }) => {
      setTimeout(() => {
        setConsensus(prev => {
          const newState = { ...prev, [engine]: value };
          const votes = [newState.arif, newState.adam, newState.apex].filter(v => v === true).length;
          const weight = votes / 3;
          let verdict: ConsensusState['verdict'] = 'pending';
          if (weight >= 0.95) verdict = 'approved';
          else if (weight >= 0.67) verdict = 'sabar';
          else if (votes > 0 && weight < 0.67) verdict = 'void';
          return { ...newState, weight, verdict };
        });
      }, delay);
    });

    setTimeout(() => setIsAnimating(false), 3000);
  };

  // Animated connection lines
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      const rect = canvas.parentElement?.getBoundingClientRect();
      if (rect) {
        canvas.width = rect.width * window.devicePixelRatio;
        canvas.height = rect.height * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
      }
    };
    resize();
    window.addEventListener('resize', resize);

    let animationId: number;

    const animate = () => {
      const rect = canvas.parentElement?.getBoundingClientRect();
      if (!rect) return;
      
      ctx.clearRect(0, 0, rect.width, rect.height);

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const radius = Math.min(rect.width, rect.height) * 0.35;

      const positions = [
        { x: centerX, y: centerY - radius }, // ARIF (top)
        { x: centerX - radius * 0.866, y: centerY + radius * 0.5 }, // ADAM (bottom left)
        { x: centerX + radius * 0.866, y: centerY + radius * 0.5 }, // APEX (bottom right)
      ];

      // Draw rigid triangle outline
      ctx.beginPath();
      ctx.moveTo(positions[0].x, positions[0].y);
      ctx.lineTo(positions[1].x, positions[1].y);
      ctx.lineTo(positions[2].x, positions[2].y);
      ctx.closePath();
      ctx.strokeStyle = 'rgba(107, 140, 206, 0.1)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Draw center point (consensus) - Square
      ctx.beginPath();
      const s = 12;
      ctx.strokeStyle = consensus.verdict === 'approved' ? '#22c55e' :
                      consensus.verdict === 'sabar' ? '#6B8CCE' :
                      consensus.verdict === 'void' ? '#ef4444' : '#6B8CCE';
      ctx.lineWidth = 2;
      ctx.strokeRect(centerX - s/2, centerY - s/2, s, s);

      // Draw orthogonal connections with status
      positions.forEach((pos, i) => {
        const engineKey = ['arif', 'adam', 'apex'][i] as keyof ConsensusState;
        const status = consensus[engineKey];
        
        ctx.beginPath();
        ctx.moveTo(pos.x, pos.y);
        // Path to center
        ctx.lineTo(pos.x, centerY);
        ctx.lineTo(centerX, centerY);
        
        ctx.strokeStyle = status === true ? '#6B8CCE' :
                          status === false ? '#ef4444' : 'rgba(107, 140, 206, 0.15)';
        ctx.lineWidth = status !== null ? 2 : 1;
        ctx.stroke();
      });

      animationId = requestAnimationFrame(animate);
    };


    animate();
    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', resize);
    };
  }, [consensus, isAnimating]);

  const getVerdictIcon = () => {
    switch (consensus.verdict) {
      case 'approved':
        return <CheckCircle2 className="w-6 h-6 text-green-400" />;
      case 'sabar':
        return <AlertCircle className="w-6 h-6 text-theory-200" />;
      case 'void':
        return <XCircle className="w-6 h-6 text-red-400" />;
      default:
        return <Activity className="w-6 h-6 text-gray-400 animate-pulse" />;
    }
  };

  const getVerdictText = () => {
    switch (consensus.verdict) {
      case 'approved':
        return { text: 'SEAL', color: 'text-green-400', bg: 'bg-green-500/10 border-green-500/50' };
      case 'sabar':
        return { text: 'SABAR', color: 'text-theory-200', bg: 'bg-theory-300/10 border-theory-300/50' };
      case 'void':
        return { text: 'VOID', color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/50' };
      default:
        return { text: 'PENDING', color: 'text-gray-400', bg: 'bg-gray-500/10 border-gray-500/50' };
    }
  };

  return (
    <TooltipProvider>
      <div className="space-y-12">
        {/* Diagram */}
        <div className="relative h-[500px]">
          <canvas
            ref={canvasRef}
            className="absolute inset-0 w-full h-full"
          />
          
          {/* Engine Cards positioned absolutely */}
          <div className="absolute inset-0 pointer-events-none">
            {/* ARIF - Top */}
            <div 
              className="absolute left-1/2 -translate-x-1/2 pointer-events-auto"
              style={{ top: '5%' }}
            >
              <EngineCard engine={ENGINES[0]} status={consensus.arif} />
            </div>
            
            {/* ADAM - Bottom Left */}
            <div 
              className="absolute pointer-events-auto"
              style={{ bottom: '15%', left: '5%' }}
            >
              <EngineCard engine={ENGINES[1]} status={consensus.adam} />
            </div>
            
            {/* APEX - Bottom Right */}
            <div 
              className="absolute pointer-events-auto"
              style={{ bottom: '15%', right: '5%' }}
            >
              <EngineCard engine={ENGINES[2]} status={consensus.apex} />
            </div>
            
            {/* Center Consensus - Square */}
            <div 
              className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
            >
              <div className={`
                w-32 h-32 flex flex-col items-center justify-center border-2 rounded-none transition-all duration-500
                ${getVerdictText().bg}
              `}>
                {getVerdictIcon()}
                <span className={`text-[10px] font-display font-bold mt-4 tracking-widest ${getVerdictText().color}`}>
                  {getVerdictText().text}
                </span>
                <span className="text-[10px] font-mono text-gray-600 mt-2">
                  W={consensus.weight.toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="flex justify-center">
          <button
            onClick={simulateConsensus}
            disabled={isAnimating}
            className={`
              px-12 py-4 rounded-none font-display text-[10px] tracking-[0.3em] transition-all uppercase
              ${isAnimating
                ? 'bg-gray-900 text-gray-600 cursor-not-allowed border border-gray-700'
                : 'bg-theory-200 text-theory-950 hover:bg-theory-100 border border-theory-300 font-bold shadow-[0_0_15px_rgba(107,140,206,0.2)] hover:shadow-[0_0_25px_rgba(138,170,224,0.3)]'
              }
            `}
          >
            {isAnimating ? 'Executing_Consensus...' : 'Initiate_Consensus_Scan'}
          </button>
        </div>

        {/* Formula Display */}
        <div className="border border-theory-300/20 bg-black/40 p-8 relative">
          <div className="absolute top-0 left-0 w-2 h-2 bg-theory-300" />
          <h4 className="text-[10px] font-display text-gray-500 mb-8 tracking-widest uppercase text-center">Consensus_Mechanism_V55.2</h4>
          
          <div className="space-y-12">
            <div className="p-8 border border-theory-300/10 bg-theory-300/5 font-mono text-lg text-center relative">
              <span className="text-theory-300">V</span><sub className="text-xs">Δ</sub>
              <span className="text-gray-700 mx-4">+</span>
              <span className="text-theory-300">V</span><sub className="text-xs">Ω</sub>
              <span className="text-gray-700 mx-4">+</span>
              <span className="text-theory-300">V</span><sub className="text-xs">Ψ</sub>
              <span className="text-gray-700 mx-4">/</span>
              <span className="text-gray-500">3</span>
              <span className="text-gray-700 mx-4">≥</span>
              <span className="text-white">0.95</span>
            </div>
            
            <div className="grid grid-cols-3 gap-8">
              {[
                { label: 'ARIF (Δ)', val: consensus.arif },
                { label: 'ADAM (Ω)', val: consensus.adam },
                { label: 'APEX (Ψ)', val: consensus.apex }
              ].map((item) => (
                <div key={item.label} className="text-center p-6 border border-theory-300/5">
                  <p className={`text-3xl font-mono font-bold mb-2 ${item.val === true ? 'text-white' : item.val === false ? 'text-red-500' : 'text-gray-800'}`}>
                    {item.val === true ? '1' : item.val === false ? '0' : '—'}
                  </p>
                  <p className="text-[9px] font-display text-gray-600 tracking-widest">{item.label}</p>
                </div>
              ))}
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-between gap-8 pt-8 border-t border-theory-300/10">
              <div className="flex items-center gap-4">
                <span className="text-[10px] font-display text-gray-500 tracking-widest">RESULT_WEIGHT:</span>
                <span className="font-mono text-2xl font-bold text-white">
                  {consensus.weight.toFixed(2)}
                </span>
              </div>
              <Badge variant="outline" className={`rounded-none px-6 py-2 text-[10px] font-display tracking-widest ${
                consensus.weight >= 0.95 ? 'border-green-500 text-green-400 bg-green-500/5' :
                consensus.weight >= 0.67 ? 'border-theory-500 text-theory-300 bg-theory-300/5' :
                consensus.weight > 0 ? 'border-red-500 text-red-500 bg-red-500/5' :
                'border-gray-800 text-gray-600'
              }`}>
                {consensus.weight >= 0.95 ? 'SEAL_STATE' : 
                 consensus.weight >= 0.67 ? 'SABAR_HOLD' : 
                 consensus.weight > 0 ? 'VOID_BLOCK' : 'AWAITING_INPUT'}
              </Badge>
            </div>
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
}

function EngineCard({ engine, status }: { engine: Engine; status: boolean | null }) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div 
          className={`
            p-6 border-2 transition-all duration-500 rounded-none w-64
            ${status === true ? 'bg-theory-300/10 border-theory-500' : 'bg-black/80 border-theory-300/20'}
          `}
        >
          <div className="flex items-center gap-6">
            <span className={`text-4xl font-display font-light ${status === true ? 'text-white' : 'text-theory-300/40'}`}>
              {engine.symbol}
            </span>
            <div>
              <p className={`text-[10px] font-display font-bold tracking-widest ${status === true ? 'text-white' : 'text-gray-500'}`}>{engine.name}</p>
              <p className="text-[8px] font-mono text-gray-600 uppercase mt-1 tracking-tighter">{engine.function}</p>
            </div>
          </div>
          {status !== null && (
            <div className="mt-6 flex items-center justify-between border-t border-theory-300/10 pt-4">
              <span className={`text-[9px] font-display tracking-widest ${status ? 'text-green-400' : 'text-red-500'}`}>
                {status ? 'VOTE_PASS' : 'VOTE_FAIL'}
              </span>
              <div className={`w-2 h-2 ${status ? 'bg-green-500' : 'bg-red-500'}`} />
            </div>
          )}
        </div>
      </TooltipTrigger>
      <TooltipContent side="top" className="rounded-none border-theory-500 bg-black p-4 font-mono">
        <div className="space-y-2">
          <p className="font-display text-[10px] text-theory-300">{engine.name}_{engine.fullName.toUpperCase()}</p>
          <p className="text-xs text-gray-400 italic">"{engine.question}"</p>
        </div>
      </TooltipContent>
    </Tooltip>
  );
}
