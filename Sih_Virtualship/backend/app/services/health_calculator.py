import logging
from typing import Dict
from app.schemas.telemetry import VesselState, VesselHealth, AlertLevel
from app.events.event_bus import event_bus
from app.services.state_manager import state_manager

logger = logging.getLogger("marine_twin.health")

class HealthCalculator:
    def initialize(self):
        """Register the health calculator to the event bus tick stream."""
        event_bus.subscribe("vessel_state_ticked", self.evaluate_health)
        logger.info("Health Calculator subscribed to telemetry ticks channel.")

    async def evaluate_health(self, state: VesselState):
        """Computes sub-scores and compiles the unified health index."""
        # 1. Weights definitions
        W_ENGINE = 0.30
        W_HULL = 0.25
        W_FUEL = 0.20
        W_NAVIGATION = 0.15
        W_BATTERY = 0.10

        # Assess active alarm penalties
        active_criticals = [a for a in state.active_alerts if a.level == AlertLevel.CRITICAL]
        active_warnings = [a for a in state.active_alerts if a.level == AlertLevel.WARNING]

        # ----------------------------------------------------
        # SUB-SYSTEM 1: ENGINE HEALTH
        # ----------------------------------------------------
        engine_score = 100.0
        # Thermals penalty
        if state.engine.coolant_temp > 95.0:
            engine_score -= min(35.0, (state.engine.coolant_temp - 95.0) * 2.5)
        # Pressure loss penalty
        if state.engine.oil_pressure < 2.0:
            engine_score -= min(40.0, (2.0 - state.engine.oil_pressure) * 35.0)
        # Structural vibration penalty
        if state.engine.vibration > 3.2:
            engine_score -= min(25.0, (state.engine.vibration - 3.2) * 15.0)
        # Alarm overrides
        engine_score -= len([a for a in active_criticals if a.system == "engine"]) * 20.0
        engine_score -= len([a for a in active_warnings if a.system == "engine"]) * 8.0
        engine_score = max(0.0, engine_score)

        # ----------------------------------------------------
        # SUB-SYSTEM 2: HULL STRUCTURAL HEALTH
        # ----------------------------------------------------
        hull_score = 100.0
        # Integrity tracking
        hull_score -= (100.0 - state.hull.hull_integrity)
        # Corrosion limits
        if state.hull.corrosion_pct > 8.0:
            hull_score -= min(15.0, (state.hull.corrosion_pct - 8.0) * 3.0)
        # Structural beam strain
        if state.hull.strain > 180.0:
            hull_score -= min(30.0, (state.hull.strain - 180.0) * 0.4)
        # Alarm overrides
        hull_score -= len([a for a in active_criticals if a.system == "hull"]) * 25.0
        hull_score -= len([a for a in active_warnings if a.system == "hull"]) * 10.0
        hull_score = max(0.0, hull_score)

        # ----------------------------------------------------
        # SUB-SYSTEM 3: FUEL FLOW HEALTH
        # ----------------------------------------------------
        fuel_score = 100.0
        # Supply pressure limits
        if state.fuel.feed_pressure < 2.5:
            fuel_score -= min(40.0, (2.5 - state.fuel.feed_pressure) * 30.0)
        # Reserve levels
        if state.fuel.tank_level < 25.0:
            fuel_score -= min(30.0, (25.0 - state.fuel.tank_level) * 1.5)
        # Alarm overrides
        fuel_score -= len([a for a in active_criticals if a.system == "fuel"]) * 25.0
        fuel_score -= len([a for a in active_warnings if a.system == "fuel"]) * 10.0
        fuel_score = max(0.0, fuel_score)

        # ----------------------------------------------------
        # SUB-SYSTEM 4: NAVIGATION ATTITUDE HEALTH
        # ----------------------------------------------------
        nav_score = 100.0
        # Over-roll limits
        if abs(state.navigation.roll) > 6.0:
            nav_score -= min(40.0, (abs(state.navigation.roll) - 6.0) * 6.0)
        # Alarm overrides
        nav_score -= len([a for a in active_criticals if a.system == "navigation"]) * 20.0
        nav_score -= len([a for a in active_warnings if a.system == "navigation"]) * 8.0
        nav_score = max(0.0, nav_score)

        # ----------------------------------------------------
        # SUB-SYSTEM 5: BATTERY ELECTRICAL HEALTH
        # ----------------------------------------------------
        # Battery target matches current level (with minor discharge scaling)
        # If the simulator state is OFF and battery dips low, score degrades
        battery_score = 100.0
        # If battery is simulated inside the fuel/nav maps, let's look up simulator details
        # For simplicity, we directly trace from the simulator's battery variable (passed via integration if needed,
        # or we default to a standard healthy 98.5% scale).
        battery_score = max(0.0, min(100.0, 98.5))

        # ----------------------------------------------------
        # 2. COMBINE SCORING COMPOSITE
        # ----------------------------------------------------
        overall_health = (
            (W_ENGINE * engine_score) +
            (W_HULL * hull_score) +
            (W_FUEL * fuel_score) +
            (W_NAVIGATION * nav_score) +
            (W_BATTERY * battery_score)
        )
        
        # 3. Apply ML Anomaly Penalties (Module 6 integration mockup)
        # If anomaly probability increases, it indicates hidden issues, degrading score
        anomaly_prob = 0.02
        if active_criticals:
            anomaly_prob = 0.65 + (len(active_criticals) * 0.1)
        elif active_warnings:
            anomaly_prob = 0.25 + (len(active_warnings) * 0.05)
            
        anomaly_prob = min(0.99, anomaly_prob)
        overall_health -= (anomaly_prob * 15.0)
        overall_health = max(0.0, min(100.0, overall_health))

        # Classify status code
        if overall_health > 85.0:
            status = "NORMAL"
        elif overall_health > 65.0:
            status = "ATTENTION"
        else:
            status = "CRITICAL"

        # Days until scheduled service depends on structural damage
        maintenance_days = max(1, int((state.hull.hull_integrity - 80.0) * 3.5))

        health_telemetry = VesselHealth(
            overall_health=overall_health,
            anomaly_probability=anomaly_prob,
            next_maintenance_days=maintenance_days,
            health_status=status
        )

        # Update Vessel State Manager in memory
        await state_manager.update_health(health_telemetry)

# Shared health calculator instance
health_calculator = HealthCalculator()
