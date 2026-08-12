/**
 * REALITY GATE — Structural Enforcement of Gödel Rule 4
 * 
 * "Reality is the final auditor. Reasoning can drift. Reality does not negotiate."
 * 
 * Every claim entering RSI TRACE must carry:
 *   1. Raw tool return value (not the agent's interpretation)
 *   2. Post-action probe (read-after-write, curl-after-change)
 *   3. Session ID in which verification occurred
 * 
 * If ANY of these are missing → claim is UNVERIFIED
 *   → cannot enter LEDGER
 *   → cannot SEAL
 *   → cannot CARRY FORWARD
 * 
 * This is NOT a doctrine. It is a gate. The gate does not ask
 * "is this allowed?" — it asks "did this actually happen?"
 * 
 * @author 333-AGI
 * @forged 2026-08-12
 * @constitutional_trigger Scar: sovereign rediscovery tax
 * @godel_rule E4 — Reality Is The Final Auditor
 */

import * as crypto from 'crypto';

// ═══════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════

/**
 * The three mandatory components of a verified claim.
 * Missing ANY one → UNVERIFIED.
 */
interface VerifiedClaim {
  // (1) Raw tool output — the actual return value, not the agent's summary
  tool_output: {
    tool_name: string;           // e.g. "forge_shell", "forge_filesystem"
    raw_return: string;          // the actual tool output verbatim
    exit_code?: number;          // for shell commands
    timestamp: string;           // ISO 8601
  };

  // (2) Post-action probe — a SEPARATE read to confirm reality changed
  post_action_probe: {
    probe_type: 'read_after_write' | 'curl_after_change' | 'hash_after_deploy' | 'ls_after_mkdir' | 'content_after_edit';
    probe_command: string;       // the verification command/query
    probe_result: string;        // what the probe returned
    probe_matches_expectation: boolean;  // does the probe confirm the change?
    timestamp: string;
  };

  // (3) Session binding — which session performed the verification
  verification_context: {
    session_id: string;          // from arif_init
    actor_id: string;            // who verified
    constitutional_chain_id?: string;  // cc_id if this was judge-gated
  };
}

/**
 * RSI Ledger entry WITH reality verification.
 * Extends the existing ledger format with the Reality Gate fields.
 */
interface VerifiedRSIEntry {
  // Existing fields (backward compatible)
  ts: string;
  prev_hash: string;
  event: string;
  turn: number;
  sessionID: string;
  actor: string;
  self_hash: string;

  // Reality Gate fields (NEW)
  reality_gate: {
    status: 'VERIFIED' | 'UNVERIFIED' | 'PARTIAL';
    tool_output_present: boolean;
    post_probe_present: boolean;
    session_binding_present: boolean;
    verification_score: number;  // 0.0 - 1.0 (must be 1.0 to pass)
    rejection_reason?: string;   // if UNVERIFIED, why
  };

  // Evidence chain
  claim: string;                 // what the agent claims happened
  evidence: {
    raw_tool_output?: string;
    post_probe_output?: string;
    expectation?: string;        // what the agent predicted would happen
    delta_s?: number;            // entropy change (if measurable)
  };

  // Existing RSI fields
  improvements_proposed: number;
  last_delta_s: number;
}

// ═══════════════════════════════════════════════════════
// THE GATE
// ═══════════════════════════════════════════════════════

/**
 * Validate a claim against the Reality Gate.
 * Returns VERIFIED only if all three components are present and consistent.
 * 
 * This is the structural enforcement of Gödel Rule 4.
 */
