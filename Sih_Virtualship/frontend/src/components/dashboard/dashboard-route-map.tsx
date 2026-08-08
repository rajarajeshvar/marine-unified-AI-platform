'use client';

import React, { useState, useEffect } from 'react';
import Map from '../route-optimization/Map';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Navigation } from 'lucide-react';

export function DashboardRouteMap() {
  const [routeData, setRouteData] = useState<any>(null);
  const [liveShips, setLiveShips] = useState<any[]>([]);

  useEffect(() => {
    const fetchRoute = async () => {
      try {
        const response = await fetch("http://localhost:8002/optimize-route", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            start: { lat: 25.0, lng: -40.0 },
            destination: { lat: 40.0, lng: -20.0 },
            optimize_for: "balanced"
          })
        });
        const data = await response.json();
        setRouteData(data);
      } catch (error) {
        console.error("Failed to fetch route:", error);
      }
    };

    const fetchLiveShips = async () => {
      try {
        const response = await fetch("http://localhost:8002/live-ships");
        const data = await response.json();
        if (data.ships) {
          setLiveShips(data.ships);
        }
      } catch (error) {
        console.error("Failed to fetch live ships:", error);
      }
    };

    fetchRoute();
    fetchLiveShips();
    
    const interval = setInterval(fetchLiveShips, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="h-[500px] flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-blue-400">
          <Navigation className="w-5 h-5" />
          Active Route & Live Fleet
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-0 overflow-hidden rounded-b-lg">
        <Map 
          routeData={routeData} 
          liveShips={liveShips} 
          onShipSelect={() => {}} 
          isEmergency={false}
          emergencyHarbor={null}
        />
      </CardContent>
    </Card>
  );
}
