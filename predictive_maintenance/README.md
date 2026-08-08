# Marine Predictive Maintenance Platform

Module 1 of an AI-powered Marine Predictive Maintenance Platform that predicts engine health and failure probabilities using historical and real-time sensor data.

## Structure

- `/ml`: Machine learning pipelines (TensorFlow, Keras, Pandas)
- `/backend`: FastAPI backend and WebSocket management
- `/frontend`: Next.js 15, React 19 dashboard UI
- `/database`: Database setup and migrations (if applicable)

## Getting Started

1. Set up your Python environment and generate the mock dataset:
   ```bash
   cd ml
   pip install -r requirements.txt
   python generate_data.py
   python train.py
   ```

2. Start the Backend and Database:
   ```bash
   docker-compose up postgres redis backend -d
   ```
   *(Alternatively, run the FastAPI server directly from the `backend/` directory)*

3. Start the Frontend Dashboard:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Integrations

This platform is modular by design. The current module predicts Engine Health, Failure Probability, and Remaining Useful Life. Future modules such as Fuel Optimization, Hull Corrosion Detection, and Digital Twin will seamlessly plug into the FastAPI endpoints and real-time WebSocket events.
