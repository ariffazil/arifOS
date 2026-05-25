/**
 * @arifos/geox — Tests
 *
 * Unit tests for envelope factories, validation, and dispatch.
 * Integration tests are skipped unless ARIFOS_TEST_ENDPOINT is set.
 */

import { describe, expect, it } from "vitest";
import {
  VERSION,
  GEOX_TOOL_NAMES,
  GEOX_TOOL_METADATA,
  isGeoxToolName,
  handlePatternMatch,
  handleReason,
  handleSynthesize,
  dispatchGeoxTool,
  createGeoxClient,
} from "../src/index.js";
import type { PatternMatchInput, ReasonInput, SynthesizeInput } from "../src/index.js";

describe("@arifos/geox public contract", () => {
  it("exports the correct version", () => {
    expect(VERSION).toBe("2026.05.25");
  });

  it("registers exactly 3 canonical tools", () => {
    expect(GEOX_TOOL_NAMES).toHaveLength(3);
    expect(GEOX_TOOL_NAMES).toEqual([
      "arif_geox_pattern_match",
      "arif_geox_reason",
      "arif_geox_synthesize",
    ]);
  });

  it("has metadata for every tool", () => {
    for (const name of GEOX_TOOL_NAMES) {
      expect(GEOX_TOOL_METADATA[name]).toBeDefined();
      expect(GEOX_TOOL_METADATA[name].stage).toBeTruthy();
      expect(typeof GEOX_TOOL_METADATA[name].readonly).toBe("boolean");
      expect(GEOX_TOOL_METADATA[name].description).toBeTruthy();
    }
  });

  it("validates geox tool names", () => {
    expect(isGeoxToolName("arif_geox_pattern_match")).toBe(true);
    expect(isGeoxToolName("arif_geox_reason")).toBe(true);
    expect(isGeoxToolName("arif_geox_synthesize")).toBe(true);
    expect(isGeoxToolName("arifOS_kernel")).toBe(false);
    expect(isGeoxToolName("unknown")).toBe(false);
  });
});

describe("arif_geox_pattern_match", () => {
  it("returns matches for a valid coarsening_upward request", () => {
    const input: PatternMatchInput = {
      dataset: "Well-A",
      pattern_type: "coarsening_upward",
      curves: ["GR", "RHOB"],
      depth_window: { top: 1500, base: 1550 },
    };

    const envelope = handlePatternMatch(input);

    expect(envelope.ok).toBe(true);
    expect(envelope.tool).toBe("arif_geox_pattern_match");
    expect(envelope.stage).toBe("111_SENSE");
    expect(envelope.payload.matches).toBeInstanceOf(Array);
    expect(envelope.payload.matches.length).toBeGreaterThan(0);
    expect(envelope.payload.summary.total_matches).toBe(envelope.payload.matches.length);
    expect(envelope.payload.summary.confidence_band).toBeDefined();
  });

  it("returns VOID for missing dataset", () => {
    const input = {
      pattern_type: "blocky",
    } as PatternMatchInput;

    const envelope = handlePatternMatch(input);

    expect(envelope.ok).toBe(false);
    expect(envelope.verdict).toBe("VOID");
    expect(envelope.errors.length).toBeGreaterThan(0);
  });

  it("returns empty matches for unknown pattern_type", () => {
    const input: PatternMatchInput = {
      dataset: "Well-B",
      pattern_type: "custom",
      custom_pattern: { unknown: true },
    };

    const envelope = handlePatternMatch(input);

    expect(envelope.ok).toBe(true);
    expect(envelope.payload.matches).toHaveLength(0);
  });
});

