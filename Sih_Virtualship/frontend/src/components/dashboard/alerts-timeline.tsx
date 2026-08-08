'use client';

import React from 'react';
import { useVessel } from '../../providers/vessel-provider';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';

export function AlertsTimeline() {
  const { alerts, events } = useVessel();

  const formatTime = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleTimeString('en-US', { hour12: false });
    } catch {
      return '--:--:--';
    }
  };

  const activeAlerts = alerts.filter((a) => a.is_active);

  return (
    <Card className="h-full flex flex-col min-h-[300px]">
      <CardHeader>
        <CardTitle>Safety Alarms & Event Logs</CardTitle>
      </CardHeader>
      
      <CardContent className="flex flex-col gap-4 overflow-hidden flex-grow">
        {/* Active Alerts List */}
        <div>
          <span className="text-[10px] text-slate-500 font-mono uppercase tracking-wider block mb-1.5 font-bold">
            Active Alarms ({activeAlerts.length})
          </span>
          {activeAlerts.length === 0 ? (
            <div className="p-3 text-center border border-slate-800/40 rounded bg-slate-950/20 text-emerald-500 font-mono text-[11px] tracking-tight">
              NO ACTIVE ALARMS - ALL SYSTEMS NOMINAL
            </div>
          ) : (
            <div className="space-y-2 max-h-[140px] overflow-y-auto pr-1">
              {activeAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-2.5 border rounded flex justify-between items-start font-mono text-[11px] leading-tight ${
                    alert.level === 'CRITICAL'
                      ? 'border-rose-950 bg-rose-950/20 text-rose-400 shadow-[inset_0_0_8px_rgba(244,63,94,0.1)]'
                      : 'border-amber-950 bg-amber-950/20 text-amber-400'
                  }`}
                >
                  <div>
                    <span className="font-bold uppercase block text-[10px] mb-0.5">
                      [{alert.level}] {alert.system.toUpperCase()} : {alert.code}
                    </span>
                    <span>{alert.message}</span>
                  </div>
                  <span className="text-slate-500 text-[10px] ml-2 shrink-0">{formatTime(alert.timestamp)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Historical Events Scroll Timeline */}
        <div className="flex-1 flex flex-col min-h-0 border-t border-slate-800/40 pt-3">
          <span className="text-[10px] text-slate-500 font-mono uppercase tracking-wider block mb-2 font-bold">
            System Event Log Stream
          </span>
          <div className="flex-grow overflow-y-auto space-y-1.5 font-mono text-[10px] pr-1.5 scrollbar-thin">
            {events.length === 0 ? (
              <div className="text-slate-650 text-center py-4">No events logged in current session.</div>
            ) : (
              events.map((event) => (
                <div
                  key={event.id}
                  className="flex items-start justify-between p-1.5 border border-slate-850 rounded bg-slate-950/15 text-slate-400 leading-tight"
                >
                  <div className="flex items-start gap-2">
                    <span
                      className={`h-1.5 w-1.5 rounded-full mt-1.5 shrink-0 ${
                        event.event_type === 'STATE_CHANGE'
                          ? 'bg-sky-400'
                          : event.event_type === 'SYSTEM_ALERT'
                          ? 'bg-amber-500'
                          : event.event_type === 'MAINTENANCE'
                          ? 'bg-purple-400'
                          : 'bg-slate-500'
                      }`}
                    />
                    <span>{event.message}</span>
                  </div>
                  <span className="text-slate-600 ml-4 shrink-0">{formatTime(event.timestamp)}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
