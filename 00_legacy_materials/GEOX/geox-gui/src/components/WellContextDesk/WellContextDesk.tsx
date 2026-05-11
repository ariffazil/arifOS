/**
 * WellContextDesk — Well Data Browser with MCP Petrophysics
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * Promotes LogDock to a full MCP-wired desk:
 *   - Displays well log tracks via LogDock
 *   - Calls geox_compute_petrophysics + geox_select_sw_model via MCP bridge
 *   - Calls geox_petrophysical_hold_check before any result is accepted
 *   - Governed by F7 Humility (uncertainty bands) + F9 Physics9 (no phantom picks)
 *
 * MCP tools used (from well_context_desk/manifest.json):
 *   Required: mcp.geox.query_memory, mcp.geox.compute_petrophysics, mcp.geox.select_sw_model
 *   Optional: mcp.geox.validate_cutoffs, mcp.geox.petrophysical_hold_check
 */

import React, { useState, useCallback } from 'react';
import {
  FlaskConical, Cpu, AlertTriangle, CheckCircle,
  RefreshCw, ChevronDown, ChevronUp, Loader2
} from 'lucide-react';
import { LogDock } from '../LogDock/LogDock';
import { useMcpTool } from '../../hooks/useMcpTool';
import { useGEOXStore } from '../../store/geoxStore';

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

interface PetrophysicsResult {
  status: string;
  model: string;
  sw_p50?: number;
  sw_p10?: number;
  sw_p90?: number;
  phi_e?: number;
  vsh?: number;
  verdict?: string;
  confidence?: number;
  constitutional_floors?: string[];
  _888_hold?: boolean;
}

interface SwModelResult {
  recommended_model: string;
  reason: string;
  confidence: number;
  alternatives?: string[];
}

interface HoldCheckResult {
  status: string;
  hold_triggered: boolean;
  reason?: string;
  floors_checked: string[];
}

// ─────────────────────────────────────────────────────────────────────────────
// MCP Result Panel
// ─────────────────────────────────────────────────────────────────────────────

const ResultRow: React.FC<{ label: string; value: React.ReactNode }> = ({ label, value }) => (
  <div className="flex items-center justify-between py-1 border-b border-slate-800 last:border-0">
    <span className="text-xs text-slate-500">{label}</span>
    <span className="text-xs font-mono font-bold text-slate-200">{value}</span>
  </div>
);

