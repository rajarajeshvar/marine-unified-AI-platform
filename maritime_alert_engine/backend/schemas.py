from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlertCreate(BaseModel):
    id: str
    ship_id: str
    priority: str
    alert_type: str
    message: str
    latitude: float
    longitude: float
    engine_health: float
    fuel_level: float
    weather_risk: float

class AlertResponse(AlertCreate):
    timestamp: datetime
    status: str
    retry_count: int
    communication_channel: Optional[str] = None

    class Config:
        from_attributes = True

class NetworkStatusUpdate(BaseModel):
    channel: str
    is_active: bool
    signal_strength: Optional[int] = 100

class NetworkStatusResponse(NetworkStatusUpdate):
    id: int
    
    class Config:
        from_attributes = True

class DeliveryLogResponse(BaseModel):
    id: int
    alert_id: str
    attempted_channel: str
    success: bool
    failure_reason: Optional[str]
    attempt_time: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
