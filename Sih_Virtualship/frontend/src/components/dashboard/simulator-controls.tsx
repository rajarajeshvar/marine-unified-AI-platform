'use client';

import React, { useState, useEffect } from 'react';
import { useVessel } from '../../providers/vessel-provider';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Loader2, CheckCircle2, AlertCircle, Play, Cpu, Eye } from 'lucide-react';

export function SimulatorControls() {
  const { 
    vesselState, 
    simulationMode, 
    changeSimulationMode, 
    changeSimulatorState, 
    changeScenario 
  } = useVessel();
  
  // Pending actions state
  const [isPending, setIsPending] = useState<string | null>(null);
  
  // Notification states
  const [notification, setNotification] = useState<{
    type: 'success' | 'error';
    message: string;
  } | null>(null);

  // Mapped active states
  const [selectedState, setSelectedState] = useState<string>('CRUISE');
  const [selectedScenario, setSelectedScenario] = useState<string>('Normal Voyage');

  // Align UI selections on mount or vesselState updates
  useEffect(() => {
    if (!vesselState) return;

    // Set simulator state fallback mapping
    const opState = vesselState.state;
    if (opState === 'DOCKED') {
      if (vesselState.engine.rpm === 0) {
        setSelectedState(prev => ['OFF', 'SHUTDOWN'].includes(prev) ? prev : 'OFF');
      } else {
        setSelectedState('IDLE');
      }
    } else if (opState === 'ANCHORED') {
      setSelectedState('IDLE');
    } else if (opState === 'MANEUVERING') {
      setSelectedState('STARTING');
    } else if (opState === 'CRUISING') {
      const activeAlerts = vesselState.alerts || [];
      if (activeAlerts.some(a => a.level === 'CRITICAL')) {
        setSelectedState('CRITICAL');
      } else if (activeAlerts.some(a => a.level === 'WARNING')) {
        setSelectedState('WARNING');
      } else if (vesselState.engine.engine_load > 85) {
        setSelectedState('HIGH_LOAD');
      } else {
        setSelectedState('CRUISE');
      }
    }

    // Set scenario fallback mapping based on alerts presence
    const activeCodes = new Set((vesselState.alerts || []).map(a => a.code));
    if (activeCodes.has("ROLL_WARNING") || activeCodes.has("ROLL_CRITICAL")) {
      setSelectedScenario("Heavy Weather");
    } else if (activeCodes.has("LEAK_DETECTED")) {
      setSelectedScenario("Fuel Leak");
    } else if (activeCodes.has("TEMP_CRITICAL") && activeCodes.has("OIL_LOW_CRITICAL")) {
      setSelectedScenario("Engine Overheat");
    } else if (activeCodes.has("VIB_CRITICAL") && !activeCodes.has("OIL_LOW_CRITICAL")) {
      setSelectedScenario("Emergency Stop");
    } else if (vesselState.state === 'DOCKED' && vesselState.engine.rpm === 0) {
      setSelectedScenario(prev => ['Docking', 'Maintenance Mode'].includes(prev) ? prev : 'Docking');
    } else {
      setSelectedScenario("Normal Voyage");
    }
  }, [vesselState]);

  if (!vesselState) return null;

  const simulatorStates = ["OFF", "STARTING", "IDLE", "CRUISE", "HIGH_LOAD", "WARNING", "CRITICAL", "SHUTDOWN"];

  const scenarios = [
    { type: "Normal Voyage", label: "Normal Voyage" },
    { type: "Heavy Weather", label: "Heavy Weather" },
    { type: "Fuel Leak", label: "Fuel Leak" },
    { type: "Engine Overheat", label: "Engine Overheat" },
    { type: "Bearing Wear", label: "Bearing Wear" },
    { type: "Cooling Failure", label: "Cooling Failure" },
    { type: "Docking", label: "Docking" },
    { type: "Emergency Stop", label: "Emergency Stop" },
    { type: "Maintenance Mode", label: "Maintenance Mode" }
  ];

  const handleModeToggle = async (mode: string) => {
    setIsPending(`mode_${mode}`);
    setNotification(null);
    try {
      await changeSimulationMode(mode);
      setNotification({
        type: 'success',
        message: `Simulation Mode changed to ${mode}`
      });
    } catch (err) {
      setNotification({
        type: 'error',
        message: `Command failed: Could not change simulation mode.`
      });
    } finally {
      setIsPending(null);
    }
  };

  const handleStateSelect = async (stateName: string) => {
    setIsPending(`state_${stateName}`);
    setNotification(null);
    try {
      await changeSimulatorState(stateName);
      setSelectedState(stateName);
      setNotification({
        type: 'success',
        message: `Operator selected ${stateName}`
      });
    } catch (err) {
      setNotification({
        type: 'error',
        message: `Command failed: Could not communicate state update.`
      });
    } finally {
      setIsPending(null);
    }
  };

  const handleScenarioSelect = async (scenarioType: string) => {
    setIsPending(`scenario_${scenarioType}`);
    setNotification(null);
    try {
      await changeScenario(scenarioType);
      setSelectedScenario(scenarioType);
      setNotification({
        type: 'success',
        message: `Voyage scenario changed to ${scenarioType}`
      });
    } catch (err) {
      setNotification({
        type: 'error',
        message: `Command failed: Could not trigger simulator scenario modifier.`
      });
    } finally {
      setIsPending(null);
    }
  };

  const isAuto = simulationMode === 'AUTO';

  return (
    <Card className="h-full flex flex-col bg-slate-900/10 border-slate-800">
      <CardHeader className="border-b border-slate-800/40 py-3 flex flex-row items-center justify-between">
        <div className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-sky-400" />
          <CardTitle>Simulator Control Center</CardTitle>
        </div>
        {/* Active status badge */}
        <span className={`px-2 py-0.5 rounded text-[8px] font-bold font-mono uppercase border ${
          isAuto 
            ? "border-sky-500 bg-sky-950/20 text-sky-400 shadow-[0_0_6px_rgba(56,189,248,0.15)] animate-pulse" 
            : "border-amber-500 bg-amber-950/10 text-amber-500"
        }`}>
          {simulationMode}
        </span>
      </CardHeader>
      
      <CardContent className="p-4 xl:p-5 space-y-4 flex-grow flex flex-col justify-between font-mono text-xs select-none">
        
        {/* Simulation Mode Toggle Options */}
        <div>
          <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-2 font-bold">
            Select Simulation Mode
          </span>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => handleModeToggle('AUTO')}
              disabled={isPending !== null}
              className={`p-2 border rounded text-[10px] font-bold uppercase tracking-wider transition-all duration-150 cursor-pointer flex items-center justify-center gap-1.5 ${
                isAuto
                  ? "border-sky-500 bg-sky-950/20 text-sky-450 shadow-[0_0_6px_rgba(56,189,248,0.1)]"
                  : "border-slate-800 bg-slate-950/10 text-slate-500 hover:border-slate-700 hover:text-slate-300"
              } disabled:opacity-50`}
            >
              {isPending === 'mode_AUTO' ? (
                <Loader2 className="h-3 w-3 animate-spin text-sky-450" />
              ) : (
                <>
                  <span className={`h-1.5 w-1.5 rounded-full ${isAuto ? 'bg-sky-400 animate-ping' : 'bg-slate-600'}`}></span>
                  Automatic
                </>
              )}
            </button>
            <button
              onClick={() => handleModeToggle('MANUAL')}
              disabled={isPending !== null}
              className={`p-2 border rounded text-[10px] font-bold uppercase tracking-wider transition-all duration-150 cursor-pointer flex items-center justify-center gap-1.5 ${
                !isAuto
                  ? "border-amber-500 bg-amber-950/20 text-amber-500 shadow-[0_0_6px_rgba(245,158,11,0.1)]"
                  : "border-slate-800 bg-slate-950/10 text-slate-500 hover:border-slate-700 hover:text-slate-300"
              } disabled:opacity-50`}
            >
              {isPending === 'mode_MANUAL' ? (
                <Loader2 className="h-3 w-3 animate-spin text-amber-500" />
              ) : (
                <>
                  <span className={`h-1.5 w-1.5 rounded-full ${!isAuto ? 'bg-amber-500' : 'bg-slate-600'}`}></span>
                  Manual
                </>
              )}
            </button>
          </div>
        </div>

        {/* Simulator Throttle State Selection */}
        <div className="border-t border-slate-800/40 pt-3.5 relative">
          <div className="flex justify-between items-center mb-2.5">
            <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-bold">
              Set Operating State
            </span>
            {isAuto && (
              <span className="text-[8px] text-slate-500 font-mono uppercase bg-slate-950/50 px-1.5 py-0.5 rounded flex items-center gap-1">
                <Eye className="h-2.5 w-2.5 text-slate-500" />
                Read-Only
              </span>
            )}
          </div>
          
          <div className="grid grid-cols-4 gap-1.5">
            {simulatorStates.map((st) => {
              const loader = isPending === `state_${st}`;
              const isCurrent = selectedState === st;
              return (
                <button
                  key={st}
                  onClick={() => handleStateSelect(st)}
                  disabled={isPending !== null || isAuto}
                  title={isAuto ? "Controlled by Automatic Simulation" : `Set state to ${st}`}
                  className={`p-2 border rounded text-[9px] font-bold uppercase tracking-wider transition-all duration-150 cursor-pointer text-center flex items-center justify-center gap-1 min-h-[32px] select-none ${
                    isCurrent
                      ? isAuto
                        ? "border-sky-500/40 bg-sky-950/10 text-sky-400/80"
                        : "border-sky-500 bg-sky-950/20 text-sky-450 shadow-[0_0_8px_rgba(56,189,248,0.15)]"
                      : "border-slate-800 bg-slate-950/20 text-slate-500 hover:border-slate-700 hover:text-slate-350"
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {loader ? <Loader2 className="h-3 w-3 animate-spin text-sky-450" /> : st}
                </button>
              );
            })}
          </div>
          {isAuto && (
            <p className="text-[8px] text-slate-600 mt-2 italic">
              * Controlled by Automatic Simulation. Toggle to MANUAL mode to override.
            </p>
          )}
        </div>

        {/* Voyage Scenario Selection */}
        <div className="border-t border-slate-800/40 pt-3.5">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-2.5 font-bold">
            Select Voyage Scenario
          </span>
          <div className="grid grid-cols-3 gap-1.5">
            {scenarios.map((sc) => {
              const isCurrent = selectedScenario === sc.type;
              const loader = isPending === `scenario_${sc.type}`;
              return (
                <button
                  key={sc.type}
                  onClick={() => handleScenarioSelect(sc.type)}
                  disabled={isPending !== null}
                  className={`p-2.5 border rounded text-[9px] font-bold uppercase tracking-wider transition-all duration-150 cursor-pointer text-center flex items-center justify-center gap-1 min-h-[34px] select-none ${
                    isCurrent
                      ? "border-sky-500/70 bg-sky-950/30 text-sky-450 shadow-[0_0_8px_rgba(56,189,248,0.15)]"
                      : "border-slate-800 bg-slate-950/20 text-slate-500 hover:border-slate-700 hover:text-slate-300"
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {loader ? <Loader2 className="h-3 w-3 animate-spin text-sky-450" /> : sc.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Inline Feedback Alerts */}
        {notification && (
          <div className={`p-2.5 border rounded-lg flex items-center gap-2 mt-2 transition-all duration-200 ${
            notification.type === 'success'
              ? 'border-emerald-950/60 bg-emerald-950/10 text-emerald-400'
              : 'border-rose-950/60 bg-rose-950/10 text-rose-500'
          }`}>
            {notification.type === 'success' 
              ? <CheckCircle2 className="h-3.5 w-3.5 flex-shrink-0" />
              : <AlertCircle className="h-3.5 w-3.5 flex-shrink-0" />
            }
            <span className="text-[10px] tracking-wide leading-tight">{notification.message}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
