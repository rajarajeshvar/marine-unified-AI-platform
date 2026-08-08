# AI-Powered Maritime Route Optimization Module

This is a production-ready Route Optimization module for an AI Smart Marine Intelligence Platform. It uses historical AIS data, current weather conditions, and vessel parameters to calculate the optimal route using a spatial A* pathfinding algorithm.

## Features
- **Intelligent Route Planning:** Calculates routes based on distance, fuel consumption, and weather risks.
- **Enterprise Dashboard:** Dark theme, fully responsive UI built with Next.js 15, Tailwind CSS, and Recharts.
- **Interactive Map:** Leaflet-powered maps showing the start, destination, and best route while avoiding simulated storm zones.
- **AI Recommendations:** Provides real-time suggestions like reducing speed or altering course based on live ocean metrics.
- **Microservices Architecture:** Decoupled FastAPI backend and Next.js frontend with Docker support.

## Getting Started

### Using Docker
1. Ensure Docker and Docker Compose are installed.
2. Run `docker-compose up --build`
3. Access the dashboard at `http://localhost:3000`

### Local Development

#### Backend
1. `cd backend`
2. `python -m venv venv`
3. `source venv/bin/activate` (or `.\venv\Scripts\Activate.ps1` on Windows)
4. `pip install -r requirements.txt`
5. `uvicorn main:app --reload`
6. API available at `http://localhost:8000/docs`

#### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`
4. Dashboard available at `http://localhost:3000`

## Structure
- `backend/`: FastAPI API, Database connection, A* Optimization Service
- `frontend/`: Next.js App Router, Map, Analytics, Dashboard Components
- `docker-compose.yml`: For easy containerized execution
