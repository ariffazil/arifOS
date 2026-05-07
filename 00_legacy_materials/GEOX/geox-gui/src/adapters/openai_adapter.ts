/**
 * OpenAI Adapter — ChatGPT Apps SDK Bridge
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * Bridges GEOX Earth Witness tools to ChatGPT via the OpenAI Actions API.
 * Enables natural language geoscience queries within ChatGPT conversations.
 *
 * Constitutional Integration:
 *   F1 Amanah     — Session state reversible, audit trail preserved
 *   F2 Truth      — All tool outputs tagged with confidence
 *   F3 Witness    — Tri-witness consensus maintained
 *   F7 Humility   — Confidence caps enforced (max 0.90)
 *   F11 Audit     — Full OpenAI interaction logging
 *   F13 Sovereign — 888_HOLD can block any OpenAI-initiated action
 *
 * Architecture:
 *   window.openai (ChatGPT SDK) → Adapter → MCP Bridge → GEOX Backend
 *
 * @module adapters/openai_adapter
 * @version 0.6.1
 */

import {
  OpenAIFunction,
  OpenAIToolCall,
  OpenAIToolResponse,
  OpenAISession,
  OpenAIAdapterState,
  AdapterStatus,
  OpenAIEvent,
  GeoxToolResult,
  mapGeoxToOpenAI,
  mapOpenAIToGeox,
  getOpenAIToolList,
  GEOX_OPENAI_TOOL_MAP,
  OpenAIInitConfig,
} from './openai_types';

// ═══════════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════════

const ADAPTER_VERSION = '0.6.1';
const API_VERSION = '2024-01-01';
const SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes
const REQUEST_TIMEOUT_MS = 30_000;

// ═══════════════════════════════════════════════════════════════════════════════
// Adapter State
// ═══════════════════════════════════════════════════════════════════════════════

let adapterState: OpenAIAdapterState = {
  status: 'idle',
  session: null,
  auth: { status: 'unauthenticated' },
  registeredTools: [],
  lastError: null,
};

const stateListeners: Set<(state: OpenAIAdapterState) => void> = new Set();

const setAdapterState = (updates: Partial<OpenAIAdapterState>) => {
  adapterState = { ...adapterState, ...updates };
  stateListeners.forEach(listener => listener(adapterState));
};

// ═══════════════════════════════════════════════════════════════════════════════
// Event Logging (F11 Auditability)
// ═══════════════════════════════════════════════════════════════════════════════

const logOpenAIEvent = (event: Omit<OpenAIEvent, 'timestamp'>) => {
  const fullEvent: OpenAIEvent = {
    ...event,
    timestamp: new Date().toISOString(),
  };

  // Send to parent for vault logging
  window.parent.postMessage(
    {
      type: 'openai.audit',
      event: fullEvent,
      session: adapterState.session?.id,
    },
    '*'
  );

  // Console log in development
  if (process.env.NODE_ENV === 'development') {
    console.log('[OpenAI Adapter]', fullEvent);
  }
};

// ═══════════════════════════════════════════════════════════════════════════════
// Session Management
// ═══════════════════════════════════════════════════════════════════════════════

