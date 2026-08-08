"use client";

import { useEffect, useState } from 'react';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

type EngineData = {
  timestamp: string;
  engine_id: string;
  engine_temperature: number;
  rpm: number;
  vibration_level: number;
  engine_load: number;
};

type PredictionData = {
  health_score: number;
  failure_probability: number;
  remaining_useful_life: number;
  maintenance_recommendation: string;
  fault_type: string;
};

export default function Dashboard() {
  const [telemetry, setTelemetry] = useState<EngineData[]>([]);
  const [prediction, setPrediction] = useState<PredictionData | null>(null);

  useEffect(() => {
    // For a real app, you'd use the actual backend URL
    const socket = new WebSocket('ws://localhost:8000/ws');

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

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric Cards */}
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/50">
          <h3 className="text-sm font-medium text-slate-400">Health Score</h3>
          <p className="text-3xl font-bold mt-2 text-emerald-400">
            {prediction?.health_score?.toFixed(1) || '--'}
          </p>
        </div>
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/50">
          <h3 className="text-sm font-medium text-slate-400">Failure Probability</h3>
          <p className={`text-3xl font-bold mt-2 ${prediction && prediction.failure_probability > 50 ? 'text-red-400' : 'text-slate-50'}`}>
            {prediction?.failure_probability?.toFixed(1) || '--'}%
          </p>
        </div>
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/50">
          <h3 className="text-sm font-medium text-slate-400">Remaining Useful Life</h3>
          <p className="text-3xl font-bold mt-2 text-blue-400">
            {prediction?.remaining_useful_life?.toFixed(0) || '--'} <span className="text-lg">hrs</span>
          </p>
        </div>
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/50">
          <h3 className="text-sm font-medium text-slate-400">Fault Type</h3>
          <p className="text-xl font-bold mt-2 text-amber-400">
            {prediction?.fault_type || 'Normal'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="col-span-2 p-4 rounded-xl border border-slate-800 bg-slate-900/50 min-h-[400px]">
          <h3 className="text-lg font-medium mb-4">Engine Temperature Trend</h3>
          {telemetry.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={telemetry}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="timestamp" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" domain={['dataMin - 10', 'dataMax + 10']} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }}
                  itemStyle={{ color: '#e2e8f0' }}
                />
                <Line type="monotone" dataKey="engine_temperature" stroke="#60a5fa" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-slate-500">
              Waiting for sensor data...
            </div>
          )}
        </div>
        
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/50 min-h-[400px]">
          <h3 className="text-lg font-medium mb-4">Maintenance Recommendation</h3>
          <div className="p-4 rounded-lg bg-slate-800 border border-slate-700">
            <p className="text-lg font-medium text-slate-200">
              {prediction?.maintenance_recommendation || 'Analyzing telemetry...'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
