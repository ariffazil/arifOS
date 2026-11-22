/**
 * @arifos/mcp - Thin MCP Client
 *
 * JavaScript/TypeScript transport adapter for the arifOS Python kernel.
 * Carries ZERO constitutional decision logic: it forwards requests over MCP
 * and returns the kernel's response verbatim.
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import type { Transport } from "@modelcontextprotocol/sdk/shared/transport.js";
import {
  ArifOSError,
  PUBLIC_TOOL_NAMES,
  isPublicToolName,
  type ArifForgeInput,
  type ArifInitInput,
  type ArifJudgeInput,
  type ArifMemoryInput,
  type ArifOSClientConfig,
  type ArifOSMetadata,
  type ArifOSToolName,
  type ArifObserveInput,
  type ArifReportInput,
  type ArifRouteInput,
  type ArifSealInput,
  type ArifThinkInput,
  type AuthContext,
  type PublicToolDefinition,
  type RuntimeEnvelope,
  type ToolInputMap,
  type ToolPayloadMap,
} from "./types.js";

export { Client } from "@modelcontextprotocol/sdk/client/index.js";
export type { Transport } from "@modelcontextprotocol/sdk/shared/transport.js";
export * from "./types.js";

export const DEFAULT_MCP_ENDPOINT = "https://mcp.arif-fazil.com/mcp";

function createTransport(config: ArifOSClientConfig): Transport {
  switch (config.transport) {
    case "stdio": {
      return new StdioClientTransport({
        command: config.command ?? "arifos-mcp",
        args: config.args ?? [],
        env: config.env,
      });
    }
    case "http": {
      const endpoint = config.endpoint ?? DEFAULT_MCP_ENDPOINT;
      return new StreamableHTTPClientTransport(new URL(endpoint));
    }
    default: {
      const exhaustive: never = config.transport;
      throw new ArifOSError(`Unknown transport: ${exhaustive}`, "TRANSPORT_ERROR");
    }
  }
}

type TextContent = { type: string; text: string };

function extractTextContent(content: unknown): TextContent[] {
  if (!Array.isArray(content)) {
    return [];
  }
  return content.filter(
    (value): value is TextContent =>
      typeof value === "object" &&
      value !== null &&
      "type" in value &&
      typeof value.type === "string" &&
      "text" in value &&
      typeof value.text === "string",
  );
}

function parseEnvelopeFromResult(
  toolName: ArifOSToolName,
  result: { structuredContent?: unknown; content?: unknown },
): RuntimeEnvelope<Record<string, unknown>> {
  if (result.structuredContent && typeof result.structuredContent === "object") {
    return {
      tool: toolName,
      ...(result.structuredContent as Record<string, unknown>),
    };
  }

  const textContent = extractTextContent(result.content);
  const fullText = textContent.map((item) => item.text).join("").trim();

  if (!fullText) {
    throw new Error("Tool returned neither structuredContent nor text JSON.");
  }

  const parsed: unknown = JSON.parse(fullText);
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    throw new Error("Expected a JSON object response from the arifOS kernel.");
  }

  return {
    tool: toolName,
    ...(parsed as Record<string, unknown>),
  };
}

export interface ArifOSMCPClient {
  readonly mcp: Client;
  readonly metadata: ArifOSMetadata | null;
  readonly sessionId: string | null;
  readonly sessionToken: string | null;
  readonly authContext: AuthContext | null;
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  callTool<N extends ArifOSToolName>(
    name: N,
    params: ToolInputMap[N],
  ): Promise<RuntimeEnvelope<ToolPayloadMap[N]>>;
  init(params: ArifInitInput): Promise<RuntimeEnvelope<ToolPayloadMap["arif_init"]>>;
  observe(params?: ArifObserveInput): Promise<RuntimeEnvelope<ToolPayloadMap["arif_observe"]>>;
  think(params?: ArifThinkInput): Promise<RuntimeEnvelope<ToolPayloadMap["arif_think"]>>;
  route(params?: ArifRouteInput): Promise<RuntimeEnvelope<ToolPayloadMap["arif_route"]>>;
  memory(params?: ArifMemoryInput): Promise<RuntimeEnvelope<ToolPayloadMap["arif_memory"]>>;
  judge(params: ArifJudgeInput): Promise<RuntimeEnvelope<ToolPayloadMap["arif_judge"]>>;
  forge(params?: ArifForgeInput): Promise<RuntimeEnvelope<ToolPayloadMap["arif_forge"]>>;
  seal(params?: ArifSealInput): Promise<RuntimeEnvelope<ToolPayloadMap["arif_seal"]>>;
  report(params?: ArifReportInput): Promise<RuntimeEnvelope<ToolPayloadMap["arif_report"]>>;
  listTools(): Promise<PublicToolDefinition[]>;
}

/**
 * Create a thin MCP client for the 9-tool arifOS wire contract
 * (8 canonical stage verbs + arif_report).
 */
