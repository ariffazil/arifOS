/**
 * GEOX GUI App — Design Forge Edition
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * Earth Intelligence Core with 000-999 Dimensional Architecture.
 *
 * Architecture:
 * - DomainVoid (000-249): Risk & Decision
 * - Domain1D (250-499): Borehole Intelligence
 * - Domain2D (500-749): Seismic & Planar
 * - Domain3D (750-999): Volume & Basin
 *
 * Integrates:
 * - Scale-Aware Georeferencing Engine
 * - Gemini LLM Intelligence Bridge
 * - Constitutional Governance (F1-F13)
 * - 888_HOLD / 999_SEAL Verdict System
 */

import { useState, useEffect } from 'react';
import { MainLayoutForge } from './components/Layout/MainLayoutForge';
import { LandingPage } from './components/LandingPage/LandingPage';
import { useGEOXStore } from './store/geoxStore';
import { useGeoxBridge } from './hooks/useGeoxBridge';
import './styles/designSystem.css';

/**
 * Style injection for Design System
 */
const StyleInject = () => (
  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');

    :root {
      --geox-void-900: #0A0C0E;
      --geox-void-800: #111418;
      --geox-void-700: #1A1F24;
      --geox-amber-500: #F59E0B;
      --geox-emerald-500: #10B981;
      --geox-crimson-500: #EF4444;
      --geox-violet-500: #8B5CF6;
      --geox-cyan-500: #06B6D4;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      padding: 0;
      background-color: var(--geox-void-900);
      color: #E2E8F0;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      overflow: hidden;
    }

    /* Scrollbar Styling */
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }

    ::-webkit-scrollbar-track {
      background: #111418;
    }

    ::-webkit-scrollbar-thumb {
      background: #2D353D;
      border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
      background: #37414A;
    }

    /* Selection Styling */
    ::selection {
      background: rgba(245, 158, 11, 0.3);
      color: #FFF;
    }
  `}</style>
);

/**
 * Main App Component
 */
function App() {
  const [showCockpit, setShowCockpit] = useState(false);
  const { setGEOXConnected, geoxUrl } = useGEOXStore();
  const { sendUiAction } = useGeoxBridge();

  // Check GEOX connection on mount
  useEffect(() => {
    sendUiAction('app.mounted', {
      timestamp: new Date().toISOString(),
      version: '2026.04.11-999',
      architecture: '000-999',
    });

    const checkConnection = async () => {
      try {
        const response = await fetch(`${geoxUrl}/health`, {
          method: 'GET',
          headers: { Accept: 'application/json' },
        });

        if (response.ok) {
          setGEOXConnected(true);
          console.log('[GEOX] Connected to:', geoxUrl);
        } else {
          setGEOXConnected(false);
          console.warn('[GEOX] Connection failed');
        }
      } catch (error) {
        setGEOXConnected(false);
        console.warn('[GEOX] Connection error:', error);
      }
    };

    checkConnection();

    // Check connection every 30 seconds
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, [geoxUrl, setGEOXConnected, sendUiAction]);

  return (
    <>
      <StyleInject />
      <div className="app">
        {showCockpit ? (
          <MainLayoutForge />
        ) : (
          <LandingPage onEnterCockpit={() => setShowCockpit(true)} />
        )}
      </div>
    </>
  );
}

export default App;
