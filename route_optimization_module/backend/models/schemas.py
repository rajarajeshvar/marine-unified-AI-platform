from pydantic import BaseModel
from typing import List, Optional

class Coordinates(BaseModel):
    lat: float
    lng: float

class RouteRequest(BaseModel):
    start: Coordinates
    destination: Coordinates
    vessel_mmsi: Optional[str] = None
    optimize_for: Optional[str] = "balanced" # fuel, time, safety, balanced

class RouteWaypoint(BaseModel):
    lat: float
    lng: float
    timestamp: Optional[str] = None
    speed_knots: Optional[float] = None
    weather_risk: Optional[float] = None

class OptimizationResponse(BaseModel):
    best_route: List[RouteWaypoint]
    alternative_routes: List[List[RouteWaypoint]]
    estimated_fuel_saved_percent: float
    estimated_eta: str
    distance_km: float
    average_speed_knots: float
    weather_risk_score: float
    safety_score: float
    total_cost: float

class Recommendation(BaseModel):
    id: str
    message: str
    type: str # warning, info, success

class DashboardMetrics(BaseModel):
    fuel_saved: float
    eta: str
    distance: float
    avg_speed: float
    weather_risk: float
    safety_score: float
    wind_speed: float
    temperature: float
    visibility: float
