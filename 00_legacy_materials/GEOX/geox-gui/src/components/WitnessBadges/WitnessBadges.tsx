/**
 * WitnessBadges — Constitutional Floor Indicators
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * Visual governance badges showing F1-F13 constitutional floor status.
 * Always visible, color-coded, with actionable guidance.
 */

import React from 'react';
import { Shield, AlertTriangle, CheckCircle, XCircle, HelpCircle } from 'lucide-react';
import * as Tooltip from '@radix-ui/react-tooltip';
import { useGovernance } from '../../store/geoxStore';
import type { ConstitutionalFloor, FloorStatus, FloorId } from '../../types';

// Badge color configurations
const statusColors: Record<FloorStatus, { bg: string; border: string; icon: string; label: string }> = {
  green: {
    bg: 'bg-green-100',
    border: 'border-green-500',
    icon: 'text-green-600',
    label: 'text-green-800',
  },
  amber: {
    bg: 'bg-amber-100',
    border: 'border-amber-500',
    icon: 'text-amber-600',
    label: 'text-amber-800',
  },
  red: {
    bg: 'bg-red-100',
    border: 'border-red-500',
    icon: 'text-red-600',
    label: 'text-red-800',
  },
  grey: {
    bg: 'bg-gray-100',
    border: 'border-gray-400',
    icon: 'text-gray-500',
    label: 'text-gray-600',
  },
};

// Status icons
const StatusIcon: React.FC<{ status: FloorStatus }> = ({ status }) => {
  const className = "w-4 h-4";
  switch (status) {
    case 'green':
      return <CheckCircle className={`${className} text-green-600`} />;
    case 'amber':
      return <AlertTriangle className={`${className} text-amber-600`} />;
    case 'red':
      return <XCircle className={`${className} text-red-600`} />;
    case 'grey':
    default:
      return <HelpCircle className={`${className} text-gray-500`} />;
  }
};

