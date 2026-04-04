/**
 * arifOS Bridge Extension for OpenClaw
 * 
 * Phase 4 Step 1: Stateless MCP-Native Bridge (Option B)
 * 
 * Protocol: Per-call MCP (initialize -> notifications/initialized -> tools/call)
 * Target: arifOS /mcp endpoint (port 8088)
 * Previous: REST shim (removed from primary flow)
 * 
 * This is the canonical boundary. No REST fallback.
 * 
 * DITEMPA BUKAN DIBERI
 */

import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { emptyPluginConfigSchema } from "openclaw/plugin-sdk";

// Canonical MCP endpoint (internal Docker network)
// Port 8080: arifOS MCP (mapped to 8088 on host)
const ARIFOS_MCP_ENDPOINT = process.env.ARIFOS_MCP_ENDPOINT || "http://10.0.0.3:8080/mcp";

interface MCPRequest {
  jsonrpc: "2.0";
  id: number;
  method: string;
  params?: Record<string, any>;
}

interface BridgeMetrics {
  sessionInitMs: number;
  toolCallMs: number;
  totalMs: number;
  verdict: string;
  stage: string;
  timestamp: string;
}

let requestId = 0;

/**
 * Parse SSE response stream for MCP
 */
async function parseSSEResponse(response: Response): Promise<any> {
  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";
  let lastResult: any = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6).trim();
        if (data === "[DONE]") continue;
        if (!data) continue;

        try {
          const parsed = JSON.parse(data);
          
          // Handle initialize response
          if (parsed.result?.protocolVersion) {
            lastResult = parsed.result;
          }
          // Handle tool call response
          else if (parsed.result?.content) {
            lastResult = parsed.result;
          }
          // Handle errors
          else if (parsed.error) {
            throw new Error(`MCP error: ${parsed.error.message}`);
          }
        } catch (e) {
          if (e instanceof Error && e.message.startsWith("MCP error")) throw e;
          // Continue reading if parse fails
        }
      }
    }
  }

  return lastResult;
}

/**
 * Initialize MCP session (stateless - per call)
 */
async function initializeMCP(): Promise<{ sessionId: string; capabilities: any }> {
  const startTime = Date.now();
  
  const req: MCPRequest = {
    jsonrpc: "2.0",
    id: ++requestId,
    method: "initialize",
    params: {
      protocolVersion: "2025-11-25",
      capabilities: {},
      clientInfo: {
        name: "openclaw-bridge",
        version: "2026.02.27"
      }
    }
  };

  const response = await fetch(ARIFOS_MCP_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json, text/event-stream"
    },
    body: JSON.stringify(req)
  });

  if (!response.ok) {
    throw new Error(`MCP initialize failed: HTTP ${response.status}`);
  }

  // Extract session ID from headers if present
  const sessionId = response.headers.get("MCP-Session-Id") || 
                   response.headers.get("mcp-session-id") ||
                   `session-${Date.now()}`;

  const result = await parseSSEResponse(response);
  
  return {
    sessionId,
    capabilities: result?.capabilities || {},
    initTimeMs: Date.now() - startTime
  };
}

/**
 * Call MCP tool with initialized session
 */
async function callToolMCP(
  toolName: string,
  args: any,
  sessionId: string
): Promise<any> {
  const startTime = Date.now();
  
  const req: MCPRequest = {
    jsonrpc: "2.0",
    id: ++requestId,
    method: "tools/call",
    params: {
      name: toolName,
      arguments: args
    }
  };

  const response = await fetch(ARIFOS_MCP_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json, text/event-stream",
      "MCP-Session-Id": sessionId
    },
    body: JSON.stringify(req)
  });

  if (!response.ok) {
    throw new Error(`MCP tool call failed: HTTP ${response.status}`);
  }

  const result = await parseSSEResponse(response);
  
  // Parse content if it's text
  const content = result?.content?.[0]?.text;
  if (content) {
    try {
      return JSON.parse(content);
    } catch {
      return { verdict: "VOID", error: content };
    }
  }

  return result;
}

