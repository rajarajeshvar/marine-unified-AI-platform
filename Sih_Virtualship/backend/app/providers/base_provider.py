from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.schemas.telemetry import (
    EngineTelemetry, FuelTelemetry, HullTelemetry, NavigationTelemetry, WeatherTelemetry, VesselEvent
)

class BaseTelemetryProvider(ABC):
    @abstractmethod
    async def get_engine_data(self) -> EngineTelemetry:
        """Fetch propulsion engine parameters."""
        pass

    @abstractmethod
    async def get_fuel_data(self) -> FuelTelemetry:
        """Fetch fuel systems and consumption metrics."""
        pass

    @abstractmethod
    async def get_hull_data(self) -> HullTelemetry:
        """Fetch hull beam strain and plates corrosion indexes."""
        pass

    @abstractmethod
    async def get_navigation_data(self) -> NavigationTelemetry:
        """Fetch GPS, velocity, and orientation roll/pitch angles."""
        pass

    @abstractmethod
    async def get_weather_data(self) -> WeatherTelemetry:
        """Fetch climate environment metrics."""
        pass

class BasePredictionProvider(ABC):
    @abstractmethod
    async def get_anomaly_probability(self) -> float:
        """Fetch real-time machine learning anomaly likelihood scores."""
        pass

    @abstractmethod
    async def get_maintenance_window_days(self) -> int:
        """Fetch predictive maintenance timeframe recommendations."""
        pass

class BaseMaintenanceProvider(ABC):
    @abstractmethod
    async def get_events(self, limit: int = 50) -> List[VesselEvent]:
        """Fetch recorded system history and maintenance logs."""
        pass
