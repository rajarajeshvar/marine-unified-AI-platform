"use client";

import { useEffect, useState, useRef } from "react";
import dynamic from "next/dynamic";
import "leaflet/dist/leaflet.css";

// Fix for default marker icons in Leaflet with Next.js
const LeafletSetup = () => {
  useEffect(() => {
    (async function init() {
      const L = (await import("leaflet")).default;
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });
    })();
  }, []);
  return null;
};

// Dynamically import map components to avoid SSR issues
const MapContainer = dynamic(() => import("react-leaflet").then((mod) => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then((mod) => mod.TileLayer), { ssr: false });
const Marker = dynamic(() => import("react-leaflet").then((mod) => mod.Marker), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then((mod) => mod.Popup), { ssr: false });
const Polyline = dynamic(() => import("react-leaflet").then((mod) => mod.Polyline), { ssr: false });

export default function Map({ routeData, liveShips, onShipSelect, isEmergency, emergencyHarbor }: { routeData: any, liveShips: any[], onShipSelect: (ship: any) => void, isEmergency?: boolean, emergencyHarbor?: any }) {
  const defaultCenter: [number, number] = [25.0, -40.0];
  const [positions, setPositions] = useState<[number, number][]>([]);
  const [shipIndex, setShipIndex] = useState(0);
  const [mounted, setMounted] = useState(false);

  // Icons
  const [shipIcon, setShipIcon] = useState<any>(null);
  const [liveShipIcon, setLiveShipIcon] = useState<any>(null);
  const [harborIcon, setHarborIcon] = useState<any>(null);

  useEffect(() => {
    setMounted(true);
    (async function initIcon() {
      const L = (await import("leaflet")).default;
      const sIcon = L.divIcon({
        className: 'custom-ship-icon',
        html: '<div style="background-color: #f59e0b; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center;"><span style="color:white; font-size: 12px;">🚢</span></div>',
        iconSize: [24, 24],
        iconAnchor: [12, 12]
      });
      const lIcon = L.divIcon({
        className: 'live-ship-icon',
        html: '<div style="background-color: #10b981; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; display: flex; align-items: center; justify-content: center;"><span style="color:white; font-size: 10px;">🟢</span></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      });
      const hIcon = L.divIcon({
        className: 'harbor-icon',
        html: '<div style="background-color: #ef4444; width: 28px; height: 28px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 15px rgba(239, 68, 68, 0.8); display: flex; align-items: center; justify-content: center;"><span style="color:white; font-size: 14px;">⚓</span></div>',
        iconSize: [28, 28],
        iconAnchor: [14, 14]
      });
      setShipIcon(sIcon);
      setLiveShipIcon(lIcon);
      setHarborIcon(hIcon);
    })();
  }, []);

  useEffect(() => {
    if (routeData && routeData.best_route) {
      const pts = routeData.best_route.map((pt: any) => [pt.lat, pt.lng] as [number, number]);
      setPositions(pts);
      // Set the static current location (e.g., 30% along the route)
      const currentIndex = Math.floor(pts.length * 0.3);
      setShipIndex(currentIndex);
    }
  }, [routeData]);

  if (!mounted) {
    return <div className="h-[500px] w-full bg-slate-800 rounded-lg animate-pulse" />;
  }

  return (
    <div className={`h-[500px] w-full rounded-lg overflow-hidden border ${isEmergency ? 'border-red-600 shadow-[0_0_15px_rgba(220,38,38,0.3)]' : 'border-slate-700'}`}>
      <LeafletSetup />
      <MapContainer center={defaultCenter} zoom={4} style={{ height: "100%", width: "100%", background: "#0f172a" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        {/* Draw a dummy storm area */}
        <Polyline 
            positions={[[25, -45], [35, -45], [35, -35], [25, -35], [25, -45]]} 
            color="red" 
            weight={2}
            dashArray="5, 10" 
        />

        {/* Render Live Ships */}
        {liveShipIcon && liveShips && liveShips.map((ship) => (
          <Marker 
            key={ship.mmsi} 
            position={[ship.lat, ship.lng]} 
            icon={liveShipIcon}
            eventHandlers={{
              click: () => onShipSelect(ship)
            }}
          >
            <Popup>
              <strong>{ship.name || "Unknown"} (MMSI: {ship.mmsi})</strong><br/>
              Speed: {ship.speed_knots} knots<br/>
              <em>Click to optimize route from here</em>
            </Popup>
          </Marker>
        ))}
        
        {positions.length > 0 && (
          <>
            <Polyline positions={positions} color={isEmergency ? "#ef4444" : "#3b82f6"} weight={4} dashArray={isEmergency ? "10, 10" : undefined} className={isEmergency ? "animate-pulse" : ""} />
            <Marker position={positions[0]}>
              <Popup>Start Location</Popup>
            </Marker>
            
            {/* Target Ship Marker */}
            {shipIcon && (
               <Marker position={positions[shipIndex]} icon={shipIcon}>
                 <Popup>
                   Current Ship Location<br/>
                   Speed: ~18 knots<br/>
                   {isEmergency && <span className="text-red-500 font-bold">EMERGENCY REROUTE ACTIVE</span>}
                 </Popup>
               </Marker>
            )}

            {/* Destination / Harbor Marker */}
            {isEmergency && harborIcon ? (
              <Marker position={positions[positions.length - 1]} icon={harborIcon}>
                <Popup>
                  <strong className="text-red-600">🚨 SAFE HARBOR 🚨</strong><br/>
                  {emergencyHarbor?.name || "Nearest Port"}
                </Popup>
              </Marker>
            ) : (
              <Marker position={positions[positions.length - 1]}>
                <Popup>Original Destination</Popup>
              </Marker>
            )}
          </>
        )}
      </MapContainer>
    </div>
  );
}
