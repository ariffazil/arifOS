/**
 * @arifos/geox — Domain Types
 *
 * Typed schemas for GEOX geoscience tools. These map to the Python-side
 * geox_mcp registry but are expressed as TypeScript contracts for
 * model-agnostic clients and servers.
 */

import type { RuntimeEnvelope } from "@arifos/mcp";

// ═══════════════════════════════════════════════════════════════════════════════
// Tool Name Registry
// ═══════════════════════════════════════════════════════════════════════════════

export const GEOX_TOOL_NAMES = [
  "arif_geox_pattern_match",
  "arif_geox_reason",
  "arif_geox_synthesize",
] as const;

export type GeoxToolName = (typeof GEOX_TOOL_NAMES)[number];

export function isGeoxToolName(value: string): value is GeoxToolName {
  return GEOX_TOOL_NAMES.includes(value as GeoxToolName);
}

// ═══════════════════════════════════════════════════════════════════════════════
// arif_geox_pattern_match — Subsurface Pattern Recognition
// ═══════════════════════════════════════════════════════════════════════════════

export type PatternType =
  | "coarsening_upward"
  | "fining_upward"
  | "blocky"
  | "serrated"
  | "cylindrical"
  | " funnel"
  | "bell"
  | "organic_rich"
  | "condensed_section"
  | "custom";

export interface PatternMatchInput {
  /** Well name, seismic volume ID, or dataset label */
  dataset: string;
  /** Type of stratigraphic or geophysical pattern to detect */
  pattern_type: PatternType;
  /** Curve names or data channels to inspect (e.g., ["GR", "RHOB", "NPHI"]) */
  curves?: string[];
  /** Depth or time window in metres or milliseconds */
  depth_window?: { top: number; base: number };
  /** Optional custom pattern definition for pattern_type === "custom" */
  custom_pattern?: Record<string, unknown>;
  /** Minimum thickness threshold (m) */
  min_thickness?: number;
  /** Session continuity token */
  session_id?: string;
}

export interface PatternMatchResult {
  matches: PatternMatch[];
  summary: {
    total_matches: number;
    dominant_pattern: string | null;
    confidence_band: "high" | "medium" | "low";
  };
}

export interface PatternMatch {
  pattern_name: string;
  top_depth: number;
  base_depth: number;
  thickness_m: number;
  confidence: number;
  curves_used: string[];
  required_context: string[];
  candidates?: PatternCandidate[];
}

export interface PatternCandidate {
  process: string;
  mechanism: string;
  prior: number;
  required_context: string[];
}

export type PatternMatchEnvelope = RuntimeEnvelope<PatternMatchResult>;

// ═══════════════════════════════════════════════════════════════════════════════
// arif_geox_reason — Evidence-Based Geological Reasoning
// ═══════════════════════════════════════════════════════════════════════════════

export type ReasonPhase = "synthesize" | "abduct" | "contradict" | "full";

export interface EvidenceItem {
  source: string;
  observation: string;
  confidence: number;
  data_type?: "log" | "seismic" | "core" | "biostrat" | "geochemical" | "analogue";
}

export interface ReasonInput {
  /** Phase-driven workflow: synthesize → abduct → contradict */
  phase: ReasonPhase;
  /** Ordered evidence list (strongest first) */
  evidence: EvidenceItem[];
  /** Starting hypotheses to test against evidence */
  hypotheses?: string[];
  /** Contextual constraints (basin type, depositional setting, etc.) */
  context?: Record<string, unknown>;
  /** Session continuity token */
  session_id?: string;
}

export interface ReasonResult {
  phase: ReasonPhase;
  synthesis?: string;
  abductions?: AbductionResult[];
  contradictions?: ContradictionResult[];
  verdict: "consistent" | "inconsistent" | "inconclusive";
  confidence: number;
}

export interface AbductionResult {
  hypothesis: string;
  posterior: number;
  supporting_evidence: string[];
  missing_context: string[];
  rank: number;
}

export interface ContradictionResult {
  claim_a: string;
  claim_b: string;
  severity: "critical" | "major" | "minor";
  resolution_hint: string;
}

export type ReasonEnvelope = RuntimeEnvelope<ReasonResult>;

// ═══════════════════════════════════════════════════════════════════════════════
// arif_geox_synthesize — Multi-Source Geoscience Synthesis
// ═══════════════════════════════════════════════════════════════════════════════

export type SynthesisType =
  | "prospect_summary"
  | "reservoir_characterization"
  | "stratigraphic_framework"
  | "risk_assessment"
  | "drill_plan"
  | "custom";

export interface SynthesisSource {
  source_id: string;
  source_type: "well" | "seismic" | "map" | "analogue" | "report" | "model";
  data: Record<string, unknown>;
  weight?: number;
}

export interface SynthesizeInput {
  synthesis_type: SynthesisType;
  sources: SynthesisSource[];
  /** Human-readable objective for the synthesis */
  objective?: string;
  /** Constraints to enforce during synthesis */
  constraints?: {
    max_sources?: number;
    required_confidence?: number;
    exclude_uncertain?: boolean;
  };
  /** Session continuity token */
  session_id?: string;
}

export interface SynthesizeResult {
  synthesis: string;
  source_weights: Record<string, number>;
  gaps: string[];
  confidence: number;
  recommended_next_steps: string[];
}

export type SynthesizeEnvelope = RuntimeEnvelope<SynthesizeResult>;

// ═══════════════════════════════════════════════════════════════════════════════
// Tool Input / Payload Maps
// ═══════════════════════════════════════════════════════════════════════════════

export interface GeoxToolInputMap {
  arif_geox_pattern_match: PatternMatchInput;
  arif_geox_reason: ReasonInput;
  arif_geox_synthesize: SynthesizeInput;
}

export interface GeoxToolPayloadMap {
  arif_geox_pattern_match: PatternMatchResult;
  arif_geox_reason: ReasonResult;
  arif_geox_synthesize: SynthesizeResult;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Tool Metadata
// ═══════════════════════════════════════════════════════════════════════════════

export const GEOX_TOOL_METADATA = {
  arif_geox_pattern_match: {
    stage: "111_SENSE",
    readonly: true,
    description:
      "Detect stratigraphic and geophysical patterns in well logs or seismic data using Physics-9 abduction grammar.",
  },
  arif_geox_reason: {
    stage: "333_MIND",
    readonly: true,
    description:
      "Run phase-driven evidence synthesis, abduction, and contradiction scanning on geological evidence.",
  },
  arif_geox_synthesize: {
    stage: "333_MIND",
    readonly: true,
    description:
      "Synthesize multi-source geoscience data into a coherent interpretation with gap detection.",
  },
} as const satisfies Record<
  GeoxToolName,
  {
    stage: string;
    readonly: boolean;
    description: string;
  }
>;

export type GeoxToolMeta = typeof GEOX_TOOL_METADATA;
