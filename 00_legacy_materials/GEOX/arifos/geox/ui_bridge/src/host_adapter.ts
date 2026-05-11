/**
 * GEOX Host Adapter — Adapter interface for different host platforms.
 *
 * Provides a unified interface for:
 * - Copilot
 * - Claude Desktop
 * - OpenAI Apps
 * - Custom GEOX host
 *
 * DITEMPA BUKAN DIBERI
 */

import {
  GeoXEventBus,
  GeoXHostBus,
  EventType,
  type HostCapabilities,
  type SecurityContext,
  type AppInitializePayload,
} from './event_bus';

/** Supported render modes */
export type RenderMode = 'inline' | 'external' | 'card' | 'text';

/** Host adapter configuration */
export interface HostAdapterConfig {
  /** Host type identifier */
  hostType: 'copilot' | 'claude' | 'openai' | 'geox-custom';
  /** Host version */
  version: string;
  /** Supported render modes */
  supportedModes: RenderMode[];
  /** Maximum inline dimensions */
  maxInlineSize?: { width: number; height: number };
  /** App origin for security */
  appOrigin: string;
}

/**
 * Abstract base class for host adapters.
 *
 * Implementations handle platform-specific concerns while exposing
 * a unified interface to GEOX Apps.
 */
export abstract class HostAdapter {
  protected config: HostAdapterConfig;
  protected capabilities: HostCapabilities;

  constructor(config: HostAdapterConfig) {
    this.config = config;
    this.capabilities = this.buildCapabilities();
  }

  /**
   * Build host capabilities report.
   */
  private buildCapabilities(): HostCapabilities {
    return {
      hostType: this.config.hostType,
      version: this.config.version,
      supportedModes: this.config.supportedModes,
      maxInlineSize: this.config.maxInlineSize,
      capabilities: this.getCapabilities(),
      supportsWebGL: true,
      supportsWASM: true,
    };
  }

  /**
   * Get platform-specific capabilities.
   * Override in subclass.
   */
  protected abstract getCapabilities(): string[];

  /**
   * Render an app inline.
   * Returns an event bus for communication.
   */
  abstract renderInline(
    container: HTMLElement,
    appUrl: string,
    initPayload: AppInitializePayload
  ): Promise<GeoXHostBus>;

  /**
   * Launch an app in external mode.
   */
  abstract launchExternal(
    appUrl: string,
    initPayload: AppInitializePayload
  ): Promise<GeoXEventBus | null>;

  /**
   * Render a card fallback.
   */
  abstract renderCard(
    container: HTMLElement,
    data: Record<string, unknown>
  ): void;

  /**
   * Get host capabilities.
   */
  getCapabilities(): HostCapabilities {
    return this.capabilities;
  }

  /**
   * Check if a render mode is supported.
   */
  supportsMode(mode: RenderMode): boolean {
    return this.config.supportedModes.includes(mode);
  }

  /**
   * Negotiate the best render mode for an app.
   */
  negotiateMode(
    appPreferred: RenderMode,
    appFallbacks: RenderMode[]
  ): RenderMode {
    const preferences = [appPreferred, ...appFallbacks];

    for (const mode of preferences) {
      if (this.supportsMode(mode)) {
        return mode;
      }
    }

    // Ultimate fallback
    return 'text';
  }
}

/**
 * Generic host adapter for standard web environments.
 */
export class GenericHostAdapter extends HostAdapter {
  protected getCapabilities(): string[] {
    return [
      'postMessage',
      'iframe_sandbox',
      'window_open',
      'localStorage',
    ];
  }

  async renderInline(
    container: HTMLElement,
    appUrl: string,
    initPayload: AppInitializePayload
  ): Promise<GeoXHostBus> {
    // Create iframe
    const iframe = document.createElement('iframe');
    iframe.src = appUrl;
    iframe.sandbox.add('allow-scripts', 'allow-same-origin', 'allow-forms');
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.border = 'none';

    container.appendChild(iframe);

    // Wait for iframe to load
    await new Promise<void>((resolve, reject) => {
      iframe.onload = () => resolve();
      iframe.onerror = () => reject(new Error('Failed to load app iframe'));

      // Timeout
      setTimeout(() => reject(new Error('Iframe load timeout')), 10000);
    });

    // Create host bus
    const bus = new GeoXHostBus(this.config.appOrigin);
    bus.attach(iframe);

    // Initialize the app
    bus.initialize(initPayload);

    return bus;
  }