export async function createClient(config: ArifOSClientConfig): Promise<ArifOSMCPClient> {
  const transport = createTransport(config);

  const mcp = new Client(
    {
      name: "@arifos/mcp",
      version: "2026.11.22",
    },
    {
      capabilities: {},
    },
  );

  let currentMetadata: ArifOSMetadata | null = null;
  let currentSessionId: string | null = null;
  let currentSessionToken: string | null = null;
  let currentAuthContext: AuthContext | null = null;

  function updateStateFromEnvelope(
    toolName: ArifOSToolName,
    envelope: RuntimeEnvelope<Record<string, unknown>>,
  ): void {
    if (typeof envelope.session_id === "string" && envelope.session_id.length > 0) {
      currentSessionId = envelope.session_id;
    }
    if (typeof envelope.session_token === "string" && envelope.session_token.length > 0) {
      currentSessionToken = envelope.session_token;
    }
    if (envelope.auth_context) {
      currentAuthContext = envelope.auth_context;
    } else if (currentSessionId) {
      currentAuthContext = {
        session_id: currentSessionId,
        session_token: currentSessionToken ?? undefined,
      };
    }

    currentMetadata = {
      session_id: currentSessionId,
      tool: envelope.tool ?? toolName,
      version: String(envelope.meta?.schema_version ?? "unknown"),
      stage: envelope.stage ?? toolName,
      verdict: envelope.verdict ?? "UNKNOWN",
      timestamp: String(envelope.meta?.timestamp ?? new Date().toISOString()),
    };
  }

  async function callPublicTool<N extends ArifOSToolName>(
    name: N,
    params: ToolInputMap[N],
  ): Promise<RuntimeEnvelope<ToolPayloadMap[N]>> {
    try {
      const effectiveArgs: Record<string, unknown> = { ...(params as Record<string, unknown>) };
      if (currentSessionId && effectiveArgs.session_id === undefined) {
        effectiveArgs.session_id = currentSessionId;
      }
      if (currentSessionToken && effectiveArgs.session_token === undefined && name !== "arif_init") {
        effectiveArgs.session_token = currentSessionToken;
      }

      const result = await mcp.callTool(
        { name, arguments: effectiveArgs },
        undefined,
        { timeout: config.timeout ?? 60000 },
      );
      const envelope = parseEnvelopeFromResult(
        name,
        result as { structuredContent?: unknown; content?: unknown },
      );
      updateStateFromEnvelope(name, envelope);
      return envelope as RuntimeEnvelope<ToolPayloadMap[N]>;
    } catch (cause) {
      if (cause instanceof ArifOSError) {
        throw cause;
      }
      throw new ArifOSError(
        `Tool call failed: ${name}`,
        "INVALID_RESPONSE",
        currentMetadata?.stage,
        undefined,
        cause,
      );
    }
  }

  const client: ArifOSMCPClient = {
    mcp,
    get metadata() {
      return currentMetadata;
    },
    get sessionId() {
      return currentSessionId;
    },
    get sessionToken() {
      return currentSessionToken;
    },
    get authContext() {
      return currentAuthContext;
    },

    async connect(): Promise<void> {
      try {
        await mcp.connect(transport);
      } catch (cause) {
        throw new ArifOSError(
          "Failed to connect to arifOS MCP server",
          "CONNECTION_FAILED",
          undefined,
          undefined,
          cause,
        );
      }
    },

    async disconnect(): Promise<void> {
      await mcp.close();
    },

    callTool<N extends ArifOSToolName>(
      name: N,
      params: ToolInputMap[N],
    ): Promise<RuntimeEnvelope<ToolPayloadMap[N]>> {
      return callPublicTool(name, params);
    },

    init(params: ArifInitInput) {
      return callPublicTool("arif_init", params);
    },
    observe(params: ArifObserveInput = {}) {
      return callPublicTool("arif_observe", params);
    },
    think(params: ArifThinkInput = {}) {
      return callPublicTool("arif_think", params);
    },
    route(params: ArifRouteInput = {}) {
      return callPublicTool("arif_route", params);
    },
    memory(params: ArifMemoryInput = {}) {
      return callPublicTool("arif_memory", params);
    },
    judge(params: ArifJudgeInput) {
      return callPublicTool("arif_judge", params);
    },
    forge(params: ArifForgeInput = {}) {
      return callPublicTool("arif_forge", params);
    },
    seal(params: ArifSealInput = {}) {
      return callPublicTool("arif_seal", params);
    },
    report(params: ArifReportInput = {}) {
      return callPublicTool("arif_report", params);
    },

    async listTools(): Promise<PublicToolDefinition[]> {
      try {
        const result = await mcp.listTools();
        const publicTools = result.tools.filter(
          (tool): tool is (typeof result.tools)[number] & { name: ArifOSToolName } =>
            isPublicToolName(tool.name),
        );

        return publicTools
          .map((tool) => ({
            name: tool.name,
            description: tool.description,
            inputSchema: tool.inputSchema,
            outputSchema: "outputSchema" in tool ? tool.outputSchema : undefined,
            annotations: tool.annotations,
          }))
          .sort(
            (left, right) =>
              PUBLIC_TOOL_NAMES.indexOf(left.name) - PUBLIC_TOOL_NAMES.indexOf(right.name),
          );
      } catch (cause) {
        throw new ArifOSError(
          "Failed to list public tools",
          "INVALID_RESPONSE",
          undefined,
          undefined,
          cause,
        );
      }
    },
  };

  return client;
}

export const quickConnect = {
  local(env?: Record<string, string>): Promise<ArifOSMCPClient> {
    return createClient({ transport: "stdio", env });
  },

  hosted(endpoint = DEFAULT_MCP_ENDPOINT): Promise<ArifOSMCPClient> {
    return createClient({ transport: "http", endpoint });
  },
};
