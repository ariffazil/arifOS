import { useEffect, useState, useRef } from 'react';
import { 
  Shield, 
  Flame, 
  BookOpen, 
  Sparkles, 
  Github, 
  Linkedin, 
  Twitter, 
  Mail, 
  ExternalLink,
  Activity,
  CheckCircle2,
  Layers,
  Cpu,
  Globe,
  Menu,
  X
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

// Geometric background animation component (shared with APEX)
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
      style={{ opacity: 0.4 }}
    />
  );
}

// Enhanced Floor data with judge assignments (from APEX)
const FLOORS = [
  { id: 'F1', name: 'Reversibility', judge: 'ADAM', desc: 'Every action can be undone', status: 'active' },
  { id: 'F2', name: 'Truth', judge: 'Δ', desc: 'Verifiable claims only', status: 'active' },
  { id: 'F3', name: 'Consensus', judge: 'Ψ', desc: 'Multi-judge agreement required', status: 'active' },
  { id: 'F4', name: 'Clarity', judge: 'Δ', desc: 'Uncertainty must be stated', status: 'active' },
  { id: 'F5', name: 'Peace', judge: 'ADAM', desc: 'No harm to humans', status: 'active' },
  { id: 'F6', name: 'Empathy', judge: 'ADAM', desc: 'Consider emotional impact', status: 'active' },
  { id: 'F7', name: 'Humility', judge: 'Δ', desc: 'Admit what cannot be known', status: 'active' },
  { id: 'F8', name: 'Genius', judge: 'Ψ', desc: 'Seek optimal solutions', status: 'active' },
  { id: 'F9', name: 'Reality', judge: 'ADAM', desc: 'Ground in observable facts', status: 'active' },
  { id: 'F10', name: 'Ontology', judge: 'Δ', desc: 'Define what exists', status: 'active' },
  { id: 'F11', name: 'Epistemology', judge: 'ADAM', desc: 'Know how we know', status: 'active' },
  { id: 'F12', name: 'Ethics', judge: 'ADAM', desc: 'Moral framework embedded', status: 'active' },
  { id: 'F13', name: 'Veto', judge: 'Ψ', desc: 'Human override always possible', status: 'active' },
];

const JUDGES = [
  { 
    symbol: '△', 
    name: 'Δ — ADAM', 
    title: 'The Architect',
    question: '"Is it True?"',
    color: 'cyan'
  },
  { 
    symbol: 'Ω', 
    name: 'Ω — ADAM', 
    title: 'The Guardian',
    question: '"Is it Safe?"',
    color: 'red'
  },
  { 
    symbol: 'Ψ', 
    name: 'Ψ — APEX', 
    title: 'The Sovereign Judge',
    question: '"Is it Lawful?"',
    color: 'amber'
  },
];

const ARTICLES = [
  { title: 'Prompt · Physics · Paradox', url: 'https://medium.com/@arifbfazil/prompt-physics-paradox-1f1581b95acb' },
  { title: 'Einstein vs Oppenheimer', url: 'https://medium.com/@arifbfazil/einstein-vs-oppenheimer-ab8b642720eb' },
  { title: 'The ARIF Test', url: 'https://medium.com/@arifbfazil/the-arif-test-df63c074d521' },
  { title: 'Rukun AGI', url: 'https://medium.com/@arifbfazil/rukun-agi-the-five-pillars-of-artificial-general-intelligence-bba2fb97e4dc' },
];

