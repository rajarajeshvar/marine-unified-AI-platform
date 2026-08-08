import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_synthetic_data(num_samples=10000):
    np.random.seed(42)
    random.seed(42)
    
    engine_ids = [f'ENG-{i:03d}' for i in range(1, 21)]
    engine_types = ['Diesel', 'Gas', 'Hybrid']
    fuel_types = ['MGO', 'HFO', 'LNG']
    manufacturers = ['MarineCorp', 'OceanTech', 'SeaPower']
    failure_modes = ['Normal', 'Overheating', 'Oil Leak', 'Fuel Injector Clogged', 'Bearing Wear', 'Vibration Anomaly']
    
    data = []
    
    start_date = datetime(2023, 1, 1)
    
    for _ in range(num_samples):
        engine_id = random.choice(engine_ids)
        timestamp = start_date + timedelta(hours=random.randint(0, 8760)) # Random time in 2023
        
        # Base healthy values
        engine_load = round(np.random.uniform(40, 95), 2)
        rpm = int(np.random.normal(1500 + engine_load * 5, 50))
        engine_temp = round(np.random.normal(70 + engine_load * 0.15, 3), 2)
        oil_pressure = round(np.random.normal(4.5, 0.2), 2)
        fuel_pressure = round(np.random.normal(6.0, 0.3), 2)
        vibration_level = round(np.random.normal(1.2, 0.1), 3)
        coolant_temp = round(np.random.normal(80, 2), 2)
        exhaust_temp = round(np.random.normal(400 + engine_load * 2, 15), 2)
        running_period = random.randint(100, 5000)
        fuel_consumption = round(engine_load * 0.8 + np.random.normal(0, 5), 2)
        
        maintenance = random.choice(['Done', 'Pending', 'Overdue'])
        engine_type = random.choice(engine_types)
        fuel_type = random.choice(fuel_types)
        manufacturer = random.choice(manufacturers)
        
        # Inject anomalies based on failure mode
        failure_mode = np.random.choice(failure_modes, p=[0.85, 0.03, 0.03, 0.03, 0.03, 0.03])
        
        if failure_mode == 'Overheating':
            engine_temp += np.random.uniform(15, 25)
            coolant_temp += np.random.uniform(10, 20)
        elif failure_mode == 'Oil Leak':
            oil_pressure -= np.random.uniform(1.0, 2.0)
            engine_temp += np.random.uniform(5, 10)
        elif failure_mode == 'Fuel Injector Clogged':
            fuel_pressure -= np.random.uniform(1.5, 2.5)
            rpm -= np.random.uniform(100, 200)
            fuel_consumption += np.random.uniform(10, 20)
        elif failure_mode == 'Bearing Wear':
            vibration_level += np.random.uniform(0.8, 1.5)
            oil_pressure -= np.random.uniform(0.5, 1.0)
        elif failure_mode == 'Vibration Anomaly':
            vibration_level += np.random.uniform(1.5, 3.0)
        
        data.append({
            'timestamp': timestamp,
            'engine_id': engine_id,
            'engine_temperature': engine_temp,
            'oil_pressure': oil_pressure,
            'fuel_pressure': fuel_pressure,
            'vibration_level': vibration_level,
            'rpm': rpm,
            'engine_load': engine_load,
            'coolant_temperature': coolant_temp,
            'exhaust_temperature': exhaust_temp,
            'running_period': running_period,
            'fuel_consumption': fuel_consumption,
            'maintenance': maintenance,
            'failure_mode': failure_mode,
            'engine_type': engine_type,
            'fuel_type': fuel_type,
            'manufacturer': manufacturer
        })
        
    df = pd.DataFrame(data)
    df.sort_values(by=['engine_id', 'timestamp'], inplace=True)
    df.to_csv('datasets/marine_engine_data.csv', index=False)
    print("Synthetic dataset generated at datasets/marine_engine_data.csv")

if __name__ == '__main__':
    generate_synthetic_data()
