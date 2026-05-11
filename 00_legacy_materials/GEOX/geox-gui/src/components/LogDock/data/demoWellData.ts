/**
 * Demo Well Data — Synthetic Well Log with Petrophysical Computations
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * Generates realistic synthetic well log curves for the Malay Basin demonstration.
 * Computes Vsh, PHIe, and Sw using the same physics models as the backend.
 *
 * Physics:
 * - GR → Vsh via Clavier-Fertl 1974
 * - NPHI + RHOB → PHIe via neutron-density crossover
 * - ILD + PHIe + Rw → Sw via Archie
 */

import type { WellLogData, LogCurve } from '../types';

// Physics constants
const RHO_WATER = 1.0;      // g/cm³
const RHO_QUARTZ = 2.65;    // g/cm³
const DT_WATER = 189.0;     // μs/ft
const DT_QUARTZ = 55.5;     // μs/ft

export function demoWellData(): WellLogData {
  const wellName = 'MALAY-PILOT-001';
  const wellId = 'MY-001';

  // Depth range: 1500m to 2500m, step 0.5m
  const top = 1500;
  const base = 2500;
  const step = 0.5;
  const depths: number[] = [];
  for (let d = top; d <= base; d += step) {
    depths.push(parseFloat(d.toFixed(1)));
  }

  // Zone definitions
  const zones = [
    { top: 1500, base: 1700, type: 'shale', vsh: 0.7, phi: 0.08 },
    { top: 1700, base: 1850, type: 'sand', vsh: 0.15, phi: 0.22, sw: 0.85 },
    { top: 1850, base: 1950, type: 'shale', vsh: 0.65, phi: 0.10 },
    { top: 1950, base: 2100, type: 'sand', vsh: 0.12, phi: 0.28, sw: 0.35 }, // PAY ZONE
    { top: 2100, base: 2250, type: 'shale', vsh: 0.8, phi: 0.06 },
    { top: 2250, base: 2400, type: 'sand', vsh: 0.18, phi: 0.18, sw: 0.70 },
    { top: 2400, base: 2500, type: 'shale', vsh: 0.75, phi: 0.09 },
  ];

  function getZone(depth: number) {
    return zones.find((z) => depth >= z.top && depth < z.base) || zones[0];
  }

  // Generate raw curves with noise
  const grValues: number[] = [];
  const ildValues: number[] = [];
  const lldValues: number[] = [];
  const nphiValues: number[] = [];
  const rhobValues: number[] = [];
  const dtValues: number[] = [];
  const caliValues: number[] = [];

  for (const d of depths) {
    const zone = getZone(d);
    const noise = () => (Math.random() - 0.5) * 0.1;

    // GR: 30 API (clean) to 120 API (shale)
    const grBase = 30 + zone.vsh * 90;
    grValues.push(Math.round((grBase + noise() * 20) * 10) / 10);

    // ILD/LLD: 0.5 (water) to 100+ (oil)
    let rtBase = 0.5;
    if (zone.type === 'sand') {
      const sw = (zone as any).sw ?? 0.5;
      rtBase = 0.5 / Math.pow(sw, 2) / Math.pow(zone.phi, 2);
      rtBase = Math.min(rtBase, 200);
    } else {
      rtBase = 5 + zone.vsh * 15;
    }
    ildValues.push(Math.round((rtBase + noise() * rtBase * 0.3) * 10) / 10);
    lldValues.push(Math.round((rtBase * 0.9 + noise() * rtBase * 0.2) * 10) / 10);

    // NPHI: porosity in % (0-60)
    const nphiBase = zone.phi * 100;
    nphiValues.push(Math.round((nphiBase + noise() * 5) * 10) / 10);

    // RHOB: 2.65 (quartz) to 2.0 (high porosity)
    const rhobBase = RHO_QUARTZ - zone.phi * (RHO_QUARTZ - RHO_WATER);
    rhobValues.push(Math.round((rhobBase + noise() * 0.1) * 100) / 100);

    // DT: 55.5 (quartz) to 189 (water)
    const dtBase = DT_QUARTZ + zone.phi * (DT_WATER - DT_QUARTZ);
    dtValues.push(Math.round((dtBase + noise() * 10) * 10) / 10);

    // Caliper: bit size (8.5) or larger in washouts
    const washout = d > 2080 && d < 2095 ? 2.0 : 1.0;
    caliValues.push(Math.round((8.5 * washout + noise() * 0.2) * 10) / 10);
  }

  // Compute derived curves
  const grClean = 30;
  const grShale = 120;
  const rw = 0.08;

  const vshValues: (number | null)[] = [];
  const phieValues: (number | null)[] = [];
  const swValues: (number | null)[] = [];

  for (let i = 0; i < depths.length; i++) {
    // VSH from GR (Clavier-Fertl 1974)
    const gr = grValues[i];
    const igr = Math.max(0, Math.min(1, (gr - grClean) / (grShale - grClean)));
    let vsh = 1.0;
    if (igr < 1) {
      vsh = 1.7 - (3.38 - (igr + 0.7) * (igr + 0.7)) ** 0.5;
    }
    vsh = Math.max(0, Math.min(1, vsh));
    vshValues.push(Math.round(vsh * 1000) / 1000);

    // PHIe from NPHI-RHOB crossover
    const phiN = nphiValues[i] / 100;
    const phiD = (RHO_QUARTZ - rhobValues[i]) / (RHO_QUARTZ - RHO_WATER);
    let phie = (phiN + phiD) / 2;
    // Gas effect correction (crossover)
    if (phiN > phiD + 0.05) {
      phie = Math.sqrt((phiN * phiN + phiD * phiD) / 2);
    }
    phie = Math.max(0, Math.min(0.4, phie));
    phieValues.push(Math.round(phie * 1000) / 1000);

    // Sw from Archie
    const rt = ildValues[i];
    let sw: number | null = null;
    if (rt > 0 && phie > 0) {
      sw = Math.pow(rw / (phie * phie * rt), 0.5);
      sw = Math.max(0, Math.min(1, sw));
    }
    swValues.push(sw != null ? Math.round(sw * 1000) / 1000 : null);
  }

  // Anomaly zones
  const anomalyZones = [
    { type: 'washout', top: 2080, base: 2095 },
    { type: 'pay_zone', top: 1950, base: 2100 },
  ];

  const curves: LogCurve[] = [
    {
      name: 'DEPT',
      type: 'sonic',
      unit: 'm',
      depth: depths,
      values: depths,
      scale: 'linear',
      color: '#94a3b8',
      visible: false,
    },
    {
      name: 'GR',
      type: 'gr',
      unit: 'API',
      depth: depths,
      values: grValues,
      min: 0,
      max: 150,
      scale: 'linear',
      color: '#22c55e',
      lineWidth: 1.5,
      visible: true,
      fill: { baseline: 150, color: '#22c55e', opacity: 0.1 },
    },
    {
      name: 'VSH',
      type: 'computed',
      unit: 'v/v',
      depth: depths,
      values: vshValues,
      min: 0,
      max: 1,
      scale: 'linear',
      color: '#f59e0b',
      lineWidth: 2,
      visible: true,
      fill: { baseline: 0, color: '#f59e0b', opacity: 0.15 },
    },
    {
      name: 'ILD',
      type: 'resistivity',
      unit: 'Ω·m',
      depth: depths,
      values: ildValues,
      min: 0.2,
      max: 200,
      scale: 'log',
      color: '#ef4444',
      lineWidth: 1.5,
      visible: true,
    },
    {
      name: 'LLD',
      type: 'resistivity',
      unit: 'Ω·m',
      depth: depths,
      values: lldValues,
      min: 0.2,
      max: 200,
      scale: 'log',
      color: '#f97316',
      lineWidth: 1,
      visible: false,
    },
    {
      name: 'NPHI',
      type: 'neutron',
      unit: '%',
      depth: depths,
      values: nphiValues,
      min: -5,
      max: 60,
      scale: 'linear',
      color: '#3b82f6',
      lineWidth: 1.5,
      visible: true,
    },
    {
      name: 'RHOB',
      type: 'density',
      unit: 'g/cm³',
      depth: depths,
      values: rhobValues,
      min: 1.9,
      max: 2.7,
      scale: 'linear',
      color: '#a855f7',
      lineWidth: 1.5,
      visible: true,
    },
    {
      name: 'DT',
      type: 'sonic',
      unit: 'μs/ft',
      depth: depths,
      values: dtValues,
      min: 40,
      max: 140,
      scale: 'linear',
      color: '#ec4899',
      lineWidth: 1,
      visible: false,
    },
    {
      name: 'PHIE',
      type: 'computed',
      unit: 'v/v',
      depth: depths,
      values: phieValues,
      min: 0,
      max: 0.5,
      scale: 'linear',
      color: '#3b82f6',
      lineWidth: 2,
      visible: true,
      fill: { baseline: 0, color: '#3b82f6', opacity: 0.15 },
    },
    {
      name: 'SW',
      type: 'computed',
      unit: 'v/v',
      depth: depths,
      values: swValues,
      min: 0,
      max: 1,
      scale: 'linear',
      color: '#06b6d4',
      lineWidth: 2,
      visible: true,
      fill: { baseline: 1, color: '#06b6d4', opacity: 0.1 },
    },
    {
      name: 'CALI',
      type: 'caliper',
      unit: 'in',
      depth: depths,
      values: caliValues,
      min: 8,
      max: 20,
      scale: 'linear',
      color: '#64748b',
      lineWidth: 1,
      visible: false,
    },
  ];

  return {
    wellName,
    wellId,
    depthRange: [top, base],
    curves,
    parameters: {
      rw,
      bitSize: 8.5,
      grClean,
      grShale,
    },
    anomalyZones,
  };
}
