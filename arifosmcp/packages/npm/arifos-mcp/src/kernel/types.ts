/**
 * @arifos/kernel/types — Shared Type Contracts
 *
 * Canonical types shared between the Python kernel (judge) and
 * the TS A-FORGE executor. Python is the authoritative implementation;
 * these TS types are the contract surface for TS consumers.
 *
 * DITEMPA BUKAN DIBERI — Forged, Not Given.
 */

// ── Uncertainty Tags ──
export type UncertaintyTag =
  | "UNKNOWN"
  | "ESTIMATE"
  | "HYPOTHESIS"
  | "PLAUSIBLE"
  | "CLAIM";

// ── Verdicts ──
export type Verdict = "SEAL" | "SABAR" | "HOLD" | "VOID";

// ── Phases ──
export type Phase = 0 | 111 | 333 | 555 | 777 | 888 | 900 | 999;

// ── Evidence ──
export interface EvidenceItem {
  id: string;
  source: string;
  payload: unknown;
  uncertainty: UncertaintyTag;
  lineageId?: string;
  timestamp?: string;
}

// ── Source Weights ──
export interface SourceWeights {
  GEOX: number;
  WEALTH: number;
  WELL: number;
  LLM: number;
  QUANTUM: number;
  HUMAN: number;
}

export const DEFAULT_SOURCE_WEIGHTS: SourceWeights = {
  GEOX: 1.0,
  WEALTH: 0.85,
  WELL: 0.7,
  LLM: 0.4,
  QUANTUM: 0.5,
  HUMAN: 1.0,
};

// ── Tripwire ──
export type TripwireId =
  | "AUTHORITY"
  | "UNCERTAINTY"
  | "INTEGRITY"
  | "ENTROPY"
  | "REVERSIBILITY"
  | "FLOOR";

export interface TripwireResult {
  id: TripwireId;
  triggered: boolean;
  reason: string;
  severity: "BLOCK" | "DELAY" | "WARN";
}

// ── Governance Scalars ──
export interface GovernanceScalars {
  delta: number;
  omega: number;
  psi: number;
}

// ── Collapse Result ──
export interface EvidenceFusion {
  totalItems: number;
  sourceBreakdown: Record<string, number>;
  weightedOmega: number;
  sourceConsensus: "HIGH" | "MODERATE" | "LOW" | "CONFLICT";
}

export interface CollapseResult {
  verdict: Verdict;
  tripwires: TripwireResult[];
  scalars: GovernanceScalars;
  evidenceFusion: EvidenceFusion;
  timestamp: string;
}

// ── Governance State ──
export interface GovernanceState {
  phase: Phase;
  evidence: EvidenceItem[];
  scalars: GovernanceScalars;
  verdict?: Verdict;
  authorityPresent: boolean;
  reversible: boolean;
  timestamp: string;
  ccId?: string;
  sessionId?: string;
  actorId?: string;
  collapse?: CollapseResult;
}

// ── Organ Interface ──
export interface Organ {
  name: string;
  compute(input: unknown): Promise<EvidenceItem[]>;
}

// ── A-FORGE Executor Types ──
export interface ExecutorReceipt {
  verdict: Verdict;
  ccId: string;
  allowedActions: string[];
  bounds: {
    reversible: boolean;
    blastRadius: string;
    maxTools: number;
  };
  authority: {
    actorId: string;
    sessionId: string;
    validUntil: string;
  };
  lineage: {
    evidenceIds: string[];
    collapseTimestamp: string;
  };
}

export interface ActionResult {
  actionId: string;
  status: "SUCCESS" | "FAILURE" | "PARTIAL";
  tool: string;
  output: unknown;
  error?: string;
  timestamp: string;
}

// ── Thresholds ──
export const OMEGA_MAX = 0.4;
export const PSI_MIN = 0.7;
export const DELTA_CRITICAL = 0.7;
export const OMEGA_WARN = 0.3;
export const OMEGA_HARD_LIMIT = 0.6;
