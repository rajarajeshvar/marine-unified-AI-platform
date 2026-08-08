import logging
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional
from app.core.config import settings
from app.schemas.telemetry import VesselState, Alert, AlertLevel
from app.events.event_bus import event_bus

logger = logging.getLogger("marine_twin.alerts")

class AlertEngine:
    def __init__(self):
        # Cache active alerts locally to manage state transitions
        # Key format: f"{system}_{code}"
        self.active_alerts: Dict[str, Alert] = {}

    def initialize(self):
        """Subscribe the alert engine to the event bus tick stream."""
        event_bus.subscribe("vessel_state_ticked", self.evaluate_state)
        logger.info("Alert Engine subscribed to telemetry ticks channel.")

    async def evaluate_state(self, state: VesselState):
        """Processes telemetry state against YAML threshold limits."""
        thresholds = settings.thresholds
        alerts_cfg = settings.alerts_config
        
        updated_alerts = []
        alerts_changed = False

        # Helper to process single metric
        def evaluate_metric(system: str, code_prefix: str, value: float, config_key: str):
            nonlocal alerts_changed
            cfg = thresholds.get(system, {}).get(config_key)
            if not cfg:
                return

            limit = cfg["warning"]
            crit_limit = cfg["critical"]
            comp = cfg["comparison"]
            
            level: Optional[AlertLevel] = None
            if comp == "above":
                if value >= crit_limit:
                    level = AlertLevel.CRITICAL
                elif value >= limit:
                    level = AlertLevel.WARNING
            else:  # below
                if value <= crit_limit:
                    level = AlertLevel.CRITICAL
                elif value <= limit:
                    level = AlertLevel.WARNING

            alert_code = f"{code_prefix}_CRITICAL" if level == AlertLevel.CRITICAL else f"{code_prefix}_WARNING"
            alert_key = f"{system}_{code_prefix}"

            if level is not None:
                # Alert is active
                # Check if it was already active with the same severity level
                existing = self.active_alerts.get(alert_key)
                cfg_details = alerts_cfg.get(alert_code, {
                    "message": f"{system.upper()} {code_prefix} limit violation",
                    "level": level.value
                })
                
                if not existing or existing.level != level:
                    # Trigger alert
                    new_alert = Alert(
                        id=str(uuid.uuid4()),
                        system=system,
                        code=alert_code,
                        message=cfg_details["message"],
                        level=level,
                        timestamp=datetime.now(timezone.utc),
                        is_active=True
                    )
                    self.active_alerts[alert_key] = new_alert
                    alerts_changed = True
                    logger.warning(f"ALERT RAISED: [{level.value}] {new_alert.message} (Value: {value:.2f})")
                    # Publish event
                    asyncio = __import__("asyncio")
                    asyncio.create_task(event_bus.publish("alert_raised", new_alert))
            else:
                # No breach. Check if we need to resolve an existing active warning
                if alert_key in self.active_alerts:
                    old_alert = self.active_alerts.pop(alert_key)
                    old_alert.is_active = False
                    old_alert.resolved_at = datetime.now(timezone.utc)
                    alerts_changed = True
                    logger.info(f"ALERT RESOLVED: {old_alert.message}")
                    # Publish event
                    asyncio = __import__("asyncio")
                    asyncio.create_task(event_bus.publish("alert_resolved", old_alert))

        # Evaluate engine metrics
        evaluate_metric("engine", "TEMP", state.engine.coolant_temp, "coolant_temp")
        evaluate_metric("engine", "RPM", state.engine.rpm, "rpm")
        evaluate_metric("engine", "OIL_LOW", state.engine.oil_pressure, "oil_pressure")
        evaluate_metric("engine", "VIB", state.engine.vibration, "vibration")
        
        # Evaluate fuel metrics
        evaluate_metric("fuel", "FUEL", state.fuel.tank_level, "tank_level")
        evaluate_metric("fuel", "PRESSURE", state.fuel.feed_pressure, "feed_pressure")

        # Evaluate hull metrics
        evaluate_metric("hull", "STRESS", state.hull.strain, "strain")
        evaluate_metric("hull", "VIB", state.hull.vibration, "vibration")

        # Evaluate navigation metrics
        evaluate_metric("navigation", "ROLL", state.navigation.roll, "roll")

        # Check special injected simulator scenarios (fuel leaks represent explicit codes)
        # If the simulator state triggers special override states, we can handle it
        # However, fuel feed pressure dropping handles scenario leaks elegantly under generic thresholds.

        if alerts_changed:
            # Sync back to the State Manager
            from app.services.state_manager import state_manager
            await state_manager.update_alerts(list(self.active_alerts.values()))

# Shared alert engine instance
alert_engine = AlertEngine()
