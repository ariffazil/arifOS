export const FLOORS = {
  F1: "Amanah — reversible or explicitly irreversible",
  F2: "Truth — epistemic tag required",
  F3: "Input Clarity — clear task definition",
  F4: "Clarity — reduce complexity",
  F5: "Peace — no unresolved panic",
  F6: "Maruah — dignity as variable",
  F7: "Humility — uncertainty band",
  F8: "Law — local-first data",
  F9: "Anti-Hantu — no phantom entries",
  F10: "AI Only Advises — human decides",
  F11: "Auth — PIN for critical",
  F12: "No Override — floors unbypassable",
  F13: "Human Veto — final authority",
};

export const EPISTEMIC = Object.freeze({
  CLAIM: "CLAIM",
  PLAUSIBLE: "PLAUSIBLE",
  HYPOTHESIS: "HYPOTHESIS",
  ESTIMATE: "ESTIMATE",
  UNKNOWN: "UNKNOWN",
});

export const HOLD = {
  type: "888_HOLD",
  reason: "Human confirmation required for irreversible or high-risk operation.",
};

export function checkFloors(args) {
  const violations = [];
  const holds = [];
  const warnings = [];

  if (args.reversible === false && !args.human_confirmed) {
    holds.push("F1: 888_HOLD — Irreversible action requires human confirmation.");
  }
  if (args.epistemic === "UNKNOWN") {
    warnings.push("F2: Epistemic state is UNKNOWN.");
  }
  if (args.ai_is_deciding) {
    violations.push("F10: AI cannot be the final decision maker.");
  }
  if (args.floor_override) {
    violations.push("F12: Floor override is not permitted.");
  }
  if ((args.peace2 ?? 1.0) < 1.0) {
    holds.push("F5: Peace² below 1.0.");
  }

  let verdict = "SEAL";
  if (violations.length > 0) verdict = "VOID";
  else if (holds.length > 0) verdict = "HOLD";
  else if (warnings.length > 0) verdict = "CAUTION";

  return {
    pass: verdict === "SEAL" || verdict === "CAUTION",
    verdict,
    violations,
    holds,
    warnings,
    epistemic: args.epistemic ?? "ESTIMATE",
    vault_log_entry: { tool: "wealth_check_floors", epoch: new Date().toISOString() },
    witness: { human: false, ai: true, earth: true },
  };
}
