'use client';

import React from 'react';
import { useVessel } from '../../providers/vessel-provider';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Sparkline } from '../charts/sparkline';

export function NavigationPanel() {
  const { vesselState, historicalStates } = useVessel();

  if (!vesselState) {
    return (
      <Card className="h-full min-h-[300px]">
        <CardContent className="flex items-center justify-center h-full text-slate-500 font-mono text-xs">
          Syncing navigation satellite locks...
        </CardContent>
      </Card>
    );
  }

  const { navigation } = vesselState;

  // Extract speed over ground historical trends
  const sogTrend = historicalStates.map(h => h.navigation?.sog || 0);

  const formatCoordinate = (val: number, isLat: boolean) => {
    const direction = isLat ? (val >= 0 ? 'N' : 'S') : (val >= 0 ? 'E' : 'W');
    const absolute = Math.abs(val);
    const degrees = Math.floor(absolute);
    const minutesMinutes = (absolute - degrees) * 60;
    const minutes = Math.floor(minutesMinutes);
    const seconds = ((minutesMinutes - minutes) * 60).toFixed(1);
    return `${degrees}°${minutes}'${seconds}" ${direction}`;
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle>Inertial Navigation & Positioning</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left Side: Gyro Compass Dial */}
        <div className="flex flex-col items-center justify-center p-3 border border-slate-800/40 rounded-lg bg-slate-950/20">
          <div className="relative w-32 h-32">
            <svg className="w-full h-full" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="45" fill="none" stroke="#1e293b" strokeWidth="1" />
              <circle cx="50" cy="50" r="42" fill="none" stroke="#0f172a" strokeWidth="1.5" />
              
              <text x="50" y="13" textAnchor="middle" fontSize="6" fontWeight="bold" fill="#f8fafc">N</text>
              <text x="87" y="52" textAnchor="middle" fontSize="6" fontWeight="bold" fill="#64748b">E</text>
              <text x="50" y="91" textAnchor="middle" fontSize="6" fontWeight="bold" fill="#64748b">S</text>
              <text x="13" y="52" textAnchor="middle" fontSize="6" fontWeight="bold" fill="#64748b">W</text>
              
              <line x1="50" y1="8" x2="50" y2="10" stroke="#f43f5e" strokeWidth="1" />
              
              <g transform={`rotate(${navigation.heading}, 50, 50)`}>
                <polygon points="50,15 52,50 48,50" fill="#f43f5e" />
                <polygon points="50,85 52,50 48,50" fill="#475569" />
                <circle cx="50" cy="50" r="2.5" fill="#f8fafc" />
              </g>
            </svg>
          </div>
          <div className="text-center font-mono mt-1">
            <span className="text-[9px] text-slate-550 block">GYRO COG</span>
            <span className="text-sm font-bold text-slate-200">{navigation.heading.toFixed(1)}°</span>
          </div>
        </div>

        {/* Right Side: Coordinates, SOG, Pitch/Roll */}
        <div className="flex flex-col justify-center gap-2.5 font-mono text-xs">
          {/* Coordinates log */}
          <div className="p-2.5 border border-slate-800/60 rounded bg-slate-950/20">
            <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-bold">GNSS Log</span>
            <span className="text-slate-200 text-xs mt-0.5 block tracking-tight">
              LAT: {formatCoordinate(navigation.latitude, true)}
            </span>
            <span className="text-slate-200 text-xs mt-0.5 block tracking-tight">
              LON: {formatCoordinate(navigation.longitude, false)}
            </span>
          </div>

          {/* SOG Speed with Sparkline */}
          <div className="p-2 border border-slate-800/60 rounded bg-slate-950/20 flex justify-between items-center">
            <div>
              <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-bold">Speed (SOG)</span>
              <span className="text-base font-bold text-sky-400">{navigation.sog.toFixed(1)} kn</span>
            </div>
            <Sparkline data={sogTrend} width={80} color="stroke-sky-400" />
          </div>

          {/* Attitude Roll / Pitch */}
          <div className="p-2 border border-slate-800/60 rounded bg-slate-950/20">
            <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-bold mb-1">Attitude Pitch/Roll</span>
            <div className="grid grid-cols-2 gap-2 text-center text-[10px]">
              <div>
                <span className="text-slate-550 block text-[8px] uppercase">Roll</span>
                <span className={`font-bold ${Math.abs(navigation.roll) > 5 ? 'text-amber-500' : 'text-emerald-500'}`}>
                  {navigation.roll.toFixed(1)}° {navigation.roll > 0 ? 'STBD' : 'PORT'}
                </span>
              </div>
              <div>
                <span className="text-slate-550 block text-[8px] uppercase">Pitch</span>
                <span className={`font-bold ${Math.abs(navigation.pitch) > 3 ? 'text-amber-500' : 'text-emerald-500'}`}>
                  {navigation.pitch.toFixed(1)}° {navigation.pitch > 0 ? 'BOW UP' : 'BOW DN'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
