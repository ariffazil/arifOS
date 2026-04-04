import { useEffect, useState } from 'react';
import Layout from '@theme/Layout';
import TrinityNav from '../components/TrinityNav';

const FLOORS = [
  { id: 'F1', name: 'Amanah', desc: 'Sacred trust and irreversibility awareness. Cross the Rubicon with care.' },
  { id: 'F2', name: 'Truth', desc: 'Factual fidelity >= 0.99. Every claim grounded in multi-source evidence.' },
  { id: 'F3', name: 'Tri-Witness', desc: 'Consensus of Human, AI, and Earth (Evidence). Triple calibration.' },
  { id: 'F4', name: 'Clarity', desc: 'Entropy reduction. Intelligence is work that turns noise into structure.' },
  { id: 'F5', name: 'Peace', desc: 'Dynamic stability and safety margins. Non-adversarial coherence.' },
  { id: 'F6', name: 'Empathy', desc: 'Stakeholder protection threshold >= 0.95. Modeling the vector of harm.' },
  { id: 'F7', name: 'Humility', desc: 'Epistemic bounds. Acknowledging the 3-5% gap in all knowledge.' },
  { id: 'F8', name: 'Genius', desc: 'The coherence mirror: G = A x P x X x E^2. Wisdom is multiplicative.' },
  { id: 'F9', name: 'Anti-Hantu', desc: 'No personhood claims. Clean split between Being and Instrument.' },
  { id: 'F10', name: 'Ontology', desc: 'Permanent binary lock. AI is a tool, never a soul.' },
  { id: 'F11', name: 'Authority', desc: 'Sovereign command validation. All power derives from the mandate.' },
  { id: 'F12', name: 'Defense', desc: 'Adversarial injection resistance. The firewall between user and prompt.' },
  { id: 'F13', name: 'Sovereignty', desc: 'Human veto preserved. No irreversible authority transfer to AI.' },
];

const ENDPOINT_SURFACES = [
  {
    path: '/mcp',
    role: 'Public MCP contract',
    when: 'Use for model-agnostic MCP clients and keep all tool calls on this single surface.',
    includes: '11 mega-tools: init_anchor, arifOS_kernel, apex_soul, vault_ledger, agi_mind, asi_heart, engineering_memory, physics_reality, math_estimator, code_engine, architect_registry.',
  },
  {
    path: '/health',
    role: 'Operator health surface',
    when: 'Use for runtime liveness, version, and capability checks.',
    includes: 'Health snapshot, version, transport, and capability map summary.',
  },
  {
    path: '/dashboard/',
    role: 'Observability surface',
    when: 'Use for human monitoring, verdict visibility, and trace inspection.',
    includes: 'APEX dashboard and live governance telemetry.',
  },
];

