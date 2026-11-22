/**
 * @arifos/mcp - Public Wire Contract Types
 *
 * Thin TypeScript mirrors for the live arifOS MCP wire contract.
 * This package carries ZERO governance authority: all constitutional
 * evaluation (F1-F13) and receipt sealing happen server-side in the
 * Python arifOS kernel (`pip install arifos`).
 *
 * Canonical wire surface (9 tools = 8 canonical stage verbs + arif_report),
 * verified against live https://mcp.arif-fazil.com/mcp tools/list.
 */

export const CANONICAL_STAGE_VERBS = [
  "arif_init",
  "arif_observe",
  "arif_think",
  "arif_route",
  "arif_memory",
  "arif_judge",
  "arif_forge",
  "arif_seal",
] as const;

export const PUBLIC_TOOL_NAMES = [
  ...CANONICAL_STAGE_VERBS,
  "arif_report",
] as const;

export type CanonicalStageVerb = (typeof CANONICAL_STAGE_VERBS)[number];
export type ArifOSToolName = (typeof PUBLIC_TOOL_NAMES)[number];

export const PUBLIC_TOOL_METADATA = {
  arif_init: {
    stage: "000_INIT",
    readonly: false,
    description: "Ignite or resume a governed session and bind actor identity.",
  },
  arif_observe: {
    stage: "111_OBSERVE",
    readonly: true,
    description: "Probe reality and collect labeled evidence (OBS/DER/INT/SPEC).",
  },
  arif_think: {
    stage: "333_THINK",
    readonly: true,
    description: "Run structured reasoning under F2/F7 before proposing an action.",
  },
  arif_route: {
    stage: "444_ROUTE",
    readonly: true,
    description: "Route an intent to the appropriate organ or governed next step.",
  },
  arif_memory: {
    stage: "555_MEMORY",
    readonly: false,
    description: "Recall, store, or promote governed institutional memory.",
  },
  arif_judge: {
    stage: "666_JUDGE",
    readonly: true,
    description: "Evaluate a proposed action against F1-F13 and return a verdict.",
  },
  arif_forge: {
    stage: "777_FORGE",
    readonly: false,
    description: "Execute an approved action (requires a prior SEAL verdict).",
  },
  arif_seal: {
    stage: "999_SEAL",
    readonly: false,
    description: "Append an auditable receipt or session closure to VAULT999.",
  },
  arif_report: {
    stage: "REPORT",
    readonly: false,
    description: "File, read, or acknowledge governed operational reports.",
  },
} as const satisfies Record<
  ArifOSToolName,
  {
    stage: string;
    readonly: boolean;
    description: string;
  }
>;

/**
 * Primary verdict lattice mirrored from arifosmcp/models/verdicts.py
 * and arifosmcp/runtime/apex_canonical.py.
 * Ordered: VOID > HOLD_888 > HOLD > SABAR > PARTIAL > PROVISIONAL > SEAL.
 */
export type Verdict =
  | "SEAL"
  | "PROVISIONAL"
  | "PARTIAL"
  | "SABAR"
  | "HOLD"
  | "HOLD_888"
  | "VOID";

/**
 * Fine-grained kernel VerdictState values observed in arifosmcp/models/verdicts.py.
 */
export type VerdictState =
  | "SEAL_CANONICAL"
  | "SEAL_QUALIFIED"
  | "WORK_DONE"
  | "WAITING_FOR_WITNESS"
  | "HOLD_888"
  | "HOLD_UNCERTAINTY"
  | "HOLD_TEMPORAL"
  | "VOID_BREACH"
  | "VOID_HANTU"
  | "VOID_IRREVERSIBLE"
  | "SABAR_EPISTEMIC"
  | "SABAR_GEOPOLITICAL"
  | "PARTIAL_DERIVED"
  | "PARTIAL_REVERSIBILITY";

export type RuntimeStatus = "SUCCESS" | "ERROR" | "TIMEOUT" | "DRY_RUN";

export const FLOOR_CODES = [
  "F1",
  "F2",
  "F3",
  "F4",
  "F5",
  "F6",
  "F7",
  "F8",
  "F9",
  "F10",
  "F11",
  "F12",
  "F13",
] as const;

export type FloorCode = (typeof FLOOR_CODES)[number];

