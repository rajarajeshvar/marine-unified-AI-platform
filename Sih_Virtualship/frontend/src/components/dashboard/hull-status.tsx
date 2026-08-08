'use client';

import React from 'react';
import { useVessel } from '../../providers/vessel-provider';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { DialGauge } from '../gauges/dial-gauge';
import { Sparkline } from '../charts/sparkline';

export function HullStatus() {
  const { vesselState, historicalStates } = useVessel();

  if (!vesselState) {
    return (
      <Card className="h-full min-h-[300px]">
        <CardContent className="flex items-center justify-center h-full text-slate-500 font-mono text-xs">
          Loading hull strain logs...
        </CardContent>
      </Card>
    );
  }

  const { hull } = vesselState;

  // Extract history series
  const strainTrend = historicalStates.map(h => h.hull?.strain || 0);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle>Hull Structural Condition</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left Side: Structural Strain with Sparkline */}
        <div className="flex flex-col items-center justify-center gap-2 bg-slate-950/10 p-2 rounded-lg">
          <DialGauge
            value={hull.strain}
            min={0}
            max={350}
            label="Structural strain"
            unit="µE"
            warningLimit={180}
            criticalLimit={240}
            precision={1}
          />
          <Sparkline data={strainTrend} color={hull.strain > 180 ? 'stroke-amber-500' : 'stroke-emerald-500'} />
        </div>

        {/* Right Side: Integrity and Corrosion */}
        <div className="flex flex-col justify-center gap-3">
          {/* Integrity Readout */}
          <div className="p-3 border border-slate-800/60 rounded-lg bg-slate-950/20 font-mono text-xs">
            <span className="text-slate-500 uppercase block text-[10px] font-bold">Plating Integrity</span>
            <div className="flex justify-between items-end mt-1">
              <span className="text-base font-bold text-emerald-400">
                {hull.hull_integrity.toFixed(2)}%
              </span>
              <span className="text-[10px] text-slate-500">Design Limit: 85.0%</span>
            </div>
          </div>

          {/* Galvanic Corrosion */}
          <div className="p-3 border border-slate-800/60 rounded-lg bg-slate-950/20 font-mono text-xs">
            <span className="text-slate-500 uppercase block text-[10px] font-bold">Galvanic Corrosion Index</span>
            <div className="flex justify-between items-end mt-1">
              <span className="text-base font-bold text-sky-400">
                {hull.corrosion_pct.toFixed(2)}%
              </span>
              <span className="text-[10px] text-slate-500">Anodic Protection: OK</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
