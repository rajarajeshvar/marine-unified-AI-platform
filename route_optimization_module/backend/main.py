from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import routes
import uvicorn
import asyncio
from services.ais_stream import ais_stream_client

app = FastAPI(title="Maritime Route Optimization API", version="1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)

@app.on_event("startup")
async def startup_event():
    # Start the AISStream websocket client in the background
    asyncio.create_task(ais_stream_client())

@app.get("/")
def read_root():
    return {"message": "Welcome to Maritime Route Optimization API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
