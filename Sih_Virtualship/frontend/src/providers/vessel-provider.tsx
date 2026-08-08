'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { DigitalTwinSnapshot, Alert, VesselEvent } from '../types/telemetry';
import { fetchClient } from '../utils/fetch-client';
import { useWebSocket } from '../hooks/use-websocket';

interface VesselContextType {
  vesselState: DigitalTwinSnapshot | null;
  historicalStates: any[];
  alerts: Alert[];
  events: VesselEvent[];
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  mlSensors: any;
  
  // Navigation
  activeTab: string;
  setActiveTab: (tab: string) => void;
  
  // Simulation Mode
  simulationMode: string;
  changeSimulationMode: (mode: string) => Promise<void>;
  
  // Actions
  changeSimulatorState: (state: string) => Promise<void>;
  changeScenario: (scenario: string) => Promise<void>;
  refreshLogs: () => Promise<void>;
}

const VesselContext = createContext<VesselContextType | undefined>(undefined);

export function VesselProvider({ children }: { children: React.ReactNode }) {
  const [activeTab, setActiveTab] = useState<string>('Overview');
  
  // Load mode from local storage on mount
  const [simulationMode, setSimulationMode] = useState<string>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('simulationMode') || 'AUTO';
    }
    return 'AUTO';
  });

  const [vesselState, setVesselState] = useState<DigitalTwinSnapshot | null>(null);
  const [historicalStates, setHistoricalStates] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [events, setEvents] = useState<VesselEvent[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [mlSensors, setMlSensors] = useState<any>(null);

  // Keep a reference to the latest vesselState to prevent timer resets
  const latestVesselStateRef = useRef<DigitalTwinSnapshot | null>(null);
  useEffect(() => {
    latestVesselStateRef.current = vesselState;
  }, [vesselState]);

  // Initialize custom reconnecting WebSocket
  const { isConnected, lastMessage } = useWebSocket<{ type: string; data: any }>();

  // Fetch initial data from REST endpoints
  const fetchLogsAndHistory = useCallback(async () => {
    try {
      const [historyData, alertsData, eventsData, currentSnapshot] = await Promise.all([
        fetchClient.get<any[]>('/telemetry/history'),
        fetchClient.get<Alert[]>('/telemetry/alerts'),
        fetchClient.get<VesselEvent[]>('/telemetry/events'),
        fetchClient.get<DigitalTwinSnapshot>('/telemetry/snapshot'),
      ]);

      setHistoricalStates(historyData);
      setAlerts(alertsData);
      setEvents(eventsData);
      setVesselState(currentSnapshot);
      setError(null);
    } catch (err: any) {
      console.error('Failed to pre-fetch vessel telemetry snapshots:', err);
      setError('Could not establish connection to the remote ship telemetry gateway.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Run initial fetch on mount
  useEffect(() => {
    fetchLogsAndHistory();
  }, [fetchLogsAndHistory]);

  // Handle incoming real-time telemetry updates from WebSockets
  useEffect(() => {
    if (!lastMessage) return;

    const { type, data } = lastMessage;

    if (type === 'welcome') {
      const snapshot = data as DigitalTwinSnapshot;
      setVesselState(snapshot);
    } else if (type === 'snapshot') {
      const newSnapshot = data as DigitalTwinSnapshot;
      setVesselState(newSnapshot);

      // Append snapshot to historical tracking (max 60 items sliding buffer)
      setHistoricalStates((prev) => {
        const updated = [...prev, {
          timestamp: newSnapshot.timestamp,
          engine: newSnapshot.engine,
          hull: newSnapshot.hull,
          fuel: newSnapshot.fuel,
          navigation: newSnapshot.navigation,
          weather: newSnapshot.weather,
          battery_level: newSnapshot.battery_level,
          health: newSnapshot.health
        }];
        if (updated.length > 60) {
          updated.shift();
        }
        return updated;
      });

      // Synchronize alarms and events list if the number of active alerts changes
      if (newSnapshot.alerts) {
        setAlerts((prev) => {
          const currentActive = prev.filter(a => a.is_active);
          if (currentActive.length !== newSnapshot.alerts.length) {
            fetchClient.get<Alert[]>('/telemetry/alerts').then(setAlerts).catch(console.error);
            fetchClient.get<VesselEvent[]>('/telemetry/events').then(setEvents).catch(console.error);
          }
          return prev;
        });
      }
    }
  }, [lastMessage]);

  // ML Watchdog Telemetry Polling (Port 8005)
  useEffect(() => {
    const fetchMLSensors = async () => {
      try {
        const response = await fetch('http://localhost:8005/sensors');
        if (response.ok) {
          const data = await response.json();
          setMlSensors(data);
        }
      } catch (err) {
        console.warn('Failed to fetch ML sensors:', err);
      }
    };

    fetchMLSensors();
    const mlInterval = setInterval(fetchMLSensors, 5000);
    return () => clearInterval(mlInterval);
  }, []);

  // Actions
  const changeSimulationMode = useCallback(async (mode: string) => {
    setSimulationMode(mode);
    if (typeof window !== 'undefined') {
      localStorage.setItem('simulationMode', mode);
    }
  }, []);

  const changeSimulatorState = useCallback(async (state: string) => {
    try {
      await fetchClient.post('/simulator/state', { state });
      await fetchLogsAndHistory();
    } catch (err: any) {
      console.error('Error changing simulator state:', err);
      throw err;
    }
  }, [fetchLogsAndHistory]);

  const changeScenario = useCallback(async (scenario: string) => {
    try {
      await fetchClient.post('/simulator/scenario', { scenario });
      await fetchLogsAndHistory();
    } catch (err: any) {
      console.error(`Error setting voyage scenario to ${scenario}:`, err);
      throw err;
    }
  }, [fetchLogsAndHistory]);

  const refreshLogs = useCallback(async () => {
    try {
      const [alertsData, eventsData] = await Promise.all([
        fetchClient.get<Alert[]>('/telemetry/alerts'),
        fetchClient.get<VesselEvent[]>('/telemetry/events'),
      ]);
      setAlerts(alertsData);
      setEvents(eventsData);
    } catch (err) {
      console.error('Failed to sync history logs timeline:', err);
    }
  }, []);

  // Client-side simulation state transitions (if in AUTO mode)
  useEffect(() => {
    if (simulationMode !== 'AUTO') return;

    const intervalId = setInterval(() => {
      const stateVal = latestVesselStateRef.current;
      if (!stateVal) return;

      const currentState = stateVal.state;
      const statesCycle = ["OFF", "STARTING", "IDLE", "CRUISE", "HIGH_LOAD", "WARNING", "CRITICAL", "SHUTDOWN"];
      
      // Determine active index in states cycle
      let currentIdx = 3; // Default CRUISE
      if (currentState === 'DOCKED') {
        currentIdx = stateVal.engine.rpm === 0 ? 0 : 2; // OFF or IDLE
      } else if (currentState === 'ANCHORED') {
        currentIdx = 2; // IDLE
      } else if (currentState === 'MANEUVERING') {
        currentIdx = 1; // STARTING
      } else if (currentState === 'CRUISING') {
        const activeAlerts = stateVal.alerts || [];
        if (activeAlerts.some(a => a.level === 'CRITICAL')) {
          currentIdx = 6; // CRITICAL
        } else if (activeAlerts.some(a => a.level === 'WARNING')) {
          currentIdx = 5; // WARNING
        } else if (stateVal.engine.engine_load > 85) {
          currentIdx = 4; // HIGH_LOAD
        } else {
          currentIdx = 3; // CRUISE
        }
      }

      // Compute next state in loop
      const nextIdx = (currentIdx + 1) % statesCycle.length;
      const nextState = statesCycle[nextIdx];

      changeSimulatorState(nextState).catch((err) => {
        console.warn('Auto transition tick failed:', err);
      });
    }, 10000);

    return () => clearInterval(intervalId);
  }, [simulationMode, changeSimulatorState]);

  return (
    <VesselContext.Provider
      value={{
        vesselState,
        historicalStates,
        alerts,
        events,
        isConnected,
        isLoading,
        error,
        mlSensors,
        activeTab,
        setActiveTab,
        simulationMode,
        changeSimulationMode,
        changeSimulatorState,
        changeScenario,
        refreshLogs,
      }}
    >
      {children}
    </VesselContext.Provider>
  );
}

export function useVessel() {
  const context = useContext(VesselContext);
  if (context === undefined) {
    throw new Error('useVessel must be used within a VesselProvider');
  }
  return context;
}
