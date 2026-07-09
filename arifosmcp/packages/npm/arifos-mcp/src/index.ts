/**
 * @arifos/mcp - Main Entry Point
 *
 * Public 8-tool MCP client adapter for model-agnostic integrations.
 * Plus shared kernel type contracts for TS consumers (A-FORGE, AAA).
 *
 * The kernel logic itself lives in Python at:
 *   /root/arifOS/arifosmcp/runtime/kernel/
 *
 * DITEMPA BUKAN DIBERI — Forged, Not Given.
 */

export {
  createClient,
  quickConnect,
  type ArifOSMCPClient,
  type Transport,
} from "./client.js";

export {
  PUBLIC_STAGES,
  PUBLIC_TOOL_METADATA,
  PUBLIC_TOOL_NAMES,
  type ArifOSClientConfig,
  type ArifOSKernelInput,
  type ArifOSMetadata,
  type ArifOSToolName,
  type ArifOSTransport,
  type AuthContext,
  type AuditRulesInput,
  type BootstrapIdentityInput,
  type CheckVitalInput,
  type FloorCode,
  type IngestEvidenceInput,
  type OpenApexDashboardInput,
  type PublicToolDefinition,
  type RuntimeAuthority,
  type RuntimeEnvelope,
  type RuntimeErrorEntry,
  type RuntimeMeta,
  type RuntimeMetrics,
  type RuntimeStatus,
  type RuntimeTrace,
  type SearchRealityInput,
  type SessionMemoryInput,
  type Stage,
  type ToolInputMap,
  type ToolMeta,
  type ToolPayloadMap,
  type Verdict,
  type VerdictEnvelope,
  ArifOSError,
  isPublicToolName,
} from "./types.js";

// ── Shared Kernel Type Contracts (for TS consumers) ──
export {
  // Evidence & uncertainty
  type UncertaintyTag,
  type EvidenceItem,
  type SourceWeights,
  DEFAULT_SOURCE_WEIGHTS,
  // Governance
  type GovernanceScalars,
  type GovernanceState,
  type CollapseResult,
  type EvidenceFusion,
  // Phases & verdicts
  type Phase,
  type Verdict as KernelVerdict,
  // Tripwires
  type TripwireId,
  type TripwireResult,
  // A-FORGE executor
  type ExecutorReceipt,
  type ActionResult,
  // Organ interface
  type Organ,
  // Thresholds
  OMEGA_MAX,
  PSI_MIN,
  DELTA_CRITICAL,
  OMEGA_WARN,
  OMEGA_HARD_LIMIT,
} from "./kernel/index.js";

/**
 * Package version.
 */
export const VERSION = "0.6.0";

/**
 * Compatible runtime labels.
 */
export const ARIFOS_COMPATIBILITY = [
  "2026.03.10-FORGED",
  "2026.03.12-FORGED",
] as const;

/**
 * Canonical public endpoints.
 */
export const ENDPOINTS = {
  VPS: "https://arifosmcp.arif-fazil.com/mcp",
  HEALTH: "https://arifosmcp.arif-fazil.com/health",
  DISCOVERY: "https://arifosmcp.arif-fazil.com/.well-known/mcp/server.json",
  DASHBOARD: "https://arifosmcp.arif-fazil.com/dashboard/",
  DOCS: "https://arifos.arif-fazil.com/public-contract",
} as const;
