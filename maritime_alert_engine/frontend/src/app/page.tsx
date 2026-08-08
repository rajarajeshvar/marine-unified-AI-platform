"use client";
import React, { useState, useEffect } from 'react';
import SimulationPanel from '@/components/SimulationPanel';
import ShipDashboard from '@/components/ShipDashboard';
import FleetDashboard from '@/components/FleetDashboard';
import AIChatbot from '@/components/AIChatbot';
const API_BASE = "http://localhost:8003";

export default function Home() {
  const [networks, setNetworks] = useState([]);
  const [alerts, setAlerts] = useState([]);

  const fetchNetworks = async () => {
    try {
      const res = await fetch(`${API_BASE}/network/status`);
      const data = await res.json();
      setNetworks(data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchAlerts = async () => {
    try {
      const res = await fetch(`${API_BASE}/alerts`);
      const data = await res.json();
      setAlerts(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchNetworks();
    fetchAlerts();

    // Setup WebSocket
    const ws = new WebSocket(`ws://localhost:8003/ws`);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'network_update' || data.event === 'alert_created') {
        fetchNetworks();
        fetchAlerts();
      }
    };

    // Polling fallback
    const interval = setInterval(() => {
      fetchNetworks();
      fetchAlerts();
    }, 5000);

    return () => {
      ws.close();
      clearInterval(interval);
    };
  }, []);

  const handleToggleNetwork = async (channel: string, isActive: boolean) => {
    try {
      await fetch(`${API_BASE}/network/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ channel, is_active: isActive })
      });
      fetchNetworks();
    } catch (e) {
      console.error(e);
    }
  };

  const triggerEmergency = async () => {
    const alertData = {
      id: `ALT-${Math.random().toString(36).substr(2, 9).toUpperCase()}`,
      ship_id: "VESSEL-001",
      priority: "critical",
      alert_type: "engine_failure",
      message: "Critical engine failure detected. Immediate assistance required.",
      latitude: 25.0,
      longitude: -40.0,
      engine_health: 5.0,
      fuel_level: 45.0,
      weather_risk: 10.0
    };

    try {
      await fetch(`${API_BASE}/alerts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(alertData)
      });
      fetchAlerts();
    } catch (e) {
      console.error(e);
    }
  };

  // Derived state for Ship Dashboard
  const activeChannel = networks.find((n: any) => n.is_active)?.channel || null;
  const pendingAlerts = alerts.filter((a: any) => a.status === 'Pending').length;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        
        <header className="flex items-center justify-between border-b border-slate-800 pb-6">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">Multi-Channel Maritime Alert Engine</h1>
            <p className="text-slate-400 mt-1">Autonomous Store-and-Forward Comm System</p>
          </div>
          <div>
            <a href="/copilot" className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded font-semibold text-sm transition-colors shadow shadow-blue-900/20 flex items-center gap-2">
              <span>⚓</span> Open Marine Copilot
            </a>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          <div className="lg:col-span-1 space-y-8">
            <SimulationPanel networks={networks} onToggle={handleToggleNetwork} />
            <ShipDashboard 
              activeChannel={activeChannel} 
              pendingAlerts={pendingAlerts} 
              triggerEmergency={triggerEmergency} 
            />
          </div>

          <div className="lg:col-span-2">
            <FleetDashboard alerts={alerts} />
          </div>

        </div>

      </div>
      <AIChatbot />
    </div>
  );
}
