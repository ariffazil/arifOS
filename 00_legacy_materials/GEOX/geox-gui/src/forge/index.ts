/**
 * GEOX Design Forge — Module Exports
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * 000-999 Dimensional Architecture
 */

// Scale Engine
export { GeoScaleEngine, createScaleEngine } from './scale/GeoScaleEngine';
export type {
  ScaleDomain,
  PixelCoordinate,
  WorldCoordinate,
  SpatialReference,
  TemporalReference,
  CalibrationResult,
  CalibratedPoint,
  GeoTransform,
  Chronostratigraphy,
  ScaleMetadata,
} from './scale/types';

// Domain Components
export { DomainVoid } from './domain/DomainVoid';
export { Domain1D } from './domain/Domain1D';
export { Domain2D } from './domain/Domain2D';
export { Domain3D } from './domain/Domain3D';

// Intelligence Layer
export { useGeminiIntelligence, useQuickInterpretation } from './intelligence/useGeminiIntelligence';
export type {
  GeminiConfig,
  GeologicalContext,
  GeologicalInterpretation,
  UseGeminiIntelligenceReturn,
} from './intelligence/useGeminiIntelligence';

// Design System
import '../styles/designSystem.css';
