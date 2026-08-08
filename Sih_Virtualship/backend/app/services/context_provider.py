import logging
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from app.db.models import AlertLog, EventLog, VesselStateHistory
from app.services.state_manager import state_manager

logger = logging.getLogger("marine_twin.rag")

class RAGContextProvider:
    @staticmethod
    async def get_vessel_context(db: Session, minutes: int = 30) -> Dict[str, Any]:
        """
        Extracts recent logs, alarms, and telemetry states to feed Module 8 RAG prompts.
        """
        logger.info(f"Extracting vessel context window for last {minutes} minutes...")
        state = await state_manager.get_state()
        
        # Calculate time constraint window
        time_limit = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        
        # Retrieve recent alerts logs
        recent_alerts = db.query(AlertLog).filter(
            AlertLog.timestamp >= time_limit
        ).order_by(AlertLog.timestamp.desc()).all()
        
        # Retrieve recent event logs
        recent_events = db.query(EventLog).filter(
            EventLog.timestamp >= time_limit
        ).order_by(EventLog.timestamp.desc()).all()

        # Build natural context block
        context = {
            "vessel_id": state.vessel_id,
            "current_time_utc": datetime.now(timezone.utc).isoformat(),
            "operational_status": {
                "state": state.state.value,
                "overall_health_score": f"{state.health.overall_health:.1f}%",
                "anomaly_probability": f"{state.health.anomaly_probability * 100:.0f}%",
                "maintenance_status": state.health.health_status,
                "days_until_maintenance": state.health.next_maintenance_days
            },
            "subsystems_telemetry": {
                "propulsion": {
                    "rpm": f"{state.engine.rpm:.0f} RPM",
                    "coolant_temperature": f"{state.engine.coolant_temp:.1f} C",
                    "lubrication_pressure": f"{state.engine.oil_pressure:.2f} bar",
                    "load": f"{state.engine.engine_load:.1f}%",
                    "vibration": f"{state.engine.vibration:.2f} mm/s"
                },
                "fuel": {
                    "tank_level": f"{state.fuel.tank_level:.1f}%",
                    "feed_pressure": f"{state.fuel.feed_pressure:.2f} bar",
                    "consumption_rate": f"{state.fuel.consumption_rate:.1f} kg/h"
                },
                "hull": {
                    "integrity": f"{state.hull.hull_integrity:.2f}%",
                    "corrosion_degradation": f"{state.hull.corrosion_pct:.4f}%",
                    "structural_strain": f"{state.hull.strain:.1f} uE"
                },
                "navigation": {
                    "latitude": state.navigation.latitude,
                    "longitude": state.navigation.longitude,
                    "speed_over_ground": f"{state.navigation.sog:.1f} knots",
                    "heading": f"{state.navigation.heading:.1f} deg"
                }
            },
            "active_alerts": [
                {
                    "system": a.system,
                    "code": a.code,
                    "message": a.message,
                    "level": a.level.value,
                    "timestamp": a.timestamp.isoformat()
                } for a in state.active_alerts
            ],
            "recent_events_log": [
                {
                    "type": e.event_type,
                    "message": e.message,
                    "timestamp": e.timestamp.isoformat()
                } for e in recent_events
            ],
            "recent_alerts_log": [
                {
                    "system": a.system,
                    "code": a.code,
                    "message": a.message,
                    "level": a.level,
                    "is_active": a.is_active,
                    "timestamp": a.timestamp.isoformat()
                } for a in recent_alerts
            ]
        }
        
        return context

# Shared context provider singleton
rag_context_provider = RAGContextProvider()
