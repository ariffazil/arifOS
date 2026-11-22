/**
 * @arifos/mcp - Main Entry Point
 *
 * Thin JavaScript/TypeScript MCP client for the arifOS governance kernel.
 *
 * Boundary:
 *   PyPI (`pip install arifos`) ships the authoritative Python kernel.
 *   npm (`npm install @arifos/mcp`) ships this JavaScript/TypeScript cable.
 *   MCP is the protocol through the cable.
 *   This package carries ZERO independent constitutional authority.
 *
 * DITEMPA BUKAN DIBERI — Forged, Not Given.
 */

export {
  createClient,
  quickConnect,
  DEFAULT_MCP_ENDPOINT,
  type ArifOSMCPClient,
  type Transport,
} from "./client.js";

export {
  CANONICAL_STAGE_VERBS,
  FLOOR_CODES,
  PUBLIC_STAGES,
  PUBLIC_TOOL_METADATA,
  PUBLIC_TOOL_NAMES,
  type ActionTier,
  type ArifForgeInput,
  type ArifInitInput,
  type ArifJudgeInput,
  type ArifMemoryInput,
  type ArifOSClientConfig,
  type ArifOSErrorCode,
  type ArifOSMetadata,
  type ArifOSToolName,
  type ArifOSTransport,
  type ArifObserveInput,
  type ArifReportInput,
  type ArifRouteInput,
  type ArifSealInput,
  type ArifThinkInput,
  type AuthContext,
  type AuthorityEnvelope,
  type CanonicalStageVerb,
  type FloorCode,
  type PublicToolDefinition,
  type ReceiptRecord,
  type RuntimeAuthority,
  type RuntimeEnvelope,
  type RuntimeErrorEntry,
  type RuntimeMeta,
  type RuntimeMetrics,
  type RuntimeStatus,
  type RuntimeTrace,
  type Stage,
  type ToolInputMap,
  type ToolMeta,
  type ToolPayloadMap,
  type Verdict,
  type VerdictEnvelope,
  type VerdictState,
  ArifOSError,
  isPublicToolName,
} from "./types.js";

// ── Shared Kernel Type Contracts (type-only mirrors for TS consumers) ──
export {
  type UncertaintyTag,
  type EvidenceItem,
  type SourceWeights,
  DEFAULT_SOURCE_WEIGHTS,
  type GovernanceScalars,
  type GovernanceState,
  type CollapseResult,
  type EvidenceFusion,
  type Phase,
  type Verdict as KernelVerdict,
  type TripwireId,
  type TripwireResult,
  type ExecutorReceipt,
  type ActionResult,
  type Organ,
  OMEGA_MAX,
  PSI_MIN,
  DELTA_CRITICAL,
  OMEGA_WARN,
  OMEGA_HARD_LIMIT,
} from "./kernel/index.js";

export const VERSION = "2026.11.22";

/**
 * Canonical public endpoints (verified 2026-11-22).
 */
export const ENDPOINTS = {
  /** Canonical hosted Streamable HTTP MCP endpoint. */
  MCP: "https://mcp.arif-fazil.com/mcp",
  /** Public health status endpoint. */
  HEALTH: "https://mcp.arif-fazil.com/health",
  /** Alias for MCP (kept for backwards compatibility with older callers). */
  VPS: "https://mcp.arif-fazil.com/mcp",
  /** Documentation & live observatory site. */
  DOCS: "https://arifos.arif-fazil.com",
  /** Authoritative Python kernel on PyPI. */
  PYPI: "https://pypi.org/project/arifos/",
  /** Canonical source repository. */
  REPO: "https://github.com/ariffazil/arifOS",
} as const;
