'use client';

import React, { useState } from 'react';
import { useVessel } from '../../providers/vessel-provider';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Wrench, ShieldAlert, CheckCircle2, AlertTriangle, Play, Sparkles } from 'lucide-react';
import { LinearBar } from '../gauges/linear-bar';

export function MaintenancePanel() {
  const { vesselState, changeScenario } = useVessel();
  const [isRunningDiag, setIsRunningDiag] = useState(false);
  const [diagMessage, setDiagMessage] = useState<string | null>(null);

  if (!vesselState) return null;

  const { health } = vesselState;

  // Static maintenance logs
  const scheduleItems = [
    { name: 'Propulsion Lubrication Cycle', interval: '500 hrs', remaining: 120, status: 'NORMAL' },
    { name: 'Auxiliary Generator Filter check', interval: '250 hrs', remaining: 12, status: 'WARNING' },
    { name: 'Hull Plating Anodes Inspection', interval: '1000 hrs', remaining: 840, status: 'NORMAL' },
    { name: 'Fuel Purifier Service Check', interval: '500 hrs', remaining: 4, status: 'CRITICAL' },
  ];

  const handleDiagnostics = () => {
    setIsRunningDiag(true);
    setDiagMessage("Analyzing system logs...");
    setTimeout(() => {
      setDiagMessage("Calibrating Ornstein-Uhlenbeck solver...");
      setTimeout(() => {
        setDiagMessage("All engine parameters normal. Health index synced.");
        setIsRunningDiag(false);
      }, 1500);
    }, 1500);
  };

  const getStatusIcon = (status: string) => {
    if (status === 'CRITICAL') return <ShieldAlert className="h-4 w-4 text-rose-500 animate-pulse" />;
    if (status === 'WARNING') return <AlertTriangle className="h-4 w-4 text-amber-500 animate-bounce" />;
    return <CheckCircle2 className="h-4 w-4 text-emerald-500" />;
  };

  const getStatusColor = (status: string) => {
    if (status === 'CRITICAL') return 'text-rose-400';
    if (status === 'WARNING') return 'text-amber-400';
    return 'text-emerald-400';
  };

  return (
    <Card className="flex flex-col h-full bg-slate-900/10 border-slate-800">
      <CardHeader className="flex flex-row items-center justify-between border-b border-slate-800/40 py-3">
        <div className="flex items-center gap-2">
          <Wrench className="h-4 w-4 text-sky-400" />
          <CardTitle>Vessel Maintenance Registry</CardTitle>
        </div>
        <span className="text-[10px] text-slate-500 font-mono">DWT: 120,000 MT</span>
      </CardHeader>

      <CardContent className="flex-grow p-4 xl:p-6 space-y-6">
        {/* Core Maintenance Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-3 border border-slate-800 bg-slate-950/40 rounded-lg text-center">
            <span className="text-[10px] text-slate-500 font-mono block uppercase">Next Drydock Count</span>
            <span className="text-2xl font-bold font-mono text-sky-400">{health.next_maintenance_days}</span>
            <span className="text-[9px] text-slate-400 block mt-0.5">DAYS REMAINING</span>
          </div>

          <div className="p-3 border border-slate-800 bg-slate-950/40 rounded-lg text-center">
            <span className="text-[10px] text-slate-500 font-mono block uppercase">System Health score</span>
            <span className="text-2xl font-bold font-mono text-emerald-400">{health.overall_health.toFixed(1)}%</span>
            <span className="text-[9px] text-slate-400 block mt-0.5">COMPOSITE INDEX</span>
          </div>

          <div className="p-3 border border-slate-800 bg-slate-950/40 rounded-lg text-center">
            <span className="text-[10px] text-slate-500 font-mono block uppercase">Anomaly Risk score</span>
            <span className="text-2xl font-bold font-mono text-amber-500">{(health.anomaly_probability * 100).toFixed(1)}%</span>
            <span className="text-[9px] text-slate-400 block mt-0.5">PREDICTIVE COEFFICIENT</span>
          </div>
        </div>

        {/* Maintenance Intervals progress */}
        <div className="space-y-4">
          <h4 className="text-[10px] text-slate-400 font-mono uppercase tracking-wider">Scheduled Service Intervals</h4>
          <div className="space-y-3.5">
            {scheduleItems.map((item) => (
              <div key={item.name} className="p-3 border border-slate-800/40 bg-slate-950/20 rounded-lg flex flex-col gap-2">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-350">{item.name}</span>
                  <span className={`flex items-center gap-1.5 ${getStatusColor(item.status)}`}>
                    {getStatusIcon(item.status)}
                    {item.remaining} / {item.interval}
                  </span>
                </div>
                <LinearBar
                  value={Math.max(0, 100 - (item.remaining / parseInt(item.interval) * 100))}
                  min={0}
                  max={100}
                  label="Wear Index"
                  unit="%"
                  warningLimit={75}
                  criticalLimit={90}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Interactive Maintenance Actions */}
        <div className="p-4 border border-slate-800 bg-slate-950/30 rounded-lg flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <h4 className="text-xs font-mono font-semibold text-slate-300">Run Diagnostic Routine</h4>
            <p className="text-[10px] text-slate-500 font-mono mt-0.5">Scans all sensors, clears anomaly registries, and updates state history.</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => changeScenario('MAINTENANCE_MODE')}
              className="flex items-center gap-2 bg-sky-650 hover:bg-sky-600 active:bg-sky-700 text-slate-950 text-[10px] font-bold font-mono px-4 py-2 rounded-lg transition-colors cursor-pointer select-none"
            >
              <Sparkles className="h-3 w-3" />
              INJECT DRY-DOCK SCENARIO
            </button>
            <button
              disabled={isRunningDiag}
              onClick={handleDiagnostics}
              className="flex items-center gap-2 border border-slate-700 hover:border-slate-500 bg-slate-900/60 hover:bg-slate-900 text-slate-300 text-[10px] font-bold font-mono px-4 py-2 rounded-lg transition-colors cursor-pointer select-none disabled:opacity-50"
            >
              <Play className={`h-3 w-3 ${isRunningDiag ? 'animate-spin' : ''}`} />
              {isRunningDiag ? 'SCANNING...' : 'DIAGNOSTICS'}
            </button>
          </div>
        </div>

        {diagMessage && (
          <div className="p-3 border border-sky-950 bg-sky-950/15 rounded-lg text-center text-xs font-mono text-sky-400">
            {diagMessage}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
