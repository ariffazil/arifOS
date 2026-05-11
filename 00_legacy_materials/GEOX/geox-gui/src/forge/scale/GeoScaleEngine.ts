/**
 * GeoScale Engine — Earth True Scale Transformation
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * Recursive georeferencing logic for 1D/2D/3D analog-to-digital transformation.
 * Calibrates every pixel to physical units and georeferences to global coordinates.
 *
 * Domain Mapping:
 * - 1D (250-499): Borehole logs, depth in meters/feet, time in Ma
 * - 2D (500-749): Maps, sections, seismic lines with X/Y coordinates
 * - 3D (750-999): Volumes with full XYZ + temporal coordinates
 */

import type {
  ScaleDomain,
  SpatialReference,
  TemporalReference,
  CalibratedPoint,
  CalibrationResult,
  GeoTransform,
  PixelCoordinate,
  WorldCoordinate,
  Chronostratigraphy,
} from './types';

/**
 * Scale transformation matrix for 2D/3D projections
 */
export interface TransformMatrix {
  a: number; // Scale X
  b: number; // Skew X
  c: number; // Skew Y
  d: number; // Scale Y
  e: number; // Translate X
  f: number; // Translate Y
}

/**
 * Ground Control Point for georeferencing
 */
export interface GroundControlPoint {
  id: string;
  pixel: PixelCoordinate;
  world: WorldCoordinate;
  accuracy?: number; // in meters
  source: 'manual' | 'auto-detected' | 'database';
}

/**
 * Earth Scale Configuration
 */
export interface EarthScaleConfig {
  domain: ScaleDomain;
  spatial: SpatialReference;
  temporal?: TemporalReference;
  units: {
    horizontal: 'meters' | 'feet' | 'kilometers' | 'miles';
    vertical: 'meters' | 'feet' | 'twt-ms' | 'twt-s'; // TWT = Two-Way Time
    temporal: 'ma' | 'ka' | 'years';
  };
  precision: {
    horizontal: number;
    vertical: number;
    temporal: number;
  };
}

/**
 * 1D Borehole Calibration
 */
export interface BoreholeCalibration {
  wellId: string;
  kbElevation: number; // Kelly Bushing elevation
  totalDepth: number;
  logRange: {
    minDepth: number;
    maxDepth: number;
    datum: 'KB' | 'DF' | 'MSL' | 'RT'; // Kelly Bushing, Derrick Floor, Mean Sea Level, Rotary Table
  };
  timeDepthModel?: TimeDepthModel;
}

/**
 * Time-Depth Model for converting TWT to depth
 */
export interface TimeDepthModel {
  checkshots: Array<{
    twt: number; // Two-way time in ms
    depth: number; // Depth in meters
    velocity?: number; // Interval velocity in m/s
  }>;
  interpolationMethod: 'linear' | 'spline' | 'ck' | 'fps'; // Claerbout, Faust, etc.
}

/**
 * 2D Map Calibration with GCPs
 */
export interface MapCalibration {
  gcps: GroundControlPoint[];
  transform: TransformMatrix;
  crs: string; // EPSG code or WKT
  rmse?: number; // Root Mean Square Error in meters
  residuals?: Array<{
    gcpId: string;
    residualX: number;
    residualY: number;
  }>;
}

/**
 * 3D Volume Calibration
 */
export interface VolumeCalibration {
  inlineRange: { min: number; max: number; step: number };
  xlineRange: { min: number; max: number; step: number };
  timeRange: { min: number; max: number; step: number };
  cornerPoints: Array<{
    inline: number;
    xline: number;
    x: number;
    y: number;
  }>;
  crs: string;
  verticalDatum: string;
}

/**
 * Chronostratigraphic Calibration via Macrostrat
 */
export interface ChronostratigraphicCalibration {
  stratigraphicColumnId: string;
  ageModel: 'gradstein2020' | 'gts2012' | 'custom';
  horizons: Array<{
    name: string;
    depth: number;
    ageMa?: number;
    period?: string;
    epoch?: string;
    stage?: string;
    confidence: number; // 0-1
  }>;
  macrostratIntegration: {
    enabled: boolean;
    apiEndpoint: string;
    lastSync: string;
  };
}

/**
 * GeoScaleEngine — Main transformation engine
 */
export class GeoScaleEngine {
  private config: EarthScaleConfig;
  private transformCache: Map<string, GeoTransform> = new Map();

  constructor(config: EarthScaleConfig) {
    this.config = config;
  }

