'use client';

import React from 'react';
import { useVessel } from '../../providers/vessel-provider';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { DialGauge } from '../gauges/dial-gauge';

export function WeatherPanel() {
  const { vesselState } = useVessel();

  if (!vesselState) {
    return (
      <Card className="h-full min-h-[140px]">
        <CardContent className="flex items-center justify-center h-full text-slate-500 font-mono text-xs">
          Loading meteorological deck reports...
        </CardContent>
      </Card>
    );
  }

  const { weather } = vesselState;

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle>Meteorological & Sea State</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-4">
        {/* Wind Speed Dial */}
        <DialGauge
          value={weather.wind_speed}
          min={0}
          max={60}
          label="Wind Velocity"
          unit="kn"
          warningLimit={25}
          criticalLimit={35}
          precision={1}
        />

        {/* Wave Height Dial */}
        <DialGauge
          value={weather.wave_height}
          min={0}
          max={12}
          label="Wave Height"
          unit="m"
          warningLimit={4.0}
          criticalLimit={7.0}
          precision={1}
        />
      </CardContent>
    </Card>
  );
}
