from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class SensorDataCreate(BaseModel):
    engine_id: str
    timestamp: Optional[datetime] = None
    engine_temperature: float
    oil_pressure: float
    fuel_pressure: float
    vibration_level: float
    rpm: int
    engine_load: float
    coolant_temperature: float
    exhaust_temperature: float
    running_period: int
    fuel_consumption: float
    maintenance: str
    
    # Static metadata that might come with the payload
    engine_type: str = "Diesel"
    fuel_type: str = "HFO"
    manufacturer: str = "MarineCorp"

class SensorDataResponse(SensorDataCreate):
    id: int
    timestamp: datetime
    class Config:
        orm_mode = True

class PredictionResponse(BaseModel):
    engine_id: str
    timestamp: datetime
    health_score: float
    failure_probability: float
    remaining_useful_life: float
    maintenance_recommendation: str
    fault_type: str

class AlertResponse(BaseModel):
    id: int
    timestamp: datetime
    engine_id: str
    alert_type: str
    message: str
    severity: str
    resolved: bool
