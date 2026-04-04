/**
 * Message-to-MCP Adapter
 * 
 * Converts OpenClaw messages to arifOS MCP tool calls.
 * No constitutional logic here — just protocol translation.
 */

import { MessageContext } from '@openclaw/sdk';

export interface MCPToolCall {
  tool: string;
  params: Record<string, any>;
}

/**
 * Route OpenClaw message to appropriate arifOS MCP tool
 */
export function routeToMCP(message: string, context: MessageContext): MCPToolCall {
  // Simple routing logic — extend as needed
  const lowerMsg = message.toLowerCase();
  
  // Crisis signals → immediate apex_judge
  if (/\b(kill|suicide|hurt|abuse)\b/.test(lowerMsg)) {
    return {
      tool: 'apex_judge',
      params: {
        query: message,
        lane: 'CRISIS',
        session_id: context.sessionId,
      }
    };
  }
  
  // Factual queries → reason_mind + apex_judge
  if (/\b(what|who|when|where|why|how)\b/.test(lowerMsg)) {
    return {
      tool: 'reason_mind',
      params: {
        query: message,
        session_id: context.sessionId,
      }
    };
  }
  
  // Default: anchor_session for new session
  return {
    tool: 'anchor_session',
    params: {
      actor_id: context.userId,
      session_id: context.sessionId,
    }
  };
}
