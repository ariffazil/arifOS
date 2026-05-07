/**
 * GEOX UI Event Bus — Host-agnostic communication layer for GEOX Apps.
 *
 * Implements the canonical event protocol over postMessage/JSON-RPC.
 * Works in both inline (iframe) and external (popup/window) modes.
 *
 * DITEMPA BUKAN DIBERI
 */

// ═══════════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════════

/** Event source identifier */
export type EventSource = 'host' | 'app';

/** Canonical event types */
export enum EventType {
  // App lifecycle
  APP_INITIALIZE = 'app.initialize',
  APP_CONTEXT_PATCH = 'app.context.patch',
  APP_STATE_SYNC = 'app.state.sync',

  // Tool interaction
  TOOL_REQUEST = 'tool.request',
  TOOL_RESULT = 'tool.result',
  TOOL_PROGRESS = 'tool.progress',

  // UI interaction
  UI_ACTION = 'ui.action',
  UI_STATE_CHANGE = 'ui.state.change',
  UI_ERROR = 'ui.error',

  // Auth
  AUTH_CHALLENGE = 'auth.challenge',
  AUTH_RESULT = 'auth.result',
  AUTH_REFRESH = 'auth.refresh',

  // Host
  HOST_CAPABILITY_REPORT = 'host.capability.report',
  HOST_RESIZE = 'host.resize',
  HOST_FOCUS = 'host.focus',
  HOST_OPEN_EXTERNAL = 'host.open.external',
  HOST_CLOSE = 'host.close',

  // Telemetry
  TELEMETRY_EMIT = 'telemetry.emit',
  TELEMETRY_FLUSH = 'telemetry.flush',
}

/** Base event structure */
export interface GeoXEvent<T = unknown> {
  /** Event type */
  type: EventType;
  /** Event source */
  source: EventSource;
  /** ISO 8601 timestamp */
  timestamp: string;
  /** Event payload */
  payload: T;
  /** Correlation ID for tracing */
  traceId: string;
  /** Sequence number for ordering */
  sequence: number;
}

/** Host capabilities report */
export interface HostCapabilities {
  hostType: 'copilot' | 'claude' | 'openai' | 'geox-custom' | 'unknown';
  version: string;
  supportedModes: ('inline' | 'external' | 'card' | 'text')[];
  maxInlineSize?: { width: number; height: number };
  capabilities: string[];
  supportsWebGL: boolean;
  supportsWASM: boolean;
}

/** Security context from host */
export interface SecurityContext {
  userId: string;
  tenantId: string;
  sessionId: string;
  permissions: string[];
  expiresAt: string;
}

/** App initialization payload */
export interface AppInitializePayload {
  sessionId: string;
  authToken: string;
  context: Record<string, unknown>;
  hostCapabilities: HostCapabilities;
  securityContext: SecurityContext;
}

/** Tool request payload */
export interface ToolRequestPayload {
  requestId: string;
  tool: string;
  args: Record<string, unknown>;
}

/** Tool result payload */
export interface ToolResultPayload {
  requestId: string;
  result: unknown;
  error?: string;
}

/** UI action payload */
export interface UiActionPayload {
  action: string;
  params: Record<string, unknown>;
  target?: string;
}

/** Telemetry payload */
export interface TelemetryPayload {
  metric: string;
  value: number;
  dimensions: Record<string, string>;
  timestamp: string;
}

/** Auth challenge payload */
export interface AuthChallengePayload {
  challenge: string;
  scope: string[];
}

/** Auth result payload */
export interface AuthResultPayload {
  token: string;
  expiresAt: string;
  refreshToken?: string;
}

/** Event handler type */
export type EventHandler<T = unknown> = (event: GeoXEvent<T>) => void | Promise<void>;

/** Event filter type */
export type EventFilter = (event: GeoXEvent) => boolean;

// ═══════════════════════════════════════════════════════════════════════════════
// Event Bus Implementation
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * GEOX Event Bus — Central communication hub for GEOX Apps.
 *
 * Handles:
 * - Sending/receiving events via postMessage
 * - Event routing and filtering
 * - Sequence numbering for ordering
 * - Trace ID propagation
 * - Connection state management
 */
export class GeoXEventBus {
  private targetWindow: Window;
  private targetOrigin: string;
  private handlers: Map<EventType, Set<EventHandler>> = new Map();
  private sequence: number = 0;
  private traceId: string;
  private isConnected: boolean = false;
  private pendingEvents: GeoXEvent[] = [];
  private messageListener: ((event: MessageEvent) => void) | null = null;

  /**
   * Create a new event bus.
   *
   * @param targetWindow - Window to send messages to (parent for inline, opener for external)
   * @param targetOrigin - Expected origin of messages (for security)
   * @param traceId - Optional trace ID for distributed tracing
   */
  constructor(targetWindow: Window, targetOrigin: string = '*', traceId?: string) {
    this.targetWindow = targetWindow;
    this.targetOrigin = targetOrigin;
    this.traceId = traceId || this.generateTraceId();

    this.setupMessageListener();
  }