  /**
   * Calibrate a 1D borehole log from pixel to depth
   */
  calibrate1D(
    pixelY: number,
    imageHeight: number,
    boreholeConfig: BoreholeCalibration
  ): CalibrationResult {
    const { minDepth, maxDepth } = boreholeConfig.logRange;
    const depthRange = maxDepth - minDepth;

    // Normalize pixel position (0 = top, 1 = bottom)
    const normalizedY = pixelY / imageHeight;

    // Map to depth (inverted because depth increases downward)
    const depth = minDepth + (normalizedY * depthRange);

    // Calculate TWT if time-depth model exists
    let twt: number | undefined;
    if (boreholeConfig.timeDepthModel) {
      twt = this.interpolateTWT(depth, boreholeConfig.timeDepthModel);
    }

    // Query Macrostrat for age if temporal reference exists
    let age: number | undefined;
    if (this.config.temporal) {
      age = this.estimateAge(depth);
    }

    return {
      domain: '1d',
      pixel: { y: pixelY },
      world: { depth, twt, age },
      confidence: this.calculateConfidence1D(depth, boreholeConfig),
      units: {
        depth: this.config.units.vertical,
        twt: 'ms',
        age: 'ma',
      },
    };
  }

  /**
   * Calibrate 2D map coordinates from pixel to world
   */
  calibrate2D(
    pixelX: number,
    pixelY: number,
    mapConfig: MapCalibration
  ): CalibrationResult {
    // Apply affine transform: X = a*x + b*y + c, Y = d*x + e*y + f
    const { a, b, c, d, e, f } = mapConfig.transform;

    const worldX = a * pixelX + b * pixelY + c;
    const worldY = d * pixelX + e * pixelY + f;

    // Calculate accuracy based on RMSE and GCP distribution
    const confidence = this.calculateConfidence2D(
      { x: pixelX, y: pixelY },
      mapConfig
    );

    return {
      domain: '2d',
      pixel: { x: pixelX, y: pixelY },
      world: {
        x: worldX,
        y: worldY,
        crs: mapConfig.crs,
      },
      confidence,
      units: {
        x: this.config.units.horizontal,
        y: this.config.units.horizontal,
      },
      metadata: {
        rmse: mapConfig.rmse,
        numGcps: mapConfig.gcps.length,
      },
    };
  }

  /**
   * Calibrate 3D seismic volume coordinates
   */
  calibrate3D(
    inline: number,
    xline: number,
    time: number,
    volumeConfig: VolumeCalibration
  ): CalibrationResult {
    // Convert inline/xline to world coordinates using corner points
    const worldCoords = this.inlineXlineToWorld(
      inline,
      xline,
      volumeConfig.cornerPoints
    );

    // Convert TWT to depth if velocity model available
    let depth: number | undefined;
    if (this.config.temporal?.velocityModel) {
      depth = this.twtToDepth(time, this.config.temporal.velocityModel);
    }

    return {
      domain: '3d',
      world: {
        x: worldCoords.x,
        y: worldCoords.y,
        z: depth || time,
        inline,
        xline,
        twt: time,
      },
      confidence: 0.95, // High confidence for regular grid
      units: {
        x: this.config.units.horizontal,
        y: this.config.units.horizontal,
        z: this.config.units.vertical,
      },
    };
  }

  /**
   * Interpolate TWT from depth using time-depth model
   */
  private interpolateTWT(depth: number, model: TimeDepthModel): number {
    const { checkshots, interpolationMethod } = model;

    if (checkshots.length === 0) return 0;
    if (checkshots.length === 1) return checkshots[0].twt;

    // Find bracketing checkshots
    let lower = checkshots[0];
    let upper = checkshots[checkshots.length - 1];

    for (let i = 0; i < checkshots.length - 1; i++) {
      if (depth >= checkshots[i].depth && depth <= checkshots[i + 1].depth) {
        lower = checkshots[i];
        upper = checkshots[i + 1];
        break;
      }
    }

    // Linear interpolation
    const ratio = (depth - lower.depth) / (upper.depth - lower.depth);
    return lower.twt + ratio * (upper.twt - lower.twt);
  }

  /**
   * Estimate geological age from depth using Macrostrat integration
   */
  private estimateAge(depth: number): number | undefined {
    // This would integrate with Macrostrat API
    // For now, return a placeholder based on typical sedimentation rates
    const sedimentationRate = 50; // meters per million years (typical)
    return depth / sedimentationRate;
  }

  /**
   * Convert inline/xline to world coordinates using bilinear interpolation
   */
  private inlineXlineToWorld(
    inline: number,
    xline: number,
    cornerPoints: VolumeCalibration['cornerPoints']
  ): { x: number; y: number } {
    // Simplified bilinear interpolation
    // In practice, this would use proper seismic geometry
    const corners = cornerPoints;
    if (corners.length < 4) {
      throw new Error('At least 4 corner points required for 3D calibration');
    }

    // Find bounding box
    const minInline = Math.min(...corners.map((c) => c.inline));
    const maxInline = Math.max(...corners.map((c) => c.inline));
    const minXline = Math.min(...corners.map((c) => c.xline));
    const maxXline = Math.max(...corners.map((c) => c.xline));

    // Normalize
    const u = (inline - minInline) / (maxInline - minInline);
    const v = (xline - minXline) / (maxXline - minXline);

    // Bilinear interpolation (simplified)
    const x = corners[0].x + u * (corners[2].x - corners[0].x);
    const y = corners[0].y + v * (corners[1].y - corners[0].y);

    return { x, y };
  }

