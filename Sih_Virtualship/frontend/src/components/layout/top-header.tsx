'use client';

import React, { useEffect, useState } from 'react';
import { useVessel } from '../../providers/vessel-provider';
import { ShieldAlert, Activity, Database, Network, Clock, Bot } from 'lucide-react';

interface TopHeaderProps {
  onToggleCopilot?: () => void;
}

export function TopHeader({ onToggleCopilot }: TopHeaderProps) {
  const { vesselState, isConnected, alerts } = useVessel();
  const [utcTime, setUtcTime] = useState<string>('');

  useEffect(() => {
    setUtcTime(new Date().toUTCString());
    const interval = setInterval(() => {
      setUtcTime(new Date().toUTCString());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const activeAlarms = alerts.filter(a => a.is_active);
  const health = vesselState?.health;

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/60 backdrop-blur-md flex items-center justify-between px-6 z-10 font-mono text-xs select-none">
      {/* Ship Branding */}
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded border border-slate-700 bg-slate-950/40">
          <Activity className="h-4 w-4 text-sky-400 animate-pulse" />
        </div>
        <div>
          <h1 className="text-sm font-bold text-slate-200 uppercase tracking-wider leading-none">
            MV TITAN PRO
          </h1>
          <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block mt-0.5">
            Operations Digital Twin
          </span>
        </div>
      </div>

      {/* Center Row: Clock and Health status */}
      <div className="flex items-center gap-8 hidden lg:flex">
        {/* UTC Clock */}
        <div className="flex items-center gap-2 text-slate-400">
          <Clock className="h-3.5 w-3.5 text-slate-500" />
          <span className="font-semibold tracking-tight">{utcTime}</span>
        </div>

        {/* Aggregate Vessel Health */}
        {health && (
          <div className="flex items-center gap-3 border-l border-slate-800 pl-8">
            <div>
              <span className="text-[9px] text-slate-500 block">VESSEL HEALTH</span>
              <span className={`text-sm font-bold tracking-tight ${
                health.overall_health > 85 ? 'text-emerald-400' : health.overall_health > 65 ? 'text-amber-400' : 'text-rose-500'
              }`}>
                {health.overall_health.toFixed(1)}%
              </span>
            </div>
            <div className={`px-2 py-0.5 border text-[9px] font-bold rounded uppercase ${
              health.health_status === 'NORMAL'
                ? 'border-emerald-950 bg-emerald-950/20 text-emerald-450'
                : health.health_status === 'ATTENTION'
                ? 'border-amber-950 bg-amber-950/20 text-amber-450'
                : 'border-rose-950 bg-rose-950/20 text-rose-500 animate-pulse'
            }`}>
              {health.health_status}
            </div>
          </div>
        )}
      </div>

      {/* Right Row: Live Sockets and Systems Status Lights */}
      <div className="flex items-center gap-6">
        {/* Status Indicators Grid */}
        <div className="flex items-center gap-4 border-r border-slate-800 pr-6 hidden sm:flex">
          {/* WebSocket status */}
          <div className="flex items-center gap-1.5" title="WebSocket Stream Connection">
            <Network className={`h-3.5 w-3.5 ${isConnected ? 'text-emerald-500' : 'text-rose-500'}`} />
            <span className="text-slate-500 font-semibold uppercase text-[9px]">WS</span>
            <span className={`h-1.5 w-1.5 rounded-full ${isConnected ? 'bg-emerald-500 shadow-[0_0_4px_rgba(16,185,129,0.8)]' : 'bg-rose-500 animate-ping'}`} />
          </div>

          {/* Database status */}
          <div className="flex items-center gap-1.5" title="PostgreSQL / SQLite Connection">
            <Database className={`h-3.5 w-3.5 ${isConnected ? 'text-emerald-500' : 'text-slate-600'}`} />
            <span className="text-slate-500 font-semibold uppercase text-[9px]">DB</span>
            <span className={`h-1.5 w-1.5 rounded-full ${isConnected ? 'bg-emerald-500 shadow-[0_0_4px_rgba(16,185,129,0.8)]' : 'bg-slate-700'}`} />
          </div>

          {/* Simulator state status */}
          <div className="flex items-center gap-1.5" title="Physics Simulator Loop status">
            <Activity className={`h-3.5 w-3.5 ${isConnected ? 'text-emerald-500' : 'text-slate-650'}`} />
            <span className="text-slate-500 font-semibold uppercase text-[9px]">SIM</span>
            <span className={`h-1.5 w-1.5 rounded-full ${isConnected ? 'bg-emerald-500 shadow-[0_0_4px_rgba(16,185,129,0.8)]' : 'bg-slate-750'}`} />
          </div>
        </div>

        {/* Active Alarms Badge */}
        <div className="flex items-center gap-2 border border-slate-800 rounded bg-slate-950/20 px-3 py-1.5 select-none" title="Active Critical/Warning Alarms count">
          <ShieldAlert className={`h-4 w-4 ${activeAlarms.length > 0 ? 'text-rose-500 animate-pulse' : 'text-slate-500'}`} />
          <span className="font-semibold text-slate-400">ALARM LOG:</span>
          <span className={`font-bold ${activeAlarms.length > 0 ? 'text-rose-500' : 'text-slate-400'}`}>
            {activeAlarms.length}
          </span>
        </div>

        {/* Copilot Toggle Button */}
        {onToggleCopilot && (
          <button 
            onClick={onToggleCopilot}
            className="flex items-center gap-2 border border-sky-900 hover:border-sky-700 bg-sky-950/30 hover:bg-sky-900/40 rounded px-3 py-1.5 text-sky-400 transition-colors"
          >
            <Bot className="h-4 w-4" />
            <span className="font-semibold hidden sm:inline">AI COPILOT</span>
          </button>
        )}
      </div>
    </header>
  );
}
