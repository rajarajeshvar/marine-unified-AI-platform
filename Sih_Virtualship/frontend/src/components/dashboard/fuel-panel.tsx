'use client';

import React from 'react';
import { useVessel } from '../../providers/vessel-provider';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { DialGauge } from '../gauges/dial-gauge';
import { LinearBar } from '../gauges/linear-bar';
import { Sparkline } from '../charts/sparkline';

export function FuelPanel() {
  const { vesselState, historicalStates, mlSensors } = useVessel();

  if (!vesselState) {
    return (
      <Card className="h-full min-h-[300px]">
        <CardContent className="flex items-center justify-center h-full text-slate-500 font-mono text-xs">
          Loading fuel flow sensor data...
        </CardContent>
      </Card>
    );
  }

  const { fuel } = vesselState;
  
  // Use ML Dataset overrides if connected to Copilot Watchdog (Port 8005)
  const displayConsumption = mlSensors?.sensor_data?.fuel_consumption ?? fuel.consumption_rate;
  const displayFeedPress = mlSensors?.sensor_data?.fuel_pressure ?? fuel.feed_pressure;

  // Extract history series
  const tankTrend = historicalStates.map(h => h.fuel?.tank_level || 0);
  const consumptionTrend = historicalStates.map(h => h.fuel?.consumption_rate || 0);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle>Fuel & Injection Systems</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left Dial: Tank Level */}
        <div className="flex flex-col items-center justify-center gap-2 bg-slate-950/10 p-2 rounded-lg">
          <DialGauge
            value={fuel.tank_level}
            min={0}
            max={100}
            label="Storage Tank Level"
            unit="%"
            warningLimit={25}
            criticalLimit={15}
            comparison="below"
            precision={1}
          />
          <Sparkline data={tankTrend} color={fuel.tank_level < 25 ? 'stroke-rose-500' : 'stroke-sky-500'} />
        </div>

        {/* Right Info Grid */}
        <div className="flex flex-col justify-center gap-3">
          {/* Consumption tracking with sparkline */}
          <div className="p-3 border border-slate-800/60 rounded-lg bg-slate-950/20 flex justify-between items-center font-mono text-xs">
            <div>
              <span className="text-slate-500 uppercase block text-[10px] font-bold">Mass Fuel Flow</span>
              <span className="text-slate-200 text-sm font-bold mt-1 block">
                {Number(displayConsumption).toFixed(1)} kg/h
              </span>
            </div>
            <Sparkline data={consumptionTrend} width={80} color="stroke-sky-400" />
          </div>

          <LinearBar
            value={displayFeedPress}
            min={0}
            max={10.0}
            label="Injection Feed Press"
            unit="bar"
            warningLimit={2.5}
            criticalLimit={1.8}
            comparison="below"
            precision={2}
          />

          <LinearBar
            value={fuel.fuel_temp}
            min={10.0}
            max={60.0}
            label="Fuel Pre-heat Temp"
            unit="°C"
            warningLimit={45.0}
            criticalLimit={55.0}
            precision={1}
          />
        </div>
      </CardContent>
    </Card>
  );
}