// Individual Floor Badge
const FloorBadge: React.FC<{ floor: ConstitutionalFloor }> = ({ floor }) => {
  const colors = statusColors[floor.status];

  return (
    <Tooltip.Provider delayDuration={100}>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>
          <div
            className={`
              flex items-center gap-2 px-3 py-2 rounded-lg border-2 cursor-help
              transition-all duration-200 hover:shadow-md
              ${colors.bg} ${colors.border}
            `}
          >
            <StatusIcon status={floor.status} />
            <div className="flex flex-col">
              <span className={`text-xs font-bold ${colors.label}`}>
                {floor.id} {floor.name}
              </span>
              {floor.status !== 'grey' && (
                <span className={`text-[10px] ${colors.label} opacity-75`}>
                  {floor.status.toUpperCase()}
                </span>
              )}
            </div>
          </div>
        </Tooltip.Trigger>

        <Tooltip.Portal>
          <Tooltip.Content
            className="bg-slate-900 text-white px-4 py-3 rounded-lg shadow-xl max-w-xs z-50"
            sideOffset={5}
          >
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-yellow-400" />
                <span className="font-bold">{floor.id} {floor.name}</span>
                <span className={`text-xs px-2 py-0.5 rounded ${
                  floor.type === 'hard' ? 'bg-red-900 text-red-200' : 'bg-blue-900 text-blue-200'
                }`}>
                  {floor.type.toUpperCase()}
                </span>
              </div>

              <p className="text-sm text-slate-300">{floor.description}</p>

              {floor.message && (
                <div className={`text-sm p-2 rounded ${
                  floor.status === 'red' ? 'bg-red-900/50 text-red-200' :
                  floor.status === 'amber' ? 'bg-amber-900/50 text-amber-200' :
                  'bg-green-900/50 text-green-200'
                }`}>
                  {floor.message}
                </div>
              )}

              <div className="text-xs text-slate-400 pt-1 border-t border-slate-700">
                Status: <span className={`
                  font-semibold
                  ${floor.status === 'green' ? 'text-green-400' : ''}
                  ${floor.status === 'amber' ? 'text-amber-400' : ''}
                  ${floor.status === 'red' ? 'text-red-400' : ''}
                  ${floor.status === 'grey' ? 'text-gray-400' : ''}
                `}>{floor.status.toUpperCase()}</span>
              </div>
            </div>

            <Tooltip.Arrow className="fill-slate-900" />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
};

// Overall Status Ribbon
const StatusRibbon: React.FC = () => {
  const governance = useGovernance();

  const ribbonConfig = {
    green: { bg: 'bg-green-600', text: 'text-white', label: 'ALL FLOORS SATISFIED', icon: CheckCircle },
    amber: { bg: 'bg-amber-500', text: 'text-white', label: 'ATTENTION REQUIRED', icon: AlertTriangle },
    red: { bg: 'bg-red-600', text: 'text-white', label: 'CONSTITUTIONAL VIOLATION', icon: XCircle },
    grey: { bg: 'bg-gray-500', text: 'text-white', label: 'INITIALIZING', icon: HelpCircle },
  };

  const config = ribbonConfig[governance.overallStatus];
  const Icon = config.icon;

  return (
    <div className={`${config.bg} ${config.text} px-4 py-2 rounded-lg flex items-center gap-2 font-bold shadow-md`}>
      <Icon className="w-5 h-5" />
      <span>{config.label}</span>
      <span className="text-xs opacity-75 ml-2">| {governance.seal}</span>
    </div>
  );
};

// Main WitnessBadges Component
export const WitnessBadges: React.FC = () => {
  const governance = useGovernance();

  // Filter to show only active floors (not grey) + always F9, F13
  const priorityFloors = ['F1', 'F4', 'F7', 'F9', 'F11', 'F13'] as FloorId[];

  return (
    <div className="flex flex-col gap-3 p-4 bg-slate-50 border-l border-slate-200 h-full">
      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        <Shield className="w-5 h-5 text-slate-700" />
        <h3 className="font-bold text-slate-800">Governance</h3>
      </div>

      {/* Overall Status */}
      <StatusRibbon />

      {/* Priority Floor Badges */}
      <div className="flex flex-col gap-2 mt-2">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Constitutional Floors
        </span>

        {priorityFloors.map((floorId) => (
          <FloorBadge key={floorId} floor={governance.floors[floorId]} />
        ))}
      </div>

      {/* All Floors Toggle */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <details className="group">
          <summary className="flex items-center gap-2 cursor-pointer text-sm text-slate-600 hover:text-slate-800">
            <span className="transition-transform group-open:rotate-90">▶</span>
            <span>View All 13 Floors</span>
          </summary>

          <div className="flex flex-col gap-2 mt-2 pl-4">
            {(Object.keys(governance.floors) as FloorId[]).map((floorId) => (
              <FloorBadge key={floorId} floor={governance.floors[floorId]} />
            ))}
          </div>
        </details>
      </div>

      {/* Seal */}
      <div className="mt-auto pt-4 text-center">
        <div className="text-xs font-mono text-slate-400 border border-slate-300 rounded px-2 py-1">
          {governance.seal}
        </div>
        <div className="text-[10px] text-slate-400 mt-1">
          Session: {governance.sessionId.slice(0, 8)}...
        </div>
      </div>
    </div>
  );
};

// Compact version for toolbar
export const WitnessBadgesCompact: React.FC = () => {
  const governance = useGovernance();

  const getStatusIcon = () => {
    switch (governance.overallStatus) {
      case 'green': return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'amber': return <AlertTriangle className="w-5 h-5 text-amber-600" />;
      case 'red': return <XCircle className="w-5 h-5 text-red-600" />;
      default: return <HelpCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <Tooltip.Provider>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>
          <button className="flex items-center gap-2 px-3 py-1.5 bg-white border border-slate-300 rounded-lg hover:bg-slate-50">
            {getStatusIcon()}
            <span className="text-sm font-medium text-slate-700">
              F1-F13
            </span>
            <span className={`
              text-xs px-1.5 py-0.5 rounded font-bold
              ${governance.overallStatus === 'green' ? 'bg-green-100 text-green-700' : ''}
              ${governance.overallStatus === 'amber' ? 'bg-amber-100 text-amber-700' : ''}
              ${governance.overallStatus === 'red' ? 'bg-red-100 text-red-700' : ''}
              ${governance.overallStatus === 'grey' ? 'bg-gray-100 text-gray-700' : ''}
            `}>
              {governance.overallStatus.toUpperCase()}
            </span>
          </button>
        </Tooltip.Trigger>

        <Tooltip.Portal>
          <Tooltip.Content className="bg-slate-900 text-white px-4 py-3 rounded-lg shadow-xl">
            <div className="space-y-2">
              <p className="font-bold">Constitutional Floors Status</p>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
                {Object.values(governance.floors).map((floor) => (
                  <div key={floor.id} className="flex items-center gap-2">
                    <div className={`
                      w-2 h-2 rounded-full
                      ${floor.status === 'green' ? 'bg-green-500' : ''}
                      ${floor.status === 'amber' ? 'bg-amber-500' : ''}
                      ${floor.status === 'red' ? 'bg-red-500' : ''}
                      ${floor.status === 'grey' ? 'bg-gray-400' : ''}
                    `} />
                    <span className={floor.status === 'red' ? 'text-red-300' : 'text-slate-300'}>
                      {floor.id} {floor.name}
                    </span>
                  </div>
                ))}
              </div>
            </div>
            <Tooltip.Arrow className="fill-slate-900" />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
};

// Grounding specific badge for Earth Witness
export const GroundedBadge: React.FC<{
  confidence: number;
  status: string;
  source: string;
}> = ({ confidence, status, source }) => {
  return (
    <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700 p-3 rounded-lg shadow-xl flex flex-col gap-1 min-w-[180px]">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Grounding</span>
        <div className={`w-2 h-2 rounded-full ${confidence >= 0.9 ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-amber-500'}`} />
      </div>
      <div className="flex items-end gap-2">
        <span className="text-2xl font-black text-white font-mono">{(confidence * 100).toFixed(0)}%</span>
        <span className="text-[10px] text-green-400 font-bold mb-1 uppercase tracking-tighter">{status}</span>
      </div>
      <div className="text-[9px] text-slate-500 border-t border-slate-800 pt-1 mt-1 font-medium italic">
        Source: {source}
      </div>
    </div>
  );
};

export default WitnessBadges;
