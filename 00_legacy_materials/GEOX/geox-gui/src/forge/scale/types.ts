/**
 * GeoScale Types — Earth True Scale Transformation
 * ═══════════════════════════════════════════════════════════════════════════════
 * Type definitions for the scale-aware layer
 */

/**
 * Dimensional Domain — 000-999 Architecture
 */
export type ScaleDomain = '1d' | '2d' | '3d' | 'void';

/**
 * Pixel coordinates in image space
 */
export interface PixelCoordinate {
  x?: number;
  y?: number;
}

/**
 * World coordinates in physical space
 */
export interface WorldCoordinate {
  x?: number;
  y?: number;
  z?: number;
  depth?: number;
  twt?: number; // Two-way time in ms
  age?: number; // Age in Ma
  inline?: number;
  xline?: number;
  crs?: string;
}

/**
 * Spatial Reference System
 */
export interface SpatialReference {
  crs: string; // EPSG code (e.g., 'EPSG:4326') or WKT
  bounds: {
    minX: number;
    minY: number;
    maxX: number;
    maxY: number;
  };
  datum?: string;
  projection?: string;
}

/**
 * Temporal Reference System
 */
export interface TemporalReference {
  ageModel: string;
  referenceFrame?: string;
  velocityModel?: number[];
  timeRange?: {
    min: number;
    max: number;
    unit: 'ma' | 'ka' | 'years';
  };
}

/**
 * Calibration result for any dimension
 */
export interface CalibrationResult {
  domain: ScaleDomain;
  pixel: PixelCoordinate;
  world: WorldCoordinate;
  confidence: number; // 0-1
  units: Record<string, string>;
  metadata?: Record<string, unknown>;
}

/**
 * Calibrated point with full context
 */
export interface CalibratedPoint {
  id: string;
  timestamp: string;
  calibration: CalibrationResult;
  source: string;
  quality: 'high' | 'medium' | 'low';
}

/**
 * Geometric transformation
 */
export interface GeoTransform {
  scale: { x: number; y: number; z?: number };
  rotation: number;
  shear: { x: number; y: number };
  translation: { x: number; y: number; z?: number };
}

/**
 * Chronostratigraphic information
 */
export interface Chronostratigraphy {
  columnId: string;
  ageModel: string;
  horizons: Array<{
    name: string;
    depth: number;
    ageMa: number;
    period?: string;
    epoch?: string;
    stage?: string;
    confidence: number;
  }>;
  source: string;
  lastUpdated: string;
}

/**
 * Scale metadata for display
 */
export interface ScaleMetadata {
  domain: ScaleDomain;
  physicalResolution: string;
  pixelResolution: string;
  units: string;
  crs?: string;
  accuracy?: string;
  lastCalibrated: string;
}

/**
 * Coordinate system conversion
 */
export interface CoordinateConversion {
  from: string;
  to: string;
  transform: (coord: WorldCoordinate) => WorldCoordinate;
  accuracy: number;
}
