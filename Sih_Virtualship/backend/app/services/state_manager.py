import asyncio
import logging
from typing import Optional, List
from datetime import datetime, timezone
from app.schemas.telemetry import (
    VesselState, EngineTelemetry, HullTelemetry, FuelTelemetry,
    NavigationTelemetry, WeatherTelemetry, VesselHealth, OperationalState, Alert
)
from app.core.config import settings
from app.events.event_bus import event_bus

logger = logging.getLogger("marine_twin.state")

class VesselStateManager:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._state: Optional[VesselState] = None
        self._initialize_default_state()

    def _initialize_default_state(self):
        """Seed the starting parameters using values defined in simulator.yaml."""
        logger.info("Initializing Vessel State Manager memory allocations...")
        try:
            config = settings.simulator_config
            init_vals = config["initial_values"]
            
            engine = EngineTelemetry(
                rpm=init_vals["rpm"],
                coolant_temp=init_vals["coolant_temp"],
                oil_pressure=init_vals["oil_pressure"],
                engine_load=init_vals["engine_load"],
                vibration=init_vals["vibration"],
                fuel_flow=init_vals["fuel_flow"]
            )
            hull = HullTelemetry(
                corrosion_pct=init_vals["hull_corrosion"],
                hull_integrity=init_vals["hull_integrity"],
                strain=init_vals["base_strain"],
                vibration=init_vals["vibration"] * 0.4
            )
            fuel = FuelTelemetry(
                tank_level=init_vals["fuel_tank_level"],
                fuel_temp=35.0,
                feed_pressure=3.5,
                consumption_rate=init_vals["fuel_flow"] * 0.85
            )
            navigation = NavigationTelemetry(
                latitude=init_vals["latitude"],
                longitude=init_vals["longitude"],
                sog=18.5,
                cog=init_vals["heading"],
                heading=init_vals["heading"],
                roll=0.0,
                pitch=0.0,
                yaw=0.0
            )
            weather = WeatherTelemetry(
                wind_speed=12.0,
                wind_direction=180.0,
                wave_height=1.2,
                wave_period=6.0,
                air_temp=18.0
            )
            health = VesselHealth(
                overall_health=100.0,
                anomaly_probability=0.01,
                next_maintenance_days=60,
                health_status="NORMAL"
            )
            
            self._state = VesselState(
                vessel_id="MV_TITAN_PRO",
                timestamp=datetime.now(timezone.utc),
                state=OperationalState.CRUISING,
                engine=engine,
                hull=hull,
                fuel=fuel,
                navigation=navigation,
                weather=weather,
                health=health,
                active_alerts=[]
            )
            logger.info("Vessel State Manager successfully seeded with default configuration.")
        except Exception as e:
            logger.critical(f"Failed to seed starting parameters from simulator.yaml: {e}", exc_info=True)
            raise e

    async def get_state(self) -> VesselState:
        """Fetch a lock-safe copy of the current state snapshot."""
        async with self._lock:
            # Pydantic validation handles copying
            return self._state.model_copy(deep=True)

    async def update_state(self, new_state: VesselState):
        """Overwrite the entire vessel state (used by bulk syncs)."""
        async with self._lock:
            self._state = new_state
        await event_bus.publish("vessel_state_changed", new_state)

    async def update_engine(self, engine: EngineTelemetry):
        async with self._lock:
            self._state.engine = engine
        await event_bus.publish("engine_updated", engine)

    async def update_hull(self, hull: HullTelemetry):
        async with self._lock:
            self._state.hull = hull
        await event_bus.publish("hull_updated", hull)

    async def update_fuel(self, fuel: FuelTelemetry):
        async with self._lock:
            self._state.fuel = fuel
        await event_bus.publish("fuel_updated", fuel)

    async def update_navigation(self, navigation: NavigationTelemetry):
        async with self._lock:
            self._state.navigation = navigation
        await event_bus.publish("navigation_updated", navigation)

    async def update_weather(self, weather: WeatherTelemetry):
        async with self._lock:
            self._state.weather = weather
        await event_bus.publish("weather_updated", weather)

    async def update_health(self, health: VesselHealth):
        async with self._lock:
            self._state.health = health
        await event_bus.publish("health_updated", health)

    async def update_alerts(self, alerts: List[Alert]):
        async with self._lock:
            self._state.active_alerts = alerts
        await event_bus.publish("alerts_updated", alerts)

    async def set_operational_state(self, state: OperationalState):
        async with self._lock:
            self._state.state = state
        await event_bus.publish("operational_state_changed", state)

# Singleton state manager instance
state_manager = VesselStateManager()
