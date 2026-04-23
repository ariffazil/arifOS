/**
 * FloorResult — Constitutional floor evaluation result
 * DITEMPA BUKAN DIBERI
 */

export interface FloorViolation {
  floor: string;
  gate: string;
  description: string;
  severity: "warning" | "hold" | "critical";
}

export interface FloorResult {
  pass: boolean;
  verdict: "SEAL" | "QUALIFY" | "HOLD" | "VOID";
  floors_checked: string[];
  violations: FloorViolation[];
  holds: string[];
  warnings: string[];
  maruah_band: string;
}

export const FLOOR_NAMES: Record<string, string> = {
  F1: "Amanah",
  F2: "Truth",
  F3: "Tri-Witness",
  F4: "ΔS Clarity",
  F5: "Peace²",
  F6: "κᵣ Empathy",
  F7: "Ω₀ Humility",
  F8: "G Genius",
  F9: "Ethics",
  F10: "Conscience",
  F11: "Audit",
  F12: "Injection",
  F13: "Sovereign",
};

export const FLOOR_ORDER = [
  "F1", "F2", "F3", "F4", "F5", "F6",
  "F7", "F8", "F9", "F10", "F11", "F12", "F13",
];