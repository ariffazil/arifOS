/**
 * @arifos/geox — Client Wrappers
 *
 * Typed convenience methods that invoke GEOX tools through an
 * @arifos/mcp client connection. These wrappers handle envelope
 * parsing and carry auth_context/session_id automatically.
 */

import {
  type RuntimeEnvelope,
  ArifOSError,
} from "@arifos/mcp/types";
import type { ArifOSMCPClient } from "@arifos/mcp/client";

import {
  type GeoxToolInputMap,
  type GeoxToolPayloadMap,
  type PatternMatchInput,
  type PatternMatchResult,
  type ReasonInput,
  type ReasonResult,
  type SynthesizeInput,
  type SynthesizeResult,
} from "./types.js";

export {
  type PatternMatchInput,
  type PatternMatchResult,
  type ReasonInput,
  type ReasonResult,
  type SynthesizeInput,
  type SynthesizeResult,
} from "./types.js";

// ═══════════════════════════════════════════════════════════════════════════════
// GeoxClient
// ═══════════════════════════════════════════════════════════════════════════════

export interface GeoxClient {
  readonly mcp: ArifOSMCPClient;
  patternMatch(
    params: PatternMatchInput,
  ): Promise<RuntimeEnvelope<PatternMatchResult>>;
  reason(params: ReasonInput): Promise<RuntimeEnvelope<ReasonResult>>;
  synthesize(
    params: SynthesizeInput,
  ): Promise<RuntimeEnvelope<SynthesizeResult>>;
}

/**
 * Wrap an existing @arifos/mcp client with GEOX-typed convenience methods.
 *
 * The underlying client is reused — no new connection is opened.
 * session_id and auth_context are carried forward automatically by
 * the base client.
 *
 * @example
 * ```typescript
 * import { createClient } from "@arifos/mcp";
 * import { createGeoxClient } from "@arifos/geox/client";
 *
 * const mcp = await createClient({ transport: "http", endpoint: "..." });
 * await mcp.connect();
 *
 * const geox = createGeoxClient(mcp);
 * const result = await geox.patternMatch({
 *   dataset: "Well-A",
 *   pattern_type: "coarsening_upward",
 *   curves: ["GR", "RHOB"],
 * });
 *
 * console.log(result.payload.matches);
 * ```
 */
export function createGeoxClient(mcp: ArifOSMCPClient): GeoxClient {
  async function callGeoxTool<N extends keyof GeoxToolInputMap>(
    name: N,
    params: GeoxToolInputMap[N],
  ): Promise<RuntimeEnvelope<GeoxToolPayloadMap[N]>> {
    try {
      // The base @arifos/mcp client is typed to the 8 public tools.
      // Domain tools bypass that contract via the raw MCP client.
      const envelope = await (mcp.callTool as (
        n: string,
        p: Record<string, unknown>,
      ) => Promise<RuntimeEnvelope<Record<string, unknown>>>)(
        name,
        params as unknown as Record<string, unknown>,
      );
      return envelope as unknown as RuntimeEnvelope<GeoxToolPayloadMap[N]>;
    } catch (cause) {
      if (cause instanceof ArifOSError) {
        throw cause;
      }
      throw new ArifOSError(
        `GEOX tool call failed: ${name}`,
        "INVALID_RESPONSE",
        undefined,
        undefined,
        cause,
      );
    }
  }

  return {
    mcp,

    async patternMatch(
      params: PatternMatchInput,
    ): Promise<RuntimeEnvelope<PatternMatchResult>> {
      return callGeoxTool("arif_geox_pattern_match", params);
    },

    async reason(params: ReasonInput): Promise<RuntimeEnvelope<ReasonResult>> {
      return callGeoxTool("arif_geox_reason", params);
    },

    async synthesize(
      params: SynthesizeInput,
    ): Promise<RuntimeEnvelope<SynthesizeResult>> {
      return callGeoxTool("arif_geox_synthesize", params);
    },
  };
}
