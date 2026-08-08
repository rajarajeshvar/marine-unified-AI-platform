from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Ship(Base):
    __tablename__ = "ships"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    engines = relationship("Engine", back_populates="ship")

class Engine(Base):
    __tablename__ = "engines"
    id = Column(String, primary_key=True, index=True)
    ship_id = Column(Integer, ForeignKey("ships.id"))
    engine_type = Column(String)
    fuel_type = Column(String)
    manufacturer = Column(String)
    ship = relationship("Ship", back_populates="engines")
    sensor_data = relationship("SensorData", back_populates="engine")
    predictions = relationship("Prediction", back_populates="engine")

class SensorData(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    engine_id = Column(String, ForeignKey("engines.id"))
    engine_temperature = Column(Float)
    oil_pressure = Column(Float)
    fuel_pressure = Column(Float)
    vibration_level = Column(Float)
    rpm = Column(Integer)
    engine_load = Column(Float)
    coolant_temperature = Column(Float)
    exhaust_temperature = Column(Float)
    running_period = Column(Integer)
    fuel_consumption = Column(Float)
    maintenance = Column(String)
    engine = relationship("Engine", back_populates="sensor_data")

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    engine_id = Column(String, ForeignKey("engines.id"))
    health_score = Column(Float)
    failure_probability = Column(Float)
    remaining_useful_life = Column(Float)
    maintenance_recommendation = Column(String)
    fault_type = Column(String)
    engine = relationship("Engine", back_populates="predictions")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    engine_id = Column(String, ForeignKey("engines.id"))
    alert_type = Column(String)
    message = Column(String)
    severity = Column(String) # low, medium, high, critical
    resolved = Column(Boolean, default=False)