export const PUBLIC_STAGES = [
  "000_INIT",
  "111_OBSERVE",
  "333_THINK",
  "444_ROUTE",
  "555_MEMORY",
  "666_JUDGE",
  "777_FORGE",
  "999_SEAL",
  "REPORT",
] as const;

export type Stage = (typeof PUBLIC_STAGES)[number] | (string & {});

/**
 * Transparent payload mirror for caller authority metadata sent to the kernel.
 * Presenting these fields NEVER grants authority client-side; the Python
 * kernel independently verifies or holds every request.
 */
export type ActionTier = "T1" | "T2" | "T3" | "standard" | "irreversible" | (string & {});

export interface AuthorityEnvelope {
  actor_id?: string | null;
  session_id?: string | null;
  session_token?: string | null;
  authority_token?: string | null;
  actor_signature?: string | null;
  key_id?: string | null;
  nonce?: string | null;
  requested_authority?: string;
  action_tier?: ActionTier;
  ack_irreversible?: boolean;
}

/**
 * Transparent payload mirror for kernel-issued receipt fields.
 * Distinct from proposal, authorization, execution, and human acceptance.
 */
export interface ReceiptRecord {
  receipt_id?: string;
  trace_id?: string;
  verdict?: Verdict | VerdictState | string;
  session_id?: string | null;
  vault_hash?: string;
  entry_hash?: string;
  prev_hash?: string;
  timestamp?: string;
  [key: string]: unknown;
}

export interface RuntimeMetrics {
  truth?: number;
  clarity_delta?: number;
  confidence?: number;
  peace?: number;
  vitality?: number;
  entropy_delta?: number;
  authority?: number;
  risk?: number;
  [key: string]: unknown;
}

export type RuntimeTrace = Partial<Record<string, Verdict>> & Record<string, Verdict | undefined>;

export interface RuntimeAuthority {
  actor_id?: string;
  level?: string;
  autonomy_band?: string;
  human_required?: boolean;
  approval_scope?: string[];
  auth_state?: string;
  [key: string]: unknown;
}

export interface RuntimeErrorEntry {
  code: string;
  message: string;
  stage?: string | null;
  recoverable?: boolean;
  [key: string]: unknown;
}

export interface RuntimeMeta {
  schema_version?: string;
  timestamp?: string;
  debug?: boolean;
  dry_run?: boolean;
  motto?: string | null;
  [key: string]: unknown;
}

export interface AuthContext {
  session_id: string;
  actor_id?: string;
  session_token?: string;
  authority_level?: string;
  [key: string]: unknown;
}

/**
 * Transparent response mirror returned by a kernel tool call.
 */
export interface RuntimeEnvelope<TPayload = Record<string, unknown>> {
  ok?: boolean;
  tool?: ArifOSToolName | string;
  session_id?: string | null;
  session_token?: string | null;
  stage?: Stage;
  verdict?: Verdict | VerdictState | string;
  status?: RuntimeStatus | string;
  trace_id?: string;
  receipt?: ReceiptRecord | null;
  metrics?: RuntimeMetrics;
  trace?: RuntimeTrace;
  authority?: RuntimeAuthority;
  payload?: TPayload;
  errors?: RuntimeErrorEntry[];
  meta?: RuntimeMeta;
  auth_context?: AuthContext | null;
  [key: string]: unknown;
}

export type VerdictEnvelope<TPayload = Record<string, unknown>> = RuntimeEnvelope<TPayload>;

export interface ArifOSMetadata {
  session_id: string | null;
  tool: ArifOSToolName | string;
  version: string;
  stage: Stage;
  verdict: Verdict | VerdictState | string;
  timestamp: string;
}

export type ArifOSTransport = "stdio" | "http";

export interface ArifOSClientConfig {
  transport: ArifOSTransport;
  /** Streamable HTTP MCP endpoint URL. Defaults to ENDPOINTS.MCP when transport is "http". */
  endpoint?: string;
  /** Optional command override for stdio transport (default: "arifos-mcp"). */
  command?: string;
  /** Optional args override for stdio transport (default: []). */
  args?: string[];
  /** Environment variables for stdio transport. */
  env?: Record<string, string>;
  timeout?: number;
  debug?: boolean;
}

// ── Per-tool input mirrors (matching live tools/list inputSchema) ──────────

