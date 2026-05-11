/**
 * LogDock Type Definitions
 * ═══════════════════════════════════════════════════════════════════════════════
 */

export type LogCurveType = 'gr' | 'sp' | 'resistivity' | 'density' | 'neutron' | 'sonic' | 'caliper' | 'computed';

export interface LogCurve {
  name: string;
  type: LogCurveType;
  unit: string;
  depth: number[];
  values: (number | null)[];
  min?: number;
  max?: number;
  scale: 'linear' | 'log';
  color: string;
  lineWidth?: number;
  visible: boolean;
  fill?: {
    baseline: number;
    color: string;
    opacity: number;
  };
}

export interface TrackConfig {
  id: string;
  title: string;
  width: number;
  curves: string[];
}

export interface WellParameters {
  rw: number;        // Formation water resistivity (ohm-m)
  bitSize: number;   // Bit diameter (inches)
  grClean: number;   // Clean sand GR value (API)
  grShale: number;   // Shale GR value (API)
}

export interface WellLogData {
  wellName: string;
  wellId: string;
  depthRange: [number, number];
  curves: LogCurve[];
  parameters: WellParameters;
  anomalyZones?: Array<{
    type: string;
    top: number;
    base: number;
  }>;
}
