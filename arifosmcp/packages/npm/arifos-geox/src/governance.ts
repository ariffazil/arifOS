/**
 * @arifos/geox — Nobel-Grade AGI Earth Governance
 *
 * The 6 survival layers that separate a subsurface toy from a
 * Nobel-grade Earth Intelligence. Every GEOX tool must route through
 * these gates before emitting a verdict.
 *
 * Layers:
 *   1. Physics First, AI Second
 *   2. Uncertainty Is First-Class Citizen
 *   3. Anti-Hallucination Hard Lock
 *   4. Decision Firewall (888_HOLD)
 *   5. Multi-Discipline Reasoning
 *   6. Memory Panjang + Trauma Industri
 *
 * DITEMPA BUKAN DIBERI.
 */

import { type RuntimeEnvelope } from "@arifos/mcp/types";

// ═══════════════════════════════════════════════════════════════════════════════
// Layer 1 — Physics First, AI Second
// ═══════════════════════════════════════════════════════════════════════════════

export interface PhysicsConstraint {
  name: string;
  check: (payload: Record<string, unknown>) => PhysicsViolation | null;
  severity: "fatal" | "warning";
}

export interface PhysicsViolation {
  constraint: string;
  message: string;
  expected: string;
  actual: string;
}

/** Hard locks that auto-FAIL any result violating subsurface physics. */
export const DEFAULT_PHYSICS_LOCKS: PhysicsConstraint[] = [
  {
    name: "shale_porosity_depth",
    severity: "fatal",
    check: (p) => {
      const porosity = extractNumber(p, "porosity", "porosity_fraction", "phi");
      const depth = extractNumber(p, "depth_m", "depth", "tvdss");
      if (porosity !== null && depth !== null && depth > 3000) {
        const lith = extractString(p, "lithology", "rock_type", "lith");
        const isShale =
          lith !== null && /shale|mudstone|claystone/i.test(lith);
        if (isShale && porosity > 0.25) {
          return {
            constraint: "shale_porosity_depth",
            message: `Shale porosity ${(porosity * 100).toFixed(1)}% at ${depth} m violates compaction physics.`,
            expected: "shale porosity ≤ 25% below 3000 m",
            actual: `${(porosity * 100).toFixed(1)}% at ${depth} m`,
          };
        }
      }
      return null;
    },
  },
  {
    name: "mass_balance",
    severity: "fatal",
    check: (p) => {
      const influx = extractNumber(p, "water_influx", "aquifer_influx");
      const production = extractNumber(p, "cumulative_production", "prod_total");
      const expansion = extractNumber(p, "fluid_expansion", "expansion");
      if (influx !== null && production !== null && expansion !== null) {
        const imbalance = Math.abs(influx + expansion - production);
        const relative = production > 0 ? imbalance / production : 0;
        if (relative > 0.15) {
          return {
            constraint: "mass_balance",
            message: `Material balance imbalance ${(relative * 100).toFixed(1)}% exceeds 15% tolerance.`,
            expected: "imbalance ≤ 15%",
            actual: `${(relative * 100).toFixed(1)}%`,
          };
        }
      }
      return null;
    },
  },
  {
    name: "darcy_sanity",
    severity: "warning",
    check: (p) => {
      const perm = extractNumber(p, "permeability_md", "perm", "k");
      const visc = extractNumber(p, "viscosity_cp", "viscosity", "mu");
      const rate = extractNumber(p, "flow_rate_bpd", "rate", "q");
      if (perm !== null && visc !== null && rate !== null) {
        if (perm < 0.001 && rate > 1000) {
          return {
            constraint: "darcy_sanity",
            message: `Flow rate ${rate} bpd incompatible with permeability ${perm} md.`,
            expected: "Darcy flow regime consistent with permeability",
            actual: `perm=${perm} md, rate=${rate} bpd`,
          };
        }
      }
      return null;
    },
  },
];

export function runPhysicsGuard(
  payload: Record<string, unknown>,
  locks: PhysicsConstraint[] = DEFAULT_PHYSICS_LOCKS,
): { passed: boolean; violations: PhysicsViolation[]; fatal: boolean } {
  const violations: PhysicsViolation[] = [];
  let fatal = false;
  for (const lock of locks) {
    const v = lock.check(payload);
    if (v) {
      violations.push(v);
      if (lock.severity === "fatal") fatal = true;
    }
  }
  return { passed: violations.length === 0, violations, fatal };
}

// ═══════════════════════════════════════════════════════════════════════════════
// Layer 2 — Uncertainty Is First-Class Citizen
// ═══════════════════════════════════════════════════════════════════════════════

export interface UncertaintyBand {
  p10: number;
  p50: number;
  p90: number;
  unit: string;
  dependencies: string[];
  killers: RiskKiller[];
}

