"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Ship, Activity, AlertTriangle, Navigation } from "lucide-react";
import Link from 'next/link';

type EngineData = {
  timestamp: string;
  engine_id: string;
  engine_temperature: number;
  rpm: number;
  vibration_level: number;
  engine_load: number;
  oil_pressure: number;
};

type PredictionData = {
  health_score: number;
  failure_probability: number;
  remaining_useful_life: number;
  maintenance_recommendation: string;
  fault_type: string;
};

export default function DigitalTwinDashboard() {
  const router = useRouter();
  const [telemetry, setTelemetry] = useState<EngineData[]>([]);
  const [prediction, setPrediction] = useState<PredictionData | null>(null);
  const [isAlerting, setIsAlerting] = useState(false);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8001/ws');

    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'sensor_update') {
        setTelemetry((prev) => {
          const updated = [...prev, msg.data];
          return updated.slice(-20); // keep last 20 data points
        });
        setPrediction(msg.prediction);
      }
    };

    return () => {
      socket.close();
    };
  }, []);

  // Autonomous Rerouting Trigger
  useEffect(() => {
    if (prediction && prediction.failure_probability > 70) {
      setIsAlerting(true);
      // Wait 3 seconds to let user see the fault on the digital twin, then redirect
      const timeout = setTimeout(() => {
        router.push('/route-optimization?emergency=true');
      }, 3000);
      return () => clearTimeout(timeout);
    } else {
      setIsAlerting(false);
    }
  }, [prediction, router]);

  return (
    <div className={`min-h-screen p-6 transition-colors duration-1000 ${isAlerting ? 'bg-red-950 text-red-50' : 'bg-slate-900 text-slate-200'}`}>
      
      {isAlerting && (
        <div className="bg-red-600 text-white p-4 rounded-lg mb-6 flex flex-col items-center justify-center animate-pulse border-4 border-red-500 shadow-[0_0_50px_rgba(220,38,38,0.6)]">
          <div className="flex items-center gap-3 text-2xl font-bold">
            <AlertTriangle className="w-8 h-8" />
            CRITICAL ENGINE FAULT: {prediction?.fault_type}
            <AlertTriangle className="w-8 h-8" />
          </div>
          <p className="mt-2 text-lg">Failure Probability: <span className="font-bold text-yellow-300">{prediction?.failure_probability}%</span></p>
          <div className="mt-4 bg-red-900/50 px-6 py-2 rounded-full font-mono text-xl border border-red-400">
            INITIATING AUTONOMOUS EMERGENCY REROUTING...
          </div>
        </div>
      )}

      <header className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <Activity className={`w-8 h-8 ${isAlerting ? 'text-red-400' : 'text-blue-500'}`} />
          <div>
            <h1 className={`text-3xl font-bold bg-clip-text text-transparent ${isAlerting ? 'bg-gradient-to-r from-red-400 to-orange-400' : 'bg-gradient-to-r from-blue-400 to-teal-400'}`}>
              Predictive Maintenance Digital Twin
            </h1>
            <p className={`${isAlerting ? 'text-red-300' : 'text-slate-400'} text-sm`}>Live Engine Telemetry & AI Prognostics</p>
          </div>
        </div>
        <Link 
          href="/route-optimization"
          className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 px-6 py-2 rounded-lg font-medium transition-colors"
        >
          <Navigation className="w-4 h-4" />
          Go to Fleet Routing Map
        </Link>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Metric Cards */}
        <div className={`p-6 rounded-xl border ${isAlerting ? 'bg-red-900/40 border-red-700' : 'bg-slate-800 border-slate-700'}`}>
          <h3 className="text-sm font-medium text-slate-400">Health Score</h3>
          <p className={`text-4xl font-bold mt-2 ${prediction && prediction.health_score < 40 ? 'text-red-400' : 'text-emerald-400'}`}>
            {prediction?.health_score?.toFixed(1) || '--'}
          </p>
        </div>
        <div className={`p-6 rounded-xl border ${isAlerting ? 'bg-red-900/40 border-red-700' : 'bg-slate-800 border-slate-700'}`}>
          <h3 className="text-sm font-medium text-slate-400">Failure Probability</h3>
          <p className={`text-4xl font-bold mt-2 ${prediction && prediction.failure_probability > 50 ? 'text-red-400 animate-pulse' : 'text-slate-50'}`}>
            {prediction?.failure_probability?.toFixed(1) || '--'}%
          </p>
        </div>
        <div className={`p-6 rounded-xl border ${isAlerting ? 'bg-red-900/40 border-red-700' : 'bg-slate-800 border-slate-700'}`}>
          <h3 className="text-sm font-medium text-slate-400">Remaining Useful Life</h3>
          <p className="text-4xl font-bold mt-2 text-blue-400">
            {prediction?.remaining_useful_life?.toFixed(0) || '--'} <span className="text-xl text-slate-500">hrs</span>
          </p>
        </div>
        <div className={`p-6 rounded-xl border ${isAlerting ? 'bg-red-900/40 border-red-700' : 'bg-slate-800 border-slate-700'}`}>
          <h3 className="text-sm font-medium text-slate-400">Current Status</h3>
          <p className={`text-2xl font-bold mt-3 ${prediction && prediction.fault_type !== 'Normal' ? 'text-red-500' : 'text-amber-400'}`}>
            {prediction?.fault_type || 'Normal'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className={`col-span-2 p-6 rounded-xl border min-h-[400px] ${isAlerting ? 'bg-red-900/20 border-red-800' : 'bg-slate-800 border-slate-700'}`}>
          <h3 className="text-lg font-medium mb-6">Engine Temperature Trend</h3>
          {telemetry.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={telemetry}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="timestamp" stroke="#94a3b8" tickFormatter={(tick) => new Date(tick).toLocaleTimeString()} />
                <YAxis stroke="#94a3b8" domain={['dataMin - 5', 'dataMax + 5']} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }}
                  itemStyle={{ color: '#e2e8f0' }}
                  labelFormatter={(label) => new Date(label).toLocaleTimeString()}
                />
                <Line type="monotone" dataKey="engine_temperature" stroke={isAlerting ? "#ef4444" : "#60a5fa"} strokeWidth={3} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-slate-500">
              Waiting for sensor data...
            </div>
          )}
        </div>
        
        <div className={`p-6 rounded-xl border ${isAlerting ? 'bg-red-900/20 border-red-800' : 'bg-slate-800 border-slate-700'}`}>
          <h3 className="text-lg font-medium mb-4">Maintenance Action</h3>
          <div className={`p-4 rounded-lg border ${isAlerting ? 'bg-red-950/80 border-red-500' : 'bg-slate-900 border-slate-700'}`}>
            <p className={`text-xl font-medium ${isAlerting ? 'text-red-300' : 'text-slate-200'}`}>
              {prediction?.maintenance_recommendation || 'Analyzing telemetry...'}
            </p>
          </div>
          
          <div className="mt-8">
             <h4 className="text-sm font-medium text-slate-400 mb-2">Live Engine Telemetry</h4>
             <div className="space-y-3">
               <div className="flex justify-between border-b border-slate-700/50 pb-2">
                 <span className="text-slate-300">Vibration Level</span>
                 <span className="font-mono text-slate-100">{telemetry.length > 0 ? telemetry[telemetry.length-1].vibration_level.toFixed(2) : '--'} g</span>
               </div>
               <div className="flex justify-between border-b border-slate-700/50 pb-2">
                 <span className="text-slate-300">Oil Pressure</span>
                 <span className="font-mono text-slate-100">{telemetry.length > 0 && telemetry[telemetry.length-1].oil_pressure !== undefined ? telemetry[telemetry.length-1].oil_pressure.toFixed(2) : '--'} bar</span>
               </div>
               <div className="flex justify-between border-b border-slate-700/50 pb-2">
                 <span className="text-slate-300">Engine Load</span>
                 <span className="font-mono text-slate-100">{telemetry.length > 0 ? telemetry[telemetry.length-1].engine_load.toFixed(1) : '--'} %</span>
               </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
