import os
from app.providers.base_provider import BaseTelemetryProvider, BasePredictionProvider, BaseMaintenanceProvider
from app.providers.simulator_provider import (
    SimulatorTelemetryProvider, SimulatorPredictionProvider, SimulatorMaintenanceProvider
)
from app.providers.module_provider import (
    ModuleTelemetryProvider, ModulePredictionProvider, ModuleMaintenanceProvider
)

class IntegrationLayer:
    def __init__(self):
        # Initialize providers singletons
        self._sim_telemetry = SimulatorTelemetryProvider()
        self._sim_prediction = SimulatorPredictionProvider()
        self._sim_maintenance = SimulatorMaintenanceProvider()
        
        self._mod_telemetry = ModuleTelemetryProvider()
        self._mod_prediction = ModulePredictionProvider()
        self._mod_maintenance = ModuleMaintenanceProvider()

    def get_telemetry_provider(self) -> BaseTelemetryProvider:
        """Determines source of truth for telemetry streams based on environmental flags."""
        use_real = os.getenv("USE_REAL_TELEMETRY", "false").lower() == "true"
        if use_real:
            return self._mod_telemetry
        return self._sim_telemetry

    def get_prediction_provider(self) -> BasePredictionProvider:
        """Determines source of truth for ML prediction scores."""
        use_real = os.getenv("USE_REAL_PREDICTIONS", "false").lower() == "true"
        if use_real:
            return self._mod_prediction
        return self._sim_prediction

    def get_maintenance_provider(self) -> BaseMaintenanceProvider:
        """Determines source of truth for historical maintenance timelines."""
        use_real = os.getenv("USE_REAL_MAINTENANCE", "false").lower() == "true"
        if use_real:
            return self._mod_maintenance
        return self._sim_maintenance

# Shared integration layer singleton
integration_layer = IntegrationLayer()
