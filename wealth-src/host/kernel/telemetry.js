export async function emitTelemetry(state = {}) {
  const holds = state.holds ?? [];
  const violations = state.violations ?? [];

  return {
    epoch: new Date().toISOString(),
    qdf: "WEALTH:v1.0.0",
    peace2: state.peace2 ?? 1.0,
    confidence: state.confidence ?? 0.5,
    holds: holds.length,
    violations: violations.length,
    verdict: violations.length > 0
      ? "VOID"
      : holds.length > 0
        ? "888-HOLD"
        : "SEALED",
    sealed: Boolean(state.sealed),
  };
}
