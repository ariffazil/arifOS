/**
 * GEOX App Runtime — Base runtime for GEOX Apps.
 *
 * Manages app lifecycle, state, and host communication.
 * DITEMPA BUKAN DIBERI
 */

import {
  GeoXEventBus,
  EventType,
  createInlineBus,
  createExternalBus,
  type AppInitializePayload,
  type HostCapabilities,
  type SecurityContext,
  type GeoXEvent,
} from './event_bus';

/** App configuration */
export interface AppConfig {
  /** App ID from manifest */
  appId: string;
  /** App version */
  version: string;
  /** Display name */
  displayName: string;
  /** Required tools */
  requiredTools: string[];
  /** Optional tools */
  optionalTools: string[];
  /** Supported events */
  supportedEvents: string[];
}

/** App state */
export interface AppState {
  /** Whether app is initialized */
  initialized: boolean;
  /** Current session ID */
  sessionId: string | null;
  /** Auth token */
  authToken: string | null;
  /** Host capabilities */
  hostCapabilities: HostCapabilities | null;
  /** Security context */
  securityContext: SecurityContext | null;
  /** App-specific state */
  data: Record<string, unknown>;
}

/**
 * GEOX App Runtime — Base class for all GEOX Apps.
 *
 * Handles:
 * - Event bus initialization
 * - Lifecycle management (init, update, destroy)
 * - State management
 * - Tool calling
 * - Telemetry
 */
export class GeoXAppRuntime {
  private bus: GeoXEventBus;
  private config: AppConfig;
  private state: AppState;
  private unsubs: (() => void)[] = [];

  /**
   * Create a new app runtime.
   *
   * @param config - App configuration
   * @param bus - Optional event bus (creates default if not provided)
   */
  constructor(config: AppConfig, bus?: GeoXEventBus) {
    this.config = config;
    this.bus = bus || this.createDefaultBus();

    this.state = {
      initialized: false,
      sessionId: null,
      authToken: null,
      hostCapabilities: null,
      securityContext: null,
      data: {},
    };

    this.setupEventHandlers();
  }

  /**
   * Create the default event bus based on runtime environment.
   */
  private createDefaultBus(): GeoXEventBus {
    // Detect if we're in an iframe (inline) or popup (external)
    const isIframe = window.parent !== window;

    if (isIframe) {
      return createInlineBus();
    } else {
      // External mode - use opener
      if (!window.opener) {
        throw new Error('External app mode requires window.opener');
      }
      return createExternalBus(window.opener, '*');
    }
  }

  /**
   * Set up default event handlers.
   */
  private setupEventHandlers(): void {
    // Handle initialization
    this.unsubs.push(
      this.bus.on<AppInitializePayload>(EventType.APP_INITIALIZE, (event) => {
        this.handleInitialize(event);
      })
    );

    // Handle context patches
    this.unsubs.push(
      this.bus.on(EventType.APP_CONTEXT_PATCH, (event) => {
        this.handleContextPatch(event);
      })
    );

    // Handle state sync requests
    this.unsubs.push(
      this.bus.on(EventType.APP_STATE_SYNC, (event) => {
        this.handleStateSync(event);
      })
    );
  }

  /**
   * Handle initialization event from host.
   */
  private handleInitialize(event: GeoXEvent<AppInitializePayload>): void {
    const payload = event.payload;

    this.state = {
      ...this.state,
      initialized: true,
      sessionId: payload.sessionId,
      authToken: payload.authToken,
      hostCapabilities: payload.hostCapabilities,
      securityContext: payload.securityContext,
    };

    // Validate capabilities
    const missingCapabilities = this.validateCapabilities(payload.hostCapabilities);
    if (missingCapabilities.length > 0) {
      console.warn('[GeoXAppRuntime] Missing capabilities:', missingCapabilities);
      this.reportError('capability_missing', { capabilities: missingCapabilities });
    }

    // Report app capabilities to host
    this.reportCapabilities();

    // Emit initialized event
    this.onInitialized();
  }

  /**
   * Handle context patch from host.
   */
  private handleContextPatch(event: GeoXEvent): void {
    if (typeof event.payload === 'object' && event.payload !== null) {
      this.state.data = {
        ...this.state.data,
        ...event.payload,
      };
      this.onContextPatched(event.payload);
    }
  }

  /**
   * Handle state sync request.
   */
  private handleStateSync(event: GeoXEvent): void {
    this.syncState();
  }

  /**
   * Validate host capabilities against app requirements.
   */
  private validateCapabilities(hostCaps: HostCapabilities): string[] {
    // This would check against manifest requirements
    // For now, return empty (no validation)
    return [];
  }

  /**
   * Report app capabilities to host.
   */
  private reportCapabilities(): void {
    this.bus.reportCapabilities({
      appId: this.config.appId,
      version: this.config.version,
      supportedEvents: this.config.supportedEvents,
    });
  }

  /**
   * Report an error to the host.
   */
  private reportError(code: string, details: Record<string, unknown>): void {
    this.bus.send(EventType.UI_ERROR, {
      code,
      details,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Get the event bus.
   */
  getBus(): GeoXEventBus {
    return this.bus;
  }

  /**
   * Get current app state.
   */
  getState(): AppState {
    return { ...this.state };
  }

  /**
   * Update app state.
   */
  setState(updater: (state: AppState) => AppState): void {
    this.state = updater(this.state);
    this.syncState();
  }

  /**
   * Synchronize state with host.
   */
  syncState(): void {
    this.bus.syncState({
      initialized: this.state.initialized,
      sessionId: this.state.sessionId,
      data: this.state.data,
    });
  }

  /**
   * Call an MCP tool via the host.
   */
  async callTool<T = unknown>(tool: string, args: Record<string, unknown>): Promise<T> {
    return this.bus.callTool<T>(tool, args);
  }

  /**
   * Send a UI action to the host.
   */
  sendAction(action: string, params: Record<string, unknown> = {}): void {
    this.bus.sendAction(action, params);
  }

  /**
   * Emit telemetry.
   */
  emitTelemetry(metric: string, value: number, dimensions: Record<string, string> = {}): void {
    this.bus.emitTelemetry(metric, value, dimensions);
  }

  /**
   * Check if app is initialized.
   */
  isInitialized(): boolean {
    return this.state.initialized;
  }

  /**
   * Wait for initialization.
   */
  async waitForInit(timeoutMs: number = 10000): Promise<void> {
    if (this.state.initialized) {
      return;
    }

    await this.bus.once(EventType.APP_INITIALIZE, timeoutMs);
  }

  /**
   * Lifecycle: Called when app is initialized.
   * Override in subclass.
   */
  protected onInitialized(): void {
    console.log('[GeoXAppRuntime] Initialized:', this.config.appId);
  }

  /**
   * Lifecycle: Called when context is patched.
   * Override in subclass.
   */
  protected onContextPatched(patch: Record<string, unknown>): void {
    // Override in subclass
  }

  /**
   * Lifecycle: Called when app is being destroyed.
   * Override in subclass.
   */
  protected onDestroy(): void {
    // Override in subclass
  }

  /**
   * Destroy the runtime.
   */
  destroy(): void {
    this.onDestroy();

    // Unsubscribe all handlers
    this.unsubs.forEach(unsub => unsub());
    this.unsubs = [];

    // Destroy event bus
    this.bus.destroy();
  }
}
