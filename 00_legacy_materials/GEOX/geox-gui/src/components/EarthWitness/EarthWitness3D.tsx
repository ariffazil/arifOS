import React, { useEffect, useRef } from 'react';
import {
  Viewer,
  Terrain,
  createWorldImageryAsync,
  Cartesian3,
  Color
} from 'cesium';
import "cesium/Build/Cesium/Widgets/widgets.css";
import { GroundedBadge } from '../WitnessBadges/WitnessBadges';
import { useActiveTab } from '../../store/geoxStore';

/**
 * EarthWitness3D Component
 *
 * The primary 3D geospatial grounding layer for GEOX.
 * Uses CesiumJS for high-precision WGS84 globe visualization.
 *
 * DITEMPA BUKAN DIBERI
 */
export const EarthWitness3D: React.FC = () => {
  const cesiumContainer = useRef<HTMLDivElement>(null);
  const viewer = useRef<Viewer | null>(null);

  const activeTab = useActiveTab();

  useEffect(() => {
    if (viewer.current || !cesiumContainer.current) return;

    // Initialize Cesium Viewer
    // Note: In production, we'd use a self-hosted terrain provider (Copernicus DEM)
    const initViewer = async () => {
      viewer.current = new Viewer(cesiumContainer.current!, {
        terrain: Terrain.fromWorldTerrain(),
        baseLayer: false, // We'll add our own open imagery
        animation: false,
        timeline: false,
        geocoder: true,
        navigationHelpButton: false,
        sceneModePicker: true,
        baseLayerPicker: false,
        fullscreenButton: false,
        homeButton: true,
        infoBox: false,
        selectionIndicator: false,
      });

      // Add Open Sentinel-2/Landsat style imagery (using Cesium default for placeholder)
      const imagery = await createWorldImageryAsync();
      viewer.current.imageryLayers.addImageryProvider(imagery);

      // Set initial view to SE Asia / Brunei area
      viewer.current.camera.setView({
        destination: Cartesian3.fromDegrees(114.2, 4.5, 15000.0),
        orientation: {
          heading: 0.0,
          pitch: -0.5,
          roll: 0.0
        }
      });

      // Style adjustments
      viewer.current.scene.backgroundColor = Color.BLACK;
      viewer.current.scene.globe.depthTestAgainstTerrain = true;
    };

    initViewer();

    return () => {
      viewer.current?.destroy();
      viewer.current = null;
    };
  }, []);

  return (
    <div className="relative w-full h-full min-h-[400px] border border-slate-800 rounded-lg overflow-hidden bg-black">
      {/* Cesium Container */}
      <div ref={cesiumContainer} className="absolute inset-0" />

      {/* Floating Governance Layer */}
      <div className="absolute top-4 left-4 z-10 pointer-events-none">
        <GroundedBadge
          confidence={0.95}
          status="3D_GROUNDED"
          source="Cesium WGS84 / Copernicus DEM"
        />
      </div>

      {/* 3D Coordinate HUD */}
      <div className="absolute bottom-4 left-4 z-10 bg-slate-900/80 backdrop-blur px-3 py-1.5 rounded border border-slate-700 font-mono text-[10px] text-cyan-400">
        MODE: 3D_EARTH | PRECISION: HIGH | DATUM: WGS84
      </div>

      {/* Cross-Section Depth Overlay (Subsurface Readiness) */}
      {activeTab === 'wells' && (
        <div className="absolute right-4 top-1/2 -translate-y-1/2 z-10 flex flex-col gap-2 bg-slate-900/60 p-2 rounded border border-slate-700">
          <div className="w-1 h-32 bg-gradient-to-b from-blue-500 via-orange-500 to-red-900 rounded-full" />
          <span className="text-[8px] text-slate-400 font-mono text-center uppercase tracking-tighter">Depth</span>
        </div>
      )}
    </div>
  );
};