  /**
   * Convert TWT to depth using velocity model
   */
  private twtToDepth(twt: number, velocityModel: number[]): number {
    // Simplified: average velocity * one-way time
    const avgVelocity = velocityModel.reduce((a, b) => a + b, 0) / velocityModel.length;
    return (avgVelocity * twt) / 2000; // Divide by 2 for one-way, 1000 for ms to s
  }

  /**
   * Calculate confidence for 1D calibration
   */
  private calculateConfidence1D(
    depth: number,
    config: BoreholeCalibration
  ): number {
    // Confidence decreases near top and bottom of log
    const { minDepth, maxDepth } = config.logRange;
    const range = maxDepth - minDepth;
    const normalizedDepth = (depth - minDepth) / range;

    // Edge penalty
    const edgePenalty = Math.min(normalizedDepth, 1 - normalizedDepth) * 2;
    const baseConfidence = 0.9;

    return Math.max(0.5, baseConfidence - (1 - edgePenalty) * 0.1);
  }

  /**
   * Calculate confidence for 2D calibration based on GCP distribution
   */
  private calculateConfidence2D(
    pixel: PixelCoordinate,
    config: MapCalibration
  ): number {
    // Base confidence from RMSE
    let confidence = config.rmse ? Math.max(0.5, 1 - config.rmse / 100) : 0.8;

    // Distance penalty from nearest GCP
    const minDistance = Math.min(
      ...config.gcps.map((gcp) => {
        const dx = gcp.pixel.x - pixel.x;
        const dy = gcp.pixel.y - pixel.y;
        return Math.sqrt(dx * dx + dy * dy);
      })
    );

    // Reduce confidence if far from GCPs
    const distancePenalty = Math.min(minDistance / 500, 0.3);
    confidence -= distancePenalty;

    return Math.max(0.5, confidence);
  }

  /**
   * Auto-detect GCPs using computer vision (placeholder for CV integration)
   */
  async detectGCPsAuto(
    imageData: ImageData,
    expectedGcps: Array<{ id: string; approximateLocation: PixelCoordinate }>
  ): Promise<GroundControlPoint[]> {
    // This would integrate with OpenCV or TensorFlow.js
    // For now, return mock data
    return expectedGcps.map((gcp) => ({
      id: gcp.id,
      pixel: gcp.approximateLocation,
      world: { x: 0, y: 0 }, // Would be matched against database
      accuracy: 5,
      source: 'auto-detected',
    }));
  }

  /**
   * Hydrate chronostratigraphy from Macrostrat API
   */
  async hydrateChronostratigraphy(
    calibration: ChronostratigraphicCalibration
  ): Promise<Chronostratigraphy> {
    if (!calibration.macrostratIntegration.enabled) {
      throw new Error('Macrostrat integration not enabled');
    }

    // This would make actual API calls to Macrostrat
    // For now, return mock data
    return {
      columnId: calibration.stratigraphicColumnId,
      ageModel: calibration.ageModel,
      horizons: calibration.horizons.map((h) => ({
        ...h,
        ageMa: h.ageMa || this.estimateAge(h.depth) || 0,
      })),
      source: 'macrostrat-api',
      lastUpdated: new Date().toISOString(),
    };
  }

  /**
   * Get scale summary for display
   */
  getScaleSummary(): {
    domain: ScaleDomain;
    resolution: string;
    units: string;
    crs?: string;
  } {
    return {
      domain: this.config.domain,
      resolution: `${this.config.precision.horizontal}m x ${this.config.precision.vertical}m`,
      units: `${this.config.units.horizontal} / ${this.config.units.vertical}`,
      crs: this.config.spatial.crs,
    };
  }
}

/**
 * Factory function to create scale engine from domain
 */
export function createScaleEngine(
  domain: ScaleDomain,
  options: Partial<EarthScaleConfig> = {}
): GeoScaleEngine {
  const defaultConfig: EarthScaleConfig = {
    domain,
    spatial: {
      crs: 'EPSG:4326',
      bounds: { minX: 0, minY: 0, maxX: 0, maxY: 0 },
    },
    units: {
      horizontal: 'meters',
      vertical: 'meters',
      temporal: 'ma',
    },
    precision: {
      horizontal: 1,
      vertical: 0.1,
      temporal: 0.01,
    },
  };

  return new GeoScaleEngine({ ...defaultConfig, ...options });
}