export function validateRealityGate(claim: VerifiedClaim): {
  status: 'VERIFIED' | 'UNVERIFIED' | 'PARTIAL';
  score: number;
  failures: string[];
} {
  const failures: string[] = [];

  // Gate 1: Tool output must be raw, not interpreted
  if (!claim.tool_output) {
    failures.push('MISSING_TOOL_OUTPUT: No raw tool return recorded. Agent claims without evidence.');
  } else if (!claim.tool_output.raw_return || claim.tool_output.raw_return.trim().length === 0) {
    failures.push('EMPTY_TOOL_OUTPUT: Tool output field exists but is empty. Phantom claim.');
  } else if (isInterpreted(claim.tool_output.raw_return)) {
    failures.push('INTERPRETED_OUTPUT: Tool output appears to be agent interpretation, not raw return. Must contain verbatim tool response.');
  }

  // Gate 2: Post-action probe must confirm the change
  if (!claim.post_action_probe) {
    failures.push('MISSING_POST_PROBE: No read-after-write verification. Change may be phantom.');
  } else if (!claim.post_action_probe.probe_result || claim.post_action_probe.probe_result.trim().length === 0) {
    failures.push('EMPTY_POST_PROBE: Post-action probe returned empty. Cannot confirm reality changed.');
  } else if (!claim.post_action_probe.probe_matches_expectation) {
    failures.push('PROBE_MISMATCH: Post-action probe did not match expectation. Reality diverged from claim.');
  }

  // Gate 3: Session binding must be present
  if (!claim.verification_context) {
    failures.push('MISSING_SESSION_BINDING: No session context. Cannot attribute verification to a session.');
  } else if (!claim.verification_context.session_id) {
    failures.push('EMPTY_SESSION_ID: Session binding exists but session_id is empty.');
  }

  // Compute score
  const gate1 = claim.tool_output?.raw_return?.trim().length > 0 && !isInterpreted(claim.tool_output?.raw_return || '') ? 1 : 0;
  const gate2 = claim.post_action_probe?.probe_matches_expectation ? 1 : 0;
  const gate3 = claim.verification_context?.session_id?.trim().length > 0 ? 1 : 0;
  const score = (gate1 + gate2 + gate3) / 3;

  // Status
  let status: 'VERIFIED' | 'UNVERIFIED' | 'PARTIAL';
  if (score === 1.0) {
    status = 'VERIFIED';
  } else if (score >= 0.667) {
    status = 'PARTIAL'; // 2 of 3 — ledger-eligible but not seal-eligible
  } else {
    status = 'UNVERIFIED';
  }

  return { status, score, failures };
}

/**
 * Check if tool output looks like agent interpretation rather than raw return.
 * Heuristic: if it contains phrases like "I confirmed", "the fix works",
 * "everything is correct" without raw command output → likely interpreted.
 */
function isInterpreted(output: string): boolean {
  const interpretationPatterns = [
    /^(I|we)\s+(confirmed|verified|checked|validated|ensured)/i,
    /^(the fix|the change|the update)\s+(works|is live|is applied|is confirmed)/i,
    /^(everything|all)\s+(is|looks)\s+(correct|good|fine|ok)/i,
    /^(✅|✓|☑)\s*(confirmed|verified|working)/i,
    /^Done\.\s*ΔS=/,  // response shape without evidence
  ];

  // If output is VERY short and matches interpretation patterns → likely interpreted
  if (output.length < 200) {
    return interpretationPatterns.some(p => p.test(output.trim()));
  }

  return false;
}

// ═══════════════════════════════════════════════════════
// RSI ENTRY FACTORY
// ═══════════════════════════════════════════════════════

/**
 * Create a verified RSI entry. This is what goes into the ledger.
 * If the Reality Gate fails, the entry is still recorded but marked UNVERIFIED
 * and CANNOT be promoted to SEAL or CARRY FORWARD.
 */
