from fastapi import APIRouter, HTTPException
from models.schemas import RouteRequest, OptimizationResponse, Recommendation
from services.optimization import AStarOptimizer
from services.ais_stream import live_ships_cache
from typing import List, Dict, Any
import random
from datetime import datetime, timedelta
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

optimizer = AStarOptimizer()

@router.get("/live-ships")
async def get_live_ships():
    # Return a list of live ships from the cache
    return {"ships": list(live_ships_cache.values())}

@router.post("/optimize-route", response_model=OptimizationResponse)

async def optimize_route(request: RouteRequest):
    try:
        response = optimizer.calculate_optimal_route(request.start, request.destination, request.optimize_for)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate-eta")
async def calculate_eta(request: RouteRequest):
    # Dummy implementation for now
    eta = datetime.now() + timedelta(days=random.randint(1, 10))
    return {"eta": eta.isoformat()}

@router.post("/calculate-fuel")
async def calculate_fuel(request: RouteRequest):
    # Dummy implementation
    fuel_estimate = random.uniform(100.0, 500.0) # in tons
    return {"estimated_fuel_tons": fuel_estimate}

@router.get("/weather")
async def get_weather(lat: float, lng: float):
    # Dummy weather data
    return {
        "wind_speed": random.uniform(5.0, 30.0),
        "temperature": random.uniform(-5.0, 35.0),
        "visibility": random.uniform(1.0, 10.0),
        "storm_warning": random.choice([True, False])
    }

@router.get("/route-history")
async def get_route_history(vessel_mmsi: str):
    return {"history": []}

@router.get("/recommendations", response_model=List[Recommendation])
async def get_recommendations(lat: float, lng: float):
    recs = [
        {"id": "1", "message": "Reduce speed to 15 knots to save 9% fuel.", "type": "info"},
        {"id": "2", "message": "Divert 35 km north to avoid severe weather.", "type": "warning"},
        {"id": "3", "message": "Maintain current course.", "type": "success"},
        {"id": "4", "message": "Heavy crosswinds detected.", "type": "warning"}
    ]
    # Return a random subset
    return random.sample(recs, k=random.randint(1, 3))

@router.post("/simulate-weather-alert")
async def trigger_weather_alert(message: str = "Severe storm detected on current route. Recommend diverting 35km North."):
    """Trigger a simulated weather alert that forwards to the AI Copilot."""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://localhost:8005/inject-alert",
                json={
                    "title": "Weather Route Optimization",
                    "message": message,
                    "severity": "critical",
                    "source": "Route Optimization Module"
                },
                timeout=2.0
            )
        return {"status": "success", "message": "Weather alert sent to Copilot"}
    except Exception as e:
        logger.error(f"Failed to forward weather alert to Copilot: {e}")
        raise HTTPException(status_code=500, detail="Could not reach Copilot backend.")

from pydantic import BaseModel
class EngineFailureAlert(BaseModel):
    engine_id: str
    fault_type: str
    failure_probability: float

@router.post("/engine-failure-alert")
async def handle_engine_failure(alert: EngineFailureAlert):
    """
    Receives critical engine failure alerts from the Predictive Maintenance Copilot.
    Triggers an automatic route diversion.
    """
    logger.info(f"Received Critical Engine Alert: {alert.fault_type} on {alert.engine_id} ({alert.failure_probability}%).")
    
    # Simulate a rerouting protocol
    reroute_action = f"Ship has been automatically rerouted to the nearest safe port due to critical {alert.fault_type} risk."
    
    return {
        "status": "rerouted",
        "action_taken": reroute_action,
        "new_destination": "Nearest Safe Port",
        "eta_impact": "+12 hours"
    }
