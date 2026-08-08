from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List, Dict
import json
import asyncio
import numpy as np
from datetime import datetime

import models
import schemas
from database import engine, get_db

# Try to load ML models (mock if not present for development)
try:
    import joblib
    from tensorflow.keras.models import load_model
    lstm_model = load_model('../ml/models/marine_engine_model.keras')
    scaler = joblib.load('../ml/preprocessing/scaler.pkl')
    # Load other encoders if necessary
    with open('../ml/models/class_mapping.json', 'r') as f:
        class_mapping = json.load(f)
except Exception as e:
    print(f"ML models not found or failed to load: {e}. Using mock predictions.")
    lstm_model = None
    scaler = None
    class_mapping = {0: "Normal", 1: "Overheating", 2: "Oil Leak", 3: "Fuel Injector Clogged"}

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Marine Predictive Maintenance API", version="1.0.0")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        encoded_message = jsonable_encoder(message)
        for connection in self.active_connections:
            try:
                await connection.send_json(encoded_message)
            except Exception as e:
                print(f"WebSocket send error: {e}")

manager = ConnectionManager()

def generate_prediction(data: schemas.SensorDataCreate):
    # Base health starts at 100
    health = 100.0
    faults = []
    
    # 1. Temperature Penalty (Normal: < 85)
    if data.engine_temperature > 85:
        penalty = (data.engine_temperature - 85) * 1.5
        health -= penalty
        if data.engine_temperature > 95:
            faults.append("Overheating")
            
    # 2. Vibration Penalty (Normal: < 1.2)
    if data.vibration_level > 1.2:
        penalty = (data.vibration_level - 1.2) * 15
        health -= penalty
        if data.vibration_level > 2.0:
            faults.append("Vibration Anomaly")
            
    # 3. Oil Pressure Penalty (Normal: > 4.5)
    if data.oil_pressure < 4.5:
        penalty = (4.5 - data.oil_pressure) * 12
        health -= penalty
        if data.oil_pressure < 3.0:
            faults.append("Low Oil Pressure")
            
    # 4. Engine Load Penalty (Normal: < 85)
    if data.engine_load > 85:
        penalty = (data.engine_load - 85) * 0.5
        health -= penalty
        if data.engine_load > 95:
            faults.append("Engine Overload")
            
    # Ensure health is within 0-100
    health = max(0.0, min(100.0, health))
    
    # Failure probability mapping based on requested ranges
    if health >= 85:
        fail_prob = (100 - health) / 15 * 10  # 0 to 10%
    elif health >= 40:
        fail_prob = 10 + (85 - health) / 45 * 50 # 10 to 60%
    elif health >= 15:
        fail_prob = 60 + (40 - health) / 25 * 30 # 60 to 90%
    else:
        fail_prob = 90 + (15 - health) / 15 * 10 # 90 to 100%
        
    fail_prob = max(0.0, min(100.0, fail_prob))
    
    # Remaining Useful Life (RUL) estimation
    base_rul = max(0, 5000 - data.running_period)
    rul = base_rul * (health / 100.0) 
    
    # Maintenance Recommendation
    if fail_prob < 10:
        recommendation = "No action required"
    elif fail_prob < 40:
        recommendation = "Schedule routine check"
    elif fail_prob < 75:
        recommendation = "Inspect immediately"
    else:
        recommendation = "URGENT: Halt operation and repair"
        
    fault_type = faults[0] if len(faults) == 1 else ("Multiple Faults" if len(faults) > 1 else "Normal")
        
    return {
        "engine_id": data.engine_id,
        "timestamp": data.timestamp or datetime.utcnow(),
        "health_score": round(health, 2),
        "failure_probability": round(fail_prob, 2),
        "remaining_useful_life": round(rul, 1),
        "maintenance_recommendation": recommendation,
        "fault_type": fault_type
    }

@app.post("/sensor-data", response_model=schemas.PredictionResponse)
async def receive_sensor_data(data: schemas.SensorDataCreate, db: Session = Depends(get_db)):
    # 1. Save sensor data
    sensor_dict = data.dict(exclude={'engine_type', 'fuel_type', 'manufacturer'})
    db_data = models.SensorData(**sensor_dict)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    
    # 2. Run prediction
    pred_result = generate_prediction(data)
        
    # 3. Save prediction
    db_pred = models.Prediction(**pred_result)
    db.add(db_pred)
    db.commit()
    
    # 4. Check alerts
    if pred_result["failure_probability"] > 90:
        alert = models.Alert(
            engine_id=data.engine_id,
            alert_type="High Risk Alert",
            message=f"CRITICAL: Engine {data.engine_id} is at {pred_result['failure_probability']:.2f}% risk of failure due to {pred_result['fault_type']}.",
            severity="critical"
        )
        db.add(alert)
        db.commit()
    elif pred_result["failure_probability"] > 70:
        alert = models.Alert(
            engine_id=data.engine_id,
            alert_type="Normal Alert",
            message=f"WARNING: Engine {data.engine_id} is at {pred_result['failure_probability']:.2f}% risk of failure.",
            severity="warning"
        )
        db.add(alert)
        db.commit()
        
    # 5. Broadcast to websockets
    await manager.broadcast({
        "type": "sensor_update",
        "data": data.dict(),
        "prediction": pred_result
    })
    
    return pred_result

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open, wait for client messages if any
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