const generateSessionId = (): string => {
  return `oa-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
};

const createSession = async (): Promise<OpenAISession> => {
  const now = new Date();
  const session: OpenAISession = {
    id: generateSessionId(),
    geoxSessionId: '', // Will be populated from init
    createdAt: now.toISOString(),
    expiresAt: new Date(now.getTime() + SESSION_TIMEOUT_MS).toISOString(),
    context: {
      preferences: {
        units: 'metric',
        coordinateSystem: 'WGS84',
        defaultModels: {
          saturation: 'archie',
          velocity: 'layered',
        },
      },
    },
  };

  // Request GEOX session initialization via MCP
  const geoxSession = await initGeoxSession();
  session.geoxSessionId = geoxSession.id;

  return session;
};

const initGeoxSession = async (): Promise<{ id: string }> => {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error('GEOX session init timeout'));
    }, REQUEST_TIMEOUT_MS);

    const handler = (event: MessageEvent) => {
      const data = event.data;
      if (data?.method === 'init.response') {
        clearTimeout(timeout);
        window.removeEventListener('message', handler);
        if (data.error) {
          reject(new Error(data.error));
        } else {
          resolve({ id: data.sessionId });
        }
      }
    };

    window.addEventListener('message', handler);
    window.parent.postMessage(
      {
        jsonrpc: '2.0',
        method: 'init.request',
        params: { source: 'openai_adapter' },
        id: generateSessionId(),
      },
      '*'
    );
  });
};

// ═══════════════════════════════════════════════════════════════════════════════
// Tool Registration
// ═══════════════════════════════════════════════════════════════════════════════

const registerToolsWithOpenAI = async (): Promise<void> => {
  const tools = getOpenAIToolList()
    .map(name => mapGeoxToOpenAI(name))
    .filter((t): t is OpenAIFunction => t !== null);

  if (!window.openai) {
    throw new Error('window.openai not available. ChatGPT Apps SDK not loaded.');
  }

  await window.openai.registerTools(tools);
  setAdapterState({ registeredTools: tools.map(t => t.name) });

  logOpenAIEvent({
    type: 'tool.start',
    payload: { registered: tools.map(t => t.name) },
  });
};

// ═══════════════════════════════════════════════════════════════════════════════
// Tool Execution
// ═══════════════════════════════════════════════════════════════════════════════

const executeGeoxTool = async (
  geoxToolName: string,
  args: Record<string, unknown>
): Promise<GeoxToolResult> => {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error(`Tool ${geoxToolName} timed out`));
    }, REQUEST_TIMEOUT_MS);

    const handler = (event: MessageEvent) => {
      const data = event.data;
      if (
        data?.jsonrpc === '2.0' &&
        data?.method === 'tool.response' &&
        data?.params?.tool === geoxToolName
      ) {
        clearTimeout(timeout);
        window.removeEventListener('message', handler);

        if (data.params.error) {
          resolve({
            ok: false,
            error: String(data.params.error),
            verdict: 'VOID',
            confidence: 0,
            floors: { passed: [], warned: [], failed: ['F12'] },
            executionTime: Date.now() - startTime,
            timestamp: new Date().toISOString(),
          });
        } else {
          const result = data.params.result;
          resolve({
            ok: true,
            data: result,
            verdict: result.verdict || 'SEAL',
            confidence: Math.min(result.confidence || 0.5, 0.90), // F7 Humility cap
            floors: result.floors || { passed: [], warned: [], failed: [] },
            executionTime: Date.now() - startTime,
            timestamp: new Date().toISOString(),
          });
        }
      }
    };

    const startTime = Date.now();
    window.addEventListener('message', handler);

    // F13 Sovereign: Check if this action should be blocked
    if (shouldBlockForSovereignReview(geoxToolName, args)) {
      clearTimeout(timeout);
      window.removeEventListener('message', handler);
      resolve({
        ok: false,
        error: '888_HOLD: Action blocked pending sovereign review (F13)',
        verdict: 'HOLD',
        confidence: 0,
        floors: { passed: [], warned: [], failed: ['F13'] },
        executionTime: 0,
        timestamp: new Date().toISOString(),
      });
      return;
    }

    window.parent.postMessage(
      {
        jsonrpc: '2.0',
        method: 'tool.request',
        params: {
          tool: geoxToolName,
          arguments: args,
          sessionId: adapterState.session?.geoxSessionId,
        },
        id: generateSessionId(),
        timestamp: new Date().toISOString(),
      },
      '*'
    );
  });
};

/**
 * F13 Sovereign: Determine if action requires human review
 */
const shouldBlockForSovereignReview = (
  toolName: string,
  args: Record<string, unknown>
): boolean => {
  // Block high-risk operations
  const highRiskTools = [
    'geox_evaluate_prospect', // Financial decisions
    'geox_build_structural_candidates', // Interpretation commitments
  ];

  if (highRiskTools.includes(toolName)) {
    // Check if confidence threshold requires review
    const prospectConfidence = args.confidence_threshold as number;
    if (prospectConfidence && prospectConfidence > 0.85) {
      return true; // Require 888_HOLD for high-confidence prospect evaluation
    }
  }

  // Check for irreversible operations
  if (toolName.includes('delete') || toolName.includes('modify')) {
    return true;
  }

  return false;
};

/**
 * Handle tool call from ChatGPT
 */
const handleToolCall = async (
  call: OpenAIToolCall
): Promise<OpenAIToolResponse> => {
  const startTime = Date.now();

  logOpenAIEvent({
    type: 'tool.start',
    payload: { tool: call.function.name, callId: call.id },
  });

  const geoxToolName = mapOpenAIToGeox(call.function.name);

  if (!geoxToolName) {
    const error = `Unknown tool: ${call.function.name}`;
    logOpenAIEvent({ type: 'tool.error', payload: { error, callId: call.id } });
    return {
      tool_call_id: call.id,
      role: 'tool',
      name: call.function.name,
      content: JSON.stringify({
        ok: false,
        error,
        verdict: 'VOID',
        floors: { passed: [], warned: [], failed: ['F2'] },
      }),
    };
  }

  try {
    const args = JSON.parse(call.function.arguments);
    const result = await executeGeoxTool(geoxToolName, args);

    logOpenAIEvent({
      type: 'tool.complete',
      payload: {
        tool: geoxToolName,
        callId: call.id,
        duration: Date.now() - startTime,
        verdict: result.verdict,
      },
    });

    // Format response for ChatGPT
    const responseContent = formatResponseForChatGPT(result, geoxToolName);

    return {
      tool_call_id: call.id,
      role: 'tool',
      name: call.function.name,
      content: JSON.stringify(responseContent),
    };
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logOpenAIEvent({
      type: 'tool.error',
      payload: { error: errorMsg, callId: call.id },
    });

    return {
      tool_call_id: call.id,
      role: 'tool',
      name: call.function.name,
      content: JSON.stringify({
        ok: false,
        error: errorMsg,
        verdict: 'VOID',
        floors: { passed: [], warned: [], failed: ['F12'] },
      }),
    };
  }
};

/**
 * Format GEOX result for ChatGPT consumption
 */
const formatResponseForChatGPT = (
  result: GeoxToolResult,
  toolName: string
): Record<string, unknown> => {
  const base = {
    ok: result.ok,
    verdict: result.verdict,
    confidence: result.confidence,
    execution_time_ms: result.executionTime,
    constitutional_status: {
      floors_passed: result.floors.passed,
      floors_warned: result.floors.warned,
      floors_failed: result.floors.failed,
    },
  };

  if (!result.ok) {
    return {
      ...base,
      error: result.error,
      explanation: getErrorExplanation(result.verdict, toolName),
    };
  }

  // Add human-readable summary based on tool type
  const summary = generateToolSummary(toolName, result.data);

  return {
    ...base,
    data: result.data,
    summary,
    // F2 Truth: Include data source and limitations
    data_quality: {
      source: 'GEOX Earth Witness MCP',
      version: ADAPTER_VERSION,
      limitations: getToolLimitations(toolName),
    },
  };
};

const getErrorExplanation = (verdict: string, toolName: string): string => {
  const explanations: Record<string, string> = {
    HOLD: `888_HOLD triggered. This ${toolName} operation requires sovereign (human) review before proceeding.`,
    VOID: 'Constitutional violation detected. The operation cannot proceed as requested.',
    CAUTION: 'Operation completed with constitutional warnings. Review floor status before acting.',
  };
  return explanations[verdict] || 'Operation failed. Check floor status for details.';
};

const generateToolSummary = (toolName: string, data: unknown): string => {
  // Tool-specific summary generators
  const summaries: Record<string, (d: unknown) => string> = {
    geox_health: () => 'GEOX system health check completed. All constitutional floors active.',
    geox_malay_basin_pilot: (d) => `Malay Basin query returned ${(d as any)?.well_count || 'available'} well records.`,
    geox_calculate_saturation: (d) => `Saturation calculation complete. Mean Sw: ${(d as any)?.sw_mean?.toFixed(2) || 'N/A'}`,
  };

  const generator = summaries[toolName];
  return generator ? generator(data) : 'Operation completed successfully.';
};

const getToolLimitations = (toolName: string): string[] => {
  const limitations: Record<string, string[]> = {
    geox_calculate_saturation: [
      'Saturation models are approximations; core calibration recommended.',
      'Monte Carlo uncertainty represents parameter variance, not model error.',
    ],
    geox_evaluate_prospect: [
      'Prospect evaluation uses available data; additional wells may change conclusions.',
      'Risk matrix is advisory; final investment decision requires full due diligence.',
    ],
    geox_query_macrostrat: [
      'Macrostrat data is regional-scale; local geology may vary.',
      'Stratigraphic correlations are probabilistic.',
    ],
  };
  return limitations[toolName] || ['Data quality depends on input sources.'];
};

// ═══════════════════════════════════════════════════════════════════════════════
// Public API
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Initialize the OpenAI adapter
 */
export const initOpenAIAdapter = async (
  config?: Partial<OpenAIInitConfig>
): Promise<void> => {
  try {
    setAdapterState({ status: 'initializing' });

    // Check if running in ChatGPT environment
    if (!window.openai) {
      console.warn('[OpenAI Adapter] window.openai not available. Running in standalone mode.');
      setAdapterState({ status: 'error', lastError: 'ChatGPT SDK not available' });
      return;
    }

    // Initialize ChatGPT SDK
    await window.openai.init({
      appId: 'geox-earth-witness',
      apiVersion: API_VERSION,
      allowedDomains: ['https://geox.arif-fazil.com', 'https://chat.openai.com'],
      sandbox: {
        allowScripts: true,
        allowForms: false,
      },
      ...config,
    });

    // Create session
    const session = await createSession();

    // Register tools
    await registerToolsWithOpenAI();

    // Set up tool call handler
    window.openai.onToolCall(handleToolCall);

    setAdapterState({
      status: 'ready',
      session,
      lastError: null,
    });

    logOpenAIEvent({
      type: 'session.update',
      payload: { status: 'initialized', sessionId: session.id },
    });
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    setAdapterState({
      status: 'error',
      lastError: errorMsg,
    });
    throw error;
  }
};

/**
 * Get current adapter state
 */
export const getAdapterState = (): OpenAIAdapterState => ({ ...adapterState });

/**
 * Subscribe to state changes
 */
export const subscribeToAdapter = (
  listener: (state: OpenAIAdapterState) => void
): () => void => {
  stateListeners.add(listener);
  listener(adapterState); // Initial call
  return () => stateListeners.delete(listener);
};

/**
 * Check if adapter is ready
 */
export const isAdapterReady = (): boolean => adapterState.status === 'ready';

/**
 * Get session ID for audit purposes
 */
export const getSessionId = (): string | null =>
  adapterState.session?.id || null;

/**
 * Reset adapter state
 */
export const resetAdapter = (): void => {
  adapterState = {
    status: 'idle',
    session: null,
    auth: { status: 'unauthenticated' },
    registeredTools: [],
    lastError: null,
  };
  stateListeners.forEach(listener => listener(adapterState));
};

// ═══════════════════════════════════════════════════════════════════════════════
// Default Export
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  init: initOpenAIAdapter,
  getState: getAdapterState,
  subscribe: subscribeToAdapter,
  isReady: isAdapterReady,
  getSessionId,
  reset: resetAdapter,
};
