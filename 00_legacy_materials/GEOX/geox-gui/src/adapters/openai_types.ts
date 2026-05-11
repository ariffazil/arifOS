/**
 * OpenAI Adapter Types — ChatGPT Apps SDK Integration
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * TypeScript definitions for OpenAI Actions API and ChatGPT Apps SDK.
 * Enables GEOX tools to be invoked directly from ChatGPT conversations.
 *
 * Constitutional Integration:
 *   F1 Amanah    — All actions reversible via session management
 *   F2 Truth     — Tool responses tagged with confidence levels
 *   F3 Witness   — Human × AI × System validation preserved
 *   F11 Audit    — Full logging of OpenAI interactions
 *
 * @module adapters/openai_types
 * @version 0.6.1
 */

// ═══════════════════════════════════════════════════════════════════════════════
// OpenAI Actions API Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * OpenAI Function Definition (Actions Schema)
 * Defines how ChatGPT sees and calls a GEOX tool
 */
export interface OpenAIFunction {
  name: string;
  description: string;
  parameters: {
    type: 'object';
    properties: Record<string, OpenAIParameter>;
    required?: string[];
  };
}

export interface OpenAIParameter {
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  description: string;
  enum?: string[];
  items?: OpenAIParameter;
  properties?: Record<string, OpenAIParameter>;
}

/**
 * OpenAI Tool Invocation from ChatGPT
 */
export interface OpenAIToolCall {
  id: string;
  type: 'function';
  function: {
    name: string;
    arguments: string; // JSON string
  };
}

/**
 * OpenAI Tool Response to ChatGPT
 */
export interface OpenAIToolResponse {
  tool_call_id: string;
  role: 'tool';
  name: string;
  content: string; // JSON string
}

// ═══════════════════════════════════════════════════════════════════════════════
// GEOX-OpenAI Bridge Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Mapped GEOX Tool for OpenAI consumption
 */
export interface MappedGeoxTool {
  geoxName: string;
  openaiName: string;
  description: string;
  parameters: OpenAIParameterMap;
  constitutionalNotes?: string[];
}

export interface OpenAIParameterMap {
  [key: string]: {
    type: OpenAIParameter['type'];
    description: string;
    required: boolean;
    default?: unknown;
    constraints?: {
      min?: number;
      max?: number;
      pattern?: string;
    };
  };
}

/**
 * Tool execution result with constitutional metadata
 */
