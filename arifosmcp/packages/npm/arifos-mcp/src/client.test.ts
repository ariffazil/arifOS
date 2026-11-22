/**
 * @arifos/mcp - Contract & Integration Tests
 */

import { afterAll, beforeAll, describe, expect, it } from "vitest";
import {
  CANONICAL_STAGE_VERBS,
  createClient,
  ENDPOINTS,
  FLOOR_CODES,
  isPublicToolName,
  PUBLIC_TOOL_NAMES,
  VERSION,
} from "./index.js";
import type { ArifOSMCPClient } from "./client.js";

const TEST_ENDPOINT = process.env.ARIFOS_TEST_ENDPOINT ?? ENDPOINTS.MCP;
const SKIP_INTEGRATION = process.env.SKIP_INTEGRATION_TESTS === "true";

describe("public package contract", () => {
  it("exports the canonical 9-tool wire contract (8 stage verbs + arif_report)", () => {
    expect(VERSION).toBe("2026.11.22");
    expect(CANONICAL_STAGE_VERBS).toEqual([
      "arif_init",
      "arif_observe",
      "arif_think",
      "arif_route",
      "arif_memory",
      "arif_judge",
      "arif_forge",
      "arif_seal",
    ]);
    expect(PUBLIC_TOOL_NAMES).toEqual([...CANONICAL_STAGE_VERBS, "arif_report"]);
    expect(isPublicToolName("arif_judge")).toBe(true);
    expect(isPublicToolName("arif_report")).toBe(true);
    expect(isPublicToolName("arifOS_kernel")).toBe(false);
  });

  it("points to the canonical live endpoint and PyPI/GitHub references", () => {
    expect(ENDPOINTS.MCP).toBe("https://mcp.arif-fazil.com/mcp");
    expect(ENDPOINTS.HEALTH).toBe("https://mcp.arif-fazil.com/health");
    expect(ENDPOINTS.PYPI).toBe("https://pypi.org/project/arifos/");
    expect(ENDPOINTS.REPO).toBe("https://github.com/ariffazil/arifOS");
    expect(FLOOR_CODES).toHaveLength(13);
  });
});

describe("@arifos/mcp live wire integration", () => {
  let client: ArifOSMCPClient;

  beforeAll(async () => {
    if (SKIP_INTEGRATION) {
      return;
    }
    client = await createClient({
      transport: "http",
      endpoint: TEST_ENDPOINT,
      timeout: 30000,
    });
    await client.connect();
  });

  afterAll(async () => {
    if (client) {
      await client.disconnect();
    }
  });

  it.skipIf(SKIP_INTEGRATION)("discovers the 9 live wire tools", async () => {
    const tools = await client.listTools();
    expect(tools.map((tool) => tool.name)).toEqual([...PUBLIC_TOOL_NAMES]);
  });
});
