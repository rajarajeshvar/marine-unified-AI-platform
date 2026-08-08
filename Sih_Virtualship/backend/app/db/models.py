from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Float
from datetime import datetime, timezone
from app.db.session import Base

class VesselStateHistory(Base):
    __tablename__ = "vessel_state_history"

    id = Column(Integer, primary_key=True, index=True)
    vessel_id = Column(String(50), index=True, default="MV_TITAN_PRO")
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    state = Column(String(30), index=True)
    
    # Store subsystems telemetry as structured JSON blobs
    engine = Column(JSON, nullable=False)
    hull = Column(JSON, nullable=False)
    fuel = Column(JSON, nullable=False)
    navigation = Column(JSON, nullable=False)
    weather = Column(JSON, nullable=False)
    health = Column(JSON, nullable=False)

class AlertLog(Base):
    __tablename__ = "alert_log"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(50), unique=True, index=True)
    system = Column(String(50), index=True)
    code = Column(String(50), index=True)
    message = Column(String(255))
    level = Column(String(20), index=True)
    timestamp = Column(DateTime, index=True)
    is_active = Column(Boolean, default=True, index=True)
    resolved_at = Column(DateTime, nullable=True)

class EventLog(Base):
    __tablename__ = "event_log"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), unique=True, index=True)
    event_type = Column(String(50), index=True)
    message = Column(String(255))
    timestamp = Column(DateTime, index=True)
