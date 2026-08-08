"use client";
import React from 'react';
import { Activity, CheckCircle2, Clock, XCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function FleetDashboard({ alerts }: any) {
  const pending = alerts.filter((a: any) => a.status === 'Pending').length;
  const delivered = alerts.filter((a: any) => a.status === 'Delivered').length;
  const failed = alerts.filter((a: any) => a.status === 'Failed').length;

  const chartData = alerts.map((a: any, i: number) => ({
    time: new Date(a.timestamp).toLocaleTimeString(),
    retry: a.retry_count
  })).reverse().slice(-10);

  return (
    <div className="col-span-1 lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
      <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
        <Activity className="w-5 h-5 text-emerald-400" />
        Fleet Operations Center (HQ)
      </h2>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-4 h-4 text-amber-500" />
            <p className="text-sm text-slate-400">Store & Forward Queue</p>
          </div>
          <p className="text-3xl text-white font-bold">{pending}</p>
        </div>
        <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <p className="text-sm text-slate-400">Delivered Alerts</p>
          </div>
          <p className="text-3xl text-white font-bold">{delivered}</p>
        </div>
        <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
          <div className="flex items-center gap-2 mb-2">
            <XCircle className="w-4 h-4 text-red-500" />
            <p className="text-sm text-slate-400">Failed Permanently</p>
          </div>
          <p className="text-3xl text-white font-bold">{failed}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-sm text-slate-400 mb-4 uppercase tracking-wider">Retry Analytics (Last 10)</h3>
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={10} />
                <YAxis stroke="#94a3b8" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', color: '#fff' }} />
                <Line type="monotone" dataKey="retry" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div>
          <h3 className="text-sm text-slate-400 mb-4 uppercase tracking-wider">Alert Timeline</h3>
          <div className="space-y-3 h-48 overflow-y-auto pr-2 custom-scrollbar">
            {alerts.map((alert: any) => (
              <div key={alert.id} className="bg-slate-800 p-3 rounded-md border border-slate-700 text-sm">
                <div className="flex justify-between items-start mb-1">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    alert.priority === 'critical' ? 'bg-red-500/20 text-red-400' : 
                    alert.priority === 'high' ? 'bg-orange-500/20 text-orange-400' : 'bg-blue-500/20 text-blue-400'
                  }`}>
                    {alert.priority.toUpperCase()}
                  </span>
                  <span className="text-xs text-slate-500">{new Date(alert.timestamp).toLocaleTimeString()}</span>
                </div>
                <p className="text-white mb-2">{alert.message}</p>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Ship: {alert.ship_id}</span>
                  <span className={`${
                    alert.status === 'Delivered' ? 'text-emerald-400' : 'text-amber-400'
                  }`}>
                    {alert.status} {alert.communication_channel ? `via ${alert.communication_channel}` : ''}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
