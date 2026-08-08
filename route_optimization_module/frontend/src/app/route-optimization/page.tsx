"use client";

import { useState, useEffect, useRef } from "react";
import Map from "@/components/Map";
import Analytics from "@/components/Analytics";
import Recommendations from "@/components/Recommendations";
import { Ship, Navigation, Shield, Wind, Thermometer, Eye, Fuel, Timer, Activity, AlertTriangle } from "lucide-react";

// Mock list of safe harbors for emergency routing
const SAFE_HARBORS = [
  { name: "Ponta Delgada, Azores", lat: 37.74, lng: -25.67 },
  { name: "Halifax, Canada", lat: 44.64, lng: -63.57 },
  { name: "Lisbon, Portugal", lat: 38.72, lng: -9.14 },
  { name: "Bermuda", lat: 32.30, lng: -64.75 }
];

// Helper to calculate distance (simple euclidean for fast nearest-neighbor)
const getDistance = (lat1: number, lng1: number, lat2: number, lng2: number) => {
  return Math.sqrt(Math.pow(lat1 - lat2, 2) + Math.pow(lng1 - lng2, 2));
};

export default function Dashboard() {
  const [routeData, setRouteData] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [liveShips, setLiveShips] = useState<any[]>([]);
  const [selectedShip, setSelectedShip] = useState<any>(null);
  
  // Predictive Maintenance State
  const [engineHealth, setEngineHealth] = useState<any>(null);
  const [isEmergency, setIsEmergency] = useState(false);
  const [emergencyHarbor, setEmergencyHarbor] = useState<any>(null);
  
  // Read emergency flag from URL instantly on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get('emergency') === 'true') {
        setIsEmergency(true);
      }
    }
  }, []);
  
  const wsRef = useRef<WebSocket | null>(null);

  const fetchRoute = async (startLat = 25.0, startLng = -40.0, destLat = 40.0, destLng = -20.0) => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/optimize-route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start: { lat: startLat, lng: startLng },
          destination: { lat: destLat, lng: destLng },
          optimize_for: "balanced"
        })
      });
      const data = await response.json();
      setRouteData(data);

      const recsResponse = await fetch(`http://localhost:8000/recommendations?lat=${startLat}&lng=${startLng}`);
      const recsData = await recsResponse.json();
      setRecommendations(recsData);
    } catch (error) {
      console.error("Failed to fetch route:", error);
    }
    setLoading(false);
  };

  const fetchLiveShips = async () => {
    try {
      const response = await fetch("http://localhost:8000/live-ships");
      const data = await response.json();
      if (data.ships) {
        setLiveShips(data.ships);
      }
    } catch (error) {
      console.error("Failed to fetch live ships:", error);
    }
  };

  // Connect to Predictive Maintenance WebSocket
  useEffect(() => {
    wsRef.current = new WebSocket("ws://localhost:8001/ws");
    
    wsRef.current.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "sensor_update") {
        setEngineHealth(msg.prediction);
      }
    };
    
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  // Handle Emergency Trigger
  useEffect(() => {
    if (engineHealth && engineHealth.failure_probability > 70 && !isEmergency) {
      setIsEmergency(true);
      
      const currentLat = selectedShip?.lat || 25.0;
      const currentLng = selectedShip?.lng || -40.0;
      
      // Find nearest harbor
      let nearest = SAFE_HARBORS[0];
      let minDistance = getDistance(currentLat, currentLng, nearest.lat, nearest.lng);
      
      for (const harbor of SAFE_HARBORS) {
        const dist = getDistance(currentLat, currentLng, harbor.lat, harbor.lng);
        if (dist < minDistance) {
          minDistance = dist;
          nearest = harbor;
        }
      }
      
      setEmergencyHarbor(nearest);
      fetchRoute(currentLat, currentLng, nearest.lat, nearest.lng);
    }
  }, [engineHealth, isEmergency, selectedShip]);

  useEffect(() => {
    fetchRoute();
    fetchLiveShips();
    const interval = setInterval(fetchLiveShips, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleShipSelect = (ship: any) => {
    setSelectedShip(ship);
    if (!isEmergency) {
      fetchRoute(ship.lat, ship.lng);
    }
  };

  return (
    <div className={`min-h-screen p-6 transition-colors duration-1000 ${isEmergency ? 'bg-red-950 text-red-50' : 'bg-slate-900 text-slate-200'}`}>
      
      {/* EMERGENCY BANNER */}
      {isEmergency && (
        <div className="bg-red-600 text-white p-4 rounded-lg mb-6 flex flex-col items-center justify-center animate-pulse border-4 border-red-500 shadow-[0_0_50px_rgba(220,38,38,0.6)]">
          <div className="flex items-center gap-3 text-2xl font-bold">
            <AlertTriangle className="w-8 h-8" />
            CRITICAL ENGINE FAULT DETECTED: {engineHealth?.fault_type}
            <AlertTriangle className="w-8 h-8" />
          </div>
          <p className="mt-2 text-lg">Failure Probability: <span className="font-bold text-yellow-300">{engineHealth?.failure_probability}%</span> | Remaining Useful Life: {engineHealth?.remaining_useful_life} hrs</p>
          <div className="mt-4 bg-red-900/50 px-6 py-2 rounded-full font-mono text-xl border border-red-400">
            AUTONOMOUS RE-ROUTING TO NEAREST SAFE HARBOR: {emergencyHarbor?.name.toUpperCase()}
          </div>
        </div>
      )}

      <header className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <Ship className={`w-8 h-8 ${isEmergency ? 'text-red-400' : 'text-blue-500'}`} />
          <div>
            <h1 className={`text-3xl font-bold bg-clip-text text-transparent ${isEmergency ? 'bg-gradient-to-r from-red-400 to-orange-400' : 'bg-gradient-to-r from-blue-400 to-teal-400'}`}>
              Maritime Route Optimizer
            </h1>
            <p className={`${isEmergency ? 'text-red-300' : 'text-slate-400'} text-sm`}>Real-time AISStream Integration Active</p>
          </div>
        </div>
        <div className="flex gap-4">
          <button 
            onClick={() => {
              if (typeof window !== 'undefined') {
                window.location.href = '/';
              }
            }}
            className="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 px-6 py-2 rounded-lg font-medium transition-colors"
          >
            Back to Digital Twin
          </button>
          <button 
            onClick={() => fetchRoute(selectedShip?.lat || 25.0, selectedShip?.lng || -40.0, isEmergency ? emergencyHarbor?.lat : 40.0, isEmergency ? emergencyHarbor?.lng : -20.0)}
            disabled={loading}
            className={`${isEmergency ? 'bg-red-700 hover:bg-red-800' : 'bg-blue-600 hover:bg-blue-700'} text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50`}
          >
            {loading ? "Optimizing..." : "Recalculate Route"}
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <Map 
            routeData={routeData} 
            liveShips={liveShips} 
            onShipSelect={handleShipSelect} 
            isEmergency={isEmergency}
            emergencyHarbor={emergencyHarbor}
          />
        </div>
        <div className="space-y-6">
          
          {/* Engine Health Integration Card */}
          <div className={`p-6 rounded-lg border ${isEmergency ? 'bg-red-900/40 border-red-700' : 'bg-slate-800 border-slate-700'}`}>
            <h3 className={`text-xl font-semibold mb-4 flex items-center gap-2 ${isEmergency ? 'text-red-300' : 'text-slate-200'}`}>
              <Activity className="w-5 h-5"/> Live Engine Health
            </h3>
            {engineHealth ? (
               <div className="space-y-3">
                 <div className="flex justify-between items-center pb-2 border-b border-slate-700/50">
                   <span className="text-slate-400">Health Score</span>
                   <span className={`font-bold ${engineHealth.health_score > 80 ? 'text-emerald-400' : 'text-red-400'}`}>{engineHealth.health_score}/100</span>
                 </div>
                 <div className="flex justify-between items-center pb-2 border-b border-slate-700/50">
                   <span className="text-slate-400">Failure Risk</span>
                   <span className={`font-bold ${engineHealth.failure_probability > 50 ? 'text-red-400' : 'text-emerald-400'}`}>{engineHealth.failure_probability}%</span>
                 </div>
                 <div className="flex justify-between items-center pb-2 border-b border-slate-700/50">
                   <span className="text-slate-400">RUL</span>
                   <span className="text-slate-200">{engineHealth.remaining_useful_life} hrs</span>
                 </div>
                 <div className="flex flex-col mt-2">
                   <span className="text-slate-400 text-sm mb-1">AI Recommendation</span>
                   <span className={`px-3 py-2 rounded text-sm font-medium ${isEmergency ? 'bg-red-950/80 text-red-200 border border-red-800' : 'bg-slate-900 text-blue-300'}`}>
                     {engineHealth.maintenance_recommendation}
                   </span>
                 </div>
               </div>
            ) : (
               <div className="text-sm text-slate-500 animate-pulse flex items-center gap-2">
                 Waiting for engine telemetry...
               </div>
            )}
          </div>

          <Recommendations recommendations={recommendations} />
          
          {/* Selected Ship Card */}
          {selectedShip && (
             <div className="bg-blue-900/30 p-6 rounded-lg border border-blue-800">
               <h3 className="text-xl font-semibold mb-2 text-blue-300 flex items-center gap-2">
                 <Ship className="w-5 h-5"/> Live Ship Selected
               </h3>
               <p className="text-sm text-slate-300 mb-1"><strong>Name:</strong> {selectedShip.name}</p>
               <p className="text-sm text-slate-300 mb-1"><strong>MMSI:</strong> {selectedShip.mmsi}</p>
               <p className="text-sm text-slate-300"><strong>Speed:</strong> {selectedShip.speed_knots} knots</p>
             </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Analytics data={routeData} />
        </div>
        
        {/* Weather Conditions Card */}
        <div className={`p-6 rounded-lg border ${isEmergency ? 'bg-red-900/30 border-red-800' : 'bg-slate-800 border-slate-700'}`}>
          <h3 className="text-xl font-semibold mb-4">Live Ocean Conditions</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className={`${isEmergency ? 'bg-red-950' : 'bg-slate-900'} p-4 rounded-lg flex flex-col items-center justify-center text-center`}>
              <Shield className={`w-8 h-8 ${isEmergency ? 'text-red-500' : 'text-emerald-500'} mb-2`} />
              <span className="text-sm text-slate-400">Safety Score</span>
              <span className="text-xl font-bold text-slate-200">{routeData?.safety_score || "--"}/100</span>
            </div>
            <div className={`${isEmergency ? 'bg-red-950' : 'bg-slate-900'} p-4 rounded-lg flex flex-col items-center justify-center text-center`}>
              <Wind className="w-8 h-8 text-blue-400 mb-2" />
              <span className="text-sm text-slate-400">Wind</span>
              <span className="text-xl font-bold text-slate-200">18 knots</span>
            </div>
            <div className={`${isEmergency ? 'bg-red-950' : 'bg-slate-900'} p-4 rounded-lg flex flex-col items-center justify-center text-center`}>
              <Thermometer className="w-8 h-8 text-red-400 mb-2" />
              <span className="text-sm text-slate-400">Temp</span>
              <span className="text-xl font-bold text-slate-200">14 °C</span>
            </div>
            <div className={`${isEmergency ? 'bg-red-950' : 'bg-slate-900'} p-4 rounded-lg flex flex-col items-center justify-center text-center`}>
              <Eye className="w-8 h-8 text-slate-300 mb-2" />
              <span className="text-sm text-slate-400">Visibility</span>
              <span className="text-xl font-bold text-slate-200">9 NM</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
