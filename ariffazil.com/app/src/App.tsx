import { useEffect, useState, useRef } from 'react';
import { 
  Shield, 
  Flame, 
  BookOpen, 
  Sparkles, 
  Github, 
  ExternalLink,
  Activity,
  CheckCircle2,
  Layers,
  Cpu,
  Globe,
  Menu,
  X,
  Zap
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
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
    
    const points: { x: number; y: number; vx: number; vy: number; connections: number[] }[] = [];
    const numPoints = 50;
    
    for (let i = 0; i < numPoints; i++) {
      points.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.2,
        vy: (Math.random() - 0.5) * 0.2,
        connections: []
      });
    }
    
    const animate = () => {
      ctx.fillStyle = 'rgba(10, 10, 10, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      points.forEach((p, i) => {
        p.x += p.vx;
        p.y += p.vy;
        
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, 1.5, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(249, 115, 22, ${0.3 + (i % 50) / 100})`;
        ctx.fill();
      });
      
      for (let i = 0; i < points.length; i++) {
        for (let j = i + 1; j < points.length; j++) {
          const dx = points[i].x - points[j].x;
          const dy = points[i].y - points[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          
          if (dist < 100) {
            ctx.beginPath();
            ctx.moveTo(points[i].x, points[i].y);
            ctx.lineTo(points[j].x, points[j].y);
            ctx.strokeStyle = `rgba(249, 115, 22, ${0.1 * (1 - dist / 100)})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }
      
      requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => window.removeEventListener('resize', resize);
  }, []);
  
  return (
    <canvas 
      ref={canvasRef} 
      className="fixed inset-0 pointer-events-none z-0"
      style={{ opacity: 0.5 }}
    />
  );
}

