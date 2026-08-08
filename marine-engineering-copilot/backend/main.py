"""
Marine Guardian AI — FastAPI Backend

Endpoints:
  POST /chat           — RAG-powered engineering copilot chat
  GET  /sensors        — Live sensor dashboard data
  GET  /health         — Service health check
  GET  /maintenance    — Recent maintenance history
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import asyncio
from contextlib import asynccontextmanager

from config import API_HOST, API_PORT
from rag_chain import get_rag_chain, extract_equipment_keywords, build_operational_context
from predictive_maintenance import (
    get_live_sensor_data, get_predictions,
    get_active_alarms, get_maintenance_history,
)
from memory import memory

last_automated_alert_signature = None

async def automated_monitoring_loop():
    global last_automated_alert_signature
    while True:
        await asyncio.sleep(10)
        try:
            sensor_data = get_live_sensor_data()
            predictions = get_predictions(sensor_data)
            
            fault_type = predictions.get("fault_type", "None")
            fail_prob = predictions.get("failure_probability", 0.0)
            
            # Check for anomalies (ONLY alert if probability >= 90%)
            if fail_prob >= 90.0:
                # Anti-spam: only send if the prediction signature has changed
                sig = f"{fault_type}_{fail_prob}"
                if sig != last_automated_alert_signature:
                    last_automated_alert_signature = sig
                    
                    alert = {
                        "title": f"🚨 ML Watchdog Alert: {fault_type if fault_type != 'None' else 'High Risk'}",
                        "message": f"Engine {predictions.get('engine_id', 'ENG-MC-005')} is exhibiting signs of {fault_type}. Failure Probability: {fail_prob}%. Recommendation: {predictions.get('maintenance_recommendation')}.",
                        "severity": "critical",
                        "source": "Predictive ML Model"
                    }
                    
                    # CROSS-SERVICE INTEGRATION: Forward to Route Optimization
                    try:
                        import httpx
                        async with httpx.AsyncClient() as client:
                            res = await client.post(
                                "http://localhost:8002/api/engine-failure-alert",
                                json={
                                    "engine_id": predictions.get('engine_id', 'ENG-MC-005'),
                                    "fault_type": fault_type,
                                    "failure_probability": fail_prob
                                },
                                timeout=2.0
                            )
                            if res.status_code == 200:
                                ro_data = res.json()
                                alert["message"] += f"\n\n**Route Optimization Response:** {ro_data.get('action_taken')}"
                    except Exception as e:
                        print(f"Failed to reach Route Optimization module: {e}")
                        
                    alerts_queue.append(alert)
        except Exception as e:
            print(f"Error in automated monitoring loop: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    asyncio.create_task(automated_monitoring_loop())
    yield
    # Shutdown

app = FastAPI(
    title="Marine Guardian AI Engineering Copilot",
    description="RAG-powered AI assistant for merchant vessel operations",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG chain
rag_chain = get_rag_chain()

# In-memory queue for automated alerts
alerts_queue = []


# --- Request / Response Models ---

class ChatRequest(BaseModel):
    message: str
    session_id: str = Field(default="default", description="Session ID for conversation memory")

class SourceInfo(BaseModel):
    source_file: str
    document_type: str
    page: object = None
    equipment_hint: str = ""

class ChatResponse(BaseModel):
    response: str
    sources: list[SourceInfo]
    sensor_data: dict
    predictions: dict
    active_alarms: list[dict]
    active_alarms: list[dict]
    maintenance_context: list[dict]

class AlertInjection(BaseModel):
    title: str
    message: str
    severity: str = "critical"
    source: str

class SensorInput(BaseModel):
    engine_id: str = "ENG-MC-005"
    timestamp: str = "2026-08-05T20:00:00Z"
    engine_temperature: float = 75.0
    oil_pressure: float = 4.0
    vibration_level: float = 2.0
    rpm: int = 1500
    engine_load: float = 50.0
    coolant_temperature: float = 70.0
    exhaust_temperature: float = 400.0
    running_period: int = 100
    fuel_consumption: float = 1000.0


# --- Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "operational", "service": "Marine Guardian AI", "version": "2.0.0"}

@app.post("/inject-alert")
def inject_alert(alert: AlertInjection):
    """Webhook for external modules (Predictive Maintenance, Route Optimization) to send alerts."""
    alerts_queue.append(alert.model_dump())
    return {"status": "alert_queued"}

@app.get("/poll-alerts")
def poll_alerts():
    """Frontend polls this to get unread automated alerts."""
    if not alerts_queue:
        return {"alerts": []}
    
    # Send all pending alerts and clear the queue
    pending_alerts = list(alerts_queue)
    alerts_queue.clear()
    return {"alerts": pending_alerts}

@app.post("/predict")
def manual_predict(sensor_input: SensorInput):
    """Allows manual JSON input to run inference through the ML model."""
    predictions = get_predictions(sensor_input.model_dump())
    return predictions


@app.get("/sensors")
def sensors_endpoint():
    """Live sensor data for the dashboard (independent of chat)."""
    sensor_data = get_live_sensor_data()
    predictions = get_predictions(sensor_data)
    alarms = get_active_alarms()

    return {
        "sensor_data": sensor_data,
        "predictions": predictions,
        "active_alarms": alarms,
    }


@app.get("/maintenance")
def maintenance_endpoint(equipment: Optional[str] = None, limit: int = 10):
    """Recent maintenance history, optionally filtered by equipment."""
    history = get_maintenance_history(equipment=equipment, limit=limit)
    return {"maintenance_history": history}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """Main RAG-powered chat endpoint."""

    print("\n" + "="*50)
    print(f"USER QUERY: {req.message}")
    print("="*50)

    # 1. Fetch live operational data
    sensor_data = get_live_sensor_data()
    predictions = get_predictions(sensor_data)
    alarms = get_active_alarms()
    recent_maintenance = get_maintenance_history(limit=3)

    # 2. Build contextual retrieval query (constraint #1)
    #    Only expands for follow-up questions; standalone queries preserved as-is
    retrieval_query = memory.get_contextual_query(req.session_id, req.message)
    
    if retrieval_query != req.message:
        print(f"EXPANDED QUERY: {retrieval_query}")

    # 3. Fetch equipment-specific maintenance if query mentions equipment (constraint #2)
    #    This is supplementary — not a replacement for general retrieval
    equipment_keywords = extract_equipment_keywords(retrieval_query)
    equipment_maintenance = []
    if equipment_keywords:
        for kw in equipment_keywords[:2]:  # limit to avoid overwhelming context
            equip_records = get_maintenance_history(equipment=kw, limit=2)
            for rec in equip_records:
                if rec not in equipment_maintenance and rec not in recent_maintenance:
                    equipment_maintenance.append(rec)
        equipment_maintenance = equipment_maintenance[:3]  # cap supplementary records

    # 4. Build structured operational context for the LLM
    live_data_str = build_operational_context(
        sensor_data, predictions, alarms, recent_maintenance,
        equipment_maintenance=equipment_maintenance if equipment_maintenance else None
    )

    # 5. Get conversation history
    chat_history = memory.get_history(req.session_id)

    # 6. Invoke RAG chain
    try:
        result = rag_chain({
            "question": req.message,
            "retrieval_query": retrieval_query,
            "live_data": live_data_str,
            "chat_history": chat_history,
        })
    except Exception as e:
        error_msg = str(e)
        print(f"LLM Connection Error: {error_msg}")
        result = {
            "response": f"⚠️ **AI Engine Error:**\n\n```\n{error_msg}\n```\n\nIf you are using OpenAI, please check that your API key is valid and your account has billing credits. If you are using Ollama, ensure it is installed and running.",
            "sources": [],
            "all_sources": []
        }

    # Debug Output
    print("\nRETRIEVED CHUNKS")
    for i, src in enumerate(result.get("all_sources", result["sources"]), 1):
        print(f"\n{i}.")
        print(f"Document: {src['source_file']}")
        print(f"Page: {src['page']}")
        print(f"Component: {src['equipment_hint']}")
        print(f"Score: {src.get('score', 'N/A')}")
    
    used_count = len(result["sources"])
    total_count = len(result.get("all_sources", result["sources"]))
    print(f"\nSOURCES USED: {used_count} / {total_count} retrieved")

    # 7. Store conversation turn
    memory.add_turn(req.session_id, "user", req.message)
    memory.add_turn(req.session_id, "assistant", result["response"])

    return ChatResponse(
        response=result["response"],
        sources=result["sources"],
        sensor_data=sensor_data,
        predictions=predictions,
        active_alarms=alarms,
        maintenance_context=recent_maintenance,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