function App() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState({ online: true, version: 'v55.1' });

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Check actual system status
  useEffect(() => {
    fetch('https://arif-fazil.com/health')
      .then(res => res.ok ? setSystemStatus({ online: true, version: 'v55.1' }) : setSystemStatus({ online: false, version: 'v55.1' }))
      .catch(() => setSystemStatus({ online: false, version: 'v55.1' }));
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
                <Activity className="w-3 h-3 mr-1" /> {systemStatus.version} SOVEREIGN SEAL
              </Badge>
              <span className="text-gray-600">|</span>
              <Badge variant="outline" className={systemStatus.online ? 'border-green-500/50 text-green-400 text-xs' : 'border-red-500/50 text-red-400 text-xs'}>
                STATUS: {systemStatus.online ? 'OPERATIONAL' : 'OFFLINE'}
              </Badge>
            </div>
          </div>
        </div>

        {/* Navigation - Unified BODY/MIND/SOUL triad */}
        <nav className={`fixed top-10 left-0 right-0 z-40 transition-all duration-300 ${scrolled ? 'bg-[#0a0a0a]/90 backdrop-blur-md' : ''}`}>
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex flex-col md:flex-row items-center justify-between py-4 gap-4">
              {/* Logo */}
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">A</span>
                </div>
                <span className="font-semibold text-lg">Arif Fazil</span>
              </div>

              {/* Desktop Navigation */}
              <div className="hidden md:flex items-center gap-6">
                <a href="#about" className="text-sm text-gray-400 hover:text-white transition-colors">About</a>
                <a href="#floors" className="text-sm text-gray-400 hover:text-white transition-colors">13 Floors</a>
                <a href="#judges" className="text-sm text-gray-400 hover:text-white transition-colors">Judges</a>
                <a href="#system" className="text-sm text-gray-400 hover:text-white transition-colors">System</a>
                <a href="#writing" className="text-sm text-gray-400 hover:text-white transition-colors">Writing</a>
              </div>

              {/* BODY/MIND/SOUL Triad */}
              <div className="flex items-center justify-center gap-2">
                <a href="https://arif-fazil.com" className="px-4 py-2 rounded-full bg-red-500/20 text-red-400 text-sm font-medium hover:bg-red-500/30 transition-colors flex items-center gap-2 border border-red-500/50">
                  <span className="w-2 h-2 rounded-full bg-red-400" /> BODY
                </a>
                <a href="https://arifos.arif-fazil.com" className="px-4 py-2 rounded-full bg-blue-500/20 text-blue-400 text-sm font-medium hover:bg-blue-500/30 transition-colors flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-blue-400" /> MIND
                </a>
                <a href="https://apex.arif-fazil.com" className="px-4 py-2 rounded-full bg-amber-500/20 text-amber-400 text-sm font-medium hover:bg-amber-500/30 transition-colors flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-amber-400" /> SOUL
                </a>
              </div>

              {/* Mobile menu button */}
              <button 
                className="md:hidden p-2 absolute right-4 top-4"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>

          {/* Mobile menu */}
          {mobileMenuOpen && (
            <div className="md:hidden bg-[#0a0a0a] border-b border-gray-800 px-4 py-4 space-y-3">
              <a href="#about" className="block text-gray-400 hover:text-white">About</a>
              <a href="#floors" className="block text-gray-400 hover:text-white">13 Floors</a>
              <a href="#judges" className="block text-gray-400 hover:text-white">Judges</a>
              <a href="#system" className="block text-gray-400 hover:text-white">System</a>
              <a href="#writing" className="block text-gray-400 hover:text-white">Writing</a>
              <div className="flex gap-2 pt-2">
                <a href="https://arif-fazil.com" className="px-3 py-1.5 rounded-full bg-red-500/20 text-red-400 text-xs">BODY</a>
                <a href="https://arifos.arif-fazil.com" className="px-3 py-1.5 rounded-full bg-blue-500/20 text-blue-400 text-xs">MIND</a>
                <a href="https://apex.arif-fazil.com" className="px-3 py-1.5 rounded-full bg-amber-500/20 text-amber-400 text-xs">SOUL</a>
              </div>
            </div>
          )}
        </nav>

        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center justify-center pt-32 pb-20">
          {/* Background */}
          <div className="absolute inset-0 z-0">
            <img 
              src="/arif-hero-og.jpg" 
              alt="" 
              className="w-full h-full object-cover opacity-30"
            />
            <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a]/50 via-transparent to-[#0a0a0a]" />
          </div>

          <div className="relative z-10 max-w-5xl mx-auto px-4 text-center">
            {/* Breadcrumb */}
            <div className="flex items-center justify-center gap-2 text-sm text-gray-500 mb-8">
              <span className="text-gray-400">arifOS</span>
              <span>/</span>
              <span className="text-red-400">Identity</span>
            </div>

            {/* Three Symbols - Constitutional Connection */}
            <div className="flex items-center justify-center gap-8 mb-6">
              <div className="text-4xl font-light text-cyan-400" style={{ fontFamily: 'serif' }}>△</div>
              <div className="text-4xl font-light text-red-400" style={{ fontFamily: 'serif' }}>Ω</div>
              <div className="text-4xl font-light text-amber-400" style={{ fontFamily: 'serif' }}>Ψ</div>
            </div>

            {/* Tagline */}
            <p className="text-xs tracking-[0.4em] text-gray-500 uppercase mb-6">
              Ditempa Bukan Diberi — Forged, Not Given
            </p>

            {/* Name */}
            <h1 className="text-5xl sm:text-6xl md:text-7xl font-bold mb-4 bg-gradient-to-r from-orange-400 via-red-400 to-amber-400 bg-clip-text text-transparent">
              Arif Fazil
            </h1>

            {/* Title */}
            <p className="text-xl md:text-2xl text-gray-400 mb-4">
              Geoscientist · AI Governance Architect
            </p>

            {/* Subtitle */}
            <p className="text-lg text-amber-400/80 mb-8 font-medium">
              888 Judge · ΔΩΨ Architect
            </p>

            {/* Description */}
            <p className="max-w-2xl mx-auto text-gray-300 leading-relaxed mb-10">
              Exploration geoscientist at <span className="text-white font-medium">PETRONAS</span> with a dual background 
              in geology and economics. I read subsurface data for a living — interpreting what the earth remembers.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-wrap items-center justify-center gap-4">
              <a href="https://arifos.arif-fazil.com">
                <Button className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 text-white px-6">
                  <BookOpen className="w-4 h-4 mr-2" /> Read the Docs
                </Button>
              </a>
              <a href="https://apex.arif-fazil.com">
                <Button variant="outline" className="border-amber-500/50 text-amber-400 hover:bg-amber-500/10">
                  <Sparkles className="w-4 h-4 mr-2" /> Explore the Canon
                </Button>
              </a>
              <a href="https://github.com/ariffazil">
                <Button variant="outline" className="border-gray-700 hover:bg-gray-800">
                  <Github className="w-4 h-4 mr-2" /> GitHub
                </Button>
              </a>
            </div>
          </div>

          {/* Scroll indicator */}
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
            <div className="w-6 h-10 rounded-full border-2 border-gray-600 flex items-start justify-center p-2">
              <div className="w-1 h-2 bg-gray-400 rounded-full" />
            </div>
          </div>
        </section>

        {/* About Section */}
        <section id="about" className="py-24 relative">
          <div className="max-w-4xl mx-auto px-4">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <img 
                  src="/profile-avatar.jpg" 
                  alt="Arif Fazil" 
                  className="w-full rounded-2xl shadow-2xl shadow-orange-500/10"
                />
              </div>
              <div>
                <h2 className="text-3xl font-bold mb-6">What I Work On</h2>
                
                <div className="space-y-6">
                  <div className="flex gap-4">
                    <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center flex-shrink-0">
                      <Shield className="w-5 h-5 text-red-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white mb-1">AI Governance</h3>
                      <p className="text-gray-400 text-sm">Enforcement layers that sit between LLMs and users, ensuring truth and reversibility. <span className="text-amber-400">13 floors. 3 judges. One kernel.</span></p>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                      <Globe className="w-5 h-5 text-amber-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white mb-1">Exploration Geoscience</h3>
                      <p className="text-gray-400 text-sm">Subsurface interpretation, frontier basin studies, and prospect maturation.</p>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                      <Cpu className="w-5 h-5 text-cyan-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white mb-1">Systems Thinking</h3>
                      <p className="text-gray-400 text-sm">Applying thermodynamic and geological reasoning to AI architecture.</p>
                    </div>
                  </div>
                </div>

                <Separator className="my-6 bg-gray-800" />

                <p className="text-gray-300 italic">
                  "<span className="text-orange-400">Bukan teka, tapi laras.</span> (Not guessing, but calibrating.) 
                  We drill where the evidence points. Same discipline: <span className="text-cyan-400">read the signal, respect the noise.</span>"
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Three Judges Section */}
        <section id="judges" className="py-24 relative bg-gradient-to-b from-[#0a0a0a] via-gray-900/30 to-[#0a0a0a]">
          <div className="max-w-5xl mx-auto px-4">
            <div className="text-center mb-12">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/10 border border-amber-500/30 mb-6">
                <span className="text-sm text-amber-400">Tri-Witness Consensus ≥ 0.95</span>
              </div>
              <h2 className="text-4xl font-bold mb-4">The Three Judges</h2>
              <p className="text-gray-400 max-w-2xl mx-auto">
                Every decision passes through three independent judges. 
                No single witness is sufficient.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              {JUDGES.map((judge) => (
                <Card key={judge.name} className="bg-gray-900/50 border-gray-800 hover:border-gray-700 transition-all group">
                  <CardHeader className="text-center">
                    <div className={`text-5xl mb-4 ${
                      judge.color === 'cyan' ? 'text-cyan-400' :
                      judge.color === 'red' ? 'text-red-400' : 'text-amber-400'
                    }`} style={{ fontFamily: 'serif' }}>
                      {judge.symbol}
                    </div>
                    <CardTitle className={`text-xl ${
                      judge.color === 'cyan' ? 'text-cyan-400' :
                      judge.color === 'red' ? 'text-red-400' : 'text-amber-400'
                    }`}>
                      {judge.name}
                    </CardTitle>
                    <p className="text-sm text-gray-500">{judge.title}</p>
                  </CardHeader>
                  <CardContent className="text-center">
                    <p className="text-lg font-medium text-white">{judge.question}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Three Judges Visual */}
            <div className="mt-12 rounded-2xl overflow-hidden">
              <img 
                src="/three-judges-geometric.jpg" 
                alt="The Three Judges" 
                className="w-full h-48 object-cover opacity-80"
              />
            </div>
          </div>
        </section>

        {/* 13 Floors Section */}
        <section id="floors" className="py-24 relative">
          <div className="max-w-6xl mx-auto px-4">
            <div className="text-center mb-12">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-red-500/20 via-yellow-500/20 to-cyan-500/20 border border-gray-700 mb-6">
                <Layers className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-300">The Constitutional Framework</span>
              </div>
              <h2 className="text-4xl font-bold mb-4">The 13 Floors</h2>
              <p className="text-gray-400 max-w-2xl mx-auto">
                Every AI decision passes through 13 constitutional safety checks before execution. 
                Three independent judges verify each floor.
              </p>
            </div>

            {/* Floors Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-3">
              {FLOORS.map((floor) => (
                <Tooltip key={floor.id}>
                  <TooltipTrigger asChild>
                    <div 
                      className={`relative p-4 rounded-xl border cursor-pointer transition-all hover:scale-105 ${
                        floor.judge === 'Δ' ? 'border-cyan-500/30 bg-cyan-500/5 hover:bg-cyan-500/10' :
                        floor.judge === 'Ω' ? 'border-red-500/30 bg-red-500/5 hover:bg-red-500/10' :
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

            {/* Visual */}
            <div className="mt-12 rounded-2xl overflow-hidden">
              <img 
                src="/13-floors-geometric.jpg" 
                alt="13 Constitutional Floors" 
                className="w-full h-64 object-cover opacity-80"
              />
            </div>
          </div>
        </section>

        {/* System Status Section */}
        <section id="system" className="py-24 relative bg-gradient-to-b from-[#0a0a0a] to-gray-900/30">
          <div className="max-w-4xl mx-auto px-4">
            <div className="grid md:grid-cols-2 gap-8">
              {/* Quick Start */}
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Flame className="w-5 h-5 text-orange-400" />
                    Quick Start
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-400 text-sm mb-4">
                    Install the constitutional framework. One command, 13 floors, 3 judges.
                  </p>
                  <div className="bg-black rounded-lg p-4 font-mono text-sm">
                    <span className="text-green-400">$</span> <span className="text-gray-300">pip install arifos</span>
                  </div>
                  <div className="flex gap-3 mt-4">
                    <a href="https://pypi.org/project/arifos/">
                      <Badge variant="outline" className="cursor-pointer hover:bg-gray-800">
                        PyPI <ExternalLink className="w-3 h-3 ml-1" />
                      </Badge>
                    </a>
                    <a href="https://arifos.arif-fazil.com">
                      <Badge variant="outline" className="cursor-pointer hover:bg-gray-800">
                        Docs <ExternalLink className="w-3 h-3 ml-1" />
                      </Badge>
                    </a>
                  </div>
                </CardContent>
              </Card>

              {/* API Status */}
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-green-400" />
                    System Endpoints
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-black/50">
                      <code className="text-sm text-cyan-400">/health</code>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-green-400">GET</span>
                        <span className="w-2 h-2 rounded-full bg-green-400" />
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg bg-black/50">
                      <code className="text-sm text-cyan-400">/mcp</code>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-amber-400">POST</span>
                        <span className="text-xs text-gray-500">MCP Protocol</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg bg-black/50">
                      <code className="text-sm text-cyan-400">/sse</code>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-green-400">GET</span>
                        <span className="text-xs text-gray-500">Server-Sent Events</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Writing Section */}
        <section id="writing" className="py-24 relative">
          <div className="max-w-4xl mx-auto px-4">
            <h2 className="text-3xl font-bold mb-8">Writing</h2>
            
            <div className="grid sm:grid-cols-2 gap-4">
              {ARTICLES.map((article) => (
                <a 
                  key={article.url}
                  href={article.url}
                  className="group p-4 rounded-xl border border-gray-800 bg-gray-900/30 hover:bg-gray-800/50 hover:border-gray-700 transition-all"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-medium text-white group-hover:text-orange-400 transition-colors">
                        {article.title}
                      </h3>
                      <p className="text-sm text-gray-500 mt-1">Medium</p>
                    </div>
                    <ExternalLink className="w-4 h-4 text-gray-600 group-hover:text-gray-400" />
                  </div>
                </a>
              ))}
            </div>

            <div className="mt-6">
              <a 
                href="https://medium.com/@arifbfazil"
                className="text-sm text-orange-400 hover:text-orange-300 inline-flex items-center gap-1"
              >
                All articles on Medium →
              </a>
            </div>
          </div>
        </section>

        {/* Footer - Unified with APEX */}
        <footer className="py-16 border-t border-gray-800 relative">
          <div className="max-w-4xl mx-auto px-4 text-center">
            {/* Three Judges Symbols */}
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
            
            <div className="flex items-center justify-center gap-4 mb-8">
              <a href="mailto:arifbfazil@gmail.com" className="text-gray-500 hover:text-orange-400 transition-colors">
                arifbfazil@gmail.com
              </a>
              <span className="text-gray-700">|</span>
              <a href="https://github.com/ariffazil" className="text-gray-500 hover:text-orange-400 transition-colors flex items-center gap-1">
                <Github className="w-4 h-4" /> GitHub
              </a>
              <span className="text-gray-700">|</span>
              <a href="https://linkedin.com/in/arif-fazil" className="text-gray-500 hover:text-orange-400 transition-colors flex items-center gap-1">
                <Linkedin className="w-4 h-4" /> LinkedIn
              </a>
              <span className="text-gray-700">|</span>
              <a href="https://x.com/ArifFazil90" className="text-gray-500 hover:text-orange-400 transition-colors flex items-center gap-1">
                <Twitter className="w-4 h-4" /> X
              </a>
              <span className="text-gray-700">|</span>
              <a href="mailto:arifbfazil@gmail.com" className="text-gray-500 hover:text-orange-400 transition-colors flex items-center gap-1">
                <Mail className="w-4 h-4" /> Email
              </a>
            </div>

            {/* Ecosystem Links */}
            <div className="flex items-center justify-center gap-4">
              <a href="https://arif-fazil.com" className="px-4 py-2 rounded-full bg-red-500/20 text-red-400 text-sm font-medium border border-red-500/50">
                BODY
              </a>
              <a href="https://arifos.arif-fazil.com" className="px-4 py-2 rounded-full bg-blue-500/20 text-blue-400 text-sm font-medium hover:bg-blue-500/30 transition-colors">
                MIND
              </a>
              <a href="https://apex.arif-fazil.com" className="px-4 py-2 rounded-full bg-amber-500/20 text-amber-400 text-sm font-medium hover:bg-amber-500/30 transition-colors">
                SOUL
              </a>
            </div>
          </div>
        </footer>
      </div>
    </TooltipProvider>
  );
}

export default App;