  /**
   * Generate a unique trace ID.
   */
  private generateTraceId(): string {
    return `geox-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Set up the message event listener.
   */
  private setupMessageListener(): void {
    this.messageListener = (event: MessageEvent) => {
      // Security: validate origin if specified
      if (this.targetOrigin !== '*' && event.origin !== this.targetOrigin) {
        console.warn(`[GeoXEventBus] Rejected message from unexpected origin: ${event.origin}`);
        return;
      }

      // Validate event structure
      const geoXEvent = event.data as GeoXEvent;
      if (!this.isValidEvent(geoXEvent)) {
        return;
      }

      // Handle the event
      this.handleIncomingEvent(geoXEvent);
    };

    window.addEventListener('message', this.messageListener);
  }

  /**
   * Validate that a message is a proper GeoXEvent.
   */
  private isValidEvent(data: unknown): data is GeoXEvent {
    if (typeof data !== 'object' || data === null) {
      return false;
    }

    const event = data as Partial<GeoXEvent>;

    return (
      typeof event.type === 'string' &&
      typeof event.source === 'string' &&
      typeof event.timestamp === 'string' &&
      typeof event.traceId === 'string' &&
      typeof event.sequence === 'number'
    );
  }

  /**
   * Handle an incoming event.
   */
  private handleIncomingEvent(event: GeoXEvent): void {
    // Update connection state on initialize
    if (event.type === EventType.APP_INITIALIZE) {
      this.isConnected = true;
      this.flushPendingEvents();
    }

    // Route to handlers
    const handlers = this.handlers.get(event.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(event);
        } catch (error) {
          console.error(`[GeoXEventBus] Handler error for ${event.type}:`, error);
        }
      });
    }

    // Broadcast to wildcard handlers
    const wildcardHandlers = this.handlers.get('*' as EventType);
    if (wildcardHandlers) {
      wildcardHandlers.forEach(handler => {
        try {
          handler(event);
        } catch (error) {
          console.error(`[GeoXEventBus] Wildcard handler error:`, error);
        }
      });
    }
  }

  /**
   * Send an event to the target window.
   */
  send<T = unknown>(type: EventType, payload: T): void {
    const event: GeoXEvent<T> = {
      type,
      source: 'app',
      timestamp: new Date().toISOString(),
      payload,
      traceId: this.traceId,
      sequence: ++this.sequence,
    };

    if (!this.isConnected && type !== EventType.APP_INITIALIZE) {
      // Queue events until initialized
      this.pendingEvents.push(event);
      return;
    }

    this.dispatch(event);
  }

  /**
   * Dispatch an event to the target window.
   */
  private dispatch(event: GeoXEvent): void {
    try {
      this.targetWindow.postMessage(event, this.targetOrigin);
    } catch (error) {
      console.error('[GeoXEventBus] Failed to send event:', error);
    }
  }

  /**
   * Flush pending events after connection.
   */
  private flushPendingEvents(): void {
    while (this.pendingEvents.length > 0) {
      const event = this.pendingEvents.shift();
      if (event) {
        this.dispatch(event);
      }
    }
  }

  /**
   * Subscribe to events of a specific type.
   *
   * @param type - Event type to subscribe to, or '*' for all events
   * @param handler - Handler function
   * @returns Unsubscribe function
   */
  on<T = unknown>(type: EventType | '*', handler: EventHandler<T>): () => void {
    const eventType = type === '*' ? '*': type;

    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }

    const handlers = this.handlers.get(eventType)!;
    handlers.add(handler as EventHandler);

    // Return unsubscribe function
    return () => {
      handlers.delete(handler as EventHandler);
    };
  }

  /**
   * Subscribe to a single event of a specific type.
   *
   * @param type - Event type to wait for
   * @param timeoutMs - Optional timeout in milliseconds
   * @returns Promise that resolves with the event
   */
  once<T = unknown>(type: EventType, timeoutMs?: number): Promise<GeoXEvent<T>> {
    return new Promise((resolve, reject) => {
      const unsubscribe = this.on<T>(type, (event) => {
        unsubscribe();
        resolve(event);
      });

      if (timeoutMs) {
        setTimeout(() => {
          unsubscribe();
          reject(new Error(`Timeout waiting for event: ${type}`));
        }, timeoutMs);
      }
    });
  }

  /**
   * Send a tool request and wait for the result.
   *
   * @param tool - Tool name
   * @param args - Tool arguments
   * @param timeoutMs - Timeout in milliseconds
   * @returns Promise that resolves with the tool result
   */
  async callTool<T = unknown>(
    tool: string,
    args: Record<string, unknown>,
    timeoutMs: number = 30000
  ): Promise<T> {
    const requestId = `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Send request
    this.send<ToolRequestPayload>(EventType.TOOL_REQUEST, {
      requestId,
      tool,
      args,
    });

    // Wait for result
    const resultEvent = await this.once<ToolResultPayload>(
      EventType.TOOL_RESULT,
      timeoutMs
    );

    if (resultEvent.payload.requestId !== requestId) {
      throw new Error('Mismatched request ID in tool result');
    }

    if (resultEvent.payload.error) {
      throw new Error(resultEvent.payload.error);
    }

    return resultEvent.payload.result as T;
  }

