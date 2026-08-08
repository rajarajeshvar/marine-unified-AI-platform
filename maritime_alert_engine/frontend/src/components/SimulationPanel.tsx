"use client";
import React from 'react';
import { Wifi, Smartphone, Satellite, Radio, Settings2, MessageSquare } from 'lucide-react';

export default function SimulationPanel({ networks, onToggle }: any) {
  const getIcon = (channel: string) => {
    switch(channel) {
      case 'twilio': return <MessageSquare className="w-5 h-5" />;
      case 'wifi': return <Wifi className="w-5 h-5" />;
      case 'cellular': return <Smartphone className="w-5 h-5" />;
      case 'satellite': return <Satellite className="w-5 h-5" />;
      case 'radio': return <Radio className="w-5 h-5" />;
      default: return <Wifi className="w-5 h-5" />;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
        <Settings2 className="w-5 h-5 text-blue-400" />
        Simulation Panel
      </h2>
      <div className="space-y-4">
        {networks.map((net: any) => (
          <div key={net.channel} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${net.is_active ? 'bg-blue-500/20 text-blue-400' : 'bg-slate-700 text-slate-400'}`}>
                {getIcon(net.channel)}
              </div>
              <div>
                <p className="text-white font-medium capitalize">{net.channel}</p>
                <p className="text-xs text-slate-400">Signal: {net.signal_strength}%</p>
              </div>
            </div>
            <button 
              onClick={() => onToggle(net.channel, !net.is_active)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${net.is_active ? 'bg-blue-500' : 'bg-slate-600'}`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${net.is_active ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