// Floor data with descriptions
const FLOORS = [
  { id: 'F1', name: 'Amanah', judge: 'Ω', desc: 'Is this reversible?' },
  { id: 'F2', name: 'Truth', judge: 'Δ', desc: 'Is this factually true?' },
  { id: 'F3', name: 'Tri-Witness', judge: 'Ψ', desc: 'Do Human, AI, and Earth agree?' },
  { id: 'F4', name: 'Clarity', judge: 'Δ', desc: 'Does it reduce confusion? (ΔS ≤ 0)' },
  { id: 'F5', name: 'Peace', judge: 'Ω', desc: 'Does it stabilize reality? (Peace² ≥ 1.0)' },
  { id: 'F6', name: 'Empathy', judge: 'Ω', desc: 'Does it protect the weakest stakeholder?' },
  { id: 'F7', name: 'Humility', judge: 'Δ', desc: 'Are we honest about uncertainty? (3-5% Band)' },
  { id: 'F8', name: 'Genius', judge: 'Ψ', desc: 'Is the intelligence governed? (G ≥ 0.80)' },
  { id: 'F9', name: 'Anti-Ghost', judge: 'Ω', desc: 'Is it authentic and non-deceptive?' },
  { id: 'F10', name: 'Ontology', judge: 'Δ', desc: 'Is it grounded in physical reality?' },
  { id: 'F11', name: 'Command', judge: 'Ω', desc: 'Is the authority verified?' },
  { id: 'F12', name: 'Defense', judge: 'Ω', desc: 'Is it resistant to injection?' },
  { id: 'F13', name: 'Sovereign', judge: 'Ψ', desc: 'Does the human have final veto?' },
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
    fetch('/health')
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data) {
          setSystemStatus({ online: true, version: data.version || 'v55.1' });
        } else {
          setSystemStatus({ online: false, version: 'v55.1' });
        }
      })
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

        {/* Navigation */}
        <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'bg-[#0a0a0a]/95 backdrop-blur-md border-b border-gray-800' : 'bg-transparent'}`}>
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-20">
              {/* Logo */}
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center shadow-lg shadow-orange-500/20">
                  <Zap className="w-5 h-5 text-white" />
                </div>
                <div className="flex flex-col">
                  <span className="font-bold text-lg tracking-tight leading-none">Arif Fazil</span>
                  <span className="text-[10px] text-gray-500 tracking-[0.2em] font-mono mt-1 uppercase">888_JUDGE</span>
                </div>
              </div>

              {/* Desktop Navigation */}
              <div className="hidden md:flex items-center gap-2">
                <div className="flex items-center gap-1 bg-gray-900/50 p-1 rounded-full border border-gray-800 mr-4">
                  <a href="https://arif-fazil.com" className="px-4 py-1.5 rounded-full bg-red-500 text-white text-xs font-bold transition-all shadow-lg shadow-red-500/20">
                    BODY
                  </a>
                  <a href="https://arifos.arif-fazil.com" className="px-4 py-1.5 rounded-full text-gray-400 text-xs font-bold hover:text-white transition-all">
                    MIND
                  </a>
                  <a href="https://apex.arif-fazil.com" className="px-4 py-1.5 rounded-full text-gray-400 text-xs font-bold hover:text-white transition-all">
                    SOUL
                  </a>
                </div>
                <div className="flex items-center gap-6 text-sm">
                  <a href="#about" className="text-gray-400 hover:text-white transition-colors">About</a>
                  <a href="#floors" className="text-gray-400 hover:text-white transition-colors">13 Floors</a>
                  <a href="https://github.com/ariffazil" className="text-gray-400 hover:text-white transition-colors p-2 rounded-full hover:bg-gray-800">
                    <Github className="w-5 h-5" />
                  </a>
                </div>
              </div>

              {/* Mobile menu button */}
              <button 
                className="md:hidden p-2 text-gray-400"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>

          {/* Mobile menu */}
          {mobileMenuOpen && (
            <div className="md:hidden bg-[#0a0a0a] border-b border-gray-800 px-4 py-6 space-y-4 animate-in slide-in-from-top duration-300">
              <div className="grid grid-cols-3 gap-2">
                <a href="https://arif-fazil.com" className="py-2 text-center rounded bg-red-500 text-white text-[10px] font-bold">BODY</a>
                <a href="https://arifos.arif-fazil.com" className="py-2 text-center rounded bg-gray-900 text-gray-400 text-[10px] font-bold">MIND</a>
                <a href="https://apex.arif-fazil.com" className="py-2 text-center rounded bg-gray-900 text-gray-400 text-[10px] font-bold">SOUL</a>
              </div>
              <a href="#about" className="block text-gray-400 hover:text-white text-center pb-2">About</a>
              <a href="#floors" className="block text-gray-400 hover:text-white text-center pb-2">13 Floors</a>
              <a href="#writing" className="block text-gray-400 hover:text-white text-center">Writing</a>
            </div>
          )}
        </nav>

        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center justify-center pt-20 overflow-hidden">
          <div className="relative z-10 max-w-4xl mx-auto px-4 text-center">
            {/* The Three Symbols */}
            <div className="flex items-center justify-center gap-8 mb-8">
              <span className="text-4xl font-light text-cyan-400 opacity-80" style={{ fontFamily: 'serif' }}>△</span>
              <span className="text-4xl font-light text-red-500 opacity-80" style={{ fontFamily: 'serif' }}>Ω</span>
              <span className="text-4xl font-light text-amber-500 opacity-80" style={{ fontFamily: 'serif' }}>Ψ</span>
            </div>

            {/* Tagline */}
            <p className="text-[10px] tracking-[0.5em] text-gray-500 uppercase mb-8">
              Ditempa Bukan Diberi — Forged, Not Given
            </p>

            {/* Name */}
            <h1 className="text-6xl sm:text-7xl md:text-8xl font-black mb-4 tracking-tighter">
              <span className="bg-gradient-to-r from-white via-gray-200 to-gray-500 bg-clip-text text-transparent">Arif Fazil</span>
            </h1>

            {/* Title */}
            <p className="text-xl md:text-2xl text-orange-500 font-mono mb-12 tracking-tight">
              Constitutional AI Governance Architect
            </p>

            {/* Description */}
            <p className="max-w-2xl mx-auto text-gray-400 leading-relaxed mb-12 text-lg">
              Geoscientist at PETRONAS interpreting the earth's memory. 
              Designing the metabolic engine for a safe AGI future.
            </p>

            {/* Status Badge */}
            <div className="flex items-center justify-center gap-4 mb-12">
              <div className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-full border ${systemStatus.online ? 'border-green-500/30 bg-green-500/5' : 'border-red-500/30 bg-red-500/5'}`}>
                <div className={`w-2 h-2 rounded-full ${systemStatus.online ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                <span className={`text-xs font-bold tracking-widest ${systemStatus.online ? 'text-green-400' : 'text-red-400'}`}>
                  {systemStatus.online ? 'SYSTEM ONLINE' : 'SYSTEM OFFLINE'}
                </span>
                <span className="text-xs text-gray-700 font-mono ml-1">{systemStatus.version}</span>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-wrap items-center justify-center gap-4">
              <a href="https://arifos.arif-fazil.com">
                <Button className="bg-white text-black hover:bg-gray-200 px-8 py-6 text-sm font-bold uppercase tracking-widest">
                  MIND <BookOpen className="w-4 h-4 ml-2" />
                </Button>
              </a>
              <a href="https://apex.arif-fazil.com">
                <Button variant="outline" className="border-gray-800 hover:bg-gray-900 text-white px-8 py-6 text-sm font-bold uppercase tracking-widest">
                  SOUL <Sparkles className="w-4 h-4 ml-2" />
                </Button>
              </a>
            </div>
          </div>

          {/* Background Image Hero */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full z-0 opacity-20 pointer-events-none">
            <img 
              src="/arif-hero-og.jpg" 
              alt="" 
              className="w-full h-full object-cover rounded-[100%] scale-150 blur-3xl"
            />
          </div>
        </section>

        {/* About Section */}
        <section id="about" className="py-32 relative border-t border-gray-900 bg-black/40">
          <div className="max-w-6xl mx-auto px-4">
            <div className="grid lg:grid-cols-12 gap-16 items-center">
              <div className="lg:col-span-5">
                <div className="relative group">
                  <div className="absolute -inset-1 bg-gradient-to-r from-orange-600 to-red-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
                  <img 
                    src="/profile-avatar.jpg" 
                    alt="Arif Fazil" 
                    className="relative w-full rounded-2xl grayscale hover:grayscale-0 transition-all duration-700 border border-gray-800"
                  />
                </div>
              </div>
              <div className="lg:col-span-7">
                <Badge className="bg-orange-500/10 text-orange-500 border-orange-500/20 mb-6">THE ARCHITECT</Badge>
                <h2 className="text-4xl font-bold mb-8">Subsurface Logic × AI Conscience</h2>
                
                <div className="space-y-10">
                  <div className="flex gap-6">
                    <div className="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center flex-shrink-0 border border-red-500/20">
                      <Shield className="w-6 h-6 text-red-500" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white mb-2 underline decoration-red-500/30 underline-offset-8">Constitutional AI</h3>
                      <p className="text-gray-400 leading-relaxed">Developing runtime enforcement layers that prevent AGI from violating physical and ethical invariant boundaries.</p>
                    </div>
                  </div>

                  <div className="flex gap-6">
                    <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center flex-shrink-0 border border-amber-500/20">
                      <Globe className="w-6 h-6 text-amber-500" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white mb-2 underline decoration-amber-500/30 underline-offset-8">Frontier Exploration</h3>
                      <p className="text-gray-400 leading-relaxed">Reading seismic signals to map the earth's history. Applying Bayesian uncertainty to multi-billion dollar decisions.</p>
                    </div>
                  </div>

                  <div className="flex gap-6">
                    <div className="w-12 h-12 rounded-xl bg-cyan-500/10 flex items-center justify-center flex-shrink-0 border border-cyan-500/20">
                      <Cpu className="w-6 h-6 text-cyan-500" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white mb-2 underline decoration-cyan-500/30 underline-offset-8">The Trinity Engine</h3>
                      <p className="text-gray-400 leading-relaxed">Synthesizing Logic (AGI), Safety (ASI), and Sovereignty (APEX) into a unified metabolic protocol.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 13 Floors Section */}
        <section id="floors" className="py-32 relative bg-[#0d0d0d]">
          <div className="max-w-6xl mx-auto px-4 text-center">
            <Badge variant="outline" className="mb-8 border-gray-700 text-gray-400 tracking-[0.3em] font-mono">13_CONSTITUTIONAL_FLOORS</Badge>
            <h2 className="text-5xl font-bold mb-6">The Immutable Anvil</h2>
            <p className="text-gray-400 max-w-2xl mx-auto mb-20 text-lg">
              Every decision produced by arifOS must pass through 13 floors of validation. 
              Violation of a Hard Floor results in immediate system <span className="text-red-500 font-mono">VOID</span>.
            </p>

            {/* Floors Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
              {FLOORS.map((floor, index) => (
                <Tooltip key={floor.id}>
                  <TooltipTrigger asChild>
                    <div 
                      className="group relative p-6 rounded-2xl border border-gray-800 bg-black/40 hover:border-orange-500/40 hover:bg-orange-500/5 transition-all cursor-crosshair h-full flex flex-col items-center justify-center text-center"
                    >
                      <span className="text-[10px] font-mono text-gray-600 mb-2">{floor.id}</span>
                      <p className="text-sm font-bold text-white mb-2">{floor.name}</p>
                      <Badge variant="outline" className="text-[9px] border-gray-800 text-gray-500 group-hover:border-orange-500/30 group-hover:text-orange-400">
                        {floor.judge}
                      </Badge>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="top" className="bg-black border-gray-800 text-white max-w-xs">
                    <p className="text-xs font-bold text-orange-400 mb-1">{floor.name}</p>
                    <p className="text-[10px] leading-relaxed italic">{floor.desc}</p>
                  </TooltipContent>
                </Tooltip>
              ))}
            </div>

            {/* Visual Alignment */}
            <div className="mt-24 rounded-3xl overflow-hidden grayscale opacity-50 hover:grayscale-0 hover:opacity-100 transition-all duration-1000 border border-gray-800">
              <img 
                src="/constitutional-floors.jpg" 
                alt="13 Constitutional Floors Diagram" 
                className="w-full h-80 object-cover"
              />
            </div>
          </div>
        </section>

        {/* Call to Action Section */}
        <section className="py-40 relative overflow-hidden text-center bg-black">
          <div className="max-w-2xl mx-auto px-4 relative z-10">
            <h2 className="text-4xl md:text-5xl font-bold mb-8">Build with Conscience</h2>
            <p className="text-gray-500 mb-12 text-lg">
              The tools are free. The audit is permanent. The mission is essential.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
              <a href="https://arif-fazil.com/mcp" className="w-full sm:w-auto">
                <Button className="w-full bg-red-600 hover:bg-red-500 text-white px-10 py-7 text-sm font-bold tracking-widest uppercase">
                  Access Portal
                </Button>
              </a>
            </div>
          </div>
          
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-orange-600/10 blur-[120px] rounded-full pointer-events-none" />
        </section>

        {/* Footer */}
        <footer className="py-20 border-t border-gray-900 bg-black">
          <div className="max-w-6xl mx-auto px-4 text-center">
            <div className="flex items-center justify-center gap-10 mb-12">
              <span className="text-2xl font-light text-cyan-800" style={{ fontFamily: 'serif' }}>△</span>
              <span className="text-2xl font-light text-red-900" style={{ fontFamily: 'serif' }}>Ω</span>
              <span className="text-2xl font-light text-amber-900" style={{ fontFamily: 'serif' }}>Ψ</span>
            </div>
            
            <p className="text-3xl font-black mb-1 tracking-widest leading-none">DITEMPA BUKAN DIBERI</p>
            <p className="text-[10px] text-gray-600 tracking-[0.8em] font-mono mb-12 uppercase">Forged, Not Given</p>
            
            <div className="flex items-center justify-center gap-8 mb-12">
              <a href="https://github.com/ariffazil" className="text-gray-500 hover:text-white transition-colors">
                <Github className="w-6 h-6" />
              </a>
              <a href="https://linkedin.com/in/arif-fazil" className="text-gray-500 hover:text-white transition-colors">
                <Linkedin className="w-6 h-6" />
              </a>
              <a href="https://x.com/ArifFazil90" className="text-gray-500 hover:text-white transition-colors">
                <Twitter className="w-6 h-6" />
              </a>
              <a href="mailto:arifbfazil@gmail.com" className="text-gray-500 hover:text-white transition-colors">
                <Mail className="w-6 h-6" />
              </a>
            </div>

            <Separator className="bg-gray-900 mb-12" />

            <div className="flex flex-col items-center gap-4 text-[10px] text-gray-700 uppercase tracking-widest">
              <span>Muhammad Arif bin Fazil · arifOS v55.1</span>
              <span>Penang, Malaysia · © 2026</span>
            </div>
          </div>
        </footer>
      </div>
    </TooltipProvider>
  );
}

export default App;
