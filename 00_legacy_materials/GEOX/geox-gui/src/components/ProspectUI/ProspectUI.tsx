import React, { useState, useEffect, useCallback } from 'react';
import { Target, MapPin, Layers, Info, CheckCircle, Crosshair, ChevronRight } from 'lucide-react';
import { useMcpTool } from '../../hooks/useMcpTool';
import { useGEOXStore } from '../../store/geoxStore';

/**
 * ProspectUI — Geofabric visualization.
 * Projects well trajectories into the prospect map view.
 */
export const ProspectUI: React.FC = () => {
    const { selectedWell, selectedProspect, updateFloorStatus } = useGEOXStore();
    const [projectedPath, setProjectedPath] = useState<any[]>([]);

    // MCP Tools
    const projectWellTool = useMcpTool<{ well_id: string; target_epsg: number }, any>(
        'geox_project_well_trajectory'
    );

    const handleProjectWell = useCallback(async () => {
        if (!selectedWell) return;

        try {
            updateFloorStatus('F4', 'amber', 'Projecting well trajectory through GeoFabric');
            const result = await projectWellTool.call({
                well_id: selectedWell,
                target_epsg: 4326 // WGS84 for display
            });

            if (result.points) {
                setProjectedPath(result.points);
                updateFloorStatus('F4', 'green', 'Trajectory projected successfully');
            }
        } catch (err) {
            console.error('Projection failed:', err);
            updateFloorStatus('F4', 'red', 'Spatial transformation failure');
        }
    }, [selectedWell, projectWellTool.call, updateFloorStatus]);

    useEffect(() => {
        if (selectedWell) {
            handleProjectWell();
        }
    }, [selectedWell, handleProjectWell]);

    return (
        <div className="h-full flex flex-col bg-slate-950 text-slate-200 geox-root">
            {/* Toolbar */}
            <div className="h-12 border-b border-slate-800 bg-slate-900/50 flex items-center px-4 gap-4">
                <Target className="w-5 h-5 text-red-500" />
                <h2 className="text-sm font-black tracking-widest uppercase italic font-ui">Prospect UI</h2>

                <div className="flex-1" />

                <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-slate-500 uppercase">Selected:</span>
                    <span className="geox-domain-indicator geox-domain-indicator--void">
                        {selectedProspect || 'NO_SCAN'}
                    </span>
                </div>
            </div>

            <div className="flex-1 relative flex">
                {/* Map View Simulated Area */}
                <div className="flex-1 bg-slate-900 relative overflow-hidden flex items-center justify-center geox-scanline">
                    {/* Radar Sweep Animation */}
                    <div className="geox-radar-sweep" />

                    {/* Prospect Boundary (Box) */}
                    <div className="w-64 h-64 border-2 border-red-500/30 bg-red-500/5 rounded-lg flex items-center justify-center relative geox-glass">
                        <span className="absolute -top-6 left-0 text-[10px] font-mono text-red-400 font-bold uppercase">Boundary: Alpha_01</span>

                        {/* Well Target (Center) */}
                        <div className="w-4 h-4 rounded-full border border-yellow-500 flex items-center justify-center geox-pulse--amber">
                            <div className="w-1 h-1 bg-yellow-500 rounded-full" />
                        </div>

                        {/* Projected Trajectory Simulation (Simplified SVG) */}
                        {projectedPath.length > 0 && (
                            <svg className="absolute inset-0 w-full h-full pointer-events-none">
                                <path
                                    d={`M 128,128 L ${projectedPath.map((p, i) => `${128 + i*2},${128 + i*4}`).join(' L ')}`}
                                    fill="none"
                                    stroke="var(--geox-cyan-400)"
                                    strokeWidth="2"
                                    strokeDasharray="4 2"
                                />
                                {projectedPath.map((p, i) => (
                                    <circle key={i} cx={128 + i*2} cy={128 + i*4} r="2" fill="var(--geox-cyan-400)" />
                                ))}
                            </svg>
                        )}
                    </div>

                    {/* Map UI Overlays */}
                    <div className="absolute bottom-4 left-4 flex flex-col gap-2">
                        <button
                            className="p-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded text-slate-400 transition-colors"
                            title="Toggle Layers"
                        >
                            <Layers className="w-4 h-4" />
                        </button>
                        <button
                            className="p-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded text-slate-400 transition-colors"
                            title="Center View"
                        >
                            <Crosshair className="w-4 h-4" />
                        </button>
                    </div>

                    <div className="absolute top-4 right-4">
                        <div className="flex items-center gap-2 p-2 bg-slate-900/80 border border-cyan-500/30 rounded backdrop-blur geox-glass-strong">
                            <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
                            <span className="text-[10px] font-mono text-cyan-400">GEO-FABRIC SYNC ENABLED</span>
                        </div>
                    </div>
                </div>

                {/* Right Sidebar */}
                <div className="w-64 border-l border-slate-800 bg-slate-950 p-4 flex flex-col gap-4 overflow-y-auto geox-scroll">
                    <div className="flex items-center gap-2">
                        <Info className="w-4 h-4 text-blue-400" />
                        <span className="text-xs font-bold uppercase text-slate-300">Spatial Audit</span>
                    </div>

                    <div className="space-y-3">
                        <div className="p-3 bg-slate-900 border border-slate-800 rounded geox-card">
                            <div className="text-[10px] text-slate-500 uppercase mb-1">Datum Integrity</div>
                            <div className="flex items-center justify-between">
                                <span className="text-xs font-mono geox-coord--latlon">UTM 48N</span>
                                <CheckCircle className="w-3 h-3 text-green-500" />
                            </div>
                        </div>

                        <div className="p-3 bg-slate-900 border border-slate-800 rounded geox-card">
                            <div className="text-[10px] text-slate-500 uppercase mb-1">Well Projection</div>
                            <div className="text-xs font-mono text-slate-300 truncate">
                                {selectedWell || 'NONE_SELECTED'}
                            </div>
                            {projectedPath.length > 0 && (
                                <div className="mt-2 text-[10px] text-cyan-400 font-mono">
                                    {projectedPath.length} points projected
                                </div>
                            )}
                        </div>

                        <button
                            onClick={handleProjectWell}
                            disabled={!selectedWell || projectWellTool.status === 'loading'}
                            className="w-full geox-btn geox-btn--primary"
                            title="Reproject trajectory through geofabric"
                        >
                            {projectWellTool.status === 'loading' ? 'Projecting...' : 'Reproject Trajectory'}
                            {!projectWellTool.status && <ChevronRight className="w-3 h-3" />}
                        </button>
                    </div>

                    <div className="mt-auto border-t border-slate-800 pt-4">
                        <div className="flex items-center gap-2 mb-2">
                            <MapPin className="w-4 h-4 text-slate-500" />
                            <span className="text-[10px] font-bold text-slate-500 uppercase">Context Map</span>
                        </div>
                        <div className="aspect-square bg-slate-900 rounded border border-slate-800 flex items-center justify-center geox-glass">
                            <span className="text-[10px] font-mono text-slate-700 uppercase tracking-tighter text-center px-4">
                                Interactive Basemap Layer
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProspectUI;
