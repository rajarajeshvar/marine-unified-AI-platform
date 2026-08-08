from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
from app.schemas.telemetry import (
    EngineTelemetry, FuelTelemetry, HullTelemetry, NavigationTelemetry, WeatherTelemetry, VesselHealth, Alert, OperationalState
)

class DigitalTwinSnapshot(BaseModel):
    timestamp: datetime = Field(..., description="UTC timestamp of the snapshot tick")
    state: OperationalState = Field(..., description="Operational status: CRUISING, DOCKED, etc.")
    engine: EngineTelemetry = Field(..., description="Engine machinery metrics")
    fuel: FuelTelemetry = Field(..., description="Fuel tank and flowmeter metrics")
    navigation: NavigationTelemetry = Field(..., description="GPS and inertial attitude metrics")
    weather: WeatherTelemetry = Field(..., description="Environmental conditions metrics")
    hull: HullTelemetry = Field(..., description="Hull strain and corrosion metrics")
    battery_level: float = Field(..., description="Auxiliary battery percentage charge (0-100)")
    alerts: List[Alert] = Field(..., description="List of currently active safety alerts")
    health: VesselHealth = Field(..., description="Aggregated systems health index indicators")