  async launchExternal(
    appUrl: string,
    initPayload: AppInitializePayload
  ): Promise<GeoXEventBus | null> {
    // Open popup
    const features = 'width=1400,height=900,menubar=no,toolbar=no,location=no';
    const popup = window.open(appUrl, '_blank', features);

    if (!popup) {
      console.error('[GenericHostAdapter] Popup blocked');
      return null;
    }

    // Create event bus
    const bus = new GeoXEventBus(popup, this.config.appOrigin);

    // Wait for popup to load, then initialize
    setTimeout(() => {
      bus.send(EventType.APP_INITIALIZE, initPayload);
    }, 1000);

    return bus;
  }

  renderCard(
    container: HTMLElement,
    data: Record<string, unknown>
  ): void {
    // Simple card rendering
    const card = document.createElement('div');
    card.className = 'geox-card';
    card.innerHTML = `
      <div class="geox-card-header">
        <h3>${data.title || 'GEOX Result'}</h3>
      </div>
      <div class="geox-card-body">
        <pre>${JSON.stringify(data, null, 2)}</pre>
      </div>
    `;
    container.appendChild(card);
  }
}

/**
 * Copilot host adapter.
 *
 * Handles Copilot-specific integration points.
 */
export class CopilotHostAdapter extends GenericHostAdapter {
  protected getCapabilities(): string[] {
    return [
      ...super.getCapabilities(),
      'copilot_skills',
      'copilot_actions',
    ];
  }

  async renderInline(
    container: HTMLElement,
    appUrl: string,
    initPayload: AppInitializePayload
  ): Promise<GeoXHostBus> {
    // Copilot may have specific iframe requirements
    // For now, use generic implementation
    return super.renderInline(container, appUrl, initPayload);
  }
}

/**
 * Claude Desktop host adapter.
 *
 * Handles Claude artifact protocol.
 */
export class ClaudeHostAdapter extends GenericHostAdapter {
  protected getCapabilities(): string[] {
    return [
      ...super.getCapabilities(),
      'claude_artifacts',
      'claude_streaming',
    ];
  }

  async renderInline(
    container: HTMLElement,
    appUrl: string,
    initPayload: AppInitializePayload
  ): Promise<GeoXHostBus> {
    // Claude has rich artifact support
    // Could use custom artifact renderer here
    return super.renderInline(container, appUrl, initPayload);
  }
}

/**
 * OpenAI Apps host adapter.
 *
 * Handles OpenAI Apps SDK conventions.
 */
export class OpenAIAppsHostAdapter extends GenericHostAdapter {
  protected getCapabilities(): string[] {
    return [
      ...super.getCapabilities(),
      'openai_widgets',
      'openai_templates',
    ];
  }

  async renderInline(
    container: HTMLElement,
    appUrl: string,
    initPayload: AppInitializePayload
  ): Promise<GeoXHostBus> {
    // OpenAI Apps may use widget protocol
    // For now, use generic iframe approach
    return super.renderInline(container, appUrl, initPayload);
  }
}

/**
 * Host adapter factory.
 */
export function createHostAdapter(
  type: 'copilot' | 'claude' | 'openai' | 'generic',
  config: Omit<HostAdapterConfig, 'hostType'>
): HostAdapter {
  const fullConfig: HostAdapterConfig = {
    hostType: type,
    ...config,
  };

  switch (type) {
    case 'copilot':
      return new CopilotHostAdapter(fullConfig);
    case 'claude':
      return new ClaudeHostAdapter(fullConfig);
    case 'openai':
      return new OpenAIAppsHostAdapter(fullConfig);
    case 'generic':
    default:
      return new GenericHostAdapter(fullConfig);
  }
}
