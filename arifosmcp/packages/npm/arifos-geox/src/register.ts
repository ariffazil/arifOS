/**
 * @arifos/geox — Server-Side Tool Registration
 *
 * `registerTools()` binds the three canonical GEOX tools to an MCP Server
 * instance. Domain packages depend on @arifos/mcp for envelope shapes and
 * on @modelcontextprotocol/sdk for server primitives.
 *
 * Architecture: @arifos/geox imports from @arifos/mcp, never the reverse.
 */

import { z } from "zod";

import {
  dispatchGeoxTool,
  GEOX_TOOL_NAMES,
  type GeoxToolName,
} from "./tools.js";

// ═══════════════════════════════════════════════════════════════════════════════
// Generic Server Interface (decoupled from exact SDK version)
// ═══════════════════════════════════════════════════════════════════════════════

/** Minimal shape of an MCP server that accepts tool registrations. */
export interface McpServerLike {
  tool(
    name: string,
    description: string,
    paramsSchema: Record<string, z.ZodTypeAny>,
    handler: (args: Record<string, unknown>) => Promise<{ content: Array<{ type: string; text: string }> }>,
  ): void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Zod Schemas (mirrors TypeScript types for runtime validation)
// ═══════════════════════════════════════════════════════════════════════════════

export const PatternMatchInputSchema = z.object({
  dataset: z.string().min(1),
  pattern_type: z.enum([
    "coarsening_upward",
    "fining_upward",
    "blocky",
    "serrated",
    "cylindrical",
    "funnel",
    "bell",
    "organic_rich",
    "condensed_section",
    "custom",
  ]),
  curves: z.array(z.string()).optional(),
  depth_window: z
    .object({
      top: z.number(),
      base: z.number(),
    })
    .optional(),
  custom_pattern: z.record(z.unknown()).optional(),
  min_thickness: z.number().positive().optional(),
  session_id: z.string().optional(),
});

export const ReasonInputSchema = z.object({
  phase: z.enum(["synthesize", "abduct", "contradict", "full"]),
  evidence: z.array(
    z.object({
      source: z.string(),
      observation: z.string(),
      confidence: z.number().min(0).max(1),
      data_type: z.enum(["log", "seismic", "core", "biostrat", "geochemical", "analogue"]).optional(),
    }),
  ),
  hypotheses: z.array(z.string()).optional(),
  context: z.record(z.unknown()).optional(),
  session_id: z.string().optional(),
});

export const SynthesizeInputSchema = z.object({
  synthesis_type: z.enum([
    "prospect_summary",
    "reservoir_characterization",
    "stratigraphic_framework",
    "risk_assessment",
    "drill_plan",
    "custom",
  ]),
  sources: z.array(
    z.object({
      source_id: z.string(),
      source_type: z.enum(["well", "seismic", "map", "analogue", "report", "model"]),
      data: z.record(z.unknown()),
      weight: z.number().optional(),
    }),
  ),
  objective: z.string().optional(),
  constraints: z
    .object({
      max_sources: z.number().optional(),
      required_confidence: z.number().optional(),
      exclude_uncertain: z.boolean().optional(),
    })
    .optional(),
  session_id: z.string().optional(),
});

// ═══════════════════════════════════════════════════════════════════════════════
// registerTools()
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Register all canonical GEOX tools on an MCP Server instance.
 *
 * @param server — An MCP SDK server or any object conforming to McpServerLike
 * @returns The list of registered tool names
 *
 * @example
 * ```typescript
 * import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
 * import { registerTools } from "@arifos/geox/register";
 *
 * const server = new McpServer({ name: "geox-domain", version: "1.0.0" });
 * registerTools(server);
 * ```
 */
export function registerTools(server: McpServerLike): GeoxToolName[] {
  server.tool(
    "arif_geox_pattern_match",
    "Detect stratigraphic and geophysical patterns in well logs or seismic data using Physics-9 abduction grammar.",
    {
      dataset: z.string().describe("Well name, seismic volume ID, or dataset label"),
      pattern_type: z
        .enum([
          "coarsening_upward",
          "fining_upward",
          "blocky",
          "serrated",
          "cylindrical",
          "funnel",
          "bell",
          "organic_rich",
          "condensed_section",
          "custom",
        ])
        .describe("Type of stratigraphic or geophysical pattern to detect"),
      curves: z.array(z.string()).optional().describe("Curve names or data channels to inspect"),
      depth_window: z
        .object({ top: z.number(), base: z.number() })
        .optional()
        .describe("Depth or time window"),
      custom_pattern: z.record(z.unknown()).optional(),
      min_thickness: z.number().positive().optional(),
      session_id: z.string().optional(),
    },
    async (args) => {
      const envelope = dispatchGeoxTool("arif_geox_pattern_match", args as unknown as import("./types.js").PatternMatchInput);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(envelope),
          },
        ],
      };
    },
  );

  server.tool(
    "arif_geox_reason",
    "Run phase-driven evidence synthesis, abduction, and contradiction scanning on geological evidence.",
    {
      phase: z.enum(["synthesize", "abduct", "contradict", "full"]).describe("Workflow phase"),
      evidence: z
        .array(
          z.object({
            source: z.string(),
            observation: z.string(),
            confidence: z.number().min(0).max(1),
            data_type: z.enum(["log", "seismic", "core", "biostrat", "geochemical", "analogue"]).optional(),
          }),
        )
        .describe("Ordered evidence list (strongest first)"),
      hypotheses: z.array(z.string()).optional().describe("Starting hypotheses to test"),
      context: z.record(z.unknown()).optional(),
      session_id: z.string().optional(),
    },
    async (args) => {
      const envelope = dispatchGeoxTool("arif_geox_reason", args as unknown as import("./types.js").ReasonInput);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(envelope),
          },
        ],
      };
    },
  );

  server.tool(
    "arif_geox_synthesize",
    "Synthesize multi-source geoscience data into a coherent interpretation with gap detection.",
    {
      synthesis_type: z
        .enum([
          "prospect_summary",
          "reservoir_characterization",
          "stratigraphic_framework",
          "risk_assessment",
          "drill_plan",
          "custom",
        ])
        .describe("Type of synthesis to perform"),
      sources: z
        .array(
          z.object({
            source_id: z.string(),
            source_type: z.enum(["well", "seismic", "map", "analogue", "report", "model"]),
            data: z.record(z.unknown()),
            weight: z.number().optional(),
          }),
        )
        .describe("Source datasets to synthesize"),
      objective: z.string().optional().describe("Human-readable objective"),
      constraints: z
        .object({
          max_sources: z.number().optional(),
          required_confidence: z.number().optional(),
          exclude_uncertain: z.boolean().optional(),
        })
        .optional(),
      session_id: z.string().optional(),
    },
    async (args) => {
      const envelope = dispatchGeoxTool("arif_geox_synthesize", args as unknown as import("./types.js").SynthesizeInput);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(envelope),
          },
        ],
      };
    },
  );

  return [...GEOX_TOOL_NAMES];
}
