"use client";
import React from 'react';
import { Navigation, AlertTriangle, ShieldAlert } from 'lucide-react';

export default function ShipDashboard({ activeChannel, signalStrength, pendingAlerts, triggerEmergency }: any) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
        <Navigation className="w-5 h-5 text-indigo-400" />
        Vessel Terminal (Ship-side)
      </h2>
      
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
          <p className="text-sm text-slate-400 mb-1">Active Comms Channel</p>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${activeChannel ? 'bg-emerald-500' : 'bg-red-500'}`} />
            <span className="text-lg text-white font-medium capitalize">{activeChannel || 'DISCONNECTED'}</span>
          </div>
        </div>
        
        <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
          <p className="text-sm text-slate-400 mb-1">Local Queue (Pending)</p>
          <div className="flex items-center gap-2">
            <AlertTriangle className={`w-5 h-5 ${pendingAlerts > 0 ? 'text-amber-500' : 'text-slate-500'}`} />
            <span className="text-lg text-white font-medium">{pendingAlerts} Alerts</span>
          </div>
        </div>
      </div>

      <button 
        onClick={triggerEmergency}
        className="w-full py-4 bg-red-500/20 hover:bg-red-500/30 border border-red-500/50 rounded-xl text-red-400 font-bold tracking-widest flex items-center justify-center gap-2 transition-colors group"
      >
        <ShieldAlert className="w-6 h-6 group-hover:scale-110 transition-transform" />
        TRIGGER AI ENGINE FAILURE
      </button>
    </div>
  );
}
