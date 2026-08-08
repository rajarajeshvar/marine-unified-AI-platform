"""
Marine Guardian AI — Predictive Maintenance Module

Uses real sensor data thresholds and fault labels from the dataset
to generate meaningful predictions instead of random values.
"""

import os
import joblib
import pandas as pd
from data_service import data_service

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'predictive_model.pkl')

model_data = None
model = None
feature_cols = None

try:
    if os.path.exists(MODEL_PATH):
        model_data = joblib.load(MODEL_PATH)
        model = model_data["model"]
        feature_cols = model_data["features"]
        print(f"[OK] Loaded trained ML model from {MODEL_PATH}")
    else:
        print(f"[WARNING] ML model not found at {MODEL_PATH}")
except Exception as e:
    print(f"[ERROR] Failed to load ML model: {e}")


def get_live_sensor_data() -> dict:
    """Fetch the next real sensor reading from the 120K-row dataset."""
    return data_service.get_latest_sensors()


def get_predictions(sensor_data: dict) -> dict:
    """
    Generate predictions using the trained Random Forest ML model.
    """
    if model is None or feature_cols is None:
        # Fallback if model not loaded
        return {
            "engine_id": sensor_data.get("engine_id", "ENG-MC-005"),
            "timestamp": sensor_data.get("timestamp", "2026-08-05T20:00:00Z"),
            "health_score": 100.0,
            "failure_probability": 0.0,
            "remaining_useful_life": 10000.0,
            "maintenance_recommendation": "Model not loaded",
            "fault_type": "None"
        }

    # Extract features in the correct order
    input_features = {}
    
    # Mapping the incoming JSON schema to the dataset training columns
    schema_to_train_map = {
        'engine_temp': sensor_data.get('engine_temperature', 75.0),
        'oil_pressure': sensor_data.get('oil_pressure', 4.0),
        'vibration_level': sensor_data.get('vibration_level', 2.0),
        'rpm': sensor_data.get('rpm', 1500),
        'engine_load': sensor_data.get('engine_load', 50.0),
        'coolant_temp': sensor_data.get('coolant_temperature', 70.0),
        'exhaust_temp': sensor_data.get('exhaust_temperature', 400.0),
        'running_period': sensor_data.get('running_period', 100),
        'fuel_consumption': sensor_data.get('fuel_consumption', 1000.0),
    }

    for col in feature_cols:
        input_features[col] = [schema_to_train_map.get(col, 0.0)]
        
    df_input = pd.DataFrame(input_features)
    
    # Inference
    probabilities = model.predict_proba(df_input)[0]
    predicted_class = model.predict(df_input)[0]
    classes = list(model.classes_)
    
    # Calculate overall failure probability (sum of probabilities of all non-Normal classes)
    if "No Failure" in classes:
        no_fail_idx = classes.index("No Failure")
        failure_prob = 1.0 - probabilities[no_fail_idx]
    else:
        failure_prob = max(probabilities)

    # RUL estimation (inverse of failure probability, scaled)
    if failure_prob > 0.7:
        rul = max(50, int(500 * (1 - failure_prob)))
    elif failure_prob > 0.3:
        rul = max(500, int(3000 * (1 - failure_prob)))
    else:
        rul = max(2000, int(5000 * (1 - failure_prob)))

    # Risk level to recommendation
    if failure_prob > 0.6:
        recommendation = "Immediate shutdown and inspection required"
        health_score = max(0.0, 100.0 - (failure_prob * 100.0) - 20.0)
    elif failure_prob > 0.3:
        recommendation = "Schedule routine check"
        health_score = 100.0 - (failure_prob * 100.0)
    else:
        recommendation = "No action required"
        health_score = 100.0 - (failure_prob * 100.0)
        
    fault_type_output = predicted_class
    if fault_type_output == "No Failure":
        fault_type_output = "None"

    return {
        "engine_id": sensor_data.get("engine_id", "ENG-MC-005"),
        "timestamp": sensor_data.get("timestamp", "2026-08-05T20:00:00Z"),
        "health_score": round(health_score, 1),
        "failure_probability": round(failure_prob * 100, 2),
        "remaining_useful_life": float(rul),
        "maintenance_recommendation": recommendation,
        "fault_type": fault_type_output
    }


def get_active_alarms() -> list[dict]:
    """Get currently active fault conditions from the sensor data."""
    return data_service.get_active_faults()


def get_maintenance_history(equipment: str = None, limit: int = 5) -> list[dict]:
    """Get recent maintenance records for context injection."""
    return data_service.get_maintenance_history(equipment=equipment, limit=limit)
