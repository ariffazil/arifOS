/**
 * DomainVoid — Risk & Decision Manifold (000-249)
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * The Decision Manifold for volumetrics, economics, and 888_HOLD governance.
 * Brutalist, forensic, high-contrast aesthetic.
 *
 * Features:
 * - Monte Carlo P90/P50/P10 analysis visualization
 * - GCOS (Geological Chance of Success) distribution curves
 * - Constitutional floor validation status
 * - 888_HOLD governance gate
 */

import React, { useState, useMemo } from 'react';
import {
  AlertTriangle,
  Shield,
  CheckCircle,
  XCircle,
  Activity,
  TrendingUp,
  TrendingDown,
  Lock,
  Scale,
  FileWarning,
} from 'lucide-react';
import type { FloorStatus, FloorId } from '../../types';

/**
 * Risk distribution data
 */
interface RiskDistribution {
  p10: number; // Optimistic
  p50: number; // Median
  p90: number; // Conservative
  mean: number;
  stdDev: number;
}

/**
 * Volumetrics assessment
 */
interface VolumetricsAssessment {
  grossRockVolume: RiskDistribution; // km³
  netToGross: RiskDistribution; // fraction
  porosity: RiskDistribution; // fraction
  hydrocarbonSaturation: RiskDistribution; // fraction
  recoveryFactor: RiskDistribution; // fraction
  formationVolumeFactor: number;
}

/**
 * GCOS components
 */
interface GCOSComponents {
  charge: number; // 0-1
  trap: number; // 0-1
  reservoir: number; // 0-1
  seal: number; // 0-1
  overall: number; // Product of components
}

/**
 * Economic metrics
 */
interface EconomicMetrics {
  npv: RiskDistribution; // $M
  irr: RiskDistribution; // %
  paybackPeriod: RiskDistribution; // years
  breakEvenPrice: number; // $/bbl
}

/**
 * Constitutional verdict
 */
interface ConstitutionalVerdict {
  floor: FloorId;
  status: FloorStatus;
  message: string;
  timestamp: string;
}

interface DomainVoidProps {
  assessment?: VolumetricsAssessment;
  gcos?: GCOSComponents;
  economics?: EconomicMetrics;
  verdicts?: ConstitutionalVerdict[];
  onHoldRequest?: () => void;
  onSealRequest?: () => void;
}

/**
 * GCOS Gauge Component
 */
