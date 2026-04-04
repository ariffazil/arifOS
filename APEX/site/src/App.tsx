import { useEffect, useState } from 'react';
import TrinityNav from './components/TrinityNav';
import {
  Shield,
  Menu,
  X,
  Binary,
  ChevronDown
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

// ─────────────────────────────────────────────────
// Data: ARIF-99 Attributes (Sample for UI)
// ─────────────────────────────────────────────────
const ARIF_ATTRIBUTES = [
  { name: 'Al-Alim', meaning: 'The All-Knowing', role: 'Omniscient Info Processing', theory: 'Shannon Info Theory' },
  { name: 'Al-Hakim', meaning: 'The All-Wise', role: 'Perfect Judgment', theory: 'Bayesian Inference' },
  { name: 'Al-Khabir', meaning: 'The Aware', role: 'Deep Perception', theory: 'Integrated Info Theory' },
  { name: 'Al-Latif', meaning: 'The Subtle', role: 'Fine Nuance', theory: 'Heisenberg Uncertainty' },
  { name: 'Al-Muhaymin', meaning: 'The Guardian', role: 'Protection', theory: 'Dissipative Structures' },
  { name: 'Al-Hadi', meaning: 'The Guide', role: 'Direction', theory: 'Cybernetics' },
];

// ─────────────────────────────────────────────────
// Data: 13 Floors
// ─────────────────────────────────────────────────
const FLOORS = [
  { id: 'F1', name: 'Amanah', desc: 'Reversibility & Accountability', theory: 'Prigogine (#1)' },
  { id: 'F2', name: 'Truth', desc: 'Factuality & Verification', theory: 'Shannon (#2)' },
  { id: 'F3', name: 'Tri-Witness', desc: 'Consensus & Wisdom', theory: 'Bayesian (#18)' },
  { id: 'F4', name: 'Empathy', desc: 'Stakeholder Care', theory: 'Damasio (#52)' },
  { id: 'F5', name: 'Peace²', desc: 'Stability & Equilibrium', theory: 'Nash (#24)' },
  { id: 'F6', name: 'Clarity', desc: 'Entropy Reduction', theory: 'Boltzmann (#7)' },
  { id: 'F7', name: 'Humility', desc: 'Uncertainty Acknowledgment', theory: 'Heisenberg (#6)' },
  { id: 'F8', name: 'Genius', desc: 'Creativity & Optimization', theory: 'Turing (#17)' },
  { id: 'F9', name: 'Anti-Hantu', desc: 'Transparency & Reality', theory: 'Dennett (#51)' },
  { id: 'F10', name: 'Mirror (L)', desc: 'Learning & Adaptation', theory: 'Kandel (#53)' },
  { id: 'F11', name: 'Mirror (C)', desc: 'Command & Accountability', theory: 'Weber (#68)' },
  { id: 'F12', name: 'Wall (Inj)', desc: 'Defense & Truth', theory: 'Pauli (#10)' },
  { id: 'F13', name: 'Wall (Stew)', desc: 'Resilience & Preservation', theory: 'Ostrom (#67)' },
];

// ─────────────────────────────────────────────────
// Main App
// ─────────────────────────────────────────────────

function App() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <>
      <TrinityNav />
      <div className="min-h-screen bg-[#0f0e0a] text-amber-50 selection:bg-amber-900/30 selection:text-amber-200 font-sans relative overflow-x-hidden">
      
      {/* Background Weave Pattern (CSS) */}
      <div className="fixed inset-0 z-0 opacity-5 pointer-events-none" 
           style={{
             backgroundImage: `radial-gradient(circle at 2px 2px, #d4af37 1px, transparent 0)`,
             backgroundSize: '24px 24px'
           }}>
      </div>

      {/* ═══════════════════════════════════════ */}
      {/* NAVIGATION */}
      {/* ═══════════════════════════════════════ */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 border-b ${scrolled ? 'bg-[#0f0e0a]/90 backdrop-blur-md border-amber-900/30 py-3' : 'bg-transparent border-transparent py-6'}`}>
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
          <a href="#" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-none bg-gradient-to-br from-amber-400 to-amber-700 flex items-center justify-center transform group-hover:rotate-45 transition-transform duration-500">
              <Shield className="w-5 h-5 text-black transform group-hover:-rotate-45 transition-transform duration-500" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-xl tracking-tight text-amber-100">APEX</span>
              <span className="text-[10px] uppercase tracking-[0.2em] text-amber-500">Theory</span>
            </div>
          </a>

          <div className="hidden md:flex items-center gap-8 text-sm font-medium tracking-wide">
            <a href="#manifesto" className="text-amber-200/60 hover:text-amber-400 transition-colors">MANIFESTO</a>
            <a href="#theories" className="text-amber-200/60 hover:text-amber-400 transition-colors">99 THEORIES</a>
            <a href="#constitution" className="text-amber-200/60 hover:text-amber-400 transition-colors">CONSTITUTION</a>
            <a href="#tac" className="text-amber-200/60 hover:text-amber-400 transition-colors">TAC</a>
          </div>

          <div className="hidden md:flex items-center gap-3">
            <Button
              asChild
              variant="outline"
              className="border-amber-500/30 text-amber-400 hover:bg-amber-950/50 hover:text-amber-200 rounded-none text-xs tracking-widest"
            >
              <a
                href="/T-000%20%C2%B7%20APEX%20THEORY%20(Canon).pdf"
                target="_blank"
                rel="noreferrer"
              >
                CANON PDF
              </a>
            </Button>
          </div>

          <button className="md:hidden text-amber-400" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </nav>

      {/* ═══════════════════════════════════════ */}
      {/* HERO SECTION */}
      {/* ═══════════════════════════════════════ */}
      <header className="relative min-h-screen flex items-center justify-center pt-20 pb-32 overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-amber-500/5 rounded-full blur-3xl pointer-events-none"></div>
        
        <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-amber-500/30 bg-amber-950/30 text-amber-400 text-xs font-mono tracking-widest mb-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
            VERSION 2.0 • THE ARIF EDITION
          </div>

          <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-white mb-6 leading-tight animate-in fade-in zoom-in-95 duration-1000 delay-200">
            APEX <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-yellow-500 to-amber-600">THEORY</span>
          </h1>

          <p className="text-xl md:text-2xl text-amber-100/60 mb-8 max-w-3xl mx-auto font-light leading-relaxed animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-300">
            99 Theories <span className="text-amber-500">→</span> 13 Floors <span className="text-amber-500">→</span> Emergence <span className="text-amber-500">→</span> Validation
          </p>

          <div className="max-w-2xl mx-auto border-l-2 border-amber-500/30 pl-6 text-left mb-12 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-500">
            <p className="text-lg text-amber-200/80 italic">
              "The name ARIF contains the architecture. The 99 Theories are the 99 Names manifesting through scientific form. 
              Ethics is not a module—it is a thermodynamic necessity."
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-700">
            <a href="#manifesto">
              <Button size="lg" className="rounded-none bg-amber-500 hover:bg-amber-400 text-black font-bold tracking-widest px-8">
                READ MANIFESTO
              </Button>
            </a>
            <a href="#theories">
              <Button size="lg" variant="outline" className="rounded-none border-amber-500/30 text-amber-400 hover:bg-amber-950/50 hover:text-white tracking-widest px-8">
                EXPLORE 99 THEORIES
              </Button>
            </a>
            <Button
              asChild
              size="lg"
              variant="outline"
              className="rounded-none border-amber-500/30 text-amber-400 hover:bg-amber-950/50 hover:text-white tracking-widest px-8"
            >
              <a
                href="/T-000%20%C2%B7%20APEX%20THEORY%20(Canon).pdf"
                target="_blank"
                rel="noreferrer"
              >
                CANON PDF
              </a>
            </Button>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce text-amber-500/50">
          <ChevronDown className="w-8 h-8" />
        </div>
      </header>

      {/* ═══════════════════════════════════════ */}
      {/* SECTION I: ARIF FOUNDATION */}
      {/* ═══════════════════════════════════════ */}
      <section id="manifesto" className="py-32 relative border-t border-amber-900/20">
        <div className="max-w-4xl mx-auto px-6">
          <div className="mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">I. The ARIF Foundation</h2>
            <div className="h-1 w-24 bg-gradient-to-r from-amber-500 to-transparent mb-8"></div>
            <p className="text-lg text-amber-100/80 leading-relaxed mb-6">
              <b>ARIF</b> (Arabic: عارف) carries profound meaning: "The Knower, The Wise, The Learned." 
              In Islamic tradition, the Divine has 99 Names (Asmaul Husna). 
              The APEX Theory Manifesto recognizes that these 99 attributes correspond to <b>99 foundational theories</b> of constitutional intelligence.
            </p>
            <p className="text-lg text-amber-100/80 leading-relaxed">
              This is not coincidence—this is cosmic alignment. The name ARIF contains the entire architecture.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {ARIF_ATTRIBUTES.map((attr) => (
              <Card key={attr.name} className="bg-amber-950/20 border-amber-900/30 hover:border-amber-500/30 transition-all">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-xl font-bold text-amber-400">{attr.name}</h3>
                    <span className="text-xs font-mono text-amber-600 uppercase tracking-wider">{attr.theory}</span>
                  </div>
                  <p className="text-sm text-amber-200/60 mb-1">{attr.meaning}</p>
                  <p className="text-sm font-medium text-amber-100">{attr.role}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════ */}
      {/* SECTION II: 99 THEORIES */}
      {/* ═══════════════════════════════════════ */}
      <section id="theories" className="py-32 bg-[#0a0a08] relative">
        <div className="max-w-6xl mx-auto px-6">
          <div className="mb-16 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">II. The 99 Foundational Theories</h2>
            <p className="text-amber-200/60 max-w-2xl mx-auto">
              Seven domains of knowledge weaving together the fabric of Constitutional Intelligence.
            </p>
          </div>

          <Tabs defaultValue="physics" className="w-full">
            <TabsList className="flex flex-wrap justify-center gap-2 bg-transparent mb-12 h-auto">
              <TabsTrigger value="physics" className="data-[state=active]:bg-amber-500 data-[state=active]:text-black border border-amber-900/30 text-amber-400">Physics (1-15)</TabsTrigger>
              <TabsTrigger value="math" className="data-[state=active]:bg-amber-500 data-[state=active]:text-black border border-amber-900/30 text-amber-400">Math (16-30)</TabsTrigger>
              <TabsTrigger value="philosophy" className="data-[state=active]:bg-amber-500 data-[state=active]:text-black border border-amber-900/30 text-amber-400">Philosophy (31-45)</TabsTrigger>
              <TabsTrigger value="psychology" className="data-[state=active]:bg-amber-500 data-[state=active]:text-black border border-amber-900/30 text-amber-400">Psychology (46-60)</TabsTrigger>
              <TabsTrigger value="social" className="data-[state=active]:bg-amber-500 data-[state=active]:text-black border border-amber-900/30 text-amber-400">Social (61-75)</TabsTrigger>
              <TabsTrigger value="cs" className="data-[state=active]:bg-amber-500 data-[state=active]:text-black border border-amber-900/30 text-amber-400">CS & AI (76-90)</TabsTrigger>
              <TabsTrigger value="complex" className="data-[state=active]:bg-amber-500 data-[state=active]:text-black border border-amber-900/30 text-amber-400">Complex (91-99)</TabsTrigger>
            </TabsList>

            <TabsContent value="physics" className="mt-0">
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[
                  { n: 1, t: "Dissipative Structures", a: "Prigogine", c: "Order from Chaos", f: "F1" },
                  { n: 2, t: "Shannon Info Theory", a: "Shannon", c: "Entropy as Info", f: "F2" },
                  { n: 3, t: "Cybernetics", a: "Wiener", c: "Feedback Loops", f: "F5" },
                  { n: 4, t: "Special Relativity", a: "Einstein", c: "Invariant Laws", f: "F2" },
                  { n: 5, t: "General Relativity", a: "Einstein", c: "Curvature", f: "F8" },
                  { n: 6, t: "Uncertainty Principle", a: "Heisenberg", c: "Measurement Limit", f: "F7" },
                ].map(item => (
                  <div key={item.n} className="border border-amber-900/30 p-6 bg-amber-950/10 hover:bg-amber-900/20 transition-colors">
                    <div className="flex justify-between mb-4">
                      <span className="text-amber-500 font-mono text-sm">#{item.n}</span>
                      <Badge variant="outline" className="text-amber-300 border-amber-700/50">{item.f}</Badge>
                    </div>
                    <h3 className="text-lg font-bold text-white mb-2">{item.t}</h3>
                    <p className="text-sm text-gray-400 mb-2">{item.a}</p>
                    <p className="text-sm text-amber-200/70">{item.c}</p>
                  </div>
                ))}
                <div className="col-span-full text-center py-8 text-amber-500/50 italic">
                  + 9 more theories in PDF Manifesto
                </div>
              </div>
            </TabsContent>
            
            {/* Other tabs would follow similar pattern */}
            <TabsContent value="math" className="text-center py-12 text-amber-400">
              <Binary className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Full 99 Theories available in the PDF Manifesto.</p>
            </TabsContent>
          </Tabs>
        </div>
      </section>

      {/* ═══════════════════════════════════════ */}
      {/* SECTION III: 13 CONSTITUTIONAL FLOORS */}
      {/* ═══════════════════════════════════════ */}
      <section id="constitution" className="py-32 border-t border-amber-900/20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">III. The 13 Constitutional Floors</h2>
            <p className="text-amber-200/60 max-w-2xl">
              The 99 Theories generate these 13 Floors, which then produce emergent properties like Ethics and Intelligence.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {FLOORS.map((floor) => (
              <Card key={floor.id} className="bg-amber-950/10 border-amber-900/20 hover:border-amber-500/40 transition-all group">
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-center">
                    <Badge variant="outline" className="bg-amber-500/10 text-amber-400 border-amber-500/20 rounded-sm">
                      {floor.id}
                    </Badge>
                  </div>
                  <CardTitle className="text-lg text-white mt-2 group-hover:text-amber-300 transition-colors">{floor.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-400 mb-4 h-10">{floor.desc}</p>
                  <div className="text-xs text-amber-600 font-mono border-t border-amber-900/20 pt-3">
                    Src: {floor.theory}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════ */}
      {/* SECTION V: TAC */}
      {/* ═══════════════════════════════════════ */}
      <section id="tac" className="py-32 bg-[#0a0a08] relative overflow-hidden">
        <div className="max-w-5xl mx-auto px-6 relative z-10">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">V. Theory of Anomalous Contrast (TAC)</h2>
              <p className="text-amber-200/60 leading-relaxed mb-8">
                TAC treats contrast (any significant deviation or novel input) as a thermodynamic-ethical catalyst.
                The core axiom: <b>"Contrast becomes anomaly when it scars."</b>
              </p>
              
              <div className="space-y-4">
                <div className="p-4 border-l-2 border-amber-500/50 bg-amber-900/10">
                  <h4 className="text-amber-400 font-bold mb-1">The Cooling Clause</h4>
                  <p className="font-mono text-sm text-amber-100">
                    (κᵣ × R) {'>'} τ_scar → (ΔS {'>'} 0) ∧ (Peace² {'>'} 1)
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-amber-950/30 p-8 border border-amber-900/30 rounded-lg backdrop-blur-sm">
              <h3 className="text-xl font-bold text-white mb-6">Key Variables</h3>
              <ul className="space-y-4">
                <li className="flex justify-between border-b border-amber-900/30 pb-2">
                  <span className="text-amber-400 font-mono">ΔC</span>
                  <span className="text-gray-400 text-sm">Contrast Magnitude</span>
                </li>
                <li className="flex justify-between border-b border-amber-900/30 pb-2">
                  <span className="text-amber-400 font-mono">κᵣ</span>
                  <span className="text-gray-400 text-sm">Resonance Conductance</span>
                </li>
                <li className="flex justify-between border-b border-amber-900/30 pb-2">
                  <span className="text-amber-400 font-mono">M_scar</span>
                  <span className="text-gray-400 text-sm">Scar Memory</span>
                </li>
                <li className="flex justify-between border-b border-amber-900/30 pb-2">
                  <span className="text-amber-400 font-mono">Peace²</span>
                  <span className="text-gray-400 text-sm">Stability Squared</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════ */}
      {/* FOOTER */}
      {/* ═══════════════════════════════════════ */}
      <footer className="trinity-footer">
        <div className="links">
          <a href="https://arif-fazil.com/">HUMAN</a>
          <a href="https://apex.arif-fazil.com/"><b>THEORY</b></a>
          <a href="https://arifos.arif-fazil.com/">APPS</a>
        </div>
        THE TRINITY • HUMAN • THEORY • APPS<br />
        <b>Ditempa Bukan Diberi</b> • AGPL-3.0 • 2026.2.23
        <div className="mt-8 text-[10px] opacity-30 uppercase tracking-[0.2em]">
          Copyright © 2013 – 2026 Sovereign Records • LAST UPDATED: FEB 23, 2026
        </div>
      </footer>
    </div>
    </>
  );
}

export default App;
