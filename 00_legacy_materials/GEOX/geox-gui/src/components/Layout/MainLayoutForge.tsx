/**
 * MainLayoutForge — GEOX Earth Intelligence Core (Design Forge Edition)
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * The 000-999 Command Center implementing:
 * - DomainVoid (000-249): Risk & Decision
 * - Domain1D (250-499): Borehole Intelligence
 * - Domain2D (500-749): Seismic & Planar
 * - Domain3D (750-999): Volume & Basin
 */

import React, { useState, useEffect } from 'react';
import {
  Gauge,
  AlignLeft,
  Activity,
  Globe,
  Target,
  Shield,
  Settings,
  Search,
  ChevronLeft,
  ChevronRight,
  Zap,
  Cpu,
  Database,
  Lock,
} from 'lucide-react';
import * as Tabs from '@radix-ui/react-tabs';
import { DomainVoid } from '../../forge/domain/DomainVoid';
import { Domain1D } from '../../forge/domain/Domain1D';
import { Domain2D } from '../../forge/domain/Domain2D';
import { Domain3D } from '../../forge/domain/Domain3D';
import { useGEOXStore, useGovernance, useGEOXConnected } from '../../store/geoxStore';
import '../../styles/designSystem.css';

/**
 * Tab configuration for 000-999 domains
 */
const DOMAIN_TABS = [
  {
    id: 'void',
    label: 'DomainVoid',
    range: '000-249',
    icon: Gauge,
    description: 'Risk & Decision',
    color: 'amber',
  },
  {
    id: '1d',
    label: 'Domain1D',
    range: '250-499',
    icon: AlignLeft,
    description: 'Borehole Intelligence',
    color: 'cyan',
  },
  {
    id: '2d',
    label: 'Domain2D',
    range: '500-749',
    icon: Activity,
    description: 'Seismic & Planar',
    color: 'violet',
  },
  {
    id: '3d',
    label: 'Domain3D',
    range: '750-999',
    icon: Globe,
    description: 'Volume & Basin',
    color: 'emerald',
  },
] as const;

type DomainTab = typeof DOMAIN_TABS[number]['id'];

/**
 * Left Sidebar — Data & Layers
 */
