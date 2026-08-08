'use client';

import React from 'react';
import { useVessel } from '../../providers/vessel-provider';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { DialGauge } from '../gauges/dial-gauge';
import { LinearBar } from '../gauges/linear-bar';
import { Sparkline } from '../charts/sparkline';

export function EngineStatus() {
  const { vesselState, historicalStates, mlSensors } = useVessel();

  if (!vesselState) {
    return (
      <Card className="h-full min-h-[300px]">
        <CardContent className="flex items-center justify-center h-full text-slate-500 font-mono text-xs">
          Awaiting engine telemetry stream...
        </CardContent>
      </Card>
    );
  }

  const { engine } = vesselState;
  
  // Use ML Dataset overrides if connected to Copilot Watchdog (Port 8005)
  const displayRpm = mlSensors?.sensor_data?.rpm ?? engine.rpm;
  const displayTemp = mlSensors?.sensor_data?.coolant_temperature ?? engine.coolant_temp;
  const displayPress = mlSensors?.sensor_data?.oil_pressure ?? engine.oil_pressure;
  const displayVib = mlSensors?.sensor_data?.vibration_level ?? engine.vibration;
  const displayLoad = mlSensors?.sensor_data?.engine_load ?? engine.engine_load;
  const displayFuelFlow = mlSensors?.sensor_data?.fuel_consumption ?? engine.fuel_flow;

  // Extract trend series data from historical ticks cache
  const rpmTrend = historicalStates.map(h => h.engine?.rpm || 0);
  const tempTrend = historicalStates.map(h => h.engine?.coolant_temp || 0);
  const pressTrend = historicalStates.map(h => h.engine?.oil_pressure || 0);
  const vibTrend = historicalStates.map(h => h.engine?.vibration || 0);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle>Propulsion Machinery Console</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {/* Instrumentation dials grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {/* RPM Dial */}
          <div className="flex flex-col items-center gap-1 bg-slate-950/10 p-1 rounded-lg">
            <DialGauge
              value={displayRpm}
              min={0}
              max={2500}
              label="Propeller RPM"
              unit="RPM"
              warningLimit={1800}
              criticalLimit={2000}
              precision={0}
            />
            <Sparkline data={rpmTrend} color="stroke-sky-500" />
          </div>

          {/* Coolant Temp Dial */}
          <div className="flex flex-col items-center gap-1 bg-slate-950/10 p-1 rounded-lg">
            <DialGauge
              value={displayTemp}
              min={0}
              max={130}
              label="Coolant Temp"
              unit="°C"
              warningLimit={95}
              criticalLimit={105}
              precision={1}
            />
            <Sparkline data={tempTrend} color={displayTemp > 95 ? 'stroke-amber-500' : 'stroke-emerald-500'} />
          </div>

          {/* Lube Oil Pressure Dial */}
          <div className="flex flex-col items-center gap-1 bg-slate-950/10 p-1 rounded-lg">
            <DialGauge
              value={displayPress}
              min={0}
              max={10.0}
              label="Lube Oil Press"
              unit="bar"
              warningLimit={2.0}
              criticalLimit={1.0}
              comparison="below"
              precision={2}
            />
            <Sparkline data={pressTrend} color={displayPress < 2.0 ? 'stroke-rose-500' : 'stroke-emerald-500'} />
          </div>

          {/* Vibration Dial */}
          <div className="flex flex-col items-center gap-1 bg-slate-950/10 p-1 rounded-lg">
            <DialGauge
              value={displayVib}
              min={0}
              max={6.0}
              label="Mach Vibration"
              unit="mm/s"
              warningLimit={3.2}
              criticalLimit={4.5}
              precision={2}
            />
            <Sparkline data={vibTrend} color={displayVib > 3.2 ? 'stroke-rose-500' : 'stroke-sky-500'} />
          </div>
        </div>

        {/* Dynamic Status Progress Tracks */}
        <div className="flex flex-col gap-2">
          <LinearBar
            value={displayLoad}
            min={0}
            max={100}
            label="Engine Power Load"
            unit="%"
            warningLimit={85}
            criticalLimit={95}
            precision={1}
          />
          <LinearBar
            value={displayFuelFlow}
            min={0}
            max={1300}
            label="Fuel Injection Rate"
            unit="L/h"
            precision={1}
          />
        </div>
      </CardContent>
    </Card>
  );
}
