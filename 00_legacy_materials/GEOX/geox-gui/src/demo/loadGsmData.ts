/**
 * GSM Data Loader Demo — DITEMPA BUKAN DIBERI
 *
 * Logic to fetch and inject GSM Malay Basin figures into the
 * Seismic Viewer and Basin Map Explorer.
 */

// Placeholder for the GeoX event bus/bridge
// In a real implementation, this would use the configured bridge
export interface GsmSeismicData {
  imageUrl: string;
  georeferenced: [number, number, number, number];
  picks?: any[];
  provenance: string;
  constitutional: {
    provenance: string;
    floorsChecked: string[];
  };
}

/**
 * Simulates loading a GSM seismic section via MCP tool
 */
export async function loadGsmSeismicLine(
  figureRef: string,
  lineId: string = 'GSM-LINE-PILOT'
): Promise<GsmSeismicData> {
  console.log(`[*] Requesting GSM Figure: ${figureRef} for ${lineId}`);

  // In the real app, we would call useGEOXStore.getState().geoxUrl
  // and use a JSON-RPC request to the MCP server.

  // Simulation of successful tool call result
  return {
    imageUrl: `/data/gsm_702001_demo/figures/${figureRef}.png`,
    georeferenced: [103.5, 4.0, 105.5, 7.0],
    picks: [
      { type: 'fault', name: 'F1', lat: 5.5, lon: 104.5, depth: 1500 },
      { type: 'horizon', name: 'Top Group I', lat: 5.5, lon: 104.5, time: 1200 }
    ],
    provenance: 'GSM-702001 (2021) Structural Analysis',
    constitutional: {
      provenance: 'GSM Validated Archive',
      floorsChecked: ['F2', 'F4', 'F9', 'F11']
    }
  };
}

/**
 * Mock action to send data to the Seismic Viewer
 */
export function injectToSeismicViewer(data: GsmSeismicData) {
  console.log('[!] Injecting to Seismic Viewer...', data);

  // Example implementation using window.postMessage
  // or the internal GEOX Store
  window.dispatchEvent(new CustomEvent('geox:seismic:load', { detail: data }));
}
