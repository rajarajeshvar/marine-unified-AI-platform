from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional
from app.db.models import VesselStateHistory, AlertLog, EventLog
from app.schemas.telemetry import VesselState, Alert, VesselEvent, OperationalState
from app.simulator.vessel_simulator import VesselSimulator

# Singleton instance of simulator representing the active vessel
simulator = VesselSimulator()

class VesselService:
    @staticmethod
    def get_simulator() -> VesselSimulator:
        return simulator

    @staticmethod
    def get_current_state() -> VesselState:
        """Fetch the current simulated state of the ship."""
        # Tick with dt=0 to fetch without advancing time manually
        return simulator.tick(dt=0)

    @staticmethod
    def tick_simulator(dt: float = 1.0) -> VesselState:
        """Tick the physics simulator to generate new data."""
        return simulator.tick(dt)

    @staticmethod
    def inject_fault(fault_code: str) -> str:
        return simulator.inject_fault(fault_code)

    @staticmethod
    def clear_fault(fault_code: str) -> str:
        return simulator.clear_fault(fault_code)

    @staticmethod
    def change_operational_state(state: OperationalState) -> str:
        return simulator.change_state(state)

    @staticmethod
    def sync_state_to_db(db: Session, state: VesselState):
        """Saves telemetry snapshot to Postgres history."""
        history_record = VesselStateHistory(
            vessel_id=state.vessel_id,
            timestamp=state.timestamp,
            state=state.state.value,
            engine=state.engine.model_dump(),
            hull=state.hull.model_dump(),
            fuel=state.fuel.model_dump(),
            navigation=state.navigation.model_dump(),
            weather=state.weather.model_dump(),
            health=state.health.model_dump()
        )
        db.add(history_record)
        
        # Sync alerts
        # 1. Update/insert active alerts
        for alert in state.active_alerts:
            existing = db.query(AlertLog).filter(AlertLog.alert_id == alert.id).first()
            if not existing:
                db_alert = AlertLog(
                    alert_id=alert.id,
                    system=alert.system,
                    code=alert.code,
                    message=alert.message,
                    level=alert.level.value,
                    timestamp=alert.timestamp,
                    is_active=alert.is_active,
                    resolved_at=alert.resolved_at
                )
                db.add(db_alert)

        # 2. Deactivate resolved alerts in database
        active_simulator_ids = {a.id for a in state.active_alerts}
        db_active_alerts = db.query(AlertLog).filter(AlertLog.is_active == True).all()
        for db_alert in db_active_alerts:
            # If the database lists it active but it is no longer in the simulator's active alerts:
            if db_alert.alert_id not in active_simulator_ids:
                db_alert.is_active = False
                db_alert.resolved_at = datetime.now(timezone.utc)
                
        # Sync events
        for event in simulator.event_log:
            existing_event = db.query(EventLog).filter(EventLog.event_id == event.id).first()
            if not existing_event:
                db_event = EventLog(
                    event_id=event.id,
                    event_type=event.event_type.value,
                    message=event.message,
                    timestamp=event.timestamp
                )
                db.add(db_event)

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def get_historical_states(db: Session, limit: int = 100) -> List[VesselStateHistory]:
        """Fetch historical logs for plotting trends on charts."""
        return db.query(VesselStateHistory).order_by(VesselStateHistory.timestamp.desc()).limit(limit).all()

    @staticmethod
    def get_alerts_log(db: Session, active_only: bool = False, limit: int = 50) -> List[AlertLog]:
        """Fetch historical and active warnings/errors."""
        query = db.query(AlertLog)
        if active_only:
            query = query.filter(AlertLog.is_active == True)
        return query.order_by(AlertLog.timestamp.desc()).limit(limit).all()

    @staticmethod
    def get_events_log(db: Session, limit: int = 50) -> List[EventLog]:
        """Fetch vessel status modifications, manual settings, and logs."""
        return db.query(EventLog).order_by(EventLog.timestamp.desc()).limit(limit).all()