const GCOSGauge: React.FC<{ components: GCOSComponents }> = ({ components }) => {
  const { charge, trap, reservoir, seal, overall } = components;

  const getColor = (value: number) => {
    if (value >= 0.6) return '#10B981';
    if (value >= 0.4) return '#F59E0B';
    return '#EF4444';
  };

  const GaugeBar: React.FC<{ label: string; value: number }> = ({ label, value }) => (
    <div className="mb-3">
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">{label}</span>
        <span className="text-xs font-mono font-bold" style={{ color: getColor(value) }}>
          {(value * 100).toFixed(0)}%
        </span>
      </div>
      <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${value * 100}%`, backgroundColor: getColor(value) }}
        />
      </div>
    </div>
  );

  return (
    <div className="geox-card">
      <div className="geox-card__header">
        <div className="flex items-center gap-2">
          <Scale className="w-4 h-4 text-amber-500" />
          <span className="geox-card__title">GCOS Distribution</span>
        </div>
        <span
          className="text-lg font-mono font-black"
          style={{ color: getColor(overall) }}
        >
          {(overall * 100).toFixed(1)}%
        </span>
      </div>
      <div className="geox-card__body">
        <GaugeBar label="Charge" value={charge} />
        <GaugeBar label="Trap" value={trap} />
        <GaugeBar label="Reservoir" value={reservoir} />
        <GaugeBar label="Seal" value={seal} />
        <div className="mt-4 pt-3 border-t border-slate-700">
          <div className="flex justify-between items-center">
            <span className="text-xs font-mono text-slate-500 uppercase">Overall COS</span>
            <span className="text-sm font-mono font-bold text-white">
              {(overall * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Volumetrics Distribution Chart
 */
const VolumetricsChart: React.FC<{ distribution: RiskDistribution; label: string; unit: string }> = ({
  distribution,
  label,
  unit,
}) => {
  const { p10, p50, p90, mean } = distribution;
  const max = p10 * 1.2;
  const min = p90 * 0.8;
  const range = max - min;

  const toPercent = (value: number) => ((value - min) / range) * 100;

  return (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">{label}</span>
        <span className="text-xs font-mono text-slate-300">
          P50: <span className="text-amber-400 font-bold">{p50.toFixed(2)}</span> {unit}
        </span>
      </div>
      <div className="relative h-8 bg-slate-800 rounded-md overflow-hidden">
        {/* P90-P10 range bar */}
        <div
          className="absolute top-2 bottom-2 bg-slate-600/50 rounded"
          style={{
            left: `${toPercent(p90)}%`,
            width: `${toPercent(p10) - toPercent(p90)}%`,
          }}
        />
        {/* P50 marker */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-amber-500"
          style={{ left: `${toPercent(p50)}%` }}
        />
        {/* Mean marker */}
        <div
          className="absolute top-1 bottom-1 w-1 bg-emerald-500 rounded-full"
          style={{ left: `${toPercent(mean)}%` }}
        />
      </div>
      <div className="flex justify-between mt-1 text-[10px] font-mono text-slate-500">
        <span>P90: {p90.toFixed(2)}</span>
        <span>Mean: {mean.toFixed(2)}</span>
        <span>P10: {p10.toFixed(2)}</span>
      </div>
    </div>
  );
};

/**
 * Constitutional Floor Status
 */
const FloorStatusPanel: React.FC<{ verdicts: ConstitutionalVerdict[] }> = ({ verdicts }) => {
  const statusIcons: Record<FloorStatus, React.ReactNode> = {
    green: <CheckCircle className="w-4 h-4 text-emerald-500" />,
    amber: <AlertTriangle className="w-4 h-4 text-amber-500" />,
    red: <XCircle className="w-4 h-4 text-red-500" />,
    grey: <Activity className="w-4 h-4 text-slate-500" />,
  };

  const statusClasses: Record<FloorStatus, string> = {
    green: 'geox-floor-badge--green',
    amber: 'geox-floor-badge--amber',
    red: 'geox-floor-badge--red',
    grey: 'geox-floor-badge--grey',
  };

  return (
    <div className="geox-card">
      <div className="geox-card__header">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-emerald-500" />
          <span className="geox-card__title">Constitutional Floors</span>
        </div>
      </div>
      <div className="geox-card__body">
        <div className="space-y-2">
          {verdicts.map((verdict) => (
            <div
              key={verdict.floor}
              className={`flex items-center justify-between p-2 rounded ${statusClasses[verdict.status]}`}
            >
              <div className="flex items-center gap-2">
                {statusIcons[verdict.status]}
                <span className="text-xs font-mono font-bold">{verdict.floor}</span>
              </div>
              <span className="text-[10px] text-right max-w-[150px] truncate">
                {verdict.message}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

/**
 * 888_HOLD Gate Control
 */
const HoldGateControl: React.FC<{
  onHoldRequest: () => void;
  onSealRequest: () => void;
  canSeal: boolean;
}> = ({ onHoldRequest, onSealRequest, canSeal }) => {
  const [confirming, setConfirming] = useState<'hold' | 'seal' | null>(null);

  return (
    <div className="geox-card border-amber-500/30">
      <div className="geox-card__header bg-amber-950/30">
        <div className="flex items-center gap-2">
          <Lock className="w-4 h-4 text-amber-500" />
          <span className="geox-card__title text-amber-400">888_HOLD Gate</span>
        </div>
      </div>
      <div className="geox-card__body">
        <p className="text-xs text-slate-400 mb-4">
          Sovereign authority checkpoint. AC_Risk ≥ 0.60 requires explicit HOLD.
          All clear for SEAL.
        </p>

        {confirming === 'hold' ? (
          <div className="space-y-3">
            <div className="flex items-center gap-2 p-3 bg-red-950/30 border border-red-500/30 rounded">
              <FileWarning className="w-5 h-5 text-red-400" />
              <span className="text-xs text-red-300">
                Confirm 888_HOLD. This will pause all operations.
              </span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  onHoldRequest();
                  setConfirming(null);
                }}
                className="geox-btn geox-btn--danger flex-1"
              >
                Confirm HOLD
              </button>
              <button
                onClick={() => setConfirming(null)}
                className="geox-btn geox-btn--ghost"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : confirming === 'seal' ? (
          <div className="space-y-3">
            <div className="flex items-center gap-2 p-3 bg-emerald-950/30 border border-emerald-500/30 rounded">
              <CheckCircle className="w-5 h-5 text-emerald-400" />
              <span className="text-xs text-emerald-300">
                Confirm 999_SEAL. This validates all constitutional floors.
              </span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  onSealRequest();
                  setConfirming(null);
                }}
                className="geox-btn geox-btn--primary flex-1"
              >
                Confirm SEAL
              </button>
              <button
                onClick={() => setConfirming(null)}
                className="geox-btn geox-btn--ghost"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="flex gap-3">
            <button
              onClick={() => setConfirming('hold')}
              className="geox-btn geox-btn--danger flex-1"
            >
              <AlertTriangle className="w-4 h-4" />
              888_HOLD
            </button>
            <button
              onClick={() => setConfirming('seal')}
              disabled={!canSeal}
              className="geox-btn geox-btn--primary flex-1"
            >
              <Shield className="w-4 h-4" />
              999_SEAL
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Economic Summary Card
 */
const EconomicSummary: React.FC<{ metrics: EconomicMetrics }> = ({ metrics }) => {
  const { npv, irr, paybackPeriod } = metrics;

  const MetricRow: React.FC<{
    label: string;
    p50: number;
    unit: string;
    trend: 'up' | 'down' | 'neutral';
  }> = ({ label, p50, unit, trend }) => (
    <div className="flex items-center justify-between py-2 border-b border-slate-700/50 last:border-0">
      <span className="text-xs font-mono text-slate-400">{label}</span>
      <div className="flex items-center gap-2">
        {trend === 'up' && <TrendingUp className="w-3 h-3 text-emerald-500" />}
        {trend === 'down' && <TrendingDown className="w-3 h-3 text-red-500" />}
        <span className="text-sm font-mono font-bold text-white">
          {p50.toFixed(1)}
          <span className="text-xs text-slate-500 ml-1">{unit}</span>
        </span>
      </div>
    </div>
  );

  return (
    <div className="geox-card">
      <div className="geox-card__header">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-emerald-500" />
          <span className="geox-card__title">Economic Metrics</span>
        </div>
      </div>
      <div className="geox-card__body">
        <MetricRow label="NPV (P50)" p50={npv.p50} unit="$M" trend="up" />
        <MetricRow label="IRR (P50)" p50={irr.p50} unit="%" trend="up" />
        <MetricRow label="Payback" p50={paybackPeriod.p50} unit="yrs" trend="down" />
        <div className="mt-3 pt-3 border-t border-slate-700">
          <div className="flex justify-between items-center">
            <span className="text-xs font-mono text-slate-500">Break-even</span>
            <span className="text-sm font-mono font-bold text-amber-400">
              ${metrics.breakEvenPrice.toFixed(2)}/bbl
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Main DomainVoid Component
 */
export const DomainVoid: React.FC<DomainVoidProps> = ({
  assessment = defaultAssessment,
  gcos = defaultGCOS,
  economics = defaultEconomics,
  verdicts = defaultVerdicts,
  onHoldRequest = () => {},
  onSealRequest = () => {},
}) => {
  // Calculate if seal is possible (all floors green)
  const canSeal = useMemo(() => {
    return verdicts.every((v) => v.status === 'green');
  }, [verdicts]);

  // Calculate AC_Risk
  const acRisk = useMemo(() => {
    return 1 - gcos.overall;
  }, [gcos]);

  return (
    <div className="h-full flex flex-col bg-[#0A0C0E] geox-root">
      {/* Domain Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-900/50">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
          <span className="text-sm font-bold text-white tracking-tight">DomainVoid</span>
          <span className="text-xs font-mono text-amber-500">000-249</span>
          <span className="geox-domain-indicator geox-domain-indicator--void">Decision</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block">
              AC_Risk
            </span>
            <span
              className={`text-sm font-mono font-black ${
                acRisk >= 0.6 ? 'text-red-500' : acRisk >= 0.35 ? 'text-amber-500' : 'text-emerald-500'
              }`}
            >
              {(acRisk * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-4 geox-scroll">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Left Column */}
          <div className="space-y-4">
            <GCOSGauge components={gcos} />
            <EconomicSummary metrics={economics} />
            <FloorStatusPanel verdicts={verdicts} />
          </div>

          {/* Right Column */}
          <div className="space-y-4">
            <div className="geox-card">
              <div className="geox-card__header">
                <span className="geox-card__title">Volumetrics Assessment</span>
              </div>
              <div className="geox-card__body">
                <VolumetricsChart
                  distribution={assessment.grossRockVolume}
                  label="Gross Rock Volume"
                  unit="km³"
                />
                <VolumetricsChart
                  distribution={assessment.netToGross}
                  label="Net to Gross"
                  unit="fraction"
                />
                <VolumetricsChart
                  distribution={assessment.porosity}
                  label="Porosity"
                  unit="fraction"
                />
                <VolumetricsChart
                  distribution={assessment.hydrocarbonSaturation}
                  label="HC Saturation"
                  unit="fraction"
                />
              </div>
            </div>

            <HoldGateControl
              onHoldRequest={onHoldRequest}
              onSealRequest={onSealRequest}
              canSeal={canSeal}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// Default data for demonstration
const defaultAssessment: VolumetricsAssessment = {
  grossRockVolume: { p10: 50, p50: 35, p90: 20, mean: 35, stdDev: 8 },
  netToGross: { p10: 0.8, p50: 0.65, p90: 0.5, mean: 0.65, stdDev: 0.1 },
  porosity: { p10: 0.25, p50: 0.2, p90: 0.15, mean: 0.2, stdDev: 0.03 },
  hydrocarbonSaturation: { p10: 0.9, p50: 0.75, p90: 0.6, mean: 0.75, stdDev: 0.1 },
  recoveryFactor: { p10: 0.4, p50: 0.3, p90: 0.2, mean: 0.3, stdDev: 0.06 },
  formationVolumeFactor: 1.2,
};

const defaultGCOS: GCOSComponents = {
  charge: 0.75,
  trap: 0.8,
  reservoir: 0.7,
  seal: 0.85,
  overall: 0.357,
};

const defaultEconomics: EconomicMetrics = {
  npv: { p10: 1200, p50: 800, p90: 400, mean: 780, stdDev: 250 },
  irr: { p10: 35, p50: 25, p90: 15, mean: 24, stdDev: 6 },
  paybackPeriod: { p10: 3, p50: 5, p90: 8, mean: 5.2, stdDev: 1.5 },
  breakEvenPrice: 45.5,
};

const defaultVerdicts: ConstitutionalVerdict[] = [
  { floor: 'F1', status: 'green', message: 'Reversibility verified', timestamp: new Date().toISOString() },
  { floor: 'F2', status: 'green', message: 'Evidence grounded', timestamp: new Date().toISOString() },
  { floor: 'F4', status: 'amber', message: 'Units validated with caution', timestamp: new Date().toISOString() },
  { floor: 'F7', status: 'green', message: 'Confidence calibrated', timestamp: new Date().toISOString() },
  { floor: 'F9', status: 'green', message: 'No consciousness claims', timestamp: new Date().toISOString() },
  { floor: 'F11', status: 'green', message: 'Audit trail complete', timestamp: new Date().toISOString() },
  { floor: 'F13', status: 'green', message: 'Sovereign authority preserved', timestamp: new Date().toISOString() },
];

export default DomainVoid;
