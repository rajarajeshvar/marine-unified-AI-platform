export type OperationalState = 'DOCKED' | 'MANEUVERING' | 'CRUISING' | 'ANCHORED';
export type AlertLevel = 'INFO' | 'WARNING' | 'CRITICAL';

export interface Alert {
  id: string;
  system: string;
  code: string;
  message: string;
  level: AlertLevel;
  timestamp: string;
  is_active: boolean;
  resolved_at: string | null;
}

export interface VesselEvent {
  id: string;
  event_type: 'STATE_CHANGE' | 'MAINTENANCE' | 'SYSTEM_ALERT' | 'SIMULATOR';
  message: string;
  timestamp: string;
}

export interface EngineTelemetry {
  rpm: number;
  coolant_temp: number;
  oil_pressure: number;
  engine_load: number;
  vibration: number;
  fuel_flow: number;
}

export interface HullTelemetry {
  corrosion_pct: number;
  hull_integrity: number;
  strain: number;
  vibration: number;
}

export interface FuelTelemetry {
  tank_level: number;
  fuel_temp: number;
  feed_pressure: number;
  consumption_rate: number;
}

export interface NavigationTelemetry {
  latitude: number;
  longitude: number;
  sog: number;
  cog: number;
  heading: number;
  roll: number;
  pitch: number;
  yaw: number;
}

export interface WeatherTelemetry {
  wind_speed: number;
  wind_direction: number;
  wave_height: number;
  wave_period: number;
  air_temp: number;
}

export interface VesselHealth {
  overall_health: number;
  anomaly_probability: number;
  next_maintenance_days: number;
  health_status: 'NORMAL' | 'ATTENTION' | 'CRITICAL';
}

export interface DigitalTwinSnapshot {
  timestamp: string;
  state: OperationalState;
  engine: EngineTelemetry;
  fuel: FuelTelemetry;
  navigation: NavigationTelemetry;
  weather: WeatherTelemetry;
  hull: HullTelemetry;
  battery_level: number;
  alerts: Alert[];
  health: VesselHealth;
  simulation_mode: string;
}