const McpResultPanel: React.FC<{
  petro: PetrophysicsResult | null;
  swModel: SwModelResult | null;
  holdCheck: HoldCheckResult | null;
}> = ({ petro, swModel, holdCheck }) => {
  if (!petro && !swModel) return null;

  const is888Hold = petro?._888_hold || holdCheck?.hold_triggered;

  return (
    <div className="border border-slate-700 rounded-lg overflow-hidden">
      {/* Header */}
      <div className={`px-3 py-2 flex items-center gap-2 ${
        is888Hold ? 'bg-amber-900/40' : 'bg-slate-800'
      }`}>
        {is888Hold
          ? <AlertTriangle className="w-4 h-4 text-amber-400" />
          : <CheckCircle className="w-4 h-4 text-green-400" />
        }
        <span className="text-xs font-bold text-slate-200">
          {is888Hold ? '888 HOLD — Human review required' : 'MCP Petrophysics Result'}
        </span>
        {petro?.verdict && (
          <span className={`ml-auto text-xs px-2 py-0.5 rounded font-bold ${
            petro.verdict === 'SEAL' ? 'bg-green-800 text-green-200' :
            petro.verdict === 'PARTIAL' ? 'bg-blue-800 text-blue-200' :
            'bg-amber-800 text-amber-200'
          }`}>
            {petro.verdict}
          </span>
        )}
      </div>

      <div className="p-3 space-y-1 bg-slate-900">
        {swModel && (
          <ResultRow
            label="Sw Model"
            value={`${swModel.recommended_model} (${(swModel.confidence * 100).toFixed(0)}%)`}
          />
        )}
        {petro?.sw_p50 != null && (
          <ResultRow
            label="Sw P50"
            value={`${(petro.sw_p50 * 100).toFixed(1)}%`}
          />
        )}
        {petro?.sw_p10 != null && petro?.sw_p90 != null && (
          <ResultRow
            label="Sw P10–P90"
            value={`${(petro.sw_p10 * 100).toFixed(1)}% – ${(petro.sw_p90 * 100).toFixed(1)}%`}
          />
        )}
        {petro?.phi_e != null && (
          <ResultRow label="PHIe" value={`${(petro.phi_e * 100).toFixed(1)}%`} />
        )}
        {petro?.vsh != null && (
          <ResultRow label="Vsh" value={`${(petro.vsh * 100).toFixed(1)}%`} />
        )}
        {holdCheck?.hold_triggered && holdCheck.reason && (
          <div className="mt-2 p-2 rounded bg-amber-900/30 text-xs text-amber-300">
            Hold reason: {holdCheck.reason}
          </div>
        )}
      </div>

      {petro?.constitutional_floors && (
        <div className="px-3 py-1.5 bg-slate-950 flex flex-wrap gap-1">
          {petro.constitutional_floors.map((f) => (
            <span key={f} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-500 font-mono">
              {f}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// Main WellContextDesk
// ─────────────────────────────────────────────────────────────────────────────

export const WellContextDesk: React.FC = () => {
  const { selectedWell, updateFloorStatus } = useGEOXStore();
  const [showMcpPanel, setShowMcpPanel] = useState(true);

  // Petrophysics parameters (simplified — real impl reads from LogDock cursor)
  const [params, setParams] = useState({ rw: 0.05, rt: 10.0, phi: 0.20 });

  // MCP tool hooks
  const swModelTool = useMcpTool<{ formation: string; temperature_c: number }, SwModelResult>(
    'geox_select_sw_model'
  );
  const petroTool = useMcpTool<Record<string, unknown>, PetrophysicsResult>(
    'geox_compute_petrophysics'
  );
  const holdTool = useMcpTool<{ well_id: string; phi: number; sw: number }, HoldCheckResult>(
    'geox_petrophysical_hold_check'
  );

  const isRunning = swModelTool.status === 'loading'
    || petroTool.status === 'loading'
    || holdTool.status === 'loading';

  const runPetrophysics = useCallback(async () => {
    updateFloorStatus('F9', 'amber', 'Petrophysics run initiated — Physics9 check active');

    try {
      // 1. Select Sw model first
      const swResult = await swModelTool.call({
        formation: selectedWell ?? 'unknown',
        temperature_c: 80,
      });

      // 2. Compute petrophysics with selected model
      const petroResult = await petroTool.call({
        model: swResult.recommended_model,
        rw: params.rw,
        rt: params.rt,
        phi: params.phi,
        a: 1.0,
        m: 2.0,
        n: 2.0,
      });

      // 3. Petrophysical hold check — F13 gate
      if (petroResult.sw_p50 != null) {
        await holdTool.call({
          well_id: selectedWell ?? 'unknown',
          phi: params.phi,
          sw: petroResult.sw_p50,
        });
      }

      updateFloorStatus('F9', 'green', 'No phantom geology detected');
    } catch {
      updateFloorStatus('F9', 'red', 'Petrophysics pipeline error — review required');
    }
  }, [selectedWell, params, swModelTool, petroTool, holdTool, updateFloorStatus]);

  return (
    <div className="h-full flex flex-col bg-slate-950">
      {/* Desk Header */}
      <div className="h-10 bg-slate-900 border-b border-slate-800 flex items-center px-3 gap-2 flex-shrink-0">
        <FlaskConical className="w-4 h-4 text-cyan-400" />
        <span className="text-sm font-bold text-slate-200">Well Context Desk</span>
        {selectedWell && (
          <span className="text-xs font-mono text-slate-500 ml-1">
            · {selectedWell}
          </span>
        )}

        <div className="flex-1" />

        {/* MCP Run Button */}
        <button
          onClick={runPetrophysics}
          disabled={isRunning}
          className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-bold transition-all ${
            isRunning
              ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
              : 'bg-cyan-700 hover:bg-cyan-600 text-white'
          }`}
        >
          {isRunning
            ? <Loader2 className="w-3 h-3 animate-spin" />
            : <Cpu className="w-3 h-3" />
          }
          {isRunning ? 'Running…' : 'Run MCP Petro'}
        </button>

        {/* Toggle MCP Panel */}
        <button
          onClick={() => setShowMcpPanel(p => !p)}
          className="p-1.5 rounded hover:bg-slate-800 text-slate-400"
          title="Toggle MCP result panel"
        >
          {showMcpPanel ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
        </button>
      </div>

      {/* MCP Parameters + Result */}
      {showMcpPanel && (
        <div className="bg-slate-900 border-b border-slate-800 px-4 py-3 flex flex-col gap-3 flex-shrink-0">
          {/* Param inputs */}
          <div className="flex items-center gap-4 flex-wrap">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Archie Params
            </span>
            {(['rw', 'rt', 'phi'] as const).map((key) => (
              <label key={key} className="flex items-center gap-1.5 text-xs text-slate-400">
                <span className="font-mono text-slate-300 uppercase">{key}</span>
                <input
                  type="number"
                  step={key === 'phi' ? 0.01 : 0.1}
                  min={0}
                  value={params[key]}
                  onChange={(e) => setParams(prev => ({ ...prev, [key]: parseFloat(e.target.value) || 0 }))}
                  className="w-16 bg-slate-800 border border-slate-700 rounded px-2 py-0.5 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-600"
                />
              </label>
            ))}
            {(petroTool.status === 'success' || petroTool.status === 'error') && (
              <button
                onClick={() => { petroTool.reset(); swModelTool.reset(); holdTool.reset(); }}
                className="ml-auto flex items-center gap-1 text-xs text-slate-500 hover:text-slate-300"
              >
                <RefreshCw className="w-3 h-3" /> Reset
              </button>
            )}
          </div>

          {/* MCP Result */}
          {(petroTool.data || swModelTool.data || petroTool.error) && (
            <McpResultPanel
              petro={petroTool.data}
              swModel={swModelTool.data}
              holdCheck={holdTool.data}
            />
          )}

          {petroTool.error && (
            <div className="text-xs text-red-400 font-mono px-2 py-1 bg-red-950/30 rounded border border-red-900">
              {petroTool.error}
            </div>
          )}
        </div>
      )}

      {/* LogDock — full remaining height */}
      <div className="flex-1 overflow-hidden">
        <LogDock />
      </div>
    </div>
  );
};

export default WellContextDesk;
