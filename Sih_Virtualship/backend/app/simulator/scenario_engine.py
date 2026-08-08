from enum import Enum
from typing import Dict, Any, Tuple

class ScenarioType(str, Enum):
    NORMAL_VOYAGE = "Normal Voyage"
    HEAVY_WEATHER = "Heavy Weather"
    FUEL_LEAK = "Fuel Leak"
    ENGINE_OVERHEAT = "Engine Overheat"
    BEARING_WEAR = "Bearing Wear"
    COOLING_FAILURE = "Cooling Failure"
    DOCKING = "Docking"
    EMERGENCY_STOP = "Emergency Stop"
    MAINTENANCE_MODE = "Maintenance Mode"

class ScenarioEngine:
    @staticmethod
    def apply_modifiers(scenario: ScenarioType, targets: Dict[str, float], current_state: Dict[str, Any]) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """
        Alters target baselines and current state dynamics based on the active scenario.
        Returns modified targets and state variables.
        """
        modified_targets = targets.copy()
        state_updates = {}

        if scenario == ScenarioType.HEAVY_WEATHER:
            # Storm forces wind speeds up, increasing waves and hull strain
            modified_targets["wind_speed"] = 42.0
            modified_targets["wave_height"] = 6.8
            modified_targets["wave_period"] = 11.5
            modified_targets["strain"] = targets.get("base_strain", 120.0) + 120.0
            modified_targets["vibration"] = targets.get("vibration", 1.8) + 1.2
            
        elif scenario == ScenarioType.FUEL_LEAK:
            # Leak increases fuel flow rate while reducing line pressure
            modified_targets["fuel_flow"] = targets.get("target_fuel_flow", 920.0) * 1.55
            modified_targets["feed_pressure"] = 1.3
            
        elif scenario == ScenarioType.ENGINE_OVERHEAT:
            # Cooling system blockage drives temp to critical limit
            modified_targets["coolant_temp"] = 118.5
            modified_targets["oil_pressure"] = 1.1
            modified_targets["vibration"] = targets.get("vibration", 1.8) + 1.5
            
        elif scenario == ScenarioType.BEARING_WEAR:
            # Friction raises load, vibration, and temperature
            modified_targets["vibration"] = targets.get("vibration", 1.8) * 2.8
            modified_targets["coolant_temp"] = targets.get("coolant_temp", 82.5) + 10.0
            modified_targets["engine_load"] = targets.get("target_load", 78.0) + 8.0
            
        elif scenario == ScenarioType.COOLING_FAILURE:
            # Moderate cooling loss causes temperature to rise slowly
            modified_targets["coolant_temp"] = 98.0
            
        elif scenario == ScenarioType.DOCKING:
            # Force speed and power to zero, coordinates lock to Rotterdam Port
            modified_targets["target_rpm"] = 0.0
            modified_targets["target_load"] = 0.0
            modified_targets["target_fuel_flow"] = 8.0
            modified_targets["sog"] = 0.0
            state_updates["latitude"] = 51.9244
            state_updates["longitude"] = 4.4777
            state_updates["heading"] = 90.0
            
        elif scenario == ScenarioType.EMERGENCY_STOP:
            # Crash astern: throttle engines instantly, deceleration causes high hull vibration
            modified_targets["target_rpm"] = 0.0
            modified_targets["target_load"] = 0.0
            modified_targets["target_fuel_flow"] = 10.0
            modified_targets["sog"] = 0.0
            modified_targets["vibration"] = 4.8
            
        elif scenario == ScenarioType.MAINTENANCE_MODE:
            # Shut down systems, allow repairs (hull integrity increases slowly)
            modified_targets["target_rpm"] = 0.0
            modified_targets["target_load"] = 0.0
            modified_targets["target_fuel_flow"] = 5.0
            modified_targets["sog"] = 0.0
            # Gradual plating replacement
            current_integrity = current_state.get("hull_integrity", 95.8)
            state_updates["hull_integrity"] = min(100.0, current_integrity + 0.05)

        return modified_targets, state_updates
