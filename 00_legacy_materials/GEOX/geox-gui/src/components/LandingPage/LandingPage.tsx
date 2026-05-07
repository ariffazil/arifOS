/**
 * GEOX Landing Page — Three Layers: Product / Workspaces / Platform
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * Layer 1: Product — Decision cockpit for exploration teams
 * Layer 2: Workspaces — Seven Sovereign Dimensions
 * Layer 3: Platform — MCP server, tools, resources for developers
 */

import React, { useState, useEffect } from 'react';
import {
  Globe, Activity, AlignLeft, Shield,
  ChevronRight, ArrowRight,
  Zap, BarChart3,
  Cpu, MapPin, Gauge,
  FileSearch, Layers, Database, Terminal,
  Box, Workflow, CpuIcon, Map, Clock
} from 'lucide-react';
import { useGEOXStore } from '../../store/geoxStore';
import './LandingPage.css';

interface LandingPageProps {
  onEnterCockpit: () => void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Layer 1: PRODUCT — Hero + Outcomes
// ═══════════════════════════════════════════════════════════════════════════════

const Hero: React.FC<{ onEnterCockpit: () => void }> = ({ onEnterCockpit }) => {
  const geoxConnected = useGEOXStore((state) => state.geoxConnected);

  return (
    <section className="hero-section">
      <div className="hero-bg-gradient" />
      <div className="hero-glow" />
      <div className="hero-grid-pattern" />

      <div className="relative z-10 text-center max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-6">
          <div className={`w-2 h-2 rounded-full ${geoxConnected ? 'bg-green-500 animate-pulse' : 'bg-amber-500'}`} />
          <span className="text-xs font-mono text-slate-400 uppercase tracking-widest">
            {geoxConnected ? 'Live Pilot: Malay Basin' : 'Connecting...'}
          </span>
        </div>

        <h1 className="text-5xl md:text-7xl font-black text-white mb-6 uppercase tracking-tighter">
          GEOX <span className="text-blue-400">Physics9</span>
        </h1>

        <p className="text-lg text-slate-300 max-w-2xl mx-auto mb-10 leading-relaxed">
          Physics9 Intelligence Core. Seven essential tools. Seven dimensions.
          Constitutional governance F1-F13. Theory of Anomalous Contrast (ToAC) at the center.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={onEnterCockpit}
            className="group flex items-center gap-3 px-8 py-4 bg-blue-500 hover:bg-blue-400 text-white font-bold rounded-xl transition-all shadow-[0_0_30px_rgba(59,130,246,0.3)] hover:shadow-[0_0_40px_rgba(59,130,246,0.5)] hover:-translate-y-0.5"
          >
            <Globe className="w-5 h-5" />
            Enter Cockpit
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>

          <a href="#workspaces" className="flex items-center gap-2 px-6 py-4 bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white border border-white/10 rounded-xl transition-all">
            <Layers className="w-5 h-5" />
            Seven Dimensions
          </a>
        </div>

        <p className="mt-12 text-xs font-mono text-slate-600 tracking-[0.3em] uppercase">
          DITEMPA BUKAN DIBERI — Forged, Not Given
        </p>
      </div>

      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-slate-500">
        <span className="text-[10px] uppercase tracking-widest">Explore</span>
        <ChevronRight className="w-4 h-4 rotate-90 animate-bounce" />
      </div>
    </section>
  );
};

const OutcomesSection: React.FC = () => (
  <section className="py-20 px-6 bg-slate-900 border-y border-slate-800">
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">From data to decision</h2>
        <p className="text-slate-400 max-w-2xl mx-auto">
          GEOX keeps geoscience workflows auditable from raw data to final verdict.
          No black boxes. No unexplained confidence.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {[
          { icon: FileSearch, title: 'Interpret', desc: 'Load seismic, well logs, and basin data. Every interpretation is tied to physical parameters you can verify.' },
          { icon: BarChart3, title: 'Compare', desc: 'Test multiple scenarios side-by-side. Compare reserves estimates, risk profiles, and structural hypotheses with quantitative deltas.' },
          { icon: Shield, title: 'Govern', desc: 'Every output is scored for feasibility, uncertainty, and risk. High-confidence claims proceed. Uncertain claims trigger hold states.' },
        ].map((item, idx) => (
          <div key={item.title} className="relative p-6 rounded-2xl bg-slate-950 border border-slate-800">
            <div className="absolute -top-3 left-6 px-2 py-1 bg-slate-900 text-xs font-mono text-slate-500 rounded">Step {idx + 1}</div>
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center mb-4">
              <item.icon className="w-6 h-6 text-blue-400" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
            <p className="text-slate-400 text-sm leading-relaxed">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

// ═══════════════════════════════════════════════════════════════════════════════
// Layer 2: WORKSPACES — Seven Dimensions
// ═══════════════════════════════════════════════════════════════════════════════

const APPS = [
  {
    icon: Gauge,
    id: 'prospect-ui',
    title: 'Prospect UI',
    subtitle: 'Risk & Discovery',
    description: 'Interactive Theory of Anomalous Contrast (ToAC) calculator for exploration play fairways. Feasibility scoring grounded in physics.',
    status: 'live',
    color: 'amber',
  },
  {
    icon: AlignLeft,
    id: 'well-desk',
    title: 'Well Desk',
    subtitle: 'Log Analysis',
    description: 'Borehole Intelligence. High-fidelity log analysis, petrophysics, and stratigraphic markers (Truth Witness).',
    status: 'live',
    color: 'cyan',
  },
  {
    icon: Activity,
    id: 'earth-volume',
    title: 'Earth Volume',
    subtitle: '3D Spatial Volumetrics',
    description: 'Seismic interpretation with constitutional overlays and volumetric synthesis. Full audit trail for every interpretation.',
    status: 'live',
    color: 'violet',
  },
  {
    icon: Globe,
    id: 'section-canvas',
    title: 'Section Canvas',
    subtitle: 'Stratigraphic Continuity',
    description: 'Interactive geologic cross-sections and 2D correlation auditing. Verified stratigraphic continuity across blocks.',
    status: 'live',
    color: 'blue',
  },
  {
    icon: Clock,
    id: 'chronos-history',
    title: 'Chronos History',
    subtitle: 'Play Cycles & Timing',
    description: '4D basin evolution analysis and hydrocarbon charge alignment verification. Temporal play cycle synchronization.',
    status: 'live',
    color: 'rose',
  },
  {
    icon: Shield,
    id: 'judge-console',
    title: 'Judge Console',
    subtitle: 'Governance & Audit',
    description: '888_JUDGE authoritative console for physical state verification and lock management. Constitutional gatekeeper.',
    status: 'live',
    color: 'slate',
  },
  {
    icon: MapPin,
    id: 'map-layer',
    title: 'Map Layer',
    subtitle: 'Transversal Geospatial',
    description: 'Unified map view for all dimensional data via standardized CRS synchronization. Transversal spatial fabric.',
    status: 'live',
    color: 'green',
  },
];

const WorkspacesSection: React.FC = () => (
  <section id="workspaces" className="py-20 px-6 bg-slate-950">
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Seven Sovereign Dimensions</h2>
        <p className="text-slate-400 max-w-2xl mx-auto">
          Deterministic subsurface dimensions that reside inside MCP hosts or standalone cockpits.
          Each dimension routes through AC_Risk for constitutional governance.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        {APPS.map((app) => (
          <div
            key={app.id}
            className="group p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-all"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 rounded-xl bg-slate-800">
                <app.icon className="w-6 h-6 text-blue-400" />
              </div>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border bg-green-500/10 text-green-400 border-green-500/30">
                {app.status}
              </span>
            </div>
            <h3 className="text-lg font-bold text-white mb-1">{app.title}</h3>
            <p className="text-xs font-mono text-slate-500 mb-3 uppercase tracking-wider">{app.subtitle}</p>
            <p className="text-sm text-slate-400 leading-relaxed">{app.description}</p>
          </div>
        ))}
      </div>

      {/* Hybrid */}
      <div className="p-8 rounded-2xl bg-slate-900 border border-slate-800">
        <div className="flex flex-col md:flex-row gap-8 items-center">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-lg bg-violet-500/10">
                <Layers className="w-5 h-5 text-violet-400" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Hybrid WebMCP</h3>
                <p className="text-sm text-slate-500">Browser + MCP bridge · Embed · Integrate</p>
              </div>
            </div>
            <p className="text-slate-400 mb-4 text-sm leading-relaxed">
              Browser apps that also speak MCP, acting as both UI and server client.
              Use WebMCP to plug GEOX tools into other systems or drive GEOX from external AI.
            </p>
          </div>
          <div className="flex-shrink-0 w-full md:w-64 p-4 rounded-xl bg-slate-950/50 border border-slate-800 text-center">
            <Cpu className="w-8 h-8 text-violet-400 mx-auto mb-3" />
            <div className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">Status</div>
            <div className="text-sm font-bold text-green-400 uppercase">Gateway Active</div>
          </div>
        </div>
      </div>
    </div>
  </section>
);

// ═══════════════════════════════════════════════════════════════════════════════
// Layer 3: PLATFORM — MCP Server, Tools, Resources, Skills
// ═══════════════════════════════════════════════════════════════════════════════

const PlatformSection: React.FC = () => {
  const metaLinks = useGEOXStore((state) => state.metaLinks);

  return (
    <section className="py-20 px-6 bg-slate-900 border-y border-slate-800">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">GEOX Platform Architecture</h2>
          <p className="text-slate-400 max-w-2xl mx-auto">
            The subsurface intelligence layer. Standardized interfaces for tools, resources, and constitutional governance.
          </p>
        </div>

        <div className="mb-12 p-8 rounded-3xl bg-slate-950 border border-slate-800 shadow-2xl">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
            <div className="text-center p-6 rounded-2xl bg-slate-900 border border-slate-800">
              <div className="flex justify-center gap-3 mb-4">
                <Box className="w-6 h-6 text-amber-400" />
                <Globe className="w-6 h-6 text-blue-400" />
              </div>
              <h4 className="font-bold text-white mb-2">Interfaces</h4>
              <p className="text-xs text-slate-500">MCP Apps · Web Cockpit · Hybrid Bridge</p>
            </div>

            <div className="relative">
              <div className="p-8 rounded-2xl bg-blue-500/10 border border-blue-500/30 text-center relative z-10">
                <CpuIcon className="w-8 h-8 text-blue-400 mx-auto mb-4" />
                <h4 className="font-bold text-white mb-2 uppercase tracking-widest">Dimension Core</h4>
                <p className="text-xs text-slate-400">Physics9 · F1-F13 Governance · Evidence Hooks</p>
              </div>
              <div className="absolute top-1/2 left-0 w-full h-px bg-blue-500/20 -translate-y-1/2 hidden md:block" />
            </div>

            <div className="text-center p-6 rounded-2xl bg-slate-900 border border-slate-800">
              <Database className="w-6 h-6 text-slate-400 mx-auto mb-4" />
              <h4 className="font-bold text-white mb-2">Data Fabric</h4>
              <p className="text-xs text-slate-500">GEO-FABRIC · CRS Registry · Subsurface Vault</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <PlatformCard
            icon={Terminal}
            title="MCP Toolset"
            description="Dimension-first tools for PROSPECT, WELL, SECTION, 3D, and 4D extraction and analysis. Governed by A2A protocols."
            link="arifOS Registry"
            href={metaLinks.find(l => l.name === 'arifOS MCP')?.url || '#'}
          />
          <PlatformCard
            icon={Map}
            title="GEO-FABRIC"
            description="Universal spatial anchor. Cross-dimensional coordinate synchronization and truth-grounding in EPSG:4326."
            link="GeoVault Access"
            href={metaLinks.find(l => l.name === 'GeoVault')?.url || '#'}
          />
          <PlatformCard
            icon={Workflow}
            title="999_SEAL Protocol"
            description="The gold standard for production governance. Every claim must pass the Floor Enforcer and 888_JUDGE audit."
            link="Governance Wiki"
            href={metaLinks.find(l => l.name === 'Ω-Wiki')?.url || '#'}
          />
          <PlatformCard
            icon={Shield}
            title="AC_Risk Core"
            description="The Agent Control Plane for risk. Every model-driven interpretation is validated against known Physics9 deterministic laws."
            link="Platform Specs"
            href="#"
          />
        </div>
      </div>
    </section>
  );
};

const PlatformCard: React.FC<{ icon: any, title: string, description: string, link: string, href: string }> =
({ icon: Icon, title, description, link, href }) => (
  <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 hover:border-slate-700 transition-colors">
    <div className="flex items-center gap-3 mb-3">
      <div className="p-2 rounded-lg bg-slate-800">
        <Icon className="w-5 h-5 text-blue-400" />
      </div>
      <h3 className="font-bold text-white">{title}</h3>
    </div>
    <p className="text-sm text-slate-400 mb-4 leading-relaxed">{description}</p>
    <a
      href={href}
      target={href !== '#' ? "_blank" : undefined}
      rel={href !== '#' ? "noopener noreferrer" : undefined}
      className="inline-flex items-center gap-1 text-xs font-bold text-blue-400 hover:text-blue-300 uppercase tracking-widest"
    >
      {link} <ArrowRight className="w-3 h-3" />
    </a>
  </div>
);

// ═══════════════════════════════════════════════════════════════════════════════
// Tools & Skills Section
// ═══════════════════════════════════════════════════════════════════════════════

const ToolsSection: React.FC = () => (
  <section className="py-20 px-6 bg-slate-950">
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Sovereign Skills & Tools</h2>
        <p className="text-slate-400">Deterministic capabilities for AI-assisted subsurface appraisal.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Terminal className="w-5 h-5 text-blue-400" />
            Physics9 Tools (Automated)
          </h3>
          <div className="space-y-3">
            <ToolItem name="geox_judge_verdict" desc="Execute 888_JUDGE floor check for a prospect scenario." />
            <ToolItem name="acp_submit_proposal" desc="Submit interpretation to the Agent Control Plane." />
            <ToolItem name="geox_transform_crs" desc="Deterministic spatial transformation via GEO-FABRIC." />
            <ToolItem name="geox_get_well_logs" desc="Fetch high-fidelity log vectors for petrophysical tying." />
          </div>
        </div>

        <div>
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Workflow className="w-5 h-5 text-amber-400" />
            Governed Skills (A2A Swarm)
          </h3>
          <div className="space-y-3">
            <SkillItem name="999_SEAL Appraisal" desc="Chain: register → propose → converge → judge → SEAL." />
            <SkillItem name="Tri-Witness Validation" desc="Cross-check: (Petrophysics ↔ Geophysics ↔ Geology)." />
            <SkillItem name="F7 Humility Guard" desc="Automatically hold proposals exceeding ±15% uncertainty." />
            <SkillItem name="Anti-Hantu Grounding" desc="Detection and rejection of hallucinatory sentience claims." />
          </div>
        </div>
      </div>
    </div>
  </section>
);

const ToolItem: React.FC<{ name: string, desc: string }> = ({ name, desc }) => (
  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 group hover:border-blue-500/30 transition-colors">
    <code className="text-sm text-blue-400 font-mono">{name}</code>
    <p className="text-xs text-slate-500 mt-1">{desc}</p>
  </div>
);

const SkillItem: React.FC<{ name: string, desc: string }> = ({ name, desc }) => (
  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 group hover:border-amber-500/30 transition-colors">
    <div className="text-sm text-amber-400 font-medium">{name}</div>
    <p className="text-xs text-slate-500 mt-1">{desc}</p>
  </div>
);

// ═══════════════════════════════════════════════════════════════════════════════
// Evidence & Governance
// ═══════════════════════════════════════════════════════════════════════════════

const EvidenceSection: React.FC = () => (
  <section className="py-20 px-6 bg-gradient-to-b from-slate-900 to-slate-950">
    <div className="max-w-6xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 border border-green-500/30 mb-6">
            <Zap className="w-3 h-3 text-green-400" />
            <span className="text-xs font-bold text-green-400 uppercase tracking-wider">Live Pilot</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Proven in the Malay Basin</h2>
          <p className="text-slate-400 mb-6 leading-relaxed">
            GEOX is currently piloted on Malay Basin exploration data.
            The basin has produced 12+ billion barrels of oil equivalent across
            142 discovered fields.
          </p>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <div className="text-2xl font-black text-white">12.4</div>
              <div className="text-xs text-slate-500">Bnboe Recoverable</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <div className="text-2xl font-black text-white">142</div>
              <div className="text-xs text-slate-500">Fields Discovered</div>
            </div>
          </div>
        </div>
        <div className="relative">
          <div className="aspect-video rounded-3xl bg-slate-950 border border-slate-800 overflow-hidden relative shadow-2xl">
            <svg className="absolute inset-0 w-full h-full" viewBox="0 0 400 225">
              <polygon points="80,60 200,30 320,70 280,160 120,180 60,120" fill="rgba(59,130,246,0.1)" stroke="rgba(59,130,246,0.5)" strokeWidth="1.5" />
              <text x="200" y="115" textAnchor="middle" fill="rgba(255,255,255,0.4)" fontSize="8" fontFamily="monospace">Malay Basin Segment</text>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </section>
);

const GovernanceSection: React.FC = () => (
  <section className="py-20 px-6 bg-slate-950 border-t border-slate-900">
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-white mb-4">Governance & Constitution</h2>
        <p className="text-slate-400">F1-F13 authoritative constraints on every call.</p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        {[
          { id: 'F1', name: 'REVERSIBLE' },
          { id: 'F2', name: 'TRUTH' },
          { id: 'F4', name: 'CLARITY' },
          { id: 'F7', name: 'HUMILITY' },
          { id: 'F9', name: 'TRANSPARENT' },
          { id: 'F11', name: 'AUDITABLE' },
          { id: 'F13', name: 'SOVEREIGN' },
        ].map((floor) => (
          <div key={floor.id} className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 text-center">
            <div className="text-lg font-black text-white mb-1">{floor.id}</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-tighter">{floor.name}</div>
          </div>
        ))}
      </div>
    </div>
  </section>
);

// ═══════════════════════════════════════════════════════════════════════════════
// Footer
// ═══════════════════════════════════════════════════════════════════════════════

const Footer: React.FC = () => (
  <footer className="py-12 px-6 bg-slate-950 border-t border-slate-900">
    <div className="max-w-6xl mx-auto text-center">
      <div className="flex items-center justify-center gap-2 mb-4">
        <Globe className="w-5 h-5 text-blue-400" />
        <span className="font-black text-white">GEOX</span>
      </div>
      <p className="text-xs text-slate-600 font-mono mb-8 uppercase tracking-widest">
        DITEMPA BUKAN DIBERI · Forged, Not Given
      </p>
      <div className="pt-8 border-t border-slate-900 text-[10px] text-slate-700 font-mono">
        GEOX Earth Intelligence Core · 2026
      </div>
    </div>
  </footer>
);

// ═══════════════════════════════════════════════════════════════════════════════
// Main Landing Page
// ═══════════════════════════════════════════════════════════════════════════════

export const LandingPage: React.FC<LandingPageProps> = ({ onEnterCockpit }) => {
  const [showNav, setShowNav] = useState(false);

  useEffect(() => {
    const handleScroll = () => setShowNav(window.scrollY > 100);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-white selection:bg-blue-500/30">
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${showNav ? 'bg-slate-950/80 backdrop-blur border-b border-slate-800' : 'bg-transparent'}`}>
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Globe className="w-5 h-5 text-blue-400" />
            <span className="font-black text-sm tracking-tight">GEOX</span>
          </div>
          <button onClick={onEnterCockpit} className="flex items-center gap-2 px-4 py-1.5 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 text-xs font-bold rounded-lg border border-blue-500/30 transition-all">
            Enter Cockpit
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>
      </nav>

      <Hero onEnterCockpit={onEnterCockpit} />
      <OutcomesSection />
      <WorkspacesSection />
      <PlatformSection />
      <ToolsSection />
      <EvidenceSection />
      <GovernanceSection />
      <Footer />
    </div>
  );
};
