/**
 * arifOS Judge Tool
 * 
 * OpenClaw tool that calls arifOS apex_judge via MCP JSON-RPC.
 * 
 * BOUNDARY: This is adapter code only. No constitutional logic.
 * All governance (F1-F13, ΔΩΨ, verdicts) happens in arifOS.
 */

import { apexJudge, ApexJudgeResult } from '../mcp-client.js';

export interface ArifOSJudgeInput {
  query: string;
  actor_id?: string;
  session_id?: string;
  context?: string;
}

/**
 * Call arifOS apex_judge for constitutional verdict.
 * 
 * This function does NOT evaluate floors. It asks arifOS to do so.
 * The verdict (SEAL/VOID/PARTIAL/SABAR/888_HOLD) comes from arifOS.
 */
export async function arifOSJudgeTool(input: ArifOSJudgeInput): Promise<ApexJudgeResult> {
  const result = await apexJudge({
    query: input.query,
    actor_id: input.actor_id,
    session_id: input.session_id,
    context: input.context,
  });

  return result;
}

export default arifOSJudgeTool;
