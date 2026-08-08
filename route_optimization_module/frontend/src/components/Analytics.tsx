"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function Analytics({ data }: { data: any }) {
  const chartData = [
    { name: 'Hour 1', fuel: 400, speed: 20 },
    { name: 'Hour 2', fuel: 300, speed: 18 },
    { name: 'Hour 3', fuel: 320, speed: 18.5 },
    { name: 'Hour 4', fuel: 280, speed: 17 },
    { name: 'Hour 5', fuel: 260, speed: 16 },
    { name: 'Hour 6', fuel: 250, speed: 15 },
  ];

  return (
    <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 h-[400px]">
      <h3 className="text-xl font-semibold mb-4 text-slate-100">Estimated Fuel Consumption vs Speed</h3>
      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis yAxisId="left" stroke="#3b82f6" />
            <YAxis yAxisId="right" orientation="right" stroke="#10b981" />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', color: '#f8fafc' }} />
            <Line yAxisId="left" type="monotone" dataKey="fuel" stroke="#3b82f6" strokeWidth={2} name="Fuel (L)" />
            <Line yAxisId="right" type="monotone" dataKey="speed" stroke="#10b981" strokeWidth={2} name="Speed (knots)" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