export interface GeoxToolResult<T = unknown> {
  ok: boolean;
  data?: T;
  error?: string;
  verdict: 'SEAL' | 'COMPLY' | 'CAUTION' | 'HOLD' | 'VOID';
  confidence: number; // 0-1, F7 Humility enforced
  floors: {
    passed: string[];
    warned: string[];
    failed: string[];
  };
  executionTime: number; // ms
  timestamp: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Session & Authentication Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * OpenAI Session Context
 * Maintains state across multi-turn ChatGPT conversations
 */
export interface OpenAISession {
  id: string;
  geoxSessionId: string;
  createdAt: string;
  expiresAt: string;
  userId?: string;
  context: {
    lastBasin?: string;
    lastWell?: string;
    activeProject?: string;
    preferences: UserPreferences;
  };
}

export interface UserPreferences {
  units: 'metric' | 'imperial';
  coordinateSystem: string;
  defaultModels: {
    saturation: 'archie' | 'simandoux' | 'indonesia';
    velocity: 'constant' | 'layered' | 'tomographic';
  };
}

/**
 * Authentication state for OpenAI integration
 */
export interface OpenAIAuth {
  status: 'unauthenticated' | 'authenticating' | 'authenticated' | 'error';
  token?: string;
  refreshToken?: string;
  expiresAt?: string;
  error?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Event Types (for window.openai bridge)
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Window.openai interface (injected by ChatGPT Apps SDK)
 */
export declare global {
  interface Window {
    openai?: {
      init: (config: OpenAIInitConfig) => Promise<void>;
      registerTools: (tools: OpenAIFunction[]) => Promise<void>;
      onToolCall: (handler: (call: OpenAIToolCall) => Promise<OpenAIToolResponse>) => void;
      emitEvent: (event: OpenAIEvent) => void;
    };
  }
}

export interface OpenAIInitConfig {
  appId: string;
  apiVersion: '2024-01-01';
  allowedDomains: string[];
  sandbox?: {
    allowScripts: boolean;
    allowForms: boolean;
  };
}

export interface OpenAIEvent {
  type: 'tool.start' | 'tool.complete' | 'tool.error' | 'session.update';
  payload: unknown;
  timestamp: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Adapter State Types
// ═══════════════════════════════════════════════════════════════════════════════

export type AdapterStatus = 'idle' | 'initializing' | 'ready' | 'error';

export interface OpenAIAdapterState {
  status: AdapterStatus;
  session: OpenAISession | null;
  auth: OpenAIAuth;
  registeredTools: string[];
  lastError: string | null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Tool Mapping Registry
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete mapping of GEOX tools to OpenAI functions
 * This is the canonical registry for the adapter
 */
export const GEOX_OPENAI_TOOL_MAP: Record<string, MappedGeoxTool> = {
  'geox_health': {
    geoxName: 'geox_health',
    openaiName: 'geox_system_health',
    description: 'Check GEOX Earth Witness system health and constitutional status. Returns version, seal status, and all F1-F13 floor states.',
    parameters: {},
    constitutionalNotes: ['F11: Returns full audit trail'],
  },
  'geox_malay_basin_pilot': {
    geoxName: 'geox_malay_basin_pilot',
    openaiName: 'geox_query_malay_basin',
    description: 'Query the Malay Basin petroleum exploration pilot dataset. Get statistics, well information, or structural interpretation data.',
    parameters: {
      query_type: {
        type: 'string',
        description: 'Type of query to execute',
        required: true,
        constraints: { pattern: '^(stats|wells|structure|production)$' },
      },
      well_id: {
        type: 'string',
        description: 'Specific well identifier (optional)',
        required: false,
      },
    },
    constitutionalNotes: ['F2: All data tagged with confidence levels', 'F7: Uncertainty quantified'],
  },
  'geox_load_seismic_line': {
    geoxName: 'geox_load_seismic_line',
    openaiName: 'geox_load_seismic',
    description: 'Load seismic line data for visualization and interpretation. Requires line ID and survey name.',
    parameters: {
      line_id: {
        type: 'string',
        description: 'Seismic line identifier',
        required: true,
      },
      survey: {
        type: 'string',
        description: 'Survey name or project code',
        required: true,
      },
      inline_range: {
        type: 'array',
        description: 'Optional inline range [start, end]',
        required: false,
      },
    },
    constitutionalNotes: ['F4: Returns clarity score for data quality'],
  },
  'geox_build_structural_candidates': {
    geoxName: 'geox_build_structural_candidates',
    openaiName: 'geox_analyze_structure',
    description: 'Generate structural interpretation candidates from seismic or well data. Uses inverse modelling constraints.',
    parameters: {
      data_source: {
        type: 'string',
        description: 'Source data type',
        required: true,
        constraints: { pattern: '^(seismic|wells|both)$' },
      },
      horizon: {
        type: 'string',
        description: 'Target horizon name',
        required: true,
      },
      max_candidates: {
        type: 'number',
        description: 'Maximum number of candidates (1-5)',
        required: false,
        default: 3,
        constraints: { min: 1, max: 5 },
      },
    },
    constitutionalNotes: ['F7: Returns multiple hypotheses', 'F2: Confidence scores attached'],
  },
  'geox_evaluate_prospect': {
    geoxName: 'geox_evaluate_prospect',
    openaiName: 'geox_evaluate_prospect',
    description: 'Evaluate petroleum prospect viability using tri-witness consensus. Returns risk matrix and recommendation.',
    parameters: {
      prospect_id: {
        type: 'string',
        description: 'Unique prospect identifier',
        required: true,
      },
      include_analogs: {
        type: 'boolean',
        description: 'Include outcrop analog data',
        required: false,
        default: true,
      },
    },
    constitutionalNotes: ['F3: Tri-witness validation', 'F7: Confidence capped at 0.90'],
  },
  'geox_calculate_saturation': {
    geoxName: 'geox_calculate_saturation',
    openaiName: 'geox_compute_saturation',
    description: 'Calculate water saturation (Sw) using Archie, Simandoux, or Indonesia models with Monte Carlo uncertainty.',
    parameters: {
      model: {
        type: 'string',
        description: 'Saturation model to use',
        required: true,
        constraints: { pattern: '^(archie|simandoux|indonesia)$' },
      },
      rt: {
        type: 'number',
        description: 'True formation resistivity (ohm-m)',
        required: true,
      },
      rw: {
        type: 'number',
        description: 'Formation water resistivity (ohm-m)',
        required: true,
      },
      porosity: {
        type: 'number',
        description: 'Porosity (fraction, 0-1)',
        required: true,
        constraints: { min: 0, max: 1 },
      },
      iterations: {
        type: 'number',
        description: 'Monte Carlo iterations (100-10000)',
        required: false,
        default: 1000,
        constraints: { min: 100, max: 10000 },
      },
    },
    constitutionalNotes: ['F7: Uncertainty quantified', 'F2: All parameters grounded'],
  },
  'geox_query_macrostrat': {
    geoxName: 'geox_query_macrostrat',
    openaiName: 'geox_query_geology',
    description: 'Query Macrostrat geological database for regional stratigraphy, lithology, and age data.',
    parameters: {
      lat: {
        type: 'number',
        description: 'Latitude (-90 to 90)',
        required: true,
        constraints: { min: -90, max: 90 },
      },
      lon: {
        type: 'number',
        description: 'Longitude (-180 to 180)',
        required: true,
        constraints: { min: -180, max: 180 },
      },
      buffer_km: {
        type: 'number',
        description: 'Search radius in kilometers',
        required: false,
        default: 10,
        constraints: { min: 0.1, max: 100 },
      },
    },
    constitutionalNotes: ['F2: External data source cited', 'F4: Structured return format'],
  },
};

/**
 * Get list of tool names available for OpenAI
 */
export const getOpenAIToolList = (): string[] => Object.keys(GEOX_OPENAI_TOOL_MAP);

/**
 * Convert GEOX tool to OpenAI function format
 */
export const mapGeoxToOpenAI = (geoxToolName: string): OpenAIFunction | null => {
  const mapping = GEOX_OPENAI_TOOL_MAP[geoxToolName];
  if (!mapping) return null;

  const properties: Record<string, OpenAIParameter> = {};
  const required: string[] = [];

  for (const [key, param] of Object.entries(mapping.parameters)) {
    properties[key] = {
      type: param.type,
      description: param.description,
      ...(param.constraints?.enum && { enum: param.constraints.enum }),
    };
    if (param.required) required.push(key);
  }

  return {
    name: mapping.openaiName,
    description: mapping.description,
    parameters: {
      type: 'object',
      properties,
      required: required.length > 0 ? required : undefined,
    },
  };
};

/**
 * Convert OpenAI function name back to GEOX tool name
 */
export const mapOpenAIToGeox = (openaiName: string): string | null => {
  const entry = Object.values(GEOX_OPENAI_TOOL_MAP).find(
    m => m.openaiName === openaiName
  );
  return entry?.geoxName || null;
};