export default function Home() {
  const [health, setHealth] = useState({ status: 'loading', version: '' });

  useEffect(() => {
    fetch('https://arifosmcp.arif-fazil.com/health')
      .then(r => r.json())
      .then(data => setHealth({ status: data.status || 'healthy', version: data.version || '2026.03.22' }))
      .catch(() => setHealth({ status: 'degraded', version: '-' }));
  }, []);

  return (
    <Layout title="arifOS - Constitutional Intelligence Kernel" description="Ditempa Bukan Diberi - The constitutional intelligence kernel that governs AI cognition via 13 mathematical floors.">
      <TrinityNav />

      {/* HERO */}
      <div className="hero hero--primary hero-polished">
        <div className="container">
          <h1 className="hero__title hero-title-polished">
            arif<span className="text-accent">OS</span>
          </h1>
          <p className="hero__subtitle hero-subtitle-polished">
            The System That Knows It Doesn't Know<br />
            <strong>Ditempa Bukan Diberi</strong> &mdash; Forged, Not Given
          </p>
          <div style={{ maxWidth: '600px', margin: '0 auto 1.5rem', opacity: 0.9 }}>
            arifOS is an open-source constitutional AI kernel that acts as a rigorous lie detector and safety firewall between language models and tools. It enforces 13 strict rules (Floors) to ensure truthfulness and protect against harmful actions.
          </div>
          <div style={{ marginTop: '1rem' }}>
            <img src="https://img.shields.io/pypi/v/arifos?color=3b82f6&label=version&style=flat-square" alt="PyPI version" />
          </div>

          <div className="hero-btn-row">
            <a href="#deploy" className="button button--lg hero-btn-primary">
              Deploy in 60 Seconds
            </a>
            <a href="/chatgpt" className="button button--lg hero-btn-secondary">
              Add to ChatGPT
            </a>
          </div>

          <div className="status-bar">
            <span>LIVE MCP ENDPOINT &rarr;</span>
            <code className="status-code">https://arifosmcp.arif-fazil.com</code>
            <span className="divider-pipe">|</span>
            <span className={`health-pulse ${health.status !== 'healthy' && health.status !== 'loading' ? 'degraded' : ''}`}></span>
            <span>STATUS:</span>
            <span className={`status-text ${health.status === 'healthy' || health.status === 'loading' ? 'status-healthy' : 'status-degraded'}`}>
              {health.status.toUpperCase()}{health.version && ` | v${health.version}`}
            </span>
          </div>

          <div style={{ marginTop: '1rem', fontSize: '0.9rem', opacity: 0.8 }}>
            <span style={{ marginRight: '8px' }}>🔍 How do we prove it is safe?</span>
            <a href="https://arifosmcp.arif-fazil.com/dashboard/" target="_blank" rel="noopener noreferrer" style={{ color: '#3b82f6', textDecoration: 'underline' }}>
              View the Live Constitutional Audit Dashboard
            </a>
          </div>
        </div>
      </div>

      {/* 13 FLOORS GRID */}
      <div className="floors-section">
        <div className="container">
          <h2 className="floors-heading">13 Constitutional Floors</h2>
          <div className="floors-grid">
            {FLOORS.map((floor) => (
              <div key={floor.id} className="floor-card">
                <div className="floor-id">{floor.id}</div>
                <h3 className="floor-name">{floor.name}</h3>
                <p className="floor-desc">{floor.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="endpoint-section">
        <div className="container">
          <h2 className="endpoint-heading">Endpoint Surface Contract</h2>
          <p className="endpoint-subhead">
            Pick one endpoint surface per session and keep all calls on that same surface.
          </p>
          <div className="endpoint-grid">
            {ENDPOINT_SURFACES.map((surface) => (
              <div key={surface.path} className="endpoint-card">
                <div className="endpoint-path">{surface.path}</div>
                <h3 className="endpoint-role">{surface.role}</h3>
                <p className="endpoint-line"><strong>Use when:</strong> {surface.when}</p>
                <p className="endpoint-line"><strong>Includes:</strong> {surface.includes}</p>
              </div>
            ))}
          </div>

          <div className="callflow-panel">
            <h3 className="callflow-heading">Recommended Public Flow</h3>
            <ol className="callflow-list">
              <li><code>bootstrap_identity</code> if you need explicit named onboarding.</li>
              <li><code>arifOS_kernel</code> for the main governed task path.</li>
              <li><code>search_reality</code>, <code>ingest_evidence</code>, <code>session_memory</code>, or <code>audit_rules</code> only when you need a focused support tool.</li>
              <li><code>check_vital</code> and <code>open_apex_dashboard</code> for operator visibility, not execution.</li>
            </ol>
          </div>
        </div>
      </div>

      {/* QUICK DEPLOY */}
      <div className="container">
        <div id="deploy" className="deploy-section">
          <h2 className="deploy-heading">Deploy or Connect in 60 Seconds</h2>
          <pre className="deploy-pre">
            <span className="code-comment"># Get the kernel</span>{'\n'}
            <span className="code-command">pip install</span> arifos{'\n'}{'\n'}
            <span className="code-comment"># Ignite canonical AAA MCP runtime (streamable HTTP)</span>{'\n'}
            <span className="code-command">python -m</span> arifosmcp.runtime http
          </pre>
          <p className="deploy-cta">
            <a href="/chatgpt" className="chatgpt-link">
              &rarr; Add arifOS as a Sovereign Connector in ChatGPT
            </a>
          </p>
          <p className="troubleshoot-note">
            Session terminated? Most cases come from mixing health/dashboard URLs with the MCP endpoint or from targeting legacy tool names. Keep the whole session on <code>/mcp</code> and use the 8 public tool names only.
          </p>
        </div>
      </div>

      {/* FOOTER */}
      <footer className="trinity-footer">
        <div className="links">
          <a href="https://arif-fazil.com/">HUMAN</a>
          <a href="https://apex.arif-fazil.com/">THEORY</a>
          <a href="https://arifos.arif-fazil.com/"><b>APPS</b></a>
        </div>
        THE TRINITY | HUMAN | THEORY | APPS<br />
        <b>Ditempa Bukan Diberi</b> | AGPL-3.0 | 2026.03.22-FORGE
        <div className="copyright-line">
          Copyright (c) 2013 &ndash; 2026 Sovereign Records | LAST UPDATED: MAR 22, 2026
        </div>
      </footer>
    </Layout>
  );
}
