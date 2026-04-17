/**
 * Verdict — Constitutional verdict types
 * DITEMPA BUKAN DIBERI
 */

export enum Verdict {
  PROCEED = "PROCEED",   // Low risk, constitution satisfied
  HOLD = "HOLD",         // Elevated risk, human review required (888_HOLD)
  BLOCK = "BLOCK",       // Critical risk, constitution violated
  SEAL = "SEAL",         // Terminal verdict, VAULT999 recorded
  VOID = "VOID",         // Action not permitted, constitution breach
}

export enum VerdictStatus {
  PENDING = "PENDING",
  APPROVED = "APPROVED",
  REJECTED = "REJECTED",
  EXPIRED = "EXPIRED",
}

export function isTerminalVerdict(v: Verdict): boolean {
  return [Verdict.SEAL, Verdict.BLOCK, Verdict.VOID].includes(v);
}

export function requiresHumanReview(v: Verdict): boolean {
  return v === Verdict.HOLD;
}