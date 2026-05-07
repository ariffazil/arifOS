import React, { useRef } from 'react';
import { useGeoxHostBridge } from '../../hooks/useGeoxHostBridge';

interface AppIframeHostProps {
  src: string;
  title: string;
  appId: string;
}

/**
 * AppIframeHost Component
 *
 * Host component that renders an external GEOX App in a sandboxed iframe
 * and establishes the bidirectional event bridge.
 */
export const AppIframeHost: React.FC<AppIframeHostProps> = ({ src, title, appId: _appId }) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const { sendToApp } = useGeoxHostBridge(iframeRef);

  return (
    <div className="relative w-full h-full flex flex-col border border-slate-800 rounded-lg overflow-hidden bg-slate-900">
      {/* Optional Iframe Header */}
      <div className="h-8 bg-slate-800 flex items-center px-4 justify-between border-b border-white/5">
        <span className="text-[10px] font-bold text-slate-400 tracking-widest uppercase flex items-center gap-2">
          <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
          {title}
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => sendToApp('app.context.patch', { force_sync: true })}
            className="text-[9px] text-slate-500 hover:text-white transition-colors"
          >
            SYNC
          </button>
        </div>
      </div>

      {/* App Iframe */}
      <iframe
        ref={iframeRef}
        src={src}
        title={title}
        className="flex-1 w-full border-none"
        sandbox="allow-scripts allow-forms allow-same-origin"
      />
    </div>
  );
};
