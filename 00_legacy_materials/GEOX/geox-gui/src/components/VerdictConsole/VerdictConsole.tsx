import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, AlertTriangle, CheckCircle, Lock, Hammer, Info, History, Play, Loader2 } from 'lucide-react';
import { twMerge } from 'tailwind-merge';
import { useMcpTool } from '../../hooks/useMcpTool';
import { useGEOXStore } from '../../store/geoxStore';
import './VerdictConsole.css';

// ══════════════════════════════════════════════════════════════════════════════
// JUDGE-CONSOLE-lite — The Sovereign Gating Station
// ══════════════════════════════════════════════════════════════════════════════

interface RiskFactor {
  key: string;
  impact: number;
  reason: string;
}

interface RiskAssessment {
  score: number;
  factors: RiskFactor[];
}

interface Verdict {
  verdictId: string;
  intentId: string;
  status: 'SEAL' | 'PARTIAL' | 'SABAR' | 'VOID' | '888_HOLD';
  confidence: number;
  risk: RiskAssessment;
  rationale: string;
  timestamp: string;
  author: string;
  auditTraceId: string;
}

// Default initial state
const defaultVerdict: Verdict = {
  verdictId: "V_INITIAL",
  intentId: "INTENT_ALPHA",
  status: "888_HOLD",
  confidence: 0.0,
  risk: { score: 1.0, factors: [] },
  rationale: "Await instruction. System currently in HOLD state. No active appraisal.",
  timestamp: new Date().toISOString(),
  author: "SYSTEM",
  auditTraceId: "AUDIT_NONE"
};

