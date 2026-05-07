import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Database,
  Target,
  Layers,
  Info,
  ChevronRight,
  ShieldCheck,
  Brain,
  Activity,
  CheckCircle2,
  Clock,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Box,
  History,
  Zap,
  Maximize
} from 'lucide-react';
import { useMcpTool } from '../../hooks/useMcpTool';

/**
 * MalayBasinPilotDashboard
 *
 * Visual GUI for the Malay Basin exploration demo.
 * Displays key metrics, play types, and exploration phases.
 * INTEGRATED: Active Reasoning Cockpit.
 */
export const MalayBasinPilotDashboard: React.FC = () => {
  const [activeTraceId, setActiveTraceId] = useState<string | null>(null);
  const [showTrace, setShowTrace] = useState(false);
  const [traceData, setTraceData] = useState<any>(null);

  const scenarioTool = useMcpTool<any, any>('geox_execute_scenario');
  const traceTool = useMcpTool<{ session_id: string }, any>('geox_get_reasoning_trace');

  const handleExecuteScenario = async () => {
    try {
      const result = await scenarioTool.call({
        scenario_id: 'MBP_2026_RECOVERY',
        parameters: {
          target_horizon: 'Group J',
          objective: 'P9 Expansion'
        }
      });

      if (result.reasoning_trace_id) {
        setActiveTraceId(result.reasoning_trace_id);
        setShowTrace(true);
        // Initial fetch
        const trace = await traceTool.call({ session_id: result.reasoning_trace_id });
        setTraceData(trace);
      }
    } catch (err) {
      console.error('Scenario execution failed:', err);
    }
  };

  // Poll for trace updates if session is active
  useEffect(() => {
    let interval: any;
    if (showTrace && activeTraceId) {
      interval = setInterval(async () => {
        const trace = await traceTool.call({ session_id: activeTraceId });
        setTraceData(trace);
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [showTrace, activeTraceId, traceTool.call]);

  return (
    <div className="h-full flex flex-col bg-slate-950 text-slate-200 overflow-hidden relative">
      {/* Header Section */}
      <div className="p-6 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-3xl font-black tracking-tighter text-white uppercase italic">
              Malay Basin <span className="text-blue-500">Pilot</span>
            </h2>
            <p className="text-slate-400 text-sm mt-1 font-mono tracking-widest uppercase">
              Petroleum Exploration Cycle: 1968–2018
            </p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/30 rounded-full text-[10px] font-bold text-blue-400 uppercase tracking-widest">
            <ShieldCheck className="w-3 h-3" />
            GSM Validated Data
          </div>
        </div>

        {/* Rapid Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
          <MetricCard
            label="Total Discoveries"
            value="181+"
            sub="Oil & Gas Fields"
            icon={Target}
            color="text-blue-400"
          />
          <MetricCard
            label="Commulative Resource"
            value="14.8"
            sub="BBOE Discovered"
            icon={Database}
            color="text-emerald-400"
          />
          <MetricCard
            label="Wells Drilled"
            value="2,100"
            sub="700 Exploratory"
            icon={Layers}
            color="text-amber-400"
          />
          <MetricCard
            label="National Share"
            value="40%"
            sub="Of Hydrocarbon Resources"
            icon={TrendingUp}
            color="text-purple-400"
          />
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-auto p-6 space-y-8 pb-32">

        {/* Play Types Analysis */}
        <section>
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
            <Layers className="w-3 h-3" />
            Play Classification (P1–P9)
          </h3>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <PlayCard
              code="P1"
              type="Basin-centre anticline"
              fields="Tapis, Jerneh, Dulang"
              share="60%"
              accent="bg-blue-500"
              median="191.6 MMboe"
            />
            <PlayCard
              code="P3"
              type="Normal fault / dip closure"
              fields="Bergading, Abu"
              share="Medium"
              accent="bg-emerald-500"
              median="52 MMboe"
            />
            <PlayCard
              code="P9"
              type="Deep HPHT / Tight"
              fields="Bergading Deep, Sepat"
              share="Emerging"
              accent="bg-orange-500"
              status="Frontier"
            />
          </div>
        </section>

        {/* Creaming Curve / EDP Phases */}
        <section className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          <div>
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
              <TrendingUp className="w-3 h-3" />
              Exploration & Discovery (EDP) Phases
            </h3>
            <div className="space-y-3">
              <EDPItem
                phase="EDP 1"
                period="1968–1976"
                title="Basin-centre anticlinal play"
                outcome="~8.7 BBOE (60% of total)"
                active
              />
              <EDPItem
                phase="EDP 2"
                period="1977–1989"
                title="Giant fields plateau"
                outcome="Basin-centre exhaustion"
              />
              <EDPItem
                phase="EDP 3"
                period="1990–2000"
                title="Flank plays rejuvenation"
                outcome="+1.5 BBOE (NE Ramp, JDA)"
              />
              <EDPItem
                phase="EDP 5"
                period="2011–2018"
                title="Residual mop-up phase"
                outcome="HPHT, Tight Sands, Basement"
              />
            </div>
          </div>

          {/* Visual Trend Placeholder */}
          <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 flex flex-col items-center justify-center min-h-[300px] group hover:border-blue-500/50 transition-all">
            <div className="w-full h-full flex flex-col items-center justify-center opacity-40 group-hover:opacity-100 transition-opacity">
              <div className="w-full h-40 flex items-end gap-1 px-4 text-xs font-mono">
                <div className="flex-1 bg-blue-500 h-[100%] rounded-t relative">
                  <span className="absolute -top-6 left-1/2 -translate-x-1/2">P1</span>
                </div>
                <div className="flex-1 bg-blue-500/80 h-[40%] rounded-t relative">
                  <span className="absolute -top-6 left-1/2 -translate-x-1/2">P3</span>
                </div>
                <div className="flex-1 bg-blue-500/60 h-[25%] rounded-t relative">
                   <span className="absolute -top-6 left-1/2 -translate-x-1/2">P5</span>
                </div>
                <div className="flex-1 bg-blue-500/40 h-[15%] rounded-t relative">
                   <span className="absolute -top-6 left-1/2 -translate-x-1/2">P7</span>
                </div>
                <div className="flex-1 bg-blue-500/20 h-[10%] rounded-t relative">
                   <span className="absolute -top-6 left-1/2 -translate-x-1/2">P9</span>
                </div>
              </div>
              <p className="mt-8 text-xs font-mono text-slate-500 uppercase tracking-widest italic">Creaming Curve Declination Path</p>
            </div>
            <div className="mt-6 flex gap-4 text-[10px] text-slate-400">
              <div className="flex items-center gap-1"><div className="w-2 h-2 bg-blue-500 rounded-sm" /> Discoveries</div>
              <div className="flex items-center gap-1"><div className="w-2 h-2 bg-slate-700 rounded-sm" /> Forecast</div>
            </div>
          </div>
        </section>

        {/* Nodal Infrastructure */}
        <section className="bg-gradient-to-br from-blue-900/40 to-slate-900/20 border border-blue-500/40 rounded-2xl p-6 shadow-2xl shadow-blue-500/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-500/20 rounded-xl border border-blue-500/30 animate-pulse">
                <Brain className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <h4 className="text-white font-bold text-lg flex items-center gap-2">
                  Active Reasoning Cockpit
                  <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full font-black uppercase tracking-tighter border border-emerald-500/30">
                    Live Engine
                  </span>
                </h4>
                <p className="text-slate-400 text-sm italic">Executing causal interpretations across Malay Basin targets.</p>
              </div>
            </div>
            <button
              onClick={handleExecuteScenario}
              disabled={scenarioTool.status === 'loading'}
              className={`px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-black transition-all flex items-center gap-2 shadow-lg shadow-blue-600/20 disabled:opacity-50 group`}
            >
              {scenarioTool.status === 'loading' ? (
                <>
                  <Activity className="w-4 h-4 animate-spin" />
                  PROCESSING...
                </>
              ) : (
                <>
                  EXECUTE 2026 SCENARIO
                  <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </div>

          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
             <div className="p-4 bg-black/40 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Reserves Recovery</p>
                <p className="text-lg font-black text-white mt-1">~2.0 BBOE</p>
                <p className="text-[9px] text-slate-500 mt-2 uppercase">Physically Grounded Forecast</p>
             </div>
             <div className="p-4 bg-black/40 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Causal Integrity</p>
                <p className="text-lg font-black text-emerald-400 mt-1 uppercase">Pass</p>
                <p className="text-[9px] text-slate-500 mt-2 uppercase">888_JUDGE VALIDATED</p>
             </div>
             <div className="p-4 bg-black/40 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Uncertainty (F7)</p>
                <p className="text-lg font-black text-slate-300 mt-1">±4%</p>
                <p className="text-[9px] text-slate-500 mt-2 uppercase">Humility Floor Enforced</p>
             </div>
          </div>
        </section>

      </div>

      {/* Reasoning Trace Sidebar / Drawer */}
      {showTrace && (
        <div className="absolute right-0 top-0 bottom-0 w-80 md:w-96 bg-slate-900/95 border-l border-slate-700 backdrop-blur-xl shadow-2xl flex flex-col z-50 animate-in slide-in-from-right duration-300">
          <div className="p-4 border-b border-slate-700 flex justify-between items-center bg-black/20">
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-blue-400" />
              <h3 className="font-black text-sm tracking-tighter uppercase italic text-white">REASONING TRACE</h3>
            </div>
            <button
              onClick={() => setShowTrace(false)}
              className="p-1 hover:bg-white/10 rounded transition-colors"
              title="Close Reasoning Trace"
            >
              <ChevronRight className="w-5 h-5 text-slate-500" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {!traceData ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-4 opacity-50">
                <Activity className="w-8 h-8 animate-pulse" />
                <p className="text-[10px] uppercase font-mono">Tracing in progress...</p>
              </div>
            ) : (
              <>
                <div className="p-3 bg-blue-500/5 border border-blue-500/20 rounded-lg">
                  <p className="text-[9px] text-blue-400/70 uppercase font-black tracking-widest mb-1">Current Goal</p>
                  <p className="text-xs font-bold text-slate-200">{traceData.goal}</p>
                </div>

                <div className="space-y-4">
                  {traceData.steps.map((step: any, idx: number) => (
                    <div key={idx} className="relative pl-6 border-l border-slate-800">
                      <div className="absolute -left-[5px] top-1 w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-black text-slate-500 uppercase">Step {idx + 1}</span>
                          <span className="text-[9px] font-mono text-slate-600 italic">Verified</span>
                        </div>
                        <p className="text-xs font-bold text-slate-100 leading-relaxed">{step.thought}</p>

                        {step.evidence && step.evidence.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {step.evidence.map((ev: string, i: number) => (
                              <span key={i} className="px-1.5 py-0.5 bg-slate-800 rounded text-[8px] font-mono text-slate-400 border border-slate-700">
                                #{ev}
                              </span>
                            ))}
                          </div>
                        )}

                        <div className="mt-2 p-2 bg-black/30 rounded border border-white/5 text-[10px] text-slate-400 font-mono italic">
                          "{step.observation}"
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-4 border-t border-slate-800">
                  <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono uppercase">
                    <span>Session Status</span>
                    <span className="text-emerald-500 font-bold">{traceData.state}</span>
                  </div>
                  <div className="mt-2 h-1 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 w-[75%] animate-pulse" />
                  </div>
                </div>
              </>
            )}
          </div>

          <div className="p-4 bg-black/40 border-t border-slate-800">
             <button
               className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[10px] font-bold uppercase tracking-widest transition-colors flex items-center justify-center gap-2"
               onClick={() => window.open(`geox://reasoning/traces/${activeTraceId}`, '_blank')}
             >
               <ExternalLink className="w-3 h-3" />
               Full Report Audit
             </button>
          </div>
        </div>
      )}

      {/* Footer Info */}
      <div className="p-4 bg-black/20 border-t border-slate-900 text-[10px] flex justify-between items-center text-slate-500 font-mono">
        <div className="flex items-center gap-2">
           <Info className="w-3 h-3" />
           DATA SRC: GSM-702001 (PETRONAS / GSM ARCHIVES)
        </div>
        <div className="uppercase tracking-widest">
           SEAL: DITEMPA BUKAN DIBERI
        </div>
      </div>
    </div>
  );
};

/* --- Subcomponents --- */

const MetricCard: React.FC<{ label: string; value: string; sub: string; icon: React.ElementType; color: string }> = ({
  label, value, sub, icon: Icon, color
}) => (
  <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl hover:border-slate-700 transition-colors group">
    <div className="flex justify-between items-start">
      <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest">{label}</p>
      <Icon className={`w-4 h-4 ${color} opacity-50`} />
    </div>
    <p className={`text-2xl font-black mt-1 ${color}`}>{value}</p>
    <p className="text-[10px] text-slate-500 mt-1 uppercase truncate">{sub}</p>
  </div>
);

const PlayCard: React.FC<{ code: string; type: string; fields: string; share: string; accent: string; median?: string; status?: string }> = ({
  code, type, fields, share, accent, median, status
}) => (
  <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl relative overflow-hidden group hover:scale-[1.02] transition-transform">
    <div className={`absolute top-0 left-0 w-1 h-full ${accent}`} />
    <div className="flex justify-between items-center mb-2">
      <span className={`px-2 py-0.5 rounded text-[10px] font-black text-white ${accent}`}>{code}</span>
      <span className="text-[10px] font-mono text-slate-500 uppercase">{share}</span>
    </div>
    <h4 className="text-sm font-bold text-white mb-2 leading-tight">{type}</h4>
    <p className="text-[10px] text-slate-400 mb-4 line-clamp-2">Example: {fields}</p>
    <div className="flex items-center justify-between mt-auto pt-2 border-t border-slate-800">
       <span className="text-[10px] text-slate-500 uppercase">Median Size</span>
       <span className="text-xs font-mono text-white">{median || status || 'N/A'}</span>
    </div>
  </div>
);

const EDPItem: React.FC<{ phase: string; period: string; title: string; outcome: string; active?: boolean }> = ({
  phase, period, title, outcome, active
}) => (
  <div className={`flex items-center gap-4 p-3 rounded-xl border ${active ? 'bg-blue-500/10 border-blue-500/30' : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'} transition-all group`}>
    <div className="w-16 text-center">
       <p className={`text-[10px] font-black ${active ? 'text-blue-400' : 'text-slate-500'}`}>{phase}</p>
       <p className="text-[8px] text-slate-600 font-mono">{period}</p>
    </div>
    <div className="flex-1">
      <h5 className="text-xs font-bold text-slate-200">{title}</h5>
      <p className="text-[10px] text-slate-500">{outcome}</p>
    </div>
    <ChevronRight className="w-4 h-4 text-slate-700 group-hover:text-slate-400 transition-colors" />
  </div>
);
