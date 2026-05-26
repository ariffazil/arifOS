/**
 * @arifos/geox — Tests
 *
 * Unit tests for envelope factories, validation, dispatch, and the
 * 6-layer Nobel-grade AGI Earth governance gates.
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
  // Governance imports
  runPhysicsGuard,
  DEFAULT_PHYSICS_LOCKS,
  createUncertaintyBand,
  enforceUncertainty,
  auditHallucination,
  enforceCitationOrUnknown,
  applyDecisionFirewall,
  isHighRiskDomain,
  HIGH_RISK_DOMAINS,
  buildHoldManifest,
  runDisciplinePanel,
  scanTrauma,
  formatTraumaWarning,
  TRAUMA_REGISTRY,
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

// ═══════════════════════════════════════════════════════════════════════════════
// Layer 1 — Physics Guard
// ═══════════════════════════════════════════════════════════════════════════════

describe("Layer 1: Physics Guard", () => {
  it("auto-FAILS shale porosity > 25% below 3000 m", () => {
    const result = runPhysicsGuard({
      porosity: 0.35,
      depth_m: 4000,
      lithology: "shale",
    });
    expect(result.passed).toBe(false);
    expect(result.fatal).toBe(true);
    expect(result.violations[0].constraint).toBe("shale_porosity_depth");
  });

  it("passes valid shale porosity", () => {
    const result = runPhysicsGuard({
      porosity: 0.15,
      depth_m: 4000,
      lithology: "shale",
    });
    expect(result.passed).toBe(true);
    expect(result.fatal).toBe(false);
  });

  it("detects mass balance violation", () => {
    const result = runPhysicsGuard({
      water_influx: 100,
      cumulative_production: 1000,
      fluid_expansion: 50,
    });
    expect(result.passed).toBe(false);
    expect(result.violations[0].constraint).toBe("mass_balance");
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Layer 2 — Uncertainty
// ═══════════════════════════════════════════════════════════════════════════════

describe("Layer 2: Uncertainty", () => {
  it("creates P10/P50/P90 band", () => {
    const band = createUncertaintyBand(320, "MMstb", [
      { rank: 1, description: "Fault seal", probability: 0.4 },
      { rank: 2, description: "Net/gross", probability: 0.3 },
    ]);
    expect(band.p50).toBe(320);
    expect(band.p10).toBeGreaterThan(band.p50);
    expect(band.p90).toBeLessThan(band.p50);
    expect(band.killers).toHaveLength(2);
  });

  it("downgrades envelope without uncertainty", () => {
    const envelope = {
      ok: true,
      payload: { matches: [] },
      errors: [],
      verdict: "SEAL",
      stage: "111_SENSE",
      status: "SUCCESS",
      metrics: {},
      trace: {},
      authority: {},
      tool: "arif_geox_pattern_match",
      session_id: null,
      meta: {},
    } as import("@arifos/mcp/types").RuntimeEnvelope<{ matches: unknown[] }>;

    const result = enforceUncertainty(envelope);
    expect(result.verdict).toBe("SABAR");
    expect(result.errors.some((e) => e.code === "UNCERTAINTY_MISSING")).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Layer 3 — Anti-Hallucination
// ═══════════════════════════════════════════════════════════════════════════════

describe("Layer 3: Anti-Hallucination", () => {
  it("flags ungrounded claims", () => {
    const audit = auditHallucination(
      ["Channel fill interpretation"],
      [{ source_type: "well", source_id: "A", observation: "Fining upward", confidence: 0.8 }],
    );
    expect(audit.clean).toBe(false);
    expect(audit.ungrounded).toContain("Channel fill interpretation");
  });

  it("VOIDs envelope with zero citations", () => {
    const envelope = {
      ok: true,
      payload: { result: "something" },
      errors: [],
      verdict: "SEAL",
      stage: "111_SENSE",
      status: "SUCCESS",
      metrics: {},
      trace: {},
      authority: {},
      tool: "arif_geox_pattern_match",
      session_id: null,
      meta: {},
    } as import("@arifos/mcp/types").RuntimeEnvelope<{ result: string }>;

    const result = enforceCitationOrUnknown(envelope, []);
    expect(result.verdict).toBe("VOID");
    expect(result.ok).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Layer 4 — Decision Firewall
// ═══════════════════════════════════════════════════════════════════════════════

describe("Layer 4: Decision Firewall (888_HOLD)", () => {
  it("identifies drilling as high-risk", () => {
    expect(isHighRiskDomain("drill")).toBe("drilling");
    expect(isHighRiskDomain("drilling")).toBe("drilling");
    expect(isHighRiskDomain("reserves")).toBe("reserves_booking");
    expect(isHighRiskDomain("well design")).toBe("well_design");
  });

  it("returns null for safe queries", () => {
    expect(isHighRiskDomain("pattern match")).toBeNull();
    expect(isHighRiskDomain("interpretation")).toBeNull();
  });

  it("transforms envelope to 888_HOLD for drilling", () => {
    const envelope = {
      ok: true,
      payload: {},
      errors: [],
      verdict: "SEAL",
      stage: "111_SENSE",
      status: "SUCCESS",
      metrics: {},
      trace: {},
      authority: {},
      tool: "arif_geox_pattern_match",
      session_id: null,
      meta: {},
    } as import("@arifos/mcp/types").RuntimeEnvelope<Record<string, unknown>>;

    const result = applyDecisionFirewall(envelope, "drill");
    expect("hold" in result).toBe(true);
    if ("hold" in result) {
      expect(result.hold.domain).toBe("drilling");
      expect(result.envelope.verdict).toBe("HOLD_888");
      expect(result.envelope.ok).toBe(false);
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Layer 5 — Multi-Discipline Reasoning
// ═══════════════════════════════════════════════════════════════════════════════

describe("Layer 5: Multi-Discipline Panel", () => {
  it("synthesizes red-flagged opinions", () => {
    const panel = runDisciplinePanel([
      { discipline: "geology", claim: "Good sand", confidence: 0.9, risk_flag: "green" },
      { discipline: "geomechanics", claim: "Will collapse", confidence: 0.8, risk_flag: "red" },
      { discipline: "drilling", claim: "Mud window sempit", confidence: 0.7, risk_flag: "red" },
    ]);
    expect(panel.dominant_risk).toBe("geomechanics");
    expect(panel.synthesis).toContain("geomechanics + drilling flags critical risk");
  });

  it("returns green when all disciplines agree", () => {
    const panel = runDisciplinePanel([
      { discipline: "geology", claim: "Good sand", confidence: 0.9, risk_flag: "green" },
      { discipline: "reservoir", claim: "High connectivity", confidence: 0.85, risk_flag: "green" },
    ]);
    expect(panel.dominant_risk).toBeNull();
    expect(panel.synthesis).toContain("All disciplines green");
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Layer 6 — Trauma Memory
// ═══════════════════════════════════════════════════════════════════════════════

describe("Layer 6: Trauma Memory", () => {
  it("has Macondo, Montara, and Piper Alpha", () => {
    const names = TRAUMA_REGISTRY.map((t) => t.name);
    expect(names).toContain("Macondo");
    expect(names).toContain("Montara");
    expect(names).toContain("Piper Alpha");
  });

  it("scans trauma by similarity tags", () => {
    const hits = scanTrauma(["cement", "deepwater"]);
    expect(hits.length).toBeGreaterThan(0);
    expect(hits.some((h) => h.name === "Macondo")).toBe(true);
  });

  it("formats trauma warnings", () => {
    const warning = formatTraumaWarning([TRAUMA_REGISTRY[0]]);
    expect(warning).toContain("Macondo");
    expect(warning).toContain("2010");
  });

  it("returns empty string for no matches", () => {
    expect(formatTraumaWarning([])).toBe("");
  });
});
