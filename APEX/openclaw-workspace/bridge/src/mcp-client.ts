/**
 * MCP JSON-RPC Client (Streamable HTTP)
 * 
 * Speaks native MCP protocol to arifOS /mcp endpoint.
 * Handles both JSON and SSE (Server-Sent Events) responses.
 * No REST fallback. No interface entropy.
 */

const MCP_ENDPOINT = process.env.ARIFOS_MCP_ENDPOINT || 'http://127.0.0.1:8088/mcp';
const MCP_VERSION = '2025-11-25';

interface MCPRequest {
  jsonrpc: '2.0';
  id: number;
  method: string;
  params?: Record<string, any>;
}

interface MCPResponse {
  jsonrpc: '2.0';
  id: number | string;
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

let requestId = 0;

async function mcpCall(method: string, params?: Record<string, any>): Promise<any> {
  const req: MCPRequest = {
    jsonrpc: '2.0',
    id: ++requestId,
    method,
    params,
  };

  const response = await fetch(MCP_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      // MCP Streamable HTTP requires accepting both JSON and SSE
      'Accept': 'application/json, text/event-stream',
    },
    body: JSON.stringify(req),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`MCP HTTP ${response.status}: ${errorText}`);
  }

  const contentType = response.headers.get('content-type') || '';
  
  if (contentType.includes('text/event-stream')) {
    // Handle SSE response (streaming)
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body for SSE');
    }
    
    // Read first SSE event
    const decoder = new TextDecoder();
    let buffer = '';
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      
      // Parse SSE data line
      const lines = buffer.split('\n');
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          try {
            const parsed: MCPResponse = JSON.parse(data);
            if (parsed.error) {
              throw new Error(`MCP error ${parsed.error.code}: ${parsed.error.message}`);
            }
            return parsed.result;
          } catch (e) {
            if (data !== '[DONE]') {
              throw e;
            }
          }
        }
      }
    }
    throw new Error('SSE stream ended without result');
  } else {
    // Handle JSON response
    const resp: MCPResponse = await response.json();
    
    if (resp.error) {
      throw new Error(`MCP error ${resp.error.code}: ${resp.error.message}`);
    }
    
    return resp.result;
  }
}

/**
 * Initialize MCP session
 */
export async function mcpInitialize(): Promise<void> {
  await mcpCall('initialize', {
    protocolVersion: MCP_VERSION,
    capabilities: {},
    clientInfo: {
      name: 'openclaw-arifos-bridge',
      version: '1.0.0',
    },
  });
}

/**
 * Call arifOS apex_judge via MCP
 */
export interface ApexJudgeParams {
  query: string;
  actor_id?: string;
  session_id?: string;
  context?: string;
}

export interface ApexJudgeResult {
  verdict: 'SEAL' | 'VOID' | 'PARTIAL' | 'SABAR' | '888_HOLD';
  stage: string;
  reason?: string;
  confidence?: number;
  error?: string;
}

export async function apexJudge(params: ApexJudgeParams): Promise<ApexJudgeResult> {
  const result = await mcpCall('tools/call', {
    name: 'apex_judge',
    arguments: {
      query: params.query,
      actor_id: params.actor_id || 'openclaw-bridge',
      session_id: params.session_id,
      context: params.context,
    },
  });

  // Handle both direct result and content array formats
  const content = result?.content || [result];
  const textContent = content.find((c: any) => c.type === 'text')?.text;
  
  if (textContent) {
    try {
      const parsed = JSON.parse(textContent);
      return {
        verdict: parsed.verdict,
        stage: parsed.stage,
        reason: parsed.reason || parsed.error,
        confidence: parsed.confidence,
      };
    } catch {
      return {
        verdict: 'VOID',
        stage: 'ERROR',
        reason: textContent,
      };
    }
  }

  return {
    verdict: result?.verdict || 'VOID',
    stage: result?.stage || 'UNKNOWN',
    reason: result?.reason || result?.error,
    confidence: result?.confidence,
  };
}

/**
 * Call arifOS anchor_session via MCP
 */
export async function anchorSession(actorId: string, sessionId?: string): Promise<any> {
  return mcpCall('tools/call', {
    name: 'anchor_session',
    arguments: {
      actor_id: actorId,
      session_id: sessionId,
    },
  });
}

/**
 * List available tools
 */
export async function listTools(): Promise<string[]> {
  const result = await mcpCall('tools/list');
  return result.tools?.map((t: any) => t.name) || [];
}

export { mcpCall };
