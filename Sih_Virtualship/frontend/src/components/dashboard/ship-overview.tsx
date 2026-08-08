'use client';

import React from 'react';
import { useVessel } from '../../providers/vessel-provider';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';

export function ShipOverview() {
  const { vesselState } = useVessel();

  if (!vesselState) return null;

  const { alerts } = vesselState;
  
  // Find the highest priority active alert to display below the ship
  const criticalAlerts = alerts.filter(a => a.level === 'CRITICAL' && a.is_active);
  const warningAlerts = alerts.filter(a => a.level === 'WARNING' && a.is_active);
  const topAlert = criticalAlerts.length > 0 ? criticalAlerts[0] : (warningAlerts.length > 0 ? warningAlerts[0] : null);

  // Helper to determine node alarm level based on system keyword matching
  const getSystemStatus = (systemName: string) => {
    const systemAlerts = alerts.filter((a) => a.system.toLowerCase() === systemName.toLowerCase());
    if (systemAlerts.some((a) => a.level === 'CRITICAL')) return 'CRITICAL';
    if (systemAlerts.some((a) => a.level === 'WARNING')) return 'WARNING';
    return 'NORMAL';
  };

  const engineStatus = getSystemStatus('engine');
  const fuelStatus = getSystemStatus('fuel');
  const hullStatus = getSystemStatus('hull');
  const navStatus = getSystemStatus('navigation');

  const statusColorClass = (status: string) => {
    if (status === 'CRITICAL') return 'bg-rose-600 border-rose-350 shadow-rose-500/80 animate-ping';
    if (status === 'WARNING') return 'bg-amber-500 border-amber-350 shadow-amber-400/85 animate-pulse';
    return 'bg-emerald-500 border-emerald-350 shadow-emerald-500/40';
  };

  const statusColorClassStatic = (status: string) => {
    if (status === 'CRITICAL') return 'bg-rose-600 border-rose-400 shadow-[0_0_8px_rgba(244,63,94,0.6)]';
    if (status === 'WARNING') return 'bg-amber-500 border-amber-350 shadow-[0_0_8px_rgba(245,158,11,0.6)]';
    return 'bg-emerald-500 border-emerald-400 shadow-[0_0_6px_rgba(16,185,129,0.4)]';
  };

  return (
    <Card className="flex flex-col h-full">
      <CardHeader className="flex flex-row items-center justify-between border-b border-slate-800/40 py-3">
        <div>
          <CardTitle>Vessel Spatial Overview</CardTitle>
          <span className="text-[10px] text-slate-500 font-mono mt-0.5 block">ID: MV_TITAN_PRO (DWT 120,000 MT)</span>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono select-none">
          <span className="flex h-2 w-2 rounded-full bg-emerald-500"></span>
          <span className="text-slate-400 uppercase">{vesselState.state}</span>
        </div>
      </CardHeader>

      <CardContent className="flex-grow flex flex-col justify-between py-4">
        {/* SVG Container Ship Profile */}
        <div className="flex-grow flex items-center justify-center min-h-[180px] border border-slate-800/40 rounded-lg bg-slate-950/20 p-4 overflow-hidden">
          <div className="relative w-full max-w-[700px] aspect-[500/120] scale-110">
            <svg className="absolute inset-0 w-full h-full text-slate-700" viewBox="0 0 500 120" fill="none" preserveAspectRatio="none">
              {/* Water level indicator */}
              <line x1="20" y1="95" x2="480" y2="95" stroke="#334155" strokeWidth="2" strokeDasharray="4 4" />
              
              {/* Hull outline */}
              <path
                d="M 50 50 L 350 50 L 355 40 L 390 40 L 392 65 L 430 65 L 450 90 L 50 90 Z"
                fill="#0f172a"
                stroke="#475569"
                strokeWidth="2"
              />
              {/* Cargo holds */}
              <rect x="70" y="55" width="50" height="25" fill="#1e293b" stroke="#334155" />
              <rect x="130" y="55" width="50" height="25" fill="#1e293b" stroke="#334155" />
              <rect x="190" y="55" width="50" height="25" fill="#1e293b" stroke="#334155" />
              <rect x="250" y="55" width="50" height="25" fill="#1e293b" stroke="#334155" />

              {/* Bridge / Superstructure */}
              <path d="M 355 40 L 358 10 L 382 10 L 385 40 Z" fill="#1e293b" stroke="#475569" strokeWidth="1.5" />
              {/* Radar mast */}
              <line x1="370" y1="10" x2="370" y2="2" stroke="#475569" strokeWidth="1.5" />
              <line x1="365" y1="4" x2="375" y2="4" stroke="#475569" strokeWidth="1.5" />

              {/* Propeller & rudder sketch */}
              <path d="M 45 90 L 35 95 L 40 90 Z" stroke="#475569" strokeWidth="1.5" />
              <line x1="35" y1="90" x2="30" y2="95" stroke="#475569" strokeWidth="2" />
            </svg>

            {/* Spatial Overlay Nodes */}
            {/* 1. Propulsion Engine Room Node (aft, lower section) */}
            <div className="absolute left-[80%] top-[70%] -translate-x-1/2 -translate-y-1/2 group cursor-pointer z-10">
              <div className="relative">
                <span className={`absolute inline-flex h-4 w-4 rounded-full opacity-75 ${statusColorClass(engineStatus)}`}></span>
                <span className={`relative inline-flex rounded-full h-3.5 w-3.5 border ${statusColorClassStatic(engineStatus)}`}></span>
              </div>
              <div className="absolute hidden group-hover:block bottom-6 left-1/2 -translate-x-1/2 bg-slate-950 border border-slate-800 text-[10px] font-mono p-2 rounded shadow-xl whitespace-nowrap z-30">
                <p className="font-semibold uppercase text-slate-350">Engine Room</p>
                <p className="text-slate-500">Status: {engineStatus}</p>
              </div>
            </div>

            {/* 2. Fuel Node (amidships-aft) */}
            <div className="absolute left-[65%] top-[72%] -translate-x-1/2 -translate-y-1/2 group cursor-pointer z-10">
              <div className="relative">
                <span className={`absolute inline-flex h-4 w-4 rounded-full opacity-75 ${statusColorClass(fuelStatus)}`}></span>
                <span className={`relative inline-flex rounded-full h-3.5 w-3.5 border ${statusColorClassStatic(fuelStatus)}`}></span>
              </div>
              <div className="absolute hidden group-hover:block bottom-6 left-1/2 -translate-x-1/2 bg-slate-950 border border-slate-800 text-[10px] font-mono p-2 rounded shadow-xl whitespace-nowrap z-30">
                <p className="font-semibold uppercase text-slate-350">Fuel Tanks</p>
                <p className="text-slate-500">Status: {fuelStatus}</p>
              </div>
            </div>

            {/* 3. Hull Integrity Center Node (forward deckholds) */}
            <div className="absolute left-[38%] top-[75%] -translate-x-1/2 -translate-y-1/2 group cursor-pointer z-10">
              <div className="relative">
                <span className={`absolute inline-flex h-4 w-4 rounded-full opacity-75 ${statusColorClass(hullStatus)}`}></span>
                <span className={`relative inline-flex rounded-full h-3.5 w-3.5 border ${statusColorClassStatic(hullStatus)}`}></span>
              </div>
              <div className="absolute hidden group-hover:block bottom-6 left-1/2 -translate-x-1/2 bg-slate-950 border border-slate-800 text-[10px] font-mono p-2 rounded shadow-xl whitespace-nowrap z-30">
                <p className="font-semibold uppercase text-slate-350">Structural Hull</p>
                <p className="text-slate-500">Status: {hullStatus}</p>
              </div>
            </div>

            {/* 4. Bridge Navigation Node (superstructure deckhouse top) */}
            <div className="absolute left-[74%] top-[25%] -translate-x-1/2 -translate-y-1/2 group cursor-pointer z-10">
              <div className="relative">
                <span className={`absolute inline-flex h-4 w-4 rounded-full opacity-75 ${statusColorClass(navStatus)}`}></span>
                <span className={`relative inline-flex rounded-full h-3.5 w-3.5 border ${statusColorClassStatic(navStatus)}`}></span>
              </div>
              <div className="absolute hidden group-hover:block bottom-6 left-1/2 -translate-x-1/2 bg-slate-950 border border-slate-800 text-[10px] font-mono p-2 rounded shadow-xl whitespace-nowrap z-30">
                <p className="font-semibold uppercase text-slate-350">Navigation Bridge</p>
                <p className="text-slate-500">Status: {navStatus}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Nodes Status Legend Grid */}
        <div className="grid grid-cols-4 gap-2 mt-4 pt-3 border-t border-slate-800/40 text-center text-[10px] font-mono select-none">
          <div className="p-2 border border-slate-800/40 rounded bg-slate-950/20">
            <span className="text-slate-500 uppercase block mb-1">Propulsion</span>
            <span className={`font-semibold ${engineStatus === 'CRITICAL' ? 'text-rose-500' : engineStatus === 'WARNING' ? 'text-amber-500' : 'text-emerald-500'}`}>{engineStatus}</span>
          </div>
          <div className="p-2 border border-slate-800/40 rounded bg-slate-950/20">
            <span className="text-slate-500 uppercase block mb-1">Fuel Tank</span>
            <span className={`font-semibold ${fuelStatus === 'CRITICAL' ? 'text-rose-500' : fuelStatus === 'WARNING' ? 'text-amber-500' : 'text-emerald-500'}`}>{fuelStatus}</span>
          </div>
          <div className="p-2 border border-slate-800/40 rounded bg-slate-950/20">
            <span className="text-slate-500 uppercase block mb-1">Hull Plating</span>
            <span className={`font-semibold ${hullStatus === 'CRITICAL' ? 'text-rose-500' : hullStatus === 'WARNING' ? 'text-amber-500' : 'text-emerald-500'}`}>{hullStatus}</span>
          </div>
          <div className="p-2 border border-slate-800/40 rounded bg-slate-950/20">
            <span className="text-slate-500 uppercase block mb-1">Bridge GPS</span>
            <span className={`font-semibold ${navStatus === 'CRITICAL' ? 'text-rose-500' : navStatus === 'WARNING' ? 'text-amber-500' : 'text-emerald-500'}`}>{navStatus}</span>
          </div>
        </div>

        {/* Route Optimization / System Alert Banner (Shows Below Ship) */}
        {topAlert && (
          <div className={`mt-4 p-3 rounded border flex items-center gap-3 animate-pulse ${
            topAlert.level === 'CRITICAL' 
              ? 'bg-rose-950/30 border-rose-500/50 text-rose-200' 
              : 'bg-amber-950/30 border-amber-500/50 text-amber-200'
          }`}>
            <div className={`flex items-center justify-center h-8 w-8 rounded-full ${
              topAlert.level === 'CRITICAL' ? 'bg-rose-600/20 text-rose-500' : 'bg-amber-600/20 text-amber-500'
            }`}>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
            <div className="flex-1">
              <h4 className={`text-xs font-bold uppercase tracking-wider mb-0.5 ${
                topAlert.level === 'CRITICAL' ? 'text-rose-400' : 'text-amber-400'
              }`}>
                {topAlert.system} Alert
              </h4>
              <p className="text-sm">{topAlert.message}</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
