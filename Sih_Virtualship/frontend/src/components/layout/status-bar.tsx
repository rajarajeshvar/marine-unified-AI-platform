'use client';

import React from 'react';
import { useVessel } from '../../providers/vessel-provider';
import { Cpu, RefreshCw } from 'lucide-react';

export function StatusBar() {
  const { vesselState, isConnected } = useVessel();

  const formatTimestamp = (isoString?: string) => {
    if (!isoString) return 'WAITING FOR SOURCE STREAM...';
    try {
      const date = new Date(isoString);
      return date.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
    } catch {
      return 'TIMESTAMP INVALID';
    }
  };

  return (
    <footer className="h-8 border-t border-slate-800 bg-slate-900/60 backdrop-blur-md flex items-center justify-between px-6 z-10 font-mono text-[10px] text-slate-500 select-none">
      {/* System Status Readouts */}
      <div className="flex items-center gap-5">
        <div className="flex items-center gap-1.5">
          <Cpu className="h-3 w-3 text-slate-600" />
          <span>GW STATE:</span>
          <span className={`font-bold ${isConnected ? 'text-emerald-500' : 'text-rose-500'}`}>
            {isConnected ? 'STREAMING ACTIVE' : 'DISCONNECTED'}
          </span>
        </div>
        <span className="text-slate-800">|</span>
        <div>
          <span>ENV:</span>
          <span className="font-bold text-sky-400 ml-1 uppercase">
            {vesselState ? 'SIMULATED HULL & PROPULSION' : 'OFFLINE'}
          </span>
        </div>
      </div>

      {/* Last Update Time Sync */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          <RefreshCw className={`h-3 w-3 text-slate-600 ${isConnected ? 'animate-spin' : ''}`} />
          <span>LAST UPDATED:</span>
          <span className="text-slate-350 font-bold">
            {formatTimestamp(vesselState?.timestamp)}
          </span>
        </div>
        <span className="text-slate-800">|</span>
        <span>GATEWAY SYS: 1.0.0</span>
      </div>
    </footer>
  );
}
