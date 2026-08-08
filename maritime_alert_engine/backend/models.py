from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from database import Base
import datetime

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(String, primary_key=True, index=True)
    ship_id = Column(String, index=True)
    priority = Column(String) # low, medium, high, critical
    alert_type = Column(String)
    message = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    engine_health = Column(Float)
    fuel_level = Column(Float)
    weather_risk = Column(Float)
    
    status = Column(String, default="Pending") # Pending, Delivered, Failed
    retry_count = Column(Integer, default=0)
    communication_channel = Column(String, nullable=True)

class NetworkStatus(Base):
    __tablename__ = "network_status"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    channel = Column(String, unique=True, index=True) # wifi, cellular, satellite, radio
    is_active = Column(Boolean, default=True)
    signal_strength = Column(Integer, default=100)

class DeliveryLog(Base):
    __tablename__ = "delivery_logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    alert_id = Column(String, index=True)
    attempted_channel = Column(String)
    success = Column(Boolean)
    failure_reason = Column(String, nullable=True)
    attempt_time = Column(DateTime, default=datetime.datetime.utcnow)
