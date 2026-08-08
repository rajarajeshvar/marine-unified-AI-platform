import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder

from app.core.config import settings
from app.api.v1.endpoints.telemetry import router as telemetry_router
from app.db.session import engine, SessionLocal
from app.db.models import Base
from app.logging.logger import setup_logging
from app.events.event_bus import event_bus
from app.services.state_manager import state_manager
from app.services.alert_engine import alert_engine
from app.services.health_calculator import health_calculator
from app.simulator.vessel_simulator import vessel_simulator
from app.websocket.connection_manager import manager
from app.schemas.snapshot import DigitalTwinSnapshot
from app.services.vessel_service import VesselService

# Set up enterprise structured JSON logging
setup_logging()
logger = logging.getLogger("marine_twin.main")

async def run_simulator_loop():
    """Background task running the physical tick loop and executing event-driven pipeline."""
    logger.info("Starting background simulator telemetry loop...")
    tick_count = 0
    last_alerts_count = 0
    last_op_state = None
    
    while True:
        try:
            # 1. Sleep for 10 seconds
            await asyncio.sleep(10.0)
            
            # 2. Step the physical simulation model
            raw_state = vessel_simulator.tick(dt=5.0)
            
            # 3. Stream state to State Manager in-memory cache
            await state_manager.update_engine(raw_state.engine)
            await state_manager.update_hull(raw_state.hull)
            await state_manager.update_fuel(raw_state.fuel)
            await state_manager.update_navigation(raw_state.navigation)
            await state_manager.update_weather(raw_state.weather)
            await state_manager.set_operational_state(raw_state.state)
            
            # 4. Announce tick event over internal Event Bus
            # This triggers active alerts assessment and health indexes calculation
            await event_bus.publish("vessel_state_ticked", raw_state)
            
            # 5. Fetch fully processed state (populated with alerts & health)
            processed_state = await state_manager.get_state()
            
            # 6. Package final compiled Digital Twin Snapshot
            snapshot = DigitalTwinSnapshot(
                timestamp=processed_state.timestamp,
                state=processed_state.state,
                engine=processed_state.engine,
                fuel=processed_state.fuel,
                navigation=processed_state.navigation,
                weather=processed_state.weather,
                hull=processed_state.hull,
                battery_level=vessel_simulator.battery_charge,
                alerts=processed_state.active_alerts,
                health=processed_state.health
            )
            
            # 7. Broadcast snapshot to WebSocket clients
            snapshot_data = jsonable_encoder(snapshot)
            await manager.broadcast({
                "type": "snapshot",
                "data": snapshot_data
            })
            
            # 8. Sync state to Postgres history logs (throttled to 10 seconds or instantly on alarm changes)
            tick_count += 1
            alerts_changed = len(processed_state.active_alerts) != last_alerts_count
            state_changed = processed_state.state != last_op_state
            
            if tick_count >= 10 or alerts_changed or state_changed:
                db = SessionLocal()
                try:
                    # Sync state manager snapshot metrics
                    VesselService.sync_state_to_db(db, processed_state)
                    tick_count = 0
                    last_alerts_count = len(processed_state.active_alerts)
                    last_op_state = processed_state.state
                except Exception as db_err:
                    logger.error(f"Error syncing telemetry logs to DB: {db_err}")
                finally:
                    db.close()
                    
        except asyncio.CancelledError:
            logger.info("Simulator loop thread halted.")
            break
        except Exception as e:
            logger.error(f"Unexpected error in background loop: {e}", exc_info=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Digital Twin service starting up...")
    try:
        # Load tables
        Base.metadata.create_all(bind=engine)
        logger.info("SQL database structure initialized.")
    except Exception as e:
        logger.error(f"Failed to generate DB tables: {e}")
        
    # Start event processors
    alert_engine.initialize()
    health_calculator.initialize()
    
    # Spawn simulator task daemon
    sim_task = asyncio.create_task(run_simulator_loop())
    
    yield
    
    # Shutdown actions
    logger.info("Shutting down Digital Twin services...")
    sim_task.cancel()
    try:
        await sim_task
    except asyncio.CancelledError:
        pass
    logger.info("Background processes stopped safely.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Apply CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routes
app.include_router(telemetry_router, prefix=settings.API_V1_STR)

@app.websocket("/ws")
async def ws_telemetry_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial baseline snapshot immediately
        state = await state_manager.get_state()
        snapshot = DigitalTwinSnapshot(
            timestamp=state.timestamp,
            state=state.state,
            engine=state.engine,
            fuel=state.fuel,
            navigation=state.navigation,
            weather=state.weather,
            hull=state.hull,
            battery_level=vessel_simulator.battery_charge,
            alerts=state.active_alerts,
            health=state.health
        )
        await manager.send_personal_message({
            "type": "welcome",
            "data": jsonable_encoder(snapshot)
        }, websocket)
        
        while True:
            # Maintain active websocket connection read loop
            data = await websocket.receive_text()
            logger.debug(f"Received client WS payload: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket connection crash: {e}")
        manager.disconnect(websocket)