export const VerdictConsole: React.FC = () => {
  const [activeVerdict, setActiveVerdict] = useState<Verdict>(defaultVerdict);
  const [prospectId, setProspectId] = useState('prospect-well-001');
  const [wellId, setWellId] = useState('well-A12');
  const [authToken, setAuthToken] = useState('Wscar_999_SEAL_');
  const [showAuthInput, setShowAuthInput] = useState(false);

  const updateFloorStatus = useGEOXStore((state) => state.updateFloorStatus);

  const { call: callJudge, status: judgeStatus, error: judgeError, data: lastResult } = useMcpTool<
    { intent_id: string; prospect_id: string; well_id: string },
    Verdict
  >('geox_judge_verdict');

  const { call: callSeal, status: sealStatus, error: sealError } = useMcpTool<
    { proposal_id: string; human_auth_token: string },
    { sealed: boolean; message: string }
  >('acp_grant_seal');

  // Sync state if call succeeds
  useEffect(() => {
    if (lastResult) {
      setActiveVerdict(lastResult);
    }
  }, [lastResult]);

  const handleEvaluate = async () => {
    try {
      await callJudge({
        intent_id: `INTENT-${Date.now()}`,
        prospect_id: prospectId,
        well_id: wellId
      });
    } catch (err) {
      console.error("Judge evaluation failed:", err);
    }
  };

  const handleSeal = async () => {
    if (!activeVerdict || activeVerdict.verdictId === 'V_INITIAL') return;

    try {
      const result = await callSeal({
        proposal_id: activeVerdict.verdictId,
        human_auth_token: authToken
      });

      if (result && result.sealed) {
        setActiveVerdict(prev => ({
          ...prev,
          status: 'SEAL',
          rationale: result.message
        }));
        // Update store floor F13 to green
        updateFloorStatus('F13', 'green', '999_SEAL Authority Granted');
      }
    } catch (err) {
      console.error("Seal grant failed:", err);
    }
  };

  const isLoading = judgeStatus === 'loading' || sealStatus === 'loading';
  const error = judgeError || sealError;

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-200 border-l border-slate-800 font-mono text-xs overflow-hidden glass-panel">
      {/* Header — Constitutional ID */}
      <div className="p-4 bg-slate-900/50 border-b border-slate-800 flex items-center justify-between" id="judge-console-header">
        <div className="flex items-center gap-2">
          <Hammer className="w-4 h-4 text-amber-500" />
          <span className="caption-mono text-slate-400">888_JUDGE CONSOLE</span>
        </div>
        <div className="px-2 py-0.5 bg-slate-800 rounded border border-slate-700 text-[10px] text-slate-500 font-bold">
          KERNEL: v1.0.MVP
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {/* Input Configuration */}
        <div className="p-4 bg-slate-900/30 border-b border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-[10px] text-slate-500 mb-1">
            <Play className="w-3 h-3 text-blue-500" />
            <span className="caption-mono text-slate-500">Evaluation Target</span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1">
              <label htmlFor="prospect-id-input" className="text-[9px] text-slate-600 uppercase font-bold tracking-tighter">Prospect ID</label>
              <input
                id="prospect-id-input"
                type="text"
                title="Prospect identifier"
                value={prospectId}
                onChange={(e) => setProspectId(e.target.value)}
                className="w-full bg-slate-950/50 border border-slate-800 rounded px-2 py-1.5 text-slate-400 focus:outline-none focus:border-blue-500/50 transition-colors font-mono"
              />
            </div>
            <div className="space-y-1">
              <label htmlFor="well-id-input" className="text-[9px] text-slate-600 uppercase font-bold tracking-tighter">Well ID</label>
              <input
                id="well-id-input"
                type="text"
                title="Well identifier"
                value={wellId}
                onChange={(e) => setWellId(e.target.value)}
                className="w-full bg-slate-950/50 border border-slate-800 rounded px-2 py-1.5 text-slate-400 focus:outline-none focus:border-blue-500/50 transition-colors font-mono"
              />
            </div>
          </div>
          <button
            onClick={handleEvaluate}
            disabled={isLoading}
            className="w-full py-2.5 premium-button-blue rounded font-black text-[10px] flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed group"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin text-blue-400" /> : <Play className="w-4 h-4 group-hover:scale-110 transition-transform" />}
            RUN PHYSICS VERDICT
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="m-4 p-3 bg-rose-500/10 border border-rose-500/30 rounded text-rose-400 flex gap-2 items-start glass-panel-light"
          >
            <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <div className="space-y-1">
              <p className="font-black uppercase tracking-widest text-[10px]">Evaluation Breach</p>
              <p className="text-[10px] leading-tight opacity-80">{error}</p>
            </div>
          </motion.div>
        )}

        {/* Active Verdict Gauge */}
        <AnimatePresence mode="wait">
          {activeVerdict && (
            <motion.div
              key={activeVerdict.verdictId}
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.02 }}
              className="p-6 space-y-6"
            >
              {/* Status Shield */}
              <div className="flex flex-col items-center justify-center space-y-3">
                <div className={twMerge(
                  "w-24 h-24 rounded-full flex items-center justify-center border-2 border-dashed transition-all duration-700 relative",
                  isLoading ? "border-slate-700 animate-spin-slow" :
                  activeVerdict.status === 'SEAL' ? "status-seal" :
                  activeVerdict.status === 'VOID' ? "status-void" :
                  "status-hold"
                )}>
                  {activeVerdict.status === 'SEAL' ? (
                    <Shield className="w-12 h-12 text-emerald-500 drop-shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
                  ) : activeVerdict.status === 'VOID' ? (
                    <AlertTriangle className="w-12 h-12 text-rose-500 drop-shadow-[0_0_10px_rgba(244,63,94,0.5)]" />
                  ) : (
                    <Lock className="w-12 h-12 text-amber-500 drop-shadow-[0_0_10px_rgba(245,158,11,0.5)]" />
                  )}

                  {/* Rotating decorative ring */}
                  <div className={twMerge(
                    "absolute inset-0 rounded-full border border-white/5 animate-spin-slow",
                    isLoading ? "opacity-10" : "opacity-30"
                  )} />
                </div>
                <div className="text-center">
                  <h3 className={twMerge(
                    "text-3xl font-black tracking-tighter transition-all duration-500 uppercase",
                    activeVerdict.status === 'SEAL' ? "text-emerald-500 glow-text-emerald" :
                    activeVerdict.status === 'VOID' ? "text-rose-500 glow-text-rose" :
                    "text-amber-500 glow-text-amber"
                  )}>
                    {activeVerdict.status}
                  </h3>
                  <div className="flex items-center justify-center gap-2 mt-1">
                    <span className="text-[9px] text-slate-500 caption-mono">{activeVerdict.verdictId}</span>
                    <span className="w-1 h-1 rounded-full bg-slate-800" />
                    <span className="text-[9px] text-slate-600 font-mono font-bold">TRACE: {activeVerdict.auditTraceId.slice(0, 8)}</span>
                  </div>
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-slate-950/50 rounded border border-slate-800/50 relative overflow-hidden group glass-panel-light">
                  <p className="text-slate-500 mb-1 text-[9px] caption-mono opacity-60">Confidence</p>
                  <p className="text-xl font-black text-emerald-400 tabular-nums">{(activeVerdict.confidence * 100).toFixed(1)}%</p>
                  <div className="h-1 w-full bg-slate-900 mt-2 rounded-full overflow-hidden border border-white/5">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${activeVerdict.confidence * 100}%` }}
                      transition={{ duration: 1, ease: "easeOut" }}
                      className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.5)]"
                    />
                  </div>
                </div>
                <div className="p-3 bg-slate-950/50 rounded border border-slate-800/50 relative overflow-hidden group glass-panel-light">
                  <p className="text-slate-500 mb-1 text-[9px] caption-mono opacity-60">Risk Score</p>
                  <p className="text-xl font-black text-rose-400 tabular-nums">{(activeVerdict.risk.score * 100).toFixed(1)}%</p>
                  <div className="h-1 w-full bg-slate-900 mt-2 rounded-full overflow-hidden border border-white/5">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${activeVerdict.risk.score * 100}%` }}
                      transition={{ duration: 1, ease: "easeOut" }}
                      className="h-full bg-gradient-to-r from-rose-600 to-rose-400 shadow-[0_0_8px_rgba(244,63,94,0.5)]"
                    />
                  </div>
                </div>
              </div>

              {/* Risk Factors */}
              {activeVerdict.risk.factors.length > 0 && (
                <div className="space-y-2">
                   <div className="flex items-center gap-1 text-slate-500 text-[9px] caption-mono opacity-60">
                    <span>Critical Risk Factors</span>
                  </div>
                  <div className="space-y-1.5">
                    {activeVerdict.risk.factors.map((f, i) => (
                      <div key={i} className="flex items-center justify-between p-2.5 bg-slate-900/40 rounded border border-slate-800/30 text-[10px] glass-panel-light hover:border-slate-700/50 transition-colors">
                        <span className="text-slate-400 font-bold tracking-tight">{f.key}</span>
                        <span className={twMerge(
                          "font-mono font-black",
                          f.impact > 0.5 ? "text-rose-400" : "text-amber-400"
                        )}>Δ {f.impact.toFixed(3)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Rationale Box */}
              <div className="space-y-2">
                <div className="flex items-center gap-1 text-slate-500 text-[9px] caption-mono opacity-60">
                  <Info className="w-3 h-3" />
                  <span>Rationale & Audit Trail</span>
                </div>
                <div className="p-4 bg-slate-900/60 rounded border border-slate-800/80 text-slate-400 leading-relaxed italic text-[11px] min-h-[60px] glass-panel-light shadow-inner">
                  "{activeVerdict.rationale}"
                </div>
              </div>

              {/* Audit Details */}
              <div className="space-y-2 pt-4 border-t border-slate-800/50">
                <div className="flex justify-between text-[10px] items-center">
                  <span className="text-slate-600 caption-mono opacity-50">Sovereign Author</span>
                  <span className="text-slate-400 font-black tracking-widest bg-slate-800 px-2 py-0.5 rounded border border-slate-700">{activeVerdict.author}</span>
                </div>
                <div className="flex justify-between text-[10px] items-center">
                  <span className="text-slate-600 caption-mono opacity-50">Gated Timestamp</span>
                  <span className="text-slate-500 font-mono">{new Date(activeVerdict.timestamp).toLocaleString()}</span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer — Controls */}
      <div className="p-4 bg-slate-900/80 border-t border-slate-800 flex gap-2 backdrop-blur-md">
        <button className="flex-1 py-3 bg-slate-800/50 hover:bg-slate-700/50 rounded border border-slate-700/50 flex items-center justify-center gap-2 transition-all group active:scale-95">
          <History className="w-4 h-4 text-slate-500 group-hover:text-slate-300" />
          <span className="caption-mono text-[10px]">HISTORY</span>
        </button>
        <div className="flex-1 flex flex-col gap-2">
          {showAuthInput ? (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              className="flex flex-col gap-2 overflow-hidden"
            >
              <input
                type="password"
                placeholder="Enter Wscar_ token..."
                value={authToken}
                onChange={(e) => setAuthToken(e.target.value)}
                autoFocus
                className="w-full bg-slate-950/80 border border-slate-700/50 rounded px-2 py-2 text-[10px] text-emerald-400 focus:border-emerald-500/50 outline-none font-mono placeholder:text-slate-700 shadow-inner"
              />
              <div className="flex gap-2">
                 <button
                  onClick={() => setShowAuthInput(false)}
                  className="flex-1 py-2 bg-slate-800/50 hover:bg-slate-700/50 rounded border border-slate-700 text-[10px] caption-mono text-slate-500"
                >
                  CANCEL
                </button>
                <button
                  onClick={handleSeal}
                  disabled={isLoading}
                  className="flex-[2] py-2 premium-button-emerald rounded font-black text-[10px] caption-mono"
                >
                  CONFIRM SEAL
                </button>
              </div>
            </motion.div>
          ) : (
            <button
              onClick={() => setShowAuthInput(true)}
              disabled={activeVerdict.status === 'SEAL' || activeVerdict.verdictId === 'V_INITIAL'}
              className={twMerge(
                "w-full py-3 rounded flex items-center justify-center gap-2 transition-all font-black group active:scale-95",
                activeVerdict.status === 'SEAL' || activeVerdict.verdictId === 'V_INITIAL'
                  ? "bg-slate-900/50 text-slate-600 border border-slate-800 cursor-not-allowed opacity-50"
                  : "premium-button-emerald"
              )}
            >
              <CheckCircle className={twMerge(
                "w-4 h-4",
                activeVerdict.status === 'SEAL' ? "text-emerald-500/20" : "text-emerald-500"
              )} />
              <span className="caption-mono text-[10px]">APPROVE & SEAL</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default VerdictConsole;