const LeftSidebar: React.FC = () => {
  const [expanded, setExpanded] = useState(true);
  const geoxConnected = useGEOXConnected();

  return (
    <div
      className={`flex flex-col bg-[#111418] border-r border-slate-800 transition-all duration-300 ${
        expanded ? 'w-64' : 'w-12'
      }`}
    >
      {/* Toggle */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="p-3 hover:bg-slate-800 border-b border-slate-800 flex items-center justify-center transition-colors"
      >
        {expanded ? (
          <ChevronLeft className="w-4 h-4 text-slate-400" />
        ) : (
          <ChevronRight className="w-4 h-4 text-slate-400" />
        )}
      </button>

      {expanded && (
        <>
          {/* Search */}
          <div className="p-3 border-b border-slate-800">
            <div className="relative">
              <Search className="absolute left-2.5 top-2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search wells, fields..."
                className="geox-input geox-input--mono pl-9 text-xs"
              />
            </div>
          </div>

          {/* Layers Tree */}
          <div className="flex-1 overflow-auto p-3 geox-scroll">
            <h4 className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider mb-3">
              Data Layers
            </h4>
            <div className="space-y-1">
              <LayerItem name="Basemap (OpenStreetMap)" checked color="#5A6773" />
              <LayerItem name="Malay Basin Pilot" checked color="#F59E0B" />
              <LayerItem name="Seismic Lines" color="#8B5CF6" />
              <LayerItem name="Well Trajectories" checked color="#06B6D4" />
              <LayerItem name="Formation Tops" color="#10B981" />
              <LayerItem name="License Blocks" color="#5A6773" />
            </div>

            <h4 className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider mb-3 mt-6">
              Active Domains
            </h4>
            <div className="space-y-2">
              {DOMAIN_TABS.map((tab) => (
                <div
                  key={tab.id}
                  className="flex items-center gap-2 p-2 rounded hover:bg-slate-800/50 transition-colors"
                >
                  <div
                    className="w-2 h-2 rounded-full"
                    style={{
                      backgroundColor:
                        tab.color === 'amber'
                          ? '#F59E0B'
                          : tab.color === 'cyan'
                          ? '#06B6D4'
                          : tab.color === 'violet'
                          ? '#8B5CF6'
                          : '#10B981',
                    }}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs text-slate-300 font-medium truncate">{tab.label}</div>
                    <div className="text-[9px] text-slate-500 font-mono">{tab.range}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Status Footer */}
          <div className="p-3 border-t border-slate-800 bg-slate-900/50">
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  geoxConnected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'
                }`}
              />
              <span className="text-[10px] font-mono text-slate-400">
                {geoxConnected ? 'EIC ONLINE' : 'OFFLINE'}
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

/**
 * Layer Item Component
 */
const LayerItem: React.FC<{ name: string; checked?: boolean; color: string }> = ({
  name,
  checked = false,
  color,
}) => (
  <label className="flex items-center gap-2 p-1.5 hover:bg-slate-800/50 rounded cursor-pointer group transition-colors">
    <input
      type="checkbox"
      defaultChecked={checked}
      className="rounded border-slate-600 bg-slate-800 text-emerald-500 focus:ring-emerald-500/20"
    />
    <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: color }} />
    <span className="text-xs text-slate-400 group-hover:text-slate-300 truncate">{name}</span>
  </label>
);

/**
 * Right Sidebar — Governance & Intelligence
 */
const RightSidebar: React.FC = () => {
  const governance = useGovernance();
  const [activePanel, setActivePanel] = useState<'floors' | 'telemetry' | 'intel'>('floors');

  const statusColor: Record<string, string> = {
    green: 'text-emerald-500',
    amber: 'text-amber-500',
    red: 'text-red-500',
    grey: 'text-slate-500',
  };

  return (
    <div className="w-80 flex flex-col bg-[#111418] border-l border-slate-800">
      {/* Panel Tabs */}
      <div className="flex border-b border-slate-800">
        {[
          { id: 'floors', icon: Shield, label: 'Governance' },
          { id: 'telemetry', icon: Cpu, label: 'Telemetry' },
          { id: 'intel', icon: Database, label: 'Intelligence' },
        ].map((panel) => (
          <button
            key={panel.id}
            onClick={() => setActivePanel(panel.id as typeof activePanel)}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 text-[10px] font-mono font-bold uppercase tracking-wider transition-colors ${
              activePanel === panel.id
                ? 'text-emerald-400 border-b-2 border-emerald-500 bg-slate-800/30'
                : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            <panel.icon className="w-3 h-3" />
            {panel.label}
          </button>
        ))}
      </div>

      {/* Panel Content */}
      <div className="flex-1 overflow-auto p-4 geox-scroll">
        {activePanel === 'floors' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono text-slate-500 uppercase">Overall Status</span>
              <span
                className={`text-xs font-mono font-bold uppercase ${statusColor[governance.overallStatus]}`}
              >
                {governance.overallStatus}
              </span>
            </div>

            {Object.values(governance.floors).map((floor) => (
              <div
                key={floor.id}
                className={`p-3 rounded-lg border transition-colors ${
                  floor.status === 'green'
                    ? 'bg-emerald-950/20 border-emerald-500/30'
                    : floor.status === 'amber'
                    ? 'bg-amber-950/20 border-amber-500/30'
                    : floor.status === 'red'
                    ? 'bg-red-950/20 border-red-500/30'
                    : 'bg-slate-800/30 border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-mono font-bold text-slate-200">{floor.id}</span>
                  <span
                    className={`text-[10px] font-mono uppercase ${statusColor[floor.status]}`}
                  >
                    {floor.status}
                  </span>
                </div>
                <span className="text-xs text-slate-300 block">{floor.name}</span>
                <span className="text-[10px] text-slate-500 block mt-1">{floor.description}</span>
                {floor.message && (
                  <span className="text-[10px] text-slate-400 block mt-1 italic">{floor.message}</span>
                )}
              </div>
            ))}
          </div>
        )}

        {activePanel === 'telemetry' && (
          <div className="space-y-4">
            <div className="geox-card">
              <div className="geox-card__header">
                <span className="geox-card__title">System Status</span>
              </div>
              <div className="geox-card__body space-y-2">
                <TelemetryRow label="CPU Usage" value="34%" status="normal" />
                <TelemetryRow label="Memory" value="2.4GB / 8GB" status="normal" />
                <TelemetryRow label="GPU" value="Active" status="good" />
                <TelemetryRow label="Network" value="45ms" status="good" />
              </div>
            </div>

            <div className="geox-card">
              <div className="geox-card__header">
                <span className="geox-card__title">Data Pipeline</span>
              </div>
              <div className="geox-card__body space-y-2">
                <TelemetryRow label="Seismic Cache" value="1.2TB" status="normal" />
                <TelemetryRow label="Well Logs" value="456 loaded" status="good" />
                <TelemetryRow label="Surfaces" value="12 active" status="good" />
              </div>
            </div>
          </div>
        )}

        {activePanel === 'intel' && (
          <div className="space-y-4">
            <div className="geox-card border-violet-500/30">
              <div className="geox-card__header bg-violet-950/20">
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4 text-violet-400" />
                  <span className="geox-card__title text-violet-400">Gemini AI</span>
                </div>
              </div>
              <div className="geox-card__body">
                <p className="text-xs text-slate-400 mb-3">
                  Earth Intelligence LLM ready for geological interpretation.
                </p>
                <div className="grid grid-cols-2 gap-2">
                  <button className="geox-btn geox-btn--secondary text-[10px] py-1.5">
                    Interpret Log
                  </button>
                  <button className="geox-btn geox-btn--secondary text-[10px] py-1.5">
                    Assess Risk
                  </button>
                  <button className="geox-btn geox-btn--secondary text-[10px] py-1.5">
                    Find Analogs
                  </button>
                  <button className="geox-btn geox-btn--secondary text-[10px] py-1.5">
                    Correlate
                  </button>
                </div>
              </div>
            </div>

            <div className="geox-card">
              <div className="geox-card__header">
                <span className="geox-card__title">Macrostrat API</span>
              </div>
              <div className="geox-card__body">
                <TelemetryRow label="Status" value="Connected" status="good" />
                <TelemetryRow label="Latency" value="120ms" status="normal" />
                <TelemetryRow label="Cache Hit" value="87%" status="good" />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Telemetry Row Component
 */
const TelemetryRow: React.FC<{
  label: string;
  value: string;
  status: 'good' | 'normal' | 'warning' | 'error';
}> = ({ label, value, status }) => {
  const statusColors = {
    good: 'text-emerald-400',
    normal: 'text-cyan-400',
    warning: 'text-amber-400',
    error: 'text-red-400',
  };

  return (
    <div className="flex items-center justify-between text-xs">
      <span className="text-slate-500">{label}</span>
      <span className={`font-mono font-medium ${statusColors[status]}`}>{value}</span>
    </div>
  );
};

/**
 * Domain Workspace Component
 */
const DomainWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<DomainTab>('void');

  return (
    <div className="flex-1 flex flex-col bg-[#0A0C0E]">
      {/* Domain Tabs */}
      <Tabs.Root value={activeTab} onValueChange={(v) => setActiveTab(v as DomainTab)}>
        <Tabs.List className="flex border-b border-slate-800 bg-[#111418]/50">
          {DOMAIN_TABS.map((tab) => (
            <Tabs.Trigger
              key={tab.id}
              value={tab.id}
              className={`
                flex items-center gap-2 px-4 py-3 text-xs font-medium border-b-2 transition-all
                data-[state=active]:border-b-2 data-[state=active]:bg-slate-800/30
                data-[state=inactive]:border-transparent data-[state=inactive]:text-slate-500
                hover:text-slate-200
                ${
                  tab.color === 'amber'
                    ? 'data-[state=active]:text-amber-400 data-[state=active]:border-amber-500'
                    : tab.color === 'cyan'
                    ? 'data-[state=active]:text-cyan-400 data-[state=active]:border-cyan-500'
                    : tab.color === 'violet'
                    ? 'data-[state=active]:text-violet-400 data-[state=active]:border-violet-500'
                    : 'data-[state=active]:text-emerald-400 data-[state=active]:border-emerald-500'
                }
              `}
            >
              <tab.icon className="w-4 h-4" />
              <span className="hidden lg:inline">{tab.label}</span>
              <span className="lg:hidden font-mono">{tab.range}</span>
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        {/* Tab Content */}
        <div className="flex-1 overflow-hidden">
          <Tabs.Content value="void" className="h-full">
            <DomainVoid />
          </Tabs.Content>
          <Tabs.Content value="1d" className="h-full">
            <Domain1D />
          </Tabs.Content>
          <Tabs.Content value="2d" className="h-full">
            <Domain2D />
          </Tabs.Content>
          <Tabs.Content value="3d" className="h-full">
            <Domain3D />
          </Tabs.Content>
        </div>
      </Tabs.Root>
    </div>
  );
};

/**
 * Header Component
 */
const Header: React.FC = () => {
  const governance = useGovernance();
  const geoxConnected = useGEOXConnected();

  const verdictText = {
    green: '999_SEAL',
    amber: '888_QUALIFY',
    red: '888_HOLD',
    grey: 'INITIALIZING',
  };

  const verdictClass = {
    green: 'geox-verdict--seal',
    amber: 'geox-verdict--hold',
    red: 'geox-verdict--void',
    grey: 'geox-floor-badge--grey',
  };

  return (
    <header className="h-14 bg-[#0A0C0E] border-b border-slate-800 flex items-center px-4 justify-between">
      {/* Logo */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-3 group cursor-pointer">
          <div className="p-2 bg-emerald-500/10 rounded-lg group-hover:bg-emerald-500/20 transition-all">
            <Globe className="w-6 h-6 text-emerald-500 group-hover:scale-110 transition-transform" />
          </div>
          <div>
            <h1 className="font-black text-lg tracking-tight leading-none text-white uppercase">
              GEOX <span className="text-emerald-500">FORGE</span>
            </h1>
            <p className="text-[10px] text-slate-600 font-mono tracking-widest mt-0.5">
              000-999 EARTH INTELLIGENCE
            </p>
          </div>
        </div>

        {/* Trinity Navigation */}
        <nav className="hidden md:flex items-center gap-1 bg-slate-800/30 p-1 rounded-lg border border-slate-700/50">
          <HeaderAppLink href="https://arifosmcp.arif-fazil.com" icon={Shield} label="arifOS" />
          <HeaderAppLink href="https://wiki.arif-fazil.com" icon={Database} label="Ω-Wiki" />
          <HeaderAppLink href="https://vault.arifosmcp.arif-fazil.com" icon={Lock} label="Vault" />
        </nav>
      </div>

      {/* Right Side */}
      <div className="flex items-center gap-4">
        {/* Connection Status */}
        <div
          className="flex items-center gap-2 px-3 py-1.5 bg-slate-800/50 rounded-lg border border-slate-700/50"
          title="MCP Server Status"
        >
          <div
            className={`w-2 h-2 rounded-full ${
              geoxConnected
                ? 'bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.6)]'
                : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]'
            }`}
          />
          <span className="text-[10px] font-mono font-bold tracking-tight text-slate-400">
            {geoxConnected ? 'EIC ONLINE' : 'DISCONNECTED'}
          </span>
        </div>

        {/* Governance Verdict */}
        <div className={`geox-verdict ${verdictClass[governance.overallStatus]}`}>
          <Lock className="w-3 h-3" />
          {verdictText[governance.overallStatus]}
        </div>

        {/* Settings */}
        <button className="p-2 hover:bg-slate-800 rounded-lg transition-colors">
          <Settings className="w-4 h-4 text-slate-400" />
        </button>
      </div>
    </header>
  );
};

/**
 * Header App Link
 */
const HeaderAppLink: React.FC<{
  href: string;
  icon: React.ElementType;
  label: string;
}> = ({ href, icon: Icon, label }) => (
  <a
    href={href}
    target="_blank"
    rel="noopener noreferrer"
    className="flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-bold text-slate-400 hover:text-white hover:bg-slate-700/50 rounded-md transition-all uppercase tracking-tighter"
  >
    <Icon className="w-3 h-3" />
    {label}
  </a>
);

/**
 * Main Layout Forge Component
 */
export const MainLayoutForge: React.FC = () => {
  return (
    <div className="h-screen flex flex-col bg-[#0A0C0E] geox-root">
      <Header />
      <div className="flex-1 flex overflow-hidden">
        <LeftSidebar />
        <DomainWorkspace />
        <RightSidebar />
      </div>
    </div>
  );
};

export default MainLayoutForge;
