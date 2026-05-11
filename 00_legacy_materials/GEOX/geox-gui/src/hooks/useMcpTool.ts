/**
 * useMcpTool — Generic MCP tool caller hook
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * Wraps a single MCP tool call with { data, status, error, call, reset }.
 * Sends tool.request via postMessage to the host bridge and resolves on
 * the matching tool.response event. Timeout: 30s.
 *
 * Constitutional integration:
 *   F11 Auditability — marks amber while in-flight, green on success
 *   F12 Resilience   — marks red on error, amber on timeout
 *
 * Usage:
 *   const { data, status, error, call } = useMcpTool<MyArgs, MyResult>('geox_compute_petrophysics');
 *   await call({ model: 'archie', rw: 0.05, ... });
 */

import { useState, useCallback, useRef } from 'react';
import { useGEOXStore } from '../store/geoxStore';

export type McpToolStatus = 'idle' | 'loading' | 'success' | 'error';

export interface McpToolState<T = unknown> {
  data: T | null;
  status: McpToolStatus;
  error: string | null;
  lastCalledAt: string | null;
}

const TIMEOUT_MS = 30_000;

export function useMcpTool<TArgs = Record<string, unknown>, TResult = unknown>(
  toolName: string,
) {
  const [state, setState] = useState<McpToolState<TResult>>({
    data: null,
    status: 'idle',
    error: null,
    lastCalledAt: null,
  });

  const pendingRef = useRef<{
    resolve: (v: TResult) => void;
    reject: (e: string) => void;
    id: string;
    timer: ReturnType<typeof setTimeout>;
    handler?: (event: MessageEvent) => void;
  } | null>(null);

  const { updateFloorStatus } = useGEOXStore();

  const call = useCallback(
    (args: TArgs): Promise<TResult> => {
      // Cancel any previous in-flight call
      if (pendingRef.current) {
        clearTimeout(pendingRef.current.timer);
        if (pendingRef.current.handler) {
          window.removeEventListener('message', pendingRef.current.handler);
        }
        pendingRef.current.reject(`Superseded by new call to ${toolName}`);
        pendingRef.current = null;
      }

      return new Promise<TResult>((resolve, reject) => {
        const callId = `${toolName}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;

        setState({
          data: null,
          status: 'loading',
          error: null,
          lastCalledAt: new Date().toISOString(),
        });
        updateFloorStatus('F11', 'amber', `${toolName} in progress…`);

        const timer = setTimeout(() => {
          if (pendingRef.current?.handler) {
            window.removeEventListener('message', pendingRef.current.handler);
          }
          pendingRef.current = null;
          const msg = `${toolName} timed out after ${TIMEOUT_MS / 1000}s`;
          setState(prev => ({ ...prev, status: 'error', error: msg }));
          updateFloorStatus('F12', 'amber', msg);
          reject(msg);
        }, TIMEOUT_MS);

        pendingRef.current = { resolve, reject, id: callId, timer };

        function _handleResponse(event: MessageEvent) {
          const data = event.data;
          if (data?.jsonrpc !== '2.0' || data?.method !== 'tool.response') return;
          if (data?.params?.tool !== toolName) return;

          clearTimeout(timer);
          window.removeEventListener('message', _handleResponse);
          pendingRef.current = null;

          if (data.params.error) {
            const errMsg = String(data.params.error);
            setState(prev => ({ ...prev, status: 'error', error: errMsg }));
            updateFloorStatus('F12', 'red', `${toolName} error: ${errMsg}`);
            reject(errMsg);
          } else {
            const result = data.params.result as TResult;
            setState(prev => ({ ...prev, data: result, status: 'success', error: null }));
            updateFloorStatus('F11', 'green', `${toolName} completed`);
            resolve(result);
          }
        }

        pendingRef.current.handler = _handleResponse;
        window.addEventListener('message', _handleResponse);

        window.parent.postMessage(
          {
            jsonrpc: '2.0',
            method: 'tool.request',
            params: { tool: toolName, arguments: args },
            id: callId,
            timestamp: new Date().toISOString(),
          },
          '*',
        );
      });
    },
    [toolName, updateFloorStatus],
  );

  const reset = useCallback(() => {
    if (pendingRef.current) {
      clearTimeout(pendingRef.current.timer);
      pendingRef.current = null;
    }
    setState({ data: null, status: 'idle', error: null, lastCalledAt: null });
  }, []);

  return { ...state, call, reset };
}
