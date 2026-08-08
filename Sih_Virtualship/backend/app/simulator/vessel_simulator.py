import logging
import math
import random
from datetime import datetime, timezone
from app.core.config import settings
from app.schemas.telemetry import (
    VesselState, EngineTelemetry, HullTelemetry, FuelTelemetry,
    NavigationTelemetry, WeatherTelemetry, VesselHealth, OperationalState
)
from app.physics.drift import calculate_ou_drift
from app.simulator.scenario_engine import ScenarioEngine, ScenarioType
from app.services.state_manager import state_manager

logger = logging.getLogger("marine_twin.simulator")

class VesselSimulator:
    def __init__(self):
        config = settings.simulator_config
        init_vals = config["initial_values"]
        
        # Simulator operating state: OFF, STARTING, IDLE, CRUISE, HIGH_LOAD, WARNING, CRITICAL, SHUTDOWN
        self.sim_state = "CRUISE"
        self.active_scenario = ScenarioType.NORMAL_VOYAGE
        
        # Telemetry variables
        self.fuel_tank_level = init_vals["fuel_tank_level"]
        self.hull_corrosion = init_vals["hull_corrosion"]
        self.hull_integrity = init_vals["hull_integrity"]
        self.base_strain = init_vals["base_strain"]
        self.battery_charge = 98.5  # %
        
        self.rpm = init_vals["rpm"]
        self.coolant_temp = init_vals["coolant_temp"]
        self.oil_pressure = init_vals["oil_pressure"]
        self.engine_load = init_vals["engine_load"]
        self.vibration = init_vals["vibration"]
        self.fuel_flow = init_vals["fuel_flow"]
        
        self.latitude = init_vals["latitude"]
        self.longitude = init_vals["longitude"]
        self.heading = init_vals["heading"]
        
        self.wind_speed = 12.0
        self.wind_direction = 180.0
        self.wave_height = 1.2
        self.wave_period = 6.0
        self.air_temp = 18.0
        
        # Chronological list of vessel event logs
        self.event_log = []

    def set_simulator_state(self, new_state: str):
        """Transition the simulator state."""
            
        valid_states = {"OFF", "STARTING", "IDLE", "CRUISE", "HIGH_LOAD", "WARNING", "CRITICAL", "SHUTDOWN"}
        if new_state not in valid_states:
            raise ValueError(f"Invalid simulator state: {new_state}")
        
        old_state = self.sim_state
        self.sim_state = new_state
        logger.info(f"Operator selected {new_state}")
        
        import uuid
        from app.schemas.telemetry import VesselEvent
        event = VesselEvent(
            id=str(uuid.uuid4()),
            event_type="STATE_CHANGE",
            message=f"Operator selected {new_state}",
            timestamp=datetime.now(timezone.utc)
        )
        self.event_log.append(event)
        if len(self.event_log) > 100:
            self.event_log.pop(0)

    def set_scenario(self, scenario: ScenarioType):
        """Activate a specific voyage scenario."""
        self.active_scenario = scenario
        logger.info(f"Voyage scenario set to: {scenario.value}")
        
        import uuid
        from app.schemas.telemetry import VesselEvent
        event = VesselEvent(
            id=str(uuid.uuid4()),
            event_type="SIMULATOR",
            message=f"Voyage scenario set to: {scenario.value}",
            timestamp=datetime.now(timezone.utc)
        )
        self.event_log.append(event)
        if len(self.event_log) > 100:
            self.event_log.pop(0)

    def tick(self, dt: float = 1.0) -> VesselState:
        """Move the physical simulator clock forward by dt seconds."""
        config = settings.simulator_config
        state_configs = config["states"]
        
        # 1. Fetch target metrics from simulator.yaml matching active simulator state
        sim_state_cfg = state_configs.get(self.sim_state, state_configs["CRUISE"])
        
        target_rpm = sim_state_cfg["target_rpm"]
        target_load = sim_state_cfg["target_load"]
        target_fuel_flow = sim_state_cfg["target_fuel_flow"]
        
        # Default targets
        targets = {
            "target_rpm": target_rpm,
            "target_load": target_load,
            "target_fuel_flow": target_fuel_flow,
            "coolant_temp": 82.5 if self.sim_state != "OFF" else 20.0,
            "oil_pressure": 4.8 if self.sim_state != "OFF" else 0.0,
            "vibration": 1.8 if self.sim_state != "OFF" else 0.05,
            "feed_pressure": 3.5 if self.sim_state != "OFF" else 0.0,
            "battery_charge": 100.0 if self.sim_state != "OFF" else 90.0,
            "wind_speed": 12.0,
            "wave_height": 1.2,
            "wave_period": 6.0,
            "strain": self.base_strain,
            "base_strain": self.base_strain,
            "sog": 18.5 if self.sim_state in ["CRUISE", "HIGH_LOAD"] else 5.0 if self.sim_state == "STARTING" else 0.0
        }
        
        current_state_vars = {
            "hull_integrity": self.hull_integrity
        }
        
        # 2. Inject overrides from the active scenario
        modified_targets, state_overrides = ScenarioEngine.apply_modifiers(
            self.active_scenario, targets, current_state_vars
        )
        
        # Apply state overrides from scenarios
        if "latitude" in state_overrides:
            self.latitude = state_overrides["latitude"]
        if "longitude" in state_overrides:
            self.longitude = state_overrides["longitude"]
        if "heading" in state_overrides:
            self.heading = state_overrides["heading"]
        if "hull_integrity" in state_overrides:
            self.hull_integrity = state_overrides["hull_integrity"]

        # 3. Step parameters using Ornstein-Uhlenbeck continuous equations
        k_normal = 0.05
        k_temp = 0.02
        k_pressure = 0.08

        # Propeller RPM
        self.rpm = calculate_ou_drift(
            self.rpm, modified_targets["target_rpm"], k_normal, dt, 2.0, min_val=0.0
        )
        # Engine Load
        self.engine_load = calculate_ou_drift(
            self.engine_load, modified_targets["target_load"], k_normal, dt, 0.8, min_val=0.0, max_val=100.0
        )
        # Fuel Flow Rate
        self.fuel_flow = calculate_ou_drift(
            self.fuel_flow, modified_targets["target_fuel_flow"], k_normal, dt, 4.0, min_val=0.0
        )
        # Coolant Temperature
        self.coolant_temp = calculate_ou_drift(
            self.coolant_temp, modified_targets["coolant_temp"], k_temp, dt, 0.3, min_val=15.0
        )
        # Lube Oil Pressure
        self.oil_pressure = calculate_ou_drift(
            self.oil_pressure, modified_targets["oil_pressure"], k_pressure, dt, 0.08, min_val=0.0
        )
        # Machine Vibration
        self.vibration = calculate_ou_drift(
            self.vibration, modified_targets["vibration"], k_normal, dt, 0.1, min_val=0.01
        )
        # Battery Charge
        battery_target = modified_targets["battery_charge"]
        if self.sim_state == "OFF":
            # Slow discharge
            self.battery_charge = calculate_ou_drift(self.battery_charge, battery_target, 0.001, dt, 0.01, min_val=0.0, max_val=100.0)
        else:
            # Alternators keep battery at 100%
            self.battery_charge = calculate_ou_drift(self.battery_charge, battery_target, 0.1, dt, 0.05, min_val=0.0, max_val=100.0)

        # 4. Step Environment variables
        self.wind_speed = calculate_ou_drift(self.wind_speed, modified_targets["wind_speed"], 0.02, dt, 1.2, min_val=0.0)
        self.wave_height = calculate_ou_drift(self.wave_height, modified_targets["wave_height"], 0.02, dt, 0.2, min_val=0.1)
        self.wave_period = calculate_ou_drift(self.wave_period, modified_targets["wave_period"], 0.02, dt, 0.1, min_val=1.0)
        
        now = datetime.now(timezone.utc)
        self.wind_direction = (180.0 + math.sin(now.timestamp() / 3600.0) * 15.0 + random.gauss(0, 0.5)) % 360.0
        self.air_temp = 17.5 + math.sin(now.timestamp() / 43200.0) * 4.5

        # 5. Fuel tank consumption
        consumption_kg_sec = (self.fuel_flow * 0.85) / 3600.0
        tank_reduction = (consumption_kg_sec / 50000.0) * 100.0
        self.fuel_tank_level = max(0.0, self.fuel_tank_level - tank_reduction * dt)

        # 6. Hull plating stress calculations
        self.hull_corrosion += (0.000008 * dt)
        if self.active_scenario != ScenarioType.MAINTENANCE_MODE:
            self.hull_integrity = max(0.0, self.hull_integrity - (self.vibration * 0.000015 + self.hull_corrosion * 0.000005) * dt)
            
        strain = calculate_ou_drift(
            modified_targets["strain"], modified_targets["strain"], 1.0, dt, 6.0, min_val=0.0
        )

        # 7. Navigation positioning update
        sog = modified_targets["sog"]
        if self.sim_state in ["CRUISE", "HIGH_LOAD", "STARTING"]:
            velocity_mps = sog * 0.5144
            
            # Minor wave yaw drift
            self.heading = (self.heading + math.sin(now.timestamp() / 400.0) * 0.8 + random.gauss(0, 0.02)) % 360.0
            heading_rad = math.radians(self.heading)
            
            self.latitude += (velocity_mps * math.cos(heading_rad) * dt) / 111000.0
            self.longitude += (velocity_mps * math.sin(heading_rad) * dt) / (111000.0 * math.cos(math.radians(self.latitude)))
        else:
            sog = 0.0

        # Pitch and roll fluctuations depend on wave heights
        roll = math.sin(now.timestamp() / 5.5) * (self.wave_height * 2.8) + random.gauss(0, 0.08)
        pitch = math.cos(now.timestamp() / 7.5) * (self.wave_height * 1.4) + random.gauss(0, 0.04)

        # 8. Compile schemas objects
        engine_telemetry = EngineTelemetry(
            rpm=self.rpm,
            coolant_temp=self.coolant_temp,
            oil_pressure=self.oil_pressure,
            engine_load=self.engine_load,
            vibration=self.vibration,
            fuel_flow=self.fuel_flow
        )
        hull_telemetry = HullTelemetry(
            corrosion_pct=self.hull_corrosion,
            hull_integrity=self.hull_integrity,
            strain=strain,
            vibration=self.vibration * 0.35
        )
        fuel_telemetry = FuelTelemetry(
            tank_level=self.fuel_tank_level,
            fuel_temp=33.8 + (self.rpm / 800.0) * 8.5,
            feed_pressure=modified_targets["feed_pressure"] + random.gauss(0, 0.05),
            consumption_rate=self.fuel_flow * 0.85
        )
        nav_telemetry = NavigationTelemetry(
            latitude=self.latitude,
            longitude=self.longitude,
            sog=sog,
            cog=self.heading + random.gauss(0, 0.1),
            heading=self.heading,
            roll=roll,
            pitch=pitch,
            yaw=math.sin(now.timestamp() / 4.0) * 0.2
        )
        weather_telemetry = WeatherTelemetry(
            wind_speed=self.wind_speed,
            wind_direction=self.wind_direction,
            wave_height=self.wave_height,
            wave_period=self.wave_period,
            air_temp=self.air_temp
        )

        # Determine target operational state
        op_state = OperationalState.CRUISING
        if self.sim_state == "OFF" or self.sim_state == "SHUTDOWN":
            op_state = OperationalState.DOCKED
        elif self.sim_state == "IDLE":
            op_state = OperationalState.ANCHORED
        elif self.sim_state == "STARTING":
            op_state = OperationalState.MANEUVERING

        # Compile current state
        state = VesselState(
            vessel_id="MV_TITAN_PRO",
            timestamp=now,
            state=op_state,
            engine=engine_telemetry,
            hull=hull_telemetry,
            fuel=fuel_telemetry,
            navigation=nav_telemetry,
            weather=weather_telemetry,
            # Placeholder values that AlertEngine and HealthCalculator will fill
            health=VesselHealth(overall_health=100.0, anomaly_probability=0.01, next_maintenance_days=60, health_status="NORMAL"),
            active_alerts=[]
        )
        
        return state

# Shared simulator singleton
vessel_simulator = VesselSimulator()
