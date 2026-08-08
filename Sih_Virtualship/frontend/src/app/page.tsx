'use client';

import React from 'react';
import { useVessel } from '../providers/vessel-provider';
import { ShipOverview } from '../components/dashboard/ship-overview';
import { EngineStatus } from '../components/dashboard/engine-status';
import { HullStatus } from '../components/dashboard/hull-status';
import { FuelPanel } from '../components/dashboard/fuel-panel';
import { NavigationPanel } from '../components/dashboard/navigation-panel';
import { AlertsTimeline } from '../components/dashboard/alerts-timeline';
import { WeatherPanel } from '../components/dashboard/weather-panel';
import { MaintenancePanel } from '../components/dashboard/maintenance-panel';
import { DashboardRouteMap } from '../components/dashboard/dashboard-route-map';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function DashboardPage() {
  const { activeTab, alerts } = useVessel();
  const router = useRouter();
  const [showPopup, setShowPopup] = useState(false);
  const [criticalFault, setCriticalFault] = useState<string>('');

  useEffect(() => {
    let isAcknowledged = false;
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      isAcknowledged = urlParams.get('acknowledged') === 'true';
    }

    const criticalAlert = alerts?.find(a => a.level === 'CRITICAL');
    if (criticalAlert && !isAcknowledged) {
      setCriticalFault(criticalAlert.message || 'ENGINE FAILURE DETECTED');
      setShowPopup(true);
      
      // Play alert sound (Web Audio API)
      try {
        const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();
        oscillator.type = 'square';
        oscillator.frequency.setValueAtTime(800, audioCtx.currentTime);
        oscillator.frequency.setValueAtTime(600, audioCtx.currentTime + 0.2);
        oscillator.frequency.setValueAtTime(800, audioCtx.currentTime + 0.4);
        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime); // Low volume
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.6);
      } catch (e) {
        console.warn("Audio context not supported or blocked");
      }
      
      const timeout = setTimeout(() => {
        setShowPopup(false);
      }, 5000); // Popup stays for 5 seconds
      
      return () => clearTimeout(timeout);
    } else {
      setShowPopup(false);
    }
  }, [alerts]);

  const SidePopup = () => {
    if (!showPopup) return null;
    return (
      <div className="fixed top-24 right-6 z-[9999] bg-slate-900 border-2 border-red-500 rounded-lg shadow-[0_0_20px_rgba(220,38,38,0.4)] p-4 max-w-sm">
        <div className="flex items-start gap-4">
          <div className="text-3xl animate-pulse">🚨</div>
          <div>
            <h3 className="text-red-400 font-bold text-sm uppercase tracking-wider mb-1">Critical Alert</h3>
            <p className="text-slate-200 text-base font-semibold">{criticalFault}</p>
            <p className="text-red-300 text-xs mt-2 font-mono">Recalculating autonomous route...</p>
          </div>
        </div>
      </div>
    );
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'Sensors':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 xl:gap-6">
            <EngineStatus />
            <FuelPanel />
            <NavigationPanel />
            <HullStatus />
          </div>
        );
      case 'Hull':
        return (
          <div className="w-full max-w-5xl mx-auto h-[calc(100vh-140px)]">
            <HullStatus />
          </div>
        );
      case 'Fuel':
        return (
          <div className="w-full max-w-5xl mx-auto h-[calc(100vh-140px)]">
            <FuelPanel />
          </div>
        );
      case 'Navigation':
        return (
          <div className="w-full max-w-5xl mx-auto h-[calc(100vh-140px)]">
            <NavigationPanel />
          </div>
        );
      case 'Weather':
        return (
          <div className="w-full max-w-5xl mx-auto h-[calc(100vh-140px)]">
            <WeatherPanel />
          </div>
        );
      case 'Maintenance':
        return (
          <div className="w-full max-w-5xl mx-auto h-[calc(100vh-140px)]">
            <MaintenancePanel />
          </div>
        );
      case 'Alerts':
        return (
          <div className="w-full max-w-5xl mx-auto h-[calc(100vh-140px)] flex flex-col">
            <AlertsTimeline />
          </div>
        );
      case 'Overview':
      default:
        return (
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 xl:gap-6">
            {/* Primary Telemetry Grid Column (Spans 2 columns on desktop) */}
            <div className="xl:col-span-2 flex flex-col gap-4 xl:gap-6">
              {/* Spatial Overview Map */}
              <div className="w-full h-[600px]">
                <ShipOverview />
              </div>
              
              {/* Route Optimization Map */}
              <div className="w-full mt-4">
                <DashboardRouteMap />
              </div>
            </div>

            {/* Auxiliary Monitoring & Control Column (Spans 1 column on desktop) */}
            <div className="flex flex-col gap-4 xl:gap-6">
              {/* Active Alarms & event list logs */}
              <div className="flex-1 min-h-[350px]">
                <AlertsTimeline />
              </div>

              {/* Local weather conditions */}
              <div>
                <WeatherPanel />
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <>
      <SidePopup />
      {renderContent()}
    </>
  );
}
