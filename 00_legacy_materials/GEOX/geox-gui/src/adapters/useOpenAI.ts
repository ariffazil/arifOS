/**
 * useOpenAI — React Hook for OpenAI Adapter
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * React hook for integrating ChatGPT Apps SDK with GEOX components.
 * Provides reactive access to adapter state and initialization controls.
 *
 * Constitutional Integration:
 *   F11 Auditability — Tracks all OpenAI interactions in component state
 *   F12 Resilience   — Error boundaries and recovery mechanisms
 *   F13 Sovereign    — User can disable OpenAI integration at any time
 *
 * @module adapters/useOpenAI
 * @version 0.6.1
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  initOpenAIAdapter,
  getAdapterState,
  subscribeToAdapter,
  isAdapterReady,
  getSessionId,
  resetAdapter,
} from './openai_adapter';
import {
  OpenAIAdapterState,
  AdapterStatus,
  OpenAISession,
  OpenAIInitConfig,
} from './openai_types';

// ═══════════════════════════════════════════════════════════════════════════════
// Hook Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface UseOpenAIReturn {
  // State
  status: AdapterStatus;
  isReady: boolean;
  isError: boolean;
  error: string | null;
  session: OpenAISession | null;
  registeredTools: string[];

  // Actions
  init: (config?: Partial<OpenAIInitConfig>) => Promise<void>;
  reset: () => void;
  refreshState: () => void;

  // Metadata
  sessionId: string | null;
  toolCount: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Hook Implementation
// ═══════════════════════════════════════════════════════════════════════════════

export function useOpenAI(): UseOpenAIReturn {
  // Local state mirrored from adapter
  const [state, setState] = useState<OpenAIAdapterState>(getAdapterState());
  const [isInitializing, setIsInitializing] = useState(false);

  // Refs for cleanup
  const unsubscribeRef = useRef<(() => void) | null>(null);
  const mountedRef = useRef(true);

  // Subscribe to adapter state changes
  useEffect(() => {
    mountedRef.current = true;

    unsubscribeRef.current = subscribeToAdapter((newState) => {
      if (mountedRef.current) {
        setState(newState);
        if (newState.status === 'ready' || newState.status === 'error') {
          setIsInitializing(false);
        }
      }
    });

    return () => {
      mountedRef.current = false;
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
      }
    };
  }, []);

  // Initialize adapter
  const init = useCallback(async (config?: Partial<OpenAIInitConfig>) => {
    if (isInitializing || state.status === 'ready') {
      return;
    }

    setIsInitializing(true);
    try {
      await initOpenAIAdapter(config);
    } catch (error) {
      // Error is handled by adapter state, just stop loading
      if (mountedRef.current) {
        setIsInitializing(false);
      }
    }
  }, [isInitializing, state.status]);

  // Reset adapter
  const reset = useCallback(() => {
    resetAdapter();
  }, []);

  // Manual state refresh
  const refreshState = useCallback(() => {
    setState(getAdapterState());
  }, []);

  // Derived state
  const isReady = state.status === 'ready';
  const isError = state.status === 'error';

  return {
    // State
    status: state.status,
    isReady,
    isError,
    error: state.lastError,
    session: state.session,
    registeredTools: state.registeredTools,

    // Actions
    init,
    reset,
    refreshState,

    // Metadata
    sessionId: getSessionId(),
    toolCount: state.registeredTools.length,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// Specialized Hooks
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Hook for checking if specific tool is available
 */
export function useOpenAIToolAvailable(toolName: string): boolean {
  const { registeredTools, isReady } = useOpenAI();
  return isReady && registeredTools.includes(toolName);
}

/**
 * Hook for auto-initializing OpenAI adapter
 */
export function useAutoInitOpenAI(
  config?: Partial<OpenAIInitConfig>,
  enabled: boolean = true
): UseOpenAIReturn {
  const openai = useOpenAI();

  useEffect(() => {
    if (enabled && openai.status === 'idle' && !openai.isError) {
      openai.init(config);
    }
  }, [enabled, openai.status, openai.isError]);

  return openai;
}

/**
 * Hook for OpenAI session metadata
 */
export function useOpenAISession(): {
  sessionId: string | null;
  geoxSessionId: string | null;
  createdAt: string | null;
  expiresAt: string | null;
  isActive: boolean;
} {
  const { session, isReady } = useOpenAI();

  return {
    sessionId: session?.id || null,
    geoxSessionId: session?.geoxSessionId || null,
    createdAt: session?.createdAt || null,
    expiresAt: session?.expiresAt || null,
    isActive: isReady && !!session,
  };
}

export default useOpenAI;
