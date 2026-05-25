/**
 * @arifos/geox — Main Entry Point
 *
 * Domain package for geoscience intelligence. Depends on @arifos/mcp
 * for governance envelopes and transport.
 *
 * DITEMPA BUKAN DIBERI — Forged, Not Given
 */

export {
  GEOX_TOOL_NAMES,
  GEOX_TOOL_METADATA,
  isGeoxToolName,
  type GeoxToolName,
  type GeoxToolMeta,
  type PatternMatchInput,
  type PatternMatchResult,
  type PatternMatch,
  type PatternCandidate,
  type PatternType,
  type ReasonInput,
  type ReasonResult,
  type ReasonPhase,
  type AbductionResult,
  type ContradictionResult,
  type EvidenceItem,
  type SynthesizeInput,
  type SynthesizeResult,
  type SynthesisType,
  type SynthesisSource,
  type GeoxToolInputMap,
  type GeoxToolPayloadMap,
  type PatternMatchEnvelope,
  type ReasonEnvelope,
  type SynthesizeEnvelope,
} from "./types.js";

export {
  handlePatternMatch,
  handleReason,
  handleSynthesize,
  dispatchGeoxTool,
} from "./tools.js";

export { createGeoxClient, type GeoxClient } from "./client.js";

export { registerTools, type McpServerLike } from "./register.js";

/**
 * Package version.
 */
export const VERSION = "2026.05.25";

/**
 * Compatible @arifos/mcp versions.
 */
export const MCP_COMPATIBILITY = [">=0.5.0"] as const;

/**
 * Canonical GEOX public endpoints.
 */
export const ENDPOINTS = {
  VPS: "https://geox.arif-fazil.com/mcp",
  HEALTH: "https://geox.arif-fazil.com/health",
  DISCOVERY: "https://geox.arif-fazil.com/.well-known/mcp/server.json",
  DOCS: "https://geox.arif-fazil.com/public-contract",
} as const;
