from typing import List
from app.providers.base_provider import BaseTelemetryProvider, BasePredictionProvider, BaseMaintenanceProvider
from app.simulator.vessel_simulator import vessel_simulator
from app.schemas.telemetry import (
    EngineTelemetry, FuelTelemetry, HullTelemetry, NavigationTelemetry, WeatherTelemetry, VesselEvent
)

class SimulatorTelemetryProvider(BaseTelemetryProvider):
    async def get_engine_data(self) -> EngineTelemetry:
        state = vessel_simulator.tick(dt=0)
        return state.engine

    async def get_fuel_data(self) -> FuelTelemetry:
        state = vessel_simulator.tick(dt=0)
        return state.fuel

    async def get_hull_data(self) -> HullTelemetry:
        state = vessel_simulator.tick(dt=0)
        return state.hull

    async def get_navigation_data(self) -> NavigationTelemetry:
        state = vessel_simulator.tick(dt=0)
        return state.navigation

    async def get_weather_data(self) -> WeatherTelemetry:
        state = vessel_simulator.tick(dt=0)
        return state.weather

class SimulatorPredictionProvider(BasePredictionProvider):
    async def get_anomaly_probability(self) -> float:
        # Simulator mocks these indices inside its health index
        state = vessel_simulator.tick(dt=0)
        return state.health.anomaly_probability

    async def get_maintenance_window_days(self) -> int:
        state = vessel_simulator.tick(dt=0)
        return state.health.next_maintenance_days

class SimulatorMaintenanceProvider(BaseMaintenanceProvider):
    async def get_events(self, limit: int = 50) -> List[VesselEvent]:
        # Expose events queue list
        return [
            VesselEvent(
                id=e.id,
                event_type=e.event_type,
                message=e.message,
                timestamp=e.timestamp
            ) for e in vessel_simulator.event_log[-limit:]
        ]
