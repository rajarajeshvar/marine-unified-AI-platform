from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.session import get_db
from app.schemas.snapshot import DigitalTwinSnapshot
from app.schemas.telemetry import OperationalState, Alert, VesselEvent
from app.simulator.scenario_engine import ScenarioType
from app.simulator.vessel_simulator import vessel_simulator
from app.services.state_manager import state_manager
from app.services.context_provider import rag_context_provider
from app.services.vessel_service import VesselService
from pydantic import BaseModel

router = APIRouter()

class SimulatorStateRequest(BaseModel):
    state: str

class ScenarioRequest(BaseModel):
    scenario: ScenarioType

@router.get("/telemetry/snapshot", response_model=DigitalTwinSnapshot)
async def get_current_snapshot():
    """Retrieve the current unified Digital Twin Snapshot."""
    state = await state_manager.get_state()
    return DigitalTwinSnapshot(
        timestamp=state.timestamp,
        state=state.state,
        engine=state.engine,
        fuel=state.fuel,
        navigation=state.navigation,
        weather=state.weather,
        hull=state.hull,
        battery_level=vessel_simulator.battery_charge,
        alerts=state.active_alerts,
        health=state.health
    )

@router.get("/telemetry/history", response_model=List[Dict[str, Any]])
def get_snapshot_history(limit: int = 60, db: Session = Depends(get_db)):
    """Fetch historical snapshot logs for plotting charts."""
    history = VesselService.get_historical_states(db, limit)
    result = []
    for item in history:
        result.append({
            "timestamp": item.timestamp,
            "state": item.state,
            "engine": item.engine,
            "fuel": item.fuel,
            "navigation": item.navigation,
            "weather": item.weather,
            "hull": item.hull,
            "battery_level": item.engine.get("battery_level", 98.5) if isinstance(item.engine, dict) else 98.5,
            "health": item.health
        })
    result.reverse()
    return result

@router.get("/telemetry/alerts")
def get_alerts_log(active_only: bool = False, limit: int = 50, db: Session = Depends(get_db)):
    """Fetch logged alarms histories."""
    alerts = VesselService.get_alerts_log(db, active_only, limit)
    return [
        {
            "id": a.alert_id,
            "system": a.system,
            "code": a.code,
            "message": a.message,
            "level": a.level,
            "timestamp": a.timestamp,
            "is_active": a.is_active,
            "resolved_at": a.resolved_at
        } for a in alerts
    ]

@router.get("/telemetry/events")
def get_events_log(limit: int = 50, db: Session = Depends(get_db)):
    """Fetch system log timeline entries."""
    events = VesselService.get_events_log(db, limit)
    return [
        {
            "id": e.event_id,
            "event_type": e.event_type,
            "message": e.message,
            "timestamp": e.timestamp
        } for e in events
    ]

@router.get("/rag/context")
async def get_rag_context(minutes: int = 30, db: Session = Depends(get_db)):
    """Exposes structured operational variables logs for Module 8 prompt injects."""
    return await rag_context_provider.get_vessel_context(db, minutes)

# ----------------------------------------------------
# SIMULATOR CALIBRATION ENDPOINTS
# ----------------------------------------------------

@router.post("/simulator/state")
def set_simulator_operating_state(req: SimulatorStateRequest):
    """Sets simulator physics throttle ranges (e.g. STARTING, CRUISE, SHUTDOWN)."""
    try:
        vessel_simulator.set_simulator_state(req.state)
        return {"message": f"Simulator operational state set to {req.state}"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/simulator/scenario")
def set_voyage_scenario(req: ScenarioRequest):
    """Triggers voyage scenario variables overlays (e.g., Heavy Weather, Fuel Leak)."""
    vessel_simulator.set_scenario(req.scenario)
    return {"message": f"Voyage scenario changed to {req.scenario.value}"}
