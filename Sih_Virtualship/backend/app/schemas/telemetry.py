from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class OperationalState(str, Enum):
    DOCKED = "DOCKED"
    MANEUVERING = "MANEUVERING"
    CRUISING = "CRUISING"
    ANCHORED = "ANCHORED"

class AlertLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class Alert(BaseModel):
    id: str
    system: str  # engine, hull, fuel, navigation, general
    code: str    # e.g., TEMP_HIGH
    message: str
    level: AlertLevel
    timestamp: datetime
    is_active: bool = True
    resolved_at: Optional[datetime] = None

class EventType(str, Enum):
    STATE_CHANGE = "STATE_CHANGE"
    MAINTENANCE = "MAINTENANCE"
    SYSTEM_ALERT = "SYSTEM_ALERT"
    SIMULATOR = "SIMULATOR"

class VesselEvent(BaseModel):
    id: str
    event_type: EventType
    message: str
    timestamp: datetime

class EngineTelemetry(BaseModel):
    rpm: float = Field(..., description="Engine Revolutions Per Minute")
    coolant_temp: float = Field(..., description="Engine Coolant Temperature in °C")
    oil_pressure: float = Field(..., description="Engine Oil Pressure in bar")
    engine_load: float = Field(..., description="Engine Load percentage (0-100)")
    vibration: float = Field(..., description="Vibration amplitude in mm/s")
    fuel_flow: float = Field(..., description="Fuel Flow Rate in liters/hour")

class HullTelemetry(BaseModel):
    corrosion_pct: float = Field(..., description="Anode corrosion / general corrosion percentage")
    hull_integrity: float = Field(..., description="Structural integrity percentage (0-100)")
    strain: float = Field(..., description="Hull strain / structural load in microstrain")
    vibration: float = Field(..., description="Hull vibration levels in mm/s")

class FuelTelemetry(BaseModel):
    tank_level: float = Field(..., description="Fuel Tank capacity percentage (0-100)")
    fuel_temp: float = Field(..., description="Fuel temperature in °C")
    feed_pressure: float = Field(..., description="Fuel feed pressure in bar")
    consumption_rate: float = Field(..., description="Aggregated fuel consumption rate in kg/hour")

class NavigationTelemetry(BaseModel):
    latitude: float = Field(..., description="Vessel latitude in decimal degrees")
    longitude: float = Field(..., description="Vessel longitude in decimal degrees")
    sog: float = Field(..., description="Speed Over Ground in knots")
    cog: float = Field(..., description="Course Over Ground in degrees (0-359)")
    heading: float = Field(..., description="Heading in degrees (0-359)")
    roll: float = Field(..., description="Vessel roll angle in degrees")
    pitch: float = Field(..., description="Vessel pitch angle in degrees")
    yaw: float = Field(..., description="Vessel yaw rate in deg/s")

class WeatherTelemetry(BaseModel):
    wind_speed: float = Field(..., description="Wind speed in knots")
    wind_direction: float = Field(..., description="Wind direction in degrees")
    wave_height: float = Field(..., description="Significant wave height in meters")
    wave_period: float = Field(..., description="Wave period in seconds")
    air_temp: float = Field(..., description="Ambient air temperature in °C")

class VesselHealth(BaseModel):
    overall_health: float = Field(..., description="Aggregated health index (0-100)")
    anomaly_probability: float = Field(..., description="Real-time ML anomaly score (0-1)")
    next_maintenance_days: int = Field(..., description="Days until recommended scheduled maintenance")
    health_status: str = Field(..., description="Status string: NORMAL, ATTENTION, CRITICAL")

class VesselState(BaseModel):
    vessel_id: str = "MV_TITAN_PRO"
    timestamp: datetime
    state: OperationalState
    engine: EngineTelemetry
    hull: HullTelemetry
    fuel: FuelTelemetry
    navigation: NavigationTelemetry
    weather: WeatherTelemetry
    health: VesselHealth
    active_alerts: List[Alert] = []
