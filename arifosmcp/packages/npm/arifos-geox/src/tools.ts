/**
 * @arifos/geox — Tool Definitions & Handlers
 *
 * Pure domain logic: schemas, validation, and handler skeletons for the
 * three canonical GEOX tools. Handlers are intentionally thin — they
 * structure input and emit a RuntimeEnvelope-shaped result.
 *
 * For server registration, use `registerTools()` from `./register.js`.
 * For client invocation, use `GeoxClient` from `./client.js`.
 */

import {
  ArifOSError,
  type RuntimeEnvelope,
  type RuntimeErrorEntry,
  type RuntimeMeta,
  type RuntimeStatus,
  type RuntimeTrace,
  type RuntimeAuthority,
  type RuntimeMetrics,
} from "@arifos/mcp/types";

import {
  GEOX_TOOL_METADATA,
  type GeoxToolName,
  type PatternMatchInput,
  type PatternMatchResult,
  type PatternMatch,
  type ReasonInput,
  type ReasonResult,
  type AbductionResult,
  type ContradictionResult,
  type SynthesizeInput,
  type SynthesizeResult,
  type GeoxToolInputMap,
  type GeoxToolPayloadMap,
} from "./types.js";

export {
  GEOX_TOOL_NAMES,
  GEOX_TOOL_METADATA,
  type GeoxToolName,
  type PatternMatchInput,
  type PatternMatchResult,
  type ReasonInput,
  type ReasonResult,
  type SynthesizeInput,
  type SynthesizeResult,
} from "./types.js";

// ═══════════════════════════════════════════════════════════════════════════════
// Envelope Factory
// ═══════════════════════════════════════════════════════════════════════════════

function createGeoxEnvelope<TPayload>(
  tool: GeoxToolName,
  payload: TPayload,
  options: {
    ok?: boolean;
    verdict?: RuntimeEnvelope<TPayload>["verdict"];
    status?: RuntimeStatus;
    errors?: RuntimeErrorEntry[];
    session_id?: string | null;
  } = {},
): RuntimeEnvelope<TPayload> {
  const meta: RuntimeMeta = {
    schema_version: "2026.05.25",
    timestamp: new Date().toISOString(),
    motto: "DITEMPA BUKAN DIBERI",
  };

  const trace: RuntimeTrace = {
    [tool]: options.verdict ?? "SEAL",
  };

  const authority: RuntimeAuthority = {
    level: "agent",
    human_required: false,
  };

  const metrics: RuntimeMetrics = {
    confidence: 0.85,
    clarity_delta: 0.0,
    entropy_delta: 0.0,
  };

  return {
    ok: options.ok ?? true,
    tool,
    session_id: options.session_id ?? null,
    stage: GEOX_TOOL_METADATA[tool].stage,
    verdict: options.verdict ?? "SEAL",
    status: options.status ?? "SUCCESS",
    metrics,
    trace,
    authority,
    payload,
    errors: options.errors ?? [],
    meta,
    auth_context: null,
    caller_context: null,
    user_model: null,
    philosophy: null,
    debug: null,
  };
}

