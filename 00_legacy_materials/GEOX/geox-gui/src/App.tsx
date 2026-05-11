/**
 * GEOX GUI App — DITEMPA BUKAN DIBERI
 *
 * Main application component for GEOX Earth Witness.
 * Landing page first, then cockpit on demand.
 */

import { useState, useEffect } from 'react';
import { MainLayout } from './components/Layout/MainLayout';
import { LandingPage } from './components/LandingPage/LandingPage';
import { useGEOXStore } from './store/geoxStore';
import { useGeoxBridge } from './hooks/useGeoxBridge';
import './App.css';

function App() {
  const [showCockpit, setShowCockpit] = useState(false);
  const { setGEOXConnected, geoxUrl } = useGEOXStore();
  const { sendUiAction } = useGeoxBridge();

  // Check GEOX connection on mount
  useEffect(() => {
    sendUiAction('app.mounted', { timestamp: new Date().toISOString() });

    const checkConnection = async () => {
      try {
        const response = await fetch(`${geoxUrl}/health`, {
          method: 'GET',
          headers: { 'Accept': 'application/json' },
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
    <div className="app">
      {showCockpit ? (
        <MainLayout />
      ) : (
        <LandingPage onEnterCockpit={() => setShowCockpit(true)} />
      )}
    </div>
  );
}

export default App;
