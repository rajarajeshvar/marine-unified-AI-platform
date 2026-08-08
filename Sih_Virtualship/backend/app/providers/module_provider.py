from typing import List
import uuid
from datetime import datetime, timezone
from app.providers.base_provider import BaseTelemetryProvider, BasePredictionProvider, BaseMaintenanceProvider
from app.schemas.telemetry import (
    EngineTelemetry, FuelTelemetry, HullTelemetry, NavigationTelemetry, WeatherTelemetry, VesselEvent
)

class ModuleTelemetryProvider(BaseTelemetryProvider):
    """Mocks calling HTTP/gRPC API controllers from other teams' modules."""
    async def get_engine_data(self) -> EngineTelemetry:
        return EngineTelemetry(
            rpm=730.0, coolant_temp=83.5, oil_pressure=4.5,
            engine_load=77.0, vibration=1.6, fuel_flow=900.0
        )

    async def get_fuel_data(self) -> FuelTelemetry:
        return FuelTelemetry(
            tank_level=80.0, fuel_temp=36.0,
            feed_pressure=3.6, consumption_rate=880.0
        )

    async def get_hull_data(self) -> HullTelemetry:
        return HullTelemetry(
            corrosion_pct=4.1, hull_integrity=96.0,
            strain=125.0, vibration=0.8
        )

    async def get_navigation_data(self) -> NavigationTelemetry:
        return NavigationTelemetry(
            latitude=51.92, longitude=4.47, sog=18.0, cog=245.0,
            heading=245.0, roll=0.5, pitch=0.2, yaw=0.0
        )

    async def get_weather_data(self) -> WeatherTelemetry:
        return WeatherTelemetry(
            wind_speed=11.5, wind_direction=175.0,
            wave_height=1.1, wave_period=5.8, air_temp=18.2
        )

class ModulePredictionProvider(BasePredictionProvider):
    """Mocks prediction models queries from Module 6 (Anomaly Detection)."""
    async def get_anomaly_probability(self) -> float:
        return 0.03

    async def get_maintenance_window_days(self) -> int:
        return 45

class ModuleMaintenanceProvider(BaseMaintenanceProvider):
    """Mocks timeline logs queries from Module 1 (Predictive Maintenance)."""
    async def get_events(self, limit: int = 50) -> List[VesselEvent]:
        return [
            VesselEvent(
                id=str(uuid.uuid4()),
                event_type="MAINTENANCE",
                message="Mock API: Turbcharger compressor blade cleaned.",
                timestamp=datetime.now(timezone.utc)
            )
        ]