export interface RiskKiller {
  rank: number;
  description: string;
  probability: number;
  mitigation?: string;
}

export function createUncertaintyBand(
  base: number,
  unit: string,
  killers: RiskKiller[],
): UncertaintyBand {
  const spread = base * 0.4;
  return {
    p10: Math.round(base + spread),
    p50: Math.round(base),
    p90: Math.round(base - spread * 0.65),
    unit,
    dependencies: killers.map((k) => k.description),
    killers: killers.sort((a, b) => a.rank - b.rank),
  };
}

/** Enforce that every quantitative claim carries uncertainty. */
export function enforceUncertainty<TPayload>(
  envelope: RuntimeEnvelope<TPayload>,
): RuntimeEnvelope<TPayload> {
  const hasUncertainty =
    envelope.payload &&
    typeof envelope.payload === "object" &&
    ("uncertainty" in (envelope.payload as object) ||
      "p10" in (envelope.payload as object) ||
      "confidence" in (envelope.payload as object));

  if (!hasUncertainty && envelope.ok) {
    envelope.errors.push({
      code: "UNCERTAINTY_MISSING",
      message:
        "Layer 2 violation: quantitative output requires uncertainty band (P10/P50/P90 or confidence interval).",
      stage: envelope.stage,
      recoverable: true,
    });
    envelope.verdict = "SABAR";
  }
  return envelope;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Layer 3 — Anti-Hallucination Hard Lock
// ═══════════════════════════════════════════════════════════════════════════════

export interface EvidenceCitation {
  source_type: "well" | "seismic" | "core" | "report" | "model" | "analogue";
  source_id: string;
  observation: string;
  page_or_depth?: string;
  confidence: number;
}

export interface HallucinationAudit {
  citations: EvidenceCitation[];
  unknowns: string[];
  assumptions: string[];
}

export function auditHallucination(
  claims: string[],
  citations: EvidenceCitation[],
): { clean: boolean; ungrounded: string[] } {
  const ungrounded: string[] = [];
  for (const claim of claims) {
    const grounded = citations.some((c) =>
      claim.toLowerCase().includes(c.observation.toLowerCase().slice(0, 20)),
    );
    if (!grounded) ungrounded.push(claim);
  }
  return { clean: ungrounded.length === 0, ungrounded };
}

/** Hard lock: if no citations and payload is not empty, downgrade to VOID. */
export function enforceCitationOrUnknown<TPayload>(
  envelope: RuntimeEnvelope<TPayload>,
  citations: EvidenceCitation[],
): RuntimeEnvelope<TPayload> {
  if (envelope.ok && citations.length === 0) {
    envelope.errors.push({
      code: "HALLUCINATION_RISK",
      message:
        "Layer 3 violation: claim emitted without evidence citation. Required: well / seismic / core / report reference.",
      stage: envelope.stage,
      recoverable: false,
    });
    envelope.verdict = "VOID";
    envelope.ok = false;
  }
  return envelope;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Layer 4 — Decision Firewall (888_HOLD)
// ═══════════════════════════════════════════════════════════════════════════════

export type HighRiskDomain =
  | "drilling"
  | "reserves_booking"
  | "barrier_integrity"
  | "well_design"
  | "abandonment"
  | "production_alteration";

export interface HoldManifest {
  domain: HighRiskDomain;
  known: string[];
  unknown: string[];
  dangerous_assumptions: string[];
  signatory_required: string;
  ai_recommendation: "WITNESS_ONLY" | "CONDITIONAL" | "HOLD";
}

export const HIGH_RISK_DOMAINS: HighRiskDomain[] = [
  "drilling",
  "reserves_booking",
  "barrier_integrity",
  "well_design",
  "abandonment",
  "production_alteration",
];

export function isHighRiskDomain(query: string): HighRiskDomain | null {
  const map: Record<string, HighRiskDomain> = {
    drill: "drilling",
    drilling: "drilling",
    reserves: "reserves_booking",
    booking: "reserves_booking",
    barrier: "barrier_integrity",
    integrity: "barrier_integrity",
    well_design: "well_design",
    casing: "well_design",
    abandonment: "abandonment",
    plug: "abandonment",
    production: "production_alteration",
    choke: "production_alteration",
  };
  const key = query.toLowerCase().replace(/\s+/g, "_");
  return map[key] ?? null;
}

export function buildHoldManifest(
  domain: HighRiskDomain,
  known: string[],
  unknown: string[],
  dangerous_assumptions: string[],
): HoldManifest {
  return {
    domain,
    known,
    unknown,
    dangerous_assumptions,
    signatory_required: "Registered Petroleum Engineer / Chief Geoscientist",
    ai_recommendation: "WITNESS_ONLY",
  };
}

/** Transform any envelope touching a high-risk domain into 888_HOLD. */
export function applyDecisionFirewall<TPayload>(
  envelope: RuntimeEnvelope<TPayload>,
  query: string,
): RuntimeEnvelope<TPayload> | { hold: HoldManifest; envelope: RuntimeEnvelope<TPayload> } {
  const domain = isHighRiskDomain(query);
  if (domain) {
    const hold = buildHoldManifest(domain, [], [], [
      "AI is witness-only for high-risk domains.",
    ]);
    envelope.verdict = "HOLD_888";
    envelope.status = "DRY_RUN";
    envelope.ok = false;
    return { hold, envelope };
  }
  return envelope;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Layer 5 — Multi-Discipline Reasoning
// ═══════════════════════════════════════════════════════════════════════════════

export type Discipline = "geology" | "geomechanics" | "drilling" | "reservoir" | "geophysics" | "petrophysics";

export interface DisciplineOpinion {
  discipline: Discipline;
  claim: string;
  confidence: number;
  risk_flag: "green" | "yellow" | "red";
}

export interface DisciplinePanel {
  opinions: DisciplineOpinion[];
  synthesis: string;
  dominant_risk: Discipline | null;
}

export function runDisciplinePanel(
  opinions: DisciplineOpinion[],
): DisciplinePanel {
  const reds = opinions.filter((o) => o.risk_flag === "red");
  const yellows = opinions.filter((o) => o.risk_flag === "yellow");
  const dominant = reds.length > 0 ? reds[0].discipline : yellows.length > 0 ? yellows[0].discipline : null;

  const synthesis =
    reds.length > 0
      ? `Geologically attractive BUT ${reds.map((r) => r.discipline).join(" + ")} flags critical risk.`
      : yellows.length > 0
        ? `Attractive with operational caution from ${yellows.map((y) => y.discipline).join(" + ")}.`
        : `All disciplines green. Proceed with standard diligence.`;

  return {
    opinions: opinions.sort((a, b) => (b.confidence - a.confidence)),
    synthesis,
    dominant_risk: dominant,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// Layer 6 — Trauma Memory (Industry Catastrophes)
// ═══════════════════════════════════════════════════════════════════════════════

export interface TraumaCase {
  name: string;
  year: number;
  basin?: string;
  failure_mode: string;
  root_cause: string;
  lessons: string[];
  similarity_tags: string[];
}

export const TRAUMA_REGISTRY: TraumaCase[] = [
  {
    name: "Macondo",
    year: 2010,
    basin: "Gulf of Mexico",
    failure_mode: "Blowout → uncontrolled release",
    root_cause: "Barrier failure + cement job inadequacy + missed negative pressure test",
    lessons: [
      "Never rely on single barrier",
      "Negative pressure test is go/no-go",
      "Cement bond log must be interpreted, not just run",
    ],
    similarity_tags: ["deepwater", "hpht", "cement", "bop", "barrier"],
  },
  {
    name: "Montara",
    year: 2009,
    basin: "Timor Sea",
    failure_mode: "Blowout during completion",
    root_cause: "Cement barrier failure + inadequate well monitoring",
    lessons: [
      "Subsea BOP must be functional before displacement",
      "Real-time pressure monitoring is non-negotiable",
    ],
    similarity_tags: ["platform", "cement", "completion", "bop"],
  },
  {
    name: "Piper Alpha",
    year: 1988,
    basin: "North Sea",
    failure_mode: "Gas explosion → platform collapse",
    root_cause: "Maintenance deferred + permit-to-work system breakdown",
    lessons: [
      "Never defer safety-critical maintenance",
      "Permit-to-work must be live, not paperwork",
      "Temporary refuge must remain intact",
    ],
    similarity_tags: ["platform", "maintenance", "permit", "safety", "gas"],
  },
];

export function scanTrauma(
  scenario_tags: string[],
): TraumaCase[] {
  return TRAUMA_REGISTRY.filter((t) =>
    t.similarity_tags.some((tag) => scenario_tags.includes(tag)),
  );
}

export function formatTraumaWarning(cases: TraumaCase[]): string {
  if (cases.length === 0) return "";
  const lines = cases.map(
    (c) =>
      `WARNING: Similar to ${c.name} (${c.year}, ${c.basin ?? "unknown basin"}) — ${c.failure_mode}.`,
  );
  return lines.join("\n");
}

// ═══════════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════════

function extractNumber(
  obj: Record<string, unknown>,
  ...keys: string[]
): number | null {
  for (const k of keys) {
    const v = obj[k];
    if (typeof v === "number") return v;
    if (typeof v === "string") {
      const parsed = parseFloat(v);
      if (!Number.isNaN(parsed)) return parsed;
    }
  }
  return null;
}

function extractString(
  obj: Record<string, unknown>,
  ...keys: string[]
): string | null {
  for (const k of keys) {
    const v = obj[k];
    if (typeof v === "string") return v;
  }
  return null;
}