function createGeoxErrorEnvelope<TPayload>(
  tool: GeoxToolName,
  code: string,
  message: string,
  session_id?: string | null,
): RuntimeEnvelope<TPayload> {
  return createGeoxEnvelope<TPayload>(tool, {} as TPayload, {
    ok: false,
    verdict: "VOID",
    status: "ERROR",
    errors: [{ code, message, stage: GEOX_TOOL_METADATA[tool].stage, recoverable: true }],
    session_id,
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// arif_geox_pattern_match — Handler
// ═══════════════════════════════════════════════════════════════════════════════

export function handlePatternMatch(
  input: PatternMatchInput,
): RuntimeEnvelope<PatternMatchResult> {
  try {
    validatePatternMatchInput(input);

    // Deterministic stub — in production this calls the Python geox_mcp engine
    const matches: PatternMatch[] = simulatePatternMatches(input);

    const result: PatternMatchResult = {
      matches,
      summary: {
        total_matches: matches.length,
        dominant_pattern:
          matches.length > 0
            ? modeString(matches.map((m) => m.pattern_name))
            : null,
        confidence_band:
          matches.length > 0 && matches.every((m) => m.confidence > 0.7)
            ? "high"
            : matches.some((m) => m.confidence > 0.5)
              ? "medium"
              : "low",
      },
    };

    return createGeoxEnvelope("arif_geox_pattern_match", result, {
      session_id: input.session_id ?? null,
    });
  } catch (cause) {
    const message = cause instanceof Error ? cause.message : String(cause);
    return createGeoxErrorEnvelope<PatternMatchResult>(
      "arif_geox_pattern_match",
      "VALIDATION_ERROR",
      message,
      input.session_id ?? null,
    );
  }
}

function validatePatternMatchInput(input: PatternMatchInput): void {
  if (!input.dataset || typeof input.dataset !== "string") {
    throw new ArifOSError("dataset is required and must be a string", "INVALID_RESPONSE");
  }
  if (!input.pattern_type) {
    throw new ArifOSError("pattern_type is required", "INVALID_RESPONSE");
  }
  if (
    input.depth_window &&
    (typeof input.depth_window.top !== "number" || typeof input.depth_window.base !== "number")
  ) {
    throw new ArifOSError("depth_window top and base must be numbers", "INVALID_RESPONSE");
  }
}

function simulatePatternMatches(input: PatternMatchInput): PatternMatch[] {
  // Physics-9 abduction grammar stub — deterministic for test stability
  const grammar: Record<
    string,
    { curves: string[]; thickness_m: number; confidence: number; candidates?: unknown[] }
  > = {
    coarsening_upward: {
      curves: ["GR", "RHOB"],
      thickness_m: 12.5,
      confidence: 0.82,
      candidates: [
        { process: "shoreface progradation", mechanism: "sediment supply exceeded accommodation", prior: 0.35 },
        { process: "delta front mouth bar", mechanism: "fluvial input into standing water", prior: 0.25 },
      ],
    },
    fining_upward: {
      curves: ["GR", "NPHI"],
      thickness_m: 8.3,
      confidence: 0.76,
      candidates: [
        { process: "channel fill", mechanism: "fluvial or tidal channel abandonment", prior: 0.4 },
        { process: "crevasse splay", mechanism: "levee breach during flood", prior: 0.2 },
      ],
    },
    blocky: {
      curves: ["GR"],
      thickness_m: 5.0,
      confidence: 0.68,
    },
    organic_rich: {
      curves: ["GR", "RHOB", "RT"],
      thickness_m: 3.2,
      confidence: 0.71,
    },
  };

  const def = grammar[input.pattern_type];
  if (!def) return [];

  const top = input.depth_window?.top ?? 1000;
  return [
    {
      pattern_name: input.pattern_type,
      top_depth: top,
      base_depth: top + def.thickness_m,
      thickness_m: def.thickness_m,
      confidence: def.confidence,
      curves_used: input.curves ?? def.curves,
      required_context: ["regional_correlation", "biostrat"],
      candidates: (def.candidates as PatternMatch["candidates"]) ?? undefined,
    },
  ];
}

// ═══════════════════════════════════════════════════════════════════════════════
// arif_geox_reason — Handler
// ═══════════════════════════════════════════════════════════════════════════════

export function handleReason(input: ReasonInput): RuntimeEnvelope<ReasonResult> {
  try {
    validateReasonInput(input);

    const abductions: AbductionResult[] =
      input.hypotheses?.map((h, i) => ({
        hypothesis: h,
        posterior: Math.max(0.1, 0.9 - i * 0.15),
        supporting_evidence: input.evidence.slice(0, 2).map((e) => e.source),
        missing_context: [],
        rank: i + 1,
      })) ?? [];

    const contradictions: ContradictionResult[] = [];
    if (input.evidence.length >= 2) {
      const last = input.evidence[input.evidence.length - 1];
      const first = input.evidence[0];
      if (last.confidence < 0.3 && first.confidence > 0.8) {
        contradictions.push({
          claim_a: first.observation,
          claim_b: last.observation,
          severity: "minor",
          resolution_hint: "Reconcile low-confidence outlier with high-confidence anchor evidence.",
        });
      }
    }

    const result: ReasonResult = {
      phase: input.phase,
      synthesis:
        input.phase === "synthesize" || input.phase === "full"
          ? `Synthesized ${input.evidence.length} evidence items into a coherent geological interpretation.`
          : undefined,
      abductions: input.phase === "abduct" || input.phase === "full" ? abductions : undefined,
      contradictions:
        input.phase === "contradict" || input.phase === "full" ? contradictions : undefined,
      verdict: contradictions.length > 0 ? "inconsistent" : "consistent",
      confidence: input.evidence.reduce((sum, e) => sum + e.confidence, 0) / input.evidence.length,
    };

    return createGeoxEnvelope("arif_geox_reason", result, {
      session_id: input.session_id ?? null,
    });
  } catch (cause) {
    const message = cause instanceof Error ? cause.message : String(cause);
    return createGeoxErrorEnvelope<ReasonResult>(
      "arif_geox_reason",
      "VALIDATION_ERROR",
      message,
      input.session_id ?? null,
    );
  }
}

function validateReasonInput(input: ReasonInput): void {
  if (!input.phase) {
    throw new ArifOSError("phase is required", "INVALID_RESPONSE");
  }
  if (!Array.isArray(input.evidence) || input.evidence.length === 0) {
    throw new ArifOSError("evidence must be a non-empty array", "INVALID_RESPONSE");
  }
  for (const item of input.evidence) {
    if (!item.source || !item.observation) {
      throw new ArifOSError("each evidence item requires source and observation", "INVALID_RESPONSE");
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// arif_geox_synthesize — Handler
// ═══════════════════════════════════════════════════════════════════════════════

export function handleSynthesize(
  input: SynthesizeInput,
): RuntimeEnvelope<SynthesizeResult> {
  try {
    validateSynthesizeInput(input);

    const totalWeight = input.sources.reduce((sum, s) => sum + (s.weight ?? 1), 0);
    const sourceWeights: Record<string, number> = {};
    for (const s of input.sources) {
      sourceWeights[s.source_id] = (s.weight ?? 1) / totalWeight;
    }

    const result: SynthesizeResult = {
      synthesis: `Synthesized ${input.sources.length} sources for objective: ${input.objective ?? input.synthesis_type}.`,
      source_weights: sourceWeights,
      gaps: input.sources.length < 3 ? ["insufficient_well_data", "missing_seismic_tie"] : [],
      confidence: Math.min(0.95, input.sources.reduce((sum, s) => sum + (s.weight ?? 1), 0) / 10),
      recommended_next_steps: ["acquire_additional_well_data", "run_geox_evidence_reason"],
    };

    return createGeoxEnvelope("arif_geox_synthesize", result, {
      session_id: input.session_id ?? null,
    });
  } catch (cause) {
    const message = cause instanceof Error ? cause.message : String(cause);
    return createGeoxErrorEnvelope<SynthesizeResult>(
      "arif_geox_synthesize",
      "VALIDATION_ERROR",
      message,
      input.session_id ?? null,
    );
  }
}

function validateSynthesizeInput(input: SynthesizeInput): void {
  if (!input.synthesis_type) {
    throw new ArifOSError("synthesis_type is required", "INVALID_RESPONSE");
  }
  if (!Array.isArray(input.sources) || input.sources.length === 0) {
    throw new ArifOSError("sources must be a non-empty array", "INVALID_RESPONSE");
  }
  for (const s of input.sources) {
    if (!s.source_id || !s.source_type) {
      throw new ArifOSError("each source requires source_id and source_type", "INVALID_RESPONSE");
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Dispatch Router
// ═══════════════════════════════════════════════════════════════════════════════

export function dispatchGeoxTool<N extends GeoxToolName>(
  name: N,
  params: GeoxToolInputMap[N],
): RuntimeEnvelope<GeoxToolPayloadMap[N]> {
  switch (name) {
    case "arif_geox_pattern_match":
      return handlePatternMatch(params as PatternMatchInput) as RuntimeEnvelope<GeoxToolPayloadMap[N]>;
    case "arif_geox_reason":
      return handleReason(params as ReasonInput) as RuntimeEnvelope<GeoxToolPayloadMap[N]>;
    case "arif_geox_synthesize":
      return handleSynthesize(params as SynthesizeInput) as RuntimeEnvelope<GeoxToolPayloadMap[N]>;
    default: {
      const exhaustive: never = name;
      throw new ArifOSError(`Unknown GEOX tool: ${exhaustive}`, "INVALID_RESPONSE");
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Utilities
// ═══════════════════════════════════════════════════════════════════════════════

function modeString(values: string[]): string | null {
  const counts = new Map<string, number>();
  for (const v of values) {
    counts.set(v, (counts.get(v) ?? 0) + 1);
  }
  let best: string | null = null;
  let bestCount = 0;
  for (const [k, c] of counts) {
    if (c > bestCount) {
      best = k;
      bestCount = c;
    }
  }
  return best;
}
