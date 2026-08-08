from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import json
import logging
import httpx

import models, schemas
from database import get_db, engine
from comm_manager import CommunicationManager
from scheduler import start_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Maritime Alert Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to send WS message: {e}")

ws_manager = ConnectionManager()

@app.on_event("startup")
def startup_event():
    start_scheduler()

@app.post("/alerts", response_model=schemas.AlertResponse)
async def create_alert(alert_in: schemas.AlertCreate, db: Session = Depends(get_db)):
    db_alert = models.Alert(**alert_in.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)

    # Process immediately
    manager = CommunicationManager(db)
    manager.process_alert(db_alert)
    
    # Refresh to get updated status
    db.refresh(db_alert)

    # Broadcast update to its own WS
    await ws_manager.broadcast(json.dumps({"event": "alert_created", "alert": alert_in.model_dump()}))
    
    # Forward the alert to the AI Copilot backend
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://localhost:8005/inject-alert",
                json={
                    "title": f"Predictive Maintenance Alert: {db_alert.equipment_type}",
                    "message": db_alert.message,
                    "severity": db_alert.priority,
                    "source": "Maritime Alert Engine"
                },
                timeout=2.0
            )
    except Exception as e:
        logger.error(f"Failed to forward alert to Copilot: {e}")
    
    return db_alert

@app.get("/alerts", response_model=List[schemas.AlertResponse])
def get_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).order_by(models.Alert.timestamp.desc()).all()

@app.get("/pending", response_model=List[schemas.AlertResponse])
def get_pending_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).filter(models.Alert.status == "Pending").order_by(models.Alert.timestamp.desc()).all()

@app.post("/retry")
def trigger_manual_retry(db: Session = Depends(get_db)):
    # Same as what the scheduler does
    manager = CommunicationManager(db)
    pending_alerts = db.query(models.Alert).filter(models.Alert.status == "Pending").all()
    count = 0
    for alert in pending_alerts:
        alert.retry_count += 1
        db.commit()
        if manager.process_alert(alert):
            count += 1
    return {"message": f"Retry attempted for {len(pending_alerts)} alerts. {count} succeeded."}

@app.get("/network/status", response_model=List[schemas.NetworkStatusResponse])
def get_network_status(db: Session = Depends(get_db)):
    return db.query(models.NetworkStatus).all()

@app.post("/network/status", response_model=schemas.NetworkStatusResponse)
async def update_network_status(status_update: schemas.NetworkStatusUpdate, db: Session = Depends(get_db)):
    db_status = db.query(models.NetworkStatus).filter(models.NetworkStatus.channel == status_update.channel).first()
    if not db_status:
        db_status = models.NetworkStatus(channel=status_update.channel)
        db.add(db_status)
    
    db_status.is_active = status_update.is_active
    db_status.signal_strength = status_update.signal_strength
    db.commit()
    db.refresh(db_status)
    
    await ws_manager.broadcast(json.dumps({"event": "network_update", "channel": db_status.channel, "is_active": db_status.is_active}))
    return db_status

@app.get("/logs", response_model=List[schemas.DeliveryLogResponse])
def get_delivery_logs(db: Session = Depends(get_db)):
    return db.query(models.DeliveryLog).order_by(models.DeliveryLog.attempt_time.desc()).all()

@app.post("/chat", response_model=schemas.ChatResponse)
async def chat_endpoint(chat_in: schemas.ChatRequest, db: Session = Depends(get_db)):
    # Very basic mock AI for the techstack
    msg = chat_in.message.lower()
    if "status" in msg or "health" in msg:
        response = "The main engine health is currently monitored. VDES and Starlink channels are active."
    elif "alert" in msg or "emergency" in msg:
        response = "There are pending alerts in the system. The autonomous engine is attempting delivery via fallback channels."
    else:
        response = f"I am your Maritime AI Assistant. You said: '{chat_in.message}'. How can I help you manage the ship today?"
    
    return {"response": response}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
