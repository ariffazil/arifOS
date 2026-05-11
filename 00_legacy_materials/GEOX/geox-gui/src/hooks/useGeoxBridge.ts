/**
 * GEOX Bridge Hook — DITEMPA BUKAN DIBERI
 *
 * React hook to manage the postMessage/JSON-RPC bridge between
 * the GEOX App and the Host environment (ChatGPT, Claude, etc.).
 */

import { useEffect, useCallback } from 'react';
import { useGEOXStore } from '../store/geoxStore';
import type {
  GeoxEvent,
  GeoxMethod,
  ContextPatchParams,
  ToolResponseParams,
  ToolRequestParams
} from '../types';

export function useGeoxBridge() {
  const store = useGEOXStore();
  const hostWindow = typeof window !== 'undefined' && window.parent !== window ? window.parent : null;

  const sendMessage = useCallback((method: GeoxMethod, params: any, id?: string | number) => {
    if (!hostWindow) {
      return;
    }

    const event: GeoxEvent = {
      jsonrpc: '2.0',
      method,
      params,
      id: id || Math.random().toString(36).substring(7),
      timestamp: new Date().toISOString(),
    };

    console.log(`[GEOX Bridge] Sending: ${method}`, event);
    hostWindow.postMessage(event, '*');
  }, [hostWindow]);

  // UI helpers
  const sendUiAction = useCallback((action: string, payload: any) => {
    sendMessage('ui.action', { action, payload });
  }, [sendMessage]);

  const sendStateSync = useCallback((stateDelta: any) => {
    sendMessage('ui.state.sync', { state_delta: stateDelta });
  }, [sendMessage]);

  const sendToolRequest = useCallback((tool: string, args: any) => {
    sendMessage('tool.request', { tool, arguments: args } as ToolRequestParams);
  }, [sendMessage]);

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // Basic JSON-RPC validation
      const data = event.data as GeoxEvent;
      if (!data || data.jsonrpc !== '2.0') return;

      console.log(`[GEOX Bridge] Received: ${data.method}`, data);

      switch (data.method) {
        case 'app.context.patch': {
          const params = data.params as ContextPatchParams;
          // Apply context to store
          if (params.coordinates) store.selectCoordinate(params.coordinates);
          if (params.well_id) store.selectWell(params.well_id);
          if (params.prospect_id) store.selectProspect(params.prospect_id);
          // Update governance if host signals new context
          store.updateFloorStatus('F11', 'green', 'Context updated from host');
          break;
        }

        case 'tool.response': {
          const params = data.params as ToolResponseParams;
          if (params.error) {
            console.error(`[GEOX Bridge] Tool ${params.tool} failed:`, params.error);
            store.updateFloorStatus('F12', 'red', `Tool ${params.tool} error: ${params.error}`);
          } else {
            console.log(`[GEOX Bridge] Tool ${params.tool} result:`, params.result);
            store.updateFloorStatus('F11', 'green', `Tool ${params.tool} result received`);
            // Trigger specific store updates based on tool name if needed
          }
          break;
        }

        case 'app.initialize': {
          console.log('[GEOX Bridge] App re-initialization requested');
          // Usually handled at mount, but can be triggered by host
          break;
        }

        default:
          console.warn(`[GEOX Bridge] Unknown method: ${data.method}`);
      }
    };

    window.addEventListener('message', handleMessage);

    if (hostWindow) {
      sendMessage('app.initialize', {
        app_id: 'geox.gui.main',
        user_id: 'local-user', // Should be dynamic
        host_capabilities: ['inline-app', 'mcp-tools'],
        initial_context: {}
      });
    }

    return () => window.removeEventListener('message', handleMessage);
  }, [hostWindow, store, sendMessage]);

  return {
    sendUiAction,
    sendStateSync,
    sendToolRequest
  };
}
