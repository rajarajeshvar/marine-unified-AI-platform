$ErrorActionPreference = "Stop"

Write-Host "Starting Digital Twin Backend (Port 8000)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\Users\rajan\OneDrive\Documents\engine_failure_prediction\Sih_Virtualship\backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --host 0.0.0.0 --port 8000"

Write-Host "Starting Maritime Alert Engine (Port 8003)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\Users\rajan\OneDrive\Documents\engine_failure_prediction\maritime_alert_engine\backend; .\venv\Scripts\Activate.ps1; python run_backend.py"

Write-Host "Starting Marine Engineering Copilot (Port 8005)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\Users\rajan\OneDrive\Documents\engine_failure_prediction\marine-engineering-copilot\backend; .\venv\Scripts\Activate.ps1; python main.py"

Write-Host "Starting Predictive Maintenance (Port 8004)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\Users\rajan\OneDrive\Documents\engine_failure_prediction\predictive_maintenance\backend; .\venv\Scripts\Activate.ps1; uvicorn main:app --host 0.0.0.0 --port 8004"

Write-Host "Starting Route Optimization Module (Port 8002)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\Users\rajan\OneDrive\Documents\engine_failure_prediction\route_optimization_module\backend; .\venv\Scripts\Activate.ps1; python main.py"

Write-Host "Starting Main Frontend (Sih_Virtualship)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\Users\rajan\OneDrive\Documents\engine_failure_prediction\Sih_Virtualship\frontend; npm run dev"

Write-Host "All services started in separate windows."