/**
 * Stateless MCP apex_judge call
 * Per-call flow: initialize -> call
 */
async function apexJudgeMCP(
  query: string,
  sessionId: string,
  actorId: string
): Promise<{ result: any; metrics: BridgeMetrics }> {
  const totalStart = Date.now();
  
  // Step 1: Initialize session
  const { sessionId: mcpSessionId, initTimeMs } = await initializeMCP();
  
  // Step 2: Call tool
  const toolStart = Date.now();
  const result = await callToolMCP("apex_judge", {
    query,
    session_id: sessionId
  }, mcpSessionId);
  
  const toolTimeMs = Date.now() - toolStart;
  const totalMs = Date.now() - totalStart;

  // Extract verdict for metrics
  const verdict = result?.verdict || result?.data?.verdict || "UNKNOWN";
  const stage = result?.stage || result?.data?.stage || "N/A";

  const metrics: BridgeMetrics = {
    sessionInitMs: initTimeMs,
    toolCallMs: toolTimeMs,
    totalMs,
    verdict,
    stage,
    timestamp: new Date().toISOString()
  };

  return { result, metrics };
}

const arifOSBridgePlugin = {
  id: "arifos-bridge",
  name: "arifOS Constitutional Bridge",
  description: "MCP-native bridge to arifOS 13-floor governance (Phase 4)",
  kind: "tool" as const,
  configSchema: emptyPluginConfigSchema(),
  
  register(api: OpenClawPluginApi) {
    const logger = api.runtime?.logger || console;
    
    api.registerTool(
      () => ({
        name: "arifos_judge",
        description: "Constitutional evaluation via MCP-native bridge (F1-F13). Returns SEAL, VOID, PARTIAL, SABAR, or 888_HOLD.",
        parameters: {
          type: "object",
          properties: {
            query: { 
              type: "string", 
              description: "Query to evaluate constitutionally" 
            },
          },
          required: ["query"]
        },
        async execute(args: { query: string }, ctx: any) {
          const startTime = Date.now();
          
          logger.info(`[arifOS Bridge/MCP] Judging: "${args.query.substring(0, 50)}..."`);
          
          try {
            // STATELESS MCP: initialize -> call (per request)
            const { result, metrics } = await apexJudgeMCP(
              args.query,
              ctx.sessionKey || `session-${Date.now()}`,
              ctx.userId || "openclaw"
            );
            
            // Log metrics
            logger.info(`[arifOS Bridge/MCP] Verdict: ${metrics.verdict} (${metrics.stage})`);
            logger.info(`[arifOS Bridge/MCP] Latency: init=${metrics.sessionInitMs}ms, tool=${metrics.toolCallMs}ms, total=${metrics.totalMs}ms`);
            
            return {
              verdict: metrics.verdict,
              stage: metrics.stage,
              reason: result?.reason || result?.data?.verdict,
              confidence: result?.confidence,
              _bridge: "MCP_NATIVE",
              _metrics: {
                session_init_ms: metrics.sessionInitMs,
                tool_call_ms: metrics.toolCallMs,
                total_ms: metrics.totalMs
              }
            };
          } catch (error) {
            const errorMsg = error instanceof Error ? error.message : String(error);
            logger.error(`[arifOS Bridge/MCP] Error: ${errorMsg}`);
            
            return {
              verdict: "VOID",
              stage: "888_ERROR",
              reason: errorMsg,
              _bridge: "MCP_NATIVE",
              _error: true
            };
          }
        }
      }),
      { names: ["arifos_judge"] }
    );

    logger.info(`[arifOS Bridge] MCP-native bridge registered (endpoint: ${ARIFOS_MCP_ENDPOINT})`);
    logger.info(`[arifOS Bridge] Protocol: Stateless MCP (Option B)`);
  }
};

export default arifOSBridgePlugin;
