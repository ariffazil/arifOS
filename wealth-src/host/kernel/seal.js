import { createHash } from "node:crypto";
import { emitTelemetry } from "./telemetry.js";

export async function seal999(state) {
  const epoch = state.epoch ?? new Date().toISOString();
  const violations = state.violations ?? [];
  const holds = state.holds ?? [];

  let verdict = "SEALED";
  if (violations.length > 0) verdict = "VOID";
  else if (holds.length > 0) verdict = "888-HOLD";
  else if ((state.peace2 ?? 1.0) < 1.0) verdict = "888-HOLD";
  else if (!state.human_confirmed && state.reversible === false) verdict = "888-HOLD";

  const sealed = verdict === "SEALED";
  const telemetry = await emitTelemetry({ ...state, epoch, verdict, sealed });
  const payload = { ...state, sealed, epoch, verdict };
  const integrity = createHash("sha256").update(JSON.stringify(payload)).digest("hex").slice(0, 16);

  return {
    ...payload,
    integrity_hash: integrity,
    telemetry,
    witness: { human: state.human_confirmed ?? false, ai: true, earth: true },
  };
}
