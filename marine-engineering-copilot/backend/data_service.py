"""
Marine Guardian AI — Unified Data Service

Provides access to structured operational data:
- Live sensor readings (from 120K-row CSV, simulating real-time progression)
- Fault codes and maintenance history
- Sensor trends over time windows
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from config import ENGINE_DATA_CSV, MAINTENANCE_LOG_CSV, FAULT_DISTRIBUTION_CSV


class MarineDataService:
    """Singleton-style data service. Load once at startup, query repeatedly."""

    def __init__(self):
        self._sensor_df = None
        self._maintenance_df = None
        self._fault_dist_df = None
        self._sensor_index = 0  # Pointer to simulate real-time progression

    def _load_sensors(self):
        if self._sensor_df is None:
            print("Loading sensor data...")
            self._sensor_df = pd.read_csv(ENGINE_DATA_CSV, parse_dates=['timestamp'])
            self._sensor_df.sort_values('timestamp', inplace=True)
            self._sensor_df.reset_index(drop=True, inplace=True)
            print(f"   [OK] {len(self._sensor_df)} sensor records loaded")
        return self._sensor_df

    def _load_maintenance(self):
        if self._maintenance_df is None:
            print("Loading maintenance logs...")
            self._maintenance_df = pd.read_csv(MAINTENANCE_LOG_CSV, parse_dates=['Date'])
            self._maintenance_df.sort_values('Date', inplace=True)
            self._maintenance_df.reset_index(drop=True, inplace=True)
            print(f"   [OK] {len(self._maintenance_df)} maintenance records loaded")
        return self._maintenance_df

    def _load_fault_dist(self):
        if self._fault_dist_df is None and os.path.exists(FAULT_DISTRIBUTION_CSV):
            self._fault_dist_df = pd.read_csv(FAULT_DISTRIBUTION_CSV)
        return self._fault_dist_df

    def get_latest_sensors(self) -> dict:
        """Get the current sensor reading (advances through the dataset to simulate real-time)."""
        df = self._load_sensors()
        row = df.iloc[self._sensor_index % len(df)]
        self._sensor_index += 1

        return {
            "engine_id": row.get('engine_id', 'ENG-MC-005'),
            "timestamp": str(row['timestamp']),
            "engine_temperature": round(float(row['engine_temp']), 1) if 'engine_temp' in row else 92.8,
            "oil_pressure": round(float(row['oil_pressure']), 2) if 'oil_pressure' in row else 3.9,
            "fuel_pressure": 6.8, # Mocked as it's not in the base CSV
            "vibration_level": round(float(row['vibration_level']), 2) if 'vibration_level' in row else 4.2,
            "rpm": int(float(row['rpm'])) if 'rpm' in row else 735,
            "engine_load": round(float(row['engine_load']), 1) if 'engine_load' in row else 81.5,
            "coolant_temperature": round(float(row['coolant_temp']), 1) if 'coolant_temp' in row else 89.4,
            "exhaust_temperature": round(float(row['exhaust_temp']), 1) if 'exhaust_temp' in row else 425.8,
            "running_period": int(float(row['running_period'])) if 'running_period' in row else 6850,
            "fuel_consumption": round(float(row['fuel_consumption']), 2) if 'fuel_consumption' in row else 205.3,
            "maintenance": row.get('maintenance_status', 'Monitor'),
            "engine_type": row.get('engine_type', 'Diesel'),
            "fuel_type": row.get('fuel_type', 'HFO'),
            "manufacturer": row.get('manufacturer', 'MarineCorp'),
            "fault_label": row.get('failure_mode', 'Normal'),
        }

    def get_sensor_trends(self, window_size: int = 20) -> list[dict]:
        """Get the last N sensor readings for trend analysis."""
        df = self._load_sensors()
        start = max(0, self._sensor_index - window_size)
        end = self._sensor_index
        rows = df.iloc[start:end]

        return [
            {
                "timestamp": str(r['timestamp']),
                "rpm": round(float(r['rpm']), 1) if 'rpm' in r else 0,
                "temperature": round(float(r['engine_temp']), 1) if 'engine_temp' in r else 0,
                "vibration": round(float(r['vibration_level']), 2) if 'vibration_level' in r else 0,
                "oil_pressure": round(float(r['oil_pressure']), 2) if 'oil_pressure' in r else 0,
            }
            for _, r in rows.iterrows()
        ]

    def get_active_faults(self) -> list[dict]:
        """Check recent sensor readings for fault conditions."""
        df = self._load_sensors()
        # Look at the last 10 readings for any non-Normal fault labels
        start = max(0, self._sensor_index - 10)
        end = self._sensor_index
        recent = df.iloc[start:end]
        fault_col = 'failure_mode' if 'failure_mode' in df.columns else 'Fault Label'
        
        faults = recent[recent[fault_col] != 'Normal']

        if faults.empty:
            return []

        return [
            {
                "timestamp": str(r['timestamp']),
                "fault_label": r[fault_col],
                "rpm": round(float(r['rpm']), 1) if 'rpm' in r else 0,
                "temperature": round(float(r['engine_temp']), 1) if 'engine_temp' in r else 0,
                "vibration": round(float(r['vibration_level']), 2) if 'vibration_level' in r else 0,
            }
            for _, r in faults.iterrows()
        ]

    def get_maintenance_history(self, equipment: str = None, limit: int = 10) -> list[dict]:
        """Get recent maintenance records, optionally filtered by equipment."""
        df = self._load_maintenance()

        if equipment:
            mask = df['Equipment'].str.contains(equipment, case=False, na=False) | \
                   df['Equipment Type'].str.contains(equipment, case=False, na=False)
            filtered = df[mask]
        else:
            filtered = df

        recent = filtered.tail(limit)
        return [
            {
                "date": str(r['Date'].date()) if pd.notna(r['Date']) else 'N/A',
                "equipment": r.get('Equipment', 'N/A'),
                "equipment_type": r.get('Equipment Type', 'N/A'),
                "fault": r.get('Fault', 'N/A'),
                "fault_code": r.get('Fault Code', 'N/A'),
                "severity": r.get('Severity', 'N/A'),
                "action_taken": r.get('Action Taken', 'N/A'),
                "maintenance_type": r.get('Maintenance Type', 'N/A'),
                "downtime_hours": r.get('Downtime Hours', 'N/A'),
                "status": r.get('Status', 'N/A'),
            }
            for _, r in recent.iterrows()
        ]

    def get_fault_codes_for_equipment(self, equipment: str, limit: int = 5) -> list[dict]:
        """Get fault codes historically associated with a specific equipment."""
        df = self._load_maintenance()
        mask = df['Equipment'].str.contains(equipment, case=False, na=False) | \
               df['Equipment Type'].str.contains(equipment, case=False, na=False)
        filtered = df[mask][['Fault Code', 'Fault', 'Severity', 'Action Taken']].drop_duplicates()
        return filtered.head(limit).to_dict('records')


# Global singleton
data_service = MarineDataService()
