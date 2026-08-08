import time
import requests
import random
from datetime import datetime

url = "http://localhost:8001/sensor-data"

engine_id = "ENG-MC-004"

def generate_normal_data():
    engine_load = round(random.uniform(40, 85), 2)
    return {
        "engine_id": engine_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "engine_temperature": round(random.uniform(70, 84), 2),
        "oil_pressure": round(random.uniform(4.5, 5.0), 2),
        "fuel_pressure": round(random.uniform(5.5, 6.5), 2),
        "vibration_level": round(random.uniform(0.8, 1.2), 3),
        "rpm": int(random.uniform(1500, 1800)),
        "engine_load": engine_load,
        "coolant_temperature": round(random.uniform(75, 82), 2),
        "exhaust_temperature": round(random.uniform(400, 500), 2),
        "running_period": 2000,
        "fuel_consumption": round(engine_load * 0.8, 2),
        "maintenance": "Done",
        "engine_type": "Diesel",
        "fuel_type": "HFO",
        "manufacturer": "MarineCorp"
    }

def generate_faulty_data():
    data = generate_normal_data()
    # Inject severe overheating and vibration fault
    data["engine_temperature"] = round(random.uniform(96, 110), 2)
    data["vibration_level"] = round(random.uniform(2.5, 3.5), 3)
    data["engine_load"] = round(random.uniform(95, 100), 2)
    return data

def main():
    print("Starting simulation... Will inject fault after 5 successful normal readings.")
    iteration = 0
    while True:
        iteration += 1
        
        if iteration > 5:
            data = generate_faulty_data()
            print("\n*** INJECTING CRITICAL ENGINE FAULT ***")
        else:
            data = generate_normal_data()
            
        try:
            response = requests.post(url, json=data)
            print(f"Sent data. Response: {response.status_code}")
            print(response.json())
        except Exception as e:
            print(f"Error connecting to backend on port 8001: {e}")
            
        time.sleep(5)

if __name__ == "__main__":
    main()