export interface ArifInitInput extends AuthorityEnvelope {
  intent: string;
  mode?:
    | "init"
    | "light"
    | "resume"
    | "validate"
    | "canary"
    | "preflight"
    | "triage"
    | "epoch_open"
    | "epoch_seal"
    | "opt_out"
    | "opt_out_profiling"
    | "challenge";
  context?: Record<string, unknown>;
  evidence?: Record<string, unknown> | Array<Record<string, unknown>>;
  tooling?: string[] | Record<string, unknown>;
  agent_policy?: Record<string, unknown>;
  verbosity?: "minimal" | "standard" | "full";
}

export interface ArifObserveInput extends AuthorityEnvelope {
  mode?: string;
  query?: string;
  url?: string;
  uri?: string;
  layers?: string[];
  result_limit?: number;
}

export interface ArifThinkInput extends AuthorityEnvelope {
  mode?: string;
  query?: string;
  plan_id?: string;
  witness_type?: string;
  context?: Record<string, unknown>;
  evidence?: Record<string, unknown> | Array<Record<string, unknown>>;
}

export interface ArifRouteInput extends AuthorityEnvelope {
  intent?: string;
  mode?: string;
  organ?: string;
  task?: string;
  organ_tool?: string;
  arguments?: Record<string, unknown>;
  mission_id?: string;
}

export interface ArifMemoryInput extends AuthorityEnvelope {
  mode?: string;
  query?: string;
  memory_id?: string;
  content?: string;
  tier?: string;
  to_tier?: string;
  new_content?: string;
  human_approval?: boolean;
  payload?: Record<string, unknown>;
}

export interface ArifJudgeInput extends AuthorityEnvelope {
  candidate: string;
  mode?: string;
  context_source?: string;
  evidence?: Record<string, unknown> | Array<Record<string, unknown>>;
}

export interface ArifForgeInput extends AuthorityEnvelope {
  mode?: string;
  manifest?: Record<string, unknown>;
  seal_verdict_id?: string;
  approved_action_hash?: string;
  query?: string;
  artifact_id?: string;
}

export interface ArifSealInput extends AuthorityEnvelope {
  mode?: string;
  payload?: string | Record<string, unknown>;
  constitutional_chain_id?: string;
  judge_state_hash?: string;
  witness_type?: string;
}

export interface ArifReportInput extends AuthorityEnvelope {
  mode?: string;
  kind?: string;
  subject?: string;
  body?: string;
  sender?: string;
  thread_id?: string;
  evidence?: Record<string, unknown> | Array<Record<string, unknown>>;
  needs_human?: boolean;
  report_id?: string;
  since?: string;
}

export interface ToolInputMap {
  arif_init: ArifInitInput;
  arif_observe: ArifObserveInput;
  arif_think: ArifThinkInput;
  arif_route: ArifRouteInput;
  arif_memory: ArifMemoryInput;
  arif_judge: ArifJudgeInput;
  arif_forge: ArifForgeInput;
  arif_seal: ArifSealInput;
  arif_report: ArifReportInput;
}

export interface ToolPayloadMap {
  arif_init: Record<string, unknown>;
  arif_observe: Record<string, unknown>;
  arif_think: Record<string, unknown>;
  arif_route: Record<string, unknown>;
  arif_memory: Record<string, unknown>;
  arif_judge: Record<string, unknown>;
  arif_forge: Record<string, unknown>;
  arif_seal: Record<string, unknown>;
  arif_report: Record<string, unknown>;
}

export interface PublicToolDefinition {
  name: ArifOSToolName;
  description?: string;
  inputSchema?: unknown;
  outputSchema?: unknown;
  annotations?: {
    readOnlyHint?: boolean;
    [key: string]: unknown;
  };
}

export type ToolMeta = typeof PUBLIC_TOOL_METADATA;

export type ArifOSErrorCode =
  | "CONNECTION_FAILED"
  | "TIMEOUT"
  | "INVALID_RESPONSE"
  | "TRANSPORT_ERROR";

export class ArifOSError extends Error {
  constructor(
    message: string,
    public readonly code: ArifOSErrorCode,
    public readonly stage?: Stage,
    public readonly floor?: FloorCode,
    public readonly cause?: unknown,
  ) {
    super(message);
    this.name = "ArifOSError";
  }
}

export function isPublicToolName(value: string): value is ArifOSToolName {
  return (PUBLIC_TOOL_NAMES as readonly string[]).includes(value);
}
