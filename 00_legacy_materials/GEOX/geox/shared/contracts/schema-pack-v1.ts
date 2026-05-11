import { z } from "zod";

/**
 * DIMENSIONS & CORE ENUMS
 * The 7-dimension canonical architecture of GEOX.
 */
export const DimensionEnum = z.enum([
  "PROSPECT",
  "WELL",
  "SECTION",
  "EARTH_3D",
  "TIME_4D",
  "PHYSICS",
  "MAP"
]);
export type Dimension = z.infer<typeof DimensionEnum>;

export const VerdictEnum = z.enum([
  "SEAL",     // ≥ 0.80 Confidence, auto-proceed
  "PARTIAL",  // ≥ 0.50 Confidence, caveats apply
  "SABAR",    // ≥ 0.25 Confidence, hold for data
  "VOID",     // < 0.25 Confidence, blocked
  "888_HOLD"  // Sovereign override / high-risk pause
]);
export type VerdictCode = z.infer<typeof VerdictEnum>;

/**
 * FOUNDATIONAL CONTRACTS
 */

export const GeoContextSchema = z.object({
  dimension: DimensionEnum,
  crs: z.string().default("WGS84"),
  epoch: z.string().optional(), // Geological time / vintage
  precision_level: z.number().min(0).max(1).default(1.0),
  is_simulated: z.boolean().default(false)
});
export type GeoContext = z.infer<typeof GeoContextSchema>;

export const BoundingBoxSchema = z.object({
  min_x: z.number(),
  max_x: z.number(),
  min_y: z.number(),
  max_y: z.number(),
  min_z: z.number(),
  max_z: z.number(),
  unit: z.string().default("m")
});
export type BoundingBox = z.infer<typeof BoundingBoxSchema>;

/**
 * EVIDENCE & MANIFOLDS
 */

export const EvidenceRefSchema = z.object({
  id: z.string().uuid(),
  kind: z.enum(["MANIFOLD", "TRUTH", "CLAIM", "TEXTURE"]),
  name: z.string(),
  source_path: z.string().optional(),
  owner: z.string().optional(),
  hash: z.string().optional() // Content integrity
});
export type EvidenceRef = z.infer<typeof EvidenceRefSchema>;

export const Physics9Schema = z.object({
  density: z.number().describe("ρ (kg/m³)"),
  vp: z.number().describe("Vp (m/s)"),
  vs: z.number().describe("Vs (m/s)"),
  resistivity: z.number().describe("ρₑ (Ω·m)"),
  susceptibility: z.number().describe("χ (SI)"),
  thermal_conductivity: z.number().describe("k (W/m·K)"),
  pore_pressure: z.number().describe("P (Pa)"),
  temperature: z.number().describe("T (K)"),
  porosity: z.number().min(0).max(1).describe("φ (0-1)")
});
export type Physics9 = z.infer<typeof Physics9Schema>;

/**
 * TRANSFORM & GOVERNANCE
 */

export const TransformRequestSchema = z.object({
  request_id: z.string().uuid(),
  context: GeoContextSchema,
  sources: z.array(EvidenceRefSchema),
  operator: z.string(), // e.g., "inverse_synthesis", "depth_conversion"
  parameters: z.record(z.string(), z.any()).default({}),
  priority: z.number().default(5)
});
export type TransformRequest = z.infer<typeof TransformRequestSchema>;

export const TransformResultSchema = z.object({
  request_id: z.string().uuid(),
  verdict: VerdictEnum,
  confidence: z.number().min(0).max(1),
  outputs: z.array(EvidenceRefSchema),
  physics_drift: z.number().optional(), // Deviation from Physics9 constraints
  commentary: z.string().optional()
});
export type TransformResult = z.infer<typeof TransformResultSchema>;

/**
 * RISK & CONSTRAINTS
 */

export const ConstraintSetSchema = z.object({
  floor_checks: z.record(z.string(), z.boolean()), // F1, F2, F9, etc.
  hard_limits: z.record(z.string(), z.tuple([z.number(), z.number()])),
  governance_level: z.number().min(0).max(11).default(1)
});
export type ConstraintSet = z.infer<typeof ConstraintSetSchema>;

export const RiskAssessmentSchema = z.object({
  uncertainty_p10: z.number(),
  uncertainty_p50: z.number(),
  uncertainty_p90: z.number(),
  conflation_risk: z.number().min(0).max(1),
  mitigation_strategy: z.string().optional()
});
export type RiskAssessment = z.infer<typeof RiskAssessmentSchema>;

/**
 * AUDIT & LOGGING
 */

export const AuditEventSchema = z.object({
  timestamp: z.string().datetime(),
  author: z.string(),
  action: z.string(),
  verdict: VerdictEnum.optional(),
  note: z.string()
});
export type AuditEvent = z.infer<typeof AuditEventSchema>;

/**
 * COMPOSITE CONTRACTS
 */

export const VerdictContractSchema = z.object({
  verdict_id: z.string().uuid(),
  code: VerdictEnum,
  rationale: z.string(),
  constraints: ConstraintSetSchema,
  risk: RiskAssessmentSchema,
  audit: z.array(AuditEventSchema),
  sealed_by: z.string().optional(),
  sealed_at: z.string().datetime().optional()
});
export type VerdictContract = z.infer<typeof VerdictContractSchema>;