describe("arif_geox_reason", () => {
  it("runs full phase reasoning on valid evidence", () => {
    const input: ReasonInput = {
      phase: "full",
      evidence: [
        { source: "Well-A GR", observation: "Fining upward motif", confidence: 0.85, data_type: "log" },
        { source: "Seismic-V1", observation: "Amplitude dimming at 1200ms", confidence: 0.7, data_type: "seismic" },
        { source: "Core-12", observation: "Bioclastic packstone", confidence: 0.9, data_type: "core" },
      ],
      hypotheses: ["Channel fill", "Shoreface progradation"],
    };

    const envelope = handleReason(input);

    expect(envelope.ok).toBe(true);
    expect(envelope.tool).toBe("arif_geox_reason");
    expect(envelope.payload.phase).toBe("full");
    expect(envelope.payload.synthesis).toBeDefined();
    expect(envelope.payload.abductions).toBeInstanceOf(Array);
    expect(envelope.payload.contradictions).toBeInstanceOf(Array);
    expect(envelope.payload.verdict).toBeDefined();
  });

  it("returns VOID for empty evidence", () => {
    const input = {
      phase: "synthesize",
      evidence: [],
    } as ReasonInput;

    const envelope = handleReason(input);

    expect(envelope.ok).toBe(false);
    expect(envelope.verdict).toBe("VOID");
  });

  it("returns VOID for missing phase", () => {
    const input = {
      evidence: [{ source: "X", observation: "Y", confidence: 0.5 }],
    } as ReasonInput;

    const envelope = handleReason(input);

    expect(envelope.ok).toBe(false);
    expect(envelope.verdict).toBe("VOID");
  });
});

describe("arif_geox_synthesize", () => {
  it("synthesizes multiple sources", () => {
    const input: SynthesizeInput = {
      synthesis_type: "prospect_summary",
      sources: [
        { source_id: "Well-A", source_type: "well", data: { porosity: 0.18 }, weight: 1.0 },
        { source_id: "Seismic-V1", source_type: "seismic", data: { amplitude: "bright" }, weight: 0.8 },
        { source_id: "Analogue-B", source_type: "analogue", data: { field: "X-field" }, weight: 0.6 },
      ],
      objective: "Evaluate prospect viability",
    };

    const envelope = handleSynthesize(input);

    expect(envelope.ok).toBe(true);
    expect(envelope.tool).toBe("arif_geox_synthesize");
    expect(envelope.payload.synthesis).toContain("Synthesized");
    expect(Object.keys(envelope.payload.source_weights)).toHaveLength(3);
    expect(envelope.payload.recommended_next_steps.length).toBeGreaterThan(0);
  });

  it("returns VOID for missing synthesis_type", () => {
    const input = {
      sources: [{ source_id: "A", source_type: "well", data: {} }],
    } as SynthesizeInput;

    const envelope = handleSynthesize(input);

    expect(envelope.ok).toBe(false);
    expect(envelope.verdict).toBe("VOID");
  });

  it("returns VOID for empty sources", () => {
    const input = {
      synthesis_type: "custom",
      sources: [],
    } as SynthesizeInput;

    const envelope = handleSynthesize(input);

    expect(envelope.ok).toBe(false);
    expect(envelope.verdict).toBe("VOID");
  });
});

describe("dispatchGeoxTool", () => {
  it("routes pattern_match correctly", () => {
    const envelope = dispatchGeoxTool("arif_geox_pattern_match", {
      dataset: "Well-A",
      pattern_type: "blocky",
    });

    expect(envelope.tool).toBe("arif_geox_pattern_match");
    expect(envelope.ok).toBe(true);
  });

  it("routes reason correctly", () => {
    const envelope = dispatchGeoxTool("arif_geox_reason", {
      phase: "synthesize",
      evidence: [{ source: "A", observation: "B", confidence: 0.8 }],
    });

    expect(envelope.tool).toBe("arif_geox_reason");
    expect(envelope.ok).toBe(true);
  });

  it("routes synthesize correctly", () => {
    const envelope = dispatchGeoxTool("arif_geox_synthesize", {
      synthesis_type: "drill_plan",
      sources: [{ source_id: "A", source_type: "well", data: {} }],
    });

    expect(envelope.tool).toBe("arif_geox_synthesize");
    expect(envelope.ok).toBe(true);
  });
});

describe("createGeoxClient (type contract)", () => {
  it("wraps an MCP client with typed methods", () => {
    // Minimal mock — enough to satisfy the type contract
    const mockMcp = {
      callTool: async (_name: string, _params: Record<string, unknown>) => ({
        ok: true,
        tool: _name,
        session_id: "mock-session",
        stage: "111_SENSE",
        verdict: "SEAL",
        status: "SUCCESS",
        metrics: {},
        trace: {},
        authority: {},
        payload: {},
        errors: [],
        meta: {},
      }),
    } as unknown as import("../src/client.js").GeoxClient["mcp"];

    const geox = createGeoxClient(mockMcp);

    expect(geox.mcp).toBe(mockMcp);
    expect(typeof geox.patternMatch).toBe("function");
    expect(typeof geox.reason).toBe("function");
    expect(typeof geox.synthesize).toBe("function");
  });
});
