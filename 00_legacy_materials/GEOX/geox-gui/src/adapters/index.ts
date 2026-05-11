/**
 * OpenAI Adapter — Index
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * Central export for OpenAI ChatGPT Apps SDK integration.
 *
 * @module adapters
 * @version 0.6.1
 */

// Types
export type {
  OpenAIFunction,
  OpenAIToolCall,
  OpenAIToolResponse,
  OpenAISession,
  OpenAIAdapterState,
  AdapterStatus,
  OpenAIEvent,
  GeoxToolResult,
  MappedGeoxTool,
  OpenAIInitConfig,
  OpenAIAuth,
  UserPreferences,
} from './openai_types';

// Type utilities
export {
  GEOX_OPENAI_TOOL_MAP,
  getOpenAIToolList,
  mapGeoxToOpenAI,
  mapOpenAIToGeox,
} from './openai_types';

// Adapter core
export {
  initOpenAIAdapter,
  getAdapterState,
  subscribeToAdapter,
  isAdapterReady,
  getSessionId,
  resetAdapter,
} from './openai_adapter';

// React hooks
export {
  useOpenAI,
  useOpenAIToolAvailable,
  useAutoInitOpenAI,
  useOpenAISession,
} from './useOpenAI';

// Default export
export { default } from './openai_adapter';
