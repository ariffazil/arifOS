import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { GroundedBadge } from '../WitnessBadges/WitnessBadges';
import { useActiveTab } from '../../store/geoxStore';

/**
 * EarthWitness Component
 *
 * The primary 2D geospatial grounding layer for GEOX.
 * Uses MapLibre GL JS for GPU-accelerated Earth visualization.
 *
 * DITEMPA BUKAN DIBERI
 */
export const EarthWitness: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [lng] = useState(114.2); // Default to SE Asia / Brunei area
  const [lat] = useState(4.5);
  const [zoom] = useState(9);

  const activeTab = useActiveTab();

  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          'osm': {
            type: 'raster',
            tiles: [
              'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
            ],
            tileSize: 256,
            attribution: '&copy; OpenStreetMap Contributors'
          }
        },
        layers: [
          {
            id: 'osm-tiles',
            type: 'raster',
            source: 'osm',
            minzoom: 0,
            maxzoom: 19
          }
        ]
      },
      center: [lng, lat],
      zoom: zoom
    });

    map.current.addControl(new maplibregl.NavigationControl(), 'top-right');

    const pilotData = {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "id": "basin_boundary",
          "properties": {"name": "Malay Basin Boundary", "type": "Basin"},
          "geometry": {
            "type": "Polygon",
            "coordinates": [[
              [102.0, 5.0], [105.0, 7.5], [107.0, 5.0], [105.0, 3.0], [102.0, 5.0]
            ]]
          }
        },
        {
          "type": "Feature",
          "id": "p1_zone",
          "properties": {"name": "P1: Basin-centre Anticline", "play": "P1", "fill": "#ff4444"},
          "geometry": {
            "type": "Polygon",
            "coordinates": [[
              [103.5, 5.5], [105.0, 6.0], [105.5, 5.5], [104.5, 4.5], [103.5, 5.5]
            ]]
          }
        }
      ]
    };

    map.current.on('load', () => {
      if (!map.current) return;

      map.current.addSource('malay_basin_pilot', {
        type: 'geojson',
        data: pilotData as any
      });

      map.current.addLayer({
        id: 'malay_basin_fill',
        type: 'fill',
        source: 'malay_basin_pilot',
        paint: {
          'fill-color': ['coalesce', ['get', 'fill'], '#3b82f6'],
          'fill-opacity': 0.2
        }
      });

      map.current.addLayer({
        id: 'malay_basin_outline',
        type: 'line',
        source: 'malay_basin_pilot',
        paint: {
          'line-color': ['coalesce', ['get', 'fill'], '#3b82f6'],
          'line-width': 2
        }
      });

      if (activeTab === 'pilot') {
        map.current.flyTo({
          center: [104.5, 5.5],
          zoom: 6.5,
          duration: 2000
        });
      }
    });

    return () => {
      map.current?.remove();
    };
  }, [lng, lat, zoom, activeTab]);

  return (
    <div className="relative w-full h-full min-h-[400px] border border-slate-800 rounded-lg overflow-hidden">
      {/* Map Container */}
      <div ref={mapContainer} className="absolute inset-0" />

      {/* Floating Governance Layer */}
      <div className="absolute top-4 left-4 z-10 pointer-events-none">
        <GroundedBadge
          confidence={0.92}
          status="GROUNDED"
          source="OpenStreetMap / Protomaps"
        />
      </div>

      {/* Coordinate HUD */}
      <div className="absolute bottom-4 left-4 z-10 bg-slate-900/80 backdrop-blur px-3 py-1.5 rounded border border-slate-700 font-mono text-[10px] text-slate-300">
        LAT: {lat.toFixed(4)} | LON: {lng.toFixed(4)} | WGS84
      </div>

      {/* ToAC Warning Overlay */}
      {activeTab === 'seismic' && (
        <div className="absolute inset-0 bg-red-500/5 pointer-events-none border-2 border-red-500/20 animate-pulse" />
      )}
    </div>
  );
};
