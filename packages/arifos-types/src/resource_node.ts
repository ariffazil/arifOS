/**
 * ResourceNode — 4-layer decision kernel
 * Geology → Engineering → Economics → Governance
 * DITEMPA BUKAN DIBERI
 */

import { EpistemicTag } from "./epistemic.js";

export interface ResourceNode {
  id: string;
  decision_context: DecisionContext;
  geology: GeologyNode;
  engineering: EngineeringNode;
  economics: EconomicsNode;
  governance: GovernanceNode;
}

export interface DecisionContext {
  jurisdiction: string;
  analysis_date: string;
  market_regime: string;
  model_version: string;
}

export interface GeologyNode {
  volume_p10?: number;
  volume_p50: number;
  volume_p90?: number;
  quality_index: number;
  depth_m: number;
  structure_complexity: number;
  seal_confidence?: number;
  charge_confidence?: number;
  recoverability_confidence?: number;
  risk_geo: number;
  epistemic_geo?: EpistemicTag;
  petrophys_source?: PetrophysSource;
}

export interface EngineeringNode {
  recovery_factor: number;
  capex_usd: number;
  opex_usd_per_unit: number;
  uptime?: number;
  cycle_time_months: number;
  infrastructure_distance_km?: number;
}

export interface EconomicsNode {
  price_model: string;
  discount_rate: number;
  fiscal_terms: string;
  npv_usd?: number;
  irr?: number;
  breakeven_usd_per_unit?: number;
  sigma_market?: number;
}

export interface GovernanceNode {
  policy_state: string;
  admissibility_status: "admissible" | "deferred" | "blocked";
  carbon_cost_usd_per_tco2e?: number;
  compliance_cost_usd?: number;
  delay_risk?: number;
  required_modifications?: string[];
  sigma_policy?: number;
  penalty_infinite?: boolean;
  peace2?: number;
  maruah_score?: number;
}

export interface PetrophysSource {
  well_id: string;
  depth_interval: [number, number];
  n_net_pay_samples: number;
  epistemic: EpistemicTag;
  model: string;
}

export function createEmptyResourceNode(id: string): ResourceNode {
  return {
    id,
    decision_context: {
      jurisdiction: "",
      analysis_date: new Date().toISOString().split("T")[0],
      market_regime: "",
      model_version: "v0.1",
    },
    geology: {
      volume_p50: 0,
      quality_index: 0,
      depth_m: 0,
      structure_complexity: 0,
      risk_geo: 1,
    },
    engineering: {
      recovery_factor: 0,
      capex_usd: 0,
      opex_usd_per_unit: 0,
      cycle_time_months: 0,
    },
    economics: {
      price_model: "",
      discount_rate: 0.1,
      fiscal_terms: "",
    },
    governance: {
      policy_state: "",
      admissibility_status: "deferred",
    },
  };
}