/**
 * GEOX GUI Types — DITEMPA BUKAN DIBERI
 *
 * TypeScript type definitions for the GEOX Geologist GUI.
 */

// ═══════════════════════════════════════════════════════════════════════════════
// Geospatial Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface Coordinate {
  lat: number;
  lon: number;
  depthM?: number;
}

export interface CoordinateWithMeta extends Coordinate {
  datum: string;
  crs: string;
  source: string;
  qcStatus: 'verified' | 'unverified' | 'suspect';
  uncertaintyM?: number;
}

export interface BoundingBox {
  minLat: number;
  minLon: number;
  maxLat: number;
  maxLon: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Map & Layer Types
// ═══════════════════════════════════════════════════════════════════════════════

export type MapLayerType = 'basemap' | 'wells' | 'seismic' | 'horizons' | 'faults' | 'geology' | 'aoi';

export interface MapLayer {
  id: string;
  name: string;
  type: MapLayerType;
  visible: boolean;
  opacity: number;
  data?: unknown;
  metadata: {
    source: string;
    lastUpdated: string;
    crs: string;
  };
}

export interface GeoSelection {
  type: 'point' | 'line' | 'polygon';
  coordinates: Coordinate[];
  properties?: Record<string, unknown>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Seismic Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface SeismicLine {
  id: string;
  name: string;
  type: '2d' | 'inline' | 'crossline' | 'arbitrary';
  traceCount: number;
  sampleCount: number;
  sampleInterval: number; // in ms or m
  startCoordinate: Coordinate;
  endCoordinate: Coordinate;
  crs: string;
  groundStatus: SeismicGrounding;
}

export interface SeismicGrounding {
  datum: 'verified' | 'unknown';
  scale: 'verified' | 'unknown' | 'interpolated';
  tie: 'confirmed' | 'unconfirmed' | 'none';
  velocityModel: 'calibrated' | 'regional' | 'unknown';
}

export interface SeismicData {
  lineId: string;
  traces: Float32Array[];
  minAmplitude: number;
  maxAmplitude: number;
  timeRange: [number, number]; // start, end in ms
}

export type DisplayMode = 'wiggle' | 'variable-area' | 'grayscale' | 'color';

export interface HorizonPick {
  id: string;
  name: string;
  horizonId: string;
  traceIndex: number;
  time: number;
  confidence: 'high' | 'medium' | 'low';
  tiedToWell?: string;
}

export interface StructuralCandidate {
  id: string;
  name: string; // "Candidate A", "Candidate B", etc.
  geometry: unknown; // Geometry data
  confidence: number; // 0-1
  physicalBasis: string;
  wellsTied: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Well Log Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface Well {
  id: string;
  name: string;
  uwi: string;
  location: CoordinateWithMeta;
  totalDepth: number;
  status: 'drilling' | 'completed' | 'suspended' | 'abandoned';
  formationTD?: string;
}

export type LogCurveType = 'gr' | 'sp' | 'resistivity' | 'density' | 'neutron' | 'sonic' | 'caliper' | 'image';

export interface WellLog {
  wellId: string;
  curves: LogCurve[];
  depthRange: [number, number];
  step: number;
}

export interface LogCurve {
  name: string;
  type: LogCurveType;
  unit: string;
  data: Float32Array;
  min: number;
  max: number;
  nullValue: number;
}

export interface LogTrack {
  id: string;
  curves: string[]; // Curve names
  width: number;
  scale: 'linear' | 'log';
}

export interface SeismicLogTie {
  status: 'tied' | 'untied' | 'attempted';
  confidence?: number;
  syntheticQuality?: 'good' | 'fair' | 'poor';
  checkshotUsed?: boolean;
  velocityModel?: string;
}

export interface DepthCursor {
  wellId: string;
  depth: number;
  timestamp: number;
  source: 'user' | 'sync';
}

// ═══════════════════════════════════════════════════════════════════════════════
// Outcrop Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface OutcropImage {
  id: string;
  name: string;
  location: CoordinateWithMeta;
  url: string;
  width: number;
  height: number;
  dateAcquired: string;
  geologist: string;
}

export interface Annotation {
  id: string;
  imageId: string;
  type: 'bedding' | 'fracture' | 'vein' | 'fossil' | 'clast' | 'lamination' | 'other';
  coordinates: [number, number][]; // Polygon or point
  description: string;
  confidence: 'high' | 'medium' | 'low';
  interpretedBy: string;
}

export interface AISuggestion {
  id: string;
  imageId: string;
  feature: string;
  confidence: number;
  alternatives: string[];
  reviewed: boolean;
  accepted?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Prospect Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface Prospect {
  id: string;
  name: string;
  play: string;
  reservoir: string;
  seal: string;
  trap: string;
  charge: string;
  structuralCandidates: StructuralCandidate[];
  closureType: '3-way' | '4-way' | 'stratigraphic' | 'combination';
  coordinates: Coordinate;
  area: BoundingBox;
}

export type DecisionGate = 'IGNITED' | 'QUALIFY' | 'HOLD' | 'PARTIAL' | 'SEAL' | 'VOID';

export interface EvidenceStack {
  seismic: EvidenceItem[];
  wellControl: EvidenceItem[];
  geospatial: EvidenceItem[];
  outcropAnalog: EvidenceItem[];
  mapClosure: EvidenceItem[];
}

export interface EvidenceItem {
  id: string;
  type: string;
  description: string;
  source: string;
  confidence: 'high' | 'medium' | 'low';
  linkedTo: string[]; // IDs of linked data
}

export interface RiskMatrix {
  reservoir: RiskLevel;
  seal: RiskLevel;
  trap: RiskLevel;
  charge: RiskLevel;
  timing: RiskLevel;
  dataQuality: RiskLevel;
}

export type RiskLevel = 'low' | 'moderate' | 'high' | 'unknown';

export interface MissingConstraint {
  id: string;
  description: string;
  blocksDecision: boolean;
  mitigation?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Governance Types (F1-F13)
// ═══════════════════════════════════════════════════════════════════════════════

export type FloorId = 'F1' | 'F2' | 'F3' | 'F4' | 'F5' | 'F6' | 'F7' | 'F8' | 'F9' | 'F10' | 'F11' | 'F12' | 'F13';

export type FloorStatus = 'green' | 'amber' | 'red' | 'grey';

export type FloorType = 'hard' | 'soft';

export interface ConstitutionalFloor {
  id: FloorId;
  name: string;
  description: string;
  type: FloorType;
  status: FloorStatus;
  message?: string;
  action?: () => void;
}

export interface GovernanceState {
  floors: Record<FloorId, ConstitutionalFloor>;
  overallStatus: FloorStatus;
  seal: string;
  sessionId: string;
  timestamp: string;
}

export interface GroundingStatus {
  f4Clarity: {
    datum: FloorStatus;
    scale: FloorStatus;
    tie: FloorStatus;
  };
  f7Humility: {
    candidatesAvailable: number;
    singleModelCollapsed: boolean;
  };
}

export interface UncertaintyState {
  quantified: boolean;
  bounds?: {
    lower: number;
    upper: number;
    confidence: number;
  };
  sources: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// UI Types
// ═══════════════════════════════════════════════════════════════════════════════

export type Tab = 'prospect' | 'well' | 'section' | 'earth3d' | 'time4d' | 'physics' | 'map';

export type ViewMode = '2d' | '3d';

export interface CursorState {
  panel: 'map' | 'seismic' | 'log' | 'outcrop';
  position: {
    lat?: number;
    lon?: number;
    traceIndex?: number;
    depth?: number;
    time?: number;
  };
  timestamp: number;
}

export interface PanelConfig {
  leftWidth: number; // percentage
  centerWidth: number;
  rightWidth: number;
  bottomHeight: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// MCP/GEOX Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface GeospatialVerification {
  ok: boolean;
  lat: number;
  lon: number;
  radiusM: number;
  geologicalProvince: string;
  jurisdiction: string;
  verdict: string;
  crs: string;
  constitutionalFloors: string[];
}

export interface ProspectEvaluation {
  success: boolean;
  prospectId: string;
  verdict: 'SEAL' | 'PARTIAL' | 'HOLD' | 'VOID';
  confidence: number;
  status: string;
  reason?: string;
  humanSignoffRequired: boolean;
}

export interface HealthStatus {
  ok: boolean;
  service: string;
  version: string;
  forge: string;
  fastmcpVersion: string;
  seal: string;
  constitutionalFloors: string[];
  timestamp: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Store Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface McpConnectionStatus {
  status: 'connected' | 'disconnected' | 'error' | 'checking';
  lastChecked: string | null;
  toolsAvailable: number;
  latencyMs: number | null;
}

export interface GEOXState {
  // View state
  activeTab: Tab;
  viewMode: ViewMode;
  panelConfig: PanelConfig;

