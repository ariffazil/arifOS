/**
 * GEOX UI Bridge — Host-agnostic communication for GEOX Apps.
 *
 * DITEMPA BUKAN DIBERI
 */

export {
  // Event Bus
  GeoXEventBus,
  GeoXHostBus,
  createInlineBus,
  createExternalBus,
  createHostBus,

  // Types
  EventType,
  type EventSource,
  type GeoXEvent,
  type EventHandler,
  type EventFilter,
  type HostCapabilities,
  type SecurityContext,

  // Payload types
  type AppInitializePayload,
  type ToolRequestPayload,
  type ToolResultPayload,
  type UiActionPayload,
  type TelemetryPayload,
  type AuthChallengePayload,
  type AuthResultPayload,
} from './event_bus';

export {
  GeoXAppRuntime,
  type AppConfig,
  type AppState,
} from './runtime';

export {
  HostAdapter,
  type HostAdapterConfig,
  type RenderMode,
} from './host_adapter';