export function createVerifiedRSIEntry(
  claim: string,
  evidence: VerifiedClaim,
  previousHash: string,
  turn: number,
  improvementsProposed: number,
  deltaS: number,
): VerifiedRSIEntry {
  const validation = validateRealityGate(evidence);

  const entry: VerifiedRSIEntry = {
    ts: new Date().toISOString(),
    prev_hash: previousHash,
    event: 'turn_rsi.verified',  // NEW event type — distinct from 'turn_rsi.pulse'
    turn,
    sessionID: evidence.verification_context.session_id,
    actor: evidence.verification_context.actor_id,
    self_hash: '', // computed below

    reality_gate: {
      status: validation.status,
      tool_output_present: !!evidence.tool_output?.raw_return,
      post_probe_present: !!evidence.post_action_probe?.probe_matches_expectation,
      session_binding_present: !!evidence.verification_context?.session_id,
      verification_score: validation.score,
      rejection_reason: validation.failures.length > 0 ? validation.failures.join('; ') : undefined,
    },

    claim,
    evidence: {
      raw_tool_output: evidence.tool_output?.raw_return,
      post_probe_output: evidence.post_action_probe?.probe_result,
      expectation: evidence.post_action_probe?.probe_command,
      delta_s: deltaS,
    },

    improvements_proposed: improvementsProposed,
    last_delta_s: deltaS,
  };

  // Compute hash
  const hashInput = JSON.stringify({
    ts: entry.ts,
    prev_hash: entry.prev_hash,
    event: entry.event,
    turn: entry.turn,
    sessionID: entry.sessionID,
    claim: entry.claim,
    reality_gate: entry.reality_gate,
  });
  entry.self_hash = crypto.createHash('sha256').update(hashInput).digest('hex').slice(0, 16);

  return entry;
}

// ═══════════════════════════════════════════════════════
// PROMOTION GATES
// ═══════════════════════════════════════════════════════

/**
 * Can this RSI entry be promoted to SEAL?
 * Only VERIFIED entries can seal. PARTIAL can ledger. UNVERIFIED cannot promote.
 */
export function canSeal(entry: VerifiedRSIEntry): { allowed: boolean; reason: string } {
  if (entry.reality_gate.status === 'VERIFIED') {
    return { allowed: true, reason: 'All three Reality Gate checks passed.' };
  }

  if (entry.reality_gate.status === 'PARTIAL') {
    return {
      allowed: false,
      reason: `Reality Gate PARTIAL (${(entry.reality_gate.verification_score * 100).toFixed(0)}%). Missing: ${entry.reality_gate.rejection_reason}. Cannot seal without full verification.`,
    };
  }

  return {
    allowed: false,
    reason: `Reality Gate UNVERIFIED. ${entry.reality_gate.rejection_reason}. This claim has no evidence of reality contact.`,
  };
}

/**
 * Can this RSI entry carry forward to the next session?
 * UNVERIFIED entries cannot carry forward — they are phantom claims.
 */
export function canCarryForward(entry: VerifiedRSIEntry): { allowed: boolean; reason: string } {
  if (entry.reality_gate.status === 'UNVERIFIED') {
    return {
      allowed: false,
      reason: `UNVERIFIED claims cannot carry forward. They are phantom claims that will compound the rediscovery tax.`,
    };
  }

  return { allowed: true, reason: `Reality Gate ${entry.reality_gate.status}. Eligible for carry-forward.` };
}

// ═══════════════════════════════════════════════════════
// EXAMPLE — Sabah Basin Reality Check
// ═══════════════════════════════════════════════════════

/*
 * EXAMPLE: Agent claims "Fixed the P50/P90 epistemic drift issue."
 *
 * WITHOUT Reality Gate:
 *   RSI entry: { event: "turn_rsi.pulse", improvements_proposed: 1, delta_s: -0.3 }
 *   → Ledger accepts. Agent moves on. Problem recurs.
 *
 * WITH Reality Gate:
 *   Agent must provide:
 *   1. Tool output: "geox_geox_prospect(mode=evaluate, ...) → returned truth_class: DER, witness_count: 3"
 *   2. Post-probe: "Read the prospect record → confirmed witness_count=3 in the returned object"
 *   3. Session: "Verified in session SEAL-d37cba515a474c52 by actor 333-AGI"
 *
 *   → Reality Gate: VERIFIED (1.0)
 *   → Can seal: YES
 *   → Can carry forward: YES
 *
 * If agent only provides interpretation ("The fix works"):
 *   → Reality Gate: UNVERIFIED (0.0)
 *   → Can seal: NO
 *   → Can carry forward: NO
 *   → Sovereign does NOT pay rediscovery tax.
 */
