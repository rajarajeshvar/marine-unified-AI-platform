from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.post("/chat")
async def chat(request: ChatRequest):
    return {
        "response": f"This is a mock response from the Copilot AI. I am analyzing the engine logs and telemetry for: '{request.message}'. (Note: Heavy ML dependencies are still installing in the background, this is a placeholder!)",
        "sources": [
            {
                "source_file": "engine_manual.pdf",
                "document_type": "manual",
                "page": "42",
                "equipment_hint": "main_engine"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
