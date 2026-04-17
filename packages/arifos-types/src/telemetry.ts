/**
 * TelemetryPayload — Structured telemetry for VAULT999 sealing
 * DITEMPA BUKAN DIBERI
 */

import { Verdict } from "./verdict.js";
import { EpistemicTag } from "./epistemic.js";

export type PipelineStage =
  | "000_INIT"
  | "111_SENSE"
  | "222_THINK"
  | "333_EXPLORE"
  | "444_PLAN"
  | "555_HEART"
  | "666_MIND"
  | "777_REASON"
  | "888_JUDGE"
  | "999_SEAL";

export interface Witness {
  human: string;
  ai: string;
  earth: string;
}

export interface TelemetryPayload {
  epoch: number;
  session_id: string;
  pipeline_stage: PipelineStage;
  dS: number;
  peace2: number;
  kappa_r: number;
  shadow: number;
  confidence: number;
  psi_le: number;
  verdict: Verdict;
  witness: Witness;
  qdf: number;
  floor_violations: string[];
  epistemic?: EpistemicTag;
  hash: string;
}

export function createTelemetryHash(payload: Omit<TelemetryPayload, "hash">): string {
  const { epoch, session_id, pipeline_stage, verdict, qdf, peace2 } = payload;
  const input = `${epoch}${session_id}${pipeline_stage}${verdict}${qdf}${peace2}`;
  return hashString(input);
}

function hashString(input: string): string {
  let hash = 0;
  for (let i = 0; i < input.length; i++) {
    const char = input.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16).padStart(16, "0");
}

export const DEFAULT_TELEMETRY: Partial<TelemetryPayload> = {
  dS: 0.1,
  peace2: 1.0,
  kappa_r: 0.8,
  shadow: 0.1,
  confidence: 0.8,
  psi_le: 0.8,
  qdf: 0.8,
  floor_violations: [],
};