  /**
   * Report capabilities to the host.
   */
  reportCapabilities(capabilities: Partial<HostCapabilities>): void {
    this.send(EventType.HOST_CAPABILITY_REPORT, capabilities);
  }

  /**
   * Emit telemetry data.
   */
  emitTelemetry(metric: string, value: number, dimensions: Record<string, string> = {}): void {
    this.send<TelemetryPayload>(EventType.TELEMETRY_EMIT, {
      metric,
      value,
      dimensions,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Send a UI action to the host.
   */
  sendAction(action: string, params: Record<string, unknown> = {}): void {
    this.send<UiActionPayload>(EventType.UI_ACTION, {
      action,
      params,
    });
  }

  /**
   * Synchronize UI state with the host.
   */
  syncState(state: Record<string, unknown>): void {
    this.send(EventType.APP_STATE_SYNC, state);
  }

  /**
   * Get the current trace ID.
   */
  getTraceId(): string {
    return this.traceId;
  }

  /**
   * Check if the bus is connected to the host.
   */
  getIsConnected(): boolean {
    return this.isConnected;
  }

  /**
   * Destroy the event bus and clean up listeners.
   */
  destroy(): void {
    if (this.messageListener) {
      window.removeEventListener('message', this.messageListener);
      this.messageListener = null;
    }
    this.handlers.clear();
    this.isConnected = false;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Host-side Event Bus
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Host-side event bus for embedding GEOX Apps.
 *
 * Used by hosts (Copilot, Claude, etc.) to communicate with embedded apps.
 */
export class GeoXHostBus {
  private iframe: HTMLIFrameElement | null = null;
  private bus: GeoXEventBus | null = null;
  private appOrigin: string;

  constructor(appOrigin: string) {
    this.appOrigin = appOrigin;
  }

  /**
   * Attach to an iframe containing a GEOX App.
   */
  attach(iframe: HTMLIFrameElement): GeoXEventBus {
    this.iframe = iframe;

    if (!iframe.contentWindow) {
      throw new Error('Iframe content window not available');
    }

    this.bus = new GeoXEventBus(iframe.contentWindow, this.appOrigin);
    return this.bus;
  }

  /**
   * Initialize the app with context.
   */
  initialize(payload: AppInitializePayload): void {
    if (!this.bus) {
      throw new Error('Host bus not attached to iframe');
    }
    this.bus.send(EventType.APP_INITIALIZE, payload);
  }

  /**
   * Send a tool result to the app.
   */
  sendToolResult(requestId: string, result: unknown, error?: string): void {
    if (!this.bus) {
      throw new Error('Host bus not attached');
    }
    this.bus.send<ToolResultPayload>(EventType.TOOL_RESULT, {
      requestId,
      result,
      error,
    });
  }

  /**
   * Challenge the app for authentication.
   */
  challengeAuth(challenge: string, scope: string[]): void {
    if (!this.bus) {
      throw new Error('Host bus not attached');
    }
    this.bus.send<AuthChallengePayload>(EventType.AUTH_CHALLENGE, {
      challenge,
      scope,
    });
  }

  /**
   * Get the underlying event bus.
   */
  getBus(): GeoXEventBus | null {
    return this.bus;
  }

  /**
   * Destroy the host bus.
   */
  destroy(): void {
    if (this.bus) {
      this.bus.destroy();
      this.bus = null;
    }
    this.iframe = null;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Factory Functions
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Create an event bus for an inline (iframe) app.
 *
 * @param hostOrigin - Origin of the host window
 * @returns GeoXEventBus instance
 */
export function createInlineBus(hostOrigin: string = '*'): GeoXEventBus {
  return new GeoXEventBus(window.parent, hostOrigin);
}

/**
 * Create an event bus for an external (popup) app.
 *
 * @param opener - Opener window
 * @param hostOrigin - Origin of the host
 * @returns GeoXEventBus instance
 */
export function createExternalBus(opener: Window, hostOrigin: string): GeoXEventBus {
  return new GeoXEventBus(opener, hostOrigin);
}

/**
 * Create a host bus for embedding apps.
 *
 * @param appOrigin - Origin of the embedded app
 * @returns GeoXHostBus instance
 */
export function createHostBus(appOrigin: string): GeoXHostBus {
  return new GeoXHostBus(appOrigin);
}