  // Data
  layers: MapLayer[];
  wells: Well[];
  seismicLines: SeismicLine[];
  prospects: Prospect[];

  // Selection (synchronized)
  selectedCoordinate: Coordinate | null;
  selectedLine: string | null;
  selectedWell: string | null;
  selectedProspect: string | null;
  cursor: CursorState | null;

  // Governance
  governance: GovernanceState;
  groundingStatus: GroundingStatus;
  uncertainty: UncertaintyState;

  // Connection
  geoxConnected: boolean;
  geoxUrl: string;
  mcpConnectionStatus: McpConnectionStatus;

  // Meta
  metaLinks: Array<{ name: string; url: string }>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// UI Bridge Event Types (JSON-RPC)
// ═══════════════════════════════════════════════════════════════════════════════

export type GeoxMethod =
  | 'app.initialize'
  | 'app.context.patch'
  | 'ui.action'
  | 'ui.state.sync'
  | 'tool.request'
  | 'tool.response';

export interface GeoxEvent<T = any> {
  jsonrpc: '2.0';
  method: GeoxMethod;
  params: T;
  id?: string | number;
  timestamp: string;
}

export interface AppInitializeParams {
  app_id: string;
  user_id: string;
  host_capabilities: string[];
  initial_context: Record<string, any>;
}

export interface ContextPatchParams {
  basin?: string;
  well_id?: string;
  prospect_id?: string;
  coordinates?: Coordinate;
  depth?: number;
  [key: string]: any;
}

export interface UIActionParams {
  action: string;
  payload: any;
}

export interface UIStateSyncParams {
  state_delta: Partial<GEOXState>;
}

export interface ToolRequestParams {
  tool: string;
  arguments: Record<string, any>;
}

export interface ToolResponseParams {
  tool: string;
  result: any;
  error?: string;
}

export type GEOXAction =
  | { type: 'SET_ACTIVE_TAB'; payload: Tab }
  | { type: 'SET_VIEW_MODE'; payload: ViewMode }
  | { type: 'SELECT_COORDINATE'; payload: Coordinate | null }
  | { type: 'SELECT_LINE'; payload: string | null }
  | { type: 'SELECT_WELL'; payload: string | null }
  | { type: 'SYNC_CURSOR'; payload: CursorState }
  | { type: 'UPDATE_GOVERNANCE'; payload: Partial<GovernanceState> }
  | { type: 'UPDATE_GROUNDING'; payload: Partial<GroundingStatus> }
  | { type: 'SET_GEOX_CONNECTED'; payload: boolean }
  | { type: 'TOGGLE_LAYER'; payload: string }
  | { type: 'SET_LAYER_OPACITY'; payload: { id: string; opacity: number } };
