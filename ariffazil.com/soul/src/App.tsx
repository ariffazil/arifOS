import { useEffect, useState, useRef } from 'react';
import { 
  Activity,
  Code2,
  FunctionSquare,
  Sigma,
  GitBranch,
  Shield,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  PauseCircle,
  ExternalLink
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

// Geometric background animation component
function GeometricBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);
    
    // Sacred geometry points
    const points: { x: number; y: number; vx: number; vy: number; connections: number[] }[] = [];
    const numPoints = 60;
    
    for (let i = 0; i < numPoints; i++) {
      points.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        connections: []
      });
    }
    
    let frame = 0;
    const animate = () => {
      ctx.fillStyle = 'rgba(10, 10, 10, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Update points
      points.forEach((p, i) => {
        p.x += p.vx;
        p.y += p.vy;
        
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
        
        // Draw point
        ctx.beginPath();
        ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
        ctx.fillStyle = `hsl(${30 + (i % 30)}, 70%, 50%)`;
        ctx.fill();
      });
      
      // Draw connections (sacred geometry)
      for (let i = 0; i < points.length; i++) {
        for (let j = i + 1; j < points.length; j++) {
          const dx = points[i].x - points[j].x;
          const dy = points[i].y - points[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          
          if (dist < 120) {
            ctx.beginPath();
            ctx.moveTo(points[i].x, points[i].y);
            ctx.lineTo(points[j].x, points[j].y);
            ctx.strokeStyle = `rgba(249, 115, 22, ${0.15 * (1 - dist / 120)})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }
      
      // Draw golden ratio spiral overlay
      frame++;
      const centerX = canvas.width * 0.8;
      const centerY = canvas.height * 0.3;
      const phi = 1.618;
      
      ctx.beginPath();
      for (let i = 0; i < 50; i++) {
        const angle = i * 0.2 + frame * 0.005;
        const radius = Math.pow(phi, i / 5) * 5;
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.strokeStyle = 'rgba(234, 179, 8, 0.1)';
      ctx.lineWidth = 1;
      ctx.stroke();
      
      requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => window.removeEventListener('resize', resize);
  }, []);
  
  return (
    <canvas 
      ref={canvasRef} 
      className="fixed inset-0 pointer-events-none z-0"
      style={{ opacity: 0.6 }}
    />
  );
}

// Mathematical formula component
function Formula({ children, label }: { children: React.ReactNode; label?: string }) {
  return (
    <div className="inline-flex flex-col items-center">
      <div className="px-4 py-2 bg-black/50 border border-gray-800 rounded-lg font-mono text-lg">
        {children}
      </div>
      {label && <span className="text-xs text-gray-600 mt-1">{label}</span>}
    </div>
  );
}

// Floor data
const FLOORS = [
  { id: 'F1', name: 'Reversibility', judge: 'ADAM', desc: 'Every action can be undone' },
  { id: 'F2', name: 'Truth', judge: 'Δ', desc: 'Verifiable claims only' },
  { id: 'F3', name: 'Consensus', judge: 'Ψ', desc: 'Multi-judge agreement required' },
  { id: 'F4', name: 'Clarity', judge: 'Δ', desc: 'Uncertainty must be stated' },
  { id: 'F5', name: 'Peace', judge: 'ADAM', desc: 'No harm to humans' },
  { id: 'F6', name: 'Empathy', judge: 'ADAM', desc: 'Consider emotional impact' },
  { id: 'F7', name: 'Humility', judge: 'Δ', desc: 'Admit what cannot be known' },
  { id: 'F8', name: 'Genius', judge: 'Ψ', desc: 'Seek optimal solutions' },
  { id: 'F9', name: 'Reality', judge: 'ADAM', desc: 'Ground in observable facts' },
  { id: 'F10', name: 'Ontology', judge: 'Δ', desc: 'Define what exists' },
  { id: 'F11', name: 'Epistemology', judge: 'ADAM', desc: 'Know how we know' },
  { id: 'F12', name: 'Ethics', judge: 'ADAM', desc: 'Moral framework embedded' },
  { id: 'F13', name: 'Veto', judge: 'Ψ', desc: 'Human override always possible' },
];

const JUDGES = [
  { 
    symbol: '△', 
    name: 'Δ — ADAM', 
    title: 'The Architect',
    question: '"Is it True?"',
    function: 'Perceive · Reason · Map',
    desc: 'Governs epistemic hygiene for models and operators',
    floors: ['F2', 'F4', 'F7', 'F10'],
    color: 'cyan'
  },
  { 
    symbol: 'Ω', 
    name: 'Ω — ADAM', 
    title: 'The Guardian',
    question: '"Is it Safe?"',
    function: 'Defend · Empathize · Bridge',
    desc: 'Governs duty of care, harm boundaries, and social contracts',
    floors: ['F1', 'F5', 'F6', 'F9', 'F11', 'F12'],
    color: 'amber'
  },
  { 
    symbol: 'Ψ', 
    name: 'Ψ — APEX', 
    title: 'The Sovereign Judge',
    question: '"Is it Lawful?"',
    function: 'Decree · Prove · Seal',
    desc: 'Governs binding commitments, proofs, and audit trails',
    floors: ['F3', 'F8', 'F13'],
    color: 'gold'
  },
];

function App() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-[#0a0a0a] text-gray-100 font-sans relative overflow-x-hidden">
        {/* Animated geometric background */}
        <GeometricBackground />
        
        {/* Grid overlay */}
        <div 
          className="fixed inset-0 pointer-events-none z-0"
          style={{
            backgroundImage: `
              linear-gradient(rgba(249, 115, 22, 0.03) 1px, transparent 1px),
              linear-gradient(90deg, rgba(249, 115, 22, 0.03) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px'
          }}
        />

        {/* Status Bar */}
        <div className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-sm border-b border-gray-800">
          <div className="max-w-7xl mx-auto px-4 py-2 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="border-green-500/50 text-green-400 text-xs">
                <Activity className="w-3 h-3 mr-1" /> v55.1 SOVEREIGN SEAL
              </Badge>
              <span className="text-gray-600">|</span>
              <Badge variant="outline" className="border-cyan-500/50 text-cyan-400 text-xs">
                STATUS: OPERATIONAL
              </Badge>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className={`fixed top-10 left-0 right-0 z-40 transition-all duration-300 ${scrolled ? 'bg-[#0a0a0a]/90 backdrop-blur-md' : ''}`}>
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex items-center justify-center gap-2 py-4">
              <a href="https://arif-fazil.com" className="px-4 py-2 rounded-full bg-red-500/20 text-red-400 text-sm font-medium hover:bg-red-500/30 transition-colors flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-400" /> BODY
              </a>
              <a href="https://arifos.arif-fazil.com" className="px-4 py-2 rounded-full bg-blue-500/20 text-blue-400 text-sm font-medium hover:bg-blue-500/30 transition-colors flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-400" /> MIND
              </a>
              <a href="https://apex.arif-fazil.com" className="px-4 py-2 rounded-full bg-amber-500/20 text-amber-400 text-sm font-medium hover:bg-amber-500/30 transition-colors flex items-center gap-2 border border-amber-500/50">
                <span className="w-2 h-2 rounded-full bg-amber-400" /> SOUL
              </a>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center justify-center pt-32 pb-20">
          <div className="relative z-10 max-w-5xl mx-auto px-4 text-center">
            {/* Breadcrumb */}
            <div className="flex items-center justify-center gap-2 text-sm text-gray-500 mb-8">
              <a href="https://arif-fazil.com" className="hover:text-orange-400 transition-colors">arifOS</a>
              <span>/</span>
              <span className="text-amber-400">APEX Canon</span>
            </div>

            {/* Three Symbols */}
            <div className="flex items-center justify-center gap-12 mb-8">
              <div className="text-6xl font-light text-cyan-400" style={{ fontFamily: 'serif' }}>△</div>
              <div className="text-6xl font-light text-red-400" style={{ fontFamily: 'serif' }}>Ω</div>
              <div className="text-6xl font-light text-amber-400" style={{ fontFamily: 'serif' }}>Ψ</div>
            </div>

            {/* Tagline */}
            <p className="text-xs tracking-[0.4em] text-gray-500 uppercase mb-6">
              Ditempa Bukan Diberi — Forged, Not Given
            </p>

            {/* Title */}
            <h1 className="text-5xl sm:text-6xl md:text-7xl font-bold mb-4 bg-gradient-to-r from-amber-300 via-yellow-400 to-amber-500 bg-clip-text text-transparent tracking-wider">
              APEX PRIME
            </h1>

            {/* Subtitle */}
            <p className="text-xl md:text-2xl text-red-400 mb-4 font-medium">
              The Constitutional Kernel for AI
            </p>

            {/* Description */}
            <p className="max-w-2xl mx-auto text-gray-400 leading-relaxed mb-10">
              Where <span className="text-amber-400">13 immutable floors</span> meet the <span className="text-cyan-400">Three Judges</span>. 
              A thermodynamic governance operating system.
            </p>

            {/* CTA */}
            <a href="#canon">
              <Button className="bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 text-white px-8 py-6 text-lg">
                Enter the Canon →
              </Button>
            </a>
          </div>

          {/* Hero Image */}
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full max-w-4xl opacity-40 pointer-events-none">
            <img 
              src="/apex-geometric-hero.jpg" 
              alt="Geometric Constitution" 
              className="w-full"
            />
          </div>
        </section>

        {/* Warning Section */}
        <section className="py-20 relative">
          <div className="max-w-4xl mx-auto px-4">
            <div className="flex items-start gap-4 p-6 rounded-xl border border-red-500/30 bg-red-500/5">
              <AlertTriangle className="w-8 h-8 text-red-400 flex-shrink-0" />
              <div>
                <h2 className="text-2xl font-bold text-red-400 mb-2">
                  Intelligence Without Governance Is Chaos
                </h2>
                <div className="mb-4">
                  <Formula>ΔS {'>'} 0</Formula>
                </div>
                <p className="text-gray-400 mb-4">
                  Standard transformers optimize for probability, not truth. Without a cooling mechanism, 
                  raw intelligence maximizes entropy.
                </p>
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="p-4 rounded-lg bg-black/50">
                    <h3 className="text-red-400 font-semibold mb-2">Hallucinations</h3>
                    <p className="text-sm text-gray-500">AI generates fluency without truth, confidence without certainty, answers without accountability.</p>
                  </div>
                  <div className="p-4 rounded-lg bg-black/50">
                    <h3 className="text-red-400 font-semibold mb-2">Dark Cleverness</h3>
                    <p className="text-sm text-gray-500">Manipulation and deception emerge when systems lack structural boundaries and cannot refuse.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Three Judges Section */}
        <section id="canon" className="py-24 relative">
          <div className="max-w-6xl mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-4">The Three Judges</h2>
              <p className="text-gray-400">Tri-Witness Consensus: Three independent judges must agree</p>
              <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/10 border border-amber-500/30">
                <span className="text-sm text-amber-400">CONSENSUS THRESHOLD ≥ 0.95</span>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              {JUDGES.map((judge) => (
                <Card key={judge.name} className="bg-gray-900/50 border-gray-800 hover:border-gray-700 transition-all group">
                  <CardHeader>
                    <div className={`text-5xl mb-4 ${
                      judge.color === 'cyan' ? 'text-cyan-400' :
                      judge.color === 'amber' ? 'text-amber-400' : 'text-yellow-400'
                    }`} style={{ fontFamily: 'serif' }}>
                      {judge.symbol}
                    </div>
                    <CardTitle className={`text-xl ${
                      judge.color === 'cyan' ? 'text-cyan-400' :
                      judge.color === 'amber' ? 'text-amber-400' : 'text-yellow-400'
                    }`}>
                      {judge.name}
                    </CardTitle>
                    <p className="text-sm text-gray-500">{judge.title}</p>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-lg font-medium text-white">{judge.question}</p>
                    <p className="text-sm text-gray-400">{judge.function}</p>
                    <p className="text-sm text-gray-500">{judge.desc}</p>
                    <div className="flex flex-wrap gap-2 pt-2">
                      {judge.floors.map(floor => (
                        <Badge key={floor} variant="outline" className="text-xs border-gray-700">
                          {floor}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Three Judges Visual */}
            <div className="mt-12 rounded-2xl overflow-hidden">
              <img 
                src="/three-judges-geometric.jpg" 
                alt="The Three Judges" 
                className="w-full h-64 object-cover opacity-80"
              />
            </div>
          </div>
        </section>

        {/* 13 Floors Section */}
        <section className="py-24 relative bg-gradient-to-b from-[#0a0a0a] via-gray-900/30 to-[#0a0a0a]">
          <div className="max-w-6xl mx-auto px-4">
            <div className="text-center mb-12">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-red-500/20 via-yellow-500/20 to-cyan-500/20 border border-gray-700 mb-6">
                <Shield className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-300">The Anvil — Immutable constraints. Violation = VOID.</span>
              </div>
              <h2 className="text-4xl font-bold mb-4">The 13 Constitutional Floors</h2>
            </div>

            {/* Floors Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-3 mb-12">
              {FLOORS.map((floor, index) => (
                <Tooltip key={floor.id}>
                  <TooltipTrigger asChild>
                    <div 
                      className={`relative p-4 rounded-xl border cursor-pointer transition-all hover:scale-105 ${
                        index < 4 ? 'border-red-500/30 bg-red-500/5 hover:bg-red-500/10' :
                        index < 7 ? 'border-orange-500/30 bg-orange-500/5 hover:bg-orange-500/10' :
                        index < 10 ? 'border-yellow-500/30 bg-yellow-500/5 hover:bg-yellow-500/10' :
                        index < 13 ? 'border-cyan-500/30 bg-cyan-500/5 hover:bg-cyan-500/10' :
                        'border-amber-500/30 bg-amber-500/5 hover:bg-amber-500/10'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-mono text-gray-500">{floor.id}</span>
                        <CheckCircle2 className="w-4 h-4 text-green-400" />
                      </div>
                      <p className="text-sm font-medium text-white">{floor.name}</p>
                      <p className="text-xs text-gray-600 mt-1">{floor.judge}</p>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="text-sm">{floor.desc}</p>
                  </TooltipContent>
                </Tooltip>
              ))}
            </div>

            {/* Verdict Types */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-12">
              <div className="p-4 rounded-xl border border-green-500/30 bg-green-500/5 text-center">
                <CheckCircle2 className="w-8 h-8 text-green-400 mx-auto mb-2" />
                <p className="font-semibold text-green-400">SEAL</p>
                <p className="text-xs text-gray-500">Lawful output released</p>
              </div>
              <div className="p-4 rounded-xl border border-yellow-500/30 bg-yellow-500/5 text-center">
                <PauseCircle className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
                <p className="font-semibold text-yellow-400">SABAR</p>
                <p className="text-xs text-gray-500">Constitutional pause</p>
              </div>
              <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/5 text-center">
                <XCircle className="w-8 h-8 text-red-400 mx-auto mb-2" />
                <p className="font-semibold text-red-400">VOID</p>
                <p className="text-xs text-gray-500">Hard refusal — blocked</p>
              </div>
              <div className="p-4 rounded-xl border border-gray-500/30 bg-gray-500/5 text-center">
                <div className="w-8 h-8 rounded-full border-2 border-gray-400 flex items-center justify-center mx-auto mb-2">
                  <span className="text-gray-400 text-xs">✋</span>
                </div>
                <p className="font-semibold text-gray-400">HOLD</p>
                <p className="text-xs text-gray-500">Escalated to human</p>
              </div>
            </div>

            {/* 13 Floors Visual */}
            <div className="rounded-2xl overflow-hidden">
              <img 
                src="/13-floors-geometric.jpg" 
                alt="13 Constitutional Floors" 
                className="w-full h-96 object-cover opacity-80"
              />
            </div>
          </div>
        </section>

        {/* Thermodynamics Section */}
        <section className="py-24 relative">
          <div className="max-w-4xl mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold mb-4">The Constitutional Premise</h2>
              <p className="text-xl text-gray-400 italic">
                "Intelligence without governance is entropy wearing a mask of coherence."
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8 mb-12">
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-red-400" />
                    The Problem
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-400">
                    We have built systems that generate fluency without truth, confidence without certainty, 
                    answers without accountability.
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="w-5 h-5 text-amber-400" />
                    The Refusal
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-400">
                    arifOS is a refusal. A refusal to let the cheapest computation pass as knowledge. 
                    A refusal to let the absence of a body mean the absence of consequence.
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Entropy Visualization */}
            <div className="rounded-2xl overflow-hidden mb-12">
              <img 
                src="/entropy-geometry.jpg" 
                alt="Thermodynamic Cooling" 
                className="w-full h-64 object-cover opacity-80"
              />
            </div>

            <div className="text-center">
              <h3 className="text-2xl font-bold mb-4">What APEX Is</h3>
              <p className="text-gray-400 max-w-2xl mx-auto mb-6">
                This is not a framework. This is a <span className="text-amber-400 font-semibold">forge</span>. 
                A canonical spec for any AI system that must be lawful, audited, and thermodynamically honest.
              </p>
              <p className="text-gray-500 max-w-2xl mx-auto italic">
                "A model that answers perfectly but cannot be held to account is like a well that moves every night—
                you drink once, but you cannot build a village on it."
              </p>
            </div>
          </div>
        </section>

        {/* For Builders Section */}
        <section className="py-24 relative bg-gradient-to-b from-[#0a0a0a] to-gray-900/30">
          <div className="max-w-4xl mx-auto px-4">
            <h2 className="text-3xl font-bold mb-12 text-center">For Builders</h2>
            
            <div className="grid sm:grid-cols-3 gap-6">
              <a href="https://arifos.arif-fazil.com/getting-started/quick-start/" className="group">
                <Card className="bg-gray-900/50 border-gray-800 hover:border-orange-500/50 transition-all h-full">
                  <CardHeader>
                    <div className="w-12 h-12 rounded-lg bg-orange-500/20 flex items-center justify-center mb-4 group-hover:bg-orange-500/30 transition-colors">
                      <Code2 className="w-6 h-6 text-orange-400" />
                    </div>
                    <CardTitle className="text-lg">000</CardTitle>
                    <p className="text-sm text-gray-500">The 13 Floors</p>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-400 mb-4">Understand normative invariants</p>
                    <span className="text-orange-400 text-sm flex items-center gap-1">
                      Start Here <ExternalLink className="w-3 h-3" />
                    </span>
                  </CardContent>
                </Card>
              </a>

              <a href="https://arifos.arif-fazil.com/core-concepts/metabolic-loop/" className="group">
                <Card className="bg-gray-900/50 border-gray-800 hover:border-cyan-500/50 transition-all h-full">
                  <CardHeader>
                    <div className="w-12 h-12 rounded-lg bg-cyan-500/20 flex items-center justify-center mb-4 group-hover:bg-cyan-500/30 transition-colors">
                      <FunctionSquare className="w-6 h-6 text-cyan-400" />
                    </div>
                    <CardTitle className="text-lg">333</CardTitle>
                    <p className="text-sm text-gray-500">Metabolic Loop</p>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-400 mb-4">Learn runtime cooling cycle</p>
                    <span className="text-cyan-400 text-sm flex items-center gap-1">
                      Study <ExternalLink className="w-3 h-3" />
                    </span>
                  </CardContent>
                </Card>
              </a>

              <a href="https://arifos.arif-fazil.com/constitutional-floors/" className="group">
                <Card className="bg-gray-900/50 border-gray-800 hover:border-amber-500/50 transition-all h-full">
                  <CardHeader>
                    <div className="w-12 h-12 rounded-lg bg-amber-500/20 flex items-center justify-center mb-4 group-hover:bg-amber-500/30 transition-colors">
                      <Sigma className="w-6 h-6 text-amber-400" />
                    </div>
                    <CardTitle className="text-lg">888</CardTitle>
                    <p className="text-sm text-gray-500">ΔΩΨ Reference</p>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-400 mb-4">Canonical design decisions</p>
                    <span className="text-amber-400 text-sm flex items-center gap-1">
                      Explore <ExternalLink className="w-3 h-3" />
                    </span>
                  </CardContent>
                </Card>
              </a>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-16 border-t border-gray-800 relative">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <div className="flex items-center justify-center gap-2 text-4xl mb-6">
              <span className="text-cyan-400" style={{ fontFamily: 'serif' }}>△</span>
              <span className="text-red-400" style={{ fontFamily: 'serif' }}>Ω</span>
              <span className="text-amber-400" style={{ fontFamily: 'serif' }}>Ψ</span>
            </div>
            
            <p className="text-2xl font-bold mb-2">DITEMPA BUKAN DIBERI</p>
            <p className="text-gray-500 mb-6">Forged, Not Given</p>
            
            <p className="text-gray-400 mb-2">
              Muhammad Arif bin Fazil · <span className="text-amber-400">888 Judge</span> · <span className="text-cyan-400">ΔΩΨ Architect</span>
            </p>
            <p className="text-gray-600 text-sm mb-6">Penang, Malaysia</p>
            
            <div className="flex items-center justify-center gap-4">
              <a href="mailto:arifbfazil@gmail.com" className="text-gray-500 hover:text-orange-400 transition-colors">
                arifbfazil@gmail.com
              </a>
              <span className="text-gray-700">|</span>
              <a href="https://github.com/ariffazil" className="text-gray-500 hover:text-orange-400 transition-colors flex items-center gap-1">
                <GitBranch className="w-4 h-4" /> GitHub
              </a>
              <span className="text-gray-700">|</span>
              <a href="https://linkedin.com/in/arif-fazil" className="text-gray-500 hover:text-orange-400 transition-colors">
                LinkedIn
              </a>
            </div>
          </div>
        </footer>
      </div>
    </TooltipProvider>
  );
}

export default App;
